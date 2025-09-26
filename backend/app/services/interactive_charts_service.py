import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from app.db import models
from app.services.market_data_service import MarketDataService
from app.services.technical_analysis_service import TechnicalAnalysisService

logger = logging.getLogger(__name__)

class InteractiveChartsService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.technical_service = TechnicalAnalysisService(db)
    
    def get_chart_data(self, symbol: str, timeframe: str = "1d", 
                      start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                      indicators: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive chart data with OHLCV and technical indicators."""
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                # Default to 1 year of data
                start_date = end_date - timedelta(days=365)
            
            # Get price data
            price_data = self.market_data_service.get_historical_data(symbol, start_date, end_date)
            if price_data is None or price_data.empty:
                return {"error": "No price data available"}
            
            # Calculate technical indicators
            technical_data = self.technical_service.calculate_technical_indicators(symbol, price_data)
            
            # Combine data
            chart_data = pd.concat([price_data, technical_data], axis=1)
            chart_data = chart_data.dropna()
            
            # Format OHLCV data
            ohlcv_data = []
            for index, row in chart_data.iterrows():
                ohlcv_data.append({
                    "timestamp": index.isoformat(),
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row['volume'])
                })
            
            # Format technical indicators
            indicators_data = {}
            if indicators:
                for indicator in indicators:
                    if indicator in chart_data.columns:
                        indicators_data[indicator] = [
                            {
                                "timestamp": index.isoformat(),
                                "value": float(row[indicator]) if pd.notna(row[indicator]) else None
                            }
                            for index, row in chart_data.iterrows()
                        ]
            
            # Calculate chart statistics
            stats = self._calculate_chart_statistics(chart_data)
            
            # Get current price
            current_price = self.market_data_service.get_current_price(symbol)
            
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "current_price": float(current_price) if current_price else None,
                "ohlcv_data": ohlcv_data,
                "indicators": indicators_data,
                "statistics": stats,
                "data_points": len(chart_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting chart data: {e}")
            return {"error": str(e)}
    
    def get_order_placement_data(self, symbol: str, user_id: str) -> Dict[str, Any]:
        """Get data needed for order placement on charts."""
        try:
            # Get current price
            current_price = self.market_data_service.get_current_price(symbol)
            if not current_price:
                return {"error": "Current price not available"}
            
            # Get user's portfolio
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            # Get user's holdings for this symbol
            holding = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio.id,
                models.Holding.symbol == symbol
            ).first()
            
            # Get recent price levels for support/resistance
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            price_data = self.market_data_service.get_historical_data(symbol, start_date, end_date)
            
            support_resistance = self._calculate_support_resistance(price_data)
            
            # Get market hours
            market_hours = self._get_market_hours()
            
            return {
                "symbol": symbol,
                "current_price": float(current_price),
                "cash_balance": float(portfolio.cash_balance),
                "holding": {
                    "quantity": float(holding.quantity) if holding else 0,
                    "average_price": float(holding.average_price) if holding else 0,
                    "current_value": float(holding.quantity * current_price) if holding else 0
                },
                "support_resistance": support_resistance,
                "market_hours": market_hours,
                "order_types": ["market", "limit", "stop", "stop_limit"],
                "time_in_force": ["day", "gtc", "ioc", "fok"]
            }
            
        except Exception as e:
            logger.error(f"Error getting order placement data: {e}")
            return {"error": str(e)}
    
    def place_order_from_chart(self, user_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order directly from the chart interface."""
        try:
            # Validate order data
            required_fields = ["symbol", "side", "quantity", "order_type"]
            for field in required_fields:
                if field not in order_data:
                    return {"error": f"Missing required field: {field}"}
            
            # Get portfolio
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            # Get current price
            current_price = self.market_data_service.get_current_price(order_data["symbol"])
            if not current_price:
                return {"error": "Current price not available"}
            
            # Calculate order value
            if order_data["order_type"] == "market":
                order_price = current_price
            elif order_data["order_type"] in ["limit", "stop", "stop_limit"]:
                if "price" not in order_data:
                    return {"error": "Price required for limit/stop orders"}
                order_price = order_data["price"]
            else:
                return {"error": "Invalid order type"}
            
            order_value = order_data["quantity"] * order_price
            
            # Check if user has sufficient funds for buy orders
            if order_data["side"] == "buy" and order_value > portfolio.cash_balance:
                return {"error": "Insufficient funds"}
            
            # Check if user has sufficient shares for sell orders
            if order_data["side"] == "sell":
                holding = self.db.query(models.Holding).filter(
                    models.Holding.portfolio_id == portfolio.id,
                    models.Holding.symbol == order_data["symbol"]
                ).first()
                
                if not holding or holding.quantity < order_data["quantity"]:
                    return {"error": "Insufficient shares"}
            
            # Create order
            order = models.Transaction(
                portfolio_id=portfolio.id,
                symbol=order_data["symbol"],
                transaction_type=order_data["side"],
                quantity=order_data["quantity"],
                price=order_price,
                timestamp=datetime.now(),
                status="pending"
            )
            
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            # Process order immediately (in a real system, this would go through an order management system)
            self._process_order(order, portfolio)
            
            return {
                "success": True,
                "order_id": order.id,
                "message": "Order placed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error placing order from chart: {e}")
            return {"error": str(e)}
    
    def get_chart_patterns(self, symbol: str, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Detect chart patterns in price data."""
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=90)
            
            # Get price data
            price_data = self.market_data_service.get_historical_data(symbol, start_date, end_date)
            if price_data is None or price_data.empty:
                return {"error": "No price data available"}
            
            patterns = []
            
            # Detect common patterns
            patterns.extend(self._detect_head_and_shoulders(price_data))
            patterns.extend(self._detect_double_top_bottom(price_data))
            patterns.extend(self._detect_triangles(price_data))
            patterns.extend(self._detect_flags_pennants(price_data))
            patterns.extend(self._detect_support_resistance(price_data))
            
            return {
                "symbol": symbol,
                "patterns": patterns,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting chart patterns: {e}")
            return {"error": str(e)}
    
    def get_volume_profile(self, symbol: str, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate volume profile for price levels."""
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get price data
            price_data = self.market_data_service.get_historical_data(symbol, start_date, end_date)
            if price_data is None or price_data.empty:
                return {"error": "No price data available"}
            
            # Calculate volume profile
            price_levels = np.linspace(price_data['low'].min(), price_data['high'].max(), 50)
            volume_profile = []
            
            for level in price_levels:
                # Find volume at this price level
                level_volume = 0
                for _, row in price_data.iterrows():
                    if row['low'] <= level <= row['high']:
                        # Distribute volume across price range
                        price_range = row['high'] - row['low']
                        if price_range > 0:
                            level_volume += row['volume'] / price_range
                
                volume_profile.append({
                    "price": float(level),
                    "volume": float(level_volume)
                })
            
            # Find POC (Point of Control) - price level with highest volume
            poc = max(volume_profile, key=lambda x: x['volume'])
            
            return {
                "symbol": symbol,
                "volume_profile": volume_profile,
                "poc": poc,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume profile: {e}")
            return {"error": str(e)}
    
    def get_market_depth(self, symbol: str) -> Dict[str, Any]:
        """Get market depth (order book) data."""
        try:
            # In a real implementation, this would connect to a market data provider
            # For now, we'll create mock data
            
            current_price = self.market_data_service.get_current_price(symbol)
            if not current_price:
                return {"error": "Current price not available"}
            
            # Generate mock order book data
            bids = []
            asks = []
            
            # Generate bids (buy orders)
            for i in range(10):
                price = current_price * (1 - (i + 1) * 0.001)
                volume = np.random.randint(100, 1000)
                bids.append({
                    "price": float(price),
                    "volume": volume,
                    "orders": np.random.randint(1, 10)
                })
            
            # Generate asks (sell orders)
            for i in range(10):
                price = current_price * (1 + (i + 1) * 0.001)
                volume = np.random.randint(100, 1000)
                asks.append({
                    "price": float(price),
                    "volume": volume,
                    "orders": np.random.randint(1, 10)
                })
            
            return {
                "symbol": symbol,
                "current_price": float(current_price),
                "bids": bids,
                "asks": asks,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market depth: {e}")
            return {"error": str(e)}
    
    def _calculate_chart_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic chart statistics."""
        try:
            stats = {
                "price_range": {
                    "high": float(data['high'].max()),
                    "low": float(data['low'].min()),
                    "range": float(data['high'].max() - data['low'].min())
                },
                "volume_stats": {
                    "total_volume": int(data['volume'].sum()),
                    "average_volume": float(data['volume'].mean()),
                    "max_volume": int(data['volume'].max())
                },
                "price_change": {
                    "start_price": float(data['close'].iloc[0]),
                    "end_price": float(data['close'].iloc[-1]),
                    "change": float(data['close'].iloc[-1] - data['close'].iloc[0]),
                    "change_percent": float((data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0] * 100)
                },
                "volatility": {
                    "daily_returns_std": float(data['close'].pct_change().std()),
                    "annualized_volatility": float(data['close'].pct_change().std() * np.sqrt(252))
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating chart statistics: {e}")
            return {}
    
    def _calculate_support_resistance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate support and resistance levels."""
        try:
            if data.empty:
                return {"support": [], "resistance": []}
            
            # Find local highs and lows
            highs = data['high'].rolling(window=5, center=True).max() == data['high']
            lows = data['low'].rolling(window=5, center=True).min() == data['low']
            
            resistance_levels = data[highs]['high'].tolist()
            support_levels = data[lows]['low'].tolist()
            
            # Remove duplicates and sort
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]
            support_levels = sorted(list(set(support_levels)))[:5]
            
            return {
                "support": [float(level) for level in support_levels],
                "resistance": [float(level) for level in resistance_levels]
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return {"support": [], "resistance": []}
    
    def _get_market_hours(self) -> Dict[str, Any]:
        """Get market hours information."""
        return {
            "market_open": "09:30",
            "market_close": "16:00",
            "timezone": "EST",
            "is_market_open": True,  # This would be calculated based on current time
            "next_open": "09:30",
            "next_close": "16:00"
        }
    
    def _detect_head_and_shoulders(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect head and shoulders patterns."""
        patterns = []
        # Simplified implementation
        # In a real system, this would use more sophisticated pattern recognition
        return patterns
    
    def _detect_double_top_bottom(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect double top and bottom patterns."""
        patterns = []
        # Simplified implementation
        return patterns
    
    def _detect_triangles(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect triangle patterns."""
        patterns = []
        # Simplified implementation
        return patterns
    
    def _detect_flags_pennants(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect flag and pennant patterns."""
        patterns = []
        # Simplified implementation
        return patterns
    
    def _detect_support_resistance(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect support and resistance levels."""
        patterns = []
        # Simplified implementation
        return patterns
    
    def _process_order(self, order: models.Transaction, portfolio: models.Portfolio):
        """Process an order (simplified implementation)."""
        try:
            # In a real system, this would go through an order management system
            # For now, we'll just update the portfolio directly
            
            if order.transaction_type == "buy":
                # Check if holding exists
                holding = self.db.query(models.Holding).filter(
                    models.Holding.portfolio_id == portfolio.id,
                    models.Holding.symbol == order.symbol
                ).first()
                
                if holding:
                    # Update existing holding
                    total_cost = (holding.quantity * holding.average_price) + (order.quantity * order.price)
                    total_quantity = holding.quantity + order.quantity
                    holding.average_price = total_cost / total_quantity
                    holding.quantity = total_quantity
                else:
                    # Create new holding
                    holding = models.Holding(
                        portfolio_id=portfolio.id,
                        symbol=order.symbol,
                        quantity=order.quantity,
                        average_price=order.price
                    )
                    self.db.add(holding)
                
                # Update cash balance
                portfolio.cash_balance -= order.quantity * order.price
                
            elif order.transaction_type == "sell":
                # Update holding
                holding = self.db.query(models.Holding).filter(
                    models.Holding.portfolio_id == portfolio.id,
                    models.Holding.symbol == order.symbol
                ).first()
                
                if holding:
                    holding.quantity -= order.quantity
                    if holding.quantity <= 0:
                        self.db.delete(holding)
                
                # Update cash balance
                portfolio.cash_balance += order.quantity * order.price
            
            # Update order status
            order.status = "filled"
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            order.status = "failed"
            self.db.commit()

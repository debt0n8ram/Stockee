from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db import models, schemas
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import requests
import os
from app.services.alpha_vantage_service import AlphaVantageService
from app.services.polygon_service import PolygonService

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self, db: Session):
        self.db = db
        self.alpha_vantage_service = AlphaVantageService()
        self.polygon_service = PolygonService()

    def search_assets(self, query: str, asset_type: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Search for assets by symbol or name"""
        # First try database search
        query_filter = models.Asset.symbol.ilike(f"%{query}%") | models.Asset.name.ilike(f"%{query}%")
        
        if asset_type:
            query_filter = and_(query_filter, models.Asset.asset_type == asset_type)
        
        assets = self.db.query(models.Asset).filter(
            and_(query_filter, models.Asset.is_active == True)
        ).limit(limit).all()
        
        if assets:
            return [
                {
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "asset_type": asset.asset_type,
                    "exchange": asset.exchange,
                    "currency": asset.currency
                }
                for asset in assets
            ]
        
        # If no results in database, try Alpha Vantage search
        try:
            av_results = self.alpha_vantage_service.search_symbols(query)
            if av_results:
                return [
                    {
                        "symbol": result['symbol'],
                        "name": result['name'],
                        "asset_type": "stock",
                        "exchange": result.get('region', ''),
                        "currency": result.get('currency', 'USD')
                    }
                    for result in av_results[:limit]
                ]
        except Exception as e:
            logger.error(f"Alpha Vantage search failed: {e}")
        
        # Fallback to Polygon search
        try:
            polygon_results = self.polygon_service.search_tickers(query, limit=limit)
            if polygon_results:
                return [
                    {
                        "symbol": result['symbol'],
                        "name": result['name'],
                        "asset_type": "stock",
                        "exchange": result.get('primary_exchange', ''),
                        "currency": result.get('currency_name', 'USD')
                    }
                    for result in polygon_results
                ]
        except Exception as e:
            logger.error(f"Polygon search failed: {e}")
        
        return []

    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price for an asset"""
        # First try to get from database
        asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
        if not asset:
            # If asset doesn't exist, try to fetch from API and create it
            return self._fetch_current_price_from_api(symbol)
        
        # Get latest price from database
        latest_price = self.db.query(models.Price).filter(
            models.Price.asset_id == asset.id
        ).order_by(desc(models.Price.timestamp)).first()
        
        if latest_price:
            return {
                'symbol': symbol,
                'price': latest_price.close_price,
                'timestamp': latest_price.timestamp.isoformat(),
                'source': 'database'
            }
        
        # If no price in database, fetch from Alpha Vantage API
        return self._fetch_current_price_from_api(symbol)

    def get_price_history(self, symbol: str, days: int = 30, interval: str = "1d") -> List[Dict]:
        """Get historical price data for an asset"""
        asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
        if not asset:
            # If asset doesn't exist, try to fetch from API
            current_price = self._fetch_current_price_from_api(symbol)
            if current_price:
                asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            else:
                return []
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        prices = self.db.query(models.Price).filter(
            and_(
                models.Price.asset_id == asset.id,
                models.Price.timestamp >= start_date,
                models.Price.timestamp <= end_date
            )
        ).order_by(models.Price.timestamp).all()
        
        # If no historical data or only one data point, try to fetch from API
        if not prices or len(prices) <= 1:
            historical_data = self._fetch_historical_data_from_api(symbol, days)
            if historical_data:
                return historical_data
        
        return [
            {
                "timestamp": price.timestamp.isoformat(),
                "open": price.open_price,
                "high": price.high_price,
                "low": price.low_price,
                "close": price.close_price,
                "volume": price.volume
            }
            for price in prices
        ]

    def get_chart_data(self, symbol: str, days: int = 30, interval: str = "1d") -> Dict:
        """Get formatted chart data for frontend"""
        price_history = self.get_price_history(symbol, days, interval)
        
        if not price_history:
            # Generate mock data for demonstration
            return self._generate_mock_chart_data(symbol, days)
        
        current_price = price_history[-1]["close"]
        previous_price = price_history[0]["close"] if len(price_history) > 1 else current_price
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
        
        return {
            "symbol": symbol,
            "data": price_history,
            "current_price": current_price,
            "change": change,
            "change_percent": change_percent
        }

    def _generate_mock_chart_data(self, symbol: str, days: int) -> Dict:
        """Generate mock chart data for demonstration"""
        import random
        from datetime import datetime, timedelta
        
        # Get current price from current_price method
        current_price_data = self.get_current_price(symbol)
        base_price = current_price_data.get('price', 100.0) if current_price_data else 100.0
        
        # Generate mock historical data
        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            
            # Add some realistic price movement
            price_change = random.uniform(-0.05, 0.05)  # ±5% daily change
            price = base_price * (1 + price_change * (i / days))
            
            # Generate OHLC data
            high = price * random.uniform(1.0, 1.03)
            low = price * random.uniform(0.97, 1.0)
            open_price = price * random.uniform(0.98, 1.02)
            close_price = price
            
            # Generate volume
            volume = random.randint(1000000, 10000000)
            
            data.append({
                "timestamp": date.isoformat(),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
        
        # Calculate change from first to last day
        if len(data) > 1:
            change = data[-1]["close"] - data[0]["close"]
            change_percent = (change / data[0]["close"]) * 100
        else:
            change = 0
            change_percent = 0
        
        return {
            "symbol": symbol,
            "data": data,
            "current_price": data[-1]["close"] if data else base_price,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": sum(d["volume"] for d in data) // len(data) if data else 0,
            "high": max(d["high"] for d in data) if data else base_price,
            "low": min(d["low"] for d in data) if data else base_price,
            "open": data[0]["open"] if data else base_price,
            "market_cap": base_price * 1000000000  # Mock market cap
        }

    def get_trending_assets(self, limit: int = 10) -> List[Dict]:
        """Get trending/most active assets"""
        # Simple implementation - get assets with recent price updates
        recent_assets = self.db.query(models.Asset).join(models.Price).filter(
            models.Price.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).distinct().limit(limit).all()
        
        return [
            {
                "symbol": asset.symbol,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "current_price": self.get_current_price(asset.symbol)
            }
            for asset in recent_assets
        ]

    def get_asset_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get news for a specific asset"""
        # Placeholder implementation - in production, integrate with news API
        return [
            {
                "title": f"Latest news about {symbol}",
                "summary": f"This is placeholder news content for {symbol}",
                "url": f"https://example.com/news/{symbol}",
                "published_at": datetime.utcnow().isoformat(),
                "source": "Example News"
            }
        ]

    def _fetch_current_price_from_api(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current price from Alpha Vantage API"""
        try:
            # Use Alpha Vantage service
            quote_data = self.alpha_vantage_service.get_current_price(symbol)
            
            if quote_data:
                # Create asset if it doesn't exist
                asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
                if not asset:
                    asset = models.Asset(
                        symbol=symbol,
                        name=quote_data.get('name', symbol),
                        asset_type='stock',
                        exchange=quote_data.get('exchange', 'NASDAQ'),
                        currency='USD',
                        is_active=True
                    )
                    self.db.add(asset)
                    self.db.commit()
                    self.db.refresh(asset)
                
                # Store price data
                self._store_price_data(symbol, quote_data['price'])
                
                return {
                    'symbol': symbol,
                    'price': quote_data['price'],
                    'change': quote_data['change'],
                    'change_percent': quote_data['change_percent'],
                    'volume': quote_data['volume'],
                    'high': quote_data['high'],
                    'low': quote_data['low'],
                    'open': quote_data['open'],
                    'timestamp': quote_data['timestamp'],
                    'source': 'alpha_vantage'
                }
            
            # Fallback to mock data for development
            mock_price = 100.0 + hash(symbol) % 1000
            return {
                'symbol': symbol,
                'price': mock_price,
                'change': 0.0,
                'change_percent': 0.0,
                'volume': 1000000,
                'high': mock_price * 1.02,
                'low': mock_price * 0.98,
                'open': mock_price,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'mock'
            }
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def _fetch_historical_data_from_api(self, symbol: str, days: int) -> List[Dict]:
        """Fetch historical data from Alpha Vantage API"""
        try:
            # Use Alpha Vantage service to get historical data
            historical_data = self.alpha_vantage_service.get_historical_data(symbol, days)
            
            if historical_data:
                # Store the data in database
                asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
                if asset:
                    for data_point in historical_data:
                        price_record = models.Price(
                            asset_id=asset.id,
                            timestamp=datetime.fromisoformat(data_point['date'].replace('Z', '+00:00')),
                            open_price=data_point['open'],
                            high_price=data_point['high'],
                            low_price=data_point['low'],
                            close_price=data_point['close'],
                            volume=data_point['volume']
                        )
                        self.db.add(price_record)
                    self.db.commit()
                
                return historical_data
            
            return []
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []

    def _store_price_data(self, symbol: str, price: float):
        """Store price data in database"""
        try:
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if asset:
                price_record = models.Price(
                    asset_id=asset.id,
                    timestamp=datetime.utcnow(),
                    open_price=price,
                    high_price=price,
                    low_price=price,
                    close_price=price,
                    volume=0
                )
                self.db.add(price_record)
                self.db.commit()
        except Exception as e:
            logger.error(f"Error storing price data for {symbol}: {e}")

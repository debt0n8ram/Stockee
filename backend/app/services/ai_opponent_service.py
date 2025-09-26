from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db import models, schemas
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import random
import numpy as np
from app.services.market_data_service import MarketDataService
from app.services.trading_service import TradingService

logger = logging.getLogger(__name__)

class AIOpponentService:
    def __init__(self, db: Session):
        self.db = db
        self.market_service = MarketDataService(db)
        self.trading_service = TradingService(db)
        
        # AI Strategy configurations
        self.strategies = {
            'conservative': {
                'name': 'Conservative AI',
                'risk_tolerance': 0.3,
                'max_position_size': 0.1,  # Max 10% per position
                'preferred_sectors': ['Technology', 'Healthcare', 'Consumer Staples'],
                'min_market_cap': 10000000000,  # $10B+
                'max_trades_per_day': 2
            },
            'aggressive': {
                'name': 'Aggressive AI',
                'risk_tolerance': 0.8,
                'max_position_size': 0.25,  # Max 25% per position
                'preferred_sectors': ['Technology', 'Biotechnology', 'Energy'],
                'min_market_cap': 1000000000,  # $1B+
                'max_trades_per_day': 5
            },
            'technical': {
                'name': 'Technical AI',
                'risk_tolerance': 0.6,
                'max_position_size': 0.15,  # Max 15% per position
                'preferred_sectors': ['Technology', 'Finance', 'Energy'],
                'min_market_cap': 5000000000,  # $5B+
                'max_trades_per_day': 3,
                'uses_technical_indicators': True
            },
            'sentiment': {
                'name': 'Sentiment AI',
                'risk_tolerance': 0.5,
                'max_position_size': 0.12,  # Max 12% per position
                'preferred_sectors': ['Technology', 'Consumer Discretionary', 'Communication'],
                'min_market_cap': 2000000000,  # $2B+
                'max_trades_per_day': 4,
                'uses_sentiment_analysis': True
            }
        }

    def create_ai_opponent(self, user_id: str, strategy_type: str = 'conservative') -> Dict:
        """Create an AI opponent for a user"""
        if strategy_type not in self.strategies:
            strategy_type = 'conservative'
        
        # Create AI portfolio with unique user ID
        import uuid
        ai_user_id = f"ai_opponent_{user_id}_{uuid.uuid4().hex[:8]}"
        ai_portfolio = models.Portfolio(
            user_id=ai_user_id,
            cash_balance=100000.0,
            total_value=100000.0
        )
        self.db.add(ai_portfolio)
        self.db.commit()
        self.db.refresh(ai_portfolio)
        
        # Create AI opponent record
        ai_opponent = models.AIOpponent(
            user_id=user_id,
            ai_user_id=ai_user_id,
            strategy_type=strategy_type,
            start_date=datetime.utcnow(),
            is_active=True
        )
        self.db.add(ai_opponent)
        self.db.commit()
        self.db.refresh(ai_opponent)
        
        return {
            "ai_opponent_id": ai_opponent.id,
            "strategy_type": strategy_type,
            "strategy_name": self.strategies[strategy_type]['name'],
            "initial_balance": 100000.0,
            "message": f"AI Opponent created with {self.strategies[strategy_type]['name']} strategy"
        }

    def execute_ai_trading_cycle(self, user_id: str) -> Dict:
        """Execute AI trading decisions for the day"""
        ai_opponent = self.db.query(models.AIOpponent).filter(
            and_(
                models.AIOpponent.user_id == user_id,
                models.AIOpponent.is_active == True
            )
        ).first()
        
        if not ai_opponent:
            return {"error": "No active AI opponent found"}
        
        ai_portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == ai_opponent.ai_user_id
        ).first()
        
        if not ai_portfolio:
            return {"error": "AI portfolio not found"}
        
        strategy = self.strategies[ai_opponent.strategy_type]
        trades_executed = []
        
        # Get current holdings to avoid over-trading
        current_holdings = self.db.query(models.Holding).filter(
            models.Holding.portfolio_id == ai_portfolio.id
        ).all()
        
        # Calculate available cash
        total_invested = sum(h.quantity * h.average_cost for h in current_holdings)
        available_cash = ai_portfolio.cash_balance
        
        # Execute trading strategy
        if ai_opponent.strategy_type == 'conservative':
            trades_executed = self._execute_conservative_strategy(
                ai_portfolio, strategy, available_cash, current_holdings
            )
        elif ai_opponent.strategy_type == 'aggressive':
            trades_executed = self._execute_aggressive_strategy(
                ai_portfolio, strategy, available_cash, current_holdings
            )
        elif ai_opponent.strategy_type == 'technical':
            trades_executed = self._execute_technical_strategy(
                ai_portfolio, strategy, available_cash, current_holdings
            )
        elif ai_opponent.strategy_type == 'sentiment':
            trades_executed = self._execute_sentiment_strategy(
                ai_portfolio, strategy, available_cash, current_holdings
            )
        
        # Update AI portfolio value
        self._update_ai_portfolio_value(ai_portfolio)
        
        return {
            "trades_executed": len(trades_executed),
            "trades": trades_executed,
            "strategy": strategy['name'],
            "portfolio_value": ai_portfolio.total_value,
            "cash_balance": ai_portfolio.cash_balance
        }

    def _execute_conservative_strategy(self, portfolio, strategy, available_cash, current_holdings):
        """Execute conservative AI strategy"""
        trades = []
        
        # Look for blue-chip stocks with strong fundamentals
        blue_chip_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'JNJ', 'PG', 'KO', 'WMT', 'JPM']
        
        for symbol in blue_chip_symbols[:strategy['max_trades_per_day']]:
            if len(trades) >= strategy['max_trades_per_day']:
                break
                
            # Check if we already have this stock
            existing_holding = next((h for h in current_holdings if h.asset.symbol == symbol), None)
            if existing_holding:
                continue
            
            # Get current price
            price_data = self.market_service.get_current_price(symbol)
            if not price_data:
                continue
            
            current_price = price_data['price']
            
            # Calculate position size (conservative: small positions)
            position_size = min(
                available_cash * strategy['max_position_size'],
                available_cash * 0.05  # Max 5% for conservative
            )
            
            if position_size < 1000:  # Minimum trade size
                continue
            
            quantity = position_size / current_price
            
            try:
                result = self.trading_service.execute_buy_order(
                    user_id=portfolio.user_id,
                    symbol=symbol,
                    quantity=quantity,
                    price=current_price,
                    order_type="market"
                )
                
                trades.append({
                    "action": "BUY",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": current_price,
                    "total": position_size
                })
                
                available_cash -= position_size
                
            except Exception as e:
                logger.error(f"Conservative AI trade failed for {symbol}: {e}")
        
        return trades

    def _execute_aggressive_strategy(self, portfolio, strategy, available_cash, current_holdings):
        """Execute aggressive AI strategy"""
        trades = []
        
        # Look for high-growth, volatile stocks
        growth_symbols = ['TSLA', 'NVDA', 'AMD', 'NFLX', 'SQ', 'ROKU', 'ZM', 'PTON', 'PLTR', 'ARKK']
        
        for symbol in growth_symbols[:strategy['max_trades_per_day']]:
            if len(trades) >= strategy['max_trades_per_day']:
                break
            
            # Check if we already have this stock
            existing_holding = next((h for h in current_holdings if h.asset.symbol == symbol), None)
            if existing_holding:
                continue
            
            # Get current price
            price_data = self.market_service.get_current_price(symbol)
            if not price_data:
                continue
            
            current_price = price_data['price']
            
            # Calculate position size (aggressive: larger positions)
            position_size = min(
                available_cash * strategy['max_position_size'],
                available_cash * 0.15  # Max 15% for aggressive
            )
            
            if position_size < 500:  # Lower minimum for aggressive
                continue
            
            quantity = position_size / current_price
            
            try:
                result = self.trading_service.execute_buy_order(
                    user_id=portfolio.user_id,
                    symbol=symbol,
                    quantity=quantity,
                    price=current_price,
                    order_type="market"
                )
                
                trades.append({
                    "action": "BUY",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": current_price,
                    "total": position_size
                })
                
                available_cash -= position_size
                
            except Exception as e:
                logger.error(f"Aggressive AI trade failed for {symbol}: {e}")
        
        return trades

    def _execute_technical_strategy(self, portfolio, strategy, available_cash, current_holdings):
        """Execute technical analysis AI strategy"""
        trades = []
        
        # Technical analysis symbols (mix of different sectors)
        tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'AMD', 'INTC', 'CRM', 'ADBE']
        
        for symbol in tech_symbols[:strategy['max_trades_per_day']]:
            if len(trades) >= strategy['max_trades_per_day']:
                break
            
            # Check if we already have this stock
            existing_holding = next((h for h in current_holdings if h.asset.symbol == symbol), None)
            if existing_holding:
                continue
            
            # Get current price and technical indicators
            price_data = self.market_service.get_current_price(symbol)
            if not price_data:
                continue
            
            current_price = price_data['price']
            
            # Simple technical analysis simulation
            # In a real implementation, this would use actual technical indicators
            technical_signal = self._get_technical_signal(symbol)
            
            if technical_signal != 'BUY':
                continue
            
            # Calculate position size
            position_size = min(
                available_cash * strategy['max_position_size'],
                available_cash * 0.08  # Max 8% for technical
            )
            
            if position_size < 800:
                continue
            
            quantity = position_size / current_price
            
            try:
                result = self.trading_service.execute_buy_order(
                    user_id=portfolio.user_id,
                    symbol=symbol,
                    quantity=quantity,
                    price=current_price,
                    order_type="market"
                )
                
                trades.append({
                    "action": "BUY",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": current_price,
                    "total": position_size,
                    "signal": technical_signal
                })
                
                available_cash -= position_size
                
            except Exception as e:
                logger.error(f"Technical AI trade failed for {symbol}: {e}")
        
        return trades

    def _execute_sentiment_strategy(self, portfolio, strategy, available_cash, current_holdings):
        """Execute sentiment analysis AI strategy"""
        trades = []
        
        # Sentiment-driven symbols (popular stocks with high social media presence)
        sentiment_symbols = ['TSLA', 'AAPL', 'GME', 'AMC', 'BB', 'NOK', 'PLTR', 'ROKU', 'ZM', 'PTON']
        
        for symbol in sentiment_symbols[:strategy['max_trades_per_day']]:
            if len(trades) >= strategy['max_trades_per_day']:
                break
            
            # Check if we already have this stock
            existing_holding = next((h for h in current_holdings if h.asset.symbol == symbol), None)
            if existing_holding:
                continue
            
            # Get current price
            price_data = self.market_service.get_current_price(symbol)
            if not price_data:
                continue
            
            current_price = price_data['price']
            
            # Simple sentiment analysis simulation
            # In a real implementation, this would analyze news and social media
            sentiment_score = self._get_sentiment_score(symbol)
            
            if sentiment_score < 0.6:  # Only buy if sentiment is positive
                continue
            
            # Calculate position size
            position_size = min(
                available_cash * strategy['max_position_size'],
                available_cash * 0.06  # Max 6% for sentiment
            )
            
            if position_size < 700:
                continue
            
            quantity = position_size / current_price
            
            try:
                result = self.trading_service.execute_buy_order(
                    user_id=portfolio.user_id,
                    symbol=symbol,
                    quantity=quantity,
                    price=current_price,
                    order_type="market"
                )
                
                trades.append({
                    "action": "BUY",
                    "symbol": symbol,
                    "quantity": quantity,
                    "price": current_price,
                    "total": position_size,
                    "sentiment_score": sentiment_score
                })
                
                available_cash -= position_size
                
            except Exception as e:
                logger.error(f"Sentiment AI trade failed for {symbol}: {e}")
        
        return trades

    def _get_technical_signal(self, symbol: str) -> str:
        """Get technical analysis signal for a symbol"""
        # Simplified technical analysis simulation
        # In reality, this would use RSI, MACD, moving averages, etc.
        signals = ['BUY', 'SELL', 'HOLD']
        weights = [0.4, 0.2, 0.4]  # Slightly biased toward BUY/HOLD
        return np.random.choice(signals, p=weights)

    def _get_sentiment_score(self, symbol: str) -> float:
        """Get sentiment score for a symbol"""
        # Simplified sentiment analysis simulation
        # In reality, this would analyze news articles, social media, etc.
        return random.uniform(0.3, 0.9)  # Random sentiment between 0.3 and 0.9

    def _update_ai_portfolio_value(self, portfolio):
        """Update AI portfolio total value"""
        holdings = self.db.query(models.Holding).filter(
            models.Holding.portfolio_id == portfolio.id
        ).all()
        
        total_value = portfolio.cash_balance
        
        for holding in holdings:
            # Get current price
            price_data = self.market_service.get_current_price(holding.asset.symbol)
            if price_data:
                current_price = price_data['price']
                total_value += holding.quantity * current_price
        
        portfolio.total_value = total_value
        self.db.commit()

    def get_competition_data(self, user_id: str) -> Dict:
        """Get comparison data between user and AI opponent"""
        ai_opponent = self.db.query(models.AIOpponent).filter(
            and_(
                models.AIOpponent.user_id == user_id,
                models.AIOpponent.is_active == True
            )
        ).first()
        
        if not ai_opponent:
            return {"error": "No active AI opponent found"}
        
        # Get user portfolio
        user_portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        # Get AI portfolio
        ai_portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == ai_opponent.ai_user_id
        ).first()
        
        if not user_portfolio or not ai_portfolio:
            return {"error": "Portfolio not found"}
        
        # Calculate performance metrics
        initial_balance = 100000.0
        
        user_return = ((user_portfolio.total_value - initial_balance) / initial_balance) * 100
        ai_return = ((ai_portfolio.total_value - initial_balance) / initial_balance) * 100
        
        return {
            "user_performance": {
                "total_value": user_portfolio.total_value,
                "cash_balance": user_portfolio.cash_balance,
                "return_percentage": user_return,
                "return_amount": user_portfolio.total_value - initial_balance
            },
            "ai_performance": {
                "total_value": ai_portfolio.total_value,
                "cash_balance": ai_portfolio.cash_balance,
                "return_percentage": ai_return,
                "return_amount": ai_portfolio.total_value - initial_balance,
                "strategy": self.strategies[ai_opponent.strategy_type]['name']
            },
            "competition": {
                "leader": "user" if user_return > ai_return else "ai",
                "difference_percentage": abs(user_return - ai_return),
                "difference_amount": abs(user_portfolio.total_value - ai_portfolio.total_value)
            },
            "ai_opponent_id": ai_opponent.id
        }

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
from app.db import models, schemas
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PortfolioService:
    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(self, user_id: str) -> models.Portfolio:
        """Create a new portfolio for a user"""
        # Check if portfolio already exists
        existing = self.get_portfolio_by_user_id(user_id)
        if existing:
            return existing
        
        portfolio = models.Portfolio(
            user_id=user_id,
            cash_balance=100000.0,
            total_value=100000.0
        )
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_portfolio_by_user_id(self, user_id: str) -> Optional[models.Portfolio]:
        """Get portfolio by user ID"""
        return self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()

    def get_holdings(self, portfolio_id: int) -> List[models.Holding]:
        """Get all holdings for a portfolio"""
        return self.db.query(models.Holding).options(
            joinedload(models.Holding.asset)
        ).filter(
            models.Holding.portfolio_id == portfolio_id
        ).all()

    def get_transactions(self, portfolio_id: int, limit: int = 50) -> List[models.Transaction]:
        """Get transaction history for a portfolio"""
        return self.db.query(models.Transaction).options(
            joinedload(models.Transaction.asset)
        ).filter(
            models.Transaction.portfolio_id == portfolio_id
        ).order_by(desc(models.Transaction.timestamp)).limit(limit).all()

    def reset_portfolio(self, portfolio_id: int) -> dict:
        """Reset portfolio to initial state"""
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.id == portfolio_id
        ).first()
        
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        # Delete all holdings and transactions
        self.db.query(models.Holding).filter(
            models.Holding.portfolio_id == portfolio_id
        ).delete()
        
        self.db.query(models.Transaction).filter(
            models.Transaction.portfolio_id == portfolio_id
        ).delete()
        
        # Reset portfolio values
        portfolio.cash_balance = 100000.0
        portfolio.total_value = 100000.0
        
        self.db.commit()
        return {"message": "Portfolio reset successfully"}

    def get_performance_metrics(self, portfolio_id: int, days: int = 30) -> dict:
        """Get portfolio performance metrics"""
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.id == portfolio_id
        ).first()
        
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        # Get analytics data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        analytics = self.db.query(models.Analytics).filter(
            and_(
                models.Analytics.portfolio_id == portfolio_id,
                models.Analytics.date >= start_date,
                models.Analytics.date <= end_date
            )
        ).order_by(models.Analytics.date).all()
        
        if not analytics:
            return {
                "total_value": portfolio.total_value,
                "cash_balance": portfolio.cash_balance,
                "total_return": 0.0,
                "daily_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "volatility": 0.0
            }
        
        latest = analytics[-1]
        earliest = analytics[0]
        
        total_return = (latest.total_value - earliest.total_value) / earliest.total_value * 100
        
        daily_returns = [a.daily_return for a in analytics if a.daily_return is not None]
        avg_daily_return = sum(daily_returns) / len(daily_returns) if daily_returns else 0
        
        return {
            "total_value": portfolio.total_value,
            "cash_balance": portfolio.cash_balance,
            "total_return": total_return,
            "daily_return": avg_daily_return,
            "sharpe_ratio": latest.sharpe_ratio or 0,
            "max_drawdown": latest.max_drawdown or 0,
            "volatility": latest.volatility or 0,
            "period_days": days
        }

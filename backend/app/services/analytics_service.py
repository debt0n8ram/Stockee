from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.db import models, schemas
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging
import numpy as np

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_performance_analytics(self, user_id: str, days: int = 30) -> Dict:
        """Get comprehensive performance analytics"""
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            return {"error": "Portfolio not found"}
        
        # Get analytics data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        analytics = self.db.query(models.Analytics).filter(
            and_(
                models.Analytics.portfolio_id == portfolio.id,
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
                "volatility": 0.0,
                "period_days": days
            }
        
        # Calculate metrics
        values = [a.total_value for a in analytics]
        returns = [a.daily_return for a in analytics if a.daily_return is not None]
        
        total_return = (values[-1] - values[0]) / values[0] * 100 if values else 0
        avg_daily_return = np.mean(returns) if returns else 0
        volatility = np.std(returns) * np.sqrt(252) if returns else 0  # Annualized
        sharpe_ratio = (avg_daily_return * 252) / (volatility * np.sqrt(252)) if volatility > 0 else 0
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown(values)
        
        return {
            "total_value": portfolio.total_value,
            "cash_balance": portfolio.cash_balance,
            "total_return": round(total_return, 2),
            "daily_return": round(avg_daily_return, 4),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown, 2),
            "volatility": round(volatility, 2),
            "period_days": days,
            "data_points": len(analytics)
        }

    def get_risk_metrics(self, user_id: str, days: int = 30) -> Dict:
        """Get risk analysis metrics"""
        performance = self.get_performance_analytics(user_id, days)
        
        # Risk assessment based on metrics
        risk_score = 0
        if performance.get("volatility", 0) > 0.2:
            risk_score += 3
        elif performance.get("volatility", 0) > 0.15:
            risk_score += 2
        elif performance.get("volatility", 0) > 0.1:
            risk_score += 1
        
        if performance.get("max_drawdown", 0) > 0.15:
            risk_score += 3
        elif performance.get("max_drawdown", 0) > 0.1:
            risk_score += 2
        elif performance.get("max_drawdown", 0) > 0.05:
            risk_score += 1
        
        risk_level = "low" if risk_score <= 2 else "medium" if risk_score <= 4 else "high"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "volatility": performance.get("volatility", 0),
            "max_drawdown": performance.get("max_drawdown", 0),
            "sharpe_ratio": performance.get("sharpe_ratio", 0),
            "var_95": self._calculate_var(performance.get("daily_return", 0), performance.get("volatility", 0))
        }

    def get_benchmark_comparison(self, user_id: str, benchmark: str = "SPY", days: int = 30) -> Dict:
        """Compare portfolio performance against benchmark"""
        portfolio_performance = self.get_performance_analytics(user_id, days)
        
        # Mock benchmark data (in production, fetch real benchmark data)
        benchmark_return = 0.05  # 5% return for SPY
        benchmark_volatility = 0.15
        benchmark_sharpe = benchmark_return / benchmark_volatility
        
        portfolio_return = portfolio_performance.get("total_return", 0) / 100
        portfolio_volatility = portfolio_performance.get("volatility", 0)
        portfolio_sharpe = portfolio_performance.get("sharpe_ratio", 0)
        
        return {
            "portfolio": {
                "return": portfolio_return,
                "volatility": portfolio_volatility,
                "sharpe_ratio": portfolio_sharpe
            },
            "benchmark": {
                "symbol": benchmark,
                "return": benchmark_return,
                "volatility": benchmark_volatility,
                "sharpe_ratio": benchmark_sharpe
            },
            "comparison": {
                "excess_return": portfolio_return - benchmark_return,
                "relative_volatility": portfolio_volatility / benchmark_volatility if benchmark_volatility > 0 else 0,
                "sharpe_difference": portfolio_sharpe - benchmark_sharpe
            }
        }

    def get_portfolio_allocation(self, user_id: str) -> Dict:
        """Get portfolio allocation breakdown"""
        portfolio = self.db.query(models.Portfolio).filter(
            models.Portfolio.user_id == user_id
        ).first()
        
        if not portfolio:
            return {"error": "Portfolio not found"}
        
        holdings = self.db.query(models.Holding).filter(
            models.Holding.portfolio_id == portfolio.id
        ).all()
        
        total_value = portfolio.total_value
        cash_percentage = (portfolio.cash_balance / total_value) * 100 if total_value > 0 else 100
        
        allocation = {
            "cash": {
                "value": portfolio.cash_balance,
                "percentage": round(cash_percentage, 2)
            },
            "stocks": [],
            "crypto": [],
            "other": []
        }
        
        for holding in holdings:
            asset = self.db.query(models.Asset).filter(models.Asset.id == holding.asset_id).first()
            if asset:
                value = holding.current_value or (holding.quantity * holding.average_cost)
                percentage = (value / total_value) * 100 if total_value > 0 else 0
                
                holding_data = {
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "value": value,
                    "percentage": round(percentage, 2),
                    "quantity": holding.quantity
                }
                
                if asset.asset_type == "stock":
                    allocation["stocks"].append(holding_data)
                elif asset.asset_type == "crypto":
                    allocation["crypto"].append(holding_data)
                else:
                    allocation["other"].append(holding_data)
        
        return allocation

    def get_correlation_analysis(self, user_id: str, days: int = 30) -> Dict:
        """Get correlation analysis between holdings"""
        # Placeholder implementation
        return {
            "message": "Correlation analysis not yet implemented",
            "correlations": []
        }

    def get_performance_heatmap(self, user_id: str, days: int = 30) -> Dict:
        """Get performance heatmap data"""
        # Placeholder implementation
        return {
            "message": "Performance heatmap not yet implemented",
            "data": []
        }

    def _calculate_max_drawdown(self, values: List[float]) -> float:
        """Calculate maximum drawdown from peak"""
        if not values:
            return 0
        
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd

    def _calculate_var(self, mean_return: float, volatility: float, confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        # Simple VaR calculation (normal distribution assumption)
        z_score = 1.645 if confidence == 0.95 else 2.326  # 95% or 99%
        return mean_return - z_score * volatility

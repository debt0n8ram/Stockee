import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import minimize
import json

from app.db import models
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

class AdvancedAnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
    
    def calculate_portfolio_metrics(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate comprehensive portfolio performance metrics."""
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)
            
            # Get portfolio data
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            # Get holdings and transactions
            holdings = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio.id
            ).all()
            
            transactions = self.db.query(models.Transaction).filter(
                models.Transaction.portfolio_id == portfolio.id,
                models.Transaction.timestamp >= start_date,
                models.Transaction.timestamp <= end_date
            ).all()
            
            # Calculate basic metrics
            total_value = portfolio.cash_balance
            total_cost = 0
            daily_returns = []
            
            for holding in holdings:
                # Get current price
                current_price = self.market_data_service.get_current_price(holding.symbol)
                if current_price:
                    holding_value = holding.quantity * current_price
                    total_value += holding_value
                    total_cost += holding.quantity * holding.average_price
                    
                    # Calculate daily returns
                    price_data = self.market_data_service.get_historical_data(
                        holding.symbol, start_date, end_date
                    )
                    if price_data:
                        returns = price_data['close'].pct_change().dropna()
                        daily_returns.extend(returns.tolist())
            
            # Calculate performance metrics
            total_return = (total_value - total_cost) / total_cost if total_cost > 0 else 0
            annualized_return = (1 + total_return) ** (365 / (end_date - start_date).days) - 1
            
            # Risk metrics
            if daily_returns:
                daily_returns_array = np.array(daily_returns)
                volatility = np.std(daily_returns_array) * np.sqrt(252)
                sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
                
                # Calculate maximum drawdown
                cumulative_returns = np.cumprod(1 + daily_returns_array)
                running_max = np.maximum.accumulate(cumulative_returns)
                drawdown = (cumulative_returns - running_max) / running_max
                max_drawdown = np.min(drawdown)
                
                # Value at Risk (VaR)
                var_95 = np.percentile(daily_returns_array, 5)
                var_99 = np.percentile(daily_returns_array, 1)
                
                # Conditional Value at Risk (CVaR)
                cvar_95 = np.mean(daily_returns_array[daily_returns_array <= var_95])
                cvar_99 = np.mean(daily_returns_array[daily_returns_array <= var_99])
            else:
                volatility = 0
                sharpe_ratio = 0
                max_drawdown = 0
                var_95 = 0
                var_99 = 0
                cvar_95 = 0
                cvar_99 = 0
            
            # Beta calculation (vs S&P 500)
            beta = self._calculate_beta(user_id, start_date, end_date)
            
            # Alpha calculation
            risk_free_rate = 0.02  # Assume 2% risk-free rate
            market_return = 0.10   # Assume 10% market return
            alpha = annualized_return - (risk_free_rate + beta * (market_return - risk_free_rate))
            
            # Information ratio
            benchmark_returns = self._get_benchmark_returns(start_date, end_date)
            if benchmark_returns and daily_returns:
                excess_returns = np.array(daily_returns) - np.array(benchmark_returns)
                tracking_error = np.std(excess_returns) * np.sqrt(252)
                information_ratio = np.mean(excess_returns) * 252 / tracking_error if tracking_error > 0 else 0
            else:
                information_ratio = 0
            
            # Calmar ratio
            calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            # Sortino ratio
            if daily_returns:
                negative_returns = np.array(daily_returns)[np.array(daily_returns) < 0]
                downside_deviation = np.std(negative_returns) * np.sqrt(252) if len(negative_returns) > 0 else 0
                sortino_ratio = annualized_return / downside_deviation if downside_deviation > 0 else 0
            else:
                sortino_ratio = 0
            
            return {
                "total_value": float(total_value),
                "total_cost": float(total_cost),
                "total_return": float(total_return),
                "annualized_return": float(annualized_return),
                "volatility": float(volatility),
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "var_95": float(var_95),
                "var_99": float(var_99),
                "cvar_95": float(cvar_95),
                "cvar_99": float(cvar_99),
                "beta": float(beta),
                "alpha": float(alpha),
                "information_ratio": float(information_ratio),
                "calmar_ratio": float(calmar_ratio),
                "sortino_ratio": float(sortino_ratio),
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {"error": str(e)}
    
    def optimize_portfolio(self, user_id: str, target_return: Optional[float] = None, risk_tolerance: float = 0.5) -> Dict[str, Any]:
        """Optimize portfolio allocation using Modern Portfolio Theory."""
        try:
            # Get current holdings
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            holdings = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio.id
            ).all()
            
            if not holdings:
                return {"error": "No holdings found"}
            
            # Get historical data for all holdings
            symbols = [holding.symbol for holding in holdings]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=252)  # 1 year of data
            
            returns_data = {}
            for symbol in symbols:
                price_data = self.market_data_service.get_historical_data(symbol, start_date, end_date)
                if price_data is not None and not price_data.empty:
                    returns = price_data['close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if not returns_data:
                return {"error": "Insufficient historical data"}
            
            # Create returns matrix
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            if returns_df.empty:
                return {"error": "No valid returns data"}
            
            # Calculate expected returns and covariance matrix
            expected_returns = returns_df.mean() * 252  # Annualized
            cov_matrix = returns_df.cov() * 252  # Annualized
            
            # Portfolio optimization
            num_assets = len(symbols)
            
            # Objective function (negative Sharpe ratio for minimization)
            def objective(weights):
                portfolio_return = np.sum(weights * expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
                return -sharpe_ratio
            
            # Constraints
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # Weights sum to 1
            
            # Bounds (no short selling)
            bounds = tuple((0, 1) for _ in range(num_assets))
            
            # Initial guess (equal weights)
            initial_weights = np.array([1/num_assets] * num_assets)
            
            # Optimize
            result = minimize(objective, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if not result.success:
                return {"error": "Optimization failed"}
            
            optimal_weights = result.x
            
            # Calculate optimal portfolio metrics
            optimal_return = np.sum(optimal_weights * expected_returns)
            optimal_volatility = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
            optimal_sharpe = optimal_return / optimal_volatility if optimal_volatility > 0 else 0
            
            # Current portfolio weights
            current_weights = {}
            total_value = portfolio.cash_balance
            for holding in holdings:
                current_price = self.market_data_service.get_current_price(holding.symbol)
                if current_price:
                    holding_value = holding.quantity * current_price
                    total_value += holding_value
                    current_weights[holding.symbol] = holding_value
            
            # Normalize current weights
            if total_value > 0:
                for symbol in current_weights:
                    current_weights[symbol] /= total_value
            
            # Add cash weight
            current_weights['CASH'] = portfolio.cash_balance / total_value if total_value > 0 else 1
            
            # Create recommendations
            recommendations = []
            for i, symbol in enumerate(symbols):
                current_weight = current_weights.get(symbol, 0)
                optimal_weight = optimal_weights[i]
                difference = optimal_weight - current_weight
                
                recommendations.append({
                    "symbol": symbol,
                    "current_weight": float(current_weight),
                    "optimal_weight": float(optimal_weight),
                    "difference": float(difference),
                    "action": "buy" if difference > 0.01 else "sell" if difference < -0.01 else "hold"
                })
            
            return {
                "current_weights": current_weights,
                "optimal_weights": {symbols[i]: float(optimal_weights[i]) for i in range(len(symbols))},
                "recommendations": recommendations,
                "optimal_return": float(optimal_return),
                "optimal_volatility": float(optimal_volatility),
                "optimal_sharpe": float(optimal_sharpe),
                "expected_returns": {symbol: float(expected_returns[symbol]) for symbol in symbols},
                "covariance_matrix": cov_matrix.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            return {"error": str(e)}
    
    def calculate_sector_allocation(self, user_id: str) -> Dict[str, Any]:
        """Calculate sector allocation and performance."""
        try:
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            holdings = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio.id
            ).all()
            
            sector_allocation = {}
            sector_performance = {}
            
            for holding in holdings:
                # Get sector information (this would come from a sector mapping service)
                sector = self._get_sector_for_symbol(holding.symbol)
                if not sector:
                    sector = "Unknown"
                
                current_price = self.market_data_service.get_current_price(holding.symbol)
                if current_price:
                    holding_value = holding.quantity * current_price
                    
                    if sector not in sector_allocation:
                        sector_allocation[sector] = 0
                        sector_performance[sector] = []
                    
                    sector_allocation[sector] += holding_value
                    
                    # Calculate performance
                    performance = (current_price - holding.average_price) / holding.average_price
                    sector_performance[sector].append(performance)
            
            # Calculate total portfolio value
            total_value = sum(sector_allocation.values())
            
            # Normalize allocation
            if total_value > 0:
                for sector in sector_allocation:
                    sector_allocation[sector] /= total_value
            
            # Calculate sector performance
            for sector in sector_performance:
                if sector_performance[sector]:
                    sector_performance[sector] = np.mean(sector_performance[sector])
                else:
                    sector_performance[sector] = 0
            
            return {
                "sector_allocation": sector_allocation,
                "sector_performance": sector_performance,
                "total_value": float(total_value)
            }
            
        except Exception as e:
            logger.error(f"Error calculating sector allocation: {e}")
            return {"error": str(e)}
    
    def calculate_attribution_analysis(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate performance attribution analysis."""
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=90)  # 3 months
            
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            holdings = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio.id
            ).all()
            
            attribution = {}
            total_contribution = 0
            
            for holding in holdings:
                # Get price data
                price_data = self.market_data_service.get_historical_data(
                    holding.symbol, start_date, end_date
                )
                
                if price_data is not None and not price_data.empty:
                    start_price = price_data['close'].iloc[0]
                    end_price = price_data['close'].iloc[-1]
                    
                    # Calculate return
                    holding_return = (end_price - start_price) / start_price
                    
                    # Calculate contribution
                    current_price = self.market_data_service.get_current_price(holding.symbol)
                    if current_price:
                        holding_value = holding.quantity * current_price
                        contribution = holding_return * (holding_value / portfolio.total_value) if portfolio.total_value > 0 else 0
                        
                        attribution[holding.symbol] = {
                            "return": float(holding_return),
                            "weight": float(holding_value / portfolio.total_value) if portfolio.total_value > 0 else 0,
                            "contribution": float(contribution)
                        }
                        
                        total_contribution += contribution
            
            return {
                "attribution": attribution,
                "total_contribution": float(total_contribution),
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating attribution analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_beta(self, user_id: str, start_date: datetime, end_date: datetime) -> float:
        """Calculate portfolio beta vs S&P 500."""
        try:
            # Get portfolio returns
            portfolio_returns = self._get_portfolio_returns(user_id, start_date, end_date)
            
            # Get S&P 500 returns
            spy_returns = self._get_benchmark_returns(start_date, end_date, "SPY")
            
            if portfolio_returns and spy_returns and len(portfolio_returns) == len(spy_returns):
                # Calculate beta using linear regression
                slope, intercept, r_value, p_value, std_err = stats.linregress(spy_returns, portfolio_returns)
                return float(slope)
            
            return 1.0  # Default beta
            
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return 1.0
    
    def _get_portfolio_returns(self, user_id: str, start_date: datetime, end_date: datetime) -> List[float]:
        """Get portfolio daily returns."""
        try:
            # This would calculate daily portfolio returns
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting portfolio returns: {e}")
            return []
    
    def _get_benchmark_returns(self, start_date: datetime, end_date: datetime, symbol: str = "SPY") -> List[float]:
        """Get benchmark returns."""
        try:
            price_data = self.market_data_service.get_historical_data(symbol, start_date, end_date)
            if price_data is not None and not price_data.empty:
                returns = price_data['close'].pct_change().dropna()
                return returns.tolist()
            return []
        except Exception as e:
            logger.error(f"Error getting benchmark returns: {e}")
            return []
    
    def _get_sector_for_symbol(self, symbol: str) -> Optional[str]:
        """Get sector for a given symbol."""
        # This would typically come from a sector mapping service
        # For now, return a mock sector
        sector_mapping = {
            "AAPL": "Technology",
            "MSFT": "Technology",
            "GOOGL": "Technology",
            "AMZN": "Consumer Discretionary",
            "TSLA": "Consumer Discretionary",
            "JPM": "Financials",
            "JNJ": "Healthcare",
            "PG": "Consumer Staples",
            "XOM": "Energy",
            "WMT": "Consumer Staples"
        }
        return sector_mapping.get(symbol, "Unknown")

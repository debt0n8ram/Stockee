import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import minimize
import json
from dataclasses import dataclass

from app.db import models
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

@dataclass
class RiskMetrics:
    """Risk metrics data class"""
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    beta: float
    alpha: float
    information_ratio: float
    calmar_ratio: float
    treynor_ratio: float

@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    total_return: float
    annualized_return: float
    cumulative_return: float
    excess_return: float
    win_rate: float
    profit_factor: float
    recovery_factor: float
    sterling_ratio: float
    burke_ratio: float
    kappa_ratio: float

class EnhancedAnalyticsService:
    """Enhanced analytics service with advanced risk management and performance metrics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.risk_free_rate = 0.02  # 2% risk-free rate
    
    def get_comprehensive_analytics(self, user_id: str, start_date: Optional[datetime] = None, 
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive portfolio analytics"""
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=365)
            
            # Get portfolio data
            portfolio_data = self._get_portfolio_data(user_id, start_date, end_date)
            if "error" in portfolio_data:
                return portfolio_data
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(portfolio_data)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(portfolio_data)
            
            # Calculate attribution analysis
            attribution = self._calculate_attribution_analysis(portfolio_data)
            
            # Calculate correlation analysis
            correlation = self._calculate_correlation_analysis(portfolio_data)
            
            # Calculate portfolio optimization
            optimization = self._calculate_portfolio_optimization(portfolio_data)
            
            # Calculate scenario analysis
            scenarios = self._calculate_scenario_analysis(portfolio_data)
            
            # Calculate stress testing
            stress_test = self._calculate_stress_testing(portfolio_data)
            
            return {
                "user_id": user_id,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date - start_date).days
                },
                "performance_metrics": performance_metrics,
                "risk_metrics": risk_metrics,
                "attribution_analysis": attribution,
                "correlation_analysis": correlation,
                "portfolio_optimization": optimization,
                "scenario_analysis": scenarios,
                "stress_testing": stress_test,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive analytics: {e}")
            return {"error": f"Failed to get analytics: {str(e)}"}
    
    def _get_portfolio_data(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get comprehensive portfolio data"""
        try:
            # Get portfolio
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            # Get holdings
            holdings = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio.id
            ).all()
            
            # Get transactions
            transactions = self.db.query(models.Transaction).filter(
                models.Transaction.portfolio_id == portfolio.id,
                models.Transaction.timestamp >= start_date,
                models.Transaction.timestamp <= end_date
            ).all()
            
            # Get benchmark data (S&P 500)
            benchmark_data = self._get_benchmark_data(start_date, end_date)
            
            # Calculate portfolio values over time
            portfolio_values = self._calculate_portfolio_values(holdings, start_date, end_date)
            
            # Calculate individual asset returns
            asset_returns = self._calculate_asset_returns(holdings, start_date, end_date)
            
            return {
                "portfolio": portfolio,
                "holdings": holdings,
                "transactions": transactions,
                "benchmark_data": benchmark_data,
                "portfolio_values": portfolio_values,
                "asset_returns": asset_returns,
                "start_date": start_date,
                "end_date": end_date
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio data: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_metrics(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            portfolio_values = portfolio_data["portfolio_values"]
            benchmark_data = portfolio_data["benchmark_data"]
            
            if not portfolio_values or len(portfolio_values) < 2:
                return {"error": "Insufficient data for performance calculation"}
            
            # Convert to pandas Series
            portfolio_series = pd.Series(portfolio_values)
            benchmark_series = pd.Series(benchmark_data)
            
            # Calculate returns
            portfolio_returns = portfolio_series.pct_change().dropna()
            benchmark_returns = benchmark_series.pct_change().dropna()
            
            # Align dates
            common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
            portfolio_returns = portfolio_returns.loc[common_dates]
            benchmark_returns = benchmark_returns.loc[common_dates]
            
            # Basic performance metrics
            total_return = (portfolio_series.iloc[-1] / portfolio_series.iloc[0]) - 1
            annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
            cumulative_return = total_return
            
            # Excess return
            excess_return = annualized_return - self.risk_free_rate
            
            # Win rate
            win_rate = (portfolio_returns > 0).mean()
            
            # Profit factor
            positive_returns = portfolio_returns[portfolio_returns > 0].sum()
            negative_returns = abs(portfolio_returns[portfolio_returns < 0].sum())
            profit_factor = positive_returns / negative_returns if negative_returns > 0 else float('inf')
            
            # Recovery factor
            max_drawdown = self._calculate_max_drawdown(portfolio_returns)
            recovery_factor = annualized_return / abs(max_drawdown) if max_drawdown < 0 else float('inf')
            
            # Sterling ratio
            sterling_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else float('inf')
            
            # Burke ratio
            burke_ratio = annualized_return / np.sqrt(sum([dd**2 for dd in self._calculate_drawdowns(portfolio_returns)]))
            
            # Kappa ratio (3rd moment)
            kappa_ratio = annualized_return / (np.std(portfolio_returns) * (1 + stats.skew(portfolio_returns)))
            
            return {
                "total_return": round(total_return * 100, 2),
                "annualized_return": round(annualized_return * 100, 2),
                "cumulative_return": round(cumulative_return * 100, 2),
                "excess_return": round(excess_return * 100, 2),
                "win_rate": round(win_rate * 100, 2),
                "profit_factor": round(profit_factor, 2),
                "recovery_factor": round(recovery_factor, 2),
                "sterling_ratio": round(sterling_ratio, 2),
                "burke_ratio": round(burke_ratio, 2),
                "kappa_ratio": round(kappa_ratio, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_risk_metrics(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics"""
        try:
            portfolio_values = portfolio_data["portfolio_values"]
            benchmark_data = portfolio_data["benchmark_data"]
            
            if not portfolio_values or len(portfolio_values) < 2:
                return {"error": "Insufficient data for risk calculation"}
            
            # Convert to pandas Series
            portfolio_series = pd.Series(portfolio_values)
            benchmark_series = pd.Series(benchmark_data)
            
            # Calculate returns
            portfolio_returns = portfolio_series.pct_change().dropna()
            benchmark_returns = benchmark_series.pct_change().dropna()
            
            # Align dates
            common_dates = portfolio_returns.index.intersection(benchmark_returns.index)
            portfolio_returns = portfolio_returns.loc[common_dates]
            benchmark_returns = benchmark_returns.loc[common_dates]
            
            # Volatility
            volatility = portfolio_returns.std() * np.sqrt(252)
            
            # Sharpe ratio
            excess_returns = portfolio_returns - self.risk_free_rate / 252
            sharpe_ratio = excess_returns.mean() / portfolio_returns.std() * np.sqrt(252)
            
            # Sortino ratio
            downside_returns = portfolio_returns[portfolio_returns < 0]
            downside_volatility = downside_returns.std() * np.sqrt(252)
            sortino_ratio = excess_returns.mean() / downside_volatility * np.sqrt(252) if downside_volatility > 0 else 0
            
            # Maximum drawdown
            max_drawdown = self._calculate_max_drawdown(portfolio_returns)
            
            # Value at Risk (VaR)
            var_95 = np.percentile(portfolio_returns, 5)
            var_99 = np.percentile(portfolio_returns, 1)
            
            # Conditional Value at Risk (CVaR)
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
            cvar_99 = portfolio_returns[portfolio_returns <= var_99].mean()
            
            # Beta
            if len(portfolio_returns) > 1 and len(benchmark_returns) > 1:
                covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
                benchmark_variance = np.var(benchmark_returns)
                beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            else:
                beta = 0
            
            # Alpha
            alpha = portfolio_returns.mean() - (self.risk_free_rate / 252 + beta * (benchmark_returns.mean() - self.risk_free_rate / 252))
            alpha = alpha * 252  # Annualize
            
            # Information ratio
            active_returns = portfolio_returns - benchmark_returns
            tracking_error = active_returns.std() * np.sqrt(252)
            information_ratio = active_returns.mean() / tracking_error * np.sqrt(252) if tracking_error > 0 else 0
            
            # Calmar ratio
            annualized_return = (1 + portfolio_returns.mean()) ** 252 - 1
            calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown < 0 else float('inf')
            
            # Treynor ratio
            treynor_ratio = (annualized_return - self.risk_free_rate) / beta if beta != 0 else 0
            
            return {
                "volatility": round(volatility * 100, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "sortino_ratio": round(sortino_ratio, 2),
                "max_drawdown": round(max_drawdown * 100, 2),
                "var_95": round(var_95 * 100, 2),
                "var_99": round(var_99 * 100, 2),
                "cvar_95": round(cvar_95 * 100, 2),
                "cvar_99": round(cvar_99 * 100, 2),
                "beta": round(beta, 2),
                "alpha": round(alpha * 100, 2),
                "information_ratio": round(information_ratio, 2),
                "calmar_ratio": round(calmar_ratio, 2),
                "treynor_ratio": round(treynor_ratio, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_attribution_analysis(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance attribution analysis"""
        try:
            holdings = portfolio_data["holdings"]
            asset_returns = portfolio_data["asset_returns"]
            portfolio_values = portfolio_data["portfolio_values"]
            
            if not holdings or not asset_returns:
                return {"error": "Insufficient data for attribution analysis"}
            
            # Calculate portfolio return
            portfolio_return = (portfolio_values[-1] / portfolio_values[0]) - 1 if len(portfolio_values) > 1 else 0
            
            # Calculate individual asset contributions
            asset_contributions = []
            total_contribution = 0
            
            for holding in holdings:
                if holding.symbol in asset_returns:
                    asset_return = asset_returns[holding.symbol]
                    asset_weight = (holding.quantity * holding.average_price) / portfolio_values[0] if portfolio_values[0] > 0 else 0
                    contribution = asset_weight * asset_return
                    
                    asset_contributions.append({
                        "symbol": holding.symbol,
                        "weight": round(asset_weight * 100, 2),
                        "return": round(asset_return * 100, 2),
                        "contribution": round(contribution * 100, 2)
                    })
                    
                    total_contribution += contribution
            
            # Calculate selection effect and allocation effect
            selection_effect = 0
            allocation_effect = 0
            
            # This is a simplified calculation - in practice, you'd compare against a benchmark
            for contribution in asset_contributions:
                selection_effect += contribution["contribution"] * 0.1  # Simplified
                allocation_effect += contribution["contribution"] * 0.05  # Simplified
            
            return {
                "total_portfolio_return": round(portfolio_return * 100, 2),
                "total_contribution": round(total_contribution * 100, 2),
                "asset_contributions": asset_contributions,
                "selection_effect": round(selection_effect, 2),
                "allocation_effect": round(allocation_effect, 2),
                "interaction_effect": round(portfolio_return * 100 - total_contribution * 100 - selection_effect - allocation_effect, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating attribution analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_correlation_analysis(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate correlation analysis between assets"""
        try:
            asset_returns = portfolio_data["asset_returns"]
            
            if not asset_returns or len(asset_returns) < 2:
                return {"error": "Insufficient data for correlation analysis"}
            
            # Create correlation matrix
            returns_df = pd.DataFrame(asset_returns)
            correlation_matrix = returns_df.corr()
            
            # Calculate average correlation
            # Exclude diagonal (self-correlation)
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
            correlations = correlation_matrix.values[mask]
            avg_correlation = np.mean(correlations) if len(correlations) > 0 else 0
            
            # Find highest and lowest correlations
            max_correlation = np.max(correlations) if len(correlations) > 0 else 0
            min_correlation = np.min(correlations) if len(correlations) > 0 else 0
            
            # Calculate diversification ratio
            portfolio_volatility = np.sqrt(np.mean([np.var(returns) for returns in asset_returns.values()]))
            weighted_avg_volatility = np.mean([np.std(returns) for returns in asset_returns.values()])
            diversification_ratio = weighted_avg_volatility / portfolio_volatility if portfolio_volatility > 0 else 1
            
            return {
                "correlation_matrix": correlation_matrix.to_dict(),
                "average_correlation": round(avg_correlation, 3),
                "max_correlation": round(max_correlation, 3),
                "min_correlation": round(min_correlation, 3),
                "diversification_ratio": round(diversification_ratio, 3),
                "assets": list(asset_returns.keys())
            }
            
        except Exception as e:
            logger.error(f"Error calculating correlation analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_portfolio_optimization(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio optimization using Modern Portfolio Theory"""
        try:
            asset_returns = portfolio_data["asset_returns"]
            holdings = portfolio_data["holdings"]
            
            if not asset_returns or len(asset_returns) < 2:
                return {"error": "Insufficient data for portfolio optimization"}
            
            # Prepare data
            returns_df = pd.DataFrame(asset_returns)
            expected_returns = returns_df.mean() * 252  # Annualize
            cov_matrix = returns_df.cov() * 252  # Annualize
            
            # Current portfolio weights
            current_weights = []
            total_value = sum(holding.quantity * holding.average_price for holding in holdings)
            
            for holding in holdings:
                if holding.symbol in expected_returns.index:
                    weight = (holding.quantity * holding.average_price) / total_value if total_value > 0 else 0
                    current_weights.append(weight)
                else:
                    current_weights.append(0)
            
            # Ensure weights sum to 1
            if sum(current_weights) > 0:
                current_weights = [w / sum(current_weights) for w in current_weights]
            
            # Calculate current portfolio metrics
            current_return = np.dot(current_weights, expected_returns)
            current_volatility = np.sqrt(np.dot(current_weights, np.dot(cov_matrix, current_weights)))
            current_sharpe = (current_return - self.risk_free_rate) / current_volatility if current_volatility > 0 else 0
            
            # Optimize portfolio
            num_assets = len(expected_returns)
            
            # Constraints: weights sum to 1
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            
            # Bounds: weights between 0 and 1
            bounds = tuple((0, 1) for _ in range(num_assets))
            
            # Initial guess
            initial_guess = [1/num_assets] * num_assets
            
            # Maximize Sharpe ratio
            def negative_sharpe(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
                return -(portfolio_return - self.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
            
            # Optimize
            result = minimize(negative_sharpe, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                optimal_weights = result.x
                optimal_return = np.dot(optimal_weights, expected_returns)
                optimal_volatility = np.sqrt(np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights)))
                optimal_sharpe = (optimal_return - self.risk_free_rate) / optimal_volatility if optimal_volatility > 0 else 0
                
                # Create weight recommendations
                weight_recommendations = []
                for i, symbol in enumerate(expected_returns.index):
                    current_weight = current_weights[i] if i < len(current_weights) else 0
                    optimal_weight = optimal_weights[i]
                    change = optimal_weight - current_weight
                    
                    weight_recommendations.append({
                        "symbol": symbol,
                        "current_weight": round(current_weight * 100, 2),
                        "optimal_weight": round(optimal_weight * 100, 2),
                        "recommended_change": round(change * 100, 2),
                        "action": "increase" if change > 0.01 else "decrease" if change < -0.01 else "hold"
                    })
                
                return {
                    "current_portfolio": {
                        "return": round(current_return * 100, 2),
                        "volatility": round(current_volatility * 100, 2),
                        "sharpe_ratio": round(current_sharpe, 2)
                    },
                    "optimal_portfolio": {
                        "return": round(optimal_return * 100, 2),
                        "volatility": round(optimal_volatility * 100, 2),
                        "sharpe_ratio": round(optimal_sharpe, 2)
                    },
                    "weight_recommendations": weight_recommendations,
                    "improvement_potential": {
                        "return_improvement": round((optimal_return - current_return) * 100, 2),
                        "volatility_improvement": round((current_volatility - optimal_volatility) * 100, 2),
                        "sharpe_improvement": round(optimal_sharpe - current_sharpe, 2)
                    }
                }
            else:
                return {"error": "Portfolio optimization failed"}
                
        except Exception as e:
            logger.error(f"Error calculating portfolio optimization: {e}")
            return {"error": str(e)}
    
    def _calculate_scenario_analysis(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate scenario analysis for different market conditions"""
        try:
            holdings = portfolio_data["holdings"]
            asset_returns = portfolio_data["asset_returns"]
            
            if not holdings or not asset_returns:
                return {"error": "Insufficient data for scenario analysis"}
            
            # Define scenarios
            scenarios = {
                "bull_market": {"return_multiplier": 1.5, "volatility_multiplier": 0.8},
                "bear_market": {"return_multiplier": -1.2, "volatility_multiplier": 1.5},
                "high_volatility": {"return_multiplier": 0.5, "volatility_multiplier": 2.0},
                "low_volatility": {"return_multiplier": 0.8, "volatility_multiplier": 0.6},
                "crisis": {"return_multiplier": -2.0, "volatility_multiplier": 3.0}
            }
            
            scenario_results = {}
            
            for scenario_name, scenario_params in scenarios.items():
                scenario_return = 0
                scenario_volatility = 0
                total_value = sum(holding.quantity * holding.average_price for holding in holdings)
                
                for holding in holdings:
                    if holding.symbol in asset_returns:
                        asset_return = asset_returns[holding.symbol]
                        weight = (holding.quantity * holding.average_price) / total_value if total_value > 0 else 0
                        
                        # Apply scenario parameters
                        adjusted_return = asset_return * scenario_params["return_multiplier"]
                        adjusted_volatility = np.std(asset_returns[holding.symbol]) * scenario_params["volatility_multiplier"]
                        
                        scenario_return += weight * adjusted_return
                        scenario_volatility += (weight ** 2) * (adjusted_volatility ** 2)
                
                scenario_volatility = np.sqrt(scenario_volatility)
                scenario_sharpe = (scenario_return - self.risk_free_rate / 252) / scenario_volatility if scenario_volatility > 0 else 0
                
                scenario_results[scenario_name] = {
                    "return": round(scenario_return * 100, 2),
                    "volatility": round(scenario_volatility * 100, 2),
                    "sharpe_ratio": round(scenario_sharpe, 2),
                    "probability": self._get_scenario_probability(scenario_name)
                }
            
            return scenario_results
            
        except Exception as e:
            logger.error(f"Error calculating scenario analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_stress_testing(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate stress testing for extreme market conditions"""
        try:
            holdings = portfolio_data["holdings"]
            asset_returns = portfolio_data["asset_returns"]
            
            if not holdings or not asset_returns:
                return {"error": "Insufficient data for stress testing"}
            
            # Define stress scenarios
            stress_scenarios = {
                "market_crash_2008": {"return_shock": -0.4, "duration_days": 30},
                "dot_com_bubble": {"return_shock": -0.5, "duration_days": 60},
                "covid_19": {"return_shock": -0.3, "duration_days": 20},
                "interest_rate_shock": {"return_shock": -0.15, "duration_days": 10},
                "currency_crisis": {"return_shock": -0.25, "duration_days": 15}
            }
            
            stress_results = {}
            
            for scenario_name, scenario_params in stress_scenarios.items():
                total_loss = 0
                total_value = sum(holding.quantity * holding.average_price for holding in holdings)
                
                for holding in holdings:
                    if holding.symbol in asset_returns:
                        weight = (holding.quantity * holding.average_price) / total_value if total_value > 0 else 0
                        asset_loss = weight * scenario_params["return_shock"]
                        total_loss += asset_loss
                
                # Calculate recovery time (simplified)
                recovery_time = self._estimate_recovery_time(abs(total_loss))
                
                stress_results[scenario_name] = {
                    "total_loss": round(total_loss * 100, 2),
                    "duration_days": scenario_params["duration_days"],
                    "estimated_recovery_time": recovery_time,
                    "severity": self._classify_stress_severity(abs(total_loss))
                }
            
            return stress_results
            
        except Exception as e:
            logger.error(f"Error calculating stress testing: {e}")
            return {"error": str(e)}
    
    def _get_benchmark_data(self, start_date: datetime, end_date: datetime) -> List[float]:
        """Get benchmark data (S&P 500)"""
        try:
            # This would typically fetch from a market data service
            # For now, return mock data
            days = (end_date - start_date).days
            return [100 * (1 + np.random.normal(0.0005, 0.02)) ** i for i in range(days)]
        except Exception as e:
            logger.error(f"Error getting benchmark data: {e}")
            return []
    
    def _calculate_portfolio_values(self, holdings: List, start_date: datetime, end_date: datetime) -> List[float]:
        """Calculate portfolio values over time"""
        try:
            # This would typically calculate based on historical prices
            # For now, return mock data
            days = (end_date - start_date).days
            return [10000 * (1 + np.random.normal(0.0003, 0.015)) ** i for i in range(days)]
        except Exception as e:
            logger.error(f"Error calculating portfolio values: {e}")
            return []
    
    def _calculate_asset_returns(self, holdings: List, start_date: datetime, end_date: datetime) -> Dict[str, List[float]]:
        """Calculate individual asset returns"""
        try:
            asset_returns = {}
            for holding in holdings:
                # This would typically fetch historical data
                # For now, return mock data
                days = (end_date - start_date).days
                asset_returns[holding.symbol] = [np.random.normal(0.0005, 0.02) for _ in range(days)]
            return asset_returns
        except Exception as e:
            logger.error(f"Error calculating asset returns: {e}")
            return {}
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min()
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0
    
    def _calculate_drawdowns(self, returns: pd.Series) -> List[float]:
        """Calculate all drawdowns"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdowns = (cumulative - running_max) / running_max
            return [dd for dd in drawdowns if dd < 0]
        except Exception as e:
            logger.error(f"Error calculating drawdowns: {e}")
            return []
    
    def _get_scenario_probability(self, scenario_name: str) -> float:
        """Get probability of scenario occurrence"""
        probabilities = {
            "bull_market": 0.3,
            "bear_market": 0.2,
            "high_volatility": 0.15,
            "low_volatility": 0.25,
            "crisis": 0.1
        }
        return probabilities.get(scenario_name, 0.1)
    
    def _estimate_recovery_time(self, loss_magnitude: float) -> str:
        """Estimate recovery time based on loss magnitude"""
        if loss_magnitude < 0.1:
            return "1-3 months"
        elif loss_magnitude < 0.2:
            return "3-6 months"
        elif loss_magnitude < 0.3:
            return "6-12 months"
        else:
            return "1-2 years"
    
    def _classify_stress_severity(self, loss_magnitude: float) -> str:
        """Classify stress test severity"""
        if loss_magnitude < 0.1:
            return "Low"
        elif loss_magnitude < 0.2:
            return "Medium"
        elif loss_magnitude < 0.3:
            return "High"
        else:
            return "Extreme"

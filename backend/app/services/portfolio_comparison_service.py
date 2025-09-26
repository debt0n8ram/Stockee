import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

class PortfolioComparisonService:
    def __init__(self, db: Session):
        self.db = db

    def compare_portfolios(self, user_id: str, benchmark: str = "SPY") -> Dict:
        """Compare user's portfolio performance against benchmarks"""
        try:
            # Get user's portfolio
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}

            # Get portfolio holdings
            holdings = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio.id
            ).all()

            if not holdings:
                return {"error": "No holdings found"}

            # Calculate portfolio performance
            portfolio_performance = self._calculate_portfolio_performance(holdings)
            
            # Get benchmark performance
            benchmark_performance = self._get_benchmark_performance(benchmark)
            
            # Calculate comparison metrics
            comparison = self._calculate_comparison_metrics(
                portfolio_performance, 
                benchmark_performance
            )

            return {
                "portfolio_performance": portfolio_performance,
                "benchmark_performance": benchmark_performance,
                "comparison": comparison,
                "benchmark_symbol": benchmark
            }

        except Exception as e:
            logger.error(f"Error comparing portfolios: {e}")
            return {"error": f"Failed to compare portfolios: {str(e)}"}

    def _calculate_portfolio_performance(self, holdings: List) -> Dict:
        """Calculate portfolio performance metrics"""
        try:
            total_value = 0
            total_cost = 0
            holdings_data = []

            for holding in holdings:
                # Get current price
                latest_price = self.db.query(models.Price).filter(
                    models.Price.asset_id == holding.asset_id
                ).order_by(models.Price.timestamp.desc()).first()

                if latest_price:
                    current_price = float(latest_price.close_price)
                    current_value = current_price * float(holding.quantity)
                    cost_basis = float(holding.avg_cost) * float(holding.quantity)
                    
                    total_value += current_value
                    total_cost += cost_basis
                    
                    # Calculate individual holding performance
                    gain_loss = current_value - cost_basis
                    gain_loss_percent = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                    
                    holdings_data.append({
                        "symbol": holding.asset.symbol,
                        "name": holding.asset.name,
                        "quantity": float(holding.quantity),
                        "avg_cost": float(holding.avg_cost),
                        "current_price": current_price,
                        "current_value": current_value,
                        "cost_basis": cost_basis,
                        "gain_loss": gain_loss,
                        "gain_loss_percent": gain_loss_percent
                    })

            # Calculate overall portfolio metrics
            total_gain_loss = total_value - total_cost
            total_gain_loss_percent = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0

            # Calculate portfolio weights
            for holding_data in holdings_data:
                holding_data["weight"] = (holding_data["current_value"] / total_value) * 100 if total_value > 0 else 0

            return {
                "total_value": total_value,
                "total_cost": total_cost,
                "total_gain_loss": total_gain_loss,
                "total_gain_loss_percent": total_gain_loss_percent,
                "holdings": holdings_data,
                "holding_count": len(holdings_data)
            }

        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {e}")
            return {}

    def _get_benchmark_performance(self, benchmark: str) -> Dict:
        """Get benchmark performance data"""
        try:
            # Get benchmark asset
            benchmark_asset = self.db.query(models.Asset).filter(
                models.Asset.symbol == benchmark.upper()
            ).first()

            if not benchmark_asset:
                return {"error": f"Benchmark {benchmark} not found"}

            # Get historical prices for the benchmark
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)  # 1 year of data

            prices = self.db.query(models.Price).filter(
                models.Price.asset_id == benchmark_asset.id,
                models.Price.timestamp >= start_date,
                models.Price.timestamp <= end_date
            ).order_by(models.Price.timestamp).all()

            if not prices:
                return {"error": "No benchmark data available"}

            # Calculate benchmark performance
            current_price = float(prices[-1].close_price)
            start_price = float(prices[0].close_price)
            
            total_return = ((current_price - start_price) / start_price) * 100

            # Calculate daily returns for volatility
            daily_returns = []
            for i in range(1, len(prices)):
                prev_price = float(prices[i-1].close_price)
                curr_price = float(prices[i].close_price)
                daily_return = (curr_price - prev_price) / prev_price
                daily_returns.append(daily_return)

            # Calculate metrics
            volatility = np.std(daily_returns) * np.sqrt(252) * 100  # Annualized volatility
            sharpe_ratio = (total_return / volatility) if volatility > 0 else 0

            # Calculate max drawdown
            max_drawdown = self._calculate_max_drawdown([float(p.close_price) for p in prices])

            return {
                "symbol": benchmark.upper(),
                "current_price": current_price,
                "start_price": start_price,
                "total_return": total_return,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "data_points": len(prices)
            }

        except Exception as e:
            logger.error(f"Error getting benchmark performance: {e}")
            return {"error": f"Failed to get benchmark data: {str(e)}"}

    def _calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calculate maximum drawdown"""
        try:
            if len(prices) < 2:
                return 0

            peak = prices[0]
            max_dd = 0

            for price in prices[1:]:
                if price > peak:
                    peak = price
                else:
                    drawdown = (peak - price) / peak
                    max_dd = max(max_dd, drawdown)

            return max_dd * 100  # Return as percentage

        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0

    def _calculate_comparison_metrics(self, portfolio: Dict, benchmark: Dict) -> Dict:
        """Calculate comparison metrics between portfolio and benchmark"""
        try:
            if "error" in portfolio or "error" in benchmark:
                return {"error": "Cannot compare due to data errors"}

            # Performance comparison
            portfolio_return = portfolio.get("total_gain_loss_percent", 0)
            benchmark_return = benchmark.get("total_return", 0)
            
            excess_return = portfolio_return - benchmark_return
            
            # Risk-adjusted metrics
            portfolio_volatility = self._calculate_portfolio_volatility(portfolio)
            benchmark_volatility = benchmark.get("volatility", 0)
            
            # Information ratio (excess return / tracking error)
            tracking_error = abs(portfolio_volatility - benchmark_volatility)
            information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
            
            # Beta calculation (simplified)
            beta = self._calculate_portfolio_beta(portfolio, benchmark)
            
            # Alpha calculation (simplified)
            alpha = portfolio_return - (benchmark_return * beta)
            
            return {
                "excess_return": excess_return,
                "portfolio_volatility": portfolio_volatility,
                "benchmark_volatility": benchmark_volatility,
                "information_ratio": information_ratio,
                "beta": beta,
                "alpha": alpha,
                "outperformance": "Yes" if excess_return > 0 else "No",
                "risk_level": self._assess_risk_level(portfolio_volatility)
            }

        except Exception as e:
            logger.error(f"Error calculating comparison metrics: {e}")
            return {"error": f"Failed to calculate comparison: {str(e)}"}

    def _calculate_portfolio_volatility(self, portfolio: Dict) -> float:
        """Calculate portfolio volatility (simplified)"""
        try:
            # This is a simplified calculation
            # In practice, you'd need historical data for each holding
            holdings = portfolio.get("holdings", [])
            
            if not holdings:
                return 0

            # Use average volatility of holdings (simplified)
            total_volatility = 0
            for holding in holdings:
                # Assume 20% volatility for individual stocks (simplified)
                weight = holding.get("weight", 0) / 100
                total_volatility += (weight * 20) ** 2

            return np.sqrt(total_volatility)

        except Exception as e:
            logger.error(f"Error calculating portfolio volatility: {e}")
            return 0

    def _calculate_portfolio_beta(self, portfolio: Dict, benchmark: Dict) -> float:
        """Calculate portfolio beta (simplified)"""
        try:
            # This is a simplified beta calculation
            # In practice, you'd need historical correlation data
            holdings = portfolio.get("holdings", [])
            
            if not holdings:
                return 1.0

            # Use average beta of holdings (simplified)
            total_beta = 0
            total_weight = 0
            
            for holding in holdings:
                weight = holding.get("weight", 0) / 100
                # Assume beta of 1.0 for individual stocks (simplified)
                beta = 1.0
                total_beta += weight * beta
                total_weight += weight

            return total_beta / total_weight if total_weight > 0 else 1.0

        except Exception as e:
            logger.error(f"Error calculating portfolio beta: {e}")
            return 1.0

    def _assess_risk_level(self, volatility: float) -> str:
        """Assess risk level based on volatility"""
        if volatility < 10:
            return "Low"
        elif volatility < 20:
            return "Medium"
        elif volatility < 30:
            return "High"
        else:
            return "Very High"

    def get_sector_allocation(self, user_id: str) -> Dict:
        """Get portfolio sector allocation"""
        try:
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

            sector_allocation = {}
            total_value = 0

            for holding in holdings:
                # Get current price
                latest_price = self.db.query(models.Price).filter(
                    models.Price.asset_id == holding.asset_id
                ).order_by(models.Price.timestamp.desc()).first()

                if latest_price:
                    current_price = float(latest_price.close_price)
                    current_value = current_price * float(holding.quantity)
                    total_value += current_value
                    
                    sector = holding.asset.sector or "Unknown"
                    
                    if sector in sector_allocation:
                        sector_allocation[sector] += current_value
                    else:
                        sector_allocation[sector] = current_value

            # Convert to percentages
            sector_percentages = {}
            for sector, value in sector_allocation.items():
                percentage = (value / total_value) * 100 if total_value > 0 else 0
                sector_percentages[sector] = {
                    "value": value,
                    "percentage": round(percentage, 2)
                }

            return {
                "sector_allocation": sector_percentages,
                "total_value": total_value,
                "sector_count": len(sector_percentages)
            }

        except Exception as e:
            logger.error(f"Error getting sector allocation: {e}")
            return {"error": f"Failed to get sector allocation: {str(e)}"}

    def get_performance_attribution(self, user_id: str) -> Dict:
        """Get performance attribution analysis"""
        try:
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

            attribution_data = []
            total_contribution = 0

            for holding in holdings:
                # Get current price
                latest_price = self.db.query(models.Price).filter(
                    models.Price.asset_id == holding.asset_id
                ).order_by(models.Price.timestamp.desc()).first()

                if latest_price:
                    current_price = float(latest_price.close_price)
                    current_value = current_price * float(holding.quantity)
                    cost_basis = float(holding.avg_cost) * float(holding.quantity)
                    
                    gain_loss = current_value - cost_basis
                    gain_loss_percent = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                    
                    # Calculate contribution to total portfolio return
                    portfolio_weight = (current_value / portfolio.total_value) * 100 if portfolio.total_value > 0 else 0
                    contribution = portfolio_weight * (gain_loss_percent / 100)
                    total_contribution += contribution
                    
                    attribution_data.append({
                        "symbol": holding.asset.symbol,
                        "name": holding.asset.name,
                        "weight": round(portfolio_weight, 2),
                        "return": round(gain_loss_percent, 2),
                        "contribution": round(contribution, 2),
                        "value": current_value
                    })

            # Sort by contribution
            attribution_data.sort(key=lambda x: x["contribution"], reverse=True)

            return {
                "attribution": attribution_data,
                "total_contribution": round(total_contribution, 2),
                "holding_count": len(attribution_data)
            }

        except Exception as e:
            logger.error(f"Error getting performance attribution: {e}")
            return {"error": f"Failed to get performance attribution: {str(e)}"}

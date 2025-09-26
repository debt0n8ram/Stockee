import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta
from decimal import Decimal
import math

logger = logging.getLogger(__name__)

class OptionsService:
    def __init__(self, db: Session):
        self.db = db

    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """Get options chain for a symbol"""
        try:
            # Get current stock price
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return {"error": "Asset not found"}

            latest_price = self.db.query(models.Price).filter(
                models.Price.asset_id == asset.id
            ).order_by(models.Price.timestamp.desc()).first()

            if not latest_price:
                return {"error": "No price data available"}

            current_price = float(latest_price.close_price)

            # Generate options chain (simulated)
            options_chain = self._generate_options_chain(symbol, current_price, expiration_date)

            return {
                "symbol": symbol,
                "current_price": current_price,
                "expiration_date": expiration_date,
                "options_chain": options_chain
            }

        except Exception as e:
            logger.error(f"Error getting options chain for {symbol}: {e}")
            return {"error": f"Failed to get options chain: {str(e)}"}

    def _generate_options_chain(self, symbol: str, current_price: float, expiration_date: Optional[str]) -> Dict:
        """Generate simulated options chain"""
        try:
            # Calculate expiration date if not provided
            if not expiration_date:
                # Default to next Friday
                today = datetime.now()
                days_ahead = 4 - today.weekday()  # Friday is 4
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                expiration_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

            # Calculate time to expiration
            exp_date = datetime.strptime(expiration_date, "%Y-%m-%d")
            time_to_exp = (exp_date - datetime.now()).days / 365.0

            # Generate strike prices around current price
            strike_prices = []
            base_strike = round(current_price)
            
            # Generate strikes from 20% below to 20% above current price
            for i in range(-20, 21):
                strike = base_strike + (i * 5)  # $5 increments
                if strike > 0:
                    strike_prices.append(strike)

            # Generate calls and puts
            calls = []
            puts = []

            for strike in strike_prices:
                # Calculate option prices using Black-Scholes (simplified)
                call_price = self._calculate_option_price(current_price, strike, time_to_exp, "call")
                put_price = self._calculate_option_price(current_price, strike, time_to_exp, "put")

                # Calculate Greeks
                greeks = self._calculate_greeks(current_price, strike, time_to_exp, "call")

                calls.append({
                    "strike": strike,
                    "bid": round(call_price * 0.98, 2),
                    "ask": round(call_price * 1.02, 2),
                    "last": round(call_price, 2),
                    "volume": np.random.randint(0, 1000),
                    "open_interest": np.random.randint(0, 5000),
                    "implied_volatility": round(np.random.uniform(0.15, 0.45), 3),
                    "delta": round(greeks["delta"], 3),
                    "gamma": round(greeks["gamma"], 4),
                    "theta": round(greeks["theta"], 3),
                    "vega": round(greeks["vega"], 3)
                })

                puts.append({
                    "strike": strike,
                    "bid": round(put_price * 0.98, 2),
                    "ask": round(put_price * 1.02, 2),
                    "last": round(put_price, 2),
                    "volume": np.random.randint(0, 1000),
                    "open_interest": np.random.randint(0, 5000),
                    "implied_volatility": round(np.random.uniform(0.15, 0.45), 3),
                    "delta": round(-greeks["delta"], 3),  # Put delta is negative
                    "gamma": round(greeks["gamma"], 4),
                    "theta": round(greeks["theta"], 3),
                    "vega": round(greeks["vega"], 3)
                })

            return {
                "calls": calls,
                "puts": puts,
                "expiration_date": expiration_date,
                "time_to_expiration": round(time_to_exp * 365, 1)
            }

        except Exception as e:
            logger.error(f"Error generating options chain: {e}")
            return {"calls": [], "puts": []}

    def _calculate_option_price(self, S: float, K: float, T: float, option_type: str) -> float:
        """Calculate option price using Black-Scholes formula (simplified)"""
        try:
            # Simplified Black-Scholes calculation
            r = 0.05  # Risk-free rate (5%)
            sigma = 0.25  # Volatility (25%)
            
            if T <= 0:
                # At expiration
                if option_type == "call":
                    return max(S - K, 0)
                else:
                    return max(K - S, 0)
            
            # Calculate d1 and d2
            d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            
            # Calculate option price
            if option_type == "call":
                price = S * self._normal_cdf(d1) - K * math.exp(-r * T) * self._normal_cdf(d2)
            else:
                price = K * math.exp(-r * T) * self._normal_cdf(-d2) - S * self._normal_cdf(-d1)
            
            return max(price, 0.01)  # Minimum price of $0.01

        except Exception as e:
            logger.error(f"Error calculating option price: {e}")
            return 0.01

    def _calculate_greeks(self, S: float, K: float, T: float, option_type: str) -> Dict:
        """Calculate option Greeks"""
        try:
            r = 0.05
            sigma = 0.25
            
            if T <= 0:
                return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}
            
            d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)
            
            # Delta
            if option_type == "call":
                delta = self._normal_cdf(d1)
            else:
                delta = self._normal_cdf(d1) - 1
            
            # Gamma
            gamma = self._normal_pdf(d1) / (S * sigma * math.sqrt(T))
            
            # Theta
            theta = -(S * self._normal_pdf(d1) * sigma) / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * self._normal_cdf(d2)
            if option_type == "put":
                theta += r * K * math.exp(-r * T)
            
            # Vega
            vega = S * self._normal_pdf(d1) * math.sqrt(T)
            
            return {
                "delta": delta,
                "gamma": gamma,
                "theta": theta / 365,  # Per day
                "vega": vega / 100  # Per 1% change in volatility
            }

        except Exception as e:
            logger.error(f"Error calculating Greeks: {e}")
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}

    def _normal_cdf(self, x: float) -> float:
        """Cumulative distribution function of standard normal distribution"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _normal_pdf(self, x: float) -> float:
        """Probability density function of standard normal distribution"""
        return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)

    def calculate_option_strategy(self, strategy_data: Dict) -> Dict:
        """Calculate option strategy P&L and risk metrics"""
        try:
            strategy_type = strategy_data.get("strategy_type")
            legs = strategy_data.get("legs", [])
            
            if not legs:
                return {"error": "No strategy legs provided"}

            # Calculate strategy metrics
            total_cost = 0
            max_profit = 0
            max_loss = 0
            breakeven_points = []
            
            for leg in legs:
                option_type = leg.get("option_type")  # "call" or "put"
                action = leg.get("action")  # "buy" or "sell"
                strike = leg.get("strike")
                premium = leg.get("premium")
                quantity = leg.get("quantity", 1)
                
                # Calculate leg cost
                leg_cost = premium * quantity
                if action == "sell":
                    leg_cost = -leg_cost  # Selling generates credit
                
                total_cost += leg_cost

            # Calculate P&L at different stock prices
            stock_prices = np.arange(0, 200, 5)  # Stock prices from $0 to $200
            pnl_data = []
            
            for stock_price in stock_prices:
                total_pnl = 0
                
                for leg in legs:
                    option_type = leg.get("option_type")
                    action = leg.get("action")
                    strike = leg.get("strike")
                    premium = leg.get("premium")
                    quantity = leg.get("quantity", 1)
                    
                    # Calculate intrinsic value
                    if option_type == "call":
                        intrinsic_value = max(stock_price - strike, 0)
                    else:
                        intrinsic_value = max(strike - stock_price, 0)
                    
                    # Calculate P&L for this leg
                    if action == "buy":
                        leg_pnl = (intrinsic_value - premium) * quantity
                    else:
                        leg_pnl = (premium - intrinsic_value) * quantity
                    
                    total_pnl += leg_pnl
                
                pnl_data.append({
                    "stock_price": stock_price,
                    "pnl": total_pnl
                })

            # Find breakeven points
            for i in range(1, len(pnl_data)):
                if pnl_data[i-1]["pnl"] * pnl_data[i]["pnl"] <= 0:
                    # Linear interpolation to find exact breakeven
                    x1, y1 = pnl_data[i-1]["stock_price"], pnl_data[i-1]["pnl"]
                    x2, y2 = pnl_data[i]["stock_price"], pnl_data[i]["pnl"]
                    
                    if y2 != y1:
                        breakeven = x1 - y1 * (x2 - x1) / (y2 - y1)
                        breakeven_points.append(round(breakeven, 2))

            # Calculate max profit and loss
            pnl_values = [point["pnl"] for point in pnl_data]
            max_profit = max(pnl_values)
            max_loss = min(pnl_values)

            return {
                "strategy_type": strategy_type,
                "total_cost": total_cost,
                "max_profit": max_profit,
                "max_loss": max_loss,
                "breakeven_points": breakeven_points,
                "pnl_data": pnl_data,
                "risk_reward_ratio": abs(max_profit / max_loss) if max_loss != 0 else 0
            }

        except Exception as e:
            logger.error(f"Error calculating option strategy: {e}")
            return {"error": f"Failed to calculate strategy: {str(e)}"}

    def get_option_strategies(self) -> Dict:
        """Get list of common option strategies"""
        return {
            "strategies": [
                {
                    "name": "Long Call",
                    "description": "Buy a call option",
                    "risk": "Limited to premium paid",
                    "reward": "Unlimited upside",
                    "market_outlook": "Bullish"
                },
                {
                    "name": "Long Put",
                    "description": "Buy a put option",
                    "risk": "Limited to premium paid",
                    "reward": "Limited to strike price minus premium",
                    "market_outlook": "Bearish"
                },
                {
                    "name": "Covered Call",
                    "description": "Sell a call option against owned stock",
                    "risk": "Unlimited downside on stock",
                    "reward": "Limited to premium received",
                    "market_outlook": "Neutral to slightly bullish"
                },
                {
                    "name": "Protective Put",
                    "description": "Buy a put option to protect stock position",
                    "risk": "Limited to premium paid",
                    "reward": "Unlimited upside on stock",
                    "market_outlook": "Bullish with downside protection"
                },
                {
                    "name": "Straddle",
                    "description": "Buy both call and put at same strike",
                    "risk": "Limited to total premium paid",
                    "reward": "Unlimited in either direction",
                    "market_outlook": "Volatile"
                },
                {
                    "name": "Strangle",
                    "description": "Buy call and put at different strikes",
                    "risk": "Limited to total premium paid",
                    "reward": "Unlimited in either direction",
                    "market_outlook": "Volatile"
                },
                {
                    "name": "Iron Condor",
                    "description": "Sell call spread and put spread",
                    "risk": "Limited to difference between strikes minus premium",
                    "reward": "Limited to premium received",
                    "market_outlook": "Range-bound"
                }
            ]
        }

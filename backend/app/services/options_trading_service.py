import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
from scipy.stats import norm
import json

from app.db import models

logger = logging.getLogger(__name__)

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class OptionStrategy(Enum):
    LONG_CALL = "long_call"
    LONG_PUT = "long_put"
    SHORT_CALL = "short_call"
    SHORT_PUT = "short_put"
    COVERED_CALL = "covered_call"
    PROTECTIVE_PUT = "protective_put"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY = "butterfly"
    IRON_CONDOR = "iron_condor"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_CALL_SPREAD = "bear_call_spread"
    BULL_PUT_SPREAD = "bull_put_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"

@dataclass
class OptionContract:
    """Represents an options contract"""
    symbol: str
    option_type: OptionType
    strike_price: float
    expiration_date: datetime
    premium: float
    volume: int = 0
    open_interest: int = 0
    implied_volatility: float = 0.0
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0

@dataclass
class OptionPosition:
    """Represents an options position"""
    contract: OptionContract
    quantity: int  # Positive for long, negative for short
    entry_price: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

@dataclass
class OptionStrategy:
    """Represents an options strategy"""
    name: str
    strategy_type: OptionStrategy
    positions: List[OptionPosition]
    max_profit: float = 0.0
    max_loss: float = 0.0
    breakeven_points: List[float] = None
    profit_loss_curve: List[Tuple[float, float]] = None

class OptionsTradingService:
    """Comprehensive options trading service with Greeks calculation and strategy builder"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def calculate_black_scholes(self, 
                               spot_price: float,
                               strike_price: float,
                               time_to_expiry: float,
                               risk_free_rate: float,
                               volatility: float,
                               option_type: OptionType) -> Dict[str, float]:
        """Calculate Black-Scholes option price and Greeks"""
        try:
            # Convert time to years
            T = time_to_expiry / 365.0
            
            # Calculate d1 and d2
            d1 = (math.log(spot_price / strike_price) + 
                  (risk_free_rate + 0.5 * volatility**2) * T) / (volatility * math.sqrt(T))
            d2 = d1 - volatility * math.sqrt(T)
            
            # Calculate option price
            if option_type == OptionType.CALL:
                price = (spot_price * norm.cdf(d1) - 
                        strike_price * math.exp(-risk_free_rate * T) * norm.cdf(d2))
            else:  # PUT
                price = (strike_price * math.exp(-risk_free_rate * T) * norm.cdf(-d2) - 
                        spot_price * norm.cdf(-d1))
            
            # Calculate Greeks
            delta = norm.cdf(d1) if option_type == OptionType.CALL else norm.cdf(d1) - 1
            gamma = norm.pdf(d1) / (spot_price * volatility * math.sqrt(T))
            theta = (-(spot_price * norm.pdf(d1) * volatility) / (2 * math.sqrt(T)) - 
                    risk_free_rate * strike_price * math.exp(-risk_free_rate * T) * 
                    (norm.cdf(d2) if option_type == OptionType.CALL else norm.cdf(-d2)))
            vega = spot_price * norm.pdf(d1) * math.sqrt(T)
            rho = (strike_price * T * math.exp(-risk_free_rate * T) * 
                   (norm.cdf(d2) if option_type == OptionType.CALL else -norm.cdf(-d2)))
            
            return {
                'price': price,
                'delta': delta,
                'gamma': gamma,
                'theta': theta,
                'vega': vega,
                'rho': rho,
                'implied_volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"Error calculating Black-Scholes: {e}")
            return {
                'price': 0.0,
                'delta': 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0,
                'implied_volatility': 0.0
            }
    
    def calculate_implied_volatility(self,
                                   market_price: float,
                                   spot_price: float,
                                   strike_price: float,
                                   time_to_expiry: float,
                                   risk_free_rate: float,
                                   option_type: OptionType,
                                   max_iterations: int = 100,
                                   tolerance: float = 0.001) -> float:
        """Calculate implied volatility using Newton-Raphson method"""
        try:
            # Initial guess
            volatility = 0.2
            
            for i in range(max_iterations):
                # Calculate theoretical price
                result = self.calculate_black_scholes(
                    spot_price, strike_price, time_to_expiry, 
                    risk_free_rate, volatility, option_type
                )
                theoretical_price = result['price']
                vega = result['vega']
                
                # Check convergence
                price_diff = theoretical_price - market_price
                if abs(price_diff) < tolerance:
                    return volatility
                
                # Update volatility using Newton-Raphson
                if vega > 0:
                    volatility = volatility - price_diff / vega
                else:
                    volatility = volatility * 0.9  # Fallback
                
                # Ensure volatility is positive
                volatility = max(0.001, volatility)
            
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating implied volatility: {e}")
            return 0.2  # Default fallback
    
    def get_option_chain(self, symbol: str, expiration_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get option chain for a symbol"""
        try:
            # Get underlying asset
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return {'error': f'Asset {symbol} not found'}
            
            # Get current price
            current_price = self._get_current_price(symbol)
            if not current_price:
                return {'error': f'No current price available for {symbol}'}
            
            # Get risk-free rate (simplified - in practice, use Treasury rates)
            risk_free_rate = 0.05  # 5% default
            
            # Get expiration dates
            if expiration_date:
                expirations = [expiration_date]
            else:
                # Generate next 4 Fridays and month-end dates
                expirations = self._generate_expiration_dates()
            
            option_chain = {
                'symbol': symbol,
                'current_price': current_price,
                'risk_free_rate': risk_free_rate,
                'expirations': [],
                'options': []
            }
            
            for exp_date in expirations:
                time_to_expiry = (exp_date - datetime.now()).days
                if time_to_expiry <= 0:
                    continue
                
                expiration_data = {
                    'expiration_date': exp_date.isoformat(),
                    'days_to_expiry': time_to_expiry,
                    'calls': [],
                    'puts': []
                }
                
                # Generate strike prices around current price
                strikes = self._generate_strike_prices(current_price)
                
                for strike in strikes:
                    # Calculate theoretical prices and Greeks
                    call_result = self.calculate_black_scholes(
                        current_price, strike, time_to_expiry, 
                        risk_free_rate, 0.25, OptionType.CALL  # 25% default volatility
                    )
                    
                    put_result = self.calculate_black_scholes(
                        current_price, strike, time_to_expiry, 
                        risk_free_rate, 0.25, OptionType.PUT
                    )
                    
                    # Create option contracts
                    call_contract = OptionContract(
                        symbol=f"{symbol}{exp_date.strftime('%y%m%d')}C{strike:08.0f}",
                        option_type=OptionType.CALL,
                        strike_price=strike,
                        expiration_date=exp_date,
                        premium=call_result['price'],
                        implied_volatility=call_result['implied_volatility'],
                        delta=call_result['delta'],
                        gamma=call_result['gamma'],
                        theta=call_result['theta'],
                        vega=call_result['vega'],
                        rho=call_result['rho']
                    )
                    
                    put_contract = OptionContract(
                        symbol=f"{symbol}{exp_date.strftime('%y%m%d')}P{strike:08.0f}",
                        option_type=OptionType.PUT,
                        strike_price=strike,
                        expiration_date=exp_date,
                        premium=put_result['price'],
                        implied_volatility=put_result['implied_volatility'],
                        delta=put_result['delta'],
                        gamma=put_result['gamma'],
                        theta=put_result['theta'],
                        vega=put_result['vega'],
                        rho=put_result['rho']
                    )
                    
                    expiration_data['calls'].append({
                        'symbol': call_contract.symbol,
                        'strike': strike,
                        'premium': call_result['price'],
                        'delta': call_result['delta'],
                        'gamma': call_result['gamma'],
                        'theta': call_result['theta'],
                        'vega': call_result['vega'],
                        'rho': call_result['rho'],
                        'implied_volatility': call_result['implied_volatility'],
                        'volume': 0,
                        'open_interest': 0
                    })
                    
                    expiration_data['puts'].append({
                        'symbol': put_contract.symbol,
                        'strike': strike,
                        'premium': put_result['price'],
                        'delta': put_result['delta'],
                        'gamma': put_result['gamma'],
                        'theta': call_result['theta'],
                        'vega': put_result['vega'],
                        'rho': put_result['rho'],
                        'implied_volatility': put_result['implied_volatility'],
                        'volume': 0,
                        'open_interest': 0
                    })
                
                option_chain['expirations'].append(expiration_data)
            
            return option_chain
            
        except Exception as e:
            logger.error(f"Error getting option chain: {e}")
            return {'error': str(e)}
    
    def create_option_strategy(self, 
                              strategy_type: OptionStrategy,
                              symbol: str,
                              positions: List[Dict[str, Any]],
                              current_price: float) -> OptionStrategy:
        """Create an options strategy"""
        try:
            option_positions = []
            
            for pos_data in positions:
                # Create option contract
                contract = OptionContract(
                    symbol=pos_data['symbol'],
                    option_type=OptionType(pos_data['option_type']),
                    strike_price=pos_data['strike_price'],
                    expiration_date=datetime.fromisoformat(pos_data['expiration_date']),
                    premium=pos_data['premium']
                )
                
                # Create position
                position = OptionPosition(
                    contract=contract,
                    quantity=pos_data['quantity'],
                    entry_price=pos_data['premium'],
                    current_price=pos_data['premium']
                )
                
                option_positions.append(position)
            
            # Calculate strategy metrics
            strategy = OptionStrategy(
                name=f"{strategy_type.value.replace('_', ' ').title()}",
                strategy_type=strategy_type,
                positions=option_positions
            )
            
            # Calculate P&L curve
            strategy.profit_loss_curve = self._calculate_profit_loss_curve(strategy, current_price)
            strategy.max_profit, strategy.max_loss = self._calculate_max_profit_loss(strategy)
            strategy.breakeven_points = self._calculate_breakeven_points(strategy)
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error creating option strategy: {e}")
            raise
    
    def calculate_strategy_greeks(self, strategy: OptionStrategy) -> Dict[str, float]:
        """Calculate aggregate Greeks for a strategy"""
        try:
            total_delta = 0.0
            total_gamma = 0.0
            total_theta = 0.0
            total_vega = 0.0
            total_rho = 0.0
            
            for position in strategy.positions:
                multiplier = position.quantity
                total_delta += position.contract.delta * multiplier
                total_gamma += position.contract.gamma * multiplier
                total_theta += position.contract.theta * multiplier
                total_vega += position.contract.vega * multiplier
                total_rho += position.contract.rho * multiplier
            
            return {
                'delta': total_delta,
                'gamma': total_gamma,
                'theta': total_theta,
                'vega': total_vega,
                'rho': total_rho
            }
            
        except Exception as e:
            logger.error(f"Error calculating strategy Greeks: {e}")
            return {
                'delta': 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0
            }
    
    def get_strategy_templates(self) -> List[Dict[str, Any]]:
        """Get predefined strategy templates"""
        return [
            {
                'name': 'Long Call',
                'type': OptionStrategy.LONG_CALL,
                'description': 'Buy a call option to profit from upward price movement',
                'max_profit': 'Unlimited',
                'max_loss': 'Premium paid',
                'breakeven': 'Strike + Premium',
                'risk_level': 'Limited',
                'setup': [
                    {'action': 'buy', 'option_type': 'call', 'quantity': 1}
                ]
            },
            {
                'name': 'Long Put',
                'type': OptionStrategy.LONG_PUT,
                'description': 'Buy a put option to profit from downward price movement',
                'max_profit': 'Strike - Premium',
                'max_loss': 'Premium paid',
                'breakeven': 'Strike - Premium',
                'risk_level': 'Limited',
                'setup': [
                    {'action': 'buy', 'option_type': 'put', 'quantity': 1}
                ]
            },
            {
                'name': 'Covered Call',
                'type': OptionStrategy.COVERED_CALL,
                'description': 'Sell a call option against owned stock',
                'max_profit': 'Premium + (Strike - Stock Price)',
                'max_loss': 'Stock Price - Premium',
                'breakeven': 'Stock Price - Premium',
                'risk_level': 'Moderate',
                'setup': [
                    {'action': 'buy', 'asset_type': 'stock', 'quantity': 100},
                    {'action': 'sell', 'option_type': 'call', 'quantity': 1}
                ]
            },
            {
                'name': 'Protective Put',
                'type': OptionStrategy.PROTECTIVE_PUT,
                'description': 'Buy a put option to protect stock position',
                'max_profit': 'Unlimited',
                'max_loss': 'Stock Price - Strike + Premium',
                'breakeven': 'Stock Price + Premium',
                'risk_level': 'Limited',
                'setup': [
                    {'action': 'buy', 'asset_type': 'stock', 'quantity': 100},
                    {'action': 'buy', 'option_type': 'put', 'quantity': 1}
                ]
            },
            {
                'name': 'Straddle',
                'type': OptionStrategy.STRADDLE,
                'description': 'Buy both call and put with same strike and expiration',
                'max_profit': 'Unlimited',
                'max_loss': 'Total Premium Paid',
                'breakeven': 'Strike ± Total Premium',
                'risk_level': 'Limited',
                'setup': [
                    {'action': 'buy', 'option_type': 'call', 'quantity': 1},
                    {'action': 'buy', 'option_type': 'put', 'quantity': 1}
                ]
            },
            {
                'name': 'Strangle',
                'type': OptionStrategy.STRANGLE,
                'description': 'Buy call and put with different strikes, same expiration',
                'max_profit': 'Unlimited',
                'max_loss': 'Total Premium Paid',
                'breakeven': 'Call Strike + Premium, Put Strike - Premium',
                'risk_level': 'Limited',
                'setup': [
                    {'action': 'buy', 'option_type': 'call', 'quantity': 1, 'strike_offset': 5},
                    {'action': 'buy', 'option_type': 'put', 'quantity': 1, 'strike_offset': -5}
                ]
            },
            {
                'name': 'Iron Condor',
                'type': OptionStrategy.IRON_CONDOR,
                'description': 'Sell call spread and put spread for income',
                'max_profit': 'Net Premium Received',
                'max_loss': 'Spread Width - Net Premium',
                'breakeven': 'Two breakeven points',
                'risk_level': 'Limited',
                'setup': [
                    {'action': 'sell', 'option_type': 'call', 'quantity': 1, 'strike_offset': 5},
                    {'action': 'buy', 'option_type': 'call', 'quantity': 1, 'strike_offset': 10},
                    {'action': 'sell', 'option_type': 'put', 'quantity': 1, 'strike_offset': -5},
                    {'action': 'buy', 'option_type': 'put', 'quantity': 1, 'strike_offset': -10}
                ]
            }
        ]
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return None
            
            price = self.db.query(models.Price).filter(
                models.Price.asset_id == asset.id
            ).order_by(models.Price.timestamp.desc()).first()
            
            return float(price.close_price) if price else None
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return None
    
    def _generate_expiration_dates(self) -> List[datetime]:
        """Generate standard expiration dates"""
        expirations = []
        today = datetime.now()
        
        # Add next 4 Fridays
        for i in range(1, 5):
            days_ahead = (4 - today.weekday()) % 7 + (i - 1) * 7
            if days_ahead == 0:
                days_ahead = 7
            exp_date = today + timedelta(days=days_ahead)
            expirations.append(exp_date)
        
        # Add month-end dates for next 3 months
        for i in range(1, 4):
            next_month = today.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            month_end = next_month - timedelta(days=1)
            expirations.append(month_end)
        
        return sorted(expirations)
    
    def _generate_strike_prices(self, current_price: float) -> List[float]:
        """Generate strike prices around current price"""
        strikes = []
        
        # Generate strikes in $5 increments for stocks under $100
        # $10 increments for stocks $100-$200
        # $25 increments for stocks over $200
        if current_price < 100:
            increment = 5
        elif current_price < 200:
            increment = 10
        else:
            increment = 25
        
        # Generate strikes from 20% below to 20% above current price
        start_strike = int(current_price * 0.8 / increment) * increment
        end_strike = int(current_price * 1.2 / increment) * increment
        
        strike = start_strike
        while strike <= end_strike:
            strikes.append(strike)
            strike += increment
        
        return strikes
    
    def _calculate_profit_loss_curve(self, strategy: OptionStrategy, current_price: float) -> List[Tuple[float, float]]:
        """Calculate profit/loss curve for a strategy"""
        try:
            curve = []
            
            # Generate price range
            price_range = np.linspace(current_price * 0.5, current_price * 1.5, 100)
            
            for price in price_range:
                total_pnl = 0.0
                
                for position in strategy.positions:
                    # Calculate P&L for this position at this price
                    if position.contract.option_type == OptionType.CALL:
                        intrinsic_value = max(0, price - position.contract.strike_price)
                    else:  # PUT
                        intrinsic_value = max(0, position.contract.strike_price - price)
                    
                    pnl = (intrinsic_value - position.entry_price) * position.quantity
                    total_pnl += pnl
                
                curve.append((price, total_pnl))
            
            return curve
            
        except Exception as e:
            logger.error(f"Error calculating P&L curve: {e}")
            return []
    
    def _calculate_max_profit_loss(self, strategy: OptionStrategy) -> Tuple[float, float]:
        """Calculate maximum profit and loss for a strategy"""
        try:
            curve = strategy.profit_loss_curve
            if not curve:
                return 0.0, 0.0
            
            profits = [pnl for _, pnl in curve]
            max_profit = max(profits)
            max_loss = min(profits)
            
            return max_profit, max_loss
            
        except Exception as e:
            logger.error(f"Error calculating max profit/loss: {e}")
            return 0.0, 0.0
    
    def _calculate_breakeven_points(self, strategy: OptionStrategy) -> List[float]:
        """Calculate breakeven points for a strategy"""
        try:
            curve = strategy.profit_loss_curve
            if not curve:
                return []
            
            breakevens = []
            for i in range(len(curve) - 1):
                price1, pnl1 = curve[i]
                price2, pnl2 = curve[i + 1]
                
                # Check if P&L crosses zero
                if (pnl1 <= 0 <= pnl2) or (pnl1 >= 0 >= pnl2):
                    # Linear interpolation to find exact breakeven
                    if pnl2 != pnl1:
                        breakeven_price = price1 + (0 - pnl1) * (price2 - price1) / (pnl2 - pnl1)
                        breakevens.append(breakeven_price)
            
            return breakevens
            
        except Exception as e:
            logger.error(f"Error calculating breakeven points: {e}")
            return []

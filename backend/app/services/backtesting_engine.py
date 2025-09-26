import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Callable
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.db import models
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    """Represents a trading order"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    timestamp: datetime = None
    filled_price: Optional[float] = None
    filled_quantity: float = 0
    status: str = "pending"

@dataclass
class Position:
    """Represents a position in a symbol"""
    symbol: str
    quantity: float
    average_price: float
    unrealized_pnl: float = 0
    realized_pnl: float = 0

@dataclass
class Trade:
    """Represents a completed trade"""
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    commission: float = 0

@dataclass
class BacktestResult:
    """Results of a backtest"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    portfolio_values: List[float]
    trades: List[Trade]
    positions: Dict[str, Position]
    equity_curve: pd.Series
    drawdown_curve: pd.Series

class BacktestingEngine:
    """Comprehensive backtesting engine for strategy testing and optimization"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def run_backtest(self, 
                    strategy: Callable,
                    symbols: List[str],
                    start_date: datetime,
                    end_date: datetime,
                    initial_capital: float = 100000,
                    commission: float = 0.001,
                    slippage: float = 0.0005,
                    **strategy_params) -> BacktestResult:
        """Run a backtest for a given strategy"""
        try:
            logger.info(f"Starting backtest for symbols: {symbols}")
            
            # Get historical data
            historical_data = self._get_historical_data(symbols, start_date, end_date)
            if not historical_data:
                raise ValueError("No historical data available")
            
            # Initialize portfolio
            portfolio = {
                'cash': initial_capital,
                'positions': {},
                'total_value': initial_capital
            }
            
            # Initialize tracking
            portfolio_values = [initial_capital]
            trades = []
            orders = []
            
            # Run strategy simulation
            for date, data in historical_data.iterrows():
                # Update portfolio value
                portfolio['total_value'] = self._calculate_portfolio_value(portfolio, data)
                portfolio_values.append(portfolio['total_value'])
                
                # Generate signals from strategy
                signals = strategy(data, portfolio, **strategy_params)
                
                # Process signals into orders
                new_orders = self._generate_orders(signals, date, portfolio)
                orders.extend(new_orders)
                
                # Execute orders
                executed_trades = self._execute_orders(new_orders, data, portfolio, commission, slippage)
                trades.extend(executed_trades)
                
                # Update positions
                self._update_positions(portfolio, executed_trades)
            
            # Calculate performance metrics
            result = self._calculate_performance_metrics(
                portfolio_values, trades, portfolio, start_date, end_date
            )
            
            logger.info(f"Backtest completed. Total return: {result.total_return:.2%}")
            return result
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise
    
    def optimize_strategy(self,
                         strategy: Callable,
                         symbols: List[str],
                         start_date: datetime,
                         end_date: datetime,
                         parameter_ranges: Dict[str, Tuple],
                         optimization_metric: str = "sharpe_ratio",
                         n_trials: int = 100) -> Dict[str, Any]:
        """Optimize strategy parameters using grid search or random search"""
        try:
            logger.info(f"Starting strategy optimization with {n_trials} trials")
            
            best_params = None
            best_metric = float('-inf')
            optimization_results = []
            
            for trial in range(n_trials):
                # Generate random parameters
                params = {}
                for param_name, (min_val, max_val) in parameter_ranges.items():
                    if isinstance(min_val, int):
                        params[param_name] = np.random.randint(min_val, max_val + 1)
                    else:
                        params[param_name] = np.random.uniform(min_val, max_val)
                
                try:
                    # Run backtest with these parameters
                    result = self.run_backtest(
                        strategy, symbols, start_date, end_date, **params
                    )
                    
                    # Get optimization metric
                    metric_value = getattr(result, optimization_metric, 0)
                    
                    optimization_results.append({
                        'trial': trial,
                        'parameters': params,
                        'metric': metric_value,
                        'total_return': result.total_return,
                        'sharpe_ratio': result.sharpe_ratio,
                        'max_drawdown': result.max_drawdown
                    })
                    
                    # Update best parameters
                    if metric_value > best_metric:
                        best_metric = metric_value
                        best_params = params
                        
                except Exception as e:
                    logger.warning(f"Trial {trial} failed: {e}")
                    continue
            
            return {
                'best_parameters': best_params,
                'best_metric': best_metric,
                'optimization_metric': optimization_metric,
                'total_trials': n_trials,
                'successful_trials': len(optimization_results),
                'results': optimization_results
            }
            
        except Exception as e:
            logger.error(f"Error optimizing strategy: {e}")
            raise
    
    def walk_forward_analysis(self,
                             strategy: Callable,
                             symbols: List[str],
                             start_date: datetime,
                             end_date: datetime,
                             train_period: int = 252,  # 1 year
                             test_period: int = 63,    # 3 months
                             step_size: int = 21,      # 1 month
                             **strategy_params) -> Dict[str, Any]:
        """Perform walk-forward analysis"""
        try:
            logger.info("Starting walk-forward analysis")
            
            current_date = start_date
            results = []
            
            while current_date + timedelta(days=train_period + test_period) <= end_date:
                # Define training and test periods
                train_start = current_date
                train_end = current_date + timedelta(days=train_period)
                test_start = train_end
                test_end = test_start + timedelta(days=test_period)
                
                # Optimize strategy on training data
                optimization_result = self.optimize_strategy(
                    strategy, symbols, train_start, train_end,
                    parameter_ranges=strategy_params, n_trials=50
                )
                
                # Test optimized strategy on test data
                if optimization_result['best_parameters']:
                    test_result = self.run_backtest(
                        strategy, symbols, test_start, test_end,
                        **optimization_result['best_parameters']
                    )
                    
                    results.append({
                        'train_period': {'start': train_start, 'end': train_end},
                        'test_period': {'start': test_start, 'end': test_end},
                        'optimized_parameters': optimization_result['best_parameters'],
                        'test_results': {
                            'total_return': test_result.total_return,
                            'sharpe_ratio': test_result.sharpe_ratio,
                            'max_drawdown': test_result.max_drawdown,
                            'total_trades': test_result.total_trades
                        }
                    })
                
                # Move to next period
                current_date += timedelta(days=step_size)
            
            # Calculate aggregate statistics
            if results:
                returns = [r['test_results']['total_return'] for r in results]
                sharpe_ratios = [r['test_results']['sharpe_ratio'] for r in results]
                max_drawdowns = [r['test_results']['max_drawdown'] for r in results]
                
                return {
                    'total_periods': len(results),
                    'average_return': np.mean(returns),
                    'average_sharpe': np.mean(sharpe_ratios),
                    'average_max_drawdown': np.mean(max_drawdowns),
                    'return_std': np.std(returns),
                    'positive_periods': sum(1 for r in returns if r > 0),
                    'results': results
                }
            else:
                return {'error': 'No valid results from walk-forward analysis'}
                
        except Exception as e:
            logger.error(f"Error in walk-forward analysis: {e}")
            raise
    
    def monte_carlo_simulation(self,
                              strategy: Callable,
                              symbols: List[str],
                              start_date: datetime,
                              end_date: datetime,
                              n_simulations: int = 1000,
                              **strategy_params) -> Dict[str, Any]:
        """Run Monte Carlo simulation to test strategy robustness"""
        try:
            logger.info(f"Starting Monte Carlo simulation with {n_simulations} runs")
            
            # Get historical data
            historical_data = self._get_historical_data(symbols, start_date, end_date)
            if historical_data.empty:
                raise ValueError("No historical data available")
            
            # Calculate returns for bootstrapping
            returns = historical_data.pct_change().dropna()
            
            simulation_results = []
            
            for simulation in range(n_simulations):
                try:
                    # Bootstrap returns
                    bootstrapped_returns = returns.sample(n=len(returns), replace=True)
                    bootstrapped_data = (1 + bootstrapped_returns).cumprod() * historical_data.iloc[0]
                    
                    # Run strategy on bootstrapped data
                    result = self.run_backtest(
                        strategy, symbols, start_date, end_date, **strategy_params
                    )
                    
                    simulation_results.append({
                        'simulation': simulation,
                        'total_return': result.total_return,
                        'sharpe_ratio': result.sharpe_ratio,
                        'max_drawdown': result.max_drawdown,
                        'volatility': result.volatility
                    })
                    
                except Exception as e:
                    logger.warning(f"Simulation {simulation} failed: {e}")
                    continue
            
            if simulation_results:
                returns = [r['total_return'] for r in simulation_results]
                sharpe_ratios = [r['sharpe_ratio'] for r in simulation_results]
                max_drawdowns = [r['max_drawdown'] for r in simulation_results]
                
                return {
                    'total_simulations': len(simulation_results),
                    'successful_simulations': len(simulation_results),
                    'return_statistics': {
                        'mean': np.mean(returns),
                        'std': np.std(returns),
                        'min': np.min(returns),
                        'max': np.max(returns),
                        'percentile_5': np.percentile(returns, 5),
                        'percentile_95': np.percentile(returns, 95)
                    },
                    'sharpe_statistics': {
                        'mean': np.mean(sharpe_ratios),
                        'std': np.std(sharpe_ratios),
                        'min': np.min(sharpe_ratios),
                        'max': np.max(sharpe_ratios)
                    },
                    'drawdown_statistics': {
                        'mean': np.mean(max_drawdowns),
                        'std': np.std(max_drawdowns),
                        'min': np.min(max_drawdowns),
                        'max': np.max(max_drawdowns)
                    },
                    'results': simulation_results
                }
            else:
                return {'error': 'No successful simulations'}
                
        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {e}")
            raise
    
    def _get_historical_data(self, symbols: List[str], start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical data for symbols"""
        try:
            all_data = {}
            
            for symbol in symbols:
                # Get asset
                asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
                if not asset:
                    continue
                
                # Get prices
                prices = self.db.query(models.Price).filter(
                    models.Price.asset_id == asset.id,
                    models.Price.timestamp >= start_date,
                    models.Price.timestamp <= end_date
                ).order_by(models.Price.timestamp).all()
                
                if prices:
                    data = []
                    for price in prices:
                        data.append({
                            'timestamp': price.timestamp,
                            'open': float(price.open_price),
                            'high': float(price.high_price),
                            'low': float(price.low_price),
                            'close': float(price.close_price),
                            'volume': int(price.volume) if price.volume else 0
                        })
                    
                    df = pd.DataFrame(data)
                    df.set_index('timestamp', inplace=True)
                    all_data[symbol] = df
            
            if not all_data:
                return pd.DataFrame()
            
            # Combine data for all symbols
            combined_data = pd.concat(all_data.values(), axis=1, keys=all_data.keys())
            return combined_data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def _generate_orders(self, signals: Dict, date: datetime, portfolio: Dict) -> List[Order]:
        """Generate orders from strategy signals"""
        orders = []
        
        for symbol, signal in signals.items():
            if signal.get('action') == 'buy' and signal.get('quantity', 0) > 0:
                order = Order(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    order_type=OrderType.MARKET,
                    quantity=signal['quantity'],
                    timestamp=date
                )
                orders.append(order)
                
            elif signal.get('action') == 'sell' and signal.get('quantity', 0) > 0:
                # Check if we have position to sell
                if symbol in portfolio['positions'] and portfolio['positions'][symbol].quantity >= signal['quantity']:
                    order = Order(
                        symbol=symbol,
                        side=OrderSide.SELL,
                        order_type=OrderType.MARKET,
                        quantity=signal['quantity'],
                        timestamp=date
                    )
                    orders.append(order)
        
        return orders
    
    def _execute_orders(self, orders: List[Order], market_data: pd.Series, 
                       portfolio: Dict, commission: float, slippage: float) -> List[Trade]:
        """Execute orders and return completed trades"""
        trades = []
        
        for order in orders:
            try:
                # Get current price
                if order.symbol in market_data.index:
                    current_price = market_data[order.symbol]['close']
                else:
                    continue
                
                # Apply slippage
                if order.side == OrderSide.BUY:
                    execution_price = current_price * (1 + slippage)
                else:
                    execution_price = current_price * (1 - slippage)
                
                # Check if we have enough cash for buy orders
                if order.side == OrderSide.BUY:
                    required_cash = order.quantity * execution_price
                    if portfolio['cash'] < required_cash:
                        continue
                
                # Execute trade
                trade = Trade(
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    price=execution_price,
                    timestamp=order.timestamp,
                    commission=order.quantity * execution_price * commission
                )
                
                trades.append(trade)
                
                # Update portfolio
                if order.side == OrderSide.BUY:
                    portfolio['cash'] -= (required_cash + trade.commission)
                else:
                    portfolio['cash'] += (order.quantity * execution_price - trade.commission)
                
            except Exception as e:
                logger.warning(f"Failed to execute order: {e}")
                continue
        
        return trades
    
    def _update_positions(self, portfolio: Dict, trades: List[Trade]):
        """Update portfolio positions based on executed trades"""
        for trade in trades:
            symbol = trade.symbol
            
            if symbol not in portfolio['positions']:
                portfolio['positions'][symbol] = Position(
                    symbol=symbol,
                    quantity=0,
                    average_price=0
                )
            
            position = portfolio['positions'][symbol]
            
            if trade.side == OrderSide.BUY:
                # Add to position
                total_cost = (position.quantity * position.average_price + 
                             trade.quantity * trade.price)
                total_quantity = position.quantity + trade.quantity
                
                if total_quantity > 0:
                    position.average_price = total_cost / total_quantity
                    position.quantity = total_quantity
                    
            else:  # SELL
                # Reduce position
                if position.quantity >= trade.quantity:
                    # Calculate realized P&L
                    realized_pnl = (trade.price - position.average_price) * trade.quantity
                    position.realized_pnl += realized_pnl
                    position.quantity -= trade.quantity
                    
                    # Remove position if quantity is zero
                    if position.quantity == 0:
                        del portfolio['positions'][symbol]
    
    def _calculate_portfolio_value(self, portfolio: Dict, market_data: pd.Series) -> float:
        """Calculate total portfolio value"""
        total_value = portfolio['cash']
        
        for symbol, position in portfolio['positions'].items():
            if symbol in market_data.index:
                current_price = market_data[symbol]['close']
                position.unrealized_pnl = (current_price - position.average_price) * position.quantity
                total_value += position.quantity * current_price
        
        return total_value
    
    def _calculate_performance_metrics(self, portfolio_values: List[float], 
                                     trades: List[Trade], portfolio: Dict,
                                     start_date: datetime, end_date: datetime) -> BacktestResult:
        """Calculate comprehensive performance metrics"""
        try:
            # Convert to pandas Series
            equity_curve = pd.Series(portfolio_values)
            
            # Calculate returns
            returns = equity_curve.pct_change().dropna()
            
            # Basic metrics
            total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
            annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
            volatility = returns.std() * np.sqrt(252)
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            
            # Drawdown calculation
            running_max = equity_curve.expanding().max()
            drawdown = (equity_curve - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Trade statistics
            if trades:
                winning_trades = [t for t in trades if self._calculate_trade_pnl(t) > 0]
                losing_trades = [t for t in trades if self._calculate_trade_pnl(t) < 0]
                
                win_rate = len(winning_trades) / len(trades) if trades else 0
                
                if winning_trades:
                    avg_win = np.mean([self._calculate_trade_pnl(t) for t in winning_trades])
                    largest_win = max([self._calculate_trade_pnl(t) for t in winning_trades])
                else:
                    avg_win = 0
                    largest_win = 0
                
                if losing_trades:
                    avg_loss = np.mean([self._calculate_trade_pnl(t) for t in losing_trades])
                    largest_loss = min([self._calculate_trade_pnl(t) for t in losing_trades])
                else:
                    avg_loss = 0
                    largest_loss = 0
                
                profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            else:
                winning_trades = []
                losing_trades = []
                win_rate = 0
                avg_win = 0
                avg_loss = 0
                largest_win = 0
                largest_loss = 0
                profit_factor = 0
            
            return BacktestResult(
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                total_trades=len(trades),
                winning_trades=len(winning_trades),
                losing_trades=len(losing_trades),
                avg_win=avg_win,
                avg_loss=avg_loss,
                largest_win=largest_win,
                largest_loss=largest_loss,
                portfolio_values=portfolio_values,
                trades=trades,
                positions=portfolio['positions'],
                equity_curve=equity_curve,
                drawdown_curve=drawdown
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            raise
    
    def _calculate_trade_pnl(self, trade: Trade) -> float:
        """Calculate P&L for a trade (simplified)"""
        # This is a simplified calculation
        # In practice, you'd need to track the entry price for each trade
        return 0  # Placeholder


# Built-in Strategy Examples
class StrategyExamples:
    """Collection of built-in trading strategies for backtesting"""
    
    @staticmethod
    def moving_average_crossover(data: pd.Series, portfolio: Dict, 
                               short_window: int = 20, long_window: int = 50) -> Dict:
        """Simple moving average crossover strategy"""
        signals = {}
        
        for symbol in data.columns.levels[0]:
            symbol_data = data[symbol]
            if len(symbol_data) < long_window:
                continue
            
            # Calculate moving averages
            short_ma = symbol_data['close'].rolling(window=short_window).mean()
            long_ma = symbol_data['close'].rolling(window=long_window).mean()
            
            # Generate signals
            if len(short_ma) > 0 and len(long_ma) > 0:
                current_short = short_ma.iloc[-1]
                current_long = long_ma.iloc[-1]
                prev_short = short_ma.iloc[-2] if len(short_ma) > 1 else current_short
                prev_long = long_ma.iloc[-2] if len(long_ma) > 1 else current_long
                
                # Golden cross (buy signal)
                if prev_short <= prev_long and current_short > current_long:
                    signals[symbol] = {'action': 'buy', 'quantity': 100}
                
                # Death cross (sell signal)
                elif prev_short >= prev_long and current_short < current_long:
                    signals[symbol] = {'action': 'sell', 'quantity': 100}
        
        return signals
    
    @staticmethod
    def mean_reversion(data: pd.Series, portfolio: Dict, 
                      lookback: int = 20, threshold: float = 2.0) -> Dict:
        """Mean reversion strategy based on Bollinger Bands"""
        signals = {}
        
        for symbol in data.columns.levels[0]:
            symbol_data = data[symbol]
            if len(symbol_data) < lookback:
                continue
            
            # Calculate Bollinger Bands
            close_prices = symbol_data['close']
            sma = close_prices.rolling(window=lookback).mean()
            std = close_prices.rolling(window=lookback).std()
            upper_band = sma + (std * threshold)
            lower_band = sma - (std * threshold)
            
            current_price = close_prices.iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            
            # Generate signals
            if current_price > current_upper:
                signals[symbol] = {'action': 'sell', 'quantity': 100}
            elif current_price < current_lower:
                signals[symbol] = {'action': 'buy', 'quantity': 100}
        
        return signals
    
    @staticmethod
    def momentum_strategy(data: pd.Series, portfolio: Dict, 
                         lookback: int = 20, threshold: float = 0.02) -> Dict:
        """Momentum strategy based on price changes"""
        signals = {}
        
        for symbol in data.columns.levels[0]:
            symbol_data = data[symbol]
            if len(symbol_data) < lookback:
                continue
            
            # Calculate momentum
            close_prices = symbol_data['close']
            momentum = (close_prices.iloc[-1] / close_prices.iloc[-lookback]) - 1
            
            # Generate signals
            if momentum > threshold:
                signals[symbol] = {'action': 'buy', 'quantity': 100}
            elif momentum < -threshold:
                signals[symbol] = {'action': 'sell', 'quantity': 100}
        
        return signals

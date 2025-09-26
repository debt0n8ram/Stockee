import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta
from decimal import Decimal
import json

logger = logging.getLogger(__name__)

class BacktestingService:
    def __init__(self, db: Session):
        self.db = db

    def run_backtest(self, strategy_config: Dict) -> Dict:
        """Run a backtest for a trading strategy"""
        try:
            strategy_type = strategy_config.get("strategy_type")
            symbols = strategy_config.get("symbols", [])
            start_date = strategy_config.get("start_date")
            end_date = strategy_config.get("end_date")
            initial_capital = strategy_config.get("initial_capital", 100000)
            commission = strategy_config.get("commission", 0.001)  # 0.1% commission
            
            if not symbols:
                return {"error": "No symbols provided"}
            
            # Parse dates
            start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=365)
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
            
            # Get historical data for all symbols
            historical_data = self._get_historical_data(symbols, start_dt, end_dt)
            
            if not historical_data:
                return {"error": "No historical data available"}
            
            # Run the strategy
            if strategy_type == "moving_average_crossover":
                results = self._run_moving_average_strategy(historical_data, strategy_config, initial_capital, commission)
            elif strategy_type == "mean_reversion":
                results = self._run_mean_reversion_strategy(historical_data, strategy_config, initial_capital, commission)
            elif strategy_type == "momentum":
                results = self._run_momentum_strategy(historical_data, strategy_config, initial_capital, commission)
            elif strategy_type == "buy_and_hold":
                results = self._run_buy_and_hold_strategy(historical_data, strategy_config, initial_capital, commission)
            else:
                return {"error": f"Unknown strategy type: {strategy_type}"}
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(results)
            
            return {
                "strategy_type": strategy_type,
                "symbols": symbols,
                "start_date": start_date,
                "end_date": end_date,
                "initial_capital": initial_capital,
                "results": results,
                "performance_metrics": performance_metrics
            }
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {"error": f"Failed to run backtest: {str(e)}"}

    def _get_historical_data(self, symbols: List[str], start_date: datetime, end_date: datetime) -> Dict:
        """Get historical data for symbols"""
        try:
            historical_data = {}
            
            for symbol in symbols:
                asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
                if not asset:
                    continue
                
                prices = self.db.query(models.Price).filter(
                    models.Price.asset_id == asset.id,
                    models.Price.timestamp >= start_date,
                    models.Price.timestamp <= end_date
                ).order_by(models.Price.timestamp).all()
                
                if prices:
                    historical_data[symbol] = [
                        {
                            'date': price.timestamp,
                            'open': float(price.open_price),
                            'high': float(price.high_price),
                            'low': float(price.low_price),
                            'close': float(price.close_price),
                            'volume': int(price.volume) if price.volume else 0
                        }
                        for price in prices
                    ]
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return {}

    def _run_moving_average_strategy(self, data: Dict, config: Dict, initial_capital: float, commission: float) -> Dict:
        """Run moving average crossover strategy"""
        try:
            symbol = list(data.keys())[0]  # Use first symbol for simplicity
            prices = data[symbol]
            
            if len(prices) < 50:
                return {"error": "Insufficient data for moving average strategy"}
            
            # Strategy parameters
            short_window = config.get("short_window", 10)
            long_window = config.get("long_window", 30)
            
            # Convert to DataFrame
            df = pd.DataFrame(prices)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate moving averages
            df['short_ma'] = df['close'].rolling(window=short_window).mean()
            df['long_ma'] = df['close'].rolling(window=long_window).mean()
            
            # Generate signals
            df['signal'] = 0
            df['signal'][short_window:] = np.where(
                df['short_ma'][short_window:] > df['long_ma'][short_window:], 1, 0
            )
            df['position'] = df['signal'].diff()
            
            # Calculate returns
            df['returns'] = df['close'].pct_change()
            df['strategy_returns'] = df['position'].shift(1) * df['returns']
            
            # Calculate portfolio value
            df['portfolio_value'] = initial_capital
            for i in range(1, len(df)):
                if df.iloc[i]['position'] != 0:
                    # Apply commission
                    commission_cost = df.iloc[i]['portfolio_value'] * commission
                    df.iloc[i, df.columns.get_loc('portfolio_value')] -= commission_cost
                
                if df.iloc[i]['strategy_returns'] != 0:
                    df.iloc[i, df.columns.get_loc('portfolio_value')] *= (1 + df.iloc[i]['strategy_returns'])
                else:
                    df.iloc[i, df.columns.get_loc('portfolio_value')] = df.iloc[i-1]['portfolio_value']
            
            # Prepare results
            trades = []
            current_position = 0
            
            for i, row in df.iterrows():
                if row['position'] != 0:
                    if row['position'] > 0:  # Buy signal
                        current_position = 1
                        trades.append({
                            'date': row['date'].strftime('%Y-%m-%d'),
                            'action': 'BUY',
                            'price': row['close'],
                            'portfolio_value': row['portfolio_value']
                        })
                    else:  # Sell signal
                        current_position = 0
                        trades.append({
                            'date': row['date'].strftime('%Y-%m-%d'),
                            'action': 'SELL',
                            'price': row['close'],
                            'portfolio_value': row['portfolio_value']
                        })
            
            return {
                'trades': trades,
                'final_portfolio_value': df.iloc[-1]['portfolio_value'],
                'total_return': (df.iloc[-1]['portfolio_value'] - initial_capital) / initial_capital * 100,
                'data_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error running moving average strategy: {e}")
            return {"error": f"Strategy execution failed: {str(e)}"}

    def _run_mean_reversion_strategy(self, data: Dict, config: Dict, initial_capital: float, commission: float) -> Dict:
        """Run mean reversion strategy"""
        try:
            symbol = list(data.keys())[0]
            prices = data[symbol]
            
            if len(prices) < 20:
                return {"error": "Insufficient data for mean reversion strategy"}
            
            # Strategy parameters
            lookback = config.get("lookback", 20)
            threshold = config.get("threshold", 2.0)  # Standard deviations
            
            df = pd.DataFrame(prices)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate rolling mean and standard deviation
            df['rolling_mean'] = df['close'].rolling(window=lookback).mean()
            df['rolling_std'] = df['close'].rolling(window=lookback).std()
            
            # Calculate z-score
            df['z_score'] = (df['close'] - df['rolling_mean']) / df['rolling_std']
            
            # Generate signals
            df['signal'] = 0
            df['signal'][lookback:] = np.where(
                df['z_score'][lookback:] < -threshold, 1,  # Buy when oversold
                np.where(df['z_score'][lookback:] > threshold, -1, 0)  # Sell when overbought
            )
            df['position'] = df['signal'].diff()
            
            # Calculate returns and portfolio value
            df['returns'] = df['close'].pct_change()
            df['strategy_returns'] = df['position'].shift(1) * df['returns']
            
            df['portfolio_value'] = initial_capital
            for i in range(1, len(df)):
                if df.iloc[i]['position'] != 0:
                    commission_cost = df.iloc[i]['portfolio_value'] * commission
                    df.iloc[i, df.columns.get_loc('portfolio_value')] -= commission_cost
                
                if df.iloc[i]['strategy_returns'] != 0:
                    df.iloc[i, df.columns.get_loc('portfolio_value')] *= (1 + df.iloc[i]['strategy_returns'])
                else:
                    df.iloc[i, df.columns.get_loc('portfolio_value')] = df.iloc[i-1]['portfolio_value']
            
            # Prepare results
            trades = []
            for i, row in df.iterrows():
                if row['position'] != 0:
                    action = 'BUY' if row['position'] > 0 else 'SELL'
                    trades.append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'action': action,
                        'price': row['close'],
                        'z_score': row['z_score'],
                        'portfolio_value': row['portfolio_value']
                    })
            
            return {
                'trades': trades,
                'final_portfolio_value': df.iloc[-1]['portfolio_value'],
                'total_return': (df.iloc[-1]['portfolio_value'] - initial_capital) / initial_capital * 100,
                'data_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error running mean reversion strategy: {e}")
            return {"error": f"Strategy execution failed: {str(e)}"}

    def _run_momentum_strategy(self, data: Dict, config: Dict, initial_capital: float, commission: float) -> Dict:
        """Run momentum strategy"""
        try:
            symbol = list(data.keys())[0]
            prices = data[symbol]
            
            if len(prices) < 30:
                return {"error": "Insufficient data for momentum strategy"}
            
            # Strategy parameters
            lookback = config.get("lookback", 20)
            threshold = config.get("threshold", 0.02)  # 2% momentum threshold
            
            df = pd.DataFrame(prices)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate momentum
            df['momentum'] = df['close'].pct_change(periods=lookback)
            
            # Generate signals
            df['signal'] = 0
            df['signal'][lookback:] = np.where(
                df['momentum'][lookback:] > threshold, 1,  # Buy on positive momentum
                np.where(df['momentum'][lookback:] < -threshold, -1, 0)  # Sell on negative momentum
            )
            df['position'] = df['signal'].diff()
            
            # Calculate returns and portfolio value
            df['returns'] = df['close'].pct_change()
            df['strategy_returns'] = df['position'].shift(1) * df['returns']
            
            df['portfolio_value'] = initial_capital
            for i in range(1, len(df)):
                if df.iloc[i]['position'] != 0:
                    commission_cost = df.iloc[i]['portfolio_value'] * commission
                    df.iloc[i, df.columns.get_loc('portfolio_value')] -= commission_cost
                
                if df.iloc[i]['strategy_returns'] != 0:
                    df.iloc[i, df.columns.get_loc('portfolio_value')] *= (1 + df.iloc[i]['strategy_returns'])
                else:
                    df.iloc[i, df.columns.get_loc('portfolio_value')] = df.iloc[i-1]['portfolio_value']
            
            # Prepare results
            trades = []
            for i, row in df.iterrows():
                if row['position'] != 0:
                    action = 'BUY' if row['position'] > 0 else 'SELL'
                    trades.append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'action': action,
                        'price': row['close'],
                        'momentum': row['momentum'],
                        'portfolio_value': row['portfolio_value']
                    })
            
            return {
                'trades': trades,
                'final_portfolio_value': df.iloc[-1]['portfolio_value'],
                'total_return': (df.iloc[-1]['portfolio_value'] - initial_capital) / initial_capital * 100,
                'data_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error running momentum strategy: {e}")
            return {"error": f"Strategy execution failed: {str(e)}"}

    def _run_buy_and_hold_strategy(self, data: Dict, config: Dict, initial_capital: float, commission: float) -> Dict:
        """Run buy and hold strategy"""
        try:
            symbol = list(data.keys())[0]
            prices = data[symbol]
            
            if len(prices) < 2:
                return {"error": "Insufficient data for buy and hold strategy"}
            
            df = pd.DataFrame(prices)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Buy at the beginning
            initial_price = df.iloc[0]['close']
            shares = (initial_capital * (1 - commission)) / initial_price
            
            # Calculate portfolio value over time
            df['portfolio_value'] = df['close'] * shares
            
            # Prepare results
            trades = [
                {
                    'date': df.iloc[0]['date'].strftime('%Y-%m-%d'),
                    'action': 'BUY',
                    'price': initial_price,
                    'shares': shares,
                    'portfolio_value': df.iloc[0]['portfolio_value']
                }
            ]
            
            return {
                'trades': trades,
                'final_portfolio_value': df.iloc[-1]['portfolio_value'],
                'total_return': (df.iloc[-1]['portfolio_value'] - initial_capital) / initial_capital * 100,
                'data_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error running buy and hold strategy: {e}")
            return {"error": f"Strategy execution failed: {str(e)}"}

    def _calculate_performance_metrics(self, results: Dict) -> Dict:
        """Calculate performance metrics for backtest results"""
        try:
            if "error" in results:
                return {"error": results["error"]}
            
            final_value = results.get("final_portfolio_value", 0)
            total_return = results.get("total_return", 0)
            trades = results.get("trades", [])
            
            # Calculate additional metrics
            num_trades = len(trades)
            winning_trades = 0
            losing_trades = 0
            
            for i in range(1, len(trades)):
                if trades[i]['action'] == 'SELL':
                    prev_trade = trades[i-1]
                    if prev_trade['action'] == 'BUY':
                        if trades[i]['portfolio_value'] > prev_trade['portfolio_value']:
                            winning_trades += 1
                        else:
                            losing_trades += 1
            
            win_rate = (winning_trades / (winning_trades + losing_trades)) * 100 if (winning_trades + losing_trades) > 0 else 0
            
            # Calculate Sharpe ratio (simplified)
            sharpe_ratio = total_return / 20 if total_return > 0 else 0  # Simplified calculation
            
            # Calculate max drawdown (simplified)
            max_drawdown = 0
            if trades:
                peak_value = trades[0]['portfolio_value']
                for trade in trades:
                    if trade['portfolio_value'] > peak_value:
                        peak_value = trade['portfolio_value']
                    else:
                        drawdown = (peak_value - trade['portfolio_value']) / peak_value * 100
                        max_drawdown = max(max_drawdown, drawdown)
            
            return {
                "total_return": round(total_return, 2),
                "final_portfolio_value": round(final_value, 2),
                "num_trades": num_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "max_drawdown": round(max_drawdown, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {"error": f"Failed to calculate metrics: {str(e)}"}

    def get_available_strategies(self) -> Dict:
        """Get list of available backtesting strategies"""
        return {
            "strategies": [
                {
                    "name": "Moving Average Crossover",
                    "type": "moving_average_crossover",
                    "description": "Buy when short MA crosses above long MA, sell when it crosses below",
                    "parameters": {
                        "short_window": {"type": "integer", "default": 10, "description": "Short moving average period"},
                        "long_window": {"type": "integer", "default": 30, "description": "Long moving average period"}
                    }
                },
                {
                    "name": "Mean Reversion",
                    "type": "mean_reversion",
                    "description": "Buy when price is oversold, sell when overbought",
                    "parameters": {
                        "lookback": {"type": "integer", "default": 20, "description": "Lookback period for mean calculation"},
                        "threshold": {"type": "float", "default": 2.0, "description": "Standard deviation threshold"}
                    }
                },
                {
                    "name": "Momentum",
                    "type": "momentum",
                    "description": "Buy on positive momentum, sell on negative momentum",
                    "parameters": {
                        "lookback": {"type": "integer", "default": 20, "description": "Momentum calculation period"},
                        "threshold": {"type": "float", "default": 0.02, "description": "Momentum threshold (2%)"}
                    }
                },
                {
                    "name": "Buy and Hold",
                    "type": "buy_and_hold",
                    "description": "Buy at the beginning and hold until the end",
                    "parameters": {}
                }
            ]
        }

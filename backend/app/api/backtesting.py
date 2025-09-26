from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.backtesting_engine import BacktestingEngine, StrategyExamples
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/backtesting", tags=["backtesting"])

class BacktestRequest(BaseModel):
    strategy_name: str
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000
    commission: float = 0.001
    slippage: float = 0.0005
    strategy_params: Dict[str, Any] = {}

class OptimizationRequest(BaseModel):
    strategy_name: str
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    parameter_ranges: Dict[str, List]  # [min, max] for each parameter
    optimization_metric: str = "sharpe_ratio"
    n_trials: int = 100
    initial_capital: float = 100000
    commission: float = 0.001
    slippage: float = 0.0005

class WalkForwardRequest(BaseModel):
    strategy_name: str
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    train_period: int = 252  # 1 year
    test_period: int = 63    # 3 months
    step_size: int = 21      # 1 month
    strategy_params: Dict[str, Any] = {}
    initial_capital: float = 100000
    commission: float = 0.001
    slippage: float = 0.0005

class MonteCarloRequest(BaseModel):
    strategy_name: str
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    n_simulations: int = 1000
    strategy_params: Dict[str, Any] = {}
    initial_capital: float = 100000
    commission: float = 0.001
    slippage: float = 0.0005

@router.post("/run")
async def run_backtest(
    request: BacktestRequest,
    db: Session = Depends(get_db)
):
    """Run a backtest for a given strategy"""
    try:
        engine = BacktestingEngine(db)
        
        # Get strategy function
        strategy_func = get_strategy_function(request.strategy_name)
        if not strategy_func:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy_name}")
        
        # Run backtest
        result = engine.run_backtest(
            strategy=strategy_func,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            commission=request.commission,
            slippage=request.slippage,
            **request.strategy_params
        )
        
        # Convert result to dict for JSON serialization
        return {
            "success": True,
            "result": {
                "total_return": result.total_return,
                "annualized_return": result.annualized_return,
                "volatility": result.volatility,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "win_rate": result.win_rate,
                "profit_factor": result.profit_factor,
                "total_trades": result.total_trades,
                "winning_trades": result.winning_trades,
                "losing_trades": result.losing_trades,
                "avg_win": result.avg_win,
                "avg_loss": result.avg_loss,
                "largest_win": result.largest_win,
                "largest_loss": result.largest_loss,
                "portfolio_values": result.portfolio_values,
                "equity_curve": result.equity_curve.tolist(),
                "drawdown_curve": result.drawdown_curve.tolist(),
                "trades_summary": [
                    {
                        "symbol": trade.symbol,
                        "side": trade.side.value,
                        "quantity": trade.quantity,
                        "price": trade.price,
                        "timestamp": trade.timestamp.isoformat(),
                        "commission": trade.commission
                    } for trade in result.trades
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def optimize_strategy(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Optimize strategy parameters"""
    try:
        engine = BacktestingEngine(db)
        
        # Get strategy function
        strategy_func = get_strategy_function(request.strategy_name)
        if not strategy_func:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy_name}")
        
        # Convert parameter ranges to tuples
        param_ranges = {}
        for param_name, range_values in request.parameter_ranges.items():
            if len(range_values) != 2:
                raise HTTPException(status_code=400, detail=f"Parameter {param_name} must have [min, max] values")
            param_ranges[param_name] = (range_values[0], range_values[1])
        
        # Run optimization
        result = engine.optimize_strategy(
            strategy=strategy_func,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            parameter_ranges=param_ranges,
            optimization_metric=request.optimization_metric,
            n_trials=request.n_trials
        )
        
        return {
            "success": True,
            "optimization_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/walk-forward")
async def walk_forward_analysis(
    request: WalkForwardRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Perform walk-forward analysis"""
    try:
        engine = BacktestingEngine(db)
        
        # Get strategy function
        strategy_func = get_strategy_function(request.strategy_name)
        if not strategy_func:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy_name}")
        
        # Run walk-forward analysis
        result = engine.walk_forward_analysis(
            strategy=strategy_func,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            train_period=request.train_period,
            test_period=request.test_period,
            step_size=request.step_size,
            **request.strategy_params
        )
        
        return {
            "success": True,
            "walk_forward_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monte-carlo")
async def monte_carlo_simulation(
    request: MonteCarloRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Run Monte Carlo simulation"""
    try:
        engine = BacktestingEngine(db)
        
        # Get strategy function
        strategy_func = get_strategy_function(request.strategy_name)
        if not strategy_func:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy_name}")
        
        # Run Monte Carlo simulation
        result = engine.monte_carlo_simulation(
            strategy=strategy_func,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            n_simulations=request.n_simulations,
            **request.strategy_params
        )
        
        return {
            "success": True,
            "monte_carlo_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/available")
async def get_available_strategies():
    """Get list of available built-in strategies"""
    return {
        "strategies": [
            {
                "name": "moving_average_crossover",
                "description": "Simple moving average crossover strategy",
                "parameters": {
                    "short_window": {"type": "int", "default": 20, "description": "Short moving average window"},
                    "long_window": {"type": "int", "default": 50, "description": "Long moving average window"}
                }
            },
            {
                "name": "mean_reversion",
                "description": "Mean reversion strategy based on Bollinger Bands",
                "parameters": {
                    "lookback": {"type": "int", "default": 20, "description": "Lookback period for Bollinger Bands"},
                    "threshold": {"type": "float", "default": 2.0, "description": "Standard deviation threshold"}
                }
            },
            {
                "name": "momentum_strategy",
                "description": "Momentum strategy based on price changes",
                "parameters": {
                    "lookback": {"type": "int", "default": 20, "description": "Lookback period for momentum calculation"},
                    "threshold": {"type": "float", "default": 0.02, "description": "Momentum threshold for signals"}
                }
            }
        ]
    }

@router.get("/performance-metrics")
async def get_performance_metrics_explanation():
    """Get explanation of performance metrics"""
    return {
        "metrics": {
            "total_return": {
                "description": "Total return over the backtest period",
                "formula": "(Final Value - Initial Value) / Initial Value"
            },
            "annualized_return": {
                "description": "Annualized return rate",
                "formula": "(1 + Total Return)^(252 / Trading Days) - 1"
            },
            "volatility": {
                "description": "Annualized volatility (standard deviation of returns)",
                "formula": "Std(Returns) * sqrt(252)"
            },
            "sharpe_ratio": {
                "description": "Risk-adjusted return measure",
                "formula": "Annualized Return / Volatility"
            },
            "max_drawdown": {
                "description": "Maximum peak-to-trough decline",
                "formula": "Min((Value - Running Max) / Running Max)"
            },
            "win_rate": {
                "description": "Percentage of profitable trades",
                "formula": "Winning Trades / Total Trades"
            },
            "profit_factor": {
                "description": "Ratio of gross profit to gross loss",
                "formula": "Average Win / Average Loss"
            }
        }
    }

@router.get("/symbols/available")
async def get_available_symbols(
    db: Session = Depends(get_db)
):
    """Get list of available symbols for backtesting"""
    try:
        from app.db import models
        
        # Get all assets with price data
        assets = db.query(models.Asset).join(models.Price).distinct().all()
        
        symbols = []
        for asset in assets:
            # Get price count for this asset
            price_count = db.query(models.Price).filter(models.Price.asset_id == asset.id).count()
            
            if price_count > 0:
                symbols.append({
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "price_count": price_count,
                    "asset_type": asset.asset_type
                })
        
        return {
            "symbols": symbols,
            "total_count": len(symbols)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare-strategies")
async def compare_strategies(
    strategies: List[BacktestRequest],
    db: Session = Depends(get_db)
):
    """Compare multiple strategies side by side"""
    try:
        engine = BacktestingEngine(db)
        results = []
        
        for strategy_request in strategies:
            # Get strategy function
            strategy_func = get_strategy_function(strategy_request.strategy_name)
            if not strategy_func:
                continue
            
            # Run backtest
            result = engine.run_backtest(
                strategy=strategy_func,
                symbols=strategy_request.symbols,
                start_date=strategy_request.start_date,
                end_date=strategy_request.end_date,
                initial_capital=strategy_request.initial_capital,
                commission=strategy_request.commission,
                slippage=strategy_request.slippage,
                **strategy_request.strategy_params
            )
            
            results.append({
                "strategy_name": strategy_request.strategy_name,
                "strategy_params": strategy_request.strategy_params,
                "total_return": result.total_return,
                "annualized_return": result.annualized_return,
                "volatility": result.volatility,
                "sharpe_ratio": result.sharpe_ratio,
                "max_drawdown": result.max_drawdown,
                "win_rate": result.win_rate,
                "total_trades": result.total_trades
            })
        
        # Sort by Sharpe ratio
        results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        
        return {
            "success": True,
            "comparison_results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_strategy_function(strategy_name: str):
    """Get strategy function by name"""
    strategy_map = {
        "moving_average_crossover": StrategyExamples.moving_average_crossover,
        "mean_reversion": StrategyExamples.mean_reversion,
        "momentum_strategy": StrategyExamples.momentum_strategy
    }
    
    return strategy_map.get(strategy_name)
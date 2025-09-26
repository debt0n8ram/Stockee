from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.options_trading_service import OptionsTradingService, OptionStrategy, OptionType
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/options", tags=["options-trading"])

class OptionChainRequest(BaseModel):
    symbol: str
    expiration_date: Optional[datetime] = None

class CreateStrategyRequest(BaseModel):
    strategy_type: str
    symbol: str
    positions: List[Dict[str, Any]]

class GreeksRequest(BaseModel):
    spot_price: float
    strike_price: float
    time_to_expiry: float  # days
    risk_free_rate: float
    volatility: float
    option_type: str

class ImpliedVolatilityRequest(BaseModel):
    market_price: float
    spot_price: float
    strike_price: float
    time_to_expiry: float
    risk_free_rate: float
    option_type: str

@router.get("/chain/{symbol}")
async def get_option_chain(
    symbol: str,
    expiration_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """Get option chain for a symbol"""
    try:
        service = OptionsTradingService(db)
        result = service.get_option_chain(symbol, expiration_date)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-greeks")
async def calculate_greeks(
    request: GreeksRequest,
    db: Session = Depends(get_db)
):
    """Calculate option Greeks using Black-Scholes"""
    try:
        service = OptionsTradingService(db)
        
        option_type = OptionType.CALL if request.option_type.lower() == "call" else OptionType.PUT
        
        result = service.calculate_black_scholes(
            spot_price=request.spot_price,
            strike_price=request.strike_price,
            time_to_expiry=request.time_to_expiry,
            risk_free_rate=request.risk_free_rate,
            volatility=request.volatility,
            option_type=option_type
        )
        
        return {
            "success": True,
            "greeks": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-implied-volatility")
async def calculate_implied_volatility(
    request: ImpliedVolatilityRequest,
    db: Session = Depends(get_db)
):
    """Calculate implied volatility"""
    try:
        service = OptionsTradingService(db)
        
        option_type = OptionType.CALL if request.option_type.lower() == "call" else OptionType.PUT
        
        implied_vol = service.calculate_implied_volatility(
            market_price=request.market_price,
            spot_price=request.spot_price,
            strike_price=request.strike_price,
            time_to_expiry=request.time_to_expiry,
            risk_free_rate=request.risk_free_rate,
            option_type=option_type
        )
        
        return {
            "success": True,
            "implied_volatility": implied_vol
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategy/create")
async def create_option_strategy(
    request: CreateStrategyRequest,
    db: Session = Depends(get_db)
):
    """Create an options strategy"""
    try:
        service = OptionsTradingService(db)
        
        # Get current price
        current_price = service._get_current_price(request.symbol)
        if not current_price:
            raise HTTPException(status_code=400, detail=f"No current price available for {request.symbol}")
        
        # Create strategy
        strategy_type = OptionStrategy(request.strategy_type)
        strategy = service.create_option_strategy(
            strategy_type=strategy_type,
            symbol=request.symbol,
            positions=request.positions,
            current_price=current_price
        )
        
        # Calculate strategy Greeks
        strategy_greeks = service.calculate_strategy_greeks(strategy)
        
        return {
            "success": True,
            "strategy": {
                "name": strategy.name,
                "strategy_type": strategy.strategy_type.value,
                "max_profit": strategy.max_profit,
                "max_loss": strategy.max_loss,
                "breakeven_points": strategy.breakeven_points,
                "profit_loss_curve": strategy.profit_loss_curve,
                "positions": [
                    {
                        "symbol": pos.contract.symbol,
                        "option_type": pos.contract.option_type.value,
                        "strike_price": pos.contract.strike_price,
                        "quantity": pos.quantity,
                        "entry_price": pos.entry_price,
                        "current_price": pos.current_price,
                        "unrealized_pnl": pos.unrealized_pnl
                    } for pos in strategy.positions
                ],
                "greeks": strategy_greeks
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/templates")
async def get_strategy_templates():
    """Get predefined strategy templates"""
    try:
        service = OptionsTradingService(None)  # No DB needed for templates
        templates = service.get_strategy_templates()
        
        return {
            "success": True,
            "templates": templates
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies/available")
async def get_available_strategies():
    """Get list of available option strategies"""
    return {
        "strategies": [
            {
                "name": "Long Call",
                "type": "long_call",
                "description": "Buy a call option to profit from upward price movement"
            },
            {
                "name": "Long Put", 
                "type": "long_put",
                "description": "Buy a put option to profit from downward price movement"
            },
            {
                "name": "Short Call",
                "type": "short_call", 
                "description": "Sell a call option to collect premium"
            },
            {
                "name": "Short Put",
                "type": "short_put",
                "description": "Sell a put option to collect premium"
            },
            {
                "name": "Covered Call",
                "type": "covered_call",
                "description": "Sell a call option against owned stock"
            },
            {
                "name": "Protective Put",
                "type": "protective_put",
                "description": "Buy a put option to protect stock position"
            },
            {
                "name": "Straddle",
                "type": "straddle",
                "description": "Buy both call and put with same strike and expiration"
            },
            {
                "name": "Strangle",
                "type": "strangle",
                "description": "Buy call and put with different strikes, same expiration"
            },
            {
                "name": "Butterfly",
                "type": "butterfly",
                "description": "Three-leg strategy with limited risk and reward"
            },
            {
                "name": "Iron Condor",
                "type": "iron_condor",
                "description": "Sell call spread and put spread for income"
            },
            {
                "name": "Bull Call Spread",
                "type": "bull_call_spread",
                "description": "Buy call, sell higher strike call"
            },
            {
                "name": "Bear Call Spread",
                "type": "bear_call_spread",
                "description": "Sell call, buy higher strike call"
            },
            {
                "name": "Bull Put Spread",
                "type": "bull_put_spread",
                "description": "Sell put, buy lower strike put"
            },
            {
                "name": "Bear Put Spread",
                "type": "bear_put_spread",
                "description": "Buy put, sell lower strike put"
            }
        ]
    }

@router.get("/symbols/available")
async def get_available_option_symbols(
    db: Session = Depends(get_db)
):
    """Get list of symbols available for options trading"""
    try:
        from app.db import models
        
        # Get assets that could have options (stocks, ETFs)
        assets = db.query(models.Asset).filter(
            models.Asset.asset_type.in_(['stock', 'etf'])
        ).all()
        
        symbols = []
        for asset in assets:
            # Check if asset has recent price data
            recent_price = db.query(models.Price).filter(
                models.Price.asset_id == asset.id
            ).order_by(models.Price.timestamp.desc()).first()
            
            if recent_price:
                symbols.append({
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "asset_type": asset.asset_type,
                    "current_price": float(recent_price.close_price)
                })
        
        return {
            "symbols": symbols,
            "total_count": len(symbols)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/education/strategies")
async def get_strategy_education():
    """Get educational content about options strategies"""
    return {
        "strategies": {
            "basic": [
                {
                    "name": "Long Call",
                    "description": "Buy a call option to profit from upward price movement",
                    "when_to_use": "When you expect the stock price to rise significantly",
                    "risk_reward": "Limited risk (premium paid), unlimited profit potential",
                    "example": "Buy AAPL $150 call for $5 when stock is at $145"
                },
                {
                    "name": "Long Put",
                    "description": "Buy a put option to profit from downward price movement", 
                    "when_to_use": "When you expect the stock price to fall significantly",
                    "risk_reward": "Limited risk (premium paid), limited profit potential",
                    "example": "Buy AAPL $140 put for $3 when stock is at $145"
                }
            ],
            "income": [
                {
                    "name": "Covered Call",
                    "description": "Sell a call option against owned stock",
                    "when_to_use": "When you own stock and want to generate income",
                    "risk_reward": "Limited upside, unlimited downside risk",
                    "example": "Own 100 AAPL shares, sell $155 call for $2"
                },
                {
                    "name": "Cash-Secured Put",
                    "description": "Sell a put option with cash to buy stock",
                    "when_to_use": "When you want to buy stock at a lower price",
                    "risk_reward": "Limited profit (premium), limited loss",
                    "example": "Sell AAPL $140 put for $3, ready to buy at $140"
                }
            ],
            "volatility": [
                {
                    "name": "Long Straddle",
                    "description": "Buy both call and put with same strike",
                    "when_to_use": "When you expect high volatility but unsure of direction",
                    "risk_reward": "Limited risk, unlimited profit potential",
                    "example": "Buy AAPL $150 call and put when expecting earnings move"
                },
                {
                    "name": "Short Straddle",
                    "description": "Sell both call and put with same strike",
                    "when_to_use": "When you expect low volatility",
                    "risk_reward": "Limited profit, unlimited risk",
                    "example": "Sell AAPL $150 call and put when expecting sideways movement"
                }
            ]
        }
    }

@router.get("/risk-calculator")
async def calculate_option_risk(
    symbol: str,
    option_type: str,
    strike_price: float,
    expiration_date: datetime,
    quantity: int,
    entry_price: float,
    current_stock_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Calculate risk metrics for an option position"""
    try:
        service = OptionsTradingService(db)
        
        # Get current stock price if not provided
        if not current_stock_price:
            current_stock_price = service._get_current_price(symbol)
            if not current_stock_price:
                raise HTTPException(status_code=400, detail=f"No current price available for {symbol}")
        
        # Calculate time to expiry
        time_to_expiry = (expiration_date - datetime.now()).days
        
        # Calculate intrinsic and time value
        if option_type.lower() == "call":
            intrinsic_value = max(0, current_stock_price - strike_price)
        else:
            intrinsic_value = max(0, strike_price - current_stock_price)
        
        time_value = entry_price - intrinsic_value
        
        # Calculate P&L
        current_option_value = intrinsic_value  # Simplified - in practice, use market price
        unrealized_pnl = (current_option_value - entry_price) * quantity
        
        # Calculate risk metrics
        max_loss = entry_price * quantity  # For long positions
        max_profit = "Unlimited" if option_type.lower() == "call" else strike_price * quantity
        
        return {
            "success": True,
            "risk_metrics": {
                "symbol": symbol,
                "option_type": option_type,
                "strike_price": strike_price,
                "quantity": quantity,
                "entry_price": entry_price,
                "current_stock_price": current_stock_price,
                "intrinsic_value": intrinsic_value,
                "time_value": time_value,
                "unrealized_pnl": unrealized_pnl,
                "max_loss": max_loss,
                "max_profit": max_profit,
                "days_to_expiry": time_to_expiry,
                "breakeven_price": strike_price + entry_price if option_type.lower() == "call" else strike_price - entry_price
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

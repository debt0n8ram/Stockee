from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.options_service import OptionsService
from app.db import models
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/options", tags=["options"])

class OptionLeg(BaseModel):
    option_type: str  # "call" or "put"
    action: str  # "buy" or "sell"
    strike: float
    premium: float
    quantity: int = 1

class OptionStrategy(BaseModel):
    strategy_type: str
    legs: List[OptionLeg]

@router.get("/symbols/available")
async def get_available_symbols(db: Session = Depends(get_db)):
    """Get list of symbols with available options"""
    # Mock available symbols
    symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "has_options": True},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "has_options": True},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "has_options": True},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "has_options": True},
        {"symbol": "TSLA", "name": "Tesla Inc.", "has_options": True},
        {"symbol": "META", "name": "Meta Platforms Inc.", "has_options": True},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "has_options": True},
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "has_options": True},
        {"symbol": "QQQ", "name": "Invesco QQQ Trust", "has_options": True},
        {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "has_options": True}
    ]
    
    return {"symbols": symbols}

@router.get("/strategies/templates")
async def get_strategy_templates(db: Session = Depends(get_db)):
    """Get predefined option strategy templates"""
    templates = [
        {
            "name": "Long Call",
            "description": "Buy a call option to profit from upward price movement",
            "legs": [
                {"option_type": "call", "action": "buy", "strike": 0, "premium": 0, "quantity": 1}
            ],
            "max_profit": "Unlimited",
            "max_loss": "Premium paid",
            "breakeven": "Strike + Premium"
        },
        {
            "name": "Long Put",
            "description": "Buy a put option to profit from downward price movement",
            "legs": [
                {"option_type": "put", "action": "buy", "strike": 0, "premium": 0, "quantity": 1}
            ],
            "max_profit": "Strike - Premium",
            "max_loss": "Premium paid",
            "breakeven": "Strike - Premium"
        },
        {
            "name": "Covered Call",
            "description": "Sell a call option against owned stock",
            "legs": [
                {"option_type": "call", "action": "sell", "strike": 0, "premium": 0, "quantity": 1}
            ],
            "max_profit": "Premium + (Strike - Stock Price)",
            "max_loss": "Stock Price - Premium",
            "breakeven": "Stock Price - Premium"
        },
        {
            "name": "Protective Put",
            "description": "Buy a put option to protect against downside risk",
            "legs": [
                {"option_type": "put", "action": "buy", "strike": 0, "premium": 0, "quantity": 1}
            ],
            "max_profit": "Unlimited",
            "max_loss": "Stock Price - Strike + Premium",
            "breakeven": "Stock Price + Premium"
        },
        {
            "name": "Straddle",
            "description": "Buy both call and put options with same strike",
            "legs": [
                {"option_type": "call", "action": "buy", "strike": 0, "premium": 0, "quantity": 1},
                {"option_type": "put", "action": "buy", "strike": 0, "premium": 0, "quantity": 1}
            ],
            "max_profit": "Unlimited",
            "max_loss": "Total Premium Paid",
            "breakeven": "Strike ± Total Premium"
        }
    ]
    
    return {"templates": templates}

@router.post("/strategy/calculate")
async def calculate_option_strategy(
    strategy: OptionStrategy,
    db: Session = Depends(get_db)
):
    """Calculate option strategy P&L and risk metrics"""
    options_service = OptionsService(db)
    result = options_service.calculate_option_strategy(strategy.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/strategies")
async def get_option_strategies():
    """Get list of common option strategies"""
    options_service = OptionsService()
    return options_service.get_option_strategies()

@router.get("/expirations/{symbol}")
async def get_expiration_dates(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get available expiration dates for a symbol"""
    # Generate common expiration dates (next 4 Fridays, monthly, quarterly)
    today = datetime.now()
    expirations = []
    
    # Next 4 Fridays
    for i in range(4):
        days_ahead = 4 - today.weekday() + (i * 7)
        if days_ahead <= 0:
            days_ahead += 7
        exp_date = today + timedelta(days=days_ahead)
        expirations.append({
            "date": exp_date.strftime("%Y-%m-%d"),
            "days_to_expiration": (exp_date - today).days,
            "type": "weekly"
        })
    
    # Monthly expirations (third Friday of each month)
    for i in range(6):
        month = today.month + i
        year = today.year
        if month > 12:
            month -= 12
            year += 1
        
        # Find third Friday of the month
        first_day = datetime(year, month, 1)
        first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
        third_friday = first_friday + timedelta(days=14)
        
        if third_friday > today:
            expirations.append({
                "date": third_friday.strftime("%Y-%m-%d"),
                "days_to_expiration": (third_friday - today).days,
                "type": "monthly"
            })
    
    return {
        "symbol": symbol.upper(),
        "expiration_dates": expirations
    }

@router.get("/greeks/{symbol}")
async def calculate_greeks(
    symbol: str,
    strike: float,
    expiration_date: str,
    option_type: str = Query(..., description="call or put"),
    db: Session = Depends(get_db)
):
    """Calculate option Greeks for a specific option"""
    options_service = OptionsService(db)
    
    # Get current stock price
    asset = options_service.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    latest_price = options_service.db.query(models.Price).filter(
        models.Price.asset_id == asset.id
    ).order_by(models.Price.timestamp.desc()).first()
    
    if not latest_price:
        raise HTTPException(status_code=404, detail="No price data available")
    
    current_price = float(latest_price.close_price)
    
    # Calculate time to expiration
    exp_date = datetime.strptime(expiration_date, "%Y-%m-%d")
    time_to_exp = (exp_date - datetime.now()).days / 365.0
    
    if time_to_exp <= 0:
        raise HTTPException(status_code=400, detail="Expiration date must be in the future")
    
    # Calculate Greeks
    greeks = options_service._calculate_greeks(current_price, strike, time_to_exp, option_type)
    
    return {
        "symbol": symbol.upper(),
        "strike": strike,
        "expiration_date": expiration_date,
        "option_type": option_type,
        "current_price": current_price,
        "time_to_expiration": round(time_to_exp * 365, 1),
        "greeks": greeks
    }

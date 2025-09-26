from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db import models, schemas
from app.services.market_data_service import MarketDataService

router = APIRouter()

@router.get("/search/{query}")
async def search_assets(
    query: str,
    asset_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search for assets by symbol or name"""
    market_service = MarketDataService(db)
    return market_service.search_assets(query, asset_type, limit)

@router.get("/price/{symbol}")
async def get_current_price(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get current price for an asset"""
    market_service = MarketDataService(db)
    price_data = market_service.get_current_price(symbol)
    if not price_data:
        raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
    return price_data

@router.get("/price/{symbol}/history")
async def get_price_history(
    symbol: str,
    days: int = 30,
    interval: str = "1d",
    db: Session = Depends(get_db)
):
    """Get historical price data for an asset"""
    market_service = MarketDataService(db)
    return market_service.get_price_history(symbol, days, interval)

@router.get("/price/{symbol}/chart")
async def get_chart_data(
    symbol: str,
    days: int = 30,
    interval: str = "1d",
    db: Session = Depends(get_db)
):
    """Get formatted chart data for frontend"""
    # Simple mock implementation for now
    import random
    from datetime import datetime, timedelta
    
    # Get current price
    market_service = MarketDataService(db)
    current_price_data = market_service.get_current_price(symbol)
    base_price = current_price_data.get('price', 100.0) if current_price_data else 100.0
    
    # Generate mock historical data
    data = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i-1)
        
        # Add some realistic price movement
        price_change = random.uniform(-0.05, 0.05)  # ±5% daily change
        price = base_price * (1 + price_change * (i / days))
        
        # Generate OHLC data
        high = price * random.uniform(1.0, 1.03)
        low = price * random.uniform(0.97, 1.0)
        open_price = price * random.uniform(0.98, 1.02)
        close_price = price
        
        # Generate volume
        volume = random.randint(1000000, 10000000)
        
        data.append({
            "timestamp": date.isoformat(),
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close_price, 2),
            "volume": volume
        })
    
    # Calculate change from first to last day
    if len(data) > 1:
        change = data[-1]["close"] - data[0]["close"]
        change_percent = (change / data[0]["close"]) * 100
    else:
        change = 0
        change_percent = 0
    
    return {
        "symbol": symbol,
        "data": data,
        "current_price": data[-1]["close"] if data else base_price,
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "volume": sum(d["volume"] for d in data) // len(data) if data else 0,
        "high": max(d["high"] for d in data) if data else base_price,
        "low": min(d["low"] for d in data) if data else base_price,
        "open": data[0]["open"] if data else base_price,
        "market_cap": base_price * 1000000000  # Mock market cap
    }

@router.get("/market-status")
async def get_market_status():
    """Get current market status (open/closed)"""
    now = datetime.now()
    # Simple market hours check (9:30 AM - 4:00 PM ET, Monday-Friday)
    is_market_open = (
        now.weekday() < 5 and  # Monday = 0, Friday = 4
        9.5 <= now.hour + now.minute/60 <= 16  # 9:30 AM to 4:00 PM
    )
    
    return {
        "is_open": is_market_open,
        "next_open": "09:30 ET" if not is_market_open else None,
        "next_close": "16:00 ET" if is_market_open else None,
        "timestamp": now
    }

@router.get("/trending")
async def get_trending_assets(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get trending/most active assets"""
    market_service = MarketDataService(db)
    return market_service.get_trending_assets(limit)

@router.get("/news/{symbol}")
async def get_asset_news(
    symbol: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get news for a specific asset"""
    market_service = MarketDataService(db)
    return market_service.get_asset_news(symbol, limit)

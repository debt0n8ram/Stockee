"""
Historical Data API Endpoints
Provides comprehensive historical data for stocks and crypto
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.historical_data_service import HistoricalDataService
from typing import Optional

router = APIRouter(prefix="/api/historical", tags=["historical-data"])

# Initialize service
historical_service = HistoricalDataService()

@router.get("/stocks/{symbol}")
async def get_stock_historical_data(
    symbol: str,
    days: int = Query(30, description="Number of days of historical data"),
    interval: str = Query("1d", description="Data interval: 1d, 1h, 1m"),
    db: Session = Depends(get_db)
):
    """Get comprehensive stock historical data from multiple APIs"""
    try:
        return await historical_service.get_stock_historical_data(symbol, days, interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crypto/{symbol}")
async def get_crypto_historical_data(
    symbol: str,
    days: int = Query(30, description="Number of days of historical data"),
    interval: str = Query("1d", description="Data interval: 1d, 1h, 1m"),
    db: Session = Depends(get_db)
):
    """Get comprehensive crypto historical data from multiple APIs"""
    try:
        return await historical_service.get_crypto_historical_data(symbol, days, interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare/{symbols}")
async def get_historical_comparison(
    symbols: str,
    days: int = Query(30, description="Number of days to compare"),
    interval: str = Query("1d", description="Data interval"),
    db: Session = Depends(get_db)
):
    """Compare historical performance of multiple assets"""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    comparison_data = {}
    
    for symbol in symbol_list:
        try:
            # Determine if it's a stock or crypto
            if symbol in ["BTC", "ETH", "SOL", "ADA", "MATIC", "AVAX", "DOGE", "SHIB", "LINK", "UNI", "LTC"]:
                data = await historical_service.get_crypto_historical_data(symbol, days, interval)
            else:
                data = await historical_service.get_stock_historical_data(symbol, days, interval)
            
            comparison_data[symbol] = data
        except Exception as e:
            comparison_data[symbol] = {"error": str(e)}
    
    return {
        "comparison": comparison_data,
        "symbols": symbol_list,
        "days": days,
        "interval": interval,
        "timestamp": datetime.now().isoformat()
    }

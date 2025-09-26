from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.charting_service import ChartingService
from typing import Optional

router = APIRouter(prefix="/api/charting", tags=["charting"])

@router.get("/candlestick/{symbol}")
async def get_candlestick_data(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe: 1m, 5m, 15m, 1h, 4h, 1d, 1w"),
    days: int = Query(30, description="Number of days to fetch"),
    db: Session = Depends(get_db)
):
    """Get candlestick data for advanced charting"""
    charting_service = ChartingService(db)
    data = charting_service.get_candlestick_data(symbol.upper(), timeframe, days)
    
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    
    return data

@router.get("/patterns/{symbol}")
async def get_chart_patterns(
    symbol: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get detected chart patterns"""
    charting_service = ChartingService(db)
    patterns = charting_service.get_chart_patterns(symbol.upper(), days)
    
    if "error" in patterns:
        raise HTTPException(status_code=400, detail=patterns["error"])
    
    return patterns

@router.get("/volume-profile/{symbol}")
async def get_volume_profile(
    symbol: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get volume profile data"""
    charting_service = ChartingService(db)
    profile = charting_service.get_volume_profile(symbol.upper(), days)
    
    if "error" in profile:
        raise HTTPException(status_code=400, detail=profile["error"])
    
    return profile

@router.get("/indicators/{symbol}")
async def get_chart_indicators(
    symbol: str,
    timeframe: str = Query("1d", description="Timeframe"),
    days: int = Query(30, description="Number of days"),
    db: Session = Depends(get_db)
):
    """Get technical indicators for chart overlay"""
    charting_service = ChartingService(db)
    data = charting_service.get_candlestick_data(symbol.upper(), timeframe, days)
    
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    
    return {
        "symbol": symbol.upper(),
        "timeframe": timeframe,
        "indicators": data.get("indicators", {}),
        "data_points": data.get("data_points", 0)
    }

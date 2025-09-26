from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.market_screener_service import MarketScreenerService
from typing import Optional, List

router = APIRouter(prefix="/api/screener", tags=["market-screener"])

@router.get("/stocks")
async def screen_stocks(
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    min_volume: Optional[int] = Query(None, description="Minimum volume"),
    exchange: Optional[str] = Query(None, description="Exchange filter"),
    sector: Optional[str] = Query(None, description="Sector filter"),
    limit: int = Query(50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Screen stocks based on various criteria"""
    screener_service = MarketScreenerService(db)
    
    filters = {
        'min_price': min_price,
        'max_price': max_price,
        'min_volume': min_volume,
        'exchange': exchange,
        'sector': sector,
        'limit': limit
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    results = screener_service.screen_stocks(filters)
    return {"results": results, "count": len(results), "filters": filters}

@router.get("/top-gainers")
async def get_top_gainers(
    limit: int = Query(20, description="Number of top gainers to return"),
    db: Session = Depends(get_db)
):
    """Get top gaining stocks"""
    screener_service = MarketScreenerService(db)
    gainers = screener_service.get_top_gainers(limit)
    return {"gainers": gainers, "count": len(gainers)}

@router.get("/top-losers")
async def get_top_losers(
    limit: int = Query(20, description="Number of top losers to return"),
    db: Session = Depends(get_db)
):
    """Get top losing stocks"""
    screener_service = MarketScreenerService(db)
    losers = screener_service.get_top_losers(limit)
    return {"losers": losers, "count": len(losers)}

@router.get("/most-active")
async def get_most_active(
    limit: int = Query(20, description="Number of most active stocks to return"),
    db: Session = Depends(get_db)
):
    """Get most actively traded stocks"""
    screener_service = MarketScreenerService(db)
    most_active = screener_service.get_most_active(limit)
    return {"most_active": most_active, "count": len(most_active)}

@router.get("/sector-performance")
async def get_sector_performance(db: Session = Depends(get_db)):
    """Get performance by sector"""
    screener_service = MarketScreenerService(db)
    sector_performance = screener_service.get_sector_performance()
    return {"sector_performance": sector_performance, "count": len(sector_performance)}

@router.get("/market-overview")
async def get_market_overview(db: Session = Depends(get_db)):
    """Get overall market overview"""
    screener_service = MarketScreenerService(db)
    overview = screener_service.get_market_overview()
    return {"market_overview": overview}

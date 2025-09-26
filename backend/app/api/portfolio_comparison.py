from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.portfolio_comparison_service import PortfolioComparisonService
from typing import Optional

router = APIRouter(prefix="/api/portfolio-comparison", tags=["portfolio-comparison"])

@router.get("/compare/{user_id}")
async def compare_portfolio(
    user_id: str,
    benchmark: str = Query("SPY", description="Benchmark symbol (e.g., SPY, QQQ, IWM)"),
    db: Session = Depends(get_db)
):
    """Compare user's portfolio performance against benchmarks"""
    comparison_service = PortfolioComparisonService(db)
    comparison = comparison_service.compare_portfolios(user_id, benchmark)
    
    if "error" in comparison:
        raise HTTPException(status_code=400, detail=comparison["error"])
    
    return comparison

@router.get("/sector-allocation/{user_id}")
async def get_sector_allocation(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get portfolio sector allocation"""
    comparison_service = PortfolioComparisonService(db)
    allocation = comparison_service.get_sector_allocation(user_id)
    
    if "error" in allocation:
        raise HTTPException(status_code=400, detail=allocation["error"])
    
    return allocation

@router.get("/performance-attribution/{user_id}")
async def get_performance_attribution(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get performance attribution analysis"""
    comparison_service = PortfolioComparisonService(db)
    attribution = comparison_service.get_performance_attribution(user_id)
    
    if "error" in attribution:
        raise HTTPException(status_code=400, detail=attribution["error"])
    
    return attribution

@router.get("/benchmarks")
async def get_available_benchmarks():
    """Get list of available benchmark symbols"""
    return {
        "benchmarks": [
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "description": "S&P 500 Index"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "description": "NASDAQ 100 Index"},
            {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "description": "Russell 2000 Index"},
            {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "description": "Total Stock Market"},
            {"symbol": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "description": "Developed Markets"},
            {"symbol": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "description": "Emerging Markets"},
            {"symbol": "BND", "name": "Vanguard Total Bond Market ETF", "description": "Total Bond Market"},
            {"symbol": "GLD", "name": "SPDR Gold Shares", "description": "Gold"},
            {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "description": "Long-term Treasury Bonds"}
        ]
    }

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.database import get_db
from app.services.advanced_analytics_service import AdvancedAnalyticsService
from app.api.auth import get_current_user

router = APIRouter()

class PortfolioMetricsRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PortfolioOptimizationRequest(BaseModel):
    target_return: Optional[float] = None
    risk_tolerance: float = 0.5

class AttributionAnalysisRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@router.get("/portfolio/metrics")
async def get_portfolio_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive portfolio performance metrics."""
    try:
        service = AdvancedAnalyticsService(db)
        metrics = service.calculate_portfolio_metrics(
            user_id=current_user,
            start_date=start_date,
            end_date=end_date
        )
        
        if "error" in metrics:
            raise HTTPException(status_code=400, detail=metrics["error"])
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio/optimize")
async def optimize_portfolio(
    request: PortfolioOptimizationRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Optimize portfolio allocation using Modern Portfolio Theory."""
    try:
        service = AdvancedAnalyticsService(db)
        optimization = service.optimize_portfolio(
            user_id=current_user,
            target_return=request.target_return,
            risk_tolerance=request.risk_tolerance
        )
        
        if "error" in optimization:
            raise HTTPException(status_code=400, detail=optimization["error"])
        
        return optimization
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/sector-allocation")
async def get_sector_allocation(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sector allocation and performance analysis."""
    try:
        service = AdvancedAnalyticsService(db)
        allocation = service.calculate_sector_allocation(user_id=current_user)
        
        if "error" in allocation:
            raise HTTPException(status_code=400, detail=allocation["error"])
        
        return allocation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolio/attribution")
async def get_attribution_analysis(
    request: AttributionAnalysisRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance attribution analysis."""
    try:
        service = AdvancedAnalyticsService(db)
        attribution = service.calculate_attribution_analysis(
            user_id=current_user,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        if "error" in attribution:
            raise HTTPException(status_code=400, detail=attribution["error"])
        
        return attribution
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/risk-metrics")
async def get_risk_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed risk metrics for the portfolio."""
    try:
        service = AdvancedAnalyticsService(db)
        metrics = service.calculate_portfolio_metrics(
            user_id=current_user,
            start_date=start_date,
            end_date=end_date
        )
        
        if "error" in metrics:
            raise HTTPException(status_code=400, detail=metrics["error"])
        
        # Extract risk-specific metrics
        risk_metrics = {
            "volatility": metrics.get("volatility", 0),
            "max_drawdown": metrics.get("max_drawdown", 0),
            "var_95": metrics.get("var_95", 0),
            "var_99": metrics.get("var_99", 0),
            "cvar_95": metrics.get("cvar_95", 0),
            "cvar_99": metrics.get("cvar_99", 0),
            "beta": metrics.get("beta", 1.0),
            "sharpe_ratio": metrics.get("sharpe_ratio", 0),
            "sortino_ratio": metrics.get("sortino_ratio", 0),
            "calmar_ratio": metrics.get("calmar_ratio", 0)
        }
        
        return risk_metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/performance-comparison")
async def get_performance_comparison(
    benchmark: str = Query("SPY", description="Benchmark symbol"),
    start_date: Optional[datetime] = Query(None, description="Start date for comparison"),
    end_date: Optional[datetime] = Query(None, description="End date for comparison"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare portfolio performance against benchmark."""
    try:
        service = AdvancedAnalyticsService(db)
        
        # Get portfolio metrics
        portfolio_metrics = service.calculate_portfolio_metrics(
            user_id=current_user,
            start_date=start_date,
            end_date=end_date
        )
        
        if "error" in portfolio_metrics:
            raise HTTPException(status_code=400, detail=portfolio_metrics["error"])
        
        # Get benchmark metrics
        benchmark_metrics = service._get_benchmark_metrics(
            benchmark, start_date, end_date
        )
        
        # Calculate comparison metrics
        comparison = {
            "portfolio": {
                "return": portfolio_metrics.get("annualized_return", 0),
                "volatility": portfolio_metrics.get("volatility", 0),
                "sharpe_ratio": portfolio_metrics.get("sharpe_ratio", 0),
                "max_drawdown": portfolio_metrics.get("max_drawdown", 0)
            },
            "benchmark": {
                "return": benchmark_metrics.get("return", 0),
                "volatility": benchmark_metrics.get("volatility", 0),
                "sharpe_ratio": benchmark_metrics.get("sharpe_ratio", 0),
                "max_drawdown": benchmark_metrics.get("max_drawdown", 0)
            },
            "comparison": {
                "excess_return": portfolio_metrics.get("annualized_return", 0) - benchmark_metrics.get("return", 0),
                "alpha": portfolio_metrics.get("alpha", 0),
                "beta": portfolio_metrics.get("beta", 1.0),
                "information_ratio": portfolio_metrics.get("information_ratio", 0)
            }
        }
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/correlation-matrix")
async def get_correlation_matrix(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get correlation matrix for portfolio holdings."""
    try:
        service = AdvancedAnalyticsService(db)
        
        # Get portfolio holdings
        from app.db import models
        portfolio = db.query(models.Portfolio).filter(
            models.Portfolio.user_id == current_user
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        holdings = db.query(models.Holding).filter(
            models.Holding.portfolio_id == portfolio.id
        ).all()
        
        if not holdings:
            raise HTTPException(status_code=404, detail="No holdings found")
        
        # Get correlation matrix
        symbols = [holding.symbol for holding in holdings]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=252)  # 1 year
        
        correlation_matrix = service._calculate_correlation_matrix(symbols, start_date, end_date)
        
        return {
            "symbols": symbols,
            "correlation_matrix": correlation_matrix,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio/efficient-frontier")
async def get_efficient_frontier(
    num_portfolios: int = Query(100, description="Number of portfolios to generate"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate efficient frontier for portfolio optimization."""
    try:
        service = AdvancedAnalyticsService(db)
        
        # Get portfolio holdings
        from app.db import models
        portfolio = db.query(models.Portfolio).filter(
            models.Portfolio.user_id == current_user
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        holdings = db.query(models.Holding).filter(
            models.Holding.portfolio_id == portfolio.id
        ).all()
        
        if not holdings:
            raise HTTPException(status_code=404, detail="No holdings found")
        
        symbols = [holding.symbol for holding in holdings]
        
        # Generate efficient frontier
        efficient_frontier = service._generate_efficient_frontier(symbols, num_portfolios)
        
        return efficient_frontier
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

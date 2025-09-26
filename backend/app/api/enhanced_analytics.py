from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.enhanced_analytics_service import EnhancedAnalyticsService
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/enhanced-analytics", tags=["enhanced-analytics"])

@router.get("/comprehensive/{user_id}")
async def get_comprehensive_analytics(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get comprehensive portfolio analytics"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/performance/{user_id}")
async def get_performance_metrics(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get performance metrics"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "performance_metrics": result.get("performance_metrics", {}),
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/risk/{user_id}")
async def get_risk_metrics(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get risk metrics"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "risk_metrics": result.get("risk_metrics", {}),
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk metrics: {str(e)}")

@router.get("/attribution/{user_id}")
async def get_attribution_analysis(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get performance attribution analysis"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "attribution_analysis": result.get("attribution_analysis", {}),
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get attribution analysis: {str(e)}")

@router.get("/correlation/{user_id}")
async def get_correlation_analysis(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get correlation analysis"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "correlation_analysis": result.get("correlation_analysis", {}),
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get correlation analysis: {str(e)}")

@router.get("/optimization/{user_id}")
async def get_portfolio_optimization(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get portfolio optimization recommendations"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "portfolio_optimization": result.get("portfolio_optimization", {}),
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio optimization: {str(e)}")

@router.get("/scenarios/{user_id}")
async def get_scenario_analysis(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get scenario analysis"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "scenario_analysis": result.get("scenario_analysis", {}),
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scenario analysis: {str(e)}")

@router.get("/stress-test/{user_id}")
async def get_stress_testing(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get stress testing results"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "user_id": user_id,
            "stress_testing": result.get("stress_testing", {}),
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stress testing: {str(e)}")

@router.get("/benchmark-comparison/{user_id}")
async def get_benchmark_comparison(
    user_id: str,
    benchmark: str = Query("SPY", description="Benchmark symbol (SPY, QQQ, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get benchmark comparison analysis"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Extract relevant metrics for benchmark comparison
        performance_metrics = result.get("performance_metrics", {})
        risk_metrics = result.get("risk_metrics", {})
        
        return {
            "user_id": user_id,
            "benchmark": benchmark,
            "portfolio_metrics": {
                "return": performance_metrics.get("annualized_return", 0),
                "volatility": risk_metrics.get("volatility", 0),
                "sharpe_ratio": risk_metrics.get("sharpe_ratio", 0),
                "max_drawdown": risk_metrics.get("max_drawdown", 0),
                "beta": risk_metrics.get("beta", 0),
                "alpha": risk_metrics.get("alpha", 0)
            },
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get benchmark comparison: {str(e)}")

@router.get("/risk-budget/{user_id}")
async def get_risk_budget_analysis(
    user_id: str,
    target_volatility: float = Query(0.15, description="Target portfolio volatility"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get risk budget analysis"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Calculate risk budget
        current_volatility = result.get("risk_metrics", {}).get("volatility", 0) / 100
        volatility_ratio = current_volatility / target_volatility if target_volatility > 0 else 0
        
        return {
            "user_id": user_id,
            "target_volatility": target_volatility * 100,
            "current_volatility": result.get("risk_metrics", {}).get("volatility", 0),
            "volatility_ratio": round(volatility_ratio, 2),
            "risk_budget_status": "over_budget" if volatility_ratio > 1.1 else "under_budget" if volatility_ratio < 0.9 else "on_target",
            "recommendations": {
                "reduce_risk": volatility_ratio > 1.1,
                "increase_risk": volatility_ratio < 0.9,
                "maintain_current": 0.9 <= volatility_ratio <= 1.1
            },
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk budget analysis: {str(e)}")

@router.get("/performance-attribution/{user_id}")
async def get_performance_attribution(
    user_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get detailed performance attribution"""
    try:
        # Parse dates
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        analytics_service = EnhancedAnalyticsService(db)
        result = analytics_service.get_comprehensive_analytics(user_id, start_dt, end_dt)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        attribution = result.get("attribution_analysis", {})
        
        return {
            "user_id": user_id,
            "performance_attribution": {
                "total_return": attribution.get("total_portfolio_return", 0),
                "asset_contributions": attribution.get("asset_contributions", []),
                "selection_effect": attribution.get("selection_effect", 0),
                "allocation_effect": attribution.get("allocation_effect", 0),
                "interaction_effect": attribution.get("interaction_effect", 0)
            },
            "analysis_period": result.get("analysis_period", {}),
            "timestamp": result.get("timestamp")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance attribution: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db import models, schemas
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.get("/performance/{user_id}")
async def get_performance_analytics(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get comprehensive performance analytics"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_performance_analytics(user_id, days)

@router.get("/risk/{user_id}")
async def get_risk_metrics(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get risk analysis metrics"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_risk_metrics(user_id, days)

@router.get("/benchmark/{user_id}")
async def get_benchmark_comparison(
    user_id: str,
    benchmark: str = "SPY",
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Compare portfolio performance against benchmark"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_benchmark_comparison(user_id, benchmark, days)

@router.get("/allocation/{user_id}")
async def get_portfolio_allocation(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get portfolio allocation breakdown"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_portfolio_allocation(user_id)

@router.get("/correlation/{user_id}")
async def get_correlation_analysis(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get correlation analysis between holdings"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_correlation_analysis(user_id, days)

@router.get("/heatmap/{user_id}")
async def get_performance_heatmap(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get performance heatmap data"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_performance_heatmap(user_id, days)

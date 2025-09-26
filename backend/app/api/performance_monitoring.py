from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.database import get_db
from app.services.performance_monitoring import get_performance_monitor
from app.api.auth import get_current_user

router = APIRouter()

class PerformanceSummaryResponse(BaseModel):
    system: Optional[Dict[str, Any]]
    application: Optional[Dict[str, Any]]
    business: Optional[Dict[str, Any]]
    timestamp: str

class HealthStatusResponse(BaseModel):
    overall: str
    checks: Dict[str, str]
    timestamp: str

@router.get("/summary")
async def get_performance_summary(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance summary."""
    try:
        monitor = get_performance_monitor(db)
        summary = monitor.get_performance_summary()
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_health_status(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system health status."""
    try:
        monitor = get_performance_monitor(db)
        health_status = monitor.get_health_status()
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-metrics")
async def get_system_metrics(
    limit: int = Query(100, description="Number of metrics to return"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system performance metrics."""
    try:
        monitor = get_performance_monitor(db)
        metrics = monitor.get_system_metrics(limit)
        
        return {
            "success": True,
            "metrics": metrics,
            "count": len(metrics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/application-metrics")
async def get_application_metrics(
    limit: int = Query(100, description="Number of metrics to return"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get application performance metrics."""
    try:
        monitor = get_performance_monitor(db)
        metrics = monitor.get_application_metrics(limit)
        
        return {
            "success": True,
            "metrics": metrics,
            "count": len(metrics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/business-metrics")
async def get_business_metrics(
    limit: int = Query(100, description="Number of metrics to return"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get business performance metrics."""
    try:
        monitor = get_performance_monitor(db)
        metrics = monitor.get_business_metrics(limit)
        
        return {
            "success": True,
            "metrics": metrics,
            "count": len(metrics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/timeframe")
async def get_metrics_for_timeframe(
    start_time: str = Query(..., description="Start time (ISO format)"),
    end_time: str = Query(..., description="End time (ISO format)"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get metrics for a specific timeframe."""
    try:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        monitor = get_performance_monitor(db)
        metrics = monitor.get_metrics_for_timeframe(start_dt, end_dt)
        
        return {
            "success": True,
            "metrics": metrics,
            "timeframe": {
                "start": start_time,
                "end": end_time
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/export")
async def export_metrics(
    format: str = Query("json", description="Export format (json)"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export performance metrics."""
    try:
        monitor = get_performance_monitor(db)
        exported_data = monitor.export_metrics(format)
        
        return {
            "success": True,
            "data": exported_data,
            "format": format,
            "exported_at": datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/realtime")
async def get_realtime_metrics(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time performance metrics."""
    try:
        monitor = get_performance_monitor(db)
        
        # Get latest metrics
        system_metrics = monitor.get_system_metrics(1)
        app_metrics = monitor.get_application_metrics(1)
        business_metrics = monitor.get_business_metrics(1)
        
        return {
            "success": True,
            "realtime": {
                "system": system_metrics[0] if system_metrics else None,
                "application": app_metrics[0] if app_metrics else None,
                "business": business_metrics[0] if business_metrics else None,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/dashboard")
async def get_dashboard_metrics(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get metrics for dashboard display."""
    try:
        monitor = get_performance_monitor(db)
        
        # Get recent metrics for dashboard
        system_metrics = monitor.get_system_metrics(24)  # Last 24 hours
        app_metrics = monitor.get_application_metrics(24)
        business_metrics = monitor.get_business_metrics(24)
        
        # Calculate trends
        system_trend = "stable"
        app_trend = "stable"
        business_trend = "stable"
        
        if len(system_metrics) >= 2:
            latest_cpu = system_metrics[-1]["cpu_percent"]
            previous_cpu = system_metrics[-2]["cpu_percent"]
            if latest_cpu > previous_cpu * 1.1:
                system_trend = "increasing"
            elif latest_cpu < previous_cpu * 0.9:
                system_trend = "decreasing"
        
        if len(app_metrics) >= 2:
            latest_requests = app_metrics[-1]["request_count"]
            previous_requests = app_metrics[-2]["request_count"]
            if latest_requests > previous_requests * 1.1:
                app_trend = "increasing"
            elif latest_requests < previous_requests * 0.9:
                app_trend = "decreasing"
        
        if len(business_metrics) >= 2:
            latest_users = business_metrics[-1]["active_users"]
            previous_users = business_metrics[-2]["active_users"]
            if latest_users > previous_users * 1.1:
                business_trend = "increasing"
            elif latest_users < previous_users * 0.9:
                business_trend = "decreasing"
        
        return {
            "success": True,
            "dashboard": {
                "system": {
                    "current": system_metrics[-1] if system_metrics else None,
                    "history": system_metrics,
                    "trend": system_trend
                },
                "application": {
                    "current": app_metrics[-1] if app_metrics else None,
                    "history": app_metrics,
                    "trend": app_trend
                },
                "business": {
                    "current": business_metrics[-1] if business_metrics else None,
                    "history": business_metrics,
                    "trend": business_trend
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/alerts")
async def get_performance_alerts(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance alerts and warnings."""
    try:
        monitor = get_performance_monitor(db)
        health_status = monitor.get_health_status()
        
        alerts = []
        
        # Check for critical issues
        if health_status["overall"] == "degraded":
            alerts.append({
                "level": "critical",
                "message": "System performance is degraded",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check individual components
        for component, status in health_status["checks"].items():
            if status == "critical":
                alerts.append({
                    "level": "critical",
                    "message": f"{component.title()} is in critical state",
                    "component": component,
                    "timestamp": datetime.now().isoformat()
                })
            elif status == "warning":
                alerts.append({
                    "level": "warning",
                    "message": f"{component.title()} is showing warning signs",
                    "component": component,
                    "timestamp": datetime.now().isoformat()
                })
        
        return {
            "success": True,
            "alerts": alerts,
            "count": len(alerts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/record/request")
async def record_request_metric(
    duration: float,
    success: bool = True,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a request performance metric."""
    try:
        monitor = get_performance_monitor(db)
        monitor.record_request(duration, success)
        
        return {
            "success": True,
            "message": "Request metric recorded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/record/websocket")
async def record_websocket_metric(
    connected: bool = True,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a WebSocket performance metric."""
    try:
        monitor = get_performance_monitor(db)
        monitor.record_websocket_connection(connected)
        
        return {
            "success": True,
            "message": "WebSocket metric recorded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/record/cache")
async def record_cache_metric(
    hit: bool = True,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a cache performance metric."""
    try:
        monitor = get_performance_monitor(db)
        monitor.record_cache_hit(hit)
        
        return {
            "success": True,
            "message": "Cache metric recorded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/record/database")
async def record_database_metric(
    duration: float,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a database performance metric."""
    try:
        monitor = get_performance_monitor(db)
        monitor.record_database_query(duration)
        
        return {
            "success": True,
            "message": "Database metric recorded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

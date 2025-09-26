from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.realtime_alerts_service import RealtimeAlertsService
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/alerts", tags=["realtime-alerts"])

class PriceAlertRequest(BaseModel):
    user_id: str
    symbol: str
    alert_type: str  # 'price_above', 'price_below', 'price_change_up', 'price_change_down'
    target_price: float
    message: Optional[str] = ""

class TechnicalAlertRequest(BaseModel):
    user_id: str
    symbol: str
    indicator_type: str  # 'rsi_overbought', 'rsi_oversold', 'macd_bullish', 'macd_bearish', 'ma_crossover'
    message: Optional[str] = ""

class VolumeAlertRequest(BaseModel):
    user_id: str
    symbol: str
    alert_type: str  # 'volume_spike', 'volume_drop'
    volume_threshold: float
    message: Optional[str] = ""

class NewsAlertRequest(BaseModel):
    user_id: str
    symbol: str
    keywords: str  # Comma-separated keywords
    message: Optional[str] = ""

@router.post("/price")
async def create_price_alert(
    request: PriceAlertRequest,
    db: Session = Depends(get_db)
):
    """Create a price-based alert"""
    alerts_service = RealtimeAlertsService(db)
    result = alerts_service.create_price_alert(
        request.user_id,
        request.symbol,
        request.alert_type,
        request.target_price,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/technical")
async def create_technical_alert(
    request: TechnicalAlertRequest,
    db: Session = Depends(get_db)
):
    """Create a technical indicator alert"""
    alerts_service = RealtimeAlertsService(db)
    result = alerts_service.create_technical_alert(
        request.user_id,
        request.symbol,
        request.indicator_type,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/volume")
async def create_volume_alert(
    request: VolumeAlertRequest,
    db: Session = Depends(get_db)
):
    """Create a volume-based alert"""
    alerts_service = RealtimeAlertsService(db)
    result = alerts_service.create_volume_alert(
        request.user_id,
        request.symbol,
        request.alert_type,
        request.volume_threshold,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/news")
async def create_news_alert(
    request: NewsAlertRequest,
    db: Session = Depends(get_db)
):
    """Create a news-based alert"""
    alerts_service = RealtimeAlertsService(db)
    result = alerts_service.create_news_alert(
        request.user_id,
        request.symbol,
        request.keywords,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/{user_id}")
async def get_user_alerts(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all alerts for a user"""
    alerts_service = RealtimeAlertsService(db)
    alerts = alerts_service.get_user_alerts(user_id)
    
    if "error" in alerts:
        raise HTTPException(status_code=400, detail=alerts["error"])
    
    return alerts

@router.delete("/{user_id}/{alert_id}")
async def delete_alert(
    user_id: str,
    alert_id: int,
    alert_type: str = Query(..., description="Type of alert: price, technical, volume, news"),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    alerts_service = RealtimeAlertsService(db)
    result = alerts_service.delete_alert(user_id, alert_id, alert_type)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/types/price")
async def get_price_alert_types():
    """Get available price alert types"""
    return {
        "price_alert_types": [
            {
                "type": "price_above",
                "description": "Alert when price goes above target",
                "example": "Alert when AAPL goes above $150"
            },
            {
                "type": "price_below",
                "description": "Alert when price goes below target",
                "example": "Alert when AAPL goes below $140"
            },
            {
                "type": "price_change_up",
                "description": "Alert when price increases by target percentage",
                "example": "Alert when AAPL increases by 5%"
            },
            {
                "type": "price_change_down",
                "description": "Alert when price decreases by target percentage",
                "example": "Alert when AAPL decreases by 5%"
            }
        ]
    }

@router.get("/types/technical")
async def get_technical_alert_types():
    """Get available technical alert types"""
    return {
        "technical_alert_types": [
            {
                "type": "rsi_overbought",
                "description": "Alert when RSI goes above 70 (overbought)",
                "indicator": "RSI"
            },
            {
                "type": "rsi_oversold",
                "description": "Alert when RSI goes below 30 (oversold)",
                "indicator": "RSI"
            },
            {
                "type": "macd_bullish",
                "description": "Alert when MACD shows bullish signal",
                "indicator": "MACD"
            },
            {
                "type": "macd_bearish",
                "description": "Alert when MACD shows bearish signal",
                "indicator": "MACD"
            },
            {
                "type": "ma_crossover",
                "description": "Alert when moving averages cross",
                "indicator": "Moving Averages"
            }
        ]
    }

@router.get("/types/volume")
async def get_volume_alert_types():
    """Get available volume alert types"""
    return {
        "volume_alert_types": [
            {
                "type": "volume_spike",
                "description": "Alert when volume exceeds threshold times average",
                "example": "Alert when volume is 2x average"
            },
            {
                "type": "volume_drop",
                "description": "Alert when volume drops below threshold of average",
                "example": "Alert when volume is 0.5x average"
            }
        ]
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db.database import get_db
from app.services.background_ai_service import get_background_ai_service, BackgroundAIService

router = APIRouter()

@router.post("/start")
async def start_background_ai_trading(
    db: Session = Depends(get_db)
):
    """Start the background AI trading service"""
    try:
        background_service = get_background_ai_service(db)
        background_service.start_background_trading()
        return {"message": "Background AI trading service started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start background AI trading: {str(e)}")

@router.post("/stop")
async def stop_background_ai_trading(
    db: Session = Depends(get_db)
):
    """Stop the background AI trading service"""
    try:
        background_service = get_background_ai_service(db)
        background_service.stop_background_trading()
        return {"message": "Background AI trading service stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop background AI trading: {str(e)}")

@router.get("/status")
async def get_background_ai_status(
    db: Session = Depends(get_db)
):
    """Get the current status of background AI trading"""
    try:
        background_service = get_background_ai_service(db)
        status = background_service.get_background_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get background AI status: {str(e)}")

@router.post("/force-trading/{user_id}")
async def force_ai_trading_round(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Force an immediate AI trading round for a specific user"""
    try:
        background_service = get_background_ai_service(db)
        result = background_service.force_ai_trading_round(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to force AI trading round: {str(e)}")

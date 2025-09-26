from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db import models, schemas
from app.services.ai_service import AIService

router = APIRouter()

@router.get("/test")
async def test_ai_connection(db: Session = Depends(get_db)):
    """Test OpenAI API connection"""
    ai_service = AIService(db)
    return ai_service.test_openai_connection()

@router.post("/chat", response_model=schemas.ChatResponse)
async def chat_with_ai(
    message: schemas.ChatMessage,
    db: Session = Depends(get_db)
):
    """Chat with AI assistant about portfolio and market data"""
    ai_service = AIService(db)
    
    try:
        response = ai_service.process_chat_message(
            user_id=message.user_id,
            message=message.message,
            session_id=message.session_id
        )
        return schemas.ChatResponse(
            response=response["response"],
            session_id=response["session_id"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/{symbol}")
async def get_price_predictions(
    symbol: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get AI price predictions for an asset"""
    ai_service = AIService(db)
    return ai_service.get_price_predictions(symbol, days)

@router.get("/insights/{user_id}")
async def get_portfolio_insights(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get AI-generated insights for user's portfolio"""
    ai_service = AIService(db)
    return ai_service.get_portfolio_insights(user_id)

@router.post("/retrain")
async def retrain_models(
    db: Session = Depends(get_db)
):
    """Trigger model retraining (admin endpoint)"""
    ai_service = AIService(db)
    return ai_service.retrain_models()

@router.get("/models/status")
async def get_model_status(
    db: Session = Depends(get_db)
):
    """Get status of AI models"""
    ai_service = AIService(db)
    return ai_service.get_model_status()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db import models, schemas
from app.services.ai_opponent_service import AIOpponentService

router = APIRouter()

@router.post("/create", response_model=schemas.AIOpponent)
async def create_ai_opponent(
    user_id: str,
    strategy_type: str = "conservative",
    db: Session = Depends(get_db)
):
    """Create an AI trading opponent for a user"""
    ai_service = AIOpponentService(db)
    
    # Check if user already has an active AI opponent
    existing_opponent = db.query(models.AIOpponent).filter(
        models.AIOpponent.user_id == user_id,
        models.AIOpponent.is_active == True
    ).first()
    
    if existing_opponent:
        raise HTTPException(status_code=400, detail="User already has an active AI opponent")
    
    result = ai_service.create_ai_opponent(user_id, strategy_type)
    
    # Return the created AI opponent
    ai_opponent = db.query(models.AIOpponent).filter(
        models.AIOpponent.id == result["ai_opponent_id"]
    ).first()
    
    return ai_opponent

@router.post("/trade/{user_id}")
async def execute_ai_trading(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Execute AI trading cycle for the day"""
    ai_service = AIOpponentService(db)
    result = ai_service.execute_ai_trading_cycle(user_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/competition/{user_id}", response_model=schemas.CompetitionData)
async def get_competition_data(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get competition data between user and AI opponent"""
    ai_service = AIOpponentService(db)
    result = ai_service.get_competition_data(user_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/opponent/{user_id}")
async def get_ai_opponent(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get AI opponent information for a user"""
    ai_opponent = db.query(models.AIOpponent).filter(
        models.AIOpponent.user_id == user_id,
        models.AIOpponent.is_active == True
    ).first()
    
    if not ai_opponent:
        raise HTTPException(status_code=404, detail="No active AI opponent found")
    
    return ai_opponent

@router.put("/opponent/{user_id}/deactivate")
async def deactivate_ai_opponent(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Deactivate AI opponent"""
    ai_opponent = db.query(models.AIOpponent).filter(
        models.AIOpponent.user_id == user_id,
        models.AIOpponent.is_active == True
    ).first()
    
    if not ai_opponent:
        raise HTTPException(status_code=404, detail="No active AI opponent found")
    
    ai_opponent.is_active = False
    ai_opponent.end_date = datetime.utcnow()
    db.commit()
    
    return {"message": "AI opponent deactivated successfully"}

@router.get("/strategies")
async def get_available_strategies():
    """Get available AI trading strategies"""
    strategies = {
        "conservative": {
            "name": "Conservative AI",
            "description": "Focuses on blue-chip stocks with low risk and steady returns",
            "risk_level": "Low",
            "max_trades_per_day": 2,
            "preferred_sectors": ["Technology", "Healthcare", "Consumer Staples"]
        },
        "aggressive": {
            "name": "Aggressive AI",
            "description": "High-risk, high-reward strategy targeting growth stocks",
            "risk_level": "High",
            "max_trades_per_day": 5,
            "preferred_sectors": ["Technology", "Biotechnology", "Energy"]
        },
        "technical": {
            "name": "Technical AI",
            "description": "Uses technical analysis and chart patterns for trading decisions",
            "risk_level": "Medium",
            "max_trades_per_day": 3,
            "preferred_sectors": ["Technology", "Finance", "Energy"]
        },
        "sentiment": {
            "name": "Sentiment AI",
            "description": "Trades based on news sentiment and social media analysis",
            "risk_level": "Medium",
            "max_trades_per_day": 4,
            "preferred_sectors": ["Technology", "Consumer Discretionary", "Communication"]
        }
    }
    
    return strategies

@router.get("/leaderboard")
async def get_ai_competition_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get leaderboard of users vs their AI opponents"""
    # Get all active AI opponents with their performance
    ai_opponents = db.query(models.AIOpponent).filter(
        models.AIOpponent.is_active == True
    ).all()
    
    leaderboard = []
    
    for opponent in ai_opponents:
        # Get user portfolio
        user_portfolio = db.query(models.Portfolio).filter(
            models.Portfolio.user_id == opponent.user_id
        ).first()
        
        # Get AI portfolio
        ai_portfolio = db.query(models.Portfolio).filter(
            models.Portfolio.user_id == opponent.ai_user_id
        ).first()
        
        if user_portfolio and ai_portfolio:
            initial_balance = 100000.0
            
            user_return = ((user_portfolio.total_value - initial_balance) / initial_balance) * 100
            ai_return = ((ai_portfolio.total_value - initial_balance) / initial_balance) * 100
            
            leaderboard.append({
                "user_id": opponent.user_id,
                "ai_strategy": opponent.strategy_type,
                "user_return": user_return,
                "ai_return": ai_return,
                "winner": "user" if user_return > ai_return else "ai",
                "difference": abs(user_return - ai_return)
            })
    
    # Sort by user return percentage
    leaderboard.sort(key=lambda x: x["user_return"], reverse=True)
    
    return leaderboard[:limit]

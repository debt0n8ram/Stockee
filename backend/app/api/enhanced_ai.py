from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.enhanced_ai_service import EnhancedAIService
from typing import Optional

router = APIRouter(prefix="/api/enhanced-ai", tags=["enhanced-ai"])

@router.get("/predictions/{symbol}")
async def get_enhanced_predictions(
    symbol: str,
    days_ahead: int = Query(7, description="Number of days to predict ahead"),
    db: Session = Depends(get_db)
):
    """Get enhanced AI predictions using multiple models"""
    ai_service = EnhancedAIService(db)
    predictions = ai_service.get_enhanced_predictions(symbol.upper(), days_ahead)
    
    if "error" in predictions:
        raise HTTPException(status_code=400, detail=predictions["error"])
    
    return predictions

@router.get("/models")
async def get_available_models():
    """Get list of available AI models"""
    return {
        "models": [
            {
                "name": "LSTM",
                "description": "Long Short-Term Memory neural network for time series prediction",
                "strengths": ["Pattern recognition", "Long-term dependencies", "Trend analysis"],
                "best_for": "Trend following strategies"
            },
            {
                "name": "Transformer",
                "description": "Attention-based neural network for sequence modeling",
                "strengths": ["Attention mechanism", "Context understanding", "Non-linear patterns"],
                "best_for": "Complex market dynamics"
            },
            {
                "name": "Ensemble",
                "description": "Combination of multiple models for improved accuracy",
                "strengths": ["Reduced overfitting", "Better generalization", "Robust predictions"],
                "best_for": "Overall market analysis"
            },
            {
                "name": "Sentiment-Adjusted",
                "description": "Ensemble model adjusted for social sentiment",
                "strengths": ["Sentiment integration", "Market psychology", "News impact"],
                "best_for": "Event-driven trading"
            }
        ]
    }

@router.get("/performance/{symbol}")
async def get_model_performance(
    symbol: str,
    days_back: int = Query(30, description="Number of days to look back for performance"),
    db: Session = Depends(get_db)
):
    """Get historical performance of AI models"""
    ai_service = EnhancedAIService(db)
    
    # Mock performance data for now
    performance_data = {
        "symbol": symbol.upper(),
        "evaluation_period": f"Last {days_back} days",
        "model_performance": [
            {
                "model": "LSTM",
                "accuracy": 0.72,
                "mae": 2.45,
                "rmse": 3.21,
                "sharpe_ratio": 1.85,
                "win_rate": 0.68
            },
            {
                "model": "Transformer",
                "accuracy": 0.75,
                "mae": 2.12,
                "rmse": 2.89,
                "sharpe_ratio": 2.01,
                "win_rate": 0.71
            },
            {
                "model": "Ensemble",
                "accuracy": 0.78,
                "mae": 1.98,
                "rmse": 2.67,
                "sharpe_ratio": 2.15,
                "win_rate": 0.74
            },
            {
                "model": "Sentiment-Adjusted",
                "accuracy": 0.81,
                "mae": 1.85,
                "rmse": 2.45,
                "sharpe_ratio": 2.28,
                "win_rate": 0.77
            }
        ],
        "best_performing_model": "Sentiment-Adjusted",
        "overall_accuracy": 0.77
    }
    
    return performance_data

@router.get("/insights/{symbol}")
async def get_ai_insights(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get AI-generated insights for a symbol"""
    ai_service = EnhancedAIService(db)
    predictions = ai_service.get_enhanced_predictions(symbol.upper(), 7)
    
    if "error" in predictions:
        raise HTTPException(status_code=400, detail=predictions["error"])
    
    return {
        "symbol": symbol.upper(),
        "insights": predictions.get("ai_insights", []),
        "confidence_scores": predictions.get("confidence_scores", {}),
        "timestamp": predictions.get("timestamp")
    }

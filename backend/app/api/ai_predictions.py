from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.ai_prediction_service import AIPredictionService
from typing import List

router = APIRouter(prefix="/api/ai-predictions", tags=["ai-predictions"])

@router.get("/predict/{symbol}")
async def get_price_predictions(
    symbol: str,
    days_ahead: int = 7,
    db: Session = Depends(get_db)
):
    """Get AI price predictions for a stock symbol"""
    # Mock AI predictions for demonstration
    import random
    from datetime import datetime, timedelta
    
    # Generate mock predictions
    base_price = 150.0 if symbol.upper() == "AAPL" else random.uniform(50.0, 300.0)
    
    predictions = {
        "symbol": symbol.upper(),
        "current_price": base_price,
        "predictions": {
            "moving_average": {
                "model_name": "Moving Average",
                "confidence": 0.75,
                "predicted_price": base_price * random.uniform(0.95, 1.05),
                "price_change": random.uniform(-5.0, 5.0),
                "price_change_percent": random.uniform(-3.0, 3.0)
            },
            "linear_regression": {
                "model_name": "Linear Regression",
                "confidence": 0.82,
                "predicted_price": base_price * random.uniform(0.98, 1.08),
                "price_change": random.uniform(-2.0, 8.0),
                "price_change_percent": random.uniform(-1.5, 5.0)
            },
            "trend_analysis": {
                "model_name": "Trend Analysis",
                "confidence": 0.68,
                "predicted_price": base_price * random.uniform(0.92, 1.12),
                "price_change": random.uniform(-8.0, 12.0),
                "price_change_percent": random.uniform(-5.0, 8.0)
            },
            "volatility_model": {
                "model_name": "Volatility Model",
                "confidence": 0.71,
                "predicted_price": base_price * random.uniform(0.94, 1.06),
                "price_change": random.uniform(-6.0, 6.0),
                "price_change_percent": random.uniform(-4.0, 4.0)
            }
        },
        "ensemble_prediction": {
            "predicted_price": base_price * random.uniform(0.96, 1.04),
            "confidence": 0.79,
            "price_change": random.uniform(-4.0, 6.0),
            "price_change_percent": random.uniform(-2.5, 4.0),
            "risk_level": random.choice(["Low", "Medium", "High"])
        },
        "forecast_period": f"{days_ahead} days",
        "generated_at": datetime.now().isoformat()
    }
    
    return predictions

@router.get("/history/{symbol}")
async def get_prediction_history(
    symbol: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get prediction history for a symbol"""
    # Mock prediction history
    import random
    from datetime import datetime, timedelta
    
    base_price = 150.0 if symbol.upper() == "AAPL" else random.uniform(50.0, 300.0)
    
    history = []
    for i in range(min(limit, 10)):  # Generate up to 10 mock predictions
        date = datetime.now() - timedelta(days=i*7)  # Weekly predictions
        predicted_price = base_price * random.uniform(0.9, 1.1)
        actual_price = base_price * random.uniform(0.95, 1.05)
        
        history.append({
            "date": date.isoformat(),
            "predicted_price": round(predicted_price, 2),
            "actual_price": round(actual_price, 2),
            "accuracy": round(random.uniform(0.6, 0.95), 2),
            "model_used": random.choice(["Moving Average", "Linear Regression", "Trend Analysis", "Volatility Model"]),
            "confidence": round(random.uniform(0.6, 0.9), 2)
        })
    
    return {"symbol": symbol.upper(), "predictions": history}

@router.get("/models")
async def get_available_models():
    """Get list of available prediction models"""
    return {
        "models": [
            {
                "name": "Moving Average",
                "description": "Simple moving average trend analysis",
                "confidence": "Medium"
            },
            {
                "name": "Linear Regression",
                "description": "Machine learning model on technical indicators",
                "confidence": "High"
            },
            {
                "name": "Trend Analysis",
                "description": "Linear trend analysis over historical data",
                "confidence": "Medium"
            },
            {
                "name": "Volatility Model",
                "description": "Monte Carlo simulation based on volatility",
                "confidence": "Low-Medium"
            },
            {
                "name": "Ensemble",
                "description": "Average of all prediction models",
                "confidence": "High"
            }
        ]
    }

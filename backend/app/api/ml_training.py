from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

from app.db.database import get_db
from app.services.ml_training_service import MLTrainingService
from app.api.auth import get_current_user

router = APIRouter()

class PricePredictionTrainingRequest(BaseModel):
    symbol: str
    model_type: str = "random_forest"
    features: Optional[List[str]] = None
    target_days: int = 1

class SentimentTrainingRequest(BaseModel):
    symbol: str
    model_type: str = "random_forest"

class PortfolioOptimizationTrainingRequest(BaseModel):
    model_type: str = "random_forest"

class ModelPredictionRequest(BaseModel):
    model_id: int
    input_data: Dict[str, Any]

@router.post("/train/price-prediction")
async def train_price_prediction_model(
    request: PricePredictionTrainingRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train a custom price prediction model for a specific symbol."""
    try:
        service = MLTrainingService(db)
        result = service.train_price_prediction_model(
            user_id=current_user,
            symbol=request.symbol,
            model_type=request.model_type,
            features=request.features,
            target_days=request.target_days
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train/sentiment")
async def train_sentiment_model(
    request: SentimentTrainingRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train a sentiment-based prediction model."""
    try:
        service = MLTrainingService(db)
        result = service.train_sentiment_model(
            user_id=current_user,
            symbol=request.symbol,
            model_type=request.model_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train/portfolio-optimization")
async def train_portfolio_optimization_model(
    request: PortfolioOptimizationTrainingRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train a portfolio optimization model."""
    try:
        service = MLTrainingService(db)
        result = service.train_portfolio_optimization_model(
            user_id=current_user,
            model_type=request.model_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def get_model_predictions(
    request: ModelPredictionRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get predictions from a trained model."""
    try:
        service = MLTrainingService(db)
        result = service.get_model_predictions(
            user_id=current_user,
            model_id=request.model_id,
            input_data=request.input_data
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_user_models(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all models for a user."""
    try:
        service = MLTrainingService(db)
        models = service.get_user_models(user_id=current_user)
        return {"models": models}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/models/{model_id}")
async def delete_model(
    model_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a trained model."""
    try:
        service = MLTrainingService(db)
        result = service.delete_model(user_id=current_user, model_id=model_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_id}/retrain")
async def retrain_model(
    model_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrain an existing model with new data."""
    try:
        service = MLTrainingService(db)
        result = service.retrain_model(user_id=current_user, model_id=model_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_id}")
async def get_model_details(
    model_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific model."""
    try:
        from app.db import models
        
        ml_model = db.query(models.MLModel).filter(
            models.MLModel.id == model_id,
            models.MLModel.user_id == current_user,
            models.MLModel.is_active == True
        ).first()
        
        if not ml_model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        import json
        
        return {
            "id": ml_model.id,
            "symbol": ml_model.symbol,
            "model_type": ml_model.model_type,
            "features": json.loads(ml_model.features),
            "target_days": ml_model.target_days,
            "training_date": ml_model.training_date.isoformat(),
            "data_points": ml_model.data_points,
            "metrics": json.loads(ml_model.metrics),
            "is_active": ml_model.is_active,
            "created_at": ml_model.created_at.isoformat(),
            "updated_at": ml_model.updated_at.isoformat() if ml_model.updated_at else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_id}/performance")
async def get_model_performance(
    model_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics for a specific model."""
    try:
        from app.db import models
        
        ml_model = db.query(models.MLModel).filter(
            models.MLModel.id == model_id,
            models.MLModel.user_id == current_user,
            models.MLModel.is_active == True
        ).first()
        
        if not ml_model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        import json
        metrics = json.loads(ml_model.metrics)
        
        return {
            "model_id": model_id,
            "symbol": ml_model.symbol,
            "model_type": ml_model.model_type,
            "metrics": metrics,
            "training_date": ml_model.training_date.isoformat(),
            "data_points": ml_model.data_points
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_id}/predictions/history")
async def get_model_predictions_history(
    model_id: int,
    limit: int = Query(50, description="Number of predictions to return"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical predictions for a model."""
    try:
        from app.db import models
        
        # Check if model exists and belongs to user
        ml_model = db.query(models.MLModel).filter(
            models.MLModel.id == model_id,
            models.MLModel.user_id == current_user,
            models.MLModel.is_active == True
        ).first()
        
        if not ml_model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # For now, return empty history as we don't have a predictions history table
        # In a real implementation, you would have a table to store predictions
        return {
            "model_id": model_id,
            "predictions": [],
            "message": "Prediction history not implemented yet"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/types/available")
async def get_available_model_types():
    """Get list of available model types."""
    return {
        "model_types": [
            {
                "name": "random_forest",
                "description": "Random Forest Regressor",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "gradient_boosting",
                "description": "Gradient Boosting Regressor",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "linear_regression",
                "description": "Linear Regression",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "ridge",
                "description": "Ridge Regression",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "lasso",
                "description": "Lasso Regression",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "svr",
                "description": "Support Vector Regression",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "neural_network",
                "description": "Multi-layer Perceptron",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "xgboost",
                "description": "XGBoost Regressor",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "lightgbm",
                "description": "LightGBM Regressor",
                "suitable_for": ["price_prediction", "sentiment", "portfolio_optimization"]
            },
            {
                "name": "lstm",
                "description": "Long Short-Term Memory Network",
                "suitable_for": ["price_prediction"]
            }
        ]
    }

@router.get("/models/features/available")
async def get_available_features():
    """Get list of available features for model training."""
    return {
        "features": [
            {
                "name": "close",
                "description": "Closing price",
                "type": "price"
            },
            {
                "name": "volume",
                "description": "Trading volume",
                "type": "volume"
            },
            {
                "name": "rsi",
                "description": "Relative Strength Index",
                "type": "technical"
            },
            {
                "name": "macd",
                "description": "MACD indicator",
                "type": "technical"
            },
            {
                "name": "sma_20",
                "description": "20-day Simple Moving Average",
                "type": "technical"
            },
            {
                "name": "sma_50",
                "description": "50-day Simple Moving Average",
                "type": "technical"
            },
            {
                "name": "bb_upper",
                "description": "Bollinger Bands Upper",
                "type": "technical"
            },
            {
                "name": "bb_lower",
                "description": "Bollinger Bands Lower",
                "type": "technical"
            },
            {
                "name": "stochastic",
                "description": "Stochastic Oscillator",
                "type": "technical"
            },
            {
                "name": "williams_r",
                "description": "Williams %R",
                "type": "technical"
            },
            {
                "name": "cci",
                "description": "Commodity Channel Index",
                "type": "technical"
            },
            {
                "name": "atr",
                "description": "Average True Range",
                "type": "technical"
            }
        ]
    }

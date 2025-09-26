from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.advanced_ml_service import AdvancedMLService
from pydantic import BaseModel
from typing import List, Optional
import asyncio

router = APIRouter(prefix="/api/advanced-ml", tags=["advanced-ml"])

class TrainModelsRequest(BaseModel):
    symbol: str
    model_types: Optional[List[str]] = None
    lookback_days: Optional[int] = 365

class PredictionRequest(BaseModel):
    symbol: str
    model_type: str
    days_ahead: Optional[int] = 7

@router.post("/train")
async def train_advanced_models(
    request: TrainModelsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Train advanced ML models for a symbol"""
    try:
        ml_service = AdvancedMLService(db)
        
        # Start training in background
        background_tasks.add_task(
            train_models_background,
            ml_service,
            request.symbol,
            request.model_types,
            request.lookback_days
        )
        
        return {
            "message": f"Training started for {request.symbol}",
            "symbol": request.symbol,
            "model_types": request.model_types or ["lstm", "transformer", "ensemble", "xgboost", "lightgbm", "catboost"],
            "status": "training_started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")

async def train_models_background(ml_service: AdvancedMLService, symbol: str, model_types: List[str], lookback_days: int):
    """Background task for training models"""
    try:
        result = ml_service.train_advanced_models(symbol, model_types)
        print(f"Training completed for {symbol}: {result}")
    except Exception as e:
        print(f"Training failed for {symbol}: {e}")

@router.get("/predictions/{symbol}")
async def get_ml_predictions(
    symbol: str,
    model_type: str = Query(..., description="Model type to use for predictions"),
    days_ahead: int = Query(7, description="Number of days to predict ahead"),
    db: Session = Depends(get_db)
):
    """Get predictions from a trained ML model"""
    try:
        ml_service = AdvancedMLService(db)
        predictions = ml_service.get_model_predictions(symbol.upper(), model_type, days_ahead)
        
        if "error" in predictions:
            raise HTTPException(status_code=400, detail=predictions["error"])
        
        return predictions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get predictions: {str(e)}")

@router.get("/performance/{symbol}")
async def get_model_performance(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get performance metrics for all trained models"""
    try:
        ml_service = AdvancedMLService(db)
        performance = ml_service.get_model_performance(symbol.upper())
        
        if "error" in performance:
            raise HTTPException(status_code=400, detail=performance["error"])
        
        return performance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")

@router.get("/models/available")
async def get_available_ml_models():
    """Get list of available ML models"""
    return {
        "models": [
            {
                "type": "lstm",
                "name": "LSTM Neural Network",
                "description": "Long Short-Term Memory network for time series prediction",
                "strengths": ["Pattern recognition", "Long-term dependencies", "Sequence modeling"],
                "best_for": "Trend following and pattern recognition",
                "training_time": "Medium",
                "accuracy": "High"
            },
            {
                "type": "transformer",
                "name": "Transformer Network",
                "description": "Attention-based neural network for sequence modeling",
                "strengths": ["Attention mechanism", "Context understanding", "Non-linear patterns"],
                "best_for": "Complex market dynamics and context-aware predictions",
                "training_time": "High",
                "accuracy": "Very High"
            },
            {
                "type": "ensemble",
                "name": "Ensemble Model",
                "description": "Combination of multiple models for improved accuracy",
                "strengths": ["Reduced overfitting", "Better generalization", "Robust predictions"],
                "best_for": "Overall market analysis and risk management",
                "training_time": "High",
                "accuracy": "Very High"
            },
            {
                "type": "xgboost",
                "name": "XGBoost",
                "description": "Gradient boosting framework for regression and classification",
                "strengths": ["High performance", "Feature importance", "Handles missing values"],
                "best_for": "Feature-based predictions and interpretability",
                "training_time": "Medium",
                "accuracy": "High"
            },
            {
                "type": "lightgbm",
                "name": "LightGBM",
                "description": "Light gradient boosting machine for fast training",
                "strengths": ["Fast training", "Memory efficient", "High accuracy"],
                "best_for": "Large datasets and real-time predictions",
                "training_time": "Low",
                "accuracy": "High"
            },
            {
                "type": "catboost",
                "name": "CatBoost",
                "description": "Gradient boosting with categorical features support",
                "strengths": ["Categorical features", "No overfitting", "Built-in regularization"],
                "best_for": "Mixed data types and robust predictions",
                "training_time": "Medium",
                "accuracy": "High"
            },
            {
                "type": "deep_learning",
                "name": "Deep Neural Network",
                "description": "Multi-layer neural network for complex pattern recognition",
                "strengths": ["Complex patterns", "Non-linear relationships", "Feature learning"],
                "best_for": "Complex market patterns and feature extraction",
                "training_time": "High",
                "accuracy": "Very High"
            }
        ]
    }

@router.get("/features/available")
async def get_available_features():
    """Get list of available features for ML models"""
    return {
        "features": [
            {
                "category": "Price Features",
                "features": [
                    {"name": "close", "description": "Closing price", "type": "numeric"},
                    {"name": "open", "description": "Opening price", "type": "numeric"},
                    {"name": "high", "description": "High price", "type": "numeric"},
                    {"name": "low", "description": "Low price", "type": "numeric"},
                    {"name": "volume", "description": "Trading volume", "type": "numeric"}
                ]
            },
            {
                "category": "Price Ratios",
                "features": [
                    {"name": "high_low_ratio", "description": "High to low price ratio", "type": "numeric"},
                    {"name": "close_open_ratio", "description": "Close to open price ratio", "type": "numeric"},
                    {"name": "volume_price_ratio", "description": "Volume to price ratio", "type": "numeric"}
                ]
            },
            {
                "category": "Returns",
                "features": [
                    {"name": "returns_1d", "description": "1-day returns", "type": "numeric"},
                    {"name": "returns_5d", "description": "5-day returns", "type": "numeric"},
                    {"name": "returns_10d", "description": "10-day returns", "type": "numeric"},
                    {"name": "returns_20d", "description": "20-day returns", "type": "numeric"}
                ]
            },
            {
                "category": "Moving Averages",
                "features": [
                    {"name": "sma_5", "description": "5-day Simple Moving Average", "type": "numeric"},
                    {"name": "sma_10", "description": "10-day Simple Moving Average", "type": "numeric"},
                    {"name": "sma_20", "description": "20-day Simple Moving Average", "type": "numeric"},
                    {"name": "sma_50", "description": "50-day Simple Moving Average", "type": "numeric"},
                    {"name": "ema_5", "description": "5-day Exponential Moving Average", "type": "numeric"},
                    {"name": "ema_10", "description": "10-day Exponential Moving Average", "type": "numeric"},
                    {"name": "ema_20", "description": "20-day Exponential Moving Average", "type": "numeric"},
                    {"name": "ema_50", "description": "50-day Exponential Moving Average", "type": "numeric"}
                ]
            },
            {
                "category": "Volatility",
                "features": [
                    {"name": "volatility_5d", "description": "5-day volatility", "type": "numeric"},
                    {"name": "volatility_20d", "description": "20-day volatility", "type": "numeric"},
                    {"name": "volatility_ratio", "description": "Short to long term volatility ratio", "type": "numeric"}
                ]
            },
            {
                "category": "Technical Indicators",
                "features": [
                    {"name": "rsi", "description": "Relative Strength Index", "type": "numeric"},
                    {"name": "macd", "description": "MACD indicator", "type": "numeric"},
                    {"name": "bollinger_upper", "description": "Bollinger Bands upper", "type": "numeric"},
                    {"name": "bollinger_lower", "description": "Bollinger Bands lower", "type": "numeric"},
                    {"name": "bollinger_position", "description": "Position within Bollinger Bands", "type": "numeric"}
                ]
            },
            {
                "category": "Volume Indicators",
                "features": [
                    {"name": "volume_sma_20", "description": "20-day volume moving average", "type": "numeric"},
                    {"name": "volume_ratio", "description": "Current to average volume ratio", "type": "numeric"},
                    {"name": "price_volume_trend", "description": "Price-volume trend indicator", "type": "numeric"}
                ]
            },
            {
                "category": "Momentum Indicators",
                "features": [
                    {"name": "momentum_5d", "description": "5-day momentum", "type": "numeric"},
                    {"name": "momentum_10d", "description": "10-day momentum", "type": "numeric"},
                    {"name": "momentum_20d", "description": "20-day momentum", "type": "numeric"}
                ]
            },
            {
                "category": "Support/Resistance",
                "features": [
                    {"name": "support_level", "description": "20-day support level", "type": "numeric"},
                    {"name": "resistance_level", "description": "20-day resistance level", "type": "numeric"},
                    {"name": "support_distance", "description": "Distance to support level", "type": "numeric"},
                    {"name": "resistance_distance", "description": "Distance to resistance level", "type": "numeric"}
                ]
            },
            {
                "category": "Time Features",
                "features": [
                    {"name": "day_of_week", "description": "Day of week (0-6)", "type": "categorical"},
                    {"name": "month", "description": "Month (1-12)", "type": "categorical"},
                    {"name": "quarter", "description": "Quarter (1-4)", "type": "categorical"}
                ]
            }
        ]
    }

@router.get("/training/status/{symbol}")
async def get_training_status(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get training status for a symbol"""
    try:
        ml_service = AdvancedMLService(db)
        
        # Check which models are trained
        import os
        models_dir = "ml_models"
        model_types = ["lstm", "transformer", "ensemble", "xgboost", "lightgbm", "catboost", "deep_learning"]
        
        trained_models = []
        for model_type in model_types:
            model_path = os.path.join(models_dir, f"{symbol.upper()}_{model_type}_model.joblib")
            if os.path.exists(model_path):
                trained_models.append(model_type)
        
        return {
            "symbol": symbol.upper(),
            "trained_models": trained_models,
            "total_models": len(model_types),
            "training_progress": len(trained_models) / len(model_types) * 100,
            "status": "completed" if len(trained_models) == len(model_types) else "in_progress"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get training status: {str(e)}")

@router.delete("/models/{symbol}")
async def delete_models(
    symbol: str,
    model_type: Optional[str] = Query(None, description="Specific model type to delete"),
    db: Session = Depends(get_db)
):
    """Delete trained models for a symbol"""
    try:
        import os
        import shutil
        
        models_dir = "ml_models"
        scalers_dir = "ml_scalers"
        
        if model_type:
            # Delete specific model
            model_path = os.path.join(models_dir, f"{symbol.upper()}_{model_type}_model.joblib")
            scaler_path = os.path.join(scalers_dir, f"{symbol.upper()}_{model_type}_scaler.joblib")
            
            deleted_files = []
            if os.path.exists(model_path):
                os.remove(model_path)
                deleted_files.append(model_path)
            if os.path.exists(scaler_path):
                os.remove(scaler_path)
                deleted_files.append(scaler_path)
            
            return {
                "message": f"Deleted {model_type} model for {symbol}",
                "deleted_files": deleted_files
            }
        else:
            # Delete all models for symbol
            model_types = ["lstm", "transformer", "ensemble", "xgboost", "lightgbm", "catboost", "deep_learning"]
            deleted_files = []
            
            for model_type in model_types:
                model_path = os.path.join(models_dir, f"{symbol.upper()}_{model_type}_model.joblib")
                scaler_path = os.path.join(scalers_dir, f"{symbol.upper()}_{model_type}_scaler.joblib")
                
                if os.path.exists(model_path):
                    os.remove(model_path)
                    deleted_files.append(model_path)
                if os.path.exists(scaler_path):
                    os.remove(scaler_path)
                    deleted_files.append(scaler_path)
            
            return {
                "message": f"Deleted all models for {symbol}",
                "deleted_files": deleted_files
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete models: {str(e)}")

@router.get("/models/list")
async def list_trained_models(
    db: Session = Depends(get_db)
):
    """List all trained models"""
    try:
        import os
        import glob
        
        models_dir = "ml_models"
        if not os.path.exists(models_dir):
            return {"trained_models": []}
        
        # Get all model files
        model_files = glob.glob(os.path.join(models_dir, "*_model.joblib"))
        
        trained_models = []
        for model_file in model_files:
            filename = os.path.basename(model_file)
            # Extract symbol and model type from filename
            parts = filename.replace("_model.joblib", "").split("_")
            if len(parts) >= 2:
                model_type = parts[-1]
                symbol = "_".join(parts[:-1])
                
                # Get file modification time
                mod_time = os.path.getmtime(model_file)
                mod_date = datetime.fromtimestamp(mod_time).isoformat()
                
                trained_models.append({
                    "symbol": symbol,
                    "model_type": model_type,
                    "file_path": model_file,
                    "created_at": mod_date
                })
        
        return {
            "trained_models": trained_models,
            "total_models": len(trained_models)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import joblib
import os
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import warnings
warnings.filterwarnings('ignore')

from app.db import models
from app.services.market_data_service import MarketDataService
from app.services.technical_analysis_service import TechnicalAnalysisService

logger = logging.getLogger(__name__)

class MLTrainingService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.technical_service = TechnicalAnalysisService(db)
        self.models_dir = "models"
        self.scalers_dir = "scalers"
        
        # Create directories if they don't exist
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.scalers_dir, exist_ok=True)
    
    def train_price_prediction_model(self, user_id: str, symbol: str, model_type: str = "random_forest", 
                                   features: List[str] = None, target_days: int = 1) -> Dict[str, Any]:
        """Train a custom price prediction model for a specific symbol."""
        try:
            if features is None:
                features = ["close", "volume", "rsi", "macd", "sma_20", "sma_50", "bb_upper", "bb_lower"]
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1000)  # ~3 years of data
            
            price_data = self.market_data_service.get_historical_data(symbol, start_date, end_date)
            if price_data is None or price_data.empty:
                return {"error": "Insufficient historical data"}
            
            # Calculate technical indicators
            technical_data = self.technical_service.calculate_technical_indicators(symbol, price_data)
            
            # Combine price and technical data
            combined_data = pd.concat([price_data, technical_data], axis=1)
            combined_data = combined_data.dropna()
            
            if len(combined_data) < 100:
                return {"error": "Insufficient data after feature engineering"}
            
            # Prepare features and target
            feature_columns = [col for col in features if col in combined_data.columns]
            if not feature_columns:
                return {"error": "No valid features found"}
            
            X = combined_data[feature_columns].values
            y = combined_data['close'].shift(-target_days).dropna().values
            
            # Align X and y
            min_length = min(len(X), len(y))
            X = X[:min_length]
            y = y[:min_length]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = self._create_model(model_type)
            
            if model_type == "lstm":
                # Reshape for LSTM
                X_train_scaled = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
                X_test_scaled = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
                
                model.fit(X_train_scaled, y_train, epochs=100, batch_size=32, verbose=0)
            else:
                model.fit(X_train_scaled, y_train)
            
            # Make predictions
            if model_type == "lstm":
                y_pred = model.predict(X_test_scaled).flatten()
            else:
                y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Calculate accuracy (percentage of correct direction predictions)
            direction_accuracy = np.mean(np.sign(y_pred[1:] - y_pred[:-1]) == np.sign(y_test[1:] - y_test[:-1]))
            
            # Save model and scaler
            model_filename = f"{user_id}_{symbol}_{model_type}_{target_days}d.joblib"
            scaler_filename = f"{user_id}_{symbol}_{model_type}_{target_days}d_scaler.joblib"
            
            if model_type == "lstm":
                model.save(os.path.join(self.models_dir, model_filename.replace('.joblib', '.h5')))
            else:
                joblib.dump(model, os.path.join(self.models_dir, model_filename))
            
            joblib.dump(scaler, os.path.join(self.scalers_dir, scaler_filename))
            
            # Save model metadata
            model_metadata = {
                "user_id": user_id,
                "symbol": symbol,
                "model_type": model_type,
                "features": feature_columns,
                "target_days": target_days,
                "training_date": datetime.now().isoformat(),
                "data_points": len(combined_data),
                "metrics": {
                    "mse": float(mse),
                    "mae": float(mae),
                    "r2": float(r2),
                    "rmse": float(rmse),
                    "direction_accuracy": float(direction_accuracy)
                },
                "model_filename": model_filename,
                "scaler_filename": scaler_filename
            }
            
            # Save to database
            ml_model = models.MLModel(
                user_id=user_id,
                symbol=symbol,
                model_type=model_type,
                features=json.dumps(feature_columns),
                target_days=target_days,
                training_date=datetime.now(),
                data_points=len(combined_data),
                metrics=json.dumps(model_metadata["metrics"]),
                model_filename=model_filename,
                scaler_filename=scaler_filename,
                is_active=True
            )
            
            self.db.add(ml_model)
            self.db.commit()
            
            return {
                "success": True,
                "model_id": ml_model.id,
                "metrics": model_metadata["metrics"],
                "features": feature_columns,
                "data_points": len(combined_data),
                "training_date": model_metadata["training_date"]
            }
            
        except Exception as e:
            logger.error(f"Error training price prediction model: {e}")
            return {"error": str(e)}
    
    def train_sentiment_model(self, user_id: str, symbol: str, model_type: str = "random_forest") -> Dict[str, Any]:
        """Train a sentiment-based prediction model."""
        try:
            # Get news data and sentiment scores
            # This would integrate with the news service
            # For now, we'll create a mock implementation
            
            # Mock sentiment data
            np.random.seed(42)
            n_samples = 1000
            
            # Generate mock features
            sentiment_scores = np.random.uniform(-1, 1, n_samples)
            news_volume = np.random.poisson(10, n_samples)
            price_changes = np.random.normal(0, 0.02, n_samples)
            
            # Create target (next day price change)
            target = price_changes + 0.1 * sentiment_scores + 0.05 * np.random.normal(0, 1, n_samples)
            
            # Prepare features
            X = np.column_stack([sentiment_scores, news_volume, price_changes])
            y = target
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = self._create_model(model_type)
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model
            model_filename = f"{user_id}_{symbol}_sentiment_{model_type}.joblib"
            scaler_filename = f"{user_id}_{symbol}_sentiment_{model_type}_scaler.joblib"
            
            joblib.dump(model, os.path.join(self.models_dir, model_filename))
            joblib.dump(scaler, os.path.join(self.scalers_dir, scaler_filename))
            
            # Save to database
            ml_model = models.MLModel(
                user_id=user_id,
                symbol=symbol,
                model_type=f"sentiment_{model_type}",
                features=json.dumps(["sentiment_score", "news_volume", "price_change"]),
                target_days=1,
                training_date=datetime.now(),
                data_points=n_samples,
                metrics=json.dumps({
                    "mse": float(mse),
                    "mae": float(mae),
                    "r2": float(r2)
                }),
                model_filename=model_filename,
                scaler_filename=scaler_filename,
                is_active=True
            )
            
            self.db.add(ml_model)
            self.db.commit()
            
            return {
                "success": True,
                "model_id": ml_model.id,
                "metrics": {
                    "mse": float(mse),
                    "mae": float(mae),
                    "r2": float(r2)
                },
                "features": ["sentiment_score", "news_volume", "price_change"],
                "data_points": n_samples
            }
            
        except Exception as e:
            logger.error(f"Error training sentiment model: {e}")
            return {"error": str(e)}
    
    def train_portfolio_optimization_model(self, user_id: str, model_type: str = "random_forest") -> Dict[str, Any]:
        """Train a portfolio optimization model."""
        try:
            # Get portfolio data
            portfolio = self.db.query(models.Portfolio).filter(
                models.Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                return {"error": "Portfolio not found"}
            
            holdings = self.db.query(models.Holding).filter(
                models.Holding.portfolio_id == portfolio.id
            ).all()
            
            if not holdings:
                return {"error": "No holdings found"}
            
            # Get historical data for all holdings
            symbols = [holding.symbol for holding in holdings]
            end_date = datetime.now()
            start_date = end_date - timedelta(days=500)
            
            # Prepare features and targets
            features = []
            targets = []
            
            for symbol in symbols:
                price_data = self.market_data_service.get_historical_data(symbol, start_date, end_date)
                if price_data is not None and not price_data.empty:
                    # Calculate features
                    returns = price_data['close'].pct_change().dropna()
                    volatility = returns.rolling(20).std()
                    momentum = price_data['close'].pct_change(20)
                    
                    # Combine features
                    feature_data = pd.DataFrame({
                        'returns': returns,
                        'volatility': volatility,
                        'momentum': momentum
                    }).dropna()
                    
                    if len(feature_data) > 50:
                        features.append(feature_data.values)
                        # Target: next period return
                        target = returns.shift(-1).dropna()
                        targets.append(target.values[:len(feature_data)])
            
            if not features:
                return {"error": "Insufficient data for training"}
            
            # Combine all data
            X = np.vstack(features)
            y = np.hstack(targets)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = self._create_model(model_type)
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model
            model_filename = f"{user_id}_portfolio_optimization_{model_type}.joblib"
            scaler_filename = f"{user_id}_portfolio_optimization_{model_type}_scaler.joblib"
            
            joblib.dump(model, os.path.join(self.models_dir, model_filename))
            joblib.dump(scaler, os.path.join(self.scalers_dir, scaler_filename))
            
            # Save to database
            ml_model = models.MLModel(
                user_id=user_id,
                symbol="PORTFOLIO",
                model_type=f"portfolio_optimization_{model_type}",
                features=json.dumps(["returns", "volatility", "momentum"]),
                target_days=1,
                training_date=datetime.now(),
                data_points=len(X),
                metrics=json.dumps({
                    "mse": float(mse),
                    "mae": float(mae),
                    "r2": float(r2)
                }),
                model_filename=model_filename,
                scaler_filename=scaler_filename,
                is_active=True
            )
            
            self.db.add(ml_model)
            self.db.commit()
            
            return {
                "success": True,
                "model_id": ml_model.id,
                "metrics": {
                    "mse": float(mse),
                    "mae": float(mae),
                    "r2": float(r2)
                },
                "features": ["returns", "volatility", "momentum"],
                "data_points": len(X)
            }
            
        except Exception as e:
            logger.error(f"Error training portfolio optimization model: {e}")
            return {"error": str(e)}
    
    def get_model_predictions(self, user_id: str, model_id: int, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get predictions from a trained model."""
        try:
            # Get model from database
            ml_model = self.db.query(models.MLModel).filter(
                models.MLModel.id == model_id,
                models.MLModel.user_id == user_id,
                models.MLModel.is_active == True
            ).first()
            
            if not ml_model:
                return {"error": "Model not found"}
            
            # Load model and scaler
            model_path = os.path.join(self.models_dir, ml_model.model_filename)
            scaler_path = os.path.join(self.scalers_dir, ml_model.scaler_filename)
            
            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                return {"error": "Model files not found"}
            
            # Load scaler
            scaler = joblib.load(scaler_path)
            
            # Load model
            if ml_model.model_type.startswith("lstm"):
                from tensorflow.keras.models import load_model
                model = load_model(model_path.replace('.joblib', '.h5'))
            else:
                model = joblib.load(model_path)
            
            # Prepare input data
            features = json.loads(ml_model.features)
            input_values = []
            
            for feature in features:
                if feature in input_data:
                    input_values.append(input_data[feature])
                else:
                    return {"error": f"Missing feature: {feature}"}
            
            # Scale input
            input_scaled = scaler.transform([input_values])
            
            # Make prediction
            if ml_model.model_type.startswith("lstm"):
                input_scaled = input_scaled.reshape((input_scaled.shape[0], 1, input_scaled.shape[1]))
                prediction = model.predict(input_scaled)[0][0]
            else:
                prediction = model.predict(input_scaled)[0]
            
            return {
                "prediction": float(prediction),
                "model_id": model_id,
                "model_type": ml_model.model_type,
                "features_used": features,
                "prediction_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting model predictions: {e}")
            return {"error": str(e)}
    
    def get_user_models(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all models for a user."""
        try:
            models_list = self.db.query(models.MLModel).filter(
                models.MLModel.user_id == user_id,
                models.MLModel.is_active == True
            ).all()
            
            result = []
            for model in models_list:
                result.append({
                    "id": model.id,
                    "symbol": model.symbol,
                    "model_type": model.model_type,
                    "features": json.loads(model.features),
                    "target_days": model.target_days,
                    "training_date": model.training_date.isoformat(),
                    "data_points": model.data_points,
                    "metrics": json.loads(model.metrics),
                    "is_active": model.is_active
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user models: {e}")
            return []
    
    def delete_model(self, user_id: str, model_id: int) -> Dict[str, Any]:
        """Delete a trained model."""
        try:
            # Get model from database
            ml_model = self.db.query(models.MLModel).filter(
                models.MLModel.id == model_id,
                models.MLModel.user_id == user_id
            ).first()
            
            if not ml_model:
                return {"error": "Model not found"}
            
            # Delete model files
            model_path = os.path.join(self.models_dir, ml_model.model_filename)
            scaler_path = os.path.join(self.scalers_dir, ml_model.scaler_filename)
            
            if os.path.exists(model_path):
                os.remove(model_path)
            if os.path.exists(scaler_path):
                os.remove(scaler_path)
            
            # Mark as inactive in database
            ml_model.is_active = False
            self.db.commit()
            
            return {"success": True, "message": "Model deleted successfully"}
            
        except Exception as e:
            logger.error(f"Error deleting model: {e}")
            return {"error": str(e)}
    
    def _create_model(self, model_type: str):
        """Create a model instance based on type."""
        if model_type == "random_forest":
            return RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == "gradient_boosting":
            return GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == "linear_regression":
            return LinearRegression()
        elif model_type == "ridge":
            return Ridge(alpha=1.0)
        elif model_type == "lasso":
            return Lasso(alpha=1.0)
        elif model_type == "svr":
            return SVR(kernel='rbf', C=1.0, gamma='scale')
        elif model_type == "neural_network":
            return MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=500)
        elif model_type == "xgboost":
            return xgb.XGBRegressor(n_estimators=100, random_state=42)
        elif model_type == "lightgbm":
            return lgb.LGBMRegressor(n_estimators=100, random_state=42)
        elif model_type == "lstm":
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(1, 8)),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1)
            ])
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            return model
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def retrain_model(self, user_id: str, model_id: int) -> Dict[str, Any]:
        """Retrain an existing model with new data."""
        try:
            # Get model from database
            ml_model = self.db.query(models.MLModel).filter(
                models.MLModel.id == model_id,
                models.MLModel.user_id == user_id
            ).first()
            
            if not ml_model:
                return {"error": "Model not found"}
            
            # Retrain based on model type
            if ml_model.model_type.startswith("sentiment"):
                result = self.train_sentiment_model(user_id, ml_model.symbol, ml_model.model_type.replace("sentiment_", ""))
            elif ml_model.model_type.startswith("portfolio_optimization"):
                result = self.train_portfolio_optimization_model(user_id, ml_model.model_type.replace("portfolio_optimization_", ""))
            else:
                result = self.train_price_prediction_model(
                    user_id, 
                    ml_model.symbol, 
                    ml_model.model_type, 
                    json.loads(ml_model.features),
                    ml_model.target_days
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error retraining model: {e}")
            return {"error": str(e)}

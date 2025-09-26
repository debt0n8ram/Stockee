import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models

class TestMLTraining:
    """Test ML training functionality."""
    
    def test_train_price_prediction_model(self, client: TestClient, test_user):
        """Test training a price prediction model."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "random_forest",
                "features": ["close", "volume", "rsi"],
                "target_days": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "model_id" in data
        assert "metrics" in data
    
    def test_train_price_prediction_model_invalid_symbol(self, client: TestClient, test_user):
        """Test training a model with invalid symbol."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "INVALID",
                "model_type": "random_forest",
                "features": ["close", "volume"],
                "target_days": 1
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_train_price_prediction_model_invalid_model_type(self, client: TestClient, test_user):
        """Test training a model with invalid model type."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "invalid_model",
                "features": ["close", "volume"],
                "target_days": 1
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_train_price_prediction_model_empty_features(self, client: TestClient, test_user):
        """Test training a model with empty features."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "random_forest",
                "features": [],
                "target_days": 1
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_train_price_prediction_model_invalid_target_days(self, client: TestClient, test_user):
        """Test training a model with invalid target days."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "random_forest",
                "features": ["close", "volume"],
                "target_days": 0
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_train_sentiment_model(self, client: TestClient, test_user):
        """Test training a sentiment model."""
        response = client.post(
            "/api/ml-training/train/sentiment",
            json={
                "symbol": "AAPL",
                "model_type": "random_forest"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "model_id" in data
        assert "metrics" in data
    
    def test_train_sentiment_model_invalid_symbol(self, client: TestClient, test_user):
        """Test training a sentiment model with invalid symbol."""
        response = client.post(
            "/api/ml-training/train/sentiment",
            json={
                "symbol": "INVALID",
                "model_type": "random_forest"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_train_portfolio_optimization_model(self, client: TestClient, test_user):
        """Test training a portfolio optimization model."""
        response = client.post(
            "/api/ml-training/train/portfolio-optimization",
            json={
                "model_type": "random_forest"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "model_id" in data
        assert "metrics" in data
    
    def test_train_portfolio_optimization_model_invalid_model_type(self, client: TestClient, test_user):
        """Test training a portfolio optimization model with invalid model type."""
        response = client.post(
            "/api/ml-training/train/portfolio-optimization",
            json={
                "model_type": "invalid_model"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_get_model_predictions(self, client: TestClient, test_user, test_ml_model):
        """Test getting model predictions."""
        response = client.post(
            "/api/ml-training/predict",
            json={
                "model_id": test_ml_model.id,
                "input_data": {
                    "close": 150.00,
                    "volume": 1000000,
                    "rsi": 50.0
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "model_id" in data
    
    def test_get_model_predictions_invalid_model_id(self, client: TestClient, test_user):
        """Test getting predictions with invalid model ID."""
        response = client.post(
            "/api/ml-training/predict",
            json={
                "model_id": 99999,
                "input_data": {
                    "close": 150.00,
                    "volume": 1000000,
                    "rsi": 50.0
                }
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_get_model_predictions_missing_input_data(self, client: TestClient, test_user, test_ml_model):
        """Test getting predictions with missing input data."""
        response = client.post(
            "/api/ml-training/predict",
            json={
                "model_id": test_ml_model.id,
                "input_data": {
                    "close": 150.00
                    # Missing volume and rsi
                }
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_get_user_models(self, client: TestClient, test_user, test_ml_model):
        """Test getting user models."""
        response = client.get("/api/ml-training/models")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) >= 1
    
    def test_get_model_details(self, client: TestClient, test_user, test_ml_model):
        """Test getting model details."""
        response = client.get(f"/api/ml-training/models/{test_ml_model.id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "symbol" in data
        assert "model_type" in data
        assert "features" in data
        assert "metrics" in data
    
    def test_get_model_details_invalid_id(self, client: TestClient, test_user):
        """Test getting model details with invalid ID."""
        response = client.get("/api/ml-training/models/99999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_model_performance(self, client: TestClient, test_user, test_ml_model):
        """Test getting model performance."""
        response = client.get(f"/api/ml-training/models/{test_ml_model.id}/performance")
        assert response.status_code == 200
        data = response.json()
        assert "model_id" in data
        assert "symbol" in data
        assert "model_type" in data
        assert "metrics" in data
    
    def test_get_model_performance_invalid_id(self, client: TestClient, test_user):
        """Test getting model performance with invalid ID."""
        response = client.get("/api/ml-training/models/99999/performance")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_delete_model(self, client: TestClient, test_user, test_ml_model):
        """Test deleting a model."""
        response = client.delete(f"/api/ml-training/models/{test_ml_model.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_delete_model_invalid_id(self, client: TestClient, test_user):
        """Test deleting a model with invalid ID."""
        response = client.delete("/api/ml-training/models/99999")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_retrain_model(self, client: TestClient, test_user, test_ml_model):
        """Test retraining a model."""
        response = client.post(f"/api/ml-training/models/{test_ml_model.id}/retrain")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "model_id" in data
    
    def test_retrain_model_invalid_id(self, client: TestClient, test_user):
        """Test retraining a model with invalid ID."""
        response = client.post("/api/ml-training/models/99999/retrain")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_get_model_predictions_history(self, client: TestClient, test_user, test_ml_model):
        """Test getting model predictions history."""
        response = client.get(f"/api/ml-training/models/{test_ml_model.id}/predictions/history")
        assert response.status_code == 200
        data = response.json()
        assert "model_id" in data
        assert "predictions" in data
    
    def test_get_model_predictions_history_invalid_id(self, client: TestClient, test_user):
        """Test getting model predictions history with invalid ID."""
        response = client.get("/api/ml-training/models/99999/predictions/history")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_available_model_types(self, client: TestClient, test_user):
        """Test getting available model types."""
        response = client.get("/api/ml-training/models/types/available")
        assert response.status_code == 200
        data = response.json()
        assert "model_types" in data
        assert len(data["model_types"]) > 0
    
    def test_get_available_features(self, client: TestClient, test_user):
        """Test getting available features."""
        response = client.get("/api/ml-training/models/features/available")
        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert len(data["features"]) > 0
    
    def test_train_multiple_models_same_symbol(self, client: TestClient, test_user):
        """Test training multiple models for the same symbol."""
        # Train first model
        response1 = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "random_forest",
                "features": ["close", "volume"],
                "target_days": 1
            }
        )
        assert response1.status_code == 200
        
        # Train second model
        response2 = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "gradient_boosting",
                "features": ["close", "volume", "rsi"],
                "target_days": 1
            }
        )
        assert response2.status_code == 200
        
        # Both should succeed
        data1 = response1.json()
        data2 = response2.json()
        assert data1["success"] == True
        assert data2["success"] == True
        assert data1["model_id"] != data2["model_id"]
    
    def test_train_model_with_lstm(self, client: TestClient, test_user):
        """Test training a model with LSTM."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "lstm",
                "features": ["close", "volume", "rsi", "macd", "sma_20", "sma_50", "bb_upper", "bb_lower"],
                "target_days": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "model_id" in data
    
    def test_train_model_with_xgboost(self, client: TestClient, test_user):
        """Test training a model with XGBoost."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "xgboost",
                "features": ["close", "volume", "rsi"],
                "target_days": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "model_id" in data
    
    def test_train_model_with_lightgbm(self, client: TestClient, test_user):
        """Test training a model with LightGBM."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "lightgbm",
                "features": ["close", "volume", "rsi"],
                "target_days": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "model_id" in data
    
    def test_train_model_with_neural_network(self, client: TestClient, test_user):
        """Test training a model with Neural Network."""
        response = client.post(
            "/api/ml-training/train/price-prediction",
            json={
                "symbol": "AAPL",
                "model_type": "neural_network",
                "features": ["close", "volume", "rsi"],
                "target_days": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "model_id" in data

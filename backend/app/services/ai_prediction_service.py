import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db import models
from app.services.market_data_service import MarketDataService
import logging
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AIPredictionService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        
    def get_price_predictions(self, symbol: str, days_ahead: int = 7) -> Dict:
        """Get AI predictions for a stock symbol"""
        try:
            # Get historical data
            historical_data = self._get_historical_data(symbol, days=90)
            if not historical_data or len(historical_data) < 30:
                return {"error": "Insufficient historical data for predictions"}
            
            # Prepare features
            features = self._prepare_features(historical_data)
            
            # Generate predictions using multiple models
            predictions = {}
            
            # Simple Moving Average
            predictions['moving_average'] = self._moving_average_prediction(historical_data, days_ahead)
            
            # Linear Regression
            predictions['linear_regression'] = self._linear_regression_prediction(features, days_ahead)
            
            # Trend Analysis
            predictions['trend_analysis'] = self._trend_analysis_prediction(historical_data, days_ahead)
            
            # Volatility-based prediction
            predictions['volatility_model'] = self._volatility_prediction(historical_data, days_ahead)
            
            # Ensemble prediction (average of all models)
            all_predictions = [pred for pred in predictions.values() if isinstance(pred, dict) and 'predicted_price' in pred]
            if all_predictions:
                avg_price = np.mean([p['predicted_price'] for p in all_predictions])
                avg_confidence = np.mean([p.get('confidence', 0.5) for p in all_predictions])
                
                predictions['ensemble'] = {
                    'predicted_price': round(avg_price, 2),
                    'confidence': round(avg_confidence, 2),
                    'model_name': 'Ensemble',
                    'description': 'Average of all prediction models'
                }
            
            # Save predictions to database
            self._save_predictions(symbol, predictions)
            
            return {
                'symbol': symbol,
                'current_price': historical_data[-1]['close'],
                'predictions': predictions,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating predictions for {symbol}: {e}")
            return {"error": f"Failed to generate predictions: {str(e)}"}

    def _get_historical_data(self, symbol: str, days: int = 90) -> List[Dict]:
        """Get historical price data for a symbol"""
        try:
            # Get data from database first
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            prices = self.db.query(models.Price).join(models.Asset).filter(
                models.Asset.symbol == symbol,
                models.Price.timestamp >= start_date,
                models.Price.timestamp <= end_date
            ).order_by(models.Price.timestamp).all()
            
            if len(prices) < 10:
                # If not enough data in database, fetch from API
                api_data = self.market_data_service.get_historical_prices(symbol, days)
                if api_data:
                    return api_data
            
            # Convert database results to list of dicts
            return [
                {
                    'date': price.timestamp.date(),
                    'open': float(price.open_price),
                    'high': float(price.high_price),
                    'low': float(price.low_price),
                    'close': float(price.close_price),
                    'volume': int(price.volume) if price.volume else 0
                }
                for price in prices
            ]
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []

    def _prepare_features(self, data: List[Dict]) -> np.ndarray:
        """Prepare features for machine learning models"""
        df = pd.DataFrame(data)
        
        # Calculate technical indicators
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        
        df['rsi'] = self._calculate_rsi(df['close'])
        df['macd'] = self._calculate_macd(df['close'])
        
        # Price changes
        df['price_change'] = df['close'].pct_change()
        df['volume_change'] = df['volume'].pct_change()
        
        # Volatility
        df['volatility'] = df['price_change'].rolling(window=10).std()
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        # Select features
        feature_columns = ['sma_5', 'sma_10', 'sma_20', 'rsi', 'macd', 'price_change', 'volume_change', 'volatility']
        features = df[feature_columns].values
        
        return features

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd

    def _moving_average_prediction(self, data: List[Dict], days_ahead: int) -> Dict:
        """Simple moving average prediction"""
        try:
            closes = [d['close'] for d in data[-20:]]  # Last 20 days
            sma_short = np.mean(closes[-5:])  # 5-day SMA
            sma_long = np.mean(closes[-20:])  # 20-day SMA
            
            # Simple trend continuation
            trend = (sma_short - sma_long) / sma_long
            current_price = closes[-1]
            predicted_price = current_price * (1 + trend * days_ahead / 20)
            
            confidence = max(0.1, min(0.8, 1 - abs(trend) * 2))
            
            return {
                'predicted_price': round(predicted_price, 2),
                'confidence': round(confidence, 2),
                'model_name': 'Moving Average',
                'description': f'Based on {len(closes)}-day moving average trend'
            }
        except Exception as e:
            logger.error(f"Error in moving average prediction: {e}")
            return {'error': str(e)}

    def _linear_regression_prediction(self, features: np.ndarray, days_ahead: int) -> Dict:
        """Linear regression prediction"""
        try:
            if len(features) < 10:
                return {'error': 'Insufficient data for linear regression'}
            
            # Use last 10 days as features, next day as target
            X = features[:-1]  # All but last
            y = features[1:, 0]  # Close prices shifted by 1
            
            if len(X) != len(y):
                min_len = min(len(X), len(y))
                X = X[:min_len]
                y = y[:min_len]
            
            # Train model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next day
            last_features = features[-1].reshape(1, -1)
            predicted_price = model.predict(last_features)[0]
            
            # Calculate confidence based on model performance
            y_pred = model.predict(X)
            mae = mean_absolute_error(y, y_pred)
            confidence = max(0.1, min(0.9, 1 - mae / np.mean(y)))
            
            return {
                'predicted_price': round(predicted_price, 2),
                'confidence': round(confidence, 2),
                'model_name': 'Linear Regression',
                'description': 'Machine learning model trained on technical indicators'
            }
        except Exception as e:
            logger.error(f"Error in linear regression prediction: {e}")
            return {'error': str(e)}

    def _trend_analysis_prediction(self, data: List[Dict], days_ahead: int) -> Dict:
        """Trend analysis prediction"""
        try:
            closes = [d['close'] for d in data[-30:]]  # Last 30 days
            
            # Calculate trend
            x = np.arange(len(closes))
            trend_coef = np.polyfit(x, closes, 1)[0]
            
            current_price = closes[-1]
            predicted_price = current_price + (trend_coef * days_ahead)
            
            # Confidence based on trend consistency
            recent_trends = []
            for i in range(5, len(closes)):
                short_trend = (closes[i] - closes[i-5]) / closes[i-5]
                recent_trends.append(short_trend)
            
            trend_consistency = 1 - np.std(recent_trends) if recent_trends else 0.5
            confidence = max(0.1, min(0.8, trend_consistency))
            
            return {
                'predicted_price': round(predicted_price, 2),
                'confidence': round(confidence, 2),
                'model_name': 'Trend Analysis',
                'description': f'Linear trend analysis over {len(closes)} days'
            }
        except Exception as e:
            logger.error(f"Error in trend analysis prediction: {e}")
            return {'error': str(e)}

    def _volatility_prediction(self, data: List[Dict], days_ahead: int) -> Dict:
        """Volatility-based prediction"""
        try:
            closes = [d['close'] for d in data[-20:]]
            volumes = [d['volume'] for d in data[-20:]]
            
            # Calculate volatility
            returns = np.diff(closes) / closes[:-1]
            volatility = np.std(returns)
            
            # Volume-weighted prediction
            avg_volume = np.mean(volumes)
            recent_volume = np.mean(volumes[-5:])
            volume_factor = recent_volume / avg_volume if avg_volume > 0 else 1
            
            current_price = closes[-1]
            
            # Monte Carlo simulation
            simulations = []
            for _ in range(100):
                random_return = np.random.normal(0, volatility)
                simulated_price = current_price * (1 + random_return)
                simulations.append(simulated_price)
            
            predicted_price = np.median(simulations)
            
            # Confidence based on volatility (lower volatility = higher confidence)
            confidence = max(0.1, min(0.7, 1 - volatility * 10))
            
            return {
                'predicted_price': round(predicted_price, 2),
                'confidence': round(confidence, 2),
                'model_name': 'Volatility Model',
                'description': f'Monte Carlo simulation with {volatility:.3f} volatility'
            }
        except Exception as e:
            logger.error(f"Error in volatility prediction: {e}")
            return {'error': str(e)}

    def _save_predictions(self, symbol: str, predictions: Dict):
        """Save predictions to database"""
        try:
            for model_name, prediction in predictions.items():
                if isinstance(prediction, dict) and 'predicted_price' in prediction:
                    ai_prediction = models.AIPrediction(
                        symbol=symbol,
                        model_name=prediction['model_name'],
                        prediction_date=datetime.now(),
                        target_date=datetime.now() + timedelta(days=7),
                        predicted_price=prediction['predicted_price'],
                        confidence=prediction.get('confidence', 0.5),
                        model_version='1.0'
                    )
                    self.db.add(ai_prediction)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving predictions: {e}")
            self.db.rollback()

    def get_prediction_history(self, symbol: str, limit: int = 20) -> List[Dict]:
        """Get prediction history for a symbol"""
        try:
            predictions = self.db.query(models.AIPrediction).filter(
                models.AIPrediction.symbol == symbol
            ).order_by(models.AIPrediction.prediction_date.desc()).limit(limit).all()
            
            return [
                {
                    'id': p.id,
                    'symbol': p.symbol,
                    'model_name': p.model_name,
                    'prediction_date': p.prediction_date,
                    'target_date': p.target_date,
                    'predicted_price': float(p.predicted_price),
                    'confidence': float(p.confidence) if p.confidence else None,
                    'model_version': p.model_version
                }
                for p in predictions
            ]
        except Exception as e:
            logger.error(f"Error getting prediction history: {e}")
            return []

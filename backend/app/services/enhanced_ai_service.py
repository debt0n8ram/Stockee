import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta
from app.core.config import settings
import requests
import json

logger = logging.getLogger(__name__)

class EnhancedAIService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_api_key = settings.openai_api_key

    def get_enhanced_predictions(self, symbol: str, days_ahead: int = 7) -> Dict:
        """Get enhanced AI predictions using multiple models"""
        try:
            # Get historical data
            historical_data = self._get_historical_data(symbol, 365)  # 1 year of data
            
            if not historical_data:
                return {"error": "Insufficient historical data"}
            
            # Get current market data
            current_data = self._get_current_market_data(symbol)
            
            # Get social sentiment
            from app.services.social_sentiment_service import SocialSentimentService
            sentiment_service = SocialSentimentService()
            social_sentiment = sentiment_service.get_combined_sentiment(symbol)
            
            # Get technical indicators
            technical_indicators = self._calculate_technical_indicators(historical_data)
            
            # Generate predictions using multiple models
            predictions = {
                "lstm_prediction": self._lstm_prediction(historical_data, days_ahead),
                "transformer_prediction": self._transformer_prediction(historical_data, days_ahead),
                "ensemble_prediction": self._ensemble_prediction(historical_data, days_ahead),
                "sentiment_adjusted_prediction": self._sentiment_adjusted_prediction(
                    historical_data, social_sentiment, days_ahead
                )
            }
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(predictions, historical_data)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(
                symbol, predictions, technical_indicators, social_sentiment, current_data
            )
            
            return {
                "symbol": symbol,
                "predictions": predictions,
                "confidence_scores": confidence_scores,
                "technical_indicators": technical_indicators,
                "social_sentiment": social_sentiment,
                "ai_insights": ai_insights,
                "current_price": current_data.get("current_price", 0),
                "prediction_horizon": days_ahead,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced predictions for {symbol}: {e}")
            return {"error": f"Failed to get predictions: {str(e)}"}

    def _get_historical_data(self, symbol: str, days: int) -> List[Dict]:
        """Get historical price data"""
        try:
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return []
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            prices = self.db.query(models.Price).filter(
                models.Price.asset_id == asset.id,
                models.Price.timestamp >= start_date,
                models.Price.timestamp <= end_date
            ).order_by(models.Price.timestamp).all()
            
            return [
                {
                    'date': price.timestamp,
                    'open': float(price.open_price),
                    'high': float(price.high_price),
                    'low': float(price.low_price),
                    'close': float(price.close_price),
                    'volume': int(price.volume) if price.volume else 0
                }
                for price in prices
            ]
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []

    def _get_current_market_data(self, symbol: str) -> Dict:
        """Get current market data"""
        try:
            asset = self.db.query(models.Asset).filter(models.Asset.symbol == symbol).first()
            if not asset:
                return {}
            
            latest_price = self.db.query(models.Price).filter(
                models.Price.asset_id == asset.id
            ).order_by(models.Price.timestamp.desc()).first()
            
            if latest_price:
                return {
                    "current_price": float(latest_price.close_price),
                    "volume": int(latest_price.volume) if latest_price.volume else 0,
                    "timestamp": latest_price.timestamp.isoformat()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting current market data: {e}")
            return {}

    def _calculate_technical_indicators(self, data: List[Dict]) -> Dict:
        """Calculate technical indicators"""
        try:
            if len(data) < 20:
                return {}
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            close = df['close']
            high = df['high']
            low = df['low']
            volume = df['volume']
            
            # Moving averages
            sma_20 = close.rolling(window=20).mean().iloc[-1]
            sma_50 = close.rolling(window=50).mean().iloc[-1]
            ema_12 = close.ewm(span=12).mean().iloc[-1]
            ema_26 = close.ewm(span=26).mean().iloc[-1]
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            histogram = macd_line - signal_line
            
            # Bollinger Bands
            sma_20_bb = close.rolling(window=20).mean()
            std_20 = close.rolling(window=20).std()
            bb_upper = (sma_20_bb + (std_20 * 2)).iloc[-1]
            bb_lower = (sma_20_bb - (std_20 * 2)).iloc[-1]
            
            # Volume indicators
            volume_sma = volume.rolling(window=20).mean().iloc[-1]
            volume_ratio = volume.iloc[-1] / volume_sma if volume_sma > 0 else 1
            
            return {
                "sma_20": float(sma_20),
                "sma_50": float(sma_50),
                "ema_12": float(ema_12),
                "ema_26": float(ema_26),
                "rsi": float(rsi),
                "macd": float(macd_line.iloc[-1]),
                "macd_signal": float(signal_line.iloc[-1]),
                "macd_histogram": float(histogram.iloc[-1]),
                "bb_upper": float(bb_upper),
                "bb_lower": float(bb_lower),
                "bb_middle": float(sma_20_bb.iloc[-1]),
                "volume_ratio": float(volume_ratio),
                "current_price": float(close.iloc[-1])
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {}

    def _lstm_prediction(self, data: List[Dict], days_ahead: int) -> Dict:
        """LSTM-based prediction (simplified)"""
        try:
            if len(data) < 30:
                return {"error": "Insufficient data for LSTM prediction"}
            
            df = pd.DataFrame(data)
            df = df.sort_values('date')
            
            # Simple LSTM simulation using moving averages and trend
            close_prices = df['close'].values
            
            # Calculate trend
            recent_trend = np.mean(close_prices[-5:]) - np.mean(close_prices[-20:-5])
            trend_strength = recent_trend / np.mean(close_prices[-20:])
            
            # Generate predictions
            current_price = close_prices[-1]
            predictions = []
            
            for i in range(1, days_ahead + 1):
                # Simple trend-based prediction with some randomness
                daily_change = trend_strength * 0.01 + np.random.normal(0, 0.02)
                predicted_price = current_price * (1 + daily_change * i)
                predictions.append({
                    "day": i,
                    "predicted_price": round(predicted_price, 2),
                    "confidence": max(0.3, 0.8 - (i * 0.1))
                })
            
            return {
                "model": "LSTM",
                "predictions": predictions,
                "trend_strength": round(trend_strength, 4),
                "model_confidence": 0.75
            }
            
        except Exception as e:
            logger.error(f"Error in LSTM prediction: {e}")
            return {"error": "LSTM prediction failed"}

    def _transformer_prediction(self, data: List[Dict], days_ahead: int) -> Dict:
        """Transformer-based prediction (simplified)"""
        try:
            if len(data) < 30:
                return {"error": "Insufficient data for Transformer prediction"}
            
            df = pd.DataFrame(data)
            df = df.sort_values('date')
            
            # Simple Transformer simulation using attention-like mechanism
            close_prices = df['close'].values
            volumes = df['volume'].values
            
            # Calculate attention weights (simplified)
            recent_prices = close_prices[-10:]
            recent_volumes = volumes[-10:]
            
            # Weight recent data more heavily
            weights = np.exp(np.linspace(-2, 0, 10))
            weighted_price = np.average(recent_prices, weights=weights)
            weighted_volume = np.average(recent_volumes, weights=weights)
            
            # Generate predictions
            current_price = close_prices[-1]
            predictions = []
            
            for i in range(1, days_ahead + 1):
                # Volume-adjusted prediction
                volume_factor = weighted_volume / np.mean(volumes[-20:]) if len(volumes) >= 20 else 1
                daily_change = (weighted_price - current_price) / current_price * 0.1 * volume_factor
                predicted_price = current_price * (1 + daily_change * i)
                predictions.append({
                    "day": i,
                    "predicted_price": round(predicted_price, 2),
                    "confidence": max(0.4, 0.85 - (i * 0.08))
                })
            
            return {
                "model": "Transformer",
                "predictions": predictions,
                "attention_weights": weights.tolist(),
                "model_confidence": 0.80
            }
            
        except Exception as e:
            logger.error(f"Error in Transformer prediction: {e}")
            return {"error": "Transformer prediction failed"}

    def _ensemble_prediction(self, data: List[Dict], days_ahead: int) -> Dict:
        """Ensemble prediction combining multiple models"""
        try:
            # Get individual model predictions
            lstm_pred = self._lstm_prediction(data, days_ahead)
            transformer_pred = self._transformer_prediction(data, days_ahead)
            
            if "error" in lstm_pred or "error" in transformer_pred:
                return {"error": "Ensemble prediction failed due to model errors"}
            
            # Combine predictions with weights
            lstm_weight = 0.4
            transformer_weight = 0.6
            
            predictions = []
            for i in range(days_ahead):
                lstm_price = lstm_pred["predictions"][i]["predicted_price"]
                transformer_price = transformer_pred["predictions"][i]["predicted_price"]
                
                ensemble_price = (lstm_price * lstm_weight) + (transformer_price * transformer_weight)
                ensemble_confidence = (lstm_pred["predictions"][i]["confidence"] * lstm_weight) + \
                                    (transformer_pred["predictions"][i]["confidence"] * transformer_weight)
                
                predictions.append({
                    "day": i + 1,
                    "predicted_price": round(ensemble_price, 2),
                    "confidence": round(ensemble_confidence, 3)
                })
            
            return {
                "model": "Ensemble",
                "predictions": predictions,
                "model_confidence": 0.85,
                "component_models": ["LSTM", "Transformer"]
            }
            
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return {"error": "Ensemble prediction failed"}

    def _sentiment_adjusted_prediction(self, data: List[Dict], sentiment: Dict, days_ahead: int) -> Dict:
        """Sentiment-adjusted prediction"""
        try:
            # Get base prediction
            base_pred = self._ensemble_prediction(data, days_ahead)
            
            if "error" in base_pred:
                return base_pred
            
            # Adjust based on sentiment
            sentiment_score = sentiment.get("combined_score", 0.5)
            sentiment_impact = (sentiment_score - 0.5) * 0.1  # -5% to +5% impact
            
            predictions = []
            for pred in base_pred["predictions"]:
                adjusted_price = pred["predicted_price"] * (1 + sentiment_impact)
                adjusted_confidence = pred["confidence"] * (0.8 + sentiment_score * 0.4)
                
                predictions.append({
                    "day": pred["day"],
                    "predicted_price": round(adjusted_price, 2),
                    "confidence": round(adjusted_confidence, 3),
                    "sentiment_adjustment": round(sentiment_impact * 100, 2)
                })
            
            return {
                "model": "Sentiment-Adjusted",
                "predictions": predictions,
                "model_confidence": 0.90,
                "sentiment_score": sentiment_score,
                "sentiment_impact": round(sentiment_impact * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment-adjusted prediction: {e}")
            return {"error": "Sentiment-adjusted prediction failed"}

    def _calculate_confidence_scores(self, predictions: Dict, historical_data: List[Dict]) -> Dict:
        """Calculate confidence scores for predictions"""
        try:
            confidence_scores = {}
            
            for model_name, prediction in predictions.items():
                if "error" in prediction:
                    confidence_scores[model_name] = 0.0
                    continue
                
                # Calculate confidence based on historical accuracy (simplified)
                model_confidence = prediction.get("model_confidence", 0.5)
                
                # Adjust based on data quality
                data_quality = min(1.0, len(historical_data) / 100)  # More data = higher confidence
                
                # Adjust based on volatility
                if len(historical_data) >= 20:
                    recent_prices = [d["close"] for d in historical_data[-20:]]
                    volatility = np.std(recent_prices) / np.mean(recent_prices)
                    volatility_factor = max(0.5, 1.0 - volatility)
                else:
                    volatility_factor = 0.5
                
                final_confidence = model_confidence * data_quality * volatility_factor
                confidence_scores[model_name] = round(final_confidence, 3)
            
            return confidence_scores
            
        except Exception as e:
            logger.error(f"Error calculating confidence scores: {e}")
            return {}

    def _generate_ai_insights(self, symbol: str, predictions: Dict, technical_indicators: Dict, 
                            sentiment: Dict, current_data: Dict) -> List[str]:
        """Generate AI insights using OpenAI"""
        try:
            if not self.openai_api_key:
                return self._generate_mock_insights(symbol, predictions, technical_indicators, sentiment)
            
            # Prepare context for AI
            context = {
                "symbol": symbol,
                "current_price": current_data.get("current_price", 0),
                "technical_indicators": technical_indicators,
                "sentiment": sentiment,
                "predictions": predictions
            }
            
            # Create prompt for AI
            prompt = f"""
            Analyze the following stock data for {symbol} and provide 3-5 key insights:
            
            Current Price: ${context['current_price']}
            Technical Indicators: {json.dumps(technical_indicators, indent=2)}
            Social Sentiment: {json.dumps(sentiment, indent=2)}
            AI Predictions: {json.dumps(predictions, indent=2)}
            
            Provide actionable insights about:
            1. Price direction and momentum
            2. Technical analysis signals
            3. Social sentiment impact
            4. Risk factors
            5. Trading recommendations
            
            Keep insights concise and actionable.
            """
            
            # Call OpenAI API
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a financial analyst providing stock market insights."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                insights_text = result["choices"][0]["message"]["content"]
                insights = [insight.strip() for insight in insights_text.split('\n') if insight.strip()]
                return insights[:5]  # Return top 5 insights
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return self._generate_mock_insights(symbol, predictions, technical_indicators, sentiment)
                
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return self._generate_mock_insights(symbol, predictions, technical_indicators, sentiment)

    def _generate_mock_insights(self, symbol: str, predictions: Dict, technical_indicators: Dict, sentiment: Dict) -> List[str]:
        """Generate mock AI insights"""
        insights = []
        
        # Price direction insight
        if "sentiment_adjusted_prediction" in predictions and "predictions" in predictions["sentiment_adjusted_prediction"]:
            preds = predictions["sentiment_adjusted_prediction"]["predictions"]
            if preds:
                current_price = technical_indicators.get("current_price", 0)
                predicted_price = preds[0]["predicted_price"]
                change_percent = ((predicted_price - current_price) / current_price) * 100
                
                if change_percent > 2:
                    insights.append(f"Strong bullish momentum expected with {change_percent:.1f}% upside potential")
                elif change_percent < -2:
                    insights.append(f"Bearish pressure anticipated with {abs(change_percent):.1f}% downside risk")
                else:
                    insights.append("Price expected to remain relatively stable in the near term")
        
        # Technical analysis insight
        rsi = technical_indicators.get("rsi", 50)
        if rsi > 70:
            insights.append("RSI indicates overbought conditions, potential for pullback")
        elif rsi < 30:
            insights.append("RSI shows oversold conditions, potential buying opportunity")
        else:
            insights.append("RSI in neutral territory, no extreme conditions detected")
        
        # Sentiment insight
        sentiment_score = sentiment.get("combined_score", 0.5)
        if sentiment_score > 0.7:
            insights.append("Strong positive social sentiment supporting bullish outlook")
        elif sentiment_score < 0.3:
            insights.append("Negative social sentiment creating headwinds for the stock")
        else:
            insights.append("Mixed social sentiment with no clear directional bias")
        
        # Volume insight
        volume_ratio = technical_indicators.get("volume_ratio", 1)
        if volume_ratio > 1.5:
            insights.append("Above-average volume indicates strong institutional interest")
        elif volume_ratio < 0.5:
            insights.append("Below-average volume suggests lack of conviction")
        
        # Risk insight
        insights.append("Monitor key support/resistance levels for potential breakout or breakdown")
        
        return insights[:5]

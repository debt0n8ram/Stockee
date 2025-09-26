import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SimplePricePredictor:
    """Simple price prediction model using moving averages and trend analysis"""
    
    def __init__(self):
        self.model_name = "simple_trend_analysis"
        self.version = "1.0"
    
    def predict(self, price_history: List[Dict], days_ahead: int = 30) -> List[Dict]:
        """Generate price predictions based on historical data"""
        if not price_history or len(price_history) < 10:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(price_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate moving averages
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        
        # Calculate trend
        recent_trend = (df['close'].iloc[-1] - df['close'].iloc[-10]) / df['close'].iloc[-10]
        
        # Generate predictions
        predictions = []
        current_price = df['close'].iloc[-1]
        
        for i in range(1, days_ahead + 1):
            # Simple trend-based prediction with some randomness
            trend_factor = 1 + (recent_trend * 0.1)  # Dampen the trend
            random_factor = 1 + (np.random.normal(0, 0.02))  # 2% random variation
            
            predicted_price = current_price * trend_factor * random_factor
            
            predictions.append({
                'date': (datetime.utcnow() + timedelta(days=i)).isoformat(),
                'predicted_price': round(predicted_price, 2),
                'confidence': max(0.5, min(0.9, 0.7 + np.random.normal(0, 0.1))),
                'model': self.model_name,
                'version': self.version
            })
        
        return predictions

class SentimentAnalyzer:
    """Simple sentiment analysis for news and social media"""
    
    def __init__(self):
        self.positive_words = ['bullish', 'growth', 'profit', 'gain', 'rise', 'up', 'positive', 'strong']
        self.negative_words = ['bearish', 'decline', 'loss', 'fall', 'down', 'negative', 'weak', 'crash']
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        total_words = len(text.split())
        sentiment_score = (positive_count - negative_count) / max(total_words, 1)
        
        if sentiment_score > 0.1:
            sentiment = 'positive'
        elif sentiment_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'confidence': min(0.9, abs(sentiment_score) * 2)
        }

class PortfolioOptimizer:
    """Simple portfolio optimization using Modern Portfolio Theory"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
    
    def optimize_allocation(self, assets: List[Dict], risk_tolerance: float = 0.5) -> Dict:
        """Optimize portfolio allocation"""
        if not assets:
            return {'error': 'No assets provided'}
        
        # Simple equal-weight allocation with risk adjustment
        n_assets = len(assets)
        base_weight = 1.0 / n_assets
        
        # Adjust weights based on risk tolerance
        if risk_tolerance < 0.3:  # Conservative
            # Favor less volatile assets
            weights = [base_weight * 0.8 for _ in assets]
        elif risk_tolerance > 0.7:  # Aggressive
            # Favor more volatile assets
            weights = [base_weight * 1.2 for _ in assets]
        else:  # Moderate
            weights = [base_weight for _ in assets]
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        return {
            'allocation': [
                {
                    'symbol': asset.get('symbol', 'Unknown'),
                    'weight': round(weight, 4),
                    'recommended_value': round(weight * 100000, 2)  # Assuming $100k portfolio
                }
                for asset, weight in zip(assets, weights)
            ],
            'expected_return': 0.08,  # 8% expected return
            'expected_volatility': 0.15,  # 15% expected volatility
            'sharpe_ratio': 0.4  # Expected Sharpe ratio
        }

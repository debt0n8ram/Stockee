"""
News and Sentiment Service
Integrates World News API, Reddit API, and Hugging Face for sentiment analysis
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class NewsSentimentService:
    def __init__(self):
        self.world_news_api_key = settings.world_news_api_key
        self.reddit_api_key = settings.reddit_api_key
        self.huggingface_api_key = settings.huggingface_api_key
        
        self.world_news_base_url = settings.world_news_base_url
        self.reddit_base_url = settings.reddit_base_url
        self.huggingface_base_url = "https://api-inference.huggingface.co/models"

    async def get_comprehensive_news(
        self, 
        query: str = "stock market",
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get news from multiple sources with sentiment analysis"""
        all_news = []
        
        # Get World News API data
        try:
            world_news = await self._get_world_news(query, limit // 2)
            all_news.extend(world_news)
        except Exception as e:
            logger.warning(f"Failed to fetch World News: {e}")
        
        # Get Reddit data
        try:
            reddit_data = await self._get_reddit_sentiment(query, limit // 2)
            all_news.extend(reddit_data)
        except Exception as e:
            logger.warning(f"Failed to fetch Reddit data: {e}")
        
        # Analyze sentiment for all news
        for news_item in all_news:
            try:
                sentiment = await self._analyze_sentiment(news_item.get("title", "") + " " + news_item.get("summary", ""))
                news_item["sentiment"] = sentiment
            except Exception as e:
                logger.warning(f"Failed to analyze sentiment: {e}")
                news_item["sentiment"] = {"label": "neutral", "score": 0.5}
        
        # Sort by relevance and recency
        all_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        
        return {
            "news": all_news[:limit],
            "total_sources": 2,
            "timestamp": datetime.now().isoformat()
        }

    async def _get_world_news(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch news from World News API"""
        if not self.world_news_api_key:
            raise Exception("World News API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.world_news_base_url}/news",
                params={
                    "api-key": self.world_news_api_key,
                    "text": query,
                    "number": limit,
                    "language": "en"
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for article in data.get("news", []):
                    news_items.append({
                        "title": article.get("title"),
                        "summary": article.get("text"),
                        "url": article.get("url"),
                        "published_at": article.get("publish_date"),
                        "source": article.get("source"),
                        "source_api": "world_news",
                        "tags": [query]
                    })
                
                return news_items

    async def _get_reddit_sentiment(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch Reddit posts for sentiment analysis"""
        if not self.reddit_api_key:
            raise Exception("Reddit API key not configured")
        
        # This is a simplified implementation
        # Full Reddit API integration would require OAuth flow
        return []

    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using Hugging Face API"""
        if not self.huggingface_api_key:
            return {"label": "neutral", "score": 0.5}
        
        # Use a pre-trained sentiment analysis model
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.huggingface_base_url}/{model_name}",
                headers={
                    "Authorization": f"Bearer {self.huggingface_api_key}"
                },
                json={
                    "inputs": text[:512]  # Limit text length
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    return {
                        "label": result.get("label", "neutral"),
                        "score": result.get("score", 0.5)
                    }
        
        return {"label": "neutral", "score": 0.5}

    async def get_market_sentiment(self, symbols: List[str]) -> Dict[str, Any]:
        """Get overall market sentiment for given symbols"""
        sentiment_data = {}
        
        for symbol in symbols:
            try:
                # Get news for the symbol
                news_data = await self.get_comprehensive_news(f"{symbol} stock", 10)
                
                # Calculate overall sentiment
                sentiments = [item.get("sentiment", {}).get("score", 0.5) for item in news_data.get("news", [])]
                
                if sentiments:
                    avg_sentiment = sum(sentiments) / len(sentiments)
                    sentiment_data[symbol] = {
                        "sentiment_score": avg_sentiment,
                        "sentiment_label": "positive" if avg_sentiment > 0.6 else "negative" if avg_sentiment < 0.4 else "neutral",
                        "news_count": len(sentiments),
                        "confidence": min(len(sentiments) / 10, 1.0)  # Confidence based on news volume
                    }
            except Exception as e:
                logger.warning(f"Failed to get sentiment for {symbol}: {e}")
                sentiment_data[symbol] = {
                    "sentiment_score": 0.5,
                    "sentiment_label": "neutral",
                    "news_count": 0,
                    "confidence": 0.0
                }
        
        return {
            "market_sentiment": sentiment_data,
            "timestamp": datetime.now().isoformat()
        }

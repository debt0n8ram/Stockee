from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.news_service import NewsService
from typing import List

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/market")
async def get_market_news(limit: int = 10):
    """Get general market news"""
    news_service = NewsService()
    news = news_service.get_market_news(limit)
    return {"news": news, "count": len(news)}

@router.get("/stock/{symbol}")
async def get_stock_news(symbol: str, limit: int = 10):
    """Get news for a specific stock"""
    news_service = NewsService()
    news = news_service.get_stock_news(symbol.upper(), limit)
    return {"symbol": symbol.upper(), "news": news, "count": len(news)}

@router.get("/crypto")
async def get_crypto_news(limit: int = 10):
    """Get cryptocurrency news"""
    news_service = NewsService()
    news = news_service.get_crypto_news(limit)
    return {"news": news, "count": len(news)}

@router.get("/sentiment")
async def analyze_news_sentiment(text: str):
    """Analyze sentiment of news text"""
    news_service = NewsService()
    sentiment = news_service.get_news_sentiment(text)
    return {"text": text, "sentiment_analysis": sentiment}

@router.get("/search")
async def search_news(
    query: str,
    limit: int = 10,
    sort_by: str = "publishedAt"
):
    """Search for news articles"""
    news_service = NewsService()
    news = news_service.search_news(query, limit, sort_by)
    return {"query": query, "news": news, "count": len(news)}

@router.get("/filter")
async def filter_news(
    category: str = None,
    source: str = None,
    sentiment: str = None,
    limit: int = 10
):
    """Filter news by category, source, or sentiment"""
    news_service = NewsService()
    news = news_service.filter_news(category, source, sentiment, limit)
    return {"filters": {"category": category, "source": source, "sentiment": sentiment}, "news": news, "count": len(news)}

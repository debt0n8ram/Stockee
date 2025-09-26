from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.social_sentiment_service import SocialSentimentService
from typing import Optional

router = APIRouter(prefix="/api/social-sentiment", tags=["social-sentiment"])

@router.get("/reddit/{symbol}")
async def get_reddit_sentiment(
    symbol: str,
    limit: int = Query(100, description="Number of posts to analyze"),
    db: Session = Depends(get_db)
):
    """Get Reddit sentiment for a symbol"""
    sentiment_service = SocialSentimentService()
    sentiment = sentiment_service.get_reddit_sentiment(symbol.upper(), limit)
    
    return sentiment

@router.get("/twitter/{symbol}")
async def get_twitter_sentiment(
    symbol: str,
    limit: int = Query(100, description="Number of tweets to analyze"),
    db: Session = Depends(get_db)
):
    """Get Twitter sentiment for a symbol"""
    sentiment_service = SocialSentimentService()
    sentiment = sentiment_service.get_twitter_sentiment(symbol.upper(), limit)
    
    return sentiment

@router.get("/combined/{symbol}")
async def get_combined_sentiment(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get combined sentiment from Reddit and Twitter"""
    sentiment_service = SocialSentimentService()
    sentiment = sentiment_service.get_combined_sentiment(symbol.upper())
    
    return sentiment

@router.get("/trending")
async def get_trending_sentiment(
    limit: int = Query(10, description="Number of trending symbols"),
    db: Session = Depends(get_db)
):
    """Get trending symbols based on social sentiment"""
    sentiment_service = SocialSentimentService()
    
    # Mock trending data for now
    trending_symbols = [
        {"symbol": "AAPL", "sentiment": "bullish", "score": 0.75, "mentions": 1250},
        {"symbol": "TSLA", "sentiment": "bearish", "score": 0.35, "mentions": 980},
        {"symbol": "NVDA", "sentiment": "bullish", "score": 0.82, "mentions": 850},
        {"symbol": "MSFT", "sentiment": "neutral", "score": 0.52, "mentions": 720},
        {"symbol": "GOOGL", "sentiment": "bullish", "score": 0.68, "mentions": 650},
        {"symbol": "AMZN", "sentiment": "neutral", "score": 0.48, "mentions": 580},
        {"symbol": "META", "sentiment": "bullish", "score": 0.71, "mentions": 520},
        {"symbol": "NFLX", "sentiment": "bearish", "score": 0.42, "mentions": 480},
        {"symbol": "AMD", "sentiment": "bullish", "score": 0.76, "mentions": 450},
        {"symbol": "INTC", "sentiment": "neutral", "score": 0.55, "mentions": 420}
    ]
    
    return {
        "trending_symbols": trending_symbols[:limit],
        "timestamp": sentiment_service._get_mock_reddit_sentiment("", 0)["timestamp"]
    }

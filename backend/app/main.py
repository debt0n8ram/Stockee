from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from dotenv import load_dotenv

from app.api import auth, portfolio, trading, market_data, analytics, ai, bank, ai_predictions, technical_analysis, news, websocket, market_screener, watchlist, charting, portfolio_comparison, options, backtesting, social_sentiment, enhanced_ai, realtime_alerts, advanced_orders, advanced_analytics, ml_training, social_features, interactive_charts, websocket_realtime, cache_management, options_trading, crypto_trading, ai_opponent, background_ai
from app.db.database import engine, Base

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Stockee API",
    description="AI-Powered Stock & Crypto Trading Simulator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(market_data.router, prefix="/api/market", tags=["Market Data"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(bank.router, tags=["Bank"])
app.include_router(ai_predictions.router, tags=["AI Predictions"])
app.include_router(technical_analysis.router, tags=["Technical Analysis"])
app.include_router(news.router, tags=["News"])
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(market_screener.router, tags=["Market Screener"])
app.include_router(watchlist.router, tags=["Watchlist"])
app.include_router(charting.router, tags=["Charting"])
app.include_router(portfolio_comparison.router, tags=["Portfolio Comparison"])
app.include_router(options.router, tags=["Options"])
app.include_router(backtesting.router, tags=["Backtesting"])
app.include_router(options_trading.router, tags=["Options Trading"])
app.include_router(crypto_trading.router, tags=["Cryptocurrency Trading"])
app.include_router(social_sentiment.router, tags=["Social Sentiment"])
app.include_router(enhanced_ai.router, tags=["Enhanced AI"])
app.include_router(realtime_alerts.router, tags=["Real-time Alerts"])
app.include_router(advanced_orders.router, tags=["Advanced Orders"])
app.include_router(advanced_analytics.router, tags=["Advanced Analytics"])
app.include_router(ml_training.router, tags=["ML Training"])
app.include_router(social_features.router, tags=["Social Features"])
app.include_router(interactive_charts.router, tags=["Interactive Charts"])
app.include_router(websocket_realtime.router, tags=["WebSocket Real-time"])
app.include_router(cache_management.router, tags=["Cache Management"])
app.include_router(ai_opponent.router, prefix="/api/ai-opponent", tags=["AI Opponent"])
app.include_router(background_ai.router, prefix="/api/background-ai", tags=["Background AI"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Stockee API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stockee-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

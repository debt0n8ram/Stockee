from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from dotenv import load_dotenv

# Import only essential modules first
from app.api import auth, portfolio, trading, market_data, analytics, bank, ai_opponent, background_ai, news, crypto, options, ai_predictions, historical_data, economic_data
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

# Include essential routers only
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(market_data.router, prefix="/api/market", tags=["Market Data"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(bank.router, tags=["Bank"])
app.include_router(news.router, tags=["News"])
app.include_router(crypto.router, tags=["Crypto"])
app.include_router(options.router, tags=["Options"])
app.include_router(ai_predictions.router, tags=["AI Predictions"])
app.include_router(ai_opponent.router, prefix="/api/ai-opponent", tags=["AI Opponent"])
app.include_router(background_ai.router, prefix="/api/background-ai", tags=["Background AI"])
app.include_router(historical_data.router, tags=["Historical Data"])
app.include_router(economic_data.router, tags=["Economic Data"])

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Stockee API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

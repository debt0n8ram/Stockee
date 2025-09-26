from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.crypto_service import CryptoService
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/api/crypto", tags=["crypto"])

class SwapQuoteRequest(BaseModel):
    from_token: str
    to_token: str
    amount: float

# Initialize crypto service
crypto_service = CryptoService()

@router.get("/prices")
async def get_crypto_prices(
    symbols: str = Query(..., description="Comma-separated list of crypto symbols"),
    db: Session = Depends(get_db)
):
    """Get current crypto prices from multiple APIs with intelligent fallback"""
    symbol_list = [s.strip() for s in symbols.split(",")]
    return await crypto_service.get_crypto_prices(symbol_list)

@router.get("/trending")
async def get_trending_crypto():
    """Get trending cryptocurrencies from multiple APIs"""
    return await crypto_service.get_trending_crypto()

@router.get("/news")
async def get_crypto_news(
    limit: int = Query(10, description="Number of news articles to return")
):
    """Get crypto news from multiple sources"""
    return await crypto_service.get_crypto_news(limit)

@router.get("/market-overview")
async def get_market_overview():
    """Get comprehensive crypto market overview"""
    return await crypto_service.get_market_overview()

@router.get("/market-data/{symbol}")
async def get_crypto_market_data(
    symbol: str,
    days: int = Query(7, description="Number of days of historical data"),
    db: Session = Depends(get_db)
):
    """Get crypto market data and historical prices"""
    symbol = symbol.upper()
    
    # Mock historical data
    base_price = 45000.0 if symbol == "BTC" else 3200.0 if symbol == "ETH" else random.uniform(0.01, 1000.0)
    
    data = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i-1)
        price_change = random.uniform(-0.1, 0.1)  # ±10% daily change
        price = base_price * (1 + price_change * (i / days))
        
        high = price * random.uniform(1.0, 1.05)
        low = price * random.uniform(0.95, 1.0)
        volume = random.randint(1000000, 10000000)
        
        data.append({
            "timestamp": date.isoformat(),
            "price": round(price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "volume": volume
        })
    
    return {
        "symbol": symbol,
        "data": data,
        "current_price": data[-1]["price"] if data else base_price,
        "change_24h": round(random.uniform(-10.0, 10.0), 2),
        "volume_24h": random.randint(1000000, 1000000000)
    }

@router.get("/defi/protocols")
async def get_defi_protocols(db: Session = Depends(get_db)):
    """Get DeFi protocols and yield farming opportunities"""
    protocols = [
        {
            "name": "Uniswap V3",
            "type": "DEX",
            "tvl": 5000000000,
            "apy": 12.5,
            "risk": "Medium"
        },
        {
            "name": "Compound",
            "type": "Lending",
            "tvl": 3000000000,
            "apy": 8.2,
            "risk": "Low"
        },
        {
            "name": "Aave",
            "type": "Lending",
            "tvl": 4000000000,
            "apy": 9.1,
            "risk": "Low"
        },
        {
            "name": "Yearn Finance",
            "type": "Yield Farming",
            "tvl": 2000000000,
            "apy": 15.8,
            "risk": "High"
        }
    ]
    
    return {"protocols": protocols}

@router.post("/swap/quote")
async def get_swap_quote(
    request: SwapQuoteRequest,
    db: Session = Depends(get_db)
):
    """Get quote for token swap"""
    # Mock swap quote
    exchange_rate = random.uniform(0.8, 1.2)
    output_amount = request.amount * exchange_rate
    fee = request.amount * 0.003  # 0.3% fee
    
    return {
        "from_token": request.from_token.upper(),
        "to_token": request.to_token.upper(),
        "input_amount": request.amount,
        "output_amount": round(output_amount, 6),
        "exchange_rate": round(exchange_rate, 6),
        "fee": round(fee, 6),
        "slippage": 0.5,
        "price_impact": round(random.uniform(0.1, 2.0), 2),
        "gas_estimate": random.randint(100000, 500000),
        "protocols_used": ["Uniswap V3", "1inch"]
    }

@router.get("/portfolio/analytics/{user_id}")
async def get_crypto_portfolio_analytics(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get crypto portfolio analytics for a user"""
    # Mock crypto portfolio analytics
    analytics = {
        "total_value": 15000.0,
        "total_invested": 12000.0,
        "total_pnl": 3000.0,
        "total_pnl_percent": 25.0,
        "positions": [
            {
                "symbol": "BTC",
                "amount": 0.5,
                "current_value": 22500.0,
                "unrealized_pnl": 2500.0,
                "pnl_percent": 12.5
            },
            {
                "symbol": "ETH",
                "amount": 5.0,
                "current_value": 16000.0,
                "unrealized_pnl": 1000.0,
                "pnl_percent": 6.67
            }
        ],
        "allocation": {
            "BTC": 60.0,
            "ETH": 40.0
        },
        "performance_7d": 5.2,
        "performance_30d": 18.7,
        "performance_90d": 45.3,
        "risk_metrics": {
            "volatility": 0.25,  # 25% volatility
            "var_95": 0.05,     # 5% VaR at 95% confidence
            "max_drawdown": 0.15, # 15% max drawdown
            "risk_level": "Medium"
        }
    }
    
    return {"user_id": user_id, "analytics": analytics}

@router.get("/defi/positions/{user_id}")
async def get_defi_positions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get DeFi positions for a user"""
    # Mock DeFi positions
    positions = [
        {
            "protocol": "Uniswap V3",
            "pool": "ETH/USDC",
            "position_type": "Liquidity Provider",
            "amount": 2.5,
            "value": 8000.0,
            "apr": 12.5,
            "fees_earned": 150.0,
            "impermanent_loss": -50.0
        },
        {
            "protocol": "Aave",
            "pool": "USDC",
            "position_type": "Lending",
            "amount": 5000.0,
            "value": 5000.0,
            "apr": 8.2,
            "fees_earned": 75.0,
            "impermanent_loss": 0.0
        },
        {
            "protocol": "Compound",
            "pool": "ETH",
            "position_type": "Borrowing",
            "amount": 1.0,
            "value": 3200.0,
            "apr": -5.5,
            "fees_earned": -25.0,
            "impermanent_loss": 0.0
        }
    ]
    
    return {"user_id": user_id, "positions": positions}

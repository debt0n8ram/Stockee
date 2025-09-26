from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.database import get_db
from app.services.interactive_charts_service import InteractiveChartsService
from app.api.auth import get_current_user

router = APIRouter()

class OrderPlacementRequest(BaseModel):
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: int
    order_type: str  # 'market', 'limit', 'stop', 'stop_limit'
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "day"

@router.get("/chart-data")
async def get_chart_data(
    symbol: str = Query(..., description="Stock symbol"),
    timeframe: str = Query("1d", description="Chart timeframe"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    indicators: Optional[str] = Query(None, description="Comma-separated list of indicators"),
    db: Session = Depends(get_db)
):
    """Get comprehensive chart data with OHLCV and technical indicators."""
    try:
        service = InteractiveChartsService(db)
        
        # Parse indicators
        indicators_list = None
        if indicators:
            indicators_list = [indicator.strip() for indicator in indicators.split(",")]
        
        result = service.get_chart_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            indicators=indicators_list
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/order-placement-data")
async def get_order_placement_data(
    symbol: str = Query(..., description="Stock symbol"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data needed for order placement on charts."""
    try:
        service = InteractiveChartsService(db)
        result = service.get_order_placement_data(symbol=symbol, user_id=current_user)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/place-order")
async def place_order_from_chart(
    request: OrderPlacementRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Place an order directly from the chart interface."""
    try:
        service = InteractiveChartsService(db)
        
        order_data = {
            "symbol": request.symbol,
            "side": request.side,
            "quantity": request.quantity,
            "order_type": request.order_type,
            "price": request.price,
            "stop_price": request.stop_price,
            "time_in_force": request.time_in_force
        }
        
        result = service.place_order_from_chart(user_id=current_user, order_data=order_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart-patterns")
async def get_chart_patterns(
    symbol: str = Query(..., description="Stock symbol"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Detect chart patterns in price data."""
    try:
        service = InteractiveChartsService(db)
        result = service.get_chart_patterns(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/volume-profile")
async def get_volume_profile(
    symbol: str = Query(..., description="Stock symbol"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Calculate volume profile for price levels."""
    try:
        service = InteractiveChartsService(db)
        result = service.get_volume_profile(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-depth")
async def get_market_depth(
    symbol: str = Query(..., description="Stock symbol"),
    db: Session = Depends(get_db)
):
    """Get market depth (order book) data."""
    try:
        service = InteractiveChartsService(db)
        result = service.get_market_depth(symbol=symbol)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart-statistics")
async def get_chart_statistics(
    symbol: str = Query(..., description="Stock symbol"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Get detailed chart statistics."""
    try:
        service = InteractiveChartsService(db)
        
        # Get chart data first
        chart_data = service.get_chart_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if "error" in chart_data:
            raise HTTPException(status_code=400, detail=chart_data["error"])
        
        # Return statistics
        return {
            "symbol": symbol,
            "statistics": chart_data.get("statistics", {}),
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/support-resistance")
async def get_support_resistance(
    symbol: str = Query(..., description="Stock symbol"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Get support and resistance levels."""
    try:
        service = InteractiveChartsService(db)
        
        # Get order placement data which includes support/resistance
        result = service.get_order_placement_data(symbol=symbol, user_id="system")
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "symbol": symbol,
            "support_resistance": result.get("support_resistance", {}),
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart-indicators/available")
async def get_available_indicators():
    """Get list of available technical indicators."""
    return {
        "indicators": [
            {
                "name": "rsi",
                "description": "Relative Strength Index",
                "type": "momentum",
                "parameters": ["period"]
            },
            {
                "name": "macd",
                "description": "Moving Average Convergence Divergence",
                "type": "trend",
                "parameters": ["fast_period", "slow_period", "signal_period"]
            },
            {
                "name": "sma",
                "description": "Simple Moving Average",
                "type": "trend",
                "parameters": ["period"]
            },
            {
                "name": "ema",
                "description": "Exponential Moving Average",
                "type": "trend",
                "parameters": ["period"]
            },
            {
                "name": "bollinger_bands",
                "description": "Bollinger Bands",
                "type": "volatility",
                "parameters": ["period", "std_dev"]
            },
            {
                "name": "stochastic",
                "description": "Stochastic Oscillator",
                "type": "momentum",
                "parameters": ["k_period", "d_period"]
            },
            {
                "name": "williams_r",
                "description": "Williams %R",
                "type": "momentum",
                "parameters": ["period"]
            },
            {
                "name": "cci",
                "description": "Commodity Channel Index",
                "type": "momentum",
                "parameters": ["period"]
            },
            {
                "name": "atr",
                "description": "Average True Range",
                "type": "volatility",
                "parameters": ["period"]
            },
            {
                "name": "volume",
                "description": "Volume",
                "type": "volume",
                "parameters": []
            }
        ]
    }

@router.get("/chart-timeframes/available")
async def get_available_timeframes():
    """Get list of available chart timeframes."""
    return {
        "timeframes": [
            {
                "name": "1m",
                "description": "1 Minute",
                "seconds": 60
            },
            {
                "name": "5m",
                "description": "5 Minutes",
                "seconds": 300
            },
            {
                "name": "15m",
                "description": "15 Minutes",
                "seconds": 900
            },
            {
                "name": "30m",
                "description": "30 Minutes",
                "seconds": 1800
            },
            {
                "name": "1h",
                "description": "1 Hour",
                "seconds": 3600
            },
            {
                "name": "4h",
                "description": "4 Hours",
                "seconds": 14400
            },
            {
                "name": "1d",
                "description": "1 Day",
                "seconds": 86400
            },
            {
                "name": "1w",
                "description": "1 Week",
                "seconds": 604800
            },
            {
                "name": "1M",
                "description": "1 Month",
                "seconds": 2592000
            }
        ]
    }

@router.get("/chart-types/available")
async def get_available_chart_types():
    """Get list of available chart types."""
    return {
        "chart_types": [
            {
                "name": "candlestick",
                "description": "Candlestick Chart",
                "features": ["ohlc", "volume", "indicators"]
            },
            {
                "name": "line",
                "description": "Line Chart",
                "features": ["close", "volume", "indicators"]
            },
            {
                "name": "bar",
                "description": "Bar Chart",
                "features": ["ohlc", "volume", "indicators"]
            },
            {
                "name": "area",
                "description": "Area Chart",
                "features": ["close", "volume", "indicators"]
            },
            {
                "name": "heikin_ashi",
                "description": "Heikin-Ashi Chart",
                "features": ["ohlc", "volume", "indicators"]
            },
            {
                "name": "renko",
                "description": "Renko Chart",
                "features": ["price", "volume"]
            },
            {
                "name": "point_figure",
                "description": "Point & Figure Chart",
                "features": ["price"]
            }
        ]
    }

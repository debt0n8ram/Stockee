from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db import models, schemas
from app.services.trading_service import TradingService
from app.services.market_data_service import MarketDataService

router = APIRouter()

@router.post("/buy", response_model=schemas.TradeResponse)
async def buy_stock(
    trade_request: schemas.TradeRequest,
    db: Session = Depends(get_db)
):
    """Place a buy order"""
    trading_service = TradingService(db)
    market_service = MarketDataService(db)
    
    # Get current price if market order
    if trade_request.order_type == "market":
        current_price_data = market_service.get_current_price(trade_request.symbol)
        if not current_price_data:
            raise HTTPException(status_code=400, detail=f"Could not get current price for {trade_request.symbol}")
        current_price = current_price_data['price']
    else:
        current_price = trade_request.limit_price
    
    if not current_price:
        raise HTTPException(status_code=400, detail="Price is required for limit orders")
    
    try:
        result = trading_service.execute_buy_order(
            user_id=trade_request.user_id,
            symbol=trade_request.symbol,
            quantity=trade_request.quantity,
            price=current_price,
            order_type=trade_request.order_type
        )
        return schemas.TradeResponse(
            success=True,
            message=f"Successfully bought {trade_request.quantity} shares of {trade_request.symbol}",
            transaction_id=result.get("transaction_id")
        )
    except Exception as e:
        return schemas.TradeResponse(
            success=False,
            message=str(e)
        )

@router.post("/sell", response_model=schemas.TradeResponse)
async def sell_stock(
    trade_request: schemas.TradeRequest,
    db: Session = Depends(get_db)
):
    """Place a sell order"""
    trading_service = TradingService(db)
    market_service = MarketDataService(db)
    
    # Get current price if market order
    if trade_request.order_type == "market":
        current_price_data = market_service.get_current_price(trade_request.symbol)
        if not current_price_data:
            raise HTTPException(status_code=400, detail=f"Could not get current price for {trade_request.symbol}")
        current_price = current_price_data['price']
    else:
        current_price = trade_request.limit_price
    
    if not current_price:
        raise HTTPException(status_code=400, detail="Price is required for limit orders")
    
    try:
        result = trading_service.execute_sell_order(
            user_id=trade_request.user_id,
            symbol=trade_request.symbol,
            quantity=trade_request.quantity,
            price=current_price,
            order_type=trade_request.order_type
        )
        return schemas.TradeResponse(
            success=True,
            message=f"Successfully sold {trade_request.quantity} shares of {trade_request.symbol}",
            transaction_id=result.get("transaction_id")
        )
    except Exception as e:
        return schemas.TradeResponse(
            success=False,
            message=str(e)
        )

@router.get("/orders/{user_id}")
async def get_open_orders(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get open orders for a user"""
    trading_service = TradingService(db)
    return trading_service.get_open_orders(user_id)

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Cancel an open order"""
    trading_service = TradingService(db)
    return trading_service.cancel_order(order_id)

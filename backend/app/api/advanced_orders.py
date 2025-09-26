from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.advanced_orders_service import AdvancedOrdersService
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/advanced-orders", tags=["advanced-orders"])

class StopLossOrderRequest(BaseModel):
    user_id: str
    symbol: str
    quantity: int
    stop_price: float
    order_type: str = "market"
    message: Optional[str] = ""

class TakeProfitOrderRequest(BaseModel):
    user_id: str
    symbol: str
    quantity: int
    limit_price: float
    order_type: str = "limit"
    message: Optional[str] = ""

class TrailingStopOrderRequest(BaseModel):
    user_id: str
    symbol: str
    quantity: int
    trail_amount: float
    trail_type: str = "percentage"  # "percentage" or "dollar"
    message: Optional[str] = ""

class BracketOrderRequest(BaseModel):
    user_id: str
    symbol: str
    quantity: int
    entry_price: float
    stop_loss_price: float
    take_profit_price: float
    message: Optional[str] = ""

class OCOOrderRequest(BaseModel):
    user_id: str
    symbol: str
    quantity: int
    stop_price: float
    limit_price: float
    message: Optional[str] = ""

class IcebergOrderRequest(BaseModel):
    user_id: str
    symbol: str
    total_quantity: int
    visible_quantity: int
    price: float
    order_type: str = "limit"
    message: Optional[str] = ""

class TWAPOrderRequest(BaseModel):
    user_id: str
    symbol: str
    quantity: int
    duration_minutes: int
    price_type: str = "market"  # "market" or "limit"
    limit_price: Optional[float] = None
    message: Optional[str] = ""

class VWAPOrderRequest(BaseModel):
    user_id: str
    symbol: str
    quantity: int
    duration_minutes: int
    price_type: str = "market"  # "market" or "limit"
    limit_price: Optional[float] = None
    message: Optional[str] = ""

@router.post("/stop-loss")
async def create_stop_loss_order(
    request: StopLossOrderRequest,
    db: Session = Depends(get_db)
):
    """Create a stop-loss order"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.create_stop_loss_order(
        request.user_id,
        request.symbol,
        request.quantity,
        request.stop_price,
        request.order_type,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/take-profit")
async def create_take_profit_order(
    request: TakeProfitOrderRequest,
    db: Session = Depends(get_db)
):
    """Create a take-profit order"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.create_take_profit_order(
        request.user_id,
        request.symbol,
        request.quantity,
        request.limit_price,
        request.order_type,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/trailing-stop")
async def create_trailing_stop_order(
    request: TrailingStopOrderRequest,
    db: Session = Depends(get_db)
):
    """Create a trailing stop order"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.create_trailing_stop_order(
        request.user_id,
        request.symbol,
        request.quantity,
        request.trail_amount,
        request.trail_type,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/bracket")
async def create_bracket_order(
    request: BracketOrderRequest,
    db: Session = Depends(get_db)
):
    """Create a bracket order (entry + stop-loss + take-profit)"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.create_bracket_order(
        request.user_id,
        request.symbol,
        request.quantity,
        request.entry_price,
        request.stop_loss_price,
        request.take_profit_price,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/{user_id}")
async def get_user_orders(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all advanced orders for a user"""
    orders_service = AdvancedOrdersService(db)
    orders = orders_service.get_user_orders(user_id)
    
    if "error" in orders:
        raise HTTPException(status_code=400, detail=orders["error"])
    
    return orders

@router.delete("/{user_id}/{order_id}")
async def cancel_order(
    user_id: str,
    order_id: int,
    db: Session = Depends(get_db)
):
    """Cancel an advanced order"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.cancel_order(user_id, order_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.put("/trailing-stop/{order_id}")
async def update_trailing_stop(
    order_id: int,
    new_stop_price: float = Query(..., description="New stop price"),
    db: Session = Depends(get_db)
):
    """Update trailing stop price"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.update_trailing_stop(order_id, new_stop_price)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/oco")
async def create_oco_order(
    request: OCOOrderRequest,
    db: Session = Depends(get_db)
):
    """Create an OCO (One-Cancels-Other) order"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.create_oco_order(
        request.user_id,
        request.symbol,
        request.quantity,
        request.stop_price,
        request.limit_price,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/iceberg")
async def create_iceberg_order(
    request: IcebergOrderRequest,
    db: Session = Depends(get_db)
):
    """Create an iceberg order"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.create_iceberg_order(
        request.user_id,
        request.symbol,
        request.total_quantity,
        request.visible_quantity,
        request.price,
        request.order_type,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/twap")
async def create_twap_order(
    request: TWAPOrderRequest,
    db: Session = Depends(get_db)
):
    """Create a TWAP (Time-Weighted Average Price) order"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.create_twap_order(
        request.user_id,
        request.symbol,
        request.quantity,
        request.duration_minutes,
        request.price_type,
        request.limit_price,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.post("/vwap")
async def create_vwap_order(
    request: VWAPOrderRequest,
    db: Session = Depends(get_db)
):
    """Create a VWAP (Volume-Weighted Average Price) order"""
    orders_service = AdvancedOrdersService(db)
    result = orders_service.create_vwap_order(
        request.user_id,
        request.symbol,
        request.quantity,
        request.duration_minutes,
        request.price_type,
        request.limit_price,
        request.message
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/types/available")
async def get_available_order_types():
    """Get available advanced order types"""
    orders_service = AdvancedOrdersService(None)
    return orders_service.get_order_types()

@router.get("/status/{order_id}")
async def get_order_status(
    order_id: int,
    db: Session = Depends(get_db)
):
    """Get status of a specific order"""
    try:
        from app.db import models
        
        order = db.query(models.AdvancedOrder).filter(
            models.AdvancedOrder.id == order_id
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "order_id": order.id,
            "symbol": order.symbol,
            "order_type": order.order_type,
            "side": order.side,
            "quantity": order.quantity,
            "stop_price": float(order.stop_price) if order.stop_price else None,
            "limit_price": float(order.limit_price) if order.limit_price else None,
            "trail_amount": float(order.trail_amount) if order.trail_amount else None,
            "trail_type": order.trail_type,
            "order_status": order.order_status,
            "message": order.message,
            "parent_order_id": order.parent_order_id,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting order status: {str(e)}")

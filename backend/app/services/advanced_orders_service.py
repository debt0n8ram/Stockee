import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta
from decimal import Decimal
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

class AdvancedOrdersService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)

    def create_stop_loss_order(self, user_id: str, symbol: str, quantity: int, stop_price: float, 
                              order_type: str = "market", message: str = "") -> Dict:
        """Create a stop-loss order"""
        try:
            # Get current price
            current_price = self.market_data_service.get_current_price(symbol)
            if not current_price:
                return {"error": "Unable to get current price"}
            
            current_price_value = current_price['price']
            
            # Validate stop price
            if stop_price >= current_price_value:
                return {"error": "Stop price must be below current price for stop-loss"}
            
            # Create order
            order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="stop_loss",
                side="sell",
                quantity=quantity,
                stop_price=stop_price,
                limit_price=None,
                order_status="pending",
                message=message,
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "order_type": order.order_type,
                "side": order.side,
                "quantity": order.quantity,
                "stop_price": float(order.stop_price),
                "current_price": current_price_value,
                "order_status": order.order_status,
                "message": order.message,
                "created_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating stop-loss order: {e}")
            return {"error": f"Failed to create stop-loss order: {str(e)}"}

    def create_take_profit_order(self, user_id: str, symbol: str, quantity: int, limit_price: float, 
                                order_type: str = "limit", message: str = "") -> Dict:
        """Create a take-profit order"""
        try:
            # Get current price
            current_price = self.market_data_service.get_current_price(symbol)
            if not current_price:
                return {"error": "Unable to get current price"}
            
            current_price_value = current_price['price']
            
            # Validate limit price
            if limit_price <= current_price_value:
                return {"error": "Limit price must be above current price for take-profit"}
            
            # Create order
            order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="take_profit",
                side="sell",
                quantity=quantity,
                stop_price=None,
                limit_price=limit_price,
                order_status="pending",
                message=message,
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "order_type": order.order_type,
                "side": order.side,
                "quantity": order.quantity,
                "limit_price": float(order.limit_price),
                "current_price": current_price_value,
                "order_status": order.order_status,
                "message": order.message,
                "created_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating take-profit order: {e}")
            return {"error": f"Failed to create take-profit order: {str(e)}"}

    def create_trailing_stop_order(self, user_id: str, symbol: str, quantity: int, trail_amount: float, 
                                  trail_type: str = "percentage", message: str = "") -> Dict:
        """Create a trailing stop order"""
        try:
            # Get current price
            current_price = self.market_data_service.get_current_price(symbol)
            if not current_price:
                return {"error": "Unable to get current price"}
            
            current_price_value = current_price['price']
            
            # Calculate initial stop price
            if trail_type == "percentage":
                stop_price = current_price_value * (1 - trail_amount / 100)
            else:  # dollar amount
                stop_price = current_price_value - trail_amount
            
            # Create order
            order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="trailing_stop",
                side="sell",
                quantity=quantity,
                stop_price=stop_price,
                limit_price=None,
                trail_amount=trail_amount,
                trail_type=trail_type,
                order_status="pending",
                message=message,
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "order_type": order.order_type,
                "side": order.side,
                "quantity": order.quantity,
                "stop_price": float(order.stop_price),
                "trail_amount": float(order.trail_amount),
                "trail_type": order.trail_type,
                "current_price": current_price_value,
                "order_status": order.order_status,
                "message": order.message,
                "created_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating trailing stop order: {e}")
            return {"error": f"Failed to create trailing stop order: {str(e)}"}

    def create_bracket_order(self, user_id: str, symbol: str, quantity: int, entry_price: float, 
                           stop_loss_price: float, take_profit_price: float, message: str = "") -> Dict:
        """Create a bracket order (entry + stop-loss + take-profit)"""
        try:
            # Validate prices
            if stop_loss_price >= entry_price:
                return {"error": "Stop-loss price must be below entry price"}
            if take_profit_price <= entry_price:
                return {"error": "Take-profit price must be above entry price"}
            
            # Create main entry order
            entry_order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="bracket_entry",
                side="buy",
                quantity=quantity,
                limit_price=entry_price,
                order_status="pending",
                message=message,
                created_at=datetime.now()
            )
            
            self.db.add(entry_order)
            self.db.commit()
            self.db.refresh(entry_order)
            
            # Create stop-loss order
            stop_loss_order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="bracket_stop_loss",
                side="sell",
                quantity=quantity,
                stop_price=stop_loss_price,
                parent_order_id=entry_order.id,
                order_status="pending",
                message=f"Stop-loss for bracket order {entry_order.id}",
                created_at=datetime.now()
            )
            
            self.db.add(stop_loss_order)
            
            # Create take-profit order
            take_profit_order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="bracket_take_profit",
                side="sell",
                quantity=quantity,
                limit_price=take_profit_price,
                parent_order_id=entry_order.id,
                order_status="pending",
                message=f"Take-profit for bracket order {entry_order.id}",
                created_at=datetime.now()
            )
            
            self.db.add(take_profit_order)
            self.db.commit()
            
            return {
                "bracket_order_id": entry_order.id,
                "symbol": entry_order.symbol,
                "quantity": entry_order.quantity,
                "entry_price": float(entry_order.limit_price),
                "stop_loss_price": float(stop_loss_order.stop_price),
                "take_profit_price": float(take_profit_order.limit_price),
                "orders": [
                    {
                        "id": entry_order.id,
                        "type": "entry",
                        "side": entry_order.side,
                        "price": float(entry_order.limit_price)
                    },
                    {
                        "id": stop_loss_order.id,
                        "type": "stop_loss",
                        "side": stop_loss_order.side,
                        "price": float(stop_loss_order.stop_price)
                    },
                    {
                        "id": take_profit_order.id,
                        "type": "take_profit",
                        "side": take_profit_order.side,
                        "price": float(take_profit_order.limit_price)
                    }
                ],
                "message": entry_order.message,
                "created_at": entry_order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating bracket order: {e}")
            return {"error": f"Failed to create bracket order: {str(e)}"}

    def get_user_orders(self, user_id: str) -> Dict:
        """Get all advanced orders for a user"""
        try:
            orders = self.db.query(models.AdvancedOrder).filter(
                models.AdvancedOrder.user_id == user_id
            ).order_by(models.AdvancedOrder.created_at.desc()).all()
            
            return {
                "orders": [
                    {
                        "id": order.id,
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
                    for order in orders
                ],
                "total_orders": len(orders)
            }
            
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return {"error": f"Failed to get orders: {str(e)}"}

    def cancel_order(self, user_id: str, order_id: int) -> Dict:
        """Cancel an advanced order"""
        try:
            order = self.db.query(models.AdvancedOrder).filter(
                models.AdvancedOrder.id == order_id,
                models.AdvancedOrder.user_id == user_id
            ).first()
            
            if not order:
                return {"error": "Order not found"}
            
            if order.order_status not in ["pending", "active"]:
                return {"error": "Order cannot be cancelled"}
            
            # Cancel the order
            order.order_status = "cancelled"
            order.updated_at = datetime.now()
            
            # If it's a bracket order, cancel related orders
            if order.order_type == "bracket_entry":
                related_orders = self.db.query(models.AdvancedOrder).filter(
                    models.AdvancedOrder.parent_order_id == order_id
                ).all()
                
                for related_order in related_orders:
                    related_order.order_status = "cancelled"
                    related_order.updated_at = datetime.now()
            
            self.db.commit()
            
            return {
                "message": "Order cancelled successfully",
                "order_id": order_id,
                "symbol": order.symbol,
                "order_type": order.order_type
            }
            
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return {"error": f"Failed to cancel order: {str(e)}"}

    def update_trailing_stop(self, order_id: int, new_stop_price: float) -> Dict:
        """Update trailing stop price"""
        try:
            order = self.db.query(models.AdvancedOrder).filter(
                models.AdvancedOrder.id == order_id,
                models.AdvancedOrder.order_type == "trailing_stop"
            ).first()
            
            if not order:
                return {"error": "Trailing stop order not found"}
            
            if order.order_status != "active":
                return {"error": "Order is not active"}
            
            # Update stop price
            old_stop_price = float(order.stop_price)
            order.stop_price = new_stop_price
            order.updated_at = datetime.now()
            
            self.db.commit()
            
            return {
                "message": "Trailing stop updated successfully",
                "order_id": order_id,
                "symbol": order.symbol,
                "old_stop_price": old_stop_price,
                "new_stop_price": new_stop_price
            }
            
        except Exception as e:
            logger.error(f"Error updating trailing stop: {e}")
            return {"error": f"Failed to update trailing stop: {str(e)}"}

    def create_oco_order(self, user_id: str, symbol: str, quantity: int, stop_price: float, 
                        limit_price: float, message: str = "") -> Dict:
        """Create an OCO (One-Cancels-Other) order"""
        try:
            # Get current price
            current_price = self.market_data_service.get_current_price(symbol)
            if not current_price:
                return {"error": "Unable to get current price"}
            
            current_price_value = current_price['price']
            
            # Validate prices
            if stop_price >= current_price_value:
                return {"error": "Stop price must be below current price"}
            if limit_price <= current_price_value:
                return {"error": "Limit price must be above current price"}
            
            # Create stop-loss order
            stop_order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="oco_stop",
                side="sell",
                quantity=quantity,
                stop_price=stop_price,
                order_status="pending",
                message=f"OCO Stop: {message}",
                created_at=datetime.now()
            )
            
            self.db.add(stop_order)
            self.db.commit()
            self.db.refresh(stop_order)
            
            # Create limit order
            limit_order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="oco_limit",
                side="sell",
                quantity=quantity,
                limit_price=limit_price,
                parent_order_id=stop_order.id,
                order_status="pending",
                message=f"OCO Limit: {message}",
                created_at=datetime.now()
            )
            
            self.db.add(limit_order)
            self.db.commit()
            self.db.refresh(limit_order)
            
            return {
                "oco_order_id": stop_order.id,
                "symbol": symbol.upper(),
                "quantity": quantity,
                "stop_price": stop_price,
                "limit_price": limit_price,
                "current_price": current_price_value,
                "orders": [
                    {
                        "id": stop_order.id,
                        "type": "stop",
                        "price": stop_price
                    },
                    {
                        "id": limit_order.id,
                        "type": "limit",
                        "price": limit_price
                    }
                ],
                "message": message,
                "created_at": stop_order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating OCO order: {e}")
            return {"error": f"Failed to create OCO order: {str(e)}"}

    def create_iceberg_order(self, user_id: str, symbol: str, total_quantity: int, 
                           visible_quantity: int, price: float, order_type: str = "limit", 
                           message: str = "") -> Dict:
        """Create an iceberg order"""
        try:
            if visible_quantity >= total_quantity:
                return {"error": "Visible quantity must be less than total quantity"}
            
            # Create iceberg order
            order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="iceberg",
                side="sell",
                quantity=total_quantity,
                limit_price=price if order_type == "limit" else None,
                order_status="pending",
                message=message,
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "total_quantity": total_quantity,
                "visible_quantity": visible_quantity,
                "price": price,
                "order_type": order_type,
                "order_status": order.order_status,
                "message": order.message,
                "created_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating iceberg order: {e}")
            return {"error": f"Failed to create iceberg order: {str(e)}"}

    def create_twap_order(self, user_id: str, symbol: str, quantity: int, 
                         duration_minutes: int, price_type: str = "market", 
                         limit_price: Optional[float] = None, message: str = "") -> Dict:
        """Create a TWAP order"""
        try:
            if duration_minutes <= 0:
                return {"error": "Duration must be positive"}
            
            # Create TWAP order
            order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="twap",
                side="sell",
                quantity=quantity,
                limit_price=limit_price if price_type == "limit" else None,
                order_status="pending",
                message=message,
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "quantity": quantity,
                "duration_minutes": duration_minutes,
                "price_type": price_type,
                "limit_price": limit_price,
                "order_status": order.order_status,
                "message": order.message,
                "created_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating TWAP order: {e}")
            return {"error": f"Failed to create TWAP order: {str(e)}"}

    def create_vwap_order(self, user_id: str, symbol: str, quantity: int, 
                         duration_minutes: int, price_type: str = "market", 
                         limit_price: Optional[float] = None, message: str = "") -> Dict:
        """Create a VWAP order"""
        try:
            if duration_minutes <= 0:
                return {"error": "Duration must be positive"}
            
            # Create VWAP order
            order = models.AdvancedOrder(
                user_id=user_id,
                symbol=symbol.upper(),
                order_type="vwap",
                side="sell",
                quantity=quantity,
                limit_price=limit_price if price_type == "limit" else None,
                order_status="pending",
                message=message,
                created_at=datetime.now()
            )
            
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "quantity": quantity,
                "duration_minutes": duration_minutes,
                "price_type": price_type,
                "limit_price": limit_price,
                "order_status": order.order_status,
                "message": order.message,
                "created_at": order.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating VWAP order: {e}")
            return {"error": f"Failed to create VWAP order: {str(e)}"}

    def get_order_types(self) -> Dict:
        """Get available advanced order types"""
        return {
            "order_types": [
                {
                    "type": "stop_loss",
                    "name": "Stop Loss",
                    "description": "Automatically sell when price drops to stop price",
                    "parameters": ["stop_price"],
                    "use_case": "Limit losses on long positions"
                },
                {
                    "type": "take_profit",
                    "name": "Take Profit",
                    "description": "Automatically sell when price reaches target",
                    "parameters": ["limit_price"],
                    "use_case": "Lock in profits on long positions"
                },
                {
                    "type": "trailing_stop",
                    "name": "Trailing Stop",
                    "description": "Stop price follows price up, locks in profits",
                    "parameters": ["trail_amount", "trail_type"],
                    "use_case": "Protect profits while allowing for upside"
                },
                {
                    "type": "bracket",
                    "name": "Bracket Order",
                    "description": "Entry order with automatic stop-loss and take-profit",
                    "parameters": ["entry_price", "stop_loss_price", "take_profit_price"],
                    "use_case": "Complete trading strategy in one order"
                },
                {
                    "type": "oco",
                    "name": "OCO Order",
                    "description": "One-Cancels-Other: Stop-loss OR limit order",
                    "parameters": ["stop_price", "limit_price"],
                    "use_case": "Execute either stop-loss or take-profit, not both"
                },
                {
                    "type": "iceberg",
                    "name": "Iceberg Order",
                    "description": "Large order split into smaller visible chunks",
                    "parameters": ["total_quantity", "visible_quantity", "price"],
                    "use_case": "Execute large orders without market impact"
                },
                {
                    "type": "twap",
                    "name": "TWAP Order",
                    "description": "Time-Weighted Average Price execution",
                    "parameters": ["quantity", "duration_minutes"],
                    "use_case": "Execute orders evenly over time"
                },
                {
                    "type": "vwap",
                    "name": "VWAP Order",
                    "description": "Volume-Weighted Average Price execution",
                    "parameters": ["quantity", "duration_minutes"],
                    "use_case": "Execute orders based on market volume"
                }
            ]
        }

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import models
from app.services.market_data_service import MarketDataService
from app.services.trading_service import TradingService
from app.services.websocket_service import WebSocketManager

logger = logging.getLogger(__name__)

class OrderExecutionEngine:
    """Real-time order execution engine for advanced orders"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.trading_service = TradingService(db)
        self.websocket_manager = WebSocketManager()
        self.running = False
        self.execution_tasks = {}
        
    async def start(self):
        """Start the order execution engine"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting order execution engine...")
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_stop_orders())
        asyncio.create_task(self._monitor_trailing_stops())
        asyncio.create_task(self._monitor_oco_orders())
        asyncio.create_task(self._monitor_iceberg_orders())
        asyncio.create_task(self._monitor_twap_orders())
        asyncio.create_task(self._monitor_vwap_orders())
        
        logger.info("Order execution engine started")
    
    async def stop(self):
        """Stop the order execution engine"""
        self.running = False
        logger.info("Order execution engine stopped")
    
    async def _monitor_stop_orders(self):
        """Monitor and execute stop-loss orders"""
        while self.running:
            try:
                # Get all pending stop-loss orders
                stop_orders = self.db.query(models.AdvancedOrder).filter(
                    models.AdvancedOrder.order_type == "stop_loss",
                    models.AdvancedOrder.order_status == "pending"
                ).all()
                
                for order in stop_orders:
                    await self._check_stop_order(order)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error monitoring stop orders: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_trailing_stops(self):
        """Monitor and update trailing stop orders"""
        while self.running:
            try:
                # Get all active trailing stop orders
                trailing_orders = self.db.query(models.AdvancedOrder).filter(
                    models.AdvancedOrder.order_type == "trailing_stop",
                    models.AdvancedOrder.order_status.in_(["pending", "active"])
                ).all()
                
                for order in trailing_orders:
                    await self._update_trailing_stop(order)
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring trailing stops: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_oco_orders(self):
        """Monitor OCO orders"""
        while self.running:
            try:
                # Get all pending OCO orders
                oco_orders = self.db.query(models.AdvancedOrder).filter(
                    models.AdvancedOrder.order_type.in_(["oco_stop", "oco_limit"]),
                    models.AdvancedOrder.order_status == "pending"
                ).all()
                
                for order in oco_orders:
                    await self._check_oco_order(order)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error monitoring OCO orders: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_iceberg_orders(self):
        """Monitor iceberg orders"""
        while self.running:
            try:
                # Get all pending iceberg orders
                iceberg_orders = self.db.query(models.AdvancedOrder).filter(
                    models.AdvancedOrder.order_type == "iceberg",
                    models.AdvancedOrder.order_status == "pending"
                ).all()
                
                for order in iceberg_orders:
                    await self._execute_iceberg_chunk(order)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring iceberg orders: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_twap_orders(self):
        """Monitor TWAP orders"""
        while self.running:
            try:
                # Get all pending TWAP orders
                twap_orders = self.db.query(models.AdvancedOrder).filter(
                    models.AdvancedOrder.order_type == "twap",
                    models.AdvancedOrder.order_status == "pending"
                ).all()
                
                for order in twap_orders:
                    await self._execute_twap_chunk(order)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring TWAP orders: {e}")
                await asyncio.sleep(15)
    
    async def _monitor_vwap_orders(self):
        """Monitor VWAP orders"""
        while self.running:
            try:
                # Get all pending VWAP orders
                vwap_orders = self.db.query(models.AdvancedOrder).filter(
                    models.AdvancedOrder.order_type == "vwap",
                    models.AdvancedOrder.order_status == "pending"
                ).all()
                
                for order in vwap_orders:
                    await self._execute_vwap_chunk(order)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring VWAP orders: {e}")
                await asyncio.sleep(15)
    
    async def _check_stop_order(self, order: models.AdvancedOrder):
        """Check if a stop-loss order should be executed"""
        try:
            current_price = self.market_data_service.get_current_price(order.symbol)
            if not current_price:
                return
            
            current_price_value = current_price['price']
            
            # Check if stop price has been hit
            if current_price_value <= order.stop_price:
                # Execute the order
                result = self.trading_service.execute_sell_order(
                    user_id=order.user_id,
                    symbol=order.symbol,
                    quantity=order.quantity,
                    price=current_price_value,
                    order_type="market"
                )
                
                if result.get("success"):
                    # Update order status
                    order.order_status = "filled"
                    order.updated_at = datetime.now()
                    self.db.commit()
                    
                    # Notify user via WebSocket
                    await self.websocket_manager.send_to_user(
                        order.user_id,
                        {
                            "type": "order_executed",
                            "order_id": order.id,
                            "symbol": order.symbol,
                            "quantity": order.quantity,
                            "price": current_price_value,
                            "order_type": "stop_loss"
                        }
                    )
                    
                    logger.info(f"Stop-loss order {order.id} executed at {current_price_value}")
                
        except Exception as e:
            logger.error(f"Error checking stop order {order.id}: {e}")
    
    async def _update_trailing_stop(self, order: models.AdvancedOrder):
        """Update trailing stop price based on current market price"""
        try:
            current_price = self.market_data_service.get_current_price(order.symbol)
            if not current_price:
                return
            
            current_price_value = current_price['price']
            current_stop_price = float(order.stop_price)
            
            # Calculate new stop price
            if order.trail_type == "percentage":
                new_stop_price = current_price_value * (1 - order.trail_amount / 100)
            else:  # dollar amount
                new_stop_price = current_price_value - order.trail_amount
            
            # Only update if new stop price is higher (for long positions)
            if new_stop_price > current_stop_price:
                order.stop_price = new_stop_price
                order.updated_at = datetime.now()
                self.db.commit()
                
                # Notify user
                await self.websocket_manager.send_to_user(
                    order.user_id,
                    {
                        "type": "trailing_stop_updated",
                        "order_id": order.id,
                        "symbol": order.symbol,
                        "new_stop_price": new_stop_price,
                        "current_price": current_price_value
                    }
                )
                
                logger.info(f"Trailing stop {order.id} updated to {new_stop_price}")
            
            # Check if stop price has been hit
            if current_price_value <= order.stop_price:
                # Execute the order
                result = self.trading_service.execute_sell_order(
                    user_id=order.user_id,
                    symbol=order.symbol,
                    quantity=order.quantity,
                    price=current_price_value,
                    order_type="market"
                )
                
                if result.get("success"):
                    order.order_status = "filled"
                    order.updated_at = datetime.now()
                    self.db.commit()
                    
                    await self.websocket_manager.send_to_user(
                        order.user_id,
                        {
                            "type": "order_executed",
                            "order_id": order.id,
                            "symbol": order.symbol,
                            "quantity": order.quantity,
                            "price": current_price_value,
                            "order_type": "trailing_stop"
                        }
                    )
                
        except Exception as e:
            logger.error(f"Error updating trailing stop {order.id}: {e}")
    
    async def _check_oco_order(self, order: models.AdvancedOrder):
        """Check if an OCO order should be executed"""
        try:
            current_price = self.market_data_service.get_current_price(order.symbol)
            if not current_price:
                return
            
            current_price_value = current_price['price']
            
            should_execute = False
            execution_price = current_price_value
            
            if order.order_type == "oco_stop":
                # Check stop price
                if current_price_value <= order.stop_price:
                    should_execute = True
            elif order.order_type == "oco_limit":
                # Check limit price
                if current_price_value >= order.limit_price:
                    should_execute = True
                    execution_price = order.limit_price
            
            if should_execute:
                # Execute this order
                result = self.trading_service.execute_sell_order(
                    user_id=order.user_id,
                    symbol=order.symbol,
                    quantity=order.quantity,
                    price=execution_price,
                    order_type="market"
                )
                
                if result.get("success"):
                    # Mark this order as filled
                    order.order_status = "filled"
                    order.updated_at = datetime.now()
                    
                    # Cancel the other OCO order
                    if order.parent_order_id:
                        other_order = self.db.query(models.AdvancedOrder).filter(
                            models.AdvancedOrder.id == order.parent_order_id
                        ).first()
                    else:
                        other_order = self.db.query(models.AdvancedOrder).filter(
                            models.AdvancedOrder.parent_order_id == order.id
                        ).first()
                    
                    if other_order:
                        other_order.order_status = "cancelled"
                        other_order.updated_at = datetime.now()
                    
                    self.db.commit()
                    
                    # Notify user
                    await self.websocket_manager.send_to_user(
                        order.user_id,
                        {
                            "type": "oco_order_executed",
                            "executed_order_id": order.id,
                            "cancelled_order_id": other_order.id if other_order else None,
                            "symbol": order.symbol,
                            "quantity": order.quantity,
                            "price": execution_price
                        }
                    )
                
        except Exception as e:
            logger.error(f"Error checking OCO order {order.id}: {e}")
    
    async def _execute_iceberg_chunk(self, order: models.AdvancedOrder):
        """Execute a chunk of an iceberg order"""
        try:
            # This is a simplified implementation
            # In a real system, you'd track executed quantity and remaining quantity
            
            current_price = self.market_data_service.get_current_price(order.symbol)
            if not current_price:
                return
            
            # For now, just execute the full order as a market order
            # In reality, you'd split this into smaller chunks over time
            result = self.trading_service.execute_sell_order(
                user_id=order.user_id,
                symbol=order.symbol,
                quantity=order.quantity,
                price=current_price['price'],
                order_type="market"
            )
            
            if result.get("success"):
                order.order_status = "filled"
                order.updated_at = datetime.now()
                self.db.commit()
                
                await self.websocket_manager.send_to_user(
                    order.user_id,
                    {
                        "type": "iceberg_order_executed",
                        "order_id": order.id,
                        "symbol": order.symbol,
                        "quantity": order.quantity,
                        "price": current_price['price']
                    }
                )
                
        except Exception as e:
            logger.error(f"Error executing iceberg chunk {order.id}: {e}")
    
    async def _execute_twap_chunk(self, order: models.AdvancedOrder):
        """Execute a chunk of a TWAP order"""
        try:
            # This is a simplified implementation
            # In a real system, you'd calculate the time intervals and execute accordingly
            
            current_price = self.market_data_service.get_current_price(order.symbol)
            if not current_price:
                return
            
            # For now, just execute the full order
            # In reality, you'd split this into time-based chunks
            result = self.trading_service.execute_sell_order(
                user_id=order.user_id,
                symbol=order.symbol,
                quantity=order.quantity,
                price=current_price['price'],
                order_type="market"
            )
            
            if result.get("success"):
                order.order_status = "filled"
                order.updated_at = datetime.now()
                self.db.commit()
                
                await self.websocket_manager.send_to_user(
                    order.user_id,
                    {
                        "type": "twap_order_executed",
                        "order_id": order.id,
                        "symbol": order.symbol,
                        "quantity": order.quantity,
                        "price": current_price['price']
                    }
                )
                
        except Exception as e:
            logger.error(f"Error executing TWAP chunk {order.id}: {e}")
    
    async def _execute_vwap_chunk(self, order: models.AdvancedOrder):
        """Execute a chunk of a VWAP order"""
        try:
            # This is a simplified implementation
            # In a real system, you'd calculate based on volume patterns
            
            current_price = self.market_data_service.get_current_price(order.symbol)
            if not current_price:
                return
            
            # For now, just execute the full order
            # In reality, you'd split this based on volume patterns
            result = self.trading_service.execute_sell_order(
                user_id=order.user_id,
                symbol=order.symbol,
                quantity=order.quantity,
                price=current_price['price'],
                order_type="market"
            )
            
            if result.get("success"):
                order.order_status = "filled"
                order.updated_at = datetime.now()
                self.db.commit()
                
                await self.websocket_manager.send_to_user(
                    order.user_id,
                    {
                        "type": "vwap_order_executed",
                        "order_id": order.id,
                        "symbol": order.symbol,
                        "quantity": order.quantity,
                        "price": current_price['price']
                    }
                )
                
        except Exception as e:
            logger.error(f"Error executing VWAP chunk {order.id}: {e}")
    
    async def execute_order_immediately(self, order_id: int) -> Dict:
        """Execute an order immediately (for testing or manual execution)"""
        try:
            order = self.db.query(models.AdvancedOrder).filter(
                models.AdvancedOrder.id == order_id
            ).first()
            
            if not order:
                return {"error": "Order not found"}
            
            if order.order_status != "pending":
                return {"error": "Order is not pending"}
            
            current_price = self.market_data_service.get_current_price(order.symbol)
            if not current_price:
                return {"error": "Unable to get current price"}
            
            # Execute the order
            if order.side == "buy":
                result = self.trading_service.execute_buy_order(
                    user_id=order.user_id,
                    symbol=order.symbol,
                    quantity=order.quantity,
                    price=current_price['price'],
                    order_type="market"
                )
            else:
                result = self.trading_service.execute_sell_order(
                    user_id=order.user_id,
                    symbol=order.symbol,
                    quantity=order.quantity,
                    price=current_price['price'],
                    order_type="market"
                )
            
            if result.get("success"):
                order.order_status = "filled"
                order.updated_at = datetime.now()
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "Order executed successfully",
                    "order_id": order_id,
                    "execution_price": current_price['price']
                }
            else:
                return {"error": "Failed to execute order"}
                
        except Exception as e:
            logger.error(f"Error executing order {order_id}: {e}")
            return {"error": f"Failed to execute order: {str(e)}"}

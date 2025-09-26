import logging
import asyncio
import json
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect
import redis
from collections import defaultdict

from app.db import models
from app.services.market_data_service import MarketDataService
from app.services.realtime_alerts_service import RealtimeAlertsService

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self, db: Session):
        self.db = db
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.symbol_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.market_data_service = MarketDataService(db)
        self.alerts_service = RealtimeAlertsService(db)
        
        # Redis for pub/sub
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        
        # Start background tasks
        asyncio.create_task(self._price_update_loop())
        asyncio.create_task(self._alert_processing_loop())
        asyncio.create_task(self._market_status_loop())
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected for user: {user_id}")
        
        # Send initial connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }, user_id)
    
    def disconnect(self, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            # Clean up subscriptions
            if user_id in self.user_subscriptions:
                del self.user_subscriptions[user_id]
            # Remove from symbol subscriptions
            for symbol, users in self.symbol_subscriptions.items():
                users.discard(user_id)
            logger.info(f"WebSocket disconnected for user: {user_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all connected users."""
        disconnected_users = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def broadcast_to_symbol_subscribers(self, symbol: str, message: Dict[str, Any]):
        """Broadcast a message to all users subscribed to a specific symbol."""
        if symbol in self.symbol_subscriptions:
            for user_id in self.symbol_subscriptions[symbol]:
                await self.send_personal_message(message, user_id)
    
    async def handle_message(self, user_id: str, message: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        try:
            message_type = message.get("type")
            
            if message_type == "subscribe_price":
                symbol = message.get("symbol")
                if symbol:
                    await self._subscribe_to_price_updates(user_id, symbol)
            
            elif message_type == "unsubscribe_price":
                symbol = message.get("symbol")
                if symbol:
                    await self._unsubscribe_from_price_updates(user_id, symbol)
            
            elif message_type == "subscribe_portfolio":
                await self._subscribe_to_portfolio_updates(user_id)
            
            elif message_type == "unsubscribe_portfolio":
                await self._unsubscribe_from_portfolio_updates(user_id)
            
            elif message_type == "subscribe_alerts":
                await self._subscribe_to_alerts(user_id)
            
            elif message_type == "unsubscribe_alerts":
                await self._unsubscribe_from_alerts(user_id)
            
            elif message_type == "subscribe_market_status":
                await self._subscribe_to_market_status(user_id)
            
            elif message_type == "unsubscribe_market_status":
                await self._unsubscribe_from_market_status(user_id)
            
            elif message_type == "ping":
                await self.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, user_id)
            
            else:
                await self.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, user_id)
                
        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {e}")
            await self.send_personal_message({
                "type": "error",
                "message": "Error processing message"
            }, user_id)
    
    async def _subscribe_to_price_updates(self, user_id: str, symbol: str):
        """Subscribe user to price updates for a symbol."""
        self.symbol_subscriptions[symbol].add(user_id)
        self.user_subscriptions[user_id].add(f"price:{symbol}")
        
        # Send current price immediately
        current_price_data = self.market_data_service.get_current_price(symbol)
        if current_price_data and isinstance(current_price_data, dict) and 'price' in current_price_data:
            await self.send_personal_message({
                "type": "price_update",
                "symbol": symbol,
                "price": float(current_price_data['price']),
                "timestamp": datetime.now().isoformat()
            }, user_id)
        
        logger.info(f"User {user_id} subscribed to price updates for {symbol}")
    
    async def _unsubscribe_from_price_updates(self, user_id: str, symbol: str):
        """Unsubscribe user from price updates for a symbol."""
        self.symbol_subscriptions[symbol].discard(user_id)
        self.user_subscriptions[user_id].discard(f"price:{symbol}")
        logger.info(f"User {user_id} unsubscribed from price updates for {symbol}")
    
    async def _subscribe_to_portfolio_updates(self, user_id: str):
        """Subscribe user to portfolio updates."""
        self.user_subscriptions[user_id].add("portfolio")
        logger.info(f"User {user_id} subscribed to portfolio updates")
    
    async def _unsubscribe_from_portfolio_updates(self, user_id: str):
        """Unsubscribe user from portfolio updates."""
        self.user_subscriptions[user_id].discard("portfolio")
        logger.info(f"User {user_id} unsubscribed from portfolio updates")
    
    async def _subscribe_to_alerts(self, user_id: str):
        """Subscribe user to alert notifications."""
        self.user_subscriptions[user_id].add("alerts")
        logger.info(f"User {user_id} subscribed to alerts")
    
    async def _unsubscribe_from_alerts(self, user_id: str):
        """Unsubscribe user from alert notifications."""
        self.user_subscriptions[user_id].discard("alerts")
        logger.info(f"User {user_id} unsubscribed from alerts")
    
    async def _subscribe_to_market_status(self, user_id: str):
        """Subscribe user to market status updates."""
        self.user_subscriptions[user_id].add("market_status")
        logger.info(f"User {user_id} subscribed to market status")
    
    async def _unsubscribe_from_market_status(self, user_id: str):
        """Unsubscribe user from market status updates."""
        self.user_subscriptions[user_id].discard("market_status")
        logger.info(f"User {user_id} unsubscribed from market status")
    
    async def _price_update_loop(self):
        """Background loop for price updates."""
        while True:
            try:
                # Get all subscribed symbols
                all_symbols = set(self.symbol_subscriptions.keys())
                
                if all_symbols:
                    # Fetch current prices for all symbols
                    price_updates = {}
                    for symbol in all_symbols:
                        current_price_data = self.market_data_service.get_current_price(symbol)
                        if current_price_data and isinstance(current_price_data, dict) and 'price' in current_price_data:
                            price_updates[symbol] = float(current_price_data['price'])
                    
                    # Send updates to subscribers
                    for symbol, price in price_updates.items():
                        await self.broadcast_to_symbol_subscribers(symbol, {
                            "type": "price_update",
                            "symbol": symbol,
                            "price": price,
                            "timestamp": datetime.now().isoformat()
                        })
                
                # Wait before next update
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _alert_processing_loop(self):
        """Background loop for processing alerts."""
        while True:
            try:
                # Check for triggered alerts
                triggered_alerts = await self.alerts_service.check_all_alerts()
                
                for alert in triggered_alerts:
                    user_id = alert.get("user_id")
                    if user_id and user_id in self.active_connections:
                        await self.send_personal_message({
                            "type": "alert_triggered",
                            "alert": alert,
                            "timestamp": datetime.now().isoformat()
                        }, user_id)
                
                # Wait before next check
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    async def _market_status_loop(self):
        """Background loop for market status updates."""
        while True:
            try:
                # Check market status
                market_status = self._get_market_status()
                
                # Send to all market status subscribers
                for user_id, subscriptions in self.user_subscriptions.items():
                    if "market_status" in subscriptions:
                        await self.send_personal_message({
                            "type": "market_status",
                            "status": market_status,
                            "timestamp": datetime.now().isoformat()
                        }, user_id)
                
                # Wait before next update
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in market status loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def _get_market_status(self) -> Dict[str, Any]:
        """Get current market status."""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        is_open = market_open <= now <= market_close and now.weekday() < 5
        
        return {
            "is_open": is_open,
            "market_open": market_open.isoformat(),
            "market_close": market_close.isoformat(),
            "current_time": now.isoformat(),
            "next_open": self._get_next_market_open().isoformat(),
            "next_close": self._get_next_market_close().isoformat()
        }
    
    def _get_next_market_open(self) -> datetime:
        """Get next market open time."""
        now = datetime.now()
        next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # If it's after market close or weekend, move to next weekday
        if now.hour >= 16 or now.weekday() >= 5:
            days_ahead = 1
            while (now + timedelta(days=days_ahead)).weekday() >= 5:
                days_ahead += 1
            next_open = (now + timedelta(days=days_ahead)).replace(hour=9, minute=30, second=0, microsecond=0)
        
        return next_open
    
    def _get_next_market_close(self) -> datetime:
        """Get next market close time."""
        now = datetime.now()
        next_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # If it's after market close or weekend, move to next weekday
        if now.hour >= 16 or now.weekday() >= 5:
            days_ahead = 1
            while (now + timedelta(days=days_ahead)).weekday() >= 5:
                days_ahead += 1
            next_close = (now + timedelta(days=days_ahead)).replace(hour=16, minute=0, second=0, microsecond=0)
        
        return next_close
    
    async def send_portfolio_update(self, user_id: str, portfolio_data: Dict[str, Any]):
        """Send portfolio update to a specific user."""
        if user_id in self.user_subscriptions and "portfolio" in self.user_subscriptions[user_id]:
            await self.send_personal_message({
                "type": "portfolio_update",
                "portfolio": portfolio_data,
                "timestamp": datetime.now().isoformat()
            }, user_id)
    
    async def send_trade_notification(self, user_id: str, trade_data: Dict[str, Any]):
        """Send trade notification to a specific user."""
        await self.send_personal_message({
            "type": "trade_notification",
            "trade": trade_data,
            "timestamp": datetime.now().isoformat()
        }, user_id)
    
    async def send_news_update(self, symbol: str, news_data: Dict[str, Any]):
        """Send news update to symbol subscribers."""
        await self.broadcast_to_symbol_subscribers(symbol, {
            "type": "news_update",
            "symbol": symbol,
            "news": news_data,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self.active_connections)
    
    def get_subscription_stats(self) -> Dict[str, Any]:
        """Get subscription statistics."""
        return {
            "total_connections": len(self.active_connections),
            "symbol_subscriptions": {symbol: len(users) for symbol, users in self.symbol_subscriptions.items()},
            "user_subscriptions": {user_id: list(subscriptions) for user_id, subscriptions in self.user_subscriptions.items()}
        }

# Global WebSocket manager instance
websocket_manager: Optional[WebSocketManager] = None

def get_websocket_manager(db: Session) -> WebSocketManager:
    """Get or create WebSocket manager instance."""
    global websocket_manager
    if websocket_manager is None:
        websocket_manager = WebSocketManager(db)
    return websocket_manager

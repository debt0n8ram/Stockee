import asyncio
import json
import logging
from typing import Dict, List, Set
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.db import models
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)

class RealtimeService:
    def __init__(self, db: Session):
        self.db = db
        self.active_connections: List[WebSocket] = []
        self.subscribed_symbols: Set[str] = set()
        self.market_data_service = MarketDataService(db)
        self.price_cache: Dict[str, Dict] = {}
        self.is_running = False

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def subscribe_to_symbol(self, websocket: WebSocket, symbol: str):
        """Subscribe to real-time updates for a symbol"""
        self.subscribed_symbols.add(symbol.upper())
        await self.send_personal_message({
            "type": "subscription_confirmed",
            "symbol": symbol.upper(),
            "message": f"Subscribed to {symbol.upper()}"
        }, websocket)

    async def unsubscribe_from_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe from real-time updates for a symbol"""
        self.subscribed_symbols.discard(symbol.upper())
        await self.send_personal_message({
            "type": "unsubscription_confirmed",
            "symbol": symbol.upper(),
            "message": f"Unsubscribed from {symbol.upper()}"
        }, websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected WebSocket clients"""
        if not self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)

        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def start_price_updates(self):
        """Start the real-time price update loop"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Starting real-time price updates")

        while self.is_running and self.active_connections:
            try:
                if self.subscribed_symbols:
                    await self.update_prices()
                
                # Wait 5 seconds before next update
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                await asyncio.sleep(5)

    async def stop_price_updates(self):
        """Stop the real-time price update loop"""
        self.is_running = False
        logger.info("Stopped real-time price updates")

    async def update_prices(self):
        """Update prices for all subscribed symbols"""
        for symbol in list(self.subscribed_symbols):
            try:
                # Get current price
                current_price = self.market_data_service.get_current_price(symbol)
                
                if current_price:
                    # Calculate change from previous price
                    previous_price = self.price_cache.get(symbol, {}).get('price')
                    change = 0
                    change_percent = 0
                    
                    if previous_price:
                        change = current_price['price'] - previous_price
                        change_percent = (change / previous_price) * 100

                    # Update cache
                    self.price_cache[symbol] = {
                        'price': current_price['price'],
                        'timestamp': datetime.now().isoformat(),
                        'change': change,
                        'change_percent': change_percent
                    }

                    # Broadcast update
                    await self.broadcast_to_all({
                        "type": "price_update",
                        "symbol": symbol,
                        "price": current_price['price'],
                        "change": change,
                        "change_percent": change_percent,
                        "timestamp": datetime.now().isoformat()
                    })

            except Exception as e:
                logger.error(f"Error updating price for {symbol}: {e}")

    async def get_market_status(self):
        """Get current market status"""
        now = datetime.now()
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        is_market_open = market_open <= now <= market_close and now.weekday() < 5
        
        return {
            "is_open": is_market_open,
            "current_time": now.isoformat(),
            "next_open": self._get_next_market_open().isoformat(),
            "next_close": self._get_next_market_close().isoformat()
        }

    def _get_next_market_open(self):
        """Get the next market open time"""
        now = datetime.now()
        next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # If it's after market close today, move to next weekday
        if now.hour >= 16 or now.weekday() >= 5:
            days_ahead = 1
            while (now + timedelta(days=days_ahead)).weekday() >= 5:
                days_ahead += 1
            next_open = (now + timedelta(days=days_ahead)).replace(hour=9, minute=30, second=0, microsecond=0)
        
        return next_open

    def _get_next_market_close(self):
        """Get the next market close time"""
        now = datetime.now()
        next_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # If it's before market open today, use today's close
        if now.hour < 9 or now.weekday() >= 5:
            days_ahead = 0
            while (now + timedelta(days=days_ahead)).weekday() >= 5:
                days_ahead += 1
            next_close = (now + timedelta(days=days_ahead)).replace(hour=16, minute=0, second=0, microsecond=0)
        
        return next_close

    async def handle_websocket_message(self, websocket: WebSocket, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                symbol = data.get("symbol")
                if symbol:
                    await self.subscribe_to_symbol(websocket, symbol)
            
            elif message_type == "unsubscribe":
                symbol = data.get("symbol")
                if symbol:
                    await self.unsubscribe_from_symbol(websocket, symbol)
            
            elif message_type == "get_market_status":
                status = await self.get_market_status()
                await self.send_personal_message({
                    "type": "market_status",
                    "data": status
                }, websocket)
            
            elif message_type == "get_subscribed_symbols":
                await self.send_personal_message({
                    "type": "subscribed_symbols",
                    "symbols": list(self.subscribed_symbols)
                }, websocket)
            
            else:
                await self.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, websocket)
                
        except json.JSONDecodeError:
            await self.send_personal_message({
                "type": "error",
                "message": "Invalid JSON format"
            }, websocket)
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send_personal_message({
                "type": "error",
                "message": "Internal server error"
            }, websocket)

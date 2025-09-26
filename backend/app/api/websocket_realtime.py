from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
import logging

from app.db.database import get_db
from app.services.websocket_service import get_websocket_manager
from app.api.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time data updates."""
    manager = get_websocket_manager(db)
    
    try:
        # Connect the WebSocket
        await manager.connect(websocket, user_id)
        
        # Listen for messages
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle the message
                await manager.handle_message(user_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user: {user_id}")
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, user_id)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Error processing message"
                }, user_id)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        # Clean up connection
        manager.disconnect(user_id)

@router.get("/ws/stats")
async def get_websocket_stats(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get WebSocket connection statistics."""
    try:
        manager = get_websocket_manager(db)
        stats = manager.get_subscription_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ws/broadcast")
async def broadcast_message(
    message: Dict[str, Any],
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Broadcast a message to all connected users (admin only)."""
    try:
        # In a real implementation, you would check if the user is an admin
        # For now, we'll allow any authenticated user to broadcast
        
        manager = get_websocket_manager(db)
        await manager.broadcast_to_all(message)
        
        return {
            "success": True,
            "message": "Message broadcasted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ws/symbol/{symbol}/broadcast")
async def broadcast_to_symbol_subscribers(
    symbol: str,
    message: Dict[str, Any],
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Broadcast a message to all users subscribed to a specific symbol."""
    try:
        manager = get_websocket_manager(db)
        await manager.broadcast_to_symbol_subscribers(symbol, message)
        
        return {
            "success": True,
            "message": f"Message broadcasted to {symbol} subscribers"
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting to symbol subscribers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ws/user/{target_user_id}/send")
async def send_message_to_user(
    target_user_id: str,
    message: Dict[str, Any],
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a specific user."""
    try:
        manager = get_websocket_manager(db)
        await manager.send_personal_message(message, target_user_id)
        
        return {
            "success": True,
            "message": f"Message sent to user {target_user_id}"
        }
        
    except Exception as e:
        logger.error(f"Error sending message to user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ws/connections")
async def get_active_connections(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of active WebSocket connections."""
    try:
        manager = get_websocket_manager(db)
        stats = manager.get_subscription_stats()
        
        return {
            "success": True,
            "active_connections": list(manager.active_connections.keys()),
            "connection_count": manager.get_connection_count(),
            "subscriptions": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting active connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ws/test")
async def test_websocket_connection(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test WebSocket connection by sending a test message."""
    try:
        manager = get_websocket_manager(db)
        
        # Send test message to current user
        await manager.send_personal_message({
            "type": "test_message",
            "message": "WebSocket connection is working!",
            "timestamp": "2024-01-01T00:00:00Z"
        }, current_user)
        
        return {
            "success": True,
            "message": "Test message sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Error sending test message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

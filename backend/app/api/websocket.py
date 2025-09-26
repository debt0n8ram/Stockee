from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.realtime_service import RealtimeService
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ws", tags=["websocket"])

# Global realtime service instance
realtime_service = None

def get_realtime_service(db: Session = Depends(get_db)) -> RealtimeService:
    """Get or create the global realtime service instance"""
    global realtime_service
    if realtime_service is None:
        realtime_service = RealtimeService(db)
    return realtime_service

@router.websocket("/prices")
async def websocket_prices(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time price updates"""
    service = get_realtime_service(db)
    
    await service.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            await service.handle_websocket_message(websocket, data)
            
    except WebSocketDisconnect:
        service.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        service.disconnect(websocket)

@router.websocket("/market-status")
async def websocket_market_status(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time market status updates"""
    service = get_realtime_service(db)
    
    await service.connect(websocket)
    
    try:
        # Send initial market status
        status = await service.get_market_status()
        await service.send_personal_message({
            "type": "market_status",
            "data": status
        }, websocket)
        
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(60)  # Update every minute
            status = await service.get_market_status()
            await service.send_personal_message({
                "type": "market_status",
                "data": status
            }, websocket)
            
    except WebSocketDisconnect:
        service.disconnect(websocket)
        logger.info("Market status WebSocket client disconnected")
    except Exception as e:
        logger.error(f"Market status WebSocket error: {e}")
        service.disconnect(websocket)

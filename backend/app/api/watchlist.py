from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.watchlist_service import WatchlistService
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

class AddToWatchlistRequest(BaseModel):
    user_id: str
    symbol: str
    alert_price: Optional[float] = None

class UpdateAlertRequest(BaseModel):
    user_id: str
    symbol: str
    alert_price: float

@router.post("/add")
async def add_to_watchlist(request: AddToWatchlistRequest, db: Session = Depends(get_db)):
    """Add a stock to user's watchlist"""
    watchlist_service = WatchlistService(db)
    result = watchlist_service.add_to_watchlist(
        request.user_id, 
        request.symbol, 
        request.alert_price
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.delete("/remove")
async def remove_from_watchlist(user_id: str, symbol: str, db: Session = Depends(get_db)):
    """Remove a stock from user's watchlist"""
    watchlist_service = WatchlistService(db)
    result = watchlist_service.remove_from_watchlist(user_id, symbol)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/{user_id}")
async def get_watchlist(user_id: str, db: Session = Depends(get_db)):
    """Get user's watchlist with current prices"""
    watchlist_service = WatchlistService(db)
    watchlist = watchlist_service.get_watchlist(user_id)
    return {"watchlist": watchlist, "count": len(watchlist)}

@router.put("/alert")
async def update_alert_price(request: UpdateAlertRequest, db: Session = Depends(get_db)):
    """Update alert price for a watchlist item"""
    watchlist_service = WatchlistService(db)
    result = watchlist_service.update_alert_price(
        request.user_id, 
        request.symbol, 
        request.alert_price
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/{user_id}/alerts")
async def get_alerts(user_id: str, db: Session = Depends(get_db)):
    """Get triggered alerts for user"""
    watchlist_service = WatchlistService(db)
    alerts = watchlist_service.get_alerts(user_id)
    return {"alerts": alerts, "count": len(alerts)}

@router.get("/{user_id}/performance")
async def get_watchlist_performance(user_id: str, db: Session = Depends(get_db)):
    """Get performance summary for user's watchlist"""
    watchlist_service = WatchlistService(db)
    performance = watchlist_service.get_watchlist_performance(user_id)
    
    if "error" in performance:
        raise HTTPException(status_code=404, detail=performance["error"])
    
    return performance

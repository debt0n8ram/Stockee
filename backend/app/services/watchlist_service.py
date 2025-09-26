import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.db import models
from app.services.market_data_service import MarketDataService
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WatchlistService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)

    def add_to_watchlist(self, user_id: str, symbol: str, alert_price: Optional[float] = None) -> Dict:
        """Add a stock to user's watchlist"""
        try:
            # Check if already in watchlist
            existing = self.db.query(models.Watchlist).filter(
                models.Watchlist.user_id == user_id,
                models.Watchlist.symbol == symbol.upper()
            ).first()
            
            if existing:
                return {"error": "Stock already in watchlist"}
            
            # Get or create asset
            asset = self.db.query(models.Asset).filter(
                models.Asset.symbol == symbol.upper()
            ).first()
            
            if not asset:
                # Create asset if it doesn't exist
                asset = models.Asset(
                    symbol=symbol.upper(),
                    name=symbol.upper(),
                    asset_type='stock',
                    exchange='NASDAQ',
                    currency='USD',
                    is_active=True
                )
                self.db.add(asset)
                self.db.commit()
                self.db.refresh(asset)
            
            # Add to watchlist
            watchlist_item = models.Watchlist(
                user_id=user_id,
                symbol=symbol.upper(),
                asset_id=asset.id,
                alert_price=alert_price,
                created_at=datetime.now()
            )
            
            self.db.add(watchlist_item)
            self.db.commit()
            self.db.refresh(watchlist_item)
            
            return {
                "message": f"Added {symbol.upper()} to watchlist",
                "watchlist_item": {
                    "id": watchlist_item.id,
                    "symbol": watchlist_item.symbol,
                    "alert_price": watchlist_item.alert_price,
                    "created_at": watchlist_item.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return {"error": f"Failed to add to watchlist: {str(e)}"}

    def remove_from_watchlist(self, user_id: str, symbol: str) -> Dict:
        """Remove a stock from user's watchlist"""
        try:
            watchlist_item = self.db.query(models.Watchlist).filter(
                models.Watchlist.user_id == user_id,
                models.Watchlist.symbol == symbol.upper()
            ).first()
            
            if not watchlist_item:
                return {"error": "Stock not found in watchlist"}
            
            self.db.delete(watchlist_item)
            self.db.commit()
            
            return {"message": f"Removed {symbol.upper()} from watchlist"}
            
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return {"error": f"Failed to remove from watchlist: {str(e)}"}

    def get_watchlist(self, user_id: str) -> List[Dict]:
        """Get user's watchlist with current prices"""
        try:
            watchlist_items = self.db.query(models.Watchlist).filter(
                models.Watchlist.user_id == user_id
            ).all()
            
            results = []
            for item in watchlist_items:
                try:
                    current_price = self.market_data_service.get_current_price(item.symbol)
                    
                    # Check if alert should be triggered
                    alert_triggered = False
                    if item.alert_price and current_price:
                        if current_price['price'] >= item.alert_price:
                            alert_triggered = True
                    
                    results.append({
                        "id": item.id,
                        "symbol": item.symbol,
                        "alert_price": float(item.alert_price) if item.alert_price else None,
                        "current_price": current_price['price'] if current_price else None,
                        "change": current_price.get('change', 0) if current_price else 0,
                        "change_percent": current_price.get('change_percent', 0) if current_price else 0,
                        "alert_triggered": alert_triggered,
                        "created_at": item.created_at.isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error getting price for {item.symbol}: {e}")
                    results.append({
                        "id": item.id,
                        "symbol": item.symbol,
                        "alert_price": float(item.alert_price) if item.alert_price else None,
                        "current_price": None,
                        "change": 0,
                        "change_percent": 0,
                        "alert_triggered": False,
                        "created_at": item.created_at.isoformat()
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting watchlist: {e}")
            return []

    def update_alert_price(self, user_id: str, symbol: str, alert_price: float) -> Dict:
        """Update alert price for a watchlist item"""
        try:
            watchlist_item = self.db.query(models.Watchlist).filter(
                models.Watchlist.user_id == user_id,
                models.Watchlist.symbol == symbol.upper()
            ).first()
            
            if not watchlist_item:
                return {"error": "Stock not found in watchlist"}
            
            watchlist_item.alert_price = alert_price
            self.db.commit()
            
            return {
                "message": f"Updated alert price for {symbol.upper()} to ${alert_price}",
                "alert_price": alert_price
            }
            
        except Exception as e:
            logger.error(f"Error updating alert price: {e}")
            return {"error": f"Failed to update alert price: {str(e)}"}

    def get_alerts(self, user_id: str) -> List[Dict]:
        """Get triggered alerts for user"""
        try:
            watchlist_items = self.db.query(models.Watchlist).filter(
                models.Watchlist.user_id == user_id,
                models.Watchlist.alert_price.isnot(None)
            ).all()
            
            alerts = []
            for item in watchlist_items:
                try:
                    current_price = self.market_data_service.get_current_price(item.symbol)
                    
                    if current_price and item.alert_price:
                        if current_price['price'] >= item.alert_price:
                            alerts.append({
                                "symbol": item.symbol,
                                "alert_price": float(item.alert_price),
                                "current_price": current_price['price'],
                                "triggered_at": datetime.now().isoformat(),
                                "message": f"{item.symbol} reached alert price of ${item.alert_price}"
                            })
                except Exception as e:
                    logger.error(f"Error checking alert for {item.symbol}: {e}")
                    continue
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []

    def get_watchlist_performance(self, user_id: str) -> Dict:
        """Get performance summary for user's watchlist"""
        try:
            watchlist_items = self.db.query(models.Watchlist).filter(
                models.Watchlist.user_id == user_id
            ).all()
            
            if not watchlist_items:
                return {"error": "No items in watchlist"}
            
            total_items = len(watchlist_items)
            positive_changes = 0
            negative_changes = 0
            total_change_percent = 0
            
            for item in watchlist_items:
                try:
                    current_price = self.market_data_service.get_current_price(item.symbol)
                    if current_price:
                        change_percent = current_price.get('change_percent', 0)
                        total_change_percent += change_percent
                        
                        if change_percent > 0:
                            positive_changes += 1
                        elif change_percent < 0:
                            negative_changes += 1
                except Exception as e:
                    logger.error(f"Error getting performance for {item.symbol}: {e}")
                    continue
            
            avg_change_percent = total_change_percent / total_items if total_items > 0 else 0
            
            return {
                "total_items": total_items,
                "positive_changes": positive_changes,
                "negative_changes": negative_changes,
                "avg_change_percent": round(avg_change_percent, 2),
                "performance_summary": "Positive" if avg_change_percent > 0 else "Negative" if avg_change_percent < 0 else "Neutral"
            }
            
        except Exception as e:
            logger.error(f"Error getting watchlist performance: {e}")
            return {"error": f"Failed to get performance: {str(e)}"}

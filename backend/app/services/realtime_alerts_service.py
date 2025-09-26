import asyncio
import logging
from typing import Dict, List, Optional, Set
from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, timedelta
from app.services.market_data_service import MarketDataService
from app.services.realtime_service import RealtimeService
import json

logger = logging.getLogger(__name__)

class RealtimeAlertsService:
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.websocket_service = RealtimeService(db)
        self.active_alerts: Dict[str, List[Dict]] = {}
        self.alert_subscribers: Set[str] = set()
        self.is_running = False

    async def start_alert_monitoring(self):
        """Start monitoring for price alerts"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Starting real-time alert monitoring")

        while self.is_running:
            try:
                await self._check_price_alerts()
                await self._check_technical_alerts()
                await self._check_volume_alerts()
                await self._check_news_alerts()
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                await asyncio.sleep(30)

    async def stop_alert_monitoring(self):
        """Stop monitoring for price alerts"""
        self.is_running = False
        logger.info("Stopped real-time alert monitoring")

    async def _check_price_alerts(self):
        """Check for price-based alerts"""
        try:
            # Get all active price alerts
            price_alerts = self.db.query(models.PriceAlert).filter(
                models.PriceAlert.is_active == True
            ).all()

            for alert in price_alerts:
                try:
                    # Get current price
                    current_price = self.market_data_service.get_current_price(alert.symbol)
                    
                    if not current_price:
                        continue

                    price = current_price['price']
                    triggered = False
                    alert_type = ""

                    # Check alert conditions
                    if alert.alert_type == "price_above" and price >= alert.target_price:
                        triggered = True
                        alert_type = "Price Above"
                    elif alert.alert_type == "price_below" and price <= alert.target_price:
                        triggered = True
                        alert_type = "Price Below"
                    elif alert.alert_type == "price_change_up" and current_price.get('change_percent', 0) >= alert.target_price:
                        triggered = True
                        alert_type = "Price Change Up"
                    elif alert.alert_type == "price_change_down" and current_price.get('change_percent', 0) <= -alert.target_price:
                        triggered = True
                        alert_type = "Price Change Down"

                    if triggered:
                        await self._trigger_alert(alert, {
                            "type": "price_alert",
                            "alert_type": alert_type,
                            "current_price": price,
                            "target_price": alert.target_price,
                            "change_percent": current_price.get('change_percent', 0)
                        })

                except Exception as e:
                    logger.error(f"Error checking price alert for {alert.symbol}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error checking price alerts: {e}")

    async def _check_technical_alerts(self):
        """Check for technical indicator alerts"""
        try:
            # Get all active technical alerts
            technical_alerts = self.db.query(models.TechnicalAlert).filter(
                models.TechnicalAlert.is_active == True
            ).all()

            for alert in technical_alerts:
                try:
                    # Get technical indicators
                    from app.services.technical_analysis_service import TechnicalAnalysisService
                    tech_service = TechnicalAnalysisService(self.db)
                    indicators = tech_service.get_indicators(alert.symbol, 30)
                    
                    if not indicators:
                        continue

                    triggered = False
                    alert_type = ""

                    # Check RSI alerts
                    if alert.indicator_type == "rsi_overbought" and indicators.get("rsi", {}).get("value", 50) > 70:
                        triggered = True
                        alert_type = "RSI Overbought"
                    elif alert.indicator_type == "rsi_oversold" and indicators.get("rsi", {}).get("value", 50) < 30:
                        triggered = True
                        alert_type = "RSI Oversold"

                    # Check MACD alerts
                    elif alert.indicator_type == "macd_bullish" and indicators.get("macd", {}).get("signal") == "bullish":
                        triggered = True
                        alert_type = "MACD Bullish"
                    elif alert.indicator_type == "macd_bearish" and indicators.get("macd", {}).get("signal") == "bearish":
                        triggered = True
                        alert_type = "MACD Bearish"

                    # Check Moving Average alerts
                    elif alert.indicator_type == "ma_crossover" and indicators.get("moving_averages", {}).get("signal") == "bullish":
                        triggered = True
                        alert_type = "Moving Average Crossover"

                    if triggered:
                        await self._trigger_alert(alert, {
                            "type": "technical_alert",
                            "alert_type": alert_type,
                            "indicator_value": indicators.get(alert.indicator_type, {}).get("value", 0),
                            "signal": indicators.get(alert.indicator_type, {}).get("signal", "neutral")
                        })

                except Exception as e:
                    logger.error(f"Error checking technical alert for {alert.symbol}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error checking technical alerts: {e}")

    async def _check_volume_alerts(self):
        """Check for volume-based alerts"""
        try:
            # Get all active volume alerts
            volume_alerts = self.db.query(models.VolumeAlert).filter(
                models.VolumeAlert.is_active == True
            ).all()

            for alert in volume_alerts:
                try:
                    # Get current volume data
                    current_price = self.market_data_service.get_current_price(alert.symbol)
                    
                    if not current_price:
                        continue

                    volume = current_price.get('volume', 0)
                    avg_volume = current_price.get('avg_volume', volume)
                    
                    if avg_volume == 0:
                        continue

                    volume_ratio = volume / avg_volume
                    triggered = False
                    alert_type = ""

                    # Check volume conditions
                    if alert.alert_type == "volume_spike" and volume_ratio >= alert.volume_threshold:
                        triggered = True
                        alert_type = "Volume Spike"
                    elif alert.alert_type == "volume_drop" and volume_ratio <= (1 / alert.volume_threshold):
                        triggered = True
                        alert_type = "Volume Drop"

                    if triggered:
                        await self._trigger_alert(alert, {
                            "type": "volume_alert",
                            "alert_type": alert_type,
                            "current_volume": volume,
                            "avg_volume": avg_volume,
                            "volume_ratio": volume_ratio
                        })

                except Exception as e:
                    logger.error(f"Error checking volume alert for {alert.symbol}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error checking volume alerts: {e}")

    async def _check_news_alerts(self):
        """Check for news-based alerts"""
        try:
            # Get all active news alerts
            news_alerts = self.db.query(models.NewsAlert).filter(
                models.NewsAlert.is_active == True
            ).all()

            for alert in news_alerts:
                try:
                    # Get recent news
                    from app.services.news_service import NewsService
                    news_service = NewsService()
                    news = news_service.get_stock_news(alert.symbol, 5)
                    
                    if not news:
                        continue

                    # Check for keywords in news
                    triggered = False
                    alert_type = ""
                    relevant_news = []

                    for article in news:
                        title = article.get('title', '').lower()
                        summary = article.get('summary', '').lower()
                        text = f"{title} {summary}"
                        
                        # Check for alert keywords
                        for keyword in alert.keywords.split(','):
                            keyword = keyword.strip().lower()
                            if keyword in text:
                                triggered = True
                                alert_type = f"News Alert: {keyword}"
                                relevant_news.append(article)
                                break

                    if triggered:
                        await self._trigger_alert(alert, {
                            "type": "news_alert",
                            "alert_type": alert_type,
                            "relevant_news": relevant_news[:3]  # Top 3 relevant articles
                        })

                except Exception as e:
                    logger.error(f"Error checking news alert for {alert.symbol}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error checking news alerts: {e}")

    async def _trigger_alert(self, alert, alert_data: Dict):
        """Trigger an alert and send notifications"""
        try:
            # Create alert record
            alert_record = models.AlertHistory(
                user_id=alert.user_id,
                symbol=alert.symbol,
                alert_type=alert_data["type"],
                message=f"{alert_data['alert_type']} alert for {alert.symbol}",
                data=json.dumps(alert_data),
                triggered_at=datetime.now()
            )
            
            self.db.add(alert_record)
            self.db.commit()

            # Send WebSocket notification
            await self._send_websocket_alert(alert.user_id, alert_data)

            # Send email notification (if configured)
            await self._send_email_alert(alert.user_id, alert_data)

            # Send push notification (if configured)
            await self._send_push_alert(alert.user_id, alert_data)

            logger.info(f"Alert triggered for {alert.symbol}: {alert_data['alert_type']}")

        except Exception as e:
            logger.error(f"Error triggering alert: {e}")

    async def _send_websocket_alert(self, user_id: str, alert_data: Dict):
        """Send alert via WebSocket"""
        try:
            message = {
                "type": "alert",
                "user_id": user_id,
                "data": alert_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket_service.broadcast_to_all(message)
            
        except Exception as e:
            logger.error(f"Error sending WebSocket alert: {e}")

    async def _send_email_alert(self, user_id: str, alert_data: Dict):
        """Send alert via email"""
        try:
            # TODO: Implement email service
            logger.info(f"Email alert sent to user {user_id}: {alert_data['alert_type']}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")

    async def _send_push_alert(self, user_id: str, alert_data: Dict):
        """Send push notification"""
        try:
            # TODO: Implement push notification service
            logger.info(f"Push alert sent to user {user_id}: {alert_data['alert_type']}")
            
        except Exception as e:
            logger.error(f"Error sending push alert: {e}")

    def create_price_alert(self, user_id: str, symbol: str, alert_type: str, target_price: float, message: str = "") -> Dict:
        """Create a price-based alert"""
        try:
            alert = models.PriceAlert(
                user_id=user_id,
                symbol=symbol.upper(),
                alert_type=alert_type,
                target_price=target_price,
                message=message,
                is_active=True,
                created_at=datetime.now()
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            return {
                "id": alert.id,
                "symbol": alert.symbol,
                "alert_type": alert.alert_type,
                "target_price": alert.target_price,
                "message": alert.message,
                "is_active": alert.is_active,
                "created_at": alert.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating price alert: {e}")
            return {"error": f"Failed to create alert: {str(e)}"}

    def create_technical_alert(self, user_id: str, symbol: str, indicator_type: str, message: str = "") -> Dict:
        """Create a technical indicator alert"""
        try:
            alert = models.TechnicalAlert(
                user_id=user_id,
                symbol=symbol.upper(),
                indicator_type=indicator_type,
                message=message,
                is_active=True,
                created_at=datetime.now()
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            return {
                "id": alert.id,
                "symbol": alert.symbol,
                "indicator_type": alert.indicator_type,
                "message": alert.message,
                "is_active": alert.is_active,
                "created_at": alert.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating technical alert: {e}")
            return {"error": f"Failed to create alert: {str(e)}"}

    def get_user_alerts(self, user_id: str) -> Dict:
        """Get all alerts for a user"""
        try:
            price_alerts = self.db.query(models.PriceAlert).filter(
                models.PriceAlert.user_id == user_id
            ).all()
            
            technical_alerts = self.db.query(models.TechnicalAlert).filter(
                models.TechnicalAlert.user_id == user_id
            ).all()
            
            volume_alerts = self.db.query(models.VolumeAlert).filter(
                models.VolumeAlert.user_id == user_id
            ).all()
            
            news_alerts = self.db.query(models.NewsAlert).filter(
                models.NewsAlert.user_id == user_id
            ).all()
            
            alert_history = self.db.query(models.AlertHistory).filter(
                models.AlertHistory.user_id == user_id
            ).order_by(models.AlertHistory.triggered_at.desc()).limit(50).all()
            
            return {
                "price_alerts": [
                    {
                        "id": alert.id,
                        "symbol": alert.symbol,
                        "alert_type": alert.alert_type,
                        "target_price": alert.target_price,
                        "message": alert.message,
                        "is_active": alert.is_active,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in price_alerts
                ],
                "technical_alerts": [
                    {
                        "id": alert.id,
                        "symbol": alert.symbol,
                        "indicator_type": alert.indicator_type,
                        "message": alert.message,
                        "is_active": alert.is_active,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in technical_alerts
                ],
                "volume_alerts": [
                    {
                        "id": alert.id,
                        "symbol": alert.symbol,
                        "alert_type": alert.alert_type,
                        "volume_threshold": alert.volume_threshold,
                        "message": alert.message,
                        "is_active": alert.is_active,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in volume_alerts
                ],
                "news_alerts": [
                    {
                        "id": alert.id,
                        "symbol": alert.symbol,
                        "keywords": alert.keywords,
                        "message": alert.message,
                        "is_active": alert.is_active,
                        "created_at": alert.created_at.isoformat()
                    }
                    for alert in news_alerts
                ],
                "alert_history": [
                    {
                        "id": alert.id,
                        "symbol": alert.symbol,
                        "alert_type": alert.alert_type,
                        "message": alert.message,
                        "data": json.loads(alert.data) if alert.data else {},
                        "triggered_at": alert.triggered_at.isoformat()
                    }
                    for alert in alert_history
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return {"error": f"Failed to get alerts: {str(e)}"}

    def delete_alert(self, user_id: str, alert_id: int, alert_type: str) -> Dict:
        """Delete an alert"""
        try:
            if alert_type == "price":
                alert = self.db.query(models.PriceAlert).filter(
                    models.PriceAlert.id == alert_id,
                    models.PriceAlert.user_id == user_id
                ).first()
            elif alert_type == "technical":
                alert = self.db.query(models.TechnicalAlert).filter(
                    models.TechnicalAlert.id == alert_id,
                    models.TechnicalAlert.user_id == user_id
                ).first()
            elif alert_type == "volume":
                alert = self.db.query(models.VolumeAlert).filter(
                    models.VolumeAlert.id == alert_id,
                    models.VolumeAlert.user_id == user_id
                ).first()
            elif alert_type == "news":
                alert = self.db.query(models.NewsAlert).filter(
                    models.NewsAlert.id == alert_id,
                    models.NewsAlert.user_id == user_id
                ).first()
            else:
                return {"error": "Invalid alert type"}
            
            if not alert:
                return {"error": "Alert not found"}
            
            self.db.delete(alert)
            self.db.commit()
            
            return {"message": "Alert deleted successfully"}
            
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            return {"error": f"Failed to delete alert: {str(e)}"}

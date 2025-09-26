from sqlalchemy.orm import Session
from app.db import models
from app.services.ai_opponent_service import AIOpponentService
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import asyncio
import time
from threading import Thread
import schedule

logger = logging.getLogger(__name__)

class BackgroundAIService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_opponent_service = AIOpponentService(db)
        self.is_running = False
        self.background_thread = None

    def start_background_trading(self):
        """Start the background AI trading service"""
        if self.is_running:
            logger.info("Background AI trading is already running")
            return

        self.is_running = True
        self.background_thread = Thread(target=self._run_background_trading, daemon=True)
        self.background_thread.start()
        logger.info("Background AI trading service started")

    def stop_background_trading(self):
        """Stop the background AI trading service"""
        self.is_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        logger.info("Background AI trading service stopped")

    def _run_background_trading(self):
        """Main background trading loop"""
        logger.info("Starting background AI trading loop")
        
        # Schedule AI trading rounds
        schedule.every(30).minutes.do(self._execute_all_ai_trading_rounds)
        schedule.every().hour.do(self._update_all_ai_portfolios)
        schedule.every().day.at("09:30").do(self._daily_ai_analysis)  # Market open
        schedule.every().day.at("16:00").do(self._daily_ai_analysis)  # Market close

        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in background AI trading loop: {e}")
                time.sleep(60)

    def _execute_all_ai_trading_rounds(self):
        """Execute trading rounds for all active AI opponents"""
        try:
            # Get all active AI opponents
            active_opponents = self.db.query(models.AIOpponent).filter(
                models.AIOpponent.is_active == True
            ).all()

            logger.info(f"Executing trading rounds for {len(active_opponents)} active AI opponents")

            for opponent in active_opponents:
                try:
                    # Execute trading round asynchronously
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(
                        self.ai_opponent_service.execute_ai_trading_round(opponent.user_id)
                    )
                    
                    logger.info(f"AI opponent {opponent.user_id} executed trading round: {result}")
                    
                except Exception as e:
                    logger.error(f"Error executing trading round for AI opponent {opponent.user_id}: {e}")

        except Exception as e:
            logger.error(f"Error in _execute_all_ai_trading_rounds: {e}")

    def _update_all_ai_portfolios(self):
        """Update portfolio values for all AI opponents"""
        try:
            active_opponents = self.db.query(models.AIOpponent).filter(
                models.AIOpponent.is_active == True
            ).all()

            logger.info(f"Updating portfolio values for {len(active_opponents)} AI opponents")

            for opponent in active_opponents:
                try:
                    ai_portfolio = self.ai_opponent_service.portfolio_service.get_portfolio_by_user_id(opponent.ai_user_id)
                    if ai_portfolio:
                        self.ai_opponent_service._update_ai_portfolio_value(ai_portfolio)
                        logger.info(f"Updated portfolio value for AI opponent {opponent.user_id}")
                        
                except Exception as e:
                    logger.error(f"Error updating portfolio for AI opponent {opponent.user_id}: {e}")

        except Exception as e:
            logger.error(f"Error in _update_all_ai_portfolios: {e}")

    def _daily_ai_analysis(self):
        """Perform daily analysis and strategy adjustments"""
        try:
            active_opponents = self.db.query(models.AIOpponent).filter(
                models.AIOpponent.is_active == True
            ).all()

            logger.info(f"Performing daily analysis for {len(active_opponents)} AI opponents")

            for opponent in active_opponents:
                try:
                    # Get competition data
                    competition_data = self.ai_opponent_service.get_competition_data(opponent.user_id)
                    
                    # Log daily performance
                    user_performance = competition_data.get('user_performance', {})
                    ai_performance = competition_data.get('ai_performance', {})
                    
                    logger.info(f"Daily analysis for {opponent.user_id}:")
                    logger.info(f"  User return: {user_performance.get('return_percentage', 0):.2f}%")
                    logger.info(f"  AI return: {ai_performance.get('return_percentage', 0):.2f}%")
                    
                    # Update opponent statistics
                    opponent.total_trades += 1
                    if ai_performance.get('return_percentage', 0) > user_performance.get('return_percentage', 0):
                        opponent.winning_trades += 1
                    
                    self.db.commit()
                    
                except Exception as e:
                    logger.error(f"Error in daily analysis for AI opponent {opponent.user_id}: {e}")

        except Exception as e:
            logger.error(f"Error in _daily_ai_analysis: {e}")

    def get_background_status(self) -> Dict[str, Any]:
        """Get the current status of background AI trading"""
        active_opponents = self.db.query(models.AIOpponent).filter(
            models.AIOpponent.is_active == True
        ).all()

        return {
            "is_running": self.is_running,
            "active_opponents_count": len(active_opponents),
            "last_update": datetime.utcnow().isoformat(),
            "next_trading_round": "Every 30 minutes",
            "next_portfolio_update": "Every hour",
            "next_daily_analysis": "9:30 AM and 4:00 PM daily"
        }

    def force_ai_trading_round(self, user_id: str) -> Dict[str, Any]:
        """Force an immediate AI trading round for a specific user"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                self.ai_opponent_service.execute_ai_trading_round(user_id)
            )
            
            logger.info(f"Forced AI trading round for {user_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error forcing AI trading round for {user_id}: {e}")
            return {"error": str(e)}

# Global instance
background_ai_service = None

def get_background_ai_service(db: Session) -> BackgroundAIService:
    """Get the global background AI service instance"""
    global background_ai_service
    if background_ai_service is None:
        background_ai_service = BackgroundAIService(db)
    return background_ai_service

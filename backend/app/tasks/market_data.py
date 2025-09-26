from celery import shared_task
from app.core.celery import celery_app
from app.services.market_data_service import MarketDataService
from app.db.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_market_data():
    """Fetch latest market data for all active assets"""
    db = SessionLocal()
    try:
        market_service = MarketDataService(db)
        
        # Get all active assets
        from app.db.models import Asset
        assets = db.query(Asset).filter(Asset.is_active == True).all()
        
        for asset in assets:
            try:
                # Fetch current price
                current_price = market_service._fetch_current_price_from_api(asset.symbol)
                if current_price:
                    logger.info(f"Updated price for {asset.symbol}: ${current_price}")
            except Exception as e:
                logger.error(f"Error fetching data for {asset.symbol}: {e}")
        
        logger.info(f"Market data fetch completed for {len(assets)} assets")
        
    except Exception as e:
        logger.error(f"Error in fetch_market_data task: {e}")
    finally:
        db.close()

@shared_task
def update_portfolio_values():
    """Update portfolio values based on current market prices"""
    db = SessionLocal()
    try:
        from app.db.models import Portfolio, Holding, Asset, Price
        from sqlalchemy import func
        
        portfolios = db.query(Portfolio).all()
        
        for portfolio in portfolios:
            holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
            
            total_value = portfolio.cash_balance
            
            for holding in holdings:
                # Get latest price for the asset
                latest_price = db.query(Price).filter(
                    Price.asset_id == holding.asset_id
                ).order_by(Price.timestamp.desc()).first()
                
                if latest_price:
                    current_value = holding.quantity * latest_price.close_price
                    holding.current_value = current_value
                    holding.unrealized_pnl = current_value - (holding.quantity * holding.average_cost)
                    total_value += current_value
            
            portfolio.total_value = total_value
        
        db.commit()
        logger.info(f"Updated portfolio values for {len(portfolios)} portfolios")
        
    except Exception as e:
        logger.error(f"Error updating portfolio values: {e}")
        db.rollback()
    finally:
        db.close()

@shared_task
def cleanup_old_data():
    """Clean up old data to keep database size manageable"""
    db = SessionLocal()
    try:
        from app.db.models import Price, Analytics
        from datetime import datetime, timedelta
        
        # Keep only last 2 years of price data
        cutoff_date = datetime.utcnow() - timedelta(days=730)
        
        old_prices = db.query(Price).filter(Price.timestamp < cutoff_date).count()
        db.query(Price).filter(Price.timestamp < cutoff_date).delete()
        
        # Keep only last year of analytics data
        cutoff_date = datetime.utcnow() - timedelta(days=365)
        old_analytics = db.query(Analytics).filter(Analytics.date < cutoff_date).count()
        db.query(Analytics).filter(Analytics.date < cutoff_date).delete()
        
        db.commit()
        logger.info(f"Cleaned up {old_prices} old price records and {old_analytics} old analytics records")
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        db.rollback()
    finally:
        db.close()

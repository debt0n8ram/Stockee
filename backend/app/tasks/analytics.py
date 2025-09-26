from celery import shared_task
from app.core.celery import celery_app
from app.services.analytics_service import AnalyticsService
from app.db.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

@shared_task
def calculate_daily_analytics():
    """Calculate daily analytics for all portfolios"""
    db = SessionLocal()
    try:
        analytics_service = AnalyticsService(db)
        
        from app.db.models import Portfolio
        portfolios = db.query(Portfolio).all()
        
        for portfolio in portfolios:
            try:
                # Calculate performance metrics
                performance = analytics_service.get_performance_analytics(portfolio.user_id, 30)
                
                # Store analytics in database
                from app.db.models import Analytics
                from datetime import datetime
                
                analytics_record = Analytics(
                    portfolio_id=portfolio.id,
                    date=datetime.utcnow().date(),
                    total_value=portfolio.total_value,
                    daily_return=performance.get('daily_return', 0),
                    cumulative_return=performance.get('total_return', 0),
                    sharpe_ratio=performance.get('sharpe_ratio', 0),
                    max_drawdown=performance.get('max_drawdown', 0),
                    volatility=performance.get('volatility', 0)
                )
                
                db.add(analytics_record)
                
            except Exception as e:
                logger.error(f"Error calculating analytics for portfolio {portfolio.id}: {e}")
        
        db.commit()
        logger.info(f"Daily analytics calculated for {len(portfolios)} portfolios")
        
    except Exception as e:
        logger.error(f"Error calculating daily analytics: {e}")
        db.rollback()
    finally:
        db.close()

@shared_task
def generate_risk_reports():
    """Generate risk reports for all portfolios"""
    db = SessionLocal()
    try:
        analytics_service = AnalyticsService(db)
        
        from app.db.models import Portfolio
        portfolios = db.query(Portfolio).all()
        
        for portfolio in portfolios:
            try:
                risk_metrics = analytics_service.get_risk_metrics(portfolio.user_id, 30)
                logger.info(f"Risk metrics calculated for portfolio {portfolio.id}: {risk_metrics}")
            except Exception as e:
                logger.error(f"Error generating risk report for portfolio {portfolio.id}: {e}")
        
        logger.info(f"Risk reports generated for {len(portfolios)} portfolios")
        
    except Exception as e:
        logger.error(f"Error generating risk reports: {e}")
    finally:
        db.close()

@shared_task
def benchmark_comparison():
    """Compare all portfolios against benchmarks"""
    db = SessionLocal()
    try:
        analytics_service = AnalyticsService(db)
        
        from app.db.models import Portfolio
        portfolios = db.query(Portfolio).all()
        
        benchmarks = ['SPY', 'QQQ', 'BTC']
        
        for portfolio in portfolios:
            for benchmark in benchmarks:
                try:
                    comparison = analytics_service.get_benchmark_comparison(portfolio.user_id, benchmark, 30)
                    logger.info(f"Benchmark comparison ({benchmark}) for portfolio {portfolio.id}")
                except Exception as e:
                    logger.error(f"Error comparing portfolio {portfolio.id} to {benchmark}: {e}")
        
        logger.info(f"Benchmark comparisons completed for {len(portfolios)} portfolios")
        
    except Exception as e:
        logger.error(f"Error in benchmark comparison: {e}")
    finally:
        db.close()

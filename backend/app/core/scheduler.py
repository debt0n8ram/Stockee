from celery import Celery
from celery.schedules import crontab
from app.core.celery import celery_app

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    # Fetch market data every 5 minutes during market hours
    'fetch-market-data': {
        'task': 'app.tasks.market_data.fetch_market_data',
        'schedule': crontab(minute='*/5', hour='9-16', day_of_week='1-5'),  # Every 5 min, 9-16, Mon-Fri
    },
    
    # Update portfolio values every 15 minutes
    'update-portfolio-values': {
        'task': 'app.tasks.market_data.update_portfolio_values',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    
    # Calculate daily analytics at end of trading day
    'calculate-daily-analytics': {
        'task': 'app.tasks.analytics.calculate_daily_analytics',
        'schedule': crontab(hour=17, minute=0, day_of_week='1-5'),  # 5 PM, Mon-Fri
    },
    
    # Generate risk reports daily
    'generate-risk-reports': {
        'task': 'app.tasks.analytics.generate_risk_reports',
        'schedule': crontab(hour=18, minute=0),  # 6 PM daily
    },
    
    # Benchmark comparison weekly
    'benchmark-comparison': {
        'task': 'app.tasks.analytics.benchmark_comparison',
        'schedule': crontab(hour=19, minute=0, day_of_week=1),  # 7 PM, Monday
    },
    
    # Retrain ML models weekly
    'retrain-ml-models': {
        'task': 'app.tasks.ai.retrain_ml_models',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # 2 AM, Monday
    },
    
    # Generate price predictions daily
    'generate-price-predictions': {
        'task': 'app.tasks.ai.generate_price_predictions',
        'schedule': crontab(hour=6, minute=0),  # 6 AM daily
    },
    
    # Analyze portfolio sentiment daily
    'analyze-portfolio-sentiment': {
        'task': 'app.tasks.ai.analyze_portfolio_sentiment',
        'schedule': crontab(hour=7, minute=0),  # 7 AM daily
    },
    
    # Cleanup old data monthly
    'cleanup-old-data': {
        'task': 'app.tasks.market_data.cleanup_old_data',
        'schedule': crontab(hour=3, minute=0, day=1),  # 3 AM, 1st of month
    },
}

celery_app.conf.timezone = 'UTC'

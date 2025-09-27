from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://stockee_user:stockee_password@localhost:5432/stockee"
    redis_url: str = "redis://localhost:6379"
    
    # API Keys - Stock Market Data
    alpha_vantage_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    finnhub_api_key: Optional[str] = None
    iex_cloud_api_key: Optional[str] = None
    quandl_api_key: Optional[str] = None
    nasdaq_data_link_api_key: Optional[str] = None
    
    # API Keys - Cryptocurrency Data
    coingecko_api_key: Optional[str] = None
    coinmarketcap_api_key: Optional[str] = None
    cryptocompare_api_key: Optional[str] = None
    coindesk_api_key: Optional[str] = None
    coinapi_api_key: Optional[str] = None
    binance_api_key: Optional[str] = None
    binance_secret_key: Optional[str] = None
    coinbase_api_key: Optional[str] = None
    coinbase_secret_key: Optional[str] = None
    
    # API Keys - News & Sentiment
    news_api_key: Optional[str] = None
    world_news_api_key: Optional[str] = None
    reddit_api_key: Optional[str] = None
    reddit_secret_key: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_secret_key: Optional[str] = None
    twitter_bearer_token: Optional[str] = None
    
    # API Keys - AI & Machine Learning
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # API Keys - Economic Data
    fred_api_key: Optional[str] = None
    world_bank_api_key: Optional[str] = None
    imf_api_key: Optional[str] = None
    
    # API Keys - Alternative Data
    glassdoor_api_key: Optional[str] = None
    indeed_api_key: Optional[str] = None
    google_trends_api_key: Optional[str] = None
    
    # API Keys - Weather & Commodities
    openweather_api_key: Optional[str] = None
    commodities_api_key: Optional[str] = None
    
    # API Configuration URLs
    coinapi_base_url: str = "https://rest.coinapi.io/v1"
    nasdaq_data_link_base_url: str = "https://data.nasdaq.com/api/v3"
    world_bank_base_url: str = "https://api.worldbank.org/v2"
    imf_base_url: str = "https://dataservices.imf.org/REST/SDMX_JSON.svc"
    world_news_base_url: str = "https://api.worldnewsapi.com/api/v1"
    reddit_base_url: str = "https://oauth.reddit.com"
    
    # API Configuration
    alpha_vantage_base_url: str = "https://www.alphavantage.co/query"
    alpha_vantage_rate_limit: int = 5
    alpha_vantage_daily_limit: int = 500
    
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_rate_limit: int = 50
    coingecko_daily_limit: int = 10000
    
    coinmarketcap_base_url: str = "https://pro-api.coinmarketcap.com/v1"
    coinmarketcap_rate_limit: int = 30
    coinmarketcap_daily_limit: int = 10000
    
    cryptocompare_base_url: str = "https://min-api.cryptocompare.com/data"
    cryptocompare_rate_limit: int = 100
    cryptocompare_daily_limit: int = 100000
    
    # Application
    secret_key: str = "your-secret-key-change-in-production"
    debug: bool = True
    environment: str = "development"
    
    # Trading
    default_starting_balance: float = 100000.0
    max_trading_hours_start: int = 9
    max_trading_hours_end: int = 16
    trading_timezone: str = "US/Eastern"
    
    # AI/ML
    ml_model_retrain_interval: int = 7
    prediction_horizon: int = 30
    sentiment_analysis_enabled: bool = True
    chatgpt_model: str = "gpt-4o-mini"
    
    # API Fallback Configuration
    enable_api_fallback: bool = True
    primary_crypto_api: str = "coingecko"
    secondary_crypto_api: str = "coinmarketcap"
    tertiary_crypto_api: str = "cryptocompare"
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    rate_limit_burst_size: int = 200
    
    # Caching Configuration
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    cache_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment

settings = Settings()

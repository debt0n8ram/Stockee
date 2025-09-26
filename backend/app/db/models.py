from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    asset_type = Column(String(20), nullable=False)  # 'stock', 'crypto', 'etf', etc.
    exchange = Column(String(50))
    currency = Column(String(10), default="USD")
    sector = Column(String(100))
    market_cap = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    prices = relationship("Price", back_populates="asset")
    transactions = relationship("Transaction", back_populates="asset")
    watchlist_items = relationship("Watchlist", back_populates="asset")

class Price(Base):
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    adjusted_close = Column(Float)
    
    # Relationships
    asset = relationship("Asset", back_populates="prices")
    
    # Indexes for time-series queries
    __table_args__ = (
        Index('idx_prices_asset_timestamp', 'asset_id', 'timestamp'),
        Index('idx_prices_timestamp', 'timestamp'),
    )

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    cash_balance = Column(Float, default=100000.0)
    total_value = Column(Float, default=100000.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    holdings = relationship("Holding", back_populates="portfolio")
    transactions = relationship("Transaction", back_populates="portfolio")

class Holding(Base):
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_value = Column(Float)
    unrealized_pnl = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    asset = relationship("Asset")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'buy', 'sell'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    order_type = Column(String(20), default="market")  # 'market', 'limit', 'stop'
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    asset = relationship("Asset", back_populates="transactions")

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    total_value = Column(Float, nullable=False)
    daily_return = Column(Float)
    cumulative_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    volatility = Column(Float)
    beta = Column(Float)
    
    # Relationships
    portfolio = relationship("Portfolio")

class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    prediction_date = Column(DateTime(timezone=True), nullable=False)
    target_date = Column(DateTime(timezone=True), nullable=False)
    predicted_price = Column(Float, nullable=False)
    confidence = Column(Float)
    model_version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("Asset")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    session_id = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    context_data = Column(Text)  # JSON string with portfolio/market context

class BankTransaction(Base):
    __tablename__ = "bank_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'deposit', 'withdrawal', 'reset'
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(String(255))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    balance_after = Column(Numeric(15, 2), nullable=False)

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    alert_price = Column(Numeric(15, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    asset = relationship("Asset", back_populates="watchlist_items")

class PriceAlert(Base):
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    alert_type = Column(String(50), nullable=False)  # 'price_above', 'price_below', 'price_change_up', 'price_change_down'
    target_price = Column(Numeric(15, 2), nullable=False)
    message = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TechnicalAlert(Base):
    __tablename__ = "technical_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    indicator_type = Column(String(50), nullable=False)  # 'rsi_overbought', 'rsi_oversold', 'macd_bullish', 'macd_bearish', 'ma_crossover'
    message = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VolumeAlert(Base):
    __tablename__ = "volume_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    alert_type = Column(String(50), nullable=False)  # 'volume_spike', 'volume_drop'
    volume_threshold = Column(Float, nullable=False)  # Multiplier for average volume
    message = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NewsAlert(Base):
    __tablename__ = "news_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    keywords = Column(String(500), nullable=False)  # Comma-separated keywords
    message = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AlertHistory(Base):
    __tablename__ = "alert_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    alert_type = Column(String(50), nullable=False)
    message = Column(String(255), nullable=False)
    data = Column(Text)  # JSON data with alert details
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())

class AdvancedOrder(Base):
    __tablename__ = "advanced_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    order_type = Column(String(50), nullable=False)  # 'stop_loss', 'take_profit', 'trailing_stop', 'bracket_entry', 'bracket_stop_loss', 'bracket_take_profit'
    side = Column(String(10), nullable=False)  # 'buy' or 'sell'
    quantity = Column(Integer, nullable=False)
    stop_price = Column(Numeric(15, 2), nullable=True)
    limit_price = Column(Numeric(15, 2), nullable=True)
    trail_amount = Column(Numeric(15, 2), nullable=True)  # For trailing stops
    trail_type = Column(String(20), nullable=True)  # 'percentage' or 'dollar'
    order_status = Column(String(20), nullable=False, default="pending")  # 'pending', 'active', 'filled', 'cancelled'
    message = Column(String(255))
    parent_order_id = Column(Integer, nullable=True)  # For bracket orders
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    model_type = Column(String(50), nullable=False)  # 'random_forest', 'lstm', 'sentiment_random_forest', etc.
    features = Column(Text, nullable=False)  # JSON string of features used
    target_days = Column(Integer, nullable=False, default=1)
    training_date = Column(DateTime(timezone=True), server_default=func.now())
    data_points = Column(Integer, nullable=False)
    metrics = Column(Text, nullable=False)  # JSON string of model metrics
    model_filename = Column(String(255), nullable=False)
    scaler_filename = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SocialPost(Base):
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(String(50), nullable=False, default="general")  # 'general', 'trade', 'analysis', 'news'
    symbol = Column(String(20), nullable=True)  # Associated stock symbol
    tags = Column(Text, nullable=True)  # JSON string of tags
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SocialLike(Base):
    __tablename__ = "social_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SocialComment(Base):
    __tablename__ = "social_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SocialFollow(Base):
    __tablename__ = "social_follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(String(100), nullable=False)
    following_id = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SocialShare(Base):
    __tablename__ = "social_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    post_id = Column(Integer, ForeignKey("social_posts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIOpponent(Base):
    __tablename__ = "ai_opponents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)  # The human user
    ai_user_id = Column(String(100), nullable=False)  # The AI's user ID
    strategy_type = Column(String(50), nullable=False)  # 'conservative', 'aggressive', 'technical', 'sentiment'
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

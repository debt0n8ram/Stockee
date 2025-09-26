import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os

from app.main import app
from app.db.database import get_db, Base
from app.db import models

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    """Create a test user."""
    return {
        "id": "test_user_123",
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def test_portfolio(db_session, test_user):
    """Create a test portfolio."""
    portfolio = models.Portfolio(
        user_id=test_user["id"],
        cash_balance=10000.00,
        total_value=10000.00,
        daily_change=0.00,
        daily_change_percent=0.00
    )
    db_session.add(portfolio)
    db_session.commit()
    db_session.refresh(portfolio)
    return portfolio

@pytest.fixture
def test_holding(db_session, test_portfolio):
    """Create a test holding."""
    holding = models.Holding(
        portfolio_id=test_portfolio.id,
        symbol="AAPL",
        quantity=10,
        average_price=150.00
    )
    db_session.add(holding)
    db_session.commit()
    db_session.refresh(holding)
    return holding

@pytest.fixture
def test_transaction(db_session, test_portfolio):
    """Create a test transaction."""
    transaction = models.Transaction(
        portfolio_id=test_portfolio.id,
        symbol="AAPL",
        transaction_type="buy",
        quantity=10,
        price=150.00,
        status="filled"
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction

@pytest.fixture
def test_asset(db_session):
    """Create a test asset."""
    asset = models.Asset(
        symbol="AAPL",
        name="Apple Inc.",
        asset_type="stock",
        exchange="NASDAQ",
        currency="USD"
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset

@pytest.fixture
def test_price_data(db_session, test_asset):
    """Create test price data."""
    price_data = models.PriceData(
        asset_id=test_asset.id,
        date="2024-01-01",
        open=150.00,
        high=155.00,
        low=149.00,
        close=154.00,
        volume=1000000
    )
    db_session.add(price_data)
    db_session.commit()
    db_session.refresh(price_data)
    return price_data

@pytest.fixture
def test_watchlist(db_session, test_user):
    """Create a test watchlist."""
    watchlist = models.Watchlist(
        user_id=test_user["id"],
        symbol="AAPL",
        alert_price=160.00
    )
    db_session.add(watchlist)
    db_session.commit()
    db_session.refresh(watchlist)
    return watchlist

@pytest.fixture
def test_alert(db_session, test_user):
    """Create a test alert."""
    alert = models.PriceAlert(
        user_id=test_user["id"],
        symbol="AAPL",
        alert_type="price_above",
        target_price=160.00,
        message="AAPL price alert",
        is_active=True
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert

@pytest.fixture
def test_ml_model(db_session, test_user):
    """Create a test ML model."""
    ml_model = models.MLModel(
        user_id=test_user["id"],
        symbol="AAPL",
        model_type="random_forest",
        features='["close", "volume", "rsi"]',
        target_days=1,
        data_points=1000,
        metrics='{"mse": 0.01, "r2": 0.95}',
        model_filename="test_model.joblib",
        scaler_filename="test_scaler.joblib",
        is_active=True
    )
    db_session.add(ml_model)
    db_session.commit()
    db_session.refresh(ml_model)
    return ml_model

@pytest.fixture
def test_social_post(db_session, test_user):
    """Create a test social post."""
    post = models.SocialPost(
        user_id=test_user["id"],
        content="Test post content",
        post_type="general",
        symbol="AAPL",
        tags='["test", "trading"]',
        likes_count=0,
        comments_count=0,
        shares_count=0,
        is_public=True
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post

@pytest.fixture
def test_social_like(db_session, test_user, test_social_post):
    """Create a test social like."""
    like = models.SocialLike(
        user_id=test_user["id"],
        post_id=test_social_post.id
    )
    db_session.add(like)
    db_session.commit()
    db_session.refresh(like)
    return like

@pytest.fixture
def test_social_comment(db_session, test_user, test_social_post):
    """Create a test social comment."""
    comment = models.SocialComment(
        user_id=test_user["id"],
        post_id=test_social_post.id,
        content="Test comment"
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment

@pytest.fixture
def test_social_follow(db_session, test_user):
    """Create a test social follow."""
    follow = models.SocialFollow(
        follower_id=test_user["id"],
        following_id="other_user_123"
    )
    db_session.add(follow)
    db_session.commit()
    db_session.refresh(follow)
    return follow

@pytest.fixture
def test_bank_transaction(db_session, test_user):
    """Create a test bank transaction."""
    transaction = models.BankTransaction(
        user_id=test_user["id"],
        transaction_type="deposit",
        amount=1000.00,
        description="Test deposit",
        balance_after=11000.00
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction

@pytest.fixture
def test_advanced_order(db_session, test_user):
    """Create a test advanced order."""
    order = models.AdvancedOrder(
        user_id=test_user["id"],
        symbol="AAPL",
        order_type="stop_loss",
        side="sell",
        quantity=10,
        stop_price=140.00,
        order_status="pending",
        message="Test stop loss order"
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order

@pytest.fixture
def test_news_article(db_session):
    """Create a test news article."""
    article = models.NewsArticle(
        title="Test News Article",
        content="This is a test news article content.",
        source="Test News",
        url="https://example.com/test-news",
        published_at="2024-01-01T12:00:00Z",
        sentiment_score=0.5,
        sentiment_label="neutral"
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article

@pytest.fixture
def test_technical_alert(db_session, test_user):
    """Create a test technical alert."""
    alert = models.TechnicalAlert(
        user_id=test_user["id"],
        symbol="AAPL",
        indicator_type="rsi_overbought",
        message="RSI overbought alert",
        is_active=True
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert

@pytest.fixture
def test_volume_alert(db_session, test_user):
    """Create a test volume alert."""
    alert = models.VolumeAlert(
        user_id=test_user["id"],
        symbol="AAPL",
        alert_type="volume_spike",
        volume_threshold=2.0,
        message="Volume spike alert",
        is_active=True
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert

@pytest.fixture
def test_news_alert(db_session, test_user):
    """Create a test news alert."""
    alert = models.NewsAlert(
        user_id=test_user["id"],
        symbol="AAPL",
        keywords="earnings,revenue,growth",
        message="News alert for AAPL",
        is_active=True
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert

@pytest.fixture
def test_alert_history(db_session, test_user):
    """Create a test alert history."""
    history = models.AlertHistory(
        user_id=test_user["id"],
        symbol="AAPL",
        alert_type="price_above",
        message="Price alert triggered",
        data='{"price": 160.00, "target": 160.00}'
    )
    db_session.add(history)
    db_session.commit()
    db_session.refresh(history)
    return history

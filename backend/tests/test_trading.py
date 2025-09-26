import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models

class TestTrading:
    """Test trading-related functionality."""
    
    def test_place_buy_order(self, client: TestClient, test_portfolio):
        """Test placing a buy order."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10,
                "order_type": "market",
                "price": 150.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["side"] == "buy"
        assert data["quantity"] == 10
    
    def test_place_sell_order(self, client: TestClient, test_portfolio, test_holding):
        """Test placing a sell order."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "sell",
                "quantity": 5,
                "order_type": "market",
                "price": 160.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["side"] == "sell"
        assert data["quantity"] == 5
    
    def test_place_limit_order(self, client: TestClient, test_portfolio):
        """Test placing a limit order."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "MSFT",
                "side": "buy",
                "quantity": 5,
                "order_type": "limit",
                "price": 290.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["order_type"] == "limit"
        assert data["price"] == 290.00
    
    def test_place_stop_order(self, client: TestClient, test_portfolio, test_holding):
        """Test placing a stop order."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "sell",
                "quantity": 10,
                "order_type": "stop",
                "price": 140.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["order_type"] == "stop"
        assert data["price"] == 140.00
    
    def test_get_open_orders(self, client: TestClient, test_portfolio):
        """Test getting open orders."""
        response = client.get(f"/api/trading/portfolio/{test_portfolio.id}/orders/open")
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
    
    def test_get_order_history(self, client: TestClient, test_portfolio):
        """Test getting order history."""
        response = client.get(f"/api/trading/portfolio/{test_portfolio.id}/orders/history")
        assert response.status_code == 200
        data = response.json()
        assert "orders" in data
    
    def test_cancel_order(self, client: TestClient, test_transaction):
        """Test canceling an order."""
        response = client.post(f"/api/trading/orders/{test_transaction.id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Order cancelled successfully"
    
    def test_get_order_status(self, client: TestClient, test_transaction):
        """Test getting order status."""
        response = client.get(f"/api/trading/orders/{test_transaction.id}/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "order_id" in data
    
    def test_place_insufficient_funds_order(self, client: TestClient, test_portfolio):
        """Test placing an order with insufficient funds."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "GOOGL",
                "side": "buy",
                "quantity": 100,  # Very large quantity
                "order_type": "market",
                "price": 2500.00
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "insufficient funds" in data["detail"].lower()
    
    def test_place_insufficient_shares_order(self, client: TestClient, test_portfolio, test_holding):
        """Test placing a sell order with insufficient shares."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "sell",
                "quantity": 100,  # More than available
                "order_type": "market",
                "price": 160.00
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "insufficient shares" in data["detail"].lower()
    
    def test_place_invalid_symbol_order(self, client: TestClient, test_portfolio):
        """Test placing an order with invalid symbol."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "INVALID",
                "side": "buy",
                "quantity": 10,
                "order_type": "market",
                "price": 100.00
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "invalid symbol" in data["detail"].lower()
    
    def test_place_invalid_order_type(self, client: TestClient, test_portfolio):
        """Test placing an order with invalid order type."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10,
                "order_type": "invalid",
                "price": 150.00
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_place_negative_quantity_order(self, client: TestClient, test_portfolio):
        """Test placing an order with negative quantity."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "buy",
                "quantity": -10,  # Negative quantity
                "order_type": "market",
                "price": 150.00
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_place_zero_quantity_order(self, client: TestClient, test_portfolio):
        """Test placing an order with zero quantity."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 0,  # Zero quantity
                "order_type": "market",
                "price": 150.00
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_place_negative_price_order(self, client: TestClient, test_portfolio):
        """Test placing an order with negative price."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10,
                "order_type": "market",
                "price": -150.00  # Negative price
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_place_zero_price_order(self, client: TestClient, test_portfolio):
        """Test placing an order with zero price."""
        response = client.post(
            "/api/trading/orders",
            json={
                "portfolio_id": test_portfolio.id,
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10,
                "order_type": "market",
                "price": 0.00  # Zero price
            }
        )
        assert response.status_code == 422  # Validation error

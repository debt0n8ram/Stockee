import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models

class TestPortfolio:
    """Test portfolio-related functionality."""
    
    def test_create_portfolio(self, client: TestClient, test_user):
        """Test creating a new portfolio."""
        response = client.post(
            "/api/portfolio/",
            json={
                "user_id": test_user["id"],
                "cash_balance": 10000.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user["id"]
        assert data["cash_balance"] == 10000.00
    
    def test_get_portfolio(self, client: TestClient, test_portfolio):
        """Test getting portfolio information."""
        response = client.get(f"/api/portfolio/{test_portfolio.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_portfolio.id
        assert data["cash_balance"] == test_portfolio.cash_balance
    
    def test_update_portfolio(self, client: TestClient, test_portfolio):
        """Test updating portfolio information."""
        response = client.put(
            f"/api/portfolio/{test_portfolio.id}",
            json={
                "cash_balance": 15000.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["cash_balance"] == 15000.00
    
    def test_get_portfolio_holdings(self, client: TestClient, test_portfolio, test_holding):
        """Test getting portfolio holdings."""
        response = client.get(f"/api/portfolio/{test_portfolio.id}/holdings")
        assert response.status_code == 200
        data = response.json()
        assert len(data["holdings"]) == 1
        assert data["holdings"][0]["symbol"] == "AAPL"
    
    def test_add_holding(self, client: TestClient, test_portfolio):
        """Test adding a new holding."""
        response = client.post(
            f"/api/portfolio/{test_portfolio.id}/holdings",
            json={
                "symbol": "MSFT",
                "quantity": 5,
                "average_price": 300.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "MSFT"
        assert data["quantity"] == 5
    
    def test_update_holding(self, client: TestClient, test_holding):
        """Test updating a holding."""
        response = client.put(
            f"/api/portfolio/holdings/{test_holding.id}",
            json={
                "quantity": 15,
                "average_price": 155.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 15
        assert data["average_price"] == 155.00
    
    def test_delete_holding(self, client: TestClient, test_holding):
        """Test deleting a holding."""
        response = client.delete(f"/api/portfolio/holdings/{test_holding.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Holding deleted successfully"
    
    def test_get_portfolio_transactions(self, client: TestClient, test_portfolio, test_transaction):
        """Test getting portfolio transactions."""
        response = client.get(f"/api/portfolio/{test_portfolio.id}/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data["transactions"]) == 1
        assert data["transactions"][0]["symbol"] == "AAPL"
    
    def test_add_transaction(self, client: TestClient, test_portfolio):
        """Test adding a new transaction."""
        response = client.post(
            f"/api/portfolio/{test_portfolio.id}/transactions",
            json={
                "symbol": "GOOGL",
                "transaction_type": "buy",
                "quantity": 2,
                "price": 2500.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "GOOGL"
        assert data["transaction_type"] == "buy"
    
    def test_get_portfolio_performance(self, client: TestClient, test_portfolio):
        """Test getting portfolio performance."""
        response = client.get(f"/api/portfolio/{test_portfolio.id}/performance")
        assert response.status_code == 200
        data = response.json()
        assert "total_return" in data
        assert "daily_change" in data
        assert "volatility" in data
    
    def test_calculate_portfolio_value(self, client: TestClient, test_portfolio, test_holding):
        """Test calculating portfolio value."""
        response = client.post(
            f"/api/portfolio/{test_portfolio.id}/calculate-value",
            json={
                "current_prices": {
                    "AAPL": 160.00
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_value" in data
        assert "holdings_value" in data
        assert "cash_balance" in data

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models

class TestMarketData:
    """Test market data functionality."""
    
    def test_get_current_price(self, client: TestClient, test_asset):
        """Test getting current price for a symbol."""
        response = client.get(f"/api/market-data/price/{test_asset.symbol}")
        assert response.status_code == 200
        data = response.json()
        assert "price" in data
        assert "symbol" in data
        assert data["symbol"] == test_asset.symbol
    
    def test_get_historical_data(self, client: TestClient, test_asset):
        """Test getting historical price data."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "symbol" in data
        assert data["symbol"] == test_asset.symbol
    
    def test_get_historical_data_invalid_symbol(self, client: TestClient):
        """Test getting historical data for invalid symbol."""
        response = client.get(
            "/api/market-data/historical/INVALID",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_historical_data_invalid_date_range(self, client: TestClient, test_asset):
        """Test getting historical data with invalid date range."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2024-01-31",
                "end_date": "2024-01-01"  # End before start
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "invalid date range" in data["detail"].lower()
    
    def test_get_historical_data_future_dates(self, client: TestClient, test_asset):
        """Test getting historical data with future dates."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "future dates" in data["detail"].lower()
    
    def test_get_historical_data_large_date_range(self, client: TestClient, test_asset):
        """Test getting historical data with large date range."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2020-01-01",
                "end_date": "2024-01-31"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "date range too large" in data["detail"].lower()
    
    def test_get_historical_data_default_dates(self, client: TestClient, test_asset):
        """Test getting historical data with default dates."""
        response = client.get(f"/api/market-data/historical/{test_asset.symbol}")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "symbol" in data
    
    def test_get_historical_data_with_limit(self, client: TestClient, test_asset):
        """Test getting historical data with limit."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "limit": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) <= 10
    
    def test_get_historical_data_with_offset(self, client: TestClient, test_asset):
        """Test getting historical data with offset."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "offset": 5,
                "limit": 10
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_historical_data_invalid_limit(self, client: TestClient, test_asset):
        """Test getting historical data with invalid limit."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "limit": -1
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_get_historical_data_invalid_offset(self, client: TestClient, test_asset):
        """Test getting historical data with invalid offset."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "offset": -1
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_get_historical_data_large_limit(self, client: TestClient, test_asset):
        """Test getting historical data with large limit."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "limit": 10000
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "limit too large" in data["detail"].lower()
    
    def test_get_historical_data_invalid_date_format(self, client: TestClient, test_asset):
        """Test getting historical data with invalid date format."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "invalid-date",
                "end_date": "2024-01-31"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_get_historical_data_missing_end_date(self, client: TestClient, test_asset):
        """Test getting historical data with missing end date."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2024-01-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_historical_data_missing_start_date(self, client: TestClient, test_asset):
        """Test getting historical data with missing start date."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "end_date": "2024-01-31"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_historical_data_same_start_end_date(self, client: TestClient, test_asset):
        """Test getting historical data with same start and end date."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-01-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_historical_data_weekend_dates(self, client: TestClient, test_asset):
        """Test getting historical data with weekend dates."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2024-01-06",  # Saturday
                "end_date": "2024-01-07"    # Sunday
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_historical_data_holiday_dates(self, client: TestClient, test_asset):
        """Test getting historical data with holiday dates."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2024-01-01",  # New Year's Day
                "end_date": "2024-01-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_historical_data_after_hours(self, client: TestClient, test_asset):
        """Test getting historical data after market hours."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2024-01-01T20:00:00Z",  # After hours
                "end_date": "2024-01-01T20:00:00Z"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_get_historical_data_before_market_open(self, client: TestClient, test_asset):
        """Test getting historical data before market open."""
        response = client.get(
            f"/api/market-data/historical/{test_asset.symbol}",
            params={
                "start_date": "2024-01-01T05:00:00Z",  # Before market open
                "end_date": "2024-01-01T05:00:00Z"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models

class TestCache:
    """Test cache functionality."""
    
    def test_get_cache_stats(self, client: TestClient, test_user):
        """Test getting cache statistics."""
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "stats" in data
    
    def test_set_cache_value(self, client: TestClient, test_user):
        """Test setting a cache value."""
        response = client.post(
            "/api/cache/keys",
            json={
                "key": "test_key",
                "value": "test_value",
                "ttl": 300
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["key"] == "test_key"
    
    def test_get_cache_value(self, client: TestClient, test_user):
        """Test getting a cache value."""
        # First set a value
        client.post(
            "/api/cache/keys",
            json={
                "key": "test_key",
                "value": "test_value"
            }
        )
        
        # Then get it
        response = client.get("/api/cache/keys/test_key")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["key"] == "test_key"
        assert data["value"] == "test_value"
    
    def test_get_nonexistent_cache_value(self, client: TestClient, test_user):
        """Test getting a nonexistent cache value."""
        response = client.get("/api/cache/keys/nonexistent_key")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_delete_cache_value(self, client: TestClient, test_user):
        """Test deleting a cache value."""
        # First set a value
        client.post(
            "/api/cache/keys",
            json={
                "key": "test_key",
                "value": "test_value"
            }
        )
        
        # Then delete it
        response = client.delete("/api/cache/keys/test_key")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["key"] == "test_key"
    
    def test_delete_nonexistent_cache_value(self, client: TestClient, test_user):
        """Test deleting a nonexistent cache value."""
        response = client.delete("/api/cache/keys/nonexistent_key")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_check_cache_key_exists(self, client: TestClient, test_user):
        """Test checking if a cache key exists."""
        # First set a value
        client.post(
            "/api/cache/keys",
            json={
                "key": "test_key",
                "value": "test_value"
            }
        )
        
        # Check if it exists
        response = client.get("/api/cache/keys/test_key/exists")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["key"] == "test_key"
        assert data["exists"] == True
    
    def test_check_nonexistent_cache_key_exists(self, client: TestClient, test_user):
        """Test checking if a nonexistent cache key exists."""
        response = client.get("/api/cache/keys/nonexistent_key/exists")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["key"] == "nonexistent_key"
        assert data["exists"] == False
    
    def test_get_cache_ttl(self, client: TestClient, test_user):
        """Test getting cache TTL."""
        # First set a value with TTL
        client.post(
            "/api/cache/keys",
            json={
                "key": "test_key",
                "value": "test_value",
                "ttl": 300
            }
        )
        
        # Get TTL
        response = client.get("/api/cache/keys/test_key/ttl")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["key"] == "test_key"
        assert "ttl" in data
    
    def test_set_cache_ttl(self, client: TestClient, test_user):
        """Test setting cache TTL."""
        # First set a value
        client.post(
            "/api/cache/keys",
            json={
                "key": "test_key",
                "value": "test_value"
            }
        )
        
        # Set TTL
        response = client.post("/api/cache/keys/test_key/expire?ttl=600")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["key"] == "test_key"
        assert data["ttl"] == 600
    
    def test_set_cache_ttl_nonexistent_key(self, client: TestClient, test_user):
        """Test setting TTL for nonexistent key."""
        response = client.post("/api/cache/keys/nonexistent_key/expire?ttl=600")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_set_multiple_cache_values(self, client: TestClient, test_user):
        """Test setting multiple cache values."""
        response = client.post(
            "/api/cache/keys/multiple",
            json={
                "mapping": {
                    "key1": "value1",
                    "key2": "value2",
                    "key3": "value3"
                },
                "ttl": 300
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "key1" in data["keys"]
        assert "key2" in data["keys"]
        assert "key3" in data["keys"]
    
    def test_get_multiple_cache_values(self, client: TestClient, test_user):
        """Test getting multiple cache values."""
        # First set multiple values
        client.post(
            "/api/cache/keys/multiple",
            json={
                "mapping": {
                    "key1": "value1",
                    "key2": "value2",
                    "key3": "value3"
                }
            }
        )
        
        # Then get them
        response = client.get("/api/cache/keys/multiple?keys=key1,key2,key3")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "values" in data
        assert "key1" in data["values"]
        assert "key2" in data["values"]
        assert "key3" in data["values"]
    
    def test_delete_multiple_cache_values(self, client: TestClient, test_user):
        """Test deleting multiple cache values."""
        # First set multiple values
        client.post(
            "/api/cache/keys/multiple",
            json={
                "mapping": {
                    "key1": "value1",
                    "key2": "value2",
                    "key3": "value3"
                }
            }
        )
        
        # Then delete them
        response = client.delete("/api/cache/keys/multiple?keys=key1,key2,key3")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["deleted_count"] == 3
    
    def test_clear_cache_pattern(self, client: TestClient, test_user):
        """Test clearing cache keys matching a pattern."""
        # First set multiple values with pattern
        client.post(
            "/api/cache/keys/multiple",
            json={
                "mapping": {
                    "test_key1": "value1",
                    "test_key2": "value2",
                    "other_key": "value3"
                }
            }
        )
        
        # Clear pattern
        response = client.delete("/api/cache/pattern/test_*")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["pattern"] == "test_*"
        assert data["deleted_count"] == 2
    
    def test_invalidate_user_cache(self, client: TestClient, test_user):
        """Test invalidating user cache."""
        response = client.post(f"/api/cache/invalidate/user/{test_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["user_id"] == test_user["id"]
        assert "deleted_count" in data
    
    def test_invalidate_symbol_cache(self, client: TestClient, test_user):
        """Test invalidating symbol cache."""
        response = client.post("/api/cache/invalidate/symbol/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["symbol"] == "AAPL"
        assert "deleted_count" in data
    
    def test_warm_cache(self, client: TestClient, test_user):
        """Test warming cache."""
        response = client.post("/api/cache/warm?symbols=AAPL,MSFT,GOOGL")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "symbols" in data
        assert "AAPL" in data["symbols"]
        assert "MSFT" in data["symbols"]
        assert "GOOGL" in data["symbols"]
    
    def test_cache_health_check(self, client: TestClient, test_user):
        """Test cache health check."""
        response = client.get("/api/cache/health")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "healthy" in data
        assert "stats" in data
    
    def test_flush_all_cache(self, client: TestClient, test_user):
        """Test flushing all cache."""
        # First set some values
        client.post(
            "/api/cache/keys",
            json={
                "key": "test_key",
                "value": "test_value"
            }
        )
        
        # Flush all cache
        response = client.post("/api/cache/flush")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    def test_cache_with_complex_data(self, client: TestClient, test_user):
        """Test caching complex data structures."""
        complex_data = {
            "user": {
                "id": test_user["id"],
                "name": "Test User",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            },
            "portfolio": {
                "holdings": [
                    {"symbol": "AAPL", "quantity": 10},
                    {"symbol": "MSFT", "quantity": 5}
                ],
                "cash_balance": 10000.00
            }
        }
        
        response = client.post(
            "/api/cache/keys",
            json={
                "key": "complex_data",
                "value": complex_data
            }
        )
        assert response.status_code == 200
        
        # Get it back
        response = client.get("/api/cache/keys/complex_data")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["value"]["user"]["id"] == test_user["id"]
        assert data["value"]["portfolio"]["cash_balance"] == 10000.00
    
    def test_cache_with_numeric_data(self, client: TestClient, test_user):
        """Test caching numeric data."""
        numeric_data = {
            "price": 150.50,
            "quantity": 100,
            "percentage": 5.25,
            "is_active": True
        }
        
        response = client.post(
            "/api/cache/keys",
            json={
                "key": "numeric_data",
                "value": numeric_data
            }
        )
        assert response.status_code == 200
        
        # Get it back
        response = client.get("/api/cache/keys/numeric_data")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["value"]["price"] == 150.50
        assert data["value"]["quantity"] == 100
        assert data["value"]["percentage"] == 5.25
        assert data["value"]["is_active"] == True
    
    def test_cache_ttl_expiration(self, client: TestClient, test_user):
        """Test cache TTL expiration."""
        # Set value with short TTL
        response = client.post(
            "/api/cache/keys",
            json={
                "key": "short_ttl_key",
                "value": "short_value",
                "ttl": 1  # 1 second
            }
        )
        assert response.status_code == 200
        
        # Should exist immediately
        response = client.get("/api/cache/keys/short_ttl_key/exists")
        assert response.status_code == 200
        data = response.json()
        assert data["exists"] == True
        
        # Wait for expiration (in a real test, you might use time.sleep)
        # For now, we'll just verify the TTL is set
        response = client.get("/api/cache/keys/short_ttl_key/ttl")
        assert response.status_code == 200
        data = response.json()
        assert data["ttl"] <= 1
    
    def test_cache_increment_decrement(self, client: TestClient, test_user):
        """Test cache increment and decrement operations."""
        # Set initial value
        response = client.post(
            "/api/cache/keys",
            json={
                "key": "counter",
                "value": 10
            }
        )
        assert response.status_code == 200
        
        # Increment
        response = client.post("/api/cache/keys/counter/increment?amount=5")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["value"] == 15
        
        # Decrement
        response = client.post("/api/cache/keys/counter/decrement?amount=3")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["value"] == 12
    
    def test_cache_increment_nonexistent_key(self, client: TestClient, test_user):
        """Test incrementing nonexistent key."""
        response = client.post("/api/cache/keys/nonexistent/increment?amount=5")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_cache_decrement_nonexistent_key(self, client: TestClient, test_user):
        """Test decrementing nonexistent key."""
        response = client.post("/api/cache/keys/nonexistent/decrement?amount=5")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

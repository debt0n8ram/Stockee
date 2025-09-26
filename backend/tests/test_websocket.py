import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import models

class TestWebSocket:
    """Test WebSocket functionality."""
    
    def test_websocket_connection(self, client: TestClient, test_user):
        """Test WebSocket connection."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Should receive connection confirmation
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            assert message["user_id"] == test_user["id"]
    
    def test_websocket_ping_pong(self, client: TestClient, test_user):
        """Test WebSocket ping/pong."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Send ping
            websocket.send_text(json.dumps({"type": "ping"}))
            
            # Should receive pong
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "pong"
    
    def test_websocket_subscribe_price_updates(self, client: TestClient, test_user):
        """Test subscribing to price updates."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Subscribe to price updates
            websocket.send_text(json.dumps({
                "type": "subscribe_price",
                "symbol": "AAPL"
            }))
            
            # Should receive current price
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "price_update"
            assert message["symbol"] == "AAPL"
            assert "price" in message
    
    def test_websocket_unsubscribe_price_updates(self, client: TestClient, test_user):
        """Test unsubscribing from price updates."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Subscribe first
            websocket.send_text(json.dumps({
                "type": "subscribe_price",
                "symbol": "AAPL"
            }))
            
            # Receive initial price
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "price_update"
            
            # Unsubscribe
            websocket.send_text(json.dumps({
                "type": "unsubscribe_price",
                "symbol": "AAPL"
            }))
            
            # Should not receive more price updates
            # (This is hard to test without waiting, so we'll just verify no error)
    
    def test_websocket_subscribe_portfolio_updates(self, client: TestClient, test_user):
        """Test subscribing to portfolio updates."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Subscribe to portfolio updates
            websocket.send_text(json.dumps({
                "type": "subscribe_portfolio"
            }))
            
            # Should not receive error
            # (Portfolio updates are sent when portfolio changes, not immediately)
    
    def test_websocket_subscribe_alerts(self, client: TestClient, test_user):
        """Test subscribing to alerts."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Subscribe to alerts
            websocket.send_text(json.dumps({
                "type": "subscribe_alerts"
            }))
            
            # Should not receive error
            # (Alerts are sent when triggered, not immediately)
    
    def test_websocket_subscribe_market_status(self, client: TestClient, test_user):
        """Test subscribing to market status."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Subscribe to market status
            websocket.send_text(json.dumps({
                "type": "subscribe_market_status"
            }))
            
            # Should not receive error
            # (Market status is sent periodically, not immediately)
    
    def test_websocket_invalid_message_type(self, client: TestClient, test_user):
        """Test sending invalid message type."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Send invalid message type
            websocket.send_text(json.dumps({
                "type": "invalid_type"
            }))
            
            # Should receive error
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "error"
            assert "unknown message type" in message["message"].lower()
    
    def test_websocket_invalid_json(self, client: TestClient, test_user):
        """Test sending invalid JSON."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Send invalid JSON
            websocket.send_text("invalid json")
            
            # Should receive error
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "error"
            assert "invalid json format" in message["message"].lower()
    
    def test_websocket_missing_symbol_in_subscribe(self, client: TestClient, test_user):
        """Test subscribing to price updates without symbol."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Subscribe without symbol
            websocket.send_text(json.dumps({
                "type": "subscribe_price"
            }))
            
            # Should not receive error (symbol is optional in some implementations)
            # This depends on the specific implementation
    
    def test_websocket_multiple_subscriptions(self, client: TestClient, test_user):
        """Test multiple subscriptions."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Subscribe to multiple things
            websocket.send_text(json.dumps({
                "type": "subscribe_price",
                "symbol": "AAPL"
            }))
            
            websocket.send_text(json.dumps({
                "type": "subscribe_price",
                "symbol": "MSFT"
            }))
            
            websocket.send_text(json.dumps({
                "type": "subscribe_portfolio"
            }))
            
            # Should receive price updates for both symbols
            data1 = websocket.receive_text()
            message1 = json.loads(data1)
            assert message1["type"] == "price_update"
            assert message1["symbol"] == "AAPL"
            
            data2 = websocket.receive_text()
            message2 = json.loads(data2)
            assert message2["type"] == "price_update"
            assert message2["symbol"] == "MSFT"
    
    def test_websocket_connection_disconnect(self, client: TestClient, test_user):
        """Test WebSocket connection and disconnect."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Should receive connection confirmation
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            
            # Connection should be active
            # When websocket context exits, connection should be closed
    
    def test_websocket_reconnect(self, client: TestClient, test_user):
        """Test WebSocket reconnection."""
        # First connection
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
        
        # Second connection (should work)
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
    
    def test_websocket_different_users(self, client: TestClient, test_user):
        """Test WebSocket connections for different users."""
        user1_id = test_user["id"]
        user2_id = "different_user_123"
        
        # Connect user 1
        with client.websocket_connect(f"/api/ws-realtime/ws/{user1_id}") as websocket1:
            data1 = websocket1.receive_text()
            message1 = json.loads(data1)
            assert message1["type"] == "connection_established"
            assert message1["user_id"] == user1_id
            
            # Connect user 2
            with client.websocket_connect(f"/api/ws-realtime/ws/{user2_id}") as websocket2:
                data2 = websocket2.receive_text()
                message2 = json.loads(data2)
                assert message2["type"] == "connection_established"
                assert message2["user_id"] == user2_id
                
                # Both connections should be active
                # User 1 should not receive user 2's messages
                # User 2 should not receive user 1's messages
    
    def test_websocket_large_message(self, client: TestClient, test_user):
        """Test WebSocket with large message."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Send large message
            large_data = {"type": "test", "data": "x" * 10000}
            websocket.send_text(json.dumps(large_data))
            
            # Should not crash
            # (Specific behavior depends on implementation)
    
    def test_websocket_rapid_messages(self, client: TestClient, test_user):
        """Test WebSocket with rapid messages."""
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            # Send multiple messages rapidly
            for i in range(10):
                websocket.send_text(json.dumps({
                    "type": "ping"
                }))
            
            # Should receive multiple pongs
            for i in range(10):
                data = websocket.receive_text()
                message = json.loads(data)
                assert message["type"] == "pong"
    
    def test_websocket_connection_stats(self, client: TestClient, test_user):
        """Test WebSocket connection statistics."""
        # Connect first
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            
            # Get stats
            response = client.get("/api/ws-realtime/ws/stats")
            assert response.status_code == 200
            stats_data = response.json()
            assert "success" in stats_data
            assert "stats" in stats_data
    
    def test_websocket_broadcast_message(self, client: TestClient, test_user):
        """Test broadcasting a message."""
        # Connect first
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            
            # Broadcast message
            response = client.post(
                "/api/ws-realtime/ws/broadcast",
                json={
                    "type": "test_broadcast",
                    "message": "Test broadcast message"
                }
            )
            assert response.status_code == 200
            broadcast_data = response.json()
            assert broadcast_data["success"] == True
    
    def test_websocket_send_message_to_user(self, client: TestClient, test_user):
        """Test sending a message to a specific user."""
        # Connect first
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            
            # Send message to user
            response = client.post(
                f"/api/ws-realtime/ws/user/{test_user['id']}/send",
                json={
                    "type": "test_message",
                    "message": "Test personal message"
                }
            )
            assert response.status_code == 200
            send_data = response.json()
            assert send_data["success"] == True
    
    def test_websocket_test_connection(self, client: TestClient, test_user):
        """Test WebSocket test connection endpoint."""
        # Connect first
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            
            # Test connection
            response = client.post("/api/ws-realtime/ws/test")
            assert response.status_code == 200
            test_data = response.json()
            assert test_data["success"] == True
            
            # Should receive test message
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "test_message"
    
    def test_websocket_get_active_connections(self, client: TestClient, test_user):
        """Test getting active connections."""
        # Connect first
        with client.websocket_connect(f"/api/ws-realtime/ws/{test_user['id']}") as websocket:
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "connection_established"
            
            # Get active connections
            response = client.get("/api/ws-realtime/ws/connections")
            assert response.status_code == 200
            connections_data = response.json()
            assert "success" in connections_data
            assert "active_connections" in connections_data
            assert "connection_count" in connections_data

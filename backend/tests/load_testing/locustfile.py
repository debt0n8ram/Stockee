"""
Load testing with Locust for the Stockee application.
"""

import json
import random
import time
from locust import HttpUser, task, between, events
from locust.exception import StopUser
import websocket
import threading
import queue

class WebSocketUser:
    """WebSocket user for load testing."""
    
    def __init__(self, user_id: str, base_url: str):
        self.user_id = user_id
        self.base_url = base_url
        self.ws = None
        self.connected = False
        self.message_queue = queue.Queue()
        self.received_messages = 0
        self.sent_messages = 0
        
    def connect(self):
        """Connect to WebSocket."""
        try:
            ws_url = self.base_url.replace('http', 'ws') + f'/api/ws-realtime/ws/{self.user_id}'
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Start WebSocket in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            return self.connected
            
        except Exception as e:
            print(f"WebSocket connection error: {e}")
            return False
    
    def on_open(self, ws):
        """WebSocket connection opened."""
        self.connected = True
        print(f"WebSocket connected for user {self.user_id}")
    
    def on_message(self, ws, message):
        """WebSocket message received."""
        try:
            data = json.loads(message)
            self.received_messages += 1
            self.message_queue.put(data)
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
    
    def on_error(self, ws, error):
        """WebSocket error."""
        print(f"WebSocket error for user {self.user_id}: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed."""
        self.connected = False
        print(f"WebSocket closed for user {self.user_id}")
    
    def send_message(self, message):
        """Send WebSocket message."""
        if self.connected and self.ws:
            try:
                self.ws.send(json.dumps(message))
                self.sent_messages += 1
                return True
            except Exception as e:
                print(f"Error sending WebSocket message: {e}")
                return False
        return False
    
    def subscribe_to_price(self, symbol: str):
        """Subscribe to price updates."""
        return self.send_message({
            "type": "subscribe_price",
            "symbol": symbol
        })
    
    def subscribe_to_portfolio(self):
        """Subscribe to portfolio updates."""
        return self.send_message({
            "type": "subscribe_portfolio"
        })
    
    def subscribe_to_alerts(self):
        """Subscribe to alerts."""
        return self.send_message({
            "type": "subscribe_alerts"
        })
    
    def ping(self):
        """Send ping message."""
        return self.send_message({
            "type": "ping"
        })
    
    def disconnect(self):
        """Disconnect WebSocket."""
        if self.ws:
            self.ws.close()
        self.connected = False

class StockeeUser(HttpUser):
    """Main user class for load testing."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize user session."""
        self.user_id = f"load_test_user_{random.randint(1000, 9999)}"
        self.ws_user = None
        self.symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
        
        # Login or create user
        self.login()
        
        # Connect WebSocket
        self.connect_websocket()
    
    def on_stop(self):
        """Clean up user session."""
        if self.ws_user:
            self.ws_user.disconnect()
    
    def login(self):
        """Login or create user."""
        try:
            # Try to login first
            response = self.client.post("/api/auth/login", json={
                "username": self.user_id,
                "password": "test_password"
            })
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            else:
                # Create new user
                response = self.client.post("/api/auth/register", json={
                    "username": self.user_id,
                    "email": f"{self.user_id}@test.com",
                    "password": "test_password"
                })
                
                if response.status_code == 200:
                    self.token = response.json()["access_token"]
                    self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                else:
                    raise Exception("Failed to create user")
                    
        except Exception as e:
            print(f"Login error for user {self.user_id}: {e}")
            raise StopUser()
    
    def connect_websocket(self):
        """Connect to WebSocket."""
        try:
            self.ws_user = WebSocketUser(self.user_id, self.client.base_url)
            if not self.ws_user.connect():
                print(f"Failed to connect WebSocket for user {self.user_id}")
        except Exception as e:
            print(f"WebSocket connection error for user {self.user_id}: {e}")
    
    @task(3)
    def get_portfolio(self):
        """Get portfolio information."""
        with self.client.get("/api/portfolio/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Portfolio request failed: {response.status_code}")
    
    @task(2)
    def get_market_data(self):
        """Get market data."""
        symbol = random.choice(self.symbols)
        with self.client.get(f"/api/market-data/price/{symbol}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Market data request failed: {response.status_code}")
    
    @task(2)
    def get_historical_data(self):
        """Get historical data."""
        symbol = random.choice(self.symbols)
        with self.client.get(f"/api/market-data/historical/{symbol}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Historical data request failed: {response.status_code}")
    
    @task(1)
    def place_order(self):
        """Place a test order."""
        symbol = random.choice(self.symbols)
        order_data = {
            "symbol": symbol,
            "side": random.choice(["buy", "sell"]),
            "quantity": random.randint(1, 10),
            "order_type": "market",
            "price": random.uniform(100, 500)
        }
        
        with self.client.post("/api/trading/orders", json=order_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Order placement failed: {response.status_code}")
    
    @task(1)
    def get_analytics(self):
        """Get analytics data."""
        with self.client.get("/api/analytics/portfolio/performance", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Analytics request failed: {response.status_code}")
    
    @task(1)
    def get_ai_insights(self):
        """Get AI insights."""
        symbol = random.choice(self.symbols)
        with self.client.get(f"/api/ai/insights/{symbol}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"AI insights request failed: {response.status_code}")
    
    @task(1)
    def get_technical_indicators(self):
        """Get technical indicators."""
        symbol = random.choice(self.symbols)
        with self.client.get(f"/api/technical-analysis/indicators/{symbol}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Technical indicators request failed: {response.status_code}")
    
    @task(1)
    def get_news(self):
        """Get news data."""
        with self.client.get("/api/news/market", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"News request failed: {response.status_code}")
    
    @task(1)
    def get_watchlist(self):
        """Get watchlist."""
        with self.client.get("/api/watchlist/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Watchlist request failed: {response.status_code}")
    
    @task(1)
    def get_social_feed(self):
        """Get social feed."""
        with self.client.get("/api/social-features/feed", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Social feed request failed: {response.status_code}")
    
    @task(1)
    def get_cache_stats(self):
        """Get cache statistics."""
        with self.client.get("/api/cache/stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Cache stats request failed: {response.status_code}")
    
    @task(1)
    def get_performance_metrics(self):
        """Get performance metrics."""
        with self.client.get("/api/performance-monitoring/summary", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Performance metrics request failed: {response.status_code}")
    
    @task(2)
    def websocket_subscribe_price(self):
        """Subscribe to price updates via WebSocket."""
        if self.ws_user and self.ws_user.connected:
            symbol = random.choice(self.symbols)
            if self.ws_user.subscribe_to_price(symbol):
                time.sleep(0.1)  # Wait for subscription
            else:
                print(f"Failed to subscribe to price updates for {symbol}")
    
    @task(1)
    def websocket_subscribe_portfolio(self):
        """Subscribe to portfolio updates via WebSocket."""
        if self.ws_user and self.ws_user.connected:
            if not self.ws_user.subscribe_to_portfolio():
                print("Failed to subscribe to portfolio updates")
    
    @task(1)
    def websocket_subscribe_alerts(self):
        """Subscribe to alerts via WebSocket."""
        if self.ws_user and self.ws_user.connected:
            if not self.ws_user.subscribe_to_alerts():
                print("Failed to subscribe to alerts")
    
    @task(1)
    def websocket_ping(self):
        """Send ping via WebSocket."""
        if self.ws_user and self.ws_user.connected:
            if not self.ws_user.ping():
                print("Failed to send ping")

class WebSocketOnlyUser(HttpUser):
    """User class for WebSocket-only load testing."""
    
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        """Initialize WebSocket-only user."""
        self.user_id = f"ws_user_{random.randint(1000, 9999)}"
        self.ws_user = None
        self.symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        
        # Connect WebSocket
        self.connect_websocket()
    
    def on_stop(self):
        """Clean up WebSocket connection."""
        if self.ws_user:
            self.ws_user.disconnect()
    
    def connect_websocket(self):
        """Connect to WebSocket."""
        try:
            self.ws_user = WebSocketUser(self.user_id, self.client.base_url)
            if not self.ws_user.connect():
                print(f"Failed to connect WebSocket for user {self.user_id}")
                raise StopUser()
        except Exception as e:
            print(f"WebSocket connection error for user {self.user_id}: {e}")
            raise StopUser()
    
    @task(5)
    def websocket_subscribe_price(self):
        """Subscribe to price updates."""
        if self.ws_user and self.ws_user.connected:
            symbol = random.choice(self.symbols)
            self.ws_user.subscribe_to_price(symbol)
    
    @task(2)
    def websocket_ping(self):
        """Send ping."""
        if self.ws_user and self.ws_user.connected:
            self.ws_user.ping()
    
    @task(1)
    def websocket_subscribe_portfolio(self):
        """Subscribe to portfolio updates."""
        if self.ws_user and self.ws_user.connected:
            self.ws_user.subscribe_to_portfolio()

class CacheLoadUser(HttpUser):
    """User class for cache load testing."""
    
    wait_time = between(0.1, 0.3)
    
    def on_start(self):
        """Initialize cache load user."""
        self.user_id = f"cache_user_{random.randint(1000, 9999)}"
        self.symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "INTC"]
        
        # Login
        self.login()
    
    def login(self):
        """Login user."""
        try:
            response = self.client.post("/api/auth/login", json={
                "username": self.user_id,
                "password": "test_password"
            })
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            else:
                # Create new user
                response = self.client.post("/api/auth/register", json={
                    "username": self.user_id,
                    "email": f"{self.user_id}@test.com",
                    "password": "test_password"
                })
                
                if response.status_code == 200:
                    self.token = response.json()["access_token"]
                    self.client.headers.update({"Authorization": f"Bearer {self.token}"})
                else:
                    raise Exception("Failed to create user")
                    
        except Exception as e:
            print(f"Login error for user {self.user_id}: {e}")
            raise StopUser()
    
    @task(10)
    def get_cached_market_data(self):
        """Get cached market data."""
        symbol = random.choice(self.symbols)
        with self.client.get(f"/api/market-data/price/{symbol}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Cached market data request failed: {response.status_code}")
    
    @task(5)
    def get_cached_historical_data(self):
        """Get cached historical data."""
        symbol = random.choice(self.symbols)
        with self.client.get(f"/api/market-data/historical/{symbol}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Cached historical data request failed: {response.status_code}")
    
    @task(3)
    def get_cached_portfolio(self):
        """Get cached portfolio."""
        with self.client.get("/api/portfolio/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Cached portfolio request failed: {response.status_code}")
    
    @task(2)
    def get_cache_stats(self):
        """Get cache statistics."""
        with self.client.get("/api/cache/stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Cache stats request failed: {response.status_code}")
    
    @task(1)
    def set_cache_value(self):
        """Set cache value."""
        key = f"test_key_{random.randint(1000, 9999)}"
        value = f"test_value_{random.randint(1000, 9999)}"
        
        with self.client.post("/api/cache/keys", json={
            "key": key,
            "value": value,
            "ttl": 300
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Set cache value failed: {response.status_code}")
    
    @task(1)
    def get_cache_value(self):
        """Get cache value."""
        key = f"test_key_{random.randint(1000, 9999)}"
        
        with self.client.get(f"/api/cache/keys/{key}", catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 is expected for random keys
                response.success()
            else:
                response.failure(f"Get cache value failed: {response.status_code}")

# Event handlers
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Handle request events."""
    if exception:
        print(f"Request failed: {name} - {exception}")
    else:
        print(f"Request completed: {name} - {response_time}ms")

@events.user_error.add_listener
def on_user_error(user_instance, exception, tb, **kwargs):
    """Handle user errors."""
    print(f"User error: {exception}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Handle test start."""
    print("Load test started")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Handle test stop."""
    print("Load test stopped")

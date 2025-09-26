# Stockee API Documentation

## Overview

The Stockee API is a comprehensive REST API for a realistic stock market and Bitcoin trading application. It provides endpoints for portfolio management, trading operations, market data, AI predictions, and real-time features.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Rate Limiting

- **Alpha Vantage**: 5 requests per minute, 500 requests per day
- **Polygon.io**: 5 requests per minute
- **News API**: 1000 requests per day
- **General API**: 100 requests per minute per user

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2023-10-26T10:30:00Z"
}
```

## Response Format

All successful responses include:

```json
{
  "data": { ... },
  "message": "Success message",
  "timestamp": "2023-10-26T10:30:00Z"
}
```

---

## Authentication Endpoints

### POST /auth/register

Register a new user.

**Request Body:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "data": {
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "created_at": "2023-10-26T10:30:00Z"
    },
    "token": "jwt_token"
  },
  "message": "User registered successfully"
}
```

### POST /auth/login

Login with username and password.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "data": {
    "user": {
      "id": "string",
      "username": "string",
      "email": "string"
    },
    "token": "jwt_token"
  },
  "message": "Login successful"
}
```

---

## Portfolio Endpoints

### GET /portfolio

Get user's portfolio summary.

**Response:**

```json
{
  "data": {
    "id": "string",
    "user_id": "string",
    "cash_balance": 10000.00,
    "total_value": 15000.00,
    "daily_change": 250.00,
    "daily_change_percent": 1.69,
    "holdings": [
      {
        "symbol": "AAPL",
        "quantity": 10,
        "average_price": 150.00,
        "current_price": 170.00,
        "value": 1700.00,
        "change": 200.00,
        "change_percent": 13.33
      }
    ],
    "transactions": []
  }
}
```

### GET /portfolio/holdings

Get detailed holdings information.

**Response:**

```json
{
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "quantity": 10,
      "average_price": 150.00,
      "current_price": 170.00,
      "value": 1700.00,
      "change": 200.00,
      "change_percent": 13.33,
      "sector": "Technology",
      "last_updated": "2023-10-26T10:30:00Z"
    }
  ]
}
```

### GET /portfolio/transactions

Get transaction history.

**Query Parameters:**

- `limit` (optional): Number of transactions to return (default: 50)
- `offset` (optional): Number of transactions to skip (default: 0)
- `symbol` (optional): Filter by symbol

**Response:**

```json
{
  "data": [
    {
      "id": "string",
      "symbol": "AAPL",
      "side": "buy",
      "quantity": 10,
      "price": 150.00,
      "total": 1500.00,
      "timestamp": "2023-10-26T10:30:00Z",
      "status": "filled"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

---

## Trading Endpoints

### POST /trading/orders

Place a new order.

**Request Body:**

```json
{
  "symbol": "AAPL",
  "side": "buy",
  "quantity": 10,
  "order_type": "market",
  "limit_price": 150.00
}
```

**Response:**

```json
{
  "data": {
    "id": "string",
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 10,
    "price": 150.00,
    "total": 1500.00,
    "status": "pending",
    "timestamp": "2023-10-26T10:30:00Z"
  },
  "message": "Order placed successfully"
}
```

### GET /trading/orders

Get open orders.

**Response:**

```json
{
  "data": [
    {
      "id": "string",
      "symbol": "AAPL",
      "side": "buy",
      "quantity": 10,
      "price": 150.00,
      "status": "pending",
      "timestamp": "2023-10-26T10:30:00Z"
    }
  ]
}
```

### DELETE /trading/orders/{order_id}

Cancel an order.

**Response:**

```json
{
  "data": {
    "id": "string",
    "status": "cancelled"
  },
  "message": "Order cancelled successfully"
}
```

---

## Market Data Endpoints

### GET /market-data/stocks/{symbol}

Get stock information and current price.

**Response:**

```json
{
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "current_price": 170.00,
    "change": 2.50,
    "change_percent": 1.49,
    "volume": 75000000,
    "market_cap": 2800000000000,
    "sector": "Technology",
    "last_updated": "2023-10-26T10:30:00Z"
  }
}
```

### GET /market-data/stocks/{symbol}/historical

Get historical price data.

**Query Parameters:**

- `period` (optional): 1d, 5d, 1m, 3m, 6m, 1y, 2y, 5y (default: 1m)
- `interval` (optional): 1m, 5m, 15m, 30m, 1h, 1d (default: 1d)

**Response:**

```json
{
  "data": [
    {
      "timestamp": "2023-10-26T10:30:00Z",
      "open": 168.50,
      "high": 171.20,
      "low": 167.80,
      "close": 170.00,
      "volume": 75000000
    }
  ]
}
```

### GET /market-data/crypto/{symbol}

Get cryptocurrency information.

**Response:**

```json
{
  "data": {
    "symbol": "BTC",
    "name": "Bitcoin",
    "current_price": 32000.00,
    "change": 500.00,
    "change_percent": 1.59,
    "market_cap": 600000000000,
    "volume_24h": 15000000000,
    "last_updated": "2023-10-26T10:30:00Z"
  }
}
```

### GET /market-data/top-stocks

Get top performing stocks.

**Query Parameters:**

- `limit` (optional): Number of stocks to return (default: 20)
- `sort` (optional): change, change_percent, volume (default: change_percent)

**Response:**

```json
{
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "current_price": 170.00,
      "change": 2.50,
      "change_percent": 1.49,
      "volume": 75000000
    }
  ]
}
```

---

## AI Prediction Endpoints

### GET /ai/predictions/{symbol}

Get AI price predictions for a symbol.

**Query Parameters:**

- `days` (optional): Number of days to predict (default: 7)
- `model` (optional): lstm, transformer, ensemble (default: ensemble)

**Response:**

```json
{
  "data": {
    "symbol": "AAPL",
    "predictions": [
      {
        "date": "2023-10-27",
        "predicted_price": 172.50,
        "confidence": 0.85,
        "model": "ensemble"
      }
    ],
    "model_info": {
      "model_type": "ensemble",
      "training_date": "2023-10-26T10:30:00Z",
      "accuracy": 0.78
    }
  }
}
```

### POST /ai/chat

Chat with AI for market insights.

**Request Body:**

```json
{
  "message": "What do you think about AAPL stock?",
  "context": {
    "symbol": "AAPL",
    "user_portfolio": true
  }
}
```

**Response:**

```json
{
  "data": {
    "response": "Based on current market conditions and technical analysis...",
    "suggestions": [
      {
        "action": "buy",
        "symbol": "AAPL",
        "confidence": 0.75,
        "reason": "Strong technical indicators"
      }
    ]
  }
}
```

---

## Technical Analysis Endpoints

### GET /technical-analysis/{symbol}/indicators

Get technical indicators for a symbol.

**Query Parameters:**

- `period` (optional): 1d, 5d, 1m, 3m, 6m, 1y (default: 1m)

**Response:**

```json
{
  "data": {
    "symbol": "AAPL",
    "indicators": {
      "rsi": {
        "value": 65.5,
        "signal": "neutral",
        "description": "RSI indicates neutral momentum"
      },
      "macd": {
        "value": 1.25,
        "signal": "bullish",
        "description": "MACD shows bullish momentum"
      },
      "moving_averages": {
        "sma_20": 165.50,
        "sma_50": 160.25,
        "sma_200": 155.75,
        "signal": "bullish"
      },
      "bollinger_bands": {
        "upper": 175.50,
        "middle": 170.00,
        "lower": 164.50,
        "signal": "neutral"
      }
    },
    "overall_signal": "bullish",
    "confidence": 0.75,
    "last_updated": "2023-10-26T10:30:00Z"
  }
}
```

### GET /technical-analysis/{symbol}/patterns

Get chart patterns and support/resistance levels.

**Response:**

```json
{
  "data": {
    "symbol": "AAPL",
    "patterns": [
      {
        "type": "ascending_triangle",
        "confidence": 0.80,
        "description": "Bullish continuation pattern"
      }
    ],
    "support_levels": [165.50, 160.25, 155.75],
    "resistance_levels": [175.50, 180.00, 185.25],
    "trend": "bullish",
    "last_updated": "2023-10-26T10:30:00Z"
  }
}
```

---

## News Endpoints

### GET /news

Get latest market news.

**Query Parameters:**

- `limit` (optional): Number of articles to return (default: 20)
- `category` (optional): general, business, technology, finance
- `symbol` (optional): Filter by symbol

**Response:**

```json
{
  "data": [
    {
      "id": "string",
      "title": "Tech Stocks Rally Amid Strong Earnings",
      "description": "Technology stocks surged today...",
      "source": "Reuters",
      "url": "https://example.com/article",
      "published_at": "2023-10-26T10:30:00Z",
      "sentiment": "positive",
      "symbols": ["AAPL", "MSFT", "GOOGL"]
    }
  ]
}
```

### GET /news/{symbol}

Get news for a specific symbol.

**Response:**

```json
{
  "data": [
    {
      "id": "string",
      "title": "Apple Reports Strong Q4 Earnings",
      "description": "Apple Inc. reported better than expected...",
      "source": "Bloomberg",
      "url": "https://example.com/article",
      "published_at": "2023-10-26T10:30:00Z",
      "sentiment": "positive"
    }
  ]
}
```

---

## Bank Endpoints

### GET /bank/balance

Get current cash balance.

**Response:**

```json
{
  "data": {
    "cash_balance": 10000.00,
    "currency": "USD",
    "last_updated": "2023-10-26T10:30:00Z"
  }
}
```

### POST /bank/deposit

Deposit money into account.

**Request Body:**

```json
{
  "amount": 1000.00,
  "description": "Initial deposit"
}
```

**Response:**

```json
{
  "data": {
    "transaction_id": "string",
    "amount": 1000.00,
    "new_balance": 11000.00,
    "timestamp": "2023-10-26T10:30:00Z"
  },
  "message": "Deposit successful"
}
```

### POST /bank/withdraw

Withdraw money from account.

**Request Body:**

```json
{
  "amount": 500.00,
  "description": "Withdrawal"
}
```

**Response:**

```json
{
  "data": {
    "transaction_id": "string",
    "amount": 500.00,
    "new_balance": 10500.00,
    "timestamp": "2023-10-26T10:30:00Z"
  },
  "message": "Withdrawal successful"
}
```

---

## Watchlist Endpoints

### GET /watchlist

Get user's watchlist.

**Response:**

```json
{
  "data": [
    {
      "id": "string",
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "current_price": 170.00,
      "change": 2.50,
      "change_percent": 1.49,
      "alert_price": 175.00,
      "added_at": "2023-10-26T10:30:00Z"
    }
  ]
}
```

### POST /watchlist

Add symbol to watchlist.

**Request Body:**

```json
{
  "symbol": "AAPL",
  "alert_price": 175.00
}
```

**Response:**

```json
{
  "data": {
    "id": "string",
    "symbol": "AAPL",
    "alert_price": 175.00,
    "added_at": "2023-10-26T10:30:00Z"
  },
  "message": "Symbol added to watchlist"
}
```

### DELETE /watchlist/{symbol}

Remove symbol from watchlist.

**Response:**

```json
{
  "data": {
    "symbol": "AAPL"
  },
  "message": "Symbol removed from watchlist"
}
```

---

## Market Screener Endpoints

### GET /market-screener

Get market screener results.

**Query Parameters:**

- `sector` (optional): Technology, Healthcare, Finance, etc.
- `min_price` (optional): Minimum price filter
- `max_price` (optional): Maximum price filter
- `min_volume` (optional): Minimum volume filter
- `min_change_percent` (optional): Minimum change percentage
- `max_change_percent` (optional): Maximum change percentage
- `limit` (optional): Number of results (default: 50)

**Response:**

```json
{
  "data": {
    "results": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology",
        "current_price": 170.00,
        "change": 2.50,
        "change_percent": 1.49,
        "volume": 75000000,
        "market_cap": 2800000000000
      }
    ],
    "total_count": 150,
    "filters_applied": {
      "sector": "Technology",
      "min_price": 100.00
    }
  }
}
```

### GET /market-screener/top-gainers

Get top gaining stocks.

**Query Parameters:**

- `limit` (optional): Number of results (default: 20)
- `sector` (optional): Filter by sector

**Response:**

```json
{
  "data": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "current_price": 170.00,
      "change": 2.50,
      "change_percent": 1.49,
      "volume": 75000000
    }
  ]
}
```

### GET /market-screener/top-losers

Get top losing stocks.

**Response:**

```json
{
  "data": [
    {
      "symbol": "MSFT",
      "name": "Microsoft Corp",
      "current_price": 330.00,
      "change": -1.20,
      "change_percent": -0.36,
      "volume": 50000000
    }
  ]
}
```

---

## WebSocket Endpoints

### WebSocket Connection

Connect to real-time price updates.

**URL:** `ws://localhost:8000/api/ws/prices`

**Authentication:**

```json
{
  "type": "authenticate",
  "token": "your_jwt_token"
}
```

**Subscribe to Price Updates:**

```json
{
  "type": "subscribe",
  "symbols": ["AAPL", "MSFT", "BTC"]
}
```

**Price Update Message:**

```json
{
  "type": "price_update",
  "symbol": "AAPL",
  "price": 170.00,
  "change": 2.50,
  "change_percent": 1.49,
  "timestamp": "2023-10-26T10:30:00Z"
}
```

**Alert Triggered Message:**

```json
{
  "type": "alert_triggered",
  "user_id": "string",
  "data": {
    "symbol": "AAPL",
    "alert_type": "price_above",
    "target_price": 175.00,
    "current_price": 176.50,
    "message": "AAPL price above $175.00"
  },
  "timestamp": "2023-10-26T10:30:00Z"
}
```

---

## Advanced Features

### Options Trading

### GET /options/chain/{symbol}

Get options chain for a symbol.

**Query Parameters:**

- `expiration` (optional): Filter by expiration date
- `strike_range` (optional): Filter by strike price range

**Response:**

```json
{
  "data": {
    "symbol": "AAPL",
    "expirations": ["2023-11-17", "2023-12-15"],
    "strikes": [
      {
        "strike": 170.00,
        "calls": [
          {
            "contract": "AAPL231117C00170000",
            "bid": 5.50,
            "ask": 5.75,
            "volume": 1000,
            "open_interest": 5000,
            "implied_volatility": 0.25
          }
        ],
        "puts": [
          {
            "contract": "AAPL231117P00170000",
            "bid": 3.25,
            "ask": 3.50,
            "volume": 800,
            "open_interest": 3000,
            "implied_volatility": 0.28
          }
        ]
      }
    ]
  }
}
```

### Backtesting

### POST /backtesting/run

Run a backtesting strategy.

**Request Body:**

```json
{
  "strategy": "ma_crossover",
  "symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2023-10-26",
  "parameters": {
    "short_period": 20,
    "long_period": 50
  },
  "initial_capital": 10000.00
}
```

**Response:**

```json
{
  "data": {
    "strategy": "ma_crossover",
    "symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-10-26",
    "initial_capital": 10000.00,
    "final_capital": 12500.00,
    "total_return": 25.00,
    "total_return_percent": 25.00,
    "sharpe_ratio": 1.25,
    "max_drawdown": -8.50,
    "trades": [
      {
        "entry_date": "2023-02-15",
        "exit_date": "2023-03-20",
        "entry_price": 150.00,
        "exit_price": 165.00,
        "quantity": 66,
        "profit": 990.00,
        "profit_percent": 10.00
      }
    ],
    "performance_metrics": {
      "win_rate": 0.65,
      "avg_win": 8.50,
      "avg_loss": -4.20,
      "profit_factor": 1.85
    }
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - External API unavailable |

## Rate Limits

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| Authentication | 10 requests | 1 minute |
| Portfolio | 100 requests | 1 minute |
| Trading | 50 requests | 1 minute |
| Market Data | 200 requests | 1 minute |
| AI Predictions | 20 requests | 1 minute |
| Technical Analysis | 100 requests | 1 minute |
| News | 50 requests | 1 minute |
| WebSocket | 100 connections | Per user |

## SDKs and Libraries

### Python

```python
import requests

class StockeeAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_portfolio(self):
        response = requests.get(f"{self.base_url}/portfolio", headers=self.headers)
        return response.json()
```

### JavaScript

```javascript
class StockeeAPI {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = { Authorization: `Bearer ${token}` };
    }
    
    async getPortfolio() {
        const response = await fetch(`${this.baseUrl}/portfolio`, {
            headers: this.headers
        });
        return response.json();
    }
}
```

## Support

For API support:

- Email: <api-support@stockee.com>
- Documentation: <https://docs.stockee.com>
- Status Page: <https://status.stockee.com>

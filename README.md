# Stockee - AI-Powered Stock & Crypto Trading Simulator

A comprehensive, visually stunning trading simulator with AI-driven insights, advanced data visualizations, and real-time market analysis. Built for both learning and professional trading simulation.

## 🚀 Core Features

### 📊 **Advanced Data Visualizations**

- **Interactive Heatmaps**: Sector performance and correlation matrices with color-coded intensity
- **3D Portfolio Visualization**: Risk-return scatter plots with portfolio weights and sector color coding
- **Advanced Candlestick Charts**: Professional OHLCV charts with technical indicators (SMA, EMA, Bollinger Bands)
- **Real-time Streaming Charts**: Live price updates with smooth animations and customizable intervals
- **Customizable Watchlists**: Drag-and-drop organization with multiple watchlists and visibility controls

### 🎨 **Visual Design Excellence**

- **Dark/Light Theme Toggle**: System-wide theme switching with smooth transitions
- **Live Market Ticker**: Scrolling real-time stock and crypto prices with live indicators
- **Micro-interactions**: Smooth animations, loading states, and hover effects throughout
- **Responsive Design**: Mobile-first approach with professional UI/UX
- **Customizable Dashboard**: Drag-and-drop widgets and personalized layouts

### 🤖 **AI-Powered Intelligence**

- **Multiple ML Models**: LSTM, Transformer, Ensemble models for price prediction
- **AI Trading Opponents**: Compete against AI with different trading strategies
- **Background AI Trading**: AI continues trading even when you're offline
- **Sentiment Analysis**: News and social media sentiment integration
- **Market Insights**: AI-generated analysis and trading recommendations

### 📈 **Comprehensive Trading Features**

- **Real-time Market Data**: Live stock and crypto prices from multiple APIs
- **Advanced Order Types**: Market, limit, stop-loss, take-profit, trailing stops
- **Portfolio Management**: Complete portfolio tracking with performance analytics
- **Risk Management**: Advanced risk metrics and portfolio optimization
- **Backtesting Engine**: Test trading strategies with historical data
- **Options Trading**: Options chain, Greeks, and strategy builder
- **Crypto Trading**: DeFi protocols, swaps, and yield farming simulation

### 🎓 **Educational Platform**

- **Trading Education**: Comprehensive learning modules covering strategies, terminology, and market psychology
- **Interactive Tooltips**: Educational content throughout the app
- **Market History**: Historical events, crashes, and recoveries
- **Strategy Library**: Pre-built trading strategies with explanations
- **Risk Education**: Position sizing, diversification, and risk management

## 🏗️ Tech Stack

### Backend

- **FastAPI** - Modern Python web framework with automatic API documentation
- **PostgreSQL + TimescaleDB** - Time-series database optimized for market data
- **SQLAlchemy** - Advanced ORM with relationship management
- **Celery** - Distributed task queue for background processing
- **Redis** - High-performance caching and message broker
- **WebSockets** - Real-time data streaming
- **Pydantic** - Data validation and serialization

### Frontend

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Full type safety and enhanced developer experience
- **Tailwind CSS** - Utility-first CSS with custom design system
- **Recharts** - Advanced charting library for data visualization
- **React Query** - Server state management and caching
- **React Beautiful DnD** - Drag and drop functionality
- **Canvas API** - High-performance custom chart rendering

### AI & ML

- **scikit-learn** - Traditional ML models (Random Forest, SVM, Linear Regression)
- **TensorFlow/PyTorch** - Deep learning models (LSTM, Transformer, Neural Networks)
- **OpenAI API** - GPT-4 integration for market analysis
- **Prophet** - Time series forecasting and trend analysis
- **Hugging Face** - Pre-trained models for sentiment analysis
- **Custom ML Pipeline** - Automated model training and retraining

### Data Sources & APIs

#### Stock Market Data

- **Alpha Vantage** - Comprehensive stock market data
- **Finnhub** - Real-time stock prices and financial data
- **Quandl/Nasdaq Data Link** - Professional historical data
- **Polygon.io** - Real-time market data and news

#### Cryptocurrency Data

- **CoinGecko** - Comprehensive crypto market data
- **CoinMarketCap** - Crypto prices and market cap data
- **CryptoCompare** - Historical crypto data and news
- **CoinAPI** - Professional crypto data API
- **Binance API** - Real-time crypto trading data

#### News & Sentiment

- **NewsAPI** - Global news aggregation
- **World News API** - International news sources
- **Reddit API** - Social sentiment analysis
- **Hugging Face** - AI-powered sentiment analysis

#### Economic Data

- **FRED API** - Federal Reserve economic data
- **World Bank API** - Global economic indicators
- **IMF API** - International monetary data
- **OpenWeatherMap** - Weather data for commodity trading

## 📁 Project Structure

```
stockee/
├── backend/                           # FastAPI backend
│   ├── app/
│   │   ├── api/                      # API routes
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── portfolio.py         # Portfolio management
│   │   │   ├── trading.py           # Trading operations
│   │   │   ├── market_data.py       # Market data endpoints
│   │   │   ├── analytics.py         # Analytics and metrics
│   │   │   ├── crypto.py            # Cryptocurrency trading
│   │   │   ├── options.py           # Options trading
│   │   │   ├── ai_predictions.py    # AI prediction models
│   │   │   ├── ai_opponent.py       # AI trading opponents
│   │   │   ├── background_ai.py     # Background AI trading
│   │   │   ├── historical_data.py   # Historical data service
│   │   │   ├── economic_data.py     # Economic indicators
│   │   │   ├── news.py              # News and sentiment
│   │   │   └── websocket_service.py # Real-time WebSocket
│   │   ├── core/                     # Core configuration
│   │   │   └── config.py            # Settings and API keys
│   │   ├── db/                       # Database models and schemas
│   │   │   ├── models.py            # SQLAlchemy models
│   │   │   ├── schemas.py           # Pydantic schemas
│   │   │   └── database.py          # Database connection
│   │   ├── services/                 # Business logic services
│   │   │   ├── portfolio_service.py # Portfolio management
│   │   │   ├── trading_service.py   # Trading operations
│   │   │   ├── market_data_service.py # Market data processing
│   │   │   ├── crypto_service.py   # Crypto data integration
│   │   │   ├── ai_opponent_service.py # AI trading logic
│   │   │   ├── historical_data_service.py # Historical data
│   │   │   ├── economic_data_service.py # Economic data
│   │   │   ├── news_sentiment_service.py # News and sentiment
│   │   │   └── weather_commodities_service.py # Weather data
│   │   └── utils/                    # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── visualizations/     # Advanced chart components
│   │   │   │   ├── InteractiveHeatmap.tsx
│   │   │   │   ├── Portfolio3DVisualization.tsx
│   │   │   │   ├── AdvancedCandlestickChart.tsx
│   │   │   │   └── StreamingChart.tsx
│   │   │   ├── ThemeToggle.tsx      # Dark/light theme toggle
│   │   │   ├── LiveTicker.tsx       # Real-time market ticker
│   │   │   ├── CustomizableWatchlist.tsx # Drag-and-drop watchlists
│   │   │   ├── Layout.tsx           # Main layout component
│   │   │   └── ErrorBoundary.tsx    # Error handling
│   │   ├── pages/                   # Page components
│   │   │   ├── Dashboard.tsx        # Main dashboard
│   │   │   ├── Trading.tsx          # Trading interface
│   │   │   ├── Portfolio.tsx        # Portfolio management
│   │   │   ├── Analytics.tsx        # Performance analytics
│   │   │   ├── MarketData.tsx       # Market data display
│   │   │   ├── DataVisualization.tsx # Advanced visualizations
│   │   │   ├── Competition.tsx      # AI trading competition
│   │   │   ├── Education/           # Trading education
│   │   │   │   └── TradingEducation.tsx
│   │   │   └── CryptoTrading.tsx    # Crypto trading interface
│   │   ├── hooks/                   # Custom React hooks
│   │   │   └── useWebSocket.ts      # WebSocket integration
│   │   ├── contexts/                # React contexts
│   │   │   └── ThemeContext.tsx     # Theme management
│   │   ├── services/                # API services
│   │   │   └── api.ts              # API client
│   │   ├── styles/                  # Styling
│   │   │   └── themes.css          # CSS variables and themes
│   │   └── utils/                   # Utility functions
│   ├── package.json
│   └── Dockerfile
├── database/                        # Database scripts and migrations
├── docker-compose.yml               # Development environment
├── env.example                      # Environment variables template
└── README.md
```

## 🚀 Quick Start

1. **Clone and setup**:

   ```bash
   git clone <repo-url>
   cd stockee
   ```

2. **Start development environment**:

   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - API Docs: <http://localhost:8000/docs>

## 🔧 Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL 13+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 📊 Database Schema

### Core Tables

- `assets` - Stock and crypto asset metadata with sector classification
- `prices` - OHLCV price data with time-series optimization (TimescaleDB)
- `portfolios` - User portfolio information with performance tracking
- `transactions` - Complete trading transaction history
- `bank_transactions` - Cash deposits, withdrawals, and balance management
- `holdings` - Current portfolio positions with unrealized P&L
- `analytics` - Performance metrics, risk analysis, and benchmarking
- `ai_predictions` - ML model predictions with confidence scores
- `ai_opponents` - AI trading opponents and competition data
- `watchlist` - User watchlists with customizable organization
- `price_alerts` - Price-based alert configurations
- `technical_alerts` - Technical indicator-based alerts
- `volume_alerts` - Volume-based alert configurations
- `news_alerts` - News and sentiment-based alerts
- `alert_history` - Alert trigger history and notifications
- `advanced_orders` - Stop-loss, take-profit, and trailing stop orders
- `ml_models` - ML model metadata and performance tracking
- `social_posts` - Social trading posts and community content
- `social_likes` - Social interaction tracking
- `social_comments` - Community comments and discussions
- `social_follows` - User following relationships
- `social_shares` - Content sharing and viral tracking

## 🤖 AI Features

### Machine Learning Models

1. **Traditional Models**: Moving averages, ARIMA, Prophet, Random Forest, SVM
2. **Deep Learning**: LSTM, Transformer models, Neural Networks
3. **Reinforcement Learning**: Trading bot agents with different strategies
4. **Ensemble Methods**: Combined model predictions for higher accuracy
5. **Sentiment Analysis**: News and social media sentiment integration
6. **Custom ML Pipeline**: Automated model training and retraining

### AI Trading Opponents

- **Multiple Strategies**: Conservative, Aggressive, Technical, Sentiment-based
- **Background Trading**: AI continues trading even when you're offline
- **Competition Mode**: Compete against AI with real-time performance tracking
- **Strategy Learning**: AI adapts and improves over time
- **Performance Metrics**: Detailed AI trading statistics and analysis

### Advanced AI Integration

- **OpenAI GPT-4**: Market analysis and trading recommendations
- **Hugging Face**: Pre-trained models for sentiment analysis
- **Custom Models**: Proprietary models trained on market data
- **Real-time Predictions**: Live AI predictions with confidence scores
- **Portfolio Optimization**: AI-powered portfolio allocation suggestions

## 📈 Roadmap

### ✅ Completed Features

- [x] **Project Setup**: Complete project structure and configuration
- [x] **Backend API**: Comprehensive FastAPI backend with all endpoints
- [x] **Database Schema**: Complete database design with TimescaleDB optimization
- [x] **Market Data Integration**: Multiple API integrations with fallback systems
- [x] **Trading Simulation**: Full trading engine with all order types
- [x] **Portfolio Management**: Complete portfolio tracking and analytics
- [x] **AI Integration**: Multiple ML models and AI trading opponents
- [x] **Advanced Visualizations**: Interactive heatmaps, 3D charts, candlestick charts
- [x] **Real-time Features**: Live ticker, streaming charts, WebSocket integration
- [x] **Theme System**: Dark/light theme toggle with smooth transitions
- [x] **Responsive Design**: Mobile-first design with professional UI/UX
- [x] **Educational Platform**: Comprehensive trading education modules
- [x] **Crypto Trading**: Complete cryptocurrency trading simulation
- [x] **Options Trading**: Options chain, Greeks, and strategy builder
- [x] **Backtesting Engine**: Historical strategy testing and analysis
- [x] **Social Features**: Community posts, likes, comments, and sharing
- [x] **Alert System**: Price, technical, volume, and news alerts
- [x] **Bank System**: Cash management and balance tracking
- [x] **Performance Analytics**: Advanced metrics and risk analysis

### 🚀 Next Phase Features

- [ ] **WebSocket Enhancement**: Real-time data streaming optimization
- [ ] **Advanced Technical Indicators**: RSI, MACD, Stochastic, Williams %R
- [ ] **Chart Pattern Recognition**: Automatic pattern detection and alerts
- [ ] **Export Features**: Chart export to PNG, PDF, and CSV formats
- [ ] **Portfolio Optimization**: Modern Portfolio Theory implementation
- [ ] **Social Trading**: Follow traders and copy trading functionality
- [ ] **Advanced Order Management**: Bracket orders, OCO, Iceberg orders
- [ ] **Mobile App**: React Native mobile application
- [ ] **Performance Monitoring**: Real-time performance metrics and alerts
- [ ] **API Documentation**: Comprehensive API documentation with examples

## 🌟 Key Features Showcase

### 📊 **Advanced Data Visualizations**

- **Interactive Heatmaps**: Sector performance with color-coded intensity
- **3D Portfolio Visualization**: Risk-return scatter plots with portfolio weights
- **Professional Charts**: Candlestick charts with technical indicators
- **Real-time Streaming**: Live price updates with smooth animations

### 🤖 **AI-Powered Intelligence**

- **Multiple ML Models**: LSTM, Transformer, Ensemble predictions
- **AI Trading Opponents**: Compete against different AI strategies
- **Background Trading**: AI continues trading when you're offline
- **Sentiment Analysis**: News and social media integration

### 🎨 **Visual Design Excellence**

- **Dark/Light Themes**: Smooth theme transitions
- **Live Market Ticker**: Real-time scrolling prices
- **Micro-interactions**: Smooth animations throughout
- **Responsive Design**: Mobile-first approach

### 📈 **Comprehensive Trading**

- **All Order Types**: Market, limit, stop-loss, trailing stops
- **Portfolio Management**: Complete tracking and analytics
- **Risk Management**: Advanced risk metrics
- **Backtesting**: Historical strategy testing

### 🎓 **Educational Platform**

- **Trading Education**: Comprehensive learning modules
- **Interactive Tooltips**: Educational content throughout
- **Strategy Library**: Pre-built strategies with explanations
- **Market History**: Historical events and analysis

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL 13+

### Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd stockee

# Start with Docker Compose
docker-compose up -d

# Or start manually
cd backend && pip install -r requirements.txt && python main_minimal.py
cd frontend && npm install && npm start
```

### Access Points

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>
- **WebSocket**: ws://localhost:8000/ws

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Alpha Vantage** - Stock market data
- **CoinGecko** - Cryptocurrency data
- **OpenAI** - AI-powered insights
- **Hugging Face** - ML models and sentiment analysis
- **React** - Frontend framework
- **FastAPI** - Backend framework
- **TimescaleDB** - Time-series database

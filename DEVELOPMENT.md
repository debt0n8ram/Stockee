# Stockee - AI-Powered Stock & Crypto Trading Simulator

## 🎯 Project Overview

Stockee is a comprehensive trading simulator that combines real-time market data, AI-powered insights, and portfolio management in a beautiful, modern web interface. Built with FastAPI, React, and PostgreSQL with TimescaleDB for time-series data.

## ✨ Key Features

### 🏗️ **Core Trading System**

- **Real-time Market Data**: Live stock and crypto prices from multiple APIs
- **Portfolio Management**: Track holdings, cash balance, and performance
- **Trading Simulation**: Buy/sell stocks and crypto with realistic order types
- **Performance Analytics**: Comprehensive metrics and risk analysis

### 🤖 **AI-Powered Features**

- **ChatGPT Integration**: Natural language Q&A about your portfolio
- **Price Predictions**: ML models for forecasting asset prices
- **Portfolio Insights**: AI-generated recommendations and analysis
- **Sentiment Analysis**: Market sentiment tracking (planned)

### 📊 **Advanced Analytics**

- **Performance Metrics**: Sharpe ratio, max drawdown, volatility
- **Benchmark Comparison**: Compare against S&P 500 and other indices
- **Risk Analysis**: VaR, correlation analysis, portfolio optimization
- **Interactive Charts**: Beautiful visualizations with Recharts

### 🎨 **Modern UI/UX**

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Themes**: Customizable interface
- **Real-time Updates**: Live data refresh and notifications
- **Intuitive Navigation**: Easy-to-use trading interface

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd stockee
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY (for ChatGPT)
# - ALPHA_VANTAGE_API_KEY (for stock data)
# - POLYGON_API_KEY (for additional data)
```

### 3. Start the Application

```bash
./start.sh
```

### 4. Access the Application

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>

## 🏗️ Architecture

### Backend (FastAPI)

```
backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Configuration
│   ├── db/            # Database models
│   ├── ml/            # ML models
│   ├── services/      # Business logic
│   └── utils/         # Utilities
```

### Frontend (React + TypeScript)

```
frontend/
├── src/
│   ├── components/    # Reusable components
│   ├── pages/         # Page components
│   ├── services/      # API services
│   └── utils/         # Utilities
```

### Database (PostgreSQL + TimescaleDB)

- **Assets**: Stock and crypto metadata
- **Prices**: OHLCV time-series data
- **Portfolios**: User portfolio information
- **Transactions**: Trading history
- **Analytics**: Performance metrics
- **AI Predictions**: ML model outputs

## 🔧 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

### Database Management

```bash
# Access PostgreSQL
docker exec -it stockee_postgres_1 psql -U stockee_user -d stockee

# Run migrations
alembic upgrade head
```

## 📊 Data Sources

### Market Data APIs

- **Alpha Vantage**: Stock market data
- **Yahoo Finance**: Additional market data
- **Binance**: Cryptocurrency data
- **Polygon.io**: Real-time market data

### AI Services

- **OpenAI GPT**: ChatGPT integration
- **Custom ML Models**: Price prediction and analysis

## 🎯 Roadmap

### Phase 1: Core Features ✅

- [x] Basic trading simulation
- [x] Portfolio management
- [x] Market data integration
- [x] Basic AI chat

### Phase 2: Advanced Features 🚧

- [ ] Advanced ML models (LSTM, Transformer)
- [ ] Sentiment analysis from news/social media
- [ ] Automated trading bots
- [ ] Advanced order types (stop-loss, trailing stops)

### Phase 3: Enterprise Features 📋

- [ ] Multi-user support
- [ ] Advanced analytics and reporting
- [ ] Mobile app
- [ ] Real-time notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions

## 🙏 Acknowledgments

- FastAPI for the excellent Python web framework
- React and Tailwind CSS for the beautiful UI
- TimescaleDB for time-series data management
- OpenAI for AI capabilities
- Alpha Vantage and other data providers

---

**Happy Trading! 📈🚀**

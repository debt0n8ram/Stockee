import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const apiService = {
    // Portfolio endpoints
    getPortfolio: async (userId: string) => {
        const response = await api.get(`/api/portfolio/${userId}`);
        return response.data;
    },

    getHoldings: async (userId: string) => {
        const response = await api.get(`/api/portfolio/${userId}/holdings`);
        return response.data;
    },

    getTransactions: async (userId: string, limit = 50) => {
        const response = await api.get(`/api/portfolio/${userId}/transactions?limit=${limit}`);
        return response.data;
    },

    resetPortfolio: async (userId: string) => {
        const response = await api.put(`/api/portfolio/${userId}/reset`);
        return response.data;
    },

    getPerformance: async (userId: string, days = 30) => {
        const response = await api.get(`/api/portfolio/${userId}/performance?days=${days}`);
        return response.data;
    },

    // Trading endpoints
    buyStock: async (userId: string, orderData: any) => {
        const response = await api.post(`/api/trading/buy`, {
            user_id: userId,
            ...orderData
        });
        return response.data;
    },

    sellStock: async (userId: string, orderData: any) => {
        const response = await api.post(`/api/trading/sell`, {
            user_id: userId,
            ...orderData
        });
        return response.data;
    },

    getOpenOrders: async (userId: string) => {
        const response = await api.get(`/api/trading/orders/${userId}`);
        return response.data;
    },

    cancelOrder: async (orderId: string) => {
        const response = await api.delete(`/api/trading/orders/${orderId}`);
        return response.data;
    },

    // Market data endpoints
    searchAssets: async (query: string, assetType?: string, limit = 20) => {
        const response = await api.get(`/api/market/search/${query}?asset_type=${assetType}&limit=${limit}`);
        return response.data;
    },

    getCurrentPrice: async (symbol: string) => {
        const response = await api.get(`/api/market/price/${symbol}`);
        return response.data;
    },

    getPriceHistory: async (symbol: string, days = 30, interval = '1d') => {
        const response = await api.get(`/api/market/price/${symbol}/history?days=${days}&interval=${interval}`);
        return response.data;
    },

    getChartData: async (symbol: string, days = 30, interval = '1d') => {
        const response = await api.get(`/api/market/price/${symbol}/chart?days=${days}&interval=${interval}`);
        return response.data;
    },

    getMarketStatus: async () => {
        const response = await api.get('/api/market/market-status');
        return response.data;
    },

    getTrendingAssets: async (limit = 10) => {
        const response = await api.get(`/api/market/trending?limit=${limit}`);
        return response.data;
    },

    getAssetNews: async (symbol: string, limit = 10) => {
        const response = await api.get(`/api/market/news/${symbol}?limit=${limit}`);
        return response.data;
    },

    // Analytics endpoints
    getPerformanceAnalytics: async (userId: string, days = 30) => {
        const response = await api.get(`/api/analytics/performance/${userId}?days=${days}`);
        return response.data;
    },

    getRiskMetrics: async (userId: string, days = 30) => {
        const response = await api.get(`/api/analytics/risk/${userId}?days=${days}`);
        return response.data;
    },

    getBenchmarkComparison: async (userId: string, benchmark = 'SPY', days = 30) => {
        const response = await api.get(`/api/analytics/benchmark/${userId}?benchmark=${benchmark}&days=${days}`);
        return response.data;
    },

    getPortfolioAllocation: async (userId: string) => {
        const response = await api.get(`/api/analytics/allocation/${userId}`);
        return response.data;
    },

    getCorrelationAnalysis: async (userId: string, days = 30) => {
        const response = await api.get(`/api/analytics/correlation/${userId}?days=${days}`);
        return response.data;
    },

    getPerformanceHeatmap: async (userId: string, days = 30) => {
        const response = await api.get(`/api/analytics/heatmap/${userId}?days=${days}`);
        return response.data;
    },

    // AI endpoints
    chatWithAI: async (message: string, userId: string, sessionId?: string) => {
        const response = await api.post('/api/ai/chat', {
            message,
            user_id: userId,
            session_id: sessionId
        });
        return response.data;
    },

    getPricePredictions: async (symbol: string, days = 30) => {
        const response = await api.get(`/api/ai/predictions/${symbol}?days=${days}`);
        return response.data;
    },

    getPortfolioInsights: async (userId: string) => {
        const response = await api.get(`/api/ai/insights/${userId}`);
        return response.data;
    },

    retrainModels: async () => {
        const response = await api.post('/api/ai/retrain');
        return response.data;
    },

    getModelStatus: async () => {
        const response = await api.get('/api/ai/models/status');
        return response.data;
    },

    // Auth endpoints
    login: async (userId: string) => {
        const response = await api.post('/api/auth/login', { user_id: userId });
        return response.data;
    },

    register: async (userId: string) => {
        const response = await api.post('/api/auth/register', { user_id: userId });
        return response.data;
    },

    getCurrentUser: async (userId: string) => {
        const response = await api.get(`/api/auth/me?user_id=${userId}`);
        return response.data;
    },

    // Bank API
    getCashBalance: async (userId: string) => {
        const response = await api.get(`/api/bank/balance/${userId}`);
        return response.data;
    },

    depositCash: async (userId: string, amount: number, description: string = 'Deposit') => {
        const response = await api.post('/api/bank/deposit', {
            user_id: userId,
            amount,
            description
        });
        return response.data;
    },

    withdrawCash: async (userId: string, amount: number, description: string = 'Withdrawal') => {
        const response = await api.post('/api/bank/withdraw', {
            user_id: userId,
            amount,
            description
        });
        return response.data;
    },

    resetBalance: async (userId: string, newBalance: number) => {
        const response = await api.post('/api/bank/reset-balance', {
            user_id: userId,
            new_balance: newBalance
        });
        return response.data;
    },

    getBankTransactions: async (userId: string, limit: number = 50) => {
        const response = await api.get(`/api/bank/transactions/${userId}?limit=${limit}`);
        return response.data;
    },

    // AI Predictions API
    getAIPredictions: async (symbol: string, daysAhead: number = 7) => {
        const response = await api.get(`/api/ai-predictions/predict/${symbol}?days_ahead=${daysAhead}`);
        return response.data;
    },

    getAIPredictionHistory: async (symbol: string, limit: number = 20) => {
        const response = await api.get(`/api/ai-predictions/history/${symbol}?limit=${limit}`);
        return response.data;
    },

    getAvailableModels: async () => {
        const response = await api.get('/api/ai-predictions/models');
        return response.data;
    },

    // Technical Analysis API
    getTechnicalIndicators: async (symbol: string, days: number = 30) => {
        const response = await api.get(`/api/technical/indicators/${symbol}?days=${days}`);
        return response.data;
    },

    getTechnicalSummary: async (symbol: string, days: number = 30) => {
        const response = await api.get(`/api/technical/indicators/${symbol}/summary?days=${days}`);
        return response.data;
    },

    // News API
    getMarketNews: async (limit: number = 10) => {
        const response = await api.get(`/api/news/market?limit=${limit}`);
        return response.data;
    },

    getStockNews: async (symbol: string, limit: number = 10) => {
        const response = await api.get(`/api/news/stock/${symbol}?limit=${limit}`);
        return response.data;
    },

    getCryptoNews: async (limit: number = 10) => {
        const response = await api.get(`/api/news/crypto?limit=${limit}`);
        return response.data;
    },

    analyzeNewsSentiment: async (text: string) => {
        const response = await api.get(`/api/news/sentiment?text=${encodeURIComponent(text)}`);
        return response.data;
    },

    searchNews: async (query: string, limit: number = 10, sortBy: string = "publishedAt") => {
        const response = await api.get(`/api/news/search?query=${encodeURIComponent(query)}&limit=${limit}&sort_by=${sortBy}`);
        return response.data;
    },

    filterNews: async (category?: string, source?: string, sentiment?: string, limit: number = 10) => {
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        if (source) params.append('source', source);
        if (sentiment) params.append('sentiment', sentiment);
        params.append('limit', limit.toString());

        const response = await api.get(`/api/news/filter?${params.toString()}`);
        return response.data;
    },

    // Market Screener API
    screenStocks: async (filters: any) => {
        const params = new URLSearchParams();
        Object.keys(filters).forEach(key => {
            if (filters[key] !== null && filters[key] !== undefined) {
                params.append(key, filters[key].toString());
            }
        });

        const response = await api.get(`/api/screener/stocks?${params.toString()}`);
        return response.data;
    },

    getTopGainers: async (limit: number = 20) => {
        const response = await api.get(`/api/screener/top-gainers?limit=${limit}`);
        return response.data;
    },

    getTopLosers: async (limit: number = 20) => {
        const response = await api.get(`/api/screener/top-losers?limit=${limit}`);
        return response.data;
    },

    getMostActive: async (limit: number = 20) => {
        const response = await api.get(`/api/screener/most-active?limit=${limit}`);
        return response.data;
    },

    getSectorPerformance: async () => {
        const response = await api.get('/api/screener/sector-performance');
        return response.data;
    },

    getMarketOverview: async () => {
        const response = await api.get('/api/screener/market-overview');
        return response.data;
    },

    // Watchlist API
    addToWatchlist: async (userId: string, symbol: string, alertPrice?: number) => {
        const response = await api.post('/api/watchlist/add', {
            user_id: userId,
            symbol: symbol,
            alert_price: alertPrice
        });
        return response.data;
    },

    removeFromWatchlist: async (userId: string, symbol: string) => {
        const response = await api.delete(`/api/watchlist/remove?user_id=${userId}&symbol=${symbol}`);
        return response.data;
    },

    getWatchlist: async (userId: string) => {
        const response = await api.get(`/api/watchlist/${userId}`);
        return response.data;
    },

    updateAlertPrice: async (userId: string, symbol: string, alertPrice: number) => {
        const response = await api.put('/api/watchlist/alert', {
            user_id: userId,
            symbol: symbol,
            alert_price: alertPrice
        });
        return response.data;
    },

    getAlerts: async (userId: string) => {
        const response = await api.get(`/api/watchlist/${userId}/alerts`);
        return response.data;
    },

    getWatchlistPerformance: async (userId: string) => {
        const response = await api.get(`/api/watchlist/${userId}/performance`);
        return response.data;
    },

    // Backtesting API
    runBacktest: async (request: any) => {
        const response = await api.post('/api/backtesting/run', request);
        return response.data;
    },

    optimizeBacktestingStrategy: async (request: any) => {
        const response = await api.post('/api/backtesting/optimize', request);
        return response.data;
    },

    runWalkForwardAnalysis: async (request: any) => {
        const response = await api.post('/api/backtesting/walk-forward', request);
        return response.data;
    },

    runMonteCarloSimulation: async (request: any) => {
        const response = await api.post('/api/backtesting/monte-carlo', request);
        return response.data;
    },

    getAvailableBacktestingStrategies: async () => {
        const response = await api.get('/api/backtesting/strategies/available');
        return response.data;
    },

    getAvailableBacktestingSymbols: async () => {
        const response = await api.get('/api/backtesting/symbols/available');
        return response.data;
    },

    getBacktestingPerformanceMetrics: async () => {
        const response = await api.get('/api/backtesting/performance-metrics');
        return response.data;
    },

    compareBacktestingStrategies: async (strategies: any[]) => {
        const response = await api.post('/api/backtesting/compare-strategies', strategies);
        return response.data;
    },

    // Options Trading API
    getOptionChain: async (symbol: string, expirationDate?: string) => {
        const params = expirationDate ? `?expiration_date=${expirationDate}` : '';
        const response = await api.get(`/api/options/chain/${symbol}${params}`);
        return response.data;
    },

    calculateOptionGreeks: async (request: any) => {
        const response = await api.post('/api/options/calculate-greeks', request);
        return response.data;
    },

    calculateImpliedVolatility: async (request: any) => {
        const response = await api.post('/api/options/calculate-implied-volatility', request);
        return response.data;
    },

    createOptionStrategy: async (request: any) => {
        const response = await api.post('/api/options/strategy/create', request);
        return response.data;
    },

    getOptionStrategyTemplates: async () => {
        const response = await api.get('/api/options/strategies/templates');
        return response.data;
    },

    getAvailableOptionStrategies: async () => {
        const response = await api.get('/api/options/strategies/available');
        return response.data;
    },

    getAvailableOptionSymbols: async () => {
        const response = await api.get('/api/options/symbols/available');
        return response.data;
    },

    getOptionEducation: async () => {
        const response = await api.get('/api/options/education/strategies');
        return response.data;
    },

    calculateOptionRisk: async (params: any) => {
        const queryParams = new URLSearchParams(params).toString();
        const response = await api.get(`/api/options/risk-calculator?${queryParams}`);
        return response.data;
    },

    // Cryptocurrency Trading API
    getCryptoPrices: async (symbols: string) => {
        const response = await api.get(`/api/crypto/prices?symbols=${symbols}`);
        return response.data;
    },

    getCryptoMarketData: async (symbol: string) => {
        const response = await api.get(`/api/crypto/market-data/${symbol}`);
        return response.data;
    },

    getDefiPools: async (protocol: string, limit: number = 50) => {
        const response = await api.get(`/api/crypto/defi/pools?protocol=${protocol}&limit=${limit}`);
        return response.data;
    },

    getYieldFarmingOpportunities: async (minApr: number = 5.0) => {
        const response = await api.get(`/api/crypto/defi/yield-farming?min_apr=${minApr}`);
        return response.data;
    },

    calculateSwapQuote: async (request: any) => {
        const response = await api.post('/api/crypto/defi/swap-quote', request);
        return response.data;
    },

    getLiquidityPoolAnalytics: async (poolAddress: string) => {
        const response = await api.get(`/api/crypto/defi/pool-analytics/${poolAddress}`);
        return response.data;
    },

    getCryptoPortfolioAnalytics: async (userId: string) => {
        const response = await api.get(`/api/crypto/portfolio/analytics/${userId}`);
        return response.data;
    },

    getDefiPositions: async (userId: string) => {
        const response = await api.get(`/api/crypto/defi/positions/${userId}`);
        return response.data;
    },

    getAvailableDefiProtocols: async () => {
        const response = await api.get('/api/crypto/defi/protocols');
        return response.data;
    },

    getAvailableDefiActions: async () => {
        const response = await api.get('/api/crypto/defi/actions');
        return response.data;
    },

    getTrendingCryptocurrencies: async (limit: number = 20) => {
        const response = await api.get(`/api/crypto/market/trending?limit=${limit}`);
        return response.data;
    },

    getCryptoCategories: async () => {
        const response = await api.get('/api/crypto/market/categories');
        return response.data;
    },

    getDefiEducation: async () => {
        const response = await api.get('/api/crypto/education/defi-basics');
        return response.data;
    },

    // AI Opponent API
    getAIStrategies: async () => {
        const response = await api.get('/api/ai-opponent/strategies');
        return response.data;
    },

    createAIOpponent: async (userId: string, strategyType: string) => {
        const response = await api.post(`/api/ai-opponent/create?user_id=${userId}&strategy_type=${strategyType}`);
        return response.data;
    },

    getAIOpponent: async (userId: string) => {
        const response = await api.get(`/api/ai-opponent/opponent/${userId}`);
        return response.data;
    },

    executeAITrading: async (userId: string) => {
        const response = await api.post(`/api/ai-opponent/trade/${userId}`);
        return response.data;
    },

    getCompetitionData: async (userId: string) => {
        const response = await api.get(`/api/ai-opponent/competition/${userId}`);
        return response.data;
    },

    getCompetitionLeaderboard: async (limit: number = 10) => {
        const response = await api.get(`/api/ai-opponent/leaderboard?limit=${limit}`);
        return response.data;
    },

    deactivateAIOpponent: async (userId: string) => {
        const response = await api.put(`/api/ai-opponent/opponent/${userId}/deactivate`);
        return response.data;
    },

    // Background AI API
    startBackgroundAI: async () => {
        const response = await api.post('/api/background-ai/start');
        return response.data;
    },

    stopBackgroundAI: async () => {
        const response = await api.post('/api/background-ai/stop');
        return response.data;
    },

    getBackgroundAIStatus: async () => {
        const response = await api.get('/api/background-ai/status');
        return response.data;
    },

    forceAITradingRound: async (userId: string) => {
        const response = await api.post(`/api/background-ai/force-trading/${userId}`);
        return response.data;
    }
};

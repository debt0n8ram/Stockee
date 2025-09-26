import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import {
    TrendingUp,
    TrendingDown,
    Activity,
    Users,
    DollarSign,
    BarChart3,
    Globe,
    Zap,
    AlertTriangle,
    CheckCircle,
    Clock,
    RefreshCw
} from 'lucide-react';
// Simple date formatting function to avoid date-fns dependency
const formatDate = (date: Date, format?: string) => {
    if (format === 'MMM dd, yyyy HH:mm:ss') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } else if (format === 'MMM dd, HH:mm') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ', ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};
import { AdvancedChart } from '../charts/AdvancedChart';

interface MarketData {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    volume: number;
    marketCap: number;
    lastUpdated: string;
}

interface PortfolioData {
    totalValue: number;
    totalChange: number;
    totalChangePercent: number;
    cashBalance: number;
    holdings: Array<{
        symbol: string;
        quantity: number;
        value: number;
        change: number;
        changePercent: number;
    }>;
}

interface NewsItem {
    id: string;
    title: string;
    summary: string;
    source: string;
    publishedAt: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    symbols: string[];
}

interface AlertItem {
    id: string;
    type: 'price' | 'volume' | 'news' | 'technical';
    symbol: string;
    message: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    timestamp: string;
    isRead: boolean;
}

interface RealTimeDashboardProps {
    className?: string;
}

export const RealTimeDashboard: React.FC<RealTimeDashboardProps> = ({ className = '' }) => {
    const [marketData, setMarketData] = useState<MarketData[]>([]);
    const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null);
    const [newsData, setNewsData] = useState<NewsItem[]>([]);
    const [alerts, setAlerts] = useState<AlertItem[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState(5000);

    // WebSocket connection for real-time data
    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/api/ws/prices');

        ws.onopen = () => {
            setIsConnected(true);
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        ws.onclose = () => {
            setIsConnected(false);
            console.log('WebSocket disconnected');
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setIsConnected(false);
        };

        return () => {
            ws.close();
        };
    }, []);

    // Auto-refresh data
    useEffect(() => {
        if (!autoRefresh) return;

        const interval = setInterval(() => {
            fetchMarketData();
            fetchPortfolioData();
            fetchNewsData();
            fetchAlerts();
        }, refreshInterval);

        return () => clearInterval(interval);
    }, [autoRefresh, refreshInterval]);

    // Handle WebSocket messages
    const handleWebSocketMessage = useCallback((data: any) => {
        switch (data.type) {
            case 'price_update':
                setMarketData(prev =>
                    prev.map(item =>
                        item.symbol === data.symbol
                            ? { ...item, price: data.price, change: data.change, changePercent: data.changePercent, lastUpdated: new Date().toISOString() }
                            : item
                    )
                );
                break;

            case 'alert_triggered':
                setAlerts(prev => [data.alert, ...prev]);
                break;

            case 'news_update':
                setNewsData(prev => [data.news, ...prev.slice(0, 9)]);
                break;

            default:
                console.log('Unknown message type:', data.type);
        }

        setLastUpdate(new Date());
    }, []);

    // Fetch market data
    const fetchMarketData = async () => {
        try {
            const response = await fetch('/api/market-data/top-stocks?limit=20');
            const data = await response.json();
            setMarketData(data.data || []);
        } catch (error) {
            console.error('Error fetching market data:', error);
        }
    };

    // Fetch portfolio data
    const fetchPortfolioData = async () => {
        try {
            const response = await fetch('/api/portfolio');
            const data = await response.json();
            setPortfolioData(data.data);
        } catch (error) {
            console.error('Error fetching portfolio data:', error);
        }
    };

    // Fetch news data
    const fetchNewsData = async () => {
        try {
            const response = await fetch('/api/news?limit=10');
            const data = await response.json();
            setNewsData(data.data || []);
        } catch (error) {
            console.error('Error fetching news data:', error);
        }
    };

    // Fetch alerts
    const fetchAlerts = async () => {
        try {
            const response = await fetch('/api/alerts');
            const data = await response.json();
            setAlerts(data.data || []);
        } catch (error) {
            console.error('Error fetching alerts:', error);
        }
    };

    // Mark alert as read
    const markAlertAsRead = async (alertId: string) => {
        try {
            await fetch(`/api/alerts/${alertId}/read`, { method: 'POST' });
            setAlerts(prev => prev.map(alert =>
                alert.id === alertId ? { ...alert, isRead: true } : alert
            ));
        } catch (error) {
            console.error('Error marking alert as read:', error);
        }
    };

    // Get market status
    const getMarketStatus = () => {
        const now = new Date();
        const hour = now.getHours();
        const day = now.getDay();

        if (day === 0 || day === 6) return 'closed';
        if (hour >= 9 && hour < 16) return 'open';
        return 'closed';
    };

    const marketStatus = getMarketStatus();

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Real-Time Dashboard</h1>
                    <p className="text-muted-foreground">
                        Last updated: {formatDate(lastUpdate, 'MMM dd, yyyy HH:mm:ss')}
                    </p>
                </div>

                <div className="flex items-center space-x-4">
                    {/* Connection Status */}
                    <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="text-sm text-muted-foreground">
                            {isConnected ? 'Connected' : 'Disconnected'}
                        </span>
                    </div>

                    {/* Market Status */}
                    <Badge variant={marketStatus === 'open' ? 'default' : 'secondary'}>
                        {marketStatus === 'open' ? 'Market Open' : 'Market Closed'}
                    </Badge>

                    {/* Auto Refresh */}
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setAutoRefresh(!autoRefresh)}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
                        Auto Refresh
                    </Button>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Portfolio Value</CardTitle>
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            ${portfolioData?.totalValue.toLocaleString() || '0'}
                        </div>
                        <div className={`text-xs flex items-center ${portfolioData?.totalChangePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {portfolioData?.totalChangePercent >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                            {portfolioData?.totalChangePercent.toFixed(2)}% ({portfolioData?.totalChange.toFixed(2)})
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Cash Balance</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            ${portfolioData?.cashBalance.toLocaleString() || '0'}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Available for trading
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {alerts.filter(alert => !alert.isRead).length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Unread notifications
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Market Activity</CardTitle>
                        <BarChart3 className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {marketData.length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Active symbols
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Main Content */}
            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="charts">Charts</TabsTrigger>
                    <TabsTrigger value="news">News</TabsTrigger>
                    <TabsTrigger value="alerts">Alerts</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Top Movers */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <TrendingUp className="h-5 w-5" />
                                    <span>Top Movers</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {marketData
                                        .sort((a, b) => Math.abs(b.changePercent) - Math.abs(a.changePercent))
                                        .slice(0, 10)
                                        .map((stock) => (
                                            <div key={stock.symbol} className="flex items-center justify-between">
                                                <div className="flex items-center space-x-3">
                                                    <div>
                                                        <p className="font-medium">{stock.symbol}</p>
                                                        <p className="text-sm text-muted-foreground">{stock.name}</p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-medium">${stock.price.toFixed(2)}</p>
                                                    <div className={`text-sm flex items-center ${stock.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                        {stock.changePercent >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                                                        {stock.changePercent.toFixed(2)}%
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Portfolio Holdings */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Users className="h-5 w-5" />
                                    <span>Portfolio Holdings</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {portfolioData?.holdings.map((holding) => (
                                        <div key={holding.symbol} className="flex items-center justify-between">
                                            <div>
                                                <p className="font-medium">{holding.symbol}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    {holding.quantity} shares
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-medium">${holding.value.toFixed(2)}</p>
                                                <div className={`text-sm flex items-center ${holding.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    {holding.changePercent >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
                                                    {holding.changePercent.toFixed(2)}%
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="charts" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        <div className="lg:col-span-2">
                            <AdvancedChart
                                symbol={selectedSymbol}
                                data={[]} // This would be populated with real data
                                onTimeframeChange={(timeframe) => console.log('Timeframe changed:', timeframe)}
                                onIndicatorChange={(indicators) => console.log('Indicators changed:', indicators)}
                            />
                        </div>

                        <div className="space-y-4">
                            {/* Symbol Selector */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Select Symbol</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-2 gap-2">
                                        {marketData.slice(0, 12).map((stock) => (
                                            <Button
                                                key={stock.symbol}
                                                variant={selectedSymbol === stock.symbol ? 'default' : 'outline'}
                                                size="sm"
                                                onClick={() => setSelectedSymbol(stock.symbol)}
                                            >
                                                {stock.symbol}
                                            </Button>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Market Overview */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Market Overview</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-3">
                                        <div className="flex justify-between">
                                            <span className="text-sm">Gainers</span>
                                            <span className="text-sm text-green-600">
                                                {marketData.filter(s => s.changePercent > 0).length}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">Losers</span>
                                            <span className="text-sm text-red-600">
                                                {marketData.filter(s => s.changePercent < 0).length}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">Unchanged</span>
                                            <span className="text-sm text-muted-foreground">
                                                {marketData.filter(s => s.changePercent === 0).length}
                                            </span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </TabsContent>

                <TabsContent value="news" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {newsData.map((news) => (
                            <Card key={news.id}>
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <CardTitle className="text-lg">{news.title}</CardTitle>
                                        <Badge variant={
                                            news.sentiment === 'positive' ? 'default' :
                                                news.sentiment === 'negative' ? 'destructive' : 'secondary'
                                        }>
                                            {news.sentiment}
                                        </Badge>
                                    </div>
                                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                                        <span>{news.source}</span>
                                        <span>•</span>
                                        <span>{formatDate(new Date(news.publishedAt), 'MMM dd, HH:mm')}</span>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground mb-3">{news.summary}</p>
                                    {news.symbols.length > 0 && (
                                        <div className="flex flex-wrap gap-1">
                                            {news.symbols.map((symbol) => (
                                                <Badge key={symbol} variant="outline" className="text-xs">
                                                    {symbol}
                                                </Badge>
                                            ))}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>

                <TabsContent value="alerts" className="space-y-4">
                    <div className="space-y-4">
                        {alerts.map((alert) => (
                            <Card key={alert.id} className={alert.isRead ? 'opacity-60' : ''}>
                                <CardContent className="p-4">
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-start space-x-3">
                                            <div className={`w-2 h-2 rounded-full mt-2 ${alert.severity === 'critical' ? 'bg-red-500' :
                                                alert.severity === 'high' ? 'bg-orange-500' :
                                                    alert.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                                                }`} />
                                            <div>
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <Badge variant="outline">{alert.type}</Badge>
                                                    <span className="font-medium">{alert.symbol}</span>
                                                    <Badge variant={
                                                        alert.severity === 'critical' ? 'destructive' :
                                                            alert.severity === 'high' ? 'destructive' : 'secondary'
                                                    }>
                                                        {alert.severity}
                                                    </Badge>
                                                </div>
                                                <p className="text-sm text-muted-foreground">{alert.message}</p>
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    {formatDate(new Date(alert.timestamp), 'MMM dd, yyyy HH:mm:ss')}
                                                </p>
                                            </div>
                                        </div>
                                        {!alert.isRead && (
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => markAlertAsRead(alert.id)}
                                            >
                                                Mark as Read
                                            </Button>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
};

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area,
    ScatterChart,
    Scatter,
    PieChart,
    Pie,
    Cell
} from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    BarChart3,
    Target,
    Shield,
    Clock,
    RefreshCw,
    Play,
    Pause,
    Square,
    RotateCcw,
    Settings,
    Bell,
    Star,
    Share2,
    Download,
    Calculator,
    Zap,
    Activity,
    AlertTriangle,
    CheckCircle,
    Eye,
    EyeOff,
    Volume2,
    VolumeX,
    ArrowUpRight,
    ArrowDownRight,
    Info,
    Lightbulb,
    Brain,
    Gauge,
    Timer,
    Layers,
    Users,
    Globe,
    TrendingUp as TrendingUpIcon,
    TrendingDown as TrendingDownIcon,
    Minus,
    Plus,
    X,
    Check,
    AlertCircle,
    BookOpen,
    FileText,
    Calendar,
    Filter,
    Search,
    MoreHorizontal,
    ChevronUp,
    ChevronDown,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
// Simple date formatting function to avoid date-fns dependency
const formatDate = (date: Date, format?: string) => {
    if (format === 'HH:mm:ss') {
        return date.toLocaleTimeString();
    } else if (format === 'MMM dd, HH:mm') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ', ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    } else if (format === 'MMM dd, yyyy HH:mm:ss') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } else if (format === 'HH:mm') {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    } else if (format === 'MMM dd, yyyy') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

interface TradingDashboardProps {
    className?: string;
}

interface MarketOverview {
    totalValue: number;
    dayChange: number;
    dayChangePercent: number;
    weekChange: number;
    weekChangePercent: number;
    monthChange: number;
    monthChangePercent: number;
    yearChange: number;
    yearChangePercent: number;
}

interface TopMover {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    volume: number;
    marketCap: number;
    sector: string;
}

interface TradingOpportunity {
    id: string;
    symbol: string;
    type: 'breakout' | 'reversal' | 'momentum' | 'support' | 'resistance';
    strength: number;
    confidence: number;
    description: string;
    entryPrice: number;
    targetPrice: number;
    stopLoss: number;
    riskReward: number;
    timeframe: string;
    timestamp: string;
}

interface MarketSentiment {
    overall: 'bullish' | 'bearish' | 'neutral';
    score: number;
    news: number;
    social: number;
    technical: number;
    volume: number;
}

interface EconomicCalendar {
    id: string;
    event: string;
    impact: 'high' | 'medium' | 'low';
    time: string;
    currency: string;
    actual: string;
    forecast: string;
    previous: string;
}

interface TradingDashboardState {
    marketOverview: MarketOverview | null;
    topMovers: TopMover[];
    tradingOpportunities: TradingOpportunity[];
    marketSentiment: MarketSentiment | null;
    economicCalendar: EconomicCalendar[];
    isConnected: boolean;
    lastUpdate: string;
    selectedTimeframe: string;
    selectedSector: string;
    showAdvanced: boolean;
}

export const TradingDashboard: React.FC<TradingDashboardProps> = ({ className = '' }) => {
    const [state, setState] = useState<TradingDashboardState>({
        marketOverview: null,
        topMovers: [],
        tradingOpportunities: [],
        marketSentiment: null,
        economicCalendar: [],
        isConnected: false,
        lastUpdate: new Date().toISOString(),
        selectedTimeframe: '1D',
        selectedSector: 'all',
        showAdvanced: false
    });

    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState(30000);

    const wsRef = useRef<WebSocket | null>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    // WebSocket connection for real-time data
    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/api/ws/trading-dashboard');

        ws.onopen = () => {
            setState(prev => ({ ...prev, isConnected: true }));
            console.log('Trading Dashboard WebSocket connected');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        ws.onclose = () => {
            setState(prev => ({ ...prev, isConnected: false }));
            console.log('Trading Dashboard WebSocket disconnected');
        };

        ws.onerror = (error) => {
            console.error('Trading Dashboard WebSocket error:', error);
            setState(prev => ({ ...prev, isConnected: false }));
        };

        wsRef.current = ws;

        return () => {
            ws.close();
        };
    }, []);

    // Auto-refresh data
    useEffect(() => {
        if (!autoRefresh) return;

        const interval = setInterval(() => {
            loadTradingData();
        }, refreshInterval);

        intervalRef.current = interval;

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, [autoRefresh, refreshInterval]);

    const handleWebSocketMessage = (data: any) => {
        switch (data.type) {
            case 'market_overview':
                setState(prev => ({ ...prev, marketOverview: data.data }));
                break;

            case 'top_movers':
                setState(prev => ({ ...prev, topMovers: data.data }));
                break;

            case 'trading_opportunities':
                setState(prev => ({ ...prev, tradingOpportunities: data.data }));
                break;

            case 'market_sentiment':
                setState(prev => ({ ...prev, marketSentiment: data.data }));
                break;

            case 'economic_calendar':
                setState(prev => ({ ...prev, economicCalendar: data.data }));
                break;

            default:
                console.log('Unknown message type:', data.type);
        }

        setState(prev => ({ ...prev, lastUpdate: new Date().toISOString() }));
    };

    const loadTradingData = async () => {
        try {
            setIsLoading(true);
            const response = await fetch('/api/trading/dashboard');
            const data = await response.json();

            if (data.success) {
                setState(prev => ({
                    ...prev,
                    marketOverview: data.data.marketOverview,
                    topMovers: data.data.topMovers,
                    tradingOpportunities: data.data.tradingOpportunities,
                    marketSentiment: data.data.marketSentiment,
                    economicCalendar: data.data.economicCalendar
                }));
            }
        } catch (error) {
            console.error('Error loading trading data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const getChangeColor = (value: number) => {
        if (value > 0) return 'text-green-600';
        if (value < 0) return 'text-red-600';
        return 'text-gray-600';
    };

    const getChangeIcon = (value: number) => {
        if (value > 0) return <TrendingUp className="h-4 w-4" />;
        if (value < 0) return <TrendingDown className="h-4 w-4" />;
        return <Minus className="h-4 w-4" />;
    };

    const getOpportunityColor = (type: string) => {
        switch (type) {
            case 'breakout': return 'bg-blue-100 text-blue-800';
            case 'reversal': return 'bg-purple-100 text-purple-800';
            case 'momentum': return 'bg-green-100 text-green-800';
            case 'support': return 'bg-yellow-100 text-yellow-800';
            case 'resistance': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getOpportunityIcon = (type: string) => {
        switch (type) {
            case 'breakout': return <ArrowUpRight className="h-4 w-4" />;
            case 'reversal': return <RotateCcw className="h-4 w-4" />;
            case 'momentum': return <Zap className="h-4 w-4" />;
            case 'support': return <Shield className="h-4 w-4" />;
            case 'resistance': return <AlertTriangle className="h-4 w-4" />;
            default: return <Info className="h-4 w-4" />;
        }
    };

    const getSentimentColor = (sentiment: string) => {
        switch (sentiment) {
            case 'bullish': return 'text-green-600';
            case 'bearish': return 'text-red-600';
            case 'neutral': return 'text-gray-600';
            default: return 'text-gray-600';
        }
    };

    const getSentimentIcon = (sentiment: string) => {
        switch (sentiment) {
            case 'bullish': return <TrendingUp className="h-4 w-4" />;
            case 'bearish': return <TrendingDown className="h-4 w-4" />;
            case 'neutral': return <Minus className="h-4 w-4" />;
            default: return <Info className="h-4 w-4" />;
        }
    };

    const getImpactColor = (impact: string) => {
        switch (impact) {
            case 'high': return 'bg-red-100 text-red-800';
            case 'medium': return 'bg-yellow-100 text-yellow-800';
            case 'low': return 'bg-green-100 text-green-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Trading Dashboard</h2>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${state.isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                            <span className="text-sm text-muted-foreground">
                                {state.isConnected ? 'Connected' : 'Disconnected'}
                            </span>
                        </div>
                        <Badge variant="outline">
                            Last updated: {formatDate(new Date(state.lastUpdate), 'HH:mm:ss')}
                        </Badge>
                    </div>
                </div>

                <div className="flex items-center space-x-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={loadTradingData}
                        disabled={isLoading}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setState(prev => ({ ...prev, showAdvanced: !prev.showAdvanced }))}
                    >
                        <Settings className="h-4 w-4 mr-2" />
                        {state.showAdvanced ? 'Simple' : 'Advanced'}
                    </Button>
                </div>
            </div>

            {/* Market Overview */}
            {state.marketOverview && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
                            <DollarSign className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                ${state.marketOverview.totalValue.toLocaleString()}
                            </div>
                            <div className={`text-xs flex items-center ${getChangeColor(state.marketOverview.dayChangePercent)}`}>
                                {getChangeIcon(state.marketOverview.dayChangePercent)}
                                <span className="ml-1">
                                    {state.marketOverview.dayChangePercent >= 0 ? '+' : ''}{state.marketOverview.dayChangePercent.toFixed(2)}%
                                </span>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Day Change</CardTitle>
                            <BarChart3 className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className={`text-2xl font-bold ${getChangeColor(state.marketOverview.dayChangePercent)}`}>
                                {state.marketOverview.dayChangePercent >= 0 ? '+' : ''}{state.marketOverview.dayChangePercent.toFixed(2)}%
                            </div>
                            <p className="text-xs text-muted-foreground">
                                ${state.marketOverview.dayChange.toLocaleString()}
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Week Change</CardTitle>
                            <Activity className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className={`text-2xl font-bold ${getChangeColor(state.marketOverview.weekChangePercent)}`}>
                                {state.marketOverview.weekChangePercent >= 0 ? '+' : ''}{state.marketOverview.weekChangePercent.toFixed(2)}%
                            </div>
                            <p className="text-xs text-muted-foreground">
                                ${state.marketOverview.weekChange.toLocaleString()}
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Month Change</CardTitle>
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className={`text-2xl font-bold ${getChangeColor(state.marketOverview.monthChangePercent)}`}>
                                {state.marketOverview.monthChangePercent >= 0 ? '+' : ''}{state.marketOverview.monthChangePercent.toFixed(2)}%
                            </div>
                            <p className="text-xs text-muted-foreground">
                                ${state.marketOverview.monthChange.toLocaleString()}
                            </p>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Main Content */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
                    <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
                    <TabsTrigger value="calendar">Economic Calendar</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Top Movers */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Top Movers</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {state.topMovers.slice(0, 10).map((mover) => (
                                        <div key={mover.symbol} className="flex items-center justify-between">
                                            <div className="flex items-center space-x-3">
                                                <div>
                                                    <p className="font-medium">{mover.symbol}</p>
                                                    <p className="text-sm text-muted-foreground">{mover.name}</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-medium">${mover.price.toFixed(2)}</p>
                                                <div className={`text-sm flex items-center ${getChangeColor(mover.changePercent)}`}>
                                                    {getChangeIcon(mover.changePercent)}
                                                    <span className="ml-1">
                                                        {mover.changePercent >= 0 ? '+' : ''}{mover.changePercent.toFixed(2)}%
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Market Sentiment */}
                        {state.marketSentiment && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Market Sentiment</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="text-center">
                                            <div className={`text-3xl font-bold ${getSentimentColor(state.marketSentiment.overall)}`}>
                                                {getSentimentIcon(state.marketSentiment.overall)}
                                                {state.marketSentiment.overall.toUpperCase()}
                                            </div>
                                            <p className="text-sm text-muted-foreground">
                                                Score: {state.marketSentiment.score}/100
                                            </p>
                                        </div>

                                        <div className="space-y-3">
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm">News Sentiment</span>
                                                <div className="flex items-center space-x-2">
                                                    <Progress value={state.marketSentiment.news} className="w-20" />
                                                    <span className="text-sm font-medium">{state.marketSentiment.news}%</span>
                                                </div>
                                            </div>

                                            <div className="flex justify-between items-center">
                                                <span className="text-sm">Social Sentiment</span>
                                                <div className="flex items-center space-x-2">
                                                    <Progress value={state.marketSentiment.social} className="w-20" />
                                                    <span className="text-sm font-medium">{state.marketSentiment.social}%</span>
                                                </div>
                                            </div>

                                            <div className="flex justify-between items-center">
                                                <span className="text-sm">Technical Sentiment</span>
                                                <div className="flex items-center space-x-2">
                                                    <Progress value={state.marketSentiment.technical} className="w-20" />
                                                    <span className="text-sm font-medium">{state.marketSentiment.technical}%</span>
                                                </div>
                                            </div>

                                            <div className="flex justify-between items-center">
                                                <span className="text-sm">Volume Sentiment</span>
                                                <div className="flex items-center space-x-2">
                                                    <Progress value={state.marketSentiment.volume} className="w-20" />
                                                    <span className="text-sm font-medium">{state.marketSentiment.volume}%</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </TabsContent>

                <TabsContent value="opportunities" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Trading Opportunities</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {state.tradingOpportunities.map((opportunity) => (
                                    <div key={opportunity.id} className="flex items-center justify-between p-4 border rounded-lg">
                                        <div className="flex items-center space-x-4">
                                            <Badge className={getOpportunityColor(opportunity.type)}>
                                                {getOpportunityIcon(opportunity.type)}
                                                <span className="ml-1 capitalize">{opportunity.type}</span>
                                            </Badge>
                                            <div>
                                                <p className="font-medium">{opportunity.symbol}</p>
                                                <p className="text-sm text-muted-foreground">{opportunity.description}</p>
                                                <p className="text-xs text-muted-foreground">{opportunity.timeframe}</p>
                                            </div>
                                        </div>

                                        <div className="text-right">
                                            <div className="flex items-center space-x-4">
                                                <div>
                                                    <p className="text-sm text-muted-foreground">Entry</p>
                                                    <p className="font-medium">${opportunity.entryPrice.toFixed(2)}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-muted-foreground">Target</p>
                                                    <p className="font-medium text-green-600">${opportunity.targetPrice.toFixed(2)}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-muted-foreground">Stop Loss</p>
                                                    <p className="font-medium text-red-600">${opportunity.stopLoss.toFixed(2)}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-muted-foreground">R/R</p>
                                                    <p className="font-medium">{opportunity.riskReward.toFixed(1)}:1</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-muted-foreground">Confidence</p>
                                                    <div className="flex items-center space-x-2">
                                                        <Progress value={opportunity.confidence} className="w-16" />
                                                        <span className="text-sm font-medium">{opportunity.confidence}%</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="sentiment" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Sentiment Analysis */}
                        {state.marketSentiment && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Sentiment Analysis</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="text-center">
                                            <div className={`text-4xl font-bold ${getSentimentColor(state.marketSentiment.overall)}`}>
                                                {getSentimentIcon(state.marketSentiment.overall)}
                                                {state.marketSentiment.overall.toUpperCase()}
                                            </div>
                                            <p className="text-lg text-muted-foreground">
                                                Overall Score: {state.marketSentiment.score}/100
                                            </p>
                                        </div>

                                        <div className="space-y-4">
                                            <div>
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="text-sm font-medium">News Sentiment</span>
                                                    <span className="text-sm font-medium">{state.marketSentiment.news}%</span>
                                                </div>
                                                <Progress value={state.marketSentiment.news} className="h-2" />
                                            </div>

                                            <div>
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="text-sm font-medium">Social Sentiment</span>
                                                    <span className="text-sm font-medium">{state.marketSentiment.social}%</span>
                                                </div>
                                                <Progress value={state.marketSentiment.social} className="h-2" />
                                            </div>

                                            <div>
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="text-sm font-medium">Technical Sentiment</span>
                                                    <span className="text-sm font-medium">{state.marketSentiment.technical}%</span>
                                                </div>
                                                <Progress value={state.marketSentiment.technical} className="h-2" />
                                            </div>

                                            <div>
                                                <div className="flex justify-between items-center mb-2">
                                                    <span className="text-sm font-medium">Volume Sentiment</span>
                                                    <span className="text-sm font-medium">{state.marketSentiment.volume}%</span>
                                                </div>
                                                <Progress value={state.marketSentiment.volume} className="h-2" />
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Sentiment Chart */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Sentiment Trends</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={300}>
                                    <AreaChart data={[
                                        { time: '00:00', news: 65, social: 70, technical: 60, volume: 55 },
                                        { time: '04:00', news: 68, social: 72, technical: 62, volume: 58 },
                                        { time: '08:00', news: 70, social: 75, technical: 65, volume: 60 },
                                        { time: '12:00', news: 72, social: 78, technical: 68, volume: 62 },
                                        { time: '16:00', news: 75, social: 80, technical: 70, volume: 65 },
                                        { time: '20:00', news: 73, social: 77, technical: 68, volume: 63 }
                                    ]}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="time" />
                                        <YAxis />
                                        <Tooltip />
                                        <Area type="monotone" dataKey="news" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                                        <Area type="monotone" dataKey="social" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                                        <Area type="monotone" dataKey="technical" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} />
                                        <Area type="monotone" dataKey="volume" stackId="1" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="calendar" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Economic Calendar</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {state.economicCalendar.map((event) => (
                                    <div key={event.id} className="flex items-center justify-between p-3 border rounded-lg">
                                        <div className="flex items-center space-x-4">
                                            <Badge className={getImpactColor(event.impact)}>
                                                {event.impact}
                                            </Badge>
                                            <div>
                                                <p className="font-medium">{event.event}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    {event.currency} • {formatDate(new Date(event.time), 'MMM dd, HH:mm')}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="text-right">
                                            <div className="flex items-center space-x-4">
                                                <div>
                                                    <p className="text-sm text-muted-foreground">Actual</p>
                                                    <p className="font-medium">{event.actual || 'N/A'}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-muted-foreground">Forecast</p>
                                                    <p className="font-medium">{event.forecast}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-muted-foreground">Previous</p>
                                                    <p className="font-medium">{event.previous}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};

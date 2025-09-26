import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
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
    Layers
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

interface EnhancedTradingInterfaceProps {
    symbol: string;
    className?: string;
}

interface MarketDepth {
    price: number;
    quantity: number;
    orders: number;
}

interface OrderBook {
    bids: MarketDepth[];
    asks: MarketDepth[];
    spread: number;
    lastUpdate: string;
}

interface TradingSignal {
    type: 'buy' | 'sell' | 'hold';
    strength: number;
    confidence: number;
    reason: string;
    timeframe: string;
}

interface RiskMetrics {
    positionSize: number;
    riskAmount: number;
    riskPercent: number;
    stopLoss: number;
    takeProfit: number;
    riskReward: number;
}

interface PriceAlert {
    id: string;
    type: 'above' | 'below' | 'change';
    price: number;
    isActive: boolean;
    message: string;
}

export const EnhancedTradingInterface: React.FC<EnhancedTradingInterfaceProps> = ({
    symbol,
    className = ''
}) => {
    const [selectedTab, setSelectedTab] = useState('overview');
    const [isConnected, setIsConnected] = useState(false);
    const [currentPrice, setCurrentPrice] = useState(0);
    const [priceChange, setPriceChange] = useState(0);
    const [priceChangePercent, setPriceChangePercent] = useState(0);
    const [volume, setVolume] = useState(0);
    const [marketCap, setMarketCap] = useState(0);
    const [orderBook, setOrderBook] = useState<OrderBook | null>(null);
    const [tradingSignals, setTradingSignals] = useState<TradingSignal[]>([]);
    const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
    const [priceAlerts, setPriceAlerts] = useState<PriceAlert[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(false);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState(1000);

    // Order form state
    const [orderType, setOrderType] = useState<'buy' | 'sell'>('buy');
    const [orderQuantity, setOrderQuantity] = useState('1');
    const [orderPrice, setOrderPrice] = useState('');
    const [isMarketOrder, setIsMarketOrder] = useState(true);
    const [stopLoss, setStopLoss] = useState('');
    const [takeProfit, setTakeProfit] = useState('');
    const [timeInForce, setTimeInForce] = useState('GTC');

    // Advanced features state
    const [showOrderBook, setShowOrderBook] = useState(true);
    const [showSignals, setShowSignals] = useState(true);
    const [showRisk, setShowRisk] = useState(true);
    const [showAlerts, setShowAlerts] = useState(true);
    const [chartTimeframe, setChartTimeframe] = useState('1m');
    const [showVolume, setShowVolume] = useState(true);
    const [showIndicators, setShowIndicators] = useState(true);

    const wsRef = useRef<WebSocket | null>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    // WebSocket connection for real-time data
    useEffect(() => {
        const ws = new WebSocket(`ws://localhost:8000/api/ws/trading/${symbol}`);

        ws.onopen = () => {
            setIsConnected(true);
            console.log('Trading WebSocket connected');
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };

        ws.onclose = () => {
            setIsConnected(false);
            console.log('Trading WebSocket disconnected');
        };

        ws.onerror = (error) => {
            console.error('Trading WebSocket error:', error);
            setIsConnected(false);
        };

        wsRef.current = ws;

        return () => {
            ws.close();
        };
    }, [symbol]);

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
            case 'price_update':
                setCurrentPrice(data.price);
                setPriceChange(data.change);
                setPriceChangePercent(data.changePercent);
                setVolume(data.volume);
                break;

            case 'order_book_update':
                setOrderBook(data.orderBook);
                break;

            case 'trading_signal':
                setTradingSignals(prev => [data.signal, ...prev.slice(0, 9)]);
                break;

            case 'price_alert':
                setPriceAlerts(prev => [data.alert, ...prev.slice(0, 9)]);
                break;

            default:
                console.log('Unknown message type:', data.type);
        }
    };

    const loadTradingData = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`/api/trading/data/${symbol}`);
            const data = await response.json();

            if (data.success) {
                setCurrentPrice(data.data.currentPrice);
                setPriceChange(data.data.priceChange);
                setPriceChangePercent(data.data.priceChangePercent);
                setVolume(data.data.volume);
                setMarketCap(data.data.marketCap);
                setOrderBook(data.data.orderBook);
                setTradingSignals(data.data.tradingSignals || []);
                setRiskMetrics(data.data.riskMetrics);
                setPriceAlerts(data.data.priceAlerts || []);
            }
        } catch (error) {
            console.error('Error loading trading data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const placeOrder = async () => {
        if (!orderQuantity || parseFloat(orderQuantity) <= 0) {
            alert('Please enter a valid quantity');
            return;
        }

        if (!isMarketOrder && (!orderPrice || parseFloat(orderPrice) <= 0)) {
            alert('Please enter a valid price for limit order');
            return;
        }

        try {
            const orderData = {
                symbol: symbol,
                side: orderType,
                quantity: parseInt(orderQuantity),
                orderType: isMarketOrder ? 'market' : 'limit',
                price: isMarketOrder ? undefined : parseFloat(orderPrice),
                stopLoss: stopLoss ? parseFloat(stopLoss) : undefined,
                takeProfit: takeProfit ? parseFloat(takeProfit) : undefined,
                timeInForce: timeInForce
            };

            const response = await fetch('/api/trading/place-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });

            const data = await response.json();
            if (data.success) {
                alert('Order placed successfully');
                // Reset form
                setOrderQuantity('1');
                setOrderPrice('');
                setStopLoss('');
                setTakeProfit('');
            } else {
                alert(data.message || 'Failed to place order');
            }
        } catch (error) {
            console.error('Error placing order:', error);
            alert('Failed to place order');
        }
    };

    const calculateRiskMetrics = () => {
        if (!orderQuantity || !currentPrice) return;

        const quantity = parseFloat(orderQuantity);
        const price = parseFloat(orderPrice) || currentPrice;
        const positionSize = quantity * price;
        const riskAmount = positionSize * 0.02; // 2% risk
        const riskPercent = (riskAmount / positionSize) * 100;
        const stopLossPrice = price * (1 - riskPercent / 100);
        const takeProfitPrice = price * (1 + riskPercent * 2 / 100); // 2:1 risk reward
        const riskReward = 2;

        setRiskMetrics({
            positionSize,
            riskAmount,
            riskPercent,
            stopLoss: stopLossPrice,
            takeProfit: takeProfitPrice,
            riskReward
        });
    };

    useEffect(() => {
        calculateRiskMetrics();
    }, [orderQuantity, orderPrice, currentPrice]);

    const getChangeColor = (value: number) => {
        if (value > 0) return 'text-green-600';
        if (value < 0) return 'text-red-600';
        return 'text-gray-600';
    };

    const getChangeIcon = (value: number) => {
        if (value > 0) return <TrendingUp className="h-4 w-4" />;
        if (value < 0) return <TrendingDown className="h-4 w-4" />;
        return null;
    };

    const getSignalColor = (type: string) => {
        switch (type) {
            case 'buy': return 'bg-green-100 text-green-800';
            case 'sell': return 'bg-red-100 text-red-800';
            case 'hold': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getSignalIcon = (type: string) => {
        switch (type) {
            case 'buy': return <TrendingUp className="h-4 w-4" />;
            case 'sell': return <TrendingDown className="h-4 w-4" />;
            case 'hold': return <Pause className="h-4 w-4" />;
            default: return <Info className="h-4 w-4" />;
        }
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">{symbol} Trading</h2>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                            <span className="text-sm text-muted-foreground">
                                {isConnected ? 'Connected' : 'Disconnected'}
                            </span>
                        </div>
                        <Badge variant="outline">
                            {formatDate(new Date(), 'HH:mm:ss')}
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
                        onClick={() => setShowAdvanced(!showAdvanced)}
                    >
                        <Settings className="h-4 w-4 mr-2" />
                        {showAdvanced ? 'Simple' : 'Advanced'}
                    </Button>
                </div>
            </div>

            {/* Price Display */}
            <Card>
                <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-3xl font-bold">{symbol}</h3>
                            <p className="text-sm text-muted-foreground">Current Price</p>
                        </div>
                        <div className="text-right">
                            <div className="text-4xl font-bold">
                                ${currentPrice.toFixed(2)}
                            </div>
                            <div className={`text-lg flex items-center justify-end ${getChangeColor(priceChangePercent)}`}>
                                {getChangeIcon(priceChangePercent)}
                                <span className="ml-1">
                                    {priceChangePercent >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%
                                </span>
                                <span className="ml-2">
                                    ({priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)})
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mt-6">
                        <div className="text-center">
                            <p className="text-sm text-muted-foreground">Volume</p>
                            <p className="text-lg font-semibold">{volume.toLocaleString()}</p>
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-muted-foreground">Market Cap</p>
                            <p className="text-lg font-semibold">${(marketCap / 1e9).toFixed(1)}B</p>
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-muted-foreground">Spread</p>
                            <p className="text-lg font-semibold">
                                {orderBook ? `$${orderBook.spread.toFixed(2)}` : 'N/A'}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Main Content */}
            <Tabs value={selectedTab} onValueChange={setSelectedTab}>
                <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="order">Order</TabsTrigger>
                    <TabsTrigger value="orderbook">Order Book</TabsTrigger>
                    <TabsTrigger value="signals">Signals</TabsTrigger>
                    <TabsTrigger value="risk">Risk</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Quick Order Form */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Quick Order</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex space-x-2">
                                        <Button
                                            variant={orderType === 'buy' ? 'default' : 'outline'}
                                            onClick={() => setOrderType('buy')}
                                            className="flex-1"
                                        >
                                            <TrendingUp className="h-4 w-4 mr-2" />
                                            Buy
                                        </Button>
                                        <Button
                                            variant={orderType === 'sell' ? 'default' : 'outline'}
                                            onClick={() => setOrderType('sell')}
                                            className="flex-1"
                                        >
                                            <TrendingDown className="h-4 w-4 mr-2" />
                                            Sell
                                        </Button>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label>Quantity</Label>
                                            <Input
                                                value={orderQuantity}
                                                onChange={(e) => setOrderQuantity(e.target.value)}
                                                type="number"
                                                placeholder="1"
                                            />
                                        </div>
                                        <div>
                                            <Label>Price</Label>
                                            <Input
                                                value={orderPrice}
                                                onChange={(e) => setOrderPrice(e.target.value)}
                                                type="number"
                                                placeholder={currentPrice.toFixed(2)}
                                                disabled={isMarketOrder}
                                            />
                                        </div>
                                    </div>

                                    <div className="flex items-center space-x-2">
                                        <Switch
                                            checked={isMarketOrder}
                                            onCheckedChange={setIsMarketOrder}
                                        />
                                        <Label>Market Order</Label>
                                    </div>

                                    <Button onClick={placeOrder} className="w-full">
                                        <Target className="h-4 w-4 mr-2" />
                                        Place {orderType.toUpperCase()} Order
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Trading Signals */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Brain className="h-5 w-5" />
                                    <span>Trading Signals</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {tradingSignals.slice(0, 5).map((signal, index) => (
                                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                                            <div className="flex items-center space-x-3">
                                                <Badge className={getSignalColor(signal.type)}>
                                                    {getSignalIcon(signal.type)}
                                                    <span className="ml-1 capitalize">{signal.type}</span>
                                                </Badge>
                                                <div>
                                                    <p className="text-sm font-medium">{signal.reason}</p>
                                                    <p className="text-xs text-muted-foreground">{signal.timeframe}</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm font-medium">{signal.confidence}%</p>
                                                <Progress value={signal.confidence} className="w-16 h-2" />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="order" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Order Form */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Place Order</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex space-x-2">
                                        <Button
                                            variant={orderType === 'buy' ? 'default' : 'outline'}
                                            onClick={() => setOrderType('buy')}
                                            className="flex-1"
                                        >
                                            <TrendingUp className="h-4 w-4 mr-2" />
                                            Buy
                                        </Button>
                                        <Button
                                            variant={orderType === 'sell' ? 'default' : 'outline'}
                                            onClick={() => setOrderType('sell')}
                                            className="flex-1"
                                        >
                                            <TrendingDown className="h-4 w-4 mr-2" />
                                            Sell
                                        </Button>
                                    </div>

                                    <div>
                                        <Label>Quantity</Label>
                                        <Input
                                            value={orderQuantity}
                                            onChange={(e) => setOrderQuantity(e.target.value)}
                                            type="number"
                                            placeholder="1"
                                        />
                                    </div>

                                    <div className="flex items-center space-x-2">
                                        <Switch
                                            checked={isMarketOrder}
                                            onCheckedChange={setIsMarketOrder}
                                        />
                                        <Label>Market Order</Label>
                                    </div>

                                    {!isMarketOrder && (
                                        <div>
                                            <Label>Limit Price</Label>
                                            <Input
                                                value={orderPrice}
                                                onChange={(e) => setOrderPrice(e.target.value)}
                                                type="number"
                                                placeholder={currentPrice.toFixed(2)}
                                            />
                                        </div>
                                    )}

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label>Stop Loss</Label>
                                            <Input
                                                value={stopLoss}
                                                onChange={(e) => setStopLoss(e.target.value)}
                                                type="number"
                                                placeholder="0.00"
                                            />
                                        </div>
                                        <div>
                                            <Label>Take Profit</Label>
                                            <Input
                                                value={takeProfit}
                                                onChange={(e) => setTakeProfit(e.target.value)}
                                                type="number"
                                                placeholder="0.00"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <Label>Time in Force</Label>
                                        <select
                                            value={timeInForce}
                                            onChange={(e) => setTimeInForce(e.target.value)}
                                            className="w-full p-2 border rounded-md"
                                        >
                                            <option value="GTC">Good Till Cancelled</option>
                                            <option value="IOC">Immediate or Cancel</option>
                                            <option value="FOK">Fill or Kill</option>
                                        </select>
                                    </div>

                                    <Button onClick={placeOrder} className="w-full">
                                        <Target className="h-4 w-4 mr-2" />
                                        Place {orderType.toUpperCase()} Order
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Risk Metrics */}
                        {riskMetrics && (
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center space-x-2">
                                        <Shield className="h-5 w-5" />
                                        <span>Risk Metrics</span>
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Position Size</p>
                                                <p className="text-lg font-semibold">${riskMetrics.positionSize.toFixed(2)}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Risk Amount</p>
                                                <p className="text-lg font-semibold text-red-600">${riskMetrics.riskAmount.toFixed(2)}</p>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Stop Loss</p>
                                                <p className="text-lg font-semibold">${riskMetrics.stopLoss.toFixed(2)}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Take Profit</p>
                                                <p className="text-lg font-semibold text-green-600">${riskMetrics.takeProfit.toFixed(2)}</p>
                                            </div>
                                        </div>

                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Risk/Reward Ratio</p>
                                            <p className="text-2xl font-bold">{riskMetrics.riskReward.toFixed(1)}:1</p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </TabsContent>

                <TabsContent value="orderbook" className="space-y-4">
                    {orderBook && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Order Book</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 gap-4">
                                    {/* Bids */}
                                    <div>
                                        <h4 className="font-semibold text-green-600 mb-2">Bids</h4>
                                        <div className="space-y-1">
                                            {orderBook.bids.slice(0, 10).map((bid, index) => (
                                                <div key={index} className="flex justify-between text-sm">
                                                    <span className="text-green-600">${bid.price.toFixed(2)}</span>
                                                    <span>{bid.quantity.toLocaleString()}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Asks */}
                                    <div>
                                        <h4 className="font-semibold text-red-600 mb-2">Asks</h4>
                                        <div className="space-y-1">
                                            {orderBook.asks.slice(0, 10).map((ask, index) => (
                                                <div key={index} className="flex justify-between text-sm">
                                                    <span className="text-red-600">${ask.price.toFixed(2)}</span>
                                                    <span>{ask.quantity.toLocaleString()}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="signals" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>All Trading Signals</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {tradingSignals.map((signal, index) => (
                                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                                        <div className="flex items-center space-x-4">
                                            <Badge className={getSignalColor(signal.type)}>
                                                {getSignalIcon(signal.type)}
                                                <span className="ml-1 capitalize">{signal.type}</span>
                                            </Badge>
                                            <div>
                                                <p className="font-medium">{signal.reason}</p>
                                                <p className="text-sm text-muted-foreground">{signal.timeframe}</p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-sm font-medium">{signal.confidence}%</p>
                                            <Progress value={signal.confidence} className="w-20 h-2" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="risk" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Risk Calculator */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Risk Calculator</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div>
                                        <Label>Risk Percentage</Label>
                                        <Slider
                                            value={[2]}
                                            onValueChange={([value]) => {
                                                // Update risk percentage
                                            }}
                                            max={10}
                                            step={0.5}
                                            className="w-full"
                                        />
                                        <p className="text-sm text-muted-foreground">2% of portfolio</p>
                                    </div>

                                    <div>
                                        <Label>Position Size</Label>
                                        <Input
                                            value={orderQuantity}
                                            onChange={(e) => setOrderQuantity(e.target.value)}
                                            type="number"
                                            placeholder="1"
                                        />
                                    </div>

                                    <div>
                                        <Label>Entry Price</Label>
                                        <Input
                                            value={orderPrice}
                                            onChange={(e) => setOrderPrice(e.target.value)}
                                            type="number"
                                            placeholder={currentPrice.toFixed(2)}
                                        />
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label>Stop Loss</Label>
                                            <Input
                                                value={stopLoss}
                                                onChange={(e) => setStopLoss(e.target.value)}
                                                type="number"
                                                placeholder="0.00"
                                            />
                                        </div>
                                        <div>
                                            <Label>Take Profit</Label>
                                            <Input
                                                value={takeProfit}
                                                onChange={(e) => setTakeProfit(e.target.value)}
                                                type="number"
                                                placeholder="0.00"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Risk Summary */}
                        {riskMetrics && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Risk Summary</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Total Risk</p>
                                            <p className="text-3xl font-bold text-red-600">
                                                ${riskMetrics.riskAmount.toFixed(2)}
                                            </p>
                                            <p className="text-sm text-muted-foreground">
                                                {riskMetrics.riskPercent.toFixed(1)}% of position
                                            </p>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="text-center p-3 border rounded">
                                                <p className="text-sm text-muted-foreground">Stop Loss</p>
                                                <p className="text-lg font-semibold">${riskMetrics.stopLoss.toFixed(2)}</p>
                                            </div>
                                            <div className="text-center p-3 border rounded">
                                                <p className="text-sm text-muted-foreground">Take Profit</p>
                                                <p className="text-lg font-semibold">${riskMetrics.takeProfit.toFixed(2)}</p>
                                            </div>
                                        </div>

                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Risk/Reward Ratio</p>
                                            <p className="text-2xl font-bold">{riskMetrics.riskReward.toFixed(1)}:1</p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
};

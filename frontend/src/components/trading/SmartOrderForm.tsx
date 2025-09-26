import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    BarChart3,
    Target,
    Shield,
    Clock,
    RefreshCw,
    Calculator,
    Zap,
    Activity,
    AlertTriangle,
    CheckCircle,
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
    ChevronRight,
    Eye,
    EyeOff,
    Volume2,
    VolumeX,
    ArrowUpRight,
    ArrowDownRight,
    Settings,
    Bell,
    Star,
    Share2,
    Download
} from 'lucide-react';
// Simple date formatting function to avoid date-fns dependency
const formatDate = (date: Date) => {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

interface SmartOrderFormProps {
    symbol: string;
    currentPrice: number;
    onOrderPlaced: (order: any) => void;
    onClose: () => void;
    className?: string;
}

interface OrderSuggestion {
    type: 'buy' | 'sell';
    quantity: number;
    price: number;
    reason: string;
    confidence: number;
    riskReward: number;
    stopLoss: number;
    takeProfit: number;
}

interface RiskAnalysis {
    positionSize: number;
    riskAmount: number;
    riskPercent: number;
    maxLoss: number;
    maxGain: number;
    probabilityOfProfit: number;
    expectedValue: number;
    sharpeRatio: number;
}

interface MarketConditions {
    volatility: number;
    trend: 'up' | 'down' | 'sideways';
    support: number;
    resistance: number;
    volume: number;
    momentum: number;
}

interface SmartOrderFormState {
    orderType: 'buy' | 'sell';
    quantity: string;
    price: string;
    isMarketOrder: boolean;
    stopLoss: string;
    takeProfit: string;
    timeInForce: string;
    orderSuggestion: OrderSuggestion | null;
    riskAnalysis: RiskAnalysis | null;
    marketConditions: MarketConditions | null;
    showAdvanced: boolean;
    showRiskAnalysis: boolean;
    showMarketConditions: boolean;
    autoCalculate: boolean;
    riskPercentage: number;
    positionSize: number;
    totalValue: number;
}

export const SmartOrderForm: React.FC<SmartOrderFormProps> = ({
    symbol,
    currentPrice,
    onOrderPlaced,
    onClose,
    className = ''
}) => {
    const [state, setState] = useState<SmartOrderFormState>({
        orderType: 'buy',
        quantity: '1',
        price: currentPrice.toFixed(2),
        isMarketOrder: false,
        stopLoss: '',
        takeProfit: '',
        timeInForce: 'GTC',
        orderSuggestion: null,
        riskAnalysis: null,
        marketConditions: null,
        showAdvanced: false,
        showRiskAnalysis: true,
        showMarketConditions: true,
        autoCalculate: true,
        riskPercentage: 2,
        positionSize: 0,
        totalValue: 0
    });

    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('basic');

    // Load smart suggestions and analysis
    useEffect(() => {
        loadSmartAnalysis();
    }, [symbol, currentPrice]);

    // Auto-calculate when inputs change
    useEffect(() => {
        if (state.autoCalculate) {
            calculateOrderSuggestion();
            calculateRiskAnalysis();
        }
    }, [state.quantity, state.price, state.orderType, state.riskPercentage]);

    const loadSmartAnalysis = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`/api/trading/smart-analysis/${symbol}?price=${currentPrice}`);
            const data = await response.json();

            if (data.success) {
                setState(prev => ({
                    ...prev,
                    orderSuggestion: data.data.orderSuggestion,
                    riskAnalysis: data.data.riskAnalysis,
                    marketConditions: data.data.marketConditions
                }));
            }
        } catch (error) {
            console.error('Error loading smart analysis:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const calculateOrderSuggestion = async () => {
        try {
            const response = await fetch('/api/trading/calculate-suggestion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol: symbol,
                    currentPrice: currentPrice,
                    orderType: state.orderType,
                    quantity: parseFloat(state.quantity) || 1,
                    riskPercentage: state.riskPercentage
                })
            });

            const data = await response.json();
            if (data.success) {
                setState(prev => ({
                    ...prev,
                    orderSuggestion: data.data
                }));
            }
        } catch (error) {
            console.error('Error calculating order suggestion:', error);
        }
    };

    const calculateRiskAnalysis = () => {
        if (!state.quantity || !state.price) return;

        const quantity = parseFloat(state.quantity);
        const price = parseFloat(state.price);
        const positionSize = quantity * price;
        const riskAmount = positionSize * (state.riskPercentage / 100);
        const stopLoss = state.stopLoss ? parseFloat(state.stopLoss) : price * (1 - state.riskPercentage / 100);
        const takeProfit = state.takeProfit ? parseFloat(state.takeProfit) : price * (1 + state.riskPercentage * 2 / 100);

        const maxLoss = Math.abs(price - stopLoss) * quantity;
        const maxGain = Math.abs(takeProfit - price) * quantity;
        const probabilityOfProfit = 0.6; // This would come from ML model
        const expectedValue = (maxGain * probabilityOfProfit) - (maxLoss * (1 - probabilityOfProfit));
        const sharpeRatio = expectedValue / Math.sqrt(maxLoss);

        setState(prev => ({
            ...prev,
            riskAnalysis: {
                positionSize,
                riskAmount,
                riskPercent: state.riskPercentage,
                maxLoss,
                maxGain,
                probabilityOfProfit,
                expectedValue,
                sharpeRatio
            },
            positionSize,
            totalValue: positionSize
        }));
    };

    const handleOrderSubmit = async () => {
        if (!state.quantity || parseFloat(state.quantity) <= 0) {
            alert('Please enter a valid quantity');
            return;
        }

        if (!state.isMarketOrder && (!state.price || parseFloat(state.price) <= 0)) {
            alert('Please enter a valid price for limit order');
            return;
        }

        try {
            const orderData = {
                symbol: symbol,
                side: state.orderType,
                quantity: parseInt(state.quantity),
                orderType: state.isMarketOrder ? 'market' : 'limit',
                price: state.isMarketOrder ? undefined : parseFloat(state.price),
                stopLoss: state.stopLoss ? parseFloat(state.stopLoss) : undefined,
                takeProfit: state.takeProfit ? parseFloat(state.takeProfit) : undefined,
                timeInForce: state.timeInForce
            };

            const response = await fetch('/api/trading/place-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });

            const data = await response.json();
            if (data.success) {
                onOrderPlaced(data.data);
                onClose();
            } else {
                alert(data.message || 'Failed to place order');
            }
        } catch (error) {
            console.error('Error placing order:', error);
            alert('Failed to place order');
        }
    };

    const applySuggestion = () => {
        if (state.orderSuggestion) {
            setState(prev => ({
                ...prev,
                orderType: state.orderSuggestion!.type,
                quantity: state.orderSuggestion!.quantity.toString(),
                price: state.orderSuggestion!.price.toString(),
                stopLoss: state.orderSuggestion!.stopLoss.toString(),
                takeProfit: state.orderSuggestion!.takeProfit.toString()
            }));
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

    const getTrendColor = (trend: string) => {
        switch (trend) {
            case 'up': return 'text-green-600';
            case 'down': return 'text-red-600';
            case 'sideways': return 'text-gray-600';
            default: return 'text-gray-600';
        }
    };

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case 'up': return <TrendingUp className="h-4 w-4" />;
            case 'down': return <TrendingDown className="h-4 w-4" />;
            case 'sideways': return <Minus className="h-4 w-4" />;
            default: return <Info className="h-4 w-4" />;
        }
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Smart Order Form</h2>
                    <p className="text-muted-foreground">
                        {symbol} • Current Price: ${currentPrice.toFixed(2)}
                    </p>
                </div>

                <div className="flex items-center space-x-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={loadSmartAnalysis}
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

            {/* Smart Suggestion */}
            {state.orderSuggestion && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <Brain className="h-5 w-5" />
                            <span>AI Suggestion</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <Badge className={state.orderSuggestion.type === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                                    {state.orderSuggestion.type === 'buy' ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                                    <span className="ml-1 uppercase">{state.orderSuggestion.type}</span>
                                </Badge>
                                <div>
                                    <p className="font-medium">{state.orderSuggestion.reason}</p>
                                    <p className="text-sm text-muted-foreground">
                                        Confidence: {state.orderSuggestion.confidence}% • R/R: {state.orderSuggestion.riskReward.toFixed(1)}:1
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center space-x-2">
                                <div className="text-right">
                                    <p className="text-sm text-muted-foreground">Suggested</p>
                                    <p className="font-medium">
                                        {state.orderSuggestion.quantity} @ ${state.orderSuggestion.price.toFixed(2)}
                                    </p>
                                </div>
                                <Button onClick={applySuggestion} size="sm">
                                    <Check className="h-4 w-4 mr-2" />
                                    Apply
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Main Content */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="basic">Basic</TabsTrigger>
                    <TabsTrigger value="advanced">Advanced</TabsTrigger>
                    <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
                    <TabsTrigger value="market">Market Conditions</TabsTrigger>
                </TabsList>

                <TabsContent value="basic" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Order Form */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Order Details</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex space-x-2">
                                        <Button
                                            variant={state.orderType === 'buy' ? 'default' : 'outline'}
                                            onClick={() => setState(prev => ({ ...prev, orderType: 'buy' }))}
                                            className="flex-1"
                                        >
                                            <TrendingUp className="h-4 w-4 mr-2" />
                                            Buy
                                        </Button>
                                        <Button
                                            variant={state.orderType === 'sell' ? 'default' : 'outline'}
                                            onClick={() => setState(prev => ({ ...prev, orderType: 'sell' }))}
                                            className="flex-1"
                                        >
                                            <TrendingDown className="h-4 w-4 mr-2" />
                                            Sell
                                        </Button>
                                    </div>

                                    <div>
                                        <Label>Quantity</Label>
                                        <Input
                                            value={state.quantity}
                                            onChange={(e) => setState(prev => ({ ...prev, quantity: e.target.value }))}
                                            type="number"
                                            placeholder="1"
                                        />
                                    </div>

                                    <div className="flex items-center space-x-2">
                                        <Switch
                                            checked={state.isMarketOrder}
                                            onCheckedChange={(checked) => setState(prev => ({ ...prev, isMarketOrder: checked }))}
                                        />
                                        <Label>Market Order</Label>
                                    </div>

                                    {!state.isMarketOrder && (
                                        <div>
                                            <Label>Limit Price</Label>
                                            <Input
                                                value={state.price}
                                                onChange={(e) => setState(prev => ({ ...prev, price: e.target.value }))}
                                                type="number"
                                                placeholder={currentPrice.toFixed(2)}
                                            />
                                        </div>
                                    )}

                                    <Button onClick={handleOrderSubmit} className="w-full">
                                        <Target className="h-4 w-4 mr-2" />
                                        Place {state.orderType.toUpperCase()} Order
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Quick Risk Summary */}
                        {state.riskAnalysis && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Risk Summary</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Position Size</p>
                                                <p className="text-lg font-semibold">${state.riskAnalysis.positionSize.toFixed(2)}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Risk Amount</p>
                                                <p className="text-lg font-semibold text-red-600">${state.riskAnalysis.riskAmount.toFixed(2)}</p>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Max Loss</p>
                                                <p className="text-lg font-semibold text-red-600">${state.riskAnalysis.maxLoss.toFixed(2)}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Max Gain</p>
                                                <p className="text-lg font-semibold text-green-600">${state.riskAnalysis.maxGain.toFixed(2)}</p>
                                            </div>
                                        </div>

                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Probability of Profit</p>
                                            <p className="text-2xl font-bold">{(state.riskAnalysis.probabilityOfProfit * 100).toFixed(1)}%</p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </TabsContent>

                <TabsContent value="advanced" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Advanced Order Settings */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Advanced Settings</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label>Stop Loss</Label>
                                            <Input
                                                value={state.stopLoss}
                                                onChange={(e) => setState(prev => ({ ...prev, stopLoss: e.target.value }))}
                                                type="number"
                                                placeholder="0.00"
                                            />
                                        </div>
                                        <div>
                                            <Label>Take Profit</Label>
                                            <Input
                                                value={state.takeProfit}
                                                onChange={(e) => setState(prev => ({ ...prev, takeProfit: e.target.value }))}
                                                type="number"
                                                placeholder="0.00"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <Label>Time in Force</Label>
                                        <select
                                            value={state.timeInForce}
                                            onChange={(e) => setState(prev => ({ ...prev, timeInForce: e.target.value }))}
                                            className="w-full p-2 border rounded-md"
                                        >
                                            <option value="GTC">Good Till Cancelled</option>
                                            <option value="IOC">Immediate or Cancel</option>
                                            <option value="FOK">Fill or Kill</option>
                                            <option value="DAY">Day Order</option>
                                        </select>
                                    </div>

                                    <div className="flex items-center space-x-2">
                                        <Switch
                                            checked={state.autoCalculate}
                                            onCheckedChange={(checked) => setState(prev => ({ ...prev, autoCalculate: checked }))}
                                        />
                                        <Label>Auto-calculate risk</Label>
                                    </div>

                                    <div>
                                        <Label>Risk Percentage</Label>
                                        <Slider
                                            value={[state.riskPercentage]}
                                            onValueChange={([value]) => setState(prev => ({ ...prev, riskPercentage: value }))}
                                            max={10}
                                            step={0.5}
                                            className="w-full"
                                        />
                                        <p className="text-sm text-muted-foreground">{state.riskPercentage}% of position</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Order Summary */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Order Summary</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex justify-between">
                                        <span className="text-sm text-muted-foreground">Symbol</span>
                                        <span className="font-medium">{symbol}</span>
                                    </div>

                                    <div className="flex justify-between">
                                        <span className="text-sm text-muted-foreground">Side</span>
                                        <span className="font-medium uppercase">{state.orderType}</span>
                                    </div>

                                    <div className="flex justify-between">
                                        <span className="text-sm text-muted-foreground">Quantity</span>
                                        <span className="font-medium">{state.quantity}</span>
                                    </div>

                                    <div className="flex justify-between">
                                        <span className="text-sm text-muted-foreground">Price</span>
                                        <span className="font-medium">
                                            {state.isMarketOrder ? 'Market' : `$${state.price}`}
                                        </span>
                                    </div>

                                    <div className="flex justify-between">
                                        <span className="text-sm text-muted-foreground">Total Value</span>
                                        <span className="font-medium">${state.totalValue.toFixed(2)}</span>
                                    </div>

                                    {state.stopLoss && (
                                        <div className="flex justify-between">
                                            <span className="text-sm text-muted-foreground">Stop Loss</span>
                                            <span className="font-medium text-red-600">${state.stopLoss}</span>
                                        </div>
                                    )}

                                    {state.takeProfit && (
                                        <div className="flex justify-between">
                                            <span className="text-sm text-muted-foreground">Take Profit</span>
                                            <span className="font-medium text-green-600">${state.takeProfit}</span>
                                        </div>
                                    )}

                                    <div className="flex justify-between">
                                        <span className="text-sm text-muted-foreground">Time in Force</span>
                                        <span className="font-medium">{state.timeInForce}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="risk" className="space-y-4">
                    {state.riskAnalysis && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Risk Metrics */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Risk Metrics</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Position Size</p>
                                                <p className="text-lg font-semibold">${state.riskAnalysis.positionSize.toFixed(2)}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Risk Amount</p>
                                                <p className="text-lg font-semibold text-red-600">${state.riskAnalysis.riskAmount.toFixed(2)}</p>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Max Loss</p>
                                                <p className="text-lg font-semibold text-red-600">${state.riskAnalysis.maxLoss.toFixed(2)}</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Max Gain</p>
                                                <p className="text-lg font-semibold text-green-600">${state.riskAnalysis.maxGain.toFixed(2)}</p>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-sm text-muted-foreground">Probability of Profit</p>
                                                <p className="text-lg font-semibold">{(state.riskAnalysis.probabilityOfProfit * 100).toFixed(1)}%</p>
                                            </div>
                                            <div>
                                                <p className="text-sm text-muted-foreground">Expected Value</p>
                                                <p className={`text-lg font-semibold ${getChangeColor(state.riskAnalysis.expectedValue)}`}>
                                                    ${state.riskAnalysis.expectedValue.toFixed(2)}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                                            <p className="text-2xl font-bold">{state.riskAnalysis.sharpeRatio.toFixed(2)}</p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Risk Visualization */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Risk Visualization</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Risk vs Reward</p>
                                            <div className="flex items-center justify-center space-x-4 mt-4">
                                                <div className="text-center">
                                                    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                                                        <span className="text-red-600 font-bold">${state.riskAnalysis.maxLoss.toFixed(0)}</span>
                                                    </div>
                                                    <p className="text-xs text-muted-foreground mt-2">Max Loss</p>
                                                </div>
                                                <div className="text-center">
                                                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                                                        <span className="text-green-600 font-bold">${state.riskAnalysis.maxGain.toFixed(0)}</span>
                                                    </div>
                                                    <p className="text-xs text-muted-foreground mt-2">Max Gain</p>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Probability Distribution</p>
                                            <div className="flex items-center justify-center space-x-4 mt-4">
                                                <div className="text-center">
                                                    <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                                                        <span className="text-red-600 font-bold">
                                                            {((1 - state.riskAnalysis.probabilityOfProfit) * 100).toFixed(0)}%
                                                        </span>
                                                    </div>
                                                    <p className="text-xs text-muted-foreground mt-2">Loss</p>
                                                </div>
                                                <div className="text-center">
                                                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                                                        <span className="text-green-600 font-bold">
                                                            {(state.riskAnalysis.probabilityOfProfit * 100).toFixed(0)}%
                                                        </span>
                                                    </div>
                                                    <p className="text-xs text-muted-foreground mt-2">Profit</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="market" className="space-y-4">
                    {state.marketConditions && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Market Conditions */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Market Conditions</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Trend</span>
                                            <div className="flex items-center space-x-2">
                                                <span className={`font-medium ${getTrendColor(state.marketConditions.trend)}`}>
                                                    {getTrendIcon(state.marketConditions.trend)}
                                                    {state.marketConditions.trend.toUpperCase()}
                                                </span>
                                            </div>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Volatility</span>
                                            <div className="flex items-center space-x-2">
                                                <Progress value={state.marketConditions.volatility} className="w-20" />
                                                <span className="font-medium">{state.marketConditions.volatility}%</span>
                                            </div>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Volume</span>
                                            <div className="flex items-center space-x-2">
                                                <Progress value={state.marketConditions.volume} className="w-20" />
                                                <span className="font-medium">{state.marketConditions.volume}%</span>
                                            </div>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Momentum</span>
                                            <div className="flex items-center space-x-2">
                                                <Progress value={state.marketConditions.momentum} className="w-20" />
                                                <span className="font-medium">{state.marketConditions.momentum}%</span>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Support & Resistance */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Support & Resistance</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Support Level</span>
                                            <span className="font-medium text-green-600">${state.marketConditions.support.toFixed(2)}</span>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Resistance Level</span>
                                            <span className="font-medium text-red-600">${state.marketConditions.resistance.toFixed(2)}</span>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <span className="text-sm text-muted-foreground">Current Price</span>
                                            <span className="font-medium">${currentPrice.toFixed(2)}</span>
                                        </div>

                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Distance to Support</p>
                                            <p className="text-lg font-semibold text-green-600">
                                                {((currentPrice - state.marketConditions.support) / currentPrice * 100).toFixed(1)}%
                                            </p>
                                        </div>

                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">Distance to Resistance</p>
                                            <p className="text-lg font-semibold text-red-600">
                                                {((state.marketConditions.resistance - currentPrice) / currentPrice * 100).toFixed(1)}%
                                            </p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
};

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
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
    Play,
    Pause,
    Square,
    RotateCcw,
    Download,
    Settings,
    TrendingUp,
    TrendingDown,
    Target,
    Shield,
    BarChart3,
    Clock,
    DollarSign,
    AlertTriangle,
    CheckCircle,
    RefreshCw
} from 'lucide-react';
// Simple date formatting function to avoid date-fns dependency
const formatDate = (date: Date, format?: string) => {
    if (format === 'MMM dd') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else if (format === 'MMM dd, yyyy') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

interface BacktestStrategy {
    id: string;
    name: string;
    description: string;
    type: 'ma_crossover' | 'mean_reversion' | 'momentum' | 'buy_hold' | 'custom';
    parameters: Record<string, any>;
    isCustom: boolean;
}

interface BacktestResult {
    id: string;
    strategy: string;
    symbol: string;
    startDate: string;
    endDate: string;
    initialCapital: number;
    finalCapital: number;
    totalReturn: number;
    totalReturnPercent: number;
    annualizedReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
    totalTrades: number;
    avgWin: number;
    avgLoss: number;
    profitFactor: number;
    trades: Array<{
        id: string;
        entryDate: string;
        exitDate: string;
        entryPrice: number;
        exitPrice: number;
        quantity: number;
        pnl: number;
        pnlPercent: number;
        type: 'buy' | 'sell';
    }>;
    equityCurve: Array<{
        date: string;
        value: number;
        drawdown: number;
    }>;
    benchmark: {
        symbol: string;
        return: number;
        returnPercent: number;
    };
}

interface BacktestingInterfaceProps {
    className?: string;
}

export const BacktestingInterface: React.FC<BacktestingInterfaceProps> = ({ className = '' }) => {
    const [strategies, setStrategies] = useState<BacktestStrategy[]>([]);
    const [selectedStrategy, setSelectedStrategy] = useState<BacktestStrategy | null>(null);
    const [backtestResults, setBacktestResults] = useState<BacktestResult[]>([]);
    const [currentBacktest, setCurrentBacktest] = useState<BacktestResult | null>(null);
    const [isRunning, setIsRunning] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('strategy');

    // Backtest parameters
    const [symbol, setSymbol] = useState('AAPL');
    const [startDate, setStartDate] = useState('2023-01-01');
    const [endDate, setEndDate] = useState('2023-12-31');
    const [initialCapital, setInitialCapital] = useState(10000);
    const [benchmark, setBenchmark] = useState('SPY');

    // Strategy parameters
    const [strategyParams, setStrategyParams] = useState<Record<string, any>>({});

    // Load strategies and results
    useEffect(() => {
        loadStrategies();
        loadBacktestResults();
    }, []);

    const loadStrategies = async () => {
        try {
            const response = await fetch('/api/backtesting/strategies');
            const data = await response.json();
            setStrategies(data.data || []);
            if (data.data && data.data.length > 0) {
                setSelectedStrategy(data.data[0]);
                setStrategyParams(data.data[0].parameters || {});
            }
        } catch (error) {
            console.error('Error loading strategies:', error);
        }
    };

    const loadBacktestResults = async () => {
        try {
            const response = await fetch('/api/backtesting/results');
            const data = await response.json();
            setBacktestResults(data.data || []);
        } catch (error) {
            console.error('Error loading backtest results:', error);
        }
    };

    const runBacktest = async () => {
        if (!selectedStrategy) return;

        try {
            setIsRunning(true);
            setIsLoading(true);

            const response = await fetch('/api/backtesting/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    strategy: selectedStrategy.type,
                    symbol: symbol,
                    startDate: startDate,
                    endDate: endDate,
                    initialCapital: initialCapital,
                    benchmark: benchmark,
                    parameters: strategyParams
                })
            });

            const data = await response.json();
            if (data.success) {
                setCurrentBacktest(data.data);
                loadBacktestResults();
            }
        } catch (error) {
            console.error('Error running backtest:', error);
        } finally {
            setIsRunning(false);
            setIsLoading(false);
        }
    };

    const saveStrategy = async () => {
        if (!selectedStrategy) return;

        try {
            const response = await fetch('/api/backtesting/strategies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: selectedStrategy.name,
                    description: selectedStrategy.description,
                    type: selectedStrategy.type,
                    parameters: strategyParams
                })
            });

            if (response.ok) {
                loadStrategies();
            }
        } catch (error) {
            console.error('Error saving strategy:', error);
        }
    };

    const exportResults = async () => {
        if (!currentBacktest) return;

        try {
            const response = await fetch(`/api/backtesting/results/${currentBacktest.id}/export`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `backtest_${currentBacktest.strategy}_${currentBacktest.symbol}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error exporting results:', error);
        }
    };

    const getPerformanceColor = (value: number) => {
        if (value > 0) return 'text-green-600';
        if (value < 0) return 'text-red-600';
        return 'text-gray-600';
    };

    const getPerformanceIcon = (value: number) => {
        if (value > 0) return <TrendingUp className="h-4 w-4" />;
        if (value < 0) return <TrendingDown className="h-4 w-4" />;
        return <BarChart3 className="h-4 w-4" />;
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Strategy Backtesting</h2>
                    <p className="text-muted-foreground">
                        Test and optimize your trading strategies with historical data
                    </p>
                </div>

                <div className="flex items-center space-x-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={loadBacktestResults}
                        disabled={isLoading}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    {currentBacktest && (
                        <Button variant="outline" size="sm" onClick={exportResults}>
                            <Download className="h-4 w-4 mr-2" />
                            Export
                        </Button>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="strategy">Strategy Builder</TabsTrigger>
                    <TabsTrigger value="results">Results</TabsTrigger>
                    <TabsTrigger value="comparison">Comparison</TabsTrigger>
                </TabsList>

                <TabsContent value="strategy" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Strategy Configuration */}
                        <div className="lg:col-span-2 space-y-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Strategy Configuration</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {/* Strategy Selection */}
                                    <div className="space-y-2">
                                        <Label>Strategy Type</Label>
                                        <Select
                                            value={selectedStrategy?.type || ''}
                                            onValueChange={(value) => {
                                                const strategy = strategies.find(s => s.type === value);
                                                setSelectedStrategy(strategy || null);
                                                setStrategyParams(strategy?.parameters || {});
                                            }}
                                        >
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select a strategy" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {strategies.map((strategy) => (
                                                    <SelectItem key={strategy.id} value={strategy.type}>
                                                        {strategy.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    {/* Backtest Parameters */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <Label>Symbol</Label>
                                            <Input
                                                value={symbol}
                                                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                                                placeholder="AAPL"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Initial Capital</Label>
                                            <Input
                                                type="number"
                                                value={initialCapital}
                                                onChange={(e) => setInitialCapital(Number(e.target.value))}
                                                placeholder="10000"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>Start Date</Label>
                                            <Input
                                                type="date"
                                                value={startDate}
                                                onChange={(e) => setStartDate(e.target.value)}
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label>End Date</Label>
                                            <Input
                                                type="date"
                                                value={endDate}
                                                onChange={(e) => setEndDate(e.target.value)}
                                            />
                                        </div>
                                    </div>

                                    {/* Strategy Parameters */}
                                    {selectedStrategy && (
                                        <div className="space-y-4">
                                            <h4 className="font-medium">Strategy Parameters</h4>
                                            {Object.entries(strategyParams).map(([key, value]) => (
                                                <div key={key} className="space-y-2">
                                                    <Label>{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</Label>
                                                    <Input
                                                        type="number"
                                                        value={value}
                                                        onChange={(e) => setStrategyParams(prev => ({
                                                            ...prev,
                                                            [key]: Number(e.target.value)
                                                        }))}
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Action Buttons */}
                                    <div className="flex space-x-2">
                                        <Button
                                            onClick={runBacktest}
                                            disabled={!selectedStrategy || isRunning}
                                            className="flex-1"
                                        >
                                            {isRunning ? (
                                                <>
                                                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                                    Running...
                                                </>
                                            ) : (
                                                <>
                                                    <Play className="h-4 w-4 mr-2" />
                                                    Run Backtest
                                                </>
                                            )}
                                        </Button>
                                        <Button variant="outline" onClick={saveStrategy}>
                                            <Settings className="h-4 w-4 mr-2" />
                                            Save
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Strategy Info */}
                        <div className="space-y-4">
                            {selectedStrategy && (
                                <Card>
                                    <CardHeader>
                                        <CardTitle>{selectedStrategy.name}</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <p className="text-sm text-muted-foreground mb-4">
                                            {selectedStrategy.description}
                                        </p>
                                        <div className="space-y-2">
                                            <div className="flex justify-between">
                                                <span className="text-sm">Type:</span>
                                                <Badge variant="outline">{selectedStrategy.type}</Badge>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-sm">Custom:</span>
                                                <span className="text-sm">{selectedStrategy.isCustom ? 'Yes' : 'No'}</span>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            )}

                            {/* Quick Stats */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Quick Stats</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <span className="text-sm">Symbol:</span>
                                            <span className="text-sm font-medium">{symbol}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">Period:</span>
                                            <span className="text-sm font-medium">
                                                {formatDate(new Date(startDate), 'MMM dd')} - {formatDate(new Date(endDate), 'MMM dd, yyyy')}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">Capital:</span>
                                            <span className="text-sm font-medium">${initialCapital.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-sm">Benchmark:</span>
                                            <span className="text-sm font-medium">{benchmark}</span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </TabsContent>

                <TabsContent value="results" className="space-y-4">
                    {currentBacktest ? (
                        <div className="space-y-6">
                            {/* Performance Summary */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <Card>
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                        <CardTitle className="text-sm font-medium">Total Return</CardTitle>
                                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                                    </CardHeader>
                                    <CardContent>
                                        <div className={`text-2xl font-bold ${getPerformanceColor(currentBacktest.totalReturnPercent)}`}>
                                            {getPerformanceIcon(currentBacktest.totalReturnPercent)}
                                            {currentBacktest.totalReturnPercent >= 0 ? '+' : ''}{currentBacktest.totalReturnPercent.toFixed(2)}%
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            ${currentBacktest.totalReturn.toLocaleString()}
                                        </p>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                        <CardTitle className="text-sm font-medium">Sharpe Ratio</CardTitle>
                                        <Target className="h-4 w-4 text-muted-foreground" />
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold">
                                            {currentBacktest.sharpeRatio.toFixed(2)}
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            Risk-adjusted return
                                        </p>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                        <CardTitle className="text-sm font-medium">Max Drawdown</CardTitle>
                                        <Shield className="h-4 w-4 text-muted-foreground" />
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold text-red-600">
                                            {currentBacktest.maxDrawdown.toFixed(2)}%
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            Maximum loss
                                        </p>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                        <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                                        <BarChart3 className="h-4 w-4 text-muted-foreground" />
                                    </CardHeader>
                                    <CardContent>
                                        <div className="text-2xl font-bold">
                                            {currentBacktest.winRate.toFixed(1)}%
                                        </div>
                                        <p className="text-xs text-muted-foreground">
                                            {currentBacktest.totalTrades} trades
                                        </p>
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Equity Curve */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Equity Curve</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ResponsiveContainer width="100%" height={400}>
                                        <AreaChart data={currentBacktest.equityCurve}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis
                                                dataKey="date"
                                                tickFormatter={(value) => formatDate(new Date(value), 'MMM dd')}
                                            />
                                            <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
                                            <Tooltip
                                                formatter={(value: number) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
                                                labelFormatter={(value) => formatDate(new Date(value), 'MMM dd, yyyy')}
                                            />
                                            <Area
                                                type="monotone"
                                                dataKey="value"
                                                stroke="#3b82f6"
                                                fill="#3b82f6"
                                                fillOpacity={0.3}
                                            />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>

                            {/* Trade Analysis */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <Card>
                                    <CardHeader>
                                        <CardTitle>Trade Distribution</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <PieChart>
                                                <Pie
                                                    data={[
                                                        { name: 'Winning Trades', value: currentBacktest.totalTrades * (currentBacktest.winRate / 100), fill: '#10b981' },
                                                        { name: 'Losing Trades', value: currentBacktest.totalTrades * ((100 - currentBacktest.winRate) / 100), fill: '#ef4444' }
                                                    ]}
                                                    cx="50%"
                                                    cy="50%"
                                                    outerRadius={80}
                                                    dataKey="value"
                                                />
                                                <Tooltip />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle>Trade Statistics</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-4">
                                            <div className="flex justify-between">
                                                <span className="text-sm">Total Trades:</span>
                                                <span className="font-medium">{currentBacktest.totalTrades}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-sm">Average Win:</span>
                                                <span className="font-medium text-green-600">${currentBacktest.avgWin.toFixed(2)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-sm">Average Loss:</span>
                                                <span className="font-medium text-red-600">${currentBacktest.avgLoss.toFixed(2)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-sm">Profit Factor:</span>
                                                <span className="font-medium">{currentBacktest.profitFactor.toFixed(2)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-sm">Annualized Return:</span>
                                                <span className="font-medium">{currentBacktest.annualizedReturn.toFixed(2)}%</span>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Recent Trades */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Recent Trades</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-2">
                                        {currentBacktest.trades.slice(-10).map((trade) => (
                                            <div key={trade.id} className="flex items-center justify-between p-3 border rounded-lg">
                                                <div className="flex items-center space-x-3">
                                                    <Badge variant={trade.type === 'buy' ? 'default' : 'secondary'}>
                                                        {trade.type.toUpperCase()}
                                                    </Badge>
                                                    <div>
                                                        <p className="font-medium">
                                                            {formatDate(new Date(trade.entryDate), 'MMM dd')} - {formatDate(new Date(trade.exitDate), 'MMM dd')}
                                                        </p>
                                                        <p className="text-sm text-muted-foreground">
                                                            Entry: ${trade.entryPrice.toFixed(2)} | Exit: ${trade.exitPrice.toFixed(2)}
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className={`font-medium ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                        {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                                                    </p>
                                                    <p className={`text-sm ${trade.pnlPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                        {trade.pnlPercent >= 0 ? '+' : ''}{trade.pnlPercent.toFixed(2)}%
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    ) : (
                        <Card>
                            <CardContent className="p-8 text-center">
                                <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                                <h3 className="text-lg font-medium mb-2">No Backtest Results</h3>
                                <p className="text-muted-foreground mb-4">
                                    Run a backtest to see detailed results and analysis
                                </p>
                                <Button onClick={() => setActiveTab('strategy')}>
                                    <Play className="h-4 w-4 mr-2" />
                                    Run Backtest
                                </Button>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="comparison" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Strategy Comparison</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {backtestResults.map((result) => (
                                    <div key={result.id} className="flex items-center justify-between p-4 border rounded-lg">
                                        <div className="flex items-center space-x-4">
                                            <div>
                                                <h4 className="font-medium">{result.strategy}</h4>
                                                <p className="text-sm text-muted-foreground">
                                                    {result.symbol} • {formatDate(new Date(result.startDate), 'MMM dd')} - {formatDate(new Date(result.endDate), 'MMM dd, yyyy')}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-6">
                                            <div className="text-center">
                                                <p className="text-sm text-muted-foreground">Return</p>
                                                <p className={`font-medium ${getPerformanceColor(result.totalReturnPercent)}`}>
                                                    {result.totalReturnPercent >= 0 ? '+' : ''}{result.totalReturnPercent.toFixed(2)}%
                                                </p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-sm text-muted-foreground">Sharpe</p>
                                                <p className="font-medium">{result.sharpeRatio.toFixed(2)}</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-sm text-muted-foreground">Drawdown</p>
                                                <p className="font-medium text-red-600">{result.maxDrawdown.toFixed(2)}%</p>
                                            </div>
                                            <div className="text-center">
                                                <p className="text-sm text-muted-foreground">Win Rate</p>
                                                <p className="font-medium">{result.winRate.toFixed(1)}%</p>
                                            </div>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setCurrentBacktest(result)}
                                            >
                                                View Details
                                            </Button>
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

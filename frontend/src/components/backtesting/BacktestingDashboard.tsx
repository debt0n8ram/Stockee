import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { apiService } from '../../services/api';
import { toast } from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Calendar, TrendingUp, TrendingDown, Target, Zap, BarChart3, Activity } from 'lucide-react';

interface BacktestingDashboardProps {
    userId: string;
}

interface Strategy {
    name: string;
    description: string;
    parameters: Record<string, any>;
}

interface BacktestResult {
    total_return: number;
    annualized_return: number;
    volatility: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    profit_factor: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    avg_win: number;
    avg_loss: number;
    largest_win: number;
    largest_loss: number;
    portfolio_values: number[];
    equity_curve: number[];
    drawdown_curve: number[];
    trades_summary: any[];
}

interface AvailableSymbol {
    symbol: string;
    name: string;
    price_count: number;
    asset_type: string;
}

export const BacktestingDashboard: React.FC<BacktestingDashboardProps> = ({ userId }) => {
    const [availableStrategies, setAvailableStrategies] = useState<Strategy[]>([]);
    const [availableSymbols, setAvailableSymbols] = useState<AvailableSymbol[]>([]);
    const [selectedStrategy, setSelectedStrategy] = useState<string>('');
    const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');
    const [initialCapital, setInitialCapital] = useState<number>(100000);
    const [commission, setCommission] = useState<number>(0.001);
    const [slippage, setSlippage] = useState<number>(0.0005);
    const [strategyParams, setStrategyParams] = useState<Record<string, any>>({});
    const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
    const [isRunning, setIsRunning] = useState<boolean>(false);
    const [optimizationResult, setOptimizationResult] = useState<any>(null);
    const [walkForwardResult, setWalkForwardResult] = useState<any>(null);
    const [monteCarloResult, setMonteCarloResult] = useState<any>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [strategiesResponse, symbolsResponse] = await Promise.all([
                    apiService.getAvailableBacktestingStrategies(),
                    apiService.getAvailableBacktestingSymbols()
                ]);

                setAvailableStrategies(strategiesResponse.strategies);
                setAvailableSymbols(symbolsResponse.symbols);

                // Set default dates (last 2 years)
                const end = new Date();
                const start = new Date();
                start.setFullYear(start.getFullYear() - 2);

                setEndDate(end.toISOString().split('T')[0]);
                setStartDate(start.toISOString().split('T')[0]);

            } catch (error: any) {
                toast.error('Failed to load backtesting data');
            }
        };

        fetchData();
    }, []);

    const handleStrategyChange = (strategyName: string) => {
        setSelectedStrategy(strategyName);
        const strategy = availableStrategies.find(s => s.name === strategyName);
        if (strategy) {
            const defaultParams: Record<string, any> = {};
            Object.entries(strategy.parameters).forEach(([key, param]: [string, any]) => {
                defaultParams[key] = param.default;
            });
            setStrategyParams(defaultParams);
        }
    };

    const handleSymbolToggle = (symbol: string) => {
        setSelectedSymbols(prev =>
            prev.includes(symbol)
                ? prev.filter(s => s !== symbol)
                : [...prev, symbol]
        );
    };

    const runBacktest = async () => {
        if (!selectedStrategy || selectedSymbols.length === 0) {
            toast.error('Please select a strategy and at least one symbol');
            return;
        }

        setIsRunning(true);
        try {
            const result = await apiService.runBacktest({
                strategy_name: selectedStrategy,
                symbols: selectedSymbols,
                start_date: new Date(startDate),
                end_date: new Date(endDate),
                initial_capital: initialCapital,
                commission: commission,
                slippage: slippage,
                strategy_params: strategyParams
            });

            setBacktestResult(result.result);
            toast.success('Backtest completed successfully!');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to run backtest');
        } finally {
            setIsRunning(false);
        }
    };

    const runOptimization = async () => {
        if (!selectedStrategy || selectedSymbols.length === 0) {
            toast.error('Please select a strategy and at least one symbol');
            return;
        }

        setIsRunning(true);
        try {
            const strategy = availableStrategies.find(s => s.name === selectedStrategy);
            if (!strategy) return;

            // Create parameter ranges for optimization
            const parameterRanges: Record<string, [number, number]> = {};
            Object.entries(strategy.parameters).forEach(([key, param]: [string, any]) => {
                if (param.type === 'int') {
                    parameterRanges[key] = [Math.max(1, param.default - 10), param.default + 20];
                } else {
                    parameterRanges[key] = [Math.max(0.1, param.default * 0.5), param.default * 2];
                }
            });

            const result = await apiService.optimizeBacktestingStrategy({
                strategy_name: selectedStrategy,
                symbols: selectedSymbols,
                start_date: new Date(startDate),
                end_date: new Date(endDate),
                parameter_ranges: parameterRanges,
                optimization_metric: 'sharpe_ratio',
                n_trials: 50,
                initial_capital: initialCapital,
                commission: commission,
                slippage: slippage
            });

            setOptimizationResult(result.optimization_result);
            toast.success('Strategy optimization completed!');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to optimize strategy');
        } finally {
            setIsRunning(false);
        }
    };

    const runWalkForward = async () => {
        if (!selectedStrategy || selectedSymbols.length === 0) {
            toast.error('Please select a strategy and at least one symbol');
            return;
        }

        setIsRunning(true);
        try {
            const result = await apiService.runWalkForwardAnalysis({
                strategy_name: selectedStrategy,
                symbols: selectedSymbols,
                start_date: new Date(startDate),
                end_date: new Date(endDate),
                train_period: 252,
                test_period: 63,
                step_size: 21,
                strategy_params: strategyParams,
                initial_capital: initialCapital,
                commission: commission,
                slippage: slippage
            });

            setWalkForwardResult(result.walk_forward_result);
            toast.success('Walk-forward analysis completed!');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to run walk-forward analysis');
        } finally {
            setIsRunning(false);
        }
    };

    const runMonteCarlo = async () => {
        if (!selectedStrategy || selectedSymbols.length === 0) {
            toast.error('Please select a strategy and at least one symbol');
            return;
        }

        setIsRunning(true);
        try {
            const result = await apiService.runMonteCarloSimulation({
                strategy_name: selectedStrategy,
                symbols: selectedSymbols,
                start_date: new Date(startDate),
                end_date: new Date(endDate),
                n_simulations: 1000,
                strategy_params: strategyParams,
                initial_capital: initialCapital,
                commission: commission,
                slippage: slippage
            });

            setMonteCarloResult(result.monte_carlo_result);
            toast.success('Monte Carlo simulation completed!');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to run Monte Carlo simulation');
        } finally {
            setIsRunning(false);
        }
    };

    const formatPercentage = (value: number) => `${(value * 100).toFixed(2)}%`;
    const formatCurrency = (value: number) => `$${value.toLocaleString()}`;

    const equityData = backtestResult?.equity_curve.map((value, index) => ({
        day: index,
        value: value
    })) || [];

    const drawdownData = backtestResult?.drawdown_curve.map((value, index) => ({
        day: index,
        drawdown: value * 100
    })) || [];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold">Backtesting Dashboard</h1>
                <div className="flex items-center space-x-2">
                    <Activity className="h-5 w-5 text-blue-500" />
                    <span className="text-sm text-gray-600">Strategy Testing & Optimization</span>
                </div>
            </div>

            <Tabs defaultValue="backtest" className="space-y-6">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="backtest">Backtest</TabsTrigger>
                    <TabsTrigger value="optimization">Optimization</TabsTrigger>
                    <TabsTrigger value="walk-forward">Walk-Forward</TabsTrigger>
                    <TabsTrigger value="monte-carlo">Monte Carlo</TabsTrigger>
                </TabsList>

                <TabsContent value="backtest" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Configuration Panel */}
                        <div className="lg:col-span-1 space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center space-x-2">
                                        <Target className="h-5 w-5" />
                                        <span>Strategy Configuration</span>
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <Label htmlFor="strategy">Strategy</Label>
                                        <Select value={selectedStrategy} onValueChange={handleStrategyChange}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select strategy" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {availableStrategies.map((strategy) => (
                                                    <SelectItem key={strategy.name} value={strategy.name}>
                                                        {strategy.description}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div>
                                        <Label>Symbols</Label>
                                        <div className="max-h-32 overflow-y-auto border rounded p-2 space-y-1">
                                            {availableSymbols.map((symbol) => (
                                                <label key={symbol.symbol} className="flex items-center space-x-2">
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedSymbols.includes(symbol.symbol)}
                                                        onChange={() => handleSymbolToggle(symbol.symbol)}
                                                        className="rounded"
                                                    />
                                                    <span className="text-sm">{symbol.symbol}</span>
                                                    <Badge variant="secondary" className="text-xs">
                                                        {symbol.price_count} prices
                                                    </Badge>
                                                </label>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label htmlFor="startDate">Start Date</Label>
                                            <Input
                                                id="startDate"
                                                type="date"
                                                value={startDate}
                                                onChange={(e) => setStartDate(e.target.value)}
                                            />
                                        </div>
                                        <div>
                                            <Label htmlFor="endDate">End Date</Label>
                                            <Input
                                                id="endDate"
                                                type="date"
                                                value={endDate}
                                                onChange={(e) => setEndDate(e.target.value)}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <Label htmlFor="capital">Initial Capital</Label>
                                        <Input
                                            id="capital"
                                            type="number"
                                            value={initialCapital}
                                            onChange={(e) => setInitialCapital(Number(e.target.value))}
                                        />
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <Label htmlFor="commission">Commission</Label>
                                            <Input
                                                id="commission"
                                                type="number"
                                                step="0.001"
                                                value={commission}
                                                onChange={(e) => setCommission(Number(e.target.value))}
                                            />
                                        </div>
                                        <div>
                                            <Label htmlFor="slippage">Slippage</Label>
                                            <Input
                                                id="slippage"
                                                type="number"
                                                step="0.0001"
                                                value={slippage}
                                                onChange={(e) => setSlippage(Number(e.target.value))}
                                            />
                                        </div>
                                    </div>

                                    {/* Strategy Parameters */}
                                    {selectedStrategy && (
                                        <div>
                                            <Label>Strategy Parameters</Label>
                                            <div className="space-y-2">
                                                {Object.entries(strategyParams).map(([key, value]) => (
                                                    <div key={key}>
                                                        <Label htmlFor={key} className="text-sm">
                                                            {key.replace(/_/g, ' ').toUpperCase()}
                                                        </Label>
                                                        <Input
                                                            id={key}
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
                                        </div>
                                    )}

                                    <Button
                                        onClick={runBacktest}
                                        disabled={isRunning}
                                        className="w-full"
                                    >
                                        {isRunning ? 'Running...' : 'Run Backtest'}
                                    </Button>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Results Panel */}
                        <div className="lg:col-span-2 space-y-6">
                            {backtestResult && (
                                <>
                                    {/* Performance Metrics */}
                                    <Card>
                                        <CardHeader>
                                            <CardTitle className="flex items-center space-x-2">
                                                <BarChart3 className="h-5 w-5" />
                                                <span>Performance Metrics</span>
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                <div className="text-center">
                                                    <div className="text-2xl font-bold text-green-600">
                                                        {formatPercentage(backtestResult.total_return)}
                                                    </div>
                                                    <div className="text-sm text-gray-600">Total Return</div>
                                                </div>
                                                <div className="text-center">
                                                    <div className="text-2xl font-bold text-blue-600">
                                                        {backtestResult.sharpe_ratio.toFixed(2)}
                                                    </div>
                                                    <div className="text-sm text-gray-600">Sharpe Ratio</div>
                                                </div>
                                                <div className="text-center">
                                                    <div className="text-2xl font-bold text-red-600">
                                                        {formatPercentage(backtestResult.max_drawdown)}
                                                    </div>
                                                    <div className="text-sm text-gray-600">Max Drawdown</div>
                                                </div>
                                                <div className="text-center">
                                                    <div className="text-2xl font-bold text-purple-600">
                                                        {formatPercentage(backtestResult.win_rate)}
                                                    </div>
                                                    <div className="text-sm text-gray-600">Win Rate</div>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>

                                    {/* Equity Curve */}
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Equity Curve</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <ResponsiveContainer width="100%" height={300}>
                                                <LineChart data={equityData}>
                                                    <CartesianGrid strokeDasharray="3 3" />
                                                    <XAxis dataKey="day" />
                                                    <YAxis />
                                                    <Tooltip formatter={(value) => [formatCurrency(Number(value)), 'Portfolio Value']} />
                                                    <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} />
                                                </LineChart>
                                            </ResponsiveContainer>
                                        </CardContent>
                                    </Card>

                                    {/* Drawdown Chart */}
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Drawdown</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <ResponsiveContainer width="100%" height={300}>
                                                <BarChart data={drawdownData}>
                                                    <CartesianGrid strokeDasharray="3 3" />
                                                    <XAxis dataKey="day" />
                                                    <YAxis />
                                                    <Tooltip formatter={(value) => [`${Number(value).toFixed(2)}%`, 'Drawdown']} />
                                                    <Bar dataKey="drawdown" fill="#ef4444" />
                                                </BarChart>
                                            </ResponsiveContainer>
                                        </CardContent>
                                    </Card>

                                    {/* Trade Statistics */}
                                    <Card>
                                        <CardHeader>
                                            <CardTitle>Trade Statistics</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                <div>
                                                    <div className="text-lg font-semibold">{backtestResult.total_trades}</div>
                                                    <div className="text-sm text-gray-600">Total Trades</div>
                                                </div>
                                                <div>
                                                    <div className="text-lg font-semibold text-green-600">
                                                        {backtestResult.winning_trades}
                                                    </div>
                                                    <div className="text-sm text-gray-600">Winning Trades</div>
                                                </div>
                                                <div>
                                                    <div className="text-lg font-semibold text-red-600">
                                                        {backtestResult.losing_trades}
                                                    </div>
                                                    <div className="text-sm text-gray-600">Losing Trades</div>
                                                </div>
                                                <div>
                                                    <div className="text-lg font-semibold">
                                                        {backtestResult.profit_factor.toFixed(2)}
                                                    </div>
                                                    <div className="text-sm text-gray-600">Profit Factor</div>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </>
                            )}
                        </div>
                    </div>
                </TabsContent>

                <TabsContent value="optimization" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Strategy Optimization</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <p className="text-gray-600">
                                Optimize strategy parameters to find the best performing configuration.
                            </p>
                            <Button onClick={runOptimization} disabled={isRunning}>
                                {isRunning ? 'Optimizing...' : 'Run Optimization'}
                            </Button>

                            {optimizationResult && (
                                <div className="space-y-4">
                                    <div className="p-4 bg-green-50 rounded-lg">
                                        <h3 className="font-semibold text-green-800">Best Parameters Found</h3>
                                        <pre className="text-sm text-green-700 mt-2">
                                            {JSON.stringify(optimizationResult.best_parameters, null, 2)}
                                        </pre>
                                    </div>
                                    <div className="grid grid-cols-3 gap-4">
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {optimizationResult.best_metric.toFixed(3)}
                                            </div>
                                            <div className="text-sm text-gray-600">Best Sharpe Ratio</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {optimizationResult.successful_trials}
                                            </div>
                                            <div className="text-sm text-gray-600">Successful Trials</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {optimizationResult.total_trials}
                                            </div>
                                            <div className="text-sm text-gray-600">Total Trials</div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="walk-forward" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Walk-Forward Analysis</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <p className="text-gray-600">
                                Test strategy robustness using rolling optimization and out-of-sample testing.
                            </p>
                            <Button onClick={runWalkForward} disabled={isRunning}>
                                {isRunning ? 'Analyzing...' : 'Run Walk-Forward Analysis'}
                            </Button>

                            {walkForwardResult && (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {formatPercentage(walkForwardResult.average_return)}
                                            </div>
                                            <div className="text-sm text-gray-600">Avg Return</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {walkForwardResult.average_sharpe.toFixed(2)}
                                            </div>
                                            <div className="text-sm text-gray-600">Avg Sharpe</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {formatPercentage(walkForwardResult.average_max_drawdown)}
                                            </div>
                                            <div className="text-sm text-gray-600">Avg Max DD</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {walkForwardResult.positive_periods}/{walkForwardResult.total_periods}
                                            </div>
                                            <div className="text-sm text-gray-600">Positive Periods</div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="monte-carlo" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Monte Carlo Simulation</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <p className="text-gray-600">
                                Test strategy robustness using Monte Carlo simulation with bootstrapped returns.
                            </p>
                            <Button onClick={runMonteCarlo} disabled={isRunning}>
                                {isRunning ? 'Simulating...' : 'Run Monte Carlo Simulation'}
                            </Button>

                            {monteCarloResult && (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {formatPercentage(monteCarloResult.return_statistics.mean)}
                                            </div>
                                            <div className="text-sm text-gray-600">Mean Return</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {formatPercentage(monteCarloResult.return_statistics.percentile_5)}
                                            </div>
                                            <div className="text-sm text-gray-600">5th Percentile</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {formatPercentage(monteCarloResult.return_statistics.percentile_95)}
                                            </div>
                                            <div className="text-sm text-gray-600">95th Percentile</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-xl font-bold">
                                                {monteCarloResult.successful_simulations}
                                            </div>
                                            <div className="text-sm text-gray-600">Successful Runs</div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};

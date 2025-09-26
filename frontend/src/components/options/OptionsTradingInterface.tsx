import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { apiService } from '../../services/api';
import { toast } from 'react-hot-toast';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    Target,
    Calculator,
    BookOpen,
    AlertTriangle,
    DollarSign,
    Calendar,
    Zap
} from 'lucide-react';

interface OptionsTradingInterfaceProps {
    userId: string;
}

interface OptionChain {
    symbol: string;
    current_price: number;
    expirations: Array<{
        expiration_date: string;
        days_to_expiry: number;
        calls: OptionContract[];
        puts: OptionContract[];
    }>;
}

interface OptionContract {
    symbol: string;
    strike: number;
    premium: number;
    delta: number;
    gamma: number;
    theta: number;
    vega: number;
    rho: number;
    implied_volatility: number;
    volume: number;
    open_interest: number;
}

interface StrategyTemplate {
    name: string;
    type: string;
    description: string;
    max_profit: string;
    max_loss: string;
    breakeven: string;
    risk_level: string;
    setup: Array<{
        action: string;
        option_type?: string;
        quantity: number;
        strike_offset?: number;
    }>;
}

interface AvailableSymbol {
    symbol: string;
    name: string;
    asset_type: string;
    current_price: number;
}

export const OptionsTradingInterface: React.FC<OptionsTradingInterfaceProps> = ({ userId }) => {
    const [selectedSymbol, setSelectedSymbol] = useState<string>('');
    const [availableSymbols, setAvailableSymbols] = useState<AvailableSymbol[]>([]);
    const [optionChain, setOptionChain] = useState<OptionChain | null>(null);
    const [selectedExpiration, setSelectedExpiration] = useState<string>('');
    const [selectedStrategy, setSelectedStrategy] = useState<string>('');
    const [strategyTemplates, setStrategyTemplates] = useState<StrategyTemplate[]>([]);
    const [strategyResult, setStrategyResult] = useState<any>(null);
    const [greeksResult, setGreeksResult] = useState<any>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);

    // Greeks calculator state
    const [spotPrice, setSpotPrice] = useState<number>(0);
    const [strikePrice, setStrikePrice] = useState<number>(0);
    const [timeToExpiry, setTimeToExpiry] = useState<number>(30);
    const [riskFreeRate, setRiskFreeRate] = useState<number>(0.05);
    const [volatility, setVolatility] = useState<number>(0.25);
    const [optionType, setOptionType] = useState<string>('call');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [symbolsResponse, templatesResponse] = await Promise.all([
                    apiService.getAvailableOptionSymbols(),
                    apiService.getOptionStrategyTemplates()
                ]);

                setAvailableSymbols(symbolsResponse.symbols);
                setStrategyTemplates(templatesResponse.templates);

            } catch (error: any) {
                toast.error('Failed to load options data');
            }
        };

        fetchData();
    }, []);

    const handleSymbolChange = async (symbol: string) => {
        setSelectedSymbol(symbol);
        if (symbol) {
            setIsLoading(true);
            try {
                const response = await apiService.getOptionChain(symbol);
                setOptionChain(response);
                if (response.expirations.length > 0) {
                    setSelectedExpiration(response.expirations[0].expiration_date);
                }
            } catch (error: any) {
                toast.error('Failed to load option chain');
            } finally {
                setIsLoading(false);
            }
        }
    };

    const calculateGreeks = async () => {
        try {
            const response = await apiService.calculateOptionGreeks({
                spot_price: spotPrice,
                strike_price: strikePrice,
                time_to_expiry: timeToExpiry,
                risk_free_rate: riskFreeRate,
                volatility: volatility,
                option_type: optionType
            });

            setGreeksResult(response.greeks);
            toast.success('Greeks calculated successfully!');
        } catch (error: any) {
            toast.error('Failed to calculate Greeks');
        }
    };

    const createStrategy = async () => {
        if (!selectedSymbol || !selectedStrategy) {
            toast.error('Please select a symbol and strategy');
            return;
        }

        try {
            // Create sample positions based on selected strategy
            const positions = createSamplePositions(selectedStrategy, selectedSymbol);

            const response = await apiService.createOptionStrategy({
                strategy_type: selectedStrategy,
                symbol: selectedSymbol,
                positions: positions
            });

            setStrategyResult(response.strategy);
            toast.success('Strategy created successfully!');
        } catch (error: any) {
            toast.error('Failed to create strategy');
        }
    };

    const createSamplePositions = (strategyType: string, symbol: string) => {
        const currentPrice = optionChain?.current_price || 100;
        const expiration = selectedExpiration || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString();

        switch (strategyType) {
            case 'long_call':
                return [{
                    symbol: `${symbol}${new Date(expiration).toISOString().slice(2, 10).replace(/-/g, '')}C${Math.round(currentPrice).toString().padStart(8, '0')}`,
                    option_type: 'call',
                    strike_price: Math.round(currentPrice),
                    expiration_date: expiration,
                    premium: 5.0,
                    quantity: 1
                }];

            case 'long_put':
                return [{
                    symbol: `${symbol}${new Date(expiration).toISOString().slice(2, 10).replace(/-/g, '')}P${Math.round(currentPrice).toString().padStart(8, '0')}`,
                    option_type: 'put',
                    strike_price: Math.round(currentPrice),
                    expiration_date: expiration,
                    premium: 3.0,
                    quantity: 1
                }];

            case 'straddle':
                return [
                    {
                        symbol: `${symbol}${new Date(expiration).toISOString().slice(2, 10).replace(/-/g, '')}C${Math.round(currentPrice).toString().padStart(8, '0')}`,
                        option_type: 'call',
                        strike_price: Math.round(currentPrice),
                        expiration_date: expiration,
                        premium: 5.0,
                        quantity: 1
                    },
                    {
                        symbol: `${symbol}${new Date(expiration).toISOString().slice(2, 10).replace(/-/g, '')}P${Math.round(currentPrice).toString().padStart(8, '0')}`,
                        option_type: 'put',
                        strike_price: Math.round(currentPrice),
                        expiration_date: expiration,
                        premium: 3.0,
                        quantity: 1
                    }
                ];

            default:
                return [];
        }
    };

    const formatCurrency = (value: number) => `$${value.toFixed(2)}`;
    const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;

    const profitLossData = strategyResult?.profit_loss_curve?.map((point: [number, number]) => ({
        price: point[0],
        pnl: point[1]
    })) || [];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold">Options Trading</h1>
                <div className="flex items-center space-x-2">
                    <Target className="h-5 w-5 text-blue-500" />
                    <span className="text-sm text-gray-600">Advanced Options Strategies</span>
                </div>
            </div>

            <Tabs defaultValue="option-chain" className="space-y-6">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="option-chain">Option Chain</TabsTrigger>
                    <TabsTrigger value="strategy-builder">Strategy Builder</TabsTrigger>
                    <TabsTrigger value="greeks-calculator">Greeks Calculator</TabsTrigger>
                    <TabsTrigger value="education">Education</TabsTrigger>
                </TabsList>

                <TabsContent value="option-chain" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <TrendingUp className="h-5 w-5" />
                                <span>Option Chain</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <Label htmlFor="symbol">Symbol</Label>
                                    <Select value={selectedSymbol} onValueChange={handleSymbolChange}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select symbol" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {availableSymbols.map((symbol) => (
                                                <SelectItem key={symbol.symbol} value={symbol.symbol}>
                                                    {symbol.symbol} - {symbol.name} ({formatCurrency(symbol.current_price)})
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                {optionChain && (
                                    <div>
                                        <Label htmlFor="expiration">Expiration</Label>
                                        <Select value={selectedExpiration} onValueChange={setSelectedExpiration}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select expiration" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {optionChain.expirations.map((exp) => (
                                                    <SelectItem key={exp.expiration_date} value={exp.expiration_date}>
                                                        {new Date(exp.expiration_date).toLocaleDateString()} ({exp.days_to_expiry} days)
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                )}
                            </div>

                            {optionChain && selectedExpiration && (
                                <div className="space-y-4">
                                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                                        <h3 className="font-semibold text-blue-800">{optionChain.symbol}</h3>
                                        <p className="text-blue-600">Current Price: {formatCurrency(optionChain.current_price)}</p>
                                    </div>

                                    {(() => {
                                        const expiration = optionChain.expirations.find(exp => exp.expiration_date === selectedExpiration);
                                        if (!expiration) return null;

                                        return (
                                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                                {/* Calls */}
                                                <div>
                                                    <h4 className="font-semibold text-green-600 mb-2">Calls</h4>
                                                    <div className="space-y-2 max-h-96 overflow-y-auto">
                                                        {expiration.calls.map((call) => (
                                                            <div key={call.symbol} className="p-3 border rounded-lg hover:bg-gray-50">
                                                                <div className="flex justify-between items-center">
                                                                    <div>
                                                                        <div className="font-medium">${call.strike}</div>
                                                                        <div className="text-sm text-gray-600">
                                                                            {formatCurrency(call.premium)}
                                                                        </div>
                                                                    </div>
                                                                    <div className="text-right text-sm">
                                                                        <div>Δ {call.delta.toFixed(3)}</div>
                                                                        <div>Γ {call.gamma.toFixed(3)}</div>
                                                                        <div>Θ {call.theta.toFixed(3)}</div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>

                                                {/* Puts */}
                                                <div>
                                                    <h4 className="font-semibold text-red-600 mb-2">Puts</h4>
                                                    <div className="space-y-2 max-h-96 overflow-y-auto">
                                                        {expiration.puts.map((put) => (
                                                            <div key={put.symbol} className="p-3 border rounded-lg hover:bg-gray-50">
                                                                <div className="flex justify-between items-center">
                                                                    <div>
                                                                        <div className="font-medium">${put.strike}</div>
                                                                        <div className="text-sm text-gray-600">
                                                                            {formatCurrency(put.premium)}
                                                                        </div>
                                                                    </div>
                                                                    <div className="text-right text-sm">
                                                                        <div>Δ {put.delta.toFixed(3)}</div>
                                                                        <div>Γ {put.gamma.toFixed(3)}</div>
                                                                        <div>Θ {put.theta.toFixed(3)}</div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })()}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="strategy-builder" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Target className="h-5 w-5" />
                                    <span>Strategy Builder</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <Label htmlFor="strategy">Strategy Type</Label>
                                    <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select strategy" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {strategyTemplates.map((template) => (
                                                <SelectItem key={template.type} value={template.type}>
                                                    {template.name}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                {selectedStrategy && (
                                    <div className="p-4 bg-gray-50 rounded-lg">
                                        {(() => {
                                            const template = strategyTemplates.find(t => t.type === selectedStrategy);
                                            if (!template) return null;

                                            return (
                                                <div>
                                                    <h4 className="font-semibold">{template.name}</h4>
                                                    <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                                                    <div className="grid grid-cols-2 gap-2 text-sm">
                                                        <div>
                                                            <span className="font-medium">Max Profit:</span> {template.max_profit}
                                                        </div>
                                                        <div>
                                                            <span className="font-medium">Max Loss:</span> {template.max_loss}
                                                        </div>
                                                        <div>
                                                            <span className="font-medium">Breakeven:</span> {template.breakeven}
                                                        </div>
                                                        <div>
                                                            <span className="font-medium">Risk:</span>
                                                            <Badge variant={template.risk_level === 'Limited' ? 'default' : 'destructive'} className="ml-1">
                                                                {template.risk_level}
                                                            </Badge>
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })()}
                                    </div>
                                )}

                                <Button
                                    onClick={createStrategy}
                                    disabled={!selectedSymbol || !selectedStrategy}
                                    className="w-full"
                                >
                                    Create Strategy
                                </Button>
                            </CardContent>
                        </Card>

                        {strategyResult && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Strategy Analysis</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-green-600">
                                                {formatCurrency(strategyResult.max_profit)}
                                            </div>
                                            <div className="text-sm text-gray-600">Max Profit</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-red-600">
                                                {formatCurrency(strategyResult.max_loss)}
                                            </div>
                                            <div className="text-sm text-gray-600">Max Loss</div>
                                        </div>
                                    </div>

                                    {strategyResult.breakeven_points && strategyResult.breakeven_points.length > 0 && (
                                        <div>
                                            <h4 className="font-semibold mb-2">Breakeven Points</h4>
                                            <div className="flex flex-wrap gap-2">
                                                {strategyResult.breakeven_points.map((point: number, index: number) => (
                                                    <Badge key={index} variant="outline">
                                                        {formatCurrency(point)}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {strategyResult.greeks && (
                                        <div>
                                            <h4 className="font-semibold mb-2">Strategy Greeks</h4>
                                            <div className="grid grid-cols-2 gap-2 text-sm">
                                                <div>Δ {strategyResult.greeks.delta.toFixed(3)}</div>
                                                <div>Γ {strategyResult.greeks.gamma.toFixed(3)}</div>
                                                <div>Θ {strategyResult.greeks.theta.toFixed(3)}</div>
                                                <div>ν {strategyResult.greeks.vega.toFixed(3)}</div>
                                            </div>
                                        </div>
                                    )}

                                    {profitLossData.length > 0 && (
                                        <div>
                                            <h4 className="font-semibold mb-2">Profit/Loss Curve</h4>
                                            <ResponsiveContainer width="100%" height={200}>
                                                <LineChart data={profitLossData}>
                                                    <CartesianGrid strokeDasharray="3 3" />
                                                    <XAxis dataKey="price" />
                                                    <YAxis />
                                                    <Tooltip formatter={(value) => [formatCurrency(Number(value)), 'P&L']} />
                                                    <Line type="monotone" dataKey="pnl" stroke="#8884d8" strokeWidth={2} />
                                                </LineChart>
                                            </ResponsiveContainer>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </TabsContent>

                <TabsContent value="greeks-calculator" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Calculator className="h-5 w-5" />
                                    <span>Greeks Calculator</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label htmlFor="spotPrice">Spot Price</Label>
                                        <Input
                                            id="spotPrice"
                                            type="number"
                                            step="0.01"
                                            value={spotPrice}
                                            onChange={(e) => setSpotPrice(Number(e.target.value))}
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="strikePrice">Strike Price</Label>
                                        <Input
                                            id="strikePrice"
                                            type="number"
                                            step="0.01"
                                            value={strikePrice}
                                            onChange={(e) => setStrikePrice(Number(e.target.value))}
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label htmlFor="timeToExpiry">Time to Expiry (days)</Label>
                                        <Input
                                            id="timeToExpiry"
                                            type="number"
                                            value={timeToExpiry}
                                            onChange={(e) => setTimeToExpiry(Number(e.target.value))}
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="riskFreeRate">Risk-Free Rate</Label>
                                        <Input
                                            id="riskFreeRate"
                                            type="number"
                                            step="0.001"
                                            value={riskFreeRate}
                                            onChange={(e) => setRiskFreeRate(Number(e.target.value))}
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label htmlFor="volatility">Volatility</Label>
                                        <Input
                                            id="volatility"
                                            type="number"
                                            step="0.01"
                                            value={volatility}
                                            onChange={(e) => setVolatility(Number(e.target.value))}
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="optionType">Option Type</Label>
                                        <Select value={optionType} onValueChange={setOptionType}>
                                            <SelectTrigger>
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="call">Call</SelectItem>
                                                <SelectItem value="put">Put</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>

                                <Button onClick={calculateGreeks} className="w-full">
                                    Calculate Greeks
                                </Button>
                            </CardContent>
                        </Card>

                        {greeksResult && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Greeks Results</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                                            <div className="text-2xl font-bold text-blue-600">
                                                {formatCurrency(greeksResult.price)}
                                            </div>
                                            <div className="text-sm text-blue-600">Option Price</div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="text-center p-3 border rounded-lg">
                                                <div className="text-lg font-semibold">
                                                    {greeksResult.delta.toFixed(3)}
                                                </div>
                                                <div className="text-sm text-gray-600">Delta (Δ)</div>
                                            </div>
                                            <div className="text-center p-3 border rounded-lg">
                                                <div className="text-lg font-semibold">
                                                    {greeksResult.gamma.toFixed(3)}
                                                </div>
                                                <div className="text-sm text-gray-600">Gamma (Γ)</div>
                                            </div>
                                            <div className="text-center p-3 border rounded-lg">
                                                <div className="text-lg font-semibold">
                                                    {greeksResult.theta.toFixed(3)}
                                                </div>
                                                <div className="text-sm text-gray-600">Theta (Θ)</div>
                                            </div>
                                            <div className="text-center p-3 border rounded-lg">
                                                <div className="text-lg font-semibold">
                                                    {greeksResult.vega.toFixed(3)}
                                                </div>
                                                <div className="text-sm text-gray-600">Vega (ν)</div>
                                            </div>
                                        </div>

                                        <div className="text-center p-3 border rounded-lg">
                                            <div className="text-lg font-semibold">
                                                {greeksResult.rho.toFixed(3)}
                                            </div>
                                            <div className="text-sm text-gray-600">Rho (ρ)</div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </TabsContent>

                <TabsContent value="education" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <BookOpen className="h-5 w-5" />
                                <span>Options Education</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-6">
                                <div>
                                    <h3 className="text-lg font-semibold mb-3">Basic Concepts</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold text-green-600">Call Options</h4>
                                            <p className="text-sm text-gray-600">
                                                Give you the right to buy a stock at a specific price.
                                                Profitable when stock price rises above strike price.
                                            </p>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold text-red-600">Put Options</h4>
                                            <p className="text-sm text-gray-600">
                                                Give you the right to sell a stock at a specific price.
                                                Profitable when stock price falls below strike price.
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-3">The Greeks</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold">Delta (Δ)</h4>
                                            <p className="text-sm text-gray-600">
                                                Measures price sensitivity to underlying asset price changes.
                                            </p>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold">Gamma (Γ)</h4>
                                            <p className="text-sm text-gray-600">
                                                Measures the rate of change of delta.
                                            </p>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold">Theta (Θ)</h4>
                                            <p className="text-sm text-gray-600">
                                                Measures time decay - how much option value decreases over time.
                                            </p>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold">Vega (ν)</h4>
                                            <p className="text-sm text-gray-600">
                                                Measures sensitivity to volatility changes.
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-3">Risk Management</h3>
                                    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                        <div className="flex items-start space-x-2">
                                            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                                            <div>
                                                <h4 className="font-semibold text-yellow-800">Important Warning</h4>
                                                <p className="text-sm text-yellow-700">
                                                    Options trading involves significant risk and may not be suitable for all investors.
                                                    You can lose more than your initial investment. Please understand the risks before trading.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};
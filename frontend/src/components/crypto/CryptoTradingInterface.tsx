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
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    Coins,
    Zap,
    Shield,
    BookOpen,
    AlertTriangle,
    DollarSign,
    Activity,
    Target,
    BarChart3
} from 'lucide-react';

interface CryptoTradingInterfaceProps {
    userId: string;
}

interface CryptoPriceData {
    price: number;
    change_24h: number;
    volume_24h: number;
}

interface CryptoPrice {
    [symbol: string]: CryptoPriceData;
}

interface CryptoMarketData {
    symbol: string;
    name: string;
    current_price: number;
    market_cap: number;
    total_volume: number;
    price_change_24h: number;
    price_change_7d: number;
    price_change_30d: number;
    circulating_supply: number;
    total_supply: number;
    max_supply: number;
    ath: number;
    atl: number;
    market_cap_rank: number;
    description: string;
    categories: string[];
    contract_address: string;
}

interface DeFiPool {
    protocol: string;
    pool_address: string;
    token0: {
        symbol: string;
        name: string;
        decimals: number;
    };
    token1: {
        symbol: string;
        name: string;
        decimals: number;
    };
    reserve0: number;
    reserve1: number;
    total_supply: number;
    fee: number;
    apr: number;
    tvl: number;
}

interface YieldFarming {
    protocol: string;
    pool_address: string;
    token0: string;
    token1: string;
    apr: number;
    tvl: number;
    risk_level: string;
    rewards_token: string;
    lock_period: number | null;
}

interface DeFiPosition {
    protocol: string;
    action: string;
    pool_address: string;
    token0_amount: number;
    token1_amount: number;
    lp_tokens: number;
    entry_price: number;
    current_value: number;
    unrealized_pnl: number;
    rewards: number;
}

interface PortfolioAnalytics {
    total_value: number;
    total_cost: number;
    total_pnl: number;
    total_pnl_percentage: number;
    positions: Array<{
        symbol: string;
        quantity: number;
        avg_price: number;
        current_price: number;
        current_value: number;
        cost_basis: number;
        unrealized_pnl: number;
        pnl_percentage: number;
    }>;
    diversification: {
        hhi: number;
        effective_assets: number;
        concentration_risk: string;
        top_holdings: any[];
    };
    risk_metrics: {
        volatility: number;
        var_95: number;
        max_drawdown: number;
        risk_level: string;
    };
}

export const CryptoTradingInterface: React.FC<CryptoTradingInterfaceProps> = ({ userId }) => {
    const [cryptoPrices, setCryptoPrices] = useState<CryptoPrice>({});
    const [selectedCrypto, setSelectedCrypto] = useState<string>('');
    const [cryptoMarketData, setCryptoMarketData] = useState<CryptoMarketData | null>(null);
    const [defiPools, setDefiPools] = useState<DeFiPool[]>([]);
    const [yieldFarming, setYieldFarming] = useState<YieldFarming[]>([]);
    const [defiPositions, setDefiPositions] = useState<DeFiPosition[]>([]);
    const [portfolioAnalytics, setPortfolioAnalytics] = useState<PortfolioAnalytics | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);

    // Swap calculator state
    const [tokenIn, setTokenIn] = useState<string>('ETH');
    const [tokenOut, setTokenOut] = useState<string>('USDC');
    const [amountIn, setAmountIn] = useState<number>(0);
    const [swapQuote, setSwapQuote] = useState<any>(null);

    // Common crypto symbols
    const commonCryptos = ['BTC', 'ETH', 'USDC', 'USDT', 'BNB', 'ADA', 'SOL', 'DOT', 'MATIC', 'AVAX'];

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch initial crypto prices
                const pricesResponse = await apiService.getCryptoPrices(commonCryptos.join(','));
                setCryptoPrices(pricesResponse.prices);

                // Fetch portfolio analytics
                const portfolioResponse = await apiService.getCryptoPortfolioAnalytics(userId);
                setPortfolioAnalytics(portfolioResponse.analytics);

                // Fetch DeFi positions
                const positionsResponse = await apiService.getDefiPositions(userId);
                setDefiPositions(positionsResponse.positions);

            } catch (error: any) {
                toast.error('Failed to load crypto data');
            }
        };

        fetchData();
    }, [userId]);

    const handleCryptoSelect = async (symbol: string) => {
        setSelectedCrypto(symbol);
        if (symbol) {
            setIsLoading(true);
            try {
                const response = await apiService.getCryptoMarketData(symbol);
                setCryptoMarketData(response.market_data);
            } catch (error: any) {
                toast.error('Failed to load market data');
            } finally {
                setIsLoading(false);
            }
        }
    };

    const fetchDefiPools = async (protocol: string) => {
        try {
            const response = await apiService.getDefiPools(protocol, 20);
            setDefiPools(response.pools);
        } catch (error: any) {
            toast.error('Failed to load DeFi pools');
        }
    };

    const fetchYieldFarming = async () => {
        try {
            const response = await apiService.getYieldFarmingOpportunities(5.0);
            setYieldFarming(response.opportunities);
        } catch (error: any) {
            toast.error('Failed to load yield farming opportunities');
        }
    };

    const calculateSwapQuote = async () => {
        if (!amountIn || amountIn <= 0) {
            toast.error('Please enter a valid amount');
            return;
        }

        try {
            const response = await apiService.calculateSwapQuote({
                token_in: tokenIn,
                token_out: tokenOut,
                amount_in: amountIn,
                protocol: 'uniswap'
            });

            setSwapQuote(response.quote);
            if (response.quote.success) {
                toast.success('Swap quote calculated!');
            } else {
                toast.error(response.quote.error || 'Failed to calculate quote');
            }
        } catch (error: any) {
            toast.error('Failed to calculate swap quote');
        }
    };

    const formatCurrency = (value: number | undefined) => {
        if (value === undefined || value === null) return '$0.00';
        return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };
    const formatPercentage = (value: number | undefined) => {
        if (value === undefined || value === null) return '0.00%';
        return `${value.toFixed(2)}%`;
    };
    const formatNumber = (value: number | undefined) => {
        if (value === undefined || value === null) return '0';
        return value.toLocaleString();
    };

    const portfolioData = portfolioAnalytics?.positions.map(pos => ({
        symbol: pos.symbol,
        value: pos.current_value,
        pnl: pos.unrealized_pnl
    })) || [];

    const yieldFarmingData = yieldFarming.slice(0, 10).map(opp => ({
        name: `${opp.token0}/${opp.token1}`,
        apr: opp.apr,
        tvl: opp.tvl / 1000000, // Convert to millions
        risk: opp.risk_level
    }));

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold">Cryptocurrency Trading</h1>
                <div className="flex items-center space-x-2">
                    <Coins className="h-5 w-5 text-yellow-500" />
                    <span className="text-sm text-gray-600">DeFi & Crypto Markets</span>
                </div>
            </div>

            <Tabs defaultValue="market" className="space-y-6">
                <TabsList className="grid w-full grid-cols-5">
                    <TabsTrigger value="market">Market</TabsTrigger>
                    <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
                    <TabsTrigger value="defi">DeFi</TabsTrigger>
                    <TabsTrigger value="swap">Swap</TabsTrigger>
                    <TabsTrigger value="education">Education</TabsTrigger>
                </TabsList>

                <TabsContent value="market" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1 space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center space-x-2">
                                        <TrendingUp className="h-5 w-5" />
                                        <span>Crypto Prices</span>
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-2">
                                    {commonCryptos.map((symbol) => (
                                        <div key={symbol} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer" onClick={() => handleCryptoSelect(symbol)}>
                                            <div className="flex items-center space-x-2">
                                                <span className="font-medium">{symbol}</span>
                                                <Badge variant="outline" className="text-xs">
                                                    {formatCurrency(cryptoPrices[symbol]?.price || 0)}
                                                </Badge>
                                            </div>
                                            <div className="text-sm text-gray-600">
                                                {cryptoPrices[symbol]?.price ? formatCurrency(cryptoPrices[symbol].price) : 'N/A'}
                                            </div>
                                        </div>
                                    ))}
                                </CardContent>
                            </Card>
                        </div>

                        <div className="lg:col-span-2 space-y-6">
                            {cryptoMarketData && (
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center space-x-2">
                                            <Activity className="h-5 w-5" />
                                            <span>{cryptoMarketData.name} ({cryptoMarketData.symbol})</span>
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                            <div className="text-center">
                                                <div className="text-2xl font-bold">
                                                    {formatCurrency(cryptoMarketData.current_price)}
                                                </div>
                                                <div className="text-sm text-gray-600">Current Price</div>
                                            </div>
                                            <div className="text-center">
                                                <div className={`text-lg font-semibold ${cryptoMarketData.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    {formatPercentage(cryptoMarketData.price_change_24h)}
                                                </div>
                                                <div className="text-sm text-gray-600">24h Change</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-lg font-semibold">
                                                    {formatCurrency(cryptoMarketData.market_cap / 1000000000)}B
                                                </div>
                                                <div className="text-sm text-gray-600">Market Cap</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-lg font-semibold">
                                                    #{cryptoMarketData.market_cap_rank}
                                                </div>
                                                <div className="text-sm text-gray-600">Rank</div>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <h4 className="font-semibold mb-2">Price Statistics</h4>
                                                <div className="space-y-1 text-sm">
                                                    <div className="flex justify-between">
                                                        <span>All-Time High:</span>
                                                        <span>{formatCurrency(cryptoMarketData.ath)}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>All-Time Low:</span>
                                                        <span>{formatCurrency(cryptoMarketData.atl)}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>7d Change:</span>
                                                        <span className={cryptoMarketData.price_change_7d >= 0 ? 'text-green-600' : 'text-red-600'}>
                                                            {formatPercentage(cryptoMarketData.price_change_7d)}
                                                        </span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>30d Change:</span>
                                                        <span className={cryptoMarketData.price_change_30d >= 0 ? 'text-green-600' : 'text-red-600'}>
                                                            {formatPercentage(cryptoMarketData.price_change_30d)}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold mb-2">Supply Information</h4>
                                                <div className="space-y-1 text-sm">
                                                    <div className="flex justify-between">
                                                        <span>Circulating:</span>
                                                        <span>{formatNumber(cryptoMarketData.circulating_supply)}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>Total Supply:</span>
                                                        <span>{formatNumber(cryptoMarketData.total_supply)}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>Max Supply:</span>
                                                        <span>{formatNumber(cryptoMarketData.max_supply)}</span>
                                                    </div>
                                                    <div className="flex justify-between">
                                                        <span>24h Volume:</span>
                                                        <span>{formatCurrency(cryptoMarketData.total_volume)}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {cryptoMarketData.categories.length > 0 && (
                                            <div>
                                                <h4 className="font-semibold mb-2">Categories</h4>
                                                <div className="flex flex-wrap gap-2">
                                                    {cryptoMarketData.categories.map((category, index) => (
                                                        <Badge key={index} variant="secondary">
                                                            {category}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            )}
                        </div>
                    </div>
                </TabsContent>

                <TabsContent value="portfolio" className="space-y-6">
                    {portfolioAnalytics && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center space-x-2">
                                        <BarChart3 className="h-5 w-5" />
                                        <span>Portfolio Overview</span>
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="text-center">
                                            <div className="text-2xl font-bold">
                                                {formatCurrency(portfolioAnalytics.total_value)}
                                            </div>
                                            <div className="text-sm text-gray-600">Total Value</div>
                                        </div>
                                        <div className="text-center">
                                            <div className={`text-2xl font-bold ${portfolioAnalytics.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                {formatCurrency(portfolioAnalytics.total_pnl)}
                                            </div>
                                            <div className="text-sm text-gray-600">Total P&L</div>
                                        </div>
                                    </div>

                                    <div className="text-center">
                                        <div className={`text-lg font-semibold ${portfolioAnalytics.total_pnl_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {formatPercentage(portfolioAnalytics.total_pnl_percentage)}
                                        </div>
                                        <div className="text-sm text-gray-600">P&L Percentage</div>
                                    </div>

                                    <div>
                                        <h4 className="font-semibold mb-2">Risk Metrics</h4>
                                        <div className="space-y-2">
                                            <div className="flex justify-between">
                                                <span>Volatility:</span>
                                                <span>{formatPercentage((portfolioAnalytics.risk_metrics?.volatility || 0) * 100)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>VaR (95%):</span>
                                                <span>{formatPercentage((portfolioAnalytics.risk_metrics?.var_95 || 0) * 100)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Max Drawdown:</span>
                                                <span>{formatPercentage((portfolioAnalytics.risk_metrics?.max_drawdown || 0) * 100)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Risk Level:</span>
                                                <Badge variant={portfolioAnalytics.risk_metrics?.risk_level === 'Low' ? 'default' : portfolioAnalytics.risk_metrics?.risk_level === 'Medium' ? 'secondary' : 'destructive'}>
                                                    {portfolioAnalytics.risk_metrics?.risk_level || 'Unknown'}
                                                </Badge>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Portfolio Allocation</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ResponsiveContainer width="100%" height={300}>
                                        <PieChart>
                                            <Pie
                                                data={portfolioData}
                                                cx="50%"
                                                cy="50%"
                                                labelLine={false}
                                                label={({ symbol, value }) => `${symbol}: ${formatCurrency(value)}`}
                                                outerRadius={80}
                                                fill="#8884d8"
                                                dataKey="value"
                                            >
                                                {portfolioData.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                ))}
                                            </Pie>
                                            <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>

                            <Card className="lg:col-span-2">
                                <CardHeader>
                                    <CardTitle>Holdings</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        {portfolioAnalytics.positions.map((position, index) => (
                                            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                                                <div className="flex items-center space-x-4">
                                                    <div>
                                                        <div className="font-semibold">{position.symbol}</div>
                                                        <div className="text-sm text-gray-600">
                                                            {position.amount?.toFixed(6) || '0.000000'} tokens
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="font-semibold">
                                                        {formatCurrency(position.current_value)}
                                                    </div>
                                                    <div className={`text-sm ${position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                        {formatCurrency(position.unrealized_pnl)} ({formatPercentage(position.pnl_percent)})
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="defi" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Zap className="h-5 w-5" />
                                    <span>DeFi Pools</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <Label htmlFor="protocol">Protocol</Label>
                                    <Select onValueChange={fetchDefiPools}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select protocol" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="uniswap">Uniswap</SelectItem>
                                            <SelectItem value="sushiswap">SushiSwap</SelectItem>
                                            <SelectItem value="curve">Curve</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2 max-h-96 overflow-y-auto">
                                    {defiPools.map((pool, index) => (
                                        <div key={index} className="p-3 border rounded-lg hover:bg-gray-50">
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <div className="font-medium">
                                                        {pool.token0.symbol}/{pool.token1.symbol}
                                                    </div>
                                                    <div className="text-sm text-gray-600">
                                                        {formatCurrency(pool.tvl)} TVL
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-sm font-semibold">
                                                        {formatPercentage(pool.fee * 100)}% fee
                                                    </div>
                                                    <div className="text-sm text-gray-600">
                                                        {formatPercentage(pool.apr)} APR
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Target className="h-5 w-5" />
                                    <span>Yield Farming</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <Button onClick={fetchYieldFarming} className="w-full">
                                    Load Yield Farming Opportunities
                                </Button>

                                {yieldFarming.length > 0 && (
                                    <div className="space-y-2 max-h-96 overflow-y-auto">
                                        {yieldFarming.slice(0, 10).map((opp, index) => (
                                            <div key={index} className="p-3 border rounded-lg hover:bg-gray-50">
                                                <div className="flex justify-between items-center">
                                                    <div>
                                                        <div className="font-medium">
                                                            {opp.token0}/{opp.token1}
                                                        </div>
                                                        <div className="text-sm text-gray-600">
                                                            {opp.protocol} • {formatCurrency(opp.tvl)} TVL
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        <div className="text-sm font-semibold text-green-600">
                                                            {formatPercentage(opp.apr)} APR
                                                        </div>
                                                        <Badge variant={opp.risk_level === 'Low' ? 'default' : opp.risk_level === 'Medium' ? 'secondary' : 'destructive'}>
                                                            {opp.risk_level}
                                                        </Badge>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>

                    {yieldFarming.length > 0 && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Yield Farming Opportunities</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={yieldFarmingData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <Tooltip formatter={(value, name) => [formatPercentage(Number(value)), 'APR']} />
                                        <Bar dataKey="apr" fill="#8884d8" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="swap" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Activity className="h-5 w-5" />
                                    <span>Token Swap</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label htmlFor="tokenIn">From</Label>
                                        <Select value={tokenIn} onValueChange={setTokenIn}>
                                            <SelectTrigger>
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {commonCryptos.map((crypto) => (
                                                    <SelectItem key={crypto} value={crypto}>
                                                        {crypto}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div>
                                        <Label htmlFor="tokenOut">To</Label>
                                        <Select value={tokenOut} onValueChange={setTokenOut}>
                                            <SelectTrigger>
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {commonCryptos.map((crypto) => (
                                                    <SelectItem key={crypto} value={crypto}>
                                                        {crypto}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>

                                <div>
                                    <Label htmlFor="amountIn">Amount</Label>
                                    <Input
                                        id="amountIn"
                                        type="number"
                                        step="0.000001"
                                        value={amountIn}
                                        onChange={(e) => setAmountIn(Number(e.target.value))}
                                        placeholder="Enter amount"
                                    />
                                </div>

                                <Button onClick={calculateSwapQuote} className="w-full">
                                    Get Quote
                                </Button>
                            </CardContent>
                        </Card>

                        {swapQuote && swapQuote.success && (
                            <Card>
                                <CardHeader>
                                    <CardTitle>Swap Quote</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                                        <div className="text-2xl font-bold text-blue-600">
                                            {swapQuote?.output_amount?.toFixed(6) || '0.000000'} {tokenOut}
                                        </div>
                                        <div className="text-sm text-blue-600">
                                            For {swapQuote?.input_amount || '0'} {tokenIn}
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <span>Price Impact:</span>
                                            <span className={swapQuote?.price_impact < 1 ? 'text-green-600' : 'text-red-600'}>
                                                {formatPercentage(swapQuote?.price_impact || 0)}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Gas Estimate:</span>
                                            <span>{swapQuote?.gas_estimate?.toLocaleString() || '0'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Protocols:</span>
                                            <span>{swapQuote?.protocols_used?.join(', ') || 'N/A'}</span>
                                        </div>
                                    </div>

                                    <Button className="w-full" disabled>
                                        Execute Swap (Demo)
                                    </Button>
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
                                <span>DeFi Education</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-6">
                                <div>
                                    <h3 className="text-lg font-semibold mb-3">DeFi Basics</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold text-blue-600">Decentralized Exchanges (DEXs)</h4>
                                            <p className="text-sm text-gray-600 mt-2">
                                                Platforms that allow users to trade cryptocurrencies without intermediaries.
                                            </p>
                                            <div className="mt-2">
                                                <Badge variant="outline" className="mr-1">Uniswap</Badge>
                                                <Badge variant="outline" className="mr-1">SushiSwap</Badge>
                                                <Badge variant="outline">PancakeSwap</Badge>
                                            </div>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold text-green-600">Liquidity Pools</h4>
                                            <p className="text-sm text-gray-600 mt-2">
                                                Pools of tokens that provide liquidity for trading and earn fees.
                                            </p>
                                            <div className="mt-2">
                                                <Badge variant="outline" className="mr-1">ETH/USDC</Badge>
                                                <Badge variant="outline" className="mr-1">BTC/WBTC</Badge>
                                                <Badge variant="outline">DAI/USDC</Badge>
                                            </div>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold text-purple-600">Yield Farming</h4>
                                            <p className="text-sm text-gray-600 mt-2">
                                                Earning rewards by providing liquidity or staking tokens.
                                            </p>
                                            <div className="mt-2">
                                                <Badge variant="outline" className="mr-1">Liquidity Mining</Badge>
                                                <Badge variant="outline" className="mr-1">Staking</Badge>
                                                <Badge variant="outline">Governance</Badge>
                                            </div>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold text-orange-600">Lending & Borrowing</h4>
                                            <p className="text-sm text-gray-600 mt-2">
                                                Decentralized protocols for lending and borrowing cryptocurrencies.
                                            </p>
                                            <div className="mt-2">
                                                <Badge variant="outline" className="mr-1">Aave</Badge>
                                                <Badge variant="outline" className="mr-1">Compound</Badge>
                                                <Badge variant="outline">MakerDAO</Badge>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-3">DeFi Risks</h3>
                                    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                        <div className="flex items-start space-x-2">
                                            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                                            <div>
                                                <h4 className="font-semibold text-yellow-800">Important Warning</h4>
                                                <p className="text-sm text-yellow-700 mt-1">
                                                    DeFi involves significant risks including smart contract vulnerabilities,
                                                    impermanent loss, and regulatory uncertainty. Only invest what you can afford to lose.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-3">DeFi Strategies</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold">Liquidity Provision</h4>
                                            <p className="text-sm text-gray-600 mt-2">
                                                Provide liquidity to earn trading fees
                                            </p>
                                            <div className="mt-2 flex justify-between text-sm">
                                                <span>Risk: Medium</span>
                                                <span className="text-green-600">5-20% APY</span>
                                            </div>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold">Yield Farming</h4>
                                            <p className="text-sm text-gray-600 mt-2">
                                                Stake tokens to earn additional rewards
                                            </p>
                                            <div className="mt-2 flex justify-between text-sm">
                                                <span>Risk: High</span>
                                                <span className="text-green-600">10-100% APY</span>
                                            </div>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold">Lending</h4>
                                            <p className="text-sm text-gray-600 mt-2">
                                                Lend tokens to earn interest
                                            </p>
                                            <div className="mt-2 flex justify-between text-sm">
                                                <span>Risk: Low</span>
                                                <span className="text-green-600">2-10% APY</span>
                                            </div>
                                        </div>
                                        <div className="p-4 border rounded-lg">
                                            <h4 className="font-semibold">Arbitrage</h4>
                                            <p className="text-sm text-gray-600 mt-2">
                                                Exploit price differences across platforms
                                            </p>
                                            <div className="mt-2 flex justify-between text-sm">
                                                <span>Risk: Medium</span>
                                                <span className="text-green-600">Variable</span>
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

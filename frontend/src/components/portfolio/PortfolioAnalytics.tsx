import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import {
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Area,
    AreaChart,
    ScatterChart,
    Scatter
} from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    BarChart3,
    PieChart as PieChartIcon,
    Shield,
    RefreshCw,
    Download
} from 'lucide-react';
// Simple date formatting function to avoid date-fns dependency
const formatDate = (date: Date, format?: string) => {
    if (format === 'MMM dd') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else if (format === 'MMM dd, yyyy') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } else if (format === 'HH:mm:ss') {
        return date.toLocaleTimeString();
    } else if (format === 'MMM dd, HH:mm') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ', ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    } else if (format === 'MMM dd, yyyy HH:mm:ss') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } else if (format === 'HH:mm') {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

interface PortfolioData {
    totalValue: number;
    totalChange: number;
    totalChangePercent: number;
    cashBalance: number;
    investedValue: number;
    dayChange: number;
    dayChangePercent: number;
    weekChange: number;
    weekChangePercent: number;
    monthChange: number;
    monthChangePercent: number;
    yearChange: number;
    yearChangePercent: number;
}

interface Holding {
    symbol: string;
    name: string;
    quantity: number;
    averagePrice: number;
    currentPrice: number;
    value: number;
    change: number;
    changePercent: number;
    weight: number;
    sector: string;
    marketCap: number;
    beta: number;
    pe: number;
    dividend: number;
}

interface PerformanceMetric {
    name: string;
    value: number;
    benchmark: number;
    description: string;
    trend: 'up' | 'down' | 'stable';
}

interface RiskMetric {
    name: string;
    value: number;
    level: 'low' | 'medium' | 'high';
    description: string;
    recommendation: string;
}

interface PortfolioAnalyticsProps {
    className?: string;
}

export const PortfolioAnalytics: React.FC<PortfolioAnalyticsProps> = ({ className = '' }) => {
    const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null);
    const [holdings, setHoldings] = useState<Holding[]>([]);
    const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetric[]>([]);
    const [riskMetrics, setRiskMetrics] = useState<RiskMetric[]>([]);
    const [historicalData, setHistoricalData] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Load portfolio data
    useEffect(() => {
        const loadData = async () => {
            await loadPortfolioData();
            await loadPerformanceMetrics();
            await loadRiskMetrics();
            await loadHistoricalData();
        };
        loadData();
    }, []);

    const loadPortfolioData = async () => {
        try {
            setIsLoading(true);
            const response = await fetch('/api/portfolio');
            const data = await response.json();
            setPortfolioData(data.data);
            setHoldings(data.data.holdings || []);
        } catch (error) {
            console.error('Error loading portfolio data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const loadPerformanceMetrics = async () => {
        try {
            const response = await fetch('/api/portfolio/performance');
            const data = await response.json();
            setPerformanceMetrics(data.data || []);
        } catch (error) {
            console.error('Error loading performance metrics:', error);
        }
    };

    const loadRiskMetrics = async () => {
        try {
            const response = await fetch('/api/portfolio/risk');
            const data = await response.json();
            setRiskMetrics(data.data || []);
        } catch (error) {
            console.error('Error loading risk metrics:', error);
        }
    };

    const loadHistoricalData = async () => {
        try {
            const response = await fetch(`/api/portfolio/history?timeframe=1Y`);
            const data = await response.json();
            setHistoricalData(data.data || []);
        } catch (error) {
            console.error('Error loading historical data:', error);
        }
    };

    // Calculate sector allocation
    const sectorAllocation = holdings.reduce((acc, holding) => {
        const existing = acc.find(item => item.sector === holding.sector);
        if (existing) {
            existing.value += holding.value;
            existing.weight += holding.weight;
        } else {
            acc.push({
                sector: holding.sector,
                value: holding.value,
                weight: holding.weight
            });
        }
        return acc;
    }, [] as Array<{ sector: string; value: number; weight: number }>);

    // Calculate top performers
    const topPerformers = holdings
        .sort((a, b) => b.changePercent - a.changePercent)
        .slice(0, 5);

    const bottomPerformers = holdings
        .sort((a, b) => a.changePercent - b.changePercent)
        .slice(0, 5);

    // Colors for charts
    const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'];

    // Custom tooltip for pie chart
    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
                    <p className="font-medium">{data.sector}</p>
                    <p className="text-sm text-muted-foreground">
                        Value: ${data.value.toLocaleString()}
                    </p>
                    <p className="text-sm text-muted-foreground">
                        Weight: {data.weight.toFixed(1)}%
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Portfolio Analytics</h2>
                    <p className="text-muted-foreground">
                        Comprehensive analysis of your investment portfolio
                    </p>
                </div>

                <div className="flex items-center space-x-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={loadPortfolioData}
                        disabled={isLoading}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Export
                    </Button>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Value</CardTitle>
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
                        <Shield className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            ${portfolioData?.cashBalance.toLocaleString() || '0'}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            {((portfolioData?.cashBalance || 0) / (portfolioData?.totalValue || 1) * 100).toFixed(1)}% of portfolio
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Day Change</CardTitle>
                        <BarChart3 className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className={`text-2xl font-bold ${portfolioData?.dayChangePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {portfolioData?.dayChangePercent >= 0 ? '+' : ''}{portfolioData?.dayChangePercent.toFixed(2)}%
                        </div>
                        <p className="text-xs text-muted-foreground">
                            ${portfolioData?.dayChange.toFixed(2)}
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Holdings</CardTitle>
                        <PieChartIcon className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {holdings.length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Active positions
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Main Content */}
            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="performance">Performance</TabsTrigger>
                    <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
                    <TabsTrigger value="allocation">Allocation</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Portfolio Value Chart */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Portfolio Value Over Time</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={300}>
                                    <AreaChart data={historicalData}>
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

                        {/* Top/Bottom Performers */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Top & Bottom Performers</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div>
                                        <h4 className="font-medium text-green-600 mb-2">Top Performers</h4>
                                        <div className="space-y-2">
                                            {topPerformers.map((holding) => (
                                                <div key={holding.symbol} className="flex items-center justify-between">
                                                    <div>
                                                        <p className="font-medium">{holding.symbol}</p>
                                                        <p className="text-sm text-muted-foreground">{holding.name}</p>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="font-medium text-green-600">
                                                            +{holding.changePercent.toFixed(2)}%
                                                        </p>
                                                        <p className="text-sm text-muted-foreground">
                                                            ${holding.change.toFixed(2)}
                                                        </p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <h4 className="font-medium text-red-600 mb-2">Bottom Performers</h4>
                                        <div className="space-y-2">
                                            {bottomPerformers.map((holding) => (
                                                <div key={holding.symbol} className="flex items-center justify-between">
                                                    <div>
                                                        <p className="font-medium">{holding.symbol}</p>
                                                        <p className="text-sm text-muted-foreground">{holding.name}</p>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="font-medium text-red-600">
                                                            {holding.changePercent.toFixed(2)}%
                                                        </p>
                                                        <p className="text-sm text-muted-foreground">
                                                            ${holding.change.toFixed(2)}
                                                        </p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="performance" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Performance Metrics */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Performance Metrics</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {performanceMetrics.map((metric) => (
                                        <div key={metric.name} className="flex items-center justify-between">
                                            <div>
                                                <p className="font-medium">{metric.name}</p>
                                                <p className="text-sm text-muted-foreground">{metric.description}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-medium">{metric.value.toFixed(2)}%</p>
                                                <p className="text-sm text-muted-foreground">
                                                    vs {metric.benchmark.toFixed(2)}% benchmark
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Performance Comparison */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Performance vs Benchmark</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={300}>
                                    <BarChart data={performanceMetrics}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <Tooltip />
                                        <Bar dataKey="value" fill="#3b82f6" name="Portfolio" />
                                        <Bar dataKey="benchmark" fill="#6b7280" name="Benchmark" />
                                    </BarChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="risk" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Risk Metrics */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Risk Metrics</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {riskMetrics.map((metric) => (
                                        <div key={metric.name} className="space-y-2">
                                            <div className="flex items-center justify-between">
                                                <span className="font-medium">{metric.name}</span>
                                                <Badge variant={
                                                    metric.level === 'high' ? 'destructive' :
                                                        metric.level === 'medium' ? 'default' : 'secondary'
                                                }>
                                                    {metric.level}
                                                </Badge>
                                            </div>
                                            <p className="text-sm text-muted-foreground">{metric.description}</p>
                                            <div className="flex items-center space-x-2">
                                                <Progress value={metric.value} className="flex-1" />
                                                <span className="text-sm font-medium">{metric.value.toFixed(1)}%</span>
                                            </div>
                                            <p className="text-xs text-muted-foreground">{metric.recommendation}</p>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Risk vs Return */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Risk vs Return Analysis</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={300}>
                                    <ScatterChart data={holdings}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="beta" name="Beta" />
                                        <YAxis dataKey="changePercent" name="Return %" />
                                        <Tooltip
                                            formatter={(value: number, name: string) => [value.toFixed(2), name]}
                                            labelFormatter={(value) => `Symbol: ${value}`}
                                        />
                                        <Scatter dataKey="changePercent" fill="#3b82f6" />
                                    </ScatterChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="allocation" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Sector Allocation */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Sector Allocation</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={300}>
                                    <PieChart>
                                        <Pie
                                            data={sectorAllocation}
                                            cx="50%"
                                            cy="50%"
                                            labelLine={false}
                                            label={({ sector, weight }) => `${sector} (${weight.toFixed(1)}%)`}
                                            outerRadius={80}
                                            fill="#8884d8"
                                            dataKey="weight"
                                        >
                                            {sectorAllocation.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip content={<CustomTooltip />} />
                                    </PieChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>

                        {/* Holdings List */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Holdings Breakdown</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {holdings.map((holding) => (
                                        <div key={holding.symbol} className="flex items-center justify-between">
                                            <div className="flex items-center space-x-3">
                                                <div>
                                                    <p className="font-medium">{holding.symbol}</p>
                                                    <p className="text-sm text-muted-foreground">{holding.sector}</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-medium">${holding.value.toLocaleString()}</p>
                                                <p className="text-sm text-muted-foreground">
                                                    {holding.weight.toFixed(1)}% • {holding.quantity} shares
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
};

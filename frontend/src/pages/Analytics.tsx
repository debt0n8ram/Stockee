import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, TrendingUp, Shield, Target, Info, BarChart, LineChart as LineChartIcon, AreaChart, Calendar, Settings } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, AreaChart as RechartsAreaChart, Area, BarChart as RechartsBarChart, Bar, ComposedChart } from 'recharts';
import { apiService } from '../services/api';
import { PerformanceAnalytics, RiskMetrics, BenchmarkComparison, PortfolioAllocation } from '../types/api';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

// Info tooltip component
const InfoTooltip: React.FC<{
    content: string;
    id: string;
    showTooltip: string | null;
    setShowTooltip: (id: string | null) => void;
}> = ({ content, id, showTooltip, setShowTooltip }) => {
    return (
        <div className="relative inline-block">
            <button
                onMouseEnter={() => setShowTooltip(id)}
                onMouseLeave={() => setShowTooltip(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
            >
                <Info className="h-4 w-4" />
            </button>
            {showTooltip === id && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-80 bg-gray-900 text-white text-sm rounded-lg p-3 shadow-lg z-50">
                    <div className="text-xs leading-relaxed">{content}</div>
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                </div>
            )}
        </div>
    );
};

export const Analytics: React.FC = () => {
    // Chart and time period state
    const [chartType, setChartType] = useState<'line' | 'area' | 'bar' | 'candlestick'>('line');
    const [timePeriod, setTimePeriod] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
    const [showTooltip, setShowTooltip] = useState<string | null>(null);

    const { data: performance, isLoading: performanceLoading } = useQuery<PerformanceAnalytics>({
        queryKey: ['performance-analytics', timePeriod],
        queryFn: () => apiService.getPerformanceAnalytics('user1', parseInt(timePeriod.replace('d', '').replace('y', '365'))),
        refetchInterval: 60000
    });

    const { data: riskMetrics, isLoading: riskLoading } = useQuery<RiskMetrics>({
        queryKey: ['risk-metrics', timePeriod],
        queryFn: () => apiService.getRiskMetrics('user1', parseInt(timePeriod.replace('d', '').replace('y', '365'))),
        refetchInterval: 60000
    });

    const { data: benchmark, isLoading: benchmarkLoading } = useQuery<BenchmarkComparison>({
        queryKey: ['benchmark-comparison', timePeriod],
        queryFn: () => apiService.getBenchmarkComparison('user1', 'SPY', parseInt(timePeriod.replace('d', '').replace('y', '365'))),
        refetchInterval: 300000
    });

    const { data: allocation, isLoading: allocationLoading } = useQuery<PortfolioAllocation>({
        queryKey: ['portfolio-allocation'],
        queryFn: () => apiService.getPortfolioAllocation('user1'),
        refetchInterval: 300000
    });

    // Generate realistic performance data based on time period
    const generatePerformanceData = () => {
        const days = timePeriod === '7d' ? 7 : timePeriod === '30d' ? 30 : timePeriod === '90d' ? 90 : 365;
        const data = [];
        const startValue = 100000;
        let portfolioValue = startValue;
        let benchmarkValue = startValue;

        for (let i = 0; i < days; i++) {
            const date = new Date();
            date.setDate(date.getDate() - (days - i));

            // Generate realistic price movements
            const portfolioChange = (Math.random() - 0.5) * 0.04; // ±2% daily change
            const benchmarkChange = (Math.random() - 0.5) * 0.02; // ±1% daily change

            portfolioValue *= (1 + portfolioChange);
            benchmarkValue *= (1 + benchmarkChange);

            data.push({
                date: date.toISOString().split('T')[0],
                portfolio: Math.round(portfolioValue),
                benchmark: Math.round(benchmarkValue),
                open: Math.round(portfolioValue * (1 + (Math.random() - 0.5) * 0.01)),
                high: Math.round(portfolioValue * (1 + Math.random() * 0.02)),
                low: Math.round(portfolioValue * (1 - Math.random() * 0.02)),
                close: Math.round(portfolioValue),
                volume: Math.round(Math.random() * 1000000 + 500000)
            });
        }
        return data;
    };

    const performanceData = generatePerformanceData();

    // Generate allocation data with fallback
    const allocationData = React.useMemo(() => {
        if (allocation?.allocation?.stocks && allocation.allocation.stocks.length > 0) {
            return allocation.allocation.stocks.map((stock: any) => ({
                name: stock.symbol,
                value: stock.value || 0,
                percentage: stock.percentage || 0
            }));
        }

        // Fallback mock data for demonstration
        return [
            { name: 'AAPL', value: 25000, percentage: 25 },
            { name: 'MSFT', value: 20000, percentage: 20 },
            { name: 'GOOGL', value: 15000, percentage: 15 },
            { name: 'TSLA', value: 10000, percentage: 10 },
            { name: 'NVDA', value: 8000, percentage: 8 },
            { name: 'Cash', value: 22000, percentage: 22 }
        ];
    }, [allocation]);

    if (performanceLoading || riskLoading || benchmarkLoading || allocationLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    // Chart type icons
    const chartTypeIcons = {
        line: LineChartIcon,
        area: AreaChart,
        bar: BarChart,
        candlestick: BarChart3 // Using BarChart3 as substitute for candlestick
    };

    // Render chart based on selected type
    const renderChart = () => {
        const commonProps = {
            data: performanceData,
            margin: { top: 5, right: 30, left: 20, bottom: 5 }
        };

        switch (chartType) {
            case 'line':
                return (
                    <LineChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, '']} />
                        <Line type="monotone" dataKey="portfolio" stroke="#3B82F6" strokeWidth={2} name="Your Portfolio" />
                        <Line type="monotone" dataKey="benchmark" stroke="#10B981" strokeWidth={2} name="S&P 500" />
                    </LineChart>
                );
            case 'area':
                return (
                    <RechartsAreaChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, '']} />
                        <Area type="monotone" dataKey="portfolio" stackId="1" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} name="Your Portfolio" />
                        <Area type="monotone" dataKey="benchmark" stackId="2" stroke="#10B981" fill="#10B981" fillOpacity={0.6} name="S&P 500" />
                    </RechartsAreaChart>
                );
            case 'bar':
                return (
                    <RechartsBarChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, '']} />
                        <Bar dataKey="portfolio" fill="#3B82F6" name="Your Portfolio" />
                        <Bar dataKey="benchmark" fill="#10B981" name="S&P 500" />
                    </RechartsBarChart>
                );
            case 'candlestick':
                return (
                    <ComposedChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, '']} />
                        <Bar dataKey="high" fill="#10B981" name="High" />
                        <Bar dataKey="low" fill="#EF4444" name="Low" />
                        <Line type="monotone" dataKey="close" stroke="#3B82F6" strokeWidth={2} name="Close" />
                    </ComposedChart>
                );
            default:
                return null;
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
                <p className="mt-2 text-gray-600">Deep dive into your portfolio performance and risk metrics</p>
            </div>

            {/* Chart Controls */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Portfolio Performance</h3>
                    <div className="flex items-center space-x-4">
                        {/* Time Period Selector */}
                        <div className="flex items-center space-x-2">
                            <Calendar className="h-4 w-4 text-gray-500" />
                            <select
                                value={timePeriod}
                                onChange={(e) => setTimePeriod(e.target.value as any)}
                                className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="7d">7 Days</option>
                                <option value="30d">30 Days</option>
                                <option value="90d">90 Days</option>
                                <option value="1y">1 Year</option>
                            </select>
                        </div>

                        {/* Chart Type Selector */}
                        <div className="flex items-center space-x-2">
                            <Settings className="h-4 w-4 text-gray-500" />
                            <div className="flex space-x-1">
                                {Object.entries(chartTypeIcons).map(([type, Icon]) => (
                                    <button
                                        key={type}
                                        onClick={() => setChartType(type as any)}
                                        className={`p-2 rounded-md transition-colors ${chartType === type
                                            ? 'bg-blue-100 text-blue-600'
                                            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                                            }`}
                                        title={`${type.charAt(0).toUpperCase() + type.slice(1)} Chart`}
                                    >
                                        <Icon className="h-4 w-4" />
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Interactive Chart */}
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        {renderChart()}
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <div className="metric-card relative">
                    <div className="flex items-center">
                        <TrendingUp className="h-8 w-8 text-green-600" />
                        <div className="ml-4">
                            <div className="flex items-center">
                                <p className="text-sm font-medium text-gray-600">Total Return</p>
                                <InfoTooltip
                                    content="Total Return measures the overall percentage gain or loss of your portfolio over the selected time period. It includes both capital gains and dividends. A positive return means your portfolio has grown, while negative indicates a loss."
                                    id="total-return"
                                    showTooltip={showTooltip}
                                    setShowTooltip={setShowTooltip}
                                />
                            </div>
                            <p className={`text-2xl font-bold ${performance?.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {performance?.total_return >= 0 ? '+' : ''}{performance?.total_return?.toFixed(2) || '0.00'}%
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card relative">
                    <div className="flex items-center">
                        <BarChart3 className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                            <div className="flex items-center">
                                <p className="text-sm font-medium text-gray-600">Sharpe Ratio</p>
                                <InfoTooltip
                                    content="Sharpe Ratio measures risk-adjusted returns. It shows how much excess return you receive for the extra volatility you endure. Higher values indicate better risk-adjusted performance. A ratio above 1.0 is considered good, above 2.0 is excellent."
                                    id="sharpe-ratio"
                                    showTooltip={showTooltip}
                                    setShowTooltip={setShowTooltip}
                                />
                            </div>
                            <p className="text-2xl font-bold text-gray-900">
                                {performance?.sharpe_ratio?.toFixed(2) || '0.00'}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card relative">
                    <div className="flex items-center">
                        <Shield className="h-8 w-8 text-red-600" />
                        <div className="ml-4">
                            <div className="flex items-center">
                                <p className="text-sm font-medium text-gray-600">Max Drawdown</p>
                                <InfoTooltip
                                    content="Maximum Drawdown is the largest peak-to-trough decline in your portfolio value. It shows the worst-case scenario loss from a peak. Lower values are better as they indicate less severe losses during market downturns."
                                    id="max-drawdown"
                                    showTooltip={showTooltip}
                                    setShowTooltip={setShowTooltip}
                                />
                            </div>
                            <p className="text-2xl font-bold text-gray-900">
                                {performance?.max_drawdown?.toFixed(2) || '0.00'}%
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card relative">
                    <div className="flex items-center">
                        <Target className="h-8 w-8 text-purple-600" />
                        <div className="ml-4">
                            <div className="flex items-center">
                                <p className="text-sm font-medium text-gray-600">Volatility</p>
                                <InfoTooltip
                                    content="Volatility measures how much your portfolio's returns fluctuate over time. Higher volatility means more price swings (both up and down). Lower volatility indicates more stable, predictable returns. It's calculated as the standard deviation of returns."
                                    id="volatility"
                                    showTooltip={showTooltip}
                                    setShowTooltip={setShowTooltip}
                                />
                            </div>
                            <p className="text-2xl font-bold text-gray-900">
                                {performance?.volatility?.toFixed(2) || '0.00'}%
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Performance Comparison */}
                <div className="card relative">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">Performance vs Benchmark</h3>
                        <InfoTooltip
                            content="This chart compares your portfolio performance against the S&P 500 benchmark. The blue line shows your portfolio value over time, while the green line represents the S&P 500. Use this to see if you're outperforming or underperforming the market."
                            id="performance-chart"
                            showTooltip={showTooltip}
                            setShowTooltip={setShowTooltip}
                        />
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={performanceData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip
                                formatter={(value: any) => [`$${value.toLocaleString()}`, 'Value']}
                                labelFormatter={(label) => `Date: ${label}`}
                            />
                            <Line
                                type="monotone"
                                dataKey="portfolio"
                                stroke="#3B82F6"
                                strokeWidth={2}
                                name="Your Portfolio"
                            />
                            <Line
                                type="monotone"
                                dataKey="benchmark"
                                stroke="#10B981"
                                strokeWidth={2}
                                name="S&P 500"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Portfolio Allocation */}
                <div className="card relative">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">Portfolio Allocation</h3>
                        <InfoTooltip
                            content="This pie chart shows how your portfolio is distributed across different assets. Each slice represents a stock or asset class, with the size indicating the percentage of your total portfolio value. Hover over slices to see exact values and percentages."
                            id="allocation-chart"
                            showTooltip={showTooltip}
                            setShowTooltip={setShowTooltip}
                        />
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={allocationData}
                                cx="50%"
                                cy="50%"
                                outerRadius={100}
                                fill="#8884d8"
                                dataKey="value"
                                label={({ name, percentage }) => `${name} ${percentage}%`}
                                labelLine={false}
                            >
                                {allocationData.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value: any) => [`$${value.toLocaleString()}`, 'Value']}
                                labelFormatter={(label, payload) => {
                                    if (payload && payload[0]) {
                                        return `${payload[0].payload.name} (${payload[0].payload.percentage}%)`;
                                    }
                                    return label;
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Risk Analysis */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="card relative">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">Risk Analysis</h3>
                        <InfoTooltip
                            content="Risk Analysis evaluates your portfolio's exposure to potential losses. Risk Level is determined by volatility and drawdown patterns. Risk Score (0-10) rates your portfolio's riskiness. VaR (Value at Risk) shows the maximum expected loss with 95% confidence."
                            id="risk-analysis"
                            showTooltip={showTooltip}
                            setShowTooltip={setShowTooltip}
                        />
                    </div>
                    <div className="space-y-4">
                        <div>
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-gray-600">Risk Level</span>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${riskMetrics?.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                                    riskMetrics?.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-red-100 text-red-800'
                                    }`}>
                                    {riskMetrics?.risk_level?.toUpperCase() || 'UNKNOWN'}
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                    className={`h-2 rounded-full ${riskMetrics?.risk_level === 'low' ? 'bg-green-500' :
                                        riskMetrics?.risk_level === 'medium' ? 'bg-yellow-500' :
                                            'bg-red-500'
                                        }`}
                                    style={{
                                        width: `${riskMetrics?.risk_level === 'low' ? '25' :
                                            riskMetrics?.risk_level === 'medium' ? '50' : '75'}%`
                                    }}
                                ></div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Risk Score</p>
                                <p className="text-2xl font-bold text-gray-900">
                                    {riskMetrics?.risk_score || 0}/10
                                </p>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-600">VaR (95%)</p>
                                <p className="text-2xl font-bold text-gray-900">
                                    {riskMetrics?.var_95?.toFixed(2) || '0.00'}%
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card relative">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">Benchmark Comparison</h3>
                        <InfoTooltip
                            content="This section compares your portfolio performance against the S&P 500 benchmark. Your Return shows your portfolio's performance, S&P 500 Return shows the market's performance. Excess Return is the difference between them. Sharpe Ratio Difference compares risk-adjusted returns."
                            id="benchmark-comparison"
                            showTooltip={showTooltip}
                            setShowTooltip={setShowTooltip}
                        />
                    </div>
                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm font-medium text-gray-600">Your Return</p>
                                <p className={`text-xl font-bold ${benchmark?.portfolio?.return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {(benchmark?.portfolio?.return * 100)?.toFixed(2) || '0.00'}%
                                </p>
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-600">S&P 500 Return</p>
                                <p className={`text-xl font-bold ${benchmark?.benchmark?.return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {(benchmark?.benchmark?.return * 100)?.toFixed(2) || '0.00'}%
                                </p>
                            </div>
                        </div>

                        <div>
                            <p className="text-sm font-medium text-gray-600">Excess Return</p>
                            <p className={`text-xl font-bold ${benchmark?.comparison?.excess_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {(benchmark?.comparison?.excess_return * 100)?.toFixed(2) || '0.00'}%
                            </p>
                        </div>

                        <div>
                            <p className="text-sm font-medium text-gray-600">Sharpe Ratio Difference</p>
                            <p className={`text-lg font-bold ${benchmark?.comparison?.sharpe_difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {benchmark?.comparison?.sharpe_difference >= 0 ? '+' : ''}{benchmark?.comparison?.sharpe_difference?.toFixed(2) || '0.00'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

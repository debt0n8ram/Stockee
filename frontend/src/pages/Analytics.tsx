import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, TrendingUp, Shield, Target } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { apiService } from '../services/api';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export const Analytics: React.FC = () => {
    const { data: performance, isLoading: performanceLoading } = useQuery(
        'performance-analytics',
        () => apiService.getPerformanceAnalytics('user1', 30),
        { refetchInterval: 60000 }
    );

    const { data: riskMetrics, isLoading: riskLoading } = useQuery(
        'risk-metrics',
        () => apiService.getRiskMetrics('user1', 30),
        { refetchInterval: 60000 }
    );

    const { data: benchmark, isLoading: benchmarkLoading } = useQuery(
        'benchmark-comparison',
        () => apiService.getBenchmarkComparison('user1', 'SPY', 30),
        { refetchInterval: 300000 }
    );

    const { data: allocation, isLoading: allocationLoading } = useQuery(
        'portfolio-allocation',
        () => apiService.getPortfolioAllocation('user1'),
        { refetchInterval: 300000 }
    );

    if (performanceLoading || riskLoading || benchmarkLoading || allocationLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    // Mock data for charts
    const performanceData = [
        { date: '2024-01-01', portfolio: 100000, benchmark: 100000 },
        { date: '2024-01-02', portfolio: 101500, benchmark: 100200 },
        { date: '2024-01-03', portfolio: 102200, benchmark: 100500 },
        { date: '2024-01-04', portfolio: 101800, benchmark: 100300 },
        { date: '2024-01-05', portfolio: 103500, benchmark: 100800 },
        { date: '2024-01-06', portfolio: 104200, benchmark: 101000 },
        { date: '2024-01-07', portfolio: 105000, benchmark: 101200 },
    ];

    const allocationData = allocation?.stocks?.map((stock: any) => ({
        name: stock.symbol,
        value: stock.value,
        percentage: stock.percentage
    })) || [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
                <p className="mt-2 text-gray-600">Deep dive into your portfolio performance and risk metrics</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <div className="metric-card">
                    <div className="flex items-center">
                        <TrendingUp className="h-8 w-8 text-green-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Total Return</p>
                            <p className={`text-2xl font-bold ${performance?.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {performance?.total_return >= 0 ? '+' : ''}{performance?.total_return?.toFixed(2) || '0.00'}%
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card">
                    <div className="flex items-center">
                        <BarChart3 className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Sharpe Ratio</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {performance?.sharpe_ratio?.toFixed(2) || '0.00'}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card">
                    <div className="flex items-center">
                        <Shield className="h-8 w-8 text-red-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Max Drawdown</p>
                            <p className="text-2xl font-bold text-gray-900">
                                {performance?.max_drawdown?.toFixed(2) || '0.00'}%
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card">
                    <div className="flex items-center">
                        <Target className="h-8 w-8 text-purple-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Volatility</p>
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
                <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Performance vs Benchmark</h3>
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
                <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Allocation</h3>
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
                            >
                                {allocationData.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value: any) => [`$${value.toLocaleString()}`, 'Value']} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Risk Analysis */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Risk Analysis</h3>
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

                <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Benchmark Comparison</h3>
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

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, TrendingDown, DollarSign, Trophy } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart as RechartsPieChart, Cell } from 'recharts';
import { apiService } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Portfolio, Performance, AIOpponent, PortfolioAllocation } from '../types/api';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export const Dashboard: React.FC = () => {
    const navigate = useNavigate();

    const { data: portfolio, isLoading: portfolioLoading } = useQuery<Portfolio>({
        queryKey: ['portfolio'],
        queryFn: () => apiService.getPortfolio('user1'),
        refetchInterval: 30000
    });

    const { data: performance, isLoading: performanceLoading } = useQuery<Performance>({
        queryKey: ['performance'],
        queryFn: () => apiService.getPerformance('user1'),
        refetchInterval: 60000
    });

    // Check for active AI competition
    const { data: aiOpponent } = useQuery<AIOpponent>({
        queryKey: ['ai-opponent'],
        queryFn: () => apiService.getAIOpponent('user1'),
        refetchInterval: 60000, // Check every minute
        retry: false // Don't retry if no opponent exists
    });

    const { data: allocation, isLoading: allocationLoading } = useQuery<PortfolioAllocation>({
        queryKey: ['allocation'],
        queryFn: () => apiService.getPortfolioAllocation('user1'),
        refetchInterval: 60000
    });

    if (portfolioLoading || performanceLoading || allocationLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    const portfolioValue = portfolio?.total_value || 0;
    const cashBalance = portfolio?.cash_balance || 0;
    const totalReturn = performance?.total_return || 0;
    const dailyReturn = performance?.daily_return || 0;

    // Mock chart data
    const chartData = [
        { date: '2024-01-01', value: 100000 },
        { date: '2024-01-02', value: 101500 },
        { date: '2024-01-03', value: 102200 },
        { date: '2024-01-04', value: 101800 },
        { date: '2024-01-05', value: 103500 },
        { date: '2024-01-06', value: 104200 },
        { date: '2024-01-07', value: 105000 },
    ];

    const pieData = allocation?.allocation?.stocks?.map((stock: any) => ({
        name: stock.symbol,
        value: stock.value,
        percentage: stock.percentage
    })) || [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="mt-2 text-gray-600">Overview of your trading portfolio</p>
            </div>

            {/* Active Competition Status */}
            {aiOpponent && (
                <div className="bg-gradient-to-r from-purple-500 to-blue-600 rounded-lg shadow-md p-6 text-white">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center">
                            <Trophy className="h-8 w-8 text-yellow-300 mr-3" />
                            <div>
                                <h3 className="text-xl font-bold">Active AI Competition</h3>
                                <p className="text-purple-100">
                                    Competing against {aiOpponent.strategy_type} AI strategy
                                </p>
                                <p className="text-sm text-purple-200">
                                    Started: {new Date(aiOpponent.start_date).toLocaleDateString()}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={() => navigate('/competition')}
                            className="bg-white text-purple-600 px-6 py-2 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
                        >
                            View Competition
                        </button>
                    </div>
                </div>
            )}

            {/* Key Metrics */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <div className="metric-card">
                    <div className="flex items-center">
                        <DollarSign className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Portfolio Value</p>
                            <p className="text-2xl font-bold text-gray-900">
                                ${portfolioValue.toLocaleString()}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card">
                    <div className="flex items-center">
                        <DollarSign className="h-8 w-8 text-green-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Cash Balance</p>
                            <p className="text-2xl font-bold text-gray-900">
                                ${cashBalance.toLocaleString()}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card">
                    <div className="flex items-center">
                        {totalReturn >= 0 ? (
                            <TrendingUp className="h-8 w-8 text-green-600" />
                        ) : (
                            <TrendingDown className="h-8 w-8 text-red-600" />
                        )}
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Total Return</p>
                            <p className={`text-2xl font-bold ${totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {totalReturn >= 0 ? '+' : ''}{totalReturn.toFixed(2)}%
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card">
                    <div className="flex items-center">
                        {dailyReturn >= 0 ? (
                            <TrendingUp className="h-8 w-8 text-green-600" />
                        ) : (
                            <TrendingDown className="h-8 w-8 text-red-600" />
                        )}
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Daily Return</p>
                            <p className={`text-2xl font-bold ${dailyReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {dailyReturn >= 0 ? '+' : ''}{dailyReturn.toFixed(2)}%
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Portfolio Value Chart */}
                <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Value Trend</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip
                                formatter={(value: any) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
                                labelFormatter={(label) => `Date: ${label}`}
                            />
                            <Line
                                type="monotone"
                                dataKey="value"
                                stroke="#3B82F6"
                                strokeWidth={2}
                                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Portfolio Allocation */}
                <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Allocation</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <RechartsPieChart>
                            <RechartsPieChart
                                data={pieData}
                                cx="50%"
                                cy="50%"
                                outerRadius={100}
                                dataKey="value"
                            >
                                {pieData.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </RechartsPieChart>
                            <Tooltip formatter={(value: any) => [`$${value.toLocaleString()}`, 'Value']} />
                        </RechartsPieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
                <div className="space-y-3">
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                        <div className="flex items-center">
                            <TrendingUp className="h-5 w-5 text-green-600 mr-3" />
                            <div>
                                <p className="text-sm font-medium text-gray-900">Bought AAPL</p>
                                <p className="text-xs text-gray-500">10 shares at $150.00</p>
                            </div>
                        </div>
                        <span className="text-sm text-gray-500">2 hours ago</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                        <div className="flex items-center">
                            <TrendingDown className="h-5 w-5 text-red-600 mr-3" />
                            <div>
                                <p className="text-sm font-medium text-gray-900">Sold TSLA</p>
                                <p className="text-xs text-gray-500">5 shares at $200.00</p>
                            </div>
                        </div>
                        <span className="text-sm text-gray-500">1 day ago</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

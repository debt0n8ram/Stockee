import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Wallet, TrendingUp, TrendingDown, DollarSign, RefreshCw } from 'lucide-react';
import { apiService } from '../services/api';
import { Portfolio as PortfolioType, Holding, Transaction } from '../types/api';

export const Portfolio: React.FC = () => {
    const { data: portfolio, isLoading: portfolioLoading } = useQuery<PortfolioType>({
        queryKey: ['portfolio'],
        queryFn: () => apiService.getPortfolio('user1'),
        refetchInterval: 30000
    });

    const { data: holdings, isLoading: holdingsLoading } = useQuery<Holding[]>({
        queryKey: ['holdings'],
        queryFn: () => apiService.getHoldings('user1'),
        refetchInterval: 30000
    });

    const { data: transactions, isLoading: transactionsLoading } = useQuery<Transaction[]>({
        queryKey: ['transactions'],
        queryFn: () => apiService.getTransactions('user1', 20),
        refetchInterval: 60000
    });

    if (portfolioLoading || holdingsLoading || transactionsLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    const portfolioValue = portfolio?.total_value || 0;
    const cashBalance = portfolio?.cash_balance || 0;
    const investedValue = portfolioValue - cashBalance;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
                    <p className="mt-2 text-gray-600">Manage your investments and track performance</p>
                </div>
                <button
                    onClick={() => apiService.resetPortfolio('user1')}
                    className="btn-secondary flex items-center"
                >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reset Portfolio
                </button>
            </div>

            {/* Portfolio Summary */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                <div className="metric-card">
                    <div className="flex items-center">
                        <DollarSign className="h-8 w-8 text-blue-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Total Value</p>
                            <p className="text-2xl font-bold text-gray-900">
                                ${portfolioValue.toLocaleString()}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="metric-card">
                    <div className="flex items-center">
                        <Wallet className="h-8 w-8 text-green-600" />
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
                        <TrendingUp className="h-8 w-8 text-purple-600" />
                        <div className="ml-4">
                            <p className="text-sm font-medium text-gray-600">Invested Value</p>
                            <p className="text-2xl font-bold text-gray-900">
                                ${investedValue.toLocaleString()}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Holdings */}
                <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Current Holdings</h3>

                    {holdings && holdings.length > 0 ? (
                        <div className="space-y-3">
                            {holdings.map((holding: any) => (
                                <div key={holding.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                    <div>
                                        <p className="font-medium text-gray-900">{holding.asset?.symbol || 'Unknown'}</p>
                                        <p className="text-sm text-gray-600">{holding.quantity} shares</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-medium text-gray-900">
                                            ${(holding.current_value || holding.quantity * holding.average_cost).toLocaleString()}
                                        </p>
                                        <p className={`text-sm ${holding.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {holding.unrealized_pnl >= 0 ? '+' : ''}${holding.unrealized_pnl?.toFixed(2) || '0.00'}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <Wallet className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                            <p>No holdings yet</p>
                            <p className="text-sm">Start trading to build your portfolio</p>
                        </div>
                    )}
                </div>

                {/* Recent Transactions */}
                <div className="card">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Transactions</h3>

                    {transactions && transactions.length > 0 ? (
                        <div className="space-y-3">
                            {transactions.map((transaction: any) => (
                                <div key={transaction.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center">
                                        {transaction.transaction_type === 'buy' ? (
                                            <TrendingUp className="h-5 w-5 text-green-600 mr-3" />
                                        ) : (
                                            <TrendingDown className="h-5 w-5 text-red-600 mr-3" />
                                        )}
                                        <div>
                                            <p className="font-medium text-gray-900">
                                                {transaction.transaction_type.toUpperCase()} {transaction.asset?.symbol || 'Unknown'}
                                            </p>
                                            <p className="text-sm text-gray-600">
                                                {transaction.quantity} shares at ${transaction.price}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-medium text-gray-900">
                                            ${transaction.total_amount.toLocaleString()}
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {new Date(transaction.timestamp).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                            <p>No transactions yet</p>
                            <p className="text-sm">Your trading history will appear here</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

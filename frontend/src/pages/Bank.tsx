import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CreditCard, DollarSign, TrendingUp, History, RefreshCw, Plus, Minus } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { apiService } from '../services/api';
import { BankTransactions } from '../types/api';

export const Bank: React.FC = () => {
    const [depositAmount, setDepositAmount] = useState('');
    const [withdrawAmount, setWithdrawAmount] = useState('');
    const [resetAmount, setResetAmount] = useState('');
    const [depositDescription, setDepositDescription] = useState('');
    const [withdrawDescription, setWithdrawDescription] = useState('');

    const queryClient = useQueryClient();
    const userId = 'user1'; // In a real app, this would come from auth context

    // Get current balance
    const { data: balance, isLoading: balanceLoading } = useQuery(
        'bank-balance',
        () => apiService.getCashBalance(userId),
        { refetchInterval: 5000 }
    );

    // Get transaction history
    const { data: transactions, isLoading: transactionsLoading } = useQuery<BankTransactions>({
        queryKey: ['bank-transactions'],
        queryFn: () => apiService.getBankTransactions(userId, 20)
    });

    // Deposit mutation
    const depositMutation = useMutation(
        (data: { amount: number; description: string }) =>
            apiService.depositCash(userId, data.amount, data.description),
        {
            onSuccess: (data) => {
                toast.success(data.message);
                setDepositAmount('');
                setDepositDescription('');
                queryClient.invalidateQueries('bank-balance');
                queryClient.invalidateQueries('bank-transactions');
                queryClient.invalidateQueries('portfolio');
            },
            onError: (error: any) => {
                toast.error(error.response?.data?.detail || 'Deposit failed');
            }
        }
    );

    // Withdraw mutation
    const withdrawMutation = useMutation(
        (data: { amount: number; description: string }) =>
            apiService.withdrawCash(userId, data.amount, data.description),
        {
            onSuccess: (data) => {
                toast.success(data.message);
                setWithdrawAmount('');
                setWithdrawDescription('');
                queryClient.invalidateQueries('bank-balance');
                queryClient.invalidateQueries('bank-transactions');
                queryClient.invalidateQueries('portfolio');
            },
            onError: (error: any) => {
                toast.error(error.response?.data?.detail || 'Withdrawal failed');
            }
        }
    );

    // Reset balance mutation
    const resetMutation = useMutation(
        (newBalance: number) => apiService.resetBalance(userId, newBalance),
        {
            onSuccess: (data) => {
                toast.success(data.message);
                setResetAmount('');
                queryClient.invalidateQueries('bank-balance');
                queryClient.invalidateQueries('bank-transactions');
                queryClient.invalidateQueries('portfolio');
            },
            onError: (error: any) => {
                toast.error(error.response?.data?.detail || 'Reset failed');
            }
        }
    );

    const handleDeposit = (e: React.FormEvent) => {
        e.preventDefault();
        const amount = parseFloat(depositAmount);
        if (amount <= 0) {
            toast.error('Amount must be positive');
            return;
        }
        depositMutation.mutate({
            amount,
            description: depositDescription || 'Deposit'
        });
    };

    const handleWithdraw = (e: React.FormEvent) => {
        e.preventDefault();
        const amount = parseFloat(withdrawAmount);
        if (amount <= 0) {
            toast.error('Amount must be positive');
            return;
        }
        if (amount > (balance?.cash_balance || 0)) {
            toast.error('Insufficient funds');
            return;
        }
        withdrawMutation.mutate({
            amount,
            description: withdrawDescription || 'Withdrawal'
        });
    };

    const handleReset = (e: React.FormEvent) => {
        e.preventDefault();
        const newBalance = parseFloat(resetAmount);
        if (newBalance < 0) {
            toast.error('Balance cannot be negative');
            return;
        }
        if (window.confirm(`Are you sure you want to reset your balance to $${newBalance.toLocaleString()}?`)) {
            resetMutation.mutate(newBalance);
        }
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Bank</h1>
                <p className="text-gray-600">Manage your cash balance and view transaction history</p>
            </div>

            {/* Balance Card */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900 mb-2">Current Balance</h2>
                        {balanceLoading ? (
                            <div className="flex items-center">
                                <RefreshCw className="animate-spin h-5 w-5 text-blue-500 mr-2" />
                                <span className="text-gray-500">Loading...</span>
                            </div>
                        ) : (
                            <div className="text-4xl font-bold text-green-600">
                                {formatCurrency(balance?.cash_balance || 0)}
                            </div>
                        )}
                    </div>
                    <div className="text-right">
                        <div className="text-sm text-gray-500">Available Cash</div>
                        <div className="text-lg font-medium text-gray-900">
                            {formatCurrency(balance?.cash_balance || 0)}
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Deposit Section */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center mb-4">
                        <Plus className="h-6 w-6 text-green-600 mr-2" />
                        <h3 className="text-xl font-semibold text-gray-900">Deposit Cash</h3>
                    </div>

                    <form onSubmit={handleDeposit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Amount
                            </label>
                            <div className="relative">
                                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                                <input
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    value={depositAmount}
                                    onChange={(e) => setDepositAmount(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                    placeholder="0.00"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Description (Optional)
                            </label>
                            <input
                                type="text"
                                value={depositDescription}
                                onChange={(e) => setDepositDescription(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                                placeholder="e.g., Initial deposit, Bonus, etc."
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={depositMutation.isLoading}
                            className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        >
                            {depositMutation.isLoading ? (
                                <RefreshCw className="animate-spin h-5 w-5 mr-2" />
                            ) : (
                                <Plus className="h-5 w-5 mr-2" />
                            )}
                            Deposit Cash
                        </button>
                    </form>
                </div>

                {/* Withdraw Section */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center mb-4">
                        <Minus className="h-6 w-6 text-red-600 mr-2" />
                        <h3 className="text-xl font-semibold text-gray-900">Withdraw Cash</h3>
                    </div>

                    <form onSubmit={handleWithdraw} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Amount
                            </label>
                            <div className="relative">
                                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                                <input
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    max={balance?.cash_balance || 0}
                                    value={withdrawAmount}
                                    onChange={(e) => setWithdrawAmount(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                                    placeholder="0.00"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Description (Optional)
                            </label>
                            <input
                                type="text"
                                value={withdrawDescription}
                                onChange={(e) => setWithdrawDescription(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                                placeholder="e.g., Cash withdrawal, etc."
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={withdrawMutation.isPending}
                            className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        >
                            {withdrawMutation.isPending ? (
                                <RefreshCw className="animate-spin h-5 w-5 mr-2" />
                            ) : (
                                <Minus className="h-5 w-5 mr-2" />
                            )}
                            Withdraw Cash
                        </button>
                    </form>
                </div>
            </div>

            {/* Reset Balance Section */}
            <div className="bg-white rounded-lg shadow-md p-6 mt-8">
                <div className="flex items-center mb-4">
                    <RefreshCw className="h-6 w-6 text-blue-600 mr-2" />
                    <h3 className="text-xl font-semibold text-gray-900">Reset Balance</h3>
                </div>
                <p className="text-gray-600 mb-4">Reset your cash balance to a specific amount (for testing purposes)</p>

                <form onSubmit={handleReset} className="flex items-end space-x-4">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            New Balance
                        </label>
                        <div className="relative">
                            <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <input
                                type="number"
                                step="0.01"
                                min="0"
                                value={resetAmount}
                                onChange={(e) => setResetAmount(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="0.00"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={resetMutation.isPending}
                        className="bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                    >
                        {resetMutation.isPending ? (
                            <RefreshCw className="animate-spin h-5 w-5 mr-2" />
                        ) : (
                            <RefreshCw className="h-5 w-5 mr-2" />
                        )}
                        Reset Balance
                    </button>
                </form>
            </div>

            {/* Transaction History */}
            <div className="bg-white rounded-lg shadow-md p-6 mt-8">
                <div className="flex items-center mb-4">
                    <History className="h-6 w-6 text-gray-600 mr-2" />
                    <h3 className="text-xl font-semibold text-gray-900">Transaction History</h3>
                </div>

                {transactionsLoading ? (
                    <div className="flex items-center justify-center py-8">
                        <RefreshCw className="animate-spin h-6 w-6 text-blue-500 mr-2" />
                        <span className="text-gray-500">Loading transactions...</span>
                    </div>
                ) : transactions && 'transactions' in transactions && Array.isArray(transactions.transactions) && transactions.transactions.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                                    <th className="text-left py-3 px-4 font-medium text-gray-700">Type</th>
                                    <th className="text-left py-3 px-4 font-medium text-gray-700">Description</th>
                                    <th className="text-right py-3 px-4 font-medium text-gray-700">Amount</th>
                                    <th className="text-right py-3 px-4 font-medium text-gray-700">Balance After</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.transactions.map((transaction: any) => (
                                    <tr key={transaction.id} className="border-b border-gray-100 hover:bg-gray-50">
                                        <td className="py-3 px-4 text-sm text-gray-600">
                                            {formatDate(transaction.timestamp)}
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${transaction.transaction_type === 'deposit'
                                                ? 'bg-green-100 text-green-800'
                                                : transaction.transaction_type === 'withdrawal'
                                                    ? 'bg-red-100 text-red-800'
                                                    : 'bg-blue-100 text-blue-800'
                                                }`}>
                                                {transaction.transaction_type.charAt(0).toUpperCase() + transaction.transaction_type.slice(1)}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-600">
                                            {transaction.description}
                                        </td>
                                        <td className={`py-3 px-4 text-sm font-medium text-right ${transaction.transaction_type === 'deposit'
                                            ? 'text-green-600'
                                            : transaction.transaction_type === 'withdrawal'
                                                ? 'text-red-600'
                                                : 'text-blue-600'
                                            }`}>
                                            {transaction.transaction_type === 'deposit' ? '+' : '-'}
                                            {formatCurrency(transaction.amount)}
                                        </td>
                                        <td className="py-3 px-4 text-sm font-medium text-right text-gray-900">
                                            {formatCurrency(transaction.balance_after)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center py-8 text-gray-500">
                        <History className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p>No transactions yet</p>
                        <p className="text-sm">Your transaction history will appear here</p>
                    </div>
                )}
            </div>
        </div>
    );
};

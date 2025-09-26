import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { toast } from 'react-hot-toast';
import { apiService } from '../services/api';

export const Competition: React.FC = () => {
    const [selectedStrategy, setSelectedStrategy] = useState('conservative');
    const [hasOpponent, setHasOpponent] = useState(false);
    const queryClient = useQueryClient();

    // Fetch available strategies
    const { data: strategies } = useQuery({
        queryKey: ['ai-strategies'],
        queryFn: () => apiService.getAIStrategies()
    });

    // Check for existing AI opponent
    const { data: opponentData, isLoading: opponentLoading } = useQuery({
        queryKey: ['ai-opponent'],
        queryFn: () => apiService.getAIOpponent('user1')
    });

    // Handle opponent data changes
    React.useEffect(() => {
        if (opponentData) {
            setHasOpponent(true);
        } else {
            setHasOpponent(false);
        }
    }, [opponentData]);

    // Fetch competition data
    const { data: competitionData, isLoading: competitionLoading } = useQuery({
        queryKey: ['competition-data'],
        queryFn: () => apiService.getCompetitionData('user1'),
        enabled: hasOpponent,
        refetchInterval: 300000 // Refresh every 5 minutes
    });

    // Fetch background AI status
    const { data: backgroundStatus, isLoading: backgroundLoading } = useQuery({
        queryKey: ['background-ai-status'],
        queryFn: () => apiService.getBackgroundAIStatus(),
        refetchInterval: 300000 // Refresh every 5 minutes
    });

    // Create AI opponent mutation
    const createOpponentMutation = useMutation({
        mutationFn: (strategyType: string) => apiService.createAIOpponent('user1', strategyType),
        onSuccess: () => {
            toast.success('AI Opponent created successfully!');
            setHasOpponent(true);
            queryClient.invalidateQueries({ queryKey: ['ai-opponent'] });
            queryClient.invalidateQueries({ queryKey: ['competition-data'] });
        },
        onError: (error: any) => {
            if (error?.response?.status === 400 && error?.response?.data?.detail?.includes('already has an active AI opponent')) {
                toast.error('You already have an active AI opponent. Please deactivate it first or refresh the page to see your current competition.');
                setHasOpponent(true); // Set to true so they can see their existing opponent
                queryClient.invalidateQueries({ queryKey: ['ai-opponent'] });
            } else {
                toast.error(error?.response?.data?.detail || error?.message || 'Failed to create AI opponent');
            }
        }
    });

    // Execute AI trading mutation
    const executeAITradingMutation = useMutation({
        mutationFn: () => apiService.executeAITrading('user1'),
        onSuccess: (data) => {
            toast.success(`AI executed ${data.trades_executed} trades!`);
            queryClient.invalidateQueries({ queryKey: ['competition-data'] });
        },
        onError: (error: any) => {
            toast.error(error?.message || 'Failed to execute AI trading');
        }
    });

    // Deactivate AI opponent mutation
    const deactivateOpponentMutation = useMutation({
        mutationFn: () => apiService.deactivateAIOpponent('user1'),
        onSuccess: () => {
            toast.success('AI Opponent deactivated successfully!');
            setHasOpponent(false);
            queryClient.invalidateQueries({ queryKey: ['ai-opponent'] });
            queryClient.invalidateQueries({ queryKey: ['competition-data'] });
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || error?.message || 'Failed to deactivate AI opponent');
        }
    });

    // Background AI control mutations
    const startBackgroundAIMutation = useMutation({
        mutationFn: () => apiService.startBackgroundAI(),
        onSuccess: () => {
            toast.success('Background AI trading started!');
            queryClient.invalidateQueries({ queryKey: ['background-ai-status'] });
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || error?.message || 'Failed to start background AI');
        }
    });

    const stopBackgroundAIMutation = useMutation({
        mutationFn: () => apiService.stopBackgroundAI(),
        onSuccess: () => {
            toast.success('Background AI trading stopped!');
            queryClient.invalidateQueries({ queryKey: ['background-ai-status'] });
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || error?.message || 'Failed to stop background AI');
        }
    });

    const handleCreateOpponent = () => {
        createOpponentMutation.mutate(selectedStrategy);
    };

    const handleExecuteAITrading = () => {
        executeAITradingMutation.mutate();
    };

    const handleDeactivateOpponent = () => {
        deactivateOpponentMutation.mutate();
    };

    const handleStartBackgroundAI = () => {
        startBackgroundAIMutation.mutate();
    };

    const handleStopBackgroundAI = () => {
        stopBackgroundAIMutation.mutate();
    };

    if (opponentLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    // Strategy Selection Screen
    if (!hasOpponent) {
        return (
            <div className="space-y-6">
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-gray-900">AI Trading Competition</h1>
                    <p className="mt-2 text-gray-600">Challenge an AI opponent and see who's the better trader!</p>
                </div>

                <div className="bg-white rounded-lg shadow-md p-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Choose Your AI Opponent Strategy</h2>
                    {strategies && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                            {Object.entries(strategies).map(([key, strategy]: [string, any]) => (
                                <div
                                    key={key}
                                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${selectedStrategy === key ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}`}
                                    onClick={() => setSelectedStrategy(key)}
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <h4 className="font-bold text-gray-900">{strategy.name}</h4>
                                        <span className={`px-2 py-1 text-xs rounded ${strategy.risk_level === 'Low' ? 'bg-green-100 text-green-800' : strategy.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                            {strategy.risk_level} Risk
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 mb-3">{strategy.description}</p>
                                    <div className="text-xs text-gray-500">
                                        <div>Max Position: {strategy.max_position_size * 100}%</div>
                                        <div>Max Trades/Day: {strategy.max_trades_per_day}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="flex justify-center">
                        <button
                            onClick={handleCreateOpponent}
                            disabled={createOpponentMutation.isPending}
                            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            {createOpponentMutation.isPending ? 'Creating...' : 'Start Competition!'}
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // Competition Dashboard
    if (competitionLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    const userData = competitionData?.user_performance;
    const aiData = competitionData?.ai_performance;
    const competition = competitionData?.competition;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">AI Trading Competition</h1>
                    <p className="mt-2 text-gray-600">
                        You vs {aiData?.strategy || 'AI Opponent'}
                    </p>
                </div>
                <div className="flex space-x-3">
                    <button
                        onClick={handleExecuteAITrading}
                        disabled={executeAITradingMutation.isPending}
                        className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50 flex items-center"
                    >
                        <span className="mr-2">▶</span>
                        {executeAITradingMutation.isPending ? 'Trading...' : 'Execute AI Trades'}
                    </button>
                    <button
                        onClick={handleDeactivateOpponent}
                        disabled={deactivateOpponentMutation.isPending}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center"
                    >
                        <span className="mr-2">⏸</span>
                        {deactivateOpponentMutation.isPending ? 'Deactivating...' : 'End Competition'}
                    </button>
                    <button
                        onClick={() => queryClient.invalidateQueries({ queryKey: ['competition-data'] })}
                        className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50 flex items-center"
                    >
                        <span className="mr-2">🔄</span>
                        Refresh
                    </button>
                </div>
            </div>

            {/* Background AI Status */}
            {backgroundStatus && (
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-900">Background AI Trading</h3>
                        <div className="flex space-x-2">
                            {backgroundStatus.is_running ? (
                                <button
                                    onClick={handleStopBackgroundAI}
                                    disabled={stopBackgroundAIMutation.isPending}
                                    className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
                                >
                                    {stopBackgroundAIMutation.isPending ? 'Stopping...' : 'Stop Background AI'}
                                </button>
                            ) : (
                                <button
                                    onClick={handleStartBackgroundAI}
                                    disabled={startBackgroundAIMutation.isPending}
                                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
                                >
                                    {startBackgroundAIMutation.isPending ? 'Starting...' : 'Start Background AI'}
                                </button>
                            )}
                        </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="text-center">
                            <div className={`text-2xl font-bold ${backgroundStatus.is_running ? 'text-green-600' : 'text-red-600'}`}>
                                {backgroundStatus.is_running ? '🟢 Running' : '🔴 Stopped'}
                            </div>
                            <p className="text-sm text-gray-600">Status</p>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">
                                {backgroundStatus.active_opponents_count || 0}
                            </div>
                            <p className="text-sm text-gray-600">Active Opponents</p>
                        </div>
                        <div className="text-center">
                            <div className="text-sm font-bold text-gray-600">
                                {backgroundStatus.next_trading_round || 'N/A'}
                            </div>
                            <p className="text-sm text-gray-600">Next Trading Round</p>
                        </div>
                    </div>
                    <div className="mt-4 text-sm text-gray-600">
                        <p><strong>Schedule:</strong> Trading rounds every 30 minutes, Portfolio updates every hour</p>
                        <p><strong>Daily Analysis:</strong> 9:30 AM and 4:00 PM market hours</p>
                    </div>
                </div>
            )}

            {/* Competition Status */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* User Performance */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                            <span className="text-2xl mr-2">👤</span>
                            <h3 className="text-lg font-bold text-gray-900">You</h3>
                        </div>
                        {competition?.leader === 'user' && (
                            <span className="text-2xl">🏆</span>
                        )}
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-600">Portfolio Value:</span>
                            <span className="font-bold">${userData?.total_value?.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Return:</span>
                            <span className={`font-bold ${userData?.return_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {userData?.return_percentage >= 0 ? '+' : ''}
                                {userData?.return_percentage?.toFixed(2)}%
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Gain/Loss:</span>
                            <span className={`font-bold ${userData?.return_amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {userData?.return_amount >= 0 ? '+' : ''}
                                ${userData?.return_amount?.toLocaleString()}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Competition Status */}
                <div className="bg-white rounded-lg shadow-md p-6 text-center">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Competition Status</h3>
                    <div className="space-y-3">
                        <div className="text-2xl font-bold text-gray-900">
                            {competition?.leader === 'user' ? 'You\'re Winning!' : competition?.leader === 'ai' ? 'AI is Winning!' : 'Tied!'}
                        </div>
                        <div className="text-sm text-gray-600">
                            {competition?.days_active || 0} days active
                        </div>
                        <div className="text-sm text-gray-600">
                            {competition?.total_trades || 0} total trades
                        </div>
                    </div>
                </div>

                {/* AI Performance */}
                <div className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                            <span className="text-2xl mr-2">🤖</span>
                            <h3 className="text-lg font-bold text-gray-900">AI Opponent</h3>
                        </div>
                        {competition?.leader === 'ai' && (
                            <span className="text-2xl">🏆</span>
                        )}
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-600">Portfolio Value:</span>
                            <span className="font-bold">${aiData?.total_value?.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Return:</span>
                            <span className={`font-bold ${aiData?.return_percentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {aiData?.return_percentage >= 0 ? '+' : ''}
                                {aiData?.return_percentage?.toFixed(2)}%
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-600">Strategy:</span>
                            <span className="font-bold text-purple-600">{aiData?.strategy}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Performance Chart */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Performance Comparison</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={[
                                { name: 'You', value: userData?.return_percentage || 0 },
                                { name: 'AI', value: aiData?.return_percentage || 0 }
                            ]}
                        >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#8884d8" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Achievements Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Achievements</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className={`p-4 rounded-lg border-2 ${competition?.leader === 'user' ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200'}`}>
                        <span className="text-3xl mb-2 block">🏅</span>
                        <h4 className="font-bold">Market Leader</h4>
                        <p className="text-sm text-gray-600">Currently outperforming AI</p>
                    </div>

                    <div className={`p-4 rounded-lg border-2 ${userData?.return_percentage > 5 ? 'border-green-400 bg-green-50' : 'border-gray-200'}`}>
                        <span className="text-3xl mb-2 block">📈</span>
                        <h4 className="font-bold">Profit Maker</h4>
                        <p className="text-sm text-gray-600">Achieved &gt;5% returns</p>
                    </div>

                    <div className={`p-4 rounded-lg border-2 ${userData?.return_percentage > aiData?.return_percentage + 10 ? 'border-blue-400 bg-blue-50' : 'border-gray-200'}`}>
                        <span className="text-3xl mb-2 block">🎯</span>
                        <h4 className="font-bold">AI Crusher</h4>
                        <p className="text-sm text-gray-600">Beat AI by &gt;10%</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Competition;
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Brain, TrendingUp, TrendingDown, Target, BarChart3, RefreshCw, Search } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { apiService } from '../services/api';

export const AIPredictions: React.FC = () => {
    const [searchSymbol, setSearchSymbol] = useState('');
    const [selectedSymbol, setSelectedSymbol] = useState('');
    const [daysAhead, setDaysAhead] = useState(7);

    // Get predictions
    const { data: predictions, isLoading: predictionsLoading, refetch: refetchPredictions } = useQuery({
        queryKey: ['ai-predictions', selectedSymbol, daysAhead],
        queryFn: () => apiService.getAIPredictions(selectedSymbol, daysAhead),
        enabled: !!selectedSymbol,
        onError: (error: any) => {
            toast.error(error.response?.data?.detail || 'Failed to get predictions');
        }
    });

    // Get prediction history
    const { data: history, isLoading: historyLoading } = useQuery({
        queryKey: ['ai-prediction-history', selectedSymbol],
        queryFn: () => apiService.getAIPredictionHistory(selectedSymbol, 10),
        enabled: !!selectedSymbol
    });

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchSymbol.trim()) {
            setSelectedSymbol(searchSymbol.trim().toUpperCase());
        }
    };

    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 0.7) return 'text-green-600 bg-green-100';
        if (confidence >= 0.5) return 'text-yellow-600 bg-yellow-100';
        return 'text-red-600 bg-red-100';
    };

    const getConfidenceText = (confidence: number) => {
        if (confidence >= 0.7) return 'High';
        if (confidence >= 0.5) return 'Medium';
        return 'Low';
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
            day: 'numeric'
        });
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Predictions</h1>
                <p className="text-gray-600">Get AI-powered price predictions using multiple machine learning models</p>
            </div>

            {/* Search Section */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <div className="flex items-center mb-4">
                    <Brain className="h-6 w-6 text-purple-600 mr-2" />
                    <h2 className="text-xl font-semibold text-gray-900">Stock Predictions</h2>
                </div>

                <form onSubmit={handleSearch} className="flex items-end space-x-4">
                    <div className="flex-1">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Stock Symbol
                        </label>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <input
                                type="text"
                                value={searchSymbol}
                                onChange={(e) => setSearchSymbol(e.target.value.toUpperCase())}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                placeholder="e.g., AAPL, MSFT, GOOGL"
                                required
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Days Ahead
                        </label>
                        <select
                            value={daysAhead}
                            onChange={(e) => setDaysAhead(parseInt(e.target.value))}
                            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        >
                            <option value={1}>1 Day</option>
                            <option value={3}>3 Days</option>
                            <option value={7}>7 Days</option>
                            <option value={14}>14 Days</option>
                            <option value={30}>30 Days</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        className="bg-purple-600 text-white py-2 px-6 rounded-lg hover:bg-purple-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 flex items-center"
                    >
                        <Brain className="h-5 w-5 mr-2" />
                        Predict
                    </button>
                </form>
            </div>

            {/* Predictions Results */}
            {selectedSymbol && (
                <>
                    {predictionsLoading ? (
                        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                            <div className="flex items-center justify-center py-12">
                                <RefreshCw className="animate-spin h-8 w-8 text-purple-500 mr-3" />
                                <span className="text-lg text-gray-600">Generating AI predictions...</span>
                            </div>
                        </div>
                    ) : predictions?.predictions ? (
                        <div className="mb-8">
                            {/* Current Price */}
                            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900">{selectedSymbol}</h3>
                                        <p className="text-gray-600">Current Price</p>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-3xl font-bold text-gray-900">
                                            {formatCurrency(predictions.current_price)}
                                        </div>
                                        <div className="text-sm text-gray-500">
                                            Generated: {formatDate(predictions.generated_at)}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Predictions Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {Object.entries(predictions.predictions).map(([modelName, prediction]: [string, any]) => {
                                    if (prediction.error) return null;

                                    const priceChange = prediction.predicted_price - predictions.current_price;
                                    const percentChange = (priceChange / predictions.current_price) * 100;

                                    return (
                                        <div key={modelName} className="bg-white rounded-lg shadow-md p-6">
                                            <div className="flex items-center justify-between mb-4">
                                                <h4 className="font-semibold text-gray-900">{prediction.model_name}</h4>
                                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(prediction.confidence)}`}>
                                                    {getConfidenceText(prediction.confidence)} Confidence
                                                </span>
                                            </div>

                                            <div className="space-y-3">
                                                <div>
                                                    <div className="text-2xl font-bold text-gray-900">
                                                        {formatCurrency(prediction.predicted_price)}
                                                    </div>
                                                    <div className={`text-sm flex items-center ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'
                                                        }`}>
                                                        {priceChange >= 0 ? (
                                                            <TrendingUp className="h-4 w-4 mr-1" />
                                                        ) : (
                                                            <TrendingDown className="h-4 w-4 mr-1" />
                                                        )}
                                                        {priceChange >= 0 ? '+' : ''}{formatCurrency(priceChange)} ({percentChange >= 0 ? '+' : ''}{percentChange.toFixed(2)}%)
                                                    </div>
                                                </div>

                                                <div className="text-sm text-gray-600">
                                                    <div className="flex items-center mb-1">
                                                        <Target className="h-4 w-4 mr-2" />
                                                        <span>Confidence: {(prediction.confidence * 100).toFixed(1)}%</span>
                                                    </div>
                                                    <p className="text-xs text-gray-500 mt-2">
                                                        {prediction.description}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Ensemble Prediction (if available) */}
                            {predictions.predictions.ensemble && (
                                <div className="bg-gradient-to-r from-purple-500 to-blue-600 rounded-lg shadow-md p-6 mt-6">
                                    <div className="flex items-center justify-between text-white">
                                        <div>
                                            <h3 className="text-xl font-bold mb-2">Ensemble Prediction</h3>
                                            <p className="text-purple-100">Average of all AI models</p>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-3xl font-bold">
                                                {formatCurrency(predictions.predictions.ensemble.predicted_price)}
                                            </div>
                                            <div className="text-purple-100">
                                                {(predictions.predictions.ensemble.confidence * 100).toFixed(1)}% Confidence
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                            <div className="text-center py-8">
                                <Brain className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                                <p className="text-gray-500">No predictions available</p>
                                <p className="text-sm text-gray-400">Try searching for a different stock symbol</p>
                            </div>
                        </div>
                    )}

                    {/* Prediction History */}
                    {history?.predictions?.length > 0 && (
                        <div className="bg-white rounded-lg shadow-md p-6">
                            <div className="flex items-center mb-4">
                                <BarChart3 className="h-6 w-6 text-gray-600 mr-2" />
                                <h3 className="text-xl font-semibold text-gray-900">Prediction History</h3>
                            </div>

                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-gray-200">
                                            <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                                            <th className="text-left py-3 px-4 font-medium text-gray-700">Model</th>
                                            <th className="text-right py-3 px-4 font-medium text-gray-700">Predicted Price</th>
                                            <th className="text-right py-3 px-4 font-medium text-gray-700">Confidence</th>
                                            <th className="text-left py-3 px-4 font-medium text-gray-700">Target Date</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {history.predictions.map((prediction: any) => (
                                            <tr key={prediction.id} className="border-b border-gray-100 hover:bg-gray-50">
                                                <td className="py-3 px-4 text-sm text-gray-600">
                                                    {formatDate(prediction.prediction_date)}
                                                </td>
                                                <td className="py-3 px-4 text-sm font-medium text-gray-900">
                                                    {prediction.model_name}
                                                </td>
                                                <td className="py-3 px-4 text-sm font-medium text-right text-gray-900">
                                                    {formatCurrency(prediction.predicted_price)}
                                                </td>
                                                <td className="py-3 px-4 text-right">
                                                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(prediction.confidence)}`}>
                                                        {(prediction.confidence * 100).toFixed(1)}%
                                                    </span>
                                                </td>
                                                <td className="py-3 px-4 text-sm text-gray-600">
                                                    {formatDate(prediction.target_date)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* How It Works */}
            <div className="bg-white rounded-lg shadow-md p-6 mt-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">How AI Predictions Work</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="text-center">
                        <div className="bg-blue-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                            <TrendingUp className="h-6 w-6 text-blue-600" />
                        </div>
                        <h4 className="font-medium text-gray-900 mb-2">Moving Average</h4>
                        <p className="text-sm text-gray-600">Simple trend analysis using historical price averages</p>
                    </div>

                    <div className="text-center">
                        <div className="bg-green-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                            <BarChart3 className="h-6 w-6 text-green-600" />
                        </div>
                        <h4 className="font-medium text-gray-900 mb-2">Linear Regression</h4>
                        <p className="text-sm text-gray-600">Machine learning model trained on technical indicators</p>
                    </div>

                    <div className="text-center">
                        <div className="bg-yellow-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                            <Target className="h-6 w-6 text-yellow-600" />
                        </div>
                        <h4 className="font-medium text-gray-900 mb-2">Trend Analysis</h4>
                        <p className="text-sm text-gray-600">Linear trend analysis over historical data</p>
                    </div>

                    <div className="text-center">
                        <div className="bg-purple-100 rounded-full p-3 w-12 h-12 mx-auto mb-3 flex items-center justify-center">
                            <Brain className="h-6 w-6 text-purple-600" />
                        </div>
                        <h4 className="font-medium text-gray-900 mb-2">Volatility Model</h4>
                        <p className="text-sm text-gray-600">Monte Carlo simulation based on price volatility</p>
                    </div>
                </div>

                <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
                    <p className="text-sm text-yellow-800">
                        <strong>Disclaimer:</strong> AI predictions are for educational purposes only and should not be used as financial advice.
                        Past performance does not guarantee future results. Always do your own research before making investment decisions.
                    </p>
                </div>
            </div>
        </div>
    );
};

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, TrendingUp, TrendingDown, DollarSign, Clock, Globe, BarChart3, Activity, Volume2, Target, Brain } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { apiService } from '../services/api';

export const MarketData: React.FC = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedAsset, setSelectedAsset] = useState<any>(null);
    const [timeframe, setTimeframe] = useState('1d');

    const { data: searchResults, isLoading: searchLoading } = useQuery(
        ['search', searchQuery],
        () => apiService.searchAssets(searchQuery),
        { enabled: searchQuery.length > 2 }
    );

    const { data: currentPrice } = useQuery(
        ['price', selectedAsset?.symbol],
        () => apiService.getCurrentPrice(selectedAsset?.symbol),
        { enabled: !!selectedAsset?.symbol }
    );

    const { data: priceHistory } = useQuery(
        ['priceHistory', selectedAsset?.symbol, timeframe],
        () => apiService.getPriceHistory(selectedAsset?.symbol, 30, timeframe),
        { enabled: !!selectedAsset?.symbol }
    );

    const { data: chartData } = useQuery(
        ['chartData', selectedAsset?.symbol, timeframe],
        () => apiService.getChartData(selectedAsset?.symbol, 30, timeframe),
        { enabled: !!selectedAsset?.symbol }
    );

    const { data: marketStatus } = useQuery(
        'market-status',
        () => apiService.getMarketStatus(),
        { refetchInterval: 60000 }
    );

    const { data: trendingAssets } = useQuery(
        'trending-assets',
        () => apiService.getTrendingAssets(10),
        { refetchInterval: 300000 }
    );

    const { data: news } = useQuery(
        ['news', selectedAsset?.symbol],
        () => apiService.getAssetNews(selectedAsset?.symbol, 5),
        { enabled: !!selectedAsset?.symbol }
    );

    const { data: aiPredictions } = useQuery(
        ['ai-predictions', selectedAsset?.symbol],
        () => apiService.getAIPredictions(selectedAsset?.symbol, 7),
        { enabled: !!selectedAsset?.symbol }
    );

    const { data: technicalIndicators } = useQuery(
        ['technical-indicators', selectedAsset?.symbol],
        () => apiService.getTechnicalIndicators(selectedAsset?.symbol, 30),
        { enabled: !!selectedAsset?.symbol }
    );

    const { data: technicalSummary } = useQuery(
        ['technical-summary', selectedAsset?.symbol],
        () => apiService.getTechnicalSummary(selectedAsset?.symbol, 30),
        { enabled: !!selectedAsset?.symbol }
    );

    const { data: marketNews } = useQuery(
        'market-news',
        () => apiService.getMarketNews(5),
        { refetchInterval: 300000 } // Refresh every 5 minutes
    );

    const timeframes = [
        { value: '1d', label: '1 Day' },
        { value: '1w', label: '1 Week' },
        { value: '1m', label: '1 Month' },
        { value: '3m', label: '3 Months' },
        { value: '1y', label: '1 Year' }
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Market Data</h1>
                <p className="mt-2 text-gray-600">Real-time market data and analysis</p>
            </div>

            {/* Market Status */}
            <div className="card">
                <div className="flex items-center justify-between">
                    <div className="flex items-center">
                        <Globe className="h-6 w-6 text-blue-600 mr-2" />
                        <h3 className="text-lg font-medium text-gray-900">Market Status</h3>
                    </div>
                    <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full mr-2 ${marketStatus?.is_open ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <span className="text-sm font-medium text-gray-600">
                            {marketStatus?.is_open ? 'Market Open' : 'Market Closed'}
                        </span>
                    </div>
                </div>
                {marketStatus && (
                    <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div>
                            <p className="text-sm text-gray-600">Next Open</p>
                            <p className="font-medium">{marketStatus.next_open || 'N/A'}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Next Close</p>
                            <p className="font-medium">{marketStatus.next_close || 'N/A'}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Last Updated</p>
                            <p className="font-medium">
                                {new Date(marketStatus.timestamp).toLocaleTimeString()}
                            </p>
                        </div>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                {/* Asset Search */}
                <div className="lg:col-span-1">
                    <div className="card">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Search Assets</h3>

                        <div className="relative mb-4">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search by symbol or name..."
                                className="input-field pl-10"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>

                        {searchLoading && (
                            <div className="text-center py-4">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                            </div>
                        )}

                        {searchResults && searchResults.length > 0 && (
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                                {searchResults.map((asset: any) => (
                                    <div
                                        key={asset.symbol}
                                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${selectedAsset?.symbol === asset.symbol
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-gray-300'
                                            }`}
                                        onClick={() => setSelectedAsset(asset)}
                                    >
                                        <div className="flex justify-between items-center">
                                            <div>
                                                <p className="font-medium text-gray-900">{asset.symbol}</p>
                                                <p className="text-sm text-gray-500">{asset.name}</p>
                                            </div>
                                            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                                                {asset.asset_type}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Trending Assets */}
                        <div className="mt-6">
                            <h4 className="text-sm font-medium text-gray-900 mb-3">Trending</h4>
                            {trendingAssets && (
                                <div className="space-y-2">
                                    {trendingAssets.map((asset: any, index: number) => (
                                        <div
                                            key={index}
                                            className="flex justify-between items-center p-2 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
                                            onClick={() => setSelectedAsset(asset)}
                                        >
                                            <div>
                                                <p className="font-medium text-gray-900">{asset.symbol}</p>
                                                <p className="text-xs text-gray-500">{asset.name}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-medium text-gray-900">
                                                    {asset.current_price && typeof asset.current_price === 'number'
                                                        ? `$${asset.current_price.toFixed(2)}`
                                                        : 'N/A'}
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Market News */}
                    {marketNews?.news && (
                        <div className="card mt-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Market News</h3>
                            <div className="space-y-3">
                                {marketNews.news.map((article: any, index: number) => (
                                    <div key={index} className="border-b border-gray-100 pb-3 last:border-b-0">
                                        <h4 className="font-medium text-gray-900 mb-1 text-sm">{article.title}</h4>
                                        <p className="text-xs text-gray-600 mb-2 line-clamp-2">{article.summary}</p>
                                        <div className="flex justify-between items-center text-xs text-gray-500">
                                            <span>{article.source}</span>
                                            <span>{new Date(article.published_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Chart and Data */}
                <div className="lg:col-span-2">
                    {selectedAsset ? (
                        <div className="space-y-6">
                            {/* Asset Info */}
                            <div className="card">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-2xl font-bold text-gray-900">{selectedAsset.symbol}</h3>
                                        <p className="text-gray-600">{selectedAsset.name}</p>
                                        <p className="text-sm text-gray-500">{selectedAsset.exchange}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-3xl font-bold text-gray-900">
                                            {currentPrice?.price && typeof currentPrice.price === 'number'
                                                ? `$${currentPrice.price.toFixed(2)}`
                                                : 'N/A'}
                                        </p>
                                        {chartData && (
                                            <div className="flex items-center mt-2">
                                                {chartData.change >= 0 ? (
                                                    <TrendingUp className="h-5 w-5 text-green-600 mr-1" />
                                                ) : (
                                                    <TrendingDown className="h-5 w-5 text-red-600 mr-1" />
                                                )}
                                                <span className={`font-medium ${chartData.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    {chartData.change >= 0 ? '+' : ''}${typeof chartData.change === 'number' ? chartData.change.toFixed(2) : '0.00'}
                                                    ({chartData.change_percent >= 0 ? '+' : ''}{typeof chartData.change_percent === 'number' ? chartData.change_percent.toFixed(2) : '0.00'}%)
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Chart */}
                            <div className="card">
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-lg font-medium text-gray-900">Price Chart</h3>
                                    <div className="flex space-x-2">
                                        {timeframes.map((tf) => (
                                            <button
                                                key={tf.value}
                                                onClick={() => setTimeframe(tf.value)}
                                                className={`px-3 py-1 text-sm rounded-md transition-colors ${timeframe === tf.value
                                                    ? 'bg-blue-600 text-white'
                                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                                    }`}
                                            >
                                                {tf.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {chartData && chartData.data && chartData.data.length > 0 ? (
                                    <ResponsiveContainer width="100%" height={400}>
                                        <LineChart data={chartData.data}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis
                                                dataKey="timestamp"
                                                tickFormatter={(value) => new Date(value).toLocaleDateString()}
                                            />
                                            <YAxis
                                                domain={['dataMin - 5', 'dataMax + 5']}
                                                tickFormatter={(value) => `$${value.toFixed(2)}`}
                                            />
                                            <Tooltip
                                                formatter={(value: any) => [`$${value.toFixed(2)}`, 'Price']}
                                                labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="close"
                                                stroke="#3B82F6"
                                                strokeWidth={2}
                                                dot={false}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
                                        <div className="text-center text-gray-500">
                                            <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                                            <p>Chart data not available</p>
                                            <p className="text-sm">Historical data will be available soon</p>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* AI Predictions */}
                            {aiPredictions?.predictions && (
                                <div className="card">
                                    <div className="flex items-center mb-4">
                                        <Brain className="h-5 w-5 text-purple-600 mr-2" />
                                        <h3 className="text-lg font-medium text-gray-900">AI Predictions (7 Days)</h3>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {Object.entries(aiPredictions.predictions).map(([modelName, prediction]: [string, any]) => {
                                            if (prediction.error || !prediction.predicted_price) return null;

                                            const priceChange = prediction.predicted_price - aiPredictions.current_price;
                                            const percentChange = (priceChange / aiPredictions.current_price) * 100;

                                            return (
                                                <div key={modelName} className="bg-gray-50 rounded-lg p-4">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <h4 className="font-medium text-gray-900 text-sm">{prediction.model_name}</h4>
                                                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${prediction.confidence >= 0.7 ? 'bg-green-100 text-green-800' :
                                                            prediction.confidence >= 0.5 ? 'bg-yellow-100 text-yellow-800' :
                                                                'bg-red-100 text-red-800'
                                                            }`}>
                                                            {(prediction.confidence * 100).toFixed(0)}%
                                                        </span>
                                                    </div>
                                                    <div className="text-lg font-bold text-gray-900">
                                                        ${typeof prediction.predicted_price === 'number' ? prediction.predicted_price.toFixed(2) : 'N/A'}
                                                    </div>
                                                    <div className={`text-sm flex items-center ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'
                                                        }`}>
                                                        {priceChange >= 0 ? (
                                                            <TrendingUp className="h-4 w-4 mr-1" />
                                                        ) : (
                                                            <TrendingDown className="h-4 w-4 mr-1" />
                                                        )}
                                                        {priceChange >= 0 ? '+' : ''}${typeof priceChange === 'number' ? priceChange.toFixed(2) : '0.00'} ({percentChange >= 0 ? '+' : ''}{typeof percentChange === 'number' ? percentChange.toFixed(1) : '0.0'}%)
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Technical Analysis Summary */}
                            {technicalSummary?.summary && (
                                <div className="card">
                                    <div className="flex items-center mb-4">
                                        <BarChart3 className="h-6 w-6 text-blue-600 mr-2" />
                                        <h3 className="text-xl font-semibold text-gray-900">Technical Analysis Summary</h3>
                                    </div>
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium text-gray-700">Overall Sentiment:</span>
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${technicalSummary.summary.overall_sentiment === 'Bullish' ? 'bg-green-100 text-green-800' :
                                                technicalSummary.summary.overall_sentiment === 'Bearish' ? 'bg-red-100 text-red-800' :
                                                    'bg-gray-100 text-gray-800'
                                                }`}>
                                                {technicalSummary.summary.overall_sentiment}
                                            </span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium text-gray-700">Risk Level:</span>
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${technicalSummary.summary.risk_level === 'High' ? 'bg-red-100 text-red-800' :
                                                technicalSummary.summary.risk_level === 'Low' ? 'bg-green-100 text-green-800' :
                                                    'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                {technicalSummary.summary.risk_level}
                                            </span>
                                        </div>
                                        {technicalSummary.summary.key_insights.length > 0 && (
                                            <div>
                                                <h4 className="text-sm font-medium text-gray-700 mb-2">Key Insights:</h4>
                                                <ul className="space-y-1">
                                                    {technicalSummary.summary.key_insights.map((insight: string, index: number) => (
                                                        <li key={index} className="text-sm text-gray-600 flex items-start">
                                                            <span className="text-blue-500 mr-2">•</span>
                                                            {insight}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        {technicalSummary.summary.recommendations.length > 0 && (
                                            <div>
                                                <h4 className="text-sm font-medium text-gray-700 mb-2">Recommendations:</h4>
                                                <ul className="space-y-1">
                                                    {technicalSummary.summary.recommendations.map((rec: string, index: number) => (
                                                        <li key={index} className="text-sm text-gray-600 flex items-start">
                                                            <span className="text-green-500 mr-2">•</span>
                                                            {rec}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Enhanced Market Metrics */}
                            <div className="card">
                                <div className="flex items-center mb-4">
                                    <BarChart3 className="h-5 w-5 text-blue-600 mr-2" />
                                    <h3 className="text-lg font-medium text-gray-900">Market Metrics</h3>
                                </div>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                                        <div className="text-2xl font-bold text-gray-900">
                                            {currentPrice?.price && typeof currentPrice.price === 'number' ? `$${currentPrice.price.toFixed(2)}` : 'N/A'}
                                        </div>
                                        <div className="text-sm text-gray-600 flex items-center justify-center">
                                            <DollarSign className="h-4 w-4 mr-1" />
                                            Current Price
                                        </div>
                                    </div>
                                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                                        <div className="text-2xl font-bold text-gray-900">
                                            {chartData?.volume && typeof chartData.volume === 'number' ? (chartData.volume / 1000000).toFixed(1) + 'M' : 'N/A'}
                                        </div>
                                        <div className="text-sm text-gray-600 flex items-center justify-center">
                                            <Volume2 className="h-4 w-4 mr-1" />
                                            Volume
                                        </div>
                                    </div>
                                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                                        <div className="text-2xl font-bold text-gray-900">
                                            {chartData?.high && typeof chartData.high === 'number' ? `$${chartData.high.toFixed(2)}` : 'N/A'}
                                        </div>
                                        <div className="text-sm text-gray-600">52W High</div>
                                    </div>
                                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                                        <div className="text-2xl font-bold text-gray-900">
                                            {chartData?.low && typeof chartData.low === 'number' ? `$${chartData.low.toFixed(2)}` : 'N/A'}
                                        </div>
                                        <div className="text-sm text-gray-600">52W Low</div>
                                    </div>
                                </div>
                            </div>

                            {/* Additional Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Price Performance */}
                                <div className="card">
                                    <div className="flex items-center mb-4">
                                        <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                                        <h3 className="text-lg font-medium text-gray-900">Price Performance</h3>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Today's Change</span>
                                            <span className={`font-medium ${chartData?.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                {chartData?.change >= 0 ? '+' : ''}${chartData?.change?.toFixed(2) || '0.00'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Today's % Change</span>
                                            <span className={`font-medium ${chartData?.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                {chartData?.change_percent >= 0 ? '+' : ''}{chartData?.change_percent?.toFixed(2) || '0.00'}%
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Open Price</span>
                                            <span className="font-medium text-gray-900">
                                                ${chartData?.open?.toFixed(2) || currentPrice?.price?.toFixed(2) || 'N/A'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Previous Close</span>
                                            <span className="font-medium text-gray-900">
                                                ${((currentPrice?.price || 0) - (chartData?.change || 0)).toFixed(2)}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Market Data */}
                                <div className="card">
                                    <div className="flex items-center mb-4">
                                        <Activity className="h-5 w-5 text-blue-600 mr-2" />
                                        <h3 className="text-lg font-medium text-gray-900">Market Data</h3>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Market Cap</span>
                                            <span className="font-medium text-gray-900">
                                                {chartData?.market_cap && typeof chartData.market_cap === 'number' ? (chartData.market_cap / 1000000000).toFixed(1) + 'B' : 'N/A'}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Exchange</span>
                                            <span className="font-medium text-gray-900">{selectedAsset.exchange || 'N/A'}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Currency</span>
                                            <span className="font-medium text-gray-900">{selectedAsset.currency?.toUpperCase() || 'USD'}</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Asset Type</span>
                                            <span className="font-medium text-gray-900">{selectedAsset.asset_type || 'Stock'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Volume Chart */}
                            {chartData && chartData.data && chartData.data.length > 0 && (
                                <div className="card">
                                    <div className="flex items-center mb-4">
                                        <Volume2 className="h-5 w-5 text-purple-600 mr-2" />
                                        <h3 className="text-lg font-medium text-gray-900">Volume Analysis</h3>
                                    </div>
                                    <ResponsiveContainer width="100%" height={200}>
                                        <BarChart data={chartData.data}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis
                                                dataKey="timestamp"
                                                tickFormatter={(value) => new Date(value).toLocaleDateString()}
                                            />
                                            <YAxis
                                                tickFormatter={(value) => (value / 1000000).toFixed(0) + 'M'}
                                            />
                                            <Tooltip
                                                formatter={(value: any) => [(value / 1000000).toFixed(1) + 'M', 'Volume']}
                                                labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                                            />
                                            <Bar dataKey="volume" fill="#8B5CF6" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            )}

                            {/* News */}
                            {news && news.length > 0 && (
                                <div className="card">
                                    <h3 className="text-lg font-medium text-gray-900 mb-4">Latest News</h3>
                                    <div className="space-y-3">
                                        {news.map((article: any, index: number) => (
                                            <div key={index} className="border-b border-gray-100 pb-3 last:border-b-0">
                                                <h4 className="font-medium text-gray-900 mb-1">{article.title}</h4>
                                                <p className="text-sm text-gray-600 mb-2">{article.summary}</p>
                                                <div className="flex justify-between items-center text-xs text-gray-500">
                                                    <span>{article.source}</span>
                                                    <span>{new Date(article.published_at).toLocaleDateString()}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="card h-96 flex items-center justify-center">
                            <div className="text-center text-gray-500">
                                <Search className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                                <p>Select an asset to view detailed market data</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

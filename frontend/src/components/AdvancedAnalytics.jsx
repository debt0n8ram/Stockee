import React, { useState, useEffect } from 'react';
import useAdvancedAnalytics from '../hooks/useAdvancedAnalytics';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const AdvancedAnalytics = ({ className = '' }) => {
    const {
        portfolioMetrics,
        portfolioOptimization,
        sectorAllocation,
        riskMetrics,
        performanceComparison,
        isLoading,
        error,
        getPortfolioMetrics,
        optimizePortfolio,
        getSectorAllocation,
        getRiskMetrics,
        getPerformanceComparison
    } = useAdvancedAnalytics();

    const [activeTab, setActiveTab] = useState('metrics');
    const [optimizationParams, setOptimizationParams] = useState({
        targetReturn: null,
        riskTolerance: 0.5
    });

    const handleOptimizePortfolio = async () => {
        try {
            await optimizePortfolio(optimizationParams.targetReturn, optimizationParams.riskTolerance);
        } catch (err) {
            console.error('Failed to optimize portfolio:', err);
        }
    };

    const renderPortfolioMetrics = () => (
        <div className="space-y-6">
            {portfolioMetrics && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Value</h4>
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Total Value:</span>
                                <span className="font-semibold">{formatCurrency(portfolioMetrics.total_value)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Total Cost:</span>
                                <span className="font-semibold">{formatCurrency(portfolioMetrics.total_cost)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Total Return:</span>
                                <span className={`font-semibold ${portfolioMetrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {formatPercentage(portfolioMetrics.total_return)}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Performance</h4>
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Annualized Return:</span>
                                <span className={`font-semibold ${portfolioMetrics.annualized_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                    {formatPercentage(portfolioMetrics.annualized_return)}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Volatility:</span>
                                <span className="font-semibold">{formatPercentage(portfolioMetrics.volatility)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Sharpe Ratio:</span>
                                <span className="font-semibold">{portfolioMetrics.sharpe_ratio.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Risk Metrics</h4>
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Max Drawdown:</span>
                                <span className="font-semibold text-red-600">{formatPercentage(portfolioMetrics.max_drawdown)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">VaR (95%):</span>
                                <span className="font-semibold">{formatPercentage(portfolioMetrics.var_95)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Beta:</span>
                                <span className="font-semibold">{portfolioMetrics.beta.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderPortfolioOptimization = () => (
        <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Optimization</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Target Return (optional)
                        </label>
                        <input
                            type="number"
                            step="0.01"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={optimizationParams.targetReturn || ''}
                            onChange={(e) => setOptimizationParams(prev => ({
                                ...prev,
                                targetReturn: e.target.value ? parseFloat(e.target.value) : null
                            }))}
                            placeholder="e.g., 0.10 for 10%"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Risk Tolerance
                        </label>
                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            className="w-full"
                            value={optimizationParams.riskTolerance}
                            onChange={(e) => setOptimizationParams(prev => ({
                                ...prev,
                                riskTolerance: parseFloat(e.target.value)
                            }))}
                        />
                        <div className="text-sm text-gray-600 mt-1">
                            {optimizationParams.riskTolerance.toFixed(1)} (0 = Conservative, 1 = Aggressive)
                        </div>
                    </div>
                </div>
                <button
                    onClick={handleOptimizePortfolio}
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                    {isLoading ? 'Optimizing...' : 'Optimize Portfolio'}
                </button>
            </div>

            {portfolioOptimization && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Optimization Results</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Optimal Portfolio</h5>
                            <div className="space-y-2">
                                {Object.entries(portfolioOptimization.optimal_weights).map(([symbol, weight]) => (
                                    <div key={symbol} className="flex justify-between">
                                        <span className="text-gray-600">{symbol}:</span>
                                        <span className="font-semibold">{formatPercentage(weight)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Expected Performance</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Expected Return:</span>
                                    <span className="font-semibold">{formatPercentage(portfolioOptimization.optimal_return)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Expected Volatility:</span>
                                    <span className="font-semibold">{formatPercentage(portfolioOptimization.optimal_volatility)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Sharpe Ratio:</span>
                                    <span className="font-semibold">{portfolioOptimization.optimal_sharpe.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderSectorAllocation = () => (
        <div className="space-y-6">
            {sectorAllocation && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Sector Allocation</h4>
                    <div className="space-y-4">
                        {Object.entries(sectorAllocation.sector_allocation).map(([sector, allocation]) => (
                            <div key={sector} className="flex items-center justify-between">
                                <span className="text-gray-600">{sector}</span>
                                <div className="flex items-center space-x-4">
                                    <div className="w-32 bg-gray-200 rounded-full h-2">
                                        <div
                                            className="bg-blue-600 h-2 rounded-full"
                                            style={{ width: `${allocation * 100}%` }}
                                        ></div>
                                    </div>
                                    <span className="font-semibold w-16 text-right">
                                        {formatPercentage(allocation)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );

    const renderRiskMetrics = () => (
        <div className="space-y-6">
            {riskMetrics && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Risk Measures</h4>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Volatility:</span>
                                <span className="font-semibold">{formatPercentage(riskMetrics.volatility)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Max Drawdown:</span>
                                <span className="font-semibold text-red-600">{formatPercentage(riskMetrics.max_drawdown)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">VaR (95%):</span>
                                <span className="font-semibold">{formatPercentage(riskMetrics.var_95)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">VaR (99%):</span>
                                <span className="font-semibold">{formatPercentage(riskMetrics.var_99)}</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow-sm border">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Risk-Adjusted Returns</h4>
                        <div className="space-y-3">
                            <div className="flex justify-between">
                                <span className="text-gray-600">Sharpe Ratio:</span>
                                <span className="font-semibold">{riskMetrics.sharpe_ratio.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Sortino Ratio:</span>
                                <span className="font-semibold">{riskMetrics.sortino_ratio.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Calmar Ratio:</span>
                                <span className="font-semibold">{riskMetrics.calmar_ratio.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">Beta:</span>
                                <span className="font-semibold">{riskMetrics.beta.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderPerformanceComparison = () => (
        <div className="space-y-6">
            {performanceComparison && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Performance Comparison</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Portfolio</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Return:</span>
                                    <span className="font-semibold">{formatPercentage(performanceComparison.portfolio.return)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Volatility:</span>
                                    <span className="font-semibold">{formatPercentage(performanceComparison.portfolio.volatility)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Sharpe:</span>
                                    <span className="font-semibold">{performanceComparison.portfolio.sharpe_ratio.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Benchmark</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Return:</span>
                                    <span className="font-semibold">{formatPercentage(performanceComparison.benchmark.return)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Volatility:</span>
                                    <span className="font-semibold">{formatPercentage(performanceComparison.benchmark.volatility)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Sharpe:</span>
                                    <span className="font-semibold">{performanceComparison.benchmark.sharpe_ratio.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Comparison</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Excess Return:</span>
                                    <span className={`font-semibold ${performanceComparison.comparison.excess_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatPercentage(performanceComparison.comparison.excess_return)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Alpha:</span>
                                    <span className={`font-semibold ${performanceComparison.comparison.alpha >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatPercentage(performanceComparison.comparison.alpha)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Information Ratio:</span>
                                    <span className="font-semibold">{performanceComparison.comparison.information_ratio.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    if (error) {
        return (
            <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
                <div className="flex">
                    <div className="text-red-600">
                        <strong>Error:</strong> {error}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`space-y-6 ${className}`}>
            <div className="bg-white rounded-lg shadow-sm border">
                <div className="border-b border-gray-200">
                    <nav className="flex space-x-8 px-6">
                        {[
                            { id: 'metrics', label: 'Portfolio Metrics' },
                            { id: 'optimization', label: 'Optimization' },
                            { id: 'sectors', label: 'Sector Allocation' },
                            { id: 'risk', label: 'Risk Metrics' },
                            { id: 'comparison', label: 'Performance Comparison' }
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                                        ? 'border-blue-500 text-blue-600'
                                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    }`}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                <div className="p-6">
                    {activeTab === 'metrics' && renderPortfolioMetrics()}
                    {activeTab === 'optimization' && renderPortfolioOptimization()}
                    {activeTab === 'sectors' && renderSectorAllocation()}
                    {activeTab === 'risk' && renderRiskMetrics()}
                    {activeTab === 'comparison' && renderPerformanceComparison()}
                </div>
            </div>
        </div>
    );
};

export default AdvancedAnalytics;

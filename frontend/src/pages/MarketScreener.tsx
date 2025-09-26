import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { MarketOverview, TopGainers, TopLosers, MostActive, SectorPerformance, ScreenedStocks } from '../types/api';
import {
    Search,
    TrendingUp,
    TrendingDown,
    Activity,
    BarChart3,
    Filter,
    Star,
    AlertTriangle,
    DollarSign,
    Volume2
} from 'lucide-react';

const MarketScreener: React.FC = () => {
    const [filters, setFilters] = useState({
        min_price: '',
        max_price: '',
        min_volume: '',
        exchange: '',
        sector: '',
        limit: 50
    });

    const [activeTab, setActiveTab] = useState('screener');

    // Market overview
    const { data: marketOverview } = useQuery<MarketOverview>({
        queryKey: ['market-overview'],
        queryFn: () => apiService.getMarketOverview(),
        refetchInterval: 300000
    });

    // Top gainers
    const { data: topGainers } = useQuery<TopGainers>({
        queryKey: ['top-gainers'],
        queryFn: () => apiService.getTopGainers(20),
        refetchInterval: 300000
    });

    // Top losers
    const { data: topLosers } = useQuery<TopLosers>({
        queryKey: ['top-losers'],
        queryFn: () => apiService.getTopLosers(20),
        refetchInterval: 300000
    });

    // Most active
    const { data: mostActive } = useQuery<MostActive>({
        queryKey: ['most-active'],
        queryFn: () => apiService.getMostActive(20),
        refetchInterval: 300000
    });

    // Sector performance
    const { data: sectorPerformance } = useQuery<SectorPerformance>({
        queryKey: ['sector-performance'],
        queryFn: () => apiService.getSectorPerformance(),
        refetchInterval: 60000
    });

    // Screened stocks
    const { data: screenedStocks, refetch: refetchScreened } = useQuery<ScreenedStocks>({
        queryKey: ['screened-stocks', filters],
        queryFn: () => apiService.screenStocks(filters),
        enabled: false
    });

    const handleFilterChange = (key: string, value: string) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleSearch = () => {
        refetchScreened();
    };

    const resetFilters = () => {
        setFilters({
            min_price: '',
            max_price: '',
            min_volume: '',
            exchange: '',
            sector: '',
            limit: 50
        });
    };

    const formatNumber = (num: number) => {
        if (num >= 1000000000) {
            return (num / 1000000000).toFixed(1) + 'B';
        } else if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    };

    const getChangeColor = (change: number) => {
        if (change > 0) return 'text-green-600';
        if (change < 0) return 'text-red-600';
        return 'text-gray-600';
    };

    const getChangeBg = (change: number) => {
        if (change > 0) return 'bg-green-100';
        if (change < 0) return 'bg-red-100';
        return 'bg-gray-100';
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Screener</h1>
                    <p className="text-gray-600">Discover stocks based on your criteria and market performance</p>
                </div>

                {/* Market Overview */}
                {marketOverview?.market_overview && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div className="card">
                            <div className="flex items-center">
                                <BarChart3 className="h-8 w-8 text-blue-600 mr-3" />
                                <div>
                                    <p className="text-sm text-gray-600">Total Stocks</p>
                                    <p className="text-2xl font-bold text-gray-900">
                                        {marketOverview.market_overview.total_stocks?.toLocaleString() || 'N/A'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <div className="flex items-center">
                                <Volume2 className="h-8 w-8 text-green-600 mr-3" />
                                <div>
                                    <p className="text-sm text-gray-600">Total Volume</p>
                                    <p className="text-2xl font-bold text-gray-900">
                                        {formatNumber(marketOverview.market_overview.total_volume || 0)}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <div className="flex items-center">
                                <TrendingUp className="h-8 w-8 text-green-600 mr-3" />
                                <div>
                                    <p className="text-sm text-gray-600">Advancing</p>
                                    <p className="text-2xl font-bold text-gray-900">
                                        {marketOverview.market_overview.advancing_stocks || 0}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <div className="flex items-center">
                                <TrendingDown className="h-8 w-8 text-red-600 mr-3" />
                                <div>
                                    <p className="text-sm text-gray-600">Declining</p>
                                    <p className="text-2xl font-bold text-gray-900">
                                        {marketOverview.market_overview.declining_stocks || 0}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Tabs */}
                <div className="mb-6">
                    <div className="border-b border-gray-200">
                        <nav className="-mb-px flex space-x-8">
                            {[
                                { id: 'screener', name: 'Stock Screener', icon: Search },
                                { id: 'gainers', name: 'Top Gainers', icon: TrendingUp },
                                { id: 'losers', name: 'Top Losers', icon: TrendingDown },
                                { id: 'active', name: 'Most Active', icon: Activity },
                                { id: 'sectors', name: 'Sector Performance', icon: BarChart3 }
                            ].map((tab) => {
                                const Icon = tab.icon;
                                return (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                                            ? 'border-blue-500 text-blue-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                            }`}
                                    >
                                        <Icon className="h-5 w-5 mr-2" />
                                        {tab.name}
                                    </button>
                                );
                            })}
                        </nav>
                    </div>
                </div>

                {/* Stock Screener */}
                {activeTab === 'screener' && (
                    <div className="space-y-6">
                        {/* Filters */}
                        <div className="card">
                            <div className="flex items-center mb-4">
                                <Filter className="h-6 w-6 text-blue-600 mr-2" />
                                <h3 className="text-lg font-medium text-gray-900">Screening Filters</h3>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Min Price ($)
                                    </label>
                                    <input
                                        type="number"
                                        className="input-field"
                                        value={filters.min_price}
                                        onChange={(e) => handleFilterChange('min_price', e.target.value)}
                                        placeholder="0.00"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Max Price ($)
                                    </label>
                                    <input
                                        type="number"
                                        className="input-field"
                                        value={filters.max_price}
                                        onChange={(e) => handleFilterChange('max_price', e.target.value)}
                                        placeholder="1000.00"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Min Volume
                                    </label>
                                    <input
                                        type="number"
                                        className="input-field"
                                        value={filters.min_volume}
                                        onChange={(e) => handleFilterChange('min_volume', e.target.value)}
                                        placeholder="1000000"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Exchange
                                    </label>
                                    <select
                                        className="input-field"
                                        value={filters.exchange}
                                        onChange={(e) => handleFilterChange('exchange', e.target.value)}
                                    >
                                        <option value="">All Exchanges</option>
                                        <option value="NASDAQ">NASDAQ</option>
                                        <option value="NYSE">NYSE</option>
                                        <option value="AMEX">AMEX</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Sector
                                    </label>
                                    <input
                                        type="text"
                                        className="input-field"
                                        value={filters.sector}
                                        onChange={(e) => handleFilterChange('sector', e.target.value)}
                                        placeholder="Technology"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Limit
                                    </label>
                                    <input
                                        type="number"
                                        className="input-field"
                                        value={filters.limit}
                                        onChange={(e) => handleFilterChange('limit', e.target.value)}
                                        placeholder="50"
                                    />
                                </div>
                            </div>

                            <div className="flex justify-end space-x-3 mt-4">
                                <button
                                    onClick={resetFilters}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                                >
                                    Reset
                                </button>
                                <button
                                    onClick={handleSearch}
                                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                                >
                                    Search
                                </button>
                            </div>
                        </div>

                        {/* Results */}
                        {screenedStocks?.results && (
                            <div className="card">
                                <h3 className="text-lg font-medium text-gray-900 mb-4">
                                    Search Results ({screenedStocks.count})
                                </h3>

                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Symbol
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Name
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Price
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Change
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Volume
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Exchange
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {screenedStocks.results.map((stock: any, index: number) => (
                                                <tr key={index} className="hover:bg-gray-50">
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                        {stock.symbol}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {stock.name}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                        ${stock.current_price?.toFixed(2) || 'N/A'}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getChangeBg(stock.change_percent)} ${getChangeColor(stock.change_percent)}`}>
                                                            {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2) || '0.00'}%
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {formatNumber(stock.volume || 0)}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {stock.exchange || 'N/A'}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Top Gainers */}
                {activeTab === 'gainers' && topGainers?.gainers && (
                    <div className="card">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Gainers</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {topGainers.gainers.map((stock: any, index: number) => (
                                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <h4 className="font-medium text-gray-900">{stock.symbol}</h4>
                                            <p className="text-sm text-gray-500">{stock.name}</p>
                                        </div>
                                        <span className="text-green-600 font-medium">
                                            +{stock.change_percent?.toFixed(2)}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-lg font-bold text-gray-900">
                                            ${stock.current_price?.toFixed(2)}
                                        </span>
                                        <span className="text-sm text-gray-500">
                                            Vol: {formatNumber(stock.volume)}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Top Losers */}
                {activeTab === 'losers' && topLosers?.losers && (
                    <div className="card">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Top Losers</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {topLosers.losers.map((stock: any, index: number) => (
                                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <h4 className="font-medium text-gray-900">{stock.symbol}</h4>
                                            <p className="text-sm text-gray-500">{stock.name}</p>
                                        </div>
                                        <span className="text-red-600 font-medium">
                                            {stock.change_percent?.toFixed(2)}%
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-lg font-bold text-gray-900">
                                            ${stock.current_price?.toFixed(2)}
                                        </span>
                                        <span className="text-sm text-gray-500">
                                            Vol: {formatNumber(stock.volume)}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Most Active */}
                {activeTab === 'active' && mostActive?.most_active && (
                    <div className="card">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Most Active</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {mostActive.most_active.map((stock: any, index: number) => (
                                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <h4 className="font-medium text-gray-900">{stock.symbol}</h4>
                                            <p className="text-sm text-gray-500">{stock.name}</p>
                                        </div>
                                        <Activity className="h-5 w-5 text-blue-600" />
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-lg font-bold text-gray-900">
                                            ${stock.current_price?.toFixed(2)}
                                        </span>
                                        <span className="text-sm text-gray-500">
                                            Vol: {formatNumber(stock.volume)}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Sector Performance */}
                {activeTab === 'sectors' && sectorPerformance && 'sector_performance' in sectorPerformance && Array.isArray(sectorPerformance.sector_performance) && (
                    <div className="card">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Sector Performance</h3>
                        <div className="space-y-4">
                            {sectorPerformance.sector_performance.map((sector: any, index: number) => (
                                <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                                    <div>
                                        <h4 className="font-medium text-gray-900">{sector.sector}</h4>
                                        <p className="text-sm text-gray-500">{sector.stocks} stocks</p>
                                    </div>
                                    <div className="text-right">
                                        <span className={`text-lg font-bold ${getChangeColor(sector.avg_change)}`}>
                                            {sector.avg_change >= 0 ? '+' : ''}{sector.avg_change?.toFixed(2)}%
                                        </span>
                                        <p className="text-sm text-gray-500">Avg Change</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MarketScreener;

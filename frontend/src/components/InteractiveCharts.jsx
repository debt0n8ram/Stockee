import React, { useState, useEffect } from 'react';
import useInteractiveCharts from '../hooks/useInteractiveCharts';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const InteractiveCharts = ({ className = '' }) => {
    const {
        chartData,
        orderPlacementData,
        chartPatterns,
        volumeProfile,
        marketDepth,
        chartStatistics,
        supportResistance,
        availableIndicators,
        availableTimeframes,
        availableChartTypes,
        isLoading,
        error,
        getChartData,
        getOrderPlacementData,
        placeOrderFromChart,
        getChartPatterns,
        getVolumeProfile,
        getMarketDepth,
        getChartStatistics,
        getSupportResistance
    } = useInteractiveCharts();

    const [activeTab, setActiveTab] = useState('chart');
    const [chartParams, setChartParams] = useState({
        symbol: 'AAPL',
        timeframe: '1d',
        startDate: null,
        endDate: null,
        indicators: []
    });
    const [orderForm, setOrderForm] = useState({
        symbol: 'AAPL',
        side: 'buy',
        quantity: 1,
        orderType: 'market',
        price: null,
        stopPrice: null
    });

    const handleGetChartData = async () => {
        try {
            await getChartData(
                chartParams.symbol,
                chartParams.timeframe,
                chartParams.startDate,
                chartParams.endDate,
                chartParams.indicators
            );
        } catch (err) {
            console.error('Failed to get chart data:', err);
        }
    };

    const handleGetOrderPlacementData = async () => {
        try {
            await getOrderPlacementData(orderForm.symbol);
        } catch (err) {
            console.error('Failed to get order placement data:', err);
        }
    };

    const handlePlaceOrder = async () => {
        try {
            await placeOrderFromChart(orderForm);
            alert('Order placed successfully!');
        } catch (err) {
            console.error('Failed to place order:', err);
        }
    };

    const handleGetChartPatterns = async () => {
        try {
            await getChartPatterns(chartParams.symbol, chartParams.startDate, chartParams.endDate);
        } catch (err) {
            console.error('Failed to get chart patterns:', err);
        }
    };

    const handleGetVolumeProfile = async () => {
        try {
            await getVolumeProfile(chartParams.symbol, chartParams.startDate, chartParams.endDate);
        } catch (err) {
            console.error('Failed to get volume profile:', err);
        }
    };

    const handleGetMarketDepth = async () => {
        try {
            await getMarketDepth(chartParams.symbol);
        } catch (err) {
            console.error('Failed to get market depth:', err);
        }
    };

    const handleGetChartStatistics = async () => {
        try {
            await getChartStatistics(chartParams.symbol, chartParams.startDate, chartParams.endDate);
        } catch (err) {
            console.error('Failed to get chart statistics:', err);
        }
    };

    const handleGetSupportResistance = async () => {
        try {
            await getSupportResistance(chartParams.symbol, chartParams.startDate, chartParams.endDate);
        } catch (err) {
            console.error('Failed to get support/resistance levels:', err);
        }
    };

    const renderChartControls = () => (
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Chart Controls</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Symbol
                    </label>
                    <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={chartParams.symbol}
                        onChange={(e) => setChartParams(prev => ({ ...prev, symbol: e.target.value }))}
                        placeholder="e.g., AAPL"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Timeframe
                    </label>
                    <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={chartParams.timeframe}
                        onChange={(e) => setChartParams(prev => ({ ...prev, timeframe: e.target.value }))}
                    >
                        {availableTimeframes.map(timeframe => (
                            <option key={timeframe.value} value={timeframe.value}>
                                {timeframe.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Start Date
                    </label>
                    <input
                        type="date"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={chartParams.startDate || ''}
                        onChange={(e) => setChartParams(prev => ({ ...prev, startDate: e.target.value }))}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        End Date
                    </label>
                    <input
                        type="date"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={chartParams.endDate || ''}
                        onChange={(e) => setChartParams(prev => ({ ...prev, endDate: e.target.value }))}
                    />
                </div>
            </div>

            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Technical Indicators
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {availableIndicators.map(indicator => (
                        <label key={indicator.name} className="flex items-center">
                            <input
                                type="checkbox"
                                className="mr-2"
                                checked={chartParams.indicators.includes(indicator.name)}
                                onChange={(e) => {
                                    if (e.target.checked) {
                                        setChartParams(prev => ({
                                            ...prev,
                                            indicators: [...prev.indicators, indicator.name]
                                        }));
                                    } else {
                                        setChartParams(prev => ({
                                            ...prev,
                                            indicators: prev.indicators.filter(i => i !== indicator.name)
                                        }));
                                    }
                                }}
                            />
                            <span className="text-sm">{indicator.name}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="flex space-x-4">
                <button
                    onClick={handleGetChartData}
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                    {isLoading ? 'Loading...' : 'Load Chart Data'}
                </button>

                <button
                    onClick={handleGetChartPatterns}
                    disabled={isLoading}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                    {isLoading ? 'Loading...' : 'Get Chart Patterns'}
                </button>

                <button
                    onClick={handleGetVolumeProfile}
                    disabled={isLoading}
                    className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
                >
                    {isLoading ? 'Loading...' : 'Get Volume Profile'}
                </button>

                <button
                    onClick={handleGetSupportResistance}
                    disabled={isLoading}
                    className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 disabled:opacity-50"
                >
                    {isLoading ? 'Loading...' : 'Get Support/Resistance'}
                </button>
            </div>
        </div>
    );

    const renderChartData = () => (
        <div className="space-y-6">
            {chartData && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Chart Data</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Symbol Information</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Symbol:</span>
                                    <span className="font-semibold">{chartData.symbol}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Timeframe:</span>
                                    <span className="font-semibold">{chartData.timeframe}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Data Points:</span>
                                    <span className="font-semibold">{chartData.data_points}</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Price Range</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">High:</span>
                                    <span className="font-semibold">{formatCurrency(chartData.price_range.high)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Low:</span>
                                    <span className="font-semibold">{formatCurrency(chartData.price_range.low)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Range:</span>
                                    <span className="font-semibold">{formatCurrency(chartData.price_range.range)}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-6">
                        <h5 className="font-medium text-gray-900 mb-3">Technical Indicators</h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {Object.entries(chartData.indicators).map(([name, data]) => (
                                <div key={name} className="bg-gray-50 p-3 rounded">
                                    <h6 className="font-medium text-gray-900 mb-2">{name}</h6>
                                    <div className="space-y-1 text-sm">
                                        {Object.entries(data).map(([key, value]) => (
                                            <div key={key} className="flex justify-between">
                                                <span className="text-gray-600">{key}:</span>
                                                <span className="font-semibold">
                                                    {typeof value === 'number' ? value.toFixed(2) : value}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderOrderPlacement = () => (
        <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Order Placement</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Symbol
                        </label>
                        <input
                            type="text"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={orderForm.symbol}
                            onChange={(e) => setOrderForm(prev => ({ ...prev, symbol: e.target.value }))}
                            placeholder="e.g., AAPL"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Side
                        </label>
                        <select
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={orderForm.side}
                            onChange={(e) => setOrderForm(prev => ({ ...prev, side: e.target.value }))}
                        >
                            <option value="buy">Buy</option>
                            <option value="sell">Sell</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Quantity
                        </label>
                        <input
                            type="number"
                            min="1"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={orderForm.quantity}
                            onChange={(e) => setOrderForm(prev => ({ ...prev, quantity: parseInt(e.target.value) }))}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Order Type
                        </label>
                        <select
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={orderForm.orderType}
                            onChange={(e) => setOrderForm(prev => ({ ...prev, orderType: e.target.value }))}
                        >
                            <option value="market">Market</option>
                            <option value="limit">Limit</option>
                            <option value="stop">Stop</option>
                            <option value="stop_limit">Stop Limit</option>
                        </select>
                    </div>

                    {orderForm.orderType === 'limit' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Limit Price
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={orderForm.price || ''}
                                onChange={(e) => setOrderForm(prev => ({ ...prev, price: parseFloat(e.target.value) }))}
                            />
                        </div>
                    )}

                    {(orderForm.orderType === 'stop' || orderForm.orderType === 'stop_limit') && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Stop Price
                            </label>
                            <input
                                type="number"
                                step="0.01"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                value={orderForm.stopPrice || ''}
                                onChange={(e) => setOrderForm(prev => ({ ...prev, stopPrice: parseFloat(e.target.value) }))}
                            />
                        </div>
                    )}
                </div>

                <div className="flex space-x-4">
                    <button
                        onClick={handleGetOrderPlacementData}
                        disabled={isLoading}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        {isLoading ? 'Loading...' : 'Get Order Data'}
                    </button>

                    <button
                        onClick={handlePlaceOrder}
                        disabled={isLoading || !orderForm.symbol || !orderForm.quantity}
                        className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                    >
                        {isLoading ? 'Placing...' : 'Place Order'}
                    </button>
                </div>
            </div>

            {orderPlacementData && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Order Placement Data</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Current Market Data</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Current Price:</span>
                                    <span className="font-semibold">{formatCurrency(orderPlacementData.current_price)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Bid:</span>
                                    <span className="font-semibold">{formatCurrency(orderPlacementData.bid)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Ask:</span>
                                    <span className="font-semibold">{formatCurrency(orderPlacementData.ask)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Spread:</span>
                                    <span className="font-semibold">{formatCurrency(orderPlacementData.spread)}</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Order Validation</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Valid:</span>
                                    <span className={`font-semibold ${orderPlacementData.valid ? 'text-green-600' : 'text-red-600'}`}>
                                        {orderPlacementData.valid ? 'Yes' : 'No'}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Estimated Cost:</span>
                                    <span className="font-semibold">{formatCurrency(orderPlacementData.estimated_cost)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Available Cash:</span>
                                    <span className="font-semibold">{formatCurrency(orderPlacementData.available_cash)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Can Afford:</span>
                                    <span className={`font-semibold ${orderPlacementData.can_afford ? 'text-green-600' : 'text-red-600'}`}>
                                        {orderPlacementData.can_afford ? 'Yes' : 'No'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderChartPatterns = () => (
        <div className="space-y-6">
            {chartPatterns.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Chart Patterns</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {chartPatterns.map((pattern, index) => (
                            <div key={index} className="bg-gray-50 p-4 rounded">
                                <h5 className="font-medium text-gray-900 mb-2">{pattern.pattern_type}</h5>
                                <div className="space-y-1 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Confidence:</span>
                                        <span className="font-semibold">{formatPercentage(pattern.confidence)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Start Date:</span>
                                        <span className="font-semibold">{new Date(pattern.start_date).toLocaleDateString()}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">End Date:</span>
                                        <span className="font-semibold">{new Date(pattern.end_date).toLocaleDateString()}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-600">Price Range:</span>
                                        <span className="font-semibold">{formatCurrency(pattern.price_range)}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );

    const renderVolumeProfile = () => (
        <div className="space-y-6">
            {volumeProfile && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Volume Profile</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Volume Statistics</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Total Volume:</span>
                                    <span className="font-semibold">{volumeProfile.total_volume.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Average Volume:</span>
                                    <span className="font-semibold">{volumeProfile.average_volume.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Max Volume:</span>
                                    <span className="font-semibold">{volumeProfile.max_volume.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Min Volume:</span>
                                    <span className="font-semibold">{volumeProfile.min_volume.toLocaleString()}</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Volume Distribution</h5>
                            <div className="space-y-2">
                                {Object.entries(volumeProfile.volume_distribution).map(([price, volume]) => (
                                    <div key={price} className="flex items-center justify-between">
                                        <span className="text-gray-600">{formatCurrency(price)}</span>
                                        <div className="flex items-center space-x-2">
                                            <div className="w-32 bg-gray-200 rounded-full h-2">
                                                <div
                                                    className="bg-blue-600 h-2 rounded-full"
                                                    style={{ width: `${(volume / volumeProfile.max_volume) * 100}%` }}
                                                ></div>
                                            </div>
                                            <span className="text-sm font-semibold w-16 text-right">
                                                {volume.toLocaleString()}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderMarketDepth = () => (
        <div className="space-y-6">
            {marketDepth && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Market Depth</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Bids</h5>
                            <div className="space-y-2">
                                {marketDepth.bids.map((bid, index) => (
                                    <div key={index} className="flex justify-between items-center">
                                        <span className="text-gray-600">{formatCurrency(bid.price)}</span>
                                        <span className="font-semibold">{bid.quantity.toLocaleString()}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Asks</h5>
                            <div className="space-y-2">
                                {marketDepth.asks.map((ask, index) => (
                                    <div key={index} className="flex justify-between items-center">
                                        <span className="text-gray-600">{formatCurrency(ask.price)}</span>
                                        <span className="font-semibold">{ask.quantity.toLocaleString()}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderChartStatistics = () => (
        <div className="space-y-6">
            {chartStatistics && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Chart Statistics</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Price Statistics</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mean:</span>
                                    <span className="font-semibold">{formatCurrency(chartStatistics.price_stats.mean)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Median:</span>
                                    <span className="font-semibold">{formatCurrency(chartStatistics.price_stats.median)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Std Dev:</span>
                                    <span className="font-semibold">{formatCurrency(chartStatistics.price_stats.std_dev)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Variance:</span>
                                    <span className="font-semibold">{formatCurrency(chartStatistics.price_stats.variance)}</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Volume Statistics</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Mean:</span>
                                    <span className="font-semibold">{chartStatistics.volume_stats.mean.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Median:</span>
                                    <span className="font-semibold">{chartStatistics.volume_stats.median.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Std Dev:</span>
                                    <span className="font-semibold">{chartStatistics.volume_stats.std_dev.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Variance:</span>
                                    <span className="font-semibold">{chartStatistics.volume_stats.variance.toLocaleString()}</span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Performance Metrics</h5>
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Total Return:</span>
                                    <span className={`font-semibold ${chartStatistics.performance.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatPercentage(chartStatistics.performance.total_return)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Volatility:</span>
                                    <span className="font-semibold">{formatPercentage(chartStatistics.performance.volatility)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Sharpe Ratio:</span>
                                    <span className="font-semibold">{chartStatistics.performance.sharpe_ratio.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-600">Max Drawdown:</span>
                                    <span className="font-semibold text-red-600">{formatPercentage(chartStatistics.performance.max_drawdown)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderSupportResistance = () => (
        <div className="space-y-6">
            {supportResistance && (
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Support & Resistance Levels</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Support Levels</h5>
                            <div className="space-y-2">
                                {supportResistance.support_levels.map((level, index) => (
                                    <div key={index} className="flex justify-between items-center">
                                        <span className="text-gray-600">{formatCurrency(level.price)}</span>
                                        <span className="font-semibold">{formatPercentage(level.strength)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <h5 className="font-medium text-gray-900 mb-3">Resistance Levels</h5>
                            <div className="space-y-2">
                                {supportResistance.resistance_levels.map((level, index) => (
                                    <div key={index} className="flex justify-between items-center">
                                        <span className="text-gray-600">{formatCurrency(level.price)}</span>
                                        <span className="font-semibold">{formatPercentage(level.strength)}</span>
                                    </div>
                                ))}
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
            {renderChartControls()}

            <div className="bg-white rounded-lg shadow-sm border">
                <div className="border-b border-gray-200">
                    <nav className="flex space-x-8 px-6">
                        {[
                            { id: 'chart', label: 'Chart Data' },
                            { id: 'order', label: 'Order Placement' },
                            { id: 'patterns', label: 'Chart Patterns' },
                            { id: 'volume', label: 'Volume Profile' },
                            { id: 'depth', label: 'Market Depth' },
                            { id: 'statistics', label: 'Statistics' },
                            { id: 'support', label: 'Support/Resistance' }
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
                    {activeTab === 'chart' && renderChartData()}
                    {activeTab === 'order' && renderOrderPlacement()}
                    {activeTab === 'patterns' && renderChartPatterns()}
                    {activeTab === 'volume' && renderVolumeProfile()}
                    {activeTab === 'depth' && renderMarketDepth()}
                    {activeTab === 'statistics' && renderChartStatistics()}
                    {activeTab === 'support' && renderSupportResistance()}
                </div>
            </div>
        </div>
    );
};

export default InteractiveCharts;

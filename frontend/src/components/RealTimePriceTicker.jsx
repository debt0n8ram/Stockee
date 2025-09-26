import React, { useState, useEffect } from 'react';
import useWebSocket from '../hooks/useWebSocket';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const RealTimePriceTicker = ({ symbols = [], className = '' }) => {
    const [prices, setPrices] = useState({});
    const [isConnected, setIsConnected] = useState(false);

    const {
        isConnected: wsConnected,
        subscribeToPrice,
        unsubscribeFromPrice,
        addMessageHandler,
        removeMessageHandler
    } = useWebSocket(`ws://localhost:8000/api/ws-realtime/ws/user123`);

    useEffect(() => {
        setIsConnected(wsConnected);
    }, [wsConnected]);

    useEffect(() => {
        // Add message handler for price updates
        const handlePriceUpdate = (data) => {
            if (data.type === 'price_update') {
                setPrices(prev => ({
                    ...prev,
                    [data.symbol]: {
                        price: data.price,
                        timestamp: data.timestamp
                    }
                }));
            }
        };

        addMessageHandler('price_update', handlePriceUpdate);

        return () => {
            removeMessageHandler('price_update');
        };
    }, [addMessageHandler, removeMessageHandler]);

    useEffect(() => {
        // Subscribe to price updates for all symbols
        symbols.forEach(symbol => {
            if (isConnected) {
                subscribeToPrice(symbol);
            }
        });

        // Cleanup subscriptions
        return () => {
            symbols.forEach(symbol => {
                unsubscribeFromPrice(symbol);
            });
        };
    }, [symbols, isConnected, subscribeToPrice, unsubscribeFromPrice]);

    if (!isConnected) {
        return (
            <div className={`bg-gray-100 p-4 rounded-lg ${className}`}>
                <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-gray-600">Connecting to real-time data...</span>
                </div>
            </div>
        );
    }

    return (
        <div className={`bg-white p-4 rounded-lg shadow-sm border ${className}`}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Real-Time Prices</h3>
                <div className="flex items-center">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                    <span className="text-sm text-gray-600">Live</span>
                </div>
            </div>

            <div className="space-y-3">
                {symbols.map(symbol => {
                    const priceData = prices[symbol];
                    return (
                        <div key={symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center">
                                <span className="font-semibold text-gray-900 mr-3">{symbol}</span>
                                {priceData ? (
                                    <span className="text-lg font-bold text-gray-900">
                                        {formatCurrency(priceData.price)}
                                    </span>
                                ) : (
                                    <span className="text-lg font-bold text-gray-400">Loading...</span>
                                )}
                            </div>

                            <div className="text-right">
                                {priceData ? (
                                    <div className="text-sm text-gray-600">
                                        {new Date(priceData.timestamp).toLocaleTimeString()}
                                    </div>
                                ) : (
                                    <div className="text-sm text-gray-400">Waiting for data...</div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            {symbols.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                    No symbols selected for real-time updates
                </div>
            )}
        </div>
    );
};

export default RealTimePriceTicker;

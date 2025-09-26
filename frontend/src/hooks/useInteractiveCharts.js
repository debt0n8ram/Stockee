import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

export const useInteractiveCharts = () => {
    const [chartData, setChartData] = useState(null);
    const [orderPlacementData, setOrderPlacementData] = useState(null);
    const [chartPatterns, setChartPatterns] = useState([]);
    const [volumeProfile, setVolumeProfile] = useState(null);
    const [marketDepth, setMarketDepth] = useState(null);
    const [chartStatistics, setChartStatistics] = useState(null);
    const [supportResistance, setSupportResistance] = useState(null);
    const [availableIndicators, setAvailableIndicators] = useState([]);
    const [availableTimeframes, setAvailableTimeframes] = useState([]);
    const [availableChartTypes, setAvailableChartTypes] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const getChartData = useCallback(async (symbol, timeframe = '1d', startDate = null, endDate = null, indicators = []) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = { symbol, timeframe };
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;
            if (indicators.length > 0) params.indicators = indicators.join(',');

            const response = await apiClient.get('/interactive-charts/chart-data', { params });
            setChartData(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get chart data');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getOrderPlacementData = useCallback(async (symbol) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/interactive-charts/order-placement-data', {
                params: { symbol }
            });
            setOrderPlacementData(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get order placement data');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const placeOrderFromChart = useCallback(async (orderData) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/interactive-charts/place-order', orderData);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to place order from chart');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getChartPatterns = useCallback(async (symbol, startDate = null, endDate = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = { symbol };
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await apiClient.get('/interactive-charts/chart-patterns', { params });
            setChartPatterns(response.data.patterns);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get chart patterns');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getVolumeProfile = useCallback(async (symbol, startDate = null, endDate = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = { symbol };
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await apiClient.get('/interactive-charts/volume-profile', { params });
            setVolumeProfile(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get volume profile');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getMarketDepth = useCallback(async (symbol) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/interactive-charts/market-depth', {
                params: { symbol }
            });
            setMarketDepth(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get market depth');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getChartStatistics = useCallback(async (symbol, startDate = null, endDate = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = { symbol };
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await apiClient.get('/interactive-charts/chart-statistics', { params });
            setChartStatistics(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get chart statistics');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getSupportResistance = useCallback(async (symbol, startDate = null, endDate = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = { symbol };
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await apiClient.get('/interactive-charts/support-resistance', { params });
            setSupportResistance(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get support/resistance levels');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getAvailableIndicators = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/interactive-charts/chart-indicators/available');
            setAvailableIndicators(response.data.indicators);
            return response.data.indicators;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get available indicators');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getAvailableTimeframes = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/interactive-charts/chart-timeframes/available');
            setAvailableTimeframes(response.data.timeframes);
            return response.data.timeframes;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get available timeframes');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getAvailableChartTypes = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/interactive-charts/chart-types/available');
            setAvailableChartTypes(response.data.chart_types);
            return response.data.chart_types;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get available chart types');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Load initial data
    useEffect(() => {
        getAvailableIndicators();
        getAvailableTimeframes();
        getAvailableChartTypes();
    }, [getAvailableIndicators, getAvailableTimeframes, getAvailableChartTypes]);

    return {
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
        getSupportResistance,
        getAvailableIndicators,
        getAvailableTimeframes,
        getAvailableChartTypes
    };
};

export default useInteractiveCharts;

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

export const useAdvancedAnalytics = () => {
    const [portfolioMetrics, setPortfolioMetrics] = useState(null);
    const [portfolioOptimization, setPortfolioOptimization] = useState(null);
    const [sectorAllocation, setSectorAllocation] = useState(null);
    const [attributionAnalysis, setAttributionAnalysis] = useState(null);
    const [riskMetrics, setRiskMetrics] = useState(null);
    const [performanceComparison, setPerformanceComparison] = useState(null);
    const [correlationMatrix, setCorrelationMatrix] = useState(null);
    const [efficientFrontier, setEfficientFrontier] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const getPortfolioMetrics = useCallback(async (startDate = null, endDate = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = {};
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await apiClient.get('/advanced-analytics/portfolio/metrics', { params });
            setPortfolioMetrics(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get portfolio metrics');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const optimizePortfolio = useCallback(async (targetReturn = null, riskTolerance = 0.5) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/advanced-analytics/portfolio/optimize', {
                target_return: targetReturn,
                risk_tolerance: riskTolerance
            });
            setPortfolioOptimization(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to optimize portfolio');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getSectorAllocation = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/advanced-analytics/portfolio/sector-allocation');
            setSectorAllocation(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get sector allocation');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getAttributionAnalysis = useCallback(async (startDate = null, endDate = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/advanced-analytics/portfolio/attribution', {
                start_date: startDate,
                end_date: endDate
            });
            setAttributionAnalysis(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get attribution analysis');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getRiskMetrics = useCallback(async (startDate = null, endDate = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = {};
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await apiClient.get('/advanced-analytics/portfolio/risk-metrics', { params });
            setRiskMetrics(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get risk metrics');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getPerformanceComparison = useCallback(async (benchmark = 'SPY', startDate = null, endDate = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const params = { benchmark };
            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await apiClient.get('/advanced-analytics/portfolio/performance-comparison', { params });
            setPerformanceComparison(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get performance comparison');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getCorrelationMatrix = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/advanced-analytics/portfolio/correlation-matrix');
            setCorrelationMatrix(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get correlation matrix');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getEfficientFrontier = useCallback(async (numPortfolios = 100) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/advanced-analytics/portfolio/efficient-frontier', {
                params: { num_portfolios: numPortfolios }
            });
            setEfficientFrontier(response.data);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get efficient frontier');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Load initial data
    useEffect(() => {
        getPortfolioMetrics();
        getSectorAllocation();
        getRiskMetrics();
    }, [getPortfolioMetrics, getSectorAllocation, getRiskMetrics]);

    return {
        portfolioMetrics,
        portfolioOptimization,
        sectorAllocation,
        attributionAnalysis,
        riskMetrics,
        performanceComparison,
        correlationMatrix,
        efficientFrontier,
        isLoading,
        error,
        getPortfolioMetrics,
        optimizePortfolio,
        getSectorAllocation,
        getAttributionAnalysis,
        getRiskMetrics,
        getPerformanceComparison,
        getCorrelationMatrix,
        getEfficientFrontier
    };
};

export default useAdvancedAnalytics;

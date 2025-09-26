import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

export const useCache = () => {
    const [cacheStats, setCacheStats] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const getCacheStats = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/cache/stats');
            setCacheStats(response.data.stats);
            return response.data.stats;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get cache stats');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const setCacheValue = useCallback(async (key, value, ttl = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/cache/keys', {
                key,
                value,
                ttl
            });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to set cache value');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getCacheValue = useCallback(async (key) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/cache/keys/${key}`);
            return response.data.value;
        } catch (err) {
            if (err.response?.status === 404) {
                return null;
            }
            setError(err.response?.data?.detail || 'Failed to get cache value');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const deleteCacheValue = useCallback(async (key) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.delete(`/cache/keys/${key}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to delete cache value');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const checkCacheKeyExists = useCallback(async (key) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/cache/keys/${key}/exists`);
            return response.data.exists;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to check cache key');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getCacheTTL = useCallback(async (key) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/cache/keys/${key}/ttl`);
            return response.data.ttl;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get cache TTL');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const setCacheTTL = useCallback(async (key, ttl) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post(`/cache/keys/${key}/expire?ttl=${ttl}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to set cache TTL');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const setMultipleCacheValues = useCallback(async (mapping, ttl = null) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/cache/keys/multiple', {
                mapping,
                ttl
            });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to set multiple cache values');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getMultipleCacheValues = useCallback(async (keys) => {
        try {
            setIsLoading(true);
            setError(null);
            const keysParam = Array.isArray(keys) ? keys.join(',') : keys;
            const response = await apiClient.get(`/cache/keys/multiple?keys=${keysParam}`);
            return response.data.values;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get multiple cache values');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const deleteMultipleCacheValues = useCallback(async (keys) => {
        try {
            setIsLoading(true);
            setError(null);
            const keysParam = Array.isArray(keys) ? keys.join(',') : keys;
            const response = await apiClient.delete(`/cache/keys/multiple?keys=${keysParam}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to delete multiple cache values');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const clearCachePattern = useCallback(async (pattern) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.delete(`/cache/pattern/${pattern}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to clear cache pattern');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const invalidateUserCache = useCallback(async (userId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post(`/cache/invalidate/user/${userId}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to invalidate user cache');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const invalidateSymbolCache = useCallback(async (symbol) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post(`/cache/invalidate/symbol/${symbol}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to invalidate symbol cache');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const warmCache = useCallback(async (symbols) => {
        try {
            setIsLoading(true);
            setError(null);
            const symbolsParam = Array.isArray(symbols) ? symbols.join(',') : symbols;
            const response = await apiClient.post(`/cache/warm?symbols=${symbolsParam}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to warm cache');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const checkCacheHealth = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/cache/health');
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to check cache health');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const flushAllCache = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/cache/flush');
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to flush cache');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Load cache stats on mount
    useEffect(() => {
        getCacheStats();
    }, [getCacheStats]);

    return {
        cacheStats,
        isLoading,
        error,
        getCacheStats,
        setCacheValue,
        getCacheValue,
        deleteCacheValue,
        checkCacheKeyExists,
        getCacheTTL,
        setCacheTTL,
        setMultipleCacheValues,
        getMultipleCacheValues,
        deleteMultipleCacheValues,
        clearCachePattern,
        invalidateUserCache,
        invalidateSymbolCache,
        warmCache,
        checkCacheHealth,
        flushAllCache
    };
};

export default useCache;

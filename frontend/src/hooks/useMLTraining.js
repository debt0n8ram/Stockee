import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

export const useMLTraining = () => {
    const [models, setModels] = useState([]);
    const [availableModelTypes, setAvailableModelTypes] = useState([]);
    const [availableFeatures, setAvailableFeatures] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const getModels = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/ml-training/models');
            setModels(response.data.models);
            return response.data.models;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get models');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getModelDetails = useCallback(async (modelId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/ml-training/models/${modelId}`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get model details');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getModelPerformance = useCallback(async (modelId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/ml-training/models/${modelId}/performance`);
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get model performance');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const trainPricePredictionModel = useCallback(async (symbol, modelType, features, targetDays = 1) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/ml-training/train/price-prediction', {
                symbol,
                model_type: modelType,
                features,
                target_days: targetDays
            });
            // Refresh models list
            await getModels();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to train price prediction model');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, [getModels]);

    const trainSentimentModel = useCallback(async (symbol, modelType) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/ml-training/train/sentiment', {
                symbol,
                model_type: modelType
            });
            // Refresh models list
            await getModels();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to train sentiment model');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, [getModels]);

    const trainPortfolioOptimizationModel = useCallback(async (modelType) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/ml-training/train/portfolio-optimization', {
                model_type: modelType
            });
            // Refresh models list
            await getModels();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to train portfolio optimization model');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, [getModels]);

    const getModelPredictions = useCallback(async (modelId, inputData) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post('/ml-training/predict', {
                model_id: modelId,
                input_data: inputData
            });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get model predictions');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const deleteModel = useCallback(async (modelId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.delete(`/ml-training/models/${modelId}`);
            // Refresh models list
            await getModels();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to delete model');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, [getModels]);

    const retrainModel = useCallback(async (modelId) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.post(`/ml-training/models/${modelId}/retrain`);
            // Refresh models list
            await getModels();
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to retrain model');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, [getModels]);

    const getModelPredictionsHistory = useCallback(async (modelId, limit = 50) => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get(`/ml-training/models/${modelId}/predictions/history`, {
                params: { limit }
            });
            return response.data;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get model predictions history');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getAvailableModelTypes = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/ml-training/models/types/available');
            setAvailableModelTypes(response.data.model_types);
            return response.data.model_types;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get available model types');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const getAvailableFeatures = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await apiClient.get('/ml-training/models/features/available');
            setAvailableFeatures(response.data.features);
            return response.data.features;
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get available features');
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Load initial data
    useEffect(() => {
        getModels();
        getAvailableModelTypes();
        getAvailableFeatures();
    }, [getModels, getAvailableModelTypes, getAvailableFeatures]);

    return {
        models,
        availableModelTypes,
        availableFeatures,
        isLoading,
        error,
        getModels,
        getModelDetails,
        getModelPerformance,
        trainPricePredictionModel,
        trainSentimentModel,
        trainPortfolioOptimizationModel,
        getModelPredictions,
        deleteModel,
        retrainModel,
        getModelPredictionsHistory,
        getAvailableModelTypes,
        getAvailableFeatures
    };
};

export default useMLTraining;

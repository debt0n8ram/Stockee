import React, { useState, useEffect } from 'react';
import useMLTraining from '../hooks/useMLTraining';
import { formatCurrency, formatPercentage } from '../utils/formatters';

const MLTraining = ({ className = '' }) => {
    const {
        models,
        availableModelTypes,
        availableFeatures,
        isLoading,
        error,
        trainPricePredictionModel,
        trainSentimentModel,
        trainPortfolioOptimizationModel,
        getModelPredictions,
        deleteModel,
        retrainModel,
        getModelDetails
    } = useMLTraining();

    const [activeTab, setActiveTab] = useState('models');
    const [selectedModel, setSelectedModel] = useState(null);
    const [trainingForm, setTrainingForm] = useState({
        symbol: '',
        modelType: 'random_forest',
        features: [],
        targetDays: 1
    });
    const [predictionForm, setPredictionForm] = useState({
        modelId: '',
        inputData: {}
    });

    const handleTrainModel = async (type) => {
        try {
            if (type === 'price_prediction') {
                await trainPricePredictionModel(
                    trainingForm.symbol,
                    trainingForm.modelType,
                    trainingForm.features,
                    trainingForm.targetDays
                );
            } else if (type === 'sentiment') {
                await trainSentimentModel(trainingForm.symbol, trainingForm.modelType);
            } else if (type === 'portfolio_optimization') {
                await trainPortfolioOptimizationModel(trainingForm.modelType);
            }
            setTrainingForm({
                symbol: '',
                modelType: 'random_forest',
                features: [],
                targetDays: 1
            });
        } catch (err) {
            console.error('Failed to train model:', err);
        }
    };

    const handleGetPrediction = async () => {
        try {
            const result = await getModelPredictions(predictionForm.modelId, predictionForm.inputData);
            alert(`Prediction: ${result.prediction}`);
        } catch (err) {
            console.error('Failed to get prediction:', err);
        }
    };

    const handleDeleteModel = async (modelId) => {
        if (window.confirm('Are you sure you want to delete this model?')) {
            try {
                await deleteModel(modelId);
            } catch (err) {
                console.error('Failed to delete model:', err);
            }
        }
    };

    const handleRetrainModel = async (modelId) => {
        try {
            await retrainModel(modelId);
        } catch (err) {
            console.error('Failed to retrain model:', err);
        }
    };

    const renderModelsList = () => (
        <div className="space-y-4">
            {models.map(model => (
                <div key={model.id} className="bg-white p-6 rounded-lg shadow-sm border">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h4 className="text-lg font-semibold text-gray-900">
                                {model.symbol} - {model.model_type}
                            </h4>
                            <p className="text-sm text-gray-600">
                                Trained on {new Date(model.training_date).toLocaleDateString()}
                            </p>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => setSelectedModel(model)}
                                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                            >
                                View Details
                            </button>
                            <button
                                onClick={() => handleRetrainModel(model.id)}
                                className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                            >
                                Retrain
                            </button>
                            <button
                                onClick={() => handleDeleteModel(model.id)}
                                className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                            >
                                Delete
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <h5 className="font-medium text-gray-900 mb-2">Features</h5>
                            <div className="text-sm text-gray-600">
                                {model.features.join(', ')}
                            </div>
                        </div>
                        <div>
                            <h5 className="font-medium text-gray-900 mb-2">Target Days</h5>
                            <div className="text-sm text-gray-600">
                                {model.target_days} day(s)
                            </div>
                        </div>
                        <div>
                            <h5 className="font-medium text-gray-900 mb-2">Data Points</h5>
                            <div className="text-sm text-gray-600">
                                {model.data_points.toLocaleString()}
                            </div>
                        </div>
                    </div>

                    <div className="mt-4">
                        <h5 className="font-medium text-gray-900 mb-2">Metrics</h5>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                                <span className="text-gray-600">MSE:</span>
                                <span className="ml-2 font-semibold">{model.metrics.mse.toFixed(4)}</span>
                            </div>
                            <div>
                                <span className="text-gray-600">MAE:</span>
                                <span className="ml-2 font-semibold">{model.metrics.mae.toFixed(4)}</span>
                            </div>
                            <div>
                                <span className="text-gray-600">R²:</span>
                                <span className="ml-2 font-semibold">{model.metrics.r2.toFixed(4)}</span>
                            </div>
                            <div>
                                <span className="text-gray-600">RMSE:</span>
                                <span className="ml-2 font-semibold">{model.metrics.rmse.toFixed(4)}</span>
                            </div>
                        </div>
                    </div>
                </div>
            ))}

            {models.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                    No models trained yet. Start by training your first model!
                </div>
            )}
        </div>
    );

    const renderTrainingForm = () => (
        <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Train Price Prediction Model</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Symbol
                        </label>
                        <input
                            type="text"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={trainingForm.symbol}
                            onChange={(e) => setTrainingForm(prev => ({ ...prev, symbol: e.target.value }))}
                            placeholder="e.g., AAPL"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Model Type
                        </label>
                        <select
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={trainingForm.modelType}
                            onChange={(e) => setTrainingForm(prev => ({ ...prev, modelType: e.target.value }))}
                        >
                            {availableModelTypes.map(type => (
                                <option key={type.name} value={type.name}>
                                    {type.description}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Features
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {availableFeatures.map(feature => (
                            <label key={feature.name} className="flex items-center">
                                <input
                                    type="checkbox"
                                    className="mr-2"
                                    checked={trainingForm.features.includes(feature.name)}
                                    onChange={(e) => {
                                        if (e.target.checked) {
                                            setTrainingForm(prev => ({
                                                ...prev,
                                                features: [...prev.features, feature.name]
                                            }));
                                        } else {
                                            setTrainingForm(prev => ({
                                                ...prev,
                                                features: prev.features.filter(f => f !== feature.name)
                                            }));
                                        }
                                    }}
                                />
                                <span className="text-sm">{feature.name}</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Target Days
                    </label>
                    <input
                        type="number"
                        min="1"
                        max="30"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={trainingForm.targetDays}
                        onChange={(e) => setTrainingForm(prev => ({ ...prev, targetDays: parseInt(e.target.value) }))}
                    />
                </div>

                <button
                    onClick={() => handleTrainModel('price_prediction')}
                    disabled={isLoading || !trainingForm.symbol || trainingForm.features.length === 0}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                    {isLoading ? 'Training...' : 'Train Model'}
                </button>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Train Sentiment Model</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Symbol
                        </label>
                        <input
                            type="text"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={trainingForm.symbol}
                            onChange={(e) => setTrainingForm(prev => ({ ...prev, symbol: e.target.value }))}
                            placeholder="e.g., AAPL"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Model Type
                        </label>
                        <select
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            value={trainingForm.modelType}
                            onChange={(e) => setTrainingForm(prev => ({ ...prev, modelType: e.target.value }))}
                        >
                            {availableModelTypes.map(type => (
                                <option key={type.name} value={type.name}>
                                    {type.description}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <button
                    onClick={() => handleTrainModel('sentiment')}
                    disabled={isLoading || !trainingForm.symbol}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                    {isLoading ? 'Training...' : 'Train Sentiment Model'}
                </button>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Train Portfolio Optimization Model</h4>
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Model Type
                    </label>
                    <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={trainingForm.modelType}
                        onChange={(e) => setTrainingForm(prev => ({ ...prev, modelType: e.target.value }))}
                    >
                        {availableModelTypes.map(type => (
                            <option key={type.name} value={type.name}>
                                {type.description}
                            </option>
                        ))}
                    </select>
                </div>

                <button
                    onClick={() => handleTrainModel('portfolio_optimization')}
                    disabled={isLoading}
                    className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
                >
                    {isLoading ? 'Training...' : 'Train Portfolio Model'}
                </button>
            </div>
        </div>
    );

    const renderPredictionForm = () => (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Get Model Prediction</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Model
                    </label>
                    <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={predictionForm.modelId}
                        onChange={(e) => setPredictionForm(prev => ({ ...prev, modelId: e.target.value }))}
                    >
                        <option value="">Select a model</option>
                        {models.map(model => (
                            <option key={model.id} value={model.id}>
                                {model.symbol} - {model.model_type}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {predictionForm.modelId && (
                <div className="mb-4">
                    <h5 className="font-medium text-gray-900 mb-2">Input Data</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {models.find(m => m.id === parseInt(predictionForm.modelId))?.features.map(feature => (
                            <div key={feature}>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    {feature}
                                </label>
                                <input
                                    type="number"
                                    step="0.01"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    value={predictionForm.inputData[feature] || ''}
                                    onChange={(e) => setPredictionForm(prev => ({
                                        ...prev,
                                        inputData: {
                                            ...prev.inputData,
                                            [feature]: parseFloat(e.target.value)
                                        }
                                    }))}
                                />
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <button
                onClick={handleGetPrediction}
                disabled={isLoading || !predictionForm.modelId || Object.keys(predictionForm.inputData).length === 0}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
                {isLoading ? 'Getting Prediction...' : 'Get Prediction'}
            </button>
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
                            { id: 'models', label: 'My Models' },
                            { id: 'training', label: 'Train New Model' },
                            { id: 'prediction', label: 'Get Prediction' }
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
                    {activeTab === 'models' && renderModelsList()}
                    {activeTab === 'training' && renderTrainingForm()}
                    {activeTab === 'prediction' && renderPredictionForm()}
                </div>
            </div>
        </div>
    );
};

export default MLTraining;

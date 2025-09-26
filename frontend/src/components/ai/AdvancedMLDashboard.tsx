import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import {
    Brain,
    TrendingUp,
    BarChart3,
    Target,
    Zap,
    CheckCircle,
    XCircle,
    Clock,
    AlertTriangle,
    Info,
    Play,
    Trash2,
    RefreshCw
} from 'lucide-react';
import { apiService } from '../../services/api';

interface MLModel {
    type: string;
    name: string;
    description: string;
    strengths: string[];
    best_for: string;
    training_time: string;
    accuracy: string;
}

interface TrainedModel {
    symbol: string;
    model_type: string;
    file_path: string;
    created_at: string;
}

interface ModelPerformance {
    model_type: string;
    r2_score: number;
    mae?: number;
    status: string;
    component_models?: string[];
}

export const AdvancedMLDashboard: React.FC = () => {
    const [availableModels, setAvailableModels] = useState<MLModel[]>([]);
    const [trainedModels, setTrainedModels] = useState<TrainedModel[]>([]);
    const [modelPerformance, setModelPerformance] = useState<Record<string, ModelPerformance>>({});
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [success, setSuccess] = useState<string>('');

    // Form state
    const [selectedSymbol, setSelectedSymbol] = useState<string>('');
    const [selectedModels, setSelectedModels] = useState<string[]>([]);
    const [lookbackDays, setLookbackDays] = useState<number>(365);
    const [predictionSymbol, setPredictionSymbol] = useState<string>('');
    const [predictionModel, setPredictionModel] = useState<string>('');
    const [daysAhead, setDaysAhead] = useState<number>(7);

    // Predictions state
    const [predictions, setPredictions] = useState<any>(null);
    const [isPredicting, setIsPredicting] = useState(false);

    useEffect(() => {
        loadAvailableModels();
        loadTrainedModels();
    }, []);

    const loadAvailableModels = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/advanced-ml/models/available`);
            const data = await response.json();
            setAvailableModels(data.models || []);
        } catch (err) {
            console.error('Failed to load available models:', err);
        }
    };

    const loadTrainedModels = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/advanced-ml/models/list`);
            const data = await response.json();
            setTrainedModels(data.trained_models || []);
        } catch (err) {
            console.error('Failed to load trained models:', err);
        }
    };

    const loadModelPerformance = async (symbol: string) => {
        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/advanced-ml/performance/${symbol}`);
            const data = await response.json();
            setModelPerformance(data.model_performance || {});
        } catch (err) {
            console.error('Failed to load model performance:', err);
        }
    };

    const handleTrainModels = async () => {
        if (!selectedSymbol || selectedModels.length === 0) {
            setError('Please select a symbol and at least one model type');
            return;
        }

        setIsLoading(true);
        setError('');
        setSuccess('');

        try {
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/advanced-ml/train`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: selectedSymbol,
                    model_types: selectedModels,
                    lookback_days: lookbackDays
                })
            });

            const data = await response.json();
            if (response.ok) {
                setSuccess(`Training started for ${selectedSymbol} with models: ${selectedModels.join(', ')}`);

                // Refresh trained models after a delay
                setTimeout(() => {
                    loadTrainedModels();
                }, 5000);
            } else {
                setError(data.detail || 'Failed to start training');
            }
        } catch (err: any) {
            setError(err.message || 'Failed to start training');
        } finally {
            setIsLoading(false);
        }
    };

    const handleGetPredictions = async () => {
        if (!predictionSymbol || !predictionModel) {
            setError('Please select a symbol and model type for predictions');
            return;
        }

        setIsPredicting(true);
        setError('');
        setPredictions(null);

        try {
            const params = new URLSearchParams({
                model_type: predictionModel,
                days_ahead: daysAhead.toString()
            });
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/advanced-ml/predictions/${predictionSymbol}?${params}`);
            const data = await response.json();

            setPredictions(data);
            setSuccess(`Predictions generated for ${predictionSymbol} using ${predictionModel} model`);

        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to get predictions');
        } finally {
            setIsPredicting(false);
        }
    };

    const handleDeleteModel = async (symbol: string, modelType?: string) => {
        try {
            const params = modelType ? new URLSearchParams({ model_type: modelType }) : '';
            const url = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/advanced-ml/models/${symbol}${params ? '?' + params : ''}`;
            const response = await fetch(url, { method: 'DELETE' });
            const data = await response.json();

            setSuccess(data.message || 'Model deleted successfully');
            loadTrainedModels();

            if (modelPerformance[symbol]) {
                loadModelPerformance(symbol);
            }

        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete model');
        }
    };

    const getModelIcon = (modelType: string) => {
        switch (modelType) {
            case 'lstm':
                return <Brain className="h-4 w-4" />;
            case 'transformer':
                return <Zap className="h-4 w-4" />;
            case 'ensemble':
                return <BarChart3 className="h-4 w-4" />;
            case 'xgboost':
            case 'lightgbm':
            case 'catboost':
                return <TrendingUp className="h-4 w-4" />;
            case 'deep_learning':
                return <Brain className="h-4 w-4" />;
            default:
                return <Target className="h-4 w-4" />;
        }
    };

    const getAccuracyColor = (accuracy: string) => {
        switch (accuracy) {
            case 'Very High':
                return 'bg-green-100 text-green-800';
            case 'High':
                return 'bg-blue-100 text-blue-800';
            case 'Medium':
                return 'bg-yellow-100 text-yellow-800';
            case 'Low':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    const getTrainingTimeColor = (time: string) => {
        switch (time) {
            case 'Low':
                return 'bg-green-100 text-green-800';
            case 'Medium':
                return 'bg-yellow-100 text-yellow-800';
            case 'High':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Advanced ML Dashboard</h1>
                    <p className="text-gray-600">Train and manage sophisticated machine learning models</p>
                </div>
                <Button onClick={loadTrainedModels} variant="outline">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                </Button>
            </div>

            {/* Alerts */}
            {error && (
                <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            {success && (
                <Alert>
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription>{success}</AlertDescription>
                </Alert>
            )}

            <Tabs defaultValue="train" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="train">Train Models</TabsTrigger>
                    <TabsTrigger value="predict">Get Predictions</TabsTrigger>
                    <TabsTrigger value="models">Trained Models</TabsTrigger>
                    <TabsTrigger value="performance">Performance</TabsTrigger>
                </TabsList>

                {/* Train Models Tab */}
                <TabsContent value="train" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Play className="h-5 w-5" />
                                Train New Models
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <Label htmlFor="symbol">Symbol</Label>
                                    <Input
                                        id="symbol"
                                        value={selectedSymbol}
                                        onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
                                        placeholder="Enter symbol (e.g., AAPL)"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="lookback">Lookback Days</Label>
                                    <Input
                                        id="lookback"
                                        type="number"
                                        value={lookbackDays}
                                        onChange={(e) => setLookbackDays(parseInt(e.target.value))}
                                        placeholder="365"
                                    />
                                </div>
                            </div>

                            <div>
                                <Label>Select Models to Train</Label>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
                                    {availableModels.map((model) => (
                                        <Card
                                            key={model.type}
                                            className={`cursor-pointer transition-colors ${selectedModels.includes(model.type)
                                                ? 'ring-2 ring-blue-500 bg-blue-50'
                                                : 'hover:bg-gray-50'
                                                }`}
                                            onClick={() => {
                                                if (selectedModels.includes(model.type)) {
                                                    setSelectedModels(selectedModels.filter(m => m !== model.type));
                                                } else {
                                                    setSelectedModels([...selectedModels, model.type]);
                                                }
                                            }}
                                        >
                                            <CardContent className="p-4">
                                                <div className="flex items-center gap-2 mb-2">
                                                    {getModelIcon(model.type)}
                                                    <h3 className="font-medium">{model.name}</h3>
                                                </div>
                                                <p className="text-sm text-gray-600 mb-2">{model.description}</p>
                                                <div className="flex gap-2 mb-2">
                                                    <Badge className={getAccuracyColor(model.accuracy)}>
                                                        {model.accuracy}
                                                    </Badge>
                                                    <Badge className={getTrainingTimeColor(model.training_time)}>
                                                        {model.training_time}
                                                    </Badge>
                                                </div>
                                                <p className="text-xs text-gray-500">
                                                    <strong>Best for:</strong> {model.best_for}
                                                </p>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            </div>

                            <Button
                                onClick={handleTrainModels}
                                disabled={isLoading || !selectedSymbol || selectedModels.length === 0}
                                className="w-full"
                            >
                                {isLoading ? (
                                    <>
                                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                        Training Models...
                                    </>
                                ) : (
                                    <>
                                        <Play className="h-4 w-4 mr-2" />
                                        Start Training
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Get Predictions Tab */}
                <TabsContent value="predict" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Target className="h-5 w-5" />
                                Get Predictions
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <Label htmlFor="pred_symbol">Symbol</Label>
                                    <Input
                                        id="pred_symbol"
                                        value={predictionSymbol}
                                        onChange={(e) => setPredictionSymbol(e.target.value.toUpperCase())}
                                        placeholder="Enter symbol"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="pred_model">Model Type</Label>
                                    <Select value={predictionModel} onValueChange={setPredictionModel}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select model" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {availableModels.map((model) => (
                                                <SelectItem key={model.type} value={model.type}>
                                                    <div className="flex items-center gap-2">
                                                        {getModelIcon(model.type)}
                                                        <span>{model.name}</span>
                                                    </div>
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div>
                                    <Label htmlFor="days_ahead">Days Ahead</Label>
                                    <Input
                                        id="days_ahead"
                                        type="number"
                                        value={daysAhead}
                                        onChange={(e) => setDaysAhead(parseInt(e.target.value))}
                                        placeholder="7"
                                    />
                                </div>
                            </div>

                            <Button
                                onClick={handleGetPredictions}
                                disabled={isPredicting || !predictionSymbol || !predictionModel}
                                className="w-full"
                            >
                                {isPredicting ? (
                                    <>
                                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                        Generating Predictions...
                                    </>
                                ) : (
                                    <>
                                        <Target className="h-4 w-4 mr-2" />
                                        Get Predictions
                                    </>
                                )}
                            </Button>

                            {predictions && (
                                <Card>
                                    <CardHeader>
                                        <CardTitle>Predictions for {predictions.symbol}</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-4">
                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <Label>Model Type</Label>
                                                    <p className="font-medium">{predictions.model_type}</p>
                                                </div>
                                                <div>
                                                    <Label>Current Price</Label>
                                                    <p className="font-medium">${predictions.current_price}</p>
                                                </div>
                                            </div>

                                            <div>
                                                <Label>Price Predictions</Label>
                                                <div className="space-y-2 mt-2">
                                                    {predictions.predictions.map((pred: any) => (
                                                        <div key={pred.day} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                                                            <span>Day {pred.day}</span>
                                                            <div className="text-right">
                                                                <p className="font-medium">${pred.predicted_price}</p>
                                                                <p className="text-sm text-gray-600">
                                                                    {pred.predicted_return > 0 ? '+' : ''}{pred.predicted_return}%
                                                                </p>
                                                            </div>
                                                            <Badge variant="outline">
                                                                {Math.round(pred.confidence * 100)}% confidence
                                                            </Badge>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Trained Models Tab */}
                <TabsContent value="models" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Brain className="h-5 w-5" />
                                Trained Models ({trainedModels.length})
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {trainedModels.length === 0 ? (
                                <div className="text-center py-8">
                                    <Brain className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                    <p className="text-gray-600">No trained models found</p>
                                    <p className="text-sm text-gray-500">Train some models to see them here</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {Object.entries(
                                        trainedModels.reduce((acc, model) => {
                                            if (!acc[model.symbol]) {
                                                acc[model.symbol] = [];
                                            }
                                            acc[model.symbol].push(model);
                                            return acc;
                                        }, {} as Record<string, TrainedModel[]>)
                                    ).map(([symbol, models]) => (
                                        <Card key={symbol}>
                                            <CardHeader>
                                                <div className="flex items-center justify-between">
                                                    <CardTitle className="flex items-center gap-2">
                                                        {symbol}
                                                        <Badge variant="outline">{models.length} models</Badge>
                                                    </CardTitle>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => handleDeleteModel(symbol)}
                                                    >
                                                        <Trash2 className="h-4 w-4 mr-2" />
                                                        Delete All
                                                    </Button>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                                    {models.map((model) => (
                                                        <div key={model.model_type} className="flex items-center justify-between p-3 border rounded">
                                                            <div className="flex items-center gap-2">
                                                                {getModelIcon(model.model_type)}
                                                                <div>
                                                                    <p className="font-medium">{model.model_type}</p>
                                                                    <p className="text-sm text-gray-600">
                                                                        {new Date(model.created_at).toLocaleDateString()}
                                                                    </p>
                                                                </div>
                                                            </div>
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => handleDeleteModel(symbol, model.model_type)}
                                                            >
                                                                <Trash2 className="h-4 w-4" />
                                                            </Button>
                                                        </div>
                                                    ))}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Performance Tab */}
                <TabsContent value="performance" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <BarChart3 className="h-5 w-5" />
                                Model Performance
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div>
                                    <Label htmlFor="perf_symbol">Symbol</Label>
                                    <div className="flex gap-2">
                                        <Input
                                            id="perf_symbol"
                                            value={selectedSymbol}
                                            onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
                                            placeholder="Enter symbol"
                                        />
                                        <Button onClick={() => loadModelPerformance(selectedSymbol)}>
                                            Load Performance
                                        </Button>
                                    </div>
                                </div>

                                {Object.keys(modelPerformance).length > 0 && (
                                    <div className="space-y-4">
                                        {Object.entries(modelPerformance).map(([modelType, performance]) => (
                                            <Card key={modelType}>
                                                <CardContent className="p-4">
                                                    <div className="flex items-center justify-between mb-4">
                                                        <div className="flex items-center gap-2">
                                                            {getModelIcon(modelType)}
                                                            <h3 className="font-medium">{modelType.toUpperCase()}</h3>
                                                        </div>
                                                        <Badge variant={performance.status === 'trained' ? 'default' : 'secondary'}>
                                                            {performance.status}
                                                        </Badge>
                                                    </div>

                                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                                        <div>
                                                            <Label>R² Score</Label>
                                                            <p className="font-medium">{performance.r2_score}</p>
                                                        </div>
                                                        {performance.mae && (
                                                            <div>
                                                                <Label>MAE</Label>
                                                                <p className="font-medium">{performance.mae}</p>
                                                            </div>
                                                        )}
                                                        {performance.component_models && (
                                                            <div className="md:col-span-2">
                                                                <Label>Component Models</Label>
                                                                <div className="flex gap-1 mt-1">
                                                                    {performance.component_models.map((model) => (
                                                                        <Badge key={model} variant="outline" className="text-xs">
                                                                            {model}
                                                                        </Badge>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};

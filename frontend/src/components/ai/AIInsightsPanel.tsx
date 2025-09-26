import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { Textarea } from '../ui/textarea';
import {
    Brain,
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    CheckCircle,
    Clock,
    MessageSquare,
    BarChart3,
    Target,
    Zap,
    Lightbulb,
    RefreshCw,
    Send,
    ThumbsUp,
    ThumbsDown
} from 'lucide-react';
// Simple date formatting function to avoid date-fns dependency
const formatDate = (date: Date, format?: string) => {
    if (format === 'MMM dd, HH:mm') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ', ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

interface AIInsight {
    id: string;
    type: 'prediction' | 'analysis' | 'recommendation' | 'alert';
    symbol: string;
    title: string;
    description: string;
    confidence: number;
    impact: 'high' | 'medium' | 'low';
    timeframe: string;
    timestamp: string;
    data: any;
}

interface AIPrediction {
    symbol: string;
    currentPrice: number;
    predictions: Array<{
        timeframe: string;
        predictedPrice: number;
        confidence: number;
        direction: 'up' | 'down' | 'sideways';
    }>;
    model: string;
    accuracy: number;
    lastUpdated: string;
}

interface AIChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
    symbols?: string[];
    suggestions?: string[];
}

interface AIInsightsPanelProps {
    symbol?: string;
    className?: string;
}

export const AIInsightsPanel: React.FC<AIInsightsPanelProps> = ({
    symbol = 'AAPL',
    className = ''
}) => {
    const [insights, setInsights] = useState<AIInsight[]>([]);
    const [predictions, setPredictions] = useState<AIPrediction | null>(null);
    const [chatMessages, setChatMessages] = useState<AIChatMessage[]>([]);
    const [chatInput, setChatInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('insights');
    const [selectedTimeframe, setSelectedTimeframe] = useState('1d');

    // Load AI insights
    useEffect(() => {
        loadAIInsights();
        loadAIPredictions();
        loadChatHistory();
    }, [symbol, selectedTimeframe]);

    const loadAIInsights = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(`/api/ai/insights/${symbol}?timeframe=${selectedTimeframe}`);
            const data = await response.json();
            setInsights(data.data || []);
        } catch (error) {
            console.error('Error loading AI insights:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const loadAIPredictions = async () => {
        try {
            const response = await fetch(`/api/ai/predictions/${symbol}?days=7`);
            const data = await response.json();
            setPredictions(data.data);
        } catch (error) {
            console.error('Error loading AI predictions:', error);
        }
    };

    const loadChatHistory = async () => {
        try {
            const response = await fetch(`/api/ai/chat/history?symbol=${symbol}`);
            const data = await response.json();
            setChatMessages(data.data || []);
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    };

    const sendChatMessage = async () => {
        if (!chatInput.trim()) return;

        const userMessage: AIChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: chatInput,
            timestamp: new Date().toISOString()
        };

        setChatMessages(prev => [...prev, userMessage]);
        setChatInput('');
        setIsLoading(true);

        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: chatInput,
                    symbol: symbol,
                    context: 'trading'
                })
            });

            const data = await response.json();
            const assistantMessage: AIChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date().toISOString(),
                symbols: data.symbols,
                suggestions: data.suggestions
            };

            setChatMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            console.error('Error sending chat message:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const rateInsight = async (insightId: string, rating: 'positive' | 'negative') => {
        try {
            await fetch(`/api/ai/insights/${insightId}/rate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rating })
            });
        } catch (error) {
            console.error('Error rating insight:', error);
        }
    };

    const getInsightIcon = (type: string) => {
        switch (type) {
            case 'prediction': return <Target className="h-4 w-4" />;
            case 'analysis': return <BarChart3 className="h-4 w-4" />;
            case 'recommendation': return <Lightbulb className="h-4 w-4" />;
            case 'alert': return <AlertTriangle className="h-4 w-4" />;
            default: return <Brain className="h-4 w-4" />;
        }
    };

    const getInsightColor = (type: string) => {
        switch (type) {
            case 'prediction': return 'text-blue-600';
            case 'analysis': return 'text-green-600';
            case 'recommendation': return 'text-yellow-600';
            case 'alert': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };

    const getImpactColor = (impact: string) => {
        switch (impact) {
            case 'high': return 'bg-red-100 text-red-800';
            case 'medium': return 'bg-yellow-100 text-yellow-800';
            case 'low': return 'bg-green-100 text-green-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className={`space-y-6 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold flex items-center space-x-2">
                        <Brain className="h-6 w-6" />
                        <span>AI Insights</span>
                    </h2>
                    <p className="text-muted-foreground">
                        Powered by advanced machine learning models
                    </p>
                </div>

                <div className="flex items-center space-x-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={loadAIInsights}
                        disabled={isLoading}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                </div>
            </div>

            {/* AI Predictions Card */}
            {predictions && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <Target className="h-5 w-5" />
                            <span>Price Predictions for {predictions.symbol}</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {predictions.predictions.map((prediction, index) => (
                                <div key={index} className="text-center p-4 border rounded-lg">
                                    <div className="text-sm text-muted-foreground mb-2">
                                        {prediction.timeframe}
                                    </div>
                                    <div className="text-2xl font-bold mb-2">
                                        ${prediction.predictedPrice.toFixed(2)}
                                    </div>
                                    <div className={`text-sm flex items-center justify-center ${prediction.direction === 'up' ? 'text-green-600' :
                                        prediction.direction === 'down' ? 'text-red-600' : 'text-gray-600'
                                        }`}>
                                        {prediction.direction === 'up' ? <TrendingUp className="h-4 w-4 mr-1" /> :
                                            prediction.direction === 'down' ? <TrendingDown className="h-4 w-4 mr-1" /> :
                                                <BarChart3 className="h-4 w-4 mr-1" />}
                                        {prediction.direction}
                                    </div>
                                    <div className="mt-2">
                                        <div className="text-xs text-muted-foreground mb-1">
                                            Confidence: {prediction.confidence}%
                                        </div>
                                        <Progress value={prediction.confidence} className="h-2" />
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="mt-4 text-sm text-muted-foreground">
                            Model: {predictions.model} | Accuracy: {predictions.accuracy}% |
                            Last updated: {formatDate(new Date(predictions.lastUpdated), 'MMM dd, HH:mm')}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Main Content */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                    <TabsTrigger value="insights">Insights</TabsTrigger>
                    <TabsTrigger value="chat">AI Chat</TabsTrigger>
                    <TabsTrigger value="analysis">Analysis</TabsTrigger>
                </TabsList>

                <TabsContent value="insights" className="space-y-4">
                    <div className="space-y-4">
                        {insights.map((insight) => (
                            <Card key={insight.id}>
                                <CardContent className="p-4">
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-start space-x-3">
                                            <div className={`${getInsightColor(insight.type)} mt-1`}>
                                                {getInsightIcon(insight.type)}
                                            </div>
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2 mb-2">
                                                    <h4 className="font-semibold">{insight.title}</h4>
                                                    <Badge variant="outline">{insight.symbol}</Badge>
                                                    <Badge className={getImpactColor(insight.impact)}>
                                                        {insight.impact} impact
                                                    </Badge>
                                                </div>
                                                <p className="text-sm text-muted-foreground mb-3">
                                                    {insight.description}
                                                </p>
                                                <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                                                    <span>Timeframe: {insight.timeframe}</span>
                                                    <span>Confidence: {insight.confidence}%</span>
                                                    <span>{formatDate(new Date(insight.timestamp), 'MMM dd, HH:mm')}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => rateInsight(insight.id, 'positive')}
                                            >
                                                <ThumbsUp className="h-3 w-3" />
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => rateInsight(insight.id, 'negative')}
                                            >
                                                <ThumbsDown className="h-3 w-3" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>

                <TabsContent value="chat" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <MessageSquare className="h-5 w-5" />
                                <span>AI Trading Assistant</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {/* Chat Messages */}
                            <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
                                {chatMessages.map((message) => (
                                    <div
                                        key={message.id}
                                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                    >
                                        <div
                                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${message.role === 'user'
                                                ? 'bg-primary text-primary-foreground'
                                                : 'bg-muted'
                                                }`}
                                        >
                                            <p className="text-sm">{message.content}</p>
                                            {message.symbols && message.symbols.length > 0 && (
                                                <div className="flex flex-wrap gap-1 mt-2">
                                                    {message.symbols.map((symbol) => (
                                                        <Badge key={symbol} variant="outline" className="text-xs">
                                                            {symbol}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            )}
                                            {message.suggestions && message.suggestions.length > 0 && (
                                                <div className="mt-2">
                                                    <p className="text-xs font-medium mb-1">Suggestions:</p>
                                                    <div className="space-y-1">
                                                        {message.suggestions.map((suggestion, index) => (
                                                            <Button
                                                                key={index}
                                                                variant="outline"
                                                                size="sm"
                                                                className="text-xs h-6"
                                                                onClick={() => setChatInput(suggestion)}
                                                            >
                                                                {suggestion}
                                                            </Button>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                                {isLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-muted px-4 py-2 rounded-lg">
                                            <div className="flex items-center space-x-2">
                                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                                                <span className="text-sm">AI is thinking...</span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Chat Input */}
                            <div className="flex space-x-2">
                                <Textarea
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    placeholder="Ask me anything about trading, market analysis, or specific stocks..."
                                    className="flex-1"
                                    rows={2}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            sendChatMessage();
                                        }
                                    }}
                                />
                                <Button
                                    onClick={sendChatMessage}
                                    disabled={!chatInput.trim() || isLoading}
                                >
                                    <Send className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="analysis" className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Technical Analysis */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <BarChart3 className="h-5 w-5" />
                                    <span>Technical Analysis</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">RSI (14)</span>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm font-medium">65.4</span>
                                            <Badge variant="outline">Neutral</Badge>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">MACD</span>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm font-medium">0.25</span>
                                            <Badge variant="default">Bullish</Badge>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">Moving Average</span>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm font-medium">Above</span>
                                            <Badge variant="default">Bullish</Badge>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">Bollinger Bands</span>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm font-medium">Middle</span>
                                            <Badge variant="outline">Neutral</Badge>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Sentiment Analysis */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Zap className="h-5 w-5" />
                                    <span>Sentiment Analysis</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">Overall Sentiment</span>
                                        <Badge variant="default">Positive</Badge>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">News Sentiment</span>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm font-medium">72%</span>
                                            <Progress value={72} className="w-20" />
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">Social Sentiment</span>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm font-medium">58%</span>
                                            <Progress value={58} className="w-20" />
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm">Analyst Sentiment</span>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm font-medium">85%</span>
                                            <Progress value={85} className="w-20" />
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
};

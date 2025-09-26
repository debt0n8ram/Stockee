import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MessageCircle, Send, Bot, User } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { apiService } from '../services/api';

export const AIAssistant: React.FC = () => {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'assistant', content: string, timestamp: Date }>>([]);
    const [sessionId, setSessionId] = useState<string | undefined>(undefined);
    const [isLoading, setIsLoading] = useState(false);

    const { data: insights } = useQuery(
        'portfolio-insights',
        () => apiService.getPortfolioInsights('user1'),
        { refetchInterval: 300000 } // 5 minutes
    );

    const { data: predictions } = useQuery(
        'price-predictions',
        () => apiService.getPricePredictions('AAPL', 7),
        { refetchInterval: 600000 } // 10 minutes
    );

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!message.trim()) return;

        const userMessage = message.trim();
        setMessage('');
        setIsLoading(true);

        // Add user message to chat history
        const newChatHistory = [...chatHistory, {
            role: 'user' as const,
            content: userMessage,
            timestamp: new Date()
        }];
        setChatHistory(newChatHistory);

        try {
            const response = await apiService.chatWithAI(userMessage, 'user1', sessionId);

            // Update session ID if provided
            if (response.session_id && !sessionId) {
                setSessionId(response.session_id);
            }

            // Add AI response to chat history
            setChatHistory([...newChatHistory, {
                role: 'assistant' as const,
                content: response.response,
                timestamp: new Date()
            }]);

        } catch (error: any) {
            toast.error('Failed to get AI response');
            console.error('Chat error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const suggestedQuestions = [
        "How is my portfolio performing?",
        "What are the best stocks to buy right now?",
        "Should I diversify my portfolio?",
        "What's the market outlook for tech stocks?",
        "How can I reduce my portfolio risk?"
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">AI Assistant</h1>
                <p className="mt-2 text-gray-600">Get insights and recommendations from our AI trading assistant</p>
            </div>

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                {/* Chat Interface */}
                <div className="lg:col-span-2">
                    <div className="card h-[600px] flex flex-col">
                        <div className="flex items-center mb-4">
                            <Bot className="h-6 w-6 text-blue-600 mr-2" />
                            <h3 className="text-lg font-medium text-gray-900">Chat with AI</h3>
                        </div>

                        {/* Chat Messages */}
                        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                            {chatHistory.length === 0 && (
                                <div className="text-center text-gray-500 py-8">
                                    <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                                    <p>Start a conversation with the AI assistant</p>
                                    <p className="text-sm">Ask about your portfolio, market trends, or trading strategies</p>
                                </div>
                            )}

                            {chatHistory.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${msg.role === 'user'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-gray-100 text-gray-900'
                                            }`}
                                    >
                                        <div className="flex items-start">
                                            {msg.role === 'assistant' && (
                                                <Bot className="h-4 w-4 mr-2 mt-1 flex-shrink-0" />
                                            )}
                                            {msg.role === 'user' && (
                                                <User className="h-4 w-4 mr-2 mt-1 flex-shrink-0" />
                                            )}
                                            <div>
                                                <p className="text-sm">{msg.content}</p>
                                                <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                                                    }`}>
                                                    {msg.timestamp.toLocaleTimeString()}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {isLoading && (
                                <div className="flex justify-start">
                                    <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                                        <div className="flex items-center">
                                            <Bot className="h-4 w-4 mr-2" />
                                            <div className="flex space-x-1">
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Message Input */}
                        <form onSubmit={handleSendMessage} className="flex space-x-2">
                            <input
                                type="text"
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                placeholder="Ask me anything about your portfolio or the market..."
                                className="flex-1 input-field"
                                disabled={isLoading}
                            />
                            <button
                                type="submit"
                                disabled={isLoading || !message.trim()}
                                className="btn-primary flex items-center"
                            >
                                <Send className="h-4 w-4" />
                            </button>
                        </form>
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Suggested Questions */}
                    <div className="card">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Suggested Questions</h3>
                        <div className="space-y-2">
                            {suggestedQuestions.map((question, index) => (
                                <button
                                    key={index}
                                    onClick={() => setMessage(question)}
                                    className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                    {question}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Portfolio Insights */}
                    {insights && (
                        <div className="card">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Insights</h3>
                            <div className="space-y-3">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Diversification Score</p>
                                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                                        <div
                                            className="bg-blue-600 h-2 rounded-full"
                                            style={{ width: `${(insights.diversification_score || 0) * 100}%` }}
                                        ></div>
                                    </div>
                                    <p className="text-xs text-gray-500 mt-1">
                                        {Math.round((insights.diversification_score || 0) * 100)}%
                                    </p>
                                </div>

                                <div>
                                    <p className="text-sm font-medium text-gray-600">Risk Level</p>
                                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${insights.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                                        insights.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-red-100 text-red-800'
                                        }`}>
                                        {insights.risk_level?.toUpperCase() || 'UNKNOWN'}
                                    </span>
                                </div>

                                <div>
                                    <p className="text-sm font-medium text-gray-600">Recommendations</p>
                                    <ul className="text-xs text-gray-600 mt-1 space-y-1">
                                        {insights.recommendations?.map((rec: string, index: number) => (
                                            <li key={index} className="flex items-start">
                                                <span className="text-blue-500 mr-1">•</span>
                                                {rec}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Price Predictions */}
                    {predictions && predictions.length > 0 && (
                        <div className="card">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">AI Predictions</h3>
                            <div className="space-y-2">
                                {predictions.slice(0, 3).map((prediction: any, index: number) => (
                                    <div key={index} className="flex justify-between items-center text-sm">
                                        <span className="text-gray-600">
                                            {new Date(prediction.date).toLocaleDateString()}
                                        </span>
                                        <span className="font-medium">
                                            ${prediction.predicted_price}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

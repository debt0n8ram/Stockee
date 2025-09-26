import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { BookOpen, CheckCircle, Clock, Target } from 'lucide-react';

const TradingEducation: React.FC = () => {
    const [completedModules, setCompletedModules] = useState<Set<string>>(new Set());

    const educationModules = [
        {
            id: 'basics',
            title: 'Trading Basics',
            description: 'Learn the fundamental concepts of stock trading, including how markets work, types of orders, and basic terminology.',
            difficulty: 'beginner',
            duration: '30 min',
            topics: ['Market Basics', 'Order Types', 'Trading Terminology', 'Risk Management']
        },
        {
            id: 'analysis',
            title: 'Technical Analysis',
            description: 'Master chart reading, technical indicators, and pattern recognition to make informed trading decisions.',
            difficulty: 'intermediate',
            duration: '45 min',
            topics: ['Chart Patterns', 'Technical Indicators', 'Support & Resistance', 'Trend Analysis']
        },
        {
            id: 'fundamental',
            title: 'Fundamental Analysis',
            description: 'Understand how to evaluate companies through financial statements, ratios, and economic indicators.',
            difficulty: 'intermediate',
            duration: '60 min',
            topics: ['Financial Statements', 'Valuation Metrics', 'Economic Indicators', 'Company Analysis']
        }
    ];

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'beginner': return 'bg-green-100 text-green-800';
            case 'intermediate': return 'bg-yellow-100 text-yellow-800';
            case 'advanced': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        Trading Education Center
                    </h1>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                        Master the art of trading with our comprehensive educational modules.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {educationModules.map((module) => (
                        <Card key={module.id} className="hover:shadow-lg transition-shadow">
                            <CardHeader>
                                <CardTitle className="flex items-center">
                                    <BookOpen className="h-5 w-5 mr-2" />
                                    {module.title}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-gray-600 mb-4">{module.description}</p>

                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <Badge className={getDifficultyColor(module.difficulty)}>
                                            {module.difficulty}
                                        </Badge>
                                        <span className="text-sm text-gray-500 flex items-center">
                                            <Clock className="h-4 w-4 mr-1" />
                                            {module.duration}
                                        </span>
                                    </div>

                                    <div>
                                        <h4 className="font-semibold text-sm mb-2">Topics:</h4>
                                        <ul className="text-sm text-gray-600 space-y-1">
                                            {module.topics.map((topic, index) => (
                                                <li key={index} className="flex items-center">
                                                    <CheckCircle className="h-3 w-3 text-green-600 mr-2" />
                                                    {topic}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <Button className="w-full">
                                        Start Learning
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TradingEducation;

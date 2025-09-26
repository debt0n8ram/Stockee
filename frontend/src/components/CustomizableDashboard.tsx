import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
    BarChart3,
    TrendingUp,
    DollarSign,
    PieChart,
    Activity,
    RefreshCw,
    Settings,
    Plus,
    Trash2,
    GripVertical
} from 'lucide-react';

interface DashboardWidget {
    id: string;
    title: string;
    type: 'chart' | 'metric' | 'table' | 'news';
    size: 'small' | 'medium' | 'large';
    position: { x: number; y: number };
    data?: any;
}

const CustomizableDashboard: React.FC = () => {
    const [widgets, setWidgets] = useState<DashboardWidget[]>([
        {
            id: 'portfolio-value',
            title: 'Portfolio Value',
            type: 'metric',
            size: 'small',
            position: { x: 0, y: 0 },
            data: { value: 125000, change: 2500, changePercent: 2.04 }
        },
        {
            id: 'market-overview',
            title: 'Market Overview',
            type: 'chart',
            size: 'large',
            position: { x: 1, y: 0 },
            data: { type: 'line', data: [] }
        },
        {
            id: 'top-gainers',
            title: 'Top Gainers',
            type: 'table',
            size: 'medium',
            position: { x: 0, y: 1 },
            data: { rows: [] }
        }
    ]);

    const [isEditing, setIsEditing] = useState(false);

    const addWidget = (type: DashboardWidget['type']) => {
        const newWidget: DashboardWidget = {
            id: `widget-${Date.now()}`,
            title: `New ${type} Widget`,
            type,
            size: 'medium',
            position: { x: 0, y: widgets.length },
            data: {}
        };
        setWidgets([...widgets, newWidget]);
    };

    const removeWidget = (id: string) => {
        setWidgets(widgets.filter(w => w.id !== id));
    };

    const renderWidget = (widget: DashboardWidget) => {
        switch (widget.type) {
            case 'metric':
                return (
                    <div className="text-center">
                        <div className="text-3xl font-bold text-gray-900">
                            ${widget.data?.value?.toLocaleString() || '0'}
                        </div>
                        <div className="text-sm text-gray-600">
                            {widget.data?.changePercent >= 0 ? '+' : ''}{widget.data?.changePercent?.toFixed(2)}%
                        </div>
                    </div>
                );
            case 'chart':
                return (
                    <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                        <BarChart3 className="h-12 w-12 text-gray-400" />
                        <span className="ml-2 text-gray-500">Chart Placeholder</span>
                    </div>
                );
            case 'table':
                return (
                    <div className="space-y-2">
                        <div className="text-sm text-gray-600">Table data will appear here</div>
                        <div className="h-32 bg-gray-50 rounded flex items-center justify-center">
                            <Activity className="h-8 w-8 text-gray-400" />
                        </div>
                    </div>
                );
            case 'news':
                return (
                    <div className="space-y-2">
                        <div className="text-sm text-gray-600">Latest market news</div>
                        <div className="h-24 bg-gray-50 rounded flex items-center justify-center">
                            <span className="text-gray-500">News feed placeholder</span>
                        </div>
                    </div>
                );
            default:
                return <div>Unknown widget type</div>;
        }
    };

    const getSizeClasses = (size: string) => {
        switch (size) {
            case 'small': return 'col-span-1';
            case 'medium': return 'col-span-2';
            case 'large': return 'col-span-3';
            default: return 'col-span-2';
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Customizable Dashboard</h1>
                        <p className="text-gray-600 mt-2">
                            Build your personalized trading dashboard with drag-and-drop widgets
                        </p>
                    </div>
                    <div className="flex items-center space-x-3">
                        <Button
                            variant="outline"
                            onClick={() => setIsEditing(!isEditing)}
                            className="flex items-center"
                        >
                            <Settings className="h-4 w-4 mr-2" />
                            {isEditing ? 'Exit Edit' : 'Edit Layout'}
                        </Button>
                        <Button className="flex items-center">
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Refresh Data
                        </Button>
                    </div>
                </div>

                {/* Widget Controls */}
                {isEditing && (
                    <Card className="mb-6">
                        <CardHeader>
                            <CardTitle>Add Widgets</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-3">
                                <Button
                                    variant="outline"
                                    onClick={() => addWidget('metric')}
                                    className="flex items-center"
                                >
                                    <DollarSign className="h-4 w-4 mr-2" />
                                    Metric
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => addWidget('chart')}
                                    className="flex items-center"
                                >
                                    <BarChart3 className="h-4 w-4 mr-2" />
                                    Chart
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => addWidget('table')}
                                    className="flex items-center"
                                >
                                    <Activity className="h-4 w-4 mr-2" />
                                    Table
                                </Button>
                                <Button
                                    variant="outline"
                                    onClick={() => addWidget('news')}
                                    className="flex items-center"
                                >
                                    <TrendingUp className="h-4 w-4 mr-2" />
                                    News
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Dashboard Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {widgets.map((widget) => (
                        <Card
                            key={widget.id}
                            className={`${getSizeClasses(widget.size)} ${isEditing ? 'ring-2 ring-blue-500' : ''}`}
                        >
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-lg font-semibold">{widget.title}</CardTitle>
                                <div className="flex items-center space-x-2">
                                    {isEditing && (
                                        <>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => removeWidget(widget.id)}
                                                className="text-red-600 hover:text-red-700"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                            <GripVertical className="h-4 w-4 text-gray-400 cursor-move" />
                                        </>
                                    )}
                                </div>
                            </CardHeader>
                            <CardContent>
                                {renderWidget(widget)}
                            </CardContent>
                        </Card>
                    ))}
                </div>

                {/* Empty State */}
                {widgets.length === 0 && (
                    <Card className="text-center py-12">
                        <CardContent>
                            <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                No widgets yet
                            </h3>
                            <p className="text-gray-600 mb-4">
                                Start building your dashboard by adding widgets
                            </p>
                            <Button onClick={() => setIsEditing(true)}>
                                <Plus className="h-4 w-4 mr-2" />
                                Add Your First Widget
                            </Button>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
};

export default CustomizableDashboard;

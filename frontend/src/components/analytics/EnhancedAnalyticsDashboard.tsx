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
    BarChart3,
    TrendingUp,
    TrendingDown,
    Shield,
    Target,
    AlertTriangle,
    PieChart,
    LineChart,
    Activity,
    DollarSign,
    Percent,
    Calendar,
    RefreshCw,
    Download,
    Settings,
    Info,
    CheckCircle,
    XCircle,
    ArrowUp,
    ArrowDown,
    Minus
} from 'lucide-react';
import { apiService } from '../../services/api';

interface PerformanceMetrics {
    total_return: number;
    annualized_return: number;
    cumulative_return: number;
    excess_return: number;
    win_rate: number;
    profit_factor: number;
    recovery_factor: number;
    sterling_ratio: number;
    burke_ratio: number;
    kappa_ratio: number;
}

interface RiskMetrics {
    volatility: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    max_drawdown: number;
    var_95: number;
    var_99: number;
    cvar_95: number;
    cvar_99: number;
    beta: number;
    alpha: number;
    information_ratio: number;
    calmar_ratio: number;
    treynor_ratio: number;
}

interface AttributionAnalysis {
    total_portfolio_return: number;
    total_contribution: number;
    asset_contributions: Array<{
        symbol: string;
        weight: number;
        return: number;
        contribution: number;
    }>;
    selection_effect: number;
    allocation_effect: number;
    interaction_effect: number;
}

interface PortfolioOptimization {
    current_portfolio: {
        return: number;
        volatility: number;
        sharpe_ratio: number;
    };
    optimal_portfolio: {
        return: number;
        volatility: number;
        sharpe_ratio: number;
    };
    weight_recommendations: Array<{
        symbol: string;
        current_weight: number;
        optimal_weight: number;
        recommended_change: number;
        action: string;
    }>;
    improvement_potential: {
        return_improvement: number;
        volatility_improvement: number;
        sharpe_improvement: number;
    };
}

interface ScenarioAnalysis {
    [key: string]: {
        return: number;
        volatility: number;
        sharpe_ratio: number;
        probability: number;
    };
}

interface StressTesting {
    [key: string]: {
        total_loss: number;
        duration_days: number;
        estimated_recovery_time: string;
        severity: string;
    };
}

export const EnhancedAnalyticsDashboard: React.FC = () => {
    const [analytics, setAnalytics] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string>('');
    const [success, setSuccess] = useState<string>('');

    // Date range
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');
    const [selectedPeriod, setSelectedPeriod] = useState<string>('1Y');

    // User ID (this would come from auth context)
    const [userId, setUserId] = useState<string>('user1');

    useEffect(() => {
        setDefaultDateRange();
    }, []);

    useEffect(() => {
        if (startDate && endDate) {
            loadAnalytics();
        }
    }, [startDate, endDate, userId]);

    const setDefaultDateRange = () => {
        const end = new Date();
        const start = new Date();
        start.setFullYear(start.getFullYear() - 1);

        setEndDate(end.toISOString().split('T')[0]);
        setStartDate(start.toISOString().split('T')[0]);
    };

    const handlePeriodChange = (period: string) => {
        setSelectedPeriod(period);
        const end = new Date();
        const start = new Date();

        switch (period) {
            case '1M':
                start.setMonth(start.getMonth() - 1);
                break;
            case '3M':
                start.setMonth(start.getMonth() - 3);
                break;
            case '6M':
                start.setMonth(start.getMonth() - 6);
                break;
            case '1Y':
                start.setFullYear(start.getFullYear() - 1);
                break;
            case '2Y':
                start.setFullYear(start.getFullYear() - 2);
                break;
            case '5Y':
                start.setFullYear(start.getFullYear() - 5);
                break;
            default:
                start.setFullYear(start.getFullYear() - 1);
        }

        setEndDate(end.toISOString().split('T')[0]);
        setStartDate(start.toISOString().split('T')[0]);
    };

    const loadAnalytics = async () => {
        setIsLoading(true);
        setError('');

        try {
            const params = new URLSearchParams({
                start_date: startDate,
                end_date: endDate
            });
            const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/enhanced-analytics/comprehensive/${userId}?${params}`);
            const data = await response.json();

            setAnalytics(data);
            setSuccess('Analytics loaded successfully');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load analytics');
        } finally {
            setIsLoading(false);
        }
    };

    const getMetricIcon = (metricName: string) => {
        switch (metricName) {
            case 'return':
            case 'total_return':
            case 'annualized_return':
                return <TrendingUp className="h-4 w-4" />;
            case 'volatility':
            case 'max_drawdown':
                return <AlertTriangle className="h-4 w-4" />;
            case 'sharpe_ratio':
            case 'sortino_ratio':
                return <Target className="h-4 w-4" />;
            case 'beta':
            case 'alpha':
                return <BarChart3 className="h-4 w-4" />;
            default:
                return <Activity className="h-4 w-4" />;
        }
    };

    const getMetricColor = (value: number, metricType: string) => {
        switch (metricType) {
            case 'return':
                return value > 0 ? 'text-green-600' : 'text-red-600';
            case 'risk':
                return value > 0.15 ? 'text-red-600' : value > 0.1 ? 'text-yellow-600' : 'text-green-600';
            case 'ratio':
                return value > 1 ? 'text-green-600' : value > 0.5 ? 'text-yellow-600' : 'text-red-600';
            default:
                return 'text-gray-600';
        }
    };

    const formatMetricValue = (value: number, type: string) => {
        switch (type) {
            case 'percentage':
                return `${value.toFixed(2)}%`;
            case 'ratio':
                return value.toFixed(2);
            case 'currency':
                return `$${value.toLocaleString()}`;
            default:
                return value.toFixed(2);
        }
    };

    const renderPerformanceMetrics = (metrics: PerformanceMetrics) => (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Total Return</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.total_return, 'return')}`}>
                                {formatMetricValue(metrics.total_return, 'percentage')}
                            </p>
                        </div>
                        <TrendingUp className="h-8 w-8 text-blue-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Annualized Return</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.annualized_return, 'return')}`}>
                                {formatMetricValue(metrics.annualized_return, 'percentage')}
                            </p>
                        </div>
                        <Calendar className="h-8 w-8 text-green-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Win Rate</p>
                            <p className="text-2xl font-bold text-blue-600">
                                {formatMetricValue(metrics.win_rate, 'percentage')}
                            </p>
                        </div>
                        <Target className="h-8 w-8 text-blue-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Profit Factor</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.profit_factor, 'ratio')}`}>
                                {formatMetricValue(metrics.profit_factor, 'ratio')}
                            </p>
                        </div>
                        <DollarSign className="h-8 w-8 text-green-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Recovery Factor</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.recovery_factor, 'ratio')}`}>
                                {formatMetricValue(metrics.recovery_factor, 'ratio')}
                            </p>
                        </div>
                        <RefreshCw className="h-8 w-8 text-purple-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Sterling Ratio</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.sterling_ratio, 'ratio')}`}>
                                {formatMetricValue(metrics.sterling_ratio, 'ratio')}
                            </p>
                        </div>
                        <BarChart3 className="h-8 w-8 text-orange-500" />
                    </div>
                </CardContent>
            </Card>
        </div>
    );

    const renderRiskMetrics = (metrics: RiskMetrics) => (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Volatility</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.volatility, 'risk')}`}>
                                {formatMetricValue(metrics.volatility, 'percentage')}
                            </p>
                        </div>
                        <Activity className="h-8 w-8 text-red-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Sharpe Ratio</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.sharpe_ratio, 'ratio')}`}>
                                {formatMetricValue(metrics.sharpe_ratio, 'ratio')}
                            </p>
                        </div>
                        <Target className="h-8 w-8 text-blue-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Max Drawdown</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.max_drawdown, 'risk')}`}>
                                {formatMetricValue(metrics.max_drawdown, 'percentage')}
                            </p>
                        </div>
                        <TrendingDown className="h-8 w-8 text-red-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">VaR (95%)</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.var_95, 'risk')}`}>
                                {formatMetricValue(metrics.var_95, 'percentage')}
                            </p>
                        </div>
                        <AlertTriangle className="h-8 w-8 text-orange-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Beta</p>
                            <p className="text-2xl font-bold text-blue-600">
                                {formatMetricValue(metrics.beta, 'ratio')}
                            </p>
                        </div>
                        <BarChart3 className="h-8 w-8 text-blue-500" />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-600">Alpha</p>
                            <p className={`text-2xl font-bold ${getMetricColor(metrics.alpha, 'return')}`}>
                                {formatMetricValue(metrics.alpha, 'percentage')}
                            </p>
                        </div>
                        <TrendingUp className="h-8 w-8 text-green-500" />
                    </div>
                </CardContent>
            </Card>
        </div>
    );

    const renderAttributionAnalysis = (attribution: AttributionAnalysis) => (
        <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-600">Total Portfolio Return</p>
                            <p className="text-2xl font-bold text-blue-600">
                                {formatMetricValue(attribution.total_portfolio_return, 'percentage')}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-600">Selection Effect</p>
                            <p className={`text-2xl font-bold ${getMetricColor(attribution.selection_effect, 'return')}`}>
                                {formatMetricValue(attribution.selection_effect, 'percentage')}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardContent className="p-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-600">Allocation Effect</p>
                            <p className={`text-2xl font-bold ${getMetricColor(attribution.allocation_effect, 'return')}`}>
                                {formatMetricValue(attribution.allocation_effect, 'percentage')}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Asset Contributions</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {attribution.asset_contributions.map((asset, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                                <div className="flex items-center gap-3">
                                    <Badge variant="outline">{asset.symbol}</Badge>
                                    <span className="text-sm text-gray-600">
                                        {formatMetricValue(asset.weight, 'percentage')} weight
                                    </span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm">
                                        Return: {formatMetricValue(asset.return, 'percentage')}
                                    </span>
                                    <span className={`font-medium ${getMetricColor(asset.contribution, 'return')}`}>
                                        Contribution: {formatMetricValue(asset.contribution, 'percentage')}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );

    const renderPortfolioOptimization = (optimization: PortfolioOptimization) => (
        <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                    <CardHeader>
                        <CardTitle>Current Portfolio</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="flex justify-between">
                            <span>Return:</span>
                            <span className={getMetricColor(optimization.current_portfolio.return, 'return')}>
                                {formatMetricValue(optimization.current_portfolio.return, 'percentage')}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span>Volatility:</span>
                            <span className={getMetricColor(optimization.current_portfolio.volatility, 'risk')}>
                                {formatMetricValue(optimization.current_portfolio.volatility, 'percentage')}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span>Sharpe Ratio:</span>
                            <span className={getMetricColor(optimization.current_portfolio.sharpe_ratio, 'ratio')}>
                                {formatMetricValue(optimization.current_portfolio.sharpe_ratio, 'ratio')}
                            </span>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Optimal Portfolio</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="flex justify-between">
                            <span>Return:</span>
                            <span className={getMetricColor(optimization.optimal_portfolio.return, 'return')}>
                                {formatMetricValue(optimization.optimal_portfolio.return, 'percentage')}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span>Volatility:</span>
                            <span className={getMetricColor(optimization.optimal_portfolio.volatility, 'risk')}>
                                {formatMetricValue(optimization.optimal_portfolio.volatility, 'percentage')}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span>Sharpe Ratio:</span>
                            <span className={getMetricColor(optimization.optimal_portfolio.sharpe_ratio, 'ratio')}>
                                {formatMetricValue(optimization.optimal_portfolio.sharpe_ratio, 'ratio')}
                            </span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Weight Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {optimization.weight_recommendations.map((rec, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                                <div className="flex items-center gap-3">
                                    <Badge variant="outline">{rec.symbol}</Badge>
                                    <span className="text-sm text-gray-600">
                                        Current: {formatMetricValue(rec.current_weight, 'percentage')}
                                    </span>
                                    <span className="text-sm text-gray-600">
                                        Optimal: {formatMetricValue(rec.optimal_weight, 'percentage')}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className={`text-sm font-medium ${rec.action === 'increase' ? 'text-green-600' :
                                        rec.action === 'decrease' ? 'text-red-600' : 'text-gray-600'
                                        }`}>
                                        {rec.action.toUpperCase()}
                                    </span>
                                    {rec.action === 'increase' && <ArrowUp className="h-4 w-4 text-green-600" />}
                                    {rec.action === 'decrease' && <ArrowDown className="h-4 w-4 text-red-600" />}
                                    {rec.action === 'hold' && <Minus className="h-4 w-4 text-gray-600" />}
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );

    const renderScenarioAnalysis = (scenarios: ScenarioAnalysis) => (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(scenarios).map(([scenario, data]) => (
                <Card key={scenario}>
                    <CardHeader>
                        <CardTitle className="text-lg capitalize">
                            {scenario.replace('_', ' ')}
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                        <div className="flex justify-between">
                            <span>Return:</span>
                            <span className={getMetricColor(data.return, 'return')}>
                                {formatMetricValue(data.return, 'percentage')}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span>Volatility:</span>
                            <span className={getMetricColor(data.volatility, 'risk')}>
                                {formatMetricValue(data.volatility, 'percentage')}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span>Sharpe Ratio:</span>
                            <span className={getMetricColor(data.sharpe_ratio, 'ratio')}>
                                {formatMetricValue(data.sharpe_ratio, 'ratio')}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span>Probability:</span>
                            <span className="text-blue-600">
                                {formatMetricValue(data.probability * 100, 'percentage')}
                            </span>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );

    const renderStressTesting = (stress: StressTesting) => (
        <div className="space-y-4">
            {Object.entries(stress).map(([scenario, data]) => (
                <Card key={scenario}>
                    <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="font-medium capitalize">
                                    {scenario.replace('_', ' ')}
                                </h3>
                                <p className="text-sm text-gray-600">
                                    Duration: {data.duration_days} days
                                </p>
                            </div>
                            <div className="text-right">
                                <p className={`text-2xl font-bold ${data.severity === 'Extreme' ? 'text-red-600' :
                                    data.severity === 'High' ? 'text-orange-600' :
                                        data.severity === 'Medium' ? 'text-yellow-600' : 'text-green-600'
                                    }`}>
                                    {formatMetricValue(data.total_loss, 'percentage')}
                                </p>
                                <p className="text-sm text-gray-600">
                                    Recovery: {data.estimated_recovery_time}
                                </p>
                            </div>
                        </div>
                        <div className="mt-3">
                            <Badge variant={
                                data.severity === 'Extreme' ? 'destructive' :
                                    data.severity === 'High' ? 'destructive' :
                                        data.severity === 'Medium' ? 'secondary' : 'default'
                            }>
                                {data.severity} Risk
                            </Badge>
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Enhanced Analytics Dashboard</h1>
                    <p className="text-gray-600">Comprehensive portfolio analysis and risk management</p>
                </div>
                <div className="flex items-center gap-2">
                    <Button onClick={loadAnalytics} disabled={isLoading}>
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Button variant="outline">
                        <Download className="h-4 w-4 mr-2" />
                        Export
                    </Button>
                </div>
            </div>

            {/* Date Range Controls */}
            <Card>
                <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <Label>Period:</Label>
                            <Select value={selectedPeriod} onValueChange={handlePeriodChange}>
                                <SelectTrigger className="w-20">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="1M">1M</SelectItem>
                                    <SelectItem value="3M">3M</SelectItem>
                                    <SelectItem value="6M">6M</SelectItem>
                                    <SelectItem value="1Y">1Y</SelectItem>
                                    <SelectItem value="2Y">2Y</SelectItem>
                                    <SelectItem value="5Y">5Y</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="flex items-center gap-2">
                            <Label>From:</Label>
                            <Input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="w-40"
                            />
                        </div>

                        <div className="flex items-center gap-2">
                            <Label>To:</Label>
                            <Input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                className="w-40"
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

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

            {/* Analytics Content */}
            {isLoading ? (
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            ) : analytics ? (
                <Tabs defaultValue="performance" className="space-y-4">
                    <TabsList>
                        <TabsTrigger value="performance">Performance</TabsTrigger>
                        <TabsTrigger value="risk">Risk Metrics</TabsTrigger>
                        <TabsTrigger value="attribution">Attribution</TabsTrigger>
                        <TabsTrigger value="optimization">Optimization</TabsTrigger>
                        <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
                        <TabsTrigger value="stress">Stress Test</TabsTrigger>
                    </TabsList>

                    <TabsContent value="performance" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <TrendingUp className="h-5 w-5" />
                                    Performance Metrics
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {renderPerformanceMetrics(analytics.performance_metrics)}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="risk" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Shield className="h-5 w-5" />
                                    Risk Metrics
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {renderRiskMetrics(analytics.risk_metrics)}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="attribution" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <PieChart className="h-5 w-5" />
                                    Performance Attribution
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {renderAttributionAnalysis(analytics.attribution_analysis)}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="optimization" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Target className="h-5 w-5" />
                                    Portfolio Optimization
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {renderPortfolioOptimization(analytics.portfolio_optimization)}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="scenarios" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <BarChart3 className="h-5 w-5" />
                                    Scenario Analysis
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {renderScenarioAnalysis(analytics.scenario_analysis)}
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="stress" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <AlertTriangle className="h-5 w-5" />
                                    Stress Testing
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                {renderStressTesting(analytics.stress_testing)}
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            ) : (
                <Card>
                    <CardContent className="p-12 text-center">
                        <BarChart3 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                        <p className="text-gray-600">No analytics data available</p>
                        <p className="text-sm text-gray-500">Select a date range and click refresh to load analytics</p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
import { Label } from '../ui/label';
import {
    LineChart,
    Line,
    BarChart,
    AreaChart,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
    Brush,
    Bar,
    Area
} from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    Volume2,
    Settings,
    Download,
    Maximize2,
    Minimize2,
    RotateCcw,
    Play,
    Pause,
    Square
} from 'lucide-react';
// Simple date formatting function to avoid date-fns dependency
const formatDate = (date: Date, format?: string) => {
    if (format === 'MMM dd, yyyy HH:mm:ss') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } else if (format === 'MMM dd, yyyy HH:mm') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' ' + date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    } else if (format === 'HH:mm') {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
};

interface AdvancedChartProps {
    symbol: string;
    data: any[];
    onTimeframeChange: (timeframe: string) => void;
    onIndicatorChange: (indicators: string[]) => void;
    className?: string;
}

interface ChartState {
    timeframe: string;
    indicators: string[];
    chartType: 'candlestick' | 'line' | 'bar' | 'area';
    showVolume: boolean;
    showGrid: boolean;
    showCrosshair: boolean;
    isFullscreen: boolean;
    isPlaying: boolean;
    playbackSpeed: number;
    currentIndex: number;
}

const timeframes = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
    { value: '1w', label: '1 Week' },
    { value: '1M', label: '1 Month' }
];

const indicators = [
    { value: 'sma', label: 'Simple Moving Average' },
    { value: 'ema', label: 'Exponential Moving Average' },
    { value: 'rsi', label: 'RSI' },
    { value: 'macd', label: 'MACD' },
    { value: 'bollinger', label: 'Bollinger Bands' },
    { value: 'stochastic', label: 'Stochastic' },
    { value: 'williams', label: 'Williams %R' },
    { value: 'cci', label: 'CCI' },
    { value: 'atr', label: 'ATR' }
];

const chartTypes = [
    { value: 'candlestick', label: 'Candlestick', icon: '📊' },
    { value: 'line', label: 'Line', icon: '📈' },
    { value: 'bar', label: 'Bar', icon: '📊' },
    { value: 'area', label: 'Area', icon: '📈' }
];

export const AdvancedChart: React.FC<AdvancedChartProps> = ({
    symbol,
    data,
    onTimeframeChange,
    onIndicatorChange,
    className = ''
}) => {
    const [chartState, setChartState] = useState<ChartState>({
        timeframe: '1d',
        indicators: ['sma', 'rsi'],
        chartType: 'candlestick',
        showVolume: true,
        showGrid: true,
        showCrosshair: true,
        isFullscreen: false,
        isPlaying: false,
        playbackSpeed: 1,
        currentIndex: data.length - 1
    });

    const [drawingMode, setDrawingMode] = useState<'none' | 'line' | 'rectangle' | 'fibonacci' | 'trend'>('none');
    const [drawings, setDrawings] = useState<any[]>([]);
    const [selectedDrawing, setSelectedDrawing] = useState<string | null>(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);

    const chartRef = useRef<HTMLDivElement>(null);
    const playbackIntervalRef = useRef<NodeJS.Timeout | null>(null);

    // Calculate technical indicators
    const calculateIndicators = useCallback((data: any[]) => {
        if (!data || data.length === 0) return data;

        let processedData = [...data];

        // Simple Moving Average
        if (chartState.indicators.includes('sma')) {
            processedData = processedData.map((item, index) => {
                if (index < 20) return item;
                const sma20 = processedData.slice(index - 19, index + 1).reduce((sum, d) => sum + d.close, 0) / 20;
                return { ...item, sma20 };
            });
        }

        // Exponential Moving Average
        if (chartState.indicators.includes('ema')) {
            const multiplier = 2 / (12 + 1);
            processedData = processedData.map((item, index) => {
                if (index === 0) return { ...item, ema12: item.close };
                const ema12 = (item.close * multiplier) + (processedData[index - 1].ema12 * (1 - multiplier));
                return { ...item, ema12 };
            });
        }

        // RSI
        if (chartState.indicators.includes('rsi')) {
            processedData = processedData.map((item, index) => {
                if (index < 14) return { ...item, rsi: 50 };

                const gains = [];
                const losses = [];

                for (let i = index - 13; i <= index; i++) {
                    const change = processedData[i].close - processedData[i - 1].close;
                    gains.push(change > 0 ? change : 0);
                    losses.push(change < 0 ? Math.abs(change) : 0);
                }

                const avgGain = gains.reduce((sum, gain) => sum + gain, 0) / 14;
                const avgLoss = losses.reduce((sum, loss) => sum + loss, 0) / 14;
                const rs = avgGain / avgLoss;
                const rsi = 100 - (100 / (1 + rs));

                return { ...item, rsi };
            });
        }

        // MACD
        if (chartState.indicators.includes('macd')) {
            const ema12Multiplier = 2 / (12 + 1);
            const ema26Multiplier = 2 / (26 + 1);

            processedData = processedData.map((item, index) => {
                if (index === 0) {
                    return { ...item, ema12: item.close, ema26: item.close, macd: 0, macdSignal: 0, macdHistogram: 0 };
                }

                const ema12 = (item.close * ema12Multiplier) + (processedData[index - 1].ema12 * (1 - ema12Multiplier));
                const ema26 = (item.close * ema26Multiplier) + (processedData[index - 1].ema26 * (1 - ema26Multiplier));
                const macd = ema12 - ema26;

                let macdSignal = 0;
                if (index >= 8) {
                    const signalMultiplier = 2 / (9 + 1);
                    macdSignal = (macd * signalMultiplier) + (processedData[index - 1].macdSignal * (1 - signalMultiplier));
                }

                const macdHistogram = macd - macdSignal;

                return { ...item, ema12, ema26, macd, macdSignal, macdHistogram };
            });
        }

        // Bollinger Bands
        if (chartState.indicators.includes('bollinger')) {
            processedData = processedData.map((item, index) => {
                if (index < 20) return item;

                const period = 20;
                const stdDev = 2;
                const sma = processedData.slice(index - period + 1, index + 1).reduce((sum, d) => sum + d.close, 0) / period;
                const variance = processedData.slice(index - period + 1, index + 1).reduce((sum, d) => sum + Math.pow(d.close - sma, 2), 0) / period;
                const standardDeviation = Math.sqrt(variance);

                return {
                    ...item,
                    bbUpper: sma + (stdDev * standardDeviation),
                    bbMiddle: sma,
                    bbLower: sma - (stdDev * standardDeviation)
                };
            });
        }

        return processedData;
    }, [chartState.indicators]);

    const processedData = calculateIndicators(data);

    // Handle timeframe change
    const handleTimeframeChange = (timeframe: string) => {
        setChartState(prev => ({ ...prev, timeframe }));
        onTimeframeChange(timeframe);
    };

    // Handle indicator toggle
    const handleIndicatorToggle = (indicator: string) => {
        setChartState(prev => ({
            ...prev,
            indicators: prev.indicators.includes(indicator)
                ? prev.indicators.filter(i => i !== indicator)
                : [...prev.indicators, indicator]
        }));
    };

    // Handle chart type change
    const handleChartTypeChange = (chartType: 'candlestick' | 'line' | 'bar' | 'area') => {
        setChartState(prev => ({ ...prev, chartType }));
    };

    // Handle fullscreen toggle
    const toggleFullscreen = () => {
        setChartState(prev => ({ ...prev, isFullscreen: !prev.isFullscreen }));
    };

    // Handle playback controls
    const startPlayback = () => {
        setChartState(prev => ({ ...prev, isPlaying: true }));
        playbackIntervalRef.current = setInterval(() => {
            setChartState(prev => {
                if (prev.currentIndex >= processedData.length - 1) {
                    return { ...prev, isPlaying: false, currentIndex: processedData.length - 1 };
                }
                return { ...prev, currentIndex: prev.currentIndex + 1 };
            });
        }, 1000 / chartState.playbackSpeed);
    };

    const pausePlayback = () => {
        setChartState(prev => ({ ...prev, isPlaying: false }));
        if (playbackIntervalRef.current) {
            clearInterval(playbackIntervalRef.current);
            playbackIntervalRef.current = null;
        }
    };

    const resetPlayback = () => {
        setChartState(prev => ({ ...prev, currentIndex: 0, isPlaying: false }));
        if (playbackIntervalRef.current) {
            clearInterval(playbackIntervalRef.current);
            playbackIntervalRef.current = null;
        }
    };

    // Handle drawing tools
    const handleMouseDown = (event: React.MouseEvent) => {
        if (drawingMode === 'none') return;

        const rect = chartRef.current?.getBoundingClientRect();
        if (!rect) return;

        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        setDrawStart({ x, y });
        setIsDrawing(true);
    };

    const handleMouseMove = (event: React.MouseEvent) => {
        if (!isDrawing || !drawStart) return;

        const rect = chartRef.current?.getBoundingClientRect();
        if (!rect) return;

        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // Update current drawing
        const newDrawing = {
            id: Date.now().toString(),
            type: drawingMode,
            start: drawStart,
            end: { x, y },
            color: '#3b82f6',
            strokeWidth: 2
        };

        setDrawings(prev => [...prev.filter(d => d.id !== 'temp'), { ...newDrawing, id: 'temp' }]);
    };

    const handleMouseUp = () => {
        if (!isDrawing) return;

        setIsDrawing(false);
        setDrawStart(null);

        // Finalize drawing
        setDrawings(prev => prev.map(d => d.id === 'temp' ? { ...d, id: Date.now().toString() } : d));
    };

    // Custom tooltip
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
                    <p className="text-sm font-medium">{formatDate(new Date(label), 'MMM dd, yyyy HH:mm')}</p>
                    <div className="space-y-1">
                        <p className="text-sm">
                            <span className="text-muted-foreground">Open:</span> ${data.open?.toFixed(2)}
                        </p>
                        <p className="text-sm">
                            <span className="text-muted-foreground">High:</span> ${data.high?.toFixed(2)}
                        </p>
                        <p className="text-sm">
                            <span className="text-muted-foreground">Low:</span> ${data.low?.toFixed(2)}
                        </p>
                        <p className="text-sm">
                            <span className="text-muted-foreground">Close:</span> ${data.close?.toFixed(2)}
                        </p>
                        {data.volume && (
                            <p className="text-sm">
                                <span className="text-muted-foreground">Volume:</span> {data.volume.toLocaleString()}
                            </p>
                        )}
                        {data.sma20 && (
                            <p className="text-sm">
                                <span className="text-muted-foreground">SMA 20:</span> ${data.sma20.toFixed(2)}
                            </p>
                        )}
                        {data.rsi && (
                            <p className="text-sm">
                                <span className="text-muted-foreground">RSI:</span> {data.rsi.toFixed(2)}
                            </p>
                        )}
                    </div>
                </div>
            );
        }
        return null;
    };

    // Render chart based on type
    const renderChart = () => {
        const chartData = chartState.isPlaying
            ? processedData.slice(0, chartState.currentIndex + 1)
            : processedData;

        const commonProps = {
            data: chartData,
            margin: { top: 20, right: 30, left: 20, bottom: 20 }
        };

        switch (chartState.chartType) {
            case 'candlestick':
                return (
                    <LineChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis
                            dataKey="timestamp"
                            tickFormatter={(value) => formatDate(new Date(value), 'HH:mm')}
                            stroke="#6b7280"
                        />
                        <YAxis
                            domain={['dataMin - 5', 'dataMax + 5']}
                            stroke="#6b7280"
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="2 2" />
                        {chartState.indicators.includes('sma') && (
                            <LineChart data={chartData}>
                                <Line type="monotone" dataKey="sma20" stroke="#f59e0b" strokeWidth={2} dot={false} />
                            </LineChart>
                        )}
                        {chartState.indicators.includes('ema') && (
                            <LineChart data={chartData}>
                                <Line type="monotone" dataKey="ema12" stroke="#10b981" strokeWidth={2} dot={false} />
                            </LineChart>
                        )}
                        {chartState.indicators.includes('bollinger') && (
                            <>
                                <LineChart data={chartData}>
                                    <Line type="monotone" dataKey="bbUpper" stroke="#8b5cf6" strokeWidth={1} dot={false} />
                                    <Line type="monotone" dataKey="bbMiddle" stroke="#8b5cf6" strokeWidth={1} dot={false} />
                                    <Line type="monotone" dataKey="bbLower" stroke="#8b5cf6" strokeWidth={1} dot={false} />
                                </LineChart>
                            </>
                        )}
                    </LineChart>
                );

            case 'line':
                return (
                    <LineChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis
                            dataKey="timestamp"
                            tickFormatter={(value) => formatDate(new Date(value), 'HH:mm')}
                            stroke="#6b7280"
                        />
                        <YAxis
                            domain={['dataMin - 5', 'dataMax + 5']}
                            stroke="#6b7280"
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Line
                            type="monotone"
                            dataKey="close"
                            stroke="#3b82f6"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4, fill: '#3b82f6' }}
                        />
                        {chartState.indicators.includes('sma') && (
                            <Line type="monotone" dataKey="sma20" stroke="#f59e0b" strokeWidth={2} dot={false} />
                        )}
                        {chartState.indicators.includes('ema') && (
                            <Line type="monotone" dataKey="ema12" stroke="#10b981" strokeWidth={2} dot={false} />
                        )}
                    </LineChart>
                );

            case 'bar':
                return (
                    <BarChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis
                            dataKey="timestamp"
                            tickFormatter={(value) => formatDate(new Date(value), 'HH:mm')}
                            stroke="#6b7280"
                        />
                        <YAxis stroke="#6b7280" />
                        <Tooltip content={<CustomTooltip />} />
                        <Bar dataKey="close" fill="#3b82f6" />
                    </BarChart>
                );

            case 'area':
                return (
                    <AreaChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis
                            dataKey="timestamp"
                            tickFormatter={(value) => formatDate(new Date(value), 'HH:mm')}
                            stroke="#6b7280"
                        />
                        <YAxis
                            domain={['dataMin - 5', 'dataMax + 5']}
                            stroke="#6b7280"
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Area
                            type="monotone"
                            dataKey="close"
                            stroke="#3b82f6"
                            fill="#3b82f6"
                            fillOpacity={0.3}
                        />
                    </AreaChart>
                );

            default:
                return null;
        }
    };

    return (
        <div className={`bg-background border border-border rounded-lg ${className} ${chartState.isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
            {/* Chart Header */}
            <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center space-x-4">
                    <h3 className="text-lg font-semibold">{symbol}</h3>
                    <div className="flex items-center space-x-2">
                        {timeframes.map((tf) => (
                            <Button
                                key={tf.value}
                                variant={chartState.timeframe === tf.value ? 'default' : 'outline'}
                                size="sm"
                                onClick={() => handleTimeframeChange(tf.value)}
                            >
                                {tf.label}
                            </Button>
                        ))}
                    </div>
                </div>

                <div className="flex items-center space-x-2">
                    {/* Chart Type Selector */}
                    <Select value={chartState.chartType} onValueChange={handleChartTypeChange}>
                        <SelectTrigger className="w-32">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {chartTypes.map((type) => (
                                <SelectItem key={type.value} value={type.value}>
                                    <div className="flex items-center space-x-2">
                                        <span>{type.icon}</span>
                                        <span>{type.label}</span>
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    {/* Playback Controls */}
                    <div className="flex items-center space-x-1">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={chartState.isPlaying ? pausePlayback : startPlayback}
                        >
                            {chartState.isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                        </Button>
                        <Button variant="outline" size="sm" onClick={resetPlayback}>
                            <RotateCcw className="h-4 w-4" />
                        </Button>
                        <Slider
                            value={[chartState.playbackSpeed]}
                            onValueChange={([value]) => setChartState(prev => ({ ...prev, playbackSpeed: value }))}
                            min={0.5}
                            max={5}
                            step={0.5}
                            className="w-20"
                        />
                    </div>

                    {/* Fullscreen Toggle */}
                    <Button variant="outline" size="sm" onClick={toggleFullscreen}>
                        {chartState.isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                    </Button>
                </div>
            </div>

            {/* Chart Controls */}
            <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center space-x-4">
                    {/* Indicators */}
                    <div className="flex items-center space-x-2">
                        <Label className="text-sm font-medium">Indicators:</Label>
                        {indicators.map((indicator) => (
                            <Badge
                                key={indicator.value}
                                variant={chartState.indicators.includes(indicator.value) ? 'default' : 'outline'}
                                className="cursor-pointer"
                                onClick={() => handleIndicatorToggle(indicator.value)}
                            >
                                {indicator.label}
                            </Badge>
                        ))}
                    </div>
                </div>

                <div className="flex items-center space-x-4">
                    {/* Chart Options */}
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <Switch
                                id="volume"
                                checked={chartState.showVolume}
                                onCheckedChange={(checked) => setChartState(prev => ({ ...prev, showVolume: checked }))}
                            />
                            <Label htmlFor="volume" className="text-sm">Volume</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                            <Switch
                                id="grid"
                                checked={chartState.showGrid}
                                onCheckedChange={(checked) => setChartState(prev => ({ ...prev, showGrid: checked }))}
                            />
                            <Label htmlFor="grid" className="text-sm">Grid</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                            <Switch
                                id="crosshair"
                                checked={chartState.showCrosshair}
                                onCheckedChange={(checked) => setChartState(prev => ({ ...prev, showCrosshair: checked }))}
                            />
                            <Label htmlFor="crosshair" className="text-sm">Crosshair</Label>
                        </div>
                    </div>

                    {/* Drawing Tools */}
                    <div className="flex items-center space-x-2">
                        <Label className="text-sm font-medium">Drawing:</Label>
                        <Select value={drawingMode} onValueChange={(value: any) => setDrawingMode(value)}>
                            <SelectTrigger className="w-32">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="none">None</SelectItem>
                                <SelectItem value="line">Line</SelectItem>
                                <SelectItem value="rectangle">Rectangle</SelectItem>
                                <SelectItem value="fibonacci">Fibonacci</SelectItem>
                                <SelectItem value="trend">Trend</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>
            </div>

            {/* Chart Container */}
            <div
                ref={chartRef}
                className="relative"
                style={{ height: chartState.isFullscreen ? 'calc(100vh - 200px)' : '500px' }}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
            >
                <ResponsiveContainer width="100%" height="100%">
                    {renderChart()}
                </ResponsiveContainer>

                {/* Volume Chart */}
                {chartState.showVolume && (
                    <div className="absolute bottom-0 left-0 right-0 h-20">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={processedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                <Bar dataKey="volume" fill="#6b7280" fillOpacity={0.6} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Drawings Overlay */}
                <svg className="absolute inset-0 pointer-events-none">
                    {drawings.map((drawing) => (
                        <g key={drawing.id}>
                            {drawing.type === 'line' && (
                                <line
                                    x1={drawing.start.x}
                                    y1={drawing.start.y}
                                    x2={drawing.end.x}
                                    y2={drawing.end.y}
                                    stroke={drawing.color}
                                    strokeWidth={drawing.strokeWidth}
                                />
                            )}
                            {drawing.type === 'rectangle' && (
                                <rect
                                    x={Math.min(drawing.start.x, drawing.end.x)}
                                    y={Math.min(drawing.start.y, drawing.end.y)}
                                    width={Math.abs(drawing.end.x - drawing.start.x)}
                                    height={Math.abs(drawing.end.y - drawing.start.y)}
                                    stroke={drawing.color}
                                    strokeWidth={drawing.strokeWidth}
                                    fill="none"
                                />
                            )}
                        </g>
                    ))}
                </svg>
            </div>

            {/* Chart Footer */}
            <div className="flex items-center justify-between p-4 border-t border-border">
                <div className="flex items-center space-x-4">
                    <span className="text-sm text-muted-foreground">
                        Last updated: {formatDate(new Date(), 'MMM dd, yyyy HH:mm:ss')}
                    </span>
                    {chartState.isPlaying && (
                        <span className="text-sm text-muted-foreground">
                            Playing at {chartState.playbackSpeed}x speed
                        </span>
                    )}
                </div>

                <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Export
                    </Button>
                    <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4 mr-2" />
                        Settings
                    </Button>
                </div>
            </div>
        </div>
    );
};

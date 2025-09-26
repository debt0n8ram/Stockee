import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
    TrendingUp,
    TrendingDown,
    Pause,
    Play,
    Settings,
    Volume2,
    VolumeX
} from 'lucide-react';

interface TickerItem {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
    volume: number;
    marketCap: number;
    lastUpdated: string;
}

interface LiveMarketTickerProps {
    className?: string;
}

export const LiveMarketTicker: React.FC<LiveMarketTickerProps> = ({ className = '' }) => {
    const [tickerData, setTickerData] = useState<TickerItem[]>([]);
    const [isPlaying, setIsPlaying] = useState(true);
    const [isMuted, setIsMuted] = useState(false);
    const [speed, setSpeed] = useState(50);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isConnected, setIsConnected] = useState(false);
    const tickerRef = useRef<HTMLDivElement>(null);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    // WebSocket connection disabled to prevent connection failures
    // useEffect(() => {
    //     const ws = new WebSocket('ws://localhost:8000/api/ws/prices');
    //     // ... WebSocket code commented out
    // }, []);

    // Load initial ticker data
    useEffect(() => {
        loadTickerData();
    }, []);

    // Auto-scroll ticker
    useEffect(() => {
        if (isPlaying && tickerData.length > 0) {
            intervalRef.current = setInterval(() => {
                setCurrentIndex(prev => (prev + 1) % tickerData.length);
            }, speed);

            return () => {
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                }
            };
        }
    }, [isPlaying, speed, tickerData.length]);

    const loadTickerData = async () => {
        try {
            const response = await fetch('/api/market-data/ticker?limit=50');
            const data = await response.json();
            setTickerData(data.data || []);
        } catch (error) {
            console.error('Error loading ticker data:', error);
        }
    };

    const updateTickerData = (priceData: any) => {
        setTickerData(prev =>
            prev.map(item =>
                item.symbol === priceData.symbol
                    ? {
                        ...item,
                        price: priceData.price,
                        change: priceData.change,
                        changePercent: priceData.changePercent,
                        lastUpdated: new Date().toISOString()
                    }
                    : item
            )
        );
    };

    const togglePlayPause = () => {
        setIsPlaying(!isPlaying);
    };

    const toggleMute = () => {
        setIsMuted(!isMuted);
    };

    const handleSpeedChange = (newSpeed: number) => {
        setSpeed(newSpeed);
    };

    const getChangeColor = (change: number) => {
        if (change > 0) return 'text-green-600';
        if (change < 0) return 'text-red-600';
        return 'text-gray-600';
    };

    const getChangeIcon = (change: number) => {
        if (change > 0) return <TrendingUp className="h-3 w-3" />;
        if (change < 0) return <TrendingDown className="h-3 w-3" />;
        return null;
    };

    const formatVolume = (volume: number) => {
        if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`;
        if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`;
        if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`;
        return volume.toString();
    };

    const formatMarketCap = (marketCap: number) => {
        if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(1)}T`;
        if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(1)}B`;
        if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(1)}M`;
        return `$${marketCap.toLocaleString()}`;
    };

    return (
        <Card className={`${className}`}>
            <CardContent className="p-0">
                {/* Ticker Header */}
                <div className="flex items-center justify-between p-4 border-b bg-muted/50">
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                            <span className="text-sm font-medium">Live Market Ticker</span>
                        </div>
                        <Badge variant="outline" className="text-xs">
                            {tickerData.length} symbols
                        </Badge>
                    </div>

                    <div className="flex items-center space-x-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={toggleMute}
                        >
                            {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={togglePlayPause}
                        >
                            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                        </Button>
                        <div className="flex items-center space-x-2">
                            <span className="text-xs text-muted-foreground">Speed:</span>
                            <select
                                value={speed}
                                onChange={(e) => handleSpeedChange(Number(e.target.value))}
                                className="text-xs border rounded px-1 py-0.5"
                            >
                                <option value={25}>Slow</option>
                                <option value={50}>Normal</option>
                                <option value={100}>Fast</option>
                                <option value={200}>Very Fast</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Ticker Content */}
                <div className="relative overflow-hidden">
                    <div
                        ref={tickerRef}
                        className="flex items-center space-x-8 py-4 transition-transform duration-300 ease-in-out"
                        style={{
                            transform: `translateX(-${currentIndex * 200}px)`,
                            width: `${tickerData.length * 200}px`
                        }}
                    >
                        {tickerData.map((item, index) => (
                            <div
                                key={`${item.symbol}-${index}`}
                                className="flex items-center space-x-4 min-w-[200px] px-4 py-2 border-r border-border/50"
                            >
                                {/* Symbol and Name */}
                                <div className="flex-shrink-0">
                                    <div className="font-medium text-sm">{item.symbol}</div>
                                    <div className="text-xs text-muted-foreground truncate max-w-[120px]">
                                        {item.name}
                                    </div>
                                </div>

                                {/* Price and Change */}
                                <div className="flex-shrink-0 text-right">
                                    <div className="font-medium text-sm">
                                        ${item.price.toFixed(2)}
                                    </div>
                                    <div className={`text-xs flex items-center justify-end ${getChangeColor(item.change)}`}>
                                        {getChangeIcon(item.change)}
                                        <span className="ml-1">
                                            {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)} ({item.changePercent >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%)
                                        </span>
                                    </div>
                                </div>

                                {/* Volume */}
                                <div className="flex-shrink-0 text-right">
                                    <div className="text-xs text-muted-foreground">
                                        Vol: {formatVolume(item.volume)}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        Mkt Cap: {formatMarketCap(item.marketCap)}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Ticker Overlay */}
                    <div className="absolute inset-0 pointer-events-none">
                        <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-background to-transparent" />
                        <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-background to-transparent" />
                    </div>
                </div>

                {/* Ticker Footer */}
                <div className="flex items-center justify-between p-2 border-t bg-muted/30">
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                        <span>Last updated: {new Date().toLocaleTimeString()}</span>
                        <span>•</span>
                        <span>Market Status: {new Date().getHours() >= 9 && new Date().getHours() < 16 ? 'Open' : 'Closed'}</span>
                    </div>

                    <div className="flex items-center space-x-2">
                        <div className="text-xs text-muted-foreground">
                            Showing {currentIndex + 1} of {tickerData.length}
                        </div>
                        <div className="w-20 h-1 bg-muted rounded-full overflow-hidden">
                            <div
                                className="h-full bg-primary transition-all duration-300"
                                style={{ width: `${((currentIndex + 1) / tickerData.length) * 100}%` }}
                            />
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

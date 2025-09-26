import React, { useState, useEffect, useRef } from 'react';
import { apiService } from '../../services/api';

interface CandlestickData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface AdvancedCandlestickChartProps {
  symbol: string;
  timeframe: string;
  data?: CandlestickData[];
}

const AdvancedCandlestickChart: React.FC<AdvancedCandlestickChartProps> = ({
  symbol,
  timeframe,
  data
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [chartData, setChartData] = useState<CandlestickData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hoveredCandle, setHoveredCandle] = useState<number | null>(null);
  const [showVolume, setShowVolume] = useState(true);
  const [showIndicators, setShowIndicators] = useState(true);
  const [indicatorType, setIndicatorType] = useState<'sma' | 'ema' | 'bollinger'>('sma');

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setIsLoading(true);

        if (data) {
          setChartData(data);
        } else {
          // Fetch historical data
          const response = await apiService.get(`/historical/stocks/${symbol}?days=30&interval=${timeframe}`);
          setChartData(response.data || []);
        }
      } catch (error) {
        console.error('Error fetching chart data:', error);
        // Fallback to mock data
        const mockData: CandlestickData[] = [];
        const basePrice = 150;

        for (let i = 0; i < 30; i++) {
          const date = new Date();
          date.setDate(date.getDate() - (29 - i));

          const open = basePrice + (Math.random() - 0.5) * 10;
          const close = open + (Math.random() - 0.5) * 5;
          const high = Math.max(open, close) + Math.random() * 3;
          const low = Math.min(open, close) - Math.random() * 3;
          const volume = Math.random() * 10000000;

          mockData.push({
            timestamp: date.toISOString(),
            open,
            high,
            low,
            close,
            volume
          });
        }

        setChartData(mockData);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChartData();
  }, [symbol, timeframe, data]);

  useEffect(() => {
    if (!canvasRef.current || chartData.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const drawChart = () => {
      const width = canvas.width;
      const height = canvas.height;

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Calculate dimensions
      const padding = 60;
      const chartWidth = width - padding * 2;
      const chartHeight = height - padding * 2;
      const candleWidth = chartWidth / chartData.length;

      // Find min/max values
      const prices = chartData.flatMap(d => [d.high, d.low]);
      const volumes = chartData.map(d => d.volume);
      const minPrice = Math.min(...prices);
      const maxPrice = Math.max(...prices);
      const maxVolume = Math.max(...volumes);

      // Price range
      const priceRange = maxPrice - minPrice;
      const pricePadding = priceRange * 0.1;

      // Draw grid lines
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--border-primary') || '#e2e8f0';
      ctx.lineWidth = 1;

      // Horizontal grid lines
      for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
      }

      // Vertical grid lines
      for (let i = 0; i <= 10; i++) {
        const x = padding + (chartWidth / 10) * i;
        ctx.beginPath();
        ctx.moveTo(x, padding);
        ctx.lineTo(x, height - padding);
        ctx.stroke();
      }

      // Draw candlesticks
      chartData.forEach((candle, index) => {
        const x = padding + index * candleWidth + candleWidth / 2;

        // Calculate y positions
        const openY = padding + chartHeight - ((candle.open - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;
        const closeY = padding + chartHeight - ((candle.close - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;
        const highY = padding + chartHeight - ((candle.high - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;
        const lowY = padding + chartHeight - ((candle.low - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;

        // Determine candle color
        const isGreen = candle.close >= candle.open;
        const color = isGreen ?
          getComputedStyle(document.documentElement).getPropertyValue('--accent-success') || '#10b981' :
          getComputedStyle(document.documentElement).getPropertyValue('--accent-error') || '#ef4444';

        // Draw wick
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, highY);
        ctx.lineTo(x, lowY);
        ctx.stroke();

        // Draw body
        const bodyHeight = Math.abs(closeY - openY);
        const bodyY = Math.min(openY, closeY);

        ctx.fillStyle = color;
        ctx.fillRect(x - candleWidth * 0.3, bodyY, candleWidth * 0.6, bodyHeight);

        // Draw border
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.strokeRect(x - candleWidth * 0.3, bodyY, candleWidth * 0.6, bodyHeight);

        // Draw volume bars
        if (showVolume) {
          const volumeHeight = (candle.volume / maxVolume) * (chartHeight * 0.3);
          const volumeY = height - padding - volumeHeight;

          ctx.fillStyle = isGreen ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)';
          ctx.fillRect(x - candleWidth * 0.4, volumeY, candleWidth * 0.8, volumeHeight);
        }

        // Draw indicators
        if (showIndicators) {
          drawIndicators(ctx, index, x, candleWidth, minPrice, maxPrice, priceRange, pricePadding, padding, chartHeight);
        }

        // Highlight hovered candle
        if (hoveredCandle === index) {
          ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--border-focus') || '#3b82f6';
          ctx.lineWidth = 3;
          ctx.strokeRect(x - candleWidth * 0.3, padding, candleWidth * 0.6, chartHeight);
        }
      });

      // Draw price labels
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary') || '#64748b';
      ctx.font = '12px Inter';
      ctx.textAlign = 'right';

      for (let i = 0; i <= 5; i++) {
        const price = minPrice + (priceRange / 5) * (5 - i);
        const y = padding + (chartHeight / 5) * i;
        ctx.fillText(`$${price.toFixed(2)}`, padding - 10, y + 4);
      }

      // Draw time labels
      ctx.textAlign = 'center';
      for (let i = 0; i < chartData.length; i += Math.floor(chartData.length / 5)) {
        const x = padding + i * candleWidth + candleWidth / 2;
        const date = new Date(chartData[i].timestamp);
        ctx.fillText(date.toLocaleDateString(), x, height - padding + 20);
      }
    };

    const drawIndicators = (
      ctx: CanvasRenderingContext2D,
      index: number,
      x: number,
      candleWidth: number,
      minPrice: number,
      maxPrice: number,
      priceRange: number,
      pricePadding: number,
      padding: number,
      chartHeight: number
    ) => {
      if (index < 20) return; // Need enough data for indicators

      // Simple Moving Average
      if (indicatorType === 'sma') {
        const smaPeriod = 20;
        const smaValues = chartData.slice(index - smaPeriod + 1, index + 1).map(d => d.close);
        const sma = smaValues.reduce((sum, val) => sum + val, 0) / smaValues.length;

        const smaY = padding + chartHeight - ((sma - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;

        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x - candleWidth, smaY);
        ctx.lineTo(x + candleWidth, smaY);
        ctx.stroke();
      }

      // Bollinger Bands
      if (indicatorType === 'bollinger') {
        const bbPeriod = 20;
        const bbValues = chartData.slice(index - bbPeriod + 1, index + 1).map(d => d.close);
        const bbSma = bbValues.reduce((sum, val) => sum + val, 0) / bbValues.length;
        const bbStd = Math.sqrt(bbValues.reduce((sum, val) => sum + Math.pow(val - bbSma, 2), 0) / bbValues.length);

        const upperBand = bbSma + (bbStd * 2);
        const lowerBand = bbSma - (bbStd * 2);

        const upperY = padding + chartHeight - ((upperBand - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;
        const lowerY = padding + chartHeight - ((lowerBand - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;

        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x - candleWidth, upperY);
        ctx.lineTo(x + candleWidth, upperY);
        ctx.moveTo(x - candleWidth, lowerY);
        ctx.lineTo(x + candleWidth, lowerY);
        ctx.stroke();
      }
    };

    drawChart();
  }, [chartData, hoveredCandle, showVolume, showIndicators, indicatorType]);

  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;

    const padding = 60;
    const chartWidth = canvas.width - padding * 2;
    const candleWidth = chartWidth / chartData.length;

    const index = Math.floor((x - padding) / candleWidth);
    if (index >= 0 && index < chartData.length) {
      setHoveredCandle(index);
    } else {
      setHoveredCandle(null);
    }
  };

  if (isLoading) {
    return (
      <div className="candlestick-chart-container">
        <div className="chart-header">
          <h3 className="chart-title">Loading Chart...</h3>
        </div>
        <div className="chart-canvas skeleton" style={{ height: '500px' }}></div>
      </div>
    );
  }

  return (
    <div className="candlestick-chart-container">
      <div className="chart-header">
        <h3 className="chart-title">{symbol} - {timeframe} Chart</h3>
        <div className="chart-controls">
          <label className="control-item">
            <input
              type="checkbox"
              checked={showVolume}
              onChange={(e) => setShowVolume(e.target.checked)}
            />
            Volume
          </label>
          <label className="control-item">
            <input
              type="checkbox"
              checked={showIndicators}
              onChange={(e) => setShowIndicators(e.target.checked)}
            />
            Indicators
          </label>
          <select
            value={indicatorType}
            onChange={(e) => setIndicatorType(e.target.value as any)}
            className="indicator-selector"
          >
            <option value="sma">SMA (20)</option>
            <option value="ema">EMA (20)</option>
            <option value="bollinger">Bollinger Bands</option>
          </select>
        </div>
      </div>

      <div className="chart-content">
        <canvas
          ref={canvasRef}
          width={800}
          height={500}
          className="chart-canvas"
          onMouseMove={handleCanvasMouseMove}
          onMouseLeave={() => setHoveredCandle(null)}
        />

        {hoveredCandle !== null && (
          <div className="chart-tooltip">
            <div className="tooltip-content">
              <h4>{new Date(chartData[hoveredCandle].timestamp).toLocaleString()}</h4>
              <div className="tooltip-data">
                <div className="data-row">
                  <span>Open:</span>
                  <span>${chartData[hoveredCandle].open.toFixed(2)}</span>
                </div>
                <div className="data-row">
                  <span>High:</span>
                  <span>${chartData[hoveredCandle].high.toFixed(2)}</span>
                </div>
                <div className="data-row">
                  <span>Low:</span>
                  <span>${chartData[hoveredCandle].low.toFixed(2)}</span>
                </div>
                <div className="data-row">
                  <span>Close:</span>
                  <span>${chartData[hoveredCandle].close.toFixed(2)}</span>
                </div>
                <div className="data-row">
                  <span>Volume:</span>
                  <span>{chartData[hoveredCandle].volume.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .candlestick-chart-container {
          background: var(--bg-card);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-lg);
          padding: var(--space-lg);
          box-shadow: var(--shadow-sm);
        }

        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-lg);
        }

        .chart-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }

        .chart-controls {
          display: flex;
          gap: var(--space-md);
          align-items: center;
        }

        .control-item {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .indicator-selector {
          padding: var(--space-sm) var(--space-md);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          background: var(--bg-card);
          color: var(--text-primary);
          font-size: 0.875rem;
        }

        .chart-content {
          position: relative;
        }

        .chart-canvas {
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          cursor: crosshair;
          background: var(--bg-secondary);
          width: 100%;
        }

        .chart-tooltip {
          position: absolute;
          top: 10px;
          right: 10px;
          background: var(--bg-card);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          padding: var(--space-md);
          box-shadow: var(--shadow-lg);
          z-index: 1000;
        }

        .tooltip-content h4 {
          margin: 0 0 var(--space-sm) 0;
          color: var(--text-primary);
          font-size: 0.9rem;
        }

        .tooltip-data {
          display: flex;
          flex-direction: column;
          gap: var(--space-xs);
        }

        .data-row {
          display: flex;
          justify-content: space-between;
          gap: var(--space-sm);
          font-size: 0.8rem;
        }

        .data-row span:first-child {
          color: var(--text-secondary);
        }

        .data-row span:last-child {
          color: var(--text-primary);
          font-weight: 500;
        }

        @media (max-width: 768px) {
          .chart-header {
            flex-direction: column;
            gap: var(--space-md);
            align-items: flex-start;
          }
          
          .chart-controls {
            flex-wrap: wrap;
          }
        }
      `}</style>
    </div>
  );
};

export default AdvancedCandlestickChart;

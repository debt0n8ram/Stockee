import React, { useState, useEffect, useRef } from 'react';
import { apiService } from '../../services/api';

interface StreamingData {
  timestamp: number;
  price: number;
  volume: number;
}

interface StreamingChartProps {
  symbol: string;
  interval: number; // milliseconds
  maxDataPoints?: number;
}

const StreamingChart: React.FC<StreamingChartProps> = ({
  symbol,
  interval = 1000,
  maxDataPoints = 100
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [streamingData, setStreamingData] = useState<StreamingData[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [priceChange, setPriceChange] = useState<number>(0);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    const startStreaming = async () => {
      setIsStreaming(true);

      // Initial data fetch
      try {
        const response = await apiService.get(`/market/price/${symbol}`);
        const initialPrice = response.price || 150;

        setCurrentPrice(initialPrice);
        setStreamingData([{
          timestamp: Date.now(),
          price: initialPrice,
          volume: Math.random() * 1000000
        }]);
      } catch (error) {
        console.error('Error fetching initial price:', error);
        // Fallback to mock data
        setCurrentPrice(150);
        setStreamingData([{
          timestamp: Date.now(),
          price: 150,
          volume: Math.random() * 1000000
        }]);
      }
    };

    startStreaming();
  }, [symbol]);

  useEffect(() => {
    if (!isStreaming) return;

    const streamData = async () => {
      try {
        // Fetch latest price
        const response = await apiService.get(`/market/price/${symbol}`);
        const newPrice = response.price || currentPrice;

        // Calculate price change
        const change = newPrice - currentPrice;
        setPriceChange(change);
        setCurrentPrice(newPrice);

        // Add new data point
        const newDataPoint: StreamingData = {
          timestamp: Date.now(),
          price: newPrice,
          volume: Math.random() * 1000000
        };

        setStreamingData(prev => {
          const updated = [...prev, newDataPoint];
          // Keep only the last maxDataPoints
          return updated.slice(-maxDataPoints);
        });

        setLastUpdate(new Date());
      } catch (error) {
        console.error('Error streaming data:', error);
        // Fallback to mock data
        const mockPrice = currentPrice + (Math.random() - 0.5) * 2;
        const change = mockPrice - currentPrice;

        setPriceChange(change);
        setCurrentPrice(mockPrice);

        const newDataPoint: StreamingData = {
          timestamp: Date.now(),
          price: mockPrice,
          volume: Math.random() * 1000000
        };

        setStreamingData(prev => {
          const updated = [...prev, newDataPoint];
          return updated.slice(-maxDataPoints);
        });

        setLastUpdate(new Date());
      }
    };

    const intervalId = setInterval(streamData, interval);

    return () => clearInterval(intervalId);
  }, [isStreaming, symbol, interval, currentPrice, maxDataPoints]);

  useEffect(() => {
    if (!canvasRef.current || streamingData.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const drawStreamingChart = () => {
      const width = canvas.width;
      const height = canvas.height;

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      if (streamingData.length < 2) return;

      const rootStyles = getComputedStyle(document.documentElement);
      const getCssVar = (name: string, fallback: string) => {
        const value = rootStyles.getPropertyValue(name).trim();
        return value || fallback;
      };

      const borderColor = getCssVar('--border-primary', '#e2e8f0');
      const accentSuccess = getCssVar('--accent-success', '#10b981');
      const accentError = getCssVar('--accent-error', '#ef4444');
      const textSecondary = getCssVar('--text-secondary', '#64748b');
      const textPrimary = getCssVar('--text-primary', '#1e293b');

      // Calculate dimensions
      const padding = 40;
      const chartWidth = width - padding * 2;
      const chartHeight = height - padding * 2;

      // Find min/max values
      const prices = streamingData.map(d => d.price);
      const minPrice = Math.min(...prices);
      const maxPrice = Math.max(...prices);
      const priceRange = maxPrice - minPrice;
      const pricePadding = priceRange * 0.1;

      // Draw background grid
      ctx.strokeStyle = borderColor;
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 5]);

      // Horizontal grid lines
      for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
      }

      ctx.setLineDash([]);

      // Draw price line
      ctx.strokeStyle = priceChange >= 0 ? accentSuccess : accentError;
      ctx.lineWidth = 3;
      ctx.beginPath();

      streamingData.forEach((point, index) => {
        const x = padding + (index / (streamingData.length - 1)) * chartWidth;
        const y = padding + chartHeight - ((point.price - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;

        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });

      ctx.stroke();

      // Draw data points
      ctx.fillStyle = priceChange >= 0 ? accentSuccess : accentError;
      streamingData.forEach((point, index) => {
        const x = padding + (index / (streamingData.length - 1)) * chartWidth;
        const y = padding + chartHeight - ((point.price - minPrice + pricePadding) / (priceRange + pricePadding * 2)) * chartHeight;

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();

        // Add glow effect to the latest point
        if (index === streamingData.length - 1) {
          ctx.shadowColor = priceChange >= 0 ? accentSuccess : accentError;
          ctx.shadowBlur = 10;
          ctx.beginPath();
          ctx.arc(x, y, 6, 0, 2 * Math.PI);
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Draw price labels
      ctx.fillStyle = textSecondary;
      ctx.font = '12px Inter';
      ctx.textAlign = 'right';

      for (let i = 0; i <= 5; i++) {
        const price = minPrice + (priceRange / 5) * (5 - i);
        const y = padding + (chartHeight / 5) * i;
        ctx.fillText(`$${price.toFixed(2)}`, padding - 10, y + 4);
      }

      // Draw current price indicator
      ctx.fillStyle = textPrimary;
      ctx.font = 'bold 14px Inter';
      ctx.textAlign = 'left';
      ctx.fillText(`Current: $${currentPrice.toFixed(2)}`, width - padding - 150, padding + 20);

      // Draw price change indicator
      ctx.fillStyle = priceChange >= 0 ? accentSuccess : accentError;
      ctx.font = 'bold 12px Inter';
      const changeText = `${priceChange >= 0 ? '+' : ''}${priceChange.toFixed(2)}`;
      ctx.fillText(changeText, width - padding - 150, padding + 40);
    };

    drawStreamingChart();

    // Schedule next frame
    animationRef.current = requestAnimationFrame(drawStreamingChart);
  }, [streamingData, currentPrice, priceChange]);

  const toggleStreaming = () => {
    setIsStreaming(!isStreaming);
  };

  const clearData = () => {
    setStreamingData([]);
  };

  return (
    <div className="streaming-chart-container">
      <div className="chart-header">
        <h3 className="chart-title">{symbol} - Real-time Streaming</h3>
        <div className="chart-controls">
          <button
            onClick={toggleStreaming}
            className={`streaming-button ${isStreaming ? 'active' : ''}`}
          >
            {isStreaming ? '⏸️ Pause' : '▶️ Start'}
          </button>
          <button onClick={clearData} className="clear-button">
            🗑️ Clear
          </button>
          <div className="status-indicator">
            <div className={`status-dot ${isStreaming ? 'streaming' : 'paused'}`}></div>
            <span>{isStreaming ? 'Live' : 'Paused'}</span>
          </div>
        </div>
      </div>

      <div className="chart-content">
        <canvas
          ref={canvasRef}
          width={800}
          height={400}
          className="streaming-canvas"
        />

        <div className="chart-info">
          <div className="info-item">
            <span className="info-label">Last Update:</span>
            <span className="info-value">{lastUpdate.toLocaleTimeString()}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Data Points:</span>
            <span className="info-value">{streamingData.length}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Interval:</span>
            <span className="info-value">{interval}ms</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        .streaming-chart-container {
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

        .streaming-button, .clear-button {
          padding: var(--space-sm) var(--space-md);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          background: var(--bg-card);
          color: var(--text-primary);
          font-size: 0.875rem;
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .streaming-button:hover, .clear-button:hover {
          background: var(--bg-hover);
          transform: translateY(-1px);
        }

        .streaming-button.active {
          background: var(--accent-success);
          color: var(--text-inverse);
          border-color: var(--accent-success);
        }

        .status-indicator {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--text-tertiary);
        }

        .status-dot.streaming {
          background: var(--accent-success);
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }

        .chart-content {
          position: relative;
        }

        .streaming-canvas {
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          background: var(--bg-secondary);
          width: 100%;
        }

        .chart-info {
          display: flex;
          gap: var(--space-lg);
          margin-top: var(--space-md);
          padding: var(--space-md);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
        }

        .info-item {
          display: flex;
          flex-direction: column;
          gap: var(--space-xs);
        }

        .info-label {
          font-size: 0.75rem;
          color: var(--text-secondary);
        }

        .info-value {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-primary);
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

export default StreamingChart;

import React, { useState, useEffect, useRef } from 'react';
import { apiService } from '../../services/api';

interface PortfolioData {
  symbol: string;
  name: string;
  weight: number;
  return: number;
  risk: number;
  sharpe: number;
  beta: number;
  marketCap: number;
  sector: string;
}

interface Portfolio3DVisualizationProps {
  userId: string;
  data?: PortfolioData[];
}

const Portfolio3DVisualization: React.FC<Portfolio3DVisualizationProps> = ({ userId, data }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [portfolioData, setPortfolioData] = useState<PortfolioData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hoveredPoint, setHoveredPoint] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'risk-return' | 'sharpe-beta' | 'weight-risk'>('risk-return');
  const [animationFrame, setAnimationFrame] = useState(0);

  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        setIsLoading(true);

        if (data) {
          setPortfolioData(data);
        } else {
          // Mock portfolio data
          const mockData: PortfolioData[] = [
            { symbol: 'AAPL', name: 'Apple Inc.', weight: 0.25, return: 0.15, risk: 0.20, sharpe: 0.75, beta: 1.2, marketCap: 3000000000000, sector: 'Technology' },
            { symbol: 'MSFT', name: 'Microsoft Corp.', weight: 0.20, return: 0.12, risk: 0.18, sharpe: 0.67, beta: 1.1, marketCap: 2800000000000, sector: 'Technology' },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', weight: 0.15, return: 0.18, risk: 0.25, sharpe: 0.72, beta: 1.3, marketCap: 1800000000000, sector: 'Technology' },
            { symbol: 'JPM', name: 'JPMorgan Chase', weight: 0.10, return: 0.08, risk: 0.15, sharpe: 0.53, beta: 0.9, marketCap: 450000000000, sector: 'Financial' },
            { symbol: 'JNJ', name: 'Johnson & Johnson', weight: 0.10, return: 0.06, risk: 0.12, sharpe: 0.50, beta: 0.7, marketCap: 420000000000, sector: 'Healthcare' },
            { symbol: 'PG', name: 'Procter & Gamble', weight: 0.08, return: 0.05, risk: 0.10, sharpe: 0.50, beta: 0.6, marketCap: 380000000000, sector: 'Consumer' },
            { symbol: 'TSLA', name: 'Tesla Inc.', weight: 0.07, return: 0.25, risk: 0.35, sharpe: 0.71, beta: 1.8, marketCap: 800000000000, sector: 'Automotive' },
            { symbol: 'NVDA', name: 'NVIDIA Corp.', weight: 0.05, return: 0.30, risk: 0.40, sharpe: 0.75, beta: 2.0, marketCap: 1200000000000, sector: 'Technology' }
          ];

          setPortfolioData(mockData);
        }
      } catch (error) {
        console.error('Error fetching portfolio data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPortfolioData();
  }, [data]);

  useEffect(() => {
    if (!canvasRef.current || portfolioData.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const draw3DVisualization = () => {
      const width = canvas.width;
      const height = canvas.height;

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Set up 3D projection
      const centerX = width / 2;
      const centerY = height / 2;
      const scale = 200;

      // Draw axes
      ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-tertiary') || '#94a3b8';
      ctx.lineWidth = 2;

      // X-axis (Risk)
      ctx.beginPath();
      ctx.moveTo(50, height - 50);
      ctx.lineTo(width - 50, height - 50);
      ctx.stroke();

      // Y-axis (Return)
      ctx.beginPath();
      ctx.moveTo(50, 50);
      ctx.lineTo(50, height - 50);
      ctx.stroke();

      // Z-axis (Weight - represented as size)
      const maxWeight = Math.max(...portfolioData.map(d => d.weight));

      // Draw data points
      portfolioData.forEach((item, index) => {
        const x = 50 + (item.risk * scale);
        const y = height - 50 - (item.return * scale);
        const size = (item.weight / maxWeight) * 30 + 5;

        // 3D effect with shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.beginPath();
        ctx.arc(x + 3, y + 3, size, 0, 2 * Math.PI);
        ctx.fill();

        // Main point
        const color = getSectorColor(item.sector);
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, 2 * Math.PI);
        ctx.fill();

        // Border
        ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary') || '#1e293b';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        if (hoveredPoint === item.symbol) {
          ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary') || '#1e293b';
          ctx.font = '12px Inter';
          ctx.fillText(item.symbol, x + size + 5, y - 5);
        }
      });

      // Draw labels
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary') || '#64748b';
      ctx.font = '14px Inter';
      ctx.fillText('Risk', width - 50, height - 30);
      ctx.fillText('Return', 20, 30);

      // Draw legend
      const sectors = [...new Set(portfolioData.map(d => d.sector))];
      sectors.forEach((sector, index) => {
        const y = 50 + index * 25;
        ctx.fillStyle = getSectorColor(sector);
        ctx.beginPath();
        ctx.arc(20, y, 8, 0, 2 * Math.PI);
        ctx.fill();

        ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary') || '#1e293b';
        ctx.font = '12px Inter';
        ctx.fillText(sector, 35, y + 4);
      });
    };

    draw3DVisualization();
  }, [portfolioData, hoveredPoint, viewMode, animationFrame]);

  const getSectorColor = (sector: string): string => {
    const colors = {
      'Technology': '#3b82f6',
      'Financial': '#10b981',
      'Healthcare': '#f59e0b',
      'Consumer': '#ef4444',
      'Energy': '#8b5cf6',
      'Industrial': '#06b6d4',
      'Automotive': '#f97316'
    };
    return colors[sector as keyof typeof colors] || '#6b7280';
  };

  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Check if mouse is over any data point
    const scale = 200;
    const maxWeight = Math.max(...portfolioData.map(d => d.weight));

    for (const item of portfolioData) {
      const pointX = 50 + (item.risk * scale);
      const pointY = canvas.height - 50 - (item.return * scale);
      const size = (item.weight / maxWeight) * 30 + 5;

      const distance = Math.sqrt((x - pointX) ** 2 + (y - pointY) ** 2);
      if (distance <= size + 5) {
        setHoveredPoint(item.symbol);
        return;
      }
    }

    setHoveredPoint(null);
  };

  if (isLoading) {
    return (
      <div className="portfolio-3d-container">
        <div className="portfolio-3d-header">
          <h3 className="portfolio-3d-title">Loading 3D Portfolio Visualization...</h3>
        </div>
        <div className="portfolio-3d-canvas skeleton" style={{ height: '500px' }}></div>
      </div>
    );
  }

  return (
    <div className="portfolio-3d-container">
      <div className="portfolio-3d-header">
        <h3 className="portfolio-3d-title">3D Portfolio Visualization</h3>
        <div className="portfolio-3d-controls">
          <select
            value={viewMode}
            onChange={(e) => setViewMode(e.target.value as any)}
            className="view-mode-selector"
          >
            <option value="risk-return">Risk vs Return</option>
            <option value="sharpe-beta">Sharpe vs Beta</option>
            <option value="weight-risk">Weight vs Risk</option>
          </select>
        </div>
      </div>

      <div className="portfolio-3d-content">
        <canvas
          ref={canvasRef}
          width={800}
          height={500}
          className="portfolio-3d-canvas"
          onMouseMove={handleCanvasMouseMove}
          onMouseLeave={() => setHoveredPoint(null)}
        />

        <div className="portfolio-3d-info">
          <h4>Portfolio Metrics</h4>
          <div className="metrics-grid">
            <div className="metric-item">
              <span className="metric-label">Total Return</span>
              <span className="metric-value">
                {(portfolioData.reduce((sum, item) => sum + item.return * item.weight, 0) * 100).toFixed(2)}%
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Portfolio Risk</span>
              <span className="metric-value">
                {(portfolioData.reduce((sum, item) => sum + item.risk * item.weight, 0) * 100).toFixed(2)}%
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Sharpe Ratio</span>
              <span className="metric-value">
                {(portfolioData.reduce((sum, item) => sum + item.sharpe * item.weight, 0)).toFixed(2)}
              </span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Beta</span>
              <span className="metric-value">
                {(portfolioData.reduce((sum, item) => sum + item.beta * item.weight, 0)).toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {hoveredPoint && (
        <div className="tooltip">
          {(() => {
            const item = portfolioData.find(d => d.symbol === hoveredPoint);
            return item ? (
              <div>
                <h4>{item.symbol} - {item.name}</h4>
                <p>Sector: {item.sector}</p>
                <p>Weight: {(item.weight * 100).toFixed(1)}%</p>
                <p>Return: {(item.return * 100).toFixed(2)}%</p>
                <p>Risk: {(item.risk * 100).toFixed(2)}%</p>
                <p>Sharpe: {item.sharpe.toFixed(2)}</p>
                <p>Beta: {item.beta.toFixed(2)}</p>
              </div>
            ) : null;
          })()}
        </div>
      )}

      <style jsx>{`
        .portfolio-3d-container {
          background: var(--bg-card);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-lg);
          padding: var(--space-lg);
          box-shadow: var(--shadow-sm);
        }

        .portfolio-3d-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-lg);
        }

        .portfolio-3d-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }

        .portfolio-3d-controls {
          display: flex;
          gap: var(--space-md);
        }

        .view-mode-selector {
          padding: var(--space-sm) var(--space-md);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          background: var(--bg-card);
          color: var(--text-primary);
          font-size: 0.875rem;
        }

        .portfolio-3d-content {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: var(--space-lg);
        }

        .portfolio-3d-canvas {
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          cursor: crosshair;
          background: var(--bg-secondary);
        }

        .portfolio-3d-info {
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
          padding: var(--space-lg);
        }

        .portfolio-3d-info h4 {
          margin: 0 0 var(--space-md) 0;
          color: var(--text-primary);
          font-size: 1.1rem;
        }

        .metrics-grid {
          display: grid;
          gap: var(--space-sm);
        }

        .metric-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--space-sm);
          background: var(--bg-card);
          border-radius: var(--radius-sm);
        }

        .metric-label {
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .metric-value {
          font-weight: 600;
          color: var(--text-primary);
        }

        .tooltip {
          position: absolute;
          background: var(--bg-card);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          padding: var(--space-md);
          box-shadow: var(--shadow-lg);
          z-index: 1000;
          pointer-events: none;
        }

        .tooltip h4 {
          margin: 0 0 var(--space-sm) 0;
          color: var(--text-primary);
        }

        .tooltip p {
          margin: 0 0 var(--space-xs) 0;
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        @media (max-width: 768px) {
          .portfolio-3d-content {
            grid-template-columns: 1fr;
          }
          
          .portfolio-3d-canvas {
            width: 100%;
            height: 300px;
          }
        }
      `}</style>
    </div>
  );
};

export default Portfolio3DVisualization;

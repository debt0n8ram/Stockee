import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';

interface HeatmapData {
  symbol: string;
  name: string;
  sector: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
}

interface InteractiveHeatmapProps {
  type: 'sector' | 'correlation';
  data?: HeatmapData[];
}

const InteractiveHeatmap: React.FC<InteractiveHeatmapProps> = ({ type, data }) => {
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hoveredCell, setHoveredCell] = useState<string | null>(null);
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

  useEffect(() => {
    const fetchHeatmapData = async () => {
      try {
        setIsLoading(true);
        
        if (data) {
          setHeatmapData(data);
        } else {
          // Fetch sector performance data
          const sectors = ['Technology', 'Healthcare', 'Financial', 'Consumer', 'Energy', 'Industrial'];
          const mockData: HeatmapData[] = [];
          
          sectors.forEach(sector => {
            for (let i = 0; i < 5; i++) {
              const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'PG'];
              const symbol = symbols[Math.floor(Math.random() * symbols.length)];
              
              mockData.push({
                symbol,
                name: `${symbol} Inc.`,
                sector,
                price: Math.random() * 500 + 50,
                change: (Math.random() - 0.5) * 20,
                changePercent: (Math.random() - 0.5) * 10,
                volume: Math.random() * 10000000,
                marketCap: Math.random() * 1000000000
              });
            }
          });
          
          setHeatmapData(mockData);
        }
      } catch (error) {
        console.error('Error fetching heatmap data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHeatmapData();
  }, [data]);

  const getColorIntensity = (value: number, type: 'change' | 'volume' | 'marketCap') => {
    if (type === 'change') {
      const maxChange = Math.max(...heatmapData.map(d => Math.abs(d.changePercent)));
      const intensity = Math.abs(value) / maxChange;
      return value >= 0 ? `rgba(16, 185, 129, ${intensity})` : `rgba(239, 68, 68, ${intensity})`;
    }
    if (type === 'volume') {
      const maxVolume = Math.max(...heatmapData.map(d => d.volume));
      const intensity = value / maxVolume;
      return `rgba(59, 130, 246, ${intensity})`;
    }
    if (type === 'marketCap') {
      const maxMarketCap = Math.max(...heatmapData.map(d => d.marketCap));
      const intensity = value / maxMarketCap;
      return `rgba(139, 92, 246, ${intensity})`;
    }
    return 'rgba(156, 163, 175, 0.3)';
  };

  const formatValue = (value: number, type: string) => {
    if (type === 'price') return `$${value.toFixed(2)}`;
    if (type === 'change') return `${value >= 0 ? '+' : ''}${value.toFixed(2)}`;
    if (type === 'changePercent') return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
    if (type === 'volume') return value > 1000000 ? `${(value / 1000000).toFixed(1)}M` : `${(value / 1000).toFixed(1)}K`;
    if (type === 'marketCap') return value > 1000000000 ? `${(value / 1000000000).toFixed(1)}B` : `${(value / 1000000).toFixed(1)}M`;
    return value.toString();
  };

  const sectors = [...new Set(heatmapData.map(d => d.sector))];

  if (isLoading) {
    return (
      <div className="heatmap-container">
        <div className="heatmap-header">
          <h3 className="heatmap-title">Loading Heatmap...</h3>
        </div>
        <div className="heatmap-grid skeleton" style={{ height: '400px' }}></div>
      </div>
    );
  }

  return (
    <div className="heatmap-container">
      <div className="heatmap-header">
        <h3 className="heatmap-title">
          {type === 'sector' ? 'Sector Performance Heatmap' : 'Correlation Matrix'}
        </h3>
        <div className="heatmap-controls">
          <select 
            value={selectedSector || ''} 
            onChange={(e) => setSelectedSector(e.target.value || null)}
            className="heatmap-filter"
          >
            <option value="">All Sectors</option>
            {sectors.map(sector => (
              <option key={sector} value={sector}>{sector}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="heatmap-grid">
        {heatmapData
          .filter(d => !selectedSector || d.sector === selectedSector)
          .map((item, index) => (
            <div
              key={`${item.symbol}-${index}`}
              className={`heatmap-cell ${hoveredCell === item.symbol ? 'hovered' : ''}`}
              style={{
                backgroundColor: getColorIntensity(item.changePercent, 'change'),
                gridColumn: `span 1`,
                gridRow: `span 1`
              }}
              onMouseEnter={() => setHoveredCell(item.symbol)}
              onMouseLeave={() => setHoveredCell(null)}
            >
              <div className="cell-content">
                <div className="cell-symbol">{item.symbol}</div>
                <div className="cell-price">{formatValue(item.price, 'price')}</div>
                <div className={`cell-change ${item.changePercent >= 0 ? 'positive' : 'negative'}`}>
                  {formatValue(item.changePercent, 'changePercent')}
                </div>
                <div className="cell-volume">Vol: {formatValue(item.volume, 'volume')}</div>
              </div>
            </div>
          ))}
      </div>

      <div className="heatmap-legend">
        <div className="legend-item">
          <div className="legend-color positive"></div>
          <span>Positive Performance</span>
        </div>
        <div className="legend-item">
          <div className="legend-color negative"></div>
          <span>Negative Performance</span>
        </div>
        <div className="legend-item">
          <div className="legend-color neutral"></div>
          <span>Neutral Performance</span>
        </div>
      </div>

      <style jsx>{`
        .heatmap-container {
          background: var(--bg-card);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-lg);
          padding: var(--space-lg);
          box-shadow: var(--shadow-sm);
        }

        .heatmap-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-lg);
        }

        .heatmap-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }

        .heatmap-controls {
          display: flex;
          gap: var(--space-md);
        }

        .heatmap-filter {
          padding: var(--space-sm) var(--space-md);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          background: var(--bg-card);
          color: var(--text-primary);
          font-size: 0.875rem;
        }

        .heatmap-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: var(--space-sm);
          margin-bottom: var(--space-lg);
        }

        .heatmap-cell {
          border-radius: var(--radius-md);
          padding: var(--space-sm);
          cursor: pointer;
          transition: all var(--transition-fast);
          border: 2px solid transparent;
          position: relative;
          overflow: hidden;
        }

        .heatmap-cell:hover {
          transform: scale(1.05);
          box-shadow: var(--shadow-lg);
          border-color: var(--border-focus);
          z-index: 10;
        }

        .heatmap-cell.hovered {
          transform: scale(1.05);
          box-shadow: var(--shadow-lg);
        }

        .cell-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          color: var(--text-primary);
          font-size: 0.75rem;
        }

        .cell-symbol {
          font-weight: 600;
          font-size: 0.8rem;
          margin-bottom: var(--space-xs);
        }

        .cell-price {
          font-weight: 700;
          font-size: 0.9rem;
          margin-bottom: var(--space-xs);
        }

        .cell-change {
          font-weight: 500;
          font-size: 0.8rem;
          margin-bottom: var(--space-xs);
        }

        .cell-change.positive {
          color: var(--accent-success);
        }

        .cell-change.negative {
          color: var(--accent-error);
        }

        .cell-volume {
          font-size: 0.7rem;
          opacity: 0.8;
        }

        .heatmap-legend {
          display: flex;
          gap: var(--space-lg);
          justify-content: center;
          flex-wrap: wrap;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .legend-color {
          width: 16px;
          height: 16px;
          border-radius: var(--radius-sm);
        }

        .legend-color.positive {
          background: var(--accent-success);
        }

        .legend-color.negative {
          background: var(--accent-error);
        }

        .legend-color.neutral {
          background: var(--text-tertiary);
        }

        @media (max-width: 768px) {
          .heatmap-grid {
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
          }
          
          .heatmap-header {
            flex-direction: column;
            gap: var(--space-md);
            align-items: flex-start;
          }
        }
      `}</style>
    </div>
  );
};

export default InteractiveHeatmap;

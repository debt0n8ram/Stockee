import React, { useState } from 'react';
import InteractiveHeatmap from '../components/visualizations/InteractiveHeatmap';
import Portfolio3DVisualization from '../components/visualizations/Portfolio3DVisualization';
import AdvancedCandlestickChart from '../components/visualizations/AdvancedCandlestickChart';
import StreamingChart from '../components/visualizations/StreamingChart';
import CustomizableWatchlist from '../components/CustomizableWatchlist';
import { BarChart3, TrendingUp, Eye, Layers, Zap } from 'lucide-react';

const DataVisualization: React.FC = () => {
  const [activeTab, setActiveTab] = useState('heatmap');
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');

  const tabs = [
    { id: 'heatmap', label: 'Interactive Heatmaps', icon: BarChart3 },
    { id: 'portfolio', label: '3D Portfolio', icon: Layers },
    { id: 'candlestick', label: 'Advanced Charts', icon: TrendingUp },
    { id: 'streaming', label: 'Real-time Streaming', icon: Zap },
    { id: 'watchlist', label: 'Customizable Watchlists', icon: Eye }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'heatmap':
        return (
          <div className="visualization-content">
            <div className="content-section">
              <h3>Sector Performance Heatmap</h3>
              <p className="section-description">
                Interactive heatmap showing sector performance with color-coded intensity.
                Hover over cells to see detailed information.
              </p>
              <InteractiveHeatmap type="sector" />
            </div>

            <div className="content-section">
              <h3>Correlation Matrix</h3>
              <p className="section-description">
                Visualize correlations between different assets and sectors.
              </p>
              <InteractiveHeatmap type="correlation" />
            </div>
          </div>
        );

      case 'portfolio':
        return (
          <div className="visualization-content">
            <div className="content-section">
              <h3>3D Portfolio Visualization</h3>
              <p className="section-description">
                Interactive 3D scatter plot showing risk vs return with portfolio weights.
                Each point represents a stock, sized by weight and colored by sector.
              </p>
              <Portfolio3DVisualization userId="demo-user" />
            </div>
          </div>
        );

      case 'candlestick':
        return (
          <div className="visualization-content">
            <div className="content-section">
              <h3>Advanced Candlestick Charts</h3>
              <p className="section-description">
                Professional candlestick charts with technical indicators, volume analysis,
                and interactive tooltips.
              </p>
              <div className="chart-controls">
                <select
                  value={selectedSymbol}
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                  className="symbol-selector"
                >
                  <option value="AAPL">Apple (AAPL)</option>
                  <option value="MSFT">Microsoft (MSFT)</option>
                  <option value="GOOGL">Google (GOOGL)</option>
                  <option value="AMZN">Amazon (AMZN)</option>
                  <option value="TSLA">Tesla (TSLA)</option>
                </select>
              </div>
              <AdvancedCandlestickChart symbol={selectedSymbol} timeframe="1d" />
            </div>
          </div>
        );

      case 'streaming':
        return (
          <div className="visualization-content">
            <div className="content-section">
              <h3>Real-time Streaming Charts</h3>
              <p className="section-description">
                Live price updates with smooth animations and real-time data streaming.
                Watch prices update in real-time with customizable intervals.
              </p>
              <div className="streaming-controls">
                <select
                  value={selectedSymbol}
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                  className="symbol-selector"
                >
                  <option value="AAPL">Apple (AAPL)</option>
                  <option value="MSFT">Microsoft (MSFT)</option>
                  <option value="GOOGL">Google (GOOGL)</option>
                  <option value="AMZN">Amazon (AMZN)</option>
                  <option value="TSLA">Tesla (TSLA)</option>
                </select>
              </div>
              <StreamingChart symbol={selectedSymbol} interval={2000} />
            </div>
          </div>
        );

      case 'watchlist':
        return (
          <div className="visualization-content">
            <div className="content-section">
              <h3>Customizable Watchlists</h3>
              <p className="section-description">
                Create multiple watchlists, drag and drop to reorder stocks,
                and customize visibility. Perfect for tracking different strategies.
              </p>
              <CustomizableWatchlist />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="data-visualization-page">
      <div className="page-header">
        <h1 className="page-title">Advanced Data Visualizations</h1>
        <p className="page-description">
          Interactive charts, heatmaps, and real-time data visualizations
          to help you make informed trading decisions.
        </p>
      </div>

      <div className="visualization-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
          >
            <tab.icon size={20} />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {renderContent()}

      <style jsx>{`
        .data-visualization-page {
          max-width: 1400px;
          margin: 0 auto;
          padding: var(--space-lg);
        }

        .page-header {
          text-align: center;
          margin-bottom: var(--space-2xl);
        }

        .page-title {
          font-size: 2.5rem;
          font-weight: 700;
          color: var(--text-primary);
          margin: 0 0 var(--space-md) 0;
          background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .page-description {
          font-size: 1.1rem;
          color: var(--text-secondary);
          margin: 0;
          max-width: 600px;
          margin: 0 auto;
        }

        .visualization-tabs {
          display: flex;
          gap: var(--space-sm);
          margin-bottom: var(--space-2xl);
          border-bottom: 1px solid var(--border-primary);
          overflow-x: auto;
        }

        .tab-button {
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          padding: var(--space-md) var(--space-lg);
          border: none;
          background: none;
          color: var(--text-secondary);
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all var(--transition-fast);
          white-space: nowrap;
          font-size: 0.9rem;
          font-weight: 500;
        }

        .tab-button:hover {
          color: var(--text-primary);
          background: var(--bg-hover);
        }

        .tab-button.active {
          color: var(--accent-primary);
          border-bottom-color: var(--accent-primary);
          background: var(--bg-hover);
        }

        .visualization-content {
          min-height: 600px;
        }

        .content-section {
          margin-bottom: var(--space-2xl);
        }

        .content-section h3 {
          font-size: 1.5rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 var(--space-md) 0;
        }

        .section-description {
          font-size: 1rem;
          color: var(--text-secondary);
          margin: 0 0 var(--space-lg) 0;
          line-height: 1.6;
        }

        .chart-controls, .streaming-controls {
          display: flex;
          gap: var(--space-md);
          margin-bottom: var(--space-lg);
          align-items: center;
        }

        .symbol-selector {
          padding: var(--space-sm) var(--space-md);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          background: var(--bg-card);
          color: var(--text-primary);
          font-size: 0.875rem;
          min-width: 200px;
        }

        .symbol-selector:focus {
          outline: none;
          border-color: var(--border-focus);
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        @media (max-width: 768px) {
          .page-title {
            font-size: 2rem;
          }
          
          .visualization-tabs {
            flex-wrap: wrap;
          }
          
          .tab-button {
            flex: 1;
            min-width: 120px;
          }
        }
      `}</style>
    </div>
  );
};

export default DataVisualization;

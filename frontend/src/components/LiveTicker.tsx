import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

interface TickerItem {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  type?: string;
}

const LiveTicker: React.FC = () => {
  const [tickerData, setTickerData] = useState<TickerItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTickerData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch popular stocks
        const stockSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'SPY', 'QQQ', 'IWM'];
        const stockPromises = stockSymbols.map(async (symbol) => {
          try {
            const response = await apiService.getCurrentPrice(symbol);
            return {
              symbol,
              price: response.price || 0,
              change: response.change || 0,
              changePercent: response.changePercent || 0,
              volume: response.volume || 0,
              type: 'stock'
            };
          } catch (err) {
            console.warn(`Failed to fetch ${symbol}:`, err);
            return null;
          }
        });

        // Fetch popular crypto
        const cryptoSymbols = ['BTC', 'ETH', 'SOL', 'ADA', 'MATIC', 'AVAX', 'DOGE', 'SHIB', 'LINK', 'UNI'];
        const cryptoPromises = cryptoSymbols.map(async (symbol) => {
          try {
            const response = await apiService.getCryptoPrices(symbol);
            const priceData = response.prices?.[symbol];
            if (priceData) {
              return {
                symbol,
                price: priceData.price || 0,
                change: priceData.change_24h || 0,
                changePercent: priceData.change_24h || 0,
                volume: priceData.volume_24h || 0,
                type: 'crypto'
              };
            }
            return null;
          } catch (err) {
            console.warn(`Failed to fetch ${symbol}:`, err);
            return null;
          }
        });

        const [stockResults, cryptoResults] = await Promise.all([
          Promise.all(stockPromises),
          Promise.all(cryptoPromises)
        ]);

        const allData = [...stockResults, ...cryptoResults]
          .filter((item): item is TickerItem & { type: string } => item !== null)
          .sort((a, b) => Math.abs(b.changePercent) - Math.abs(a.changePercent));

        setTickerData(allData);
      } catch (err) {
        setError('Failed to fetch ticker data');
        console.error('Ticker error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTickerData();

    // Update every 5 minutes instead of 30 seconds to reduce API calls
    const interval = setInterval(fetchTickerData, 300000);

    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price: number, type: string) => {
    if (type === 'crypto') {
      return price < 1 ? `$${price.toFixed(6)}` : `$${price.toFixed(2)}`;
    }
    return `$${price.toFixed(2)}`;
  };

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}`;
  };

  const formatChangePercent = (changePercent: number) => {
    const sign = changePercent >= 0 ? '+' : '';
    return `${sign}${changePercent.toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <div className="live-ticker">
        <div className="ticker-container">
          <div className="ticker-content skeleton" style={{ height: '60px' }}></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="live-ticker">
        <div className="ticker-container">
          <div className="ticker-error">
            <span>⚠️ {error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="live-ticker">
      <div className="ticker-header">
        <div className="ticker-label">
          <span className="live-indicator"></span>
          Live Market Ticker
        </div>
        <div className="ticker-stats">
          {tickerData.length} Assets • Updated {new Date().toLocaleTimeString()}
        </div>
      </div>

      <div className="ticker-container">
        <div className="ticker-content">
          {tickerData.map((item, index) => (
            <div
              key={`${item.symbol}-${index}`}
              className={`ticker-item ${item.type} fade-in`}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="ticker-symbol">
                <span className="symbol-text">{item.symbol}</span>
                <span className="asset-type">{item.type === 'crypto' ? '₿' : '📈'}</span>
              </div>

              <div className="ticker-price">
                {formatPrice(item.price, item.type)}
              </div>

              <div className={`ticker-change ${item.change >= 0 ? 'positive' : 'negative'}`}>
                <span className="change-value">{formatChange(item.change)}</span>
                <span className="change-percent">{formatChangePercent(item.changePercent)}</span>
              </div>

              <div className="ticker-volume">
                Vol: {item.volume > 1000000000
                  ? `${(item.volume / 1000000000).toFixed(1)}B`
                  : item.volume > 1000000
                    ? `${(item.volume / 1000000).toFixed(1)}M`
                    : `${(item.volume / 1000).toFixed(1)}K`
                }
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .live-ticker {
          background: var(--bg-card);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-lg);
          overflow: hidden;
          box-shadow: var(--shadow-sm);
          margin-bottom: var(--space-lg);
        }
        
        .ticker-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--space-sm) var(--space-md);
          background: var(--bg-secondary);
          border-bottom: 1px solid var(--border-primary);
        }
        
        .ticker-label {
          display: flex;
          align-items: center;
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .live-indicator {
          width: 8px;
          height: 8px;
          background: var(--accent-success);
          border-radius: 50%;
          margin-right: var(--space-sm);
          animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
        
        .ticker-stats {
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
        
        .ticker-container {
          overflow-x: auto;
          scrollbar-width: thin;
        }
        
        .ticker-content {
          display: flex;
          gap: var(--space-lg);
          padding: var(--space-md);
          animation: scroll 60s linear infinite;
        }
        
        @keyframes scroll {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
        
        .ticker-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          min-width: 120px;
          padding: var(--space-sm);
          border-radius: var(--radius-md);
          background: var(--bg-tertiary);
          transition: all var(--transition-fast);
          cursor: pointer;
        }
        
        .ticker-item:hover {
          background: var(--bg-hover);
          transform: translateY(-2px);
          box-shadow: var(--shadow-md);
        }
        
        .ticker-symbol {
          display: flex;
          align-items: center;
          gap: var(--space-xs);
          margin-bottom: var(--space-xs);
        }
        
        .symbol-text {
          font-weight: 600;
          color: var(--text-primary);
        }
        
        .asset-type {
          font-size: 0.75rem;
          opacity: 0.7;
        }
        
        .ticker-price {
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--text-primary);
          margin-bottom: var(--space-xs);
        }
        
        .ticker-change {
          display: flex;
          flex-direction: column;
          align-items: center;
          font-size: 0.8rem;
          font-weight: 500;
        }
        
        .ticker-change.positive {
          color: var(--accent-success);
        }
        
        .ticker-change.negative {
          color: var(--accent-error);
        }
        
        .change-value {
          font-size: 0.9rem;
        }
        
        .change-percent {
          font-size: 0.75rem;
          opacity: 0.8;
        }
        
        .ticker-volume {
          font-size: 0.7rem;
          color: var(--text-tertiary);
          margin-top: var(--space-xs);
        }
        
        .ticker-error {
          padding: var(--space-md);
          text-align: center;
          color: var(--accent-error);
          background: var(--bg-tertiary);
        }
        
        @media (max-width: 768px) {
          .ticker-item {
            min-width: 100px;
          }
          
          .ticker-price {
            font-size: 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default LiveTicker;

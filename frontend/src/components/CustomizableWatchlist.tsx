import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { apiService } from '../services/api';
import { X, Plus, Edit3, Trash2, Eye, EyeOff } from 'lucide-react';

interface WatchlistItem {
  id: string;
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  sector: string;
  isVisible: boolean;
}

interface Watchlist {
  id: string;
  name: string;
  items: WatchlistItem[];
  isDefault: boolean;
}

const CustomizableWatchlist: React.FC = () => {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [activeWatchlist, setActiveWatchlist] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSymbol, setNewSymbol] = useState('');
  const [editingItem, setEditingItem] = useState<string | null>(null);

  useEffect(() => {
    const initializeWatchlists = () => {
      // Create default watchlist
      const defaultWatchlist: Watchlist = {
        id: 'default',
        name: 'My Watchlist',
        items: [],
        isDefault: true
      };
      
      setWatchlists([defaultWatchlist]);
      setActiveWatchlist('default');
      setIsLoading(false);
    };

    initializeWatchlists();
  }, []);

  const fetchStockData = async (symbol: string): Promise<WatchlistItem | null> => {
    try {
      const response = await apiService.get(`/market/price/${symbol}`);
      
      return {
        id: `${symbol}-${Date.now()}`,
        symbol: symbol.toUpperCase(),
        name: `${symbol} Inc.`, // This would come from the API
        price: response.price || 0,
        change: response.change || 0,
        changePercent: response.changePercent || 0,
        volume: response.volume || 0,
        marketCap: response.marketCap || 0,
        sector: 'Technology', // This would come from the API
        isVisible: true
      };
    } catch (error) {
      console.error(`Error fetching data for ${symbol}:`, error);
      return null;
    }
  };

  const addToWatchlist = async () => {
    if (!newSymbol.trim()) return;

    const stockData = await fetchStockData(newSymbol.trim());
    if (!stockData) {
      alert('Failed to fetch stock data. Please check the symbol.');
      return;
    }

    setWatchlists(prev => prev.map(watchlist => {
      if (watchlist.id === activeWatchlist) {
        return {
          ...watchlist,
          items: [...watchlist.items, stockData]
        };
      }
      return watchlist;
    }));

    setNewSymbol('');
    setShowAddForm(false);
  };

  const removeFromWatchlist = (itemId: string) => {
    setWatchlists(prev => prev.map(watchlist => {
      if (watchlist.id === activeWatchlist) {
        return {
          ...watchlist,
          items: watchlist.items.filter(item => item.id !== itemId)
        };
      }
      return watchlist;
    }));
  };

  const toggleVisibility = (itemId: string) => {
    setWatchlists(prev => prev.map(watchlist => {
      if (watchlist.id === activeWatchlist) {
        return {
          ...watchlist,
          items: watchlist.items.map(item => 
            item.id === itemId ? { ...item, isVisible: !item.isVisible } : item
          )
        };
      }
      return watchlist;
    }));
  };

  const handleDragEnd = (result: any) => {
    if (!result.destination) return;

    setWatchlists(prev => prev.map(watchlist => {
      if (watchlist.id === activeWatchlist) {
        const items = Array.from(watchlist.items);
        const [reorderedItem] = items.splice(result.source.index, 1);
        items.splice(result.destination.index, 0, reorderedItem);

        return {
          ...watchlist,
          items
        };
      }
      return watchlist;
    }));
  };

  const createNewWatchlist = () => {
    const newWatchlist: Watchlist = {
      id: `watchlist-${Date.now()}`,
      name: `Watchlist ${watchlists.length + 1}`,
      items: [],
      isDefault: false
    };

    setWatchlists(prev => [...prev, newWatchlist]);
    setActiveWatchlist(newWatchlist.id);
  };

  const deleteWatchlist = (watchlistId: string) => {
    if (watchlists.find(w => w.id === watchlistId)?.isDefault) {
      alert('Cannot delete the default watchlist');
      return;
    }

    setWatchlists(prev => prev.filter(w => w.id !== watchlistId));
    if (activeWatchlist === watchlistId) {
      setActiveWatchlist('default');
    }
  };

  const currentWatchlist = watchlists.find(w => w.id === activeWatchlist);

  if (isLoading) {
    return (
      <div className="watchlist-container">
        <div className="watchlist-header">
          <h3 className="watchlist-title">Loading Watchlists...</h3>
        </div>
        <div className="watchlist-content skeleton" style={{ height: '400px' }}></div>
      </div>
    );
  }

  return (
    <div className="watchlist-container">
      <div className="watchlist-header">
        <h3 className="watchlist-title">Customizable Watchlists</h3>
        <div className="watchlist-actions">
          <button onClick={createNewWatchlist} className="btn btn-primary">
            <Plus size={16} />
            New Watchlist
          </button>
        </div>
      </div>

      <div className="watchlist-tabs">
        {watchlists.map(watchlist => (
          <div
            key={watchlist.id}
            className={`watchlist-tab ${activeWatchlist === watchlist.id ? 'active' : ''}`}
            onClick={() => setActiveWatchlist(watchlist.id)}
          >
            <span>{watchlist.name}</span>
            {!watchlist.isDefault && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteWatchlist(watchlist.id);
                }}
                className="delete-tab-btn"
              >
                <X size={14} />
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="watchlist-content">
        <div className="watchlist-toolbar">
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn btn-secondary"
          >
            <Plus size={16} />
            Add Stock
          </button>
        </div>

        {showAddForm && (
          <div className="add-form">
            <input
              type="text"
              placeholder="Enter stock symbol (e.g., AAPL)"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
              className="symbol-input"
              onKeyPress={(e) => e.key === 'Enter' && addToWatchlist()}
            />
            <button onClick={addToWatchlist} className="btn btn-primary">
              Add
            </button>
            <button onClick={() => setShowAddForm(false)} className="btn btn-secondary">
              Cancel
            </button>
          </div>
        )}

        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="watchlist-items">
            {(provided) => (
              <div
                {...provided.droppableProps}
                ref={provided.innerRef}
                className="watchlist-items"
              >
                {currentWatchlist?.items.map((item, index) => (
                  <Draggable key={item.id} draggableId={item.id} index={index}>
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className={`watchlist-item ${snapshot.isDragging ? 'dragging' : ''} ${!item.isVisible ? 'hidden' : ''}`}
                      >
                        <div className="item-content">
                          <div className="item-symbol">
                            <span className="symbol-text">{item.symbol}</span>
                            <span className="sector-badge">{item.sector}</span>
                          </div>
                          
                          <div className="item-price">
                            <span className="price-value">${item.price.toFixed(2)}</span>
                            <span className={`price-change ${item.changePercent >= 0 ? 'positive' : 'negative'}`}>
                              {item.changePercent >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%
                            </span>
                          </div>
                          
                          <div className="item-volume">
                            Vol: {item.volume > 1000000 
                              ? `${(item.volume / 1000000).toFixed(1)}M` 
                              : `${(item.volume / 1000).toFixed(1)}K`
                            }
                          </div>
                        </div>
                        
                        <div className="item-actions">
                          <button
                            onClick={() => toggleVisibility(item.id)}
                            className="action-btn"
                            title={item.isVisible ? 'Hide' : 'Show'}
                          >
                            {item.isVisible ? <Eye size={16} /> : <EyeOff size={16} />}
                          </button>
                          <button
                            onClick={() => removeFromWatchlist(item.id)}
                            className="action-btn delete"
                            title="Remove"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>

        {currentWatchlist?.items.length === 0 && (
          <div className="empty-watchlist">
            <p>No stocks in this watchlist yet.</p>
            <p>Click "Add Stock" to get started!</p>
          </div>
        )}
      </div>

      <style jsx>{`
        .watchlist-container {
          background: var(--bg-card);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-lg);
          padding: var(--space-lg);
          box-shadow: var(--shadow-sm);
        }

        .watchlist-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-lg);
        }

        .watchlist-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }

        .watchlist-actions {
          display: flex;
          gap: var(--space-md);
        }

        .watchlist-tabs {
          display: flex;
          gap: var(--space-sm);
          margin-bottom: var(--space-lg);
          border-bottom: 1px solid var(--border-primary);
        }

        .watchlist-tab {
          padding: var(--space-sm) var(--space-md);
          border-bottom: 2px solid transparent;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: var(--space-sm);
          transition: all var(--transition-fast);
          color: var(--text-secondary);
        }

        .watchlist-tab:hover {
          color: var(--text-primary);
          background: var(--bg-hover);
        }

        .watchlist-tab.active {
          color: var(--accent-primary);
          border-bottom-color: var(--accent-primary);
        }

        .delete-tab-btn {
          background: none;
          border: none;
          color: var(--text-tertiary);
          cursor: pointer;
          padding: 2px;
          border-radius: var(--radius-sm);
          transition: all var(--transition-fast);
        }

        .delete-tab-btn:hover {
          color: var(--accent-error);
          background: var(--bg-hover);
        }

        .watchlist-content {
          min-height: 400px;
        }

        .watchlist-toolbar {
          display: flex;
          gap: var(--space-md);
          margin-bottom: var(--space-lg);
        }

        .add-form {
          display: flex;
          gap: var(--space-md);
          margin-bottom: var(--space-lg);
          padding: var(--space-md);
          background: var(--bg-tertiary);
          border-radius: var(--radius-md);
        }

        .symbol-input {
          flex: 1;
          padding: var(--space-sm) var(--space-md);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          background: var(--bg-card);
          color: var(--text-primary);
          font-size: 0.875rem;
        }

        .symbol-input:focus {
          outline: none;
          border-color: var(--border-focus);
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .watchlist-items {
          display: flex;
          flex-direction: column;
          gap: var(--space-sm);
        }

        .watchlist-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--space-md);
          background: var(--bg-secondary);
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-md);
          transition: all var(--transition-fast);
          cursor: grab;
        }

        .watchlist-item:hover {
          background: var(--bg-hover);
          box-shadow: var(--shadow-sm);
        }

        .watchlist-item.dragging {
          transform: rotate(5deg);
          box-shadow: var(--shadow-lg);
        }

        .watchlist-item.hidden {
          opacity: 0.5;
          background: var(--bg-tertiary);
        }

        .item-content {
          display: flex;
          align-items: center;
          gap: var(--space-lg);
          flex: 1;
        }

        .item-symbol {
          display: flex;
          flex-direction: column;
          gap: var(--space-xs);
          min-width: 120px;
        }

        .symbol-text {
          font-weight: 600;
          font-size: 1rem;
          color: var(--text-primary);
        }

        .sector-badge {
          font-size: 0.75rem;
          color: var(--text-tertiary);
          background: var(--bg-tertiary);
          padding: 2px 6px;
          border-radius: var(--radius-sm);
          width: fit-content;
        }

        .item-price {
          display: flex;
          flex-direction: column;
          gap: var(--space-xs);
          min-width: 100px;
        }

        .price-value {
          font-weight: 700;
          font-size: 1.1rem;
          color: var(--text-primary);
        }

        .price-change {
          font-size: 0.875rem;
          font-weight: 500;
        }

        .price-change.positive {
          color: var(--accent-success);
        }

        .price-change.negative {
          color: var(--accent-error);
        }

        .item-volume {
          font-size: 0.875rem;
          color: var(--text-secondary);
          min-width: 80px;
        }

        .item-actions {
          display: flex;
          gap: var(--space-sm);
        }

        .action-btn {
          background: none;
          border: 1px solid var(--border-primary);
          border-radius: var(--radius-sm);
          padding: var(--space-xs);
          cursor: pointer;
          color: var(--text-secondary);
          transition: all var(--transition-fast);
        }

        .action-btn:hover {
          background: var(--bg-hover);
          color: var(--text-primary);
        }

        .action-btn.delete:hover {
          color: var(--accent-error);
          border-color: var(--accent-error);
        }

        .empty-watchlist {
          text-align: center;
          padding: var(--space-2xl);
          color: var(--text-secondary);
        }

        .empty-watchlist p {
          margin: 0 0 var(--space-sm) 0;
        }

        @media (max-width: 768px) {
          .item-content {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--space-sm);
          }
          
          .add-form {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default CustomizableWatchlist;

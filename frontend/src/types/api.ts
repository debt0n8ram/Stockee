// API Response Types
export interface Portfolio {
    id: number;
    user_id: string;
    cash_balance: number;
    total_value: number;
    created_at: string;
    updated_at: string;
}

export interface Holding {
    id: number;
    portfolio_id: number;
    asset_id: number;
    quantity: number;
    average_cost: number;
    current_value: number;
    unrealized_pnl: number;
    created_at: string;
    updated_at: string;
    asset?: Asset;
}

export interface Transaction {
    id: number;
    portfolio_id: number;
    asset_id: number;
    transaction_type: 'buy' | 'sell';
    quantity: number;
    price: number;
    total_amount: number;
    timestamp: string;
    asset?: Asset;
}

export interface Asset {
    id: number;
    symbol: string;
    name: string;
    asset_type: string;
    exchange: string;
    currency: string;
    sector: string;
    market_cap: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface Performance {
    total_return: number;
    daily_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    volatility: number;
    beta: number;
}

export interface MarketOverview {
    market_overview: {
        total_stocks: number;
        total_volume: number;
        advancing_stocks: number;
        declining_stocks: number;
        unchanged_stocks: number;
    };
}

export interface TopGainers {
    gainers: Array<{
        symbol: string;
        name: string;
        price: number;
        change: number;
        change_percent: number;
        volume: number;
    }>;
}

export interface TopLosers {
    losers: Array<{
        symbol: string;
        name: string;
        price: number;
        change: number;
        change_percent: number;
        volume: number;
    }>;
}

export interface MostActive {
    most_active: Array<{
        symbol: string;
        name: string;
        price: number;
        change: number;
        change_percent: number;
        volume: number;
    }>;
}

export interface SectorPerformance {
    sector_performance: Array<{
        sector: string;
        stocks: number;
        avg_change: number;
        market_cap: number;
    }>;
}

export interface ScreenedStocks {
    results: Array<{
        symbol: string;
        name: string;
        price: number;
        change: number;
        change_percent: number;
        volume: number;
        market_cap: number;
        sector: string;
        exchange: string;
    }>;
    count: number;
}

export interface AIOpponent {
    id: number;
    user_id: string;
    ai_user_id: string;
    strategy_type: string;
    start_date: string;
    end_date?: string;
    is_active: boolean;
    total_trades: number;
    winning_trades: number;
    created_at: string;
    updated_at: string;
}

export interface PortfolioAllocation {
    allocation: {
        cash: {
            value: number;
            percentage: number;
        };
        stocks: Array<{
            symbol: string;
            name: string;
            value: number;
            percentage: number;
            quantity: number;
        }>;
        crypto: Array<{
            symbol: string;
            name: string;
            value: number;
            percentage: number;
            quantity: number;
        }>;
        other: Array<{
            symbol: string;
            name: string;
            value: number;
            percentage: number;
            quantity: number;
        }>;
    };
    total_value: number;
    cash_percentage: number;
}

export interface BankTransactions {
    transactions: Array<{
        id: number;
        user_id: string;
        transaction_type: 'deposit' | 'withdrawal';
        amount: number;
        description: string;
        balance_after: number;
        timestamp: string;
    }>;
}

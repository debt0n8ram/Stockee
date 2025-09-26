-- Initialize Stockee database
-- This script runs when the PostgreSQL container starts for the first time

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create custom types
DO $$ BEGIN
    CREATE TYPE order_status AS ENUM ('pending', 'filled', 'cancelled', 'rejected');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE order_type AS ENUM ('market', 'limit', 'stop_loss', 'take_profit', 'trailing_stop');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE order_side AS ENUM ('buy', 'sell');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE asset_type AS ENUM ('stock', 'crypto', 'etf', 'option');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_prices_symbol_timestamp ON prices (symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_prices_timestamp ON prices (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions (user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions (symbol);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_holdings_user_id ON holdings (user_id);
CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON holdings (symbol);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist (user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_symbol ON watchlist (symbol);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_symbol ON price_alerts (symbol);
CREATE INDEX IF NOT EXISTS idx_technical_alerts_user_id ON technical_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_technical_alerts_symbol ON technical_alerts (symbol);
CREATE INDEX IF NOT EXISTS idx_volume_alerts_user_id ON volume_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_volume_alerts_symbol ON volume_alerts (symbol);
CREATE INDEX IF NOT EXISTS idx_news_alerts_user_id ON news_alerts (user_id);
CREATE INDEX IF NOT EXISTS idx_news_alerts_symbol ON news_alerts (symbol);
CREATE INDEX IF NOT EXISTS idx_alert_history_user_id ON alert_history (user_id);
CREATE INDEX IF NOT EXISTS idx_alert_history_timestamp ON alert_history (triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_advanced_orders_user_id ON advanced_orders (user_id);
CREATE INDEX IF NOT EXISTS idx_advanced_orders_symbol ON advanced_orders (symbol);
CREATE INDEX IF NOT EXISTS idx_advanced_orders_status ON advanced_orders (order_status);
CREATE INDEX IF NOT EXISTS idx_ml_models_user_id ON ml_models (user_id);
CREATE INDEX IF NOT EXISTS idx_ml_models_symbol ON ml_models (symbol);
CREATE INDEX IF NOT EXISTS idx_ml_models_type ON ml_models (model_type);
CREATE INDEX IF NOT EXISTS idx_social_posts_user_id ON social_posts (user_id);
CREATE INDEX IF NOT EXISTS idx_social_posts_symbol ON social_posts (symbol);
CREATE INDEX IF NOT EXISTS idx_social_posts_created_at ON social_posts (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_likes_post_id ON social_likes (post_id);
CREATE INDEX IF NOT EXISTS idx_social_likes_user_id ON social_likes (user_id);
CREATE INDEX IF NOT EXISTS idx_social_comments_post_id ON social_comments (post_id);
CREATE INDEX IF NOT EXISTS idx_social_comments_user_id ON social_comments (user_id);
CREATE INDEX IF NOT EXISTS idx_social_follows_follower_id ON social_follows (follower_id);
CREATE INDEX IF NOT EXISTS idx_social_follows_following_id ON social_follows (following_id);
CREATE INDEX IF NOT EXISTS idx_social_shares_post_id ON social_shares (post_id);
CREATE INDEX IF NOT EXISTS idx_social_shares_user_id ON social_shares (user_id);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_prices_symbol_timestamp_composite ON prices (symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_user_symbol ON transactions (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_transactions_user_timestamp ON transactions (user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_holdings_user_symbol ON holdings (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_symbol ON watchlist (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_symbol ON price_alerts (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_technical_alerts_user_symbol ON technical_alerts (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_volume_alerts_user_symbol ON volume_alerts (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_news_alerts_user_symbol ON news_alerts (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_alert_history_user_timestamp ON alert_history (user_id, triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_advanced_orders_user_symbol ON advanced_orders (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_ml_models_user_symbol ON ml_models (user_id, symbol);
CREATE INDEX IF NOT EXISTS idx_social_posts_user_created ON social_posts (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_posts_symbol_created ON social_posts (symbol, created_at DESC);

-- Create partial indexes for active records
CREATE INDEX IF NOT EXISTS idx_price_alerts_active ON price_alerts (user_id, symbol) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_technical_alerts_active ON technical_alerts (user_id, symbol) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_volume_alerts_active ON volume_alerts (user_id, symbol) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_news_alerts_active ON news_alerts (user_id, symbol) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_advanced_orders_active ON advanced_orders (user_id, symbol) WHERE order_status = 'pending';
CREATE INDEX IF NOT EXISTS idx_ml_models_active ON ml_models (user_id, symbol) WHERE is_active = true;

-- Create TimescaleDB hypertables for time-series data
SELECT create_hypertable('prices', 'timestamp', if_not_exists => TRUE);
SELECT create_hypertable('alert_history', 'triggered_at', if_not_exists => TRUE);

-- Create continuous aggregates for better performance
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_prices
WITH (timescaledb.continuous) AS
SELECT 
    symbol,
    time_bucket('1 day', timestamp) AS day,
    first(open, timestamp) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, timestamp) AS close,
    sum(volume) AS volume
FROM prices
GROUP BY symbol, day;

-- Create retention policy for old data
SELECT add_retention_policy('prices', INTERVAL '2 years', if_not_exists => TRUE);
SELECT add_retention_policy('alert_history', INTERVAL '1 year', if_not_exists => TRUE);

-- Create compression policy for old data
SELECT add_compression_policy('prices', INTERVAL '7 days', if_not_exists => TRUE);

-- Create functions for common operations
CREATE OR REPLACE FUNCTION get_portfolio_value(user_id_param TEXT)
RETURNS DECIMAL AS $$
DECLARE
    total_value DECIMAL;
BEGIN
    SELECT COALESCE(SUM(h.quantity * p.close), 0)
    INTO total_value
    FROM holdings h
    JOIN LATERAL (
        SELECT close
        FROM prices
        WHERE symbol = h.symbol
        ORDER BY timestamp DESC
        LIMIT 1
    ) p ON true
    WHERE h.user_id = user_id_param;
    
    RETURN total_value;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_daily_change(user_id_param TEXT)
RETURNS DECIMAL AS $$
DECLARE
    current_value DECIMAL;
    previous_value DECIMAL;
BEGIN
    -- Get current portfolio value
    SELECT get_portfolio_value(user_id_param) INTO current_value;
    
    -- Get previous day's portfolio value
    SELECT COALESCE(SUM(h.quantity * p.close), 0)
    INTO previous_value
    FROM holdings h
    JOIN LATERAL (
        SELECT close
        FROM prices
        WHERE symbol = h.symbol
        AND timestamp < CURRENT_DATE
        ORDER BY timestamp DESC
        LIMIT 1
    ) p ON true
    WHERE h.user_id = user_id_param;
    
    RETURN current_value - previous_value;
END;
$$ LANGUAGE plpgsql;

-- Create views for common queries
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT 
    h.user_id,
    h.symbol,
    h.quantity,
    h.average_price,
    p.close AS current_price,
    h.quantity * p.close AS current_value,
    h.quantity * (p.close - h.average_price) AS unrealized_gain_loss,
    (p.close - h.average_price) / h.average_price * 100 AS unrealized_gain_loss_percent
FROM holdings h
JOIN LATERAL (
    SELECT close
    FROM prices
    WHERE symbol = h.symbol
    ORDER BY timestamp DESC
    LIMIT 1
) p ON true;

CREATE OR REPLACE VIEW top_performers AS
SELECT 
    symbol,
    close AS current_price,
    close - LAG(close) OVER (PARTITION BY symbol ORDER BY timestamp) AS price_change,
    (close - LAG(close) OVER (PARTITION BY symbol ORDER BY timestamp)) / LAG(close) OVER (PARTITION BY symbol ORDER BY timestamp) * 100 AS price_change_percent
FROM prices
WHERE timestamp >= CURRENT_DATE
ORDER BY price_change_percent DESC;

-- Create triggers for automatic updates
CREATE OR REPLACE FUNCTION update_portfolio_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to relevant tables
DROP TRIGGER IF EXISTS trigger_update_portfolio_timestamp ON portfolios;
CREATE TRIGGER trigger_update_portfolio_timestamp
    BEFORE UPDATE ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_portfolio_timestamp();

DROP TRIGGER IF EXISTS trigger_update_holdings_timestamp ON holdings;
CREATE TRIGGER trigger_update_holdings_timestamp
    BEFORE UPDATE ON holdings
    FOR EACH ROW
    EXECUTE FUNCTION update_portfolio_timestamp();

-- Create sample data for testing (optional)
-- INSERT INTO assets (symbol, name, type, sector, market_cap, created_at) VALUES
-- ('AAPL', 'Apple Inc.', 'stock', 'Technology', 2800000000000, NOW()),
-- ('MSFT', 'Microsoft Corporation', 'stock', 'Technology', 2500000000000, NOW()),
-- ('GOOGL', 'Alphabet Inc.', 'stock', 'Technology', 1800000000000, NOW()),
-- ('BTC', 'Bitcoin', 'crypto', 'Cryptocurrency', 600000000000, NOW()),
-- ('ETH', 'Ethereum', 'crypto', 'Cryptocurrency', 200000000000, NOW());

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO stockee;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO stockee;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO stockee;

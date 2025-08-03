-- Initialize crytata database
-- This script runs when the TimescaleDB container starts

-- Create database if not exists
-- (Database is already created by POSTGRES_DB environment variable)

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create tables (these will be created by SQLAlchemy, but we can add custom indexes here)

-- Create indexes for better performance
-- Note: These indexes will be created by the application, but we can add additional ones here

-- Create a function to get the latest kline for each symbol and interval
CREATE OR REPLACE FUNCTION get_latest_klines(symbol_filter TEXT DEFAULT NULL)
RETURNS TABLE (
    symbol TEXT,
    interval TEXT,
    open_time TIMESTAMPTZ,
    close_price NUMERIC,
    volume NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (k.symbol, k.interval)
        k.symbol,
        k.interval,
        k.open_time,
        k.close_price,
        k.volume
    FROM klines k
    WHERE (symbol_filter IS NULL OR k.symbol = symbol_filter)
    ORDER BY k.symbol, k.interval, k.open_time DESC;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get price statistics for a symbol
CREATE OR REPLACE FUNCTION get_price_stats(
    symbol_filter TEXT,
    interval_filter TEXT,
    days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
    symbol TEXT,
    interval TEXT,
    avg_price NUMERIC,
    min_price NUMERIC,
    max_price NUMERIC,
    price_volatility NUMERIC,
    total_volume NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        k.symbol,
        k.interval,
        AVG(k.close_price) as avg_price,
        MIN(k.close_price) as min_price,
        MAX(k.close_price) as max_price,
        STDDEV(k.close_price) as price_volatility,
        SUM(k.volume) as total_volume
    FROM klines k
    WHERE k.symbol = symbol_filter 
        AND k.interval = interval_filter
        AND k.open_time >= NOW() - INTERVAL '1 day' * days_back
    GROUP BY k.symbol, k.interval;
END;
$$ LANGUAGE plpgsql;

-- Create a view for recent market data
CREATE OR REPLACE VIEW recent_market_data AS
SELECT 
    k.symbol,
    k.interval,
    k.open_time,
    k.close_price,
    k.volume,
    t.last_price as ticker_price,
    t.price_change_percent
FROM klines k
LEFT JOIN (
    SELECT DISTINCT ON (symbol) 
        symbol, 
        last_price, 
        price_change_percent,
        timestamp
    FROM tickers 
    ORDER BY symbol, timestamp DESC
) t ON k.symbol = t.symbol
WHERE k.open_time >= NOW() - INTERVAL '1 day'
ORDER BY k.symbol, k.interval, k.open_time DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crytata;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crytata;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO crytata; 
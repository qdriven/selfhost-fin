-- VNPY 加密货币交易系统数据库初始化脚本

-- 启用 TimescaleDB 扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建交易品种表
CREATE TABLE IF NOT EXISTS symbols (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL UNIQUE,
    exchange VARCHAR(20) NOT NULL,
    product VARCHAR(20) NOT NULL DEFAULT 'spot',
    base_currency VARCHAR(10) NOT NULL,
    quote_currency VARCHAR(10) NOT NULL,
    min_volume DECIMAL(20, 8),
    lot_size DECIMAL(20, 8),
    price_tick DECIMAL(20, 8),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建 K 线数据表
CREATE TABLE IF NOT EXISTS bar_data (
    datetime TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    interval VARCHAR(10) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    turnover DECIMAL(20, 8) NOT NULL DEFAULT 0,
    open_price DECIMAL(20, 8) NOT NULL,
    high_price DECIMAL(20, 8) NOT NULL,
    low_price DECIMAL(20, 8) NOT NULL,
    close_price DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 将 bar_data 转换为超表
SELECT create_hypertable('bar_data', 'datetime', if_not_exists => TRUE);

-- 创建逐笔交易数据表
CREATE TABLE IF NOT EXISTS tick_data (
    datetime TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    volume DECIMAL(20, 8) NOT NULL DEFAULT 0,
    turnover DECIMAL(20, 8) NOT NULL DEFAULT 0,
    open_interest DECIMAL(20, 8) NOT NULL DEFAULT 0,
    last_price DECIMAL(20, 8) NOT NULL,
    last_volume DECIMAL(20, 8) NOT NULL DEFAULT 0,
    limit_up DECIMAL(20, 8),
    limit_down DECIMAL(20, 8),
    open_price DECIMAL(20, 8) NOT NULL DEFAULT 0,
    high_price DECIMAL(20, 8) NOT NULL DEFAULT 0,
    low_price DECIMAL(20, 8) NOT NULL DEFAULT 0,
    pre_close DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_price_1 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_price_2 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_price_3 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_price_4 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_price_5 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_price_1 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_price_2 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_price_3 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_price_4 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_price_5 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_volume_1 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_volume_2 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_volume_3 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_volume_4 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    bid_volume_5 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_volume_1 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_volume_2 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_volume_3 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_volume_4 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    ask_volume_5 DECIMAL(20, 8) NOT NULL DEFAULT 0,
    localtime TIMESTAMPTZ DEFAULT NOW()
);

-- 将 tick_data 转换为超表
SELECT create_hypertable('tick_data', 'datetime', if_not_exists => TRUE);

-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
    orderid VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    type VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    offset VARCHAR(10) NOT NULL DEFAULT 'none',
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    traded DECIMAL(20, 8) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    reference VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建成交记录表
CREATE TABLE IF NOT EXISTS trades (
    tradeid VARCHAR(50) PRIMARY KEY,
    orderid VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    offset VARCHAR(10) NOT NULL DEFAULT 'none',
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
    gateway_name VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建持仓表
CREATE TABLE IF NOT EXISTS positions (
    symbol VARCHAR(50) NOT NULL,
    exchange VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL DEFAULT 0,
    frozen DECIMAL(20, 8) NOT NULL DEFAULT 0,
    price DECIMAL(20, 8) NOT NULL DEFAULT 0,
    pnl DECIMAL(20, 8) NOT NULL DEFAULT 0,
    yd_volume DECIMAL(20, 8) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, exchange, direction)
);

-- 创建账户表
CREATE TABLE IF NOT EXISTS accounts (
    accountid VARCHAR(50) PRIMARY KEY,
    balance DECIMAL(20, 8) NOT NULL DEFAULT 0,
    frozen DECIMAL(20, 8) NOT NULL DEFAULT 0,
    gateway_name VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建策略表
CREATE TABLE IF NOT EXISTS strategies (
    strategy_name VARCHAR(100) PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    author VARCHAR(50),
    parameters TEXT,
    variables TEXT,
    status VARCHAR(20) DEFAULT 'stopped',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建策略日志表
CREATE TABLE IF NOT EXISTS strategy_logs (
    id SERIAL PRIMARY KEY,
    datetime TIMESTAMPTZ NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL
);

-- 将 strategy_logs 转换为超表
SELECT create_hypertable('strategy_logs', 'datetime', if_not_exists => TRUE);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_bar_symbol_interval ON bar_data (symbol, interval, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_tick_symbol ON tick_data (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades (symbol, datetime DESC);
CREATE INDEX IF NOT EXISTS idx_strategy_logs_name ON strategy_logs (strategy_name, datetime DESC);

-- 创建数据保留策略（可选）
-- 保留1年的分钟级K线数据
-- SELECT add_retention_policy('bar_data', INTERVAL '1 year');

-- 保留3个月的Tick数据
-- SELECT add_retention_policy('tick_data', INTERVAL '3 months');

-- 保留6个月的策略日志
-- SELECT add_retention_policy('strategy_logs', INTERVAL '6 months');

-- 插入一些常见的交易对
INSERT INTO symbols (symbol, exchange, product, base_currency, quote_currency) VALUES
('BTCUSDT', 'OKX', 'spot', 'BTC', 'USDT'),
('ETHUSDT', 'OKX', 'spot', 'ETH', 'USDT'),
('BNBUSDT', 'OKX', 'spot', 'BNB', 'USDT'),
('ADAUSDT', 'OKX', 'spot', 'ADA', 'USDT'),
('SOLUSDT', 'OKX', 'spot', 'SOL', 'USDT'),
('DOTUSDT', 'OKX', 'spot', 'DOT', 'USDT'),
('AVAXUSDT', 'OKX', 'spot', 'AVAX', 'USDT'),
('MATICUSDT', 'OKX', 'spot', 'MATIC', 'USDT')
ON CONFLICT (symbol) DO NOTHING;

-- 授予权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vnpy;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vnpy; 
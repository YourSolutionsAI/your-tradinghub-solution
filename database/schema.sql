-- Live Trading Bot Database Schema
-- Erstelle diese Tabellen in deiner Supabase Datenbank

-- Bot Status Tracking
CREATE TABLE bot_status (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    is_trading BOOLEAN DEFAULT FALSE,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trading Pairs Configuration
CREATE TABLE trading_pairs (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trades Log (Alle ausgeführten Trades)
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    side VARCHAR(10) NOT NULL, -- BUY/SELL
    symbol VARCHAR(20) NOT NULL,
    amount DECIMAL(20,8) NOT NULL,
    order_id VARCHAR(100),
    price DECIMAL(20,8),
    fee DECIMAL(20,8),
    status VARCHAR(20) DEFAULT 'completed',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market Data Storage
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(20,8) NOT NULL,
    volume_24h DECIMAL(20,2),
    price_change_24h DECIMAL(10,4),
    high_24h DECIMAL(20,8),
    low_24h DECIMAL(20,8),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Portfolio Snapshots
CREATE TABLE portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    total_balance_usdt DECIMAL(20,2),
    assets JSONB, -- Array of {asset, balance}
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trading Strategies Configuration
CREATE TABLE trading_strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL, -- 'simple_ma', 'rsi', etc.
    parameters JSONB, -- Strategy-specific parameters
    is_active BOOLEAN DEFAULT TRUE,
    max_order_size DECIMAL(20,2) DEFAULT 50.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Metrics
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    successful_trades INTEGER DEFAULT 0,
    total_profit_usdt DECIMAL(20,2) DEFAULT 0,
    total_fees_usdt DECIMAL(20,2) DEFAULT 0,
    roi_percentage DECIMAL(10,4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Error Logs
CREATE TABLE error_logs (
    id SERIAL PRIMARY KEY,
    error_message TEXT NOT NULL,
    component VARCHAR(50), -- 'trading_bot', 'api', etc.
    stack_trace TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes für Performance
CREATE INDEX idx_trades_symbol_timestamp ON trades(symbol, timestamp);
CREATE INDEX idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);
CREATE INDEX idx_portfolio_snapshots_timestamp ON portfolio_snapshots(timestamp);
CREATE INDEX idx_error_logs_timestamp ON error_logs(timestamp);

-- Row Level Security (RLS) aktivieren
ALTER TABLE bot_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_pairs ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE error_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies (Alle Tabellen für authentifizierte Benutzer zugänglich)
DO $$
BEGIN
    -- Bot Status
    CREATE POLICY "Allow all for authenticated users" ON bot_status FOR ALL TO authenticated USING (true);
    
    -- Trading Pairs
    CREATE POLICY "Allow all for authenticated users" ON trading_pairs FOR ALL TO authenticated USING (true);
    
    -- Trades
    CREATE POLICY "Allow all for authenticated users" ON trades FOR ALL TO authenticated USING (true);
    
    -- Market Data
    CREATE POLICY "Allow all for authenticated users" ON market_data FOR ALL TO authenticated USING (true);
    
    -- Portfolio Snapshots
    CREATE POLICY "Allow all for authenticated users" ON portfolio_snapshots FOR ALL TO authenticated USING (true);
    
    -- Trading Strategies
    CREATE POLICY "Allow all for authenticated users" ON trading_strategies FOR ALL TO authenticated USING (true);
    
    -- Performance Metrics
    CREATE POLICY "Allow all for authenticated users" ON performance_metrics FOR ALL TO authenticated USING (true);
    
    -- Error Logs
    CREATE POLICY "Allow all for authenticated users" ON error_logs FOR ALL TO authenticated USING (true);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Initiale Daten einfügen
INSERT INTO trading_pairs (symbol, is_active) VALUES
    ('BTCUSDT', true),
    ('ETHUSDT', true)
ON CONFLICT (symbol) DO NOTHING;

INSERT INTO bot_status (status, is_trading) VALUES
    ('stopped', false)
ON CONFLICT DO NOTHING;

-- Kommentar: Schema für professionelles Live Trading
COMMENT ON TABLE trades IS 'Alle ausgeführten Live-Trades mit Binance';
COMMENT ON TABLE market_data IS 'Historische Marktdaten für Analyse';
COMMENT ON TABLE portfolio_snapshots IS 'Portfolio-Zustand über Zeit';
COMMENT ON TABLE trading_strategies IS 'Konfigurierte Trading-Strategien';
COMMENT ON TABLE performance_metrics IS 'Tägliche Performance-Metriken';

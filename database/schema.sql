-- Trading Bot Database Schema für Supabase
-- Dieses Schema sollte in der Supabase SQL Editor ausgeführt werden

-- Aktiviere Row Level Security
-- Die Tabellen sind öffentlich lesbar, aber nur authentifizierte Benutzer können schreiben

-- 1. Bot Status Tabelle
CREATE TABLE IF NOT EXISTS bot_status (
    id BIGSERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'stopped', -- running, stopped, error
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_heartbeat TIMESTAMPTZ DEFAULT NOW(),
    error_message TEXT,
    configuration JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Marktdaten Tabelle
CREATE TABLE IF NOT EXISTS market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume_24h DECIMAL(20, 8),
    price_change_24h DECIMAL(10, 4),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    raw_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Trades Tabelle
CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(50),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- BUY, SELL
    amount DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8),
    commission DECIMAL(20, 8),
    commission_asset VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, cancelled
    strategy_used VARCHAR(50),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    binance_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Portfolio Snapshots Tabelle
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id BIGSERIAL PRIMARY KEY,
    total_balance_usdt DECIMAL(20, 8) NOT NULL DEFAULT 0,
    assets JSONB NOT NULL DEFAULT '[]',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Trading Strategien Tabelle
CREATE TABLE IF NOT EXISTS trading_strategies (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL, -- simple_ma, rsi, bollinger, custom
    parameters JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT false,
    max_order_size DECIMAL(20, 8) DEFAULT 100,
    risk_percentage DECIMAL(5, 2) DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Error Logs Tabelle
CREATE TABLE IF NOT EXISTS error_logs (
    id BIGSERIAL PRIMARY KEY,
    component VARCHAR(50) NOT NULL, -- trading_bot, dashboard, api
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    context JSONB,
    severity VARCHAR(20) DEFAULT 'error', -- info, warning, error, critical
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Konfiguration Tabelle
CREATE TABLE IF NOT EXISTS bot_configuration (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    is_sensitive BOOLEAN DEFAULT false, -- für API Keys etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Benutzer Einstellungen (für Dashboard)
CREATE TABLE IF NOT EXISTS user_settings (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    settings JSONB NOT NULL DEFAULT '{}',
    notification_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- 9. Benachrichtigungen Tabelle
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info', -- info, warning, error, success
    is_read BOOLEAN DEFAULT false,
    data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10. Performance Metriken
CREATE TABLE IF NOT EXISTS performance_metrics (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_profit_usdt DECIMAL(20, 8) DEFAULT 0,
    total_volume_usdt DECIMAL(20, 8) DEFAULT 0,
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    win_rate DECIMAL(5, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(date)
);

-- Indizes für bessere Performance
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_timestamp ON trades(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_portfolio_timestamp ON portfolio_snapshots(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read);

-- Trigger für updated_at Felder
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_bot_status_updated_at BEFORE UPDATE ON bot_status FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON trading_strategies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_config_updated_at BEFORE UPDATE ON bot_configuration FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
ALTER TABLE bot_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE error_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE bot_configuration ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;

-- Policies für öffentliche Leserechte (Dashboard)
CREATE POLICY "Öffentlicher Lesezugriff auf bot_status" ON bot_status FOR SELECT USING (true);
CREATE POLICY "Öffentlicher Lesezugriff auf market_data" ON market_data FOR SELECT USING (true);
CREATE POLICY "Öffentlicher Lesezugriff auf trades" ON trades FOR SELECT USING (true);
CREATE POLICY "Öffentlicher Lesezugriff auf portfolio_snapshots" ON portfolio_snapshots FOR SELECT USING (true);
CREATE POLICY "Öffentlicher Lesezugriff auf trading_strategies" ON trading_strategies FOR SELECT USING (true);
CREATE POLICY "Öffentlicher Lesezugriff auf error_logs" ON error_logs FOR SELECT USING (true);
CREATE POLICY "Öffentlicher Lesezugriff auf performance_metrics" ON performance_metrics FOR SELECT USING (true);

-- Policies für Service Role (Bot kann alles)
CREATE POLICY "Service Role kann alles auf bot_status" ON bot_status USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Service Role kann alles auf market_data" ON market_data USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Service Role kann alles auf trades" ON trades USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Service Role kann alles auf portfolio_snapshots" ON portfolio_snapshots USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Service Role kann alles auf trading_strategies" ON trading_strategies USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Service Role kann alles auf error_logs" ON error_logs USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Service Role kann alles auf bot_configuration" ON bot_configuration USING (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Service Role kann alles auf performance_metrics" ON performance_metrics USING (auth.jwt() ->> 'role' = 'service_role');

-- Policies für authentifizierte Benutzer
CREATE POLICY "Benutzer können eigene Einstellungen verwalten" ON user_settings 
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Benutzer können eigene Benachrichtigungen verwalten" ON notifications 
  FOR ALL USING (auth.uid() = user_id);

-- Authentifizierte Benutzer können Strategien bearbeiten
CREATE POLICY "Authentifizierte Benutzer können Strategien bearbeiten" ON trading_strategies 
  FOR ALL USING (auth.role() = 'authenticated');

-- Beispiel-Daten einfügen
INSERT INTO bot_configuration (key, value, description, category) VALUES
('default_trading_pairs', '["BTCUSDT", "ETHUSDT", "ADAUSDT"]', 'Standard Trading-Paare', 'trading'),
('risk_per_trade', '0.01', 'Risiko pro Trade (1%)', 'risk_management'),
('max_daily_trades', '50', 'Maximale Trades pro Tag', 'limits'),
('enable_notifications', 'true', 'Benachrichtigungen aktivieren', 'notifications')
ON CONFLICT (key) DO NOTHING;

INSERT INTO trading_strategies (name, symbol, strategy_type, parameters, is_active) VALUES
('BTC Moving Average', 'BTCUSDT', 'simple_ma', '{"short_period": 10, "long_period": 20}', true),
('ETH RSI Strategy', 'ETHUSDT', 'rsi', '{"period": 14, "oversold": 30, "overbought": 70}', false)
ON CONFLICT DO NOTHING;

-- Views für Dashboard
CREATE OR REPLACE VIEW dashboard_summary AS
SELECT 
    (SELECT status FROM bot_status ORDER BY timestamp DESC LIMIT 1) as bot_status,
    (SELECT total_balance_usdt FROM portfolio_snapshots ORDER BY timestamp DESC LIMIT 1) as portfolio_value,
    (SELECT COUNT(*) FROM trades WHERE DATE(timestamp) = CURRENT_DATE) as trades_today,
    (SELECT COUNT(*) FROM trading_strategies WHERE is_active = true) as active_strategies;

-- Realtime für Dashboard (Supabase Realtime)
-- Diese müssen in der Supabase UI aktiviert werden:
-- ALTER PUBLICATION supabase_realtime ADD TABLE bot_status;
-- ALTER PUBLICATION supabase_realtime ADD TABLE market_data;
-- ALTER PUBLICATION supabase_realtime ADD TABLE trades;
-- ALTER PUBLICATION supabase_realtime ADD TABLE portfolio_snapshots;

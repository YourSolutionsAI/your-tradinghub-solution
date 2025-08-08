# Trading Bot System - Setup Anleitung

Dieses System besteht aus einem Python Trading Bot (Railway), einem Next.js Dashboard (Vercel) und einer Postgres Datenbank (Supabase).

## 📋 Übersicht

### Architektur
- **Trading Bot**: Python-basiert, läuft persistent auf Railway
- **Dashboard**: Next.js React App, deployed auf Vercel
- **Datenbank**: PostgreSQL mit Supabase (Auth, Realtime, API)
- **Börse**: Binance (Testnet und Live)

### Funktionen
- ✅ Automatisiertes Trading basierend auf verschiedenen Strategien
- ✅ Real-time Dashboard mit Marktdaten und Portfolio-Übersicht
- ✅ Trade-History und Performance-Tracking
- ✅ Konfigurierbares Risikomanagement
- ✅ Error-Logging und Monitoring
- ✅ Responsive Web-Interface

## 🚀 Setup-Anleitung

### 0. GitHub Projekt: https://github.com/YourSolutionsAI/your-tradinghub-solution.git 

✅ ERLEDIGT

### 1. Binance API Setup

#### Schritt 1: Binance Account erstellen
1. Registrieren Sie sich bei [Binance](https://www.binance.com)
2. Aktivieren Sie 2FA (Zwei-Faktor-Authentifizierung)
3. Verifizieren Sie Ihren Account

✅ ERLEDIGT

#### Schritt 2: API Keys erstellen
1. Gehen Sie zu "API Management" in Ihren Account-Einstellungen
2. Erstellen Sie einen neuen API Key
3. **Wichtig**: Aktivieren Sie nur "Spot Trading" (nicht Futures)
4. Notieren Sie sich:
   - `API Key` QVF77fJKJSEQCgIDfw2HJ77WtIoer90ABvR15t89ECaKdiE8ewfNJ9F5NYpwZs2D

   - `Secret Key` G5EVKVicRAT7TLOwkNyqBzu63bBlJRi9AEmE1bxhWSaKvXBGntfHob0Uf0Ymtz2K
✅ ERLEDIGT

#### Schritt 3: Testnet aktivieren (empfohlen für den Start) <-- AMMERKUNG -- WIRD NICHT GENUTZT!!>
1. Besuchen Sie [Binance Testnet](https://testnet.binance.vision/)
2. Melden Sie sich mit Ihrem Binance Account an
3. Erstellen Sie Testnet API Keys
4. Laden Sie Testguthaben auf

❌ WIRD NICHT GENTUZT

### 2. Supabase Setup

#### Schritt 1: Supabase Projekt erstellen
1. Gehen Sie zu [Supabase](https://supabase.com)
2. Erstellen Sie einen neuen Account oder melden Sie sich an
3. Klicken Sie auf "New Project"
4. Wählen Sie einen Namen und ein sicheres Datenbankpasswort
5. Wählen Sie eine Region (empfohlen: Europa für DSGVO-Konformität)

✅ ERLEDIGT

#### Schritt 2: Datenbank Schema einrichten
1. Gehen Sie zum SQL Editor in Ihrem Supabase Dashboard
2. Kopieren Sie den Inhalt von `database/schema.sql`
3. Führen Sie das SQL-Script aus
4. Überprüfen Sie, dass alle Tabellen erstellt wurden

✅ ERLEDIGT

#### Schritt 3: API Keys notieren
Notieren Sie sich aus den Projekteinstellungen:
- `Project URL` https://snemqjltnqflyfrmjlpj.supabase.co
- `Project API Key (anon public)` eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNuZW1xamx0bnFmbHlmcm1qbHBqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2ODE5ODQsImV4cCI6MjA3MDI1Nzk4NH0.51bZ3mq7uEuxO_N7daFK5S6eikAWjxzgatiTIvD5UQs
- `Project API Key (service_role)` - **Nur für den Bot!** eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNuZW1xamx0bnFmbHlmcm1qbHBqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDY4MTk4NCwiZXhwIjoyMDcwMjU3OTg0fQ.Sx62aDm4lzt943k9-cugGQxfZhHEiv0gcBT_P0b_6gI

✅ ERLEDIGT

#### Schritt 4: Realtime aktivieren <-- ANMERKUNG <-- FÜR SPÄTER IST AKTUELL NIOCH NICHT VERFÜGBAR AUF SUPABASE>
1. Gehen Sie zu "Database" → "Replication"
2. Aktivieren Sie Realtime für folgende Tabellen:
   - `bot_status`
   - `market_data`
   - `trades`
   - `portfolio_snapshots`

❌ WIRD NICHT GENUTZT

### 3. Railway Deployment (Trading Bot)

#### Schritt 1: Railway Account erstellen
1. Gehen Sie zu [Railway](https://railway.app)
2. Melden Sie sich mit GitHub an
3. Verifizieren Sie Ihren Account

 ✅ERLEDIGT

#### Schritt 2: Projekt deployen
1. Klicken Sie auf "New Project"
2. Wählen Sie "Deploy from GitHub repo"
3. Verbinden Sie Ihr GitHub Repository
4. Wählen Sie den `trading-bot` Ordner als Root-Verzeichnis

#### Schritt 3: Umgebungsvariablen setzen
Fügen Sie folgende Environment Variables hinzu:

```bash
# Binance API
BINANCE_API_KEY=ihr_binance_api_key
BINANCE_API_SECRET=ihr_binance_secret_key
BINANCE_TESTNET=true

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=ihr_supabase_anon_key
SUPABASE_SERVICE_KEY=ihr_supabase_service_key

# Bot Konfiguration
TRADING_PAIRS=BTCUSDT,ETHUSDT,ADAUSDT
MIN_BALANCE_THRESHOLD=0.001
MAX_ORDER_SIZE=100

# API Security
API_KEY=ihr_sicherer_api_key_für_dashboard

# Railway
PORT=8000
```

#### Schritt 4: Deployment überwachen
1. Warten Sie, bis das Deployment abgeschlossen ist
2. Überprüfen Sie die Logs auf Fehler
3. Notieren Sie sich die Railway App URL

### 4. Vercel Deployment (Dashboard)

#### Schritt 1: Vercel Account erstellen
1. Gehen Sie zu [Vercel](https://vercel.com)
2. Melden Sie sich mit GitHub an

#### Schritt 2: Projekt deployen
1. Klicken Sie auf "New Project"
2. Importieren Sie Ihr GitHub Repository
3. Setzen Sie `dashboard` als Root-Verzeichnis
4. Framework: "Next.js"

#### Schritt 3: Umgebungsvariablen setzen
```bash
# Supabase (Public)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=ihr_supabase_anon_key

# Bot API
NEXT_PUBLIC_BOT_API_URL=https://ihre-railway-app.railway.app
BOT_API_KEY=ihr_sicherer_api_key_für_dashboard
```

#### Schritt 4: Domain konfigurieren (optional)
1. Gehen Sie zu "Settings" → "Domains"
2. Fügen Sie Ihre eigene Domain hinzu
3. Konfigurieren Sie DNS-Einstellungen

### 5. Lokale Entwicklung

#### Voraussetzungen
- Python 3.11+
- Node.js 18+
- Git

#### Trading Bot lokal ausführen
```bash
cd trading-bot
pip install -r requirements.txt
cp env.example .env
# .env Datei mit Ihren Werten ausfüllen
python main.py
```

#### Dashboard lokal ausführen
```bash
cd dashboard
npm install
cp env.example .env.local
# .env.local Datei mit Ihren Werten ausfüllen
npm run dev
```

## 🔧 Konfiguration

### Trading Strategien

#### Moving Average Strategie
```json
{
  "strategy_type": "simple_ma",
  "parameters": {
    "short_period": 10,
    "long_period": 20
  }
}
```

#### RSI Strategie
```json
{
  "strategy_type": "rsi",
  "parameters": {
    "period": 14,
    "oversold": 30,
    "overbought": 70
  }
}
```

### Risikomanagement
- Setzen Sie `MIN_BALANCE_THRESHOLD` für minimale Handelsbeträge
- Konfigurieren Sie `MAX_ORDER_SIZE` für maximale Order-Größen
- Verwenden Sie den Testnet-Modus für erste Tests

## 📊 Monitoring

### Dashboard Features
- Real-time Bot-Status
- Portfolio-Übersicht
- Trade-History
- Marktdaten-Charts
- Error-Logs

### Logging
- Alle Trades werden in Supabase gespeichert
- Error-Logs mit Stack-Traces
- Performance-Metriken

## ⚠️ Sicherheitshinweise

### API Keys
- **NIEMALS** API Keys in Code committen
- Verwenden Sie verschiedene Keys für Testnet und Live-Trading
- Rotieren Sie Keys regelmäßig

### Bot-Sicherheit
- Starten Sie immer im Testnet-Modus
- Setzen Sie niedrige Order-Limits
- Überwachen Sie den Bot regelmäßig
- Implementieren Sie Stop-Loss-Mechanismen

### Datenbank-Sicherheit
- Verwenden Sie Row Level Security (RLS)
- Beschränken Sie Service-Role-Zugriff
- Backup-Strategie implementieren

## 🔄 Updates und Wartung

### Bot Updates
```bash
# Railway: Push zu GitHub triggert automatisches Deployment
git push origin main
```

### Dashboard Updates
```bash
# Vercel: Push zu GitHub triggert automatisches Deployment
git push origin main
```

### Datenbank Migrations
- Führen Sie Schema-Änderungen über Supabase SQL Editor aus
- Erstellen Sie Backups vor größeren Änderungen

## 🛠️ Troubleshooting

### Häufige Probleme

#### Bot startet nicht
1. Überprüfen Sie API Keys
2. Kontrollieren Sie Supabase-Verbindung
3. Prüfen Sie Railway-Logs

#### Dashboard zeigt keine Daten
1. Supabase RLS-Policies überprüfen
2. CORS-Einstellungen kontrollieren
3. API-Endpunkte testen

#### Trading-Fehler
1. Binance API Limits überprüfen
2. Account-Balance kontrollieren
3. Symbol-Verfügbarkeit prüfen

### Support
- GitHub Issues für Bug-Reports
- Supabase Community für Datenbank-Fragen
- Binance API Dokumentation für Trading-Issues

## 📈 Erweiterungen

### Mögliche Verbesserungen
- Weitere Trading-Strategien
- Backtesting-Funktionalität
- Mobile App
- Telegram-Benachrichtigungen
- Advanced Charting
- Multi-Exchange Support

---

**Hinweis**: Dieses System ist für Bildungszwecke entwickelt. Trading mit echtem Geld birgt Risiken. Handeln Sie verantwortungsbewusst und nur mit Geld, das Sie sich leisten können zu verlieren.

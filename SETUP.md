# 🚀 Live Trading Bot Setup - Komplett-Anleitung

## 📋 Übersicht
Professioneller Trading Bot für Binance **LIVE TRADING** mit Next.js Dashboard.

### Architektur
- **Bot**: Python (FastAPI) → Render
- **Frontend**: Next.js → Vercel  
- **Database**: PostgreSQL → Supabase
- **Exchange**: Binance **LIVE API**

---

## 🏗️ Teil 1: Supabase Database Setup

### 1.1 Supabase Projekt erstellen
1. Gehe zu [supabase.com](https://supabase.com)
2. Erstelle neues Projekt
3. Wähle Region: **Deutschland** (eu-central-1)
4. Notiere dir:
   - **Project URL**: `https://xxx.supabase.co`
   - **Anon Public Key**: `eyJhbG...`

### 1.2 Datenbank Schema
1. Gehe zu **SQL Editor** in Supabase
2. Kopiere Inhalt von `database/schema.sql`
3. Führe das komplette SQL aus
4. Bestätige: 8 Tabellen wurden erstellt

---

## 🤖 Teil 2: Bot Deployment (Render)

### 2.1 Render Account Setup
1. Gehe zu [render.com](https://render.com)
2. Erstelle Account / Login mit GitHub
3. Verbinde dein GitHub Repository

### 2.2 Web Service erstellen
1. **New** → **Web Service**
2. **Repository**: `your-tradinghub-solution`
3. **Branch**: `main`
4. **Root Directory**: (leer lassen)
5. **Build Command**: (automatisch erkannt)
6. **Start Command**: `python bot/api.py`

### 2.3 Environment Variables setzen
```bash
# Binance LIVE API (WICHTIG: Keine Testnet!)
BINANCE_API_KEY=dein_echter_binance_api_key
BINANCE_API_SECRET=dein_echter_binance_api_secret

# Supabase
SUPABASE_URL=https://deinprojekt.supabase.co
SUPABASE_ANON_KEY=dein_supabase_anon_key

# Security
API_KEY=dein_sicherer_random_key_hier

# Optional
PORT=8000
```

### 2.4 Deploy
1. Klicke **Create Web Service**
2. Warte auf Build (3-5 Minuten)
3. Teste Health Check: `https://dein-bot.onrender.com/health`

---

## 🌐 Teil 3: Frontend Deployment (Vercel)

### 3.1 Vercel Setup
1. Gehe zu [vercel.com](https://vercel.com)
2. Login mit GitHub
3. **New Project** → Repository auswählen

### 3.2 Vercel Konfiguration
- **Framework Preset**: Next.js
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

### 3.3 Environment Variables
```bash
# Bot API
NEXT_PUBLIC_BOT_API_URL=https://dein-bot.onrender.com
BOT_API_KEY=gleicher_key_wie_in_render

# Supabase (für Frontend)
NEXT_PUBLIC_SUPABASE_URL=https://deinprojekt.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=dein_supabase_anon_key
```

### 3.4 Deploy
1. **Deploy** klicken
2. Warte auf Build
3. Teste Dashboard: `https://dein-dashboard.vercel.app`

---

## 🔑 Teil 4: Binance API Setup (LIVE)

### 4.1 Binance Account
1. Erstelle/Login bei [binance.com](https://binance.com)
2. **Verifizierung**: KYC abschließen
3. **2FA aktivieren**: Sicherheit!

### 4.2 API Keys erstellen
1. **Account** → **API Management**
2. **Create API** 
3. **Label**: `TradingBot-Live`
4. **Restrictions**:
   - ✅ **Enable Spot & Margin Trading**
   - ❌ **Enable Futures** (optional)
   - ✅ **IP Restriction**: Render IPs hinzufügen
5. **API Key** und **Secret** kopieren

### 4.3 Sicherheit Checklist
- ✅ 2FA aktiviert
- ✅ IP-Restrictions gesetzt
- ✅ Nur nötige Permissions
- ✅ API Keys sicher gespeichert

---

## 🧪 Teil 5: System Test

### 5.1 Bot Status Test
```bash
curl https://dein-bot.onrender.com/health
# Sollte zeigen: {"status":"healthy","bot_initialized":true}
```

### 5.2 Frontend Test
1. Öffne Dashboard: `https://dein-dashboard.vercel.app`
2. **Bot Status**: Sollte "STOPPED" zeigen
3. **Portfolio**: Deine echten Binance Guthaben
4. **Trading Pairs**: BTC/ETH vorausgewählt

### 5.3 Live Trading Test
1. **⚠️ WICHTIG**: Starte mit kleinen Beträgen!
2. Dashboard → **Start Trading**
3. Logs in Render prüfen
4. Nach 1-2 Minuten → **Stop Trading**

---

## ⚙️ Teil 6: Konfiguration

### 6.1 Trading Pairs anpassen
- Dashboard → **Trading Pairs** Tab
- Beliebte Pairs auswählen
- **Empfehlung**: 2-3 stabile Pairs

### 6.2 Risiko-Management
**Aktuelle Einstellungen**:
- 5% der USDT-Balance pro Trade
- Max. 50 USDT pro Order
- 30 Sekunden Check-Intervall
- Simple Moving Average Strategie

### 6.3 Monitoring
- **Logs**: Render Dashboard → Logs
- **Performance**: Supabase → Tables
- **Alerts**: Email bei Fehlern

---

## 🚨 Wichtige Sicherheitshinweise

### ❌ NIEMALS:
- API Keys in Git committen
- Testnet und Live vermischen
- Bot unüberwacht laufen lassen
- Mit Geld handeln, das du nicht verlieren kannst

### ✅ IMMER:
- Klein anfangen (10-50 USDT)
- Regelmäßig Logs prüfen
- Stop-Loss Limits beachten
- Bot Status überwachen

---

## 🆘 Troubleshooting

### Bot startet nicht
1. Render Logs prüfen
2. Binance API Keys validieren
3. Supabase Verbindung testen

### Dashboard zeigt keine Daten
1. BOT_API_KEY in Vercel prüfen
2. CORS Headers in bot/api.py
3. Network Tab im Browser

### Trading funktioniert nicht
1. Binance Account: Trading enabled?
2. Ausreichend USDT Balance?
3. Trading Pairs verfügbar?

---

## 📞 Support

Bei Problemen:
1. **Logs sammeln**: Render + Vercel + Browser Console
2. **Error Details**: Genaue Fehlermeldung
3. **Account Status**: Binance + Supabase + Deployment Status

**🎯 Ziel**: Professioneller, sicherer Live Trading Bot für echte Gewinne!**

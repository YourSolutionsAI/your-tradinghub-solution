import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from dotenv import load_dotenv
from binance.spot import Spot as BinanceClient
from supabase import create_client, Client as SupabaseClient
import pandas as pd

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class TradingBot:
    def __init__(self):
        """Initialisierung des Trading Bots"""
        # Binance Client – Live-Handel (binance-connector)
        try:
            api_key = os.getenv("BINANCE_API_KEY")
            api_secret = os.getenv("BINANCE_API_SECRET")
            self.binance_client = BinanceClient(api_key=api_key, api_secret=api_secret)
            logger.info("Binance Client (LIVE, binance-connector) erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Binance Client Fehler: {e}")
            # Fallback abschalten? Für Stabilität belassen wir None und überspringen Market-Calls
            self.binance_client = None
        
        # Supabase Client
        self.supabase: SupabaseClient = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
        
        # Bot Konfiguration
        self.is_running = False
        # Trading Pairs aus Environment Variable oder Standard-Werte
        trading_pairs_env = os.getenv("TRADING_PAIRS", "BTCUSDT,ETHUSDT,ADAUSDT")
        self.trading_pairs = [pair.strip() for pair in trading_pairs_env.split(",")]
        self.balance_threshold = float(os.getenv("MIN_BALANCE_THRESHOLD", "0.001"))
        
    async def start_bot(self):
        """Startet den Trading Bot"""
        logger.info("Trading Bot wird gestartet...")
        self.is_running = True
        
        # Bot Status in Supabase aktualisieren
        await self.update_bot_status("running")
        
        while self.is_running:
            try:
                # Marktdaten analysieren
                await self.analyze_market()
                
                # Trading-Signale prüfen
                await self.check_trading_signals()
                
                # Portfolio-Status aktualisieren
                await self.update_portfolio_status()
                
                # 30 Sekunden warten
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Fehler im Bot-Loop: {e}")
                await self.log_error(str(e))
                await asyncio.sleep(60)  # Längere Pause bei Fehlern
    
    async def stop_bot(self):
        """Stoppt den Trading Bot"""
        logger.info("Trading Bot wird gestoppt...")
        self.is_running = False
        await self.update_bot_status("stopped")
    
    async def analyze_market(self):
        """Analysiert Marktdaten für alle Trading-Paare"""
        if not self.binance_client:
            logger.warning("Binance Client nicht verfügbar - überspringe Marktanalyse")
            return
            
        for symbol in self.trading_pairs:
            try:
                # Aktuelle Preisdaten abrufen
                ticker = self.binance_client.ticker_price(symbol)
                price = float(ticker['price'])
                
                # Historische Kerzendaten (24h)
                klines = self.binance_client.klines(symbol, interval="1h", limit=24)
                
                # Marktdaten in Supabase speichern
                await self.save_market_data(symbol, price, klines)
                
            except Exception as e:
                logger.error(f"Fehler bei Marktanalyse für {symbol}: {e}")
    
    async def check_trading_signals(self):
        """Überprüft Trading-Signale basierend auf gespeicherten Strategien"""
        try:
            # Aktive Strategien aus Supabase abrufen
            strategies = self.supabase.table("trading_strategies").select("*").eq("is_active", True).execute()
            
            for strategy in strategies.data:
                symbol = strategy['symbol']
                strategy_type = strategy['strategy_type']
                
                if strategy_type == "simple_ma":
                    await self.check_moving_average_signal(symbol, strategy)
                elif strategy_type == "rsi":
                    await self.check_rsi_signal(symbol, strategy)
                    
        except Exception as e:
            logger.error(f"Fehler bei Signal-Überprüfung: {e}")
    
    async def check_moving_average_signal(self, symbol: str, strategy: Dict):
        """Einfache Moving Average Strategie"""
        try:
            # Letzten 50 Kerzendaten abrufen
            klines = self.binance_client.klines(symbol, interval="15m", limit=48)
            
            # Preise extrahieren
            prices = [float(kline[4]) for kline in klines]  # Schlusskurse
            
            if len(prices) >= 20:
                ma_short = sum(prices[-10:]) / 10  # 10-Perioden MA
                ma_long = sum(prices[-20:]) / 20   # 20-Perioden MA
                current_price = prices[-1]
                
                # Signal generieren
                if ma_short > ma_long and current_price > ma_short:
                    await self.execute_buy_order(symbol, strategy)
                elif ma_short < ma_long and current_price < ma_short:
                    await self.execute_sell_order(symbol, strategy)
                    
        except Exception as e:
            logger.error(f"Fehler bei MA-Signal für {symbol}: {e}")
    
    async def check_rsi_signal(self, symbol: str, strategy: Dict):
        """RSI-basierte Strategie"""
        # Implementierung für RSI-Signale
        pass
    
    async def execute_buy_order(self, symbol: str, strategy: Dict):
        """Führt eine Kauforder aus"""
        try:
            # Account-Balance prüfen
            account = self.binance_client.account()
            usdt_balance = float([asset['free'] for asset in account['balances'] if asset['asset'] == 'USDT'][0])
            
            if usdt_balance > self.balance_threshold:
                order_amount = min(usdt_balance * 0.1, strategy.get('max_order_size', 100))  # 10% der Balance oder max_order_size
                
                # Echte Order (LIVE)
                order = self.binance_client.new_order(symbol=symbol, side='BUY', type='MARKET', quoteOrderQty=order_amount)
                await self.log_trade("BUY", symbol, order_amount, order.get('orderId', 'unknown'))
                    
        except Exception as e:
            logger.error(f"Fehler bei Kauforder für {symbol}: {e}")
    
    async def execute_sell_order(self, symbol: str, strategy: Dict):
        """Führt eine Verkaufsorder aus"""
        try:
            # Asset-Balance prüfen
            account = self.binance_client.account()
            asset = symbol.replace('USDT', '')
            asset_balance = float([a['free'] for a in account['balances'] if a['asset'] == asset][0])
            
            if asset_balance > 0:
                # Echte Order (LIVE)
                order = self.binance_client.new_order(symbol=symbol, side='SELL', type='MARKET', quantity=asset_balance)
                await self.log_trade("SELL", symbol, asset_balance, order.get('orderId', 'unknown'))
                    
        except Exception as e:
            logger.error(f"Fehler bei Verkaufsorder für {symbol}: {e}")
    
    async def save_market_data(self, symbol: str, price: float, klines: List):
        """Speichert Marktdaten in Supabase"""
        try:
            market_data = {
                "symbol": symbol,
                "price": price,
                "timestamp": datetime.utcnow().isoformat(),
                "volume_24h": sum([float(kline[5]) for kline in klines]),
                "price_change_24h": ((price - float(klines[0][4])) / float(klines[0][4])) * 100
            }
            
            self.supabase.table("market_data").insert(market_data).execute()
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Marktdaten: {e}")
    
    async def log_trade(self, side: str, symbol: str, amount: float, order_id: str):
        """Loggt einen Trade in Supabase"""
        try:
            trade_log = {
                "side": side,
                "symbol": symbol,
                "amount": amount,
                "order_id": order_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            self.supabase.table("trades").insert(trade_log).execute()
            logger.info(f"Trade geloggt: {side} {amount} {symbol}")
            
        except Exception as e:
            logger.error(f"Fehler beim Trade-Logging: {e}")
    
    async def update_portfolio_status(self):
        """Aktualisiert den Portfolio-Status"""
        try:
            account = self.binance_client.get_account()
            
            portfolio_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_balance_usdt": 0,
                "assets": []
            }
            
            for asset in account['balances']:
                balance = float(asset['free']) + float(asset['locked'])
                if balance > 0:
                    portfolio_data["assets"].append({
                        "asset": asset['asset'],
                        "balance": balance
                    })
            
            # Gesamtwert in USDT berechnen
            total_usdt = 0
            for asset_data in portfolio_data["assets"]:
                if asset_data["asset"] == "USDT":
                    total_usdt += asset_data["balance"]
                else:
                    try:
                        ticker = self.binance_client.ticker_price(f"{asset_data['asset']}USDT")
                        total_usdt += asset_data["balance"] * float(ticker['price'])
                    except:
                        pass  # Ignoriere Assets ohne USDT-Paar
            
            portfolio_data["total_balance_usdt"] = total_usdt
            
            # In Supabase speichern
            self.supabase.table("portfolio_snapshots").insert(portfolio_data).execute()
            
        except Exception as e:
            logger.error(f"Fehler beim Portfolio-Update: {e}")
    
    async def update_bot_status(self, status: str):
        """Aktualisiert den Bot-Status in Supabase"""
        try:
            status_data = {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "last_heartbeat": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("bot_status").upsert(status_data).execute()
            
        except Exception as e:
            logger.error(f"Fehler beim Status-Update: {e}")
    
    async def log_error(self, error_message: str):
        """Loggt Fehler in Supabase"""
        try:
            error_log = {
                "error_message": error_message,
                "timestamp": datetime.utcnow().isoformat(),
                "component": "trading_bot"
            }
            
            self.supabase.table("error_logs").insert(error_log).execute()
            
        except Exception as e:
            logger.error(f"Fehler beim Error-Logging: {e}")
    
    def update_trading_pairs(self, new_pairs: List[str]):
        """Aktualisiert die Trading Pairs zur Laufzeit"""
        self.trading_pairs = new_pairs
        logger.info(f"Trading Pairs aktualisiert: {', '.join(new_pairs)}")
    
    def get_available_symbols(self):
        """Ruft alle verfügbaren Trading-Symbole von Binance ab"""
        try:
            exchange_info = self.binance_client.exchange_info()
            symbols = [symbol['symbol'] for symbol in exchange_info['symbols']
                      if symbol['status'] == 'TRADING' and symbol['symbol'].endswith('USDT')]
            return sorted(symbols)
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der verfügbaren Symbole: {e}")
            return []

async def main():
    """Hauptfunktion"""
    bot = TradingBot()
    
    try:
        await bot.start_bot()
    except KeyboardInterrupt:
        logger.info("Bot wird durch Benutzer gestoppt...")
        await bot.stop_bot()

if __name__ == "__main__":
    asyncio.run(main())

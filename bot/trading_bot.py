import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from dotenv import load_dotenv
from binance.spot import Spot as BinanceClient
from supabase import create_client, Client as SupabaseClient
import pandas as pd

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class TradingBot:
    def __init__(self):
        """Initialisierung des Live Trading Bots"""
        self.is_running = False
        self.trading_pairs = ["BTCUSDT", "ETHUSDT"]  # Default pairs
        self.balance_threshold = 10.0  # Minimum USDT für Trading
        
        # Binance Client (LIVE)
        self._init_binance_client()
        
        # Supabase Client
        self._init_supabase_client()
        
        logger.info("Trading Bot initialisiert - LIVE TRADING AKTIV!")
    
    def _init_binance_client(self):
        """Initialisiert Binance Client für Live Trading"""
        try:
            api_key = os.getenv("BINANCE_API_KEY")
            api_secret = os.getenv("BINANCE_API_SECRET")
            
            if not api_key or not api_secret:
                raise ValueError("Binance API Keys fehlen!")
            
            self.binance_client = BinanceClient(
                api_key=api_key, 
                api_secret=api_secret,
                base_url="https://api.binance.com"  # Live API
            )
            
            # Test der Verbindung
            account = self.binance_client.account()
            logger.info(f"✅ Binance LIVE verbunden - Account Status: {account.get('accountType', 'SPOT')}")
            
        except Exception as e:
            logger.error(f"❌ Binance Client Fehler: {e}")
            self.binance_client = None
    
    def _init_supabase_client(self):
        """Initialisiert Supabase Client"""
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url or not supabase_key:
                logger.warning("Supabase Credentials fehlen - läuft ohne DB")
                self.supabase = None
                return
            
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("✅ Supabase verbunden")
            
        except Exception as e:
            logger.error(f"❌ Supabase Client Fehler: {e}")
            self.supabase = None
    
    async def start_trading(self):
        """Startet den Trading Loop"""
        if not self.binance_client:
            logger.error("Binance Client nicht verfügbar!")
            return
        
        logger.info("🚀 Trading gestartet!")
        self.is_running = True
        
        while self.is_running:
            try:
                await self._trading_cycle()
                await asyncio.sleep(30)  # 30 Sekunden zwischen Checks
                
            except Exception as e:
                logger.error(f"Fehler im Trading Loop: {e}")
                await asyncio.sleep(60)  # Längere Pause bei Fehlern
    
    async def stop_trading(self):
        """Stoppt den Trading Bot"""
        logger.info("🛑 Trading gestoppt!")
        self.is_running = False
    
    async def _trading_cycle(self):
        """Ein Trading-Zyklus"""
        # 1. Portfolio Status prüfen
        portfolio = self.get_portfolio()
        
        # 2. Marktdaten abrufen
        for symbol in self.trading_pairs:
            try:
                market_data = self.get_market_data(symbol)
                
                # 3. Einfache Trading-Logik (Moving Average)
                signal = self._analyze_market(symbol, market_data)
                
                if signal == "BUY":
                    await self._execute_buy(symbol)
                elif signal == "SELL":
                    await self._execute_sell(symbol)
                    
            except Exception as e:
                logger.error(f"Fehler bei {symbol}: {e}")
    
    def _analyze_market(self, symbol: str, market_data: dict) -> str:
        """Einfache Moving Average Strategie"""
        try:
            # Hole historische Daten
            klines = self.binance_client.klines(symbol, "15m", limit=50)
            prices = [float(k[4]) for k in klines]  # Schlusskurse
            
            if len(prices) < 20:
                return "HOLD"
            
            # Moving Averages berechnen
            ma_10 = sum(prices[-10:]) / 10
            ma_20 = sum(prices[-20:]) / 20
            current_price = prices[-1]
            
            # Einfache Signale
            if ma_10 > ma_20 and current_price > ma_10:
                return "BUY"
            elif ma_10 < ma_20 and current_price < ma_10:
                return "SELL"
            
            return "HOLD"
            
        except Exception as e:
            logger.error(f"Markt-Analyse Fehler für {symbol}: {e}")
            return "HOLD"
    
    async def _execute_buy(self, symbol: str):
        """Führt Kauf-Order aus"""
        try:
            # Portfolio prüfen
            account = self.binance_client.account()
            usdt_balance = float([b['free'] for b in account['balances'] if b['asset'] == 'USDT'][0])
            
            if usdt_balance < self.balance_threshold:
                logger.info(f"Zu wenig USDT für {symbol}: {usdt_balance}")
                return
            
            # 5% der Balance oder max 50 USDT
            order_amount = min(usdt_balance * 0.05, 50.0)
            
            if order_amount < 10:  # Minimum Order
                return
            
            # Live Order ausführen
            order = self.binance_client.new_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quoteOrderQty=order_amount
            )
            
            logger.info(f"✅ GEKAUFT: {order_amount} USDT von {symbol} - Order ID: {order['orderId']}")
            
            # In Datenbank loggen
            if self.supabase:
                self._log_trade("BUY", symbol, order_amount, order['orderId'])
            
        except Exception as e:
            logger.error(f"Kauf-Fehler für {symbol}: {e}")
    
    async def _execute_sell(self, symbol: str):
        """Führt Verkauf-Order aus"""
        try:
            # Asset Balance prüfen
            asset = symbol.replace('USDT', '')
            account = self.binance_client.account()
            asset_balance = float([b['free'] for b in account['balances'] if b['asset'] == asset][0])
            
            if asset_balance <= 0:
                return
            
            # Live Order ausführen
            order = self.binance_client.new_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=asset_balance
            )
            
            logger.info(f"✅ VERKAUFT: {asset_balance} {asset} - Order ID: {order['orderId']}")
            
            # In Datenbank loggen
            if self.supabase:
                self._log_trade("SELL", symbol, asset_balance, order['orderId'])
            
        except Exception as e:
            logger.error(f"Verkauf-Fehler für {symbol}: {e}")
    
    def get_portfolio(self) -> dict:
        """Ruft aktuelles Portfolio ab"""
        try:
            account = self.binance_client.account()
            portfolio = {
                "balances": [],
                "total_value_usdt": 0
            }
            
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    portfolio["balances"].append({
                        "asset": balance['asset'],
                        "free": free,
                        "locked": locked,
                        "total": total
                    })
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Portfolio-Fehler: {e}")
            return {"balances": [], "total_value_usdt": 0}
    
    def get_market_data(self, symbol: str) -> dict:
        """Ruft Marktdaten ab"""
        try:
            ticker = self.binance_client.ticker_price(symbol)
            stats = self.binance_client.ticker_24hr(symbol)
            
            return {
                "symbol": symbol,
                "price": float(ticker['price']),
                "change": float(stats['priceChange']),
                "change_percent": float(stats['priceChangePercent']),
                "volume": float(stats['volume']),
                "high": float(stats['highPrice']),
                "low": float(stats['lowPrice'])
            }
            
        except Exception as e:
            logger.error(f"Marktdaten-Fehler für {symbol}: {e}")
            return {}
    
    def update_trading_pairs(self, pairs: List[str]):
        """Aktualisiert Trading Pairs"""
        self.trading_pairs = pairs
        logger.info(f"Trading Pairs aktualisiert: {pairs}")
    
    def get_available_symbols(self) -> List[str]:
        """Ruft verfügbare Symbole ab"""
        try:
            exchange_info = self.binance_client.exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols'] 
                      if s['status'] == 'TRADING' and s['symbol'].endswith('USDT')]
            return sorted(symbols)
        except Exception as e:
            logger.error(f"Symbole-Fehler: {e}")
            return []
    
    def _log_trade(self, side: str, symbol: str, amount: float, order_id: str):
        """Loggt Trade in Supabase"""
        try:
            if not self.supabase:
                return
            
            trade_data = {
                "side": side,
                "symbol": symbol,
                "amount": amount,
                "order_id": order_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            }
            
            self.supabase.table("trades").insert(trade_data).execute()
            
        except Exception as e:
            logger.error(f"Trade-Log Fehler: {e}")

# Für direkte Ausführung
if __name__ == "__main__":
    async def main():
        bot = TradingBot()
        try:
            await bot.start_trading()
        except KeyboardInterrupt:
            await bot.stop_trading()
            logger.info("Bot beendet")
    
    asyncio.run(main())

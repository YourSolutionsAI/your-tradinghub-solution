from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import asyncio
import logging
from datetime import datetime
import json

from main import TradingBot

app = FastAPI(title="Trading Bot API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifische Domains verwenden
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Global Bot Instance
bot_instance: Optional[TradingBot] = None
bot_task: Optional[asyncio.Task] = None

# Pydantic Models
class BotStatusResponse(BaseModel):
    status: str
    last_heartbeat: Optional[str]
    uptime: Optional[str]
    is_trading: bool

class BotControlRequest(BaseModel):
    action: str  # start, stop, restart

class StrategyRequest(BaseModel):
    name: str
    symbol: str
    strategy_type: str
    parameters: Dict[str, Any]
    is_active: bool
    max_order_size: Optional[float] = 100.0

class StrategyUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None
    max_order_size: Optional[float] = None

class ConfigurationRequest(BaseModel):
    key: str
    value: Any
    description: Optional[str] = None

# Authentifizierung (einfache API Key Authentifizierung)
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = os.getenv("API_KEY", "your-secret-api-key")
    if credentials.credentials != api_key:
        raise HTTPException(status_code=401, detail="Ungültiger API Key")
    return credentials

# Health Check
@app.get("/health")
async def health_check():
    """Health Check Endpoint für Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "bot_running": bot_instance is not None and bot_instance.is_running
    }

# Bot Status
@app.get("/api/bot/status", response_model=BotStatusResponse)
async def get_bot_status():
    """Aktuellen Bot-Status abrufen"""
    global bot_instance, bot_task
    
    if bot_instance is None:
        return BotStatusResponse(
            status="stopped",
            last_heartbeat=None,
            uptime=None,
            is_trading=False
        )
    
    return BotStatusResponse(
        status="running" if bot_instance.is_running else "stopped",
        last_heartbeat=datetime.utcnow().isoformat(),
        uptime=None,  # Implementierung für Uptime-Berechnung
        is_trading=bot_instance.is_running
    )

# Bot Kontrolle
@app.post("/api/bot/control")
async def control_bot(
    request: BotControlRequest, 
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Bot starten, stoppen oder neustarten"""
    global bot_instance, bot_task
    
    try:
        if request.action == "start":
            if bot_instance is None:
                bot_instance = TradingBot()
            
            if not bot_instance.is_running:
                bot_task = asyncio.create_task(bot_instance.start_bot())
                return {"message": "Bot wird gestartet", "status": "starting"}
            else:
                return {"message": "Bot läuft bereits", "status": "running"}
                
        elif request.action == "stop":
            if bot_instance and bot_instance.is_running:
                await bot_instance.stop_bot()
                if bot_task:
                    bot_task.cancel()
                return {"message": "Bot wird gestoppt", "status": "stopping"}
            else:
                return {"message": "Bot läuft nicht", "status": "stopped"}
                
        elif request.action == "restart":
            if bot_instance and bot_instance.is_running:
                await bot_instance.stop_bot()
                if bot_task:
                    bot_task.cancel()
            
            bot_instance = TradingBot()
            bot_task = asyncio.create_task(bot_instance.start_bot())
            return {"message": "Bot wird neugestartet", "status": "restarting"}
            
        else:
            raise HTTPException(status_code=400, detail="Ungültige Aktion")
            
    except Exception as e:
        logger.error(f"Fehler bei Bot-Kontrolle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Strategien verwalten
@app.get("/api/strategies")
async def get_strategies():
    """Alle Trading-Strategien abrufen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        strategies = bot_instance.supabase.table("trading_strategies").select("*").execute()
        return strategies.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/strategies")
async def create_strategy(
    strategy: StrategyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Neue Trading-Strategie erstellen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        strategy_data = {
            "name": strategy.name,
            "symbol": strategy.symbol,
            "strategy_type": strategy.strategy_type,
            "parameters": strategy.parameters,
            "is_active": strategy.is_active,
            "max_order_size": strategy.max_order_size
        }
        
        result = bot_instance.supabase.table("trading_strategies").insert(strategy_data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/strategies/{strategy_id}")
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Trading-Strategie aktualisieren"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        update_data = {}
        if strategy_update.is_active is not None:
            update_data["is_active"] = strategy_update.is_active
        if strategy_update.parameters is not None:
            update_data["parameters"] = strategy_update.parameters
        if strategy_update.max_order_size is not None:
            update_data["max_order_size"] = strategy_update.max_order_size
        
        result = bot_instance.supabase.table("trading_strategies").update(update_data).eq("id", strategy_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Strategie nicht gefunden")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Trading-Strategie löschen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        result = bot_instance.supabase.table("trading_strategies").delete().eq("id", strategy_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Strategie nicht gefunden")
            
        return {"message": "Strategie gelöscht"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio-Informationen
@app.get("/api/portfolio")
async def get_portfolio():
    """Aktuelles Portfolio abrufen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        # Aktuelles Portfolio aus Binance abrufen
        account = bot_instance.binance_client.get_account()
        
        portfolio = {
            "balances": [],
            "total_value_usdt": 0
        }
        
        for asset in account['balances']:
            balance = float(asset['free']) + float(asset['locked'])
            if balance > 0:
                portfolio["balances"].append({
                    "asset": asset['asset'],
                    "free": float(asset['free']),
                    "locked": float(asset['locked']),
                    "total": balance
                })
        
        return portfolio
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Marktdaten
@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str):
    """Marktdaten für ein Symbol abrufen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        # Aktuelle Daten von Binance
        ticker = bot_instance.binance_client.get_symbol_ticker(symbol=symbol.upper())
        stats = bot_instance.binance_client.get_ticker(symbol=symbol.upper())
        
        return {
            "symbol": symbol.upper(),
            "price": float(ticker['price']),
            "price_change": float(stats['priceChange']),
            "price_change_percent": float(stats['priceChangePercent']),
            "volume": float(stats['volume']),
            "high": float(stats['highPrice']),
            "low": float(stats['lowPrice'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trades History
@app.get("/api/trades")
async def get_trades(limit: int = 50):
    """Trade-Historie abrufen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        trades = bot_instance.supabase.table("trades").select("*").order("timestamp", desc=True).limit(limit).execute()
        return trades.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Konfiguration
@app.get("/api/config")
async def get_configuration():
    """Bot-Konfiguration abrufen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        config = bot_instance.supabase.table("bot_configuration").select("*").execute()
        return config.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/config")
async def update_configuration(
    config: ConfigurationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Bot-Konfiguration aktualisieren"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        config_data = {
            "key": config.key,
            "value": config.value,
            "description": config.description
        }
        
        result = bot_instance.supabase.table("bot_configuration").upsert(config_data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error Logs
@app.get("/api/logs/errors")
async def get_error_logs(limit: int = 100):
    """Error Logs abrufen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        logs = bot_instance.supabase.table("error_logs").select("*").order("timestamp", desc=True).limit(limit).execute()
        return logs.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Performance Metriken
@app.get("/api/performance")
async def get_performance_metrics():
    """Performance-Metriken abrufen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        metrics = bot_instance.supabase.table("performance_metrics").select("*").order("date", desc=True).limit(30).execute()
        return metrics.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Trading Pairs Management
@app.get("/api/trading-pairs")
async def get_current_trading_pairs():
    """Aktuelle Trading Pairs abrufen"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    return {
        "current_pairs": bot_instance.trading_pairs,
        "available_symbols": bot_instance.get_available_symbols()
    }

@app.put("/api/trading-pairs")
async def update_trading_pairs(
    pairs: List[str],
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Trading Pairs aktualisieren"""
    global bot_instance
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        # Validierung: Überprüfen ob alle Pairs existieren
        available_symbols = bot_instance.get_available_symbols()
        invalid_pairs = [pair for pair in pairs if pair not in available_symbols]
        
        if invalid_pairs:
            raise HTTPException(
                status_code=400, 
                detail=f"Ungültige Trading Pairs: {', '.join(invalid_pairs)}"
            )
        
        # Trading Pairs aktualisieren
        bot_instance.update_trading_pairs(pairs)
        
        return {
            "message": "Trading Pairs erfolgreich aktualisiert",
            "new_pairs": pairs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Startup Event
@app.on_event("startup")
async def startup_event():
    """Bot beim Start der API initialisieren"""
    global bot_instance
    logger.info("API wird gestartet...")
    
    try:
        bot_instance = TradingBot()
        logger.info("Trading Bot initialisiert")
    except Exception as e:
        logger.error(f"Fehler bei Bot-Initialisierung: {e}")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """Bot beim Herunterfahren stoppen"""
    global bot_instance, bot_task
    logger.info("API wird heruntergefahren...")
    
    if bot_instance and bot_instance.is_running:
        await bot_instance.stop_bot()
        
    if bot_task:
        bot_task.cancel()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)

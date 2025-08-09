from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import asyncio
import logging
from datetime import datetime

from trading_bot import TradingBot

# Lifespan Events (Modern FastAPI) - Definition vor App
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI Lifespan Events"""
    global bot_instance
    
    # Startup
    logger.info("🚀 Trading Bot API gestartet")
    try:
        bot_instance = TradingBot()
        logger.info("✅ Trading Bot bereit für Live Trading")
    except Exception as e:
        logger.error(f"❌ Bot Initialisierung fehlgeschlagen: {e}")
    
    yield
    
    # Shutdown
    global bot_task
    logger.info("🛑 API wird heruntergefahren")
    if bot_instance and bot_instance.is_running:
        await bot_instance.stop_trading()
    if bot_task:
        bot_task.cancel()

# App mit Lifespan
app = FastAPI(
    title="Live Trading Bot API",
    description="Professional Trading Bot für Binance Live Trading",
    version="2.0.0",
    lifespan=lifespan
)

# CORS für Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion: spezifische Domains
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
    is_trading: bool
    trading_pairs: List[str]
    last_check: Optional[str]

class TradingControlRequest(BaseModel):
    action: str  # start, stop

class TradingPairsRequest(BaseModel):
    pairs: List[str]

# Auth Check
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = os.getenv("API_KEY", "your-secret-api-key")
    if credentials.credentials != api_key:
        raise HTTPException(status_code=401, detail="Ungültiger API Key")
    return credentials

# Health Check
@app.get("/health")
async def health_check():
    """Health Check für Deployment"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "bot_initialized": bot_instance is not None,
        "bot_running": bot_instance.is_running if bot_instance else False
    }

# Bot Status
@app.get("/api/bot/status", response_model=BotStatusResponse)
async def get_bot_status():
    """Bot Status abrufen"""
    global bot_instance
    
    if not bot_instance:
        return BotStatusResponse(
            status="not_initialized",
            is_trading=False,
            trading_pairs=[],
            last_check=None
        )
    
    return BotStatusResponse(
        status="running" if bot_instance.is_running else "stopped",
        is_trading=bot_instance.is_running,
        trading_pairs=bot_instance.trading_pairs,
        last_check=datetime.utcnow().isoformat()
    )

# Bot Kontrolle
@app.post("/api/bot/control")
async def control_bot(
    request: TradingControlRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Bot starten/stoppen"""
    global bot_instance, bot_task
    
    try:
        if request.action == "start":
            if not bot_instance:
                bot_instance = TradingBot()
            
            if not bot_instance.is_running:
                bot_task = asyncio.create_task(bot_instance.start_trading())
                return {"message": "Trading gestartet", "status": "starting"}
            else:
                return {"message": "Trading läuft bereits", "status": "running"}
        
        elif request.action == "stop":
            if bot_instance and bot_instance.is_running:
                await bot_instance.stop_trading()
                if bot_task:
                    bot_task.cancel()
                return {"message": "Trading gestoppt", "status": "stopped"}
            else:
                return {"message": "Trading läuft nicht", "status": "stopped"}
        
        else:
            raise HTTPException(status_code=400, detail="Ungültige Aktion (start/stop)")
    
    except Exception as e:
        logger.error(f"Bot-Kontrolle Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio
@app.get("/api/portfolio")
async def get_portfolio():
    """Aktuelles Portfolio von Binance"""
    global bot_instance
    
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        portfolio = bot_instance.get_portfolio()
        return portfolio
    except Exception as e:
        logger.error(f"Portfolio Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Marktdaten
@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str):
    """Marktdaten für Symbol"""
    global bot_instance
    
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        market_data = bot_instance.get_market_data(symbol.upper())
        return market_data
    except Exception as e:
        logger.error(f"Marktdaten Fehler für {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Trading Pairs
@app.get("/api/trading-pairs")
async def get_trading_pairs():
    """Aktuelle Trading Pairs und verfügbare Symbole"""
    global bot_instance
    
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    return {
        "current_pairs": bot_instance.trading_pairs,
        "available_symbols": bot_instance.get_available_symbols()
    }

@app.put("/api/trading-pairs")
async def update_trading_pairs(
    request: TradingPairsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)
):
    """Trading Pairs aktualisieren"""
    global bot_instance
    
    if not bot_instance:
        raise HTTPException(status_code=400, detail="Bot nicht initialisiert")
    
    try:
        # Validierung
        available_symbols = bot_instance.get_available_symbols()
        invalid_pairs = [pair for pair in request.pairs if pair not in available_symbols]
        
        if invalid_pairs:
            raise HTTPException(
                status_code=400,
                detail=f"Ungültige Trading Pairs: {', '.join(invalid_pairs)}"
            )
        
        # Update
        bot_instance.update_trading_pairs(request.pairs)
        
        return {
            "message": "Trading Pairs aktualisiert",
            "new_pairs": request.pairs
        }
    
    except Exception as e:
        logger.error(f"Trading Pairs Update Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# Main
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)

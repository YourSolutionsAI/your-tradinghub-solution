#!/usr/bin/env python3
"""
Railway Entry Point für Trading Bot
Startet die FastAPI App aus dem trading-bot Verzeichnis
"""

import sys
import os
from pathlib import Path

# Füge trading-bot Verzeichnis zum Python Path hinzu
trading_bot_dir = Path(__file__).parent / "trading-bot"
sys.path.insert(0, str(trading_bot_dir))

# Wechsle ins trading-bot Verzeichnis
os.chdir(trading_bot_dir)

# Importiere und starte die FastAPI App
if __name__ == "__main__":
    import uvicorn
    from api import app
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine.math_engine import get_historical_data, analyze_technicals
from engine.news_engine import fetch_and_score_news
from typing import Optional
import urllib.request
import json
from engine.db import init_db, log_telemetry

app = FastAPI(title="Nexus Trader API")

@app.on_event("startup")
def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/ping")
def ping():
    return {"status": "ok"}

@app.get("/api/chart/{ticker}")
def get_chart(ticker: str):
    data = get_historical_data(ticker)
    return {"ticker": ticker, "data": data}

@app.get("/api/macro-drivers/{ticker}")
def get_macro_drivers(ticker: str):
    prompt = f"Identify the top 3 macroeconomic or geopolitical drivers that currently affect the stock ticker {ticker}. Return ONLY a comma-separated list of 3 short phrases (e.g., 'WTI Crude Oil, OPEC policy, Geopolitics'). No other text or markdown."
    try:
        url = "http://localhost:11434/api/generate"
        payload = json.dumps({
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False
        }).encode("utf-8")
        
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        return {"drivers": result.get("response", "").strip()}
    except Exception as e:
         print(f"Ollama Macro Error: {e}")
         return {"drivers": ""}

@app.get("/api/signal/{ticker}")
def get_signal(ticker: str, macro: Optional[str] = None, trading_mode: Optional[str] = "day"):
    # 1. Math Data
    math_data = analyze_technicals(ticker)
    math_score = math_data["score"]
    
    # 2. News Data
    news_data = fetch_and_score_news(ticker, macro)
    vader_score = news_data["vader_score"]
    ai_score = news_data["ai_score"]
    
    # 3. Conviction Score (Depends if AI is connected and what Trading Mode is active)
    if isinstance(ai_score, int):
        if trading_mode == "day":
            # Day Trading: Pure Price Action Bias (80/10/10)
            conviction_value = (math_score * 0.8) + (vader_score * 0.1) + (ai_score * 0.1)
        else:
            # Swing Trading: Macro Influenced (40/20/40)
            conviction_value = (math_score * 0.4) + (vader_score * 0.2) + (ai_score * 0.4)
    else:
        if trading_mode == "day":
            # Fallback when AI missing
            conviction_value = (math_score * 0.9) + (vader_score * 0.1)
        else:
            conviction_value = (math_score * 0.6) + (vader_score * 0.4)
    
    if conviction_value >= 65:
        conviction_signal = "STRONG BUY"
    elif conviction_value >= 55:
        conviction_signal = "BUY"
    elif conviction_value <= 35:
        conviction_signal = "STRONG SELL"
    elif conviction_value <= 45:
        conviction_signal = "SELL"
    else:
        conviction_signal = "HOLD"
        
    payload = {
        "ticker": ticker,
        "macro": macro if macro else "",
        "math": math_data,
        "news": news_data,
        "conviction": {
            "score": round(conviction_value, 2),
            "signal": conviction_signal
        }
    }
    
    # Asynchronously log to SQLite
    log_telemetry(payload)
    
    return payload

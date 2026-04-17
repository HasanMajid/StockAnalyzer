from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from engine.math_engine import get_historical_data, analyze_technicals
from engine.news_engine import fetch_and_score_news

app = FastAPI(title="Nexus Trader API")

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

@app.get("/api/signal/{ticker}")
def get_signal(ticker: str):
    # 1. Math Data
    math_data = analyze_technicals(ticker)
    math_score = math_data["score"]
    
    # 2. News Data
    news_data = fetch_and_score_news(ticker)
    vader_score = news_data["vader_score"]
    ai_score = news_data["ai_score"]
    
    # 3. Conviction Score (Depends if AI is connected)
    if isinstance(ai_score, int):
        # 40% Math, 20% VADER, 40% AI
        conviction_value = (math_score * 0.4) + (vader_score * 0.2) + (ai_score * 0.4)
    else:
        # 60% Math, 40% VADER (fallback when AI missing)
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
        
    return {
        "ticker": ticker,
        "math": math_data,
        "news": news_data,
        "conviction": {
            "score": round(conviction_value, 2),
            "signal": conviction_signal
        }
    }

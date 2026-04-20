import yfinance as yf
import pandas as pd

def get_historical_data(ticker: str, period="5d", interval="15m"):
    """
    Fetches historical OHLC data optimized for Lightweight Charts.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            return []

        # Convert to lightweight charts format: { time: string, open, high, low, close }
        formatted_data = []
        for index, row in df.iterrows():
            # index is a pandas Timestamp.
            # Lightweight charts expects time in 'YYYY-MM-DD' or timestamp in seconds.
            formatted_data.append({
                "time": int(index.timestamp()) if hasattr(index, 'timestamp') else str(index.date()),
                "open": round(row['Open'], 4),
                "high": round(row['High'], 4),
                "low": round(row['Low'], 4),
                "close": round(row['Close'], 4)
            })
            
        return formatted_data
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return []

def analyze_technicals(ticker: str) -> dict:
    """
    Computes a Math Score based on 15m short-term price action and geometry.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="5d", interval="15m")
        
        if df.empty or len(df) < 14:
            return {"score": 50, "signal": "HOLD", "current_price": 0.0, "change_pct": 0.0, "volatility": "Unknown", "pattern": "None"}
            
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100
        
        # Simple RSI (14-period)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # Simple moving average comparisons
        sma_5 = df['Close'].rolling(window=5).mean().iloc[-1]
        
        math_score = 50
        
        if rsi < 35: math_score += 20 # Oversold (Bullish)
        elif rsi > 65: math_score -= 20 # Overbought (Bearish)
            
        if current_price > sma_5: math_score += 10 # Short-term momentum
        else: math_score -= 10
        # Candlestick Pattern Recognition (Price Action Morphology)
        o1, c1, h1, l1 = df['Open'].iloc[-1], df['Close'].iloc[-1], df['High'].iloc[-1], df['Low'].iloc[-1]
        o2, c2, h2, l2 = df['Open'].iloc[-2], df['Close'].iloc[-2], df['High'].iloc[-2], df['Low'].iloc[-2]
        
        body1 = abs(o1 - c1)
        range1 = h1 - l1
        upper_wick1 = h1 - max(o1, c1)
        lower_wick1 = min(o1, c1) - l1
        body2 = abs(o2 - c2)
        
        pattern = "None"
        if range1 > 0:
            if lower_wick1 > (2 * body1) and upper_wick1 < (0.2 * body1):
                pattern = "Bullish Hammer"
                math_score += 15
            elif upper_wick1 > (2 * body1) and lower_wick1 < (0.2 * body1):
                pattern = "Bearish Shooting Star"
                math_score -= 15
            elif c2 < o2 and c1 > o1 and o1 <= c2 and c1 >= o2 and body1 > body2:
                pattern = "Bullish Engulfing"
                math_score += 15
            elif c2 > o2 and c1 < o1 and o1 >= c2 and c1 <= o2 and body1 > body2:
                pattern = "Bearish Engulfing"
                math_score -= 15
            elif body1 < (0.1 * range1):
                pattern = "Doji"

        # Volatility metric (Rough Bollinger band width width proxy via standard dev)
        std_dev = df['Close'].rolling(window=14).std().iloc[-1]
        volatility = "High" if std_dev / current_price > 0.005 else "Low" # Scaled down for 15m

        # Bound score 0-100
        math_score = max(0, min(100, math_score))
        
        signal = "BUY" if math_score >= 65 else ("SELL" if math_score <= 35 else "HOLD")
        
        if pd.isna(math_score) or pd.isna(current_price): return {"score": 50, "signal": "HOLD", "current_price": 0.0, "change_pct": 0.0, "volatility": "Unknown", "pattern": "None"}

        return {
            "score": int(math_score),
            "signal": signal,
            "current_price": round(current_price, 2),
            "change_pct": round(change_pct, 2),
            "volatility": volatility,
            "pattern": pattern
        }
        
    except Exception as e:
        print(f"Error in technical analysis: {e}")
        return {"score": 50, "signal": "HOLD", "current_price": 0.0, "change_pct": 0.0, "volatility": "Unknown"}

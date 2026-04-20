import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "nexus_telemetry.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT,
            macro TEXT,
            current_price REAL,
            math_score INTEGER,
            math_pattern TEXT,
            ai_score INTEGER,
            vader_score INTEGER,
            conviction_score REAL,
            signal_type TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_telemetry(payload):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        ticker = payload.get("ticker", "UNKNOWN")
        macro = payload.get("macro", "")
        
        # Safe extraction from nested mathematical dictionary
        math_data = payload.get("math", {})
        price = math_data.get("current_price", 0.0)
        m_score = math_data.get("score", 50)
        m_pattern = math_data.get("pattern", "None")
        
        # Safe extraction from news dictionary
        news_data = payload.get("news", {})
        ai_score_raw = news_data.get("ai_score", 50)
        ai_score = int(ai_score_raw) if isinstance(ai_score_raw, int) else 50
        v_score = news_data.get("vader_score", 50)
        
        # Conviction extraction
        conv_data = payload.get("conviction", {})
        c_score = conv_data.get("score", 50.0)
        s_type = conv_data.get("signal", "HOLD")
        
        cursor.execute('''
            INSERT INTO signal_logs (ticker, macro, current_price, math_score, math_pattern, ai_score, vader_score, conviction_score, signal_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticker, macro, price, m_score, m_pattern, ai_score, v_score, c_score, s_type
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Telemetry logging error: {e}")

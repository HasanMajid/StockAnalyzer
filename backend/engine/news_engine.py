import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import os
from google import genai
from dotenv import load_dotenv
import json

load_dotenv()
analyzer = SentimentIntensityAnalyzer()

# Configure Gemini if API key is present
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    client = genai.Client(api_key=GEMINI_KEY)

def analyze_with_llm(headlines: list):
    """Passes headlines to Gemini to return a score and short reasoning."""
    if not GEMINI_KEY:
        return {"score": "NO_API_KEY", "reasoning": ""}
    if not headlines:
        return {"score": 50, "reasoning": "No news to analyze."}
        
    try:
        prompt = f"""
        You are an expert day trader evaluating the immediate short-term impact of the following breaking news headlines on the stock it refers to (typically an energy company).
        Rate the overall sentiment from 0 (Extremely Bearish/Sell) to 100 (Extremely Bullish/Buy). 50 is Neutral.
        Respond with ONLY a valid JSON object in this exact format: {{"score": 75, "reasoning": "Brief 1-sentence explanation of why."}}
        
        Headlines:
        {json.dumps(headlines)}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        # Parse JSON
        text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(text)
        return {"score": data.get("score", 50), "reasoning": data.get("reasoning", "")}
    except Exception as e:
        print(f"LLM API Error: {e}")
        return {"score": "ERROR", "reasoning": str(e)}

def fetch_and_score_news(ticker: str):
    """
    Fetches news, scores individually with VADER, and sends aggregate to Gemini LLM.
    """
    print(f"Fetching news for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        raw_news = stock.news
        
        if not raw_news:
            return {"articles": [], "vader_score": 50, "ai_score": 50, "aggregate_score": 50}
            
        parsed_articles = []
        total_compound = 0
        headline_list = []
        
        for item in raw_news[:10]:
            title = item.get("title", "")
            publisher = item.get("publisher", "Unknown")
            link = item.get("link", "#")
            
            headline_list.append(title)
            sentiment_dict = analyzer.polarity_scores(title)
            compound = sentiment_dict['compound'] 
            total_compound += compound
            
            if compound >= 0.05:
                tag = "bullish"
            elif compound <= -0.05:
                tag = "bearish"
            else:
                tag = "neutral"
                
            parsed_articles.append({
                "id": item.get("uuid", str(time.time())),
                "source": publisher,
                "title": title,
                "sentiment": tag,
                "link": link,
                "time": "Recent"
            })
            
        # VADER Math
        avg_compound = total_compound / len(parsed_articles)
        vader_score = int(((avg_compound + 1) / 2) * 100)
        
        # AI LLM Math
        ai_data = analyze_with_llm(headline_list)
        ai_score = ai_data.get("score", 50)
        ai_reasoning = ai_data.get("reasoning", "")
        
        try:
            agg = int((vader_score + ai_score) / 2) if isinstance(ai_score, int) else vader_score
        except:
            agg = vader_score
        
        return {
            "articles": parsed_articles,
            "vader_score": vader_score,
            "ai_score": ai_score,
            "ai_reasoning": ai_reasoning,
            # We provide a blended aggregate just in case
            "aggregate_score": agg
        }
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return {"articles": [], "vader_score": 50, "ai_score": 50, "aggregate_score": 50}

import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time

analyzer = SentimentIntensityAnalyzer()

def fetch_and_score_news(ticker: str):
    """
    Fetches news from Yahoo Finance and scores it using VADER sentiment analysis.
    Returns a list of parsed articles and an aggregate sentiment score.
    """
    try:
        stock = yf.Ticker(ticker)
        # yfinance news returns a list of dictionaries
        raw_news = stock.news
        
        if not raw_news:
            return {"articles": [], "aggregate_score": 50}
            
        parsed_articles = []
        total_compound = 0
        
        for item in raw_news[:10]: # Top 10 latest
            title = item.get("title", "")
            publisher = item.get("publisher", "Unknown")
            link = item.get("link", "#")
            
            # Use VADER on the title (financial headlines are very dense)
            sentiment_dict = analyzer.polarity_scores(title)
            compound = sentiment_dict['compound'] # Ranges from -1 to 1
            
            total_compound += compound
            
            # Map to bullish/bearish/neutral
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
                "time": "Recent" # yf provides publish time as unix timestamp, but 'Recent' is fine for MVP
            })
            
        # Normalize aggregate score to 0 - 100 where 50 is neutral
        avg_compound = total_compound / len(parsed_articles)
        # avg_compound is -1 to +1. 
        # Map: -1 -> 0, 0 -> 50, +1 -> 100
        aggregate_score = int(((avg_compound + 1) / 2) * 100)
        
        return {
            "articles": parsed_articles,
            "aggregate_score": aggregate_score
        }
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return {"articles": [], "aggregate_score": 50}

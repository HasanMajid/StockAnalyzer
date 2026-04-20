import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import json
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import quote
import email.utils
import datetime

analyzer = SentimentIntensityAnalyzer()

def analyze_with_llm(articles_data: list):
    """Passes headlines and publication dates to Local Ollama to return a score and short reasoning."""
    if not articles_data:
        return {"score": 50, "reasoning": "No news to analyze."}
        
    try:
        prompt = f"""
        You are an expert day trader evaluating the immediate short-term impact of the following breaking news headlines on the stock it refers to.
        Rate the overall sentiment from 0 (Extremely Bearish/Sell) to 100 (Extremely Bullish/Buy). 50 is Neutral.
        CRITICAL: Notice the publication date of each article. Discount the impact of old news mathematically. News older than 48 hours should carry drastically less conviction.
        Respond with ONLY a valid JSON object in this exact format: {{"score": 75, "reasoning": "Brief 1-sentence explanation of why."}}
        
        Headlines and Publication Dates:
        {json.dumps(articles_data)}
        """
        
        url = "http://localhost:11434/api/generate"
        payload = json.dumps({
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }).encode("utf-8")
        
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req)
        response_body = response.read().decode('utf-8')
        
        # Parse JSON
        result = json.loads(response_body)
        text = result.get("response", "{}").strip()
        data = json.loads(text)
        
        return {"score": data.get("score", 50), "reasoning": data.get("reasoning", "")}
    except Exception as e:
        print(f"Ollama API Error: {e}")
        return {"score": "ERROR", "reasoning": str(e)}

def fetch_rss_news(query_string: str) -> list:
    """Helper to fetch from Google News RSS"""
    query_encoded = quote(query_string)
    url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en-CA&gl=CA&ceid=CA:en"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response_xml = urllib.request.urlopen(req).read()
        root = ET.fromstring(response_xml)
        return root.findall('./channel/item')
    except Exception as e:
        print(f"RSS Fetch Error: {e}")
        return []

def fetch_and_score_news(ticker: str, macro: str = None):
    """
    Fetches exact company news + macro drivers, enforces strict time limits, scores individually with VADER, and sends aggregate to LLM.
    """
    print(f"Fetching news for {ticker} via Google News (with macros: {macro})...")
    try:
        # Extract precise company name natively
        try:
            stock_info = yf.Ticker(ticker).info
            company_name = stock_info.get("shortName", "")
            if company_name:
                company_name = company_name.split(",")[0].replace("Corp.", "").replace("Inc.", "").strip()
        except:
            company_name = ""
            
        # Build Boolean queries natively forcing only stock/financial news
        base_query = f'"{ticker}"'
        if company_name:
             base_query += f' OR "{company_name}"'
             
        primary_query = f'({base_query}) (stock OR TSX OR energy) when:7d'
        
        # Dual scrape execution
        primary_items = fetch_rss_news(primary_query)
        macro_items = []
        if macro:
            macro_query = f'({macro.replace(",", " OR ")}) when:3d'
            macro_items = fetch_rss_news(macro_query)
        
        all_items = [(i, False) for i in primary_items] + [(i, True) for i in macro_items]
        
        if not all_items:
            return {"articles": [], "vader_score": 50, "ai_score": 50, "aggregate_score": 50}
            
        parsed_articles = []
        total_compound = 0
        vader_counted = 0
        ai_payload = []
        seen_titles = set()
        
        for item, is_macro in all_items:
            title = item.find('title').text if item.find('title') is not None else ""
            if not title or title in seen_titles: continue
            
            seen_titles.add(title)
            
            publisher = item.find('source').text if item.find('source') is not None else "Google News"
            link = item.find('link').text if item.find('link') is not None else "#"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else "Recent"
            
            # Parse accurate temporal relativity
            try:
                dt = email.utils.parsedate_to_datetime(pub_date)
                now = datetime.datetime.now(datetime.timezone.utc)
                hours_ago = int((now - dt).total_seconds() / 3600)
                if hours_ago < 24:
                    formatted_time = f"Published {hours_ago} hours ago"
                else:
                    formatted_time = f"Published {hours_ago // 24} days ago"
            except:
                formatted_time = "Recent"
            
            ai_payload.append({
                "headline": title,
                "date": formatted_time
            })
            
            tag = "neutral"
            
            # Conditionally Bypass VADER dictionary logic for Macro inputs
            if not is_macro:
                sentiment_dict = analyzer.polarity_scores(title)
                compound = sentiment_dict['compound'] 
                total_compound += compound
                vader_counted += 1
                
                if compound >= 0.05:
                    tag = "bullish"
                elif compound <= -0.05:
                    tag = "bearish"
            else:
                tag = "neutral" # Visually uncolored tag for purely macro items
                
            parsed_articles.append({
                "id": str(time.time()) + title[:5],
                "source": publisher,
                "title": title,
                "sentiment": tag,
                "link": link,
                "time": formatted_time
            })
            
            # Limit strictly to the top 15 parsed articles
            if len(parsed_articles) >= 15:
                break
                
        # VADER Math Calculation (only against counted items)
        if vader_counted > 0:
            avg_compound = total_compound / vader_counted
            vader_score = int(((avg_compound + 1) / 2) * 100)
        else:
            vader_score = 50
        
        # AI LLM Math (Now receives timestamps natively)
        ai_data = analyze_with_llm(ai_payload)
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
            "aggregate_score": agg
        }
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return {"articles": [], "vader_score": 50, "ai_score": 50, "aggregate_score": 50}

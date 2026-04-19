from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
# Initialize analyzer
analyzer = SentimentIntensityAnalyzer()


# stock = yf.Ticker("CJ.TO")
stock = yf.Ticker("Cardinal Energy")

news = stock.news
print(news)

# Test sentence
sentence = "CJ.TO"
vs = analyzer.polarity_scores('Iran war live: IRGC says Hormuz closed until US blockade lifted')

# Output results
print(f"Sentence: {sentence}")
print(f"Scores: {vs}")
# Example Output: {'neg': 0.0, 'neu': 0.254, 'pos': 0.746, 'compound': 0.8316}


'''
Sentence: U.S. and Iran war is bad, but I am bullish on oil prices.
Scores: {'neg': 0.299, 'neu': 0.701, 'pos': 0.0, 'compound': -0.5719}


Sentence: strait of hormuz, should i buy CJ stock (cardinal energy).
Scores: {'neg': 0.0, 'neu': 0.811, 'pos': 0.189, 'compound': 0.2732}

Sentence: strait of hormuz
Scores: {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}

Sentence: U.S. and Iran
Scores: {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}

Sentence: U.S. and Iran war.
Scores: {'neg': 0.565, 'neu': 0.435, 'pos': 0.0, 'compound': -0.5994}

CIBC Changes Estimates for Some North American Energy Equities
Sentence: CJ.TO
Scores: {'neg': 0.0, 'neu': 0.792, 'pos': 0.208, 'compound': 0.2732}

Does Record Q4 Output and Weaker Earnings Shift the Bull Case For Cardinal Energy (TSX:CJ)?
Sentence: CJ.TO
Scores: {'neg': 0.161, 'neu': 0.722, 'pos': 0.117, 'compound': -0.2023}

Does Record Q4 Output and Weaker Earnings Shift the Bull Case For Cardinal Energy (TSX:CJ)?
Sentence: CJ.TO
Scores: {'neg': 0.161, 'neu': 0.722, 'pos': 0.117, 'compound': -0.2023}

Cardinal Energy (TSX:CJ) Valuation After Upsized Equity Raise And Reford 2 Growth Plans
Sentence: CJ.TO
Scores: {'neg': 0.0, 'neu': 0.701, 'pos': 0.299, 'compound': 0.5719}

'''

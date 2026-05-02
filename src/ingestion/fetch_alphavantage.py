import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Loading API key from .env
load_dotenv()
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

def fetch_alpha_vantage_data(symbol="SPY"):
    print(f"Fetching data for {symbol} via Alpha Vantage...")
    os.makedirs('data', exist_ok=True)

    #Fetching Time-Series Market Data
    ts_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    ts_response = requests.get(ts_url).json()

    if "Time Series (Daily)" in ts_response:
        ts_data = ts_response["Time Series (Daily)"]
        df_ts = pd.DataFrame.from_dict(ts_data, orient='index')
        df_ts.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df_ts.index.name = 'Date'
        df_ts = df_ts.apply(pd.to_numeric) # Convert strings to floats

        # targets
        df_ts['Price_Movement'] = df_ts['Close'] - df_ts['Open']
        df_ts['Direction'] = df_ts['Price_Movement'].apply(lambda x: 'Up' if x > 0 else 'Down')
        df_ts['Volatility'] = df_ts['High'] - df_ts['Low']

        df_ts.to_csv('data/av_timeseries.csv')
        print("Saved Alpha Vantage Time-Series data.")
    else:
        print("Error fetching time-series. (Check API limits)")

    #Fetching News & Sentiment Data
    news_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={API_KEY}"
    news_response = requests.get(news_url).json()

    if "feed" in news_response:
        news_data = []
        for item in news_response["feed"]:

            score = float(item.get("overall_sentiment_score", 0))
            

            if score >= 0.15: sentiment = "Positive"
            elif score <= -0.15: sentiment = "Negative"
            else: sentiment = "Neutral"

            news_data.append({
                "Date": item["time_published"],
                "Headline": item["title"],
                "Sentiment": sentiment
            })

        df_news = pd.DataFrame(news_data)
        df_news.to_csv('data/av_news_sentiment.csv', index=False)
        print("Saved Alpha Vantage News & Sentiment data.")
    else:
        print("Error fetching news. (Check API limits)")

if __name__ == "__main__":
    fetch_alpha_vantage_data()

import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Loading API key from .env
load_dotenv()
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

def fetch_alpha_vantage_data(symbol="SPY"):
    print(f"Fetching time-series data for {symbol} via Alpha Vantage...")
    os.makedirs('data', exist_ok=True)

    #Fetch Time-Series Market Data
    ts_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    ts_response = requests.get(ts_url).json()

    if "Time Series (Daily)" in ts_response:
        ts_data = ts_response["Time Series (Daily)"]
        df_ts = pd.DataFrame.from_dict(ts_data, orient='index')
        df_ts.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df_ts.index.name = 'Date'
        df_ts = df_ts.apply(pd.to_numeric)

        #targets
        df_ts['Price_Movement'] = df_ts['Close'] - df_ts['Open']
        df_ts['Direction'] = df_ts['Price_Movement'].apply(lambda x: 'Up' if x > 0 else 'Down')
        df_ts['Volatility'] = df_ts['High'] - df_ts['Low']

        df_ts.to_csv('data/av_timeseries.csv')
        print("Saved Alpha Vantage Time-Series data.")
    else:
        
        print(f"Error fetching time-series: {ts_response}")

if __name__ == "__main__":
    fetch_alpha_vantage_data()

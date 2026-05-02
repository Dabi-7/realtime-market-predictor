import yfinance as yf
import pandas as pd
import os

def fetch_market_data(ticker="^GSPC", start="2020-01-01", end="2026-05-01"):
    print(f"Fetching data for {ticker}...")
    # Fetch data from Yahoo Finance
    df = yf.download(ticker, start=start, end=end)
    
    # Calculate daily price movement (True if Close > Open, False otherwise)
    df['Price_Movement'] = df['Close'] - df['Open']
    df['Direction'] = df['Price_Movement'].apply(lambda x: 'Up' if x > 0 else 'Down')
    
    # Calculate Volatility (High - Low)
    df['Volatility'] = df['High'] - df['Low']
    
    # Save to the DVC-tracked data folder
    os.makedirs('data', exist_ok=True)
    output_path = 'data/yahoo_finance_historical.csv'
    df.to_csv(output_path)
    print(f"Saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    fetch_market_data()

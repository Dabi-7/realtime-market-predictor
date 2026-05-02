import feedparser
import pandas as pd
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def classify_sentiment(text, analyzer):
    # Get the compound score from VADER
    score = analyzer.polarity_scores(text)['compound']
    
    # Map to exactly 3 classes as required: Positive, Negative, Neutral
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def fetch_rss_news():
    print("Fetching RSS feeds...")
    # Using Yahoo Finance RSS as a reliable alternative if Reuters is blocking
    rss_url = "https://finance.yahoo.com/news/rssindex"
    feed = feedparser.parse(rss_url)
    
    analyzer = SentimentIntensityAnalyzer()
    news_data = []
    
    for entry in feed.entries:
        title = entry.title
        published = entry.published
        sentiment = classify_sentiment(title, analyzer)
        
        news_data.append({
            "Date": published,
            "Headline": title,
            "Sentiment": sentiment
        })
        
    df = pd.DataFrame(news_data)
    
    # Save to the DVC-tracked data folder
    os.makedirs('data', exist_ok=True)
    output_path = 'data/rss_news_sentiment.csv'
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} labeled headlines to {output_path}")

if __name__ == "__main__":
    fetch_rss_news()

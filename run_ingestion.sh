#!/bin/bash

set -e

echo "starting data ingestion pipeline.........."

echo "Running Yahoo finance & RSS scrpers..........."

python src/ingestion/fetch_prices.py
python src/ingestion/fetch_news.py

echo "Running alph vangatage script........."
python src/ingestion/fetch_alphavantage.py

echo "Tracking new data with dvc......"

dvc add data/yahoo_finance_historical.csv
dvc add data/rss_news_sentiment.csv
dvc add data/av_timeseries.csv
dvc add data/av_news_sentiment.csv

echo "pushing updates to github"
git add data/*.csv
git commit -m "feat: added alphavantage to ingestion pipeline to bypass reddit api blocker"

git push origin main

echo "pipeline execution completed......."

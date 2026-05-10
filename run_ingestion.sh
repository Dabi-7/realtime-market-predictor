#!/bin/bash
set -e

echo "starting data ingestion pipeline.........."

echo "Running Yahoo finance & RSS scrpers..........."
python src/ingestion/fetch_prices.py
python src/ingestion/fetch_news.py

echo "Running alph vangatage script........."
python src/ingestion/fetch_alphavantage.py

echo "pipeline execution completed......."

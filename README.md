# Real-Time Market Movement Prediction System 📈

This project implements a complete machine learning pipeline to predict the direction of financial markets (Up/Down). It integrates market data with sentiment analysis from news feeds and compares three different sequential deep learning architectures.

## Overview
Predicting market trends is a complex task. This system approaches it by combining:
1.  **Technical Indicators:** Price, Volume, and Volatility data.
2.  **Sentiment Analysis:** Daily aggregated sentiment scores from global news headlines.
3.  **Sequential Modeling:** Utilizing RNNs, LSTMs, and GRUs to capture temporal dependencies in the data.

##  Tech Stack
- **Languages:** Python 3.x
- **Deep Learning:** TensorFlow / Keras
- **Experiment Tracking:** MLflow
- **Data Manipulation:** Pandas, NumPy
- **Preprocessing:** Scikit-Learn (MinMaxScaler)

##  Models Compared
The system trains and evaluates three models to find the best performer:
* **Simple RNN:** The baseline for sequential data.
* **LSTM (Long Short-Term Memory):** Designed to prevent the vanishing gradient problem and remember long-term trends.
* **GRU (Gated Recurrent Unit):** A streamlined, faster version of LSTM that often provides comparable performance.

##  Experiment Tracking (MLflow)
We use **MLflow** to track every training run. This allows us to monitor:
- **Metrics:** Accuracy, F1-Score, and RMSE.
- **Hyperparameters:** Lookback window size (10 days), batch size, and epochs.
- **Model Registry:** Automated saving of `.keras` model artifacts for deployment.

### How to View the Dashboard
1. Ensure the project has been run and the `mlruns` directory exists.
2. Run the following command in your terminal:
   ```bash
   mlflow ui
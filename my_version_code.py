import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, GRU, SimpleRNN, Dropout, Input
import mlflow
import mlflow.keras

#setting up mlflow and directories
# Ensure the API output folder exists
os.makedirs("final_weights", exist_ok=True)

# Use the Docker service name for MLflow, fallback to localhost for local testing
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment("RealTime_Market_Prediction")

#data ingestion
yahoo_df = pd.read_csv("yahoo_finance_historical.csv")
news_df = pd.read_csv("rss_news_sentiment.csv")
av_df = pd.read_csv("av_timeseries.csv")

sentiment_map = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
news_df['Sentiment'] = news_df['Sentiment'].map(sentiment_map)

if av_df['Direction'].dtype == 'object':
    direction_map = {'Up': 1, 'Down': 0, '1': 1, '0': 0}
    av_df['Direction'] = av_df['Direction'].map(direction_map)

news_df['Date'] = pd.to_datetime(news_df['Date']).dt.tz_localize(None)
av_df['Date'] = pd.to_datetime(av_df['Date']).dt.tz_localize(None)

daily_sentiment = news_df.groupby('Date')['Sentiment'].mean().reset_index()
df = pd.merge(av_df, daily_sentiment, on='Date', how='left')

df['Sentiment'] = df['Sentiment'].fillna(0)
features = ['Open', 'High', 'Low', 'Close', 'Volume', 'Volatility', 'Sentiment']
target = 'Direction'

df = df.dropna(subset=[target])
df[features] = df[features].apply(pd.to_numeric, errors='coerce').astype('float32')
df[target] = pd.to_numeric(df[target], errors='coerce').astype('float32')

df = df.sort_values('Date').set_index('Date')

#scaling
scaler = MinMaxScaler()
scaled_features = scaler.fit_transform(df[features])

#exporting the scalar file
joblib.dump(scaler, "final_weights/scaler.pkl")
print("Scaler exported to final_weights/scaler.pkl")

# sequence generation
def create_sequences(data, target_data, window_size=10):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:(i + window_size)])
        y.append(target_data.iloc[i + window_size])
    return np.array(X, dtype='float32'), np.array(y, dtype='float32')

WINDOW_SIZE = 10
X, y = create_sequences(scaled_features, df[target], WINDOW_SIZE)

split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

def build_sequential_model(model_type='LSTM'):
    model = Sequential()
    model.add(Input(shape=(WINDOW_SIZE, len(features))))
    
    if model_type == 'RNN':
        model.add(SimpleRNN(64, return_sequences=False))
    elif model_type == 'LSTM':
        model.add(LSTM(64, return_sequences=False))
    elif model_type == 'GRU':
        model.add(GRU(64, return_sequences=False))
    
    model.add(Dropout(0.2))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

#training and mlflow tracking
model_names = ['RNN', 'LSTM', 'GRU']
performance = {}

for name in model_names:
    with mlflow.start_run(run_name=f"Execution_{name}"):
        print(f"\n--- Training and Logging {name} ---")
        
        mlflow.log_param("architecture", name)
        mlflow.log_param("window_size", WINDOW_SIZE)
        mlflow.log_param("features_count", len(features))
        mlflow.log_param("epochs", 15)
        
        model = build_sequential_model(name)
        history = model.fit(X_train, y_train, epochs=15, batch_size=16, verbose=1, validation_split=0.1)
        
        for epoch, loss in enumerate(history.history['loss']):
            mlflow.log_metric("train_loss", loss, step=epoch)
        
        y_probs = model.predict(X_test)
        y_preds = (y_probs > 0.5).astype(int)
        
        acc = accuracy_score(y_test, y_preds)
        f1 = f1_score(y_test, y_preds)
        rmse = np.sqrt(mean_squared_error(y_test, y_probs))
        
        mlflow.log_metric("test_accuracy", acc)
        mlflow.log_metric("test_f1", f1)
        mlflow.log_metric("test_rmse", rmse)
        
        # Log to MLflow UI
        mlflow.keras.log_model(model, name=f"MarketModel_{name}")
        
        # exporting file for backend api container
        file_path = f"final_weights/{name.lower()}.keras"
        model.save(file_path)
        print(f"Exported {name} model to {file_path}")
        
        performance[name] = {'Accuracy': acc, 'F1-Score': f1, 'RMSE': rmse}

print("\nFinal Results Table:")
print(pd.DataFrame(performance).T)

## Real-Time Market Movement Prediction (MLOps Project)

End-to-end MLOps pipeline that ingests market + news data, trains sequential deep-learning models (RNN/LSTM/GRU) to predict next-day market direction (Up/Down), and serves predictions via a FastAPI backend with a Streamlit frontend. Orchestration is done with Apache Airflow.

### What’s in this repo
- **Airflow DAG**: `dags/market_pipeline.py` schedules ingestion → training → (placeholder) deployment.
- **Ingestion scripts**: `src/ingestion/` fetch Yahoo Finance prices, Yahoo Finance RSS headlines (VADER sentiment), and Alpha Vantage daily time series.
- **Training**: `my_version_code.py` merges data, builds 10-day sequences, trains RNN/LSTM/GRU, and exports model weights + scaler.
- **Backend API**: `api/main.py` loads exported `.keras` models + `scaler.pkl` and exposes `/predict`.
- **Frontend**: `frontend/app.py` provides an interactive 10-day input grid or CSV upload and calls the API.

---

## Architecture (high level)

1. **Ingestion** (`run_ingestion.sh`)
    - `src/ingestion/fetch_prices.py` → `data/yahoo_finance_historical.csv`
    - `src/ingestion/fetch_news.py` → `data/rss_news_sentiment.csv`
    - `src/ingestion/fetch_alphavantage.py` → `data/av_timeseries.csv`
2. **Training** (`my_version_code.py`)
    - Builds sliding windows of **10 days** over these features:
       `Open, High, Low, Close, Volume, Volatility, Sentiment`
    - Exports to `final_weights/`:
       - `rnn.keras`, `lstm.keras`, `gru.keras`
       - `scaler.pkl`
3. **Serving**
    - FastAPI loads the artifacts and returns direction + probability.
    - Streamlit UI sends a `(1, 10, 7)` payload to the backend.

---

## Quickstart (recommended): Docker Compose

### Prerequisites
- Docker + Docker Compose

### 1) Set environment variables

Alpha Vantage ingestion requires an API key.

Create a `.env` file in the repo root:

```bash
ALPHAVANTAGE_API_KEY=your_key_here
```

### 2) Build and start everything

```bash
docker compose up --build
```

This starts:
- **Airflow**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **Frontend (Streamlit)**: http://localhost:8501

Airflow runs in **standalone** mode. The admin password is printed in the Airflow container logs; in this repo there’s also a local dev helper file `standalone_admin_password.txt` (treat it as a secret for your machine).

### 3) Run the pipeline

In the Airflow UI, enable and trigger the DAG:
- DAG id: `market_prediction_pipeline`

The DAG runs:
1) `./run_ingestion.sh`
2) `python my_version_code.py`
3) a placeholder “deployment trigger” step

After training completes, updated artifacts will be available in `final_weights/`, and the API will use them (the Compose file mounts `./final_weights` into the API container).

---

## API usage

### Health check

```bash
curl http://localhost:8000/
```

### Prediction

Endpoint: `POST /predict`

Payload format (note the **nested shape**):

```json
{
   "features": [
      [
         [Open, High, Low, Close, Volume, Volatility, Sentiment],
         [Open, High, Low, Close, Volume, Volatility, Sentiment]
         // ... 10 rows total
      ]
   ],
   "model_choice": "LSTM"
}
```

Example:

```bash
curl -X POST http://localhost:8000/predict \
   -H 'Content-Type: application/json' \
   -d '{"features": [[[1,2,0.5,1.5,1000,1.5,0],[1,2,0.5,1.6,1100,1.5,0],[1,2,0.5,1.7,1200,1.5,0],[1,2,0.5,1.8,1300,1.5,0],[1,2,0.5,1.9,1400,1.5,0],[1,2,0.5,2.0,1500,1.5,0],[1,2,0.5,2.1,1600,1.5,0],[1,2,0.5,2.2,1700,1.5,0],[1,2,0.5,2.3,1800,1.5,0],[1,2,0.5,2.4,1900,1.5,0]]],"model_choice":"LSTM"}'
```

Response:

```json
{
   "predicted_direction": "Up",
   "probability_up": 0.73,
   "model_used": "LSTM"
}
```

---

## Frontend (Streamlit)

Open http://localhost:8501

The UI supports:
- Manual editing of the 10-day grid
- Uploading a CSV containing the required columns:
   `Open, High, Low, Close, Volume, Volatility, Sentiment`

Inside Docker Compose, the frontend calls the backend at `http://api:8000/predict` (service name `api`).

---

## Local development (without Docker)

### Prerequisites
- Python 3.10 recommended

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run ingestion

```bash
./run_ingestion.sh
```

### 3) Train models + export artifacts

```bash
python my_version_code.py
```

Note: `my_version_code.py` currently logs MLflow runs to `sqlite:////opt/airflow/mlflow.db` (a path that makes most sense inside the Airflow container). For local-only runs, you can change the tracking URI to a local path (or set up MLflow separately) if you want to use the UI.

### 4) Run the API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 5) Run the frontend

```bash
streamlit run frontend/app.py --server.port 8501
```

If you run Streamlit locally, you may need to change the API URL in `frontend/app.py` from `http://api:8000/predict` to `http://localhost:8000/predict`.

---

## Data & artifacts

- `data/` contains CSV outputs and `.dvc` files. If your environment uses DVC and the CSVs are missing, run `dvc pull`.
- `final_weights/` contains exported models and scaler used by the API. If these are missing, either:
   - run training (`python my_version_code.py`), or
   - run `dvc pull` (if configured in your environment).

---

## Troubleshooting

- **Alpha Vantage fails / empty output**: ensure `ALPHAVANTAGE_API_KEY` is set and be aware of Alpha Vantage rate limits.
- **API errors about missing files**: verify `final_weights/scaler.pkl` and `final_weights/{rnn,lstm,gru}.keras` exist (and that Docker volume mount is correct).
- **Airflow won’t start**: Compose removes a stale PID file (`airflow-webserver.pid`) on startup; if you still see issues, check the Airflow container logs.

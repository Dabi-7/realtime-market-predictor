from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
import joblib

app = FastAPI(title="Real-Time Market Predictor API")

WINDOW_SIZE = 10
FEATURES = ['Open', 'High', 'Low', 'Close', 'Volume', 'Volatility', 'Sentiment']
N_FEATURES = len(FEATURES)

print("Loading model and scaler...")
model = tf.keras.models.load_model("final_weights/model.keras")
scaler = joblib.load("final_weights/scaler.pkl")
print("Systems Online!")

class MarketData(BaseModel):
    # Expects (1, 10, 7)
    features: list[list[list[float]]]

@app.get("/")
def health_check():
    return {"status": "System Online. Ready for predictions."}

@app.post("/predict")
def predict_market(data: MarketData):
    try:
        input_data = np.array(data.features, dtype=np.float32)

        #shape: (1, 10, 7)
        if input_data.shape != (1, WINDOW_SIZE, N_FEATURES):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid shape {input_data.shape}. Expected (1, {WINDOW_SIZE}, {N_FEATURES})."
            )

        
        flat_data = input_data.reshape(-1, N_FEATURES)
        flat_scaled = scaler.transform(flat_data)
        input_scaled = flat_scaled.reshape(input_data.shape)

        prediction = model.predict(input_scaled, verbose=0)
        prob_up = float(prediction[0][0])

        return {
            "probability_up": prob_up,
            "predicted_direction": "Up" if prob_up > 0.5 else "Down",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
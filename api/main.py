from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf
import joblib
import numpy as np

app = FastAPI()

print("Loading models and scaler...")
# Loading scaler
scaler = joblib.load("final_weights/scaler.pkl")

# loading all models
models = {
    "LSTM": tf.keras.models.load_model("final_weights/lstm.keras"),
    "RNN": tf.keras.models.load_model("final_weights/rnn.keras"),
    "GRU": tf.keras.models.load_model("final_weights/gru.keras")
}
print("All assets loaded successfully!")

class MarketData(BaseModel):
    features: list[list[list[float]]]
    model_choice: str 

@app.get("/")
def health_check():
    return {
        "status": "online",
        "message": "Market Predictor API is running!",
        "models_loaded": ["LSTM", "RNN", "GRU"]
    }


@app.post("/predict")
def predict_market(data: MarketData):
    
    if data.model_choice not in models:
        raise HTTPException(status_code=400, detail="Invalid model_choice. Must be RNN, LSTM, or GRU.")
    
    
    input_data = np.array(data.features)
    
    samples, time_steps, features = input_data.shape
    reshaped_data = input_data.reshape(-1, features)
    scaled_data = scaler.transform(reshaped_data)
    final_input = scaled_data.reshape(samples, time_steps, features)
    
    #predicting
    selected_model = models[data.model_choice]
    prediction = selected_model.predict(final_input, verbose=0)
    
    probability = float(prediction[0][0])
    direction = "Up" if probability > 0.5 else "Down"
    
    return {
        "predicted_direction": direction,
        "probability_up": probability,
        "model_used": data.model_choice
    }

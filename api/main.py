from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf
import numpy as np

# 1. Initialize the API
app = FastAPI(title="Real-Time Market Predictor API")

# 2. Load the model into memory exactly ONCE when the server starts.
# (Make sure this path points exactly to where the model.keras file is)
print("Loading model...")
model = tf.keras.models.load_model("model.keras")
print("Model loaded successfully!")

# 3. Define what the incoming JSON payload should look like
class MarketData(BaseModel):
    # We expect a list of numbers representing the market features
    features: list[list[float]] 

@app.get("/")
def health_check():
    return {"status": "System Online. Ready for predictions."}

@app.post("/predict")
def predict_market(data: MarketData):
    try:
        # Convert the incoming JSON list into a NumPy array
        input_data = np.array(data.features)
        
        # Run the AI prediction
        prediction = model.predict(input_data)
        
        # Extract the number from the prediction array and return it
        return {"predicted_price": float(prediction[0][0])}
    
    except Exception as e:
        # If the shape is wrong, return a clean error message
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

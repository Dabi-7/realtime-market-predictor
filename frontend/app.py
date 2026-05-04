import streamlit as st
import requests

st.set_page_config(page_title="Market Predictor", layout="centered")

st.title(" Real-Time Market Movement Predictor")

st.markdown("Enter today's market features to predict tomorrow's movement.")

# --- Feature Inputs ---
st.subheader(" Input Market Features")

col1, col2 = st.columns(2)

with col1:
    open_price = st.number_input("Open Price")
    high_price = st.number_input("High Price")
    low_price = st.number_input("Low Price")
    volume = st.number_input("Volume")

with col2:
    close_price = st.number_input("Close Price")
    sentiment = st.number_input("Sentiment Score")
    volatility = st.number_input("Volatility")

# --- Predict Button ---
if st.button("Predict"):

    features = [
        open_price, high_price, low_price,
        volume, close_price, sentiment, volatility
    ]

    # Validation
    if all(v == 0 for v in features):
        st.warning(" Please enter valid feature values")
    else:
        data = {"features": features}

        with st.spinner(" Predicting..."):
            try:
                response = requests.post(
                    "http://localhost:8000/predict",
                    json=data,
                    timeout=5
                )

                if response.status_code == 200:
                    result = response.json()
                    prediction = result.get("prediction")

                    st.subheader(" Prediction Result")

                    if prediction == 1:
                        st.success(" Market will go UP")
                    elif prediction == 0:
                        st.error(" Market will go DOWN")
                    else:
                        st.warning(" Unexpected prediction output")

                else:
                    st.error(f" API Error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error(" Backend not running (Start FastAPI server)")
            except requests.exceptions.Timeout:
                st.error("️ Request timed out")
            except Exception as e:
                st.error(f" Error: {str(e)}")
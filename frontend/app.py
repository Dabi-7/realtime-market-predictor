import streamlit as st
import requests

st.set_page_config(page_title="Market Predictor", layout="centered")

st.title(" Real-Time Market Movement Predictor")

st.write("Enter today's market features to predict tomorrow's movement.")

# --- Input Fields (7 features) ---
feature1 = st.number_input("Feature 1")
feature2 = st.number_input("Feature 2")
feature3 = st.number_input("Feature 3")
feature4 = st.number_input("Feature 4")
feature5 = st.number_input("Feature 5")
feature6 = st.number_input("Feature 6")
feature7 = st.number_input("Feature 7")

# --- Predict Button ---
if st.button("Predict"):
    data = {
        "features": [
            feature1, feature2, feature3,
            feature4, feature5, feature6, feature7
        ]
    }

    try:
        response = requests.post("http://localhost:8000/predict", json=data)
        result = response.json()

        prediction = result.get("prediction")

        if prediction == 1:
            st.success("📈 Market will go UP")
        else:
            st.error("📉 Market will go DOWN")

    except:
        st.error(" Error connecting to backend API")
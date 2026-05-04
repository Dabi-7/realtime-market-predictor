import streamlit as st
import requests

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Market Predictor",
    layout="centered"
)

# -------------------------------
# Title
# -------------------------------
st.title(" Real-Time Market Movement Predictor")
st.markdown("Enter today's market data to predict tomorrow's trend.")

# -------------------------------
# Input Section
# -------------------------------
st.subheader(" Enter Market Features")

col1, col2 = st.columns(2)

with col1:
    open_price = st.number_input("Open Price", value=0.0)
    high_price = st.number_input("High Price", value=0.0)
    low_price = st.number_input("Low Price", value=0.0)
    close_price = st.number_input("Close Price", value=0.0)

with col2:
    volume = st.number_input("Volume", value=0.0)
    volatility = st.number_input("Volatility", value=0.0)
    sentiment = st.number_input("Sentiment Score", value=0.0)

# -------------------------------
# Predict Button
# -------------------------------
if st.button(" Predict Market Direction"):

    # Single day input (7 features)
    single_day = [
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        volatility,
        sentiment
    ]

    # -------------------------------
    # Validation
    # -------------------------------
    if all(v == 0 for v in single_day):
        st.warning(" Please enter valid values for prediction.")
        st.stop()

    # -------------------------------
    # Convert to (1, 10, 7)
    # -------------------------------
    sequence = [single_day] * 10

    data = {
        "features": [sequence]
    }

    # -------------------------------
    # API Call
    # -------------------------------
    with st.spinner(" Running prediction..."):
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json=data,
                timeout=5
            )

            # -------------------------------
            # Handle Response
            # -------------------------------
            if response.status_code == 200:
                result = response.json()

                direction = result.get("predicted_direction")
                probability = result.get("probability_up")

                st.subheader(" Prediction Result")

                if direction == "Up":
                    st.success(f" Market will go UP")
                else:
                    st.error(f" Market will go DOWN")

                # Confidence
                if probability is not None:
                    st.info(f"Confidence Score: {probability:.2f}")

                # Debug info (optional for presentation)
                with st.expander(" Show Input Sent to Model"):
                    st.write(data)

            else:
                st.error(f" API Error: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error(" Cannot connect to backend. Make sure FastAPI is running.")

        except requests.exceptions.Timeout:
            st.error("️ Request timed out.")

        except Exception as e:
            st.error(f" Unexpected Error: {str(e)}")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Model: RNN / LSTM / GRU | Built with Streamlit + FastAPI")
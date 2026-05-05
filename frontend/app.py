import streamlit as st
import requests
import pandas as pd

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
st.title("Real-Time Market Movement Predictor")
st.markdown("Enter the last **10 days** of market data to predict tomorrow's trend.")

# -------------------------------
# Input Section: The Interactive Grid
# -------------------------------
st.subheader("10-Day Market History")
st.caption("You can edit the cells below manually, or click the top-left cell and **paste data directly from Excel/CSV**.")

# 1. Define the required features
features = ['Open', 'High', 'Low', 'Close', 'Volume', 'Volatility', 'Sentiment']

# 2. Create a default dataframe with 10 rows (Day 1 to 10) filled with 0.0
default_data = pd.DataFrame(
    0.0, 
    index=[f"Day {i+1}" for i in range(10)], 
    columns=features
)

# 3. Render the interactive spreadsheet!
edited_df = st.data_editor(default_data, use_container_width=True)


# Add this right above your st.data_editor line!
uploaded_file = st.file_uploader("Upload a 10-day CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV
    df = pd.read_csv(uploaded_file)
    
    # Ensure it only grabs the 7 features we need, and exactly 10 rows
    try:
        df = df[features].tail(10)
        
        # Overwrite the default 0.0 dataframe with the uploaded data
        default_data.update(df.values)
        st.success("File uploaded successfully! Review the data below.")
    except Exception as e:
        st.error("The uploaded CSV is missing required columns. Ensure it has: Open, High, Low, Close, Volume, Volatility, Sentiment")

selected_model = st.selectbox(
    "Choose AI Architecture to Test", 
    ["LSTM", "RNN", "GRU"],
    help="Select which neural network will process the data."
)
# -------------------------------
# Predict Button
# -------------------------------
if st.button("🔮 Predict Market Direction"):

    # Convert the interactive dataframe into a 10x7 Python list
    sequence = edited_df.values.tolist()

    # -------------------------------
    # Validation
    # -------------------------------
    # Check if the user left everything as 0.0

    if (edited_df.values == 0.0).all():
        st.warning("Please enter real market data. The model cannot predict on all zeros.")
        st.stop()

    # 2. Prevent impossible negative values (Prices and Volume can never be below 0)
    if (edited_df[['Open', 'High', 'Low', 'Close', 'Volume']] < 0).any().any():
        st.error("Market prices and trading volume cannot be negative. Please fix the data.")
        st.stop()

    # 3. Ensure they didn't just fill out Day 1 and leave the rest blank
    if (edited_df['Close'] == 0.0).sum() > 0:
        st.warning("The AI requires a full 10-day history. Please ensure no closing prices are zero.")
        st.stop()

    # -------------------------------
    # Prepare the (1, 10, 7) payload
    # -------------------------------
    data = {
        "features": [sequence]
        "model_choice": selected_model
    }

    # -------------------------------
    # API Call
    # -------------------------------
    with st.spinner("Running prediction..."):
        try:
            # Using the Docker Compose network name 'api'
            response = requests.post(
                "http://api:8000/predict",
                json=data,
                timeout=5
            )

            # -------------------------------
            # Handle Response
            # -------------------------------
            if response.status_code == 200:
                result = response.json()

                direction = result.get("predicted_direction")
                probability = result.get("probability_up", 0.0)

                st.subheader("Prediction Result")

                if direction == "Up":
                    st.success(f"Market will go **UP**")
                else:
                    st.error(f"Market will go **DOWN**")

                # Confidence Metric
                st.metric("Confidence Score", f"{probability * 100:.2f}%")

                # Debug info 
                with st.expander("Show JSON Payload Sent to API"):
                    st.json(data)

            else:
                st.error(f"API Error: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Make sure the FastAPI container is running.")
        except requests.exceptions.Timeout:
            st.error("Request timed out.")
        except Exception as e:
            st.error(f"Unexpected Error: {str(e)}")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Model: RNN / LSTM | Built with Streamlit + FastAPI + Docker")

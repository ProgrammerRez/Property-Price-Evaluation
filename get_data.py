import streamlit as st
import requests
import datetime
import pandas as pd
import os
import joblib

# === Load your trained model ===
model = joblib.load('model.pkl', 'rb')

# === Get user's IP ===
def get_user_ip():
    try:
        ip = requests.get('https://api64.ipify.org?format=json').json()["ip"]
        return ip
    except:
        return "Unknown"

# === Prediction Function ===
def predict_price(features):
    input_df = pd.DataFrame([features])
    prediction = model.predict(input_df)[0]
    return round(prediction, 2)

# === CSV Logging Function ===
def log_to_csv(data, file_path="user_log.csv"):
    df = pd.DataFrame([data])
    if not os.path.isfile(file_path):
        df.to_csv(file_path, index=False)  # Write headers if file doesn't exist
    else:
        df.to_csv(file_path, mode='a', index=False, header=False)  # Append without headers

# === Streamlit UI ===
st.title("🏠 Real Estate Price Estimator")
st.write("Enter property details below to get an estimated price.")

# === Inputs ===
area = st.number_input("Area (in sq ft)", min_value=500, max_value=10000, step=50)
bedrooms = st.slider("Bedrooms", 1, 10, 3)
bathrooms = st.slider("Bathrooms", 1, 10, 2)
location = st.selectbox("Location", ["Downtown", "Suburbs", "Countryside"])

# One-hot encode location
location_cols = {
    "location_Downtown": 0,
    "location_Suburbs": 0,
    "location_Countryside": 0
}
location_key = f"location_{location}"
location_cols[location_key] = 1

# Combine all input features
features = {
    "area": area,
    "bedrooms": bedrooms,
    "bathrooms": bathrooms,
    **location_cols
}

# === Prediction & Logging ===
if st.button("Predict Price"):
    user_ip = get_user_ip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    price = predict_price(features)

    # Show result
    st.success(f"🏷️ Estimated Price: ${price}")

    # Log entry as a structured dictionary
    log_data = {
        "Timestamp": timestamp,
        "User IP": user_ip,
        "Area": area,
        "Bedrooms": bedrooms,
        "Bathrooms": bathrooms,
        "Location": location,
        "Predicted Price ($)": price
    }

    log_to_csv(log_data)  # Save to CSV

    st.info("Your prediction has been logged. Thank you for the input!")

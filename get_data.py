import streamlit as st
import requests
import datetime
import pandas as pd
import os
import joblib  # or use pickle if you saved the model that way

# === Load your trained model ===
model = joblib.load('model.pkl')  # or use pickle.load(open('model.pkl', 'rb')) if you used pickle

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
st.markdown("""
Welcome! This is a small-scale project to estimate property prices based on a few basic features.

If you (or someone you know) has experience in real estate, your feedback is **highly appreciated**! 💬  
""")

st.divider()

# === Input Fields ===
area = st.number_input("📏 Area (in sq ft)", min_value=500, max_value=10000, step=50)
bedrooms = st.slider("🛏️ Bedrooms", 1, 10, 3)
bathrooms = st.slider("🛁 Bathrooms", 1, 10, 2)
location = st.selectbox("📍 Location", ["Downtown", "Suburbs", "Countryside"])

# === One-hot encode the location ===
location_cols = {
    "location_Downtown": 0,
    "location_Suburbs": 0,
    "location_Countryside": 0
}
location_cols[f"location_{location}"] = 1

# === Combine all features ===
features = {
    "area": area,
    "bedrooms": bedrooms,
    "bathrooms": bathrooms,
    **location_cols
}

# === Predict & Log ===
if st.button("🚀 Predict Price"):
    user_ip = get_user_ip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    price = predict_price(features)

    # Show result
    st.success(f"🏷️ Estimated Price: **${price}**")

    # Log to CSV
    log_data = {
        "Timestamp": timestamp,
        "User IP": user_ip,
        "Area": area,
        "Bedrooms": bedrooms,
        "Bathrooms": bathrooms,
        "Location": location,
        "Predicted Price ($)": price
    }
    log_to_csv(log_data)

    st.info("✅ Your input has been logged for model improvement. Thank you!")

st.divider()
st.caption("🔒 Your IP is only used for anonymous feedback tracking. No personal data is stored.")

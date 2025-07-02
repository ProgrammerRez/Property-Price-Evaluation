import streamlit as st
import pandas as pd
import joblib
import json
import os

# ----------------- Load Model -----------------
model = joblib.load("model.pkl")

# ----------------- Load Locality Data -----------------
with open("merged_output.json", "r") as f:
    raw_data = json.load(f)

# Convert keys to int for locality encoding
locality_data = {int(k): v for k, v in raw_data.items()}
name_to_id = {v["locality"]: k for k, v in locality_data.items()}
id_to_name = {k: v["locality"] for k, v in locality_data.items()}

# ----------------- UI -----------------
st.title("🏠 Real Estate Price Prediction App")

# Select locality
selected_locality_name = st.selectbox("Select Locality", list(name_to_id.keys()))
selected_locality_id = name_to_id[selected_locality_name]
locality_encoded = selected_locality_id
actual_price_per_sqft = float(locality_data[locality_encoded]["price_per_sqft"])

# Show price/sqft
st.info(f"📊 **Avg. Price per Sqft in {selected_locality_name}**: PKR {actual_price_per_sqft:,.0f}")

# User Inputs
area_sqft = st.number_input("📐 Area in Square Feet", min_value=50.0, value=1000.0, step=10.0)
bedrooms = st.number_input("🛏️ Number of Bedrooms", min_value=0, value=2, step=1)
baths = st.number_input("🛁 Number of Bathrooms", min_value=0, value=2, step=1)

property_types = [
    "Farm House", "Flat", "House", "Lower Portion",
    "Penthouse", "Room", "Upper Portion"
]
property_type = st.radio("🏢 Select Property Type", property_types)

# One-hot encode property type
property_type_encoded = {f"property_type_{ptype}": 0 for ptype in property_types}
property_type_encoded[f"property_type_{property_type}"] = 1

# Feature dictionary
input_data = {
    "locality": locality_encoded,
    "baths": baths,
    "area_sqft": area_sqft,
    "bedrooms": bedrooms,
    "price_per_sqft": actual_price_per_sqft,
    **property_type_encoded
}

# Maintain model training order
column_order = [
    'locality', 'baths', 'area_sqft', 'bedrooms',
    'property_type_Farm House', 'property_type_Flat', 'property_type_House',
    'property_type_Lower Portion', 'property_type_Penthouse',
    'property_type_Room', 'property_type_Upper Portion', 'price_per_sqft'
]

# Fill any missing one-hot encodings
for col in column_order:
    if col not in input_data:
        input_data[col] = 0

# Create DataFrame
input_df = pd.DataFrame([[input_data[col] for col in column_order]], columns=column_order)

# Prediction
if st.button("🔮 Predict Property Price"):
    predicted_price = model.predict(input_df)[0]
    predicted_pps = predicted_price / area_sqft if area_sqft > 0 else 0

    st.success(f"💰 **Estimated Price**: PKR {predicted_price:,.0f}")
    st.info(f"📐 **Predicted Price per Sqft**: PKR {predicted_pps:,.2f}")
    st.subheader("📋 Model Input Data")
    st.write(input_df)

# ----------------- 📝 Review System -----------------
st.markdown("---")
st.header("📝 Share Your Review")

# Review inputs
review_city = st.text_input("📍 Area/City Name", placeholder="e.g. Cantt Lahore")
review_name = st.text_input("👤 Your Name", placeholder="e.g. Umar Bhai")
review_text = st.text_area("💬 Your Review", placeholder="Write your experience here...")

REVIEW_FILE = "reviews.json"

# Load existing reviews
if os.path.exists(REVIEW_FILE):
    with open(REVIEW_FILE, "r") as f:
        stored_reviews = json.load(f)
else:
    stored_reviews = []

# Submit review
if st.button("✅ Submit Review"):
    if review_city and review_name and review_text:
        new_review = {
            "City": review_city.strip(),
            "Name": review_name.strip(),
            "Review": review_text.strip()
        }
        stored_reviews.append(new_review)
        with open(REVIEW_FILE, "w") as f:
            json.dump(stored_reviews, f, indent=4)
        st.success("🎉 Thank you! Your review has been submitted.")
    else:
        st.warning("⚠️ Please fill in all fields before submitting.")

# Show reviews
if stored_reviews:
    st.markdown("### 💡 Recent Reviews")
    for rev in reversed(stored_reviews[-5:]):  # show latest 5
        st.markdown(f"""
        **📍 {rev['City']}**  
        _✍️ {rev['Name']}_  
        > {rev['Review']}
        """)

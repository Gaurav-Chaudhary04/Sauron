import json
import streamlit as st
import numpy as np
import pandas as pd
import joblib
import os
import time

QUEUE_FILE = "queue_data.txt"

# Load trained models
model1 = joblib.load("model_total_time.pkl")  # Model for predicting Total_Time
model2 = joblib.load("model_durations.pkl")   # Model for predicting Green & Red Duration

def get_latest_queue_length():
    try:
        with open(QUEUE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0  # Default queue length

# Initialize session state
if "queue_n" not in st.session_state:
    st.session_state.queue_n = get_latest_queue_length()

# Streamlit UI
st.title("🚦Smart Traffic Light Duration Predictor")

st.markdown("### Enter Queue Lengths (meters):")

# Display queue_n in the main UI
st.info(f"📊 **Queue Length (North):** {st.session_state.queue_n} meters")

queue_s = st.number_input("Queue Length (South)", min_value=0, max_value=2500, value=600)
queue_e = st.number_input("Queue Length (East)", min_value=0, max_value=2500, value=800)
queue_w = st.number_input("Queue Length (West)", min_value=0, max_value=2500, value=700)

# Prediction Function
def predict_durations(queue_n, queue_s, queue_e, queue_w):
    total_queue = queue_n + queue_s + queue_e + queue_w
    
    # Predict Total Time
    predicted_total_time = model1.predict(pd.DataFrame([[total_queue]], columns=["Total_Queue"]))[0]

    # Predict Green & Red Duration
    input_features = pd.DataFrame([[queue_n, queue_s, queue_e, queue_w, predicted_total_time]],
                                  columns=["Queue_N", "Queue_S", "Queue_E", "Queue_W", "Total_Time"])
    predicted_durations = model2.predict(input_features)
    
    # Save the predictions to a file that lightsimu.py can read
    timings = {
        "green_duration": float(predicted_durations[0][0]),
        "red_duration": float(predicted_durations[0][1])
    }

    with open("traffic_timings.json", "w") as f:
        json.dump(timings, f)
    
    return predicted_total_time, predicted_durations[0][0], predicted_durations[0][1]

# Buttons for North-South and East-West selection
st.markdown("### Select Traffic Direction")
col1, col2 = st.columns(2)
with col1:
    ns_selected = st.button("North-South")
with col2:
    ew_selected = st.button("East-West")

# Run prediction if a button is clicked
if ns_selected or ew_selected:
    st.session_state.queue_n = get_latest_queue_length()  # Update queue_n before prediction
    total_time, green_duration, red_duration = predict_durations(
        st.session_state.queue_n, queue_s, queue_e, queue_w
    )
    
    if ew_selected:
        green_duration, red_duration = red_duration, green_duration  # Swap durations for East-West
    
    st.success(f"🚦**Predicted Total Time:** {total_time:.2f} sec")
    st.info(f"✅ **Green Light Duration:** {green_duration:.2f} sec")
    st.warning(f"🛑 **Red Light Duration:** {red_duration:.2f} sec")

# Auto-refresh every 7 seconds
time.sleep(7)
st.session_state.queue_n = get_latest_queue_length()
st.rerun()


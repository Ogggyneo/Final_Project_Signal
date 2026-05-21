import serial
import pandas as pd
import numpy as np
import joblib
import time
from collections import deque

# =========================
# LOAD TRAINED MODEL
# =========================
model = joblib.load("D:\SPRING(1)\ENG\Final_Project_Signal\Final_Project_ENG\src\calorie_model.pkl")
scaler = joblib.load("src\scaler.pkl")

# =========================
# SERIAL CONFIG
# =========================
PORT = "COM3"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print("🚀 WEARABLE AI STARTED")

# =========================
# BUFFER (important for stability)
# =========================
window_size = 30
bpm_buffer = deque(maxlen=window_size)
steps_buffer = deque(maxlen=window_size)
dist_buffer = deque(maxlen=window_size)

# =========================
# USER PROFILE (personalization)
# =========================
USER_AGE = 22
USER_HEIGHT = 175
USER_WEIGHT = 70
USER_BMI = USER_WEIGHT / ((USER_HEIGHT/100)**2)

# =========================
# LIVE LOOP
# =========================
while True:
    try:
        line = ser.readline().decode().strip()

        if not line or "time_ms" in line:
            continue

        parts = line.split(",")

        if len(parts) != 4:
            continue

        # =========================
        # PARSE ESP32 DATA
        # =========================
        t, bpm, steps, dist = parts

        bpm = float(bpm)
        steps = float(steps)
        dist = float(dist)

        bpm_buffer.append(bpm)
        steps_buffer.append(steps)
        dist_buffer.append(dist)

        # wait until buffer fills
        if len(bpm_buffer) < 10:
            continue

        # =========================
        # FEATURES (SMOOTHED)
        # =========================
        features = pd.DataFrame([{
            "Age": USER_AGE,
            "Height(cm)": USER_HEIGHT,
            "Weight(kg)": USER_WEIGHT,
            "BMI": USER_BMI,
            "Average Heart Rate": np.mean(bpm_buffer),
            "Distance(km)": np.max(dist_buffer),
            "Running Time(min)": len(bpm_buffer)/60
        }])

        # =========================
        # PREDICTION
        # =========================
        X_scaled = scaler.transform(features)
        calories = model.predict(X_scaled)[0]

        # =========================
        # ACTIVITY CLASSIFICATION
        # =========================
        avg_bpm = np.mean(bpm_buffer)

        if avg_bpm < 90:
            activity = "REST 💤"
        elif avg_bpm < 130:
            activity = "WALK 🚶"
        else:
            activity = "RUN 🏃"

        # =========================
        # OUTPUT
        # =========================
        print("\n========================")
        print(f"Heart Rate: {avg_bpm:.1f}")
        print(f"Steps: {steps}")
        print(f"Distance: {dist}")
        print(f"Activity: {activity}")
        print(f"🔥 Calories: {calories:.2f}")
        print("========================")

    except KeyboardInterrupt:
        print("Stopped")
        break
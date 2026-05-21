import pandas as pd
import numpy as np
import os
import joblib

# =========================
# LOAD ESP32 RAW DATA
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(
    os.path.join(BASE_DIR, "esp32_data.csv")
)

# =========================
# CLEAN
# =========================
df = df.dropna()

# remove bpm = 0
df = df[df["bpm"] > 0]

# =========================
# COMPUTE FEATURES
# =========================

# average heart rate
avg_hr = df["bpm"].mean()

# total distance
distance = df["distance"].max()

# running time in minutes
time_min = (
    df["time_ms"].max() -
    df["time_ms"].min()
) / 60000.0

# pace
pace = distance / time_min

# HR x time
hr_time = avg_hr * time_min

# =========================
# USER INFO
# =========================
age = 21
height = 170
weight = 65

# BMI
bmi = weight / ((height / 100) ** 2)

# =========================
# CREATE MODEL INPUT
# =========================
features = pd.DataFrame([{

    "Age": age,

    "Height(cm)": height,

    "Weight(kg)": weight,

    "BMI": bmi,

    "Average Heart Rate": avg_hr,

    "Distance(km)": distance,

    "Running Time(min)": time_min,

    "Pace": pace,

    "HR_Time": hr_time
}])

print("\n========== MODEL INPUT ==========\n")
print(features)

# =========================
# LOAD MODEL
# =========================
model = joblib.load(
    os.path.join(BASE_DIR, "calorie_model.pkl")
)

# =========================
# PREDICT
# =========================
prediction = model.predict(features)[0]

print("\n=================================")
print(f"Predicted Calories: {prediction:.2f} kcal")
print("=================================\n")
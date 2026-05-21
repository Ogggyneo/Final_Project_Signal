import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib

# =========================
# LOAD YOUR FITNESS DATASET
# =========================
df = pd.read_csv("D:\SPRING(1)\ENG\Final_Project_Signal\Final_Project_ENG\src\cleaned_data.csv")  
# file contains your table:
# Age,Height,Weight,BMI,AvgHeartRate,Distance,RunningTime,Calories

# =========================
# CLEAN
# =========================
df = df.dropna()

# =========================
# FEATURES + TARGET
# =========================
X = df[[
    "Age",
    "Height(cm)",
    "Weight(kg)",
    "BMI",
    "Average Heart Rate",
    "Distance(km)",
    "Running Time(min)"
]]

y = df["Calories Burned"]

# =========================
# SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# SCALE
# =========================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =========================
# MODEL
# =========================
model = RandomForestRegressor(
    n_estimators=300,
    random_state=42
)

model.fit(X_train_scaled, y_train)

# =========================
# SAVE MODEL
# =========================
joblib.dump(model, "calorie_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("MODEL TRAINED + SAVED ✔")
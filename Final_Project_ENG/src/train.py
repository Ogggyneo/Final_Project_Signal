import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib

# =========================
# LOAD DATASET
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "cleaned_data.csv"))
df = df.dropna()

# =========================
# FEATURES + TARGET
# =========================
FEATURES = [
    "Age",
    "Height(cm)",
    "Weight(kg)",
    "BMI",
    "Average Heart Rate",
    "Distance(km)",
    "Running Time(min)",
]
TARGET = "Calories Burned"

X = df[FEATURES]
y = df[TARGET]

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
X_test_scaled  = scaler.transform(X_test)

# =========================
# MODEL
# =========================
model = RandomForestRegressor(n_estimators=300, random_state=42)
model.fit(X_train_scaled, y_train)

# =========================
# METRICS  ← NEW
# =========================
y_pred = model.predict(X_test_scaled)

r2   = r2_score(y_test, y_pred)
mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# 5-fold cross-validation R²
cv_scores = cross_val_score(model, scaler.transform(X), y, cv=5, scoring="r2")

print("\n========== MODEL METRICS ==========")
print(f"  R² Score   : {r2:.4f}")
print(f"  MAE        : {mae:.2f} kcal")
print(f"  RMSE       : {rmse:.2f} kcal")
print(f"  CV R² (5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print("====================================\n")

# Feature importance
importances = model.feature_importances_
print("  Feature Importances:")
for name, imp in sorted(zip(FEATURES, importances), key=lambda x: -x[1]):
    bar = "█" * int(imp * 40)
    print(f"    {name:<22} {imp:.4f}  {bar}")
print()

# =========================
# SAVE
# =========================
joblib.dump(model,  os.path.join(BASE_DIR, "calorie_model.pkl"))
joblib.dump(scaler, os.path.join(BASE_DIR, "scaler.pkl"))

print("MODEL TRAINED + SAVED ✔")
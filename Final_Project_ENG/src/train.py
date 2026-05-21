import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# LOAD + CLEAN
# =========================
df = pd.read_csv(os.path.join(BASE_DIR, "cleaned_data.csv")).dropna()

df = df[
    (df["Average Heart Rate"] > 40) & (df["Average Heart Rate"] < 220) &
    (df["Distance(km)"] > 0) &
    (df["Running Time(min)"] > 0) &
    (df["Weight(kg)"] > 30) & (df["Weight(kg)"] < 250) &
    (df["Height(cm)"] > 120) & (df["Height(cm)"] < 220) &
    (df["Age"] > 10) & (df["Age"] < 90)
]

# =========================
# PHYSICS LABEL
# =========================
df["Speed_kmh"] = df["Distance(km)"] / (df["Running Time(min)"] / 60)
df["MET"]       = pd.cut(
    df["Speed_kmh"],
    bins=[0, 6, 8, 10, 12, 14, 999],
    labels=[3.5, 6.0, 8.3, 9.8, 11.0, 12.5]
).astype(float)

df["HR_Intensity"] = (df["Average Heart Rate"] - 60) / (200 - 60)
df["HR_Modifier"]  = 1.0 + (df["HR_Intensity"] - 0.5) * 0.15

df["Calories_Physics"] = (
    df["MET"] * df["Weight(kg)"] * (df["Running Time(min)"] / 60) * df["HR_Modifier"]
)

# =========================
# FEATURES + TARGET
# =========================
FEATURES = [
    "Weight(kg)",
    "Running Time(min)",
    "Distance(km)",
    "MET",
    "HR_Intensity",
    "Speed_kmh",
    "Age",
    "Average Heart Rate",
]

TARGET = "Calories_Physics"

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# TRAIN
# =========================
model = Pipeline([
    ("scaler", StandardScaler()),
    ("ridge",  RidgeCV(alphas=[0.01, 0.1, 1, 10, 100, 1000], cv=5)),
])

model.fit(X_train, y_train)

# =========================
# EVALUATE
# =========================
y_pred     = model.predict(X_test)
train_pred = model.predict(X_train)

r2       = r2_score(y_test, y_pred)
mae      = mean_absolute_error(y_test, y_pred)
rmse     = np.sqrt(mean_squared_error(y_test, y_pred))
train_r2 = r2_score(y_train, train_pred)

kf        = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X, y, cv=kf, scoring="r2")

print(f"\nBest alpha : {model.named_steps['ridge'].alpha_}")

print("\n========== RIDGE REGRESSION METRICS ==========")
print(f"  Train R²       : {train_r2:.4f}")
print(f"  Test R²        : {r2:.4f}")
print(f"  MAE            : {mae:.2f} kcal")
print(f"  RMSE           : {rmse:.2f} kcal")
print(f"  CV R² (5-fold) : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print("===============================================")

gap = train_r2 - r2
if gap < 0.05:
    print("\n  ✔ No overfitting")
elif gap < 0.15:
    print("\n  ✔ Minimal overfitting — acceptable")
else:
    print("\n  ⚠ Overfitting — increase alpha")

# =========================
# COEFFICIENTS
# =========================
print("\n========== FEATURE COEFFICIENTS ==========")
coefs = model.named_steps["ridge"].coef_
for name, coef in sorted(zip(FEATURES, coefs), key=lambda x: -abs(x[1])):
    bar  = "█" * int(abs(coef) / max(abs(coefs)) * 40)
    sign = "+" if coef >= 0 else "-"
    print(f"  {name:<22} {sign}{abs(coef):7.2f}  {bar}")
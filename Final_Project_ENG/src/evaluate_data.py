import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "cleaned_data.csv")).dropna()

# Apply same cleaning as model
df = df[
    (df["Average Heart Rate"] > 40) & (df["Average Heart Rate"] < 220) &
    (df["Distance(km)"] >= 0) &
    (df["Running Time(min)"] > 0) &
    (df["Calories Burned"] > 0) &
    (df["Weight(kg)"] > 30) & (df["Weight(kg)"] < 250) &
    (df["Height(cm)"] > 120) & (df["Height(cm)"] < 220) &
    (df["Age"] > 10) & (df["Age"] < 90)
]

# ============================================================
# PHYSICS-BASED CALORIE ESTIMATE
# Using the standard MET formula:
#   Calories = MET × Weight(kg) × Duration(hours)
#   MET is approximated from speed (km/h)
# MET lookup (approximate):
#   < 6 km/h  → 3.5  (brisk walk)
#   6–8       → 6.0  (light jog)
#   8–10      → 8.3  (moderate run)
#   10–12     → 9.8  (fast run)
#   > 12      → 11.0 (sprint)
# ============================================================

df["Speed_kmh"] = df["Distance(km)"] / (df["Running Time(min)"] / 60)

def speed_to_met(speed):
    if speed < 6:   return 3.5
    elif speed < 8: return 6.0
    elif speed < 10: return 8.3
    elif speed < 12: return 9.8
    else:            return 11.0

df["MET"] = df["Speed_kmh"].apply(speed_to_met)
df["Physics_Calories"] = df["MET"] * df["Weight(kg)"] * (df["Running Time(min)"] / 60)

# ============================================================
# CHECK 1: How well do actual labels match physics formula?
# ============================================================
from sklearn.metrics import r2_score, mean_absolute_error

r2_physics  = r2_score(df["Calories Burned"], df["Physics_Calories"])
mae_physics = mean_absolute_error(df["Calories Burned"], df["Physics_Calories"])

print("\n========== PHYSICS FORMULA vs YOUR LABELS ==========")
print(f"  R²  between formula and labels : {r2_physics:.4f}")
print(f"  MAE between formula and labels : {mae_physics:.2f} kcal")
print()
if r2_physics > 0.85:
    print("  ✔ Labels are CONSISTENT with physics — model should achieve >0.85 R²")
    print("    → Your issue is likely model config or feature set")
elif r2_physics > 0.6:
    print("  ⚠ Moderate consistency — labels may come from different devices/methods")
    print("    → This caps your model R² around 0.5–0.7 no matter what")
else:
    print("  ✗ Labels are INCONSISTENT with physics")
    print("    → Calorie values may be estimated incorrectly, or source is unreliable")
    print("    → Consider replacing labels with physics_calories (see below)")

# ============================================================
# CHECK 2: Dataset size
# ============================================================
print(f"\n========== DATASET SIZE ==========")
print(f"  Rows: {len(df)}")
if len(df) < 500:
    print("  ✗ Very small — Random Forest will overfit badly. Need 1000+ rows.")
elif len(df) < 1000:
    print("  ⚠ Small dataset — use simpler models (Ridge, SVR) or get more data")
else:
    print("  ✔ Size looks reasonable")

# ============================================================
# CHECK 3: Is Gender in the dataset?
# ============================================================
print(f"\n========== COLUMNS IN YOUR DATASET ==========")
print(f"  {list(df.columns)}")
if any("gender" in c.lower() or "sex" in c.lower() for c in df.columns):
    print("  ✔ Gender column found — MAKE SURE it's included in FEATURES")
    print("    Gender accounts for ~10-15% calorie difference at same HR/pace")
else:
    print("  ⚠ No Gender column found")
    print("    Gender is the #1 missing feature for calorie prediction")
    print("    At same weight/HR/pace, males burn ~15% more than females")

# ============================================================
# CHECK 4: Are key correlations strong?
# ============================================================
print(f"\n========== RAW CORRELATIONS WITH CALORIES BURNED ==========")
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
corr = df[numeric_cols].corr()["Calories Burned"].drop("Calories Burned")
for feat, val in corr.sort_values(ascending=False).items():
    bar = "█" * int(abs(val) * 30)
    sign = "+" if val >= 0 else "-"
    print(f"  {feat:<25} {sign}{abs(val):.4f}  {bar}")

print()
if corr["Running Time(min)"] < 0.5 and corr["Distance(km)"] < 0.5:
    print("  ✗ Running Time and Distance have LOW correlation with Calories!")
    print("    This strongly suggests label noise or data recording errors.")
    print("    Expected: both should have r > 0.7 in a clean running dataset.")

# ============================================================
# CHECK 5: Calories per km sanity check
# ============================================================
df["Cal_per_km"] = df["Calories Burned"] / df["Distance(km)"].replace(0, np.nan)
print(f"\n========== CALORIES PER KM SANITY CHECK ==========")
print(f"  Expected range: 50–100 kcal/km for most runners")
print(f"  Your data:")
print(f"    Mean   : {df['Cal_per_km'].mean():.1f}")
print(f"    Median : {df['Cal_per_km'].median():.1f}")
print(f"    Std    : {df['Cal_per_km'].std():.1f}")
print(f"    Min    : {df['Cal_per_km'].min():.1f}")
print(f"    Max    : {df['Cal_per_km'].max():.1f}")
pct_insane = ((df["Cal_per_km"] < 20) | (df["Cal_per_km"] > 200)).mean() * 100
print(f"    Outside 20–200 range : {pct_insane:.1f}% of rows")
if pct_insane > 10:
    print("  ✗ Too many physiologically impossible values — labels are unreliable")

# ============================================================
# OPTION: Replace labels with physics formula
# ============================================================
print(f"\n========== OPTION: USE PHYSICS LABELS ==========")
print("""
  If your labels are noisy, replace them with the physics estimate:

      df["Calories Burned"] = df["MET"] * df["Weight(kg)"] * (df["Running Time(min)"] / 60)

  This will likely push R² above 0.90 because the model will learn
  a deterministic formula rather than noisy device readings.

  Trade-off: your model will be a smooth physics approximation,
  not a learned correction of real device data.
""")

# ============================================================
# PLOTS
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Plot 1: Physics vs Actual labels
ax = axes[0]
ax.scatter(df["Physics_Calories"], df["Calories Burned"], alpha=0.3, s=15)
mn = min(df["Physics_Calories"].min(), df["Calories Burned"].min())
mx = max(df["Physics_Calories"].max(), df["Calories Burned"].max())
ax.plot([mn, mx], [mn, mx], "r--", lw=2)
ax.set_xlabel("Physics Formula Calories")
ax.set_ylabel("Your Labels (Calories Burned)")
ax.set_title(f"Physics vs Labels  (R²={r2_physics:.3f})")
ax.grid(True, alpha=0.3)

# Plot 2: Calories vs Running Time
ax = axes[1]
ax.scatter(df["Running Time(min)"], df["Calories Burned"], alpha=0.3, s=15)
ax.set_xlabel("Running Time (min)")
ax.set_ylabel("Calories Burned")
ax.set_title("Calories vs Running Time\n(should be roughly linear)")
ax.grid(True, alpha=0.3)

# Plot 3: Calories vs Distance
ax = axes[2]
ax.scatter(df["Distance(km)"], df["Calories Burned"], alpha=0.3, s=15)
ax.set_xlabel("Distance (km)")
ax.set_ylabel("Calories Burned")
ax.set_title("Calories vs Distance\n(should be roughly linear)")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "data_diagnostics.png"), dpi=150)
plt.show()
print("Plots saved → data_diagnostics.png")
"""
evaluate.py
Run this after train.py to generate all validation charts.
Outputs saved to src/plots/ — use them in your slides.

Usage:
    python evaluate.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib

# =========================
# PATHS
# =========================
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

FEATURES = [
    "Age", "Height(cm)", "Weight(kg)", "BMI",
    "Average Heart Rate", "Distance(km)", "Running Time(min)",
]
TARGET = "Calories Burned"
FEAT_LABELS = ["Age", "Height", "Weight", "BMI", "Heart Rate", "Distance", "Run Time"]

# =========================
# LOAD + RETRAIN (reproducible)
# =========================
df = pd.read_csv(os.path.join(BASE_DIR, "cleaned_data.csv")).dropna()
X  = df[FEATURES]
y  = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

model = RandomForestRegressor(n_estimators=300, random_state=42)
model.fit(X_train_s, y_train)

y_pred = model.predict(X_test_s)

r2   = r2_score(y_test, y_pred)
mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
importances = model.feature_importances_

PALETTE = {"teal": "#0D9488", "mint": "#2DD4BF", "red": "#F43F5E",
           "amber": "#F59E0B", "muted": "#94A3B8", "dark": "#1E293B"}

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Predicted vs Actual scatter
# ─────────────────────────────────────────────────────────────────────────────
def plot_pred_vs_actual():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(y_test, y_pred, alpha=0.7, color=PALETTE["teal"],
               edgecolors="white", linewidths=0.5, s=60, label="Predictions")

    lims = [min(y_test.min(), y_pred.min()) - 50,
            max(y_test.max(), y_pred.max()) + 50]
    ax.plot(lims, lims, "--", color=PALETTE["red"], linewidth=1.5, label="Perfect (y = x)")

    ax.set_xlabel("Actual Calories Burned", fontsize=12, color=PALETTE["dark"])
    ax.set_ylabel("Predicted Calories Burned", fontsize=12, color=PALETTE["dark"])
    ax.set_title("Predicted vs Actual Calories", fontsize=14, fontweight="bold", color=PALETTE["dark"])
    ax.legend(fontsize=10)
    ax.set_xlim(lims); ax.set_ylim(lims)
    ax.grid(True, alpha=0.3, color=PALETTE["muted"])
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("white")

    # annotate metrics
    ax.text(0.05, 0.92, f"R² = {r2:.3f}", transform=ax.transAxes,
            fontsize=11, color=PALETTE["dark"], fontweight="bold")
    ax.text(0.05, 0.84, f"MAE = {mae:.1f} kcal", transform=ax.transAxes,
            fontsize=10, color=PALETTE["muted"])
    ax.text(0.05, 0.77, f"RMSE = {rmse:.1f} kcal", transform=ax.transAxes,
            fontsize=10, color=PALETTE["muted"])

    path = os.path.join(PLOTS_DIR, "pred_vs_actual.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Feature Importance
# ─────────────────────────────────────────────────────────────────────────────
def plot_feature_importance():
    sorted_idx = np.argsort(importances)
    labels_sorted = [FEAT_LABELS[i] for i in sorted_idx]
    vals_sorted   = importances[sorted_idx]
    colors = [PALETTE["teal"] if v >= sorted(importances)[-2] else
              PALETTE["mint"] if v >= np.median(importances) else
              PALETTE["muted"] for v in vals_sorted]

    fig, ax = plt.subplots(figsize=(6, 4.5))
    bars = ax.barh(labels_sorted, vals_sorted * 100, color=colors,
                   edgecolor="white", height=0.6)

    for bar, val in zip(bars, vals_sorted):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{val*100:.1f}%", va="center", fontsize=10, color=PALETTE["dark"])

    ax.set_xlabel("Importance (%)", fontsize=11, color=PALETTE["dark"])
    ax.set_title("Feature Importance — Random Forest", fontsize=13,
                 fontweight="bold", color=PALETTE["dark"])
    ax.set_xlim(0, max(vals_sorted * 100) + 4)
    ax.grid(axis="x", alpha=0.3, color=PALETTE["muted"])
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)

    path = os.path.join(PLOTS_DIR, "feature_importance.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — Residuals distribution
# ─────────────────────────────────────────────────────────────────────────────
def plot_residuals():
    residuals = y_test.values - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # residuals over samples
    axes[0].scatter(range(len(residuals)), residuals, alpha=0.7,
                    color=PALETTE["teal"], edgecolors="white", linewidths=0.4, s=50)
    axes[0].axhline(0, color=PALETTE["red"], linewidth=1.5, linestyle="--")
    axes[0].set_title("Residuals per Sample", fontsize=12, fontweight="bold", color=PALETTE["dark"])
    axes[0].set_xlabel("Sample Index", color=PALETTE["dark"])
    axes[0].set_ylabel("Error (kcal)", color=PALETTE["dark"])
    axes[0].grid(True, alpha=0.3)
    axes[0].set_facecolor("#F8FAFC")

    # histogram
    axes[1].hist(residuals, bins=15, color=PALETTE["teal"], edgecolor="white", alpha=0.85)
    axes[1].axvline(0, color=PALETTE["red"], linewidth=1.5, linestyle="--", label="Zero error")
    axes[1].axvline(mae, color=PALETTE["amber"], linewidth=1.5, linestyle=":", label=f"MAE = {mae:.0f}")
    axes[1].axvline(-mae, color=PALETTE["amber"], linewidth=1.5, linestyle=":")
    axes[1].set_title("Residuals Distribution", fontsize=12, fontweight="bold", color=PALETTE["dark"])
    axes[1].set_xlabel("Error (kcal)", color=PALETTE["dark"])
    axes[1].set_ylabel("Count", color=PALETTE["dark"])
    axes[1].legend(fontsize=9)
    axes[1].set_facecolor("#F8FAFC")

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)

    fig.patch.set_facecolor("white")
    path = os.path.join(PLOTS_DIR, "residuals.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Dataset distribution overview
# ─────────────────────────────────────────────────────────────────────────────
def plot_data_distribution():
    cols_to_plot = ["Age", "Average Heart Rate", "Distance(km)", "Calories Burned"]
    plot_labels  = ["Age", "Avg Heart Rate (BPM)", "Distance (km)", "Calories Burned"]

    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    colors = [PALETTE["teal"], PALETTE["mint"], PALETTE["amber"], PALETTE["red"]]

    for ax, col, label, color in zip(axes, cols_to_plot, plot_labels, colors):
        ax.hist(df[col].dropna(), bins=20, color=color, edgecolor="white", alpha=0.85)
        ax.set_title(label, fontsize=11, fontweight="bold", color=PALETTE["dark"])
        ax.set_ylabel("Count", fontsize=9, color=PALETTE["dark"])
        ax.grid(axis="y", alpha=0.3)
        ax.set_facecolor("#F8FAFC")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=9)

        # mean line
        mean_val = df[col].mean()
        ax.axvline(mean_val, color=PALETTE["dark"], linewidth=1.5,
                   linestyle="--", label=f"Mean: {mean_val:.1f}")
        ax.legend(fontsize=8)

    fig.suptitle("Training Dataset — Feature Distributions (n=200)",
                 fontsize=13, fontweight="bold", color=PALETTE["dark"])
    fig.patch.set_facecolor("white")
    path = os.path.join(PLOTS_DIR, "data_distribution.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Simulated live BPM signal (REST → WALK → RUN)
# ─────────────────────────────────────────────────────────────────────────────
def plot_live_bpm_signal():
    np.random.seed(0)
    t = np.arange(0, 120, 1)   # seconds

    bpm = np.where(t < 30,
                   72 + np.random.randn(len(t)) * 3,
           np.where(t < 60,
                   90 + (t - 30) * 1.2 + np.random.randn(len(t)) * 4,
                   128 + (t - 60) * 0.4 + np.random.randn(len(t)) * 5))

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, bpm, color=PALETTE["teal"], linewidth=2, label="Heart Rate (BPM)")
    ax.axhline(90,  color=PALETTE["amber"], linewidth=1.5, linestyle="--", label="Walk threshold (90 BPM)")
    ax.axhline(130, color=PALETTE["red"],   linewidth=1.5, linestyle="--", label="Run threshold (130 BPM)")

    # activity zone shading
    ax.axvspan(0,  30,  alpha=0.06, color=PALETTE["muted"], label="REST")
    ax.axvspan(30, 60,  alpha=0.06, color=PALETTE["amber"])
    ax.axvspan(60, 120, alpha=0.06, color=PALETTE["red"])

    # labels
    for txt, xpos, ypos in [("REST 💤", 15, 60), ("WALK 🚶", 45, 60), ("RUN 🏃", 90, 60)]:
        ax.text(xpos, ypos, txt, ha="center", fontsize=11,
                color=PALETTE["dark"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none"))

    ax.set_xlabel("Time (seconds)", fontsize=11, color=PALETTE["dark"])
    ax.set_ylabel("BPM", fontsize=11, color=PALETTE["dark"])
    ax.set_title("Live Heart Rate Signal — Activity Classification", fontsize=13,
                 fontweight="bold", color=PALETTE["dark"])
    ax.set_ylim(40, 175)
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_facecolor("#F8FAFC")
    ax.spines[["top", "right"]].set_visible(False)
    fig.patch.set_facecolor("white")

    path = os.path.join(PLOTS_DIR, "live_bpm_signal.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {path}")

# ─────────────────────────────────────────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n Generating validation plots...")
    plot_pred_vs_actual()
    plot_feature_importance()
    plot_residuals()
    plot_data_distribution()
    plot_live_bpm_signal()

    print(f"\n All plots saved to: {PLOTS_DIR}")
    print(f"\n Summary:")
    print(f"   R²   = {r2:.4f}")
    print(f"   MAE  = {mae:.2f} kcal")
    print(f"   RMSE = {rmse:.2f} kcal")
    print(f"   Dataset size = {len(df)} samples\n")
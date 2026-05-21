# 🏃 Wearable AI Fitness Tracker

A real-time wearable fitness monitoring system built on the **ESP32 (Yolo UNO)** board that tracks heart rate, step count, and distance — then uses a trained **Machine Learning model** to predict calories burned and classify activity level.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [ML Pipeline](#ml-pipeline)
- [Live Prediction](#live-prediction)
- [Serial Data Format](#serial-data-format)
- [Configuration](#configuration)

---

## Overview

This project combines embedded firmware and a Python-based AI pipeline into a wearable device that can:

- **Measure heart rate** in real-time via the MAX30102 pulse sensor
- **Count steps and estimate distance** using the BMI160 accelerometer
- **Display live stats** on a 128×64 OLED screen
- **Stream sensor data** over serial (USB) to a PC
- **Predict calories burned** using a Random Forest regression model
- **Classify activity** as REST 💤 / WALK 🚶 / RUN 🏃 based on heart rate

---

## System Architecture

```
┌─────────────────────────────────────┐
│           ESP32 (Yolo UNO)          │
│                                     │
│  BMI160 Accelerometer               │
│    → Step detection (low-pass +     │
│      peak detection algorithm)      │
│    → Distance calculation           │
│                                     │
│  MAX30102 Heart Rate Sensor         │
│    → IR-based BPM measurement       │
│                                     │
│  SSD1306 OLED Display               │
│    → Live BPM / Steps / Distance    │
│                                     │
│  Serial Output (115200 baud)        │
│    → CSV stream to PC               │
└─────────────┬───────────────────────┘
              │ USB / Serial
              ▼
┌─────────────────────────────────────┐
│         Python (PC Side)            │
│                                     │
│  process_real.py → capture CSV      │
│  predict.py → live AI inference     │
│    - Random Forest model            │
│    - StandardScaler normalization   │
│    - Activity classification        │
└─────────────────────────────────────┘
```

---

## Hardware Requirements

| Component | Details |
|-----------|---------|
| Microcontroller | ESP32 — Yolo UNO board |
| Accelerometer | BMI160 (I2C address `0x69`) |
| Heart Rate Sensor | MAX30102 |
| Display | SSD1306 OLED 128×64 (I2C address `0x3C`) |
| Interface | I2C on pins SDA=11, SCL=12 |

---

## Software Requirements

**Firmware (PlatformIO)**

- [PlatformIO IDE](https://platformio.org/) (VS Code extension or CLI)
- Platform: `espressif32`
- Framework: `arduino`

Libraries (auto-installed via `platformio.ini`):

```
sparkfun/SparkFun MAX3010x Pulse and Proximity Sensor Library @ ^1.1.2
adafruit/Adafruit NeoPixel
kosme/arduinoFFT @ ^2.0.4
adafruit/Adafruit GFX Library @ ^1.12.6
adafruit/Adafruit SSD1306 @ ^2.5.16
```

**Python (ML Pipeline)**

- Python 3.8+
- Dependencies:

```bash
pip install pandas numpy scikit-learn joblib pyserial matplotlib
```

---

## Project Structure

```
Final_Project_ENG/
├── platformio.ini              # PlatformIO build config
├── boards/
│   └── yolo_uno.json           # Custom board definition
├── src/
│   ├── main.cpp                # Main firmware loop
│   ├── components/
│   │   ├── bmi.h / bmi.cpp     # BMI160 driver + step detection
│   │   ├── max.h / max.cpp     # MAX30102 heart rate driver
│   │   └── oled.h              # OLED display helpers
│   ├── data/
│   │   ├── Process.py          # Raw dataset cleaning script
│   │   └── calories_burned_data.csv  # Raw fitness dataset
│   ├── train.py                # ML model training
│   ├── predict.py              # Live serial inference
│   ├── process_real.py         # Serial data capture → CSV
│   ├── cleaned_data.csv        # Cleaned training data
│   ├── calorie_model.pkl       # Trained Random Forest model
│   └── scaler.pkl              # Fitted StandardScaler
└── test_code/
    ├── full_bmi_max30102_oled.txt  # Full integration test sketch
    └── oled_test.txt               # OLED-only test sketch
```

---

## Getting Started

### 1. Flash the Firmware

1. Open the project folder `Final_Project_ENG/` in VS Code with PlatformIO installed.
2. Connect the Yolo UNO board via USB.
3. Update the serial port in `platformio.ini` if needed (default: `COM3`).
4. Build and upload:

```bash
pio run --target upload
```

5. Open the serial monitor at **115200 baud** to verify sensor output.

### 2. Capture Live Data

Run `process_real.py` to collect ESP32 sensor data into a CSV file:

```bash
cd src
python process_real.py
```

Press `Ctrl+C` to stop. Data is saved to `esp32_data.csv`.

---

## ML Pipeline

### Data Preparation

`data/Process.py` cleans the raw `calories_burned_data.csv` and selects these features:

| Feature | Description |
|---------|-------------|
| Age | User age |
| Height (cm) | User height |
| Weight (kg) | User weight |
| BMI | Body Mass Index |
| Average Heart Rate | Mean BPM during activity |
| Distance (km) | Total distance covered |
| Running Time (min) | Duration of activity |
| **Calories Burned** | Target variable |

```bash
python data/Process.py
```

### Train the Model

`train.py` trains a **Random Forest Regressor** (300 estimators) with `StandardScaler` normalization and saves the model artifacts:

```bash
python train.py
# Output: calorie_model.pkl, scaler.pkl
```

---

## Live Prediction

`predict.py` reads the serial stream from the ESP32 in real-time, smooths the sensor readings using a rolling window buffer, and runs inference every loop:

```bash
python predict.py
```

**Update your user profile** at the top of `predict.py` before running:

```python
USER_AGE    = 22
USER_HEIGHT = 175   # cm
USER_WEIGHT = 70    # kg
```

Example output:

```
========================
Heart Rate : 125.3 BPM
Steps      : 1042
Distance   : 0.78 km
Activity   : WALK 🚶
🔥 Calories : 87.43
========================
```

**Activity classification thresholds:**

| Average BPM | Activity |
|-------------|----------|
| < 90 | REST 💤 |
| 90 – 130 | WALK 🚶 |
| > 130 | RUN 🏃 |

---

## Serial Data Format

The ESP32 streams CSV lines over serial at 115200 baud:

```
<time_ms>,<bpm>,<steps>,<distance_km>
```

Example:

```
12450,72.5,340,0.255
```

Lines containing `time_ms` or `SYSTEM` are treated as headers/debug and skipped by the Python scripts.

---

## Configuration

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| Serial port | `platformio.ini` / `predict.py` | `COM3` | USB port of the board |
| I2C pins | `main.cpp` | SDA=11, SCL=12 | Wire bus pins |
| Step threshold | `bmi.cpp` | `300` | Acceleration magnitude threshold |
| Step debounce | `bmi.cpp` | `300 ms` | Minimum time between steps |
| Step length | `bmi.cpp` | `0.75 m` | Assumed stride length |
| BPM smoothing | `max.cpp` | `0.7 / 0.3` | EMA weights (old/new) |
| Prediction window | `predict.py` | `30 samples` | Rolling buffer size |

import serial
import pandas as pd
import time

# =========================
# CONFIG
# =========================
PORT = "COM3"        # change this (Windows: COM3, COM4...)
BAUD = 115200
OUTPUT_FILE = "esp32_data.csv"

# =========================
# OPEN SERIAL
# =========================
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print("Reading ESP32 data... Press Ctrl+C to stop")

data = []

try:
    while True:
        line = ser.readline().decode("utf-8").strip()

        if not line:
            continue

        # skip headers or debug text
        if "time_ms" in line or "SYSTEM" in line:
            continue

        parts = line.split(",")

        # expect: time_ms,bpm,steps,distance
        if len(parts) == 4:
            try:
                row = {
                    "time_ms": float(parts[0]),
                    "bpm": float(parts[1]),
                    "steps": int(parts[2]),
                    "distance": float(parts[3])
                }

                data.append(row)

                print(row)

            except:
                continue

except KeyboardInterrupt:
    print("\nStopping... saving CSV")

# =========================
# EXPORT CSV
# =========================
df = pd.DataFrame(data)
df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved to {OUTPUT_FILE}")
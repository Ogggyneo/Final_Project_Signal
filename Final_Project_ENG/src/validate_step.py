"""
validate_steps.py
Compare device step counts against a manual (ground-truth) count.
Run this while connected to the ESP32 over serial.

Usage:
    python validate_steps.py
Then walk a known number of steps, press Enter to record each trial.
"""

import serial
import time
import os

# =========================
# CONFIG
# =========================
PORT = "COM3"       # change to your port (Mac: /dev/cu.usbserial-*, Linux: /dev/ttyUSB0)
BAUD = 115200

# =========================
# RESULTS TABLE
# =========================
results = []

def get_current_steps(ser, timeout=3):
    """Read the latest step count from the ESP32 serial stream."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            line = ser.readline().decode("utf-8").strip()
            if not line or "SYSTEM" in line or "time_ms" in line:
                continue
            parts = line.split(",")
            if len(parts) == 4:
                steps = int(float(parts[2]))
                return steps
        except Exception:
            continue
    return None

def run_validation():
    print("\n==============================================")
    print("  STEP COUNT VALIDATION")
    print("==============================================")
    print(f"  Port: {PORT}  |  Baud: {BAUD}")
    print("  Instructions:")
    print("  1. Enter how many steps you PLAN to walk")
    print("  2. Walk exactly that many steps")
    print("  3. Press Enter — the device count is recorded")
    print("  4. Repeat for each trial")
    print("  Type 'done' to finish and see results\n")

    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)
        print("  Serial connected ✔\n")
    except Exception as e:
        print(f"  Serial connection failed: {e}")
        print("  Running in OFFLINE mode — enter device counts manually.\n")
        ser = None

    trial = 1
    while True:
        manual_input = input(f"  Trial {trial} — planned steps (or 'done'): ").strip()
        if manual_input.lower() == "done":
            break

        try:
            manual_count = int(manual_input)
        except ValueError:
            print("  Please enter a number.")
            continue

        if ser:
            # reset hint
            print(f"  Walk {manual_count} steps now, then press Enter...")
            input()
            device_count = get_current_steps(ser)
            if device_count is None:
                device_count = int(input("  Could not read serial — enter device count manually: "))
        else:
            device_count = int(input(f"  Enter the step count shown on the device: "))

        error_pct = abs(device_count - manual_count) / manual_count * 100
        results.append({
            "trial":    trial,
            "manual":   manual_count,
            "device":   device_count,
            "error":    device_count - manual_count,
            "error_%":  round(error_pct, 1),
        })
        print(f"  → Device: {device_count}  |  Error: {device_count - manual_count} steps ({error_pct:.1f}%)\n")
        trial += 1

    if ser:
        ser.close()

    # =========================
    # PRINT RESULTS TABLE
    # =========================
    if not results:
        print("  No trials recorded.")
        return

    print("\n==============================================")
    print("  RESULTS")
    print(f"  {'Trial':<8} {'Manual':<10} {'Device':<10} {'Error':<10} {'Error %'}")
    print("  " + "-" * 46)
    for r in results:
        sign = "+" if r["error"] > 0 else ""
        print(f"  {r['trial']:<8} {r['manual']:<10} {r['device']:<10} {sign}{r['error']:<10} {r['error_%']} %")

    avg_err     = sum(abs(r["error"]) for r in results) / len(results)
    avg_err_pct = sum(r["error_%"] for r in results) / len(results)
    print("  " + "-" * 46)
    print(f"  {'Average':<8} {'':<10} {'':<10} {avg_err:<10.1f} {avg_err_pct:.1f} %")
    print("==============================================\n")

    # =========================
    # SAVE TO CSV
    # =========================
    import csv
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "step_validation.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["trial", "manual", "device", "error", "error_%"])
        writer.writeheader()
        writer.writerows(results)
    print(f"  Saved to: {out_path}")

if __name__ == "__main__":
    run_validation()
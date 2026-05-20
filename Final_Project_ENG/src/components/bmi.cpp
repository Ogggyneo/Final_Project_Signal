#include <Arduino.h>
#include "bmi.h"
#include <Wire.h>
#include <math.h>

// ================= GLOBAL VARIABLES =================
int stepCount = 0;

float prevAcc = 0;
float filteredAcc = 0;
float prevFiltered = 0;

float alpha = 0.9;  // smoothing factor

unsigned long lastStepTime = 0;
const int stepDelay = 300; // ms debounce

float stepLength = 0.75; // meters (average walking/jogging)

// ================= INIT BMI160 =================
void initBMI160()
{
    Wire.begin(11, 12);
    Wire.setClock(100000);

    Wire.beginTransmission(BMI160_ADDR);
    Wire.write(0x7E);   // command register
    Wire.write(0x11);   // accelerometer normal mode

    byte error = Wire.endTransmission();

    if (error == 0)
    {
        Serial.println("BMI160 INIT OK");
    }
    else
    {
        Serial.print("BMI160 INIT FAIL: ");
        Serial.println(error);
    }

    delay(100);
}

// ================= READ ACCELERATION =================
bool readBMI160(int16_t &ax, int16_t &ay, int16_t &az)
{
    Wire.beginTransmission(BMI160_ADDR);
    Wire.write(0x12);

    if (Wire.endTransmission(false) != 0)
        return false;

    if (Wire.requestFrom(BMI160_ADDR, 6) != 6)
        return false;

    ax = (int16_t)(Wire.read() | (Wire.read() << 8));
    ay = (int16_t)(Wire.read() | (Wire.read() << 8));
    az = (int16_t)(Wire.read() | (Wire.read() << 8));

    return true;
}

// ================= ACC MAGNITUDE =================
float calculateAccelerationMagnitude(int16_t ax, int16_t ay, int16_t az)
{
    return sqrt(ax * ax + ay * ay + az * az);
}

// ================= STEP DETECTION =================
void detectStep(float acc)
{
    // low-pass filter (smooth signal)
    filteredAcc = alpha * filteredAcc + (1 - alpha) * acc;

    float diff = filteredAcc - prevFiltered;

    unsigned long now = millis();

    // peak detection + debounce
    if (prevFiltered > 0 &&
        diff < 0 &&
        filteredAcc > 300 &&   // threshold (adjust if needed)
        (now - lastStepTime > stepDelay))
    {
        stepCount++;
        lastStepTime = now;

        Serial.print("STEP: ");
        Serial.println(stepCount);
    }

    prevFiltered = filteredAcc;
}

// ================= DISTANCE =================
float getDistanceKm()
{
    return (stepCount * stepLength) / 1000.0;
}
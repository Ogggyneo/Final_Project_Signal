#include <Arduino.h>
#include "bmi.h"
#include <Wire.h>
#include <math.h>

// ===== GLOBAL VARIABLES =====
int stepCount = 0;

float prevAcc = 0;
float prevFiltered = 0;

// ===== INIT BMI160 =====
void initBMI160()
{
    Wire.begin(11, 12);   // SDA=11 SCL=12
    Wire.setClock(100000);

    Wire.beginTransmission(BMI160_ADDR);

    Wire.write(0x7E);     // CMD register
    Wire.write(0x11);     // ACC normal mode

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

// ===== READ ACC DATA =====
bool readBMI160(int16_t &ax, int16_t &ay, int16_t &az)
{
    Wire.beginTransmission(BMI160_ADDR);
    Wire.write(0x12);

    if (Wire.endTransmission(false) != 0)
    {
        return false;
    }

    int bytesReceived = Wire.requestFrom(BMI160_ADDR, 6);

    if (bytesReceived != 6)
    {
        return false;
    }

    ax = (int16_t)(Wire.read() | (Wire.read() << 8));
    ay = (int16_t)(Wire.read() | (Wire.read() << 8));
    az = (int16_t)(Wire.read() | (Wire.read() << 8));

    return true;
}

// ===== CALCULATE MAGNITUDE =====
float calculateAccelerationMagnitude(int16_t ax, int16_t ay, int16_t az)
{
    float fax = (float)ax;
    float fay = (float)ay;
    float faz = (float)az;

    return sqrt(fax * fax + fay * fay + faz * faz);
}

// ===== STEP DETECTION =====
void detectStep(float acc)
{
    // high-pass like filter
    float filtered = acc - prevAcc;

    float diff = filtered - prevFiltered;

    // peak detection
    if (prevFiltered > 0 &&
        diff < 0 &&
        filtered > 400)
    {
        stepCount++;

        Serial.print("STEP: ");
        Serial.println(stepCount);
    }

    prevAcc = acc;
    prevFiltered = filtered;
}
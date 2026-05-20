#include <Arduino.h>
#include <Wire.h>
#include "components\bmi.h"
#include "components\max.h"

void setup()
{
    Serial.begin(115200);
    delay(3000);
    
    Serial.println();

    Serial.println("SYSTEM START");
    //BMI
    initBMI160();
    Serial.println("BMI160 READY");
    //MAX
    if(!initMAX30102())
    {
        Serial.println("MAX30102 INIT FAIL");
    }
    else
    {
        Serial.println("MAX30102 READY");
    }
}

void loop()
{
    // BMI160 variables
    int16_t ax, ay, az;

    // read accelerometer
    if (readBMI160(ax, ay, az))
    {
        // calculate acceleration magnitude
        float acc =
            calculateAccelerationMagnitude(ax, ay, az);

        // detect steps
        detectStep(acc);

        // debug print
        // Serial.print("AX: ");
        // Serial.print(ax);
        // Serial.print(" AY: ");
        // Serial.print(ay);
        // Serial.print(" AZ: ");
        // Serial.print(az);
        // Serial.print(" | MAG: ");
        // Serial.print(acc);
    }
    else
    {
        Serial.println("BMI160 READ FAIL");
    }
    //max30102 variables
    float bpm = readHeartRate();
    // print data
    Serial.print("BPM: ");
    Serial.println(bpm);
    Serial.print(" | STEPS: ");
    Serial.println(stepCount);

    delay(50);
}
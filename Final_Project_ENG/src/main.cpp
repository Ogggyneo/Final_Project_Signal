#include <Arduino.h>
#include <Wire.h>

#include "components/bmi.h"

void setup()
{
    Serial.begin(115200);

    delay(5000);

    Serial.println("START");

    Wire.begin();

    initBMI160();

    Serial.println("BMI READY");
}

void loop()
{
    Serial.println("XYZ");

    int16_t ax, ay, az;

    readBMI160(ax, ay, az);

    Serial.print("AX: ");
    Serial.print(ax);

    Serial.print(" AY: ");
    Serial.print(ay);

    Serial.print(" AZ: ");
    Serial.println(az);

    delay(1000);
}
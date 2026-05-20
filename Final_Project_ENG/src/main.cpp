#include <Arduino.h>

void setup()
{
    Serial.begin(115200);

    delay(5000);

    Serial.println();
    Serial.println("HELLO ESP32");
}

void loop()
{
    Serial.println("RUNNING");

    delay(1000);
}
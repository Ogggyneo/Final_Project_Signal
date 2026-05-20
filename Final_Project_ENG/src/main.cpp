// 

#include <Arduino.h>

void setup()
{
    Serial.begin(115200);
    delay(2000);

    Serial.println("HELLO");
}

void loop()
{
    Serial.println("RUNNING");
    delay(1000);
}
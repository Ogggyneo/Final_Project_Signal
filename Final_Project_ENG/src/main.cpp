#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "components/bmi.h"
#include "components/max.h"

// ================= OLED =================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ================= SETUP =================
void setup()
{
    Serial.begin(115200);
    delay(3000);

    // ✅ USE YOUR PINS
    Wire.begin(11, 12);
    Wire.setClock(100000);

    Serial.println("SYSTEM START");

    // ================= OLED INIT =================
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
    {
        Serial.println("OLED FAIL (try 0x3D)");
        while (1);
    }

    display.clearDisplay();
    display.display();

    // ================= SENSOR INIT =================
    initBMI160();
    initMAX30102();

    Serial.println("SENSORS READY");
}

// ================= LOOP =================
void loop()
{
    static unsigned long lastDraw = 0;

    int16_t ax, ay, az;
    float distance = 0;

    // ================= BMI =================
    if (readBMI160(ax, ay, az))
    {
        float acc = calculateAccelerationMagnitude(ax, ay, az);
        detectStep(acc);
        distance = getDistanceKm();
    }

    // ================= HEART RATE =================
    float bpm = readHeartRate();

    // ================= SERIAL CSV =================
    Serial.print(millis());
    Serial.print(",");
    Serial.print(bpm);
    Serial.print(",");
    Serial.print(stepCount);
    Serial.print(",");
    Serial.println(distance);

    // ================= OLED (STABLE UPDATE) =================
    if (millis() - lastDraw > 200)
    {
        lastDraw = millis();

        display.clearDisplay();

        display.setTextSize(1);
        display.setTextColor(WHITE);

        display.setCursor(0, 0);
        display.println("WEARABLE AI");

        display.setCursor(0, 15);
        display.print("BPM: ");
        display.println(bpm);

        display.setCursor(0, 30);
        display.print("Steps: ");
        display.println(stepCount);

        display.setCursor(0, 45);
        display.print("Dist: ");
        display.println(distance);

        display.display();
    }

    delay(50);
}
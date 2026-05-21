#ifndef OLED_TIMER_H
#define OLED_TIMER_H

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ===== OLED CONFIG =====
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

// ===== DISPLAY OBJECT =====
extern Adafruit_SSD1306 display;

// ===== TIMER VARIABLES =====
extern int totalSeconds;
extern unsigned long previousMillis;
extern const long interval;

// ===== FUNCTIONS =====
void setup();
void loop();

#endif
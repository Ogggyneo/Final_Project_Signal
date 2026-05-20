#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup() {
  Serial.begin(115200);
  delay(2000);

  Wire.begin(11, 12);
  Wire.setClock(100000);

  Serial.println("=== OLED TEST ===");

  // thử init với 0x3C trước
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("⚠️ thử 0x3D...");

    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3D)) {
      Serial.println("OLED NOT FOUND");
      while (1);
    }
  }

  Serial.println("OLED FOUND");

  display.ssd1306_command(SSD1306_DISPLAYON);
  delay(100);

  // TEST 1: HELLO
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(0, 10);
  display.println("HELLO");
  display.display();

  delay(2000);

  // TEST 2: FULL PIXEL
  display.clearDisplay();
  for (int x = 0; x < SCREEN_WIDTH; x++) {
    for (int y = 0; y < SCREEN_HEIGHT; y++) {
      display.drawPixel(x, y, WHITE);
    }
  }
  display.display();

  delay(2000);

  // TEST 3: CLEAR
  display.clearDisplay();
  display.display();
}

void loop() {}
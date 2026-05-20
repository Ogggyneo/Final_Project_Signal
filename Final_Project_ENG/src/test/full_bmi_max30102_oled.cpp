#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "MAX30105.h"

// ===== OLED =====
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ===== MAX30102 =====
MAX30105 particleSensor;
float bpm = 0;
long lastBeat = 0;
long prevIR = 0;
long prevDiffIR = 0;

// ===== BMI160 =====
#define BMI160_ADDR 0x69

// STEP variables
int stepCount = 0;
float prevAcc = 0;
float prevDiffAcc = 0;

// ===== INIT BMI160 =====
void initBMI160() {
  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(0x7E);   // CMD register
  Wire.write(0x11);   // ACC normal mode
  Wire.endTransmission();
  delay(100);
}

// ===== READ ACC =====
void readBMI160(int16_t &ax, int16_t &ay, int16_t &az) {
  Wire.beginTransmission(BMI160_ADDR);
  Wire.write(0x12);
  Wire.endTransmission(false);

  Wire.requestFrom(BMI160_ADDR, 6);

  ax = Wire.read() | (Wire.read() << 8);
  ay = Wire.read() | (Wire.read() << 8);
  az = Wire.read() | (Wire.read() << 8);
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  Wire.begin(11, 12);
  Wire.setClock(100000);

  // ===== OLED =====
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3D)) {
      Serial.println("OLED FAIL");
      while (1);
    }
  }
  display.clearDisplay();
  display.setTextColor(WHITE);

  // ===== MAX30102 =====
  if (!particleSensor.begin(Wire)) {
    Serial.println("MAX30102 FAIL");
    while (1);
  }
  particleSensor.setup(60, 4, 2, 100, 411, 4096);
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);

  // ===== BMI160 =====
  initBMI160();

  Serial.println("SYSTEM READY");
}

void loop() {

  // ===== BPM =====
  long ir = particleSensor.getIR();
  long diffIR = ir - prevIR;

  if (prevDiffIR > 0 && diffIR < 0 && ir > 50000) {
    long now = millis();
    long delta = now - lastBeat;
    lastBeat = now;

    float newBPM = 60.0 / (delta / 1000.0);

    if (newBPM > 40 && newBPM < 180) {
      bpm = 0.7 * bpm + 0.3 * newBPM;
    }
  }

  prevDiffIR = diffIR;
  prevIR = ir;

  // ===== STEP (IMPROVED) =====
  int16_t ax, ay, az;
  readBMI160(ax, ay, az);

  float acc = sqrt(ax * ax + ay * ay + az * az);

  float filtered = acc - prevAcc;
  float diffAcc = filtered - prevDiffAcc;

  // detect step peak
  if (prevDiffAcc > 0 && diffAcc < 0 && filtered > 400) {
    stepCount++;
  }

  prevAcc = acc;
  prevDiffAcc = filtered;

  // ===== OLED =====
  display.clearDisplay();

  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("WEARABLE");

  display.setTextSize(2);
  display.setCursor(0, 20);
  display.print("BPM:");
  display.println((int)bpm);

  display.setCursor(0, 45);
  display.print("STEP:");
  display.println(stepCount);

  display.display();

  // ===== DEBUG =====
  Serial.print("BPM: ");
  Serial.print(bpm);
  Serial.print(" | STEP: ");
  Serial.println(stepCount);

  delay(50);
}
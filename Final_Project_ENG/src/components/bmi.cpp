#include <Arduino.h>
#include "bmi.h"
#include <Wire.h>
#include <math.h>

//global variables
int StepCount = 0;
float prevAcc = 0;
float prevDiffAcc = 0;

// init 
void initBMI160(){
    Wire.beginTransmission(BMI160_ADDR);
    Wire.write(0x7E);   // CMD register
    Wire.write(0x11);   // ACC normal mode
    Wire.endTransmission();
    delay(100);
}
// read acc data 

void readBMI160(int16_t &ax, int16_t &ay, int16_t &az){
    Wire.beginTransmission(BMI160_ADDR);
    Wire.write(0x12);
    Wire.endTransmission(false);

    Wire.requestFrom(BMI160_ADDR, 6);

    ax = Wire.read() | (Wire.read() << 8);
    ay = Wire.read() | (Wire.read() << 8);
    az = Wire.read() | (Wire.read() << 8);
}
// calculate magnitude 
float calculateAccelerationMagnitude(int16_t ax, int16_t ay, int16_t az){
    return sqrt((float)(ax * ax + ay * ay + az * az));
}
//step detection 
void detectStep (float acc){
    float filtered = acc - prevAcc;
    float diffAcc = filtered - prevDiffAcc;

    // detect step peak
    if (prevDiffAcc > 0 && diffAcc < 0 && filtered > 400) {
        StepCount++;
    }

    prevAcc = acc;
    prevDiffAcc = filtered;
}
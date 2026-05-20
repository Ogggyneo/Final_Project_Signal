#include <Arduino.h>
#include "D:\SPRING(1)\ENG\Final_Project_Signal\Final_Project_ENG\src\components\bmi.h"
void loop(){
  //BMI
    int16_t ax, ay, az;
    readBMI160(ax, ay, az);
    float acc = calculateAccelerationMagnitude(ax, ay, az);
    detectStep(acc);
}
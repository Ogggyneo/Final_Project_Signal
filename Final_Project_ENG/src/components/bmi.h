#ifndef BMI_H
#define BMI_H
#include <Arduino.h>
#define BMI160_ADDR 0x69
//global variables
extern int StepCount;
extern float prevAcc, prevDiffAcc;
// function declare 
void initBMI160();
void readBMI160(int16_t &ax, int16_t &ay, int16_t &az);
void CalculateAcc(int16_t ax, int16_t ay, int16_t az);
void detectStep(float acc);

#endif
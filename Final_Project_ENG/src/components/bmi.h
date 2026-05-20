#ifndef BMI_H
#define BMI_H
#include <Arduino.h>
#define BMI160_ADDR 0x69
//global variables
extern int stepCount;
// filter 
extern float alpha;
extern float filteredAcc;
extern float prevFilteredAcc;


// function declare 
void initBMI160();

bool readBMI160(int16_t &ax, int16_t &ay, int16_t &az);

float calculateAccelerationMagnitude(int16_t ax, int16_t ay, int16_t az);

void detectStep(float acc);

float getDistanceKm();

#endif
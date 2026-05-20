#ifndef MAX_H
#define MAX_H

#include <Arduino.h>
#include "MAX30105.h"
extern MAX30105 particleSensor;
extern float bpm;

extern long lastBeat;
extern long prevIR;
extern long prevDiffIR;

bool initMAX30102();

float readHeartRate();

#endif
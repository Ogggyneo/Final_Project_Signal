#include "max.h"
#include <Wire.h>

MAX30105 particleSensor;
float bpm = 0;
long lastBeat = 0;
long prevIR = 0;
long prevDiffIR = 0;

bool initMAX30102()
{
    if (!particleSensor.begin(Wire))
    {
        return false;
    }

    particleSensor.setup(
        60,     // brightness
        4,      // average
        2,      // LED mode
        100,    // sample rate
        411,    // pulse width
        4096    // ADC range
    );

    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);

    return true;
}

float readHeartRate()
{
    long ir = particleSensor.getIR();

    long diffIR = ir - prevIR;

    if (
        prevDiffIR > 0 &&
        diffIR < 0 &&
        ir > 50000
    )
    {
        long now = millis();

        long delta = now - lastBeat;

        lastBeat = now;

        float newBPM =
            60.0 / (delta / 1000.0);

        if (newBPM > 40 && newBPM < 180)
        {
            bpm = 0.7 * bpm + 0.3 * newBPM;
        }
    }

    prevDiffIR = diffIR;
    prevIR = ir;

    return bpm;
}
#pragma once

#include "utility.h"
const short num_buffers = 2;
class AnalogReader;
class FeatureExtractor {
public:
    FeatureExtractor(){
        for (int i = 0;i<num_buffers;i++)
            for (int j = 0;j<num_features;j++)
                buffer[i][j] = 0;
        la[0] = 0;
        la[1] = 0;
        la[2] = 0;
        la[3] = 0;
     }
    bool update();
    float buffer[num_buffers][num_features];
    byte activeBuffer = 0;
    float la[4];
    AnalogReader *reader;
private:
    byte it=0;
};
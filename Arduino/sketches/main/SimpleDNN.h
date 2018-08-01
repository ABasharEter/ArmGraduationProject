#pragma once
#include "utility.h"
#include "FeatureExtractor.h"
class SimpleDNN{
public:
    float output1[num_output1];
    float output2[num_output2];
    void process();
    void run(){ is_running = true; }
    FeatureExtractor* fe;
private:
    bool is_running = false;
    byte it = 0;
    float buffer[num_hidden];
};
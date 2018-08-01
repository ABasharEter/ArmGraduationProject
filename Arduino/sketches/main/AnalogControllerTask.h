#pragma once
#include "utility.h"
#include "FeatureExtractor.h"
#include "AnalogReader.h"
#include "SimpleDNN.h"
template<unsigned short TS>
class AnalogControllerTask {
public:
    AnalogControllerTask() {
        last_time = -1;
        fe.reader = &reader;
        dnn.fe = &fe;
    }
    inline void run() {
        if(last_time == -1)
            last_time = micros();
        else {
            if(micros()-last_time < ts()+10){
                delayMicroseconds(micros()-last_time);
            }
            else if(micros()-last_time > ts()+10)
                digitalWrite(8,LOW);
            digitalWrite(8,HIGH);
            reader.Read();
            if(fe.update()){
                dnn.run();
            }
            dnn.process();
            last_time = micros();
        }
    }
    
    inline static constexpr int ts() { return TS; };
    AnalogReader reader;
    FeatureExtractor fe;
    SimpleDNN dnn;
private:
    long long last_time;
};

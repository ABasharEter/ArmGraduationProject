#pragma once
#include "utility.h"

template<unsigned short TS>
class AnalogReadingTask {
public:
    AnalogReadingTask() {
        last_time = -1;
    }
    inline void run() {
        if(last_time == -1)
            last_time = micros();
        else {
            if(micros()-last_time < ts()+10){
                delayMicroseconds(micros()-last_time);
            }else if(micros()-last_time > ts()+10)
                digitalWrite(8,LOW);
            digitalWrite(8,HIGH);
            reader.Read();
            reader.dump();
            last_time = micros();
        }
    }
    inline static constexpr int ts() { return TS; };
    AnalogReader reader;
private:
    long long last_time;
};

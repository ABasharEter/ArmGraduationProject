#pragma once

#include <Arduino.h>
#include "utility.h"
inline void fastADC(){
 sbi(ADCSRA,ADPS2);
 cbi(ADCSRA,ADPS1);
 cbi(ADCSRA,ADPS0);
}
class AnalogReader {
public:
    void Read();
    void dumpPacked();
    void dump();
    union {struct{short x0,x1,x2,x3;};short a[4];};
private:
};

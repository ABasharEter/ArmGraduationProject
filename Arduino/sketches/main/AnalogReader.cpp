#include "AnalogReader.h"
#include <Arduino.h>

void AnalogReader::Read()
{
    x0 = analogRead(A0);
    x1 = analogRead(A1);
    x2 = analogRead(A2);
    x3 = analogRead(A3);
}

void AnalogReader::dump()
{
    Serial.print(x0);
    Serial.print(",");
    Serial.print(x1);
    Serial.print(",");
    Serial.print(x2);
    Serial.print(",");
    Serial.println(x3);
}

void AnalogReader::dumpPacked()
{
    uint64_t v = x0|x1<<10ull|((uint64_t)x2)<<20ull|((uint64_t)x3)<<30ull;
    uint32_t v1 = v;
    byte v2 = v>>32;
    Serial.println(v1);
    Serial.println(v2);
}

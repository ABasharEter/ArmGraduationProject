#include <Arduino.h>
#include "utility.h"
#include "AnalogReader.h"
#include "AnalogReaderTask.h"


AnalogReadingTask<1000> t;

void setup() {
  // initialize serial communication at 115200 bits per second:
  Serial.begin(115200);
  pinMode(12, OUTPUT); 
  fastADC();
}
bool is;
void loop() {
  digitalWrite(12,is);
  is = !is;
  t.run();
} 

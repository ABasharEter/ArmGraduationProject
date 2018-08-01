#include "utility.h"
#include "AnalogReader.h"
#include "AnalogReaderTask.h"
#include "AnalogControllerTask.h"

#define ADC_Mode LOW

AnalogReadingTask<1000> adc_t;
AnalogControllerTask<1000> afe_t;

const int output1_up_probability_pin = 5;
const int output1_down_probability_pin = 3;
const int output2_grape_direction_pin = 9;
const int output2_extend_probability_pin = 6;
const int freq_pin = 12;
const int mode_pin = 7;
const int error_pin = 8;

void setup() {
  // initialize serial communication at 115200 bits per second:
  Serial.begin(115200);
  pinMode(freq_pin, OUTPUT); 
  pinMode(mode_pin, INPUT); 
  pinMode(error_pin, OUTPUT); 
  pinMode(output1_up_probability_pin, OUTPUT);
  pinMode(output1_down_probability_pin, OUTPUT);
  pinMode(output2_grape_direction_pin, OUTPUT);
  pinMode(output2_extend_probability_pin, OUTPUT);
  fastADC();
}
bool is;
void loop() {
  digitalWrite(freq_pin,is);
  is = !is;
  mode = digitalRead(mode_pin);
  if(ADC_Mode == mode)
    adc_t.run(); 
  else
  {
    afe_t.run();
    byte idx = 0;
    if(afe_t.dnn.output1[idx] < afe_t.dnn.output1[1])
      idx = 1;
    else if(afe_t.dnn.output1[idx] < afe_t.dnn.output1[2])
      idx = 2;
    if(idx == 1){
      analogWrite(output1_down_probability_pin,0);
      analogWrite(output1_up_probability_pin,0);
      analogWrite(output1_down_probability_pin,0);
    }
    else if(idx == 0){
      analogWrite(output1_up_probability_pin,(byte)(afe_t.dnn.output1[idx]*255));
      analogWrite(output1_down_probability_pin,0);
    }
    else{
      analogWrite(output1_up_probability_pin,0);
      analogWrite(output1_down_probability_pin,(byte)(afe_t.dnn.output1[idx]*255));
    }

    idx = 0;
    if(afe_t.dnn.output2[idx] < afe_t.dnn.output2[1])
      idx = 1;
    else if(afe_t.dnn.output2[idx] < afe_t.dnn.output2[2])
      idx = 2;
    if(idx == 1){
      analogWrite(output2_grape_direction_pin,0);
      analogWrite(output2_grape_direction_pin,0);
    }
    else if(idx == 0){
      analogWrite(output2_grape_direction_pin,(byte)(afe_t.dnn.output2[idx]*255));
      analogWrite(output2_extend_probability_pin,0);
    }
    else{
      analogWrite(output2_grape_direction_pin,0 );
      analogWrite(output2_extend_probability_pin,(byte)(afe_t.dnn.output2[idx]*255));
    }
  }
} 

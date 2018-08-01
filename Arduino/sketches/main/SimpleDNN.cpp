#include "utility.h"
#include "AnalogReader.h"
#include "FeatureExtractor.h"
#include "SimpleDNN.h"

float dot(const float* w,float* a,int n){
    float ans = w[0];
    w++;
    for(int i=0;i<n;i++)
        ans += w[i]*a[i];
    return ans;
}

float dot2(uint16_t address,float* a,int n){
    float ans = pgm_read_float_near(address);
    address++;
    for(int i=0;i<n;i++)
        ans += pgm_read_float_near(address+i)*a[i];
    return ans;
}

float sigmoid(float a){
    return 1/(1+exp(-a));
}

const int process_chunk =6; 

void SimpleDNN::process(){
    if(is_running){
        if(it >=num_hidden){
            for(byte i=0;i<num_output1;i++)
                output1[i] = sigmoid(dot2((uint16_t)(o1_mat +i*(num_hidden+1)),buffer,num_hidden));
            for(byte i=0;i<num_output2;i++)
                output2[i] = sigmoid(dot2((uint16_t)(o2_mat+i*(num_hidden+1)),buffer,num_hidden));
            it = 0;
            is_running = false;
        }else{
            byte last = it+process_chunk;
            for(byte i=it;i<last;i++){
                buffer[i] = sigmoid(dot2((uint16_t)(h_mat+i*(num_features+1)),fe->buffer[fe->activeBuffer],num_features));
            }
            it=last;
        }
    }
}
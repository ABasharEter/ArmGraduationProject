#include "utility.h"
#include "AnalogReader.h"
#include "FeatureExtractor.h"

#define Ch0_min         0
#define Ch1_min         1
#define Ch2_min         2
#define Ch3_min         3

#define Ch0_max         4
#define Ch1_max         5
#define Ch2_max         6
#define Ch3_max         7

#define Ch0_avg         8
#define Ch1_avg         9
#define Ch2_avg         10
#define Ch3_avg         11

#define Ch0_energy      12
#define Ch1_energy      13
#define Ch2_energy      14
#define Ch3_energy      15

#define Ch0_iemg        16
#define Ch1_iemg        17
#define Ch2_iemg        18
#define Ch3_iemg        19

#define Ch0_mav         20
#define Ch1_mav         21
#define Ch2_mav         22
#define Ch3_mav         23

#define Ch0_var         24
#define Ch1_var         25
#define Ch2_var         26
#define Ch3_var         27

#define Ch0_rms         28
#define Ch1_rms         29
#define Ch2_rms         30
#define Ch3_rms         31

#define Ch0_wl          32
#define Ch1_wl          33
#define Ch2_wl          34
#define Ch3_wl          35

#define Ch0_zc0         36
#define Ch1_zc0         37
#define Ch2_zc0         38
#define Ch3_zc0         39

#define Ch0_hemg0       40
#define Ch1_hemg0       41
#define Ch2_hemg0       42
#define Ch3_hemg0       43

#define Ch0_hemg1       44
#define Ch1_hemg1       45
#define Ch2_hemg1       46
#define Ch3_hemg1       47


#define Ch0_sqr      Ch0_energy
#define Ch1_sqr      Ch1_energy
#define Ch2_sqr      Ch2_energy
#define Ch3_sqr      Ch3_energy


#define Ch0_abs     Ch0_iemg
#define Ch1_abs     Ch0_iemg
#define Ch2_abs     Ch0_iemg
#define Ch3_abs     Ch0_iemg

const short windowSize = 150;
const float histogram_splits[] = {-2.5,0,2.5};
const float correction_a = -2.5+0.7/2.0;
const float correction_b = 5.0/1024.0;

bool FeatureExtractor::update(){
    byte bufferindex = activeBuffer+1;
    if(bufferindex>=num_buffers)
        bufferindex=0;
    float x0 = reader->x0*correction_b+correction_a;
    float x1 = reader->x0*correction_b+correction_a;
    float x2 = reader->x0*correction_b+correction_a;
    float x3 = reader->x0*correction_b+correction_a;

    buffer[bufferindex][Ch0_min] = min(buffer[bufferindex][Ch0_min],x0);
    buffer[bufferindex][Ch1_min] = min(buffer[bufferindex][Ch1_min],x1);
    buffer[bufferindex][Ch2_min] = min(buffer[bufferindex][Ch2_min],x2);
    buffer[bufferindex][Ch3_min] = min(buffer[bufferindex][Ch3_min],x3);
    
    buffer[bufferindex][Ch0_max] = max(buffer[bufferindex][Ch0_max],x0);
    buffer[bufferindex][Ch1_max] = max(buffer[bufferindex][Ch1_max],x1);
    buffer[bufferindex][Ch2_max] = max(buffer[bufferindex][Ch2_max],x2);
    buffer[bufferindex][Ch3_max] = max(buffer[bufferindex][Ch3_max],x3);

    buffer[bufferindex][Ch0_avg] += x0;
    buffer[bufferindex][Ch1_avg] += x1;
    buffer[bufferindex][Ch2_avg] += x2;
    buffer[bufferindex][Ch3_avg] += x3;

    buffer[bufferindex][Ch0_sqr] += x0*x0;
    buffer[bufferindex][Ch1_sqr] += x1*x1;
    buffer[bufferindex][Ch2_sqr] += x2*x2;
    buffer[bufferindex][Ch3_sqr] += x3*x3;

    buffer[bufferindex][Ch0_abs] += abs(x0);
    buffer[bufferindex][Ch1_abs] += abs(x1);
    buffer[bufferindex][Ch2_abs] += abs(x2);
    buffer[bufferindex][Ch3_abs] += abs(x3);

    
    buffer[bufferindex][Ch0_wl] += x0-la[0];
    buffer[bufferindex][Ch1_wl] +=  x1-la[1];
    buffer[bufferindex][Ch2_wl] += x2-la[2];
    buffer[bufferindex][Ch3_wl] +=  x3-la[3];

    buffer[bufferindex][Ch0_zc0] += ((x0>0) != (la[0]>0));
    buffer[bufferindex][Ch1_zc0] += ((x1>0) != (la[1]>0));
    buffer[bufferindex][Ch2_zc0] += ((x2>0) != (la[2]>0));
    buffer[bufferindex][Ch3_zc0] +=  ((x3>0) != (la[3]>0));

    buffer[bufferindex][Ch0_hemg0] += (x0 >= histogram_splits[0] && x0 < histogram_splits[1]);
    buffer[bufferindex][Ch1_hemg0] += (x1 >= histogram_splits[0] && x1 < histogram_splits[1]);
    buffer[bufferindex][Ch2_hemg0] += (x2 >= histogram_splits[0] && x2 < histogram_splits[1]);
    buffer[bufferindex][Ch3_hemg0] += (x3 >= histogram_splits[0] && x3 < histogram_splits[1]);

    buffer[bufferindex][Ch0_hemg1] += (x0 >= histogram_splits[1] && x0 < histogram_splits[2]);
    buffer[bufferindex][Ch1_hemg1] += (x1 >= histogram_splits[1] && x1 < histogram_splits[2]);
    buffer[bufferindex][Ch2_hemg1] += (x2 >= histogram_splits[1] && x2 < histogram_splits[2]);
    buffer[bufferindex][Ch3_hemg1] += (x3 >= histogram_splits[1] && x3 < histogram_splits[2]);
    la[0] = x0;
    la[1] = x1;
    la[2] = x2;
    la[3] = x3;
    it++;
    if(it == windowSize){
        buffer[bufferindex][Ch0_avg] /= windowSize;
        buffer[bufferindex][Ch1_avg] /= windowSize;
        buffer[bufferindex][Ch2_avg] /= windowSize;
        buffer[bufferindex][Ch3_avg] /= windowSize;

        buffer[bufferindex][Ch0_var] = buffer[bufferindex][Ch0_sqr]/(windowSize-1);
        buffer[bufferindex][Ch1_var] = buffer[bufferindex][Ch1_sqr]/(windowSize-1);
        buffer[bufferindex][Ch2_var] = buffer[bufferindex][Ch2_sqr]/(windowSize-1);
        buffer[bufferindex][Ch3_var] = buffer[bufferindex][Ch3_sqr]/(windowSize-1);

        buffer[bufferindex][Ch0_rms] = sqrt(buffer[bufferindex][Ch0_sqr]/windowSize);
        buffer[bufferindex][Ch1_rms] = sqrt(buffer[bufferindex][Ch1_sqr]/windowSize);
        buffer[bufferindex][Ch2_rms] = sqrt(buffer[bufferindex][Ch2_sqr]/windowSize);
        buffer[bufferindex][Ch3_rms] = sqrt(buffer[bufferindex][Ch3_sqr]/windowSize);
        
        buffer[bufferindex][Ch0_mav] = buffer[bufferindex][Ch0_abs]/windowSize;
        buffer[bufferindex][Ch1_mav] = buffer[bufferindex][Ch1_abs]/windowSize;
        buffer[bufferindex][Ch2_mav] = buffer[bufferindex][Ch2_abs]/windowSize;
        buffer[bufferindex][Ch3_mav] = buffer[bufferindex][Ch3_abs]/windowSize;

        for (int i=0;i<num_features;i++)
            buffer[bufferindex][i] = (buffer[bufferindex][i]-input_mean[i])/input_std[i];
        it=0;
        for (int j = 0;j<num_features;j++)
            buffer[activeBuffer][j] = 0;
        activeBuffer++;
        if(activeBuffer>=num_buffers)
            activeBuffer=0;
        return true;
    }
    return false;
}
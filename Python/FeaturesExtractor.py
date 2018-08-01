import bz2
import pickle
import numpy as np
import pandas as pd
import os
from Questions import Question

import pylab as plt

def zc(x,t):
    return np.nonzero(np.diff(x>t))[0].size

class FeaturesExtractor:
    def __init__(self,datafiles,num_channels=4,windowSize=150,strides=50,zc_threshoed=[0],histogram_splits=np.arctanh(np.linspace(np.tanh(-2.5),np.tanh(2.5),3))):
        self.windowSize = windowSize
        self.dataFiles = datafiles
        self.strides = strides
        self.num_channels = num_channels
        self.features = {
            "min":np.min,
            "max":np.max,
            "avg":np.mean,
            "energy":lambda x: np.sum(x*x),
            "iemg":lambda x: np.sum(np.abs(x)),
            "mav":lambda x: np.mean(np.abs(x)),
            "var":lambda x: np.sum(x*x)/(x.size-1),
            "rms":lambda x: np.sqrt(np.mean(x*x)),
            "wl":lambda x: np.sum(np.diff(x))}
        histogram_splits = [-1e9]+histogram_splits+[1e9]
        self.features.update(dict([("zc"+str(i),lambda x: zc(x,i)) for i in zc_threshoed]))
        self.features.update(dict([("hemg"+str(i),lambda x: np.nonzero((x>=histogram_splits[i]) & (x<histogram_splits[i+1]))[0].size) for i in range(len(histogram_splits)-1)]))
        featuresXchannels = [(f,i) for f in self.features.keys() for i in range(num_channels)]
        self.index2channel = dict(zip(range(len(featuresXchannels)),[x[1] for x in featuresXchannels]))
        self.index2features = dict(zip(range(len(featuresXchannels)),[x[0] for x in featuresXchannels]))
        self.idx = 0

    def saveProcessedDataCSV(self,filename):
        df = pd.DataFrame()
        features = np.array([s[0] for s in self.samples])
        labels = [s[1] for s in self.samples]
        print(features.shape)
        #df["label"] =labels
        num_labels = max([len(l) for l in labels])
        for i in range(num_labels):
            df["label_" + str(i)] = [l[i] for l in labels]
        print(features.shape)
        for i in range(len(self.features)*self.num_channels):
            df["Ch{0}_{1}".format(self.index2channel[i], self.index2features[i])] = features[:,i]
        df.to_csv(filename,index=False)

    def saveProcessedData(self,filename):
        with bz2.BZ2File(filename,'w') as f:
            pickle.dump(self.data,f)

    def loadProcessedData(self,filename):
        with bz2.BZ2File(filename,'r') as f:
            self.data = pickle.load(filename)

    def loadData(self):
        self.data = []
        o1 = {"UP":-1,"Steady":0,"Down":1}
        o2 = {"Grape":-1,"Realease":0,"Extend":1}
        for fn in self.dataFiles:
            with bz2.BZ2File(fn,'r') as f:
                questions = pickle.load(f)
                samples = [(np.array(q.data),(o1[q.label[0]],o2[q.label[1]])) for q in questions]
                self.data.extend(samples)
    
    def processData(self):
        self.samples = []
        for questionSamples,label in self.data:
            self.samples.extend([(self.processSample(sample,label),label) for sample in self.splitData(questionSamples)])

    def splitData(self,sample):
        samples = []
        signal = sample
        for i in range(0,len(signal),self.strides):
            window = signal[i:i+self.windowSize,:]
            #NEED Windowing
            if(window.shape[0] < self.windowSize):
                continue
            samples.append(window)
        samples=np.array(samples)
        return samples
    
    def processSample(self,sample,label):
        self.idx +=1
        result = np.array([
            self.features[self.index2features[i]](sample[:,self.index2channel[i]]) 
                            for i in range(self.num_channels*len(self.features))
        ])
        return result

files = ['data/test_data4.bz2']
fe = FeaturesExtractor(files)
fe.loadData()
fe.processData()
fe.saveProcessedDataCSV('data.csv')
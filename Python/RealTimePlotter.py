import serial
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
import time
from threading import Thread,Event,Lock


class RealTimePlotter:
    def __init__(self,fs,channels=4):
        self.fs = fs
        self.channels = channels
        plt.ion()
        plt.style.use('fivethirtyeight')
        matplotlib.rcParams['lines.linewidth'] = 1
        self.fig, axis = plt.subplots(ncols=2,nrows=self.channels)
        self.time_axis = [axis[i][0] for i in range(channels)]
        self.freq_axis = [axis[i][1] for i in range(channels)]
        self.fig.suptitle('Real-time updated data', fontsize='12', fontweight='bold')
        self.fig.subplots_adjust(hspace=0.3)
        self.time_line = [None]*channels
        self.freq_line = [None]*channels
        
        for i in range(channels):
            self.time_axis[i].set_title('Channel {0} Signal'.format(i), fontsize='11', fontweight='bold')
            self.time_axis[i].set_ylabel('Amplitude(V)', fontsize='9', fontstyle='italic')
            self.freq_axis[i].set_title('Channel {0} Spectrum'.format(i), fontsize='11', fontweight='bold')
            self.freq_axis[i].set_ylabel('Amplitude(dB)', fontsize='9', fontstyle='italic')
        self.freq_axis[channels-1].set_xlabel('F(Hz)', fontsize='9', fontstyle='italic')
        self.time_axis[channels-1].set_xlabel('T(sec)', fontsize='9', fontstyle='italic')
        
    def show(self):
        try:
            y = [-2.8,2.8]
            for i in range(self.channels):
                self.time_line[i], = self.time_axis[i].plot(y, y)
                self.freq_line[i], = self.freq_axis[i].plot(y, y)
            self.fig.canvas.draw()
            self.fig.show()
            plt.show(block=False)
        except KeyboardInterrupt:
            self.fig.close('all')
    
    def plot(self,buffer):
        try:
            for i in range(self.channels):
                signal = buffer[:,i].reshape((buffer[:,i].shape[0]))
                fft = 20*np.log10(np.abs(np.fft.rfft(signal,n=signal.shape[0]))+1e-8)
                ts = 1/self.fs
                t = np.linspace(0,ts,signal.shape[0])
                f = np.linspace(0,self.fs/2,fft.shape[0])
                #self.time_axis.clear()
                #self.freq_axis.clear()
                self.time_line[i].set_xdata(t)
                self.time_line[i].set_ydata(signal)
                
                self.freq_line[i].set_xdata(f)
                self.freq_line[i].set_ydata(fft)

                self.time_axis[i].relim() 
                self.time_axis[i].autoscale_view(True,True,False) 
                self.freq_axis[i].relim() 
                self.freq_axis[i].autoscale_view(True,True,True) 
                #self.time_axis.plot(t,buffer)
                #self.freq_axis.plot(f,fft)
            self.fig.canvas.draw()
            plt.pause(0.001)
        except Exception as e:
            print(e)
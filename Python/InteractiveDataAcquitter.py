
from RealTimePlotter import RealTimePlotter
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from SerialBuffer import SerialBuffer
import bz2
import pickle
from textwrap import wrap
from Questions import Question
import numpy as np

class InteractiveDataAcquitter:
    def __init__(self,fs,buffer_size,filename,questions = [],port ="COM3"):
        self.serialBuffer = SerialBuffer(port,buffer_size)
        self.serialBuffer.callbacks.append(self.callback)
        self.filename = filename
        self.questions = questions
        self.current_question = 0
        self.running = False
        self.finished = False
        self.plotter = RealTimePlotter(fs)
        self.plotter.fig.suptitle('Interactive Data Acquitter', fontsize='12', fontweight='bold')  
        self.plotter.fig.subplots_adjust(left=0.27)
        questions_axes = plt.axes([0, 0.9, 0.2, 0.8])
        questions_axes.get_xaxis().set_visible(False)
        questions_axes.get_yaxis().set_visible(False)
        self.next_axes = plt.axes([0, 0.05, 0.2, 0.10])
        if(len(self.questions) == 0):
            self.questions_text = questions_axes.text(0,0,"No question provided",ha='left', fontsize=11, wrap=True)
        else:
            qtext = '\n'.join(wrap(self.questions[0].text, 40))
            self.questions_text = questions_axes.text(0,0,qtext,ha='left', fontsize=11, wrap=True)
        self.btn_next = Button(self.next_axes, 'Continue')
        self.btn_next.on_clicked(self.next)
        for q in self.questions:
            q.currentSample = 0

    def start(self):
        self.serialBuffer.start()
        self.plotter.show()
        self.serialBuffer.loop()

    def next(self,event):
        if(not self.finished and not self.running):
            self.running = True
            qtext = '\n'.join(wrap(self.questions[self.current_question].text + ". Collecting data ...", 40))
            self.questions_text.set_text(qtext)
        if(self.finished and not self.running):
            self.serialBuffer.stop()
            plt.close()

    def callback(self,buffer):
        self.plotter.plot(buffer)
        if(self.running):
            q = self.questions[self.current_question]
            if q.data is None:
                q.data = buffer
            else:
                q.data = np.vstack((q.data,buffer))
            q.currentSample +=1
            if(q.currentSample >= q.numSamples):
                self.running = False
                self.current_question +=1
                if(self.current_question >= len(self.questions)):
                    self.current_question = 0
                    qtext = '\n'.join(wrap("Test Finished! Data will be saved to {0}. Press continue to exit!".format(self.filename), 40))
                    self.questions_text.set_text(qtext)
                    self.finished = True
                    self.save_data()
                    
                else:
                    qtext = '\n'.join(wrap(self.questions[self.current_question].text, 40))
                    self.questions_text.set_text(qtext)

    def save_data(self):
        with bz2.BZ2File(self.filename,'w') as f:
            pickle.dump(self.questions,f)


if __name__ == "__main__":
    o1 = ["UP","Steady","Down"]
    o1=["x","y"]
    o2=["a"]
    #o2 = ["Grape","Realease","Extend"]
    q = [Question(x + " " + y,[x,y],5) for x in o1 for y in o2]
    ida = InteractiveDataAcquitter(1000,500,"data/test_data10.bz2",q)
    ida.start()
import numpy as np
import keras
from keras.models import Sequential,Model
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D,Input
from keras.utils import to_categorical
from keras.callbacks import History
from MultiOutputModelCheckpoint import MultiOutputModelCheckpoint
import pandas as pd
from keras import regularizers
from sklearn.model_selection import train_test_split
import matplotlib
import matplotlib.pyplot as plt


class DNNModel:
    def __init__(self,mode_name,input_shape=None,l2_regularizer_param = 0.001):
        self.input_shape = input_shape
        self.num_classes = [3,3]
        self.kernel_regularizer=regularizers.l2(l2_regularizer_param)
        self.mode_name = mode_name
        self.std = None
        self.mean = None

    def createModel(self):
        i = Input(shape=self.input_shape)
        x = Dense(35,activation='sigmoid',kernel_regularizer=self.kernel_regularizer,name='hidden')(i)
        o0 = Dense(self.num_classes[0],activation='softmax',name='output1',kernel_regularizer=self.kernel_regularizer)(x)
        o1 = Dense(self.num_classes[1],activation='softmax',name='output2',kernel_regularizer=self.kernel_regularizer)(x)
        self.model = Model(inputs=[i],outputs=[o0,o1])
        self.model.compile(loss=keras.losses.categorical_crossentropy,
                            optimizer=keras.optimizers.Adam(),
                            metrics=['accuracy'])
        self.model.summary()

    def loadData(self,filename):
        df = pd.read_csv(filename)
        x_df = df.loc[:, (df.columns != 'label_1') & (df.columns != 'label_0')]
        x_train = x_df.as_matrix()
        self.mean = np.mean(x_train,axis=0)
        x_train -= self.mean
        self.std = np.std(x_train,axis=0)
        x_train /=self.std

        if(self.input_shape is None):
            self.input_shape = [x_train.shape[1]]
        y0_train = df[["label_0"]].as_matrix()
        y1_train = df[["label_1"]].as_matrix()
        random_state  = 58
        self.x_train, self.x_test, self.y0_train, self.y0_test,self.y1_train, self.y1_test = train_test_split(x_train, y0_train,y1_train, test_size=0.20,random_state =random_state)
   
    def loadModel(self):
        self.createModel()
        self.model.load_weights('{0}.h5'.format(self.mode_name))
    
    def toCPPText(self,mat):
        if(np.isscalar(mat)):
            return str(mat)
        text = "{"+",".join([self.toCPPText(x) for x in mat])+"}"
        return text

    def saveCPPConstantParameters(self,filename):
        h_params = self.model.get_layer('hidden').get_weights()
        h_mat = np.vstack((h_params[1],h_params[0])).T
        h_values_text = self.toCPPText(h_mat)

        o1_params = self.model.get_layer('output1').get_weights()
        o1_mat = np.vstack((o1_params[1],o1_params[0])).T
        o1_values_text = self.toCPPText(o1_mat)

        o2_params = self.model.get_layer('output2').get_weights()
        o2_mat = np.vstack((o2_params[1],o2_params[0])).T
        o2_values_text = self.toCPPText(o2_mat)

        std_text = self.toCPPText(self.std)
        mean_text = self.toCPPText(self.mean)

        num_features = h_params[0].shape[0]
        num_hidden = h_mat.shape[0]
        num_output1 = o1_mat.shape[0]
        num_output2 = o2_mat.shape[0]

        cpp_float_type = "float"

        cpp_code = ""
        cpp_code += "const {0} h_mat[{1}][{2}] PROGMEM  {3};\n".format(cpp_float_type,h_mat.shape[0],h_mat.shape[1],h_values_text)
        cpp_code += "const {0} o1_mat[{1}][{2}] PROGMEM = {3};\n".format(cpp_float_type,o1_mat.shape[0],o1_mat.shape[1],o1_values_text)
        cpp_code += "const {0} o2_mat[{1}][{2}] PROGMEM = {3};\n".format(cpp_float_type,o2_mat.shape[0],o2_mat.shape[1],o2_values_text)
        cpp_code += "const {0} input_std[{1}] = {2};\n".format(cpp_float_type,self.std.shape[0],std_text)
        cpp_code += "const {0} input_mean[{1}] = {2};\n".format(cpp_float_type,self.mean.shape[0],mean_text)
        
        cpp_code += "const int num_features = {0};\n".format(num_features)
        cpp_code += "const int num_hidden = {0};\n".format(num_hidden)
        cpp_code += "const int num_output1 = {0};\n".format(num_output1)
        cpp_code += "const int num_output2 = {0};\n".format(num_output2)
        
        with open(filename, "w") as cpp_file:
            cpp_file.write(cpp_code)


    def loadBestModel(self):
        self.createModel()
        self.model.load_weights('best_{0}.h5'.format(self.mode_name))
    
    def saveModel(self):
        self.model.save_weights('{0}.h5'.format(self.mode_name))
        
    def train(self, epochs = 5000,batch_size = 500,verbose = 1,callables=[]):
        y0_train = to_categorical(self.y0_train,num_classes=3)
        y0_test = to_categorical(self.y0_test,num_classes=3)
        y1_train = to_categorical(self.y1_train,num_classes=3)
        y1_test = to_categorical(self.y1_test,num_classes=3)
        self.history = History()
        self.best_model = MultiOutputModelCheckpoint('best_{0}.h5'.format(self.mode_name)
                            ,save_best_only=True,monitor=['val_output1_acc','val_output2_acc'],
                            combine_func=lambda x: len(x)/np.sum(1/np.array(x))+np.mean(np.array(x))*0.6,period=10,mode='max')
        
        callables.extend([self.best_model,self.history])
        self.model.fit(self.x_train, [y0_train,y1_train],
                batch_size=batch_size, epochs=epochs,
                validation_data=(self.x_test, [y0_test,y1_test]),
                callbacks=callables)

    def evaluate(self,verbose=1):
        y0_test = to_categorical(self.y0_test,num_classes=3)
        y1_test = to_categorical(self.y1_test,num_classes=3)
        score = self.model.evaluate(self.x_test, (y0_test,y1_test), verbose=verbose)
        if(verbose ==1):
            print('Test loss:', score[0])
            print('Test accuracy:', score[1])
        return score

    def plotHistory(self,to_file=False):
        history = self.history.history
        f, (ax1, ax2) = plt.subplots(2, 1)
        t = np.arange(len(history['loss']))
        ax1.plot(t, history['output1_loss'],'#FF9303',label='Training1 loss')
        ax1.plot(t, history['output2_loss'],'#FFC903',label='Training2 loss')
        ax1.plot(t,history['val_output1_loss'],'#FF1003',label='Validation1 loss')
        ax1.plot(t,history['val_output2_loss'],'#E00298',label='Validation2 loss')
        ax1.axvline(x=self.best_model.best_epoch,c='#03E0FF',label='Best Model',ls='-')
        ax1.set_xticks(list(ax1.get_xticks()) + [self.best_model.best_epoch])
        ax1.set_ylabel('loss')
        ax1.set_xlabel('epoch')
        ax1.legend()
        ax2.plot(t,history['output1_acc'],'#B407D2',label='Training1 accuracy')
        ax2.plot(t,history['output2_acc'],'#6614D4',label='Training2 accuracy')
        ax2.plot(t,history['val_output1_acc'],'#02DF33',label='Validation1 accuracy')
        ax2.plot(t,history['val_output2_acc'],'#02CBC3',label='Validation2 accuracy')
        ax2.axvline(x=self.best_model.best_epoch,c='#03E0FF',label='Best Model',ls='-')
        ax2.set_xticks(list(ax2.get_xticks()) + [self.best_model.best_epoch])
        ax2.set_ylabel('accuracy')
        ax2.set_xlabel('epoch')
        ax2.legend()
        if(to_file):
            f.savefig('{0}_history.png'.format(self.mode_name))
        plt.show(True)

def train():
    m = DNNModel('simpleDNN')
    m.loadData('data.csv')
    m.createModel()
    m.train(epochs=10000,batch_size=m.x_train.shape[0])
    m.saveModel()
    m.plotHistory(True)

def createCPP():
    m = DNNModel('simpleDNN')
    m.loadData('data.csv')
    m.loadBestModel()
    m.saveCPPConstantParameters('SimpleDNNModelParameters.cpp')
train()
createCPP()


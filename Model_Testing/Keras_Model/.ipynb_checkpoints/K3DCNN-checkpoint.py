#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
from tensorflow.keras.models import load_model
import numpy as np


# In[2]:


class Model_3DCNN_K:
    
    def __init__(self):
        try:
            self.model = load_model('./model_K/basic_model-best-model-rlf.h5')
            self.predict = []
            self.debug = False
        except:
            print("files of model does not exist")
    
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.predict = []
        self.debug = False
    
    def setDebug(self, flag):
        self.debug = flag
    
    def predict_action(self, data):
        """data shape:(1, 16, 112, 112, 3)"""
        
        x = data.astype('float32')
        label = -1
#         if data != None:
        if data.shape[0] !=16 :
            st = time.time()
            self.predict = self.model.predict(x)[0]

            label = np.argmax(self.predict)
            et = time.time()
            tt = et-st
            if self.debug:
                print(label)
                print(self.predict)
                print(tt)
#         return label
        return self.predict
    
    def __del__(self):
        print('Finish')
#         self.session.close()


# In[ ]:





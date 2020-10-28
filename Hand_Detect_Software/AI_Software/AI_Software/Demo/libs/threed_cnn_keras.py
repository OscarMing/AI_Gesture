#!/usr/bin/env python
# coding: utf-8

import numpy as np
import os
from tensorflow.keras.models import load_model
import time

from libs.utils import local_path

class Model_3DCNN_K:
    
    def __init__(self, threshold=0.88):
        print("Model_3DCNN_K -  __init__(self, h5_path, threshold=0.88)")
        try:
            root_path = os.path.abspath(os.getcwd())
            self.h5_path = os.path.join(root_path, "models", "3dcnn", "keras_model", "basic_model-best-model-2020-10-11_16-41-12.h5")
            self.model = load_model(local_path(root_path, self.h5_path))
            self.threshold = threshold
            self.predict = []
            self.debug = False
        except:
            print("Model_3DCNN_K - files of model does not exist")
    
    def setDebug(self, flag):
        self.debug = flag
    
    def predict_action(self, data):
        """data shape:(1, 16, 112, 112, 3)"""
        
        x = data.astype('float32')
        label = -1
        if x.shape[0] !=16 :
            st = time.time()
            
            self.predict = self.model.predict(x)

            if np.max(self.predict[0]) >= self.threshold:
                label = np.argmax(self.predict[0])
            
            et = time.time()
            tt = et-st
            if self.debug:
                print("Model_3DCNN_K - label =", label)
                print("Model_3DCNN_K - self.predict[0] =", self.predict[0])
                print("Model_3DCNN_K - tt =", tt)
        return label
    
    def __del__(self):
        print("Model_3DCNN_K - __del__")
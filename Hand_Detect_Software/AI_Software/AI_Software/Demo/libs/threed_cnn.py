#!/usr/bin/env python
# coding: utf-8

import numpy as np
import os
import tensorflow as tf
import time

from libs.utils import local_path

class Model_3DCNN:
    # disable_eager_execution for tf v1 syntax run on tf v2 wev
#     tf.compat.v1.disable_eager_execution()
    def __init__(self, threshold=0.5, debug_flag=False):
        raise "Model_3DCNN is not supported"
#         print("Model_3DCNN - __init__(self, threshold=0.5, debug_flag=False)")
#         try:
#             root_path = os.path.abspath(os.getcwd())
#             self.meta_path = os.path.join(root_path, "models", "3dcnn", "3DCNN_Model-29.meta")
#             self.ckp_path = os.path.join(root_path, "models", "3dcnn") + "\\"
#             self.session = tf.compat.v1.Session()
#             self.saver = tf.compat.v1.train.import_meta_graph(local_path(root_path, self.meta_path))
#             self.saver.restore(self.session, tf.compat.v1.train.latest_checkpoint(local_path(root_path, self.ckp_path)))
#             self.predict = tf.compat.v1.get_collection("predict")
#             self.debug = debug_flag
#             self.threshold = threshold
#         except:
#             print("Model_3DCNN - files of model does not exist")
    
#     def setDebug(self, flag):
#         self.debug = flag
    
#     def predict_action(self, data):
#         """data shape:(1, 16, 112, 112, 3)"""
        
#         label = -1
#         if data is not None:
#             st = time.time()
#             pred = self.session.run(self.predict, feed_dict={"input_x:0": data,"training:0": False})
# #             print(pred[0])
# #             label = self.session.run(tf.argmax(pred[0], 1))[0]
#             if np.max(pred[0], axis=1) >= self.threshold:
#                 label = np.argmax(pred[0], axis=1)
#             et = time.time()
#             tt = et-st
#             if self.debug:
#                 print(label[0])
#                 print(tt)
#                 print("Model_3DCNN_K - label =", label)
#                 print("Model_3DCNN_K - pred =", pred)
#                 print("Model_3DCNN_K - tt =", tt)
#         return label[0]
    
#     def __del__(self):
#         print("Model_3DCNN - __del__")
#         self.session.close()
#!/usr/bin/env python
# coding: utf-8

import cv2
import numpy as np
import os
import queue
from skimage.measure import compare_ssim
from threading import Thread
import time

from libs.threed_cnn import Model_3DCNN
from libs.threed_cnn_keras import Model_3DCNN_K
from libs.utils import local_path
from libs.utils import StateFlow
from libs.youtube_lib import Youtube_360_Degree

def construct_data(isPath=True, data_list=None, resize=None):
    imgs = None
    for data in data_list:
        if isPath:
            img = cv2.imread(data)
        else:
            img = data
        if resize is not None:
            img = cv2.resize(img, resize, interpolation=cv2.INTER_CUBIC)
        if imgs is None:
            imgs = img[np.newaxis, ...]
        else:
            imgs = np.append(imgs, img[np.newaxis, ...],  axis=0)
    imgs = imgs[np.newaxis, ...]
    return imgs

class Three_D_CNN_Thread(Thread, StateFlow):
    
    Source_Type = dict({"File": 0, "Queue":1})
    Gesture_name = dict({3: "Hand Up", 2: "Hand Down", 0: "Hand Left", 1: "Hand Right", 4:"Turning Hand Clockwise", 5:"Turning Hand Counterclockwise"})
    
    def __init__(self, data_path, data_queue, source_type="Queue", app_mode="Youtube_360_video", args=[], kwargs={}, daemon=True, enable_component=True):
        StateFlow.__init__(self)
        Thread.__init__(self, args=args, kwargs=kwargs, daemon=daemon)
        self.data_path = data_path
        self.data_queue = data_queue
        self.source_type = self.Source_Type[source_type]
        self.model = None
        self.youtube_360_video = None
        self.stop_by_inner = False
        self.enable_component = enable_component
        self.mode = app_mode
    
    # for origin model
    def start(self, youtube_360_video_url, youtube_auto_refresh):
        print("Three_D_CNN_Thread - start(self, meta_path, ckp_path, youtube_360_video_url) is called")
        if self.model is None:
            self.model = Model_3DCNN()
        Thread.start(self)
        if self.enable_component:
            if self.mode == "Youtube_360_video":
                self.start_component(youtube_360_video_url, youtube_auto_refresh)
        
        self.state = self.state_map["Started"]
    
    # for keras model
    def start(self, youtube_360_video_url, youtube_auto_refresh):
        print("Three_D_CNN_Thread - start(self, h5_path, youtube_360_video_url) is called")
        if self.model is None:
            self.model = Model_3DCNN_K()
        Thread.start(self)
        if self.enable_component:
            self.__start_component(youtube_360_video_url, youtube_auto_refresh)
        
        self.state = self.state_map["Started"]
    
    def stop(self):
        self.state = self.state_map["Stopping"]
        if self.enable_component:
            self.__stop_component()
    
    def __start_component(self, youtube_360_video_url, youtube_auto_refresh):
        if self.mode == "Youtube_360_video":
            if self.youtube_360_video is None:
                self.youtube_360_video = Youtube_360_Degree(youtube_360_video_url, youtube_auto_refresh)
                self.youtube_360_video.bind_to("Three_D_CNN_Thread", self.component_status_changed)
                self.youtube_360_video.start()
    
    def __stop_component(self):
        if self.mode == "Youtube_360_video":
            if self.youtube_360_video is not None:
                self.youtube_360_video.stop()
    
    def run(self):
        count = -1
        predict_flag = False
        current_index = -1
        start_index = -1
        end_index = -1
        data = []
        predict_count = 0
        frame_list = [] # for "Queue" type
        frame_count = -1 # for "Queue" type
        current_score = -1 # for "Queue" type
        while not (self.state == self.state_map["Stopping"]):
            if (self.data_queue.empty()):
                continue
            
            check_file = True
            predict_files = []
            if self.source_type == self.Source_Type["Queue"]:
                frame_count += 1
                frame_dict = self.data_queue.get()
                frame = None
                score = -1
                for key, value in frame_dict.items():
                    frame_list.append(value)
                    score  = key
                del frame_dict
                if frame_count < 8:
                    continue
                if frame_count <= end_index:
                    continue
                if not predict_flag:
                    if 0.18 < score and score < 0.85:
                        current_score = score
#                         print("3DCNN - start_index = ", start_index, " frame_count = ", frame_count, " end_index = ", end_index)
                        if start_index != -1 and end_index != -1:
                            if (start_index < frame_count) and (frame_count <= end_index):
                                continue
                            elif (frame_count - end_index) <= 19:
                                continue
                        predict_flag = True
                        current_index = frame_count
                        start_index = current_index - 5
                        end_index = current_index + 11
                    continue
                else:
                    for i in range(start_index, end_index):
                        if i > frame_count-1:
                            check_file = False
                            break
                        else:
                            predict_files.append(frame_list[i])
                    if check_file:
                        if len(predict_files) == 16:
                            data = construct_data(isPath=False, data_list=predict_files)
                            predict_flag = False
            else:
                count = self.data_queue.get()
                if count == -1:
                    continue
                if int(count) < 9:
                    continue
                for i in range(int(count)-8, int(count)+8):
                    img_path = os.path.join(self.data_path, str(i)+".jpg")
                    if not os.path.exists(img_path):
                        check_file = False
                    else:
                        predict_files.append(img_path)
                if check_file:
                    data = construct_data(data_list=predict_files)
            
            # model predict
            if not check_file:
                del predict_files
            else:
                label = self.model.predict_action(data)
                predict_count += 1
#                 self.save_continue_frame(predict_files, predict_count) # test 16 frame to folder
                del predict_files
#                 print("Three_D_CNN_Thread - predict: "+str(label), " current_score = ", current_score, " predict_count = ", predict_count)
                if self.enable_component:
                    if self.mode == "Youtube_360_video":
                        if self.youtube_360_video is not None:
                            if label != -1:                            
#                                 print("Three_D_CNN_Thread - predict: ", self.Gesture_name[label], " current_score = ", current_score, " predict_count = ", predict_count)
                                self.youtube_360_video.send_command(label)
                
        del self.model
        self.state = self.state_map["Stopped"]
    
    # predict 16 frame to folder
    def save_continue_frame(self, frames, index):
        # data: rgb
        root_path = os.path.abspath(os.getcwd())
        predict_path = os.path.join(root_path, "images", "predict", str(index))
        if not os.path.exists(predict_path):
            os.makedirs(predict_path)
        count = 0
        for frame in frames:
            img_path = os.path.join(predict_path, str(count)+".jpg")
            img_path = local_path(root_path, img_path)
            cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            count += 1
    
    def component_status_changed(self, old_state, new_state):
        print("Three_D_CNN_Thread - component_status_changed is called - old_state: %d, new_state: %d"%(old_state, new_state))
        if self.mode == "Youtube_360_video":
            if new_state == self.youtube_360_video.state_map["Stopped"]: 
                flag = self.youtube_360_video.stop_by_inner
                if flag:
                    self.stop_by_inner = True
                    self.youtube_360_video = None
                    self.stop()
    
    def __del__(self):
        print("Three_D_CNN_Thread - __del__")
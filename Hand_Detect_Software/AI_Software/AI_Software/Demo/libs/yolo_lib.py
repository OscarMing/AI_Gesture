#!/usr/bin/env python
# coding: utf-8

import cv2
import numpy as np
import os
import queue
from threading import Thread
import time

from libs.utils import local_path
from libs.utils import StateFlow
from libs.yolo import YOLO

def is_yolo_detect_hand(frame, yolo, size=416, confidence=0.25, resize=(256, 256)):
    yolo.size = int(size)
    yolo.confidence = float(confidence)
    conf_sum = 0
    detection_count = 0
    
    output = yolo.is_inference(frame)
    return output

def yolo_detect_hand(frame, yolo, size=416, confidence=0.25, resize=(256, 256)):
    yolo.size = int(size)
    yolo.confidence = float(confidence)
    conf_sum = 0
    detection_count = 0
    width, height, inference_time, results, cpu_percent, memory_percent = yolo.inference(frame)
#     print("%s in %s seconds: %s classes found!" %
#           (os.path.basename(path), round(inference_time, 2), len(results)))
    hand_img = None
#     print("len of result = "+str(len(results)))
#     if len(results) > 1:
#         return None, inference_time, cpu_percent, memory_percent
    for detection in results:
        _, name, confidence, x, y, w, h = detection
#         print("confidence = "+str(confidence))
        cx = x + (w / 2)
        cy = y + (h / 2)

        conf_sum += confidence
        detection_count += 1
        
        # checking boundary
        x_begin = x
        y_begin = y
        if x_begin < 0:
            x_begin = 0
        if y_begin < 0:
            y_begin = 0
        x_end = x + w
        y_end = y + h
        if x_end > width:
            x_end = width
        if y_end > height:
            y_end = height
#         print(x, y, width, height, x_begin, y_begin, x_end, y_end)
        hand_img = cv2.resize(frame[y_begin:y_end, x_begin:x_end, :], resize, interpolation=cv2.INTER_CUBIC)
    return hand_img, inference_time, cpu_percent, memory_percent

def yolo_multi_img_detect_hand(paths, yolo, size=416, confidence=0.25, resize=(256, 256)):
#     files = []
    files_name = []
    files_ext = []
    mats = None
    
    root_path = os.path.abspath(os.getcwd())
    for path in paths:
        root, file = os.path.split(path)
        files_name.append(file.split(".")[0])
        files_ext.append("." + file.split(".")[1])
        img_path = local_path(root_path, path)
        mat = cv2.imread(img_path)
        if mats is None:
            mats = mat[np.newaxis, ...]
        else:
            mats = np.append(mats, mat[np.newaxis, ...],  axis=0)
#     print("mats.shape:", mats.shape)
    yolo.size = int(size)
    yolo.confidence = float(confidence)
    
    conf_sum = 0
    detection_count = 0
#     print(mat.shape)
    output = yolo.is_inference_many(mats)
    indexs = []
    for i in output:
        indexs.append(files_name[i])
    return indexs

def test_yolo_img_detect_hand(path, yolo, size=416, confidence=0.25, to_path="./", sep_img=False, resize=(256, 256)):
    root, file = os.path.split(path)
    file_name = file.split(".")[0]
    file_ext = "." + file.split(".")[1]
    yolo.size = int(size)
    yolo.confidence = float(confidence)
    
    conf_sum = 0
    detection_count = 0
    root_path = os.path.abspath(os.getcwd())
    img_path = local_path(root_path, path)
    mat = cv2.imread(path)
#     print(mat.shape)
    width, height, inference_time, results, cpu_percent, memory_percent = yolo.inference(mat)

#     print("%s in %s seconds: %s classes found!" %
#           (os.path.basename(path), round(inference_time, 2), len(results)))
    
    output = []
    for detection in results:
        _, name, confidence, x, y, w, h = detection

        conf_sum += confidence
        detection_count += 1
        
        # checking boundary
        x_begin = x
        y_begin = y
        if x_begin < 0:
            x_begin = 0
        if y_begin < 0:
            y_begin = 0
        x_end = x + w
        y_end = y + h
        if x_end > width:
            x_end = width
        if y_end > height:
            y_end = height

        # draw a bounding box rectangle and label on the image
        if not sep_img:
            color = (255, 0, 255)
#             cv2.rectangle(mat, (x, y), (x + w, y + h), color, 1)
            cv2.rectangle(mat, (x_begin, y_begin), (x_end, y_end), color, 1)
            text = "%s (%s)" % (name, round(confidence, 2))
#             cv2.putText(mat, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.25, color, 1)
            cv2.putText(mat, text, (x_begin, y_begin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.25, color, 1)
        else:
            output = cv2.resize(mat[y_begin:y_end, x_begin:x_end, :], resize, interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(to_path+file_name+"_yolo_"+str(detection_count)+file_ext, cv2.cvtColor(output, cv2.COLOR_RGB2BGR))

#         print("%s with %s confidence" % (name, round(confidence, 2)))
    if not sep_img:
        cv2.imwrite(to_path+file_name+"_yolo"+file_ext, cv2.cvtColor(mat, cv2.COLOR_RGB2BGR))
    else:
        if len(results) == 0:
            cv2.imwrite(to_path+file_name+"_yolo"+file_ext, cv2.cvtColor(mat, cv2.COLOR_RGB2BGR))

def test_yolo_multi_img_detect_hand(paths, yolo, size=416, confidence=0.25, to_path="./", sep_img=False, resize=(256, 256)):
    files_name = []
    files_ext = []
    mats = None
    root_path = os.path.abspath(os.getcwd())
    for path in paths:
        root, file = os.path.split(path)
        files_name.append(file.split(".")[0])
        files_ext.append("." + file.split(".")[1])
        img_path = local_path(root_path, path)
        mat = cv2.imread(img_path)
        if mats is None:
            mats = mat[np.newaxis, ...]
        else:
            mats = np.append(mats, mat[np.newaxis, ...],  axis=0)
    yolo.size = int(size)
    yolo.confidence = float(confidence)
    
    conf_sum = 0
    detection_count = 0
    output = yolo.inference_many(mats)
    
    for key, value in output.items():
        width, height, inference_time, results, cpu_percent, memory_percent = value
        output = []
        for detection in results:
            _, name, confidence, x, y, w, h = detection
            
            conf_sum += confidence
            detection_count += 1
            
            # checking boundary
            x_begin = x
            y_begin = y
            if x_begin < 0:
                x_begin = 0
            if y_begin < 0:
                y_begin = 0
            x_end = x + w
            y_end = y + h
            if x_end > width:
                x_end = width
            if y_end > height:
                y_end = height
            
            if not sep_img:
                # draw a bounding box rectangle and label on the image
                color = (255, 0, 255)
                cv2.rectangle(mats[key,...], (x_begin, y_begin), (x_end, y_end), color, 1)
                text = "%s (%s)" % (name, round(confidence, 2))
                cv2.putText(mats[key,...], text, (x_begin, y_begin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.25, color, 1)
            else:
                output = cv2.resize(mats[key, y_begin:y_end, x_begin:x_end, :], resize, interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(to_path+files_name[key]+"_yolo_"+str(detection_count)+files_ext[key], output)
        if not sep_img:
            cv2.imwrite(to_path+files_name[key]+"_yolo"+files_ext[key], cv2.cvtColor(mats[key,...], cv2.COLOR_RGB2BGR))
        else:
            if len(results) == 0:
                cv2.imwrite(to_path+files_name[key]+"_yolo"+files_ext[key], cv2.cvtColor(mats[key,...], cv2.COLOR_RGB2BGR))

class Yolo_Detect_Thread(Thread, StateFlow):
    
    Source_Type = dict({"File": 0, "Queue":1})
    
    def __init__(self, data_path, data_queue,source_type="Queue", args=[], kwargs={}, daemon=True):
        StateFlow.__init__(self)
        Thread.__init__(self, args=args, kwargs=kwargs, daemon=daemon)
        self.data_path = data_path
        self.data_queue = data_queue
        self.model = None
        self.source_type = self.Source_Type[source_type]
    
    def start(self, acceleration=False):
        if self.model is None:
            self.model = YOLO(["hand"], acceleration=acceleration)
        if self.source_type == self.Source_Type["File"]:
            Thread.start(self)
        self.state = self.state_map["Started"]
    
    def stop(self):
        self.state = self.state_map["Stopping"]
    
    def run(self):
        index = 1
        total = 16
        count = 1
        while not (self.state == self.state_map["Stopping"]):
            if self.source_type == self.Source_Type["File"]:
                img_path = os.path.join(self.data_path, str(index)+".jpg")
                if os.path.exists(img_path):
                    index +=1
                if (count-1)*total < index and index < count*total+1:
                    continue
                image_paths = []
                for i in range(total):
                    img_path = os.path.join(self.data_path, str((count-1)*total+i+1)+".jpg")
                    image_paths.append(img_path)
                results = yolo_multi_img_detect_hand(image_paths, self.model, size=416, confidence=0.25, resize=(256, 256))
#                 print("Yolo - reuslts =", results)
                for j in results:
                    self.data_queue.put(j)
                count +=1
            else:
                time.sleep(0.5)
        del self.model
        self.state = self.state_map["Stopped"]
        
    def __del__(self):
        print("Yolo - __del__")
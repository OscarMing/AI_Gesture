#!/usr/bin/env python
# coding: utf-8

import cv2
import numpy as np
import os
import psutil
import time

from libs.utils import local_path

class YOLO:
    
    def __init__(self, labels, size=416, confidence=0.5, threshold=0.3, acceleration=False):
        root_path = os.path.abspath(os.getcwd())
        self.cfg_path = os.path.join(root_path, "models", "yolo", "cross-hands-tiny-prn.cfg")
        self.weight_path = os.path.join(root_path, "models", "yolo", "cross-hands-tiny-prn.weights")
        self.confidence = confidence
        self.threshold = threshold
        self.size = size

        self.labels = labels
        self.net = cv2.dnn.readNetFromDarknet(local_path(root_path, self.cfg_path), local_path(root_path, self.weight_path))
        
        # cuda
#         self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#         self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
#         #opencv
#         self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
#         self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL_FP16)
        if acceleration:
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL_FP16)
    
    def inference_from_file(self, file):
        mat = cv2.imread(file)
        return self.inference(mat)

    def inference(self, image):
        ih, iw = image.shape[:2]

        ln = self.net.getLayerNames()
        ln = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (self.size, self.size), swapRB=True, crop=False)
        self.net.setInput(blob)
        start = time.time()
        layerOutputs = self.net.forward(ln)
        end = time.time()
        inference_time = end - start
#         print("yolo spending time: ", inference_time)
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        boxes = []
        confidences = []
        classIDs = []
        results = []
        
        for output in layerOutputs:
            # loop over each of the detections
            for detection in output:
                # extract the class ID and confidence (i.e., probability) of
                # the current object detection
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > self.confidence:
#                     print("qoo = "+str(len(output)))
                    # scale the bounding box coordinates back relative to the
                    # size of the image, keeping in mind that YOLO actually
                    # returns the center (x, y)-coordinates of the bounding
                    # box followed by the boxes' width and height
                    box = detection[0:4] * np.array([iw, ih, iw, ih])
                    (centerX, centerY, width, height) = box.astype("int")
                    # use the center (x, y)-coordinates to derive the top and
                    # and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    # update our list of bounding box coordinates, confidences,
                    # and class IDs
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence, self.threshold)
          
        if len(idxs) > 0:
            for i in idxs.flatten():
                # extract the bounding box coordinates
                x, y = (boxes[i][0], boxes[i][1])
                w, h = (boxes[i][2], boxes[i][3])
                id = classIDs[i]
                confidence = confidences[i]

                results.append((id, self.labels[id], confidence, x, y, w, h))

        return iw, ih, inference_time, results, cpu_percent, memory_percent

    def inference_many(self, images):
        ih, iw = images.shape[1:3]

        ln = self.net.getLayerNames()
        ln = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        blob = cv2.dnn.blobFromImages(images, 1 / 255.0, (self.size, self.size), swapRB=True, crop=False)
        self.net.setInput(blob)
        start = time.time()
        layerOutputs = self.net.forward(ln)
        end = time.time()
        inference_time = end - start
#         print("yolo spending time: ", inference_time)
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        # to group
        layerOutputs_sep = dict()
        for i in range(images.shape[0]):
            layerOutputs_sep[i] = []
        move_index = 0
        for i in range(images.shape[0]):
            for output in layerOutputs:
                layerOutputs_sep[i].append(output[move_index])
            move_index += 1
        detect_output = dict()
        for key, value in layerOutputs_sep.items():
            boxes = []
            confidences = []
            classIDs = []
            for output in value:
                # loop over each of the detections
                for detection in output:
                    # extract the class ID and confidence (i.e., probability) of
                    # the current object detection
                    scores = detection[5:]
                    classID = np.argmax(scores)
                    confidence = scores[classID]
                    # filter out weak predictions by ensuring the detected
                    # probability is greater than the minimum probability
                    if confidence > self.confidence:
                        # scale the bounding box coordinates back relative to the
                        # size of the image, keeping in mind that YOLO actually
                        # returns the center (x, y)-coordinates of the bounding
                        # box followed by the boxes' width and height
                        box = detection[0:4] * np.array([iw, ih, iw, ih])
                        (centerX, centerY, width, height) = box.astype("int")
                        # use the center (x, y)-coordinates to derive the top and
                        # and left corner of the bounding box
                        x = int(centerX - (width / 2))
                        y = int(centerY - (height / 2))
                        # update our list of bounding box coordinates, confidences,
                        # and class IDs
                        boxes.append([x, y, int(width), int(height)])
                        confidences.append(float(confidence))
                        classIDs.append(classID)
                        
            idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence, self.threshold)
            
            results = []
            if len(idxs) > 0:
                for i in idxs.flatten():
                    # extract the bounding box coordinates
                    x, y = (boxes[i][0], boxes[i][1])
                    w, h = (boxes[i][2], boxes[i][3])
                    id = classIDs[i]
                    confidence = confidences[i]
                    results.append((id, self.labels[id], confidence, x, y, w, h))
            detect_output[key] = [iw, ih, inference_time, results, cpu_percent, memory_percent]
        return detect_output
    
    def is_inference(self, image):
        ih, iw = image.shape[:2]

        ln = self.net.getLayerNames()
        ln = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (self.size, self.size), swapRB=True, crop=False)
        self.net.setInput(blob)
#         start = time.time()
        layerOutputs = self.net.forward(ln)
#         end = time.time()
#         inference_time = end - start
# #         print("yolo spending time: ", inference_time)
#         cpu_percent = psutil.cpu_percent()
#         memory_percent = psutil.virtual_memory().percent
        
        boxes = []
        confidences = []
        classIDs = []
        results = []
        
        for output in layerOutputs:
            # loop over each of the detections
            for detection in output:
                # extract the class ID and confidence (i.e., probability) of
                # the current object detection
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > self.confidence:
#                     print("qoo = "+str(len(output)))
                    # scale the bounding box coordinates back relative to the
                    # size of the image, keeping in mind that YOLO actually
                    # returns the center (x, y)-coordinates of the bounding
                    # box followed by the boxes' width and height
                    box = detection[0:4] * np.array([iw, ih, iw, ih])
                    (centerX, centerY, width, height) = box.astype("int")
                    # use the center (x, y)-coordinates to derive the top and
                    # and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    # update our list of bounding box coordinates, confidences,
                    # and class IDs
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence, self.threshold)
        
        existed = False
        if len(idxs) > 0:
            for i in idxs.flatten():
                existed = True
                break

        return existed
    
    def is_inference_many(self, images):
        ih, iw = images.shape[1:3]

        ln = self.net.getLayerNames()
        ln = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        blob = cv2.dnn.blobFromImages(images, 1 / 255.0, (self.size, self.size), swapRB=True, crop=False)
        self.net.setInput(blob)
#         start = time.time()
        layerOutputs = self.net.forward(ln)
#         end = time.time()
#         inference_time = end - start
# #         print("yolo spending time: ", inference_time)
#         cpu_percent = psutil.cpu_percent()
#         memory_percent = psutil.virtual_memory().percent
        # to group
        layerOutputs_sep = dict()
        for i in range(images.shape[0]):
            layerOutputs_sep[i] = []
        move_index = 0
        for i in range(images.shape[0]):
            for output in layerOutputs:
                layerOutputs_sep[i].append(output[move_index])
            move_index += 1
        detect_output = dict()
        results = []
        for key, value in layerOutputs_sep.items():
            boxes = []
            confidences = []
            classIDs = []
            for output in value:
                # loop over each of the detections
                for detection in output:
                    # extract the class ID and confidence (i.e., probability) of
                    # the current object detection
                    scores = detection[5:]
                    classID = np.argmax(scores)
                    confidence = scores[classID]
                    # filter out weak predictions by ensuring the detected
                    # probability is greater than the minimum probability
                    if confidence > self.confidence:
                        # scale the bounding box coordinates back relative to the
                        # size of the image, keeping in mind that YOLO actually
                        # returns the center (x, y)-coordinates of the bounding
                        # box followed by the boxes' width and height
                        box = detection[0:4] * np.array([iw, ih, iw, ih])
                        (centerX, centerY, width, height) = box.astype("int")
                        # use the center (x, y)-coordinates to derive the top and
                        # and left corner of the bounding box
                        x = int(centerX - (width / 2))
                        y = int(centerY - (height / 2))
                        # update our list of bounding box coordinates, confidences,
                        # and class IDs
                        boxes.append([x, y, int(width), int(height)])
                        confidences.append(float(confidence))
                        classIDs.append(classID)
                        
            idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence, self.threshold)
            
            if len(idxs) > 0:
                results.append(key)
        return results
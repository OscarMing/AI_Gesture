#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2
import datetime
import keyboard
import numpy as np
import os
import queue
import shutil
import sys

# from skimage.measure import compare_ssim # remove for 0.18 version
from skimage.metrics import structural_similarity

from threading import Thread
import time


# In[2]:


from libs.threed_cnn_lib import Three_D_CNN_Thread
from libs.timer_lib import LoopTimer
from libs.utils import local_path
from libs.utils import StateFlow
from libs.yolo_lib import Yolo_Detect_Thread


# ## reset old folder

# In[3]:


def reset_data_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    if not os.path.exists(path):
        os.makedirs(path)


# ## init variables

# In[4]:


# control flow
demo_ready = False
demo_started = False
demo_stopped = False

cam_device = None
capture_thread = None
controller = None
data_source_type = "Queue" # type: Queue or File
# data_source_type = "File" # type: Queue or File

root_path = os.path.abspath(os.getcwd())

cam_data_path = os.path.join(root_path, "images", "cam")
predict_data_path = os.path.join(root_path, "images", "predict")

timer_interval = 3*60 # type: File

threed_cnn_model_type = "keras" # 3dcnn model
threed_cnn_mode = "Youtube_360_video"

youtube_360_video_url = r"https://www.youtube.com/watch?v=UaXjcIl-6q8"
youtube_auto_refresh = True


# ## construct controller for 3dcnn, yolo, removed timer, youtube

# In[5]:


class Controller(StateFlow):
    
    def __init__(self, cam_data_path, model_type="normal", threed_cnn_mode="Youtube_360_video", data_source_type="Queue", youtube_360_video_url=None, youtube_auto_refresh=False, timer_interval=60):
        StateFlow.__init__(self)
        self.model_type = model_type
        self.cam_data_path = cam_data_path
        self.threed_cnn_mode = threed_cnn_mode
        self.youtube_360_video_url = youtube_360_video_url
        self.youtube_auto_refresh = youtube_auto_refresh
        self.timer_interval = timer_interval
        self.data_source_type = data_source_type
        # init models
        self.yolo_detect_thread = None
        self.threed_cnn_thread = None
        self.remove_timer = None
        self.data_queue = queue.Queue(maxsize=0)
        self.current_time = datetime.datetime.now().timestamp()
    
    def init_components(self):
        self.init_threed_cnn_thread(self.cam_data_path, threed_cnn_mode, self.data_source_type)
        self.init_yolo_thread(self.cam_data_path, self.data_source_type)
        if (self.data_source_type == "File"):
            self.init_timer()
        self.state = self.state_map["Init"]
        
    def start_components(self):
        if self.model_type.lower() == "keras":
            self.start_threed_cnn_thread(self.youtube_360_video_url, self.youtube_auto_refresh)
        else:
            self.start_threed_cnn_thread(self.youtube_360_video_url, self.youtube_auto_refresh)
        self.start_yolo_thread()
        if (self.data_source_type == "File"):
            self.start_timer()
        self.state = self.state_map["Started"]
    
    def stop_components(self):
        self.state = self.state_map["Stopping"]
        if self.threed_cnn_thread is not None:
            self.stop_threed_cnn_thread()
        if self.yolo_detect_thread is not None:
            self.stop_yolo_thread()
        if self.remove_timer is not None:
            self.stop_timer()
        self.state = self.state_map["Stopped"]
    
    # 3dcnn model
    def init_threed_cnn_thread(self, data_path, mode, source_type="Queue"):
        if self.threed_cnn_thread is None:
            self.threed_cnn_thread = Three_D_CNN_Thread(data_path, self.data_queue, source_type=source_type, app_mode=mode)
        self.threed_cnn_thread.bind_to("Controller", self.threed_cnn_status_changed)
    
    # for origin model
    def start_threed_cnn_thread(self, youtube_360_video_url, youtube_auto_refresh):
        print("Controller - start_threed_cnn_thread(self, youtube_360_video_url, youtube_auto_refresh) is called")
        if self.threed_cnn_thread is not None:
            self.threed_cnn_thread.start(youtube_360_video_url, youtube_auto_refresh)
    
    # for keras model
    def start_threed_cnn_thread(self, youtube_360_video_url, youtube_auto_refresh):
        print("Controller - start_threed_cnn_thread(youtube_360_video_url, youtube_auto_refresh) is called")
        if self.threed_cnn_thread is not None:
            self.threed_cnn_thread.start(youtube_360_video_url, youtube_auto_refresh)
    
    def stop_threed_cnn_thread(self):
        if self.threed_cnn_thread is not None:
            self.threed_cnn_thread.stop()
    
    def threed_cnn_status_changed(self, old_state, new_state):
        print("Controller - threed_cnn_status_changed is called - old_state: %d, new_state: %d"%(old_state, new_state))
        if self.threed_cnn_thread.state == self.threed_cnn_thread.state_map['Stopped']:
            stop_by_inner = self.threed_cnn_thread.stop_by_inner
            if stop_by_inner:
                self.threed_cnn_thread = None
                self.stop_components()
    
    # yolo model
    def init_yolo_thread(self, data_path, source_type="Queue"):
        if self.yolo_detect_thread is None:
            self.yolo_detect_thread = Yolo_Detect_Thread(data_path, self.data_queue, source_type=source_type)
        self.yolo_detect_thread.bind_to("Controller", self.yolo_status_changed)
    
    def start_yolo_thread(self):
        if self.yolo_detect_thread is not None:
            self.yolo_detect_thread.start()
    
    def stop_yolo_thread(self):
        if self.yolo_detect_thread is not None:
            self.yolo_detect_thread.stop()
    
    def yolo_status_changed(self, old_state, new_state):
        print("Controller - yolo_status_changed is called - old_state: %d, new_state: %d"%(old_state, new_state))
        
    def init_timer(self):
        if self.remove_timer is None:
            self.remove_timer = LoopTimer(self.timer_interval, self.update_cam_folder)
    
    def start_timer(self):
        if self.remove_timer is not None:
            self.remove_timer.start()
    
    def stop_timer(self):
        if self.remove_timer is not None:
            self.remove_timer.cancel()
    
    def update_cam_folder(self):
        if self.state == self.state_map["Stopped"]:
            return
        
        self.current_time = datetime.datetime.now().timestamp()
        count = 0
        
        for roots, dirs, files in os.walk(self.cam_data_path):
            for each in files:
                if each.find('checkpoint') == -1:
                    if self.current_time - os.path.getctime(os.path.join(roots, each)) >= self.timer_interval:
                        count += 1
                        os.remove(os.path.join(roots, each))
    
        print("Controller - Timer-delete", str(count), " files")


# In[6]:


def start_capture_thread(cam_device, queue):
    global demo_started
    global demo_stopped
    global data_source_type
    
    # continuously read fames from the camera and control fps
    target = 0
    counter = 0
    while True:
        if counter == target:
            ret, frame = cam_device.read()
            if (demo_started):
                data_dict = dict()
                frame_resize = cv2.resize(frame, (112,112), interpolation=cv2.INTER_CUBIC)
                data = cv2.cvtColor(frame_resize, cv2.COLOR_BGR2RGB)
                if data_source_type == "Queue":
                    frame_diff = cv2.resize(frame, (28, 28), interpolation=cv2.INTER_CUBIC)
                    frame_diff_rgb = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2RGB)
                    gray = cv2.cvtColor(frame_diff_rgb, cv2.COLOR_RGB2GRAY)
                    data_dict["data_gray"] = gray    
                data_dict["data"] = data
                queue.put(data_dict)
            else:
                ret = cam_device.grab()
            counter = 0 
        else:
            ret = cam_device.grab() 
            counter += 1
        
        if (demo_stopped):
            print("main - capture_thread stop")
            break


# In[7]:


def exitApp(controller):
    
    keyboard.wait("q")
    print("main - [+] Pressed", "q", ":exitApp")
    
    if controller is not None:
        controller.stop_components()


# In[8]:


def controller_status_changed(old_state, new_state):
    global demo_ready
    global demo_started
    global demo_stopped
    
    print("main - controller_status_changed is called - old_state: %d, new_state: %d"%(old_state, new_state))
    if new_state == Controller.state_map["Stopped"]:
        reset_data_folder(cam_data_path+"\\")
        reset_data_folder(predict_data_path+"\\")
        demo_stopped = True
    elif new_state == Controller.state_map["Started"]:
        demo_started = True
    elif new_state == Controller.state_map["Init"]:
        demo_ready = True


# In[9]:


def main():
    global cam_device
    global capture_thread
    global data_source_type
    global demo_ready
    global demo_started
    global demo_stopped
    
    reset_data_folder(cam_data_path+"\\")
    reset_data_folder(predict_data_path+"\\")
    
    # initialize webcam capture object
    cam_device = cv2.VideoCapture(0)

    # retrieve properties of the capture object
    cap_width = cam_device.get(cv2.CAP_PROP_FRAME_WIDTH)
    cap_height = cam_device.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cap_fps = cam_device.get(cv2.CAP_PROP_FPS)
#     print('main -  Cam width:', cap_width)
#     print('main -  Cam height:', cap_height)
#     print('main -  Cam FPS:', cap_fps)
    
    # create a queue for cam
    cam_frames_queue = queue.Queue(maxsize=0)
    
    # start the capture thread: reads frames from the camera (non-stop) and stores the result in img
    capture_thread = Thread(target=start_capture_thread, args=(cam_device, cam_frames_queue,), daemon=True) # a deamon thread is killed when the application exits
    capture_thread.start()
    
    controller = Controller(cam_data_path, threed_cnn_model_type, threed_cnn_mode, data_source_type, youtube_360_video_url, youtube_auto_refresh, timer_interval)
    controller.bind_to("main", controller_status_changed)
    controller.init_components()
    
    exit_thread = Thread(target=exitApp, args=(controller,), daemon=True) # a deamon thread is killed when the application exits
    exit_thread.start()
    
    # wait to init
    while not demo_ready:
        time.sleep(0.5)
    print("main - demo is initialized")
    
    controller.start_components()
    # wait to start
    while not demo_started:
        time.sleep(0.5)
    print("main - demo is started")
    
    # initialize time and frame count variables
    frames = 0
    time_total = 0
    cam_data_dict = None
    send_data = dict() # score:frame
    diff_data = [None, None]
    while (True):
        if (cam_frames_queue.empty()):
            continue
            
        # blocks until the entire frame is read
        frames += 1
        cam_data_dict = cam_frames_queue.get()
        
        if data_source_type == "Queue":
            start = time.time()
            if cam_data_dict is not None:
                if frames == 1:
                    diff_data[0] = cam_data_dict["data_gray"]
                    send_data[-1] = cam_data_dict["data"]
                elif frames == 2:
                    diff_data[1] = cam_data_dict["data_gray"]
                    send_data[-1] = cam_data_dict["data"]
                else:
                    (diff_data[0], diff_data[1]) = (diff_data[1], cam_data_dict["data_gray"])
                if frames >= 2:
                    (score, diff) = structural_similarity(diff_data[0], diff_data[1], full=True)
                    send_data[score] = cam_data_dict["data"]
                controller.data_queue.put(send_data.copy())
                end = time.time()
                time_total += (end-start)
#                 print("main - frames =", frames, "spending time =", (end-start), " time_total =", time_total)
#                 img_path = os.path.join(cam_data_path, str(frames)+".jpg")
#                 img_path = local_path(root_path, img_path)
#                 cv2.imwrite(img_path, cv2.cvtColor(cam_data_dict["data"], cv2.COLOR_RGB2BGR)) #test
        else:
            if cam_data_dict is not None:
                img_path = os.path.join(cam_data_path, str(frames)+".jpg")
                img_path = local_path(root_path, img_path)
                cv2.imwrite(img_path, cv2.cvtColor(cam_data_dict["data"], cv2.COLOR_RGB2BGR))
        send_data.clear()
        cam_data_dict.clear()
        
        if demo_stopped:
            print("main - main leave loop")
            break
    if capture_thread is not None:
        capture_thread.join()
    if cam_device is not None:
        cam_device.release()
    exit()


# In[10]:


main()


# In[ ]:





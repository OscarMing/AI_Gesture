#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import subprocess
from threading import Thread
import time

from libs.desktop_lib import Desktop
from libs.utils import StateFlow

class Youtube_360_Degree(Desktop, StateFlow):

    Gesture_KeyBoard_map = {0: "a", 1: "d", 2: "s", 3: "w", 4: "]", 5: "["}
    
    KeyBoard_Commands = dict({"W": "Hand Up", "w": "Hand Up", "S": "Hand Down", "s": "Hand Down", "A": "Hand Left", "a": "Hand Left", "D": "Hand Right", "d": "Hand Right", "]":"Turning Hand Clockwise", "[":"Turning Hand Counterclockwise"})
    
    Video_State = dict({"Stopped": 0, "Started":1, "Paused": 2, "Init": -1})
    
    def __init__(self, url, auto_refresh=False):
        StateFlow.__init__(self)
        self.url = url
        self.browser = None
        self.chromedriver = None
        self.stop_by_inner = False
        self.__monitor_thread = None
        self.auto_refresh = auto_refresh
    
    def start(self):
        if not self.__process_exists("chromedriver.exe"):
            try:
                self.chromedriver = subprocess.Popen(["chromedriver.exe"])
            except:
                self.chromedriver = None
                print("Youtube - chrome driver is not starting")
                raise "Youtube - chrome driver is not starting"
        else:
            print("Youtube - chrome driver is starting")
        if self.browser is None:
            if self.url is None:
                print("Youtube - url is empty")
                raise "Youtube - url is empty"
            self.browser = webdriver.Chrome()
            self.wait = WebDriverWait(self.browser, 3)
            self.browser.maximize_window()
            try:
                self.browser.get(self.url)
            except:
                print("Youtube - network is not connected")
                raise "Youtube - network is not connected"
            self.presence = EC.presence_of_element_located
            self.visible = EC.visibility_of_element_located
            self.full_screen()
        self.__start_video_state_thread()
        self.state = self.state_map["Started"]
    
    def stop(self):
        self.state = self.state_map["Stopping"]
        if self.browser is not None:
            self.browser.quit()
            self.browser = None
        if self.chromedriver is not None:
            self.chromedriver.kill()
            self.chromedriver = None
        self.state = self.state_map["Stopped"]
    
    def send_command(self, command):
        if self.state != self.state_map["Started"]:
            return
        if self.browser is None:
            raise "Youtube - browser is not initialized"
        if self.chromedriver is None: 
            raise "Youtube - chromedriver is not initialized"
        
        action = ""
        if command in self.Gesture_KeyBoard_map.keys():
            action = self.Gesture_KeyBoard_map[command]
        else:
            print("Youtube - command is not supported")
            raise "Youtube - command is not supported"
        
        if action == "":
            return
        
        if action in self.KeyBoard_Commands.keys():
            body_element = self.__find_element_by_tag('body')
#             print("Youtube - action = "+str(self.KeyBoard_Commands[action]))
            try:
                if body_element is None or body_element == "":
                    print("Youtube - body element is not finded")
                    raise "Youtube - body element is not finded"
                else:    
                    ActionChains(self.browser).key_down(action).click(body_element).key_up(action).perform()
            except:
                print("Youtube - except")
        else:
            print("Youtube - command of keyboard is not supported")
            raise "Youtube - command of keyboard is not supported"
    
    def __start_video_state_thread(self):
        if self.__monitor_thread is None:
            self.__monitor_thread = Thread(target=self.__monitor_video_state, daemon=True)
            self.__monitor_thread.start()
    
    def __monitor_video_state(self):
        while True:
            if self.state == self.state_map["Started"]:
                video_state = self.__getVideoState()
#                 print("Youtube - video_state = "+str(video_state))
                if video_state == self.Video_State['Stopped']:
                    if self.auto_refresh:
                        self.refresh()
                        self.wait.until(self.visible((By.ID, "video-title")))
                        self.full_screen()
                    else:
                        self.stop_by_inner = True
                        self.stop()
                        break
            elif self.state == self.state_map["Stopped"]:
                break             
    
    def __getVideoState(self):
        video_state = -1
        if self.browser is not None:
            video_state = self.browser.execute_script("return document.getElementById('movie_player').getPlayerState()")
        return video_state
        
    def __process_exists(self, process_name):
        call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
        processes = []
        for process in subprocess.check_output(call).splitlines()[3:]:
            process = process.decode()
            processes.append(process.split())
        return True if len(processes) != 0 else False
    
    def __find_element_by_tag(self, name):
        element = self.browser.find_element_by_tag_name(name)
        return element
    
    def full_screen(self):
        full_screen_button = self.browser.find_elements_by_xpath("//*[@class='ytp-fullscreen-button ytp-button']")[0]
        full_screen_button.click()
    
    def refresh(self):
        if self.browser is not None:
            self.browser.refresh()
    
    def __del__(self):
        print("Youtube - __del__")
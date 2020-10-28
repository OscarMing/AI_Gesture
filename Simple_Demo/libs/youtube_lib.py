#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import subprocess
from threading import Thread


# In[2]:


class Youtube_360_Degree(object):

    KeyBoard_Commands = dict({"W": "Hand Up", "w": "Hand Up", "S": "Hand Down", "s": "Hand Down", "A": "Hand Left", "a": "Hand Left", "D": "Hand Right", "d": "Hand Right", "]":"Turning Hand Clockwise", "[":"Turning Hand Counterclockwise"})
    
    State = dict({"Ready": 0, "Started":1, "Stopping": 2, "Stopped": 3})
    
    Video_State = dict({"Stopped": 0, "Started":1, "Paused": 2, "Init": -1})
    
    def __init__(self, url):
        self.url = url
        self.browser = None
        self.chromedriver = None
        self.__observers = dict()
        self.stop_by_inner = False
        self.__monitor_thread = None
        self.__state = self.State["Ready"]
    
    @property
    def state(self):
        return self.__state
    
    def start(self):
        if not self.__process_exists("chromedriver.exe"):
            try:
                self.chromedriver = subprocess.Popen(["chromedriver.exe"])
            except:
                self.chromedriver = None
                raise "chrome driver is not starting"
        else:
            print("chrome driver is starting")
        if self.browser is None:
            if self.url is None:
                raise "url is empty"
            self.browser = webdriver.Chrome()
            self.browser.maximize_window()
            self.browser.get(self.url)
            self.full_screen()
        self.__start_video_state_thread()
        self.__update_state(self.State["Started"])
    
    def stop(self):
        self.__update_state(self.State["Stopping"])
        if self.browser is not None:
            self.browser.quit()
            self.browser = None
        if self.chromedriver is not None:
            self.chromedriver.kill()
            self.chromedriver = None
        self.__update_state(self.State["Stopped"])
    
    def __update_state(self, state):
        old_state = self.__state
        if old_state != state:
            self.__state = state
            print("state of Youtube_360_Degree is changed. ", "old_state = ", old_state, " new_state = ", self.__state)
            for name, callback in self.__observers.items():
                callback(old_state, self.__state)
    
    def bind_to(self, name, callback):
        if name not in self.__observers.keys():
            print('Youtube_360_Degree - bound is called - %s is not in observers'%(name))
            self.__observers[name] = callback
        else:
            print('Youtube_360_Degree - bound is called - %s is in observers'%(name))
    
    def unbind_from(self, name):
        if name in self.__observers.keys():
            print('Youtube_360_Degree - unbound is called - %s is in observers'%(name))
            del self.__observers[name]
        else:
            print('Youtube_360_Degree - unbound is called - %s is not in observers'%(name))
    
    def print_observers(self):
        for name, callback in self.__observers.items():
            print("Youtube_360_Degree - observers - name:", name, " callback:", str(callback))
    
    def send_keyBoard_command(self, name):
        if self.__state != self.State["Started"]:
            return
        if self.browser is None:
            raise "browser is not initialized"
        if self.chromedriver is None: 
            raise "chromedriver is not initialized"
        if name in self.KeyBoard_Commands.keys():
            body_element = self.__find_element_by_tag('body')
#             print(body_element)
            print("Youtube_360_Degree - action = "+str(self.KeyBoard_Commands[name]))
            try:
                if body_element is None or body_element == "":
                    raise "body element is not finded"
                else:    
                    ActionChains(self.browser).key_down(name).click(body_element).key_up(name).perform()
            except:
                print("except")
        else:
            raise "command of keyboard is not supported"
    
    def __start_video_state_thread(self):
        if self.__monitor_thread is None:
            self.__monitor_thread = Thread(target=self.__monitor_video_state, daemon=True)
            self.__monitor_thread.start()
    
    def __monitor_video_state(self):
        while True:
            if self.__state == self.State["Started"]:
                video_state = self.__getVideoState()
#                 print("video_state = "+str(video_state))
                if video_state == self.Video_State['Stopped']:
                    self.stop_by_inner = True
                    self.stop()
                    break
            elif self.__state == self.State["Stopped"]:
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
#         print(processes)
        return True if len(processes) != 0 else False
    
    def __find_element_by_tag(self, name):
        element = self.browser.find_element_by_tag_name(name)
        return element
    
    def full_screen(self):
        full_screen_button = self.browser.find_elements_by_xpath("//*[@class='ytp-fullscreen-button ytp-button']")[0]
        full_screen_button.click()
    
    def __del__(self):
        print("Youtube_360_Degree-__del__")





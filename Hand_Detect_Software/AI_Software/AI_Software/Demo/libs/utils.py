#!/usr/bin/env python
# coding: utf-8

import os

def local_path(root_path, abs_path):
    abs_path = abs_path.replace(root_path, "")
    return "."+"/".join(abs_path.split(os.sep))

class StateFlow(object):
    
    state_map = dict({"Ready": 0, "Init":1, "Started":2, "Stopping": 3, "Stopped": 4})
    
    def __init__(self):
        self._observers = dict()
        self._state = self.state_map["Ready"]
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        old_state = self._state
        if old_state != value:
            self._state = value
            print("state of StateFlow is changed. ", "old_state = ", old_state, " new_state = ", value)
            self._update_state(old_state, value)
    
    def _update_state(self, old_state, new_state):
        for name, callback in self._observers.items():
            callback(old_state, new_state)
    
    def bind_to(self, name, callback):
        if name not in self._observers.keys():
            print('StateFlow - bound is called - %s is not in observers'%(name))
            self._observers[name] = callback
        else:
            print('StateFlow - bound is called - %s is in observers'%(name))
    
    def unbind_from(self, name):
        if name in self._observers.keys():
            print('StateFlow - unbound is called - %s is in observers'%(name))
            del self._observers[name]
        else:
            print('StateFlow - unbound is called - %s is not in observers'%(name))
    
    def print_observers(self):
        for name, callback in self._observers.items():
            print("StateFlow - observers - name:", name, " callback:", str(callback))
            
    def __del__(self):
        print("StateFlow - __del__")
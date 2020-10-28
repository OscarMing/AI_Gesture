#!/usr/bin/env python
# coding: utf-8

import abc

class Desktop(abc.ABC):
    
    @abc.abstractmethod
    def start(self):
        return NotImplemented
    
    @abc.abstractmethod
    def stop(self):
        return NotImplemented
    
    @abc.abstractmethod
    def send_command(self, command):
        return NotImplemented
    
    def __del__(self):
        print("Desktop - __del__")
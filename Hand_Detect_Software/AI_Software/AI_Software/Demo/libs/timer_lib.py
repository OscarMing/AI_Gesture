from threading import Timer

class LoopTimer(Timer):  
    """Call a function after a specified number of seconds:


            t = LoopTimer(30.0, f, args=[], kwargs={})
            t.start()
            t.cancel()     # stop the timer's action if it's still waiting


    """
    def __init__(self, interval, function, args=[], kwargs={}):
        Timer.__init__(self,interval, function, args, kwargs)


    def run(self):
        '''self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()'''
        while True:
            self.finished.wait(self.interval)
            if self.finished.is_set():
                self.finished.set()
                break
            self.function(*self.args, **self.kwargs)
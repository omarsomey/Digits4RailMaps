from threading import Thread
import cv2
import subprocess
from subprocess import PIPE
import os
import time
import timeit
from FPS import FPS

class See3Cam:
    
    def __init__(self, src, width, height, framerate, name, label):
        self.src = src  
        self.name = name
        self.label = label
        self.width = width
        self.height = height
        self.framerate = framerate
        self.grabbed = False
        self.frame = None
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3, width)
        self.stream.set(4, height)
        self.stream.set(cv2.CAP_PROP_FPS, framerate)
        self.connected = True
        self.stopped = False
        self.fps = FPS()

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        print("Camera started")
        self.fps.start()
        return self
    
    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()
            self.fps.update()

    
    def read(self):
        return self.grabbed ,self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

    def show_fps(self):
        self.fps.stop()
        print("[INFO] elapsed time read: {:.2f}".format(self.fps.elapsed()))
        print("[INFO] approx. FPS read: {:.2f}".format(self.fps.fps()))
        self.fps.start()
    

    


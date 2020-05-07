from threading import Thread
import cv2
import subprocess
from subprocess import PIPE
import os
import time
import timeit
from queue import Queue


class See3Cam:
    
    def __init__(self, src, width, height, framerate, name):
        self.src = src
        self.name = name
        self.width = width
        self.height = height
        self.framerate = framerate
        self.grabbed = False
        self.frame = None
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3, width)
        self.stream.set(4, height)
        self.stream.set(cv2.CAP_PROP_FPS, framerate)
        self.running = self.stream.isOpened()
        self.connected = True
        self.stopped = False

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    
    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()

    
    def read(self):
        return self.grabbed ,self.frame

    def stop(self):
        self.stopped = True
    

    def find_cam(self, cam):
        cmd = ["/usr/bin/v4l2-ctl", "--list-devices"]
        out, err = subprocess.Popen(cmd,stdout=PIPE, stderr=PIPE).communicate()
        out, err = out.strip(), err.strip()
        for l in [i.split(b'\n\t') for i in out.split(b'\n\n')]:
            if cam in l[0].decode(encoding="UTF-8"):
                return (True, l[1].decode(encoding="UTF-8")[-1])
        return False, None
    
    


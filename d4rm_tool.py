import tkinter
import time
import timeit
import datetime
import threading
import multiprocessing
import random
from queue import Queue
import os
import sys
import numpy
from GpsCapture import GpsCapture
from See3Cam import See3Cam
from FPS import FPS
from Controller.RecordingThreadController import RecordingThreadController
from Controller.CamRecordThreadController import CamThreadController
from Controller.GpsRecordThreadController import GpsThreadController
from Controller.CamPollingThreadController import CamPollingThreadController
import cv2
from GuiPart import GuiPart
import serial
import serial.tools.list_ports
import PIL.Image, PIL.ImageTk
import PIL 
from PIL import Image
from PIL import ImageTk
import subprocess
from subprocess import PIPE

import imageio
import timeit
import time
from statistics import mean
from jproperties import Properties
import set_id as s


class ThreadedClient:
    """
    Launch the main part of the GUI and the differents threads of the Tool.
    One class responsible of the different control threads 
    """

    def __init__(self, master):

        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well.
        """
        self.master = master
        self.cam_prop_path = "Properties/cam.properties"
        self.second_cam_prop_path = "Properties/second-cam.properties"
        self.gps_prop_path = "Properties/gps.properties"
        self.record= False
        self.img = None
        self.frame = None
        self.frame1 = None
        self.f = 0
        self.check = False
        s.setId(self.cam_prop_path, self.second_cam_prop_path, self.gps_prop_path) # set the Id at the beginning of the app 
        self.cam_properties= self.getProperties(self.cam_prop_path)
        self.second_cam_properties = self.getProperties(self.second_cam_prop_path)
        self.gps_properties = self.getProperties(self.gps_prop_path)

        self.running = 1
        self.cameras_state = self.find_cam()
        self.verify_gps_connection, self.gps_port = self.find_gps()
        print(self.cameras_state)
        print(self.verify_gps_connection)

        # Set up the GUI part
        self.gui = GuiPart(master, self, self.cameras_state, self.verify_gps_connection, self.recordData, self.stopRecord)

        if self.cameras_state[0]:
            self.camera = See3Cam(src=self.cameras_state[1], width=1280, height=720, framerate=30, name="cam")
            self.camera.start()
            self.camPollThread = CamPollingThreadController(self, self.camera, self.gui)
            self.camPollThread.start()
            self.camThread = CamThreadController(self, self.camera, self.camera.name, self.cam_properties, self.gui)
        if self.cameras_state[2]:
            self.camera1 = See3Cam(src=self.cameras_state[3], width=1280, height=720, framerate=30, name="cam1")
            self.camera1.start()
            self.camPollThread1 = CamPollingThreadController(self, self.camera1, self.gui)
            self.camPollThread1.start()
            self.cam1Thread = CamThreadController(self, self.camera1, self.camera1.name, self.second_cam_properties, self.gui)
        if self.verify_gps_connection:
            self.gps = GpsCapture()
            self.gps.start()
            self.gpsThread = GpsThreadController(self, self.gps, self.gps_properties, self.gui)


        self.fps = FPS()
 
        
        # Set up the thread for the GPS checking
        gps_controller = threading.Thread(target=self.checkGpsConnection, args=(1,))
        gps_controller.setDaemon(True)
        gps_controller.start()

        # Set up the thread for the camera checking
        camera_controller = threading.Thread(target=self.checkCameraConnection, args=(1,))
        camera_controller.setDaemon(True)
        camera_controller.start()




        self.video_output = True
        # Start the periodic call in the GUI .

        self.periodicCall()



    def periodicCall(self):
        """
        Check every 1 ms the connection to the GPS system and camera and 
        send them to GUI part.
        """

        if self.gps.running or self.frame is not None or self.frame1 is not None:
            self.check = True

        # Update the GUI of the camera and GPS status
        self.gui.processIncoming(self.cameras_state,  self.gps.running, self.video_output, self.frame, self.frame1)
            

        if not self.running:
            # This is the brutal stop of the system.
            sys.exit(1)
        self.master.after(1, self.periodicCall)

    def checkGpsConnection(self, interval = 1):
        """
        Thread to Check the port connection and the status of the GPS System
        every second.
        """
        while True:
            # Get the GPS port connection
            verify_gps_connection, gps_port = self.gps.get_port()
            if not verify_gps_connection:
                self.gps.running = False
                self.gps.isConnected = False
            elif not self.gps.running:
                self.gps.running = False
                self.gps.open_gps(gps_port,self.gps.baudrate)
            else:
                self.gps.running = True
                self.gps.isConnected = True

            time.sleep(interval)
            


    def checkCameraConnection(self, interval = 1):
        """
        Thread to Check the port connection and the status of the Camera
        every second.
        """
        while True:
            self.cameras_state = self.find_cam()
            if not self.cameras_state[0]:
                time.sleep(1)
                continue
            if not self.cameras_state[2]:
                time.sleep(1)
                continue

            time.sleep(interval)

  

    def recordData(self):
        """
        This function listens to the record button and starts the recording thread accordingly
        """
        if self.check:
            if not self.record:
                self.video_output = False
                self.camPollThread.stop()
                self.camPollThread1.stop()
                self.camThread.start()
                self.cam1Thread.start()
                self.gpsThread.start()
                self.record = True
                self.gui.btn_record.configure(text="Recording", bg="red")
                self.gui.progress_bar.start(int(10000/100)) #  duration of videos in seconds divided by 100
            else:
                print("Alreadiy recording")
                self.gui.notification_label.configure(text="Already recording !")
        else:
            print("Cannot record, There is no device connected !")
            self.gui.notification_label.configure(text="Cannot record, There is no device connected !")


    def stopRecord(self):
        """
        This function listens to the record button and starts the recording thread accordingly
        """
        if self.record:
            self.video_output = True
            self.camThread.stop()
            self.cam1Thread.stop()
            self.gpsThread.stop()
            self.camPollThread.start()
            self.camPollThread1.start()
            self.record = False
            self.gui.btn_record.configure(text="Record Data", bg="green")
            self.gui.progress_bar.stop()
        else:
            print("There is no recording")

    def getProperties(self, path):
        props = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.rstrip() #removes trailing whitespace and '\n' chars
                if "=" not in line: continue #skips blanks and comments w/o =
                if line.startswith("#"): continue #skips comments which contain =
                k, v = line.split("=", 1)
                props[k] = v
        return props
     

    def find_cam(self):
        camera_indexes =[]
        cmd = ["/usr/bin/v4l2-ctl", "--list-devices"]
        out, err = subprocess.Popen(cmd,stdout=PIPE, stderr=PIPE).communicate()
        out, err = out.strip(), err.strip()
        for l in [i.split(b'\n\t') for i in out.split(b'\n\n')]:
            if "See3CAM_CU20" in l[0].decode(encoding="UTF-8"):
                camera_indexes.append(int(l[1].decode(encoding="UTF-8")[-1]))



        if camera_indexes.__len__() == 2:
            return (True, camera_indexes[0], True, camera_indexes[1])
        elif camera_indexes.__len__() == 1:
            return (True, camera_indexes[0], False, None)
        else:
            return (False, None, False, None)

    def find_gps(self):
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]

        for t in myports:
            if 'FT232R USB UART' in t:
                gpsport = t[0]
                self.isConnected = True
                return(True, gpsport)

        self.isConnected= False
        return (False, None)
    


rand = random.Random()
root = tkinter.Tk()
client = ThreadedClient(root)

def close_application_globally():
    """
    This function close the different threads of the application when
    the user exits the App.    
    """
    try:
        client.camera.stop()
        client.camera1.stop()
    except AttributeError:
        print("There is no camera")

    client.running = 0

    
    root.destroy()
    sys.exit(1)

root.protocol("WM_DELETE_WINDOW", close_application_globally)
root.mainloop()
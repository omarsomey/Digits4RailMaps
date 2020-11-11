import tkinter
from tkinter import ttk
from tkinter import Tk
from tkinter import Button
import time
import timeit
import datetime
import threading
import random
import errno
import sys
import os
import PIL.Image, PIL.ImageTk
import PIL 
from PIL import Image
from PIL import ImageTk
from GuiPart import GuiPart
from GpsCapture import GpsCapture
from See3Cam import See3Cam
from FPS import FPS
from Controller.CamRecordThreadController import CamThreadController
from Controller.GpsRecordThreadController import GpsThreadController
from Controller.CamPollingThreadController import CamPollingThreadController
from checkConnections import find_cam, find_gps, find_hd
import shutil


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
        self.exitFlag = False ## Flag to terminate all the threads 
        self.directory = "/home/knorr-bremse/"
        self.record= False
        self.camera = None
        self.camera1 = None
        self.gps = None
        self.check = True
        self.cameras_state = find_cam()
        self.verify_gps_connection, self.gps_port = find_gps()
        self.verify_hd_connection = find_hd()
        self.i = 0

        
        print(self.cameras_state)
        print(self.verify_gps_connection, self.gps_port)

        # Set up the GUI part
        self.gui = GuiPart(master, self, self.cameras_state, self.verify_gps_connection, self.recordData)

        if self.cameras_state[0]:
            self.camera = See3Cam(src=self.cameras_state[1], width=1920, height=1080, framerate=30, name="cam", label="1")
            self.camera.start()
            self.camThread = CamThreadController(self, self.camera, self.camera.name, self.gui)
        if self.cameras_state[2]:
            self.camera1 = See3Cam(src=self.cameras_state[3], width=1920, height=1080, framerate=30, name="cam1", label="2")
            self.camera1.start()
            self.cam1Thread = CamThreadController(self, self.camera1, self.camera1.name, self.gui)
        if self.verify_gps_connection:
            self.gps = GpsCapture()
            self.gps.start()
            self.gpsThread = GpsThreadController(self, self.gps, self.gui)



        # Start the periodic call in the GUI .

        self.periodicCall()



    def periodicCall(self):
        """
        Check every 15 ms the connection to the GPS system and camera and 
        send them to GUI part.
        """
        # Check the connections of the devices
        self.verify_gps_connection, self.gps_port = find_gps()
        self.cameras_state = find_cam()
        # Checking if there is at least one device connected
        if (self.verify_gps_connection and self.gps is not None) or self.camera is not None or self.camera1 is not None:
            self.check = True
        else:
            self.check = False

        # Update the GUI of the camera and GPS status
        self.gui.processIncoming(self.cameras_state,  self.verify_gps_connection, self.verify_hd_connection, self.record)

        self.master.after(1, self.periodicCall)



    def recordData(self):
        """
        This function listens to the record button and starts the recording thread accordingly
        """
        if self.check:
            if not self.record:
                self.dirname = self.gui.title.get()
                try:
                    os.mkdir(self.directory + self.dirname)
                except FileExistsError:
                    self.i = self.i+1
                    if self.i>=10:
                        self.dirname = self.dirname +"_"+str(self.i)
                    else:
                        self.dirname = self.dirname+"_0"+str(self.i)
                    os.mkdir(self.directory + self.dirname)
                if self.camera is not None:
                    os.mkdir(self.directory + self.dirname + "/Camera 1")
                    self.camThread.start()
                if self.camera1 is not None:
                    self.camPollThread1.stop()
                    os.mkdir(self.directory + self.dirname + "/Camera 2")
                    self.cam1Thread.start()
                if self.gps is not None and self.gps.running:
                    os.mkdir(self.directory + self.dirname + "/GPS")
                    self.gpsThread.start()
                self.record = True
                self.gui.btn_record.configure(text="Stop", bg="red")
                self.gui.notification_label.configure(text="Recording in Progress")
                self.gui.progress_bar.start(int(10000/100)) #  duration of videos in seconds divided by 100
            else:
                if self.camera is not None:
                    self.camThread.stop()
                if self.camera1 is not None:
                    self.cam1Thread.stop()
                if self.gps is not None and self.gps.running:
                    self.gpsThread.stop()
                self.gui.notification_label.configure(text="Recording Stopped")
                self.gui.btn_record.configure(text="Record Data", bg="green")
                self.gui.progress_bar.stop()
                self.record = False
                        
        else:
            self.gui.notification_label.configure(text="Cannot record, There is no device connected !")



def main():
    root = tkinter.Tk()
    root.title("Digits4RailMaps Recording Tool")
    img = ImageTk.PhotoImage(file='kb.ico')
    root.tk.call('wm', 'iconphoto', root._w, img)
    client = ThreadedClient(root)

    def close_application_globally():
        """
        This function close the different threads of the application when
        the user exits the App.    
        """
        client.exitFlag = True
        if client.camera is not None:
            if client.record:  
                client.camThread.stop()
            client.camera.stop()
        if client.camera1 is not None:
            if client.record:
                client.cam1Thread.stop()
            client.camera1.stop()
        if client.gps is not None and client.gps.running:
            if client.record:
                client.gpsThread.stop()
            client.gps.stop()
        client.running = 0
        root.destroy()
        sys.exit(1)

    root.protocol("WM_DELETE_WINDOW", close_application_globally)
    root.mainloop()

if __name__ == "__main__":
    main()
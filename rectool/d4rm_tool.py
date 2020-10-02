import tkinter
from tkinter import ttk
from tkinter import Tk, W, E, Frame
from tkinter import Button, Entry, Label, LabelFrame, StringVar
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
import PIL 
from PIL import Image
from PIL import ImageTk
import time
import timeit
import datetime
import threading
import random
import os
import errno
import sys
import numpy
import cv2
import serial
import serial.tools.list_ports
import subprocess
from subprocess import PIPE
import imageio
from GuiPart import GuiPart
from GpsCapture import GpsCapture
from See3Cam import See3Cam
from FPS import FPS
from Controller.CamRecordThreadController import CamThreadController
from Controller.GpsRecordThreadController import GpsThreadController
from Controller.CamPollingThreadController import CamPollingThreadController
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
        self.img = None
        self.mem = False
        self.mem1 = False
        self.camera = None
        self.camera1 = None
        self.gps = None
        self.check = True
        self.running = 1
        self.cameras_state = self.find_cam()
        self.verify_gps_connection, self.gps_port = self.find_gps()
        self.verify_hd_connection = self.find_hd()
        self.i = 0

        
        print(self.cameras_state)
        print(self.verify_gps_connection, self.gps_port)

        # Set up the GUI part
        self.gui = GuiPart(master, self, self.cameras_state, self.verify_gps_connection, self.recordData)

        if self.cameras_state[0]:
            self.camera = See3Cam(src=self.cameras_state[1], width=1280, height=720, framerate=30, name="cam", label="1")
            self.camera.start()
            self.camPollThread = CamPollingThreadController(self, self.camera, self.gui)
            self.camPollThread.start()
            self.camThread = CamThreadController(self, self.camera, self.camera.name, self.gui)
        if self.cameras_state[2]:
            self.camera1 = See3Cam(src=self.cameras_state[3], width=1280, height=720, framerate=30, name="cam1", label="2")
            self.camera1.start()
            self.camPollThread1 = CamPollingThreadController(self, self.camera1, self.gui)
            self.camPollThread1.start()
            self.cam1Thread = CamThreadController(self, self.camera1, self.camera1.name, self.gui)
        if self.verify_gps_connection:
            self.gps = GpsCapture()
            self.gps.start()
            self.gpsThread = GpsThreadController(self, self.gps, self.gui)


        self.fps = FPS()
 
        
        # Set up the thread for the GPS checking
        gps_controller = threading.Thread(target=self.checkGpsConnection, args=(1,))
        gps_controller.setDaemon(True)
        gps_controller.start()

        # Set up the thread for the camera checking
        camera_controller = threading.Thread(target=self.checkCameraConnection, args=(1,))
        camera_controller.setDaemon(True)
        camera_controller.start()


        # Start the periodic call in the GUI .

        self.periodicCall()



    def periodicCall(self):
        """
        Check every 1 ms the connection to the GPS system and camera and 
        send them to GUI part.
        """
        if (self.verify_gps_connection and self.gps is not None) or self.camera is not None or self.camera1 is not None:
            self.check = True
        else:
            self.check = False

        # Update the GUI of the camera and GPS status
        self.gui.processIncoming(self.cameras_state,  self.verify_gps_connection, self.verify_hd_connection, self.record)
            

        if not self.running:
            # This is the brutal stop of the system.
            sys.exit(1)
        self.master.after(15, self.periodicCall)

    def checkGpsConnection(self, interval = 1):
        """
        Thread to Check the port connection and the status of the GPS System
        every second.
        """
        while not self.exitFlag:
            # Get the GPS port connection
            self.verify_gps_connection, self.gps_port = self.find_gps()
            #self.verify_hd_connection = self.find_hd()
            # if not verify_gps_connection:
            #     self.gps.running = False
            #     self.gps.isConnected = False
            # elif not self.gps.running:
            #     self.gps.running = False
            #     self.gps.open_gps(gps_port,self.gps.baudrate)
            # else:
            #     self.gps.running = True
            #     self.gps.isConnected = True

            time.sleep(interval)
            


    def checkCameraConnection(self, interval = 1):
        """ 
        Thread to Check the port connection and the status of the Camera
        every second.
        """
        while not self.exitFlag:
            self.cameras_state = self.find_cam()
            # if (self.camera is not None) and not (self.cameras_state[0] or not self.camera.isRunning()):
            #     self.camThread.stop()
            #     self.camPollThread.stop()
            #     self.camera.stop()
            #     self.camera = None
            # if (self.camera1 is not None) and (not self.cameras_state[2] or not self.camera1.isRunning()):
            #     self.cam1Thread.stop()
            #     self.camPollThread1.stop()
            #     self.camera1.stop()
            #     self.camera1 = None
            # if self.cameras_state[0] and self.camera is None:
            #     self.camera = See3Cam(src=self.cameras_state[1], width=1920, height=1080, framerate=30, name="cam", label="1")
            #     self.camera.start()
            #     self.camPollThread = CamPollingThreadController(self, self.camera, self.gui)
            #     self.camPollThread.start()
                
            # if self.cameras_state[2] and self.camera1 is None:
            #     self.camera1 = See3Cam(src=self.cameras_state[3], width=1920, height=1080, framerate=30, name="cam1", label="2")
            #     self.camera1.start()
            #     self.camPollThread1 = CamPollingThreadController(self, self.camera1, self.gui)
            #     self.camPollThread1.start()
            
            
            # if self.cameras_state[0]:
            #     self.mem = True
            # if self.cameras_state[2]:
            #     self.mem1 = True
            # if not self.cameras_state[0]:
            #     if self.mem:
            #         self.camera.stop()
            #         self.alert_popup("Error !", "A camera has been unplugged !", "Please connect the camera again and restart the Tool.")
            #         self.mem = False
            #         self.cam
            #     continue
            # if not self.cameras_state[2]:
            #     if self.mem1:
            #         self.camera1.stop()
            #         self.alert_popup("Error !", "A camera has been unplugged !", "Please connect the camera again and restart the Tool.")
            #         self.mem1 = False

            #     continue

            time.sleep(interval)

    
    def browseDirectory(self):
        try:
            self.directory = filedialog.askdirectory() +"/"
        except TypeError:
            self.alert_popup("Warning !","You have not selected a directory !", "The Data will be recorded on the last location")


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
                    #self.alert_popup("Error !", "Folder "+ self.directory + " already exists","Please Enter a new directory name in the field above")
                    if self.i>=10:
                        self.dirname = self.dirname +"_"+str(self.i)
                    else:
                        self.dirname = self.dirname+"_0"+str(self.i)
                    os.mkdir(self.directory + self.dirname)
                if self.camera is not None:
                    self.camPollThread.stop()
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
                    self.camPollThread.start()
                if self.camera1 is not None:
                    self.cam1Thread.stop()
                    self.camPollThread1.start()
                if self.gps is not None and self.gps.running:
                    self.gpsThread.stop()
                self.gui.notification_label.configure(text="Recording Stopped")
                self.gui.btn_record.configure(text="Record Data", bg="green")
                self.gui.progress_bar.stop()
                self.record = False
                        

        else:
            self.gui.notification_label.configure(text="Cannot record, There is no device connected !")


     
    def alert_popup(self, title, message, path):
        """Generate a pop-up window for special messages."""
        popup = Tk()
        popup.title(title)
        w = 400     # popup window width
        h = 200     # popup window height
        sw = popup.winfo_screenwidth()
        sh = popup.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        popup.geometry('%dx%d+%d+%d' % (w, h, x, y))
        m = message
        m += '\n'
        m += path
        w = Label(popup, text=m, width=120, height=10)
        w.pack()
        b = Button(popup, text="OK", command=popup.destroy, width=10)
        b.pack()
        popup.mainloop()

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
            if '/dev/ttyUSB0' in t:
                gpsport = t[0]
                self.isConnected = True
                return(True, gpsport)

        self.isConnected= False
        return (False, None)

    def find_hd(self):
        if not os.listdir("/media/knorr-bremse"):
            return False
        else:
            return True
    

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
            else:
                client.camPollThread.stop()
            client.camera.stop()
        if client.camera1 is not None:
            if client.record:
                client.cam1Thread.stop()
            else:
                client.camPollThread1.stop()
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
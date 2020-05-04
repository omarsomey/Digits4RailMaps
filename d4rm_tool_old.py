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
from RecordingThreadController import RecordingThreadController
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

# Importing the libraries for the object detection
import torch
from torch.autograd import Variable
import cv2
from data import BaseTransform, VOC_CLASSES as labelmap
from ssd import build_ssd
import imageio
import timeit
import time
from statistics import mean
from jproperties import Properties

cuda=torch.cuda.device(0)
if torch.cuda.is_available():
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
else:
    torch.set_default_tensor_type('torch.FloatTensor')

# Creating the SSD neural network
net = build_ssd('test') # We create an object that is our neural network ssd.
net.load_state_dict(torch.load('ssd300_mAP_77.43_v2.pth', map_location = lambda storage, loc: storage)) # We get the weights of the neural network from another one that is pretrained (ssd300_mAP_77.43_v2.pth).

# Creating the transformation
transform = BaseTransform(net.size, (104/256.0, 117/256.0, 123/256.0)) # We create an object of the BaseTransform class, a class that will do the required transformations so that the image can be the input of the neural network.



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
        self.gps_destination_file_name = ""
        self.frames_destination_timestamp =""
        self.video_destination_file_handler = cv2.VideoWriter()
        self.gps_destination_dir = "/home/knorr-bremse/Projects/Digits4RailMaps/icom_track_gui/GPS/"
        self.video_destination_dir = "/home/knorr-bremse/Projects/Digits4RailMaps/icom_track_gui/Videos/"
        self.record= False
        self.img = None
        self.frame = None
        self.frame1 = None
        self.f = 0
        self.check = False
        self.brahim = 1.0/25

        # p = Properties()
        # with open('config.properties', 'rb') as f:
        #     p.load(f, 'utf-8')

        # print(p["video_id"].data)                     #### incremtentaiton properties file 
        # p["video_id"]=str(int(p["video_id"].data) +1)
        # print(p["video_id"].data)
        # with open('config.properties', 'wb') as f:
        #     p.store(f, encoding="utf-8")

        self.frame = None
        # Create the gps queue
        self.gps_queue = Queue()
        # principal thread
        self.running = 1
        self.cameras_state = self.find_cam()
        print(self.cameras_state)
        if self.cameras_state[0]:
            self.camera = See3Cam(src=self.cameras_state[1], width=1280, height=720, framerate=30, name="CAM")
            self.camera.start()
        if self.cameras_state[2]:
            self.camera1 = See3Cam(src=self.cameras_state[3], width=1280, height=720, framerate=30, name="CAM1")
            self.camera1.start()

        self.fps = FPS()
        
        # Set up Gps
        self.gps = GpsCapture()
        # Set up the GUI part
        self.gui = GuiPart(master, self, self.cameras_state, self.gps.running, self.recordData, self.stopRecord)
        

        
        # Set up the thread for the GPS checking
        gps_controller = threading.Thread(target=self.checkGpsConnection, args=(2,))
        gps_controller.setDaemon(True)
        gps_controller.start()

        # Set up the thread for the camera checking
        camera_controller = threading.Thread(target=self.checkCameraConnection, args=(2,))
        camera_controller.setDaemon(True)
        camera_controller.start()

        # # Set up the thread for the video stream
        # camera_controller = threading.Thread(target=self.readCameraThread, args=(self.brahim,))
        # camera_controller.setDaemon(True)
        # camera_controller.start()

        # Set up the thread for the GPS stream
        camera_controller = threading.Thread(target=self.readGpsThread, args=(self.brahim,))           ## refactoring
        camera_controller.setDaemon(True)
        camera_controller.start()

        # Set up the Thread for the data recording
        self.recordingThread = RecordingThreadController(self, self.video_destination_dir, self.gps_destination_dir, self.gui)
        


        self.video_output = True
        # Start the periodic call in the GUI .

        self.fps.start()
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
        # # Repeat this function every 1 ms 
        # self.f = self.f+1
        # print(self.f)
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

            
        
    def readCameraThread(self, interval=0.05):
        while True:
            if self.cameras_state[0]:
                try:
                    self.grabbed ,self.frame = self.camera.read()
                except AttributeError:
                    time.sleep(2)
            if self.cameras_state[2]:
                try:
                    self.grabbed1 ,self.frame1 = self.camera1.read()
                except AttributeError:
                    time.sleep(2)
            # try:
            #     self.frame = self.detect(self.frame2, net.eval(), transform)
            # except RuntimeError:
            #     print("Runtime error")
            # if  self.recordingThread.record_thread is not None and self.recordingThread.isAlive():
            #     print("putting in cam queue")
            #     self.cam_queue.put(self.frame)
            time.sleep(interval)

            self.fps.update()

    def readGpsThread(self, interval=1):

        while True:

            if self.gps.running:
                self.gps.read()

            time.sleep(interval)
            # if  self.recordingThread.record_thread is not None and self.recordingThread.isAlive():
            #     print("Putting in gps queue")
            #     self.gps_queue.put(self.gps)


    def recordData(self):
        """
        This function listens to the record button and starts the recording thread accordingly
        """
        if self.check:
            if not self.record:
                self.video_output = False
                self.recordingThread.start()
                self.record = True
                self.gui.btn_record.configure(text="Recording", bg="red")
                self.gui.progress_bar.start(int(10000/100)) #  duration of videos divided by 100
            else:
                print("Alreadiy recording")
        else:
            print("Cannot record, There is no device connected !")


    def stopRecord(self):
        """
        This function listens to the record button and starts the recording thread accordingly
        """
        if self.record:
            self.video_output = True
            self.recordingThread.stop()
            self.record = False
            self.gui.btn_record.configure(text="Record Data", bg="green")
            self.gui.progress_bar.stop()
        else:
            print("There is no recording")

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
    
    def detect(self, frame, net, transform): # We define a detect function that will take as inputs, a frame, a ssd neural network, and a transformation to be applied on the images, and that will return the frame with the detector rectangle.

        height, width = frame.shape[:2] # We get the height and the width of the frame.
        frame_t = transform(frame)[0] # We apply the transformation to our frame.
        x = torch.from_numpy(frame_t).permute(2, 0, 1) # We convert the frame into a torch tensor.
        x = Variable(x.unsqueeze(0)) # We add a fake dimension corresponding to the batch.
        x = x.cuda()
        y = net(x) # We feed the neural network ssd with the image and we get the output y.
        detections = y.data # We create the detections tensor contained in the output y.
        scale = torch.Tensor([width, height, width, height]) # We create a tensor object of dimensions [width, height, width, height].
        for i in range(detections.size(1)): # For every class:
            if (labelmap[i-1] == "car") or (labelmap[i-1] == "person") or (labelmap[i-1] == "motorbike") or (labelmap[i-1] == "bicycle") or (labelmap[i-1] == "bus"):
                j = 0 # We initialize the loop variable j that will correspond to the occurrences of the class.
                while detections[0, i, j, 0] >= 0.6: # We take into account all the occurrences j of the class i that have a matching score larger than 0.6.
                    # We get the coordinates of the points at the upper left and the lower right of the detector rectangle.
                    pt = (detections[0, i, j, 1:] * scale).cpu().numpy()
                    topLeft = (int(pt[0]), int(pt[1])) # We get the top Left corner of the ogject detected
                    bottomRight = (int(pt[2]), int(pt[3])) # We get the bottom Right corner of the object detected
                    x, y = topLeft[0] , topLeft[1] # We get the coordinates of the top Left Corner
                    x = max(x,0)
                    y = max(y,0)
                    w, h = bottomRight[0] - topLeft[0], bottomRight[1] - topLeft[1] # We get the width and the height of the object detected
                    #print("x = ", x, " y  = ", y, "w = ", w , " h = " ,h)
                    cv2.rectangle(frame, topLeft, bottomRight, (0, 0, 0), cv2.FILLED) # We draw a rectangle around the detected object.
                    cv2.putText(frame, labelmap[i - 1], topLeft, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA) # We put the label of the class right above the rectangle.
                    j += 1 # We increment j to get to the next occurrence.
        return frame # We return the original frame with the detector rectangle and the label around the detected object.

    

rand = random.Random()
root = tkinter.Tk()
client = ThreadedClient(root)

def close_application_globally():
    """
    This function close the different threads of the application when
    the user exits the App.    
    """
    client.fps.stop()
    try:
        client.camera.stop()
        client.camera1.stop()
    except AttributeError:
        print("There is no camera")
    print("[INFO] elapsed time: {:.2f}".format(client.fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(client.fps.fps()))
    print("Closing Threads and dependencies")
    client.running = 0
    client.gps.stop()
    
    root.destroy()
    sys.exit(1)

root.protocol("WM_DELETE_WINDOW", close_application_globally)
root.mainloop()
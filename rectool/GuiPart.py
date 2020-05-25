import tkinter
from tkinter import ttk
from tkinter import Tk, W, E, Frame
from tkinter import Button, Entry, Label, LabelFrame
from tkinter import IntVar
from queue import Queue
import PIL.Image, PIL.ImageTk
import PIL 
from PIL import Image
from PIL import ImageTk
import cv2



class GuiPart:
    """
    Independent  class responsible for the GUI part of the tool
    """

    def __init__(self, master, client, camStatus, gpsStatus, recordData, stopRecord):

        """
        Set up of the GUI, creation of the different frames
        """

        self.camStatus = camStatus
        self.gpsStatus = gpsStatus
        self.client = client
        self.frame_width = 900
        self.frame_height =800
        self.frame1_width = 900
        self.frame1_height = 800
        self.img = None
        self.img1 = None
        

        style = ttk.Style()
        style.theme_create("ToolStyle", parent="alt", settings={
            "TNotebook" : {"configure": {"tabmargins": [2, 5, 2, 0] } },
            "TNotebook.Tab": {"configure": {"padding": [20, 20]},},
            "TProgressbar": {"configure":{"foreground": 'red',"background": 'red'}}
            })

        style.theme_use("ToolStyle")
        style.configure('TNotebook.Tab', font=('Arial Bold', '15', 'bold'), padding=[10 ,10])


        self.tab_parent = ttk.Notebook(master)
        self.recording_tab = ttk.Frame(self.tab_parent)
        self.video_tab = ttk.Frame(self.tab_parent)

        self.tab_parent.add(self.recording_tab, text="Data recording",)
        self.tab_parent.add(self.video_tab, text="Video Output")
        self.tab_parent.pack(expand=1, fill='both')


        self.topFrame()
        self.leftFrame()
        self.rightFrame()
        self.videoFrame()
        self.videoFrame1()
        self.framesCanvas()

    def topFrame(self):
        #welcome text
        self.topframe = Frame(self.recording_tab, borderwidth=5, relief=tkinter.GROOVE)
        self.topframe.pack(side = tkinter.TOP)
        self.welcome_text = tkinter.Label(self.topframe, text="D4RM synchronising tool", font=("Arial Bold", 20))
        self.welcome_text.pack(side = tkinter.TOP)
        
    def leftFrame(self):
        self.leftframe = LabelFrame(self.recording_tab, text="Input devices and settings", font=("Arial Bold", 15), height=800, width=500, borderwidth=5, relief=tkinter.GROOVE)
        self.leftframe.pack(side = tkinter.LEFT)
        self.leftframe.pack_propagate(False)
        self.cameraLabel()
        self.gpsLabel()

    
    def cameraLabel(self):
        # First camera Label
        self.camera_status_label = tkinter.Label(self.leftframe, text="First Cameras Status", font=("Arial Bold", 15), padx=15, pady=15)
        self.camera_status_label.pack()

        self.camera_device_label = tkinter.Label(self.leftframe, text="Unknown", font=("Arial Bold", 20),padx=5, pady=15)
        self.camera_device_label.pack()

        # Second camera label
        self.camera_status_label = tkinter.Label(self.leftframe, text="Second Cameras Status", font=("Arial Bold", 15), padx=15, pady=15)
        self.camera_status_label.pack()

        self.camera1_device_label = tkinter.Label(self.leftframe, text="Unknown", font=("Arial Bold", 20),padx=5, pady=15)
        self.camera1_device_label.pack()


    def gpsLabel(self):
        self.gps_status_label = tkinter.Label(self.leftframe, text="GPS Status", font=("Arial Bold", 15), padx=15, pady=15)
        self.gps_status_label.pack()
        
        self.gps_device_label = tkinter.Label(self.leftframe, text="Unknown", font=("Arial Bold", 20),padx=5, pady=15)
        self.gps_device_label.pack()
    
    def rightFrame(self):
        self.rightframe = LabelFrame(self.recording_tab, text="System informations", font=("Arial Bold", 15), height=800, width=1300, borderwidth=5, relief=tkinter.GROOVE)
        self.rightframe.pack(side = tkinter.LEFT)
        self.rightframe.pack_propagate(False)
        self.systemInfo()
        self.recordingButtons()
        self.progressBar()
        
        


    def systemInfo(self):
        self.notification_label = tkinter.Label(self.rightframe, text="Unknown", font=("Arial Bold", 20),padx=5, pady=15)
        self.notification_label.pack(anchor=tkinter.S, expand=True)


    def recordingButtons(self):
        # Start recording Button
        self.btn_record = tkinter.Button(self.rightframe, text="Record Data", command=self.client.recordData, font=("Arial Bold", 20))
        self.btn_record.pack(anchor=tkinter.S, expand=True)
        # Stop recording Button
        self.btn_stop = tkinter.Button(self.rightframe, text="Stop recording", command=self.client.stopRecord, font=("Arial Bold", 20))
        self.btn_stop.pack(anchor=tkinter.S, expand=True)

    
    def progressBar(self):
        self.progress_bar = ttk.Progressbar(self.rightframe, orient='horizontal', length = 350, mode='determinate')
        self.progress_bar.pack(anchor=tkinter.S, expand=True)

    
    def videoFrame(self):
        # Set up of the Right frame (Camera output)
        self.videoframe = LabelFrame(self.video_tab, text="Camera output", font=("Arial Bold", 15), height=800, width=900, borderwidth=5, relief=tkinter.GROOVE)
        self.videoframe.pack(side = tkinter.LEFT)
        self.videoframe.pack_propagate(False)

    def videoFrame1(self):
        # Set up of the left frame (Camera output 1)
        self.videoframe1 = LabelFrame(self.video_tab, text="Second Camera output", font=("Arial Bold", 15), height=800, width=900, borderwidth=5, relief=tkinter.GROOVE)
        self.videoframe1.pack(side = tkinter.LEFT)
        self.videoframe1.pack_propagate(False)
    
    
    def framesCanvas(self):
        # Set of the canvas comporting the camera output frames
        self.canvas = tkinter.Canvas(self.videoframe, width = self.frame_width, height = self.frame_height, highlightcolor = "red", bd=5)
        self.canvas.pack(anchor=tkinter.NW)
        self.first_canvas = self.canvas.create_text(0,0, font="Times 20 italic bold", text=" Unknown", anchor = tkinter.NW)

        # Set of the canvas comporting the second camera output frames
        self.canvas1 = tkinter.Canvas(self.videoframe1, width = self.frame1_width, height = self.frame1_height, highlightcolor = "red", bd=5)
        self.canvas1.pack(anchor=tkinter.NE)
        self.second_canvas = self.canvas1.create_text(0,0, font="Times 20 italic bold", text=" Unknown", anchor = tkinter.NW)


    def processIncoming(self,camStatus, gpsStatus, record):
        """Handle the Status of the devices every 1 ms"""
        
        # If GPS connected
        if gpsStatus:
            self.gps_device_label.configure(text="Connected")
        else:
            self.gps_device_label.configure(text="Disconnected")
        if camStatus[0]:
            self.camera_device_label.configure(text="Connected")
            if record:
                self.canvas.delete(self.first_canvas)
                self.first_canvas = self.canvas.create_text(0,0, font="Times 20 italic bold", text=" Recording in progress, Can't show the video stream !", anchor = tkinter.NW)
        else:
            self.camera_device_label.configure(text="Disconnected")
            self.canvas.delete(self.first_canvas)
            self.first_canvas = self.canvas.create_text(0,0, font="Times 20 italic bold", text=" Camera Disconnected", anchor = tkinter.NW)

        if camStatus[2]:
            self.camera1_device_label.configure(text="Connected")
            if record:
                self.canvas1.delete(self.second_canvas)
                self.second_canvas = self.canvas1.create_text(0,0, font="Times 20 italic bold", text=" Recording in progress, Can't show the video stream !", anchor = tkinter.NW)
        else:
            self.camera1_device_label.configure(text="Disconnected")
            self.canvas1.delete(self.second_canvas)
            self.second_canvas = self.canvas1.create_text(0,0, font="Times 20 italic bold", text=" Camera Disconnected", anchor = tkinter.NW)

import tkinter
from tkinter import ttk
from tkinter import Tk, W, E, Frame
from tkinter import Button, Entry, Label, LabelFrame, StringVar
from tkinter import IntVar
from queue import Queue
import PIL.Image, PIL.ImageTk
import PIL 
from PIL import Image
from PIL import ImageTk
import cv2
import shutil




class GuiPart:
    """
    Independent  class responsible for the GUI part of the tool
    """

    def __init__(self, master, client, camStatus, gpsStatus, recordData):

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
        self.switch_state = False
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
        self.tab_parent.add(self.video_tab, text="Video Preview")
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
        self.welcome_text = tkinter.Label(self.topframe, text="Digits4RailMaps Recording Tool", font=("Arial Bold", 30))
        self.welcome_text.pack(side = tkinter.TOP)
        
    def leftFrame(self):
        self.leftframe = LabelFrame(self.recording_tab, text="Connection Status", font=("Arial Bold", 20), height=800, width=100, borderwidth=5, relief=tkinter.GROOVE)
        self.leftframe.pack(side = tkinter.LEFT, fill="both", expand="yes")
        self.leftframe.pack_propagate(False)
        self.cameraLabel()
        self.gpsLabel()

    
    def cameraLabel(self):
        # First camera Label
        self.camera_status_label = tkinter.Label(self.leftframe, text="Camera 1", font=("Arial Bold", 15), padx=15, pady=15)
        self.camera_status_label.pack(fill=tkinter.X)

        self.camera_device_label = tkinter.Label(self.leftframe, text="Unknown", font=("Arial Bold", 20),padx=5, pady=15)
        self.camera_device_label.pack(fill=tkinter.X)

        # Second camera label
        self.camera1_status_label = tkinter.Label(self.leftframe, text="Camera 2", font=("Arial Bold", 15), padx=15, pady=15)
        self.camera1_status_label.pack(fill=tkinter.X)

        self.camera1_device_label = tkinter.Label(self.leftframe, text="Unknown", font=("Arial Bold", 20),padx=5, pady=15)
        self.camera1_device_label.pack(fill=tkinter.X)


    def gpsLabel(self):
        self.gps_status_label = tkinter.Label(self.leftframe, text="GPS", font=("Arial Bold", 15), padx=15, pady=15)
        self.gps_status_label.pack(fill=tkinter.X)
        
        self.gps_device_label = tkinter.Label(self.leftframe, text="Unknown", font=("Arial Bold", 20),padx=5, pady=15)
        self.gps_device_label.pack(fill=tkinter.X)
    
    def rightFrame(self):
        self.rightframe = LabelFrame(self.recording_tab, text="Recording Tab", font=("Arial Bold", 20), height=800, width=1300, borderwidth=5, relief=tkinter.GROOVE)
        self.rightframe.pack(side = tkinter.LEFT, fill="both", expand="yes")
        self.rightframe.pack_propagate(False)
        self.rightframe.grid_columnconfigure(1, weight=1)
        self.rightframe.grid_columnconfigure(0, weight=1)
        self.recordingTitle()
        self.recordingLocation()
        self.memoryBar()
        self.systemInfo()
        self.progressBar()
        self.recordingButtons()
        self.switchButton()
        
        
        

    def recordingTitle(self):
        self.recording_label = tkinter.Label(self.rightframe, text="Recording Title", font=("Arial Bold", 20, 'bold'),padx=20, pady=15)
        self.recording_label.grid(row=0, sticky=W)
        self.title = StringVar()
        self.e = ttk.Entry(self.rightframe, textvariable=self.title, width=80, font=("Arial Bold", 15))
        self.e.grid(row=1, ipady=5, sticky=W, pady=20, padx=20, columnspan=2)


    def recordingLocation(self):
        self.location_label = tkinter.Label(self.rightframe, text="Recording Location :", font=("Arial Bold", 20,'bold'),padx=20, pady=15)
        self.location_label.grid(row=3, sticky=W)
        self.btn_record = tkinter.Button(self.rightframe, text="Browse Directory", command=self.client.browseDirectory, font=("Arial Bold", 15))
        self.btn_record.grid(row=3, column=1, sticky=W, pady=0, padx=20)
        self.location = tkinter.Label(self.rightframe, text=self.client.directory, font=("Arial Bold", 15), padx=5, pady=15)
        self.location.grid(row=4, column=0, columnspan=2, sticky=W, padx=20)



    def memoryBar(self):
        total, used, free = shutil.disk_usage("/")
        maxValue = (total // (2**30))
        currentValue = (used // (2**30))
        freeSpace = (free // (2**30))
        self.memory_bar = ttk.Progressbar(self.rightframe, orient='horizontal', length = 500, mode='determinate')
        self.memory_bar.grid(row=5, sticky=W, pady=20, padx=20)
        self.memory_bar["value"]=currentValue
        self.memory_bar["maximum"]=maxValue
        self.disk_space = tkinter.Label(self.rightframe, text="Free Space: " + str(freeSpace)+"GB", font=("Arial Bold", 15),padx=5, pady=15, width=20, height=2, anchor="e")
        self.disk_space.grid(row=5, column=1, sticky=W, columnspan=2)

    def systemInfo(self):
        self.status_label = tkinter.Label(self.rightframe, text="Recording Status : ", font=("Arial Bold", 20, 'bold'),padx=20, pady=15)
        self.status_label.grid(row=7, sticky=W)
        self.notification_label = tkinter.Label(self.rightframe, text="Ready to Record", font=("Arial Bold", 18,'bold'), fg="red",padx=5, pady=15, width=20, height=4)
        self.notification_label.grid(row=7, column=1, sticky=W, columnspan=2)


    def recordingButtons(self):
        # Start recording Button

        self.btn_record = tkinter.Button(self.rightframe, text="Record Data", command=self.client.recordData, font=("Arial Bold", 20), height=3, width=25)
        self.btn_record.grid(row=10, sticky=W, pady=20, padx=20)
        # Stop recording Button
        # self.btn_stop = tkinter.Button(self.rightframe, text="Stop recording", command=self.client.stopRecord, font=("Arial Bold", 20))
        # self.btn_stop.pack(anchor=tkinter.S, expand=True)

    
    def progressBar(self):
        self.progress_bar = ttk.Progressbar(self.rightframe, orient='horizontal', length = 500, mode='determinate')
        self.progress_bar.grid(row=11, sticky=W, pady=20, padx=20)

    def switchButton(self):
        self.switch_button = tkinter.Button(self.video_tab, text="Switch Cameras", command=self.switchCameras, font=("Arial Bold", 15))
        self.switch_button.pack(side = tkinter.TOP)
        self.topframe = Frame(self.video_tab, borderwidth=5, relief=tkinter.GROOVE)
        self.topframe.pack(side = tkinter.TOP)

    def switchCameras(self):
        if self.client.cameras_state[0] and self.client.cameras_state[2]:
            self.client.camera.label, self.client.camera1.label = self.client.camera1.label, self.client.camera.label
    
    def videoFrame(self):
        # Set up of the Right frame (Camera output)
        self.videoframe = LabelFrame(self.video_tab, text="Camera output", font=("Arial Bold", 15), height=600, width=900, borderwidth=5, relief=tkinter.GROOVE)
        self.videoframe.pack(side = tkinter.LEFT)
        self.videoframe.pack_propagate(False)

    def videoFrame1(self):
        # Set up of the left frame (Camera output 1)
        self.videoframe1 = LabelFrame(self.video_tab, text="Second Camera output", font=("Arial Bold", 15), height=600, width=900, borderwidth=5, relief=tkinter.GROOVE)
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
        
        self.location.configure(text=self.client.directory)
        total, used, free = shutil.disk_usage("/")
        self.total = (total // (2**30))
        self.used = (used // (2**30))
        self.free = (free // (2**30))
        self.memory_bar["value"]= self.used
        self.memory_bar["maximum"]= self.total
        self.disk_space.configure(text="Free Space: "+ str(self.free)+"GB")
        # If GPS connected
        if gpsStatus:
            self.gps_device_label.configure(text="Connected", bg="green")
            self.gps_status_label.configure(bg="green")
        else:
            self.gps_device_label.configure(text="Disconnected", bg="red")
            self.gps_status_label.configure(bg="red")
        if camStatus[0]:
            self.camera_device_label.configure(text="Connected", bg="green")
            self.camera_status_label.configure(bg="green")
            if record:
                self.canvas.delete(self.first_canvas)
                self.first_canvas = self.canvas.create_text(0,0, font="Times 20 italic bold", text=" Recording in progress, Can't show the video stream !", anchor = tkinter.NW)
        else:
            self.camera_status_label.configure(bg="red")
            self.camera_device_label.configure(text="Disconnected", bg="red")
            self.canvas.delete(self.first_canvas)
            self.first_canvas = self.canvas.create_text(0,0, font="Times 20 italic bold", text=" Camera Disconnected", anchor = tkinter.NW)

        if camStatus[2]:
            self.camera1_device_label.configure(text="Connected", bg="green")
            self.camera1_status_label.configure(bg="green")
            if record:
                self.canvas1.delete(self.second_canvas)
                self.second_canvas = self.canvas1.create_text(0,0, font="Times 20 italic bold", text=" Recording in progress, Can't show the video stream !", anchor = tkinter.NW)
        else:
            self.camera1_status_label.configure(bg="red")
            self.camera1_device_label.configure(text="Disconnected", bg="red")
            self.canvas1.delete(self.second_canvas)
            self.second_canvas = self.canvas1.create_text(0,0, font="Times 20 italic bold", text=" Camera Disconnected", anchor = tkinter.NW)

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
        #self.progressBar()
        
        


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
        self.videoframe = LabelFrame(self.video_tab, text="Camera output", font=("Arial Bold", 15), height=self.frame_height, width=self.frame_width,borderwidth=5, relief=tkinter.GROOVE)
        self.videoframe.pack(side = tkinter.RIGHT)
        self.videoframe.pack_propagate(False)
        # Set up of the left frame (Camera output 1)
        self.videoframe1 = LabelFrame(self.video_tab, text="Second Camera output", font=("Arial Bold", 15), height=self.frame_height, width=self.frame_width,borderwidth=5, relief=tkinter.GROOVE)
        self.videoframe1.pack(side = tkinter.RIGHT)
        self.videoframe1.pack_propagate(False)
    
    
    def framesCanvas(self):
        # Set of the canvas comporting the camera output frames
        self.canvas = tkinter.Canvas(self.videoframe, width = self.frame_width, height = self.frame_height, highlightcolor = "red", bd=5)
        self.canvas.pack(anchor=tkinter.CENTER)
        self.first_canvas = self.canvas.create_text(0,0, font="Times 20 italic bold", text="  Camera Not Connected !", anchor = tkinter.NW)

        # Set of the canvas comporting the second camera output frames
        self.canvas1 = tkinter.Canvas(self.videoframe1, width = self.frame1_width, height = self.frame1_height, highlightcolor = "red", bd=5)
        self.canvas1.pack(anchor=tkinter.CENTER)
        self.second_canvas = self.canvas1.create_text(0,0, font="Times 20 italic bold", text="  Camera Not Connected !", anchor = tkinter.NW)


    def processIncoming(self,camStatus, gpsStatus, videoOutput, frame, frame1):
        """Handle the Status of the devices every 1 ms"""
        
        # If GPS connected
        if gpsStatus:
            self.gps_device_label.configure(text="Connected")
        else:
            self.gps_device_label.configure(text="Disconnected")
        
        # # if Both cameras are disconnected
        # if not camStatus[0] and not camStatus[2]:
        #     self.notification_label.configure(text="Both cameras are disconnected !", fg="red")
        
        # # if one of the cameras is disconnected
        # if not camStatus[0] or not camStatus[2]:
        #     self.notification_label.configure(text="One of the cameras is disconnected !", fg="red")


        # If First Camera connected
        if camStatus[0]:
            self.camera_device_label.configure(text="Connected")
            if videoOutput:
                if frame is not None:
                    self.notification_label.configure(text="No Recording in Procces, Press the record button to start recording")
                    self.photo = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.photo)) # Transform the frame into PIL image
                    self.img = self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW) # Display the image into the canvas GUI
                    #self.canvas.itemconfigure(self.first_canvas, image=self.photo)
            else:
                self.canvas.itemconfigure(self.first_canvas, text="  Can't show the video, recording in process.")
                self.notification_label.configure(text="Recording in Procces")

        else:
            self.camera_device_label.configure(text="Disconnected")
            self.canvas.itemconfigure(self.first_canvas, text=" Camera Not Connected !")
        
        # If second camera connected
        if camStatus[2]:
            self.camera1_device_label.configure(text="Connected")
            if videoOutput:
                if frame1 is not None:
                    self.notification_label.configure(text="No Recording in Procces, Press the record button to start recording")
                    self.photo1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                    self.photo1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.photo1)) # Transform the frame into PIL image
                    self.img1 = self.canvas1.create_image(0, 0, image = self.photo1, anchor = tkinter.NW) # Display the image into the canvas GUI
                    #self.canvas1.itemconfigure(self.first_canvas, image=self.photo1)
            else:
                self.canvas1.itemconfigure(self.second_canvas, text="  Can't show the video, recording in process.")
                self.notification_label.configure(text="Recording in Procces")

        else:
            self.camera1_device_label.configure(text="Disconnected")
            self.canvas1.itemconfigure(self.second_canvas, font="Times 20 italic bold", text=" Camera Not Connected !")

        # # If both cameras are disconnected
        # if not camStatus[0] or not camStatus[2]:
        #     if not camStatus[0] and not camStatus[2]:
        #         self.notification_label.configure(text="Both cameras are disconnected ! Connect the cameras and restart the Application please", fg="red")
        #     else:
        #         self.notification_label.configure(text="One of the cameras is disconnected ! Connect the camera and restart the Application please", fg="red")
        
        # # If Both cameras are connected
        # else:
        #     # If there is no recording show the videos in the tool
        #     if videoOutput:
        #         if frame is not None:
        #             self.notification_label.configure(text="No Recording in Procces, Press the record button to start recording")
        #             self.photo = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #             self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.photo)) # Transform the frame into PIL image
        #             #self.img = self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW) # Display the image into the canvas GUI
        #             self.canvas.itemconfigure(self.first_canvas, image=self.photo)
        #         if frame1 is not None:
        #             self.notification_label.configure(text="No Recording in Procces, Press the record button to start recording")
        #             self.photo1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        #             self.photo1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.photo1)) # Transform the frame into PIL image
        #             #self.img1 = self.canvas1.create_image(0, 0, image = self.photo1, anchor = tkinter.NW) # Display the image into the canvas GUI
        #             self.canvas1.itemconfigure(self.first_canvas, image=self.photo1)
        #     # Hide the videos if there is recording
        #     else:
        #         #self.canvas.create_text(0,0, font="Times 20 italic bold", text="  Can't show the video, recording in process.", anchor = tkinter.NW)
        #         self.canvas.itemconfigure(self.first_canvas, text="  Can't show the video, recording in process.")
        #         self.notification_label.configure(text="Recording in Procces")
        #         #self.canvas1.create_text(0,0, font="Times 20 italic bold", text="  Can't show the video, recording in process.", anchor = tkinter.NW)
        #         self.canvas1.itemconfigure(self.second_canvas, text="  Can't show the video, recording in process.")


import threading
import cv2
import time
import datetime
import io
import numpy as np
from FPS import FPS
import PIL.Image, PIL.ImageTk
import PIL 
from PIL import Image
from PIL import ImageTk
import tkinter

class CamPollingThreadController:
	"""Separate Thread Class responsible of the files recording
	"""
	def __init__(self, client, cam, gui):
		"""Constructor
		
		Arguments:
			videoDirectory {str} -- Path to the directory containing the videos and the csv files of the frames.
			gui {GuiPart} -- GUI object to configure the Graphical user interface of the App.
		"""
		self.client = client
		self.cam = cam
		self.gui = gui
		self.display_thread = None
		self.stop_display_thread = threading.Event()
		self.f = None


	
	def displayFrames(self):
		while not self.stop_display_thread.is_set():
			ret, frame = self.cam.read()
			if np.array_equal(self.f, frame):
				continue
			self.f = frame
			self.photo = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.photo)) # Transform the frame into PIL image
			self.img = self.gui.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW) # Display the image into the canvas GUI

	def start(self):
		"""Function to start the recording thread
		"""
		self.stop_display_thread.clear()
		self.display_thread = threading.Thread(target=self.displayFrames, args=())
		self.display_thread.setDaemon(True)
		self.display_thread.start()
		
	def stop(self):
		"""Function to sto the recording thread
		"""
		self.stop_display_thread.set()
		self.display_thread.join(4)
		self.display_thread = None

	def isAlive(self):
		"""Function to check if the thread is still alive
		
		Returns:
			[bool] -- Thread running: True, Thread stopped: False
		"""
		return self.display_thread.isAlive()



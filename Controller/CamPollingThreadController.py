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
from FPS import FPS
import imutils


class CamPollingThreadController:
	"""Separate Thread Class responsible of the files recording
	"""
	def __init__(self, client, cam, gui, label):
		"""Constructor
		
		Arguments:
			videoDirectory {str} -- Path to the directory containing the videos and the csv files of the frames.
			gui {GuiPart} -- GUI object to configure the Graphical user interface of the App.
		"""
		self.client = client
		self.cam = cam
		self.gui = gui
		self.label = label
		self.display_thread = None
		self.stop_display_thread = threading.Event()
		self.f = None
	
	def displayFrames(self):
		while not self.stop_display_thread.is_set() and not self.client.exitFlag:
			ret, frame = self.cam.read()
			if np.array_equal(self.f, frame) and frame is None:
				continue
			self.f = frame
			if frame is None:
				print("frame none")
			self.photo = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.photo)) # Transform the frame into PIL image
			if self.label == 1:
				self.gui.videoframe1.configure(image=self.photo)
				self.gui.videoframe1.image = self.photo
			if self.label == 2:
				self.gui.videoframe2.configure(image=self.photo)
				self.gui.videoframe2.image = self.photo
				

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
		self.display_thread.join(0.1)
		self.display_thread = None
	def isAlive(self):
		"""Function to check if the thread is still alive
		
		Returns:
			[bool] -- Thread running: True, Thread stopped: False
		"""
		return self.display_thread.isAlive()



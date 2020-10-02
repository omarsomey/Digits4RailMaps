import threading
import cv2
import time
import datetime
import io
import numpy as np
import tkinter
import imutils
import PIL 
from FPS import FPS


class CamPollingThreadController:
	"""Separate Thread Class responsible for polling the frames from the cameras
	"""
	def __init__(self, client, cam, gui):
		"""Constructor

		Args:
			client ([Tk]): [Tki client]
			cam ([See3Cam]): [camera object]
			gui ([GuiPart]): [GUI object]
		"""
		self.client = client
		self.cam = cam
		self.gui = gui
		self.display_thread = None
		self.stop_display_thread = threading.Event()
		self.f = None
		self.fps = FPS()
	
	def displayFrames(self):
		"""This function is displaying the frames into the canvas inside the GUI
		"""

		self.gui.canvas.delete(self.gui.first_canvas)   # Remove last picture in the first canvas
		self.gui.canvas1.delete(self.gui.second_canvas) # Remove last picture in the second canvas
		self.fps.start()
		start = time.time()
		while not self.stop_display_thread.is_set() and not self.client.exitFlag:
			ret, frame = self.cam.read()				# Read frame from the camera
			if np.array_equal(self.f, frame):
				continue
			self.fps.update()
			self.f = frame
			currentTime = time.time()
			if (currentTime-start)>=10:
				self.fps.stop()
				print("[INFO] elapsed time: {:.2f}".format(self.fps.elapsed()))
				print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
				start = time.time()
				self.fps.start()
			self.photo = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # change color spaces from BGR to RGB
			scale = 70
			w = int(frame.shape[1]*scale / 100) 		# Get new width of the scaled frane
			h = int(frame.shape[0]*scale / 100)			# Get new height of the scaled frame
			self.photo = cv2.resize(self.photo, (w ,h), interpolation=cv2.INTER_AREA) # Req 132: Rescaling of the frames to new dimensions
			self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(self.photo))

			if self.cam.label == "1": 
				self.gui.first_canvas = self.gui.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
				self.gui.videoframe.image = self.photo
			if self.cam.label == "2":
				self.gui.second_canvas = self.gui.canvas1.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
				self.gui.videoframe1.image = self.photo
					
				

				

	def start(self):
		"""Function to start the polling thread
		"""
		self.stop_display_thread.clear()
		self.display_thread = threading.Thread(target=self.displayFrames, args=())
		self.display_thread.setDaemon(True)
		self.display_thread.start()
		
	def stop(self):
		"""Function to sto the polling thread
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



import threading
import cv2
import time
import datetime
import io
import numpy as np
from jproperties import Properties
from FPS import FPS

class CamThreadController:
	"""Separate Thread Class responsible of the files recording
	"""
	def __init__(self, client, cam, name, gui):
		"""Constructor
		
		Arguments:
			videoDirectory {str} -- Path to the directory containing the videos and the csv files of the frames.
			gui {GuiPart} -- GUI object to configure the Graphical user interface of the App.
		"""
		self.client = client
		self.cam = cam
		self.name = name
		self.duration = 10
		self.gui = gui
		self.video_handler = cv2.VideoWriter()
		self.record_thread = None
		self.stop_record_thread = threading.Event()
		self.fourcc_codec = cv2.VideoWriter_fourcc(*'MJPG')#XVID
		self.f = None
		self.fps = FPS()

	def getNewFiles(self, videoDirectory, id, name):
		"""This Function is a generator of the new files names caller each 15 minutes
		
		Arguments:
			videoDirectory {str} -- Path to the directory containing the csv files of the GPS track log.
			id {str} -- new id for each file. 
		
		Returns:
			[str] -- frames file name.
			[str] -- video file name.
		"""

		frames_filename = videoDirectory + "track_frames_" + self.name +"_"+ id +"_"+ time.strftime("%d-%m-%Y-%H-%M-%S") + ".csv"
		self.frames_recorder = open(frames_filename, 'a')
		self.frames_recorder.write("frames_id,frames_timestamp \n")
		self.frames_recorder.close()
		video_filename = videoDirectory + "track_video_"+ self.name +"_" + id +"_" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".avi"
		self.video_handler.open(video_filename, self.fourcc_codec, 28, (self.client.camera.width,self.client.camera.height))
		return  frames_filename, video_filename

	def openfiles(self, frames_filename):
		"""This function open the files
		
		Arguments:
			frames_filename {str} -- File name of the frames csv file.
			video_filename {str} -- File name of the video.
		"""
		self.frames_recorder = open(frames_filename, 'a')

	def write(self, videoHandler, frame, framesHandler, frame_id):
		""" This function write the data into the corresponding directories
		
		Arguments:
			videoHandler {str} -- Video file handler to write the video.
			framesHandler {str} -- frames file handler to write the csv file.
			frame_id {integer} -- The id of each frame from the camera. 
		"""
		
		framesHandler.write(str(frame_id)+","+str(datetime.datetime.utcnow())+"\n")
		videoHandler.write(frame)
		framesHandler.close()
	
	def record(self, properties, path):
		"""This function is the main thread 
		"""
		self.fps.start()
		start = time.time()
		id = self.getId(properties)
		frame_id = 0
		frames_filename, video_filename = self.getNewFiles(path, id, self.cam)
		while  not self.stop_record_thread.is_set():
			ret, frame = self.cam.read()
			if np.array_equal(self.f, frame):
				continue
			self.fps.update()
			self.f = frame
			currentTime = time.time()
			if(int(currentTime-start) >= self.duration):
				self.fps.stop()
				print("[INFO] elapsed time: {:.2f}".format(self.fps.elapsed()))
				print("[INFO] approx. FPS: {:.2f}".format(self.fps.fps()))
				id = self.getId(properties)
				frames_filename, video_filename = self.getNewFiles(path, id, self.name)
				frame_id = 0
				start = time.time()
				self.fps.start()
			self.openfiles(frames_filename)
			self.write(self.video_handler, frame, self.frames_recorder, frame_id)
			frame_id = frame_id +1
		self.video_handler.release()
			
	def start(self, properties, path):
		"""Function to start the recording thread
		"""
		self.stop_record_thread.clear()
		self.record_thread = threading.Thread(target=self.record, args=(properties, path,))
		self.record_thread.setDaemon(True)
		self.record_thread.start()
		
	def stop(self):
		"""Function to sto the recording thread
		"""
		self.stop_record_thread.set()
		self.record_thread.join(4)
		self.record_thread = None
		self.fps.stop()

	def isAlive(self):
		"""Function to check if the thread is still alive
		
		Returns:
			[bool] -- Thread running: True, Thread stopped: False
		"""
		return self.record_thread.isAlive()

	def getId(self, properties):
		"""Function to get a new ID each time a file is created
		
		Returns:
			[integer] -- ID
		"""
		# Read last availaible id 
		p = Properties()
		with open(properties, 'rb') as f:
			p.load(f, 'utf-8')
		id = str(int(p["video_id"].data))
		# Increment the id in the file
		p["video_id"]=str(int(p["video_id"].data) +1)
		with open(properties, 'wb') as f:
			p.store(f, encoding="utf-8")

		# Return availaible id
		return id

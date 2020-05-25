import threading
import time
import datetime
import io
import numpy as np
from jproperties import Properties

class GpsThreadController:
	"""Separate Thread Class responsible of the files recording
	"""
	def __init__(self, client, gps, properties, gui):
		"""Constructor
		
		Arguments:
			videoDirectory {str} -- Path to the directory containing the videos and the csv files of the frames.
			gui {GuiPart} -- GUI object to configure the Graphical user interface of the App.
		"""
		self.client = client
		self.gps = gps
		self.properties = properties
		self.gui = gui
		self.properties_path = self.properties['properties-path']
		self.gps_path = self.properties['gps-path']
		self.gps_id = self.properties['gps-id']
		self.duration = self.properties['duration']
		self.record_thread = None
		self.stop_record_thread = threading.Event()

	def getNewFiles(self, gpsDirectory, id):
		"""This Function is a generator of the new files names caller each 15 minutes
		
		Arguments:
			videoDirectory {str} -- Path to the directory containing the csv files of the GPS track log.
			id {str} -- new id for each file. 
		
		Returns:
			[str] -- frames file name.
			[str] -- video file name.
		"""
		gps_filename = gpsDirectory + "track_gps_" + id + "_" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".csv"
		self.gps_recorder = open(gps_filename, 'a')
		self.gps_recorder.write("sentence_identifier,time,latitude,latitude_direction,longitude,longitude_direction,quality,hdop,altitude,altitude_unit,undulation,u_unit,age,checksum,timestamp,frames_id\n")
		self.gps_recorder.close()
		return  gps_filename

	def openfiles(self, gps_filename):
		"""This function open the files
		
		Arguments:
			frames_filename {str} -- File name of the frames csv file.
			video_filename {str} -- File name of the video.
		"""
		self.gps_recorder = open(gps_filename, 'a')

	def write(self, gpsHandler, gps, frame_id):
		""" This function write the data into the corresponding directories
		
		Arguments:
			videoHandler {str} -- Video file handler to write the video.
			framesHandler {str} -- frames file handler to write the csv file.
			frame_id {integer} -- The id of each frame from the camera. 
		"""
		
		gpsHandler.write(gps.sentence_identifier+","+ gps.g_time +","+ gps.latitude +","+ gps.latitude_direction +"," + gps.longitude +","+ gps.longitude_direction +","+ gps.quality +","+ gps.hdop +","+ gps.altitude +","+ gps.altitude_unit +","+ gps.undulation +","+ gps.u_unit +","+ gps.age +","+ gps.checksum +","+ str(datetime.datetime.utcnow())+","+str(frame_id)+" \n")
		gpsHandler.close()

	def record(self):
		"""This function is the main thread 
		"""
		start = time.time()
		id = self.getId()
		frame_id = 0
		gps_filename = self.getNewFiles(self.gps_path, id)
		while  not self.stop_record_thread.is_set() and not self.client.exitFlag:
			self.gpsSentence = self.gps.read()
			currentTime = time.time()
			if(int(currentTime-start) >= int(self.duration)):
				id = self.getId()
				gps_filename = self.getNewFiles(self.gps_path, id)
				frame_id = 0
				start = time.time()
			self.openfiles(gps_filename)
			self.write(self.gps_recorder, self.gps, frame_id)
			frame_id = frame_id +1
			
	def start(self):
		"""Function to start the recording thread
		"""
		self.stop_record_thread.clear()
		self.record_thread = threading.Thread(target=self.record, args=())
		self.record_thread.setDaemon(True)
		self.record_thread.start()
		
	def stop(self):
		"""Function to sto the recording thread
		"""
		self.stop_record_thread.set()
		self.record_thread.join(4)
		self.record_thread = None

	def isAlive(self):
		"""Function to check if the thread is still alive
		
		Returns:
			[bool] -- Thread running: True, Thread stopped: False
		"""
		return self.record_thread.isAlive()

	def getId(self):
		"""Function to get a new ID each time a file is created
		
		Returns:
			[integer] -- ID
		"""
		# Read last availaible id 
		p = Properties()
		with open(self.properties_path, 'rb') as f:
			p.load(f, 'utf-8')
		id = str(int(p["gps-id"].data))
		# Increment the id in the file
		p["gps-id"]=str(int(p["gps-id"].data) +1)
		with open(self.properties_path, 'wb') as f:
			p.store(f, encoding="utf-8")

		# Return availaible id
		return id

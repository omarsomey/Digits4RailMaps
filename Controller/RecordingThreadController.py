import threading
import cv2
import time
import datetime
import io
import numpy as np

class RecordingThreadController:
	"""Separate Thread Class responsible of the files recording
	"""
	def __init__(self, client, videoDirectory, gpsDirectory, gui):
		"""Constructor
		
		Arguments:
			gps {GpsCapture} -- GpsCapture object
			frame {Queue} -- Queue containing the frames to record
			videoDirectory {str} -- Path to the directory containing the videos and the csv files of the frames.
			gpsDirectory {str} -- Path to the directory containing the csv files of the GPS track log.
			gui {GuiPart} -- GUI object to configure the Graphical user interface of the App.
		"""
		self.client = client
		self.videoDirectory = videoDirectory
		self.gpsDirectory = gpsDirectory
		self.gui = gui
		self.video_handler = cv2.VideoWriter()
		self.video1_handler = cv2.VideoWriter()
		self.duration = 10
		self.record_thread = None
		self.stop_record_thread = threading.Event()
		self.fourcc_codec = cv2.VideoWriter_fourcc(*'MJPG')#XVID

	def getNewFiles(self, gpsDirectory, videoDirectory, id):
		"""This Function is a generator of the new files names caller each 15 minutes
		
		Arguments:
			gpsDirectory {str} -- Path to the directory containing the videos and the csv files of the frames. 
			videoDirectory {str} -- Path to the directory containing the csv files of the GPS track log.
			id {str} -- new id for each file. 
		
		Returns:
			[str] -- gps file name.
			[str] -- frames file name.
			[str] -- video file name.
		"""

		gps_filename = gpsDirectory + "track_gps_" + id + "_" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".csv"
		frames_filename = videoDirectory + "track_frames_" + id +"_"+ time.strftime("%d-%m-%Y-%H-%M-%S") + ".csv"
		self.gps_recorder = open(gps_filename, 'a')
		self.frames_recorder = open(frames_filename, 'a')
		self.gps_recorder.write("sentence_identifier,time,latitude,latitude_direction,longitude,longitude_direction,quality,hdop,altitude,altitude_unit,undulation,u_unit,age,checksum,timestamp,frames_id\n")
		self.frames_recorder.write("frames_id,frames_timestamp \n")
		self.gps_recorder.close()
		self.frames_recorder.close()
		video_filename = videoDirectory + "track_video_pos1_" + id +"_" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".avi"
		video1_filename = videoDirectory + "track_video_pos2_" + id +"_" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".avi"
		self.video_handler.open(video_filename, self.fourcc_codec, 28, (self.client.camera.width,self.client.camera.height))
		self.video1_handler.open(video1_filename, self.fourcc_codec, 28, (self.client.camera.width,self.client.camera.height))
		return gps_filename, frames_filename, video_filename, video1_filename

	def openfiles(self, gps_filename, frames_filename, video_filename):
		"""This function open the files
		
		Arguments:
			gps_filename {str} -- File name of the GPS track log (csv). 
			frames_filename {str} -- File name of the frames csv file.
			video_filename {str} -- File name of the video.
		"""
		self.gps_recorder = open(gps_filename, 'a')
		self.frames_recorder = open(frames_filename, 'a')

	def write(self, videoHandler, videoHandler1, gpsHandler, framesHandler, gps, frame, frame1, frame_id):
		""" This function write the data into the corresponding directories
		
		Arguments:
			videoHandler {str} -- Video file handler to write the video.
			gpsHandler {str} -- Gps file handler to write the csv file. 
			framesHandler {str} -- frames file handler to write the csv file.
			gps {GpsCapture} -- GpsCapture object to access the Gps system.
			frame {src Image(Mat)} -- The written frame from the source camera.
			frame_id {integer} -- The id of each frame from the camera. 
		"""
		ret , frame = self.client.camera.read()
		ret1, frame1 = self.client.camera1.read()
		gpsHandler.write(gps.sentence_identifier+","+ gps.g_time +","+ gps.latitude +","+ gps.latitude_direction +"," + gps.longitude +","+ gps.longitude_direction +","+ gps.quality +","+ gps.hdop +","+ gps.altitude +","+ gps.altitude_unit +","+ gps.undulation +","+ gps.u_unit +","+ gps.age +","+ gps.checksum +","+ str(datetime.datetime.utcnow())+","+str(frame_id)+" \n")
		framesHandler.write(str(frame_id)+","+str(datetime.datetime.utcnow())+"\n")
		videoHandler.write(frame)
		videoHandler1.write(frame1)
		gpsHandler.close()
		framesHandler.close()
	
	def record(self):
		"""This function is the main thread 
		"""
		start = time.time()
		id = self.getId()
		frame_id = 0
		self.old_frame = self.client.frame
		self.old_frame1 = self.client.frame1
		gps_filename, frames_filename, video_filename, video1_filename = self.getNewFiles(self.gpsDirectory, self.videoDirectory,id)
		while  not self.stop_record_thread.is_set():
			# if np.array_equal(self.client.frame, self.old_frame):
			# 	continue
			# if np.array_equal(self.client.frame1, self.old_frame):
			# 	continue
			self.old_frame = self.client.frame
			self.old_frame1 = self.client.frame1
			currentTime = time.time()
			if(int(currentTime-start) >= self.duration):
				id = self.getId()
				gps_filename, frames_filename, video_filename, video1_filename = self.getNewFiles(self.gpsDirectory, self.videoDirectory, id)
				frame_id = 0
				start = time.time()
			
			self.openfiles(gps_filename, frames_filename, video_filename)
			self.write(self.video_handler, self.video1_handler, self.gps_recorder, self.frames_recorder, self.client.gps, self.client.frame, self.client.frame1, frame_id)
			frame_id = frame_id +1
		self.video_handler.release()
		self.video1_handler.release()
			
	def start(self):
		"""Function to start the recording thread
		"""
		self.stop_record_thread.clear()
		self.record_thread = threading.Thread(target=self.record)
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
		f= open("available_id.txt")
		id = f.read()
		f.close()
		# Increment the id in the file
		f= open("available_id.txt","w")
		f.write(str(int(id)+1))
		# Return availaible id
		return id

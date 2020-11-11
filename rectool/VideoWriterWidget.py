from threading import Thread, Event
import threading
import cv2
import time
from FPS import FPS
import subprocess
from subprocess import PIPE
import numpy as np


class VideoWriterWidget(object):
    def __init__(self, video_file_name, src=0):
        # Create a VideoCapture object
        self.frame_name = str(src) # if using webcams, else just use src as it is.
        self.video_file = video_file_name
        self.video_file_name = video_file_name + '.avi'
        self.capture = cv2.VideoCapture(src)
        self.capture.set(3, 1920)
        self.capture.set(4,1080)
        self.count = 0
        self.count1 = 0
        self.f = None
        self.stop_record_thread = threading.Event()

        # Default resolutions of the frame are obtained (system dependent)
        self.frame_width = int(self.capture.get(3))
        self.frame_height = int(self.capture.get(4))

        # Set up codec and output video settings
        self.codec = cv2.VideoWriter_fourcc('M','J','P','G')
        self.output_video = cv2.VideoWriter(self.video_file_name, self.codec, 27, (self.frame_width, self.frame_height))

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        self.fps = FPS()

        # Start another thread to save frames
        print('initialized {}'.format(self.video_file))

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
                self.fps.update()
                self.count += 1


    def save_frame(self):
        # Save obtained frame into video output file
        self.output_video.write(self.frame)
        self.count1 +=1

    def start_recording(self):
        # Create another thread to show/save frames
        def start_recording_thread():
            self.fps.start()
            while self.stop_record_thread.is_set():
                try:
                    self.save_frame()
                    self.f = self.frame
                except AttributeError:
                    pass
        self.stop_record_thread.set()
        self.recording_thread = Thread(target=start_recording_thread, args=())
        self.recording_thread.daemon = True
        self.recording_thread.start()


    def stop_recording(self):
        """Function to sto the recording thread
		"""
        self.stop_record_thread.clear()
        try:
            self.fps.stop()
            self.recording_thread.join(0.1)
            print("Recording stopped")
        except AttributeError:
            print("Attribute Error: thread already killed")

        self.recording_thread = None
        self.capture.release()
        self.output_video.release()


if __name__ == '__main__':

    def find_cam():
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


    start = time.time()
    src1 = find_cam()[1]
    video_writer_widget1 = VideoWriterWidget('Camera 1', src1)
    src3 = find_cam()[3]
    video_writer_widget3 = VideoWriterWidget('Camera 3', src3)

    # Since each video player is in its own thread, we need to keep the main thread alive.
    # Keep spinning using time.sleep() so the background threads keep running
    # Threads are set to daemon=True so they will automatically die
    # when the main thread dies
    currentTime = time.time()
    video_writer_widget1.start_recording()
    video_writer_widget3.start_recording()
    while currentTime-start <= 1000:
        currentTime = time.time()
    video_writer_widget1.stop_recording()
    video_writer_widget3.stop_recording()

    print(src1, "  ", video_writer_widget1.count)
    print(src1, "  ", video_writer_widget1.count1)
    print(src3, "  ", video_writer_widget3.count)
    print(src3, "  ", video_writer_widget3.count1)
    print("[INFO] elapsed time: {:.2f}".format(video_writer_widget1.fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(video_writer_widget1.fps.fps()))
    print("[INFO] elapsed time: {:.2f}".format(video_writer_widget3.fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(video_writer_widget3.fps.fps()))

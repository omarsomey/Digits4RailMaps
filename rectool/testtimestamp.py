import cv2
import numpy as np
import time
from See3Cam import See3Cam

# Create a VideoCapture object
cap = See3Cam(src=0, width=1280, height=720, framerate=30, name="cam", label="1")
cap.start()

# Check if camera opened successfully
# if (cap.isRunning() == False): 
#   print("Unable to read camera feed")

# Default resolutions of the frame are obtained.The default resolutions are system dependent.
# We convert the resolutions from float to integer.
frame_width = 1920
frame_height = 1080
a= 0
c = 0
f = None
# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('X','V','I','D'), 30, (frame_width,frame_height))

while(True):
  ret, frame = cap.read()
  if np.array_equal(f, frame):
    continue
  f = frame
  # Write the frame into the file 'output.avi'
  b = time.time()-a
  print(b)
  print("DIF = ", (b-c)*1000)
  c = b
  a = time.time()
  out.write(frame)
    

# When everything done, release the video capture and video write objects
cap.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows() 
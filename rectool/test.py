from See3Cam import See3Cam
import subprocess
from subprocess import PIPE
import time
import cv2
from FPS import FPS
import numpy as np

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
        


def main():
    fps = FPS()
    fps1= FPS()
    print(find_cam())
    cam = See3Cam(src=find_cam()[1], width=1920, height=1080, framerate=30, name="cam", label="1")
    cam.start()
    cam1 = See3Cam(src=find_cam()[3], width=1920, height=1080, framerate=30, name="cam", label="2")
    cam1.start()
    time.sleep(2)
    disc = False
    start = time.time()
    fps.start()
    fps1.start()
    f = None
    f1 = None

    out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 28, (1920,1080))
    out1 = cv2.VideoWriter('outpy1.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 28, (1920,1080))


    while True:
        ret, frame = cam.read()
        if ret: 
            if not np.array_equal(f, frame):
                fps.update()
        ret1, frame1 = cam1.read()
        if ret1:
            if not np.array_equal(f1, frame1):
                fps1.update()
        f = frame
        f1 = frame1
        currentTime = time.time()
        if (currentTime-start) >= 10 :
            fps.stop()
            fps1.stop()
            print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
            print("[INFO] elapsed time: {:.2f}".format(fps1.elapsed()))
            print("[INFO] approx. FPS: {:.2f}".format(fps1.fps()))
            start = time.time()
            fps.start()
            fps1.start()
        out.write(frame)
        out1.write(frame1)
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            break
        
    out.release()
    out1.release()
    cam.stop()
    cam1.stop()


        # if not find_cam()[0]:
        #     cam = None
        #     disc= True
        #     continue   
        # if find_cam()[0] and disc:
        #     cam = See3Cam(src=find_cam()[1], width=1920, height=1080, framerate=30, name="cam", label="1")
        #     cam.start()
        #     disc = False
        # f = cam.read()

        # cv2.imshow('preview',f)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break







if __name__ == "__main__":
    main()
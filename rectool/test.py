from See3Cam import See3Cam
import subprocess
from subprocess import PIPE
import time
import cv2

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
    print(find_cam())
    cam = See3Cam(src=find_cam()[1], width=1920, height=1080, framerate=30, name="cam", label="1")
    cam.start()
    disc = False
    while True:
        if not find_cam()[0]:
            cam = None
            disc= True
            continue
        if find_cam()[0] and disc:
            cam = See3Cam(src=find_cam()[1], width=1920, height=1080, framerate=30, name="cam", label="1")
            cam.start()
            disc = False
        f = cam.read()

        cv2.imshow('preview',f)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break







if __name__ == "__main__":
    main()
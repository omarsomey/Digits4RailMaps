import subprocess
import serial
import os
from subprocess import PIPE

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
        



def find_gps():
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        for t in myports:
            if '/dev/ttyUSB0' in t:
                gpsport = t[0]
                return(True, gpsport)

        return (False, None)

        

def find_hd():
    if not os.listdir("/media/knorr-bremse"):
        return False
    else:
        return True
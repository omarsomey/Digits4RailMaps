from GpsCapture import GpsCapture
import time
import serial
import serial.tools.list_ports


myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]

for t in myports:
    print(t)
    if '/dev/ttyUSB0' in t:
        gpsport = t[0]
        print("True", gpsport)




gps = GpsCapture()
gps.start()
while True:
    gps.read()
    print(gps.gpsSentence)
    time.sleep(0.2)
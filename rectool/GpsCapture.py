import serial
import serial.tools.list_ports
from threading import Thread


class GpsCapture:

    global gpsport

    def __init__(self):
        """Constructor of the GpsCapture class
        """
        self.running = False
        self.isConnected = self.get_port()[0]
        self.sentence_identifier = ""
        self.baudrate = 9600
        self.gpsSentence = ""
        self.g_time = ""
        self.hdop = ""
        self.latitude = ""
        self.latitude_direction = ""
        self.longitude = ""
        self.longitude_direction = ""
        self.quality = ""
        self.timestamp = ""
        self.quality = ""
        self.u_unit = ""
        self.undulation = ""
        self.altitude_unit = ""
        self.altitude = ""
        self.age = ""
        self.checksum = ""
        self.open_gps(self.get_port()[1], self.baudrate)
        self.stopped = False

    def get_port(self):
        """ This function get the different ports of the laptop,
        and check if the gps is connected.
        
        Returns:
            bool -- True : Gps connected, False : Gps not connected
            str -- The port of the connected gps
        """
        global gpsport
        
        myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]

        for t in myports:
            if '/dev/ttyUSB0' in t:
                gpsport = t[0]
                self.isConnected = True
                return(True, gpsport)

        self.isConnected= False
        return (False, None)



    def open_gps(self, port, baudrate):
        """ This function open the Gps.
        
        Arguments:
            port {str} -- the specific port of the connection
            baudrate {integer} -- Baudrate of the connection
        """
        if self.isConnected:
            try:
                self.ser = serial.Serial(port= port,baudrate=baudrate,parity=serial.PARITY_ODD,stopbits=serial.STOPBITS_TWO,bytesize=serial.SEVENBITS)
                self.running = True
            except:
                print("There was a Problem opening the GPS device")
                self.running = False
        else:
            self.running = False

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            try:
                self.gpsSentence = self.ser.readline()
                self.split(self.gpsSentence)
            except:
                print("Cannot read the GPS")


    def split(self, gpsSentence):
        """This function read he differents values of the gps.
        """
        stringSplit = str(self.gpsSentence).split(',')
        if stringSplit[0] == "b\'$GNGGA":
            self.sentence_identifier = stringSplit[0]
            self.g_time              = stringSplit[1]
            self.latitude            = stringSplit[2]
            self.latitude_direction  = stringSplit[3]
            self.longitude           = stringSplit[4]
            self.longitude_direction = stringSplit[5]
            self.quality             = stringSplit[6]
            self.hdop                = stringSplit[7]
            self.altitude            = stringSplit[8]
            self.altitude_unit       = stringSplit[9]
            self.undulation          = stringSplit[10]  
            self.u_unit              = stringSplit[11]
            self.age                 = stringSplit[12]
            self.checksum            = stringSplit[13]
            self.timestamp           = stringSplit[14]


    def read(self):
        return self.gpsSentence
    

    def stop(self):
        """This function stops the Gps 
        """
        self.stopped = True
        self.running = False
        print("Gps stopped")
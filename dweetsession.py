
import time
import dweepy
import serial
import requests
from configparser import ConfigParser

class DweetSession(object):

    def __init__(self, thingId, key, pcBuffer, deviceBuffer, port, mode):
        self.thingId = thingId
        self.key = key
        self.port = port
        self.mode = mode
        self.session = requests.Session()
        self.serial_port = serial.Serial(port)
        if mode == 'DTE':          # in DTE (pc) mode look for dweets in the device buffer, write dweets to the PC buffer
            self.thisBuffer = pcBuffer
            self.thatBuffer = deviceBuffer
        
        elif mode == 'DCE':        # in DCE (device) mode look for dweets in the PC buffer, write dweets to the device buffer
            self.thisBuffer = deviceBuffer
            self.thatBuffer = pcBuffer
        
    @classmethod
    def from_config_file(cls, configFile, port, mode):
        # open our config file
        cfg = ConfigParser()
        cfg.read(configFile)
        
        # get thing ID from config file 
        thingId = cfg.get("thing", "id")
        thingKey = cfg.get("thing", "key")
        if thingKey == 'None' or thingKey == '':
            thingKey = None
        
        # get some defaults out of the config file
        defaultPcBuffer = cfg.get("defaults", "pc_buffer")
        defaultDevBuffer = cfg.get("defaults", "device_buffer")
        
        if port is None:
            if mode == 'DTE':
                port = cfg.get("defaults", "DTE_port")
            if mode == 'DCE':
                port = cfg.get("defaults", "DCE_port")
        
        return cls(thingId, thingKey, defaultPcBuffer, defaultDevBuffer, port, mode)
        
    def restart_session(self):
        ''' starts a new requests session
        '''
        self.session = requests.Session()
        
    def send_dweet(self, content):
        try:
            dweepy.dweet_for(self.thingId, content, key = self.key, session = self.session)
        
        except dweepy.DweepyError as e:
            print(e)
            print("Trying again...")
            time.sleep(2)
            self.send_dweet(content)
            pass
    
    def listen_for_dweets(self):
        try:
            for dweet in dweepy.listen_for_dweets_from( self.thingId, key=self.key, timeout=90000, session=self.session ):
                yield dweet
                
        # if you get an error because dweet closed the connection, open it again.
        except requests.exceptions.ConnectionError as e:
            print(e.response)
            print("Connection closed by dweet, restarting:")
            self.listen_for_dweets()
        
    def keepalive(self):
        """ dweet.io seems to close the connection after 60 seconds of inactivity. This sends a dummy payload every 45s to avoid that. 
        """
        while True:
            time.sleep(45)
            self.send_dweet({"keepalive": 1})
                
        
        

# standard imports
import time
from configparser import ConfigParser

# 3rd party imports
import dweepy
import serial
import requests

class DweetSession(object):

    def __init__(self, thingId, key, pc_keyword, device_keyword, port, mode):
        self.thingId = thingId
        self.key = key
        self.port = port
        self.mode = mode
        self.session = requests.Session()
        self.serial_port = serial.Serial(port)
        if mode == 'DTE':          # in DTE (pc) mode look for dweets under the device keyword, write dweets under the PC keyword
            self.fromThisDevice = pc_keyword
            self.fromThatDevice = device_keyword
        
        elif mode == 'DCE':        # in DCE (device) mode look for dweets under the PC keyword, write dweets under the device keyword
            self.fromThisDevice = device_keyword
            self.fromThatDevice = pc_keyword
        
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
        default_pc_keyword = cfg.get("defaults", "pc_buffer")
        default_device_buffer = cfg.get("defaults", "device_buffer")
        
        if port is None:
            if mode == 'DTE':
                port = cfg.get("defaults", "DTE_port")
            if mode == 'DCE':
                port = cfg.get("defaults", "DCE_port")
        
        return cls(thingId, thingKey, default_pc_keyword, default_device_buffer, port, mode)
        
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
            return self.send_dweet(content)
            
        except requests.exceptions.ConnectionError as e:
            print(e.response)
            print("Connection closed by dweet, restarting:")
            self.restart_session()
            return self.send_dweet(content)
    
    def listen_for_dweets(self):
        ''' makes a call to dweepy to start a listening stream. error handling needs work
        '''
        try:
            for dweet in dweepy.listen_for_dweets_from( self.thingId, key=self.key, timeout=90000, session=self.session ):
                yield dweet
                
        # if you get an error because dweet closed the connection, open it again.
        except requests.exceptions.ConnectionError as e:
            print(e.response)
            print("Connection closed by dweet, restarting:")
            self.restart_session()
            return self.listen_for_dweets()
        
    def keepalive(self):
        """ dweet.io seems to close the connection after 60 seconds of inactivity. This sends a dummy payload every 45s to avoid that. 
        """
        while True:
            time.sleep(45)
            self.send_dweet({"keepalive": 1})
                
        
        
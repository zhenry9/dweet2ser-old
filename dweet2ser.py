
# standard imports
import sys
import argparse
import time    
import datetime
from multiprocessing import pool, freeze_support
from configparser import ConfigParser
import threading

freeze_support()

# 3rd party imports
import dweepy
import serial
import requests
from colorama import init
from termcolor import colored
 
def keepalive(id, thingKey):
    """ dweet.io seems to close the connection after 60 seconds of inactivity. This sends a dummy payload every 45s to avoid that. 
    """
    while True:
        time.sleep(45)
        dweepy.dweet_for(thing_name=id, key=thingKey, payload={"keepalive": 1})
    
def listen_to_dweet(id, thingKey, ser, target, sesh):
    """listens for dweets for the given ID and writes to the given serial port.
       CP 545 data is expected as b'TN_0000_0000_01_12:34:56.7890_01234\x09\xDE\xCA\x0D\x0A'
    """ 
    for dweet in dweepy.listen_for_dweets_from( id, key=thingKey, timeout=90000, session=sesh ):     
        content = dweet["content"]
        
        if target in content:
            output = content[target]
            if type(output) is not str: # make sure the output is a string
                output = str(output)
            outputBytes = bytes.fromhex(output) # convert dweet string into bytes for RS232.
            ser.write(outputBytes)
            timestamp = str(datetime.datetime.now())
            outputText = outputBytes.strip().decode('latin-1')
            print(timestamp + ":\treceived " + colored("dweet", "cyan")) 
            print("\t\t\t\t" + outputText) 
            print("\t\t\t\twritten to " + colored("serial\n", "red"))
            
def listen_to_serial(id, thingKey, ser, target, sesh):
    """listens to serial port, if it hears something it dweets it
    """
    while True:
        if ser.in_waiting > 0:
            serData = ser.readline()
            dweepy.dweet_for(id, {target: serData.hex()}, key=thingKey, session = sesh)
            timestamp = str(datetime.datetime.now())
            print(timestamp + ":\treceived " + colored("serial data", "red"))
            print("\t\t\t\t " + serData.strip().decode('latin-1'))
            print("\t\t\t\tsent to  " + colored("dweet.io\n", "cyan"))
              
            
def main():
    
    # colorama call
    init()
    
    # open our config file
    cfg = ConfigParser()
    cfg.read("config.txt")
    
    # get thing ID from config file 
    thingId = cfg.get("thing", "id")
    thingKey = cfg.get("thing", "key")
    if thingKey == 'None' or thingKey == '':
        thingKey = None
    
    # get some defaults out of the config file
    defaultPcBuffer = cfg.get("defaults", "pc_buffer")
    defaultDevBuffer = cfg.get("defaults", "device_buffer")
    
    # start parsing CL arguments
    parser = argparse.ArgumentParser(description = "An interface for connecting an RS232 port to dweet.io.")
    parser.add_argument('--port', '-p', type=str, help='Manually specify port you are connecting to, overriding default e.g. COM7 or /dev/tty0')
    parser.add_argument('mode', type=str, choices=['DTE', 'DCE'], help='Whether you are on the software side (DTE) or the device side (DCE) of the connection.', default='DTE')
    
    args = parser.parse_args()
    
    # there are 2 "buffer" values being written to on dweet, one for the device and one for the PC.
    if args.mode == 'DTE':          # in DTE (pc) mode look for dweets in the device buffer, write dweets to the PC buffer
        port = cfg.get("defaults", "DTE_port")
        buffer1 = defaultPcBuffer
        buffer2 = defaultDevBuffer
    
    elif args.mode == 'DCE':        # in DCE (device) mode look for dweets in the PC buffer, write dweets to the device buffer
        port = cfg.get("defaults", "DCE_port")
        buffer1 = defaultDevBuffer
        buffer2 = defaultPcBuffer
  
    if args.port is not None:
        port = args.port
       
    serialPort = serial.Serial(port)
    # start a session to share for all dweepy requests
    sesh = requests.Session()
    
    # start the keepalive function
    p = pool.Pool()
    p.apply_async(keepalive, args=[thingId, thingKey])
    
    t1=threading.Thread(target = listen_to_serial, args=[thingId, thingKey, serialPort, buffer1, sesh])
    t2=threading.Thread(target = listen_to_dweet, args=[thingId, thingKey, serialPort, buffer2, sesh])
    t1.daemon = True
    t2.daemon = True
  
    print(colored("\n\t\t" + sys.argv[0] + " running on port: " + port + " in " + args.mode + " mode.\n", "red"))
    
    print("\t\t*************************************************")
    print("\t\t**               " + colored("Dweet", "cyan")+ " to " + colored("Serial", "red") + "               **") 
    print("\t\t**                by Zach Henry                **") 
    print("\t\t*************************************************") 
  
    try:
        t1.start()
        t2.start()
        
    # if you get an error because dweet closed the connection, open it again.
    except requests.exceptions.ConnectionError as e:
        print(e.response)
        print("Connection closed by dweet, restarting:")
        sesh = requests.Session()
        t1.start()
        t2.start()
    
    while True: # infinite loop to keep script alive
        pass

if __name__ == "__main__":  
    main()        

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
# colorama call
init()

# local imports
import dweetsession

CONFIG_FILE = "./config.txt"
    
def listen_to_dweet(dweetSesh):
    """listens for dweets for the given ID and writes to the given serial port.
       CP 545 data is expected as b'TN_0000_0000_01_12:34:56.7890_01234\x09\xDE\xCA\x0D\x0A'
    """ 
    ser = dweetSesh.serial_port
    target = dweetSesh.thatBuffer
    for dweet in dweetSesh.listen_for_dweets():     
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
                
    
def listen_to_serial(dweetSesh):
    """listens to serial port, if it hears something it dweets it
    """
    ser = dweetSesh.serial_port
    target = dweetSesh.thisBuffer
    while True:
        if ser.in_waiting > 0:
            serData = ser.readline()
            timestamp = str(datetime.datetime.now())
            print(timestamp + ":\treceived " + colored("serial data", "red"))
            print("\t\t\t\t " + serData.strip().decode('latin-1'))
            print("\t\t\t\tsent to  " + colored("dweet.io\n", "cyan"))
            dweetSesh.send_dweet({target: serData.hex()})
                
            
              
            
def main():
    
    # start parsing CL arguments
    parser = argparse.ArgumentParser(description = "An interface for connecting an RS232 port to dweet.io.")
    parser.add_argument('--port', '-p', type=str, help='Manually specify port you are connecting to, overriding default e.g. COM7 or /dev/tty0')
    parser.add_argument('mode', type=str, choices=['DTE', 'DCE'], help='Whether you are on the software side (DTE) or the device side (DCE) of the connection.', default='DTE')
    
    args = parser.parse_args()
    
    dweetSesh = dweetsession.DweetSession.from_config_file(CONFIG FILE, args.port, args.mode)
    
    # start the keepalive function
    p = pool.Pool()
    p.apply_async(dweetSesh.keepalive)
    
    t1=threading.Thread(target = listen_to_serial, args=[dweetSesh])
    t2=threading.Thread(target = listen_to_dweet, args=[dweetSesh])
    t1.daemon = True
    t2.daemon = True
    
  
    print(colored("\n\t\t" + sys.argv[0] + " running on port: " + port + " in " + args.mode + " mode.\n", "red"))
    
    print("\t\t*************************************************")
    print("\t\t**               " + colored("Dweet", "cyan")+ " to " + colored("Serial", "red") + "               **") 
    print("\t\t**                by Zach Henry                **") 
    print("\t\t*************************************************") 
  
    
    t1.start() # start listen to serial thread
    t2.start() # start listen to dweet thread
        
    
    while True: # infinite loop to keep script alive
        pass

if __name__ == "__main__":  
    main()        
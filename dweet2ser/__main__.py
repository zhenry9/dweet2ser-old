
# standard imports
import os
import sys
import argparse   
import threading

# 3rd party imports
from colorama import init
from termcolor import colored
# colorama call
init()

# local imports
from dweet2ser import dweetsession
from dweet2ser import connections

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
            
def main(): 
    # start parsing CL arguments
    parser = argparse.ArgumentParser(description = "An interface for connecting an RS232 port to dweet.io.")
    parser.add_argument('--port', '-p', type=str, help='Manually specify port you are connecting to, overriding default e.g. COM7 or /dev/tty0')
    parser.add_argument('mode', type=str, choices=['DTE', 'DCE'], help='Whether you are on the software side (DTE) or the device side (DCE) of the connection.', default='DTE')
    
    args = parser.parse_args()  
    dweetSesh = dweetsession.DweetSession.from_config_file(CONFIG_FILE, args.port, args.mode)
    
    t0=threading.Thread(target = dweetSesh.keepalive) # thread to send a dummy dweet every 45 seconds to keep the connection alive
    t1=threading.Thread(target = connections.listen_to_serial, args=[dweetSesh]) # thread to monitor the serial port for data
    t2=threading.Thread(target = connections.listen_to_dweet, args=[dweetSesh]) # thread to listen for incoming dweets
    
    t0.daemon = True
    t1.daemon = True
    t2.daemon = True
    
    print(colored("\n\t\t" + sys.argv[0] + " running on port: " + dweetSesh.port + " in " + dweetSesh.mode + " mode.\n", "red"))
    
    print("\t\t*************************************************")
    print("\t\t**               " + colored("Dweet", "cyan")+ " to " + colored("Serial", "red") + "               **") 
    print("\t\t**                by Zach Henry                **") 
    print("\t\t*************************************************") 
  
    t0.start() # start the keepalive thread
    t1.start() # start listen to serial thread
    t2.start() # start listen to dweet thread
        
    
    while True: # infinite loop to keep script alive
        pass

if __name__ == "__main__":  
    sys.exit(main())        
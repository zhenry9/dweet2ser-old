
# standard imports
import sys
import argparse   
import datetime
import threading

# local imports
import dweetsession
import connections

CONFIG_FILE = "./config.txt"
            
def main():
    
    # start parsing CL arguments
    parser = argparse.ArgumentParser(description = "An interface for connecting an RS232 port to dweet.io.")
    parser.add_argument('--port', '-p', type=str, help='Manually specify port you are connecting to, overriding default e.g. COM7 or /dev/tty0')
    parser.add_argument('mode', type=str, choices=['DTE', 'DCE'], help='Whether you are on the software side (DTE) or the device side (DCE) of the connection.', default='DTE')
    
    args = parser.parse_args()  
    dweetSesh = dweetsession.DweetSession.from_config_file(CONFIG_FILE, args.port, args.mode)
    
    # start the keepalive function
    
    t0=threading.Thread(target = dweetSesh.keepalive)
    t1=threading.Thread(target = connections.listen_to_serial, args=[dweetSesh])
    t2=threading.Thread(target = connections.listen_to_dweet, args=[dweetSesh])
    
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
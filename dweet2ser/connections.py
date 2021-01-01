
# standard imports
import datetime

# 3rd party imports
from colorama import init
from termcolor import colored
# colorama call
init()

def listen_to_dweet(dweetSesh):
    """listens for dweets for the given ID and writes to the given serial port.
       CP 545 data is expected as b'TN_0000_0000_01_12:34:56.7890_01234\x09\xDE\xCA\x0D\x0A'
    """ 
    ser = dweetSesh.serial_port
    target = dweetSesh.fromThatDevice
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
    target = dweetSesh.fromThisDevice
    while True:
        if ser.in_waiting > 0:
            serData = ser.readline()
            timestamp = str(datetime.datetime.now())
            print(timestamp + ":\treceived " + colored("serial data", "red"))
            print("\t\t\t\t " + serData.strip().decode('latin-1'))
            print("\t\t\t\tsent to  " + colored("dweet.io\n", "cyan"))
            dweetSesh.send_dweet({target: serData.hex()})
                           
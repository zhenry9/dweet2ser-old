
import json
import requests
import time  
import dweepy
import serial  
from multiprocessing import pool
 
# dweet.io seems to close the connection after 60 seconds of inactivity. This sends a dummy payload every 45s to avoid that. 
def keepalive(id):
    while True:
        time.sleep(45)
        dweepy.dweet_for(thing_name=id,payload={"keepalive": 1})
    
# listens for dweets for the given ID and writes to the given serial port.
# CP 545 data is expected as output=TN_0000_0000_01_12:34:56.7890_01234
def listen(id, ser):
    sesh = requests.Session()
    for dweet in dweepy.listen_for_dweets_from( id, timeout=90000, session=sesh ):     
        content = dweet["content"]
        
        if "output" in content:
            output = content["output"]
            if type(output) is not str: # make sure the output is a string
                output = str(output)
            outputBytes = output.encode() # convert dweet string into bytes for RS232.
            outputBytes += b'\x09\xDE\xCA\x0D\x0A' # add the necessary bytes to make the output into the expected format
            ser.write(outputBytes)
            print(output)
            
def main():  
  
    # replace with your thing Id  
    thingId = "zhenry_cp545_test" 
    serialPort = serial.Serial('COM50')
    
    p = pool.Pool()
    p.apply_async(keepalive, args=[thingId])
  
    print("\t\t*************************************************")
    print("\t\t**           Dweet to Serial                   **") 
    print("\t\t**               by Zach                       **") 
    print("\t\t*************************************************") 
  
    try:
        listen(thingId, serialPort)
        
    # if you get an error because dweet closed the connection, open it again.
    except requests.exceptions.ConnectionError as e:
        print(e.response)
        print("Connection closed by dweet, restarting:")
        listen(thingId, serialPort)
        

if __name__ == "__main__":  
    main()        
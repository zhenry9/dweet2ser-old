
import dweepy
import time

def keepalive(id, thingKey):
    """ dweet.io seems to close the connection after 60 seconds of inactivity. This sends a dummy payload every 45s to avoid that. 
    """
    while True:
        time.sleep(45)
        dweepy.dweet_for(thing_name=id, key=thingKey, payload={"keepalive": 1})
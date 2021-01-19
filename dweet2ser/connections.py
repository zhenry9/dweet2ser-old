# standard imports
import datetime
import multiprocessing
import queue
import time

from colorama import init
from termcolor import colored

# 3rd party imports

# colorama call
init()


def _write_to_serial(output, ser):
    if type(output) is not str:  # make sure the output is a string
        output = str(output)
    output_bytes = bytes.fromhex(output)  # convert dweet string into bytes for RS232.
    ser.write(output_bytes)
    timestamp = str(datetime.datetime.now())
    output_text = output_bytes.strip().decode('latin-1')
    print(timestamp + ":\treceived " + colored("dweet", "cyan"))
    print("\t\t\t\t" + output_text)
    print("\t\t\t\twritten to " + colored("serial\n", "red"))


def _write_last_dweet(dweet_sesh):
    ser = dweet_sesh.serial_port
    target = dweet_sesh.fromThatDevice
    dweet: dict = dweet_sesh.get_latest_dweet()
    content = dweet[0]["content"]
    if target in content:
        _write_to_serial(content[target], ser)


def _listen(dweet_sesh):
    ser = dweet_sesh.serial_port
    target = dweet_sesh.fromThatDevice
    for dweet in dweet_sesh.listen_for_dweets():
        content = dweet["content"]
        if target in content:
            _write_to_serial(content[target], ser)


def listen_to_dweet(dweet_sesh, bucket):
    """
    Starts listening for dweets. Watches the bucket and restarts the thread if a crash message is received.
    """
    # TODO: this seems pretty ugly. Figure out why stream crashes silently and find a better fix

    t = multiprocessing.Process(target=_listen, args=[dweet_sesh])
    t.daemon = True
    t.start()
    while True:
        try:
            # if another thread wrote a crash message its time to restart the stream
            if bucket.get(block=False) == 'crash':
                t.kill()
                timestamp = str(datetime.datetime.now())
                print(timestamp + ":\tListen thread crashed, restarting.")
                # retrieve the last dweet and send to serial, in case it was missed during crash
                _write_last_dweet(dweet_sesh)
                t.start()
        except queue.Empty:
            time.sleep(.01)
            pass


def listen_to_serial(dweet_sesh, bucket):
    """listens to serial port, if it hears something it dweets it
    """
    ser = dweet_sesh.serial_port
    target = dweet_sesh.fromThisDevice
    # TODO: find a way to listen to serial without an infinite loop
    # TODO: verify readline() will work with data other than CP540
    while True:
        if ser.in_waiting > 0:
            ser_data = ser.readline()
            timestamp = str(datetime.datetime.now())
            print(timestamp + ":\treceived " + colored("serial data", "red"))
            print("\t\t\t\t " + ser_data.strip().decode('latin-1'))
            print("\t\t\t\tsent to  " + colored("dweet.io\n", "cyan"))
            dweet_sesh.send_dweet({target: ser_data.hex()}, bucket)

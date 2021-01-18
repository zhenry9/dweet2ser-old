
# local imports
import queue

from . import dweetsession
from . import connections
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

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.txt')
bucket = queue.Queue()


def process_input(cmd):
    if cmd == "RESTART" or cmd == "restart":
        return bucket.put('crash', block=False)
    if cmd == "path":
        print(f"Path to config file: {CONFIG_FILE}")
        return
    else:
        # print command help
        print("Type 'RESTART' to restart the listen thread.\n"
              "Type 'path' to display path to config file.")
        return


def main():
    # start parsing CL arguments
    parser = argparse.ArgumentParser(description="An interface for connecting an RS232 port to dweet.io.")
    parser.add_argument('--port', '-p', type=str,
                        help='Manually specify port you are connecting to, overriding default e.g. COM7 or /dev/tty0')
    parser.add_argument('mode', type=str, choices=['DTE', 'DCE'],
                        help='Whether you are on the software side (DTE) or the device side (DCE) of the connection.',
                        default='DTE')

    args = parser.parse_args()
    dweet_sesh = dweetsession.DweetSession.from_config_file(CONFIG_FILE, args.port, args.mode)

    # thread to send a dummy dweet every 45 seconds to keep the connection alive
    t0 = threading.Thread(target=dweet_sesh.keepalive, args=[bucket])
    # thread to monitor the serial port for data
    t1 = threading.Thread(target=connections.listen_to_serial, args=[dweet_sesh, bucket])
    # thread to listen for incoming dweets
    t2 = threading.Thread(target=connections.listen_to_dweet, args=[dweet_sesh, bucket])

    t0.daemon = True
    t1.daemon = True
    t2.daemon = True

    print(colored("\n\t\t" + sys.argv[0] +
                  " running on port: " + dweet_sesh.port +
                  " in " + dweet_sesh.mode + " mode.\n", "red"))

    print("\t\t*************************************************")
    print("\t\t**               " + colored("Dweet", "cyan") + " to " + colored("Serial", "red") + "               **")
    print("\t\t**                by Zach Henry                **")
    print("\t\t*************************************************")

    t0.start()  # start the keepalive thread
    t1.start()  # start listen to serial thread
    t2.start()  # start listen to dweet thread

    while True:
        cmd = input("Type 'exit' to exit or ENTER for help.\n")
        if cmd == 'exit':
            break
        process_input(cmd)


if __name__ == "__main__":
    sys.exit(main())


# local imports
import queue

from . import setup_config
from . import dweetsession

# standard imports
import sys
import argparse


# 3rd party imports
from colorama import init
from termcolor import colored

# colorama call
init()

CFG = setup_config.DweetConfiguration().parser
bucket = queue.Queue()


def process_input(cmd):
    if cmd == "RESTART" or cmd == "restart":
        return bucket.put('crash', block=False)
    if cmd == "path":
        print(f"Path to config file: {CFG.get('User', 'user_config_file')}")
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
    dweet_sesh = dweetsession.DweetSession.from_config_parser(CFG, args.port, args.mode, bucket)

    dweet_sesh.start()

    print(colored("\n\t\t" + sys.argv[0] +
                  " running on port: " + dweet_sesh.port +
                  " in " + dweet_sesh.mode + " mode.\n", "red"))

    print("\t\t*************************************************")
    print("\t\t**               " + colored("Dweet", "cyan") + " to " + colored("Serial", "red") + "               **")
    print("\t\t**                by Zach Henry                **")
    print("\t\t*************************************************")

    while True:
        cmd = input("Type 'exit' to exit or ENTER for help.\n")
        if cmd == 'exit':
            break
        process_input(cmd)


if __name__ == "__main__":
    sys.exit(main())

# dweet2ser
A serial <-> dweet.io interface

dweet2ser allows for the two-way exchange of serial data between a device and a PC, using the free dweet.io API as an intermediary. This is particularly useful for connecting to faraway devices, not on the same LAN.

## Installation
Download dweet2ser.py and config.txt to the same directory. Update config.txt to your needs. The script requires the dweepy, requests, pyserial, colorama and termcolor python packages as dependencies. I'll try to make an installable python package eventually.

## Usage
### On the PC side of the connection:
  >`py dweet2ser.py DTE -p COM50`

This opens an instance of dweet2ser in DTE mode on windows port COM50. If you don't specify a port, the default from config.txt will be used. DTE mode means we are on the PC side, listening to data from the device (DCE) side.

### On the device side of the connection:
  >`py dweet2ser.py DCE -p /dev/tty0`
 
This opens an instance of dweet2ser in DCE mode on the linux port /dev/tty0. If you don't specify a port, the default from config.txt will be used. DCE mode means we are on the device side, sending data to the PC (DTE) side.

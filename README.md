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

### Virtual COM ports
On the PC (DTE) side you'll need to set up a virtual null modem to allow dweet2ser to communicate with the target software. This is just a pair of com ports connected to each other. dweet2ser connects to one port, and your software application connects to the other. 

On Windows this can be accomplished with [com0com](http://com0com.sourceforge.net/).

In the above example, we could used com0com to create a virtual null modem with ports COM50 and COM51. dweet2ser would connect to COM50, and the PC software to COM51.

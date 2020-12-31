# dweet2ser
A serial <-> dweet.io interface

<img src="dweet2ser-signal-flow.png" height="300" align="middle">

dweet2ser allows for the two-way exchange of data between a serial device and a PC over the internet, using the free dweet.io API as an intermediary. This is particularly useful for connecting to faraway devices that aren't on the same LAN.

dweet2ser works for connecting remotely to things like weather stations, sensors, or other devices that send simple data intermittently. It is not going to work for things like modems, due to the limitations of dweet.io among other things.

## Installation
Download dweet2ser.py, dweetsession.py and config.txt to the same directory. Update config.txt to your needs. The script requires the dweepy, requests, pyserial, colorama and termcolor python packages as dependencies. I'll try to make an installable python package eventually.

In windows, you can alternately download the bin/dweet2ser.exe binary. You will still need config.txt in the same directory, with the settings you want.

## Usage
The below assumes a Python environment. If you are using the windows executable, replace `python dweet2ser.py` with `dweet2ser`.

### Display help page

  `python dweet2ser.py -h`
  
This prints out the help page for command line options.

### On the device side of the connection:
  
  `python dweet2ser.py DCE -p /dev/tty0`
 
This opens an instance of dweet2ser in DCE mode on the linux port /dev/tty0. If you don't specify a port, the default from config.txt will be used. DCE mode means we are on the device side, sending data to the PC (DTE) side.

### On the PC side of the connection:
  
  `python dweet2ser.py DTE -p COM50`

This opens an instance of dweet2ser in DTE mode on windows port COM50. If you don't specify a port, the default from config.txt will be used. DTE mode means we are on the PC side, listening to data from the device (DCE) side.

### Virtual COM ports
On the PC (DTE) side you'll need to set up a virtual null modem to allow dweet2ser to communicate with the target software. This is just a pair of com ports connected to each other. dweet2ser connects to one port, and your software application connects to the other. 

On Windows this can be accomplished with [com0com](http://com0com.sourceforge.net/).

In the above example, we could use com0com to create a virtual null modem with ports COM50 and COM51. dweet2ser would connect to COM50, and the PC software to COM51.

## Licensing and Copyright
MIT License
Copyright (c) Zach Henry.

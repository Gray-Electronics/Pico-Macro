# DIY Raspberry Pi Pico Macropad Keyboard
Welcome to the DIY Macropad Keyboard setup repository! This collection of guides is designed to assist you in setting up a custom macropad keyboard using the DIY Raspberry Pi Pico Programmable Macropad Kits. The following will walk you through the process of setting up and programming your macropads with CircuitPython.

## Getting Started
If you don't have a kit already, you can pick one up here: 
* [Raspberry Pi Pico Kit | eBay ](https://www.ebay.com/itm/266628455392)
* [Raspberry Pi Pico Kit | Tindie ](https://www.tindie.com/products/33114/)

After soldering the provided components to the board, proceed with the setup below.

## What's Covered
- CircuitPython and library setup
- Setting up and configuring code
- Other configurations

## CircuitPython and Library Setup
### Firmware
Download the CircuitPython firmware file for your respective board from [CircuitPython's download page](https://circuitpython.org/downloads). Next, flash your board with the UF2 file per [these instructions](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython#start-the-uf2-bootloader-2977081).

Proceed to the next steps once you have installed the firmware onto your board and have the `CIRCUITPY` drive available on your computer.

### Libraries
An additional CircuitPython library is needed for your board to emulate a keyboard. Download the CircuitPython libraries package from [CircuitPython's libraries page](https://circuitpython.org/libraries). Make sure to download the bundle corresponding to the firmware version you flashed onto your board.


Once downloaded, unzip the bundle, and expand the `lib` subfolder. Take/copy out the `adafruit_hid` folder and move it into your `CIRCUITPY` drive. Place this folder under the `lib` directory in your `CIRCUITPY` drive.

## Setting Up and Configuring Code
### `code.py`
Download the `code.py` file from this repository and copy it to your `CIRCUITPY` drive. 

At its core, this code takes in a configuration file called `config.json` (see below) to set up the keys, controls, and LEDs then monitors for key presses, which it then sends to your computer as a sequence of keystrokes.

### `config.json`
All key sequences, control buttons (like `PROGRAM` and `LED`), and LEDs are defined in a file called `config.json`. There are example files in this repository. There are two options to generate the configuration file:

* Visit [our configuration generator page]() and generate it via the provided UI
* Generate it by hand

If you would like to generate it by hand, you can find the compatible keycodes [here](https://docs.circuitpython.org/projects/hid/en/latest/_modules/adafruit_hid/keycode.html).

## Other Configurations
### Disabling USB Storage
If you would your keyboard to not present itself as a USB drive during everyday operation, follow the below steps. 

**NOTE:** Before beginning this process, ensure that your configuration file has a `PROGRAM` button that is correctly configured.

1. Download the `boot.py` file from this repository and upload it to your board. This file will run before `code.py` and has the ability to disable USB storage and mounting.
2. Create a file called `disable_mount.txt` on your board.
3. Open `disable_mount.txt` and enter the GPIO pin that your `PROGRAM` button is hooked to.
4. Save the file and power your board off and back on.

After these steps, you shouldn't see your board appear as a USB storage device. 

To remount your device, hold down the `PROGRAM` button until you see the `CIRCUITPY` drive appear in your file explorer (approximately 5 seconds).

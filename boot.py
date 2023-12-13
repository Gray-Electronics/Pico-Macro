import os

import board
import digitalio
import storage


def init_gpio(gpio: str):
    try:
        return digitalio.DigitalInOut(getattr(board, gpio))
    except AttributeError:
        print(f"Invalid GPIO {gpio}")
        exit()
    except Exception as e:
        print(f"Error trying to initialize pin. Exception: {str(e)}")
        exit()


def init_button(gpio: str):
    try:
        pin = init_gpio(gpio)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.DOWN
        return pin
    except Exception as e:
        print(f"Error initializing button on pin {gpio}. Exception: {str(e)}")
        exit()


if "disable_mount.txt" not in os.listdir('/'):
    exit()

gpio = ''

with open("disable_mount.txt") as f:
    gpio = f.read().strip().upper()

if not gpio.startswith("GP"):
    print(f"Invalid GPIO {gpio}")
    exit()

btn = init_button(gpio)

if not btn.value:
    storage.disable_usb_drive()
    storage.remount('/', readonly=False)

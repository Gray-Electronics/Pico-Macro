import json
import os
import time

import board
import digitalio
import microcontroller
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

keyboard = Keyboard(usb_hid.devices)


def blink_onboard_led():
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT
    while True:
        led.value = True
        time.sleep(2)
        led.value = False
        time.sleep(2)


def toggle_leds(*args):
    for led in args:
        led.value = not led.value


def program(*args):
    try:
        with open("tmp", "w"):
            pass
        os.remove("tmp")
        microcontroller.reset()
    except Exception:
        print("File system is not writable by code, it is unsafe to restart")
        return


def exec(seq: list):
    for cmd in seq:
        if cmd[0] == "press":
            keyboard.press(cmd[1])
        elif cmd[0] == "release":
            keyboard.release(cmd[1])
        elif cmd[0] == "delay":
            time.sleep(cmd[1])
    return


def init_gpio(gpio: str):
    try:
        return digitalio.DigitalInOut(getattr(board, gpio))
    except AttributeError:
        print(f"Invalid GPIO {gpio}")
        blink_onboard_led()
    except Exception as e:
        print(f"Error trying to initialize pin. Exception: {str(e)}")
        blink_onboard_led()


def init_button(gpio: str):
    try:
        pin = init_gpio(gpio)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.DOWN
        return pin
    except Exception as e:
        print(f"Error initializing button on pin {gpio}. Exception: {str(e)}")
        blink_onboard_led()


def get_config(fail_callback) -> dict:
    try:
        with open("config.json") as f:
            return json.load(f)
    except ValueError as e:
        print(f"Config file is invalid JSON. Exception: {str(e)}")
        fail_callback()
    except Exception as e:
        print(f"Error trying to get config file. Exception: {str(e)}")
        fail_callback()


def validate_controls(controls: list, fail_callback):
    if not len(controls):
        return

    for control in controls:
        if type(control) is not dict:
            print(f"Control {control} is not a dictionary")
            fail_callback()
        elif control.get("GPIO") is None or control.get("control") is None:
            print("Control config is missing an expected key.")
            print("Expected: 'GPIO', 'control'")
            fail_callback()
        elif type(control["GPIO"]) is not str or type(control["control"]) is not str:
            print(f"Control {control} does not have string values")
            fail_callback()


def validate_leds(leds: list, fail_callback):
    if not len(leds):
        return

    for led in leds:
        if type(led) is not str:
            print(f"LED pin {led} is not a string")
            fail_callback()


def validate_keys(keys: list, fail_callback):
    if not len(keys):
        return

    for key in keys:
        if type(key) is not dict:
            print(f"Key {key} is not a dictionary")
            fail_callback()
        elif (
            key.get("GPIO") is None
            or key.get("repeating") is None
            or key.get("sequence") is None
        ):
            print("Key config is missing an expected key.")
            print("Expected: 'GPIO', 'repeating', 'sequence'")
            fail_callback()
        elif (
            type(key["GPIO"]) is not str
            or type(key["repeating"]) is not bool
            or type(key["sequence"]) is not list
        ):
            print(f"Key {key} does not have expected value types")
            fail_callback()

        for cmd in key["sequence"]:
            if type(cmd) is not list:
                print(f"Command {cmd} is not a list")
                fail_callback()
            elif len(cmd) != 2:
                print(f"Command list {cmd} is not proper length")
                fail_callback()


def validate_config(config, fail_callback):
    if type(config) is not dict:
        print("Config is not a dict")
        fail_callback()
    elif (
        config.get("controls") is None
        or config.get("leds") is None
        or config.get("keys") is None
    ):
        print("Missing an expected top level config key.")
        print("Expected: 'controls', 'leds', 'keys'")
        fail_callback()
    elif (
        type(config["controls"]) is not list
        or type(config["leds"]) is not list
        or type(config["keys"]) is not list
    ):
        print("Config values are not list types")
        fail_callback()

    validate_controls(config["controls"], fail_callback)
    validate_leds(config["leds"], fail_callback)
    validate_keys(config["keys"], fail_callback)


def main():
    config = get_config(blink_onboard_led)
    validate_config(config, blink_onboard_led)
    state = []
    MAXDELAY = 0.3

    for key in config["keys"]:
        btn = init_button(key["GPIO"])
        v = btn.value
        state.append([btn, v, time.time() if v else None])
        for cmd in key["sequence"]:
            try:
                cmd[1] = getattr(Keycode, cmd[1])
                continue
            except AttributeError:
                pass

            try:
                cmd[1] = int(cmd[1])
                continue
            except AttributeError:
                pass

            try:
                cmd[1] = int(cmd[1], 16)
                continue
            except AttributeError:
                pass

            print(f"Keycode {cmd[1]} is invalid")
            blink_onboard_led()

    leds = []
    for led in config["leds"]:
        pin = init_gpio(led)
        pin.direction = digitalio.Direction.OUTPUT
        pin.value = True
        leds.append(pin)

    controls = []
    for control in config["controls"]:
        btn = init_button(control["GPIO"])
        if control["control"] == "led":
            controls.append([btn, False, toggle_leds, leds])
        elif control["control"] == "program":
            controls.append([btn, False, program, []])

    while True:
        for idx, (key, prev, t) in enumerate(state):
            if not key.value and not prev:
                continue
            elif key.value and not prev:
                exec(config["keys"][idx]["sequence"])
                state[idx][1] = True
                state[idx][2] = time.time()
            elif not key.value and prev:
                state[idx][1] = False
            elif key.value and prev and config["keys"][idx]["repeating"]:
                if time.time() - t > MAXDELAY:
                    exec(config["keys"][idx]["sequence"])
                time.sleep(0.075)
            else:
                continue

        for idx, (control, prev, func, args) in enumerate(controls):
            if not control.value and not prev:
                continue
            elif control.value and not prev:
                func(*args)
                controls[idx][1] = True
            elif not control.value and prev:
                controls[idx][1] = False
            else:
                continue


main()

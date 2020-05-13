#!/usr/bin/python


"""

Auto Trigger Go thing.

James Cooper 2020
Originally written for the Opera Double Bill, GSMD


"""
import argparse
import pyautogui

from pythonosc import osc_server
from pythonosc import dispatcher

press = pyautogui.press

system_id = "keys"

command_keys = {
"all_stop": "space",
"red_stop": "f2",
"blue_stop": "f4",
"green_stop": "f6",
"yellow_stop": "f8",
"red_start": "f1",
"blue_start": "f3",
"green_start": "f5",
"yellow_start": "f7",
"next_cue": "pagedown",
"prev_cue": "pageup",
"first_cue": "home",
"last_cue": "end",
"load": "f12",
}


def get_auto_trigger(unused_addr, args, value):
    if value in command_keys.keys():
        print(f"[{args[0]}] ~ {value}")
        press(command_keys[value])
    else:
        print(f"Unrecognised command: '{value}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
    default="127.0.0.1", help="The IP you're listening for OSC 'GO' triggers from")
    parser.add_argument("--port",
    type = int, default=42020, help="The port you're listening to.")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map(f"/kinesys/{system_id}/keys", get_auto_trigger, "Kinesys Control")

    server = osc_server.ThreadingOSCUDPServer(
    (args.ip, args.port), dispatcher)
    print(f"Listening on {server.server_address}")
    server.serve_forever()

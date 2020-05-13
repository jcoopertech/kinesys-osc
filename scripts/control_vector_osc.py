#!/usr/bin/python


"""

Auto Trigger Go

James Cooper 2020
Originally written for the Opera Double Bill, GSMD


"""
import argparse
import pyautogui

from pythonosc import osc_server
from pythonosc import dispatcher

press = pyautogui.press

system_id = "SST_Auto"
system_address = f"/kinesys/{system_id}"

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

CurrentCue = 0

DISCLAIMER = """
This utility allows you to control Kinesys Vector from any software, able to
send OSC packets.

Kinesys automation software is not designed to allow this capability.

By using this software, you accept ALL and TOTAL responsibility for how the
system operates. I am providing the means, in good faith, for a virtual show.
This means that Kinesys is not controlling real world items, and therefore will
not endanger anyone in the process.

I will not be held accountable for any ways you use this software, in the event
of damage, injury, or any other unexpected malfunction of any system this
interfaces with.

==
"""
def accept_disclaimer():
    print(DISCLAIMER)
    user_input = str(input("\nPlease type \"responsible\" to continue."))
    return True

def get_auto_trigger(unused_addr, value):
    if value in command_keys.keys():
        print(f"[ {unused_addr} ] ~ {value}")
        press(command_keys[value])
        # Increment cue number to track along with Vector
        if value == "next_cue":
            CurrentCue += 1
    else:
        print(f"Unrecognised command: '{value}'")


def sync_to_latest_cue(unused_addr, value):
        print(f"[ {unused_addr} ] ~ Current Cue: {value}")
        print("Syncing the cues")
        press(command_keys["first_cue"])
        for cue in range(22):
            if CueNumber == value:
                break
            press(command_keys["next_cue"])

if __name__ == "__main__":
    if accept_disclaimer() or True:
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip",
        default="127.0.0.1", help="The IP you're listening for OSC 'GO' triggers from")
        parser.add_argument("--port",
        type = int, default=42020, help="The port you're listening to.")
        args = parser.parse_args()

        dispatcher = dispatcher.Dispatcher()
        dispatcher.map(f"{system_address}/control", get_auto_trigger)
        dispatcher.map(f"{system_address}/place", sync_to_latest_cue)

        server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
        print(f"Listening on {server.server_address}")
        server.serve_forever()

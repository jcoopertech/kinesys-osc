#!/usr/bin/python


"""

Auto Trigger Go

James Cooper 2020
Originally written for the Opera Double Bill, GSMD


"""
import argparse
import pyautogui
import pickle

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

CurrentCue = 1

cuelist = [
1.0,
2.0,
3.0,
4.0,
4.24,
4.25,
5.0,
6.0,
7.0,
8.0,
9.0,
10.0,
]

DISCLAIMER = """
==
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
    global CurrentCue
    global cuelist
    value = round(float(value),3)
    if value in command_keys.keys():
        if value == "first_cue":
            CurrentCue = cuelist[0]
        elif value == "last_cue":
            CurrentCue = cuelist[-1]
        try:
            print(f"[ {unused_addr} ] ~ {value} - Current Cue: {cuelist[CurrentCue-1]}")
        except IndexError as e:
            print(f"{e}")
            print(f"[ {unused_addr} ] ~ {value} - Current Cue: {CurrentCue}\nCaptain, we've gone off the deep end. len(cuelist) = {len(cuelist)}")
        press(command_keys[value])
        # Increment cue number to track along with Vector
        if value == "next_cue":
            CurrentCue += 1
    else:
        print(f"Unrecognised command: '{value}'")


def sync_to_latest_cue(unused_addr, value):
    global CurrentCue
    global cuelist
    CurrentCue = 1
    value = round(float(value),3)
    if value not in cuelist:
        print("FATAL ERROR: Cue number could not be found in cuelist.")
    elif value in cuelist:
        print(f"[ {unused_addr} ] ~ Current Cue: {value}")
        print(f"Syncing the cues")
        # First, stop anything moving, and clear playbacks, to avoid double loaded PBs
        press(command_keys["all_stop"])
        # Go to the top of the stack
        press(command_keys["first_cue"])
        for cue in cuelist:
            if cuelist[CurrentCue-1] == value:
                print(f"loading cue {cuelist[CurrentCue-1]}")
                press(command_keys["load"])
                break
            print(f"skipping cue {cuelist[CurrentCue-1]}")
            press(command_keys["next_cue"])
            CurrentCue += 1


def add_cue(unused_addr, value):
    global cuelist
    value = round(float(value),3)
    if value in cuelist:
        print(f"Cue {value} already exists")
    if value not in cuelist:
        print(f"Adding Cue {value} to Cuelist")
        cuelist.append(value)
        cuelist.sort()
        print(cuelist)


def delete_cue(unused_addr, value):
    global cuelist
    value = round(float(value), 3)
    if value not in cuelist:
        print(f"Cue {value} wasn't in the list anyway")
    if value in cuelist:
        cuelist.remove(value)
        cuelist.sort()
        print(f"Cue {value} has been deleted.")
        print(cuelist)


def load_cuelist(unused_addr, value):
    global cuelist
    cuelist = pickle.load(open(f"{value}.qlist", "rb"))
    print(f"Loaded {value}.qlist from disk successfully.\n{cuelist}")


def save_cuelist(unused_addr, value):
    global cuelist
    pickle.dump(cuelist, open(f"{value}.qlist", "wb"))
    print(f"Saved {value}.qlist to  disk successfully.\n{cuelist}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
    default="127.0.0.1", help="The IP you're listening for OSC 'GO' triggers from")
    parser.add_argument("--port",
    type = int, default=42020, help="The port you're listening to.")
    parser.add_argument("--cuelist",
    default=None, help="The filename of the .qlist file you want to load.")
    args = parser.parse_args()

    if accept_disclaimer():
        dispatcher = dispatcher.Dispatcher()
        dispatcher.map(f"{system_address}/control", get_auto_trigger)
        dispatcher.map(f"{system_address}/place", sync_to_latest_cue)
        dispatcher.map(f"{system_address}/cue/add", add_cue)
        dispatcher.map(f"{system_address}/cue/delete", delete_cue)
        dispatcher.map(f"{system_address}/cue/save", save_cuelist)
        dispatcher.map(f"{system_address}/cue/open", load_cuelist)

        server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
        if args.cuelist == None:
            print("No cuelist specified, we're going on the hard coded values")
            print(cuelist)
        else:
            print(f"Loading \"{args.cuelist}.qlist\" cuelist file.")
            load_cuelist(None, args.cuelist)
        print(f"Listening on {server.server_address}")
        server.serve_forever()

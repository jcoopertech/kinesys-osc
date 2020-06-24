#!/usr/bin/python
"""
kinesys-osc

MIT License

Copyright (c) 2020 James Cooper

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import pyautogui
import pickle
from time import strftime
from pythonosc import osc_server
from pythonosc import dispatcher
import os


class Job():
    def __init__(self, unused_addr, value, opfunct):
        self.addr = unused_addr
        self.value = value
        self.execute = opfunct

    def do(self):
        self.execute(self.addr, self.value)


class Buffer():
    """Create a wrapper class for the buffer system, full of job objects"""
    def __init__(self):
        self.tasks = []

    def add_task(self, unused_addr, value, opfunct):
        print(f"BUFFER ADD: {opfunct.__name__} {unused_addr} {value}")
        self.tasks.append(Job(unused_addr,value,opfunct))

    def delete_first(self):
        print(f"BUFFER DEL: {self.tasks[0].execute.__name__} {self.tasks[0].addr} {self.tasks[0].value}")
        self.tasks.pop(0)

    def get_buffer(self):
        return self.tasks

    def do(self):
        while len(self.tasks) != 0:
            self.tasks[0].do()
            self.delete_first()


def accept_disclaimer():
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
    print(DISCLAIMER)
    user_input = str(input("\nPlease type \"responsible\" to continue."))
    if user_input == "responsible":
        return True
    else:
        print("""Apparently you're not responsible.
        Either write code to bypass this check, or contact james@jcooper.tech to skip for free.""")

doingCMD = False
isSyncing = False
MainBuffer = Buffer()
bufferBlock = False

def buffer_management(MainBuffer):
    global bufferBlock
    if bufferBlock == True:
        return
    elif bufferBlock == False:
        bufferBlock = True
    if len(MainBuffer.get_buffer()) > 0:
        MainBuffer.do()
    bufferBlock = False


def get_auto_trigger(unused_addr, value):
    global MainBuffer
    global isSyncing
    global bufferBlock
    global doingCMD
    if doingCMD == True or isSyncing == True:
        MainBuffer.add_task(unused_addr, value, get_auto_trigger)
        return
    else:
        doingCMD = True

    """
    Main command function for jumping around cuelist and controlling Vector.
    """
    global CurrentCue
    global cuelist
    if value in command_keys.keys():
        # If valid OSC command to the /control addr:
        if value == "first_cue":
            #These 3 if statements are mainly handling printed values showing current stack pointer.
            CurrentCue = cuelist[0]
        elif value == "last_cue":
            CurrentCue = cuelist[-1]
        elif value == "next_cue":
            try:
                # Set CurrentCue to the cuelist item after the current one.
                # Can cause a TOS error when we get to the end, or lots of cmds being sent, so we just go to the end,
                # Vector doesn't wrap around.
                CurrentCue = cuelist[int(cuelist.index(CurrentCue))+1]
            except IndexError as e:
                #print(e)
                #print("Going to last cue")
                CurrentCue = cuelist[-1]
        elif value == "prev_cue":
            try:
                if cuelist.index(CurrentCue)-1 <= 0:
                    CurrentCue = cuelist[0]
                else:
                    CurrentCue = cuelist[cuelist.index(CurrentCue)-1]
                # This doesn't work because negative values wrap to the hi end of the list of course(!)
                # So we add in a 0 or lower check for the cue pointer
            except IndexError as e:
                # In theory, this should never be called, because of the wrap around above.
                print(e)
                print("Probably at the start of the cuelist. Setting current cue to first cue.")
                CurrentCue = cuelist[0]
        try:
            # Just print the current thing. This shouldn't actually ever raise an Index error anymore.
            print(f"{strftime('%H:%M:%S %a %b %Z')}[ {unused_addr} ] ~ {value} - Current Cue: {CurrentCue}")
        except IndexError as e:
            print(f"{e}")
            print(f"[ {unused_addr} ] ~ {value} - Current Cue: {CurrentCue}\nCaptain, we've gone off the deep end. len(cuelist) = {len(cuelist)}")
        press(command_keys[value])
        # Increment cue number to track along with Vector

    else:
        # only raised on the /control OSC addr - i.e. there's not a keyboard press for the command
        print(f"Unrecognised command: '{value}'")
    doingCMD=False
    buffer_management(MainBuffer)



def sync_to_latest_cue(unused_addr, value):
    global isSyncing
    global MainBuffer
    if isSyncing == True:
        MainBuffer.add_task(unused_addr, value, sync_to_latest_cue)
        return
    else:
        isSyncing = True


    global CurrentCue
    global cuelist
    value = round(float(value),3)
    if value not in cuelist:
        raise IndexError(f"Cue 'value={value}'' could not be found in cuelist.")
    elif value in cuelist:
        print(f"{strftime('%H:%M:%S %a %b %Z')}[ {unused_addr} ] ~ Desired Cue: {value}")
        print(f"Syncing the cues")
        # First, stop anything moving, and clear playbacks, to avoid double loaded PBs
        press(command_keys["all_stop"])
        # Go to the top of the stack
        press(command_keys["first_cue"])
        CurrentCue = cuelist[0]
        for cue in cuelist[0:cuelist.index(value)+1]:
            # iterate through the cuelist segment up till the cue we want +1 because indexing not hi-end inclusive.
            CurrentCue = cue
            if CurrentCue == value:
####                print(f"Loading cue {CurrentCue}")
##                press(command_keys["load"])
                print(f"{strftime('%H:%M:%S %a %b %Z')}[ {unused_addr} ] ~ {value} - Current Cue: {CurrentCue}")
                break
            print(f"skipping cue {CurrentCue}, now in {cuelist[cuelist.index(CurrentCue)+1]}")
            press(command_keys["next_cue"])
    isSyncing = False
    buffer_management(MainBuffer)


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


press = pyautogui.press
GSMD=None # Are you Guildhall School of Music and Drama? If so, getPerks()
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


cuelist = [
0.1,0.2,0.3,0.9,1.0,2.0,2.1,2.9,3.0,4.0,5.0,5.1,5.9,6.0,7.0,7.1,8.0,8.9,9.0,10.0]

CurrentCue = cuelist[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
    default="127.0.0.1", help="The IP you're listening for OSC 'GO' triggers from")
    parser.add_argument("--port",
    type = int, default=42020, help="The port you're listening to.")
    parser.add_argument("--cuelist",
    default=None, help="The filename of the .qlist file you want to load.")
    parser.add_argument("--fsafe",
    default=True, help="Controls whether pyautogui is in Failsafe Mode. [True]")
    args = parser.parse_args()
    if args.fsafe == False:
        pyautogui.FAILSAFE = False
    else:
        pyautogui.FAILSAFE = True

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
            # If we don't pass a --cuelist argument to the program.
            print("No cuelist specified, we're going on the hard coded values")
            print(f"Loaded cuelist:\n{cuelist}")
            print(f"Starting Cue: {CurrentCue}")
        else:
            print(f"Loading \"{args.cuelist}.qlist\" cuelist file.")
            load_cuelist(None, args.cuelist)
        print(f"Listening on {server.server_address}")
        server.serve_forever()

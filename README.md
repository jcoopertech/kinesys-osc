# kinesys-osc
## OSC control for Kinesys Vector v2 Motion Control and Automation System.

## Purpose
Emulates Kinesys Vector V2 Keyboard Shortcuts, to emulate an operator starting playbacks. This is to enable timecode triggered automation in a **simulation** environment.

**This code should never be used to control motors or drives in a real world scenario. You take sole responsibility for how you use this code.**

**This system was built for a virtual show, where Vector sends Media Server Packets to D3, for simulation of set piece movement.**

## Dependencies
```
pyAutoGUI
pythonosc
```

These can be installed by using `pip` or `pip3` on Mac.
```
pip install pyAutoGUI
pip install pythonosc
```
## Usage
On Windows:
```
python control_vector_osc.py --ip IP --port PORT --cuelist FILE_NAME
```

On Mac:
```
python3 control_vector_osc.py --ip IP --port PORT --cuelist FILE_NAME
```

### Default values:
Arguments are all optional - default values are:
```
--ip: 127.0.0.1
--port: 42020
--cuelist: None
```

If cuelist is `None`, it will load whatever is programmed in the file as "`cuelist`"

At the current time, this is:
```python
cuelist = [
1.0, 2.0, 3.0, 4.0, 4.24, 4.25, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
]
```

### Available Vector control commands:
All OSC commands below are prefixed with the following `system_address`:
```python
system_id = "CustomStringHere"
system_address = f"/kinesys/{system_id}"
```
By default, `system_id = "SST_Auto"`

Shown below are the currently available Vector control features, next to the button presses they emulate.
These commands should be given as values under the `/control` address
```python
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
```

#### Example operation of control OSC:
This gives an example of the OSC commands needed to load the first cue, then start the red playback in Vector.
```
/kinesys/SST_Auto/control first_cue
/kinesys/SST_Auto/control load
/kinesys/SST_Auto/control red_start
```

### Cuelists
We can go to a specific place in the Vector show by using the `place` command.
This requires you to have an up-to-date `cuelist` array in the programming code - so that Python knows what cue Vector is skipping.
If one is missing / one is added, we'll start to undershoot or overshoot cues in the cuelist - which won't be fun.

#### Available Cuelist manipulation commands:
`/place` - to go to a specific Cue in Vector

`/cue/add N` - to add a cue of number N (the cuelist is automatically sorted)

`/cue/delete N` - delete the cue

`/cue/save F` - save the current python `cuelist` array to `F.qlist`

`/cue/open F` - load the `cuelist` array from the `F.qlist` file on disk.

##### Example operation of OSC cuelist manipulation
This sequence of commands adds cue 2.1, deletes cue 1, and saves these changes to `mycuelist.qlist`.
We then put Vector into cue 6, which can then be loaded, and playbacks started as needed.
```
/kinesys/SST_Auto/cue/add 2.1
/kinesys/SST_Auto/cue/delete 1
/kinesys/SST_Auto/cue/save mycuelist
/kinesys/SST_Auto/place 6
/kinesys/SST_Auto/control load
/kinesys/SST_Auto/control yellow_start
```

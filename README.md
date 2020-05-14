# auto-sim
Controlling Kinesys Vector automation over OSC.

## Purpose
Outputs OSC data, based on programmed cues, which are triggered by OSC.

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
### Usage
On Windows:
```
python control_vector_osc.py --ip IP --port PORT --cuelist FILE_NAME
```

On Mac:
```
python3 control_vector_osc.py --ip IP --port PORT --cuelist FILE_NAME
```

#### Default values:
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
Shown below are the currently available Vector control features, next to the button presses they emulate.
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

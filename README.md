# auto-sim
Controlling Kinesys Vector automation over OSC.

## Purpose
Outputs OSC data, based on programmed cues, which are triggered by OSC.

### Usage
On windows:
`python control_vector_osc.py --ip IP --port PORT --cuelist NameOf.qlistFile.`

All arguments are optional, and default values are:
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

### Available OSC commands:
Shown below are the currently available features, next to the button presses they emulate.
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

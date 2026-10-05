---
name: tap-tapping
description: Decode Tap tapcodes (which fingers tapped), map finger combinations to app actions or keyboard shortcuts, and give haptic feedback. Use for tapping, finger combos, chords, tap-to-action, shortcuts, v1 input modes, or the v2 TAPPING model.
---

# Tapping

Works on v1 and v2. Start from the `tap-getting-started` skill for connection.

## Tapcode bitmask

A tapcode is an int 1-31. Each bit is one finger:

| Bit | Value | Finger |
|-----|-------|--------|
| 0 | 1 | thumb |
| 1 | 2 | index |
| 2 | 4 | middle |
| 3 | 8 | ring |
| 4 | 16 | pinky |

Examples: `1` thumb, `2` index, `3` thumb+index, `6` index+middle, `31` all five.

```python
FINGERS = ["thumb", "index", "middle", "ring", "pinky"]

def first(value):  # v1 int, v2 [int]
    return value[0] if isinstance(value, (list, tuple)) else value

def fingers(tapcode):
    return [name for bit, name in enumerate(FINGERS) if tapcode & (1 << bit)]

ACTIONS = {
    2: "next",       # index
    4: "previous",   # middle
    6: "select",     # index + middle
    31: "quit",      # all fingers
}

def on_tap(identifier, tapcode):
    action = ACTIONS.get(first(tapcode))
    if action:
        handle(action)
```

Single-finger taps are the most reliable. Prefer them for frequent actions. Use 2-finger combos next. Use 3+ finger combos only for rare actions.

## Turn on tap events

- **v1**: `await sdk.set_input_mode(InputModeController())` after `start()`.
  - `InputModeText()` (default): the Tap types letters on the OS keyboard. The SDK gets no taps.
  - `InputModeController()`: the SDK gets tap, mouse, and air-gesture events. No typing.
  - `InputModeControllerText()`: both at the same time.
  - The SDK re-sends the mode every 10 s, so the device stays in it.
- **v2**: `set_feature(DeviceFeatures.MODEL_DETECTION, True)`, `set_vision_sensor_model(ModelTypes.TAPPING)`, `set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)`.

## Double taps and multi-taps

The SDK reports every tap. Detect double taps yourself with a time window:

```python
import time

last = {"code": None, "t": 0.0}

def on_tap(identifier, tapcode):
    code, now = first(tapcode), time.monotonic()
    if code == last["code"] and now - last["t"] < 0.35:
        handle_double(code)
        last["code"] = None
        return
    last.update(code=code, t=now)
    handle_single(code)
```

If single and double must not both fire, delay the single action until the window ends (schedule it with `loop.call_later(0.35, ...)` and cancel it on the second tap).

## Map taps to keyboard shortcuts

The SDK does not send OS key presses. Add a library in the user's app, for example `pip install pynput`:

```python
from pynput.keyboard import Controller, Key
kb = Controller()
SHORTCUTS = {2: Key.right, 4: Key.left, 6: Key.space}

def on_tap(identifier, tapcode):
    key = SHORTCUTS.get(first(tapcode))
    if key:
        kb.press(key); kb.release(key)
```

macOS: the terminal / IDE needs Accessibility permission to send keys.

## Haptic feedback

```python
await sdk.send_vibration_sequence([80])              # short buzz
await sdk.send_vibration_sequence([100, 100, 100])   # double buzz
```

Values are on/off durations in ms (10-2550, max 18 values). From a sync callback, schedule it: `asyncio.get_running_loop().create_task(sdk.send_vibration_sequence([80]))`.

## Docs

- v1 events: https://tapwithus.github.io/tap-python-sdk/latest/v1/reference/events/
- v1 input modes: https://tapwithus.github.io/tap-python-sdk/latest/v1/how-to/switch-input-modes/
- v2 events: https://tapwithus.github.io/tap-python-sdk/latest/v2/reference/events/

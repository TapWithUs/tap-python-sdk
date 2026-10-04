---
name: tap-imu-motion
description: Use Tap hand motion - v2 IMU motion data (dx, dy, roll, pitch, yaw) and v1 mouse events - to move a cursor, steer, tilt, or rotate things. Use for air mouse, pointer, cursor control, tilt, orientation, euler angles, roll/pitch/yaw, or motion-driven UI.
---

# IMU motion and mouse

The two protocols give motion in different ways.

## v2 (`TapSDK2`): IMU motion feature

```python
from tapsdk import DeviceFeatures

def on_motion(identifier, motion):
    dx, dy, is_mouse, (roll, pitch, yaw) = motion
    ...

sdk.register_imu_motion_data_events(on_motion)
await sdk.start()
await sdk.set_feature(DeviceFeatures.IMU_MOTION_DATA, True)
```

- `dx`, `dy`: signed int pointer deltas since the last packet. Add them to a cursor position.
- `is_mouse`: `True` when the device considers the motion a pointer movement.
- `roll`, `pitch`, `yaw`: signed ints, orientation in degrees.
- Turn off with `set_feature(DeviceFeatures.IMU_MOTION_DATA, False)` to save battery and bandwidth.
- Motion works together with `MODEL_DETECTION` (air gestures). The `tap-knob` and `tap-dpad` skills combine them.

## v1 (`TapSDK`): mouse events

```python
from tapsdk import InputModeController

def on_mouse(identifier, vx, vy, proximity):
    ...

sdk.register_mouse_events(on_mouse)
await sdk.start()
await sdk.set_input_mode(InputModeController())
```

- `vx`, `vy`: signed velocities. `proximity`: `True` when a surface is detected (optical mouse on Tap Strap).
- v1 has no euler angles. For orientation on v1, use raw IMU (`tap-raw-sensors`).
- TapXR Spatial Control: `await sdk.set_input_type(InputType.MOUSE)` forces air-mouse; `InputType.AUTO` returns to automatic.

## Patterns

**Cursor on a canvas** (clamp to bounds, optional gain):

```python
GAIN = 1.0
x, y = 400, 300

def on_motion(identifier, motion):
    global x, y
    dx, dy, _, _ = motion
    x = min(max(x + dx * GAIN, 0), WIDTH)
    y = min(max(y + dy * GAIN, 0), HEIGHT)
```

**Relative rotation (roll as a dial)**: store a reference roll when the user starts (for example on a pinch-hold), then use `roll - reference`. Do not use absolute roll; it depends on how the hand is held. See `tap-knob`.

**Smoothing**: an exponential moving average removes jitter:

```python
alpha = 0.3
smooth = alpha * value + (1 - alpha) * smooth
```

**Dead zone**: ignore `abs(dx) + abs(dy) < 2` to stop drift when the hand is still.

**Rate**: count packets per second if timing matters (see `examples/v2.py` in the repo). Do not assume a fixed rate.

## Axes

- Tap Strap: https://raw.githubusercontent.com/TapWithUs/tap-python-sdk/master/docs/assets/TAP-axis-alpha.png
- TapXR: https://raw.githubusercontent.com/TapWithUs/tap-python-sdk/master/docs/assets/TAPXR-axis.png

If a direction is inverted on the user's device, flip the sign. Ask the user to test and tell you.

## Docs

- v2 events: https://tapwithus.github.io/tap-python-sdk/latest/v2/reference/events/
- v1 events: https://tapwithus.github.io/tap-python-sdk/latest/v1/reference/events/
- Spatial Control (v1 TapXR): https://tapwithus.github.io/tap-python-sdk/latest/v1/how-to/use-spatial-control/

---
name: tap-vision-models
description: Switch the Tap v2 vision model between TAPPING and AIR_GESTURE, set the op mode, and decode UnifiedAirGestures (swipes, pinches, holds, fist). Use for air gestures, pinch, swipe, fist, model switching, gesture mode vs tap mode, or v1 AirGestures.
---

# Vision models and air gestures

**v2 (`TapSDK2`) only** for model switching. v1 air gestures are at the end of this page.

The v2 device runs one vision model at a time:

| `ModelTypes` | Output | Callback |
|--------------|--------|----------|
| `TAPPING` | finger taps | `register_tap_events`: `cb(id, [tapcode])` |
| `AIR_GESTURE` | swipes, pinches, holds, fist | `register_air_gesture_events`: `cb(id, [code])` |

| `VisionSensorOpModes` | Meaning | Use with |
|-----------------------|---------|----------|
| `TRIGGER` | Run the model when a tap-like trigger occurs | `TAPPING` |
| `STREAM` | Run the model all the time | `AIR_GESTURE` |
| `STREAM_ON_TRIGGER` | Start streaming after a trigger | experiments |

## Enable and switch

```python
from tapsdk import DeviceFeatures, ModelTypes, TapSDK2, UnifiedAirGestures, VisionSensorOpModes, connect

async def use_air_gestures(sdk):
    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    await sdk.set_vision_sensor_model(ModelTypes.AIR_GESTURE)
    await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)

async def use_tapping(sdk):
    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    await sdk.set_vision_sensor_model(ModelTypes.TAPPING)
    await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)
```

Call these after `await sdk.start()`. You can switch at runtime, as often as needed. Read the current state with `await sdk.get_vision_sensor_model()` and `await sdk.get_vision_sensor_op_mode()` (each returns the enum; they time out after 2 s if the device does not answer).

To start from a clean state, turn all features off first:

```python
for feature in DeviceFeatures:
    await sdk.set_feature(feature, False)
```

## UnifiedAirGestures codes

Letters: A = thumb, B = index, C = middle, D = ring, E = pinky. "AB" = thumb touches index (pinch).

| Code | Name | Meaning |
|------|------|---------|
| 100 | `COMBINED_GESTURE_NONE` | No gesture / hand relaxed. Use it as "release" after a hold. |
| 101 | `COMBINED_GESTURE_LEFT` | Swipe left |
| 102 | `COMBINED_GESTURE_RIGHT` | Swipe right |
| 103 | `COMBINED_GESTURE_UP` | Swipe up |
| 104 | `COMBINED_GESTURE_DOWN` | Swipe down |
| 105-108 | `COMBINED_GESTURE_AB` / `AC` / `AD` / `AE` | Short pinch: thumb + index / middle / ring / pinky |
| 109 | `COMBINED_GESTURE_FIST` | Fist |
| 110-113 | `COMBINED_GESTURE_AB_HOLD` ... `AE_HOLD` | Pinch held |
| 114 | `COMBINED_GESTURE_FIST_HOLD` | Fist held |

```python
def on_air_gesture(identifier, data):
    gesture = UnifiedAirGestures(int(data[0]))
    if gesture is UnifiedAirGestures.COMBINED_GESTURE_LEFT:
        go_back()
```

The device sends gesture packets continuously in `STREAM` mode, so the same code repeats. To act once per gesture, act when the code **changes**, or ignore repeats within about 40 ms. Holds repeat until the hand relaxes and `NONE` (100) arrives. Wait for a few `NONE` packets in a row before you treat a hold as released (see `tap-dpad`).

## Example: switch models with a gesture

Fist-hold switches to tapping; all-five-finger tap (31) switches back:

```python
loop = asyncio.get_running_loop()

def on_air_gesture(identifier, data):
    if data[0] == UnifiedAirGestures.COMBINED_GESTURE_FIST_HOLD.value:
        loop.create_task(use_tapping(sdk))

def on_tap(identifier, data):
    if data[0] == 31:
        loop.create_task(use_air_gestures(sdk))
```

## Standby

`DeviceFeatures.STANDBY_GESTURE_DETECTION` lets the user put the device in standby with a gesture. `register_standby_state_events(cb(id, is_standby))` reports changes. `await sdk.set_standby_state(False)` wakes it; `await sdk.get_standby_state()` reads it.

## v1 air gestures (TapXR / Tap Strap 2 in Controller mode)

v1 has no model switching. In `InputModeController()`, `register_air_gesture_events` gives `cb(id, gesture: int)` that matches `AirGestures` (for example `UP_ONE_FINGER`, `LEFT_TWO_FINGERS`, `PINCH`, `THUMB_FINGER`, `STATE_FIST`). `register_air_gesture_state_events` gives `cb(id, MouseModes)` when the air-mouse state changes.

## Docs

- Features model: https://tapwithus.github.io/tap-python-sdk/latest/v2/explanation/features/
- Use features: https://tapwithus.github.io/tap-python-sdk/latest/v2/how-to/use-features/
- Enumerations: https://tapwithus.github.io/tap-python-sdk/latest/reference/enumerations/

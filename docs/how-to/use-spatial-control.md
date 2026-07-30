# Use Spatial Control (TapXR)

Spatial Control lets authorized apps force input type (air mouse vs tapping) and receive extended air-gesture state. It requires TapXR with experimental Spatial Control firmware and developer access. Request access via [Tap contact](https://www.tapwithus.com/contact-us/).

## Force input type

```python
from tapsdk import InputType

await tap.set_input_type(InputType.MOUSE)     # air / optical mouse
await tap.set_input_type(InputType.KEYBOARD)  # tapping / keyboard
await tap.set_input_type(InputType.AUTO)      # posture-based selection
```

Combine with a controller-capable [input mode](switch-input-modes.md) so your app receives events.

## Extended air gestures

Register both gesture and state callbacks:

```python
from tapsdk import AirGestures
from tapsdk.enumerations import MouseModes

tap.register_air_gesture_events(
    lambda id, g: print(AirGestures(g))
)
tap.register_air_gesture_state_events(
    lambda id, mode: print(MouseModes(mode))
)
```

State events report mouse-mode changes (`STDBY`, `AIR_MOUSE`, `OPTICAL1`, `OPTICAL2`). Gesture values include directional swipes, pinches, thumb contacts, and fist/open states — see [AirGestures](../reference/enumerations.md).

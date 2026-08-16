# Connect and listen for events

## Preferred: auto-detect, then assert v1

Turn the Tap on. Then:

```python
import asyncio
from tapsdk import InputModeController, TapSDK, connect

async def main():
    sdk = await connect()
    assert isinstance(sdk, TapSDK)

    sdk.register_connection_events(lambda tap: print("connected", tap))
    sdk.register_tap_events(lambda id, tapcode: print("tap", id, tapcode))
    await sdk.start()
    await sdk.set_input_mode(InputModeController())
    await asyncio.Event().wait()

asyncio.run(main())
```

`connect()` attaches to an already-connected Tap when possible, detects v1 vs v2 from GATT characteristics, and returns `TapSDK` or `TapSDK2`. It does **not** start notifications — register callbacks, then `await sdk.start()`.

On v1, `tapcode` is an `int`. Register `connection` callbacks before `start()` so they fire.

## Explicit `TapSDK`

```python
from tapsdk import TapSDK

tap = TapSDK()
tap.register_connection_events(on_connect)
await tap.run()  # connect_tap + start
```

## Connection and disconnection callbacks

```python
def on_connect(tap_sdk):
    print("connected", tap_sdk)

def on_disconnect(client):
    print("disconnected", client)

tap.register_connection_events(on_connect)
tap.register_disconnection_events(on_disconnect)
```

On v1, `on_connect` receives the SDK instance. `on_disconnect` receives the underlying Bleak client (platform-dependent).

## Subscribe to input events

```python
from tapsdk import AirGestures
from tapsdk.enumerations import MouseModes

tap.register_tap_events(lambda id, tapcode: print("tap", id, tapcode))
tap.register_mouse_events(lambda id, vx, vy, prox: print("mouse", vx, vy, prox))
tap.register_air_gesture_events(
    lambda id, gesture: print("gesture", AirGestures(gesture))
)
tap.register_air_gesture_state_events(
    lambda id, mode: print("mouse mode", MouseModes(mode))
)
tap.register_raw_data_events(lambda id, packets: print("raw", packets))
```

Tap and mouse events are only delivered when the device is in a controller-capable mode. See [Switch input modes](switch-input-modes.md).

## Keep the process alive

`start()` / `run()` return after notifications are set up. Keep the event loop running, for example:

```python
await tap.start()
await asyncio.Event().wait()
```

See also [`examples/basic.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/basic.py) and [`examples/connect.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/connect.py).

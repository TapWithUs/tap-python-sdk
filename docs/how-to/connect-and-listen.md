# Connect and listen for events

## Connect

Pair the Tap with the OS first. Then:

```python
import asyncio
from tapsdk import TapSDK

async def main():
    tap = TapSDK()
    await tap.run()

asyncio.run(main())
```

`run()` attaches to an already-connected Tap when possible. If none is found, it scans (and on Windows also polls for paired devices that reconnect without advertising).

## Connection and disconnection callbacks

Register callbacks before `await run()`:

```python
def on_connect(sdk):
    print("connected", sdk)

def on_disconnect(client):
    print("disconnected", client)

tap = TapSDK()
tap.register_connection_events(on_connect)
tap.register_disconnection_events(on_disconnect)
```

`on_connect` receives the `TapSDK` instance. `on_disconnect` receives the underlying Bleak client (platform-dependent).

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

`run()` returns after notifications are set up. Keep the event loop running, for example:

```python
await tap.run()
await asyncio.Event().wait()
```

Or follow the pattern in [`examples/basic.py`](../../examples/basic.py), which sleeps between mode changes.

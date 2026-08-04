# Connect and listen for events

## Preferred: auto-detect protocol

Pair the Tap with the OS first. Then:

```python
import asyncio
from tapsdk import connect

async def main():
    sdk = await connect()
    sdk.register_connection_events(lambda id: print("connected", id))
    sdk.register_tap_events(lambda id, tapcode: print("tap", id, tapcode))
    await sdk.start()
    await asyncio.Event().wait()

asyncio.run(main())
```

`connect()` attaches to an already-connected Tap when possible (same Windows
retrieve / scan / reconnect-poller path as before), detects v1 vs v2 from GATT
characteristics, and returns `TapSDK` or `TapSDK2`. It does **not** start
notifications — register callbacks, then `await sdk.start()`.

Tap callback shape differs by protocol: v1 passes `tapcode` as an `int`; v2
passes a one-element list (`[tapcode]`). Same finger bitmask either way.

Register `connection` callbacks before `start()` so they fire. Event callbacks
may also be added after `start()` for later events.

## Explicit protocol

If you know the firmware protocol:

```python
from tapsdk import TapSDK  # or TapSDK2

tap = TapSDK()
tap.register_connection_events(on_connect)
await tap.run()  # connect_tap + start
```

## Connection and disconnection callbacks

```python
def on_connect(sdk_or_serial):
    print("connected", sdk_or_serial)

def on_disconnect(client):
    print("disconnected", client)

sdk.register_connection_events(on_connect)
sdk.register_disconnection_events(on_disconnect)
```

On v1 (`TapSDK`), `on_connect` receives the SDK instance. On v2 (`TapSDK2`), it
receives the device serial number. `on_disconnect` receives the underlying Bleak
client (platform-dependent).

## Subscribe to input events (v1)

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

## Subscribe to input events (v2)

```python
from tapsdk import DeviceFeatures, UnifiedAirGestures

# tapcode is [int], e.g. [5] for thumb + middle — not a bare int
sdk.register_tap_events(lambda id, tapcode: print("tap", id, tapcode))
sdk.register_air_gesture_events(
    lambda id, data: print("gesture", UnifiedAirGestures(int(data[0])))
)
sdk.register_imu_motion_data_events(
    lambda id, motion: print("motion", motion)
)
sdk.register_raw_imu_data_events(lambda id, packets: print("raw imu", packets))
sdk.register_standby_state_events(
    lambda id, standby: print("standby" if standby else "active")
)

await sdk.start()
await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
await sdk.set_feature(DeviceFeatures.IMU_MOTION_DATA, True)
```

v2 has no `set_input_mode` — toggle streams with `DeviceFeatures`. Full walkthrough: [Use v2 features](use-v2-features.md).

## Keep the process alive

`start()` / `run()` return after notifications are set up. Keep the event loop running, for example:

```python
await sdk.start()
await asyncio.Event().wait()
```

See also [`examples/connect.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/connect.py) and [`examples/basic.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/basic.py).

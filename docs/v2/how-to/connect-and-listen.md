# Connect and listen for events

## Preferred: auto-detect, then assert v2

Turn the Tap on. Then:

```python
import asyncio
from tapsdk import DeviceFeatures, TapSDK2, connect

async def main():
    sdk = await connect()
    assert isinstance(sdk, TapSDK2)

    sdk.register_connection_events(
        lambda serial: print("connected", serial.decode("utf-8"))
    )
    sdk.register_tap_events(lambda id, tapcode: print("tap", id, tapcode))
    await sdk.start()
    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    await asyncio.Event().wait()

asyncio.run(main())
```

`connect()` attaches to an already-connected Tap when possible, detects v1 vs v2 from GATT characteristics, and returns `TapSDK` or `TapSDK2`. It does **not** start notifications — register callbacks, then `await sdk.start()`.

On v2, `tapcode` is a one-element list (`[tapcode]`). Register `connection` callbacks before `start()` so they fire.

## Explicit `TapSDK2`

```python
from tapsdk import TapSDK2

sdk = TapSDK2()
sdk.register_connection_events(on_connect)
await sdk.run()  # connect_tap + start
```

## Connection and disconnection callbacks

```python
def on_connect(serial_number):
    print("connected", serial_number.decode("utf-8"))

def on_disconnect(client):
    print("disconnected", client)

sdk.register_connection_events(on_connect)
sdk.register_disconnection_events(on_disconnect)
```

On v2, `on_connect` receives the device serial number (`bytes`). `on_disconnect` receives the underlying Bleak client (platform-dependent).

## Subscribe to input events

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

v2 has no `set_input_mode` — toggle streams with `DeviceFeatures`. Full walkthrough: [Use features](use-features.md).

## Keep the process alive

`start()` / `run()` return after notifications are set up. Keep the event loop running, for example:

```python
await sdk.start()
await asyncio.Event().wait()
```

See also [`examples/connect.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/connect.py) and [`examples/v2.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/v2.py).

# Getting started (`TapSDK2`)

This tutorial walks you through installing the SDK, connecting with `TapSDK2`, and printing tap events. By the end you will have a small asyncio program that talks to the TapXR developer firmware (and TapBand, same BLE API).

The [docs home](../../index.md) has one script that works for Tap Strap and TapXR. Use this page when you already know you have `set_feature`.

TapBand is coming soon and is not for sale yet. Join the [TapBand waitlist](https://www.tapwithus.com/tapband-waitlist/).

## What you need

- Python 3.10 or newer
- A TapXR on the TapXR developer firmware, or TapBand (GATT characteristic `c3ff000e` present)

If `connect()` returns `TapSDK`, use the [`TapSDK` tutorial](../../v1/tutorial/getting-started.md) instead.

## 1. Install the SDK

```bash
pip install tap-python-sdk
```

Then import with `from tapsdk import ...`. The PyPI name is `tap-python-sdk`; the import name is `tapsdk`.

On Linux, also install BlueZ tooling and add your user to the `bluetooth` group:

```bash
sudo apt-get install bluez-tools libbluetooth-dev
sudo usermod -G bluetooth -a "$USER"
su - "$USER"
```

## 2. Create a project file

Create `hello_tap.py`:

```python
import asyncio
from tapsdk import DeviceFeatures, ModelTypes, VisionSensorOpModes, connect


def on_tap(identifier, tapcode):
    code = tapcode[0] if isinstance(tapcode, (list, tuple)) else tapcode
    print(f"{identifier} tapped {code}")


def on_connect(serial_number):
    print("Connected:", serial_number.decode("utf-8"))


async def main():
    sdk = await connect()
    if not hasattr(sdk, "set_feature"):
        raise SystemExit("This device uses set_input_mode. See the TapSDK tutorial.")

    sdk.register_connection_events(on_connect)
    sdk.register_tap_events(on_tap)

    await sdk.start()
    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    await sdk.set_vision_sensor_model(ModelTypes.TAPPING)
    await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)

    await asyncio.Event().wait()


asyncio.run(main())
```

Or construct `TapSDK2()` and call `await sdk.run()` when you already know the firmware uses features.

## 3. Run it

1. Turn the Tap on.
2. Run:

```bash
python hello_tap.py
```

3. When you see `Connected: …`, tap with one or more fingers. You should see lines like:

```text
b'SERIAL…' tapped [5]
```

On `TapSDK2`, `tapcode` is a one-element list `[tapcode]`; the value is the same finger bitmask as `TapSDK` (bit 0 = thumb … bit 4 = pinky). See [Events](../reference/events.md).

Without `DeviceFeatures.MODEL_DETECTION` and a vision model, model events stay off.

## 4. What just happened

1. `await connect()` attaches to a Tap (already connected, or by scan) and returns `TapSDK2` for developer firmware. Notifications are **not** started yet.
2. `register_*` attaches callbacks (sync; register connection callbacks before `start()`).
3. `await sdk.start()` arms framed notifications, starts keepalive, and fires the connection callback with the serial number (`bytes`).
4. `set_feature(MODEL_DETECTION, True)` plus the tapping model enables tap delivery. There is no `set_input_mode` on `TapSDK2`.

## Next steps

- Enable IMU, vision, standby, or haptics: [How-to guides](../how-to/index.md)
- Full callback and command signatures: [API reference](../reference/index.md)
- Why features replace modes: [Explanation](../explanation/index.md)
- Auto-detect sample: [`examples/connect.py`](https://github.com/TapWithUs/tap-python-sdk/blob/master/examples/connect.py)
- Feature cycle demo: [`examples/features.py`](https://github.com/TapWithUs/tap-python-sdk/blob/master/examples/features.py)

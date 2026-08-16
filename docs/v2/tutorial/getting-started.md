# Getting started (v2)

This tutorial walks you through installing the SDK, connecting with `TapSDK2`, and printing tap events. By the end you will have a small asyncio program that talks to a framed-protocol Tap.

## What you need

- Python 3.9 or newer
- A TapBand or TapXR on **v2** framed firmware (GATT characteristic `c3ff000e` present)

If `connect()` returns `TapSDK`, use the [v1 tutorial](../../v1/tutorial/getting-started.md) instead.

## 1. Install the SDK

```bash
pip install tap-python-sdk
```

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
from tapsdk import DeviceFeatures, TapSDK2, connect


def on_tap(identifier, tapcode):
    print(f"{identifier} tapped {tapcode}")


def on_connect(serial_number):
    print("Connected:", serial_number.decode("utf-8"))


async def main():
    sdk = await connect()
    assert isinstance(sdk, TapSDK2), "Expected v2 TapSDK2 — this device is v1"

    sdk.register_connection_events(on_connect)
    sdk.register_tap_events(on_tap)

    await sdk.start()
    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)

    await asyncio.Event().wait()


asyncio.run(main())
```

Or construct `TapSDK2()` and call `await sdk.run()` when you already know the firmware is v2.

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

On v2, `tapcode` is a one-element list `[tapcode]`; the value is the same finger bitmask as v1 (bit 0 = thumb … bit 4 = pinky). See [Events](../reference/events.md).

Without `DeviceFeatures.MODEL_DETECTION`, model events stay off.

## 4. What just happened

1. `await connect()` attaches to a Tap (already connected, or by scan), detects protocol, and returns `TapSDK2` for v2. Notifications are **not** started yet.
2. `register_*` attaches callbacks (sync; register connection callbacks before `start()`).
3. `await sdk.start()` arms framed notifications, starts keepalive, and fires the connection callback with the serial number (`bytes`).
4. `set_feature(MODEL_DETECTION, True)` enables tap / model delivery. There is no `set_input_mode` on v2.

## Next steps

- Enable IMU, vision, standby, or haptics: [How-to guides](../how-to/index.md)
- Full callback and command signatures: [API reference](../reference/index.md)
- Why features replace modes: [Explanation](../explanation/index.md)
- Auto-detect sample: [`examples/connect.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/connect.py)
- Feature cycle demo: [`examples/v2.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/v2.py)

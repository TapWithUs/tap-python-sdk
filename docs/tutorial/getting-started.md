# Getting started

This tutorial walks you through installing the SDK, connecting to a Tap, and printing tap events. By the end you will have a small asyncio program that talks to a real device.

## What you need

- Python 3.9 or newer
- A Tap Strap or TapXR, updated with Tap Manager
- The Tap already paired with your computer over Bluetooth

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
from tapsdk import (
    DeviceFeatures,
    InputModeController,
    TapSDK2,
    connect,
)


def on_tap(identifier, tapcode):
    print(f"{identifier} tapped {tapcode}")


def on_connect(identifier):
    print("Connected:", identifier)


async def main():
    sdk = await connect()
    sdk.register_connection_events(on_connect)
    sdk.register_tap_events(on_tap)

    await sdk.start()
    if isinstance(sdk, TapSDK2):
        print("Protocol: v2")
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    else:
        print("Protocol: v1")
        await sdk.set_input_mode(InputModeController())

    # Keep receiving events
    await asyncio.Event().wait()


asyncio.run(main())
```

## 3. Run it

1. Turn the Tap on and confirm it is connected in the OS Bluetooth settings.
2. Run:

```bash
python hello_tap.py
```

3. When you see `Connected: …`, tap with one or more fingers. You should see lines like:

```text
# v1 (TapSDK) — tapcode is an int
XX:XX:XX:XX:XX:XX tapped 5

# v2 (TapSDK2) — tapcode is a one-element list
b'SERIAL…' tapped [5]
```

On both protocols the value is a finger bitmask (bit 0 = thumb … bit 4 = pinky); `5` / `[5]` means thumb + middle. On **v1**, `tapcode` is an `int`; on **v2**, it is `[tapcode]` (see [Events](../reference/events.md)).

The sample enables tap delivery after `start()`: Controller mode on v1, `DeviceFeatures.MODEL_DETECTION` on v2. Without those steps, Text-mode v1 stays silent and v2 model events stay off.

## 4. What just happened

1. `await connect()` attaches to an already-paired Tap (or scans), ensures GATT services are discovered, detects v1 vs v2 (`c3ff000e`), and returns `TapSDK` or `TapSDK2`. Notifications are **not** started yet.
2. `register_*` attaches callbacks (sync; register connection callbacks before `start()`).
3. `await sdk.start()` arms GATT notifications and fires the connection callback.
4. The sample then enables taps for the detected protocol (`set_input_mode` / `set_feature`).
5. On v1, `on_connect` receives the SDK instance; on v2, it receives the device serial number (bytes).

## Next steps

- Switch modes, stream sensors, or send haptics: [How-to guides](../how-to/index.md)
- Full callback and command signatures: [API reference](../reference/index.md)
- Why modes and sensors are designed this way: [Explanation](../explanation/index.md)
- Auto-detect sample: [`examples/connect.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/connect.py)
- Explicit v1 sample: [`examples/basic.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/basic.py)

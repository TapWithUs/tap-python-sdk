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
from tapsdk import TapSDK, InputModeController


def on_tap(identifier, tapcode):
    print(f"{identifier} tapped {tapcode}")


def on_connect(sdk):
    print("Connected to Tap")


async def main():
    tap = TapSDK()
    tap.register_connection_events(on_connect)
    tap.register_tap_events(on_tap)

    await tap.run()
    await tap.set_input_mode(InputModeController())

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

3. When you see `Connected to Tap`, switch to Controller mode is already requested — tap with one or more fingers. You should see lines like:

```text
XX:XX:XX:XX:XX:XX tapped 5
```

`tapcode` is a bitmask of fingers (bit 0 = thumb … bit 4 = pinky). `5` means thumb + middle.

## 4. What just happened

1. `TapSDK()` creates a BLE client for your platform.
2. `register_*` attaches callbacks (sync; call these before `run()`).
3. `await tap.run()` connects to an already-paired Tap, or scans until one appears.
4. `set_input_mode(InputModeController())` tells the device to send controller events to your app.

In Text mode (the default), the Tap behaves like a normal keyboard/mouse for the OS and does not emit tap events to the SDK.

## Next steps

- Switch modes, stream sensors, or send haptics: [How-to guides](../how-to/index.md)
- Full callback and command signatures: [API reference](../reference/index.md)
- Why modes and sensors are designed this way: [Explanation](../explanation/index.md)
- Runnable sample covering more events: [`examples/basic.py`](../../examples/basic.py)

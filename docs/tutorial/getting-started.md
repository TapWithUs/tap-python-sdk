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
from tapsdk import TapSDK2, connect


def on_tap(identifier, tapcode):
    print(f"{identifier} tapped {tapcode}")


def on_connect(identifier):
    print("Connected:", identifier)


async def main():
    sdk = await connect()
    sdk.register_connection_events(on_connect)
    sdk.register_tap_events(on_tap)

    await sdk.start()
    print("Protocol:", "v2" if isinstance(sdk, TapSDK2) else "v1")

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
XX:XX:XX:XX:XX:XX tapped 5
```

`tapcode` is a bitmask of fingers (bit 0 = thumb … bit 4 = pinky). `5` means thumb + middle.

On a **v1** device, enable Controller (or Controller+Text) so taps reach the SDK instead of only the OS keyboard. See [Switch input modes](../how-to/switch-input-modes.md). On **v2**, tap events arrive through the framed protocol without `set_input_mode`.

## 4. What just happened

1. `await connect()` attaches to an already-paired Tap (or scans), detects v1 vs v2 from GATT (`c3ff000e`), and returns `TapSDK` or `TapSDK2`. Notifications are **not** started yet.
2. `register_*` attaches callbacks (sync; register connection callbacks before `start()`).
3. `await sdk.start()` arms GATT notifications and fires the connection callback.
4. On v1, `on_connect` receives the SDK instance; on v2, it receives the device serial number (bytes).

In Text mode (v1 default), the Tap behaves like a normal keyboard/mouse for the OS and does not emit tap events to the SDK until you switch to Controller.

## Next steps

- Switch modes, stream sensors, or send haptics: [How-to guides](../how-to/index.md)
- Full callback and command signatures: [API reference](../reference/index.md)
- Why modes and sensors are designed this way: [Explanation](../explanation/index.md)
- Auto-detect sample: [`examples/connect.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/connect.py)
- Explicit v1 sample: [`examples/basic.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/basic.py)

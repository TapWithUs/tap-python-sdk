# Getting started (v1)

This tutorial walks you through installing the SDK, connecting with `TapSDK`, and printing tap events. By the end you will have a small asyncio program that talks to a classic-protocol Tap.

## What you need

- Python 3.9 or newer
- A Tap Strap or TapXR on **v1** firmware (no framed `c3ff000e` characteristic)
- The Tap already paired with your computer over Bluetooth

If `connect()` returns `TapSDK2`, use the [v2 tutorial](../../v2/tutorial/getting-started.md) instead.

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
from tapsdk import InputModeController, TapSDK, connect


def on_tap(identifier, tapcode):
    print(f"{identifier} tapped {tapcode}")


def on_connect(sdk):
    print("Connected:", sdk)


async def main():
    sdk = await connect()
    assert isinstance(sdk, TapSDK), "Expected v1 TapSDK — this device is v2"

    sdk.register_connection_events(on_connect)
    sdk.register_tap_events(on_tap)

    await sdk.start()
    await sdk.set_input_mode(InputModeController())

    await asyncio.Event().wait()


asyncio.run(main())
```

Or construct `TapSDK()` and call `await tap.run()` when you already know the firmware is v1.

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

`tapcode` is an `int` finger bitmask (bit 0 = thumb … bit 4 = pinky); `5` means thumb + middle. See [Events](../reference/events.md).

Without Controller (or Controller+Text) mode, Text-mode devices stay silent for SDK tap events.

## 4. What just happened

1. `await connect()` attaches to an already-paired Tap, detects protocol, and returns `TapSDK` for v1. Notifications are **not** started yet.
2. `register_*` attaches callbacks (sync; register connection callbacks before `start()`).
3. `await sdk.start()` arms GATT notifications and fires the connection callback with the SDK instance.
4. `set_input_mode(InputModeController())` enables app-bound tap delivery.

## Next steps

- Switch modes, stream sensors, or send haptics: [How-to guides](../how-to/index.md)
- Full callback and command signatures: [API reference](../reference/index.md)
- Why modes and sensors are designed this way: [Explanation](../explanation/index.md)
- Explicit v1 sample: [`examples/basic.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/basic.py)

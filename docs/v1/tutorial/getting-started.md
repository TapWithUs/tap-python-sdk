# Getting started (`TapSDK`)

This tutorial walks you through installing the SDK, connecting with `TapSDK`, and printing tap events. By the end you will have a small asyncio program that talks to input-mode firmware (Tap Strap / Tap Strap 2).

The [docs home](../../index.md) has one script that works for Tap Strap and TapXR. Use this page when you already know you have `set_input_mode`.

## What you need

- Python 3.10 or newer
- A Tap Strap or Tap Strap 2 (no framed `c3ff000e` characteristic)

If `connect()` returns `TapSDK2`, use the [`TapSDK2` tutorial](../../v2/tutorial/getting-started.md) instead.

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
from tapsdk import InputModeController, connect


def on_tap(identifier, tapcode):
    code = tapcode[0] if isinstance(tapcode, (list, tuple)) else tapcode
    print(f"{identifier} tapped {code}")


def on_connect(sdk):
    print("Connected:", sdk)


async def main():
    sdk = await connect()
    if not hasattr(sdk, "set_input_mode"):
        raise SystemExit("This device uses set_feature. See the TapSDK2 tutorial.")

    sdk.register_connection_events(on_connect)
    sdk.register_tap_events(on_tap)

    await sdk.start()
    await sdk.set_input_mode(InputModeController())

    await asyncio.Event().wait()


asyncio.run(main())
```

Or construct `TapSDK()` and call `await tap.run()` when you already know the firmware uses input modes.

## 3. Run it

1. Turn the Tap on.
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

1. `await connect()` attaches to a Tap (already connected, or by scan) and returns `TapSDK` for input-mode firmware. Notifications are **not** started yet.
2. `register_*` attaches callbacks (sync; register connection callbacks before `start()`).
3. `await sdk.start()` arms GATT notifications and fires the connection callback with the SDK instance.
4. `set_input_mode(InputModeController())` enables app-bound tap delivery.

## Next steps

- Switch modes, stream sensors, or send haptics: [How-to guides](../how-to/index.md)
- Full callback and command signatures: [API reference](../reference/index.md)
- Why modes and sensors are designed this way: [Explanation](../explanation/index.md)
- Explicit `TapSDK` sample: [`examples/basic.py`](https://github.com/TapWithUs/tap-python-sdk/blob/master/examples/basic.py)

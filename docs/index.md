# Tap Python SDK documentation

This package talks to Tap Strap, Tap Strap 2, TapXR, and TapBand over BLE. One install. One connect path. The SDK selects the firmware API for you.

## Devices

| Device | Status | Gestures |
|--------|--------|----------|
| Tap Strap, Tap Strap 2 | Available | Finger taps, mouse, and `AirGestures` in Controller mode |
| TapXR | Available. Use the TapXR developer firmware. | Full set: taps, thumb swipes up/down/left/right, thumb-to-finger pinches with hold, fist with hold |
| TapBand | Coming soon ([waitlist](https://www.tapwithus.com/tapband-waitlist/)). Same BLE API as TapXR. Not for sale yet. | Same full set as TapXR |

Python, Web, iOS, and Android all receive the **raw** gesture detections from the sensor. In Python that is `register_air_gesture_events`. iOS and Android also add a processed layer (click, drag, drop with debounce). Swipes and pinches are not iOS/Android-only.

## First program

Same script as [Getting started on the developer portal](https://dev.tapwithus.com/docs/getting-started/). Pair the Tap in OS Bluetooth settings, then:

```python
import asyncio
from tapsdk import (
    DeviceFeatures,
    InputModeController,
    ModelTypes,
    VisionSensorOpModes,
    connect,
)


def on_tap(identifier, tapcode):
    # tapcode is int 1..31 — bit0=thumb … bit4=pinky
    code = tapcode[0] if isinstance(tapcode, (list, tuple)) else tapcode
    print(f"{identifier} tapped {code} (0b{int(code):05b})")


async def main():
    sdk = await connect()
    sdk.register_tap_events(on_tap)
    await sdk.start()
    if hasattr(sdk, "set_input_mode"):
        await sdk.set_input_mode(InputModeController())
    else:
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
        await sdk.set_vision_sensor_model(ModelTypes.TAPPING)
        await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)

    print("Waiting for taps… (Ctrl+C to quit)")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
```

`connect()` returns `TapSDK` or `TapSDK2` from firmware. You do not pick a product version. Enable input after `start()`, or you get no tap events.

## Firmware APIs

| I want to… | Go to |
|------------|--------|
| Input modes on Tap Strap / Tap Strap 2 | [`TapSDK`](v1/index.md) |
| Features and air gestures on TapXR / TapBand | [`TapSDK2`](v2/index.md) |

Do not mix the two APIs on one page. Home is the shared first path.

## Shared

| Goal | Page |
|------|------|
| Install on macOS, Windows, or Linux | [Install the SDK](how-to/install.md) |
| Package exports and GATT map | [Package](reference/package.md) |
| Enumerations | [Enumerations](reference/enumerations.md) |
| Changelog | [Release notes](release-notes.md) |

## Package

- **PyPI:** [`tap-python-sdk`](https://pypi.org/project/tap-python-sdk/) (`pip install tap-python-sdk`)
- **Import name:** `tapsdk` (`from tapsdk import connect`)
- **Python:** 3.10+
- **Status:** production
- **Source:** [TapWithUs/tap-python-sdk](https://github.com/TapWithUs/tap-python-sdk)

## Platforms

macOS (CoreBluetooth), Windows 10+ (Bleak/WinRT), and Linux (BlueZ). `connect()` attaches to an already-connected Tap when one is present; otherwise it scans.

# Tap Python SDK documentation

This package talks to Tap Strap, Tap Strap 2, TapXR, and TapBand over BLE. Firmware uses one of two protocols. Pick the tree that matches your device (or what `connect()` returns).

## Pick a protocol

What your app can do depends on firmware protocol. Pick the tree that matches your device (or what `connect()` returns).

| Capability | [v1 (`TapSDK`)](v1/index.md) | [v2 (`TapSDK2`)](v2/index.md) |
|------------|------------------------------|-------------------------------|
| Hardware | Tap Strap, Tap Strap 2, TapXR | TapBand, TapXR |
| Finger taps to your app | ✅ | ✅ |
| HID keyboard / mouse | ✅ | ❌ |
| Pointer / mouse motion | ✅ | ✅ |
| Air gestures | Partial | Full |
| Raw finger accelerometers | Tap Strap / Tap Strap 2 only | ❌ |
| Raw IMU | ✅ | ✅ |
| Vision model / stream control | ❌ | ✅ |
| Standby state | ❌ | ✅ |
| Haptic sequences | ✅ | ✅ |

Both protocols stay first-class in the same package. Prefer `await connect()`: it detects the protocol and returns `TapSDK` or `TapSDK2`. Then follow that protocol’s section.

## Shared

| Goal | Page |
|------|------|
| Install on macOS, Windows, or Linux | [Install the SDK](how-to/install.md) |
| Package exports and GATT map | [Package](reference/package.md) |
| Enumerations | [Enumerations](reference/enumerations.md) |
| Changelog | [Release notes](release-notes.md) |

## Package

- **PyPI:** [`tap-python-sdk`](https://pypi.org/project/tap-python-sdk/)
- **Import name:** `tapsdk`
- **Python:** 3.9+
- **Status:** beta
- **Source:** [TapWithUs/tap-python-sdk](https://github.com/TapWithUs/tap-python-sdk)

## Platforms

macOS (CoreBluetooth), Windows 10+ (Bleak/WinRT), and Linux (BlueZ). `connect()` attaches to an already-connected Tap when one is present; otherwise it scans.

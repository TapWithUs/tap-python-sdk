---
name: tap-python-sdk
description: >-
  Build Python host apps with the Tap BLE SDK (tap-python-sdk / import tapsdk).
  Use when connecting Tap Strap or TapXR, receiving tap bitmasks, mouse or
  air-gesture events, enabling Controller mode or MODEL_DETECTION, or when the
  user mentions TapSDK, TapSDK2, connect(), or silent/zero tap callbacks.
---

# Tap Python SDK (app builders)

BLE SDK for **Tap Strap** / Strap 2 and **TapXR**. Package **`tap-python-sdk`** on PyPI; import **`tapsdk`**. Python **≥ 3.10** (align with current 0.9.x on PyPI — check `tapsdk/__version__.py`).

**TapBand** has the broadest gestures but is **not** a public SDK first-run target. If mentioned, link https://www.tapwithus.com/tapband-waitlist/. XR gestures are a **subset** of Band — do **not** invent a per-gesture missing list.

## Install

```bash
pip install tap-python-sdk
```

## Connect order (required)

1. **Pair in OS Bluetooth first.** Official SDKs do **not** scan for unpaired devices.
2. `sdk = await connect()` → `TapSDK` (v1) or `TapSDK2` (v2) from GATT.
3. Register callbacks (`register_tap_events`, connection, …).
4. `await sdk.start()` — arms notifications.
5. **Unlock app taps** (Text/HID boot mode yields **zero** callbacks):
   - **v1:** `await sdk.set_input_mode(InputModeController())`
   - **v2:** `await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)`
6. Keep the asyncio loop alive (`await asyncio.Event().wait()`).

Canonical sample: `examples/connect.py`. Portal:
[Getting started](https://dev.tapwithus.com/docs/getting-started/) ·
[How Tap works](https://dev.tapwithus.com/docs/how-tap-works/).

### Minimal pattern

```python
import asyncio
from tapsdk import DeviceFeatures, InputModeController, TapSDK2, connect

async def main():
    sdk = await connect()
    sdk.register_tap_events(lambda id, code: print(id, code))
    await sdk.start()
    if isinstance(sdk, TapSDK2):
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    else:
        await sdk.set_input_mode(InputModeController())
    await asyncio.Event().wait()

asyncio.run(main())
```

## Controller vs Text vs v2

| Path | What to call | Result |
|------|----------------|--------|
| Text (default) | nothing | HID keyboard — **no** SDK taps |
| v1 Controller | `InputModeController()` | Finger bitmasks to app |
| v2 | `DeviceFeatures.MODEL_DETECTION` | Model/tap events; **no** `set_input_mode` |

## Bitmask

Tap codes **1–31**: bit0 = thumb … bit4 = pinky. Example `5` = thumb + middle.
v2 often delivers `[n]` (one-element list).

## Zero events — check these first

1. Forgot Controller / MODEL_DETECTION after `start()`.
2. Not paired in OS Bluetooth.
3. Process exited (no wait loop).
4. v1 APIs used on v2 (or reverse).
5. Device off / stale firmware.

## Footguns / honesty

- **Spatial Control** (`set_input_type`): authorized **TapXR** / **v1 only** — **not** on `TapSDK2`. Mention as out-of-scope, not first-run.
- Do **not** invent GATT UUIDs, gesture tables, or undocumented APIs.
- Do **not** claim TapBand is a documented public first-run SDK target.

## More

- Repo agent brief: `AGENTS.md`
- Hosted docs: https://tapwithus.github.io/tap-python-sdk/
- In-repo: `docs/v1/tutorial/getting-started.md`, `docs/v2/tutorial/getting-started.md`

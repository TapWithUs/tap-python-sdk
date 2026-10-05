# Tap Python SDK

Connect order, every time: `await connect()`, then `register_*` callbacks, then `await sdk.start()`, then enable input, then keep the loop alive. `connect()` alone delivers no taps.

> Docs: https://tapwithus.github.io/tap-python-sdk/
> Skills: https://github.com/TapWithUs/tap-python-sdk/tree/master/plugins/tap-python-sdk/skills
> Package: `pip install tap-python-sdk` (Python 3.10+, macOS / Windows / Linux, import name `tapsdk`)

BLE SDK for Tap Strap, Tap Strap 2, TapXR, and TapBand. It receives taps, air gestures, mouse / IMU motion, and raw sensor data, and sends haptics and mode commands.

## Two protocols, one entry point

`await connect()` attaches to the Tap, detects the firmware protocol, and returns:

- `TapSDK` (**v1**, classic firmware): input modes (`InputModeText`, `InputModeController`, `InputModeControllerText`, `InputModeRaw`)
- `TapSDK2` (**v2**, framed firmware): `DeviceFeatures` switches, vision models (`ModelTypes.TAPPING` / `AIR_GESTURE`), IMU motion with roll / pitch / yaw

Check with `isinstance(sdk, TapSDK2)`. Write code that handles both unless the user names the device.

## Required order

```python
import asyncio
from tapsdk import DeviceFeatures, InputModeController, ModelTypes, TapSDK2, VisionSensorOpModes, connect

def first(v):                      # v1 sends int, v2 sends [int]
    return v[0] if isinstance(v, (list, tuple)) else v

async def main():
    sdk = await connect()                                   # 1. connect + detect
    sdk.register_tap_events(lambda i, t: print(first(t)))  # 2. register callbacks
    await sdk.start()                                       # 3. start notifications
    if isinstance(sdk, TapSDK2):                            # 4. enable input
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
        await sdk.set_vision_sensor_model(ModelTypes.TAPPING)
        await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)
    else:
        await sdk.set_input_mode(InputModeController())
    await asyncio.Event().wait()                            # 5. keep running

asyncio.run(main())
```

## Callback signatures

| Register | v1 `TapSDK` | v2 `TapSDK2` |
|----------|-------------|--------------|
| `register_tap_events` | `(id, tapcode: int)` | `(id, [tapcode])` |
| `register_air_gesture_events` | `(id, gesture: int)` -> `AirGestures` | `(id, [code])` -> `UnifiedAirGestures` |
| `register_mouse_events` | `(id, vx, vy, proximity)` | n/a |
| `register_imu_motion_data_events` | n/a | `(id, (dx, dy, is_mouse, [roll, pitch, yaw]))` |
| `register_raw_data_events` | `(id, [{"type", "ts", "payload"}])` | same (alias of `register_raw_imu_data_events`) |
| `register_air_gesture_state_events` | `(id, MouseModes)` | n/a |
| `register_standby_state_events` | n/a | `(id, is_standby: bool)` |
| `register_connection_events` | `(sdk)` | `(serial: bytes)` |
| `register_disconnection_events` | `(client)` | `(client)` |

Tapcode bits: thumb = 1, index = 2, middle = 4, ring = 8, pinky = 16.

## Gotchas

- v1 boots in **Text mode**: the Tap types on the OS keyboard and the SDK gets **no** taps. Call `set_input_mode(InputModeController())` after `start()`.
- v2 sends nothing until features are on: `MODEL_DETECTION` + a vision model for taps / gestures, `IMU_MOTION_DATA` for motion, `RAW_IMU_DATA` for raw.
- v2 runs one vision model at a time: `TAPPING` (with `TRIGGER`) or `AIR_GESTURE` (with `STREAM`).
- Register callbacks before `start()`. `start()` returns right away; keep the event loop alive.
- Callbacks run on the Bluetooth notification path. Keep them short; never block. Schedule async work with `asyncio.get_running_loop().create_task(...)` or push to an `asyncio.Queue`.
- Haptics: `await sdk.send_vibration_sequence([on_ms, off_ms, ...])`, 10-2550 ms per value, max 18 values.
- Do not invent APIs, UUIDs, or enum values. Check `tapsdk/enumerations.py` and the docs.
- Update firmware with the Tap Manager app. v1 raw sensors need Developer mode in Tap Manager.
- Test with the real device and ask the user what they see. There is no simulator.

## Skills

| Skill | Use for |
|-------|---------|
| `tap-getting-started` | install, pairing, connect, quickstart script, troubleshooting |
| `tap-tapping` | tapcodes, finger combos, double taps, shortcuts, haptics |
| `tap-vision-models` | v2 model switching, `UnifiedAirGestures` (swipe, pinch, hold, fist) |
| `tap-imu-motion` | pointer, tilt, roll / pitch / yaw, v1 mouse |
| `tap-raw-sensors` | raw accelerometer / gyro, sensitivity, CSV logging |
| `tap-knob` | v2 pinch-hold + twist to change a value |
| `tap-dpad` | v2 swipes, pinch select, hold to rotate or drag |
| `tap-build-an-app` | complete apps: queue pattern, browser / pygame / keyboard output |

Skill files live in `plugins/tap-python-sdk/skills/<name>/SKILL.md` in the SDK repository.

## Contributing to this repository

Only for work on the SDK itself (not for apps that use it):

- Use the local virtual environment: `.venv/bin/python`, `.venv/bin/pip install -e ".[dev]"`.
- Test: `.venv/bin/pytest`. Lint: `.venv/bin/flake8`.
- Docs follow Diátaxis per protocol (see `.cursor/rules/diataxis-docs.mdc`); `mkdocs build --strict` must pass.
- Add a user-facing entry under `## Unreleased` in `docs/release-notes.md` for every PR.
- When the public API changes, update the matching skill in `plugins/tap-python-sdk/skills/` and this file.

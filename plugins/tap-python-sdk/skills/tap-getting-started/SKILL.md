---
name: tap-getting-started
description: First skill for any Tap app. The connect order is await connect(), then register_* callbacks, then await sdk.start(), then enable input. connect() alone delivers no taps. Use for install, pairing, "connect to my Tap", setup, or no tap events.
---

# Tap getting started

Works for both protocols. `connect()` returns `TapSDK` (v1, classic firmware) or `TapSDK2` (v2, framed firmware). Write code that handles both unless the user says which device they have.

## 1. Ask the user (once)

- Which device: Tap Strap, Tap Strap 2, TapXR, or TapBand?
- Which OS: macOS, Windows, or Linux?
- Is the Tap turned on, charged, and paired in the OS Bluetooth settings?
- Is the firmware up to date (update it in the Tap Manager app)?

## 2. Install

Use a project virtual environment. Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install tap-python-sdk
python -c "from tapsdk import connect; print('ok')"
```

Platform notes:

- macOS: the terminal or IDE asks for Bluetooth permission on the first run. Accept it (System Settings > Privacy & Security > Bluetooth).
- Windows 10+: no extra steps.
- Linux: `sudo apt-get install bluez-tools libbluetooth-dev`, then `sudo usermod -G bluetooth -a $USER` and log in again. The device name must start with `Tap`.

## 3. Connect and listen (v1/v2 agnostic)

Copy [scripts/quickstart.py](scripts/quickstart.py) into the project and run it. The required order is:

1. `sdk = await connect()`: attach and detect the protocol. Notifications are not running yet.
2. `sdk.register_*(callback)`: register every callback before `start()`.
3. `await sdk.start()`: start notifications.
4. Enable input:
   - v1: `await sdk.set_input_mode(InputModeController())`. v1 boots in Text mode, which types on the OS keyboard and sends **no** tap events to the SDK.
   - v2: `set_feature(DeviceFeatures.MODEL_DETECTION, True)`, then pick a vision model (see the `tap-vision-models` skill).
5. Keep the loop alive: `await asyncio.Event().wait()`.

## 4. Callback shapes differ between v1 and v2

| Callback | v1 `TapSDK` | v2 `TapSDK2` |
|----------|-------------|--------------|
| `register_tap_events` | `cb(identifier, tapcode: int)` | `cb(identifier, [tapcode])` |
| `register_air_gesture_events` | `cb(identifier, gesture: int)` (`AirGestures`) | `cb(identifier, [code])` (`UnifiedAirGestures`) |
| `register_connection_events` | `cb(sdk)` | `cb(serial: bytes)` |
| `register_disconnection_events` | `cb(client)` | `cb(client)` |
| mouse / motion | `register_mouse_events`: `cb(id, vx, vy, proximity)` | `register_imu_motion_data_events`: `cb(id, (dx, dy, is_mouse, [roll, pitch, yaw]))` |

Normalize with:

```python
def first(value):
    return value[0] if isinstance(value, (list, tuple)) else value
```

Check the protocol with `isinstance(sdk, TapSDK2)`.

## 5. Callback rules

- Callbacks run on the Bluetooth notification path. Keep them short. Do not `await` or block in them.
- To run async work from a callback, use `asyncio.get_running_loop().create_task(...)`, or put the event on an `asyncio.Queue` (see `tap-build-an-app`).
- `send_vibration_sequence([on_ms, off_ms, on_ms, ...])` gives haptic feedback (10-2550 ms per value, up to 18 values).
- `await sdk.get_device_info()` reads the name, firmware, and battery.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No device found / scan timeout | Turn the Tap on, pair it in OS Bluetooth settings, close Tap Manager and other apps that hold the connection, then retry. |
| Connected but no tap events (v1) | Set `InputModeController()` after `start()`. |
| Connected but no tap events (v2) | Enable `MODEL_DETECTION` and set the `TAPPING` model with `TRIGGER` op mode. |
| Letters appear in the editor when tapping | Device is in Text mode (v1). Set Controller mode. |
| `ConnectionError: GATT services not available` | Turn Bluetooth off and on, unpair and pair again. |
| macOS: nothing happens, no error | Grant Bluetooth permission to the terminal / IDE, then restart it. |
| Linux: permission denied | Add the user to the `bluetooth` group and log in again. |
| Events stop after some seconds | Keep the process alive (`asyncio.Event().wait()`); do not exit `main()`. |

Debug logging: `logging.basicConfig(level=logging.INFO); logging.getLogger("tapsdk").setLevel(logging.DEBUG)`.

## More

- Docs: https://tapwithus.github.io/tap-python-sdk/
- Next skills: `tap-tapping`, `tap-vision-models`, `tap-imu-motion`, `tap-raw-sensors`, `tap-knob`, `tap-dpad`, `tap-build-an-app`

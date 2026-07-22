# TapSDK

Primary entry point. Import with `from tapsdk import TapSDK`.

Construction imports a platform BLE backend (macOS, Windows, or Linux). Creating `TapSDK` on an unsupported platform, or with the wrong Bleak pin, raises `ImportError`.

## Constructor

```python
TapSDK(address=None)
```

| Parameter | Description |
|-----------|-------------|
| `address` | Optional BLE address / platform device id. On Linux, if omitted, the SDK picks a connected device whose name starts with `Tap`. |

## Connection

### `async run()`

Connect to a Tap and start GATT notifications for tap, mouse, air-gesture, and raw characteristics.

- Prefer an already OS-connected / paired device.
- Otherwise scan until a Tap advertising the Tap service UUID is found.
- On Windows, also polls for paired devices that reconnect without advertising.
- Invokes the connection callback when notifications are armed.

Returns when setup finishes; it does not block forever. Keep the asyncio loop alive yourself.

## Commands

### `async set_input_mode(input_mode, identifier=None)`

Write an [input mode](input-modes.md) command to the device.

| Parameter | Description |
|-----------|-------------|
| `input_mode` | Instance of `InputModeText`, `InputModeController`, `InputModeControllerText`, or `InputModeRaw` |
| `identifier` | Reserved for multi-device use; currently unused |

Starts periodic mode refresh on first call. Changing raw sensitivities while already in a different raw configuration is rejected with a warning.

### `async set_input_type(input_type, identifier=None)`

TapXR Spatial Control only. Force mouse, keyboard, or automatic input selection.

| Parameter | Description |
|-----------|-------------|
| `input_type` | `InputType.MOUSE`, `InputType.KEYBOARD`, or `InputType.AUTO` |
| `identifier` | Reserved; currently unused |

### `async send_vibration_sequence(sequence, identifier=None)`

Send haptic on/off periods.

| Parameter | Description |
|-----------|-------------|
| `sequence` | List of integers (ms). Each value is clamped to 0–2550 and stored as `value // 10`. Max length 18. |
| `identifier` | Reserved; currently unused |

### `async get_device_info() -> DeviceInfo`

Read public device information. Requires a bonded connection (DIS/BAS characteristics are encrypted on Tap firmware). Missing characteristics yield `None` for that field.

Returns a `DeviceInfo` dataclass:

| Field | Description |
|-------|-------------|
| `name` | Device name |
| `fw_version` | Firmware revision |
| `fw_version2` | Secondary firmware version (`None` if absent) |
| `model_version` | Model version as hex (e.g. `0x2A`; `None` if absent) |
| `hardware_revision` | Hardware revision |
| `serial_number` | Serial number |
| `manufacturer` | Manufacturer name |
| `software_revision` | Bootloader revision on Tap |
| `battery_level` | 0–100 |

```python
from tapsdk import DeviceInfo

info = await tap_device.get_device_info()
print(info.name, info.fw_version, info.model_version, info.battery_level)
```

## Event registration

All `register_*` methods are synchronous. Pass a callable; pass `None` is not required to clear (re-assign by registering again). See [Events](events.md).

| Method | Callback signature |
|--------|-------------------|
| `register_connection_events` | `(tap_sdk)` |
| `register_disconnection_events` | `(client)` — Bleak disconnected callback |
| `register_tap_events` | `(identifier, tapcode)` |
| `register_mouse_events` | `(identifier, vx, vy, proximity)` |
| `register_air_gesture_events` | `(identifier, gesture)` |
| `register_air_gesture_state_events` | `(identifier, mouse_mode)` |
| `register_raw_data_events` | `(identifier, packets)` |

## Attributes (runtime)

| Attribute | Meaning |
|-----------|---------|
| `client` | Underlying `TapClient` / `BleakClient` |
| `input_mode` | Last requested `InputMode` instance |
| `input_type` | Last requested `InputType` |
| `mouse_mode` | Current `MouseModes` from air-gesture state notifications |

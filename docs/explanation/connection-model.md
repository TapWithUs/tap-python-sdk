# Connection model

The Tap is a Bluetooth Low Energy peripheral. This SDK does not use HID for app control; it opens a GATT session with Bleak and talks to Tap’s proprietary service. Mode / feature commands and streams differ by protocol generation.

## Preferred entry: `connect()` then `start()`

```text
await connect()  →  register callbacks  →  await sdk.start()
```

1. `connect()` calls shared `connect_tap()` (attach / scan / Windows retrieve), ensures GATT services are populated (`ensure_gatt_services`), then `detect_protocol()`: if characteristic `c3ff000e` is present, return `TapSDK2`; else `TapSDK`. Empty service caches raise instead of defaulting to v1.
2. Notifications are **not** started yet — register callbacks first.
3. `start()` arms protocol-specific notifies and fires the connection callback.

`TapSDK.run()` / `TapSDK2.run()` still work: connect if needed, then `start()`, in one call.

Both classes share `tapsdk._transport` (`TapClient`, `connect_tap`) and `tapsdk.device_info` (`get_device_info`).

## Why pair with the OS first

On every platform the most reliable path is: pair in system Bluetooth settings, ensure the device is connected (or connectable), then call `connect()` (or `run()`). The SDK then attaches to that session instead of racing a cold advertisement scan.

Platform differences matter:

- **macOS** retrieves already-connected peripherals that expose the Tap service.
- **Windows** uses WinRT to find connected Tap devices and opens a GATT session without Bleak’s normal connect wait (which can hang if the session is already active). If nothing is connected, it scans and also polls for paired reconnects that do not advertise.
- **Linux** lists BlueZ devices with `bt-device` and connects to names starting with `Tap`.

## v1 vs v2 GATT paths

| | v1 (`TapSDK`) | v2 (`TapSDK2`) |
|--|---------------|----------------|
| Detect | No `c3ff000e` | Has `c3ff000e` |
| Events | Separate notify chars (tap, mouse, air-gesture, NUS raw) | Single framed notify `c3ff000e` |
| Commands | NUS RX (`set_input_mode` / `set_input_type`) + UI haptics char | Framed writes on `c3ff000f` (`set_feature`, vision, IMU, haptics, standby) |
| Keepalive | Mode refresh task after first mode write | Periodic keepalive after `start()` |
| Connection callback arg | SDK instance | Serial number (bytes) |

## Single device today

Method signatures accept an `identifier` argument on commands, but the SDK currently drives one `TapClient` at a time. Multi-device support is a separate concern from documentation of the present API.

## Notifications vs commands

- **Commands** are GATT writes (NUS / UI on v1; framed write char on v2).
- **Events** are GATT notifications parsed into callback arguments.

On v1, after you set a mode, a background refresh task rewrites mode and input type periodically so a flaky link is less likely to leave the device in the wrong state. On v2, keepalive writes keep the framed session alive.

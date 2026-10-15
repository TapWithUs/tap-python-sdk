# Connection model

The Tap is a Bluetooth Low Energy peripheral. This SDK does not use HID for app control; it opens a GATT session with Bleak and talks to Tap’s proprietary service.

## Preferred entry: `connect()` then `start()`

```text
await connect()  →  assert TapSDK2  →  register callbacks  →  await sdk.start()
```

1. `connect()` calls shared `connect_tap()` (attach if already connected, otherwise scan), ensures GATT services are populated (`ensure_gatt_services`), then `detect_protocol()`: if characteristic `c3ff000e` is present, return `TapSDK2`. Empty service caches raise instead of guessing.
2. Notifications are **not** started yet — register callbacks first.
3. `start()` arms framed notifications, reads serial, starts keepalive, and fires the connection callback with the serial number (`bytes`).

`TapSDK2.run()` still works: connect if needed, then `start()`, in one call.

`TapSDK2` shares `tapsdk._transport` (`TapClient`, `connect_tap`) and `tapsdk.device_info` (`get_device_info`) with `TapSDK`.

## How `connect()` finds a device

`connect()` attaches to an already-connected Tap when one is present. Otherwise it scans.

On Windows, pass `skip_scan=True` to skip the live BLE scan fallback entirely and only attach to a Tap Windows already reports as connected/paired (via AEP) or an explicitly given `address`; if that attempt doesn't succeed, `connect()` raises `ConnectionError` immediately instead of scanning and waiting. This has no effect on macOS/Linux.

An unbonded/unpaired GATT connection (typically the live-scan fallback path) can expose a reduced, v1-looking characteristic set on a v2 device even though it's a v2 device — Windows omits characteristics requiring a security level the current link doesn't satisfy. If you see a Tap misdetected as v1, or `"Characteristic ... was not found!"`, fully unpair the Tap in Windows Settings, re-pair via **Settings > Bluetooth & devices > Add device**, power-cycle the Tap, then reconnect. Background: [Windows BLE connect notes](../../windows-ble-connect-notes.md).

## v2 GATT path

| Concern | Behavior |
|---------|----------|
| Detect | Has `c3ff000e` |
| Events | Single framed notify `c3ff000e` |
| Commands | Framed writes on `c3ff000f` (`set_feature`, vision, IMU, haptics, standby) |
| Keepalive | Periodic keepalive after `start()` |
| Connection callback arg | Serial number (bytes) |

## Single device today

Method signatures accept an `identifier` argument on commands, but the SDK currently drives one `TapClient` at a time. Multi-device support is a separate concern from documentation of the present API.

## Notifications vs commands

- **Commands** are GATT writes on the framed write characteristic.
- **Events** are framed notifications parsed into callback arguments.

Keepalive writes keep the framed session alive after `start()`.

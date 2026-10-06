# Connection model

The Tap is a Bluetooth Low Energy peripheral. This SDK does not use HID for app control; it opens a GATT session with Bleak and talks to Tap’s proprietary service.

## Preferred entry: `connect()` then `start()`

```text
await connect()  →  assert TapSDK  →  register callbacks  →  await sdk.start()
```

1. `connect()` calls shared `connect_tap()` (attach if already connected, otherwise scan), ensures GATT services are populated (`ensure_gatt_services`), then `detect_protocol()`: if characteristic `c3ff000e` is absent, return `TapSDK`. Empty service caches raise instead of guessing.
2. Notifications are **not** started yet — register callbacks first.
3. `start()` arms v1 notify characteristics and fires the connection callback with the SDK instance.

`TapSDK.run()` still works: connect if needed, then `start()`, in one call.

`TapSDK` shares `tapsdk._transport` (`TapClient`, `connect_tap`) and `tapsdk.device_info` (`get_device_info`) with `TapSDK2`.

## How `connect()` finds a device

`connect()` attaches to an already-connected Tap when one is present. Otherwise it scans.

On Windows, pass `skip_scan=True` to skip the live BLE scan fallback entirely and only attach to a Tap Windows already reports as connected/paired (via AEP) or an explicitly given `address`; if that attempt doesn't succeed, `connect()` raises `ConnectionError` immediately instead of scanning and waiting. This has no effect on macOS/Linux.

An unbonded/unpaired GATT connection (typically the live-scan fallback path) can expose a reduced, v1-looking characteristic set on a v2 device even though it's a v2 device — Windows omits characteristics requiring a security level the current link doesn't satisfy. If you see a Tap misdetected as v1, or `"Characteristic ... was not found!"`, fully unpair the Tap in Windows Settings, re-pair via **Settings > Bluetooth & devices > Add device**, power-cycle the Tap, then reconnect. Background: [Windows BLE connect notes](../../windows-ble-connect-notes.md).

## v1 GATT path

| Concern | Behavior |
|---------|----------|
| Detect | No `c3ff000e` |
| Events | Separate notify chars (tap, mouse, air-gesture, NUS raw) |
| Commands | NUS RX (`set_input_mode` / `set_input_type`) + UI haptics char |
| Keepalive | Mode refresh task after first mode write |
| Connection callback arg | SDK instance |

## Single device today

Method signatures accept an `identifier` argument on commands, but the SDK currently drives one `TapClient` at a time. Multi-device support is a separate concern from documentation of the present API.

## Notifications vs commands

- **Commands** are GATT writes (NUS / UI).
- **Events** are GATT notifications parsed into callback arguments.

After you set a mode, a background refresh task rewrites mode and input type periodically so a flaky link is less likely to leave the device in the wrong state.

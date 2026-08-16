# Features model

On v2 (`TapSDK2`), the device does not use Text / Controller / Raw mode writes. Streams and behaviors are toggled with [`DeviceFeatures`](../../reference/enumerations.md#devicefeatures) over framed GATT writes.

## Why features instead of modes

v1 modes are a single personality for the whole device (who receives HID vs app events). v2 firmware exposes independent streams: model detection (taps / air gestures), IMU motion, raw IMU, standby, and vision sensor settings. Your app enables only what it needs.

## Typical flow

1. `await connect()` → `TapSDK2`
2. Register callbacks
3. `await sdk.start()` (notifications + keepalive)
4. `set_feature(...)` / vision / IMU helpers as needed

## Related

- Recipes: [Use features](../how-to/use-features.md)
- API: [TapSDK2](../reference/tapsdk2.md)
- Wire path: [Connection model](connection-model.md)

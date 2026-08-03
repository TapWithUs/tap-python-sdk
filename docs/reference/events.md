# Events

Callbacks are registered with `TapSDK` / `TapSDK2` `register_*` methods. They run on the asyncio / Bleak notification path — keep them short or schedule work onto another task.

## Connection

### v1 (`TapSDK`)

```text
register_connection_events(cb)
cb(tap_sdk: TapSDK) -> None
```

Called after GATT notifications are started successfully.

### v2 (`TapSDK2`)

```text
register_connection_events(cb)
cb(serial_number: bytes) -> None
```

Called after framed notifications start, serial is read, and keepalive begins. Decode with `serial_number.decode("utf-8")` when printing.

### Disconnect (both)

```text
register_disconnection_events(cb)
cb(client) -> None
```

Passed through to Bleak’s disconnected callback.

## Tap

```text
register_tap_events(cb)
cb(identifier, tapcode) -> None
```

On **v1**, `tapcode` is an `int` in **1–31**. Bit 0 (LSb) is the thumb; bit 4 is the pinky. Example: `5` (`0b00101`) = thumb + middle.

On **v2**, the second argument is a one-element list `[tapcode]` from the framed parser (same bitmask meaning).

While air-mouse mode is active on v1, tapcodes `2` and `4` are remapped into air-gesture handling instead of the tap callback.

## Mouse (v1 only)

```text
register_mouse_events(cb)
cb(identifier, vx: int, vy: int, proximity: bool) -> None
```

`vx` / `vy` are signed velocities. `proximity` is `True` when a surface is detected.

## Air gesture

### v1

```text
register_air_gesture_events(cb)
cb(identifier, gesture: int) -> None
```

`gesture` matches [`AirGestures`](enumerations.md).

```text
register_air_gesture_state_events(cb)
cb(identifier, mouse_mode: MouseModes) -> None
```

Fired when the device reports mouse-mode changes (`0x14` payload).

### v2

```text
register_air_gesture_events(cb)
cb(identifier, gesture_data) -> None
```

`gesture_data` is a one-element list; `gesture_data[0]` matches [`UnifiedAirGestures`](enumerations.md#unifiedairgestures). TapSDK2 has no air-gesture **state** register.

## Raw sensors (v1)

```text
register_raw_data_events(cb)
cb(identifier, packets: list[dict]) -> None
```

Each dict:

| Key | Type | Description |
|-----|------|-------------|
| `type` | `str` | `"imu"` or `"accl"` |
| `ts` | `int` | Device timestamp (ms) |
| `payload` | `list` | Sample values (scaled or raw LSB) |

## Raw IMU (v2)

```text
register_raw_imu_data_events(cb)   # or register_raw_data_events
cb(identifier, packets: list[dict]) -> None
```

Same packet dict shape as v1 raw sensors (`type` / `ts` / `payload`). Enable with `DeviceFeatures.RAW_IMU_DATA` and optionally `set_imu_sensitivity(..., scaled=True)`.

## IMU motion (v2 only)

```text
register_imu_motion_data_events(cb)
cb(identifier, motion_data) -> None
```

`motion_data` is `(dx, dy, is_mouse, euler_angles)` where `euler_angles` is `[roll, pitch, yaw]` (signed ints). Enable with `DeviceFeatures.IMU_MOTION_DATA`.

## Standby state (v2 only)

```text
register_standby_state_events(cb)
cb(identifier, is_standby: bool) -> None
```

Also resolved by `get_standby_state()`. Enable related detection with `DeviceFeatures.STANDBY_GESTURE_DETECTION` when needed.

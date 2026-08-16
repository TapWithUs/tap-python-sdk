# Events

Callbacks are registered with `TapSDK2` `register_*` methods. They run on the asyncio / Bleak notification path — keep them short or schedule work onto another task.

## Connection

```text
register_connection_events(cb)
cb(serial_number: bytes) -> None
```

Called after framed notifications start, serial is read, and keepalive begins. Decode with `serial_number.decode("utf-8")` when printing.

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

The second argument is a one-element list `[tapcode]` from the framed parser. The bitmask meaning matches v1: bit 0 (LSb) is the thumb; bit 4 is the pinky. Example: `[5]` = thumb + middle.

## Air gesture

```text
register_air_gesture_events(cb)
cb(identifier, gesture_data) -> None
```

`gesture_data` is a one-element list; `gesture_data[0]` matches [`UnifiedAirGestures`](../../reference/enumerations.md#unifiedairgestures). TapSDK2 has no air-gesture **state** register.

## Raw IMU

```text
register_raw_imu_data_events(cb)   # or register_raw_data_events
cb(identifier, packets: list[dict]) -> None
```

Each dict:

| Key | Type | Description |
|-----|------|-------------|
| `type` | `str` | `"imu"` or `"accl"` |
| `ts` | `int` | Device timestamp (ms) |
| `payload` | `list` | Sample values (scaled or raw LSB) |

Enable with `DeviceFeatures.RAW_IMU_DATA` and optionally `set_imu_sensitivity(..., scaled=True)`.

## IMU motion

```text
register_imu_motion_data_events(cb)
cb(identifier, motion_data) -> None
```

`motion_data` is `(dx, dy, is_mouse, euler_angles)` where `euler_angles` is `[roll, pitch, yaw]` (signed ints). Enable with `DeviceFeatures.IMU_MOTION_DATA`.

## Standby state

```text
register_standby_state_events(cb)
cb(identifier, is_standby: bool) -> None
```

Also resolved by `get_standby_state()`. Enable related detection with `DeviceFeatures.STANDBY_GESTURE_DETECTION` when needed.

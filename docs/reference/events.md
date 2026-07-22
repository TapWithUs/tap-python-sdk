# Events

Callbacks are registered with `TapSDK.register_*` methods. They run on the asyncio / Bleak notification path — keep them short or schedule work onto another task.

## Connection

```text
register_connection_events(cb)
cb(tap_sdk: TapSDK) -> None
```

Called after GATT notifications are started successfully.

```text
register_disconnection_events(cb)
cb(client) -> None
```

Passed through to Bleak’s disconnected callback.

## Tap

```text
register_tap_events(cb)
cb(identifier, tapcode: int) -> None
```

`tapcode` is an 8-bit value in **1–31**. Bit 0 (LSb) is the thumb; bit 4 is the pinky. Example: `5` (`0b00101`) = thumb + middle.

While air-mouse mode is active, tapcodes `2` and `4` are remapped into air-gesture handling instead of the tap callback.

## Mouse

```text
register_mouse_events(cb)
cb(identifier, vx: int, vy: int, proximity: bool) -> None
```

`vx` / `vy` are signed velocities. `proximity` is `True` when a surface is detected.

## Air gesture

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

## Raw sensors

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

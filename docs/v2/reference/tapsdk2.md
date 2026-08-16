# TapSDK2

v2 framed-protocol entry point. Import with `from tapsdk import TapSDK2`, or prefer [`connect()`](#connect) which returns `TapSDK` or `TapSDK2` (use [v1 docs](../../v1/index.md) when it returns `TapSDK`).

Commands and events use framed messages on `c3ff000e` (notify) / `c3ff000f` (write). There is no NUS `set_input_mode` path — enable streams with [`DeviceFeatures`](../../reference/enumerations.md#devicefeatures).

## `connect`

```python
from tapsdk import connect

sdk = await connect(address=None, **kwargs)
```

Attach to a Tap, detect v1 vs v2 (`c3ff000e` present → v2), and return `TapSDK` or `TapSDK2` with an already-connected client.

| Parameter | Description |
|-----------|-------------|
| `address` | Optional BLE address / platform device id (same rules as the constructor) |
| `**kwargs` | Forwarded to the SDK constructor (for example `keepalive_timeout` on v2) |

Does **not** start notifications. Register callbacks, then `await sdk.start()`.

## Constructor

```python
TapSDK2(client=None, address=None, *, get_timeout=2.0, keepalive_timeout=10)
```

| Parameter | Description |
|-----------|-------------|
| `client` | Optional already-connected `TapClient` (from `connect()`) |
| `address` | Optional BLE address / platform device id |
| `get_timeout` | Seconds to wait for get-request replies (default `2.0`) |
| `keepalive_timeout` | Seconds between keepalive writes after `start()` (default `10`) |

## Connection

### `async start()`

Start notifications on the framed read characteristic, read the serial number, start keepalive, then invoke the connection callback with the serial (bytes). Raises `ConnectionError` if the client is not connected.

### `async run()`

Connect via shared `connect_tap()` if needed, then call `start()`.

## Commands

### Features

```python
await sdk.set_feature(DeviceFeatures.RAW_IMU_DATA, True)
enabled = await sdk.get_feature(DeviceFeatures.RAW_IMU_DATA)
```

| Method | Description |
|--------|-------------|
| `async set_feature(feature, enable, identifier=None)` | Enable or disable a [`DeviceFeatures`](../../reference/enumerations.md#devicefeatures) stream |
| `async get_feature(feature, identifier=None) -> bool` | Read current feature enable state |

### Vision sensor

| Method | Returns |
|--------|---------|
| `async set_vision_sensor_op_mode(mode: VisionSensorOpModes)` | — |
| `async get_vision_sensor_op_mode() -> VisionSensorOpModes` | Current op mode |
| `async set_vision_sensor_model(model: ModelTypes)` | — |
| `async get_vision_sensor_model() -> ModelTypes` | Current model |

### IMU sensitivity

```python
await sdk.set_imu_sensitivity(
    xl_sensitivity=ImuAcclSensitivity.G2,
    gyro_sensitivity=ImuGyroSensitivity.DPS125,
    scaled=True,
)
gyro, xl = await sdk.get_imu_sensitivity()
```

| Parameter | Description |
|-----------|-------------|
| `xl_sensitivity` | Thumb IMU accelerometer range |
| `gyro_sensitivity` | Thumb IMU gyroscope range |
| `scaled` | If `True`, raw IMU callbacks use mg/mdps scale factors |
| `finger_accl_sens` | Optional finger accel enum used only for local scaling |

### Haptics and keepalive

| Method | Description |
|--------|-------------|
| `async set_haptic_pattern(sequence)` | Periods in ms; each clamped to 0–2550 as `value // 10`; max 18 values |
| `async send_vibration_sequence(sequence)` | Alias for `set_haptic_pattern` |
| `async send_keepalive_message()` | Manual keepalive (also sent periodically after `start()`) |

### Standby

| Method | Returns |
|--------|---------|
| `async set_standby_state(standby: bool)` | — |
| `async get_standby_state() -> bool` | `True` if device reports standby |

### Device info

`async get_device_info() -> DeviceInfo` — shared DIS/BAS reader via `tapsdk.device_info`.

## Event registration

See [Events](events.md) for callback shapes. Methods:

| Method | Notes |
|--------|-------|
| `register_connection_events` | `(serial_number: bytes)` |
| `register_disconnection_events` | `(client)` |
| `register_tap_events` | Tap gesture from model detection |
| `register_air_gesture_events` | Unified air-gesture codes |
| `register_raw_imu_data_events` | Raw IMU packet batches |
| `register_raw_data_events` | Alias for `register_raw_imu_data_events` |
| `register_imu_motion_data_events` | Motion deltas + Euler angles |
| `register_standby_state_events` | Standby boolean |

TapSDK2 does **not** expose `register_mouse_events` or `register_air_gesture_state_events`.

## Attributes (runtime)

| Attribute | Meaning |
|-----------|---------|
| `client` | Underlying `TapClient` / `BleakClient` |
| `device_serial_number` | Serial bytes after `start()`; `None` before |
| `keep_alive_manager` | `KeepAliveManager` instance |

# Input modes

Defined in `tapsdk.inputmodes`. Prefer importing the concrete classes from `tapsdk`.

## Base: `InputMode`

| Attribute / method | Description |
|--------------------|-------------|
| `COMMAND_PREFIX` | `bytearray([0x3, 0xc, 0x0])` |
| `get_command()` | Full GATT write payload: prefix + mode `code` |
| `name` | Human-readable label |

## `InputModeText`

Normal Tap operation for the OS. Mode code `0x00`. SDK tap events are not produced.

## `InputModeController`

Controller-only. Mode code `0x01`. Device sends tap / mouse / gesture events to the SDK.

## `InputModeControllerText`

Combined Text + Controller. Mode code `0x05`.

## `InputModeRaw`

```python
InputModeRaw(
    scaled=False,
    finger_accl_sens=None,
    imu_gyro_sens=None,
    imu_accl_sens=None,
)
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `scaled` | `False` | If `True`, raw payloads are multiplied by sensitivity scale factors (mg / mdps) |
| `finger_accl_sens` | `FingerAcclSensitivity.G2` | Finger accelerometer range |
| `imu_gyro_sens` | `ImuGyroSensitivity.DPS125` | IMU gyro range |
| `imu_accl_sens` | `ImuAcclSensitivity.G2` | IMU accelerometer range |

Mode code: `0x0a` followed by the three sensitivity enum values.

### `RawSensorsSensitivity`

Internal helper used by `InputModeRaw`.

| Method | Returns |
|--------|---------|
| `tolist()` | `[finger, gyro, imu_accl]` integer values for the command |
| `get_scale_factors()` | `[finger_mg_per_lsb, gyro_mdps_per_lsb, imu_mg_per_lsb]` |

## `input_type_command(input_type)`

Builds the Spatial Control write: `bytearray([0x3, 0xd, 0x0, input_type.value])`. Used by `TapSDK.set_input_type`.

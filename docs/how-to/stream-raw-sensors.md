# Stream raw sensor data

Enable Developer mode in the Tap Manager app first. Raw mode is available on Tap Strap / Tap Strap 2 (finger accelerometers) and Tap Strap 2 / TapXR (thumb IMU).

## Enter raw mode

```python
from tapsdk import InputModeRaw
from tapsdk.enumerations import (
    FingerAcclSensitivity,
    ImuGyroSensitivity,
    ImuAcclSensitivity,
)

tap.register_raw_data_events(on_raw)

await tap.set_input_mode(InputModeRaw(
    scaled=True,
    finger_accl_sens=FingerAcclSensitivity.G4,
    imu_gyro_sens=ImuGyroSensitivity.DPS250,
    imu_accl_sens=ImuAcclSensitivity.G4,
))
```

With `scaled=True`, accelerometer values are in mg and gyro values in mdps. With `scaled=False`, payloads are raw LSB counts.

## Handle packets

```python
def on_raw(identifier, packets):
    for packet in packets:
        # packet["type"]: "imu" or "accl"
        # packet["ts"]:   ms timestamp from the device clock
        # packet["payload"]: list of samples
        print(identifier, packet["type"], packet["ts"], packet["payload"])
```

- **`imu`:** 6 values — gyro x/y/z then accelerometer x/y/z on the thumb.
- **`accl`:** 15 values — 3-axis accelerometer for thumb, index, middle, ring, pinky (Tap Strap family).

## Sensitivity options

See [`FingerAcclSensitivity`](../reference/enumerations.md), [`ImuGyroSensitivity`](../reference/enumerations.md), and [`ImuAcclSensitivity`](../reference/enumerations.md).

For coordinate frames and sampling rates, see [Raw sensors explained](../explanation/raw-sensors.md).

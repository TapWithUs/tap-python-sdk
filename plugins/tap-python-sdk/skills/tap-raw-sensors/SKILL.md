---
name: tap-raw-sensors
description: Stream raw accelerometer and gyroscope samples from a Tap (v1 raw mode or v2 RAW_IMU_DATA), set sensitivity and scaling, log to CSV, and plot. Use for raw sensors, raw IMU, accelerometer, gyro, data logging, datasets, custom gesture recognition, or research.
---

# Raw sensors

For research, datasets, and custom gesture models. For pointer movement or orientation, prefer `tap-imu-motion` (less data, already processed).

## Packet format (both protocols)

The callback gets a list of packets: `cb(identifier, packets: list[dict])`.

| Key | Type | Meaning |
|-----|------|---------|
| `type` | `str` | `"imu"` (thumb IMU) or `"accl"` (finger accelerometers) |
| `ts` | `int` | Device timestamp in ms (device clock, not wall time) |
| `payload` | `list` | `imu`: `[gyro_x, gyro_y, gyro_z, accl_x, accl_y, accl_z]` (6 values). `accl`: 5 fingers x `[x, y, z]` (15 values, thumb first). |

Units: raw LSB counts, or **mdps** (gyro) and **mg** (accelerometer) when scaling is on. Rate is about 200 Hz per sensor, delivered in batches.

## v2 (`TapSDK2`)

```python
from tapsdk import DeviceFeatures
from tapsdk.enumerations import ImuAcclSensitivity, ImuGyroSensitivity

sdk.register_raw_imu_data_events(on_raw)       # register_raw_data_events also works
await sdk.start()
await sdk.set_feature(DeviceFeatures.RAW_IMU_DATA, True)
await sdk.set_imu_sensitivity(
    xl_sensitivity=ImuAcclSensitivity.G2,      # G2 / G4 / G8 / G16
    gyro_sensitivity=ImuGyroSensitivity.DPS125,  # DPS125 ... DPS2000
    scaled=True,                               # payload in mg / mdps
)
# later
await sdk.set_feature(DeviceFeatures.RAW_IMU_DATA, False)
```

`await sdk.get_imu_sensitivity()` returns `(ImuGyroSensitivity, ImuAcclSensitivity)`.

## v1 (`TapSDK`)

```python
from tapsdk import InputModeController, InputModeRaw
from tapsdk.enumerations import FingerAcclSensitivity, ImuAcclSensitivity, ImuGyroSensitivity

sdk.register_raw_data_events(on_raw)
await sdk.start()
await sdk.set_input_mode(InputModeRaw(
    scaled=True,
    finger_accl_sens=FingerAcclSensitivity.G2,   # default G2
    imu_gyro_sens=ImuGyroSensitivity.DPS125,     # default DPS125
    imu_accl_sens=ImuAcclSensitivity.G2,         # default G2
))
# leave raw mode
await sdk.set_input_mode(InputModeController())
```

- To change sensitivity, leave raw mode first, then enter it again with new values. The SDK ignores a raw-to-raw change.
- Raw streaming needs **Developer mode** turned on in Tap Manager.
- Tap Strap streams finger accelerometers; Tap Strap 2 and TapXR also stream the thumb IMU.

## Log to CSV

Copy [scripts/log_csv.py](scripts/log_csv.py): `python log_csv.py --seconds 30 --out raw.csv`. It works on v1 and v2.

## Plot (optional, in the user's app)

```python
# pip install pandas matplotlib
import pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv("raw.csv", header=None)
imu = df[df[2] == "imu"]
imu.plot(x=1, y=[6, 7, 8], title="thumb accelerometer (mg)")   # accl_x/y/z columns
plt.show()
```

## Tips

- Callbacks get batches at high rate. Append to a list or queue; write files or plot outside the callback.
- Use `ts` for timing between samples, not `time.time()`.
- Lower sensitivity (G2, DPS125) gives more resolution; raise it for fast, strong motion so values do not clip.

## Docs

- v1 raw sensors: https://tapwithus.github.io/tap-python-sdk/latest/v1/how-to/stream-raw-sensors/
- v1 raw explanation (axes, scaling): https://tapwithus.github.io/tap-python-sdk/latest/v1/explanation/raw-sensors/
- v2 events: https://tapwithus.github.io/tap-python-sdk/latest/v2/reference/events/

# Use features

Recipes for `TapSDK2` (framed protocol). Prefer `await connect()` so protocol detection picks v2 automatically; or construct `TapSDK2()` when you know the firmware.

There is no `set_input_mode`. Enable streams with [`DeviceFeatures`](../../reference/enumerations.md#devicefeatures).

## Connect and enable features

```python
import asyncio
from tapsdk import DeviceFeatures, TapSDK2, connect
from tapsdk.enumerations import (
    ImuAcclSensitivity,
    ImuGyroSensitivity,
    ModelTypes,
    VisionSensorOpModes,
)

async def main():
    sdk = await connect()
    assert isinstance(sdk, TapSDK2)

    sdk.register_tap_events(lambda id, code: print("tap", code))
    sdk.register_air_gesture_events(lambda id, data: print("air", data))
    sdk.register_imu_motion_data_events(lambda id, motion: print("motion", motion))
    sdk.register_raw_imu_data_events(lambda id, packets: print("raw", len(packets)))
    sdk.register_standby_state_events(lambda id, s: print("standby", s))

    await sdk.start()

    # Turn unrelated streams off first (example pattern)
    for feature in DeviceFeatures:
        await sdk.set_feature(feature, False)

    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    await sdk.set_vision_sensor_model(ModelTypes.AIR_GESTURE)
    await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)

    await asyncio.Event().wait()

asyncio.run(main())
```

## Stream IMU motion

```python
await sdk.set_feature(DeviceFeatures.IMU_MOTION_DATA, True)
# callback: (identifier, (dx, dy, is_mouse, [roll, pitch, yaw]))
```

## Stream raw IMU

```python
await sdk.set_feature(DeviceFeatures.RAW_IMU_DATA, True)
await sdk.set_imu_sensitivity(
    xl_sensitivity=ImuAcclSensitivity.G2,
    gyro_sensitivity=ImuGyroSensitivity.DPS125,
    scaled=True,
)
```

Packet dicts use `type` / `ts` / `payload`. See [Events](../reference/events.md#raw-imu).

## Standby

```python
await sdk.set_feature(DeviceFeatures.STANDBY_GESTURE_DETECTION, True)
await sdk.set_standby_state(False)
is_standby = await sdk.get_standby_state()
```

## Haptics

```python
await sdk.send_vibration_sequence([500, 200, 500])
# same as await sdk.set_haptic_pattern([...])
```

Full demo that cycles features: [`examples/v2.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/v2.py). API surface: [TapSDK2 reference](../reference/tapsdk2.md).

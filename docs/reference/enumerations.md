# Enumerations

All live in `tapsdk.enumerations`. `InputType`, `AirGestures`, `DeviceFeatures`, `UnifiedAirGestures`, `VisionSensorOpModes`, and `ModelTypes` are also re-exported from `tapsdk`.

## `InputType`

Spatial Control input selection.

| Member | Value |
|--------|-------|
| `MOUSE` | 1 |
| `KEYBOARD` | 2 |
| `AUTO` | 3 |

## `MouseModes`

Reported by air-gesture state events (`0x14` notifications) on v1.

| Member | Value |
|--------|-------|
| `STDBY` | 0 |
| `AIR_MOUSE` | 1 |
| `OPTICAL1` | 2 |
| `OPTICAL2` | 3 |

## `AirGestures`

v1 air-gesture codes (and remapped tap codes in air-mouse).

| Member | Value |
|--------|-------|
| `NONE` | 0 |
| `GENERAL` | 1 |
| `UP_ONE_FINGER` | 2 |
| `UP_TWO_FINGERS` | 3 |
| `DOWN_ONE_FINGER` | 4 |
| `DOWN_TWO_FINGERS` | 5 |
| `LEFT_ONE_FINGER` | 6 |
| `LEFT_TWO_FINGERS` | 7 |
| `RIGHT_ONE_FINGER` | 8 |
| `RIGHT_TWO_FINGERS` | 9 |
| `PINCH` | 10 |
| `THUMB_FINGER` | 12 |
| `THUMB_MIDDLE` | 14 |
| `STATE_OPEN` | 100 |
| `STATE_THUMB_FINGER` | 101 |
| `STATE_THUMB_MIDDLE` | 102 |
| `STATE_THUMB_RING` | 103 |
| `STATE_THUMB_PINKY` | 104 |
| `STATE_FIST` | 105 |

## `UnifiedAirGestures`

v2 unified / combined air-gesture codes from `TapSDK2` air-gesture events.

| Member | Value |
|--------|-------|
| `COMBINED_GESTURE_NONE` | 100 |
| `COMBINED_GESTURE_LEFT` | 101 |
| `COMBINED_GESTURE_RIGHT` | 102 |
| `COMBINED_GESTURE_UP` | 103 |
| `COMBINED_GESTURE_DOWN` | 104 |
| `COMBINED_GESTURE_AB` | 105 |
| `COMBINED_GESTURE_AC` | 106 |
| `COMBINED_GESTURE_AD` | 107 |
| `COMBINED_GESTURE_AE` | 108 |
| `COMBINED_GESTURE_FIST` | 109 |
| `COMBINED_GESTURE_AB_HOLD` | 110 |
| `COMBINED_GESTURE_AC_HOLD` | 111 |
| `COMBINED_GESTURE_AD_HOLD` | 112 |
| `COMBINED_GESTURE_AE_HOLD` | 113 |
| `COMBINED_GESTURE_FIST_HOLD` | 114 |

## `VisionSensorOpModes`

v2 vision sensor operating mode (`set_vision_sensor_op_mode`).

| Member | Value |
|--------|-------|
| `TRIGGER` | 0 |
| `STREAM_ON_TRIGGER` | 1 |
| `STREAM` | 2 |

## `ModelTypes`

v2 vision / model selection (`set_vision_sensor_model`).

| Member | Value |
|--------|-------|
| `TAPPING` | 0 |
| `AIR_GESTURE` | 1 |

## `DeviceFeatures`

v2 streams toggled with `TapSDK2.set_feature` / `get_feature`.

| Member | Value | Notes |
|--------|-------|-------|
| `RAW_IMU_DATA` | 0 | Raw IMU packet stream |
| `MODEL_DETECTION` | 1 | Tap / air-gesture model events |
| `IMU_MOTION_DATA` | 2 | Motion deltas + Euler |
| `TRIGGER_DETECTIONS` | 3 | Reserved; not implemented yet |
| `STANDBY_GESTURE_DETECTION` | 4 | Standby gesture events |

## `FingerAcclSensitivity`

| Member | Approx. range |
|--------|----------------|
| `G2` | ±2 g |
| `G4` | ±4 g |
| `G8` | ±8 g |
| `G16` | ±16 g |

## `ImuGyroSensitivity`

| Member | Approx. range |
|--------|----------------|
| `DPS125` | ±125 °/s |
| `DPS250` | ±250 °/s |
| `DPS500` | ±500 °/s |
| `DPS1000` | ±1000 °/s |
| `DPS2000` | ±2000 °/s |

## `ImuAcclSensitivity`

| Member | Approx. range |
|--------|----------------|
| `G2` | ±2 g |
| `G4` | ±4 g |
| `G8` | ±8 g |
| `G16` | ±16 g |

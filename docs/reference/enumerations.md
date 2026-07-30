# Enumerations

All live in `tapsdk.enumerations`. `InputType` and `AirGestures` are also re-exported from `tapsdk`.

## `InputType`

Spatial Control input selection.

| Member | Value |
|--------|-------|
| `MOUSE` | 1 |
| `KEYBOARD` | 2 |
| `AUTO` | 3 |

## `MouseModes`

Reported by air-gesture state events (`0x14` notifications).

| Member | Value |
|--------|-------|
| `STDBY` | 0 |
| `AIR_MOUSE` | 1 |
| `OPTICAL1` | 2 |
| `OPTICAL2` | 3 |

## `AirGestures`

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

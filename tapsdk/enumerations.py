from enum import Enum


class MouseModes(Enum):
    """Mouse / air-mouse state reported by air-gesture state events."""

    STDBY = 0
    AIR_MOUSE = 1
    OPTICAL1 = 2
    OPTICAL2 = 3


class InputType(Enum):
    """Spatial Control input modality (TapXR experimental firmware)."""

    MOUSE = 1
    KEYBOARD = 2
    AUTO = 3


class AirGestures(Enum):
    """Air-gesture and spatial-state codes from gesture notifications."""

    NONE = 0
    GENERAL = 1
    UP_ONE_FINGER = 2
    UP_TWO_FINGERS = 3
    DOWN_ONE_FINGER = 4
    DOWN_TWO_FINGERS = 5
    LEFT_ONE_FINGER = 6
    LEFT_TWO_FINGERS = 7
    RIGHT_ONE_FINGER = 8
    RIGHT_TWO_FINGERS = 9
    PINCH = 10
    THUMB_FINGER = 12
    THUMB_MIDDLE = 14
    STATE_OPEN = 100
    STATE_THUMB_FINGER = 101
    STATE_THUMB_MIDDLE = 102
    STATE_THUMB_RING = 103
    STATE_THUMB_PINKY = 104
    STATE_FIST = 105


class FingerAcclSensitivity(Enum):
    """Dynamic range for per-finger accelerometers in raw mode."""

    G2 = 1
    G4 = 2
    G8 = 3
    G16 = 4


class ImuGyroSensitivity(Enum):
    """Dynamic range for the thumb IMU gyroscope in raw mode."""

    DPS125 = 1
    DPS250 = 2
    DPS500 = 3
    DPS1000 = 4
    DPS2000 = 5


class ImuAcclSensitivity(Enum):
    """Dynamic range for the thumb IMU accelerometer in raw mode."""

    G2 = 1
    G4 = 2
    G8 = 3
    G16 = 4

from enum import Enum


class MouseModes(Enum):
    STDBY = 0
    AIR_MOUSE = 1
    OPTICAL1 = 2
    OPTICAL2 = 3


class InputType(Enum):
    MOUSE = 1
    KEYBOARD = 2
    AUTO = 3


class AirGestures(Enum):
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
    G2 = 1
    G4 = 2
    G8 = 3
    G16 = 4


class ImuGyroSensitivity(Enum):
    DPS125 = 1
    DPS250 = 2
    DPS500 = 3
    DPS1000 = 4
    DPS2000 = 5


class ImuAcclSensitivity(Enum):
    G2 = 1
    G4 = 2
    G8 = 3
    G16 = 4


class UnifiedAirGestures(Enum):
    COMBINED_GESTURE_NONE = 100
    COMBINED_GESTURE_LEFT = 101
    COMBINED_GESTURE_RIGHT = 102
    COMBINED_GESTURE_UP = 103
    COMBINED_GESTURE_DOWN = 104
    COMBINED_GESTURE_AB = 105
    COMBINED_GESTURE_AC = 106
    COMBINED_GESTURE_AD = 107
    COMBINED_GESTURE_AE = 108
    COMBINED_GESTURE_FIST = 109
    COMBINED_GESTURE_AB_HOLD = 110
    COMBINED_GESTURE_AC_HOLD = 111
    COMBINED_GESTURE_AD_HOLD = 112
    COMBINED_GESTURE_AE_HOLD = 113
    COMBINED_GESTURE_FIST_HOLD = 114


class VisionSensorOpModes(Enum):
    TRIGGER = 0
    STREAM_ON_TRIGGER = 1
    STREAM = 2


class ModelTypes(Enum):
    TAPPING = 0
    AIR_GESTURE = 1


class DeviceFeatures(Enum):
    RAW_IMU_DATA = 0
    MODEL_DETECTION = 1
    IMU_MOTION_DATA = 2
    TRIGGER_DETECTIONS = 3      # Not implemented yet
    STANDBY_GESTURE_DETECTION = 4

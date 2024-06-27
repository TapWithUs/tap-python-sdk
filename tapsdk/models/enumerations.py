from enum import Enum


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


class MouseModes(Enum):
    STDBY = 0
    AIR_MOUSE = 1
    OPTICAL1 = 2
    OPTICAL2 = 3

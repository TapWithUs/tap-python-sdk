from enum import Enum

class AirGestures(Enum):
	NONE                = 0
	GENERAL             = 1
	UP_ONE_FINGER		= 2
	UP_TWO_FINGERS      = 3
	DOWN_ONE_FINGER		= 4
	DOWN_TWO_FINGERS    = 5
	LEFT_ONE_FINGER		= 6
	LEFT_TWO_FINGERS    = 7
	RIGHT_ONE_FINGER	= 8
	RIGHT_TWO_FINGERS   = 9
	THUMB_FINGER		= 12
	THUMB_MIDDLE   		= 14

  # class AirGestures(IntEnum):
    #     Undefined = -1000,
    #     OneFingerUp = 2,
    #     TwoFingersUp = 3,
    #     OnefingerDown = 4,
    #     TwoFingersDown = 5,
    #     OneFingerLeft = 6,
    #     TwoFingersLeft = 7,
    #     OneFingerRight = 8,
    #     TwoFingersRight = 9,
    #     IndexToThumbTouch = 1000,
    #     MiddleToThumbTouch = 1001

class MouseModes(Enum):
	STDBY               = 0
	AIR_MOUSE           = 1
	OPTICAL1            = 2
	OPTICAL2            = 3
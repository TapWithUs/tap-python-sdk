from enum import Enum

class AirGestures(Enum):
	NONE                = 0
	GENERAL             = 1
	UP                  = 2
	UP_TWO_FINGERS      = 3
	DOWN                = 4
	DOWN_TWO_FINGERS    = 5
	LEFT                = 6
	LEFT_TWO_FINGERS    = 7
	RIGHT               = 8
	RIGHT_TWO_FINGERS   = 9

class MouseModes(Enum):
	STDBY               = 0
	AIR_MOUSE           = 1
	OPTICAL1            = 2
	OPTICAL2            = 3
import abc
from enum import Enum, IntEnum


class TapSDKBase(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def register_tap_events(self, listener):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_mouse_events(self, listener):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_connection_events(self, listener):
        raise NotImplementedError()
   
    @abc.abstractmethod
    def register_raw_data_events(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_disconnection_events(self, listener):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_air_gesture_events(self, listener):
        raise NotImplementedError

    @abc.abstractmethod
    def set_input_mode(self, mode, tap_identifier):
        raise NotImplementedError()

    @abc.abstractmethod
    def set_raw_sensors_mode(self, device_accel_sens, imu_gyro_sens, imu_accel_sens, identifier):
        raise NotImplementedError

    @abc.abstractmethod
    def send_vibration_sequence(self, sequence, identifier):
        raise NotImplementedError

    class TapMode(IntEnum):
        Text = 0
        Controller = 1
        ControllerWithHIDMouse = 3
        RawSensor = 10

    class AirGestures(IntEnum):
        Undefined = -1000,
        OneFingerUp = 2,
        TwoFingersUp = 3,
        OnefingerDown = 4,
        TwoFingersDown = 5,
        OneFingerLeft = 6,
        TwoFingersLeft = 7,
        OneFingerRight = 8,
        TwoFingersRight = 9,
        IndexToThumbTouch = 1000,
        MiddleToThumbTouch = 1001


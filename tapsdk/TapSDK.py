import abc
from enum import Enum, IntEnum


class TapSDKBase(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def register_connection_events(self, listener):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def register_disconnection_events(self, listener):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def register_tap_events(self, listener):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_mouse_events(self, listener):
        raise NotImplementedError()
   
    @abc.abstractmethod
    def register_raw_data_events(self, listener):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_air_gesture_events(self, listener):
        raise NotImplementedError
    
    @abc.abstractmethod
    def register_air_gesture_state_events(self, listener):
        raise NotImplementedError

    @abc.abstractmethod
    def set_input_mode(self, mode, tap_identifier):
        raise NotImplementedError()

    @abc.abstractmethod
    def send_vibration_sequence(self, sequence, identifier):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError



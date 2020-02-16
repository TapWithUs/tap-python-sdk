import abc


class TapSDKBase(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def register_tap_events(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_mouse_events(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_connection_events(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def register_disconnection_events(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def set_input_mode(self, mode):
        raise NotImplementedError()


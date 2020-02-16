import abc


class BlePeripheralBase(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def connect(self, name: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def enable_notification(self, characteristic, callback):
        raise NotImplementedError()

    @abc.abstractmethod
    def disable_notification(self, characteristic):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def read_from_char(self, characteristic):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def write_to_char(self, characteristic):
        raise NotImplementedError()


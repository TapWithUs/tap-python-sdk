import logging
import asyncio 
from asyncio.events import AbstractEventLoop
import platform

from typing import Callable

from bleak import BleakClient
from bleak import _logger as logger
from bleak.backends.corebluetooth.discovery import discover


from ..device import BlePeripheralBase
from ...TapSDK import TapSDKBase

class BlePeripheral(BlePeripheralBase):
    def __init__(self):
        self.manager = BleakClient("dssdfs")

    def connect(self, name: str):
        pass

    def enable_notification(self, characteristic, callback):
        pass

    def disable_notification(self, characteristic):
        pass
    
    def read_from_char(self, characteristic):
        pass

    def write_to_char(self, characteristic):
        pass



class TapMacSDK(TapSDKBase):
    def __init__(self, loop: AbstractEventLoop = None):
        super(TapMacSDK, self).__init__()
        self.mode = 1
        self.loop = loop
        self.manager = BleakClient("29934722-8924-4B47-AF8E-923D6C9FED82", loop)

    def OnTapped(self, identifier, tapcode):
        print(identifier + " tapped " + str(tapcode))

    def OnTapConnected(self, identifier, name, fw):
        print(identifier + " Tap: " + str(name), " FW Version: ", fw)

    def OnTapDisconnected(self, identifier):
        print(identifier + " Tap: " + identifier + " disconnected")

    def OnMoused(self, identifier, vx, vy, isMouse):
        print(identifier + " mouse movement: " + vx + vy)

    def register_tap_events(self, cb: Callable):
        TAPManager.Instance.OnTapped += self.OnTapped

    def register_mouse_events(self, cb: Callable):
        self.device.enable_notification()
        TAPManager.Instance.OnMoused += self.OnMoused

    def register_connection_events(self, cb: Callable):
        TAPManager.Instance.OnTapConnected += self.OnTapConnected

    def register_disconnection_events(self, cb: Callable):
        TAPManager.Instance.OnTapDisconnected += self.OnTapDisconnected

    def set_input_mode(self, mode):
        self.mode = mode

    def run(self):
        TAPManager.Instance.Start()
    
    async def list_connected_taps(self):
        devices = await discover(loop=self.loop)
        return devices


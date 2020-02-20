import logging
import asyncio 
from asyncio.events import AbstractEventLoop
import platform

from typing import Callable

from bleak import BleakClient
from bleak import _logger as logger
from bleak.backends.corebluetooth.discovery import discover
from bleak.backends.corebluetooth import CBAPP as cbapp


from ...TapSDK import TapSDKBase
from ...models import TapUUID
from .inputmodes import TapInputModes
from ...models.enumerations import MouseModes
from tapsdk import parsers

import objc
import uuid
objc.loadBundle("CoreBluetooth", globals(),
    bundle_path=objc.pathForFramework(u'/System/Library/Frameworks/IOBluetooth.framework/Versions/A/Frameworks/CoreBluetooth.framework'))

class TapClient(BleakClient):
    def __init__(self, address, loop=None, **kwargs):
        super().__init__(address, loop=loop, **kwargs)
    
    async def connect_retrieved(self, **kwargs) -> bool:
        paired_taps = get_paired_taps()

        logger.debug("Connecting to Tap device @ {}".format(self.address))

        await cbapp.central_manager_delegate.connect_(paired_taps[0])

        # Now get services
        await self.get_services()

        return True

def get_paired_taps():
    paired_taps = cbapp.central_manager_delegate.central_manager.retrieveConnectedPeripheralsWithServices_(
        [CBUUID.UUIDWithString_(str(uuid.UUID(TapUUID.tap_service)))])
    # await cbapp.central_manager_delegate.connect_(a[0])
    logger.debug("Found connected Taps @ {}".format(paired_taps))
    return paired_taps

class TapMacSDK(TapSDKBase):
    def __init__(self, loop: AbstractEventLoop = None):
        super(TapMacSDK, self).__init__()
        self.loop = loop
        self.manager = TapClient("29934722-8924-4B47-AF8E-923D6C9FED82", loop)
        self.mouse_event_cb = None
        self.tap_event_cb = None
        self.air_gesture_event_cb = None
        self.raw_data_event_cb = None
        self.air_gesture_state_event_cb = None
        self.input_mode_refresh = InputModeAutoRefresh(self._refresh_input_mode, timeout=10)
        self.mouse_mode = MouseModes.STDBY
        self.input_mode = TapInputModes("text")

    async def register_tap_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.tap_data_characteristic, self.on_tapped)
            self.tap_event_cb = cb

    async def register_mouse_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.mouse_data_characteristic, self.on_moused)
            self.mouse_event_cb = cb
    
    async def register_air_gesture_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.air_gesture_data_characteristic, self.on_air_gesture)
            self.air_gesture_event_cb = cb
    
    async def register_air_gesture_state_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.air_gesture_data_characteristic, self.on_air_gesture)
            self.air_gesture_state_event_cb = cb

    async def register_raw_data_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.raw_sensors_characteristic, self.on_raw_data)
            self.raw_data_event_cb = cb

    async def register_connection_events(self, cb: Callable):
        pass

    async def register_disconnection_events(self, cb: Callable):
        pass

    def on_moused(self, identifier, data):
        if self.mouse_event_cb:
            vx, vy, prox = parsers.mouse_data_msg(data)
            self.mouse_event_cb(identifier, vx, vy, prox)
    
    def on_tapped(self, identifier, data):
        tapcode = parsers.tap_data_msg(data)
        if self.mouse_mode == MouseModes.AIR_MOUSE:
            if tapcode in [2, 4]:
                self.on_air_gesture(identifier, [tapcode+10])
        elif self.tap_event_cb:
            self.tap_event_cb(identifier, tapcode)
    
    def on_raw_data(self, identifier, data):
        if self.raw_data_event_cb:
            messages = parsers.raw_data_msg(data)
            self.raw_data_event_cb(identifier, messages)

    def on_air_gesture(self, identifier, data):
        if data[0] == 0x14: # mouse mode event
            self.mouse_mode = MouseModes(data[1])
            if self.air_gesture_state_event_cb:
                self.air_gesture_state_event_cb(identifier, self.mouse_mode == MouseModes.AIR_MOUSE)
        elif self.air_gesture_event_cb:
            if data[0] != 0x14:
                gesture = data[0]
                self.air_gesture_event_cb(identifier, gesture)
    
    async def send_vibration_sequence(self, sequence, identifier=None):
        if len(sequence) > 18:
            sequence = sequence[:18]
        for i, d in enumerate(sequence):
            sequence[i] = max(0,min(255,d//10))
 
        write_value = bytearray([0x0,0x2] + sequence)
        await self.manager.write_gatt_char(TapUUID.ui_cmd_characteristic, write_value)

    async def set_input_mode(self, input_mode:TapInputModes, identifier=None):
        if  (input_mode.mode == "raw" and 
            self.input_mode.mode == "raw" and 
            self.input_mode.get_command() != input_mode.get_command()):
            logger.warning("Can't change \"raw\" sensitivities while in \"raw\"")
            return

        self.input_mode = input_mode
        write_value = input_mode.get_command()

        if self.input_mode_refresh.is_running == False:
            await self.input_mode_refresh.start()

        await self._write_input_mode(write_value)

    async def _refresh_input_mode(self):
        await self.set_input_mode(self.input_mode)
        logger.debug("Input Mode Refreshed: " + self.input_mode.get_name())
        
    async def _write_input_mode(self, value):
        await self.manager.write_gatt_char(TapUUID.tap_mode_characteristic, value)
    
    async def list_connected_taps(self):
        devices = await discover(loop=self.loop)
        return devices
    
    async def run(self):
        await self.manager.connect_retrieved()

class InputModeAutoRefresh:
    def __init__(self, set_function: Callable, timeout:int=10):
        self.set_function = set_function
        self.is_running = False
        self.timeout = timeout
        self.wd_task = None

    async def start(self):
        if self.is_running == False:
            self.wd_task = asyncio.create_task(self.periodic())
            self.is_running = True
            logger.debug("Input Mode Auto Refresh Started")
    
    async def stop(self):
        if self.is_running == True:
            self.wd_task.cancel()
            self.is_running = False
            logger.debug("Input Mode Auto Refresh Stopped")

    async def periodic(self):
        while True:
            await self.set_function()
            await asyncio.sleep(self.timeout)

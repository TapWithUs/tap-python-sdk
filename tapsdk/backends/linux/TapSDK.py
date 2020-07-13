import logging
import asyncio 
from asyncio.events import AbstractEventLoop
import platform

import bluetooth

from typing import Callable

from bleak import BleakClient
from bleak import _logger as logger
from bleak import BleakScanner
from subprocess import Popen, PIPE

from ...TapSDK import TapSDKBase
from ...models import TapUUID
from .inputmodes import TapInputMode
from ...models.enumerations import MouseModes
from tapsdk import parsers

class TapClient(BleakClient):
    def __init__(self, address=None, loop=None, **kwargs):
        super().__init__(address, loop=loop, **kwargs)
    
    async def connect_retrieved(self, **kwargs) -> bool:
        async with BleakClient(self.address, loop=self.loop) as client:
            connected = await client.is_connected()
            if connected:
                logger.info("Connected to {0}".format(self.address))
            else:
                logger.error("Failed to connect to {0}".format(self.address))
            return connected

    async def __debug(self): 
        for service in  client.services:
            logger.info("[service] {}: {}".format(service.uuid, service.description))
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value =  bytes(await clien.read_gatt_char(char.uuid))
                    except Exception as e:
                        value = str(e).encode
                else:
                    value = None
                # if value:
                logger.info(
                    "\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(
                        char.uuid,
                        "<handle geos here>",  #char.handle,
                        ",".join(char.properties),
                        char.description,
                        value,
                    )
                )

def is_tap_device(device):
    return True or len(device.metadata) > 0

class TapLinuxSDK(TapSDKBase):
    def __init__(self, address=None, loop: AbstractEventLoop = None):
        super(TapLinuxSDK, self).__init__()
        self.loop = loop
        self.address = None
        self.address = self.get_mac_addr()
        self.manager = TapClient(address=self.address,loop=loop)
        self.mouse_event_cb = None
        self.tap_event_cb = None
        self.air_gesture_event_cb = None
        self.raw_data_event_cb = None
        self.air_gesture_state_event_cb = None
        self.input_mode_refresh = InputModeAutoRefresh(self._refresh_input_mode, timeout=10)
        self.mouse_mode = MouseModes.STDBY
        self.input_mode = TapInputMode("text")

    async def register_tap_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.tap_data_characteristic.lower(), self.on_tapped)
            self.tap_event_cb = cb

    async def register_mouse_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.mouse_data_characteristic.lower(), self.on_moused)
            self.mouse_event_cb = cb
    
    async def register_air_gesture_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.air_gesture_data_characteristic.lower(), self.on_air_gesture)
            self.air_gesture_event_cb = cb
    
    async def register_air_gesture_state_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.air_gesture_data_characteristic.lower(), self.on_air_gesture)
            self.air_gesture_state_event_cb = cb

    async def register_raw_data_events(self, cb: Callable):
        if cb:
            await self.manager.start_notify(TapUUID.raw_sensors_characteristic.lower(), self.on_raw_data)
            self.raw_data_event_cb = cb

    async def register_connection_events(self, cb: Callable):
        pass

    async def register_disconnection_events(self, cb: Callable):
        pass

    def get_mac_addr(self) -> str:
        if not self.address:
            try:
                with Popen(["bt-device", "--list"], stdout=PIPE, text=True) as btdevice_process:
                    exit_code = btdevice_process.wait()
                    if exit_code:
                        raise ConnectionError("Failed to find any TAP decive")
                    connected_bt_devices = btdevice_process.stdout.read().splitlines();
                    tap_devices = list(filter(lambda line: line.startswith("Tap_"), connected_bt_devices))
                    for d in tap_devices:
                        logger.info("Found tap device: {}".format(d))
                    if len(tap_devices) > 1:
                        raise ValueError("Found more than 1 Tap device. Set the MAC address of the device you want to connect to and try again.")
                    if len(tap_devices) == 0:
                        raise ValueError("No Tap device was found. Make sure the device is connected and its human readable name starts with Tap_.")
                    device_decs = tap_devices[0]
                    tap_mac_address = device_decs[-18:-1] # only the mac_address part of the description.
                    return tap_mac_address
            except Exception as e:
                logger.error("Failed to find any TAP device: {}".format(e))
                raise e
 
    def on_moused(self, identifier, data):
        if self.mouse_event_cb:
            args = parsers.mouse_data_msg(data)
            self.mouse_event_cb(identifier, *args)
    
    def on_tapped(self, identifier, data):
        args = parsers.tap_data_msg(data)
        if self.mouse_mode == MouseModes.AIR_MOUSE:
            tapcode = args[0]
            if tapcode in [2, 4]:
                self.on_air_gesture(identifier, [tapcode+10])
        elif self.tap_event_cb:
            self.tap_event_cb(identifier, *args)
    
    def on_raw_data(self, identifier, data):
        if self.raw_data_event_cb:
            args = parsers.raw_data_msg(data)
            self.raw_data_event_cb(identifier, args)

    def on_air_gesture(self, identifier, data):
        if data[0] == 0x14: # mouse mode event
            self.mouse_mode = MouseModes(data[1])
            if self.air_gesture_state_event_cb:
                self.air_gesture_state_event_cb(identifier, self.mouse_mode == MouseModes.AIR_MOUSE)
        elif self.air_gesture_event_cb:
            args = parsers.air_gesture_data_msg(data)
            self.air_gesture_event_cb(identifier, *args)
    
    async def send_vibration_sequence(self, sequence:list, identifier=None):
        if len(sequence) > 18:
            sequence = sequence[:18]
        for i, d in enumerate(sequence):
            sequence[i] = max(0,min(255,d//10))
 
        write_value = bytearray([0x0,0x2] + sequence)
        await self.manager.write_gatt_char(TapUUID.ui_cmd_characteristic.lower() , write_value)

    async def set_input_mode(self, input_mode:TapInputMode, identifier=None):
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
        # TODO: uncomment me
        # await self.manager.write_gatt_char(TapUUID.tap_mode_characteristic.lower(), value)
        pass

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

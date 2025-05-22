import asyncio
import logging
import platform
from typing import Callable

from bleak import BleakClient, BleakScanner

from . import parsers
from .enumerations import InputType, MouseModes
from .inputmodes import TapInputMode, input_type_command

logger = logging.getLogger(__name__)

tap_service = 'c3ff0001-1d8b-40fd-a56f-c7bd5d0f3370'
nus_service = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
tap_data_characteristic = 'c3ff0005-1d8b-40fd-a56f-c7bd5d0f3370'
mouse_data_characteristic = 'c3ff0006-1d8b-40fd-a56f-c7bd5d0f3370'
ui_cmd_characteristic = 'c3ff0009-1d8b-40fd-a56f-c7bd5d0f3370'
air_gesture_data_characteristic = 'c3ff000a-1d8b-40fd-a56f-c7bd5d0f3370'
tap_mode_characteristic = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'        # nus rx
raw_sensors_characteristic = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'     # nus tx


if platform.system() == "Darwin":
    from bleak.backends.corebluetooth.CentralManagerDelegate import (
        CBUUID, CentralManagerDelegate)

    def string2uuid(uuid_str: str) -> CBUUID:
        """Convert a string to a uuid"""
        return CBUUID.UUIDWithString_(uuid_str)

    class TapClient(BleakClient):
        def __init__(self, address="", **kwargs):
            super().__init__(address, **kwargs)

        async def connect_retrieved(self, **kwargs) -> bool:
            self._central_manager_delegate = CentralManagerDelegate.alloc().init()
            paired_taps = self.get_paired_taps()
            if len(paired_taps) == 0:
                return False
            self._peripheral = paired_taps[0]
            logger.debug("Connecting to Tap device @ {}".format(self._peripheral))
            await self.connect()

            # Now get services
            await self.get_services()

            return True

        def get_paired_taps(self):
            paired_taps = self._central_manager_delegate.central_manager.retrieveConnectedPeripheralsWithServices_(
                            [string2uuid(tap_service)])
            logger.debug("Found connected Taps @ {}".format(paired_taps))
            return paired_taps

elif platform.system() == "Windows":
    class TapClient(BleakClient):
        def __init__(self, address="", **kwargs):
            super().__init__(address, **kwargs)

        async def connect_retrieved(self, **kwargs) -> bool:
            return False

elif platform.system() == "Linux":
    class TapClient(BleakClient):
        def __init__(self, address=None, **kwargs):
            address = address if address else get_mac_addr()
            super().__init__(address, **kwargs)

        async def connect_retrieved(self, **kwargs) -> bool:
            await self.connect()
            connected = self.is_connected()
            if connected:
                logger.info("Connected to {0}".format(self.address))
                await self.__debug()
            else:
                logger.error("Failed to connect to {0}".format(self.address))
            return connected

        async def __debug(self):
            for service in self.services:
                logger.info("[service] {}: {}".format(service.uuid, service.description))
                for char in service.characteristics:
                    if "read" in char.properties:
                        try:
                            value = bytes(await self.read_gatt_char(char.uuid))
                        except Exception as e:
                            value = str(e).encode
                    else:
                        value = None
                    # if value:
                    logger.info(
                        "\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(
                            char.uuid,
                            "<handle geos here>",  # char.handle,
                            ",".join(char.properties),
                            char.description,
                            value,
                        )
                    )

    def get_mac_addr() -> str:
        from subprocess import PIPE, Popen
        try:
            with Popen(["bt-device", "--list"], stdout=PIPE, text=True) as btdevice_process:
                exit_code = btdevice_process.wait()
                if exit_code:
                    raise ConnectionError("Failed to find any TAP decive")
                connected_bt_devices = btdevice_process.stdout.read().splitlines()
                tap_devices = list(filter(lambda line: line.startswith("Tap"), connected_bt_devices))
                for d in tap_devices:
                    logger.info("Found tap device: %s", d)
                if len(tap_devices) > 1:
                    logger.info("Found more than 1 Tap device:")
                    for i, d in enumerate(tap_devices):
                        logger.info("%s. %s", i + 1, d)
                    tap_devices = [tap_devices[int(input("Select the device number: ")) - 1]]
                if len(tap_devices) == 0:
                    raise ValueError(
                        "No Tap device was found. Make sure the device is connected and its human readable name "
                        "starts with Tap.")
                device_decs = tap_devices[0]
                tap_mac_address = device_decs[-18:-1]  # only the mac_address part of the description.
                return tap_mac_address
        except Exception as e:
            logger.error("Failed to find any TAP device: {}".format(e))
            raise e


class TapSDK():
    def __init__(self, **kwargs):
        self.client = TapClient(address=kwargs.get("address"))
        self.mouse_event_cb = None
        self.tap_event_cb = None
        self.air_gesture_event_cb = None
        self.raw_data_event_cb = None
        self.air_gesture_state_event_cb = None
        self.connection_cb = None
        self.input_mode_refresh = InputModeAutoRefresh(self._refresh_input_mode, timeout=10)
        self.mouse_mode = MouseModes.STDBY
        self.input_mode = TapInputMode("text")
        self.input_type = InputType.AUTO

    def register_tap_events(self, cb: Callable):
        self.tap_event_cb = cb

    def register_mouse_events(self, cb: Callable):
        self.mouse_event_cb = cb

    def register_air_gesture_events(self, cb: Callable):
        self.air_gesture_event_cb = cb

    def register_air_gesture_state_events(self, cb: Callable):
        self.air_gesture_state_event_cb = cb

    def register_raw_data_events(self, cb: Callable):
        self.raw_data_event_cb = cb

    def register_connection_events(self, cb: Callable):
        self.connection_cb = cb

    def register_disconnection_events(self, cb: Callable):
        self.client.set_disconnected_callback(cb)

    def on_moused(self, identifier, data):
        if self.mouse_event_cb:
            args = parsers.mouse_data_msg(data)
            self.mouse_event_cb(identifier, *args)

    def on_tapped(self, identifier, data):
        args = parsers.tap_data_msg(data)
        if self.mouse_mode == MouseModes.AIR_MOUSE:
            tapcode = args[0]
            if tapcode in [2, 4]:
                self.on_air_gesture(identifier, [tapcode + 10])
        elif self.tap_event_cb:
            self.tap_event_cb(identifier, *args)

    def on_raw_data(self, identifier, data):
        if self.raw_data_event_cb:
            scale = False
            sensitivity = [0, 0, 0]
            if isinstance(self.input_mode, TapInputMode) and self.input_mode.mode == "raw":
                scale = getattr(self.input_mode, "scaled", scale)
                sensitivity = getattr(self.input_mode, "sensitivity", sensitivity)
            args = parsers.raw_data_msg(data, scaled=scale, sensitivity=sensitivity)
            self.raw_data_event_cb(identifier, args)

    def on_air_gesture(self, identifier, data):
        if data[0] == 0x14:  # mouse mode event
            self.mouse_mode = MouseModes(data[1])
            if self.air_gesture_state_event_cb:
                self.air_gesture_state_event_cb(identifier, self.mouse_mode)
        elif self.air_gesture_event_cb:
            args = parsers.air_gesture_data_msg(data)
            self.air_gesture_event_cb(identifier, *args)

    async def send_vibration_sequence(self, sequence, identifier=None):
        if len(sequence) > 18:
            sequence = sequence[:18]
        for i, d in enumerate(sequence):
            sequence[i] = max(0, min(255, d // 10))

        write_value = bytearray([0x0, 0x2] + sequence)
        await self.client.write_gatt_char(ui_cmd_characteristic, write_value)

    async def set_input_mode(self, input_mode: TapInputMode, identifier=None):
        if (input_mode.mode == "raw" and self.input_mode.mode == "raw" and
           self.input_mode.get_command() != input_mode.get_command()):
            logger.warning("Can't change \"raw\" sensitivities while in \"raw\"")
            return

        self.input_mode = input_mode
        write_value = input_mode.get_command()

        if not self.input_mode_refresh.is_running:
            await self.input_mode_refresh.start()

        await self._write_input_mode(write_value)

    async def set_input_type(self, input_type: InputType, identifier=None):
        assert isinstance(input_type, InputType), "input_type must be of type InputType"
        self.input_type = input_type
        write_value = input_type_command(self.input_type)

        if not self.input_mode_refresh.is_running:
            await self.input_mode_refresh.start()

        await self._write_input_mode(write_value)

    async def _refresh_input_mode(self):
        await self.set_input_mode(self.input_mode)
        logger.debug(f"Input Mode Refreshed: {self.input_mode.get_name()}")
        await self.set_input_type(self.input_type)
        logger.debug(f"Input Type Refreshed: {self.input_type}")

    async def _write_input_mode(self, value):
        await self.client.write_gatt_char(tap_mode_characteristic, value)

    async def run(self):
        stop_event = asyncio.Event()
        devices = []

        async def detection_cb(device, adv_data):
            logger.debug("detected %s %s", device, adv_data)
            if tap_service.lower() in adv_data.service_uuids:
                if device.address not in [d.address for d in devices]:
                    devices.append(device)
                    logger.debug("detected %s %s", device, adv_data)
                    stop_event.set()

        connected = await self.client.connect_retrieved()
        if not connected:
            logger.info("Couldn't find connected Tap device. Scanning for Tap devices...")
            async with BleakScanner(detection_callback=detection_cb) as _:
                await stop_event.wait()

            self.client = TapClient(devices[0])
            await self.client.connect()
            await self.client.pair()
        if self.client.is_connected:
            for ch, cb in [(tap_data_characteristic, self.on_tapped),
                           (mouse_data_characteristic, self.on_moused),
                           (air_gesture_data_characteristic, self.on_air_gesture),
                           (raw_sensors_characteristic, self.on_raw_data)]:
                try:
                    await self.client.start_notify(ch, cb)
                except Exception as e:
                    logger.warning("Failed to start notify for air gesture state: " + str(e))
            if self.connection_cb:
                self.connection_cb(self)


class InputModeAutoRefresh:
    def __init__(self, set_function, timeout=10):
        self.set_function = set_function
        self.is_running = False
        self.timeout = timeout
        self.wd_task = None

    async def start(self):
        if not self.is_running:
            self.wd_task = asyncio.create_task(self.periodic())
            self.is_running = True
            logger.debug("Input Mode Auto Refresh Started")

    async def stop(self):
        if self.is_running:
            self.wd_task.cancel()
            self.is_running = False
            logger.debug("Input Mode Auto Refresh Stopped")

    async def periodic(self):
        while True:
            await self.set_function()
            await asyncio.sleep(self.timeout)

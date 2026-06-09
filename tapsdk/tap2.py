import asyncio
import logging
import platform
from typing import Callable

from bleak import BleakClient, BleakScanner

from . import encoder, parsers
from .enumerations import (
    DeviceFeatures,
    FingerAcclSensitivity,
    ImuAcclSensitivity,
    ImuGyroSensitivity,
    ModelTypes,
    VisionSensorOpModes,
)
from .inputmodes import RawSensorsSensitivity

logger = logging.getLogger(__name__)

tap_service = 'c3ff0001-1d8b-40fd-a56f-c7bd5d0f3370'
tap_data_read_characteristic = 'c3ff000e-1d8b-40fd-a56f-c7bd5d0f3370'
tap_data_write_characteristic = 'c3ff000f-1d8b-40fd-a56f-c7bd5d0f3370'
serial_number_characteristic = '00002a25-0000-1000-8000-00805f9b34fb'


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
                    logger.info(
                        "\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(
                            char.uuid,
                            "<handle geos here>",
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
                tap_mac_address = device_decs[-18:-1]
                return tap_mac_address
        except Exception as e:
            logger.error("Failed to find any TAP device: {}".format(e))
            raise e


class KeepAliveManager:
    """Manages periodic keepalive messages to maintain device connection."""

    def __init__(self, set_function, timeout=10):
        self.set_function = set_function
        self.is_running = False
        self.timeout = timeout
        self.wd_task = None

    async def start(self):
        if not self.is_running:
            self.wd_task = asyncio.create_task(self.periodic())
            self.is_running = True
            logger.debug("KeepAliveManager Started")

    async def stop(self):
        if self.is_running:
            self.wd_task.cancel()
            self.is_running = False
            logger.debug("KeepAliveManager Stopped")

    async def periodic(self):
        while True:
            await self.set_function()
            await asyncio.sleep(self.timeout)


class TapSDK2:
    def __init__(self, **kwargs):
        self.client = TapClient(address=kwargs.get("address"))
        self._write_lock = asyncio.Lock()
        self.device_serial_number = None
        self._scale_factors = None

        self.tap_event_cb = None
        self.air_gesture_event_cb = None
        self.raw_data_event_cb = None
        self.imu_motion_data_cb = None
        self.standby_state_event_cb = None
        self.connection_cb = None

        self.keep_alive_manager = KeepAliveManager(
            self.send_keepalive_message,
            timeout=kwargs.get("keepalive_timeout", 10),
        )

    async def _write_tap_gatt_char(self, write_value: bytearray):
        async with self._write_lock:
            await self.client.write_gatt_char(
                tap_data_write_characteristic,
                write_value,
                response=True,
            )

    def register_tap_events(self, cb: Callable):
        self.tap_event_cb = cb

    def register_air_gesture_events(self, cb: Callable):
        self.air_gesture_event_cb = cb

    def register_raw_imu_data_events(self, cb: Callable):
        self.raw_data_event_cb = cb

    def register_raw_data_events(self, cb: Callable):
        self.register_raw_imu_data_events(cb)

    def register_imu_motion_data_events(self, cb: Callable):
        self.imu_motion_data_cb = cb

    def register_standby_state_events(self, cb: Callable):
        self.standby_state_event_cb = cb

    def register_connection_events(self, cb: Callable):
        self.connection_cb = cb

    def register_disconnection_events(self, cb: Callable):
        self.client.set_disconnected_callback(cb)

    def on_inc_msg(self, sender, data):
        if not data:
            logger.debug("Received empty notification from %s", sender)
            return

        args = parsers.tap_inc_msg(data, scale_factors=self._scale_factors)
        if not args:
            logger.debug(
                "Received unsupported notification payload from %s: %s",
                sender,
                bytes(data).hex(),
            )
            return

        if args['type'] == 'imu_raw':
            if self.raw_data_event_cb:
                self.raw_data_event_cb(sender, args['data'])
        elif args['type'] == 'imu_motion':
            if self.imu_motion_data_cb:
                self.imu_motion_data_cb(sender, args['data'])
        elif args['type'] == 'air_gesture':
            if self.air_gesture_event_cb:
                self.air_gesture_event_cb(sender, args['data'])
        elif args['type'] == 'tap_gesture':
            if self.tap_event_cb:
                self.tap_event_cb(sender, args['data'])
        elif args['type'] == 'standby_state':
            if self.standby_state_event_cb:
                self.standby_state_event_cb(sender, args['data'])

    async def set_feature(self, feature: DeviceFeatures, enable: bool, identifier=None):
        if not isinstance(feature, DeviceFeatures):
            raise ValueError("feature must be of type DeviceFeatures")
        write_value = encoder.encode_set_feature(feature.value, int(enable))
        await self._write_tap_gatt_char(write_value)

    async def set_vision_sensor_op_mode(self, mode: VisionSensorOpModes, identifier=None):
        if not isinstance(mode, VisionSensorOpModes):
            raise ValueError("mode must be of type VisionSensorOpModes")
        write_value = encoder.encode_set_vision_sensor_op_mode(mode.value)
        await self._write_tap_gatt_char(write_value)

    async def set_vision_sensor_model(self, model: ModelTypes, identifier=None):
        if not isinstance(model, ModelTypes):
            raise ValueError("model must be of type ModelTypes")
        write_value = encoder.encode_set_vision_sensor_model(model.value)
        await self._write_tap_gatt_char(write_value)

    async def set_imu_sensitivity(
        self,
        xl_sensitivity: ImuAcclSensitivity,
        gyro_sensitivity: ImuGyroSensitivity,
        scaled=False,
        finger_accl_sens=None,
        identifier=None,
    ):
        if not isinstance(xl_sensitivity, ImuAcclSensitivity):
            raise ValueError("xl_sensitivity must be of type ImuAcclSensitivity")
        if not isinstance(gyro_sensitivity, ImuGyroSensitivity):
            raise ValueError("gyro_sensitivity must be of type ImuGyroSensitivity")
        if finger_accl_sens is not None and not isinstance(finger_accl_sens, FingerAcclSensitivity):
            raise ValueError("finger_accl_sens must be of type FingerAcclSensitivity")
        if scaled:
            self._scale_factors = RawSensorsSensitivity(
                finger_accl_sens or FingerAcclSensitivity.G2,
                gyro_sensitivity,
                xl_sensitivity,
            ).get_scale_factors()
        else:
            self._scale_factors = None
        write_value = encoder.encode_set_imu_sensitivity(
            xl_sensitivity.value,
            gyro_sensitivity.value,
        )
        await self._write_tap_gatt_char(write_value)

    async def set_haptic_pattern(self, sequence: list, identifier=None):
        if not isinstance(sequence, list) or not all(isinstance(i, int) for i in sequence):
            raise ValueError("sequence must be a list of integers")
        if len(sequence) > 18:
            sequence = sequence[:18]
        for i, d in enumerate(sequence):
            sequence[i] = max(0, min(255, d // 10))
        write_value = bytearray([0x0, 0x2] + sequence)
        write_value = encoder.encode_set_haptic_pattern(write_value)
        await self._write_tap_gatt_char(write_value)

    async def send_vibration_sequence(self, sequence, identifier=None):
        await self.set_haptic_pattern(sequence, identifier=identifier)

    async def send_keepalive_message(self, identifier=None):
        write_value = encoder.encode_keepalive_message()
        await self._write_tap_gatt_char(write_value)

    async def set_standby_state(self, standby: bool, identifier=None):
        write_value = encoder.encode_standby_state_set(standby)
        await self._write_tap_gatt_char(write_value)

    async def get_standby_state(self, identifier=None):
        write_value = encoder.encode_standby_state_get()
        await self._write_tap_gatt_char(write_value)

    async def run(self):
        stop_event = asyncio.Event()
        devices = []

        async def detection_cb(device, adv_data):
            logger.debug("detected %s %s", device, adv_data)
            if tap_service.lower() in adv_data.service_uuids:
                if device.address not in [d.address for d in devices]:
                    devices.append(device)
                    stop_event.set()

        connected = await self.client.connect_retrieved()
        if not connected:
            logger.info("Couldn't find connected Tap device. Scanning for Tap devices...")
            async with BleakScanner(detection_callback=detection_cb):
                await stop_event.wait()

            self.client = TapClient(devices[0])
            await self.client.connect()
            if platform.system() != "Darwin":
                await self.client.pair()

        if self.client.is_connected:
            await self.client.start_notify(tap_data_read_characteristic, self.on_inc_msg)
            self.device_serial_number = await self.client.read_gatt_char(
                serial_number_characteristic,
            )
            logger.info(
                "Device serial number: %s",
                self.device_serial_number.decode('utf-8'),
            )
            await self.keep_alive_manager.start()
            if self.connection_cb:
                self.connection_cb(self.device_serial_number)

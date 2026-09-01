import asyncio
import logging
from typing import Callable

from . import encoder, parsers
from ._transport import TapClient, client_connected, connect_tap, set_disconnected_callback
from .device_info import DeviceInfo, read_device_info, serial_number_characteristic
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

DEFAULT_GET_TIMEOUT_SEC = 2.0

tap_data_read_characteristic = 'c3ff000e-1d8b-40fd-a56f-c7bd5d0f3370'
tap_data_write_characteristic = 'c3ff000f-1d8b-40fd-a56f-c7bd5d0f3370'


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
    def __init__(self, client=None, address=None, **kwargs):
        if address is None:
            address = kwargs.get("address")
        self._address = address
        if client is not None:
            self.client = client
        else:
            # Darwin TapClient defaults to ""; Linux treats falsy address as auto-detect.
            self.client = TapClient(address=address if address is not None else "")
        self._write_lock = asyncio.Lock()
        self.device_serial_number = None
        self._scale_factors = None
        self._pending_requests = {}
        self._get_timeout = kwargs.get("get_timeout", DEFAULT_GET_TIMEOUT_SEC)

        self.tap_event_cb = None
        self.air_gesture_event_cb = None
        self.raw_data_event_cb = None
        self.imu_motion_data_cb = None
        self.standby_state_event_cb = None
        self.connection_cb = None
        self._disconnect_cb = None

        self.keep_alive_manager = KeepAliveManager(
            self.send_keepalive_message,
            timeout=kwargs.get("keepalive_timeout", 10),
        )

    def _resolve_pending_request(self, key, value):
        future = self._pending_requests.get(key)
        if future is not None and not future.done():
            future.set_result(value)

    async def _request_and_wait(self, key, write_value):
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending_requests[key] = future
        try:
            await self._write_tap_gatt_char(write_value)
            return await asyncio.wait_for(future, timeout=self._get_timeout)
        finally:
            if self._pending_requests.get(key) is future:
                self._pending_requests.pop(key, None)

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
        self._disconnect_cb = cb
        set_disconnected_callback(self.client, cb)

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
            self._resolve_pending_request(('standby_state',), args['data'])
            if self.standby_state_event_cb:
                self.standby_state_event_cb(sender, args['data'])
        elif args['type'] == 'config_feature':
            feature_data = args['data']
            self._resolve_pending_request(
                ('config_feature', feature_data['feature_number']),
                feature_data['feature_value'],
            )
        elif args['type'] == 'config_vision_op_mode':
            self._resolve_pending_request(('config_vision_op_mode',), args['data'])
        elif args['type'] == 'config_vision_model':
            self._resolve_pending_request(('config_vision_model',), args['data'])
        elif args['type'] == 'config_imu_sensitivity':
            self._resolve_pending_request(('config_imu_sensitivity',), args['data'])

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
        scaled = [max(0, min(255, d // 10)) for d in sequence[:encoder.HAPTIC_UI_DURATION_SLOT_COUNT]]
        write_value = encoder.encode_set_haptic_pattern(scaled)
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
        return await self._request_and_wait(
            ('standby_state',),
            encoder.encode_standby_state_get(),
        )

    async def get_feature(self, feature: DeviceFeatures, identifier=None):
        if not isinstance(feature, DeviceFeatures):
            raise ValueError("feature must be of type DeviceFeatures")
        return await self._request_and_wait(
            ('config_feature', feature.value),
            encoder.encode_get_feature(feature.value),
        )

    async def get_vision_sensor_op_mode(self, identifier=None):
        mode_value = await self._request_and_wait(
            ('config_vision_op_mode',),
            encoder.encode_get_vision_sensor_op_mode(),
        )
        return VisionSensorOpModes(mode_value)

    async def get_vision_sensor_model(self, identifier=None):
        model_value = await self._request_and_wait(
            ('config_vision_model',),
            encoder.encode_get_vision_sensor_model(),
        )
        return ModelTypes(model_value)

    async def get_imu_sensitivity(self, identifier=None):
        gyro_value, xl_value = await self._request_and_wait(
            ('config_imu_sensitivity',),
            encoder.encode_get_imu_sensitivity(),
        )
        return ImuGyroSensitivity(gyro_value), ImuAcclSensitivity(xl_value)

    async def get_device_info(self) -> DeviceInfo:
        """Read device name, FW versions, battery, and other public device fields.

        Shared with TapSDK — DIS/BAS and Tap proprietary readable chars, not the
        framed v2 command pipe. Missing characteristics yield None.
        """
        return await read_device_info(self.client)

    async def start(self):
        """Start GATT notifications on an already-connected client."""
        if not client_connected(self.client):
            raise ConnectionError("Tap client is not connected; call connect() or run() first")
        if self._disconnect_cb:
            set_disconnected_callback(self.client, self._disconnect_cb)
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

    async def run(self):
        if not client_connected(self.client):
            self.client = await connect_tap(address=self._address)
        await self.start()

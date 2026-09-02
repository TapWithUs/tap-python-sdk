import asyncio
import logging
from typing import Callable

from . import parsers
from ._transport import TapClient, client_connected, connect_tap, set_disconnected_callback, tap_service  # noqa: F401
from .device_info import (  # noqa: F401
    DeviceInfo,
    battery_level_characteristic,
    battery_service,
    device_information_service,
    device_name_characteristic,
    firmware_revision_characteristic,
    format_model_version_hex,
    fw_version2_characteristic,
    gap_device_name_characteristic,
    hardware_revision_characteristic,
    manufacturer_name_characteristic,
    model_version_characteristic,
    read_device_info,
    serial_number_characteristic,
    software_revision_characteristic,
)
from .enumerations import InputType, MouseModes
from .inputmodes import InputModeText, InputMode, InputModeRaw, input_type_command

logger = logging.getLogger(__name__)

# Back-compat alias for tests/callers that imported the private helper name.
_format_model_version_hex = format_model_version_hex

nus_service = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
tap_data_characteristic = 'c3ff0005-1d8b-40fd-a56f-c7bd5d0f3370'
mouse_data_characteristic = 'c3ff0006-1d8b-40fd-a56f-c7bd5d0f3370'
ui_cmd_characteristic = 'c3ff0009-1d8b-40fd-a56f-c7bd5d0f3370'
air_gesture_data_characteristic = 'c3ff000a-1d8b-40fd-a56f-c7bd5d0f3370'
tap_mode_characteristic = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'        # nus rx
raw_sensors_characteristic = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'     # nus tx

# Firmware parks NUS commands in one shared 24-byte slot until low-priority
# bt_task drains it. Under IMU load that drain can lag; 50 ms was too short
# and the InputType write (AUTO) was getting overwritten by the mode write.
MODE_COMMAND_SETTLE_SECONDS = 0.2


class TapSDK():
    """High-level async API for one Tap Strap / TapXR over BLE (v1 protocol).

    Register event callbacks, then ``await run()`` (or ``await start()`` after
    ``connect()``) to subscribe to notifications. Issue commands with
    ``set_input_mode``, ``set_input_type``, and ``send_vibration_sequence``.
    """

    def __init__(self, client=None, address=None, **kwargs):
        """Create an SDK instance.

        Args:
            client: Optional already-connected ``TapClient`` (from ``connect()``).
            address: Optional BLE address or platform device id. On Linux, if
                omitted, a connected device whose name starts with ``Tap`` is
                selected.
        """
        if address is None:
            address = kwargs.get("address")
        self._address = address
        if client is not None:
            self.client = client
        else:
            # Darwin TapClient defaults to ""; Linux treats falsy address as auto-detect.
            self.client = TapClient(address=address if address is not None else "")
        self.mouse_event_cb = None
        self.tap_event_cb = None
        self.air_gesture_event_cb = None
        self.raw_data_event_cb = None
        self.air_gesture_state_event_cb = None
        self.connection_cb = None
        self._disconnect_cb = None
        self._mode_write_lock = asyncio.Lock()
        self.input_mode_refresh = InputModeAutoRefresh(self._refresh_input_mode, timeout=10)
        self.mouse_mode = MouseModes.STDBY
        self.input_mode = InputModeText()  # Default input mode is Text Mode
        self.input_type = InputType.AUTO

    @staticmethod
    def _client_connected(client) -> bool:
        return client_connected(client)

    def register_tap_events(self, cb: Callable):
        """Register ``cb(identifier, tapcode)`` for tap events."""
        self.tap_event_cb = cb

    def register_mouse_events(self, cb: Callable):
        """Register ``cb(identifier, vx, vy, proximity)`` for mouse motion."""
        self.mouse_event_cb = cb

    def register_air_gesture_events(self, cb: Callable):
        """Register ``cb(identifier, gesture)`` for air-gesture codes."""
        self.air_gesture_event_cb = cb

    def register_air_gesture_state_events(self, cb: Callable):
        """Register ``cb(identifier, mouse_mode)`` for mouse-mode changes."""
        self.air_gesture_state_event_cb = cb

    def register_raw_data_events(self, cb: Callable):
        """Register ``cb(identifier, packets)`` for raw sensor batches."""
        self.raw_data_event_cb = cb

    def register_connection_events(self, cb: Callable):
        """Register ``cb(tap_sdk)`` called after notifications are started."""
        self.connection_cb = cb

    def register_disconnection_events(self, cb: Callable):
        """Register Bleak's disconnected callback ``cb(client)``."""
        self._disconnect_cb = cb
        set_disconnected_callback(self.client, cb)

    def on_moused(self, identifier, data):
        if self.mouse_event_cb:
            args = parsers.mouse_data_msg(data)
            self.mouse_event_cb(identifier, *args)

    def on_tapped(self, identifier, data):
        args = parsers.tap_data_msg(data)
        # In air-mouse, codes 2/4 are click-like gestures; other taps still
        # deliver as tap events (do not drop them on the elif).
        if self.mouse_mode == MouseModes.AIR_MOUSE:
            tapcode = args[0]
            if tapcode in [2, 4]:
                self.on_air_gesture(identifier, [tapcode + 10])
                return
        if self.tap_event_cb:
            self.tap_event_cb(identifier, *args)

    def on_raw_data(self, identifier, data):
        if self.raw_data_event_cb:
            scale_factors = None
            if isinstance(self.input_mode, InputModeRaw):
                if self.input_mode.scaled:
                    scale_factors = self.input_mode.sensitivity.get_scale_factors()
            args = parsers.raw_data_msg(data, scale_factors=scale_factors)
            self.raw_data_event_cb(identifier, args)

    def on_air_gesture(self, identifier, data):
        if data[0] == 0x14:  # mouse mode event
            self.mouse_mode = MouseModes(data[1])
            if self.air_gesture_state_event_cb:
                self.air_gesture_state_event_cb(identifier, self.mouse_mode)
        elif self.air_gesture_event_cb:
            args = parsers.air_gesture_data_msg(data)
            self.air_gesture_event_cb(identifier, *args)

    async def get_device_info(self) -> DeviceInfo:
        """Read device name, FW versions, battery, and other public device fields.

        Requires a bonded connection (these characteristics are encrypted on Tap
        firmware). Missing characteristics yield None for that field.
        """
        return await read_device_info(self.client)

    async def send_vibration_sequence(self, sequence, identifier=None):
        """Send a haptic on/off sequence.

        Args:
            sequence: Periods in milliseconds (10–2550, 10 ms steps). Alternating
                on/off durations. At most 18 values; longer lists are truncated.
            identifier: Reserved for multi-device use; currently unused.
        """
        if len(sequence) > 18:
            sequence = sequence[:18]
        for i, d in enumerate(sequence):
            sequence[i] = max(0, min(255, d // 10))

        write_value = bytearray([0x0, 0x2] + sequence)
        await self.client.write_gatt_char(ui_cmd_characteristic, write_value)

    async def set_input_mode(self, input_mode: InputMode, identifier=None):
        """Set Text, Controller, Controller+Text, or Raw input mode.

        Args:
            input_mode: An ``InputMode`` instance from ``tapsdk``.
            identifier: Reserved for multi-device use; currently unused.
        """
        if (isinstance(input_mode, InputModeRaw) and isinstance(self.input_mode, InputModeRaw) and
           self.input_mode.get_command() != input_mode.get_command()):
            logger.warning("Can't change \"raw\" sensitivities while in \"raw\"")
            return

        self.input_mode = input_mode
        await self._write_input_mode(input_mode.get_command())
        # Re-assert type so Controller starts with AUTO (orientation), not a
        # stale forced mouse/keyboard left on the device.
        await self._write_input_mode(input_type_command(self.input_type))
        if not self.input_mode_refresh.is_running:
            await self.input_mode_refresh.start()

    async def set_input_type(self, input_type: InputType, identifier=None):
        """Force Spatial Control input type on TapXR (experimental firmware).

        Args:
            input_type: ``InputType.MOUSE``, ``KEYBOARD``, or ``AUTO``.
            identifier: Reserved for multi-device use; currently unused.
        """
        assert isinstance(input_type, InputType), "input_type must be of type InputType"
        self.input_type = input_type
        await self._write_input_mode(input_type_command(self.input_type))
        if not self.input_mode_refresh.is_running:
            await self.input_mode_refresh.start()

    async def _refresh_input_mode(self):
        await self._write_input_mode(self.input_mode.get_command())
        logger.debug("Input Mode Refreshed: %s", self.input_mode)
        await self._write_input_mode(input_type_command(self.input_type))
        logger.debug("Input Type Refreshed: %s", self.input_type)

    async def _write_input_mode(self, value):
        # Firmware forwards NUS commands through one shared packet slot before
        # its low-priority BT task consumes them. Keep writes apart so a second
        # command cannot replace the first before that task reads it.
        async with self._mode_write_lock:
            await self.client.write_gatt_char(
                tap_mode_characteristic,
                value,
                response=True,
            )
            await asyncio.sleep(MODE_COMMAND_SETTLE_SECONDS)

    async def start(self):
        """Start GATT notifications on an already-connected client."""
        if not client_connected(self.client):
            raise ConnectionError("Tap client is not connected; call connect() or run() first")
        if self._disconnect_cb:
            set_disconnected_callback(self.client, self._disconnect_cb)
        for ch, cb in [(tap_data_characteristic, self.on_tapped),
                       (mouse_data_characteristic, self.on_moused),
                       (air_gesture_data_characteristic, self.on_air_gesture),
                       (raw_sensors_characteristic, self.on_raw_data)]:
            try:
                await self.client.start_notify(ch, cb)
            except Exception as e:
                logger.warning("Failed to start notify for %s: %s", ch, e)
        if self.connection_cb:
            self.connection_cb(self)

    async def run(self):
        """Connect to a Tap and start GATT notifications.

        Attaches to an already-connected device when possible; otherwise scans
        (and on Windows polls for paired reconnects). Invokes the connection
        callback when notifications are armed. Returns after setup — keep the
        asyncio event loop alive to continue receiving events.
        """
        if not client_connected(self.client):
            self.client = await connect_tap(address=self._address)
        await self.start()


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
            await asyncio.sleep(self.timeout)
            await self.set_function()

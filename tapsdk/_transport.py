import asyncio
import logging
import platform

from bleak import BleakClient, BleakScanner

logger = logging.getLogger(__name__)

tap_service = 'c3ff0001-1d8b-40fd-a56f-c7bd5d0f3370'


def client_connected(client) -> bool:
    """Sync-safe connected check across bleak versions.

    bleak 0.12 returns ``_DeprecatedIsConnectedReturn``: truthy via ``__bool__``,
    but also callable — calling it returns a Future (always truthy as an object).
    Never call the wrapper; read the bool value only.
    """
    val = getattr(client, "is_connected", False)
    if isinstance(val, bool):
        return val
    # bleak 0.12 deprecation wrapper
    underlying = getattr(val, "_value", None)
    if isinstance(underlying, bool):
        return underlying
    if callable(val):
        result = val()
        if asyncio.iscoroutine(result):
            result.close()
            return False
        if asyncio.isfuture(result):
            return bool(result.result()) if result.done() else False
        return bool(result)
    return bool(val)


if platform.system() == "Darwin":
    try:
        from bleak.backends.corebluetooth.CentralManagerDelegate import (
            CBUUID, CentralManagerDelegate)
    except ImportError as e:
        raise ImportError(
            "tapsdk requires bleak==0.12.1 on macOS; the installed bleak version "
            "no longer exposes bleak.backends.corebluetooth.CentralManagerDelegate "
            "at this import path. Reinstall with the pinned dependency from setup.py."
        ) from e

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
    try:
        from bleak_winrt.windows.devices.bluetooth import (BluetoothLEDevice,  # noqa: F401
                                                           BluetoothConnectionStatus, BluetoothCacheMode)
        from bleak_winrt.windows.devices.bluetooth.genericattributeprofile import GattSession, GattSessionStatus
        from bleak_winrt.windows.devices.enumeration import DeviceInformation, DeviceInformationKind
    except ImportError as e:
        # bleak>=0.22.0 no longer depends on bleak_winrt (see #21), so it must be
        # installed explicitly; setup.py pins bleak==0.22.3 + bleak-winrt==1.2.0
        # for Windows. Fail fast if that pin was not honored, rather than
        # silently disabling the Windows BLE backend at runtime.
        raise ImportError(
            "tapsdk requires bleak==0.22.3 and bleak-winrt==1.2.0 on Windows. "
            "Reinstall with the pinned dependencies from setup.py, or see "
            "https://github.com/TapWithUs/tap-python-sdk/issues/21."
        ) from e

    async def get_connected_taps():
        # use the following device properties: Paired, Connected, Device Address
        request_properties = [
            "System.Devices.Aep.IsPaired",
            "System.Devices.Aep.IsConnected",
            "System.Devices.Aep.DeviceAddress",]
        aqs_filter = BluetoothLEDevice.get_device_selector_from_connection_status(BluetoothConnectionStatus.CONNECTED)
        devices = await DeviceInformation.find_all_async(aqs_filter, request_properties,
                                                         DeviceInformationKind.ASSOCIATION_ENDPOINT)
        taps = []
        for device in devices:
            try:
                # Extract the Bluetooth address from the device id
                # device.id format: "BluetoothLE#BluetoothLExx:xx:xx:xx:xx:xx-yy:yy:yy:yy:yy:yy"
                device_address_str = device.id.split("-")[-1].upper()
                # Convert MAC address string (e.g. "AA:BB:CC:DD:EE:FF") to a uint64
                address_int = int(device_address_str.replace(":", ""), 16)
                ble_device = await BluetoothLEDevice.from_bluetooth_address_async(address_int)
                if ble_device is None:
                    logger.error(f"Could not create BLE device for {device.name}")
                    continue
                services = await ble_device.get_gatt_services_async()
                logger.info(f"Device {device.name} has the following services:")
                for service in services.services:
                    logger.info(f"Service UUID: {service.uuid}")
                    if str(service.uuid).lower() == tap_service.lower():
                        taps.append(device)
                        break
            except Exception as e:
                logger.error(f"Failed to retrieve services for device {device.name}: {e}")
        return taps

    async def get_tap_device():
        taps = await get_connected_taps()
        if not taps:
            logger.info("No connected Tap devices found.")
            return None
        return taps[0].id  # Return the full WinRT device ID for BleakClient

    class TapClient(BleakClient):
        def __init__(self, address="", **kwargs):
            super().__init__(address, **kwargs)

        async def connect_retrieved(self, **kwargs) -> bool:
            if not self.address:
                logger.info("No connected Tap devices found.")
                return False
            logger.info(f"Connecting to Tap device @ {self.address}")

            # Bypass Bleak's connect() entirely because the device is already connected
            # at the OS level. Bleak's connect() waits for a GattSessionStatus.ACTIVE event,
            # but that event has already fired before the handler is attached — so it hangs.
            # Instead, we manually set up _requester and _session on the backend.
            try:
                remote_mac = self.address.split("-")[-1]
                address_int = int(remote_mac.replace(":", ""), 16)

                backend = self._backend

                # Get the BluetoothLEDevice for the already-connected device
                backend._requester = await BluetoothLEDevice.from_bluetooth_address_async(address_int)
                if backend._requester is None:
                    logger.error(f"Could not get BluetoothLEDevice for {self.address}")
                    return False

                # Open the GATT session (already ACTIVE since device is connected)
                backend._session = await GattSession.from_device_id_async(
                    backend._requester.bluetooth_device_id
                )
                backend._session.maintain_connection = True

                # Force uncached GATT discovery so Windows does not serve a
                # stale cached table that may be missing characteristics.
                backend.services = None
                backend.services = await backend.get_services(
                    service_cache_mode=BluetoothCacheMode.UNCACHED,
                    cache_mode=BluetoothCacheMode.UNCACHED,
                )
                if backend.services:
                    for svc in backend.services.services.values():
                        char_uuids = [str(c.uuid) for c in svc.characteristics]
                        logger.debug("Discovered service %s with characteristics: %s", svc.uuid, char_uuids)

                is_active = backend._session.session_status == GattSessionStatus.ACTIVE
                logger.info(f"Session status ACTIVE: {is_active}")
                return is_active

            except Exception as e:
                logger.error(f"connect_retrieved failed: {e}")
                return False


elif platform.system() == "Linux":
    from bleak.backends.bluezdbus import defs
    from bleak.backends.bluezdbus.utils import assert_reply, unpack_variants
    from bleak.backends.device import BLEDevice
    from dbus_next import BusType, Message, Variant
    from dbus_next.aio import MessageBus

    BLUEZ_RESOLVE_TIMEOUT_SEC = 30.0
    BLUEZ_RESOLVE_POLL_SEC = 0.25

    class TapClient(BleakClient):
        def __init__(self, address=None, **kwargs):
            if not address:
                address = "00:00:00:00:00:00"
            kwargs.setdefault("timeout", BLUEZ_RESOLVE_TIMEOUT_SEC)
            super().__init__(address, **kwargs)

        async def get_services(self, **kwargs):
            if not self.is_connected:
                from bleak.exc import BleakError
                raise BleakError("Not connected")
            if self._services_resolved:
                return self.services
            if not self._properties.get("ServicesResolved"):
                logger.info(
                    "Waiting for ServicesResolved on %s (up to %.0fs)",
                    self.address,
                    BLUEZ_RESOLVE_TIMEOUT_SEC,
                )
                self._services_resolved_event = asyncio.Event()
                try:
                    await asyncio.wait_for(
                        self._services_resolved_event.wait(),
                        BLUEZ_RESOLVE_TIMEOUT_SEC,
                    )
                finally:
                    self._services_resolved_event = None
            if not self._properties.get("ServicesResolved"):
                from bleak.exc import BleakError
                raise BleakError(
                    "ServicesResolved did not become true for {}".format(self.address)
                )
            self._services_resolved = True
            return self.services

        async def connect_retrieved(self, **kwargs) -> bool:
            try:
                await self.connect(timeout=kwargs.get("timeout", BLUEZ_RESOLVE_TIMEOUT_SEC))
            except Exception as e:
                logger.error(
                    "Failed to connect to %s: %s: %s",
                    self.address,
                    type(e).__name__,
                    e or repr(e),
                )
                return False
            connected = client_connected(self)
            if connected:
                logger.info("Connected to {0}".format(self.address))
                await self.__debug()
                connected = client_connected(self)
                if not connected:
                    logger.error("Lost connection to {0} during service dump".format(self.address))
            else:
                logger.error("Failed to connect to {0}".format(self.address))
            return connected

        async def __debug(self):
            for service in self.services:
                logger.info("[service] {}: {}".format(service.uuid, service.description))
                for char in service.characteristics:
                    logger.info(
                        "\t[Characteristic] {0}: ({1}) | Name: {2}".format(
                            char.uuid,
                            ",".join(char.properties),
                            char.description,
                        )
                    )

    def _ble_device_from_props(path, props):
        mac = props.get("Address")
        name = props.get("Name") or props.get("Alias") or ""
        return BLEDevice(
            mac,
            name,
            {"path": path, "props": props},
            rssi=props.get("RSSI", 0),
        )

    async def _bluez_managed_devices(bus):
        reply = await bus.call(
            Message(
                destination=defs.BLUEZ_SERVICE,
                path="/",
                member="GetManagedObjects",
                interface=defs.OBJECT_MANAGER_INTERFACE,
            )
        )
        assert_reply(reply)
        devices = {}
        for path, interfaces in reply.body[0].items():
            if defs.DEVICE_INTERFACE not in interfaces:
                continue
            devices[path] = unpack_variants(interfaces[defs.DEVICE_INTERFACE])
        return devices

    def _is_tap_props(props):
        name = props.get("Name") or props.get("Alias") or ""
        uuids = [u.lower() for u in props.get("UUIDs", [])]
        return name.startswith("Tap") or tap_service.lower() in uuids

    async def get_bluez_tap_devices(connected_only=False, services_resolved_only=False):
        bus = await MessageBus(bus_type=BusType.SYSTEM, negotiate_unix_fd=True).connect()
        try:
            managed = await _bluez_managed_devices(bus)
            taps = []
            for path, props in managed.items():
                is_connected = bool(props.get("Connected", False))
                if connected_only and not is_connected:
                    continue
                if services_resolved_only and not props.get("ServicesResolved", False):
                    continue
                if not _is_tap_props(props):
                    continue
                if not props.get("Address"):
                    continue
                taps.append((is_connected, _ble_device_from_props(path, props)))
            taps.sort(key=lambda item: not item[0])
            return [device for _, device in taps]
        finally:
            bus.disconnect()

    async def _bluez_set_trusted(bus, path):
        reply = await bus.call(
            Message(
                destination=defs.BLUEZ_SERVICE,
                path=path,
                interface=defs.PROPERTIES_INTERFACE,
                member="Set",
                signature="ssv",
                body=[defs.DEVICE_INTERFACE, "Trusted", Variant("b", True)],
            )
        )
        assert_reply(reply)

    async def _bluetoothctl_connect(address):
        logger.info("Connecting via bluetoothctl: %s", address)
        for args in (
            ("trust", address),
            ("pair", address),
            ("connect", address),
        ):
            proc = await asyncio.create_subprocess_exec(
                "bluetoothctl",
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            out, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=BLUEZ_RESOLVE_TIMEOUT_SEC,
            )
            text = (out or b"").decode(errors="replace").strip()
            if text:
                logger.info("bluetoothctl %s: %s", args[0], text)
        return True

    async def bluez_connect_and_resolve(device, timeout=BLUEZ_RESOLVE_TIMEOUT_SEC):
        path = device.details["path"]
        address = device.address
        bus = await MessageBus(bus_type=BusType.SYSTEM, negotiate_unix_fd=True).connect()
        try:
            managed = await _bluez_managed_devices(bus)
            props = managed.get(path)
            if props is None:
                for p, candidate in managed.items():
                    if (candidate.get("Address") or "").lower() == address.lower():
                        path, props = p, candidate
                        break
            if props is None:
                logger.error("BlueZ device not found for %s", address)
                return None

            if props.get("Connected", False) and props.get("ServicesResolved", False):
                return _ble_device_from_props(path, props)

            await _bluez_set_trusted(bus, path)

            if not props.get("Connected", False):
                await _bluetoothctl_connect(address)
                managed = await _bluez_managed_devices(bus)
                props = managed.get(path) or props
                if not props.get("Connected", False):
                    logger.info("bluetoothctl connect failed; trying BlueZ Connect")
                    reply = await bus.call(
                        Message(
                            destination=defs.BLUEZ_SERVICE,
                            path=path,
                            interface=defs.DEVICE_INTERFACE,
                            member="Connect",
                        )
                    )
                    assert_reply(reply)

            deadline = asyncio.get_running_loop().time() + timeout
            last_log = 0.0
            while asyncio.get_running_loop().time() < deadline:
                managed = await _bluez_managed_devices(bus)
                props = managed.get(path)
                if props is None:
                    for p, candidate in managed.items():
                        if (candidate.get("Address") or "").lower() == address.lower():
                            path, props = p, candidate
                            break
                if props is None:
                    logger.error("BlueZ device path disappeared while resolving: %s", address)
                    return None
                connected = bool(props.get("Connected", False))
                resolved = bool(props.get("ServicesResolved", False))
                paired = bool(props.get("Paired", False))
                now = asyncio.get_running_loop().time()
                if now - last_log >= 2.0:
                    logger.info(
                        "BlueZ %s: Connected=%s Paired=%s ServicesResolved=%s",
                        address,
                        connected,
                        paired,
                        resolved,
                    )
                    last_log = now
                if connected and resolved:
                    logger.info("BlueZ ready for %s", address)
                    return _ble_device_from_props(path, props)
                await asyncio.sleep(BLUEZ_RESOLVE_POLL_SEC)

            logger.error(
                "Timed out waiting for BlueZ ServicesResolved on %s "
                "(Connected=%s Paired=%s ServicesResolved=%s)",
                address,
                props.get("Connected", False),
                props.get("Paired", False),
                props.get("ServicesResolved", False),
            )
            return None
        finally:
            bus.disconnect()

    def _filter_address(devices, address):
        if not address:
            return devices
        return [d for d in devices if d.address.lower() == address.lower()]

    async def _attach_resolved(device) -> TapClient:
        resolved = await bluez_connect_and_resolve(device)
        if resolved is None:
            return None
        client = TapClient(resolved)
        if await client.connect_retrieved():
            return client
        return None

    async def connect_tap_linux(address=None) -> TapClient:
        if address is not None and not isinstance(address, str):
            client = await _attach_resolved(address)
            if client is not None:
                return client

        known = _filter_address(
            await get_bluez_tap_devices(connected_only=True, services_resolved_only=True),
            address if isinstance(address, str) else None,
        )
        if known:
            logger.info("Attaching to already-connected Tap @ %s", known[0].address)
            client = await _attach_resolved(known[0])
            if client is not None:
                return client

        logger.info("No connected Tap found. Scanning and waiting for a Tap device...")
        found_event = asyncio.Event()
        found = {}
        addr_filter = address if isinstance(address, str) else None

        async def detection_cb(device, adv_data):
            logger.debug("detected %s %s", device, adv_data)
            uuids = [u.lower() for u in (adv_data.service_uuids or [])]
            name = device.name or ""
            if tap_service.lower() in uuids or name.startswith("Tap"):
                if addr_filter and device.address.lower() != addr_filter.lower():
                    return
                logger.info("Found advertising Tap via scan: %s", device.address)
                found["scanned"] = device
                found_event.set()

        async def bluez_reconnect_poller():
            while not found_event.is_set():
                await asyncio.sleep(1)
                taps = _filter_address(
                    await get_bluez_tap_devices(
                        connected_only=True,
                        services_resolved_only=True,
                    ),
                    addr_filter,
                )
                if taps:
                    logger.info("Found Tap connected via BlueZ: %s", taps[0].address)
                    found["bluez"] = taps[0]
                    found_event.set()

        async with BleakScanner(detection_callback=detection_cb):
            poller_task = asyncio.create_task(bluez_reconnect_poller())
            await found_event.wait()
            poller_task.cancel()

        device = found.get("bluez") or found.get("scanned")
        client = await _attach_resolved(device)
        if client is None:
            raise ConnectionError("Failed to connect to a Tap device")
        return client


async def connect_tap(address=None) -> TapClient:
    """Scan/attach to a Tap and return a connected client with GATT services.

    Uses the same platform paths as the former TapSDK.run() connect half:
    retrieve already-connected devices when possible; otherwise scan (and on
    Windows poll for paired reconnects).
    """
    if platform.system() == "Linux":
        return await connect_tap_linux(address=address)

    if platform.system() == "Windows":
        # First, try to attach to an already-connected Tap device
        tap_device = address or await get_tap_device()
        client = None
        connected = False
        if tap_device:
            client = TapClient(tap_device)
            connected = await client.connect_retrieved()

        if not connected:
            # Run BleakScanner and Windows reconnect-poller concurrently.
            # - BleakScanner finds unpaired/advertising devices and pairs them.
            # - The poller detects already-paired devices reconnecting (not advertising).
            logger.info("No connected Tap found. Scanning and waiting for a Tap device...")
            found_event = asyncio.Event()
            found_device = {}  # shared mutable container

            async def detection_cb(device, adv_data):
                if tap_service.lower() in adv_data.service_uuids:
                    logger.info(f"Found advertising Tap via scan: {device.address}")
                    found_device["scanned"] = device
                    found_event.set()

            async def windows_reconnect_poller():
                """Poll Windows for already-paired Tap devices reconnecting."""
                while not found_event.is_set():
                    await asyncio.sleep(3)
                    tap_id = await get_tap_device()
                    if tap_id:
                        logger.info(f"Found already-paired Tap reconnected: {tap_id}")
                        found_device["winrt"] = tap_id
                        found_event.set()

            async with BleakScanner(detection_callback=detection_cb):
                poller_task = asyncio.create_task(windows_reconnect_poller())
                await found_event.wait()
                poller_task.cancel()

            if "winrt" in found_device:
                # Already-paired device reconnected — attach via WinRT path
                client = TapClient(found_device["winrt"])
                connected = await client.connect_retrieved()
            elif "scanned" in found_device:
                # Device was seen advertising. Windows may have already claimed the
                # connection by now, so try the WinRT path first, then fall back to
                # Bleak's connect()+pair() if the device is still advertising.
                await asyncio.sleep(1)  # brief wait for Windows to finish pairing
                tap_id = await get_tap_device()
                if tap_id:
                    logger.info(f"Scanned device is now connected via Windows: {tap_id}")
                    client = TapClient(tap_id)
                    connected = await client.connect_retrieved()
                if not connected:
                    logger.info("Falling back to Bleak connect+pair...")
                    client = TapClient(found_device["scanned"])
                    await client.connect()
                    await client.pair(protection_level=2)
                    connected = client_connected(client)

        if client is None or not client_connected(client):
            raise ConnectionError("Failed to connect to a Tap device on Windows")
        return client

    # Darwin
    stop_event = asyncio.Event()
    devices = []

    async def detection_cb(device, adv_data):
        logger.debug("detected %s %s", device, adv_data)
        if tap_service.lower() in adv_data.service_uuids:
            if device.address not in [d.address for d in devices]:
                devices.append(device)
                stop_event.set()

    client = TapClient(address=address if address is not None else "")

    connected = await client.connect_retrieved()
    if not connected:
        logger.info("Couldn't find connected Tap device. Scanning for Tap devices...")
        async with BleakScanner(detection_callback=detection_cb):
            await stop_event.wait()

        client = TapClient(devices[0])
        await client.connect()

    if not client_connected(client):
        raise ConnectionError("Failed to connect to a Tap device")
    return client

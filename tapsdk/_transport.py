import asyncio
import atexit
import functools
import logging
import platform

from bleak import BleakClient, BleakScanner

logger = logging.getLogger(__name__)

tap_service = "c3ff0001-1d8b-40fd-a56f-c7bd5d0f3370"


def client_connected(client) -> bool:
    """Return whether ``client`` reports an active GATT connection."""
    return bool(getattr(client, "is_connected", False))


def set_disconnected_callback(client, callback) -> None:
    """Register a disconnect callback on Bleak 3.x (constructor-only public API)."""
    if callback is None:
        client._backend.set_disconnected_callback(None)
        return
    client._backend.set_disconnected_callback(functools.partial(callback, client))


if platform.system() == "Darwin":
    try:
        from bleak.backends.corebluetooth.CentralManagerDelegate import (
            CBUUID,
            CentralManagerDelegate,
        )
        from bleak.backends.device import BLEDevice
    except ImportError as e:
        raise ImportError(
            "tapsdk requires bleak>=3.0.2 on macOS. Reinstall with the pinned "
            "dependency from setup.py."
        ) from e

    def string2uuid(uuid_str: str) -> CBUUID:
        return CBUUID.UUIDWithString_(uuid_str)

    def _ble_device_from_peripheral(peripheral, manager) -> BLEDevice:
        return BLEDevice(
            peripheral.identifier().UUIDString(),
            peripheral.name(),
            (peripheral, manager),
        )

    async def _darwin_retrieve_connected_ble_device():
        manager = CentralManagerDelegate()
        await manager.wait_until_ready()
        peripherals = manager.central_manager.retrieveConnectedPeripheralsWithServices_(
            [string2uuid(tap_service)]
        )
        logger.debug("Found connected Taps @ %s", peripherals)
        if not peripherals:
            return None
        return _ble_device_from_peripheral(peripherals[0], manager)

    class TapClient(BleakClient):
        async def connect_retrieved(self, **kwargs) -> bool:
            try:
                await self.connect(timeout=kwargs.get("timeout", 30))
            except Exception as e:
                logger.error("connect_retrieved failed: %s", e)
                return False
            return client_connected(self)

elif platform.system() == "Windows":
    # See docs/windows-ble-connect-notes.md#watchdog-timing-windows_connect_attempt_watchdog_sec
    WINDOWS_CONNECT_ATTEMPT_WATCHDOG_SEC = 20

    try:
        from winrt.windows.devices.bluetooth import (  # noqa: F401
            BluetoothCacheMode,
            BluetoothConnectionStatus,
            BluetoothLEDevice,
        )
        from winrt.windows.devices.bluetooth.genericattributeprofile import (  # noqa: F401
            GattSession,
            GattSessionStatus,
        )
        from winrt.windows.devices.enumeration import (  # noqa: F401
            DeviceInformation,
            DeviceInformationKind,
        )
    except ImportError as e:
        raise ImportError(
            "tapsdk requires bleak>=3.0.2 on Windows (PyWinRT via bleak). "
            "Reinstall with the pinned dependency from setup.py."
        ) from e

    def _windows_parse_address_from_device_id(device_id: str):
        if not device_id or "-" not in device_id:
            return None
        candidate = device_id.split("-")[-1].upper()
        try:
            int(candidate.replace(":", ""), 16)
        except ValueError:
            return None
        if ":" in candidate:
            return candidate
        if len(candidate) != 12:
            return None
        return ":".join(candidate[i : i + 2] for i in range(0, 12, 2))

    async def get_connected_taps():
        request_properties = [
            "System.Devices.Aep.IsPaired",
            "System.Devices.Aep.IsConnected",
            "System.Devices.Aep.DeviceAddress",
        ]
        aqs_filter = BluetoothLEDevice.get_device_selector_from_connection_status(
            BluetoothConnectionStatus.CONNECTED
        )
        devices = await DeviceInformation.find_all_async_with_kind_aqs_filter_and_additional_properties(
            aqs_filter,
            request_properties,
            DeviceInformationKind.ASSOCIATION_ENDPOINT,
        )
        taps = []
        for device in devices:
            logger.debug("Candidate connected AEP device: name=%s id=%s", device.name, device.id)
            try:
                device_address_str = _windows_parse_address_from_device_id(device.id)
                if not device_address_str:
                    logger.debug("Skipping AEP device with unparseable address in id=%s", device.id)
                    continue
                address_int = int(device_address_str.replace(":", ""), 16)
                ble_device = await BluetoothLEDevice.from_bluetooth_address_async(
                    address_int
                )
                if ble_device is None:
                    logger.error(
                        "Could not create BLE device for %s (id=%s, parsed_address=%s)",
                        device.name,
                        device.id,
                        device_address_str,
                    )
                    continue
                try:
                    services = await ble_device.get_gatt_services_async()
                    logger.info("Device %s has the following services:", device.name)
                    for service in services.services:
                        logger.info("Service UUID: %s", service.uuid)
                        if str(service.uuid).lower() == tap_service.lower():
                            taps.append(device_address_str)
                            break
                finally:
                    # See docs/windows-ble-connect-notes.md#closing-ble-device-handles-in-get_connected_taps
                    close = getattr(ble_device, "close", None)
                    if callable(close):
                        try:
                            close()
                        except Exception:
                            pass
            except Exception as e:
                logger.error(
                    "Failed to retrieve services for device %s: %s", device.name, e
                )
        return taps

    async def get_tap_device():
        taps = await get_connected_taps()
        if not taps:
            logger.info("No connected Tap devices found.")
            return None
        return taps[0]

    async def _windows_warn_if_unbonded(client) -> None:
        # See docs/windows-ble-connect-notes.md#unbonded-connection-warning-_windows_warn_if_unbonded
        try:
            requester = getattr(client._backend, "_requester", None)
            if requester is None:
                return
            device_information = await DeviceInformation.create_from_id_async(
                requester.device_information.id
            )
            if not device_information.pairing.is_paired:
                logger.warning(
                    "Tap @ %s is not paired/bonded with Windows. This can "
                    "cause v2-only GATT characteristics to be missing from "
                    "discovery (protocol misdetected as v1, 'Characteristic "
                    "... was not found!' warnings). Fix: pair the Tap "
                    "manually via Windows Settings > Bluetooth & devices > "
                    "Add device, power-cycle the Tap, then rerun.",
                    client.address,
                )
        except Exception:
            pass

    class TapClient(BleakClient):
        def __init__(self, *args, **kwargs):
            # See docs/windows-ble-connect-notes.md#forcing-uncached-services-in-tapclient__init__
            kwargs.setdefault("winrt", {}).setdefault("use_cached_services", False)
            super().__init__(*args, **kwargs)

        async def connect_retrieved(self, **kwargs) -> bool:
            if not self.address:
                logger.info("No connected Tap devices found.")
                return False
            logger.info("Connecting to Tap device @ %s", self.address)
            # See docs/windows-ble-connect-notes.md#primary-connect-timeout-vs-watchdog
            timeout = kwargs.get("timeout", 8)
            primary_error = None
            # See docs/windows-ble-connect-notes.md#already_connected---skipping-the-doomed-primary-connect
            if not kwargs.get("already_connected", False):
                try:
                    await self.connect(timeout=timeout)
                except Exception as e:
                    primary_error = e
                else:
                    return client_connected(self)

            try:
                address_int = int(str(self.address).replace(":", ""), 16)
            except ValueError:
                logger.error("connect_retrieved failed: %s", primary_error)
                return False

            try:
                requester = await BluetoothLEDevice.from_bluetooth_address_async(
                    address_int
                )
                if requester is None:
                    logger.error(
                        "WinRT fallback could not create BluetoothLEDevice for %s",
                        self.address,
                    )
                    return False

                backend = self._backend
                backend._requester = requester

                # See docs/windows-ble-connect-notes.md#services-changed-retry-loop-in-the-winrt-fallback
                loop = asyncio.get_running_loop()
                services_changed_event = asyncio.Event()

                def _on_services_changed(sender, args) -> None:
                    loop.call_soon_threadsafe(services_changed_event.set)

                services_changed_token = requester.add_gatt_services_changed(
                    _on_services_changed
                )
                try:
                    backend._session = await GattSession.from_device_id_async(
                        requester.bluetooth_device_id
                    )
                    backend._session.maintain_connection = True

                    # See docs/windows-ble-connect-notes.md#leaked-gattsession-cleanup-atexit
                    def _close_leaked_session(_backend=backend) -> None:
                        try:
                            if _backend._session is not None:
                                _backend._session.close()
                                _backend._session = None
                        except Exception:
                            pass
                        try:
                            if _backend._requester is not None:
                                _backend._requester.close()
                                _backend._requester = None
                        except Exception:
                            pass

                    atexit.register(_close_leaked_session)

                    load_services = getattr(backend, "get_services", None)
                    if load_services is None:
                        load_services = getattr(backend, "_get_services", None)
                    if load_services is None:
                        logger.error(
                            "WinRT fallback has no service loader on backend for %s",
                            self.address,
                        )
                        return False

                    service_cache_mode = BluetoothCacheMode.UNCACHED
                    while True:
                        services_changed_event.clear()
                        services = await load_services(
                            service_cache_mode=service_cache_mode,
                            cache_mode=BluetoothCacheMode.UNCACHED,
                        )
                        if not services_changed_event.is_set():
                            backend.services = services
                            break
                        logger.debug(
                            "WinRT fallback: services changed mid-discovery "
                            "for %s, re-fetching",
                            self.address,
                        )
                        # See docs/windows-ble-connect-notes.md#service-cache-mode-on-retry
                        service_cache_mode = BluetoothCacheMode.CACHED

                    # See docs/windows-ble-connect-notes.md#polling-for-session_status--active
                    session_deadline = asyncio.get_running_loop().time() + 5.0
                    while (
                        backend._session.session_status != GattSessionStatus.ACTIVE
                        and asyncio.get_running_loop().time() < session_deadline
                    ):
                        await asyncio.sleep(0.1)
                    if backend._session.session_status != GattSessionStatus.ACTIVE:
                        logger.warning(
                            "WinRT fallback GattSession not ACTIVE after 5s "
                            "for %s (status=%s); characteristics may still "
                            "be incomplete.",
                            self.address,
                            backend._session.session_status,
                        )
                finally:
                    requester.remove_gatt_services_changed(services_changed_token)

                if backend._session.session_status == GattSessionStatus.ACTIVE:
                    if primary_error is not None:
                        logger.info(
                            "Primary address connect failed (%s); WinRT fallback session is active for %s",
                            primary_error,
                            self.address,
                        )
                    logger.info(
                        "WinRT fallback session active for %s",
                        self.address,
                    )
                    return True
            except Exception as fallback_error:
                logger.error(
                    "connect_retrieved failed for %s (primary=%s, fallback=%s)",
                    self.address,
                    primary_error,
                    fallback_error,
                )
            return False

elif platform.system() == "Linux":
    from bleak.backends.device import BLEDevice
    from dbus_fast.aio import MessageBus
    from dbus_fast.constants import BusType, MessageType
    from dbus_fast.message import Message
    from dbus_fast.signature import Variant

    BLUEZ_SERVICE = "org.bluez"
    DEVICE_INTERFACE = "org.bluez.Device1"
    OBJECT_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"
    PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"

    BLUEZ_RESOLVE_TIMEOUT_SEC = 30.0
    BLUEZ_RESOLVE_POLL_SEC = 0.25

    def _assert_reply(reply: Message) -> None:
        if reply.message_type == MessageType.ERROR:
            raise RuntimeError(f"D-Bus error: {reply.error_name} {reply.body}")
        assert reply.message_type == MessageType.METHOD_RETURN

    def _unpack_variants(props):
        return {
            key: (value.value if isinstance(value, Variant) else value)
            for key, value in props.items()
        }

    class TapClient(BleakClient):
        def __init__(self, address=None, **kwargs):
            if not address:
                address = "00:00:00:00:00:00"
            kwargs.setdefault("timeout", BLUEZ_RESOLVE_TIMEOUT_SEC)
            super().__init__(address, **kwargs)

        async def connect_retrieved(self, **kwargs) -> bool:
            try:
                await self.connect(
                    timeout=kwargs.get("timeout", BLUEZ_RESOLVE_TIMEOUT_SEC)
                )
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
                logger.info("Connected to %s", self.address)
                await self._debug_services()
                connected = client_connected(self)
                if not connected:
                    logger.error(
                        "Lost connection to %s during service dump", self.address
                    )
            else:
                logger.error("Failed to connect to %s", self.address)
            return connected

        async def _debug_services(self):
            for service in self.services:
                logger.info(
                    "[service] %s: %s", service.uuid, service.description
                )
                for char in service.characteristics:
                    logger.info(
                        "\t[Characteristic] %s: (%s) | Name: %s",
                        char.uuid,
                        ",".join(char.properties),
                        char.description,
                    )

    def _ble_device_from_props(path, props):
        mac = props.get("Address")
        name = props.get("Name") or props.get("Alias") or ""
        return BLEDevice(mac, name, {"path": path, "props": props})

    async def _bluez_managed_devices(bus):
        reply = await bus.call(
            Message(
                destination=BLUEZ_SERVICE,
                path="/",
                member="GetManagedObjects",
                interface=OBJECT_MANAGER_INTERFACE,
            )
        )
        _assert_reply(reply)
        devices = {}
        for path, interfaces in reply.body[0].items():
            if DEVICE_INTERFACE not in interfaces:
                continue
            devices[path] = _unpack_variants(interfaces[DEVICE_INTERFACE])
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
                destination=BLUEZ_SERVICE,
                path=path,
                interface=PROPERTIES_INTERFACE,
                member="Set",
                signature="ssv",
                body=[DEVICE_INTERFACE, "Trusted", Variant("b", True)],
            )
        )
        _assert_reply(reply)

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
                            destination=BLUEZ_SERVICE,
                            path=path,
                            interface=DEVICE_INTERFACE,
                            member="Connect",
                        )
                    )
                    _assert_reply(reply)

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
                    logger.error(
                        "BlueZ device path disappeared while resolving: %s", address
                    )
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


async def connect_tap(address=None, skip_scan: bool = False) -> TapClient:
    """Scan/attach to a Tap and return a connected client with GATT services.

    Uses the same platform paths as the former TapSDK.run() connect half:
    retrieve already-connected devices when possible; otherwise scan (and on
    Windows poll for paired reconnects).

    ``skip_scan`` (Windows only): if True, never falls back to the
    BleakScanner-based scan/poll loop - only attempts to attach to a Tap
    already reported connected/paired via AEP (``get_tap_device()``) or an
    explicitly given ``address``. Raises ``ConnectionError`` immediately if
    that attempt doesn't succeed.
    """
    if platform.system() == "Linux":
        return await connect_tap_linux(address=address)

    if platform.system() == "Windows":
        async def _try_connect_retrieved(client, **kwargs):
            try:
                return await asyncio.wait_for(
                    client.connect_retrieved(**kwargs),
                    timeout=WINDOWS_CONNECT_ATTEMPT_WATCHDOG_SEC,
                )
            except asyncio.TimeoutError:
                logger.error(
                    "connect_retrieved timed out for %s after %ss",
                    getattr(client, "address", None),
                    WINDOWS_CONNECT_ATTEMPT_WATCHDOG_SEC,
                )
                return False
            except asyncio.CancelledError as e:
                logger.error(
                    "connect_retrieved cancelled for %s: %s",
                    getattr(client, "address", None),
                    e,
                )
                return False
            except Exception as e:
                logger.error(
                    "connect_retrieved failed for %s: %s",
                    getattr(client, "address", None),
                    e,
                )
                return False

        tap_device = address or await get_tap_device()
        # See docs/windows-ble-connect-notes.md#already_connected-derivation-in-connect_tap
        already_connected = tap_device is not None and address is None
        client = None
        connected = False
        if tap_device:
            client = TapClient(tap_device)
            connected = await _try_connect_retrieved(
                client, already_connected=already_connected
            )

        if not connected and skip_scan:
            raise ConnectionError(
                "No Tap device is currently connected/paired in Windows "
                "(skip_scan=True, not falling back to a BLE scan)."
            )

        if not connected:
            logger.info("No connected Tap found. Scanning and waiting for a Tap device...")
            while not connected:
                found_event = asyncio.Event()
                found_device = {}
                saw_advertisement = False
                waiting_log_emitted = False

                async def detection_cb(device, adv_data):
                    nonlocal saw_advertisement
                    uuids = [u.lower() for u in (adv_data.service_uuids or [])]
                    name = (getattr(device, "name", "") or "")
                    if tap_service.lower() in uuids or name.startswith("Tap"):
                        if not saw_advertisement:
                            logger.info("Found advertising Tap via scan: %s", device.address)
                        saw_advertisement = True
                        found_device["scanned"] = device
                        found_event.set()

                async def windows_reconnect_poller():
                    nonlocal waiting_log_emitted
                    while not found_event.is_set():
                        await asyncio.sleep(3)
                        tap_id = await get_tap_device()
                        if tap_id:
                            logger.info("Found already-paired Tap reconnected: %s", tap_id)
                            found_device["winrt"] = tap_id
                            found_event.set()
                            continue
                        if saw_advertisement and not waiting_log_emitted:
                            logger.info(
                                "Tap is advertising but not connected/paired in Windows yet; "
                                "trying direct BLE connection from scan results."
                            )
                            waiting_log_emitted = True

                async with BleakScanner(detection_callback=detection_cb):
                    poller_task = asyncio.create_task(windows_reconnect_poller())
                    await found_event.wait()
                    poller_task.cancel()

                if "winrt" in found_device:
                    client = TapClient(found_device["winrt"])
                    connected = await _try_connect_retrieved(
                        client, already_connected=True
                    )
                    if connected:
                        break

                if "scanned" in found_device:
                    scan_client = TapClient(found_device["scanned"])
                    if await _try_connect_retrieved(scan_client):
                        client = scan_client
                        connected = True
                        break
                    logger.info(
                        "Direct BLE connect to scanned Tap failed; continuing to scan."
                    )
                    tap_id = await get_tap_device()
                    if tap_id:
                        logger.info("Found already-paired Tap reconnected: %s", tap_id)
                        client = TapClient(tap_id)
                        connected = await _try_connect_retrieved(
                            client, already_connected=True
                        )
                        if connected:
                            break
                    await asyncio.sleep(1)

        if client is None or not client_connected(client):
            raise ConnectionError("Failed to connect to a Tap device on Windows")
        await _windows_warn_if_unbonded(client)
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

    if address:
        client = TapClient(address)
        if await client.connect_retrieved():
            return client
    else:
        retrieved = await _darwin_retrieve_connected_ble_device()
        if retrieved is not None:
            client = TapClient(retrieved)
            if await client.connect_retrieved():
                return client

    logger.info("Couldn't find connected Tap device. Scanning for Tap devices...")
    async with BleakScanner(detection_callback=detection_cb):
        await stop_event.wait()

    client = TapClient(devices[0])
    await client.connect()

    if not client_connected(client):
        raise ConnectionError("Failed to connect to a Tap device")
    return client

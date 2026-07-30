import asyncio
from unittest.mock import AsyncMock, MagicMock

from tapsdk.tap import DeviceInfo, TapSDK, _format_model_version_hex
from tapsdk.tap import (
    battery_level_characteristic,
    device_name_characteristic,
    firmware_revision_characteristic,
    fw_version2_characteristic,
    gap_device_name_characteristic,
    hardware_revision_characteristic,
    manufacturer_name_characteristic,
    model_version_characteristic,
    serial_number_characteristic,
    software_revision_characteristic,
)


def test_format_model_version_hex():
    assert _format_model_version_hex("42") == "0x2A"
    assert _format_model_version_hex("0") == "0x0"
    assert _format_model_version_hex(None) is None


def test_get_device_info_reads_dis_and_bas():
    values = {
        device_name_characteristic: b"Tap_XR42",
        firmware_revision_characteristic: b"3.5.24",
        fw_version2_characteristic: b"1.5.24",
        model_version_characteristic: b"42",
        hardware_revision_characteristic: b"4.4",
        serial_number_characteristic: b"ABCDEF0123456789",
        manufacturer_name_characteristic: b"TAP Systems",
        software_revision_characteristic: b"012",
        battery_level_characteristic: bytes([87]),
    }

    async def read_gatt_char(uuid):
        return values[uuid]

    sdk = TapSDK.__new__(TapSDK)
    sdk.client = MagicMock()
    sdk.client.name = None
    sdk.client.read_gatt_char = AsyncMock(side_effect=read_gatt_char)

    info = asyncio.run(sdk.get_device_info())

    assert info == DeviceInfo(
        name="Tap_XR42",
        fw_version="3.5.24",
        fw_version2="1.5.24",
        model_version="0x2A",
        hardware_revision="4.4",
        serial_number="ABCDEF0123456789",
        manufacturer="TAP Systems",
        software_revision="012",
        battery_level=87,
    )


def test_get_device_info_prefers_client_name_and_tolerates_missing_chars():
    async def read_gatt_char(uuid):
        if uuid == firmware_revision_characteristic:
            return b"1.2.3"
        raise Exception("missing")

    sdk = TapSDK.__new__(TapSDK)
    sdk.client = MagicMock()
    sdk.client.name = "Tap_FromScan"
    sdk.client.read_gatt_char = AsyncMock(side_effect=read_gatt_char)

    info = asyncio.run(sdk.get_device_info())

    assert info.name == "Tap_FromScan"
    assert info.fw_version == "1.2.3"
    assert info.fw_version2 is None
    assert info.model_version is None
    assert info.battery_level is None
    assert info.serial_number is None


def test_resolve_device_name_falls_back_to_tap_characteristic():
    async def read_gatt_char(uuid):
        if uuid == device_name_characteristic:
            return b"Tap_FromGatt"
        if uuid == gap_device_name_characteristic:
            return b"ShouldNotUse"
        return None

    sdk = TapSDK.__new__(TapSDK)
    sdk.client = MagicMock()
    sdk.client.name = None
    sdk.client.read_gatt_char = AsyncMock(side_effect=read_gatt_char)

    name = asyncio.run(sdk._resolve_device_name())
    assert name == "Tap_FromGatt"

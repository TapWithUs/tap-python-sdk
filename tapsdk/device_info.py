"""Shared device metadata reads (DIS/BAS + Tap proprietary fields).

Not protocol-specific — same GATT UUIDs on v1 and v2 firmware.
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Standard BLE services exposed by Tap firmware (DIS + BAS).
device_information_service = '0000180a-0000-1000-8000-00805f9b34fb'
battery_service = '0000180f-0000-1000-8000-00805f9b34fb'
manufacturer_name_characteristic = '00002a29-0000-1000-8000-00805f9b34fb'
serial_number_characteristic = '00002a25-0000-1000-8000-00805f9b34fb'
hardware_revision_characteristic = '00002a27-0000-1000-8000-00805f9b34fb'
firmware_revision_characteristic = '00002a26-0000-1000-8000-00805f9b34fb'
software_revision_characteristic = '00002a28-0000-1000-8000-00805f9b34fb'  # bootloader on Tap
battery_level_characteristic = '00002a19-0000-1000-8000-00805f9b34fb'
gap_device_name_characteristic = '00002a00-0000-1000-8000-00805f9b34fb'

# Tap proprietary readable fields (same on v1/v2 devices).
device_name_characteristic = 'c3ff0003-1d8b-40fd-a56f-c7bd5d0f3370'
model_version_characteristic = 'c3ff000c-1d8b-40fd-a56f-c7bd5d0f3370'
fw_version2_characteristic = 'c3ff000d-1d8b-40fd-a56f-c7bd5d0f3370'


@dataclass(frozen=True)
class DeviceInfo:
    """Public device information from BLE DIS/BAS and Tap service fields."""
    name: Optional[str] = None
    fw_version: Optional[str] = None
    fw_version2: Optional[str] = None
    model_version: Optional[str] = None
    hardware_revision: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    software_revision: Optional[str] = None
    battery_level: Optional[int] = None


def format_model_version_hex(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    try:
        return f"0x{int(value):X}"
    except ValueError:
        return value


async def _read_gatt_string(client, uuid: str) -> Optional[str]:
    try:
        raw = await client.read_gatt_char(uuid)
    except Exception as e:
        logger.debug("Failed to read %s: %s", uuid, e)
        return None
    if not raw:
        return None
    return bytes(raw).decode("utf-8", errors="replace").rstrip("\x00").strip() or None


async def _read_gatt_uint8(client, uuid: str) -> Optional[int]:
    try:
        raw = await client.read_gatt_char(uuid)
    except Exception as e:
        logger.debug("Failed to read %s: %s", uuid, e)
        return None
    if not raw:
        return None
    return int(raw[0])


async def resolve_device_name(client) -> Optional[str]:
    name = getattr(client, "name", None) or None
    if name:
        return name
    # Tap stores the user-visible name on the proprietary readable char (not GAP 0x2a00).
    name = await _read_gatt_string(client, device_name_characteristic)
    if name:
        return name
    return await _read_gatt_string(client, gap_device_name_characteristic)


async def read_device_info(client) -> DeviceInfo:
    """Read device name, FW versions, battery, and other public device fields.

    Requires a bonded connection (these characteristics are encrypted on Tap
    firmware). Missing characteristics yield None for that field.
    """
    model_version_raw = await _read_gatt_string(client, model_version_characteristic)

    return DeviceInfo(
        name=await resolve_device_name(client),
        fw_version=await _read_gatt_string(client, firmware_revision_characteristic),
        fw_version2=await _read_gatt_string(client, fw_version2_characteristic),
        model_version=format_model_version_hex(model_version_raw),
        hardware_revision=await _read_gatt_string(client, hardware_revision_characteristic),
        serial_number=await _read_gatt_string(client, serial_number_characteristic),
        manufacturer=await _read_gatt_string(client, manufacturer_name_characteristic),
        software_revision=await _read_gatt_string(client, software_revision_characteristic),
        battery_level=await _read_gatt_uint8(client, battery_level_characteristic),
    )

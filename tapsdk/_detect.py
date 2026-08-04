import asyncio
from typing import Literal

V2_READ_CHAR = "c3ff000e-1d8b-40fd-a56f-c7bd5d0f3370"


async def ensure_gatt_services(client) -> None:
    """Populate ``client.services`` when connect left discovery unfinished."""
    if getattr(client, "services", None):
        return
    get_services = getattr(client, "get_services", None)
    if not callable(get_services):
        return
    result = get_services()
    if asyncio.iscoroutine(result):
        await result


def detect_protocol(client) -> Literal["v1", "v2"]:
    """Return ``\"v2\"`` if the framed-protocol read characteristic is present.

    Requires GATT services to be discovered. Call ``ensure_gatt_services`` first
    when the client may still have an empty service cache.
    """
    services = getattr(client, "services", None)
    if not services:
        raise ConnectionError(
            "GATT services not available; cannot detect Tap protocol"
        )
    for service in services:
        for char in service.characteristics:
            if str(char.uuid).lower() == V2_READ_CHAR:
                return "v2"
    return "v1"

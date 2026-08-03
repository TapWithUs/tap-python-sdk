from typing import Literal

V2_READ_CHAR = "c3ff000e-1d8b-40fd-a56f-c7bd5d0f3370"


def detect_protocol(client) -> Literal["v1", "v2"]:
    """Return ``\"v2\"`` if the framed-protocol read characteristic is present."""
    services = getattr(client, "services", None)
    if not services:
        return "v1"
    for service in services:
        for char in service.characteristics:
            if str(char.uuid).lower() == V2_READ_CHAR:
                return "v2"
    return "v1"

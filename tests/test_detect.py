import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from tapsdk._detect import V2_READ_CHAR, detect_protocol, ensure_gatt_services


def _fake_client(char_uuids):
    chars = [SimpleNamespace(uuid=u) for u in char_uuids]
    service = SimpleNamespace(characteristics=chars)
    return SimpleNamespace(services=[service])


def test_detect_protocol_v2_when_read_char_present():
    client = _fake_client([
        "c3ff0001-1d8b-40fd-a56f-c7bd5d0f3370",
        V2_READ_CHAR,
        "c3ff000f-1d8b-40fd-a56f-c7bd5d0f3370",
    ])
    assert detect_protocol(client) == "v2"


def test_detect_protocol_v1_without_v2_char():
    client = _fake_client([
        "c3ff0005-1d8b-40fd-a56f-c7bd5d0f3370",
        "c3ff0006-1d8b-40fd-a56f-c7bd5d0f3370",
    ])
    assert detect_protocol(client) == "v1"


def test_detect_protocol_raises_when_no_services():
    with pytest.raises(ConnectionError, match="GATT services"):
        detect_protocol(SimpleNamespace(services=None))
    with pytest.raises(ConnectionError, match="GATT services"):
        detect_protocol(SimpleNamespace(services=[]))


def test_detect_protocol_case_insensitive():
    client = _fake_client([V2_READ_CHAR.upper()])
    assert detect_protocol(client) == "v2"


def test_ensure_gatt_services_skips_when_populated():
    client = _fake_client([V2_READ_CHAR])
    client.get_services = AsyncMock()
    asyncio.run(ensure_gatt_services(client))
    client.get_services.assert_not_called()


def test_ensure_gatt_services_discovers_when_empty():
    service = SimpleNamespace(
        characteristics=[SimpleNamespace(uuid=V2_READ_CHAR)],
    )

    async def get_services():
        client.services = [service]

    client = SimpleNamespace(services=None, get_services=get_services)
    asyncio.run(ensure_gatt_services(client))
    assert detect_protocol(client) == "v2"


def test_connect_ensures_services_before_detect():
    from tapsdk import connect
    from tapsdk.tap2 import TapSDK2

    service = SimpleNamespace(
        characteristics=[SimpleNamespace(uuid=V2_READ_CHAR)],
    )

    async def get_services():
        client.services = [service]

    client = SimpleNamespace(services=None, get_services=get_services)

    with patch("tapsdk._transport.connect_tap", new=AsyncMock(return_value=client)):
        sdk = asyncio.run(connect())
    assert isinstance(sdk, TapSDK2)
    assert client.services == [service]

from types import SimpleNamespace

from tapsdk._transport import client_connected


def test_client_connected_plain_bool():
    assert client_connected(SimpleNamespace(is_connected=True)) is True
    assert client_connected(SimpleNamespace(is_connected=False)) is False


def test_client_connected_missing_property():
    assert client_connected(SimpleNamespace()) is False

import asyncio
from types import SimpleNamespace

from tapsdk._transport import client_connected


def test_client_connected_plain_bool():
    assert client_connected(SimpleNamespace(is_connected=True)) is True
    assert client_connected(SimpleNamespace(is_connected=False)) is False


def test_client_connected_bleak012_wrapper_not_called():
    """bleak 0.12 wrapper is callable but must not be called (returns a Future)."""

    class DeprecatedIsConnectedReturn:
        def __init__(self, value):
            self._value = value
            self.calls = 0

        def __bool__(self):
            return self._value

        def __call__(self):
            self.calls += 1
            fut = asyncio.get_event_loop().create_future()
            fut.set_result(self._value)
            return fut

    wrapper = DeprecatedIsConnectedReturn(False)
    assert client_connected(SimpleNamespace(is_connected=wrapper)) is False
    assert wrapper.calls == 0

    wrapper_true = DeprecatedIsConnectedReturn(True)
    assert client_connected(SimpleNamespace(is_connected=wrapper_true)) is True
    assert wrapper_true.calls == 0


def test_client_connected_future_from_callable_not_treated_as_connected():
    def fake_is_connected():
        fut = asyncio.get_event_loop().create_future()
        fut.set_result(False)
        return fut

    # No _value attr — falls through to callable path; Future.result() is False
    assert client_connected(SimpleNamespace(is_connected=fake_is_connected)) is False

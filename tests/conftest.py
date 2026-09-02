import sys
import types


def pytest_configure(config):
    def stub(name, **attrs):
        mod = sys.modules.setdefault(name, types.ModuleType(name))
        for key, value in attrs.items():
            setattr(mod, key, value)
        return mod

    class Dummy:
        def __init__(self, *args, **kwargs):
            pass

    def noop(*a, **k):
        pass

    stub("bleak", BleakClient=Dummy, BleakScanner=Dummy,
         _logger=types.SimpleNamespace(debug=noop, info=noop, error=noop))
    stub("bleak.backends")
    stub("bleak.backends.device", BLEDevice=Dummy)
    stub("dbus_fast", BusType=types.SimpleNamespace(SYSTEM="system"))
    stub("dbus_fast.aio", MessageBus=Dummy)
    stub("dbus_fast.constants", BusType=types.SimpleNamespace(SYSTEM="system"),
         MessageType=types.SimpleNamespace(ERROR="error", METHOD_RETURN="method_return"))
    stub("dbus_fast.message", Message=Dummy)
    stub("dbus_fast.signature", Variant=Dummy)
    stub("bleak.backends.corebluetooth.CentralManagerDelegate",
         CBUUID=type("CBUUID", (), {"UUIDWithString_": staticmethod(lambda x: x)}),
         CentralManagerDelegate=Dummy)

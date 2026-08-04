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

    stub("bleak", BleakClient=Dummy, BleakScanner=Dummy,
         _logger=types.SimpleNamespace(debug=lambda *a, **k: None, info=lambda *a, **k: None, error=lambda *a, **k: None))
    stub("bleak.backends")
    stub("bleak.backends.device", BLEDevice=Dummy)
    stub("bleak.backends.bluezdbus", defs=types.SimpleNamespace(
        BLUEZ_SERVICE="", DEVICE_INTERFACE="", OBJECT_MANAGER_INTERFACE="", PROPERTIES_INTERFACE=""))
    stub("bleak.backends.bluezdbus.utils", assert_reply=lambda *a: None, unpack_variants=lambda v: v)
    stub("dbus_next", BusType=types.SimpleNamespace(SYSTEM="system"), Message=Dummy, Variant=Dummy)
    stub("dbus_next.aio", MessageBus=Dummy)
    stub("bleak.backends.corebluetooth.CentralManagerDelegate",
         CBUUID=type("CBUUID", (), {"UUIDWithString_": staticmethod(lambda x: x)}),
         CentralManagerDelegate=type("CentralManagerDelegate", (), {
             "alloc": classmethod(lambda cls: type("Obj", (), {"init": lambda self: None})())}))

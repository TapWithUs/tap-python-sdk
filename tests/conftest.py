import platform
import sys
import types


def pytest_configure(config):
    # macOS CI lacks usable CoreBluetooth; other runners use real bleak/winrt.
    if platform.system() != "Darwin":
        return

    bleak_stub = types.ModuleType("bleak")

    class Dummy:
        def __init__(self, *args, **kwargs):
            pass

    bleak_stub.BleakClient = Dummy
    bleak_stub.BleakScanner = Dummy
    bleak_stub._logger = types.SimpleNamespace(
        debug=lambda *a, **k: None,
        info=lambda *a, **k: None,
        error=lambda *a, **k: None,
    )
    sys.modules.setdefault("bleak", bleak_stub)

    core_mod = types.ModuleType("bleak.backends.corebluetooth.CentralManagerDelegate")
    core_mod.CBUUID = type("CBUUID", (), {"UUIDWithString_": staticmethod(lambda x: x)})
    core_mod.CentralManagerDelegate = type(
        "CentralManagerDelegate",
        (),
        {"alloc": classmethod(lambda cls: type("Obj", (), {"init": lambda self: None})())},
    )
    sys.modules.setdefault("bleak.backends.corebluetooth.CentralManagerDelegate", core_mod)

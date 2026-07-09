import importlib
import platform
import sys
import types
from unittest.mock import patch


def _make_bleak_stub():
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
    core_mod = types.ModuleType(
        "bleak.backends.corebluetooth.CentralManagerDelegate"
    )
    core_mod.CBUUID = type("CBUUID", (), {"UUIDWithString_": staticmethod(lambda x: x)})
    core_mod.CentralManagerDelegate = type(
        "CentralManagerDelegate",
        (),
        {"alloc": classmethod(lambda cls: type("Obj", (), {"init": lambda self: None})())},
    )
    return bleak_stub, core_mod


def _clear_tapsdk_modules():
    for name in list(sys.modules):
        if name == "tapsdk" or name.startswith("tapsdk."):
            del sys.modules[name]


def test_tapclient_defined_for_current_platform():
    platform_name = platform.system()
    bleak_stub, core_stub = _make_bleak_stub()
    module_stubs = {
        "bleak": bleak_stub,
        "bleak.backends.corebluetooth.CentralManagerDelegate": core_stub,
    }

    _clear_tapsdk_modules()
    with patch.dict(sys.modules, module_stubs):
        with patch("platform.system", return_value=platform_name):
            module = importlib.import_module("tapsdk.tap")
    assert hasattr(module, "TapClient")

import importlib
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


def _load_tap(platform_name: str):
    bleak_stub, core_stub = _make_bleak_stub()
    with patch.dict(
        sys.modules,
        {
            "bleak": bleak_stub,
            "bleak.backends.corebluetooth.CentralManagerDelegate": core_stub,
        },
    ):
        with patch("platform.system", return_value=platform_name):
            if "tapsdk.tap" in sys.modules:
                module = importlib.reload(sys.modules["tapsdk.tap"])
            else:
                module = importlib.import_module("tapsdk.tap")
    return module


def test_tapclient_defined_for_all_platforms():
    for name in ["Linux", "Windows", "Darwin"]:
        module = _load_tap(name)
        assert hasattr(module, "TapClient")

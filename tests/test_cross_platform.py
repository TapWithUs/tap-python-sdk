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


def _make_winrt_stubs():
    bluetooth = types.ModuleType("bleak_winrt.windows.devices.bluetooth")
    bluetooth.BluetoothLEDevice = type(
        "BluetoothLEDevice",
        (),
        {
            "get_device_selector_from_connection_status": staticmethod(lambda _status: ""),
            "from_bluetooth_address_async": staticmethod(lambda _address: None),
        },
    )
    bluetooth.BluetoothConnectionStatus = type(
        "BluetoothConnectionStatus",
        (),
        {"CONNECTED": 1},
    )
    bluetooth.BluetoothCacheMode = type("BluetoothCacheMode", (), {"UNCACHED": 1})

    gatt = types.ModuleType(
        "bleak_winrt.windows.devices.bluetooth.genericattributeprofile"
    )
    gatt.GattSession = type(
        "GattSession",
        (),
        {"from_device_id_async": staticmethod(lambda _device_id: None)},
    )
    gatt.GattSessionStatus = type("GattSessionStatus", (), {"ACTIVE": 1})

    enumeration = types.ModuleType("bleak_winrt.windows.devices.enumeration")
    enumeration.DeviceInformation = type(
        "DeviceInformation",
        (),
        {"find_all_async": staticmethod(lambda *_args, **_kwargs: [])},
    )
    enumeration.DeviceInformationKind = type(
        "DeviceInformationKind",
        (),
        {"ASSOCIATION_ENDPOINT": 1},
    )

    return {
        "bleak_winrt": types.ModuleType("bleak_winrt"),
        "bleak_winrt.windows": types.ModuleType("bleak_winrt.windows"),
        "bleak_winrt.windows.devices": types.ModuleType("bleak_winrt.windows.devices"),
        "bleak_winrt.windows.devices.bluetooth": bluetooth,
        "bleak_winrt.windows.devices.bluetooth.genericattributeprofile": gatt,
        "bleak_winrt.windows.devices.enumeration": enumeration,
    }


def _clear_tapsdk_modules():
    for name in list(sys.modules):
        if name == "tapsdk" or name.startswith("tapsdk."):
            del sys.modules[name]


def _winrt_stubs_needed() -> bool:
    try:
        import bleak_winrt  # noqa: F401
    except ImportError:
        return True
    return False


def test_tapclient_defined_for_current_platform():
    platform_name = platform.system()
    bleak_stub, core_stub = _make_bleak_stub()
    module_stubs = {
        "bleak": bleak_stub,
        "bleak.backends.corebluetooth.CentralManagerDelegate": core_stub,
    }
    if platform_name == "Windows" and _winrt_stubs_needed():
        module_stubs.update(_make_winrt_stubs())

    _clear_tapsdk_modules()
    try:
        with patch.dict(sys.modules, module_stubs):
            with patch("platform.system", return_value=platform_name):
                module = importlib.import_module("tapsdk.tap")
        assert hasattr(module, "TapClient")
    finally:
        _clear_tapsdk_modules()

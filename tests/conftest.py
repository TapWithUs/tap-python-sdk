import sys
import types


def _install_winrt_stubs():
    try:
        import bleak_winrt  # noqa: F401
    except ImportError:
        pass
    else:
        return

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

    for name, mod in [
        ("bleak_winrt", types.ModuleType("bleak_winrt")),
        ("bleak_winrt.windows", types.ModuleType("bleak_winrt.windows")),
        ("bleak_winrt.windows.devices", types.ModuleType("bleak_winrt.windows.devices")),
        ("bleak_winrt.windows.devices.bluetooth", bluetooth),
        ("bleak_winrt.windows.devices.bluetooth.genericattributeprofile", gatt),
        ("bleak_winrt.windows.devices.enumeration", enumeration),
    ]:
        sys.modules.setdefault(name, mod)


def pytest_configure(config):
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
    _install_winrt_stubs()

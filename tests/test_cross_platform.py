import platform


def test_tapclient_importable():
    import tapsdk.tap as tap

    assert hasattr(tap, "TapClient")


def test_platform_ble_backend_is_not_silently_disabled():
    """Guard against optional BLE backend imports failing silently.

    tapsdk.tap used to swallow ImportError for the platform-specific BLE
    backend and fall back to `None` symbols, which let the module import
    successfully while every BLE call would later crash with AttributeError.
    This asserts the backend symbols used on the running platform were
    actually imported.
    """
    import tapsdk.tap as tap

    system = platform.system()
    if system == "Darwin":
        assert tap.CBUUID is not None
        assert tap.CentralManagerDelegate is not None
    elif system == "Windows":
        assert tap.BluetoothLEDevice is not None
        assert tap.BluetoothConnectionStatus is not None
        assert tap.BluetoothCacheMode is not None
        assert tap.GattSession is not None
        assert tap.GattSessionStatus is not None
        assert tap.DeviceInformation is not None
        assert tap.DeviceInformationKind is not None

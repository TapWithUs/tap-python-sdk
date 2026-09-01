import platform


def test_tapclient_importable():
    import tapsdk._transport as transport
    import tapsdk.tap as tap

    assert hasattr(transport, "TapClient")
    assert hasattr(tap, "TapClient")
    assert tap.TapClient is transport.TapClient


def test_platform_ble_backend_is_not_silently_disabled():
    """Guard against optional BLE backend imports failing silently."""
    import tapsdk._transport as transport

    system = platform.system()
    if system == "Darwin":
        assert transport.CBUUID is not None
        assert transport.CentralManagerDelegate is not None
    elif system == "Windows":
        assert transport.BluetoothLEDevice is not None
        assert transport.BluetoothConnectionStatus is not None
        assert transport.BluetoothCacheMode is not None
        assert transport.DeviceInformation is not None
        assert transport.DeviceInformationKind is not None

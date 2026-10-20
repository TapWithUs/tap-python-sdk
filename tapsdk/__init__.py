"""Tap Strap / TapXR / TapBand Python BLE SDK.

Public exports: ``connect``, ``TapSDK``, ``TapSDK2``, input-mode classes,
``InputType``, and gesture/feature enumerations. See the ``docs/`` directory
for tutorials, how-to guides, reference, and explanation. TapBand uses the
same BLE API as TapXR and is coming soon.
"""

from tapsdk.enumerations import (AirGestures, DeviceFeatures,  # noqa: F401
                                 ImuAcclSensitivity, InputType, ModelTypes,
                                 UnifiedAirGestures, VisionSensorOpModes)
from tapsdk.inputmodes import (InputModeController, InputModeControllerText,  # noqa: F401
                               InputModeRaw, InputModeText)


async def connect(address=None, *, skip_scan: bool = False, **kwargs):
    """Attach to a Tap and return ``TapSDK`` or ``TapSDK2`` from firmware.

    Does not start notifications. Register callbacks, then ``await sdk.start()``.
    Enable input with ``hasattr(sdk, "set_input_mode")`` (Controller mode) or
    ``DeviceFeatures.MODEL_DETECTION`` plus a vision model.

    ``skip_scan`` (Windows only): if True, never falls back to a live BLE
    advertisement scan - only attempts to attach to a Tap Windows already
    reports as connected/paired (via AEP) or an explicitly given ``address``.
    Raises ``ConnectionError`` immediately if that attempt doesn't succeed,
    instead of scanning and waiting for a Tap to become available.
    """
    from tapsdk._detect import detect_protocol, ensure_gatt_services
    from tapsdk._transport import connect_tap
    from tapsdk.tap import TapSDK
    from tapsdk.tap2 import TapSDK2

    client = await connect_tap(address=address, skip_scan=skip_scan)
    await ensure_gatt_services(client)
    if detect_protocol(client) == "v2":
        return TapSDK2(client=client, **kwargs)
    return TapSDK(client=client, **kwargs)


def __getattr__(name):
    if name == "TapSDK":
        from tapsdk.tap import TapSDK

        return TapSDK
    if name == "TapSDK2":
        from tapsdk.tap2 import TapSDK2

        return TapSDK2
    if name == "DeviceInfo":
        from tapsdk.device_info import DeviceInfo

        return DeviceInfo
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

"""Tap Strap / TapXR Python BLE SDK.

Public exports: ``connect``, ``TapSDK``, ``TapSDK2``, input-mode classes,
``InputType``, and gesture/feature enumerations. See the ``docs/`` directory
for tutorials, how-to guides, reference, and explanation.
"""

from tapsdk.enumerations import (AirGestures, DeviceFeatures,  # noqa: F401
                                 ImuAcclSensitivity, InputType, ModelTypes,
                                 UnifiedAirGestures, VisionSensorOpModes)
from tapsdk.inputmodes import (InputModeController, InputModeControllerText,  # noqa: F401
                               InputModeRaw, InputModeText)


async def connect(address=None, **kwargs):
    """Attach to a Tap, detect v1/v2 protocol, return the matching SDK.

    Does not start notifications. Register callbacks, then ``await sdk.start()``.
    """
    from tapsdk._detect import detect_protocol
    from tapsdk._transport import connect_tap
    from tapsdk.tap import TapSDK
    from tapsdk.tap2 import TapSDK2

    client = await connect_tap(address=address)
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

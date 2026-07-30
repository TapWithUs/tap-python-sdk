"""Tap Strap / TapXR Python BLE SDK.

Public exports: ``TapSDK``, ``TapSDK2``, input-mode classes, ``InputType``,
and gesture/feature enumerations. See the ``docs/`` directory for tutorials,
how-to guides, reference, and explanation.
"""

from tapsdk.enumerations import (AirGestures, DeviceFeatures,  # noqa: F401
                                 ImuAcclSensitivity, InputType, ModelTypes,
                                 UnifiedAirGestures, VisionSensorOpModes)
from tapsdk.inputmodes import (InputModeController, InputModeControllerText,  # noqa: F401
                               InputModeRaw, InputModeText)


def __getattr__(name):
    if name == "TapSDK":
        from tapsdk.tap import TapSDK

        return TapSDK
    if name == "TapSDK2":
        from tapsdk.tap2 import TapSDK2

        return TapSDK2
    if name == "DeviceInfo":
        from tapsdk.tap import DeviceInfo

        return DeviceInfo
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

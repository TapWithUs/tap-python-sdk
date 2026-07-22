from tapsdk.enumerations import InputType, AirGestures  # noqa: F401
from tapsdk.inputmodes import InputModeRaw, InputModeController, InputModeText, InputModeControllerText  # noqa: F401


def __getattr__(name):
    if name == "TapSDK":
        from tapsdk.tap import TapSDK

        return TapSDK
    if name == "DeviceInfo":
        from tapsdk.tap import DeviceInfo

        return DeviceInfo
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

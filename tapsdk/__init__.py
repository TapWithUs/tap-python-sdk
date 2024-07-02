import platform
from .models.enumerations import InputType

this_platform = platform.system()

if this_platform == "Windows":
    from tapsdk.backends.dotnet.TapSDK import TapWindowsSDK as TapSDK
    from tapsdk.backends.dotnet.inputmodes import TapInputMode
elif this_platform in ["Darwin", "Linux"]:
    from tapsdk.backends.posix.TapSDK import TapPosixSDK as TapSDK
    from tapsdk.backends.posix.inputmodes import TapInputMode

else:
   raise ValueError("Value for platfrom is unknown: {}".format(this_platform))

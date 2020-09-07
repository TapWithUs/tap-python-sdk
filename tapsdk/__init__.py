import platform
from enum import Enum

this_platform = platform.system()

if this_platform == "Windows":
    from tapsdk.backends.dotnet.TapSDK import TapWindowsSDK as TapSDK
    from tapsdk.backends.dotnet.inputmodes import TapInputMode
elif this_platform == "Darwin":
    from tapsdk.backends.macos.TapSDK import TapMacSDK as TapSDK 
    from tapsdk.backends.macos.inputmodes import TapInputMode
elif this_platform == "Linux":
    from tapsdk.backends.linux.TapSDK import TapLinuxSDK as TapSDK
    from tapsdk.backends.linux.inputmodes import TapInputMode
else:
   raise ValueError("Value for platfrom is unknown: {}".format(this_platform))

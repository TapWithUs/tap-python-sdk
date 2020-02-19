import platform
from enum import Enum

this_platform = platform.system()

if this_platform == "Windows":
    from tapsdk.backends.dotnet.TapSDK import TapWindowsSDK as TapSDK
    from tapsdk.backends.dotnet.inputmodes import TapInputModes
elif this_platform == "Darwin":
    from tapsdk.backends.macos.TapSDK import TapMacSDK as TapSDK 
    from tapsdk.backends.macos.inputmodes import TapInputModes

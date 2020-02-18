import platform
from enum import Enum

this_platform = platform.system()

if this_platform == "Windows":
    from tapsdk.backends.dotnet.TapSDK import TapWindowsSDK as TapSDK
elif this_platform == "Darwin":
    from tapsdk.backends.macos.TapSDK import TapMacSDK as TapSDK 

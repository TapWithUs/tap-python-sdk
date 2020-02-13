import platform
from enum import Enum

this_platform = platform.system()

if this_platform == "Windows":
    import clr

    # sys.path.append(r"C:\Users\oded\PycharmProjects\tap-sdk")
    # clr.AddReference(r"TAPWin")
    clr.AddReference(r"C:\Users\oded\tap-standalonewin-sdk\tap-standalonewin-sdk\TAPWinApp\bin\Debug\TAPWin")
    from TapSDK.backends.dotnet.TapWindowsSDK import TapWindowsSDK as TapSDK

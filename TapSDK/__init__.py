import platform

this_platform = platform.system()

if this_platform == "Windows":
    import clr

    # sys.path.append(r"C:\Users\oded\PycharmProjects\tap-sdk")
    clr.AddReference(r"TAPWin")
    from tapsdk.backends.dotnet.TapWindowsSDK import TapWindowsSDK as TapSDK

elif this_platform == "Darwin":
    from tapsdk.backends.macos.TapMacSDK import TapMacSDK as TapSDK 
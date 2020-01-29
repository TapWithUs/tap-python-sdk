import platform

this_platform = platform.system()

if this_platform == "Windows":
    import clr

    # sys.path.append(r"C:\Users\oded\PycharmProjects\tap-sdk")
    clr.AddReference(r"TAPWin")
    from TapSDK.backends.dotnet.TapWindowsSDK import TapWindowsSDK as TapSDK

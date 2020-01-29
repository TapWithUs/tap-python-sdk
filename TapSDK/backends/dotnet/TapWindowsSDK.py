import clr
from TapSDK.TapSDK import TapSDK

clr.AddReference(r"TAPWin")
from TAPWin import TAPManager
from TAPWin import TAPManagerLog
from TAPWin import TAPInputMode


class TapWindowsSDK(TapSDK):
    def __init__(self):
        self.mode = 1
        TAPManagerLog.Instance.OnLineLogged += print

    def OnTapped(self, identifier, tapcode):
        print(identifier + " tapped " + str(tapcode))

    def OnTapConnected(self, identifier, name, fw):
        print(identifier + " Tap: " + str(name), " FW Version: ", fw)

    def OnTapDisconnected(self, identifier):
        print(identifier + " Tap: " + identifier + " disconnected")

    def OnMoused(self, identifier, vx, vy, isMouse):
        print(identifier + " mouse movement: " + vx + vy)

    def register_tap_events(self):
        TAPManager.Instance.OnTapped += self.OnTapped

    def register_mouse_events(self):
        TAPManager.Instance.OnMoused += self.OnMoused

    def register_connection_events(self):
        TAPManager.Instance.OnTapConnected += self.OnTapConnected

    def register_disconnection_events(self):
        TAPManager.Instance.OnTapDisconnected += self.OnTapDisconnected

    def set_input_mode(self, mode):
        self.mode = mode

    def run(self):
        TAPManager.Instance.Start()


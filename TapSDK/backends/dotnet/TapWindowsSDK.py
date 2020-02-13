import clr
from TapSDK.TapSDK import TapSDK

clr.AddReference(r"TAPWin")
from TAPWin import TAPManager
from TAPWin import TAPManagerLog
from TAPWin import TAPInputMode
from TAPWin import RawSensorSensitivity
from TAPWin import TAPAirGesture
from TAPWin import RawSensorData


class TapWindowsSDK(TapSDK):
    def __init__(self):
        TapSDK.__init__(self)
        self.airGestureState = False
        self.mode = None
        self.tapConnected = False
        TAPManagerLog.Instance.OnLineLogged += print

    @staticmethod
    def OnTapped(identifier, tapcode):
        print(identifier + " tapped " + str(tapcode))

    def OnTapConnected(self, identifier, name, fw):
        self.tapConnected = True
        print(identifier + " Tap: " + str(name), " FW Version: ", fw)

    def OnTapDisconnected(self, identifier):
        self.tapConnected = False
        self.mode = None
        print(identifier + " Tap: " + identifier + " disconnected")

    @staticmethod
    def OnMoused(identifier: str, vx: int, vy: int, isMouse: bool):
        print("dx: " + str(vx) + " dy: " + str(vy) + " In mouse:" + str(isMouse))

    @staticmethod
    def OnRawSensorDataReceived(identifier, raw_sensor_data):
        print(raw_sensor_data)

    @staticmethod
    def OnAirGestured(identifier: str, airGesture: bool):
        print(identifier + " air gesture: " + str(airGesture))

    @staticmethod
    def OnChangedAirGestureState(identifier: str, air_gesture_state: bool):
        print(str(identifier) + "air gesture state: " + str(air_gesture_state))

    def register_tap_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapped += listener
        else:
            TAPManager.Instance.OnTapped += self.OnTapped

    def register_mouse_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnMoused += listener
        else:
            TAPManager.Instance.OnMoused += self.OnMoused

    def register_connection_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapConnected += listener
        else:
            TAPManager.Instance.OnTapConnected += self.OnTapConnected

    def register_disconnection_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapDisconnected += listener
        else:
            TAPManager.Instance.OnTapDisconnected += self.OnTapDisconnected

    def register_raw_sensor_data_stream(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnRawSensorDataReceieved += listener
        else:
            TAPManager.Instance.OnRawSensorDataReceieved += self.OnRawSensorDataReceived

    def register_air_gesture_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnAirGestured += listener
        else:
            TAPManager.Instance.OnAirGestured += self.OnAirGestured

    def register_air_gesture_state_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnChangedAirGestureState += listener
        else:
            TAPManager.Instance.OnChangedAirGestureState += self.OnChangedAirGestureState

    def set_input_mode(self, mode, tap_identifier=""):
        self.mode = mode
        print("input mode: " + str(mode))
        if mode == self.TapMode.Text.value:
            TAPManager.Instance.SetTapInputMode(TAPInputMode.Text(), "")
        if mode == self.TapMode.Controller.value:
            TAPManager.Instance.SetTapInputMode(TAPInputMode.Controller(), "")
        if mode == self.TapMode.ControllerWithHIDMouse:
            TAPManager.Instance.SetTapInputMode(TAPInputMode.ControllerWithMouseHID(), "")

    def set_raw_sensors_mode(self, device_accel_sens, imu_gyro_sens, imu_accel_sens):
        TAPManager.Instance.SetTapInputMode(TAPInputMode.RawSensor(RawSensorSensitivity(device_accel_sens, imu_gyro_sens, imu_accel_sens)))

    def run(self):
        TAPManager.Instance.setDefaultInputMode(TAPInputMode.Controller(), True)
        TAPManager.Instance.Start()



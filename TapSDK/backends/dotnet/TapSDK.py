import clr
from tapsdk.TapSDK import TapSDKBase
from System import Array

clr.AddReference(r"TAPWin")
from TAPWin import TAPManager
from TAPWin import TAPManagerLog
from TAPWin import TAPInputMode
from TAPWin import RawSensorSensitivity
from TAPWin import TAPAirGesture
from TAPWin import RawSensorData


class TapWindowsSDK(TapSDKBase):
    def __init__(self):
        TapSDK.__init__(self)
        TAPManagerLog.Instance.OnLineLogged += print

    @staticmethod
    def OnTapped(identifier, tapcode):
        print(identifier + " tapped " + str(tapcode))

    def OnTapConnected(self, identifier, name, fw):
        print(identifier + " Tap: " + str(name), " FW Version: ", fw)

    def OnTapDisconnected(self, identifier):
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

    def register_raw_data_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnRawSensorDataReceieved += listener
        else:
            TAPManager.Instance.OnRawSensorDataReceieved += self.OnRawSensorDataReceived

    def register_air_gesture_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnAirGestured += listener
        else:
            TAPManager.Instance.OnAirGestured += self.OnAirGestured

    def register_air_gesture_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnChangedAirGestureState += listener
        else:
            TAPManager.Instance.OnChangedAirGestureState += self.OnChangedAirGestureState

    def get_input_mode_object(self, mode_num):
        if mode_num == self.TapMode.Text.value:
            return TAPInputMode.Text()
        if mode_num == self.TapMode.Controller.value:
            return TAPInputMode.Controller()
        if mode_num == self.TapMode.ControllerWithHIDMouse:
            return TAPInputMode.ControllerWithMouseHID()

        print("Unhandled value. Defaulting to Controller mode object")
        return TAPInputMode.Controller()

    def set_input_mode(self, mode, tap_identifier=""):
        print("input mode: " + TapSDK.TapMode(mode).name)
        input_mode_obj = self.get_input_mode_object(mode)
        TAPManager.Instance.SetTapInputMode(input_mode_obj, tap_identifier)

    def set_default_input_mode(self, mode, identifier=""):
        set_all = False
        if identifier == "":
            set_all = True
        mode_obj = self.get_input_mode_object(mode)
        TAPManager.Instance.setDefaultInputMode(mode_obj, set_all)

    def set_raw_sensors_mode(self, device_accel_sens=0, imu_gyro_sens=0, imu_accel_sens=0, identifier=""):
        TAPManager.Instance.SetTapInputMode(TAPInputMode.RawSensor(RawSensorSensitivity(device_accel_sens, imu_gyro_sens, imu_accel_sens)), identifier)

    def send_vibration_sequence(self, sequence, identifier):
        vibrations_array = Array[int](sequence)
        TAPManager.Instance.Vibrate(vibrations_array, identifier)

    def run(self):
        # TAPManager.Instance.setDefaultInputMode(TAPInputMode.Controller(), True)
        self.set_default_input_mode(TapSDK.TapMode.Controller.value)
        TAPManager.Instance.Start()




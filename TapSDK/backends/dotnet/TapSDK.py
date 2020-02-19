import clr
from tapsdk.TapSDK import TapSDKBase
from .inputmodes import TapInputModes
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
        super().__init__(self)
        TAPManagerLog.Instance.OnLineLogged += print

    def register_tap_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapped += listener

    def register_mouse_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnMoused += listener

    def register_connection_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapConnected += listener

    def register_disconnection_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapDisconnected += listener

    def register_raw_data_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnRawSensorDataReceieved += listener

    def register_air_gesture_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnAirGestured += listener

    def register_air_gesture_state_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnChangedAirGestureState += listener

    def set_input_mode(self, mode:TapInputModes, tap_identifier=""):
        print("input mode: " + mode.get_name())
        TAPManager.Instance.SetTapInputMode(mode.get_object(), tap_identifier)

    def set_default_input_mode(self, mode, identifier=""):
        set_all = False
        if identifier == "":
            set_all = True
        mode_obj = TapInputModes(mode).get_object()
        TAPManager.Instance.setDefaultInputMode(mode_obj, set_all)

    def set_raw_sensors_mode(self, device_accel_sens=0, imu_gyro_sens=0, imu_accel_sens=0, identifier=""):
        TAPManager.Instance.SetTapInputMode(TAPInputMode.RawSensor(RawSensorSensitivity(device_accel_sens, imu_gyro_sens, imu_accel_sens)), identifier)

    def send_vibration_sequence(self, sequence, identifier):
        vibrations_array = Array[int](sequence)
        TAPManager.Instance.Vibrate(vibrations_array, identifier)

    def run(self):
        self.set_default_input_mode("controller")
        TAPManager.Instance.Start()




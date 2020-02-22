import logging
import clr
import System

clr.AddReference(r"tapsdk/backends/dotnet/TAPWin")
from TAPWin import TAPInputMode
from TAPWin import RawSensorSensitivity


class TapInputMode:
    def __init__(self, mode, sensitivity: list=[0, 0, 0]):
        self._modes = {
                "text" : {"name": "Text Mode", "code": TAPInputMode.Text()},
                "controller" : {"name": "Controller Mode", "code": TAPInputMode.Controller()},
                "controller_text" : {"name": "Controller and Text Mode", "code": TAPInputMode.ControllerWithMouseHID()},
                "raw" : {"name": "Raw sensors Mode", "code":  TAPInputMode.RawSensor(RawSensorSensitivity(System.Byte(0), System.Byte(0), System.Byte(0)))}
                }
        self.sensitivity = sensitivity
        if mode in self._modes.keys():
            self.mode = mode
            if mode == "raw":
                self._register_sensitivity(sensitivity)
        else:
            logging.warning("Invalid mode \"%s\". Set to \"text\"" % mode)
            self.mode = "text"

    def _register_sensitivity(self, sensitivity):
        if isinstance(sensitivity, list) and len(sensitivity) == 3:
            sensitivity[0] = max(0, min(4,sensitivity[0])) # fingers accelerometers
            sensitivity[1] = max(0, min(5,sensitivity[1])) # imu gyro
            sensitivity[2] = max(0, min(4,sensitivity[2])) # imu accelerometer
            self.sensitivity = sensitivity
            self._modes["raw"]["code"] = TAPInputMode.RawSensor(RawSensorSensitivity(System.Byte(sensitivity[0]), System.Byte(sensitivity[1]), System.Byte(sensitivity[2])))

    def get_object(self):
        return self._modes[self.mode]["code"]

    def get_name(self):
        return self._modes[self.mode]["name"]

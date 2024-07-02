import logging
from ...models.enumerations import InputType


class TapInputMode:
    def __init__(self, mode, sensitivity=[0, 0, 0]):
        self._modes = {
                "text": {"name": "Text Mode", "code": bytearray([0x3, 0xc, 0x0, 0x0])},
                "controller": {"name": "Controller Mode", "code": bytearray([0x3, 0xc, 0x0, 0x1])},
                "controller_text": {"name": "Controller and Text Mode", "code": bytearray([0x3, 0xc, 0x0, 0x3])},
                "raw": {"name": "Raw sensors Mode", "code": bytearray([0x3, 0xc, 0x0, 0xa])}
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
            sensitivity[0] = max(0, min(4, sensitivity[0]))  # fingers accelerometers
            sensitivity[1] = max(0, min(5, sensitivity[1]))  # imu gyro
            sensitivity[2] = max(0, min(4, sensitivity[2]))  # imu accelerometer
            self.sensitivity = sensitivity
            self._modes["raw"]["code"] = self._modes["raw"]["code"][:4] + bytearray(sensitivity)

    def get_command(self):
        return self._modes[self.mode]["code"]

    def get_name(self):
        return self._modes[self.mode]["name"]


def input_type_command(input_type):
    assert isinstance(input_type, InputType), "input_type must be of type InputType"
    return bytearray([0x3, 0xd, 0x0, input_type.value])

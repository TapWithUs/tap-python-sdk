from enum import Enum
import logging
from .enumerations import InputType, FingerAcclSensitivity, ImuGyroSensitivity, ImuAcclSensitivity

logger = logging.getLogger(__name__)


class RawSensorsSensitivity():
    finger_acc_scales = [None, 3.91, 7.81, 15.62, 31.25]  # mg/lsb
    imu_gyro_scales = [None, 4.375, 8.75, 17.5, 35, 70]  # mdps/lsb
    imu_acc_scales = [None, 0.061, 0.122, 0.244, 0.488]  # mg/lsb

    def __init__(self, finger_accl_sens, imu_gyro_sens, imu_accl_sens):
        assert all(isinstance(s, Enum) for s in [finger_accl_sens, imu_gyro_sens, imu_accl_sens]), \
            "sensitivity values must be of type Enum"
        self.sens_values = [finger_accl_sens.value, imu_gyro_sens.value, imu_accl_sens.value]
        self.scale_factors = [      # in g, dps, g
            self.finger_acc_scales[self.sens_values[0]]/1000.0,
            self.imu_gyro_scales[self.sens_values[1]]/1000.0,
            self.imu_acc_scales[self.sens_values[2]]/1000.0
        ]

    def tolist(self):
        return self.sens_values

    def get_scale_factors(self):
        return self.scale_factors


class InputMode:
    COMMAND_PREFIX = bytearray([0x3, 0xc, 0x0])

    def get_command(self):
        return self.COMMAND_PREFIX + self.code

    def __repr__(self):
        return self.name


class InputModeController(InputMode):
    def __init__(self):
        self.name = "Controller Mode"
        self.code = bytearray([0x1])


class InputModeText(InputMode):
    def __init__(self):
        self.name = "Text Mode"
        self.code = bytearray([0x0])


class InputModeControllerText(InputMode):
    def __init__(self):
        self.name = "Controller and Text Mode"
        self.code = bytearray([0x3])


class InputModeRaw(InputMode):
    def __init__(self, scaled=False, finger_accl_sens=None,
                 imu_gyro_sens=None, imu_accl_sens=None):
        self.name = "Raw sensors Mode"
        self.scaled = scaled
        self.sensitivity = RawSensorsSensitivity(finger_accl_sens or FingerAcclSensitivity.G2,
                                                 imu_gyro_sens or ImuGyroSensitivity.DPS125,
                                                 imu_accl_sens or ImuAcclSensitivity.G2)
        self.code = bytearray([0xa]) + bytearray(self.sensitivity.tolist())


def input_type_command(input_type):
    assert isinstance(input_type, InputType), "input_type must be of type InputType"
    return bytearray([0x3, 0xd, 0x0, input_type.value])

from tapsdk.enumerations import InputType, FingerAcclSensitivity, ImuGyroSensitivity, ImuAcclSensitivity
from tapsdk.inputmodes import (InputModeController, InputModeControllerText,
                               InputModeRaw, InputModeText, input_type_command)


def test_input_mode_basic():
    assert InputModeText().get_command() == bytearray([0x3, 0xc, 0x0, 0x0])
    assert InputModeController().get_command() == bytearray([0x3, 0xc, 0x0, 0x1])
    assert InputModeControllerText().get_command() == bytearray([0x3, 0xc, 0x0, 0x3])


def test_input_mode_raw_with_sensitivity():
    mode = InputModeRaw(
        finger_accl_sens=FingerAcclSensitivity.G2,
        imu_gyro_sens=ImuGyroSensitivity.DPS250,
        imu_accl_sens=ImuAcclSensitivity.G8
    )
    assert mode.get_command() == bytearray([0x3, 0xc, 0x0, 0xa, 1, 2, 3])


def test_input_mode_raw_with_partial_sensitivity():
    mode = InputModeRaw(finger_accl_sens=FingerAcclSensitivity.G16)
    assert mode.get_command() == bytearray([0x3, 0xc, 0x0, 0xa, 4, 1, 1])


def test_input_mode_raw_scaled():
    mode = InputModeRaw(scaled=True)
    assert mode.scaled is True
    assert mode.get_command() == bytearray([0x3, 0xc, 0x0, 0xa, 1, 1, 1])


def test_input_type_command():
    assert input_type_command(InputType.MOUSE) == bytearray([0x3, 0xd, 0x0, InputType.MOUSE.value])

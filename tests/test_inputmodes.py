from tapsdk.inputmodes import TapInputMode, input_type_command
from tapsdk.enumerations import InputType


def test_input_mode_basic():
    assert TapInputMode("text").get_command() == bytearray([0x3, 0xc, 0x0, 0x0])
    assert TapInputMode("controller").get_command() == bytearray([0x3, 0xc, 0x0, 0x1])
    assert TapInputMode("controller_text").get_command() == bytearray([0x3, 0xc, 0x0, 0x3])


def test_input_mode_raw_with_sensitivity():
    mode = TapInputMode("raw", sensitivity=[1, 2, 3])
    assert mode.get_command() == bytearray([0x3, 0xc, 0x0, 0xa, 1, 2, 3])


def test_input_type_command():
    assert input_type_command(InputType.MOUSE) == bytearray([0x3, 0xd, 0x0, InputType.MOUSE.value])

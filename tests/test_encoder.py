from tapsdk import encoder


def test_encode_set_haptic_pattern_ui_header_and_zero_padding():
    msg = encoder.encode_set_haptic_pattern([50, 20, 50, 20])
    # external_comm header + 2-byte UI header + 18 duration slots
    assert len(msg) == 4 + 2 + encoder.HAPTIC_UI_DURATION_SLOT_COUNT
    assert msg[0] == encoder.OutCommandType.PERIPHERAL_COMMAND
    assert msg[1] == encoder.OutSubCommandType1.PHERIPHERAL_TYPE_HAPTIC
    assert msg[2] == encoder.OutSubCommandType2.SET_HAPTIC_PATTERN
    assert msg[4] == encoder.HAPTIC_UI_PERIPHERAL_TYPE
    assert msg[5] == encoder.HAPTIC_UI_ACTION_CONSTANT_POWER_SEQUENCE
    assert list(msg[6:10]) == [50, 20, 50, 20]
    assert all(b == 0 for b in msg[10:])

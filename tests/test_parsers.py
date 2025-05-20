import tapsdk.parsers as parsers


def test_mouse_data_msg():
    data = bytearray([0, 1, 0, 2, 0, 0, 0, 0, 0, 1])
    assert parsers.mouse_data_msg(data) == (1, 2, True)


def test_tap_data_msg():
    data = bytearray([5])
    assert parsers.tap_data_msg(data) == [5]


def test_raw_data_msg():
    ts = 42
    payload = [1, 2, 3, 4, 5, 6]
    msg = bytearray()
    msg += ts.to_bytes(4, "little")
    for v in payload:
        msg += v.to_bytes(2, "little", signed=True)
    msg += bytearray([0, 0, 0, 0])
    assert parsers.raw_data_msg(msg) == [{"type": "imu", "ts": ts, "payload": payload}]

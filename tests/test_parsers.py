import platform

import tapsdk.parsers as parsers


def test_mouse_data_msg():
    data = bytearray([0, 1, 0, 2, 0, 0, 0, 0, 0, 1])
    assert parsers.mouse_data_msg(data) == (1, 2, True)


def test_tap_data_msg():
    data = bytearray([5])
    assert parsers.tap_data_msg(data) == [5]


def test_raw_data_msg():
    # 1. packet with one imu message
    # IMU message: type=0, timestamp=123, 6 samples (12 bytes)
    ts = 123
    imu_ts = ts  # type bit is 0, so ts stays 123
    imu_bytes = imu_ts.to_bytes(4, 'little', signed=False)
    imu_payload = b''
    imu_samples = [100, -100, 200, -200, 300, -300]
    for v in imu_samples:
        imu_payload += v.to_bytes(2, 'little', signed=True)
    imu_packet = bytearray(imu_bytes + imu_payload)
    result = parsers.raw_data_msg(imu_packet)
    assert result == [{
        'type': 'imu',
        'ts': 123,
        'payload': imu_samples
    }]

    # 2. packet with one accl message
    # Accl message: type=1, timestamp=456, 15 samples (30 bytes)
    accl_ts = (1 << 31) + 456  # set MSB for accl
    accl_bytes = accl_ts.to_bytes(4, 'little', signed=False)
    accl_samples = list(range(1, 16))
    accl_payload = b''
    for v in accl_samples:
        accl_payload += v.to_bytes(2, 'little', signed=True)
    accl_packet = bytearray(accl_bytes + accl_payload)
    result = parsers.raw_data_msg(accl_packet)
    assert result == [{
        'type': 'accl',
        'ts': 456,
        'payload': accl_samples
    }]

    # 3. packet with imu message and accl message
    # imu first, then accl
    combo_packet = bytearray(imu_bytes + imu_payload + accl_bytes + accl_payload)
    result = parsers.raw_data_msg(combo_packet)
    assert result == [
        {'type': 'imu', 'ts': 123, 'payload': imu_samples},
        {'type': 'accl', 'ts': 456, 'payload': accl_samples}
    ]


def test_raw_data_imu_msg_scaled():
    g_scale = 17.5
    a_scale = 0.122
    ts = 123
    imu_ts = ts
    imu_bytes = imu_ts.to_bytes(4, 'little', signed=False)
    imu_samples = [100, -100, 200, -200, 300, -300]
    payload = b''
    for v in imu_samples:
        payload += v.to_bytes(2, 'little', signed=True)
    packet = bytearray(imu_bytes + payload)
    result = parsers.raw_data_msg(packet, scale_factors=[0, g_scale, a_scale])
    expected = [imu_samples[i] * g_scale if i < 3 else imu_samples[i] * a_scale
                for i in range(6)]
    assert result == [{
        'type': 'imu',
        'ts': 123,
        'payload': expected
    }]


def test_raw_data_accl_msg_scaled():
    a_scale = 0.061
    ts = (1 << 31) + 456  # set MSB for accl
    accl_bytes = ts.to_bytes(4, 'little', signed=False)
    accl_samples = list(range(1, 16))
    payload = b''
    for v in accl_samples:
        payload += v.to_bytes(2, 'little', signed=True)
    packet = bytearray(accl_bytes + payload)
    result = parsers.raw_data_msg(packet, scale_factors=[a_scale, 0, 0])
    expected = [v * a_scale for v in accl_samples]
    assert result == [{
        'type': 'accl',
        'ts': 456,
        'payload': expected
    }]


def test_tapclient_defined_for_current_platform():
    import tapsdk.tap as tap

    assert hasattr(tap, "TapClient")
    assert platform.system() in {"Linux", "Windows", "Darwin"}

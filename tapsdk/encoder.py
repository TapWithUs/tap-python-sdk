CMD_BYTE_INDEX = 0
SUBCMD1_BYTE_INDEX = 1
SUBCMD2_BYTE_INDEX = 2
SUBCMD3_BYTE_INDEX = 3
PAYLOAD_START_INDEX = 4
METADATA_SIZE_BYTES = PAYLOAD_START_INDEX

PAYLOAD_FEATURE_NUMBER_INDEX = 0
PAYLOAD_FEATURE_VALUE_INDEX = 1


class OutCommandType:
    FEATURE_COMMAND = 0
    PERIPHERAL_COMMAND = 1
    KEEPALIVE_COMMAND = 2
    STANDBY_STATE_COMMAND = 3


class OutSubCommandType1:
    PERIPHERAL_TYPE_VISION_SENSOR = 0
    PERIPHERAL_TYPE_IMU = 1
    PHERIPHERAL_TYPE_HAPTIC = 2
    STANDBY_STATE_GET = 3
    STANDBY_STATE_SET = 4
    SET_FEATURE = 0
    GET_FEATURE = 1


class OutSubCommandType2:
    SET_VISUAL_SENSOR_OP_MODE = 0
    SET_VISUAL_SENSOR_MODEL = 1
    SET_IMU_SENSITIVITY = 2
    SET_HAPTIC_PATTERN = 3
    GET_VISUAL_SENSOR_OP_MODE = 10
    GET_VISUAL_SENSOR_MODEL = 11
    GET_IMU_SENSITIVITY = 12


class OutSubCommandType3:
    NONE = 0


# UI-command body embedded in external_comm SET haptic payload (tap_ui_commands_packet.h)
HAPTIC_UI_PERIPHERAL_TYPE = 0
HAPTIC_UI_ACTION_CONSTANT_POWER_SEQUENCE = 2
HAPTIC_UI_DURATION_SLOT_COUNT = 18


def encode_msg(cmd, subcmd1, subcmd2, subcmd3, payload):
    msg = bytearray(METADATA_SIZE_BYTES + len(payload))
    msg[CMD_BYTE_INDEX] = cmd
    msg[SUBCMD1_BYTE_INDEX] = subcmd1
    msg[SUBCMD2_BYTE_INDEX] = subcmd2
    msg[SUBCMD3_BYTE_INDEX] = subcmd3
    msg[PAYLOAD_START_INDEX:] = payload
    return msg


def encode_set_feature(feature_number: int, feature_value: int):
    payload = bytearray(2)
    payload[PAYLOAD_FEATURE_NUMBER_INDEX] = feature_number
    payload[PAYLOAD_FEATURE_VALUE_INDEX] = feature_value
    return encode_msg(
        OutCommandType.FEATURE_COMMAND,
        OutSubCommandType1.SET_FEATURE,
        0,
        0,
        payload,
    )


def encode_get_feature(feature_number: int):
    payload = bytearray(1)
    payload[0] = feature_number
    return encode_msg(
        OutCommandType.FEATURE_COMMAND,
        OutSubCommandType1.GET_FEATURE,
        0,
        0,
        payload,
    )


def encode_set_vision_sensor_op_mode(mode: int):
    payload = bytearray(1)
    payload[0] = mode
    return encode_msg(
        OutCommandType.PERIPHERAL_COMMAND,
        OutSubCommandType1.PERIPHERAL_TYPE_VISION_SENSOR,
        OutSubCommandType2.SET_VISUAL_SENSOR_OP_MODE,
        0,
        payload,
    )


def encode_set_vision_sensor_model(model: int):
    payload = bytearray(1)
    payload[0] = model
    return encode_msg(
        OutCommandType.PERIPHERAL_COMMAND,
        OutSubCommandType1.PERIPHERAL_TYPE_VISION_SENSOR,
        OutSubCommandType2.SET_VISUAL_SENSOR_MODEL,
        0,
        payload,
    )


def encode_set_imu_sensitivity(xl_sensitivity: int, gyro_sensitivity: int):
    payload = bytearray(2)
    payload[0] = gyro_sensitivity
    payload[1] = xl_sensitivity
    return encode_msg(
        OutCommandType.PERIPHERAL_COMMAND,
        OutSubCommandType1.PERIPHERAL_TYPE_IMU,
        OutSubCommandType2.SET_IMU_SENSITIVITY,
        0,
        payload,
    )


def encode_set_haptic_pattern(scaled_durations):
    """Build SET haptic message. Durations are in 10 ms units (host ms // 10)."""
    durations = bytearray(scaled_durations[:HAPTIC_UI_DURATION_SLOT_COUNT])
    if len(durations) < HAPTIC_UI_DURATION_SLOT_COUNT:
        durations.extend([0] * (HAPTIC_UI_DURATION_SLOT_COUNT - len(durations)))
    payload = bytearray(
        [HAPTIC_UI_PERIPHERAL_TYPE, HAPTIC_UI_ACTION_CONSTANT_POWER_SEQUENCE],
    ) + durations
    return encode_msg(
        OutCommandType.PERIPHERAL_COMMAND,
        OutSubCommandType1.PHERIPHERAL_TYPE_HAPTIC,
        OutSubCommandType2.SET_HAPTIC_PATTERN,
        0,
        payload,
    )


def encode_keepalive_message():
    return encode_msg(OutCommandType.KEEPALIVE_COMMAND, 0, 0, 0, bytearray())


def encode_get_vision_sensor_op_mode():
    return encode_msg(
        OutCommandType.PERIPHERAL_COMMAND,
        OutSubCommandType1.PERIPHERAL_TYPE_VISION_SENSOR,
        OutSubCommandType2.GET_VISUAL_SENSOR_OP_MODE,
        0,
        bytearray(),
    )


def encode_get_vision_sensor_model():
    return encode_msg(
        OutCommandType.PERIPHERAL_COMMAND,
        OutSubCommandType1.PERIPHERAL_TYPE_VISION_SENSOR,
        OutSubCommandType2.GET_VISUAL_SENSOR_MODEL,
        0,
        bytearray(),
    )


def encode_get_imu_sensitivity():
    return encode_msg(
        OutCommandType.PERIPHERAL_COMMAND,
        OutSubCommandType1.PERIPHERAL_TYPE_IMU,
        OutSubCommandType2.GET_IMU_SENSITIVITY,
        0,
        bytearray(),
    )


def encode_standby_state_get():
    return encode_msg(
        OutCommandType.STANDBY_STATE_COMMAND,
        OutSubCommandType1.STANDBY_STATE_GET,
        0,
        0,
        bytearray(),
    )


def encode_standby_state_set(standby: bool):
    payload = bytearray(1)
    payload[0] = 1 if standby else 0
    return encode_msg(
        OutCommandType.STANDBY_STATE_COMMAND,
        OutSubCommandType1.STANDBY_STATE_SET,
        0,
        0,
        payload,
    )

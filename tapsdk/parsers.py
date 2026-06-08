def tapcode_to_fingers(tapcode: int):
    return '{0:05b}'.format(1)[::-1]


def mouse_data_msg(data: bytearray, parse_euler_angles=False):
    vx = int.from_bytes(data[1:3], "little", signed=True)
    vy = int.from_bytes(data[3:5], "little", signed=True)
    prox = data[9] == 1
    if not parse_euler_angles:
        return vx, vy, prox
    euler_angles = [
        int.from_bytes(data[i:i + 2], "little", signed=True)
        for i in range(10, 16, 2)
    ]
    return vx, vy, prox, euler_angles


def air_gesture_data_msg(data: bytearray):
    return [data[0]]


def tap_data_msg(data: bytearray):
    return [data[0]]


def raw_data_msg(data: bytearray, scale_factors=None):
    '''
    Parses raw data messages into structured data with optional scaling.
    Raw data is packed into messages with the following structure:
         [msg_type (1 bit)][timestamp (31 bit)][payload (12 - 30 bytes)]
             * msg type     - '0' for imu message
                        - '1' for accelerometers message
            * timestamp - unsigned int, given in milliseconds
            * payload     - for imu message is 12 bytes
                          composed by a series of 6 uint16 numbers
                          representing [g_x, g_y, g_z, xl_x, xl_y, xl_z]
                        - for accelerometers message is 30 bytes
                          composed by a series of 15 uint16 numbers
                          representing [xl_x_thumb , xl_y_thumb,  xl_z_thumb,
                                          xl_x_finger, xl_y_finger, xl_z_finger,
                                        ...]

    '''
    L = len(data)
    ptr = 0
    messages = []
    while ptr <= L:
        # decode timestamp and message type
        ts = int.from_bytes(data[ptr:ptr+4], "little", signed=False)
        if ts == 0:
            break
        ptr += 4

        # resolve message type
        if ts > raw_data_msg.msg_type_value:
            msg = "accl"
            ts -= raw_data_msg.msg_type_value
            num_of_samples = 15
        else:
            msg = "imu"
            num_of_samples = 6

        # parse payload
        payload = []
        for i in range(num_of_samples):
            val = int.from_bytes(data[ptr:ptr+2], "little", signed=True)
            ptr += 2
            payload.append(val)

        if scale_factors:
            if msg == "accl":
                payload = [v * scale_factors[0] for v in payload]
            elif msg == "imu":
                payload = [payload[j] * scale_factors[1] if j < 3 else payload[j] * scale_factors[2]
                           for j in range(num_of_samples)]
        messages.append({"type": msg, "ts": ts, "payload": payload})
    return messages


raw_data_msg.msg_type_value = 2**31


CMD_BYTE_INDEX = 0
SUBCMD1_BYTE_INDEX = 1
SUBCMD2_BYTE_INDEX = 2
SUBCMD3_BYTE_INDEX = 3
PAYLOAD_START_INDEX = 4


class IncCommandType:
    IMU_DATA = 0
    MODEL_DETECTION = 1
    STANDBY_STATE = 2


class IncSubCommandType1:
    IMU_MOTION_DATA = 0
    IMU_RAW_DATA = 1
    TAP_GESTURE = 2
    AIR_GESTURE = 3


def tap_inc_msg(data: bytearray, scale_factors=None):
    cmd_type = data[CMD_BYTE_INDEX]
    if cmd_type == IncCommandType.IMU_DATA:
        sub_cmd_type = data[SUBCMD1_BYTE_INDEX]
        if sub_cmd_type == IncSubCommandType1.IMU_MOTION_DATA:
            return {
                "type": "imu_motion",
                "data": mouse_data_msg(data[PAYLOAD_START_INDEX:], parse_euler_angles=True),
            }
        if sub_cmd_type == IncSubCommandType1.IMU_RAW_DATA:
            return {
                "type": "imu_raw",
                "data": raw_data_msg(data[PAYLOAD_START_INDEX:], scale_factors),
            }
    elif cmd_type == IncCommandType.MODEL_DETECTION:
        sub_cmd_type = data[SUBCMD1_BYTE_INDEX]
        if sub_cmd_type == IncSubCommandType1.TAP_GESTURE:
            return {
                "type": "tap_gesture",
                "data": tap_data_msg(data[PAYLOAD_START_INDEX:]),
            }
        if sub_cmd_type == IncSubCommandType1.AIR_GESTURE:
            return {
                "type": "air_gesture",
                "data": air_gesture_data_msg(data[PAYLOAD_START_INDEX:]),
            }
    elif cmd_type == IncCommandType.STANDBY_STATE:
        return {
            "type": "standby_state",
            "data": data[PAYLOAD_START_INDEX] == 1,
        }
    return None

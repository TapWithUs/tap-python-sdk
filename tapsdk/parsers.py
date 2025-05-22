def tapcode_to_fingers(tapcode: int):
    return '{0:05b}'.format(1)[::-1]


def mouse_data_msg(data: bytearray):
    vx = int.from_bytes(data[1:3], "little", signed=True)
    vy = int.from_bytes(data[3:5], "little", signed=True)
    prox = data[9] == 1
    return vx, vy, prox


def air_gesture_data_msg(data: bytearray):
    return [data[0]]


def tap_data_msg(data: bytearray):
    return [data[0]]


def raw_data_msg(data: bytearray, scaled: bool = False, sensitivity=None):
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
    if sensitivity is None:
        sensitivity = [0, 0, 0]

    finger_acc_scales = [31.25, 3.91, 7.81, 15.62, 31.25]
    gyro_scales = [17.5, 4.375, 8.75, 17.5, 35, 70]
    imu_acc_scales = [0.122, 0.061, 0.122, 0.244, 0.488]

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

        if scaled:
            if msg == "imu":
                g_scale = gyro_scales[sensitivity[1]] / 1000.0
                xl_scale = imu_acc_scales[sensitivity[2]] / 1000.0
                payload = [payload[j] * g_scale if j < 3 else payload[j] * xl_scale
                           for j in range(num_of_samples)]
            else:  # accl message
                acc_scale = finger_acc_scales[sensitivity[0]] / 1000.0
                payload = [v * acc_scale for v in payload]

        messages.append({"type": msg, "ts": ts, "payload": payload})
    return messages


raw_data_msg.msg_type_value = 2**31

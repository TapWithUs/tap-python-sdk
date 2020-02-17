from TapSDK import TapSDK

tap_instance = TapSDK()
tap_identifiers = []


def on_connect(identifier, name, fw):
    print(identifier + " Tap: " + str(name), " FW Version: ", fw)
    tap_identifiers.append(identifier)
    print("Connected taps:")
    for identifier in tap_identifiers:
        print(identifier)


def on_disconnect(identifier):
    print("Tap has disconnected")
    tap_instance.airGestureState = False
    tap_instance.mode = None
    tap_identifiers.remove(identifier)
    for identifier in tap_identifiers:
        print(identifier)


def on_mouse_event(identifier, dx, dy, isMouse):
    if isMouse:
        print(str(dx), str(dy))
    else:
        pass
        # print("Air: ", str(dx), str(dy))


def on_tap_event(identifier, tapcode):
    print(identifier, str(tapcode))
    if int(tapcode) == 17:
        sequence = [500, 200, 500, 500, 500, 200]
        tap_instance.send_vibration_sequence(sequence, identifier)


def on_air_gesture_event(identifier, air_gesture):
    print(" Air gesture: " + TapSDK.AirGestures(air_gesture).name)
    if air_gesture == TapSDK.AirGestures.OneFingerUp.value:
        tap_instance.set_raw_sensors_mode(0, 0, 0, identifier)
    if air_gesture == TapSDK.AirGestures.OnefingerDown.value:
        tap_instance.set_input_mode(TapSDK.TapMode.Text.value, identifier)
    if air_gesture == TapSDK.AirGestures.OnefingerLeft.value:
        tap_instance.set_input_mode(TapSDK.TapMode.Controller.value, identifier)


def on_air_gesture_state_event(identifier: str, air_gesture_state: bool):
    if air_gesture_state:
        tap_instance.airGestureState = True
        print("Entered air mouse mode")
    else:
        tap_instance.airGestureState = False
        print("Left air mouse mode")


def on_raw_sensor_data(identifier, raw_sensor_data):
    if raw_sensor_data.GetPoint(1).z > 2000 and raw_sensor_data.GetPoint(2).z > 2000 and raw_sensor_data.GetPoint(3).z > 2000 and raw_sensor_data.GetPoint(4).z > 2000:
        tap_instance.set_input_mode(TapSDK.TapMode.Controller.value, identifier)


def main():
    tap_instance.register_connection_events(on_connect)
    tap_instance.register_disconnection_events(on_disconnect)
    tap_instance.register_mouse_events(on_mouse_event)
    tap_instance.register_tap_events(on_tap_event)
    tap_instance.register_raw_sensor_data_stream(on_raw_sensor_data)
    tap_instance.register_air_gesture_events(on_air_gesture_event)
    tap_instance.register_air_gesture_state_events(on_air_gesture_state_event)
    tap_instance.run()

    while True:
        pass


if __name__ == "__main__":
    main()

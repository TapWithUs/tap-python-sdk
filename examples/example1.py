import asyncio

from tapsdk import TapSDK, TapInputModes
from tapsdk.models import AirGestures

tap_instance = []
tap_identifiers = []


def on_connect(identifier, name, fw):
    print(identifier + " Tap: " + str(name), " FW Version: ", fw)
    tap_identifiers.append(identifier)
    print("Connected taps:")
    for identifier in tap_identifiers:
        print(identifier)


def on_disconnect(identifier):
    print("Tap has disconnected")
    tap_identifiers.remove(identifier)
    for identifier in tap_identifiers:
        print(identifier)


def on_mouse_event(identifier, dx, dy, isMouse):
    if isMouse:
        print(str(dx), str(dy))
    else:
        pass
        # print("Air: ", str(dx), str(dy))


async def on_tap_event(identifier, tapcode):
    print(identifier, str(tapcode))
    if int(tapcode) == 17:
        sequence = [500, 200, 500, 500, 500, 200]
        await tap_instance.send_vibration_sequence(sequence, identifier)


async def on_air_gesture_event(identifier, air_gesture):
    print(" Air gesture: " + AirGestures(air_gesture).name)
    if air_gesture == AirGestures.UP_ONE_FINGER.value:
        await tap_instance.set_raw_sensors_mode(0, 0, 0, identifier)
    if air_gesture == AirGestures.DOWN_ONE_FINGER.value:
        await tap_instance.set_input_mode(TapInputModes("text"), identifier)
    if air_gesture == AirGestures.LEFT_ONE_FINGER.value:
        await tap_instance.set_input_mode(TapInputModes("controller"), identifier)


def on_air_gesture_state_event(identifier: str, air_gesture_state: bool):
    if air_gesture_state:
        print("Entered air mouse mode")
    else:
        print("Left air mouse mode")


def on_raw_sensor_data(identifier, raw_sensor_data):
    if raw_sensor_data.GetPoint(1).z > 2000 and raw_sensor_data.GetPoint(2).z > 2000 and raw_sensor_data.GetPoint(3).z > 2000 and raw_sensor_data.GetPoint(4).z > 2000:
        tap_instance.set_input_mode(TapInputModes("controller"), identifier)


async def main(loop):
    global tap_instance
    tap_instance = TapSDK(loop)
    await print("aaa")
    await tap_instance.run()
    await tap_instance.register_connection_events(on_connect)
    await tap_instance.register_disconnection_events(on_disconnect)
    await tap_instance.register_mouse_events(on_mouse_event)
    await tap_instance.register_tap_events(on_tap_event)
    await tap_instance.register_raw_data_events(on_raw_sensor_data)
    await tap_instance.register_air_gesture_events(on_air_gesture_event)
    await tap_instance.register_air_gesture_state_events(on_air_gesture_state_event)
    await tap_instance.set_input_mode(TapInputModes("controller"))
    await asyncio.sleep(50.0, loop=loop)

    while True:
        pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

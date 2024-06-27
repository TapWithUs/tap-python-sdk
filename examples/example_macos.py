import asyncio
import time

from tapsdk import TapInputMode, TapSDK
from tapsdk.models import AirGestures


def OnMouseModeChange(identifier, mouse_mode):
    print(str(identifier) + " changed to mode " + str(mouse_mode))


def OnTapped(identifier, tapcode):
    print(str(identifier) + " tapped " + str(tapcode))


def OnGesture(identifier, gesture):
    print(str(identifier) + " gesture " + str(AirGestures(gesture)))


def OnMoused(identifier, vx, vy, isMouse):
    print(str(identifier) + " mouse movement: %d, %d, %d" % (vx, vy, isMouse))


def OnRawData(identifier, packets):
    for m in packets:
        print(f"{m['type']}, {time.time()}, {m['payload']}")


async def run(loop):
    client = TapSDK(loop)
    await client.run()
    print("Connected: {0}".format(client.client.is_connected))

    await client.register_air_gesture_events(OnGesture)
    await client.register_tap_events(OnTapped)
    await client.register_raw_data_events(OnRawData)
    await client.register_mouse_events(OnMoused)
    await client.register_air_gesture_state_events(OnMouseModeChange)

    print("Set Controller Mode for 10 seconds")
    await client.set_input_mode(TapInputMode("controller"))
    await asyncio.sleep(10)

    print("Set Text Mode for 10 seconds")
    await client.set_input_mode(TapInputMode("text"))
    await asyncio.sleep(10)

    print("Send Haptics")
    await client.send_vibration_sequence([100, 200, 100, 200, 500])
    await asyncio.sleep(5)

    print("Set Raw Mode for 5 seconds")
    await asyncio.sleep(2)
    await client.set_input_mode(TapInputMode("raw", sensitivity=[0, 0, 0]))
    await asyncio.sleep(5)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(run(loop))

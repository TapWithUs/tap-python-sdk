import os

from tapsdk import TapSDK, TapInputMode
from tapsdk.models import AirGestures

import asyncio
import logging
from bleak import _logger as logger


def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print("{0}: {1}".format(sender, data))


def OnMouseModeChange(identifier, mouse_mode):
    print(identifier + " changed to mode " + str(mouse_mode))


def OnTapped(identifier, tapcode):
    print(identifier + " tapped " + str(tapcode))


def OnGesture(identifier, gesture):
    print(identifier + " gesture " + str(AirGestures(gesture)))


def OnTapConnected(self, identifier, name, fw):
    print(identifier + " Tap: " + str(name), " FW Version: ", fw)


def OnTapDisconnected(self, identifier):
    print(identifier + " Tap: " + identifier + " disconnected")


def OnMoused(identifier, vx, vy, isMouse):
    print(identifier + " mouse movement: %d, %d, %d" % (vx, vy, isMouse))


def OnRawData(identifier, packets):
    OnRawData.cnt += 1
    if OnRawData.cnt % 20:
        return

    for imu_mgs in list(filter(lambda m: m["type"] == "accl", packets))[:1]:
        payload = [("{:>2}".format(int(p / 10))) for p in imu_mgs["payload"]]
        logger.warning("{} raw imu : {}".format(identifier, payload))


    """
    for m in packets:
        if m["type"] == "imu":
            # print("imu")
            OnRawData.imu_cnt += 1
            if OnRawData.imu_cnt == 208:
                OnRawData.imu_cnt = 0
                # print("imu, " + str(time.time()) + ", " + str(m["payload"]))
        if m["type"] == "accl":
            # print("accl")
            OnRawData.accl_cnt += 1
            if OnRawData.accl_cnt == 200:
                OnRawData.accl_cnt = 0
                print("accl, " + str(time.time()) + ", " + str(m["payload"]))

"""


OnRawData.imu_cnt = 0
OnRawData.accl_cnt = 0
OnRawData.cnt = 0


async def run(loop=None, debug=False):
    if debug:
        import sys

        loop.set_debug(True)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.WARNING)
        logger.addHandler(h)

    sdk = TapSDK(None, loop)
    if not await sdk.client.connect_retrieved():
        logger.error("Failed to connect the the Device.")
        return

    logger.info("Connected to {}".format(sdk.client.address))

    vibrations = [10000]
    logger.info("sending vibration sequence: {}".format(vibrations))
    await sdk.send_vibration_sequence(vibrations)

    await sdk.register_air_gesture_events(OnGesture)
    await sdk.register_tap_events(OnTapped)
    await sdk.register_raw_data_events(OnRawData)
    await sdk.register_mouse_events(OnMoused)
    await sdk.register_air_gesture_state_events(OnMouseModeChange)

    # logger.info("Changing to text mode")
    await sdk.set_input_mode(TapInputMode("text"))
    # await asyncio.sleep(30))
    logger.info("Changing to raw mode")
    await sdk.set_input_mode(TapInputMode("raw", sensitivity=[1023, 1023, 1023]))

    await asyncio.sleep(2 * 60)
    await sdk.send_vibration_sequence(vibrations)


if __name__ == "__main__":
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run(event_loop, True))

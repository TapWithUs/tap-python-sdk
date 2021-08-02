from tapsdk import TapSDK, TapInputMode
from tapsdk.models import AirGestures


import os
os.environ["PYTHONASYNCIODEBUG"] = str(1)
import asyncio
import platform
import logging
from bleak import _logger as logger

import time




def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print("{0}: {1}".format(sender, data))


def OnMouseModeChange(identifier, mouse_mode):
    print(str(identifier) + " changed to mode " + str(mouse_mode))


def OnTapped(identifier, tapcode):
    print(str(identifier) + " tapped " + str(tapcode))


def OnGesture(identifier, gesture):
    print(str(identifier) + " gesture " + str(AirGestures(gesture)))


def OnTapConnected(self, identifier, name, fw):
    print(str(identifier) + " Tap: " + str(name), " FW Version: ", fw)


def OnTapDisconnected(self, identifier):
    print(str(identifier) + " Tap: " + identifier + " disconnected")


def OnMoused(identifier, vx, vy, isMouse):
    print(str(identifier) + " mouse movement: %d, %d, %d" %(vx, vy, isMouse))


def OnRawData(identifier, packets):
    # imu_msg = [m for m in packets if m["type"] == "imu"][0]
    # if len(imu_msg) > 0:
    #     OnRawData.cnt += 1
    #     if OnRawData.cnt == 10:
    #         OnRawData.cnt = 0
    #         logger.info(identifier + " raw imu : " + str(imu_msg["ts"]))

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
    
OnRawData.imu_cnt = 0
OnRawData.accl_cnt = 0
OnRawData.cnt = 0


async def run(loop, debug=False):
    if debug:
        import sys

        # loop.set_debug(True)
        l = logging.getLogger("asyncio")
        l.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.INFO)
        l.addHandler(h)
        logger.addHandler(h)
    
    client = TapSDK(loop)
    # devices = await client.list_connected_taps()
    x = await client.manager.connect_retrieved()
    x = await client.manager.is_connected()
    logger.info("Connected: {0}".format(x))

    await client.set_input_mode(TapInputMode("controller"))

    await client.register_air_gesture_events(OnGesture)
    await client.register_tap_events(OnTapped)
    # await client.register_raw_data_events(OnRawData)
    await client.register_mouse_events(OnMoused)
    await client.register_air_gesture_state_events(OnMouseModeChange)
    
    await asyncio.sleep(3)
    # await client.set_input_mode(TapInputMode("raw", sensitivity=[0,0,0]))
    # await asyncio.sleep(3)
    # await client.set_input_mode(TapInputMode("text"))
    # await asyncio.sleep(3)
    # await client.set_input_mode(TapInputMode("raw", sensitivity=[2,2,2]))
    # await client.send_vibration_sequence([100, 200, 300, 400, 500])

    await asyncio.sleep(50.0, loop=loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, True))

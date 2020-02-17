from tapsdk.backends.macos.TapMacSDK import TapMacSDK
from tapsdk.models.inputmodes import TapInputModes
import os
os.environ["PYTHONASYNCIODEBUG"] = str(1)
import asyncio
import platform
import logging
from bleak import _logger as logger

from tapsdk.models import AirGestures


def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print("{0}: {1} aaaaaaaa".format(sender, data))

def OnTapped(identifier, tapcode):
    print(identifier + " tapped " + str(tapcode))

def OnGesture(identifier, gesture):
    print(identifier + " gesture " + str(AirGestures(gesture)))

def OnTapConnected(self, identifier, name, fw):
    print(identifier + " Tap: " + str(name), " FW Version: ", fw)

def OnTapDisconnected(self, identifier):
    print(identifier + " Tap: " + identifier + " disconnected")

def OnMoused(identifier, vx, vy, isMouse):
    print(identifier + " mouse movement: %d, %d, %d" %(vx, vy, isMouse))


async def run(loop, debug=False):
    if debug:
        import sys

        # loop.set_debug(True)
        l = logging.getLogger("asyncio")
        l.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        l.addHandler(h)
        logger.addHandler(h)
    
    client = TapMacSDK(loop)
    # devices = await client.list_connected_taps()
    x = await client.manager.connect_retrieved()
    x = await client.manager.is_connected()
    logger.info("Connected: {0}".format(x))

    await client.set_input_mode(TapInputModes("controller"))

    await client.register_air_gesture_events(OnGesture)
    await client.register_tap_events(OnTapped)
    # await client.register_mouse_events(OnMoused)
    
    await asyncio.sleep(5)

    await client.send_haptic_command([100, 200, 300, 400, 500])

    await asyncio.sleep(50.0, loop=loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, True))
    # asyncio.run(run(loop, True))
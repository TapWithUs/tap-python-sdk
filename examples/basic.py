import asyncio
import logging
import time

from tapsdk import TapInputMode, TapSDK, InputType, AirGestures


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def OnDisconnection(identifier):
    logger.info("Disconnected. %s", identifier)


def OnConnection(identifier):
    logger.info("Connected. %s", identifier)


def OnMouseModeChange(identifier, mouse_mode):
    logger.info("%s changed to mode %s", identifier, mouse_mode)


def OnTapped(identifier, tapcode):
    logger.info("%s tapped %s", identifier, tapcode)


def OnGesture(identifier, gesture):
    logger.info("%s gesture %s", identifier, AirGestures(gesture))


def OnMoused(identifier, vx, vy, isMouse):
    logger.info("%s mouse movement: %d, %d, %d", identifier, vx, vy, isMouse)


def OnRawData(identifier, packets):
    for m in packets:
        logger.info("%s, %s, %s", m['type'], time.time(), m['payload'])


async def run(loop):
    client = TapSDK(loop=loop)

    client.register_disconnection_events(OnDisconnection)
    client.register_connection_events(OnConnection)
    client.register_air_gesture_events(OnGesture)
    client.register_tap_events(OnTapped)
    client.register_raw_data_events(OnRawData)
    client.register_mouse_events(OnMoused)
    client.register_air_gesture_state_events(OnMouseModeChange)
    await client.run()
    logger.info("Connected: %s", client.client.is_connected)

    logger.info("Set Controller Mode for 5 seconds")
    await client.set_input_mode(TapInputMode("controller"))
    await asyncio.sleep(5)

    logger.info("Force Mouse Mode for 5 seconds")
    await client.set_input_type(InputType.MOUSE)
    await asyncio.sleep(5)

    logger.info("Force keyboard Mode for 5 seconds")
    await client.set_input_type(InputType.KEYBOARD)
    await asyncio.sleep(5)

    logger.info("Set auto Mode for 10 seconds")
    await client.set_input_type(InputType.AUTO)
    await asyncio.sleep(10)

    logger.info("Set Text Mode for 10 seconds")
    await client.set_input_mode(TapInputMode("text"))
    await asyncio.sleep(10)

    logger.info("Send Haptics")
    await client.send_vibration_sequence([100, 200, 100, 200, 500])
    await asyncio.sleep(5)

    logger.info("Set Raw Mode for 5 seconds")
    await asyncio.sleep(2)
    await client.set_input_mode(TapInputMode("raw", sensitivity=[0, 0, 0]))
    await asyncio.sleep(5)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(run(loop))

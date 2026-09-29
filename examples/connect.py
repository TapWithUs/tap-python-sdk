import asyncio
import logging

from tapsdk import TapSDK2, connect

logging.basicConfig(level=logging.INFO)
logging.getLogger("tapsdk").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


def on_connect(identifier):
    logger.info("Connected: %s", identifier)


def on_disconnect(client):
    logger.info("Disconnected: %s", client)


def on_tap(identifier, tapcode):
    logger.info("Tap %s: %s", identifier, tapcode)


async def main():
    # Two-phase: connect+detect, register callbacks, then start notifies.
    async with await connect() as sdk:
        sdk.register_connection_events(on_connect)
        sdk.register_disconnection_events(on_disconnect)
        sdk.register_tap_events(on_tap)

        await sdk.start()
        protocol_type = "v2" if isinstance(sdk, TapSDK2) else "v1"
        logger.info("Protocol: %s", protocol_type)
        logger.info("Device info: %s", await sdk.get_device_info())

        await sdk.send_vibration_sequence([100, 200, 100])
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

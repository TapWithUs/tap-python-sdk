import asyncio
import logging

from tapsdk import (
    DeviceFeatures,
    InputModeController,
    ModelTypes,
    VisionSensorOpModes,
    connect,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("tapsdk").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


def on_connect(identifier):
    logger.info("Connected: %s", identifier)


def on_disconnect(client):
    logger.info("Disconnected: %s", client)


def on_tap(identifier, tapcode):
    code = tapcode[0] if isinstance(tapcode, (list, tuple)) else tapcode
    logger.info("Tap %s: %s", identifier, code)


async def enable_input(sdk):
    """Switch out of keyboard mode so tap events reach this process."""
    if hasattr(sdk, "set_input_mode"):
        await sdk.set_input_mode(InputModeController())
    else:
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
        await sdk.set_vision_sensor_model(ModelTypes.TAPPING)
        await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)


async def main():
    # connect, register callbacks, start notifies, then enable input.
    async with await connect() as sdk:
        sdk.register_connection_events(on_connect)
        sdk.register_disconnection_events(on_disconnect)
        sdk.register_tap_events(on_tap)

        await sdk.start()
        await enable_input(sdk)
        logger.info("SDK class: %s", type(sdk).__name__)
        logger.info("Device info: %s", await sdk.get_device_info())

        await sdk.send_vibration_sequence([100, 200, 100])
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

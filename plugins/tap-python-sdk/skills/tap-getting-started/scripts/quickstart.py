"""Connect to any Tap and print taps and air gestures.

Run:  python quickstart.py            # taps
      python quickstart.py --air      # air gestures (TapXR developer firmware / TapBand)
"""
import argparse
import asyncio

from tapsdk import (DeviceFeatures, InputModeController, ModelTypes,
                    VisionSensorOpModes, connect)

FINGERS = ["thumb", "index", "middle", "ring", "pinky"]


def first(value):
    """Some firmware sends a bare int; some sends a one-element list."""
    return value[0] if isinstance(value, (list, tuple)) else value


def fingers(tapcode):
    return [name for bit, name in enumerate(FINGERS) if tapcode & (1 << bit)]


def on_tap(identifier, tapcode):
    code = first(tapcode)
    print(f"tap {code:2d} -> {'+'.join(fingers(code))}")


def on_air_gesture(identifier, gesture):
    print("air gesture", first(gesture))


async def enable_input(sdk, air):
    if hasattr(sdk, "set_input_mode"):
        # TapSDK boots in Text mode, which sends no tap events to the SDK.
        await sdk.set_input_mode(InputModeController())
        return
    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    if air:
        await sdk.set_vision_sensor_model(ModelTypes.AIR_GESTURE)
        await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)
    else:
        await sdk.set_vision_sensor_model(ModelTypes.TAPPING)
        await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)


async def main(air):
    sdk = await connect()
    sdk.register_tap_events(on_tap)
    sdk.register_air_gesture_events(on_air_gesture)
    sdk.register_disconnection_events(lambda client: print("disconnected"))
    await sdk.start()
    print("connected,", type(sdk).__name__)
    await enable_input(sdk, air)

    await sdk.send_vibration_sequence([100, 100, 100])
    print("ready - tap your fingers (Ctrl+C to quit)")
    await asyncio.Event().wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--air",
        action="store_true",
        help="use the air-gesture model (TapXR developer firmware / TapBand)",
    )
    try:
        asyncio.run(main(parser.parse_args().air))
    except KeyboardInterrupt:
        pass

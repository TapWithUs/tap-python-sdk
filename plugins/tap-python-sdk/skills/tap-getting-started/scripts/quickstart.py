"""Connect to any Tap (v1 or v2) and print taps and air gestures.

Run:  python quickstart.py            # taps
      python quickstart.py --air      # air gestures instead of taps (v2 model switch)
"""
import argparse
import asyncio

from tapsdk import (DeviceFeatures, InputModeController, ModelTypes, TapSDK2,
                    VisionSensorOpModes, connect)

FINGERS = ["thumb", "index", "middle", "ring", "pinky"]


def first(value):
    """v1 sends a bare int; v2 sends a one-element list."""
    return value[0] if isinstance(value, (list, tuple)) else value


def fingers(tapcode):
    return [name for bit, name in enumerate(FINGERS) if tapcode & (1 << bit)]


def on_tap(identifier, tapcode):
    code = first(tapcode)
    print(f"tap {code:2d} -> {'+'.join(fingers(code))}")


def on_air_gesture(identifier, gesture):
    print("air gesture", first(gesture))


async def main(air):
    sdk = await connect()
    is_v2 = isinstance(sdk, TapSDK2)
    sdk.register_tap_events(on_tap)
    sdk.register_air_gesture_events(on_air_gesture)
    sdk.register_disconnection_events(lambda client: print("disconnected"))
    await sdk.start()
    print("connected, protocol", "v2" if is_v2 else "v1")

    if is_v2:
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
        if air:
            await sdk.set_vision_sensor_model(ModelTypes.AIR_GESTURE)
            await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)
        else:
            await sdk.set_vision_sensor_model(ModelTypes.TAPPING)
            await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)
    else:
        # v1 boots in Text mode, which sends no tap events to the SDK.
        await sdk.set_input_mode(InputModeController())

    await sdk.send_vibration_sequence([100, 100, 100])
    print("ready - tap your fingers (Ctrl+C to quit)")
    await asyncio.Event().wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--air", action="store_true", help="v2: use the air-gesture model")
    try:
        asyncio.run(main(parser.parse_args().air))
    except KeyboardInterrupt:
        pass

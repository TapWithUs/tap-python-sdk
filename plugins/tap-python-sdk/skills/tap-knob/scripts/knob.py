"""Knob: hold a pinch and twist the hand to turn a value up or down (Tap v2).

Run:  python knob.py
Hold thumb+index (AB) and roll the wrist: the value changes. Relax the hand to release.
Each pinch (AB, AC, AD, AE) is a separate knob, so one hand controls four values.
"""
import asyncio

HOLD_CODES = {110: 0, 111: 1, 112: 2, 113: 3}   # AB_HOLD..AE_HOLD -> knob index
NONE_CODE = 100


def wrap_degrees(delta):
    """Shortest signed angle, so crossing +/-180 does not jump."""
    return (delta + 180) % 360 - 180


class KnobTracker:
    """Turns air-gesture codes plus IMU roll into knob steps.

    on_gesture(code) -> "start" | "release" | None
    on_roll(roll)    -> signed int steps (0 when idle)
    active           -> knob index 0-3 while a pinch is held, else None
    """

    def __init__(self, step_deg=1.0, release_after=4):
        self.step_deg = step_deg
        self.release_after = release_after
        self.active = None
        self._anchor = None
        self._none_count = 0

    def on_gesture(self, code):
        if code == NONE_CODE:
            if self.active is None:
                return None
            self._none_count += 1
            if self._none_count >= self.release_after:
                self.active = None
                self._anchor = None
                return "release"
            return None
        self._none_count = 0
        knob = HOLD_CODES.get(code)
        if knob is None or knob == self.active:
            return None
        self.active = knob
        self._anchor = None
        return "start"

    def on_roll(self, roll):
        if self.active is None:
            return 0
        if self._anchor is None:
            self._anchor = roll
            return 0
        steps = int(wrap_degrees(roll - self._anchor) / self.step_deg)
        if steps:
            self._anchor = wrap_degrees(self._anchor + steps * self.step_deg)
        return steps


async def main():
    from tapsdk import DeviceFeatures, ModelTypes, TapSDK2, VisionSensorOpModes, connect

    sdk = await connect()
    if not isinstance(sdk, TapSDK2):
        raise SystemExit("The knob needs a v2 (TapSDK2) device: air-gesture holds + IMU roll.")

    knob = KnobTracker(step_deg=2)
    values = [50, 50, 50, 50]
    loop = asyncio.get_running_loop()

    def on_air_gesture(identifier, data):
        event = knob.on_gesture(int(data[0]))
        if event == "start":
            print(f"knob {knob.active} grabbed")
            loop.create_task(sdk.send_vibration_sequence([40]))
        elif event == "release":
            print("released")

    def on_motion(identifier, motion):
        _, _, _, (roll, _, _) = motion
        steps = knob.on_roll(roll)
        if steps:
            i = knob.active
            values[i] = max(0, min(100, values[i] + steps))
            print(f"knob {i}: {values[i]:3d} {'#' * (values[i] // 5)}")

    sdk.register_air_gesture_events(on_air_gesture)
    sdk.register_imu_motion_data_events(on_motion)
    await sdk.start()
    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    await sdk.set_vision_sensor_model(ModelTypes.AIR_GESTURE)
    await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)
    await sdk.set_feature(DeviceFeatures.IMU_MOTION_DATA, True)
    print("ready - hold a pinch and twist (Ctrl+C to quit)")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

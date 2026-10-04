"""D-Pad: swipe for directions, pinch to select, hold a pinch to rotate or drag (Tap v2).

Run:  python dpad.py
- Swipe left / right / up / down       -> direction
- Short pinch AB / AC / AD / AE        -> select item 0-3
- Hold a pinch, then twist within 1 s  -> rotate mode (roll angle)
- Hold a pinch, do not twist           -> drag mode (dx, dy)
- Relax the hand                       -> release
- Hold a fist                          -> hide; relax to show again
"""
import asyncio
import time

NONE, LEFT, RIGHT, UP, DOWN = 100, 101, 102, 103, 104
FIST_HOLD = 114
SWIPES = {LEFT: "left", RIGHT: "right", UP: "up", DOWN: "down"}
PINCHES = {105: 0, 106: 1, 107: 2, 108: 3}        # AB, AC, AD, AE
HOLDS = {110: 0, 111: 1, 112: 2, 113: 3}          # AB_HOLD..AE_HOLD


class DpadStateMachine:
    """Turns air-gesture codes plus IMU motion into D-Pad events.

    Every method returns a list of event tuples:
      ("direction", "left"|"right"|"up"|"down")
      ("pinch", index)            short pinch, only when nothing is held
      ("hold", index)             pinch-hold started, mode is "pending"
      ("mode", "rotate"|"drag")   mode locked
      ("rotate", degrees)         roll relative to the start of the hold
      ("drag", dx, dy)            pointer deltas
      ("release", index)
      ("hide",) / ("show",)
    Pass `now` in seconds (time.monotonic()).
    """

    def __init__(self, rotate_lock_deg=25.0, lock_window_s=1.0, release_after=4,
                 show_after=2, debounce_s=0.040):
        self.rotate_lock_deg = rotate_lock_deg
        self.lock_window_s = lock_window_s
        self.release_after = release_after
        self.show_after = show_after
        self.debounce_s = debounce_s
        self.held = None
        self.mode = None
        self.hidden = False
        self._hold_start = 0.0
        self._ref_roll = None
        self._last_roll = None
        self._roll_travel = 0.0
        self._none_count = 0
        self._last_code = None
        self._last_code_t = -1.0

    def _debounced(self, code, now):
        if code == self._last_code and now - self._last_code_t < self.debounce_s:
            return True
        self._last_code, self._last_code_t = code, now
        return False

    def _release(self):
        events = [("release", self.held)] if self.held is not None else []
        self.held = self.mode = self._ref_roll = self._last_roll = None
        self._none_count = 0
        return events

    def _lock(self, mode):
        self.mode = mode
        return [("mode", mode)]

    def tick(self, now):
        """Lock drag mode when the twist window ends without enough roll."""
        if self.mode == "pending" and now - self._hold_start >= self.lock_window_s:
            return self._lock("rotate" if self._roll_travel >= self.rotate_lock_deg else "drag")
        return []

    def on_gesture(self, code, now):
        events = self.tick(now)
        if code == NONE:
            self._none_count += 1
            if self.hidden and self._none_count >= self.show_after:
                self.hidden = False
                self._none_count = 0
                events.append(("show",))
            elif self.held is not None and self._none_count >= self.release_after:
                events += self._release()
            return events
        if self.hidden:
            return events
        self._none_count = 0

        if code == FIST_HOLD:
            if not self._debounced(code, now):
                events += self._release()
                self.hidden = True
                events.append(("hide",))
        elif code in SWIPES:
            if not self._debounced(code, now):
                events.append(("direction", SWIPES[code]))
        elif code in HOLDS:
            index = HOLDS[code]
            if index != self.held and not self._debounced(code, now):
                events += self._release()
                self.held, self.mode = index, "pending"
                self._hold_start, self._roll_travel = now, 0.0
                events.append(("hold", index))
        elif code in PINCHES:
            if self.held is None and not self._debounced(code, now):
                events.append(("pinch", PINCHES[code]))
        return events

    def on_motion(self, dx, dy, roll, now):
        events = self.tick(now)
        if self.held is None:
            return events
        if self.mode == "drag":
            if dx or dy:
                events.append(("drag", dx, dy))
            return events
        if self._last_roll is not None:
            self._roll_travel += abs(roll - self._last_roll)
        self._last_roll = roll
        if self._ref_roll is None:
            self._ref_roll = roll
        if self.mode == "pending" and self._roll_travel >= self.rotate_lock_deg:
            events += self._lock("rotate")
        events.append(("rotate", roll - self._ref_roll))
        return events


async def main():
    from tapsdk import DeviceFeatures, ModelTypes, TapSDK2, VisionSensorOpModes, connect

    sdk = await connect()
    if not isinstance(sdk, TapSDK2):
        raise SystemExit("The D-Pad needs a v2 (TapSDK2) device: air gestures + IMU motion.")

    dpad = DpadStateMachine()
    loop = asyncio.get_running_loop()

    def show(events):
        for event in events:
            if event[0] in ("hold", "mode", "pinch"):
                loop.create_task(sdk.send_vibration_sequence([40]))
            if event[0] not in ("rotate", "drag"):
                print(*event)

    def on_air_gesture(identifier, data):
        show(dpad.on_gesture(int(data[0]), time.monotonic()))

    def on_motion(identifier, motion):
        dx, dy, _, (roll, _, _) = motion
        events = dpad.on_motion(dx, dy, roll, time.monotonic())
        show(events)
        for event in events:
            if event[0] in ("rotate", "drag"):
                print(*event, end="        \r")

    sdk.register_air_gesture_events(on_air_gesture)
    sdk.register_imu_motion_data_events(on_motion)
    await sdk.start()
    await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    await sdk.set_vision_sensor_model(ModelTypes.AIR_GESTURE)
    await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)
    await sdk.set_feature(DeviceFeatures.IMU_MOTION_DATA, True)
    print("ready - swipe, pinch, or hold a pinch (Ctrl+C to quit)")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

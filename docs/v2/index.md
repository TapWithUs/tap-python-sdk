# `TapSDK2`

Developer firmware: `DeviceFeatures`, vision / IMU / standby commands, tap codes as one-element lists. Typical hardware: TapXR with the TapXR developer firmware, and TapBand.

TapBand uses the same BLE API as TapXR and is coming soon. It is not for sale yet. Join the [TapBand waitlist](https://www.tapwithus.com/tapband-waitlist/).

The TapXR developer firmware supports the full gesture set: taps, thumb swipes, pinches with hold, fist with hold. Python receives those raw detections with `register_air_gesture_events` (`UnifiedAirGestures`).

| Goal | Section |
|------|---------|
| First working connection | [Tutorial](tutorial/getting-started.md) |
| Solve a specific task | [How-to guides](how-to/index.md) |
| Look up an API, type, or event | [Reference](reference/index.md) |
| Understand the features model | [Explanation](explanation/index.md) |

Shared install, enums, and package notes live on the [Home](../index.md) page. For input-mode firmware (Tap Strap / Tap Strap 2), use [`TapSDK`](../v1/index.md).

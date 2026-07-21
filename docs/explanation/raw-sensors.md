# Raw sensors

Raw mode exposes the motion sensors behind Tap’s gesture pipeline. That is useful for research, custom gesture models, and XR prototypes — not for everyday typing.

## What is streamed

1. **Finger accelerometers** (Tap Strap / Tap Strap 2): one 3-axis sensor per finger, ~200 Hz, configurable ±2/4/8/16 g.
2. **Thumb IMU** (Tap Strap 2 / TapXR): accelerometer + gyro, ~208 Hz, configurable accelerometer and gyro ranges.

Samples are timestamped in milliseconds on an internal device clock. Timestamps are not synchronized to wall time by the SDK.

## Scaling

Firmware sends integer LSB counts. `InputModeRaw(scaled=True)` multiplies by the scale factors that belong to the selected sensitivity enums, yielding **mg** (accelerometer) and **mdps** (gyro). If you scale yourself, keep `scaled=False` and use `RawSensorsSensitivity.get_scale_factors()`.

You cannot change sensitivity while remaining in raw mode with a different command; leave raw mode, then re-enter with new enums.

## Reference frames

Axes are defined relative to the hardware. See the diagrams in the repository root:

- `TAP-axis-alpha.png` — Tap Strap
- `TAPXR-axis.png` — TapXR

Additional protocol notes: [Tap Strap Raw Sensors Mode](https://tapwithus.atlassian.net/wiki/spaces/TD/pages/792002574/Tap+Strap+Raw+Sensors+Mode) (internal Confluence).

## Developer mode

Raw streaming expects Developer mode enabled in Tap Manager. Without it, characteristics may be present but the stream may not behave as documented.

# Switch input modes

Input mode controls whether the Tap talks to the OS as a keyboard/mouse, streams events to your app, or both.

## Choose a mode

```python
from tapsdk import (
    InputModeText,
    InputModeController,
    InputModeControllerText,
    InputModeRaw,
)

await tap.set_input_mode(InputModeText())              # OS typing only; no SDK tap events
await tap.set_input_mode(InputModeController())        # SDK events only
await tap.set_input_mode(InputModeControllerText())    # both
await tap.set_input_mode(InputModeRaw(...))            # raw sensor stream
```

## When to use each

| Mode | Use when |
|------|----------|
| Text | You want normal Tap typing; your app does not need tap events |
| Controller | Your app is the sole consumer (games, custom UI) |
| Controller + Text | Users still type while your app also listens |
| Raw | You need accelerometer / IMU samples |

## Refresh behavior

After the first `set_input_mode` / `set_input_type`, the SDK periodically rewrites the mode so the device stays in sync if the link hiccups. You do not need to call refresh yourself.

## Changing raw sensitivities

You cannot change raw sensitivity enums while already in raw mode with a different command payload. Leave raw mode first (for example switch to Controller), then enter raw again with the new settings. See [Stream raw sensors](stream-raw-sensors.md).

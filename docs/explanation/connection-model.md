# Connection model

The Tap is a Bluetooth Low Energy peripheral. This SDK does not use HID for app control; it opens a GATT session with Bleak and talks to Tap’s proprietary service plus a Nordic UART-style service for mode commands and raw data.

## Why pair with the OS first

On every platform the most reliable path is: pair in system Bluetooth settings, ensure the device is connected (or connectable), then call `TapSDK.run()`. The SDK then attaches to that session instead of racing a cold advertisement scan.

Platform differences matter:

- **macOS** retrieves already-connected peripherals that expose the Tap service.
- **Windows** uses WinRT to find connected Tap devices and opens a GATT session without Bleak’s normal connect wait (which can hang if the session is already active). If nothing is connected, it scans and also polls for paired reconnects that do not advertise.
- **Linux** lists BlueZ devices with `bt-device` and connects to names starting with `Tap`.

## Single device today

Method signatures accept an `identifier` argument on commands, but the SDK currently drives one `TapClient` at a time. Multi-device support is a separate concern from documentation of the present API.

## Notifications vs commands

- **Commands** (mode, input type, haptics) are GATT writes.
- **Events** (tap, mouse, air gesture, raw) are GATT notifications parsed into callback arguments.

After you set a mode, a background refresh task rewrites mode and input type periodically so a flaky link is less likely to leave the device in the wrong state.

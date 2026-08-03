# Package layout

## Public imports (`tapsdk`)

| Name | Kind |
|------|------|
| `connect` | Async factory — attach, detect v1/v2, return `TapSDK` or `TapSDK2` (notifies not started) |
| `TapSDK` | Class (lazy import from `tapsdk.tap`) — v1 protocol |
| `TapSDK2` | Class (lazy import from `tapsdk.tap2`) — v2 framed protocol |
| `InputModeText` | Class |
| `InputModeController` | Class |
| `InputModeControllerText` | Class |
| `InputModeRaw` | Class |
| `InputType` | Enum |
| `AirGestures` | Enum |
| `ImuAcclSensitivity` | Enum |
| `DeviceFeatures` | Enum |
| `UnifiedAirGestures` | Enum |
| `VisionSensorOpModes` | Enum |
| `ModelTypes` | Enum |
| `DeviceInfo` | Dataclass (lazy import from `tapsdk.device_info`) |

Version string: `tapsdk.__version__`.

## Modules

| Module | Role |
|--------|------|
| `tapsdk._transport` | Shared `TapClient`, `connect_tap()` scan/attach |
| `tapsdk._detect` | `detect_protocol(client)` → `"v1"` / `"v2"` |
| `tapsdk.device_info` | Shared `DeviceInfo` / `get_device_info` GATT reads (DIS/BAS) |
| `tapsdk.tap` | `TapSDK` (v1), GATT UUIDs |
| `tapsdk.tap2` | `TapSDK2` (v2), framed-protocol UUIDs |
| `tapsdk.inputmodes` | Mode command builders |
| `tapsdk.enumerations` | Public enums |
| `tapsdk.parsers` | Notification payload parsers |
| `tapsdk.encoder` | v2 outbound framed commands |

## GATT characteristics (SDK-owned)

| Constant | UUID | Use |
|----------|------|-----|
| `tap_service` | `c3ff0001-…` | Tap proprietary service |
| `tap_data_characteristic` | `c3ff0005-…` | v1 tap events (notify) |
| `mouse_data_characteristic` | `c3ff0006-…` | v1 mouse events (notify) |
| `ui_cmd_characteristic` | `c3ff0009-…` | v1 haptics (write) |
| `air_gesture_data_characteristic` | `c3ff000a-…` | v1 air gestures / mouse mode (notify) |
| `tap_mode_characteristic` | `6e400002-…` | NUS RX — mode / input-type commands (write) |
| `raw_sensors_characteristic` | `6e400003-…` | NUS TX — raw stream (notify) |
| `tap_data_read_characteristic` | `c3ff000e-…` | v2 framed notify (also used for protocol detect) |
| `tap_data_write_characteristic` | `c3ff000f-…` | v2 framed write |

Lower-level BLE protocol details: [Tap BLE API Documentation](https://tapwithus.atlassian.net/wiki/spaces/FIR/pages/426803201/Tap+BLE+API+Documentation) (internal).

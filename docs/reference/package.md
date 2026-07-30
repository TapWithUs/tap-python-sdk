# Package layout

## Public imports (`tapsdk`)

| Name | Kind |
|------|------|
| `TapSDK` | Class (lazy import from `tapsdk.tap`) |
| `InputModeText` | Class |
| `InputModeController` | Class |
| `InputModeControllerText` | Class |
| `InputModeRaw` | Class |
| `InputType` | Enum |
| `AirGestures` | Enum |
| `DeviceInfo` | Dataclass (lazy import from `tapsdk.tap`) |

Version string: `tapsdk.__version__`.

## Modules

| Module | Role |
|--------|------|
| `tapsdk.tap` | BLE client, `TapSDK`, GATT UUIDs |
| `tapsdk.inputmodes` | Mode command builders |
| `tapsdk.enumerations` | Public enums |
| `tapsdk.parsers` | Notification payload parsers |

## GATT characteristics (SDK-owned)

| Constant | UUID | Use |
|----------|------|-----|
| `tap_service` | `c3ff0001-…` | Tap proprietary service |
| `tap_data_characteristic` | `c3ff0005-…` | Tap events (notify) |
| `mouse_data_characteristic` | `c3ff0006-…` | Mouse events (notify) |
| `ui_cmd_characteristic` | `c3ff0009-…` | Haptics (write) |
| `air_gesture_data_characteristic` | `c3ff000a-…` | Air gestures / mouse mode (notify) |
| `tap_mode_characteristic` | `6e400002-…` | NUS RX — mode / input-type commands (write) |
| `raw_sensors_characteristic` | `6e400003-…` | NUS TX — raw stream (notify) |

Lower-level BLE protocol details: [Tap BLE API Documentation](https://tapwithus.atlassian.net/wiki/spaces/FIR/pages/426803201/Tap+BLE+API+Documentation) (internal).

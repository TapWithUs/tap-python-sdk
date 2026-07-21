# Migrate from 0.6.x to 0.7.x

## Input modes

```python
# 0.6
TapInputMode("controller")
TapInputMode("raw", sensitivity=[2, 1, 4])

# 0.7
from tapsdk import InputModeController, InputModeRaw
from tapsdk.enumerations import FingerAcclSensitivity, ImuGyroSensitivity, ImuAcclSensitivity

InputModeController()
InputModeRaw(
    finger_accl_sens=FingerAcclSensitivity.G4,
    imu_gyro_sens=ImuGyroSensitivity.DPS125,
    imu_accl_sens=ImuAcclSensitivity.G8,
)
```

## Imports

```python
# 0.6
from tapsdk.models import AirGestures

# 0.7
from tapsdk import AirGestures
```

## Async API

- Removed: `loop=` constructor argument.
- `register_*` remains synchronous — call before `await run()`.
- `set_input_mode`, `set_input_type`, and `send_vibration_sequence` are **async** and must be awaited.

## Examples and backends

- Use [`examples/basic.py`](../../examples/basic.py) instead of `example_unix.py` / `example_win.py`.
- Windows no longer uses `TAPWin.dll`; Bleak/WinRT is required.
- Python 3.9+ is required.

# Input modes

Tap hardware always has a “personality” toward the host: it can act as a keyboard/mouse for the operating system, stream structured controller events to an app, stream raw IMU data, or combine some of these.

On `TapSDK`, the SDK models that personality as **input modes** (`set_input_mode` / NUS).

- **Text** — OS-facing HID behavior; your Python callbacks stay quiet for taps.
- **Controller** — events are for your app; classic typing to the OS is not the goal.
- **Controller + Text** — parallel paths when users still need to type.
- **Raw** — bypass gesture interpretation and ship sensor samples.

Modes are orthogonal to the **TapXR input type** (mouse vs keyboard vs auto, `set_input_type`) on stock TapXR firmware. Mode answers “who receives data and in what form?”; input type answers “which XR input modality is forced?”.

Text mode and HID exist only on this firmware (Tap Strap and stock TapXR). The TapXR developer firmware (`TapSDK2`) has no input modes, no HID, and no input type.

Switching modes is a small binary command on the NUS RX characteristic. The SDK owns the byte layout so applications work with typed classes instead of magic numbers.

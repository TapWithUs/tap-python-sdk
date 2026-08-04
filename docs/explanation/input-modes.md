# Input modes

Tap hardware always has a “personality” toward the host: it can act as a keyboard/mouse for the operating system, stream structured controller events to an app, stream raw IMU data, or combine some of these.

!!! note "v1 only"
    Input modes (`set_input_mode` / NUS) apply to **v1** (`TapSDK`). **v2** (`TapSDK2`) has no Text / Controller / Raw mode write — enable streams with [`DeviceFeatures`](../reference/enumerations.md#devicefeatures). See [Use v2 features](../how-to/use-v2-features.md) and the [connection model](connection-model.md) v1 vs v2 table.

The SDK models that personality as **input modes**:

- **Text** — OS-facing HID behavior; your Python callbacks stay quiet for taps.
- **Controller** — events are for your app; classic typing to the OS is not the goal.
- **Controller + Text** — parallel paths when users still need to type.
- **Raw** — bypass gesture interpretation and ship sensor samples.

Modes are orthogonal to **Spatial Control input type** (mouse vs keyboard vs auto) on TapXR. Mode answers “who receives data and in what form?”; input type answers “which XR input modality is forced?” when you have experimental firmware access.

Switching modes is a small binary command on the NUS RX characteristic. The SDK owns the byte layout so applications work with typed classes instead of magic numbers.

## TapStrap Python SDK (beta)

[![PyPI version](https://img.shields.io/pypi/v/tap-python-sdk.svg)](https://pypi.org/project/tap-python-sdk/)

### What Is This ?

TAP python SDK allows you to build python app that can establish BLE connection with Tap Strap and TapXR, send commands and receive events and data - Thus allowing TAP to act as a controller for your app!  
The library is developed with Python >= 3.9 and is **currently in beta**.


### Supported Platforms
This package supports the following platforms:
* MacOS (tested on 10.15.2) - using Apple's CoreBluetooth library. The library depends on PyObjC which Apple includes with their Python version on OSX. Note that if you're using a different Python, be sure to install PyObjC for that version of Python.  
* Windows 10 - using [Bleak](https://github.com/hbldh/bleak) with WinRT for BLE connectivity (no external DLL required).
* Linux (tested on Ubuntu 18.04) - need to install libbluetooth-dev and bluez-tools
    ```
    sudo apt-get install bluez-tools libbluetooth-dev
    ```
    also the user needs to be in the bluetooth group:
    ```
    sudo usermod -G bluetooth -a <username>
    #and can reload groups in this shell by running the following command or by logging out and back in:
    su - $USER
    ```


### Installation

Install the package from PyPI:
```console
pip install tap-python-sdk
```

Or clone this repo and install the package locally:
```console
git clone https://github.com/TapWithUs/tap-python-sdk
cd tap-python-sdk
pip install .
```


The SDK is asyncio-based. Pair your Tap device with the OS first, then connect and register callbacks inside an async entry point:

```python
import asyncio
from tapsdk import TapSDK

async def main():
    tap_device = TapSDK()
    tap_device.register_tap_events(lambda identifier, tapcode: print(identifier, tapcode))
    await tap_device.run()  # connects to a paired Tap, or scans until one is found

asyncio.run(main())
```

If no Tap is already connected at the OS level, `run()` will scan and wait for a device. On Windows and MacOS it also polls for already-paired devices that reconnect without advertising.

Also make sure that you have updated your Tap device to the latest version.

### BLE GATT reference

Verified against firmware `tap_rd/ble-mcu-hw-v3-sdk-14.0` branch **`TAP_XR_develop`** (`ble_tap_service.c`, `services_init`, Nordic `ble_nus`). Also matches the other official Tap SDKs and [Tap BLE API Documentation](https://tapwithus.atlassian.net/wiki/spaces/FIR/pages/426803201/Tap+BLE+API+Documentation).

Tap base UUID: `c3ff0000-1d8b-40fd-a56f-c7bd5d0f3370` (16-bit offsets below). NUS is the standard Nordic UART base `6e400000-b5a3-f393-e0a9-e50e24dcca9e`.

**Advertising:** primary adv carries HID (`0x1812`); Tap service UUID is in the **scan response**. Active scan (or OS-paired reconnect) is needed to see `c3ff0001-…` in advertised service lists.

#### Services the firmware always registers

From `services_init()` / device mediator on `TAP_XR_develop`:

| Service | UUID | Role |
| --- | --- | --- |
| HID | `00001812-0000-1000-8000-00805f9b34fb` | Keyboard / mouse HID over GATT |
| Battery | `0000180f-0000-1000-8000-00805f9b34fb` | Battery Level |
| Device Information | `0000180a-0000-1000-8000-00805f9b34fb` | FW / HW / serial strings |
| Buttonless DFU | Nordic DFU | FOTA bootloader trigger |
| **Tap** | `c3ff0001-1d8b-40fd-a56f-c7bd5d0f3370` | Proprietary events / commands |
| **NUS** | `6e400001-b5a3-f393-e0a9-e50e24dcca9e` | Mode / raw-sensor channel |

#### Required by this Python SDK

Minimum used for discovery, mode control, and tap events (Windows SDK similarly requires Tap Data + NUS RX):

| Role | UUID | FW properties | Purpose |
| --- | --- | --- | --- |
| Tap service | `c3ff0001-…` | (service; scan response) | Find / filter Tap |
| Tap data | `c3ff0005-…` | Notify | Tap codes (`register_tap_events`) |
| NUS service | `6e400001-…` | (service) | Mode channel |
| NUS RX | `6e400002-…` | Write | Input mode / type (`set_input_mode`, `set_input_type`); refresh ~every 10s in controller/raw |

#### Used optionally by this SDK

Notify setup is best-effort if a characteristic is missing on older devices.

| Characteristic | UUID | FW properties | Purpose |
| --- | --- | --- | --- |
| Mouse data | `c3ff0006-…` | Notify, Write, WriteWithoutResponse | Surface mouse (`register_mouse_events`) |
| UI / haptic | `c3ff0009-…` | Write, WriteWithoutResponse | Vibration (`send_vibration_sequence`) |
| Air gesture | `c3ff000a-…` | Notify, WriteWithoutResponse, Read | Air gestures / mouse-mode state (`register_air_gesture_*`) |
| NUS TX | `6e400003-…` | Notify | Raw sensors (`register_raw_data_events`; Developer mode) |

#### Other Tap-service characteristics (on device; unused here)

Registered in `ble_tap_init()` on `TAP_XR_develop`:

| Char | UUID | FW properties | Notes |
| --- | --- | --- | --- |
| Settings | `c3ff0002-…` | Read, Write | Device settings |
| Name | `c3ff0003-…` | Read, Write | BLE name (Android SDK) |
| Mapping RX | `c3ff0007-…` | Write, WriteWithoutResponse | Custom map upload |
| Mapping TX | `c3ff0008-…` | Notify | Custom map download |
| Data request | `c3ff000b-…` | Notify, WriteWithoutResponse, Read | State queries (Android SDK) |
| Kneron model ver | `c3ff000c-…` | Notify, Read | TapXR NPU model |
| Kneron FW ver | `c3ff000d-…` | Notify, Read | TapXR NPU firmware |

Constants: [`tapsdk/tap.py`](tapsdk/tap.py).

### Features

This SDK implements two basic interfaces with a Tap device.

First is setting the operation mode:

1. *Text mode* - the Tap device will operate normally, with no events being sent to the SDK
2. *Controller mode* - the Tap device will send events to the SDK
3. *Controller and Text mode* - the Tap device will operate normally, in parallel with sending events to the SDK
4. *Raw data mode* - the Tap device will stream raw sensors data to the SDK.

Second, subscribing to the following events:

1. *Tap event* - whenever a tap event has occurred
2. *Mouse event* - whenever a mouse movement has occurred
3. *AirGesture event* - whenever one of the gestures is detected
4. *Raw data* - whenever new raw data sample is being made.

Additional to these functional events, there are also some state events, such as connection and disconnection of Tap devices to the SDK backend.

#### Spatial Control - NEW
Authorized developers can gain access to the experimental Spatial Control features:
1. Extended AirGesture state - enabling aggregation for pinch, drag and swipe gestures.
2. Select input type - enabling the selection of input type to be activated - i.e. AirMouse/Tapping. 

These features are only available on TapXR and only for qualified developers. Request access [here](https://www.tapwithus.com/contact-us/)


### Migration from 0.6.x

If you are upgrading from an earlier release, note these breaking changes:

* `TapInputMode("controller")` → `InputModeController()` (and similarly for other modes). Import from `tapsdk`.
* `TapInputMode("raw", sensitivity=[2, 1, 4])` → `InputModeRaw(finger_accl_sens=..., imu_gyro_sens=..., imu_accl_sens=...)`. Use the typed enums in `tapsdk.enumerations`.
* `from tapsdk.models import AirGestures` → `from tapsdk import AirGestures`
* The `loop=` constructor argument has been removed.
* Event registration (`register_*`) is synchronous; call it before `await tap_device.run()`.
* Commands (`set_input_mode`, `set_input_type`, `send_vibration_sequence`) are async and must be awaited.
* OS-specific examples (`example_unix.py`, `example_win.py`) have been replaced by a single cross-platform `examples/basic.py`.


### High level API
The SDK uses callbacks to implement user functions on the various events. To register a callback, you just have to instance a TapSDK object and:

```python
def on_tap_event(identifier, tapcode):
    print(identifier + " tapped " + str(tapcode))

tap_device.register_tap_events(on_tap_event)
```
#### Commands list
1. ```set_input_mode(self, input_mode:InputMode, identifier=None):```
This function sends a mode selection command. It accepts an object of type ```InputMode``` such as ```InputModeText```, ```InputModeController```, ```InputModeControllerText```, or ```InputModeRaw```.  
For example:
    ```python
    from tapsdk import InputModeController
    await tap_device.set_input_mode(InputModeController())
    ```  
    For raw sensors mode, you can specify sensitivity and scaling:
    ```python
    from tapsdk import InputModeRaw
    from tapsdk.enumerations import FingerAcclSensitivity, ImuGyroSensitivity, ImuAcclSensitivity
    await tap_device.set_input_mode(InputModeRaw(
        scaled=True,
        finger_accl_sens=FingerAcclSensitivity.G4,
        imu_gyro_sens=ImuGyroSensitivity.DPS250,
        imu_accl_sens=ImuAcclSensitivity.G4
    ))
    ```
2. ```set_input_type(self, input_type:InputType, identifier=None):```   
    > **Only for TapXR and with Spatial Control experimental firmware**

    This function sends a command to force input type. It accepts an enum of type ```InputType``` initialized with any of the types ```InputType.MOUSE```, ```InputType.KEYBOARD```, or ```InputType.AUTO```.  
    For example:
    ```python
    from tapsdk import InputType
    await tap_device.set_input_type(InputType.AUTO)
    ```  
    This will set the input to be automatically selected by the Tap device, based on hand posture.

3. ```send_vibration_sequence(self, sequence:list, identifier=None):```
This function sends a series of haptic activations. ```sequence``` is a list of integers indicating the activation and delay periods one after another. The periods are in millisecond units, in the range of [10,2550] and in resolution of 10ms. Each haptic command supports up to 18 period definitions (i.e. 9 haptics + delay pairs).  
For example: 
    ```python 
    await tap_device.send_vibration_sequence(sequence=[1000,300,200])
    ```  
    will trigger a 1s haptic, followed by 300ms delay, followed by 200ms haptic.


#### Events list
1. ```register_connection_events(self, listener:Callable):```  
Register callback to a Tap strap connection event.
    ```python
    def on_connect(tap_sdk_instance):
        print("Connected to Tap device")

    tap_device.register_connection_events(on_connect)
    ``` 

2. ```register_disconnection_events(self, listener:Callable):```  
Register callback to a Tap strap disconnection event.
    ```python
    def on_disconnect(client):
        print("Tap device disconnected")

    tap_device.register_disconnection_events(on_disconnect)
    ``` 

3. ```register_tap_events(self, listener:Callable):```  
Register callback to a tap event.
    ```python
    def on_tap_event(identifier, tapcode):
        print(identifier + " - tapped " + str(tapcode))

    tap_device.register_tap_events(on_tap_event)
    ```    
    ```tapcode``` is an 8-bit unsigned number, between 1 and 31 which is formed by a binary representation of the fingers that are tapped.
The LSb is thumb finger, the MSb is the pinky finger. 
For example: if combination equals 5 - its binary form is 10100 - means that the thumb and the middle fingers were tapped.


4. ```register_mouse_events(self, listener:Callable):```  
Register callback to a mouse or air mouse movement event.
    ```python
    def on_mouse_event(identifier, vx, vy, proximity):
        print(identifier + " - moused: %d, %d" %(vx, vy))

    tap_device.register_mouse_events(on_mouse_event)
    ``` 
    ```vx``` and ```vy``` are the horizontal and vertical velocities of the mouse movement respectively.
```proximity``` is a boolean that indicates proximity with a surface.
5. ```register_raw_data_events(self, listener:Callable):```  
Register callback to raw sensors data packet received event.
    ```python
    def on_raw_sensor_data(identifier, packets):
        for packet in packets:
            print(identifier, packet["type"], packet["ts"], packet["payload"])

    tap_device.register_raw_data_events(on_raw_sensor_data)
    ``` 
    The callback receives a list of dicts, each with keys `type` (`"imu"` or `"accl"`), `ts` (millisecond timestamp), and `payload` (list of sample values). When `InputModeRaw(scaled=True)` is active, values are in mg and mdps.
    You'll find more information on that mode in the dedicated section below or [here](https://tapwithus.atlassian.net/wiki/spaces/TD/pages/792002574/Tap+Strap+Raw+Sensors+Mode).

6. ```register_air_gesture_events(self, listener:Callable):```  
Register callback to air gesture events.
    ```python
    from tapsdk import AirGestures

    def on_airgesture(identifier, gesture):
        print(identifier + " - gesture: " + str(AirGestures(gesture)))

    tap_device.register_air_gesture_events(on_airgesture)
    ``` 
    ```gesture``` is an integer code of the air gesture detected. The air gesture values are enumerated in the ```AirGestures``` class, including directional gestures (`UP_ONE_FINGER`, `PINCH`, etc.), thumb gestures (`THUMB_FINGER`, `THUMB_MIDDLE`), and spatial state gestures (`STATE_OPEN`, `STATE_FIST`, etc.).

7. ```register_air_gesture_state_events(self, listener:Callable):```  
Register callback to mouse-mode state changes (e.g. air mouse, optical mouse).
    ```python
    from tapsdk.enumerations import MouseModes

    def on_mouse_mode_change(identifier, mouse_mode):
        print(identifier + " - mode: " + str(mouse_mode))

    tap_device.register_air_gesture_state_events(on_mouse_mode_change)
    ``` 
    ```mouse_mode``` is a ```MouseModes``` enum value: `STDBY`, `AIR_MOUSE`, `OPTICAL1`, or `OPTICAL2`.

### Raw sensors mode

**Make sure that "Developer mode" is enabled on TapManager app for this mode to work properly**

In raw sensors mode, the Tap device continuously sends raw data from the following sensors:
1. Five 3-axis accelerometers - one per each finger (**available only on TAP Strap and Tap Strap 2**).
    * sampled at 200Hz
    * allows dynamic range configuration (±2G, ±4G, ±8G, ±16G)
2. IMU (3-axis accelerometer + gyro) located on the thumb (**available on TAP Strap 2 and TapXR**).
    * sampled at 208Hz. 
    * allows dynamic range configuration for the accelerometer (±2G, ±4G, ±8G, ±16G) and for the gyro (±125dps, ±250dps, ±500dps, ±1000dps, ±2000dps).

The sensors measurements are given with respect to the reference system below.

![alt text](TAP-axis-alpha.png "Tap Strap reference frame")
![alt text](TAPXR-axis.png "TapXR reference frame")

Each sample (of accelerometer or imu) is preambled with a millisecond timestamp, referenced to an internal Tap clock.


The dynamic range of the sensors is determined with the ```set_input_mode``` method by passing an ```InputModeRaw``` instance with the desired sensitivity enums, and a boolean flag indicating if the data should be scaled to mg and mdps for the accelerometer and gyro respectively:
```python
from tapsdk import InputModeRaw
from tapsdk.enumerations import FingerAcclSensitivity, ImuGyroSensitivity, ImuAcclSensitivity

await tap_device.set_input_mode(InputModeRaw(
    scaled=True,
    finger_accl_sens=FingerAcclSensitivity.G4,
    imu_gyro_sens=ImuGyroSensitivity.DPS250,
    imu_accl_sens=ImuAcclSensitivity.G4
))
```
Refer to `FingerAcclSensitivity`, `ImuGyroSensitivity`, and `ImuAcclSensitivity` in [`tapsdk.enumerations`](tapsdk/enumerations.py) for the available sensitivity values.

### Examples

You can find some examples in the [examples folder](examples).

### Testing

To run the tests, first install the development dependencies:

```bash
pip install .[dev]
```

Then run the tests using pytest:

```bash
pytest
```


### Known Issues
See [History.md](History.md) for release notes. No known issues at 0.7.0.

### Support

Please refer to the issues tab! :)

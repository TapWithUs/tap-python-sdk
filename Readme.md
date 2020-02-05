## TapStrap Python SDK

### What Is This ?

TAP python SDK allows you to build python app that can establish BLE connection with the Tap Strap, send commands and receive  events and data - Thus allowing TAP to act as a controller for your app!


### Compatibility


### Installation

#### Windows
The Windows BLE backend is actually a wrapper to the dynamic library compiled from windows SDK from 

Download/clone the repo and install it.
```console
    git clone https://github.com/TapWithUs/tap-python-sdk
    cd tap-python-sdk
    python setup.py install
```

Then just import tapsdk into your source code:
```python
    from tapsdk import TapSDK

    tap_device = TapSDK()
```

### Features

This SDK implements two basic interfaces with the Tap Strap.
First is setting the operation mode of the Tap strap:

1. **Text mode** - the strap will operate normally, with no events being sent to the SDK.
2. **Controller mode** - the strap will send events to the SDK
3. **Raw data mode** - the strap will just send raw sensors data to the SDK

Second, subscribing to the following Tap events:

1. **Tap event** - whenever a tap event has occured
2. **Mouse event** - whenever a mouse movement has occured
3. **AirGesture event** - for 3D gestures
4. **Raw data** - stream of raw data

TAPKit uses delegates to call the neccessary functions, and supports multiple delegates.

To add a delegate, you must implement TAPKitDelegate protocol.
Functions available (all optional) in TAPKitDelegate:



### centralBluetoothState(poweredOn:Bool)

Called whenever bluetooth state is changed. You can use this function to alert the user for example.


### tapConnected(withIdentifier identifier: String, name: String)

Called when a TAP device is connected to the iOS device, sending the TAP identifier and it's display name.
Each TAP device has an identifier (a unique string) to allow you to keep track of all the taps that are connected
(if for example you're developing a multiplayer game, you need to keep track of the players).
This identifier is used in the rest of the TAPKitDelegate functions.
* TAPKit does NOT scan for TAP devices, therefor the use must pair the devices to the iOS device first.


### tapDisconnected(withIdentifier identifier: String)

Called when a TAP device is disconnected from the iOS device, sending the TAP identifier.



### tapFailedToConnect(withIdentifier identifier: String, name: String)

Called when a TAP device failed to connect, sending the TAP identifier and it's display name.


### tapped(identifier: String, combination: UInt8)

This is where magic will happen.
This function will tell you which TAP was being tapped (identifier:String), and which fingers are tapped (combination:UInt8)
Combination is a 8-bit unsigned number, between 1 and 31.
It's binary form represents the fingers that are tapped.
The LSB is thumb finger, the MSB (bit number 5) is the pinky finger.
For example: if combination equls 3 - it's binary form is 00101,
Which means that the thumb and the middle fingers are tapped.
For your convenience, you can convert the binary format into fingers boolean array (explanation follows)

### moused(identifier:String, velocityX:Int16, velocityY:Int16, isMouse:Bool)

This function will be called when the user is using the TAP as a mouse.
velocityX and velocityY are the velocities of the mouse movement. These values can be multiplied by a constant to simulate "mouse sensitivity" option.
isMouse is a boolean that determine if the movement is real (true) or falsely detected by the TAP (false).

## Adding a TAPKitDelegate :

If your class implements TAPKitDelegate, you can tell TAPKit to add the class as a delegate, thus allowing your class to receive the above callbacks. To do so:

```swift
    TAPKit.sharedKit.addDelegate(self)
```

After you added your class as a delegate, you need to call the "start" function.
The "start" function should be called once, usually in the main screen where you need the tapConnected callback.

```swift
    TAPKit.sharedKit.start()
```

## Removing a TAPKitDelegate

If you no longer need the callbacks, you can remove your class as a TAPKitDelegate:

```swift
    TAPKit.sharedKit.removeDelegate(self)
```

## Converting a binary combination to fingers array

As said before, the tapped combination is an unsigned 8-bit integer. to convert it to array of booleans:

```swift
    let fingers = TAPCombination.toFingers(combination)
```

While:
fingers[0] indicates if the thumb is being tapped.
fingers[1] indicates if the index finger is being tapped.
fingers[2] indicates if the middle finger is being tapped.
fingers[3] indicates if the ring finger is being tapped.
fingers[4] indicates if the pinky finger is being tapped.


## Get the connected TAPS

If you wish at any point in your app, as long as TAPKit has been started, you can receive a dictionary of connected taps.

```swift
    let taps = TAPKit.sharedKit.getConnectedTaps()
```
While the result is a dictionary where the key is the tap identifier, and the value is it's display name.


## TAPInputMode

Each TAP has a mode in which it works as.
Two modes available:
CONTROLLER MODE (Default) - allows receiving the "tapped" func callback in TAPKitDelegate with the fingers combination without any post-processing.
TEXT MODE - the TAP device will behave as a plain bluetooth keyboard, "tapped" func in TAPKitDelegate will not be called.

When a TAP device is connected it is by default set to controller mode.

If you wish for a TAP to act as a bluetooth keyboard and allow the user to enter text input in your app, you can set the mode:

```swift
    TAPKit.sharedKit.setTAPInputMode(TAPInputMode.text, forIdentifiers: [String])
```

The first parameter is the mode. You can use any of these modes: TAPInputMode.controller, TAPInputMode.text
the second parameter is an array of identifiers of TAP devices that you want to change the mode. You can pass nil if you want ALL the TAP devices to change their mode.

Just don't forget to switch back to controller mode after the user has entered the text :

```swift
TAPKit.sharedKit.setTAPInputMode(TAPInputMode.controller, forIdentifiers: [String])
```

You can ask TAPKit which mode a specific TAP device is in.
The result is a string, which can be compared to TAPInputMode.text or TAPInputMode.controller :

```swift
    let mode = TAPKit.sharedKit.getTAPInputMode(forTapIdentifier: identifier)
    if mode == TAPInputMode.controller {

    } else if mode == TAPInputMode.text {

    }
```

## Logging

TAPKit has a log, which logs all the events that happens. This can be useful for debugging, or should be attached when reporting a bug :)

There are 4 types of events:

```swift
    @objc public enum TAPKitLogEvent : Int {
        case warning = 0
        case error = 1
        case info = 2
        case fatal = 3
    }
```

To enable logging of all the events:

```swift
    TAPKit.log.enableAllEvents()
```

To disable logging of all the events:

```swift
    TAPKit.log.disableAllEvents()
```

To enable a specific event, errors for example:

```swift
    TAPKit.log.enable(event: .error)
```

And to disable a spcific event, warnings for example:

```swift
    TAPKit.log.disable(event: .warning)
```

### Examples

The xcode project contains an example app where you can see how to use the features of TAPKit.

### Support

Please refer to the issues tab! :)






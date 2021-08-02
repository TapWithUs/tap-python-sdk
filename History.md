# History
## 0.5.0 (2021-08-03)
______________________
### Main features

* Support Bleak 0.12.1 for mac

### Known Issues
* Windows backend -  
    * Raw sensor data rate might be lower than expected.
    * Sometimes a Tap strap wouldn't be detected upon connection. In this case try restarting your Tap and/or the Python application. In worst case scenario re-pair your Tap. 
* MacOS & Linux backends - 
    * Doesn't support multiple Tap strap connections.
    * OnConnect and OnDisconnect events are not implemented 
    * Raw sensor data is given unscaled (i.e. unitless), thereforein order to scale to physical units need to multiply by the relevant scale factor

## 0.3.0 (2020-09-07)
______________________
### Main features

* Linux support
* Some bug fixes

## 0.2.0 (2020-02-22)
______________________
### Main features

* Added dll to enable windows backend.
* fix parsers output types on gesture and tap messages

## 0.1.0 (2020-02-20)
______________________
### Main features

* SDK created.



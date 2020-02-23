# History


## 0.2.0 (2020-02-22)
______________________
### Main features

* Added dll to enable windows backend.
* fix parsers output types on gesture and tap messages

### Known Issues
* Windows backend -  
    * Raw sensor data rate might be lower than expected.
    * Sometimes a Tap strap wouldn't be detected upon connection. In this case try restarting your Tap and/or the Python application. In worst case scenario re-pair your Tap. 
* MacOS backend - 
    * Doesn't support multiple Tap strap connections.
    * OnConnect and OnDisconnect events are not implemented 
    * Raw sensor data is given unscaled (i.e. unitless), thereforein order to scale to physical units need to multiply by the relevant scale factor


## 0.1.0 (2020-02-20)
______________________
### Main features

* SDK created.



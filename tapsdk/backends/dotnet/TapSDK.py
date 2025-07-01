import clr
from ...TapSDK import TapSDKBase
from .inputmodes import TapInputMode
import System

clr.AddReference(r"tapsdk/backends/dotnet/TAPWin")
from TAPWin import TAPManager
from TAPWin import TAPManagerLog
from TAPWin import TAPInputMode
from TAPWin import RawSensorSensitivity
from TAPWin import TAPAirGesture
from TAPWin import RawSensorData


class TapWindowsSDK(TapSDKBase):
    def __init__(self, *args):
        super().__init__()
        TAPManagerLog.Instance.OnLineLogged += print

    def register_tap_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapped += listener

    def register_mouse_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnMoused += listener

    def register_connection_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapConnected += listener

    def register_disconnection_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnTapDisconnected += listener

    def register_raw_data_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnRawSensorDataReceieved += listener

    def register_air_gesture_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnAirGestured += listener

    def register_air_gesture_state_events(self, listener=None):
        if listener is not None:
            TAPManager.Instance.OnChangedAirGestureState += listener

    def set_input_mode(self, mode:TapInputMode, tap_identifier=""):
        print("input mode: " + mode.get_name())
        TAPManager.Instance.SetTapInputMode(mode.get_object(), tap_identifier)

    def set_default_input_mode(self, mode, identifier=""):
        set_all = False
        if identifier == "":
            set_all = True
        mode_obj = TapInputMode(mode).get_object()
        TAPManager.Instance.SetDefaultInputMode(mode_obj, set_all)

    def send_vibration_sequence(self, sequence:list, identifier):
        vibrations_array = System.Array[int](sequence)
        TAPManager.Instance.Vibrate(vibrations_array, identifier)

    def run(self):
        self.set_default_input_mode("controller")
        TAPManager.Instance.Start()

    async def list_connected_taps(self):
        """
        Get a list of currently connected TAP devices.
        Returns a list of TAP device identifiers.
        
        This method attempts to retrieve connected TAP devices from the TAPManager.
        If the TAPManager doesn't expose the expected methods, it will return an empty list.
        """
        try:
            # Try to get connected taps from the TAPManager
            # The exact method name may vary depending on the TAPWin DLL version
            if hasattr(TAPManager.Instance, 'GetConnectedTaps'):
                connected_taps = TAPManager.Instance.GetConnectedTaps()
                if connected_taps is not None:
                    # Convert .NET collection to Python list
                    return list(connected_taps)
            elif hasattr(TAPManager.Instance, 'GetConnectedDevices'):
                connected_devices = TAPManager.Instance.GetConnectedDevices()
                if connected_devices is not None:
                    return list(connected_devices)
            elif hasattr(TAPManager.Instance, 'ConnectedTaps'):
                # Try accessing as a property
                connected_taps = TAPManager.Instance.ConnectedTaps
                if connected_taps is not None:
                    return list(connected_taps)
            elif hasattr(TAPManager.Instance, 'ConnectedDevices'):
                # Try accessing as a property
                connected_devices = TAPManager.Instance.ConnectedDevices
                if connected_devices is not None:
                    return list(connected_devices)
            else:
                # Log that the method is not available in this version of TAPWin
                print("Warning: TAPManager does not expose connected device enumeration methods")
                return []
        except Exception as e:
            # Handle any other exceptions that might occur
            print(f"Error retrieving connected TAP devices: {e}")
            return []
        
        # If we reach here, no method was found or all returned None
        return []




from unittest.mock import MagicMock

from tapsdk.enumerations import MouseModes
from tapsdk.tap import TapSDK


def _sdk():
    sdk = TapSDK.__new__(TapSDK)
    sdk.mouse_mode = MouseModes.STDBY
    sdk.tap_event_cb = MagicMock()
    sdk.air_gesture_event_cb = MagicMock()
    sdk.air_gesture_state_event_cb = None
    return sdk


def test_standby_delivers_tap_events():
    sdk = _sdk()
    sdk.on_tapped("id", bytearray([3, 0, 0, 0]))
    sdk.tap_event_cb.assert_called_once_with("id", 3)


def test_air_mouse_maps_click_taps_to_gestures_only():
    sdk = _sdk()
    sdk.mouse_mode = MouseModes.AIR_MOUSE
    sdk.on_tapped("id", bytearray([2, 0, 0, 0]))
    sdk.tap_event_cb.assert_not_called()
    sdk.air_gesture_event_cb.assert_called_once_with("id", 12)


def test_air_mouse_still_delivers_non_click_taps():
    sdk = _sdk()
    sdk.mouse_mode = MouseModes.AIR_MOUSE
    sdk.on_tapped("id", bytearray([1, 0, 0, 0]))
    sdk.tap_event_cb.assert_called_once_with("id", 1)
    sdk.air_gesture_event_cb.assert_not_called()

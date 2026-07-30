# Release notes

Changelog for published `tap-python-sdk` releases on PyPI.

Add user-facing changes for the next release under **Unreleased** in your pull
request. At release time `scripts/prepare_release.py` renames this section to the
new version and opens a fresh empty one.

## Unreleased
______________________
### Main features

* Versioned docs site (mike) deployed after successful PyPI publish, with a release notes page derived from `docs/release-notes.md` (#47) (#48)
* Prep-commit-then-tag release flow: author-written `Unreleased` entries, `scripts/prepare_release.py`, and a verify-only publish pipeline (#47) (#48)
* Shared reusable test workflow used by CI and Publish (#39) (#48)

### Bug fixes

## 0.7.0 (2026-06-09)
______________________
### Main features

* Unified cross-platform implementation in `tapsdk/tap.py` (removed separate posix/dotnet backends).
* Windows rewritten to use Bleak/WinRT instead of TAPWin.dll.
* `InputMode` API: `TapInputMode("…")` replaced by `InputModeText`, `InputModeController`, `InputModeControllerText`, `InputModeRaw`.
* Raw mode: typed sensitivity enums and optional scaling to mg/mdps (`scaled=True`).
* Connection and disconnection events implemented on all platforms.
* Windows: BLE scan and reconnect polling for paired devices.
* Python requirement raised to 3.9+.
* CI: cross-platform pytest and flake8.
* New `AirGestures` values (thumb and state gestures).

### Breaking changes

* Removed `TapInputMode`, `loop` constructor argument, `tapsdk.models`, and OS-specific examples.
* Windows no longer uses bundled TAPWin.dll.

## 0.6.0 (2024-07-04)
______________________
### Main features

* Added Spatial features for TapXR.
* Mac and Linux backends unified to posix backend.

### Known Issues
* Windows backend -
    * Raw sensor data rate might be lower than expected.
    * Sometimes a Tap strap wouldn't be detected upon connection. In this case try restarting your Tap and/or the Python application. In worst case scenario re-pair your Tap.
    * Spatial features are still not available for Windows backend.
* MacOS & Linux backends -
    * Doesn't support multiple Tap strap connections.
    * OnConnect and OnDisconnect events are not implemented
    * Raw sensor data is given unscaled (i.e. unitless), therefore in order to scale to physical units need to multiply by the relevant scale factor

## 0.5.1 (2024-01-01)
______________________
### Main features

* Support TapXR Air Gesture pinch

## 0.5.0 (2021-08-03)
______________________
### Main features

* Support Bleak 0.12.1 for mac

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

# AGENTS.md — Tap Python SDK (app builders)

Short guide for coding agents that build apps with this SDK. Full skill:
[`.cursor/skills/tap-python-sdk/SKILL.md`](.cursor/skills/tap-python-sdk/SKILL.md)
(Claude twin: [`.claude/skills/tap-python-sdk/SKILL.md`](.claude/skills/tap-python-sdk/SKILL.md)).

## When to use

Use when the user builds a **Python host app** that connects to a Tap over BLE
and needs tap / mouse / air-gesture / sensor callbacks.

## Package

| | |
|--|--|
| PyPI | `tap-python-sdk` (0.9.x) |
| Import | `tapsdk` |
| Python | ≥ 3.10 |
| Hardware (documented) | **Tap Strap** / Strap 2, **TapXR** |
| Not first-run | **TapBand** — [waitlist](https://www.tapwithus.com/tapband-waitlist/); XR gestures are a subset of Band — do not invent a missing-gesture list |

## Install

```bash
pip install tap-python-sdk
```

## Connect order (happy path)

1. **Pair in OS Bluetooth** (macOS / Windows / Linux). SDKs do **not** scan for unpaired devices.
2. `sdk = await connect()` → `TapSDK` (v1) or `TapSDK2` (v2).
3. Register callbacks (`register_tap_events`, …).
4. `await sdk.start()`.
5. **Unlock taps** (required — Text/HID mode is silent):
   - **v1:** `await sdk.set_input_mode(InputModeController())`
   - **v2:** `await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)`
6. Keep the event loop alive (`await asyncio.Event().wait()`).

Portal: [Getting started](https://dev.tapwithus.com/docs/getting-started/) ·
[How Tap works](https://dev.tapwithus.com/docs/how-tap-works/).
In-repo sample: [`examples/connect.py`](examples/connect.py).

## Controller vs Text

| Mode | Effect |
|------|--------|
| **Text** (boot default) | HID keyboard — **zero** SDK tap callbacks |
| **Controller** (v1) | App receives finger bitmasks |
| **MODEL_DETECTION** (v2) | App receives model/tap events (no `set_input_mode` on v2) |

## Tapcode bitmask

Values **1–31**. bit0 = thumb … bit4 = pinky. Example: `5` → `0b00101` → thumb + middle.
On v2, `tapcode` is often a one-element list `[n]`.

## Zero events — top causes

1. Still in Text mode / forgot Controller or MODEL_DETECTION after `start()`.
2. Device not paired in OS Bluetooth.
3. Process exited — no keep-alive wait loop.
4. Wrong protocol path (v1 APIs on v2 or vice versa).
5. Tap off / firmware not updated (Tap Manager).

## Do not invent

- No GATT UUIDs or gesture tables beyond published docs.
- **Spatial Control** (`set_input_type`) = authorized TapXR / **v1 only** — not on `TapSDK2`. Out of scope for first-run.
- Do not treat TapBand as a documented public first-run target.

## More docs

- Hosted: https://tapwithus.github.io/tap-python-sdk/
- v1 tutorial: `docs/v1/tutorial/getting-started.md`
- v2 tutorial: `docs/v2/tutorial/getting-started.md`

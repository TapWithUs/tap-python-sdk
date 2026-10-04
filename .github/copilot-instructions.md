# Tap Python SDK — AI instructions (GitHub Copilot)

> Portal Getting started: https://dev.tapwithus.com/docs/getting-started/  
> Hosted docs: https://tapwithus.github.io/tap-python-sdk/  
> LLM index: https://dev.tapwithus.com/llms.txt  
> In-repo brief: [`AGENTS.md`](../AGENTS.md) · skill: [`.cursor/skills/tap-python-sdk/SKILL.md`](../.cursor/skills/tap-python-sdk/SKILL.md)

Package **`tap-python-sdk`** on PyPI; import **`tapsdk`**. Python ≥ 3.10.

## Happy path (required)

1. **Pair in OS Bluetooth first.** SDKs do **not** scan for unpaired devices.
2. `sdk = await connect()` → register callbacks → `await sdk.start()`.
3. Unlock taps (Text/HID boot mode is **silent** — zero SDK tap callbacks):
   - **v1:** `await sdk.set_input_mode(InputModeController())`
   - **v2:** `await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)`
4. Keep the asyncio loop alive.

## Bitmask

Tap codes **1–31**: bit0 = thumb … bit4 = pinky.

## Hardware honesty

- Documented SDK targets: **Tap Strap** / Strap 2 and **TapXR**.
- **TapBand** is **not** a public first-run target — https://www.tapwithus.com/tapband-waitlist/
- XR gestures are a subset of Band; do not invent a missing-gesture list.

## Footguns

- **Spatial Control** (`set_input_type`) = authorized TapXR / **v1 only** — **not** on `TapSDK2`. Out of scope for first-run.
- Do **not** invent GATT UUIDs, gesture tables, or undocumented APIs.

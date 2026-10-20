## Tap Python SDK

[![PyPI version](https://img.shields.io/pypi/v/tap-python-sdk.svg)](https://pypi.org/project/tap-python-sdk/)

BLE SDK for Python apps that connect to **Tap Strap**, **Tap Strap 2**, **TapXR**, and **TapBand**. Send commands and receive tap, mouse, air-gesture, and raw sensor events.

**Python 3.10+** · **macOS / Windows / Linux**

TapBand uses the same BLE API as TapXR and is coming soon. It is not for sale yet. Join the [TapBand waitlist](https://www.tapwithus.com/tapband-waitlist/).

### Documentation

Published docs (MkDocs Material, versioned with mike): [https://tapwithus.github.io/tap-python-sdk/](https://tapwithus.github.io/tap-python-sdk/)

| I want to… | Go to |
|------------|--------|
| First connect (Tap Strap and TapXR) | [Docs home](docs/index.md) |
| Input modes (`TapSDK`) | [TapSDK](docs/v1/index.md) |
| Features and air gestures (`TapSDK2`) | [TapSDK2](docs/v2/index.md) |
| Install the package | [Install the SDK](docs/how-to/install.md) |
| Read the changelog | [Release notes](docs/release-notes.md) |

Full index: [docs/index.md](docs/index.md). Local preview: `pip install -r requirements-docs.txt && mkdocs serve`.

### Install

```console
pip install tap-python-sdk
```

Requires **Python 3.10 or newer**. PyPI name: `tap-python-sdk`. Import name: `tapsdk` (`from tapsdk import connect`). Platform notes (BlueZ on Linux, Bleak 3.x, pairing): [Install the SDK](docs/how-to/install.md).

### Quick start

One path for Tap Strap and TapXR. Pair the Tap in OS Bluetooth settings, then run:

```python
import asyncio
from tapsdk import (
    DeviceFeatures,
    InputModeController,
    ModelTypes,
    VisionSensorOpModes,
    connect,
)


def on_tap(identifier, tapcode):
    # tapcode is int 1..31 — bit0=thumb … bit4=pinky
    code = tapcode[0] if isinstance(tapcode, (list, tuple)) else tapcode
    print(f"{identifier} tapped {code} (0b{int(code):05b})")


async def main():
    sdk = await connect()
    sdk.register_tap_events(on_tap)
    await sdk.start()
    if hasattr(sdk, "set_input_mode"):
        await sdk.set_input_mode(InputModeController())
    else:
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
        await sdk.set_vision_sensor_model(ModelTypes.TAPPING)
        await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)

    print("Waiting for taps… (Ctrl+C to quit)")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
```

The script switches the Tap out of keyboard mode. Call that enable step after `start()`, or you get no tap events.

Turn the Tap on. Update firmware with Tap Manager. `connect()` attaches and returns `TapSDK` or `TapSDK2` from the firmware. You do not pick a protocol. More: [`examples/connect.py`](examples/connect.py).

### Air gestures (raw swipes, pinches, fist)

Python, Web, iOS, and Android all receive the **raw** gesture detections from the sensor. In Python that is `register_air_gesture_events`. iOS and Android also add a processed layer (click, drag, drop with debounce). Swipes and pinches are not iOS/Android-only.

The TapXR developer firmware (and TapBand, same BLE API) supports the full set: taps, thumb swipes up/down/left/right, thumb-to-finger pinches with hold, and fist with hold. Codes match `UnifiedAirGestures`.

```python
import asyncio
from tapsdk import (
    DeviceFeatures,
    ModelTypes,
    UnifiedAirGestures,
    VisionSensorOpModes,
    connect,
)


def first(value):
    return value[0] if isinstance(value, (list, tuple)) else value


def on_air_gesture(identifier, data):
    gesture = UnifiedAirGestures(int(first(data)))
    print(identifier, gesture.name)


async def main():
    sdk = await connect()
    sdk.register_air_gesture_events(on_air_gesture)
    await sdk.start()
    if hasattr(sdk, "set_feature"):
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
        await sdk.set_vision_sensor_model(ModelTypes.AIR_GESTURE)
        await sdk.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)
    print("Swipe, pinch, or make a fist. Ctrl+C to quit.")
    await asyncio.Event().wait()


asyncio.run(main())
```

| `UnifiedAirGestures` | Meaning |
|----------------------|---------|
| `COMBINED_GESTURE_LEFT` / `RIGHT` / `UP` / `DOWN` | Thumb swipe |
| `COMBINED_GESTURE_AB` … `AE` | Short pinch (thumb + index / middle / ring / pinky) |
| `COMBINED_GESTURE_AB_HOLD` … `AE_HOLD` | Pinch held |
| `COMBINED_GESTURE_FIST` / `FIST_HOLD` | Fist / fist held |
| `COMBINED_GESTURE_NONE` | Hand relaxed (use as release after a hold) |

Tap Strap and Tap Strap 2 in Controller mode report `AirGestures` on the same callback (`UP_ONE_FINGER`, `PINCH`, `STATE_FIST`, and related codes). Normalize the payload with `first()` on every device.

### AI-Assisted Development

You do not need to be a developer to build with a Tap. Install the Tap skills into your coding agent, then describe the app you want in plain words. The agent knows how to connect, which events each device sends, and how to build common interactions.

The installer writes into the **current folder**. Add `-g` to install for your user instead, so the skills are available in every project.

| Tool | This folder (default) | Every project (`-g`) |
|------|------------------------|----------------------|
| Claude Code | `.claude/skills/` | `claude plugin install … --scope user` |
| Codex | `.agents/skills/` | `codex plugin add …` |
| Cursor | `.cursor/skills/` + [`.cursor/rules/tap-sdk.mdc`](.cursor/rules/tap-sdk.mdc) | `~/.cursor/skills/` + `~/.cursor/rules/tap-sdk.mdc` |
| Any agent that reads `AGENTS.md` | [`AGENTS.md`](AGENTS.md) | `~/.codex/AGENTS.md` |

Run the commands below in your project folder.

#### This folder

```console
./install-skills.sh claude    # .claude/skills/
./install-skills.sh codex     # .agents/skills/
./install-skills.sh cursor    # .cursor/skills/ and .cursor/rules/
./install-skills.sh agents    # ./AGENTS.md
./install-skills.sh all       # all four, this folder
./install-skills.sh -g all    # all four, every project
```

Or, without a clone:

```console
curl -sL https://raw.githubusercontent.com/TapWithUs/tap-python-sdk/master/install-skills.sh | bash -s cursor
curl -sL https://raw.githubusercontent.com/TapWithUs/tap-python-sdk/master/install-skills.sh | bash
curl -sL https://raw.githubusercontent.com/TapWithUs/tap-python-sdk/master/install-skills.sh | bash -s -- -g all
```

#### Every project

```console
./install-skills.sh -g claude
./install-skills.sh -g codex
./install-skills.sh -g cursor
./install-skills.sh -g agents
./install-skills.sh -g all
```

`-g claude` and `-g codex` need the `claude` and `codex` commands. You can also open `/plugins` in Codex and install **Tap Python SDK** from the marketplace list.

#### What's included

- **tap-getting-started**: install, pairing, connect to any Tap, quickstart script, troubleshooting
- **tap-tapping**: which fingers tapped, finger combos, double taps, keyboard shortcuts, haptics
- **tap-vision-models**: tapping vs air-gesture model; swipes, pinches, holds, fist
- **tap-imu-motion**: pointer movement, tilt, roll / pitch / yaw, and mouse events
- **tap-raw-sensors**: raw accelerometer and gyro streams, sensitivity, CSV logging
- **tap-knob**: hold a pinch and twist to turn a value up or down (TapXR developer firmware / TapBand)
- **tap-dpad**: swipe for directions, pinch to select, hold to rotate or drag (TapXR developer firmware / TapBand)
- **tap-build-an-app**: turn Tap events into a complete app: browser page, game, keyboard control

#### Onboard your agent

1. Make an empty folder for your project and open your coding agent in it.
2. Install the skills (see above).
3. Turn on your Tap, charge it, pair it in your computer's Bluetooth settings, and update its firmware with Tap Manager.
4. Tell the agent which device you have (Tap Strap, Tap Strap 2, or TapXR) and which computer (macOS, Windows, or Linux). TapBand uses the same API as TapXR and is coming soon.
5. Ask it to connect first: *"Use the tap-getting-started skill to connect to my Tap and show my taps."* Tap your fingers and tell the agent what you see.
6. When taps arrive, describe your app. Build one interaction at a time and try each one with the device.
7. If something does not work, tell the agent exactly what happened (for example "nothing prints when I tap" or "letters appear in my editor"). It can use the troubleshooting table in `tap-getting-started`.

#### Sample prompts

- "Connect to my Tap and print which fingers I tap."
- "Make a presentation clicker: index finger = next slide, middle finger = previous slide, buzz on each tap."
- "Map my tap combos to keyboard shortcuts for my video editor."
- "Make a volume knob: hold a pinch and twist my wrist to change the system volume."
- "Build a browser D-Pad game: swipe to move, pinch to pick a shape, hold and twist to rotate it."
- "Show a cursor on a web page that follows my hand motion, and click with a pinch."
- "Switch between the tapping model and the air-gesture model when I make a fist."
- "Record 30 seconds of raw IMU data to CSV and plot it."
- "Build a drum machine: each finger plays a different drum sound."

### Features (summary)

- **Connect:** `await connect()` attaches and returns `TapSDK` or `TapSDK2` from firmware
- **Input modes** (`TapSDK`): Text, Controller, Controller+Text, Raw sensors — [TapSDK how-tos](docs/v1/how-to/index.md)
- **Features** (`TapSDK2`): `DeviceFeatures`, vision model/op-mode, IMU motion/raw, standby — [TapSDK2 how-tos](docs/v2/how-to/index.md)
- **Events:** tap, mouse, air gesture (raw detections), raw / IMU packets, connect/disconnect
- **Commands:** set mode / features, Spatial Control input type (TapXR), haptic sequences
- **Spatial Control** (authorized TapXR builds): [Use Spatial Control](docs/v1/how-to/use-spatial-control.md)

### Migrating from 0.6.x

Breaking API changes for `TapSDK` are listed in [Migrate from 0.6](docs/v1/how-to/migrate-from-0.6.md) and [Release notes](docs/release-notes.md).

### Contributing

Every pull request should add a user-facing entry under the **Unreleased**
heading in [Release notes](docs/release-notes.md). PRs with no user-facing change
(CI, refactors, typo fixes) can skip this by adding the `skip-changelog` label.

### Releasing

Releases use a prep-commit-then-tag flow so the tag, PyPI artifact, and docs all
match:

```bash
python scripts/prepare_release.py X.Y.Z   # bumps version, cuts Unreleased -> X.Y.Z
git add tapsdk/__version__.py docs/release-notes.md
git commit -m "Release X.Y.Z"
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin HEAD vX.Y.Z
```

Pushing the tag runs [`.github/workflows/publish.yml`](.github/workflows/publish.yml),
which re-runs tests, verifies the version and release notes, and publishes to
PyPI. Versioned docs deploy separately after a successful publish. See the header
comments in that workflow for details.

### Testing

```bash
pip install .[dev]
pytest
```

### Support

Use the [GitHub issues](https://github.com/TapWithUs/tap-python-sdk/issues) tab.

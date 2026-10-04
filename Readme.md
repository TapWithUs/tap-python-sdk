## Tap Python SDK (beta)

[![PyPI version](https://img.shields.io/pypi/v/tap-python-sdk.svg)](https://pypi.org/project/tap-python-sdk/)

BLE SDK for building Python apps that connect to **Tap Strap**, **Tap Strap 2**, **TapXR**, and **TapBand**, send commands, and receive tap, mouse, air-gesture, and raw sensor events.

**Python ≥ 3.10** · **macOS / Windows / Linux** · **currently in beta**

### Documentation

Published docs (MkDocs Material, versioned with mike): [https://tapwithus.github.io/tap-python-sdk/](https://tapwithus.github.io/tap-python-sdk/)

Docs are split by BLE protocol. Pick the path that matches your device (or what `connect()` returns):

| I want to… | Go to |
|------------|--------|
| Choose protocol / compare v1 vs v2 | [Docs home](docs/index.md) |
| Start with classic `TapSDK` (v1) | [v1 Getting started](docs/v1/tutorial/getting-started.md) |
| Start with framed `TapSDK2` (v2) | [v2 Getting started](docs/v2/tutorial/getting-started.md) |
| Install the package | [Install the SDK](docs/how-to/install.md) |
| Read the changelog | [Release notes](docs/release-notes.md) |

Full index: [docs/index.md](docs/index.md). Local preview: `pip install -r requirements-docs.txt && mkdocs serve`.

### Install

```console
pip install tap-python-sdk
```

Platform notes (BlueZ on Linux, Bleak 3.x, pairing): [Install the SDK](docs/how-to/install.md).

### Quick example

```python
import asyncio
from tapsdk import TapSDK2, connect

async def main():
    sdk = await connect()  # auto-detects v1 / v2
    sdk.register_tap_events(lambda identifier, tapcode: print(identifier, tapcode))
    await sdk.start()
    print("Protocol:", "v2" if isinstance(sdk, TapSDK2) else "v1")
    await asyncio.Event().wait()

asyncio.run(main())
```

Turn the Tap on. Update firmware with Tap Manager. `connect()` picks `TapSDK` (v1) or `TapSDK2` (v2) from GATT. More: [`examples/connect.py`](examples/connect.py).

### AI-Assisted Development

You do not need to be a developer to build with a Tap. Install the Tap skills into your coding agent, then describe the app you want in plain words. The agent knows how to connect, which events each device sends, and how to build common interactions.

| Tool | What gets installed | Setup |
|------|---------------------|-------|
| Claude Code | Plugin [`plugins/tap-python-sdk/`](plugins/tap-python-sdk/) | Add this repo as a plugin marketplace, then install `tap-python-sdk` |
| Codex | Same plugin | Add this repo as a plugin marketplace, then install `tap-python-sdk` |
| Cursor | Skills in `.cursor/skills/` + rule [`.cursor/rules/tap-sdk.mdc`](.cursor/rules/tap-sdk.mdc) | `install-skills.sh cursor` in your project folder |
| Any agent that reads `AGENTS.md` | [`AGENTS.md`](AGENTS.md) | `install-skills.sh agents` in your project folder |

#### Claude Code

```console
claude plugin marketplace add TapWithUs/tap-python-sdk
claude plugin install tap-python-sdk@tap-python-sdk-marketplace
```

#### Codex

```console
codex plugin marketplace add TapWithUs/tap-python-sdk
codex plugin add tap-python-sdk@tap-python-sdk-marketplace
```

You can also open `/plugins` in Codex and install **Tap Python SDK** from the marketplace list.

#### Cursor

Run this in your project folder:

```console
curl -sL https://raw.githubusercontent.com/TapWithUs/tap-python-sdk/master/install-skills.sh | bash -s cursor
```

#### All at once

Run this in your project folder. It installs the Claude Code and Codex plugins (if those CLIs are installed), plus the Cursor files and `AGENTS.md`:

```console
curl -sL https://raw.githubusercontent.com/TapWithUs/tap-python-sdk/master/install-skills.sh | bash
```

From a clone of this repo: `./install-skills.sh` (menu) or `./install-skills.sh claude|codex|cursor|agents|all`.

#### What's included

- **tap-getting-started**: install, pairing, connect to any Tap (v1 or v2), quickstart script, troubleshooting
- **tap-tapping**: which fingers tapped, finger combos, double taps, keyboard shortcuts, haptics
- **tap-vision-models**: switch between the tapping and air-gesture models; swipes, pinches, holds, fist (v2)
- **tap-imu-motion**: pointer movement, tilt, roll / pitch / yaw (v2) and mouse events (v1)
- **tap-raw-sensors**: raw accelerometer and gyro streams, sensitivity, CSV logging
- **tap-knob**: hold a pinch and twist to turn a value up or down (v2)
- **tap-dpad**: swipe for directions, pinch to select, hold to rotate or drag (v2)
- **tap-build-an-app**: turn Tap events into a complete app: browser page, game, keyboard control

#### Onboard your agent

1. Make an empty folder for your project and open your coding agent in it.
2. Install the skills (see above).
3. Turn on your Tap, charge it, pair it in your computer's Bluetooth settings, and update its firmware with Tap Manager.
4. Tell the agent which device you have (Tap Strap, Tap Strap 2, TapXR, or TapBand) and which computer (macOS, Windows, or Linux).
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

- **Protocols:** v1 (`TapSDK`) and v2 framed (`TapSDK2`); `connect()` auto-detects
- **Modes (v1):** Text, Controller, Controller+Text, Raw sensors — [v1 how-tos](docs/v1/how-to/index.md)
- **Features (v2):** `DeviceFeatures`, vision model/op-mode, IMU motion/raw, standby — [v2 how-tos](docs/v2/how-to/index.md)
- **Events:** tap, mouse, air gesture, raw / IMU packets, connect/disconnect
- **Commands:** set mode / features, Spatial Control input type (TapXR), haptic sequences
- **Spatial Control** (authorized TapXR builds): [Use Spatial Control](docs/v1/how-to/use-spatial-control.md)

### Migrating from 0.6.x

Breaking API changes for v1 (`TapSDK`) are listed in [Migrate from 0.6](docs/v1/how-to/migrate-from-0.6.md) and [Release notes](docs/release-notes.md).

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

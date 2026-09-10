## Tap Python SDK (beta)

[![PyPI version](https://img.shields.io/pypi/v/tap-python-sdk.svg)](https://pypi.org/project/tap-python-sdk/)

BLE SDK for building Python apps that connect to **Tap Strap** / **Tap Strap 2** and **TapXR**, send commands, and receive tap, mouse, air-gesture, and raw sensor events.

**Documented SDK hardware:** Tap Strap and TapXR. **TapBand** has the broadest gestures but is not a public first-run SDK target — [waitlist](https://www.tapwithus.com/tapband-waitlist/).

**Python ≥ 3.10** · **macOS / Windows / Linux** · **currently in beta** · PyPI package `tap-python-sdk`, import `tapsdk`

### Documentation

- **Portal (start here):** [Getting started](https://dev.tapwithus.com/docs/getting-started/) · [How Tap works](https://dev.tapwithus.com/docs/how-tap-works/)
- **App builders / coding agents:** [AGENTS.md](AGENTS.md) · Cursor skill [`.cursor/skills/tap-python-sdk/SKILL.md`](.cursor/skills/tap-python-sdk/SKILL.md)
- **Hosted MkDocs** (versioned with mike): [https://tapwithus.github.io/tap-python-sdk/](https://tapwithus.github.io/tap-python-sdk/)

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

Pair the Tap in **OS Bluetooth settings** first. The SDK attaches to a device the OS already knows — it does not scan for unpaired devices.

Platform notes (BlueZ on Linux, Bleak 3.x, pairing): [Install the SDK](docs/how-to/install.md).

### Quick example

Tap boots in **Text** (HID) mode — you get **zero** tap callbacks until you switch. After `start()`, use **Controller** on v1 or **MODEL_DETECTION** on v2:

```python
import asyncio
from tapsdk import DeviceFeatures, InputModeController, TapSDK2, connect


def on_tap(identifier, tapcode):
    # tapcode is int 1..31 (v1) or [int] (v2) — bit0=thumb … bit4=pinky
    print(identifier, tapcode)


async def main():
    sdk = await connect()  # auto-detects v1 / v2
    sdk.register_tap_events(on_tap)
    await sdk.start()

    if isinstance(sdk, TapSDK2):
        print("Protocol: v2")
        await sdk.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    else:
        print("Protocol: v1")
        await sdk.set_input_mode(InputModeController())

    print("Waiting for taps… (Ctrl+C to quit)")
    await asyncio.Event().wait()


asyncio.run(main())
```

Turn the Tap on. Update firmware with Tap Manager. `connect()` picks `TapSDK` (v1) or `TapSDK2` (v2) from GATT. More: [`examples/connect.py`](examples/connect.py).

### Features (summary)

- **Protocols:** v1 (`TapSDK`) and v2 framed (`TapSDK2`); `connect()` auto-detects
- **Modes (v1):** Text, Controller, Controller+Text, Raw sensors — [v1 how-tos](docs/v1/how-to/index.md)
- **Features (v2):** `DeviceFeatures`, vision model/op-mode, IMU motion/raw, standby — [v2 how-tos](docs/v2/how-to/index.md)
- **Events:** tap, mouse, air gesture, raw / IMU packets, connect/disconnect
- **Commands:** set mode / features, haptic sequences
- **Out of scope for first-run:** Spatial Control (`set_input_type` on authorized TapXR / v1 only — not on `TapSDK2`). See [Use Spatial Control](docs/v1/how-to/use-spatial-control.md) only if you have access.

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

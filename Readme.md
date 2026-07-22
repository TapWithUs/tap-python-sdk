## TapStrap Python SDK (beta)

[![PyPI version](https://img.shields.io/pypi/v/tap-python-sdk.svg)](https://pypi.org/project/tap-python-sdk/)

BLE SDK for building Python apps that connect to **Tap Strap** and **TapXR**, send commands, and receive tap, mouse, air-gesture, and raw sensor events.

**Python ≥ 3.9** · **macOS / Windows / Linux** · **currently in beta**

### Documentation

Published docs (MkDocs Material, versioned with mike): [https://tapwithus.github.io/tap-python-sdk/](https://tapwithus.github.io/tap-python-sdk/)

Pick the path that matches your goal:

| I want to… | Go to |
|------------|--------|
| Get a first working connection | [Tutorial: Getting started](docs/tutorial/getting-started.md) |
| Solve a specific task | [How-to guides](docs/how-to/index.md) |
| Look up APIs and types | [Reference](docs/reference/index.md) |
| Understand modes and sensors | [Explanation](docs/explanation/index.md) |
| Read the changelog | [Release notes](docs/release-notes.md) |

Full index: [docs/index.md](docs/index.md). Local preview: `pip install -r requirements-docs.txt && mkdocs serve`.

### Install

```console
pip install tap-python-sdk
```

Platform notes (BlueZ on Linux, Bleak pins, pairing): [Install the SDK](docs/how-to/install.md).

### Quick example

```python
import asyncio
from tapsdk import TapSDK, InputModeController

async def main():
    tap = TapSDK()
    tap.register_tap_events(lambda identifier, tapcode: print(identifier, tapcode))
    await tap.run()
    await tap.set_input_mode(InputModeController())
    await asyncio.Event().wait()

asyncio.run(main())
```

Pair the Tap with the OS first. Update firmware with Tap Manager. More complete flow: [`examples/basic.py`](examples/basic.py).

### Features (summary)

- **Modes:** Text, Controller, Controller+Text, Raw sensors
- **Events:** tap, mouse, air gesture, air-gesture state, raw packets, connect/disconnect
- **Commands:** set mode, set Spatial Control input type (TapXR), haptic sequences
- **Spatial Control** (authorized TapXR builds): see [Use Spatial Control](docs/how-to/use-spatial-control.md)

### Migrating from 0.6.x

Breaking API changes are listed in [Migrate from 0.6](docs/how-to/migrate-from-0.6.md) and [Release notes](docs/release-notes.md).

### Releasing

PyPI releases publish on annotated `v*` tags. Docs deploy separately after a successful publish. See the header comments in [`.github/workflows/publish.yml`](.github/workflows/publish.yml).

### Testing

```bash
pip install .[dev]
pytest
```

### Support

Use the [GitHub issues](https://github.com/TapWithUs/tap-python-sdk/issues) tab.

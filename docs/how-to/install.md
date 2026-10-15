# Install the SDK

## From PyPI

```bash
pip install tap-python-sdk
```

## From source

```bash
git clone https://github.com/TapWithUs/tap-python-sdk
cd tap-python-sdk
pip install .
```

For development (tests and flake8):

```bash
pip install .[dev]
```

## Platform prerequisites

### macOS

Uses Apple CoreBluetooth via Bleak 3.x. If you use a non-system Python, install PyObjC for that interpreter.

### Windows 10+

Uses Bleak 3.x with PyWinRT (installed via bleak). No external DLL is required.

Pair the Tap once via **Settings > Bluetooth & devices > Add device** before
connecting with the SDK. If a device connects but is misdetected as v1, or
you see `"Characteristic ... was not found!"`, fully unpair it and re-pair
through Settings rather than relying on the SDK's own scan/attach — see
[Windows BLE connect notes](../windows-ble-connect-notes.md) for background.

Pass `skip_scan=True` to `connect()` to only attach to a Tap Windows already
reports as connected/paired, without falling back to a live BLE scan:

```python
sdk = await connect(skip_scan=True)
```

### Linux

Install BlueZ tools and grant Bluetooth access:

```bash
sudo apt-get install bluez-tools libbluetooth-dev
sudo usermod -G bluetooth -a <username>
su - $USER
```

Uses Bleak 3.x with BlueZ. The device’s Bluetooth name must start with `Tap` for the Linux discovery path.

## Verify the import

```bash
python -c "from tapsdk import TapSDK; print('ok')"
```

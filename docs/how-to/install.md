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

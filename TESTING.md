# Testing Suite

This SDK interfaces with Bluetooth hardware, so running tests on machines without the accessory requires mocking the BLE backend.  The tests in `tests/` rely on small stubs that replace the `bleak` library and patch the detected platform.  This allows the package to be imported and exercised without real hardware.

## Running Tests Locally

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -v
```

## Continuous Integration

A GitHub Actions workflow (`.github/workflows/test.yml`) is provided.  It runs the test suite on Windows, macOS and Linux against multiple Python versions.  The workflow installs the package in editable mode and executes `pytest`.

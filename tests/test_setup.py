import os


def test_package_metadata_python_requires_and_bleak_pin():
    here = os.path.dirname(os.path.dirname(__file__))
    setup_path = os.path.join(here, "setup.py")
    with open(setup_path, encoding="utf-8") as f:
        content = f.read()
    assert 'DISTRIBUTION_NAME = "tap-python-sdk"' in content
    assert 'PACKAGE_NAME = "tapsdk"' in content
    assert "name=DISTRIBUTION_NAME" in content
    assert 'python_requires=">=3.10"' in content or "python_requires='>=3.10'" in content
    assert '"Development Status :: 5 - Production/Stable"' in content
    assert "bleak>=3.0.2,<4" in content
    assert "REQUIRED = [" in content
    assert "bleak==0.12.1" not in content
    assert "bleak-winrt" not in content

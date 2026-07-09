import platform

import pytest


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Windows import of tap.py requires bleak_winrt, unavailable with bleak 3.x (see #21)",
)
def test_tapclient_importable():
    import tapsdk.tap as tap

    assert hasattr(tap, "TapClient")

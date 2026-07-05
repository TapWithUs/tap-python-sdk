import platform

import tapsdk.tap as tap


def test_tapclient_defined_for_current_platform():
    assert hasattr(tap, "TapClient")
    assert platform.system() in {"Linux", "Windows", "Darwin"}

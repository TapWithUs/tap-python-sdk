def test_tapclient_importable():
    import tapsdk.tap as tap

    assert hasattr(tap, "TapClient")

from types import SimpleNamespace

from tapsdk._detect import V2_READ_CHAR, detect_protocol


def _fake_client(char_uuids):
    chars = [SimpleNamespace(uuid=u) for u in char_uuids]
    service = SimpleNamespace(characteristics=chars)
    return SimpleNamespace(services=[service])


def test_detect_protocol_v2_when_read_char_present():
    client = _fake_client([
        "c3ff0001-1d8b-40fd-a56f-c7bd5d0f3370",
        V2_READ_CHAR,
        "c3ff000f-1d8b-40fd-a56f-c7bd5d0f3370",
    ])
    assert detect_protocol(client) == "v2"


def test_detect_protocol_v1_without_v2_char():
    client = _fake_client([
        "c3ff0005-1d8b-40fd-a56f-c7bd5d0f3370",
        "c3ff0006-1d8b-40fd-a56f-c7bd5d0f3370",
    ])
    assert detect_protocol(client) == "v1"


def test_detect_protocol_v1_when_no_services():
    assert detect_protocol(SimpleNamespace(services=None)) == "v1"
    assert detect_protocol(SimpleNamespace(services=[])) == "v1"


def test_detect_protocol_case_insensitive():
    client = _fake_client([V2_READ_CHAR.upper()])
    assert detect_protocol(client) == "v2"

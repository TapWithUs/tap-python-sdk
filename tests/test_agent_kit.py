import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "tap-python-sdk"
SKILLS = sorted(p for p in (PLUGIN / "skills").iterdir() if p.is_dir())


def _load(script):
    spec = importlib.util.spec_from_file_location(script.stem, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


knob = _load(PLUGIN / "skills" / "tap-knob" / "scripts" / "knob.py")
dpad = _load(PLUGIN / "skills" / "tap-dpad" / "scripts" / "dpad.py")


def test_marketplaces_point_at_plugin():
    claude = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    codex = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text())
    assert (ROOT / claude["plugins"][0]["source"]).resolve() == PLUGIN
    assert (ROOT / codex["plugins"][0]["source"]["path"]).resolve() == PLUGIN
    for manifest in (".claude-plugin", ".codex-plugin"):
        assert json.loads((PLUGIN / manifest / "plugin.json").read_text())["name"] == PLUGIN.name


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_skill_frontmatter(skill):
    text = (skill / "SKILL.md").read_text()
    front = re.match(r"^---\nname: (\S+)\ndescription: (.+)\n---\n", text)
    assert front, "SKILL.md needs name + description frontmatter"
    assert front.group(1) == skill.name
    for link in re.findall(r"\]\((scripts/[^)]+)\)", text):
        assert (skill / link).exists(), link


def test_knob_steps_and_release():
    k = knob.KnobTracker(step_deg=2, release_after=4)
    assert k.on_roll(10) == 0                       # idle: no steps
    assert k.on_gesture(111) == "start" and k.active == 1
    assert k.on_roll(10) == 0                       # first roll sets the reference
    assert [k.on_roll(r) for r in (11, 12, 15, 9)] == [0, 1, 1, -2]
    assert k.on_gesture(110) == "start" and k.active == 0  # switching pinch re-grabs
    assert k.on_roll(179) == 0 and k.on_roll(-177) == 2    # 4 deg across +/-180, not -356
    assert [k.on_gesture(100) for _ in range(4)] == [None, None, None, "release"]
    assert k.active is None


def test_dpad_rotate_lock():
    d = dpad.DpadStateMachine()
    assert d.on_gesture(101, 0.0) == [("direction", "left")]
    assert d.on_gesture(101, 0.01) == []            # debounced repeat
    assert d.on_gesture(105, 0.1) == [("pinch", 0)]
    assert d.on_gesture(110, 0.2) == [("hold", 0)] and d.mode == "pending"
    assert d.on_gesture(105, 0.25) == []            # pinch ignored while holding
    d.on_motion(0, 0, 0, 0.3)
    assert ("mode", "rotate") in d.on_motion(0, 0, 30, 0.5)
    assert d.on_motion(5, 5, 40, 0.6) == [("rotate", 40)]
    events = [e for t in range(4) for e in d.on_gesture(100, 0.7 + t * 0.05)]
    assert events == [("release", 0)] and d.held is None


def test_dpad_drag_lock_and_fist():
    d = dpad.DpadStateMachine()
    d.on_gesture(112, 0.0)
    d.on_motion(0, 0, 0, 0.1)
    d.on_motion(0, 0, 5, 0.5)                        # small twist only
    assert d.on_motion(3, -2, 5, 1.1) == [("mode", "drag"), ("drag", 3, -2)]
    assert d.on_gesture(114, 1.2) == [("release", 2), ("hide",)]
    assert d.on_gesture(101, 1.3) == []              # hidden: ignored
    assert d.on_gesture(100, 1.4) == [] and d.on_gesture(100, 1.5) == [("show",)]

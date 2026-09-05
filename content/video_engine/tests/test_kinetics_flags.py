"""P39 T4: the kill switch. The template reads `timeline.kinetics` - a map of capability
name to boolean - and every flag defaults to false, meaning the tagged baseline behaviour.

Three things are pinned here:
  1. the defaults block exists in the template and every value in it is `false`
  2. an explicit all-false map, and an unknown flag name, both render pixel-identical to the
     golden frame (the switch is inert when off, and a typo cannot turn anything on)
  3. the flag names are exactly the six designed-out capabilities of doc 47 s1 / P38, plus min_jerk (2026-09-05)

Rendering tests need playwright + chromium and are skipped without them; the static checks
always run.
"""
from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402

CAPABILITIES = ["curvature_stroke", "analytic_spring", "area_squash", "arap_morph", "dqs_skinning", "prop_attach",
                "min_jerk",    # + the minimum-jerk transition (FINDING-the-animation-math s2, 2026-09-05)
                "km_ink"]      # + Kubelka-Munk on overlapping ink (44 s44.1, P43 T3, 2026-09-05)


def _defaults_block() -> dict[str, str]:
    src = RB.TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"const KINETICS_DEFAULTS = Object\.freeze\(\{(.*?)\}\);", src, re.S)
    assert m, "template has no KINETICS_DEFAULTS block"
    return dict(re.findall(r"(\w+)\s*:\s*(true|false)", m.group(1)))


def test_every_capability_flag_defaults_to_current_behaviour() -> None:
    defaults = _defaults_block()
    assert sorted(defaults) == sorted(CAPABILITIES), f"flag set drifted from doc 47 s1: {sorted(defaults)}"
    on = [k for k, v in defaults.items() if v != "false"]
    assert not on, f"a capability defaults to the NEW behaviour - forbidden by P39: {on}"


def test_template_reads_the_flags_from_the_timeline() -> None:
    src = RB.TEMPLATE.read_text(encoding="utf-8")
    assert "TL.kinetics" in src
    assert "const kin = (name) => KIN[name] === true" in src


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
@pytest.mark.parametrize("name", sorted(RB.FLAG_FRAMES))
def test_each_flag_golden_differs_from_the_flag_off_render(name: str) -> None:
    """P43 T6: a flag-ON golden that matched the flag-off render at its t would prove nothing. The squash frame is
    compared against its spring-only twin (the spring is what gives it a velocity), every other against all-off."""
    surface, flags, t = RB.FLAG_FRAMES[name]
    off = {"analytic_spring": True} if "area_squash" in flags else {}
    a = RB.rgb_bytes(RB.render_surface(surface, t, kinetics=off))[1]
    b = RB.rgb_bytes((RB.FRAMES / f"{name}.png").read_bytes())[1]
    assert a != b, f"{name}: the flag changed nothing at t={t}"


@pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
@pytest.mark.parametrize("kinetics", [
    {name: False for name in CAPABILITIES},          # explicit all-off
    {"not_a_capability": True},                      # a typo cannot turn anything on
])
def test_flags_off_render_the_golden_frame_exactly(kinetics: dict) -> None:
    tl, uris, t, aspect = RB.load_surface("dock-pair-16x9")
    tl = copy.deepcopy(tl); tl["kinetics"] = kinetics
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "flags.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        actual = RB.render_frame(html, t, aspect)
    golden = (RB.FRAMES / "dock-pair-16x9.png").read_bytes()
    assert RB.rgb_bytes(golden)[1] == RB.rgb_bytes(actual)[1], f"flags {json.dumps(kinetics)} changed the render"

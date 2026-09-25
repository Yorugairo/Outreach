"""P72 T27 (the second half) - the small engine rows, one test group per row, in the order they were committed (the
first half's rows are test_small_engine_rows.py). Each group's header names its row and its ruling.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as BST  # noqa: E402
import build_golden_sources as G  # noqa: E402
import render_baseline as RB  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CHECKLIST = ROOT / "content/video_engine/scripts/species/checklist.mjs"
DROP = ROOT / "content/video_engine/scripts/kinetics/drop.mjs"
TAG = r"\[(?:DERIVED: |MEASURED: |UNSOURCED - )"


def _chromium_available() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _render(tl: dict, uris: dict, times: list[float], probe: str | None = None) -> list[tuple[bytes, object]]:
    """(png, probe result) at each instant, on one served page (the golden's own capture: a pure function of t)."""
    import served_player as SP
    w, h = RB.STAGE[tl.get("aspect") or "16:9"]
    out = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "t27b.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, w, h) as (page, errs):
            for t in times:
                png = RB.frame_png(page, t, (w, h))
                out.append((png, page.evaluate(probe) if probe else None))
            assert not errs, errs
    return out


# ---- R26-9 TR-3: the transition numbers carry their sources ------------------------------------------------------

def _transitions_region() -> str:
    src = ENGINE.read_text(encoding="utf-8")
    a = src.index("  const WIPE = ")
    a = src.rindex("/* P72 T27 / R26-9 TR-3", 0, a) if "/* P72 T27 / R26-9 TR-3" in src[:a] else a
    b = src.index("\n", src.index("  const SLIDE_S = "))
    return src[a:b]


def _declared(region: str) -> list[str]:
    names: list[str] = []
    for line in region.splitlines():
        m = re.match(r"\s*const ([A-Z][A-Z0-9_]* = -?[\d.]+(?:, [A-Z][A-Z0-9_]* = -?[\d.]+)*);", line)
        if m:
            names += re.findall(r"([A-Z][A-Z0-9_]*) = ", m.group(1))
    return names


def test_the_transitions_region_declares_the_numbers_the_plan_names() -> None:
    names = _declared(_transitions_region())
    for n in ("WIPE", "DISSOLVE_S", "MOUNT_STEPS", "SUCK_S", "SUCK_TURN", "DIP_S", "BLURZOOM_S", "BLURZOOM_SCALE",
              "BLURZOOM_BLUR", "BLURZOOM_IN", "SLIDE_S"):
        assert n in names, (n, names)


def test_every_transition_constant_carries_a_source_tag() -> None:
    """E42 D6: a shipped number carries its tag - `NAME <value> [DERIVED: ...]`, `[MEASURED: ...]` or `[UNSOURCED - ...]`."""
    region = _transitions_region()
    untagged = [n for n in _declared(region)
                if not re.search(rf"\b{n}\b(?:\s+-?[\d.]+)?\s+{TAG}", region)]
    assert untagged == [], f"transition constants with no source tag: {untagged}"

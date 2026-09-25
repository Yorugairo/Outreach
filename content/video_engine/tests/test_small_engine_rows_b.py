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


# ---- R26-302: a checklist column waits for its own instant --------------------------------------------------------

def _card_chart(at=None) -> tuple[dict, dict, dict]:
    tl, uris = G.test_card()
    chart = next(iter(tl["evidence"].values()))["chart"]
    if at is not None:
        chart["checklist"]["at"] = at
    return tl, uris, chart


@pytest.mark.parametrize("at, says", [
    ("6.0", r"checklist: `at` must be a list of one instant per column"),
    ([None, None, 6.0], r"checklist: `at` names 3 columns, the head 4"),
    ([None, None, None, -1.0], r"checklist: `at` column 4 is -1.0"),
    ([None, None, None, True], r"checklist: `at` column 4 is True"),
    ([None, None, None, "6"], r"checklist: `at` column 4 is '6'"),
    ([None, None, None, float("nan")], r"checklist: `at` column 4 is nan"),
])
def test_a_malformed_column_at_is_refused_by_name(at, says) -> None:
    _, _, chart = _card_chart(at)
    problems = BST.checklist_problems(chart)
    assert problems and re.search(says, " | ".join(problems)), problems
    with pytest.raises(ValueError, match=r"ev-x: checklist: `at`"):
        BST.check_checklist("ev-x", chart)


def test_a_good_column_at_and_none_both_pass() -> None:
    assert BST.checklist_problems(_card_chart()[2]) == []
    assert BST.checklist_problems(_card_chart([None, None, None, 6.0])[2]) == []
    assert BST.checklist_problems(_card_chart([0, 1.5, None, 6])[2]) == []


def _node(js: str) -> object:
    url = CHECKLIST.resolve().as_uri()
    code = f"import * as C from {json.dumps(url)};\n{js}"
    r = subprocess.run(["node", "--input-type=module", "-e", code], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_the_cell_clock_waits_for_its_column_and_is_the_old_clock_without_one() -> None:
    got = _node("""
      const V = C.CHECKLIST, clk = (t, d, k, at) => C.checklistCellClock(t, d, k, false, V, at);
      console.log(JSON.stringify({
        plain: [clk(5, 1, 3), clk(5, 1, 3, null), clk(5, 1, 3, undefined)],
        waits: clk(5, 1, 3, 6), after: clk(7, 1, 3, 6), early: clk(5, 4, 3, 2),
        recap: C.checklistCellClock(5, 1, 3, true, V, 6)}));""")
    assert got["plain"] == [5 - 1 - 1.6] * 3, got          # no `at`: tRel - rowDelay - OFFS[k], as it always was
    assert got["waits"] == pytest.approx(-1.0), got           # the column's instant is later than the row's: it waits
    assert got["after"] == pytest.approx(1.0), got
    assert got["early"] == pytest.approx(5 - 4 - 1.6), got    # an instant BEFORE the row's own clock never draws early
    assert got["recap"] == pytest.approx(-1.0), got           # ... on a recap too


def test_the_engine_carries_the_species_column_clock() -> None:
    src = ENGINE.read_text(encoding="utf-8")
    assert "const checklistCellClock = (tRel, rowDelay, k, recap, V = CHECKLIST, at = null) => {" in src
    assert "checklistCellClock(tRel, rowDelay, k, recap, V, c.at)" in src


# every cell of the test card's rows: its text, its column and the opacity its group carries
CELLS = """() => [...document.querySelectorAll('.dock svg.chartbox text.cs')].map((e) => ({
  text: e.textContent, fill: e.getAttribute('fill'), o: +(e.parentNode.getAttribute('opacity') || 1) }))"""


@needs_browser
def test_the_paper_column_writes_on_its_own_instant() -> None:
    """Row 20's defect on the golden card: the Believed column waits for its word at tRel 6.0 (t 8.45 on this card's
    clock - enter 2.0 + CARD_IN x 0.6). Before it, row 1's answer (+1.6 on its row, long due) is not on the card;
    after it, it is; every other cell reads exactly as the card without `at`."""
    tl0, uris, _ = _card_chart()
    tl1, _, _ = _card_chart([None, None, None, 6.0])
    t_before, t_after = 2.45 + 6.0 - 0.05, 2.45 + 6.0 + 0.40
    base = [p for _, p in _render(tl0, uris, [t_before, t_after], CELLS)]
    colat = [p for _, p in _render(tl1, uris, [t_before, t_after], CELLS)]
    believed = G.test_card()[0]["evidence"]["ev-golden-test-card"]["chart"]["checklist"]["rows"][0]["cells"][3]
    pick = lambda cells, txt: next(c for c in cells if c["text"] == txt)   # noqa: E731
    assert pick(base[0], believed)["o"] == 1, base[0]                       # the card without `at`: already written
    assert pick(colat[0], believed)["o"] == 0, colat[0]                     # with it: waiting for its instant
    assert pick(colat[1], believed)["o"] == 1, colat[1]                     # ... and written after it
    others = lambda cells: [c for c in cells if c["fill"] != "#ff8a8c"]    # noqa: E731 - every column but Believed
    assert others(colat[0]) == others(base[0]) and others(colat[1]) == others(base[1])

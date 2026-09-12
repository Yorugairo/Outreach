"""P52 T10: the caption's arrival, as a declaration and as a gate reading.

The mechanism itself (one envelope, per-word offsets, the exactness of both ends, the seek test) is
pinned in `tests/kinetics/stagger.test.mjs` - the module is the source of truth and node tests it.
What is pinned HERE is everything python owns:

  the DEFAULT      `cap_arrive` is absent unless a build asks. No field, no timeline key, no engine
                   branch taken - which is why every golden and both shorts compile and render
                   byte-identical to their pre-slice selves (E21's pop is untouched).
  the DECLARATION  the compiler stamps the arrival on every caption page and on the timeline, and
                   REFUSES a kind it does not know (a typo must not silently ship the pop).
  the ENGINE       reads the page's kind, paints it from the module, and puts the blur on the WORD
                   SPAN - never on the strip (a filter on the strip blurs the whole caption).
  the GATE         M08 counts a fade-up page's words at their ENVELOPE starts, not their raw onsets:
                   a crowded onset does not arrive when it is spoken, it arrives one stagger later.
  the PARITY       the gate's mirrored law returns exactly what the module returns, checked by
                   running the module in node (skipped where node is absent).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as BST  # noqa: E402
import gate_motion_density as G  # noqa: E402
import render_baseline as RB  # noqa: E402

MODULE = ROOT / "content/video_engine/scripts/kinetics/stagger.mjs"
TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
FADE = "fade_up"


# ---- the default: nothing is declared, nothing changes -----------------------------------------

def test_the_arrival_is_absent_by_default_and_pop_writes_nothing() -> None:
    """None and "pop" are the same answer: no field. This is the byte-identity of every existing build."""
    assert BST.CAPTION_ARRIVE is None, "the compiler ships with no arrival declared"
    keep = BST.CAPTION_ARRIVE
    try:
        for asked in (None, "", "   ", "pop"):
            BST.CAPTION_ARRIVE = asked
            assert BST._caption_arrive() is None, asked
        BST.CAPTION_ARRIVE = FADE
        assert BST._caption_arrive() == FADE
    finally:
        BST.CAPTION_ARRIVE = keep


def test_an_unknown_arrival_is_refused_by_name() -> None:
    keep = BST.CAPTION_ARRIVE
    try:
        BST.CAPTION_ARRIVE = "fadeup"
        with pytest.raises(SystemExit) as e:
            BST._caption_arrive()
        assert "fadeup" in str(e.value) and "fade_up" in str(e.value)
    finally:
        BST.CAPTION_ARRIVE = keep


def test_the_compiler_stamps_the_page_beside_cap_mode_and_the_timeline_beside_caption_modes() -> None:
    """The two anchors, read off the source: the page field sits with `cap_mode`, the timeline field
    with `caption_modes`, and both are written only when the build asked."""
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    assert '"cap_arrive": _caption_arrive()' in src
    assert '**({"caption_arrive": _caption_arrive()} if _caption_arrive() else {})' in src
    assert BST.CAPTION_ARRIVALS == ("pop", FADE)


@pytest.mark.parametrize("build", ["build-short-t0", "build-short"])
def test_no_shipped_short_carries_an_arrival(build: str) -> None:
    """The approved cuts on disk: no page field, no timeline key. If this fails, a build that the
    operator approved has been recompiled with the new register turned on."""
    tl_path = TOKYO / build / "tokyo-short.timeline.json"
    if not tl_path.exists():
        pytest.skip(f"{build} is not on disk here")
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    assert "caption_arrive" not in tl
    assert not [pg for pg in tl.get("caption_pages", []) if "cap_arrive" in pg]


# ---- the engine ---------------------------------------------------------------------------------

def test_the_engine_reads_the_arrival_and_paints_it_from_the_module() -> None:
    src = RB.player_text()
    assert '(pg.cap_arrive || TL.caption_arrive) === "fade_up"' in src, "the page's kind wins over the timeline's"
    assert "const fuStarts = fuArrive ? staggerStarts(" in src
    assert "fadeUpAt(t, fuStarts[j], FADE_UP)" in src
    # the module is INLINED (no runtime import) and its region sits before the caption block that calls it
    assert "/* KINETICS:BEGIN stagger */" in src
    assert src.index("/* KINETICS:BEGIN stagger */") < src.index("const fuStarts = fuArrive ?")


def test_the_blur_is_a_filter_on_the_word_span_and_never_on_the_strip() -> None:
    src = RB.player_text()
    assert 'ws[j].style.filter = f.b > 0.01 ? "blur(" + f.b.toFixed(2) + "px)" : ""' in src
    assert "cap.style.filter" not in src, "a filter on the strip would blur the whole caption at once"
    assert "#caption { filter" not in src


def test_the_pop_is_still_there_word_for_word() -> None:
    """The default register is not touched by the new one: the lines that paint it are intact."""
    src = RB.player_text()
    assert 'const pop = kin("analytic_spring") ? springPop : stagePop;' in src
    assert "const e = pop(clamp01((t + 0.05 - x.s) / STAGE_POP_S));" in src
    assert "const STAGE_POP_S = 0.2;" in src
    assert "RISE_PX: 6" in src and "POP: 1.10" in src, "MARK's dials are unchanged"


# ---- the gate reads the envelope ---------------------------------------------------------------

def _pages(n: int = 6, page_s: float = 0.0, onsets: list[float] | None = None, arrive: str | None = None) -> list[dict]:
    onsets = onsets if onsets is not None else [page_s + 0.25 * i for i in range(n)]
    pg = {"s": page_s, "e": page_s + 2.0, "cap_mode": "stage",
          "t": [{"w": f"w{i}", "s": o, "e": o + 0.3} for i, o in enumerate(onsets)]}
    if arrive:
        pg["cap_arrive"] = arrive
    return [pg]


def _tl(pages: list[dict], runtime: float = 30.0, **extra) -> dict:
    return {"runtime_s": runtime, "caption_modes": ["stage", "anchor"], "caption_pages": pages,
            "scenes": [{"scene_id": "s00", "world": {"asset_id": "w"}, "span": [0.0, runtime]}], **extra}


def test_without_an_arrival_the_word_events_are_the_raw_onsets() -> None:
    """The reading every build before this slice gets, unchanged."""
    onsets = [0.0, 0.01, 0.02, 1.0]
    A = G.analyse(_tl(_pages(onsets=onsets)), [], {})
    for o in onsets:
        assert any(abs(t - o) < 1e-9 for t in A["events"]), o
    assert A["cap_arrive"] is None


def test_a_fade_up_page_is_counted_at_its_envelope_starts_not_its_crowded_onsets() -> None:
    crowded = [5.0, 5.0, 5.01, 5.02, 6.0]
    A = G.analyse(_tl(_pages(page_s=5.0, onsets=crowded, arrive=FADE)), [], {})
    want = G._stagger_starts(crowded, 5.0)
    assert want[:4] == [5.0, 5.055, pytest.approx(5.11), pytest.approx(5.165)]
    assert want[4] == 6.0, "the far word keeps its own spoken time - E21's clock survives"
    for t in want:
        assert any(abs(e - t) < 1e-9 for e in A["events"]), t
    # the instants that are NOT arrivals are not credited
    assert not any(abs(e - 5.01) < 1e-9 for e in A["events"]), "5.01 is when the word was said, not when it arrives"
    assert A["cap_arrive"] == FADE


def test_the_timeline_level_arrival_applies_to_every_page() -> None:
    A = G.analyse(_tl(_pages(page_s=2.0, onsets=[2.0, 2.0, 2.0]), caption_arrive=FADE), [], {})
    assert A["cap_arrive"] == FADE
    for t in (2.0, 2.055, 2.11):
        assert any(abs(e - t) < 1e-9 for e in A["events"]), t


def _dense_stage(arrive: str | None, runtime: float = 90.0) -> dict:
    """15s scenes - nothing but the captions can carry the stretch, which is the M08 case (E21)."""
    scenes, t, i = [], 0.0, 0
    while t < runtime:
        scenes.append({"scene_id": f"s{i:02d}", "world": {"asset_id": f"world-{i}"}, "span": [t, min(t + 15.0, runtime)]})
        t += 15.0
        i += 1
    pages, t = [], 0.0
    while t < runtime:
        pg = {"s": t, "e": t + 1.4, "cap_mode": "stage",
              "t": [{"w": "x", "s": t + 0.2 * k, "e": t + 0.2 * k + 0.2} for k in range(5)]}
        if arrive:
            pg["cap_arrive"] = arrive
        pages.append(pg)
        t += 1.5
    return {"runtime_s": runtime, "caption_modes": ["stage", "anchor"], "caption_pages": pages, "scenes": scenes}


@pytest.mark.parametrize("arrive", [None, FADE])
def test_m08_passes_on_both_registers_and_names_the_envelope(arrive: str | None) -> None:
    gates, _ = G.run(_dense_stage(arrive), [], {})
    g = {x.id: x for x in gates}
    assert g["M08"].level == "PASS", g["M08"]
    assert g["M01"].level == "PASS", g["M01"]
    named = "envelope" in g["M08"].message
    assert named == (arrive == FADE), g["M08"].message


def test_m08_still_fails_when_the_stretch_carries_anchor_pages_under_a_fade_up_timeline() -> None:
    """The register does not buy a pass: a lower-third page is still not motion (E21)."""
    tl = _dense_stage(FADE)
    for pg in tl["caption_pages"]:
        pg["cap_mode"] = "anchor"
    g = {x.id: x for x in G.run(tl, [], {})[0]}
    assert g["M08"].level == "FAIL", g["M08"]


# ---- the parity: the gate's mirror against the module itself ------------------------------------

@pytest.mark.skipif(shutil.which("node") is None, reason="node is not on PATH")
def test_the_gates_mirrored_law_is_the_modules_law() -> None:
    cases: list[tuple[list[float | None], float]] = [
        ([0.0, 0.0, 0.01, 0.02, 1.0], 0.0), ([10.0, 10.3, 10.62, 11.4], 10.0),
        ([None, 1.4, None, None], 1.0), ([0.5], 2.0), ([], 0.0)]
    payload = [[[-1.0 if o is None else o for o in c[0]], c[1]] for c in cases]
    spec = json.dumps(MODULE.as_uri())   # a file:// URL: node will not import a bare Windows path
    js = (
        "import { staggerStarts, FADE_UP } from " + spec + ";\n"
        "const cases = " + json.dumps(payload) + ";\n"
        "console.log(JSON.stringify({ stagger: FADE_UP.STAGGER_S, out: cases.map(([o, g]) =>"
        " staggerStarts(o.map((v) => (v === -1 ? null : v)), g)) }));\n"
    )
    p = ROOT / "content/video_engine/tests/.stagger-parity.mjs"
    try:
        p.write_text(js, encoding="utf-8")
        got = json.loads(subprocess.run(["node", str(p)], capture_output=True, text=True, check=True).stdout)
    finally:
        p.unlink(missing_ok=True)
    assert got["stagger"] == G.CAP_STAGGER_S, "the gate's stagger drifted from the module's dial"
    for (onsets, origin), want in zip(cases, got["out"]):
        mine = G._stagger_starts(onsets, origin)
        assert len(mine) == len(want)
        for a, b in zip(mine, want):
            assert abs(a - b) < 1e-12, (onsets, origin, mine, want)

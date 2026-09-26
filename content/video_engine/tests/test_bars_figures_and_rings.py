"""P72 T18 - FIGURES AND RINGS ON A BARS PAGE (R26-284, R26-288, R26-255, R26-256).

R26-284 (found by P69 T25, `p69t25/m28/crops.png`): on the 94 bars page the bar's own value faded while the figure
wrote "94%" a few px off it - the probe's M28 FAIL `val:94% on bracket:94%` for ~0.6 s. The hand-over is now IN
PLACE: when the bar's printed number already STOOD at the figure's word (its page had built), the number leaves over
FIGURE.HAND of the word, the figure's group is not up until it has, and the hand writes the figure in its place over
the rest - so the page prints the number once at every frame. A figure written while its bar still grows (the H
door's two: the 20 bar's "20%" at its page's start, the wafer panel's "3x" on its panel's build) keeps the write it
had, byte for byte. And a row that restates its bar's own value compiles with a WARN naming the row, the figure and
the value (a double print is legibility, M28 - never a truth rule; s106: advice, never a refusal).

R26-288: a ring on a bar resolved to the WHOLE bar, so its ellipse crossed "Capex, next two years". A datum target
may now name `part: "value"` - the bar's printed value (its pill on an emphasized bar), read live, so a bar whose
compare re-values it (P69 T26a) carries its ring. The rings alone take it; a malformed or misplaced key is refused
by name (a target that resolves to nothing is a truth rule).

R26-255: on a bars page with chart STATES the painter re-placed a centred bar figure by the LINE rule, beside its bar.
R26-256: an emphasized bar's pill (the page's own statement of that bar's number) did not yield to its figure.

The fixtures are test_compare_on_bars'; the browser proofs need playwright + chromium and are skipped without them.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as GM  # noqa: E402
import probe as PR  # noqa: E402
import test_compare_on_bars as CB  # noqa: E402 - the three H objects and their served fixtures

ASPECT, FIG_AT, FIG_S = CB.ASPECT, CB.FIG_AT, CB.FIG_S
VALUE_TARGET = {"kind": "datum", "index": 0, "part": "value"}
WHERE = "shot row 17 (324.9-338.4s)"


def _world(plate_tail: str, obj: dict, tmp: Path, oid: str = "fx-bars", extra: dict | None = None,
           stamp: bool = True) -> tuple[dict, str]:
    """A bars object on disk and its world as a 16:9 build stamps it (full-stage), plate `ledger:<oid>:<tail>`."""
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    for k, v in (extra or {}).items():
        (tmp / f"evidence/objects/{k}.series.json").write_text(json.dumps(v), encoding="utf-8")
    plate = f"ledger:{oid}:{plate_tail}"
    world = CB._world_at(plate, tmp, ASPECT)
    if not stamp:   # the rescale fixture is test_compare_on_bars' own, built its way (its states unstamped)
        return world, plate
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world, plate


def _figure(text: str, index: int = 0, at: float = FIG_AT, **kw) -> dict:
    return dict({"kind": "figure", "at": at, "dur": FIG_S, "text": text, "target": {"kind": "datum", "index": index}}, **kw)


def _ring(kind: str = "callout", target: dict | None = None, at: float = FIG_AT, dur: float = 3.0, **kw) -> dict:
    sp = {"kind": kind, "at": at, "dur": dur, "target": copy.deepcopy(target or VALUE_TARGET)}
    if kind == B.SPECIES_RING:
        sp["form"] = "dashed"
    return dict(sp, **kw)


# ---- R26-284: the compiler ADVISES a figure that restates its bar's own value ----------------------------------------


def test_a_figure_that_restates_its_bars_value_is_warned_naming_the_row_the_figure_and_the_value(tmp_path):
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    warns = B.figure_value_advice(world, [_figure("94%")], WHERE)
    assert len(warns) == 1, warns
    w = warns[0]
    assert w.startswith(WHERE), f"the WARN names the row: {w}"
    assert "'94%'" in w and "bar 0" in w and "Capex, next two years" in w, f"... the figure, the bar and its value: {w}"
    assert "R26-284" in w and "s106" in w, w


@pytest.mark.parametrize("text", ["94 %", "94%", " 94% "])
def test_the_restatement_is_read_on_what_the_page_prints_not_on_the_authored_spacing(tmp_path, text):
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    assert B.figure_value_advice(world, [_figure(text)], WHERE), text


@pytest.mark.parametrize("text", ["94 cents", "0.94", "$94B", "of every dollar"])
def test_a_figure_that_says_what_the_value_does_not_is_not_advised(tmp_path, text):
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    assert B.figure_value_advice(world, [_figure(text)], WHERE) == []


def test_a_restating_figure_on_a_panel_names_the_panel_and_its_bar(tmp_path):
    """The wafer panel's "3x" (H row 21's shape): the panel's own bar prints "3x"."""
    world, _plate = _world("bars", CB.OBJ_13, tmp_path)
    warns = B.figure_value_advice(world, [_figure("3x", 1)], WHERE)
    assert len(warns) == 1 and "'3x'" in warns[0] and "bar 1" in warns[0], warns


def test_the_warn_never_refuses_the_row(tmp_path):
    """s106: legibility advises. The row compiles as authored - species validation and the page's own checks pass."""
    world, plate = _world("bars", CB.OBJ_94, tmp_path)
    species = [_figure("94%")]
    assert B.validate_species(species, (0, 0, 0), plate) == []
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        B.derive_rescale_states(world, species, plate, tmp_path, sid="s01")
    finally:
        B.ASPECT = saved
    assert B.figure_value_advice(world, species, WHERE), "and the advice still stands on the compiled row"


def test_a_line_page_figure_is_never_advised(tmp_path):
    """A line page prints no value on a datum - a figure there is E50's number at its point, never a restatement."""
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    lined = copy.deepcopy(world)
    lined["page"]["builder"] = "dense-line"
    assert B.figure_value_advice(lined, [_figure("94%")], WHERE) == []


# ---- R26-288: a `value` target on a bar, for the rings alone --------------------------------------------------------


@pytest.mark.parametrize("kind", ["callout", B.SPECIES_RING])
def test_a_ring_may_name_its_bars_value(kind, tmp_path):
    _world_, plate = _world("bars", CB.OBJ_94, tmp_path)
    assert B.validate_species([_ring(kind)], (0, 0, 0), plate) == []


@pytest.mark.parametrize("kind", ["spotlight", "squiggle", "punch", "focus_zoom", "figure", "build_to"])
def test_any_other_species_naming_a_value_is_refused_by_name(kind):
    errs = B._validate_target(kind, dict(VALUE_TARGET), B.SPECIES_TARGETS.get(kind, B.TARGET_KINDS))
    assert errs and any("part" in e and "R26-288" in e for e in errs), errs


@pytest.mark.parametrize("part", ["label", "bar", "", 0, True, None])
def test_a_malformed_part_is_refused_by_name(part):
    errs = B._validate_target("callout", dict(VALUE_TARGET, part=part), B.SPECIES_TARGETS["callout"])
    assert errs and any("part" in e for e in errs), (part, errs)


def test_a_value_on_a_docked_chart_is_refused_it_names_a_bar_of_the_page():
    errs = B._validate_target("callout", dict(VALUE_TARGET, dock=0), B.SPECIES_TARGETS["callout"])
    assert errs and any("part" in e and "dock" in e for e in errs), errs


def test_a_value_the_page_does_not_print_is_refused_by_name(tmp_path):
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    with pytest.raises(ValueError, match=r"bar 3.*R26-288"):
        B.check_value_targets(world, [_ring(target=dict(VALUE_TARGET, index=3))])
    B.check_value_targets(world, [_ring()])   # the one bar: nothing to say


def test_a_value_target_on_a_line_page_is_refused(tmp_path):
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    lined = copy.deepcopy(world)
    lined["page"]["builder"] = "dense-line"
    with pytest.raises(ValueError, match=r"value.*R26-288"):
        B.check_value_targets(lined, [_ring()])


def test_a_ring_on_a_value_that_writes_the_number_again_is_advised(tmp_path):
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    warns = B.figure_value_advice(world, [_ring(label="94%")], WHERE)
    assert len(warns) == 1 and "label" in warns[0] and "'94%'" in warns[0], warns
    assert B.figure_value_advice(world, [_ring()], WHERE) == [], "a ring with no label circles the number, once"


# ---- the player ------------------------------------------------------------------------------------------------------


needs_browser = CB.needs_browser

READ = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, S = (st.states || [st])[st.active | 0] || st, PF = st.perform || { figures: [] };
  const stg = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return r.width > 0 ? [r.x - stg.x, r.y - stg.y, r.width, r.height] : null; };
  const eff = (el) => { let o = 1; for (let e = el; e && e.getAttribute; e = e.parentNode) { const a = e.getAttribute('opacity');
    if (a != null && a !== '') o *= +a; const cs = getComputedStyle(e); if (cs.display === 'none') return 0; o *= +cs.opacity; } return o; };
  const bars = (S.bars || []).map(b => ({ box: R(b.bar), lab: R(b.lab), val: b.val ? { box: R(b.val), eff: eff(b.val) } : null }));
  const pill = S.callout ? { eff: eff(S.callout), box: R(S.callout.querySelector('rect.cpill') || S.callout) } : null;
  const figs = (PF.figures || []).map(fg => ({ eff: eff(fg.g), gop: +(fg.g.getAttribute('opacity') || 0), box: R(fg.label), anchor: fg.label.getAttribute('text-anchor'),
    glyphs: fg.lg.map(ts => +(ts.getAttribute('opacity') || 0)) }));
  const unite = (a, b) => !a ? b : !b ? a : [Math.min(a[0], b[0]), Math.min(a[1], b[1]),
    Math.max(a[0] + a[2], b[0] + b[2]) - Math.min(a[0], b[0]), Math.max(a[1] + a[3], b[1] + b[3]) - Math.min(a[1], b[1])];
  let ring = null;
  for (const L of [document.getElementById('species'), document.getElementById('species-under')]) if (L)
    for (const el of L.querySelectorAll('path.co, path.rngdash')) if (eff(el) > 0.05) ring = unite(ring, R(el));
  return { bars, pill, figs, ring };
}"""


class _Page(CB._Served):
    """A served one-scene timeline: `read(t)` is this file's READ, `m28(ts)` the probe's own label gate over instants."""

    def read(self, t: float) -> dict:
        for _ in range(2):   # the probe's warm seek
            self.seek(t)
        return self.page.evaluate(READ)

    def m28(self, ts: list[float]) -> GM.Gate:
        insts = []
        for t in ts:
            for _ in range(2):
                self.seek(t)
            dom = self.page.evaluate(PR.READ_DOM)
            insts.append(PR.derive(dom, t, "p72-t18", {}, ASPECT, {}, self.page.evaluate(PR.READ_DOCKS)))
        return GM._labels_gate({"player_sha256": "x", "instants": insts})


def _serve(world: dict, species: list[dict]) -> _Page:
    return _Page(*CB._one_scene(world, species))


def _centre(b: list[float]) -> tuple[float, float]:
    return b[0] + b[2] / 2, b[1] + b[3] / 2


def _meets(a, b) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


HAND_TS = [FIG_AT + FIG_S * k for k in (-0.2, 0.02, 0.1, 0.2, 0.3, 0.38, 0.42, 0.5, 0.6, 0.8, 1.0, 1.3)]


@needs_browser
def test_the_94_page_prints_its_number_once_at_every_frame_through_the_hand_over(tmp_path):
    """Acceptance (1): H row 17's page with its figure (the draft-4 row R26-284 was measured on). M28 over the whole
    hand-over PASSES (at the base: `val:94% on bracket:94%`), and at no probed frame are the value and the figure up
    together; the figure lands where the value stood (centred on its bar)."""
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    P = _serve(world, [_figure("94%")])
    try:
        gate = P.m28(HAND_TS)
        assert gate.level in ("PASS", "INFO"), gate.message
        for t in HAND_TS:
            s = P.read(t)
            val, fig = s["bars"][0]["val"]["eff"], s["figs"][0]["eff"]
            assert not (val > 0.05 and fig > 0.05), f"t={t:.2f}: the value ({val:.3f}) and the figure ({fig:.3f}) both up"
        done = P.read(FIG_AT + FIG_S + 0.5)
        assert done["figs"][0]["eff"] == 1 and all(g == 1 for g in done["figs"][0]["glyphs"]), "the hand has written it"
        assert done["bars"][0]["val"]["eff"] == 0, "and the value is gone while the figure stands"
        fx, _fy = _centre(done["figs"][0]["box"])
        bx, _by = _centre(done["bars"][0]["box"])
        assert abs(fx - bx) < 1.0, f"in the value's place, centred on its bar: {fx} vs {bx}"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
def test_the_hand_waits_for_the_number_then_writes_it(tmp_path):
    """The order of the hand-over: the value alone, the value leaving, then the hand writing - never a glyph early."""
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    P = _serve(world, [_figure("94%")])
    try:
        mid = P.read(FIG_AT + FIG_S * 0.2)
        assert 0 < mid["bars"][0]["val"]["eff"] < 1, "the value is leaving on the figure's own clock"
        assert mid["figs"][0]["eff"] == 0, "and the figure is not up while it does"
        late = P.read(FIG_AT + FIG_S * 0.55)
        assert late["bars"][0]["val"]["eff"] == 0 and late["figs"][0]["eff"] == 1, late
        assert 0 < late["figs"][0]["glyphs"][0] < 1 or late["figs"][0]["glyphs"][-1] < 1, "the hand is still writing"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
def test_a_figure_written_as_its_bar_grows_keeps_its_write(tmp_path):
    """The H door's shape (row 18b: the figure on the page's first word, the bar still growing): nothing stood, so
    nothing waits - the figure is up from its word and writes on the base clock (FIGURE.WRITE over the word). The
    fixture's bars grow 4.4-7.4 s; the figure is written at 4.6."""
    world, _plate = _world("bars", CB.OBJ_20, tmp_path)
    at = 4.6
    P = _serve(world, [_figure("20%", at=at)])
    try:
        s = P.read(at + FIG_S * 0.1)
        assert s["figs"][0]["gop"] == 1, "the figure is up from its word"
        per = 0.6 / 3
        want = min(1.0, max(0.0, 0.1 / (per * 1.6)))
        assert abs(s["figs"][0]["glyphs"][0] - want) < 1e-3, (s["figs"][0]["glyphs"], want)
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
def test_the_value_comes_back_only_after_the_figure_has_gone(tmp_path):
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    leave_at, leave_s = FIG_AT + FIG_S + 1.0, 0.8
    P = _serve(world, [_figure("94%", leave_at=leave_at, leave_s=leave_s)])
    try:
        for k in (0.05, 0.25, 0.45, 0.55, 0.75, 0.95):
            s = P.read(leave_at + leave_s * k)
            val, fig = s["bars"][0]["val"]["eff"], s["figs"][0]["eff"]
            assert not (val > 0.05 and fig > 0.05), f"k={k}: value {val:.3f} and figure {fig:.3f} both up on the leave"
        back = P.read(leave_at + leave_s + 0.2)
        assert back["figs"][0]["eff"] == 0 and back["bars"][0]["val"]["eff"] == 1, back
        assert not P.errs, P.errs
    finally:
        P.close()


# ---- R26-256: the emphasized bar's pill yields --------------------------------------------------------------------


@needs_browser
def test_an_emphasized_bars_pill_yields_to_its_figure(tmp_path):
    world, _plate = _world("bars:0", CB.OBJ_20, tmp_path)
    P = _serve(world, [_figure("20%")])
    try:
        before = P.read(FIG_AT - 0.3)
        assert before["pill"] and before["pill"]["eff"] > 0.95, f"the fixture: the pill states the bar's number {before}"
        for t in HAND_TS:
            s = P.read(t)
            pill, fig = s["pill"]["eff"], s["figs"][0]["eff"]
            assert not (pill > 0.05 and fig > 0.05), f"t={t:.2f}: the pill ({pill:.3f}) and the figure ({fig:.3f}) both up"
        done = P.read(FIG_AT + FIG_S + 0.5)
        assert done["pill"]["eff"] == 0 and done["figs"][0]["eff"] == 1, done
        gate = P.m28(HAND_TS)
        assert gate.level in ("PASS", "INFO"), gate.message
        assert not P.errs, P.errs
    finally:
        P.close()


# ---- R26-255: a centred bar figure keeps its anchor on a page with chart states ------------------------------------


@needs_browser
def test_a_bars_page_with_a_chart_to_keeps_its_centred_figure_centred(tmp_path):
    """Acceptance (3): the wafer row rescales into a three-bar row (the bars move); its "3x" figure stays centred on
    its bar before, across and after the rescale - never re-placed beside it by the line rule."""
    world, _plate = _world("bars;then=fx-wafer-next:bars", CB.OBJ_13, tmp_path, oid="fx-wafer",
                           extra={"fx-wafer-next": CB.OBJ_13_NEXT}, stamp=False)
    species = [_figure("3x", 1, at=6.0), {"kind": "chart_to", "to": "rescale", "state": 1, "at": 10.0, "dur": 2.0}]
    P = _serve(world, species)
    try:
        for t in (8.5, 11.0, 13.0):
            s = P.read(t)
            fg, bar = s["figs"][0], s["bars"][1]
            assert fg["anchor"] == "middle", f"t={t}: the figure's anchor is {fg['anchor']!r} - re-placed by the line rule"
            fx, _ = _centre(fg["box"])
            bx, _ = _centre(bar["box"])
            assert abs(fx - bx) < 1.5, f"t={t}: the figure ({fx:.1f}) left its bar's centre ({bx:.1f})"
        assert not P.errs, P.errs
    finally:
        P.close()


# ---- R26-288: the ring circles the value, not the bar --------------------------------------------------------------


@needs_browser
@pytest.mark.parametrize("kind", ["callout", B.SPECIES_RING])
def test_a_ring_on_a_bars_value_circles_the_label_not_the_bar(kind, tmp_path):
    """Acceptance (2): on the 94 page the ring's ellipse is centred on "94%" and never crosses the bar's own name
    ("Capex, next two years") - at the base it circled the whole bar and crossed it."""
    world, _plate = _world("bars", CB.OBJ_94, tmp_path)
    P = _serve(world, [_ring(kind)])
    try:
        s = P.read(FIG_AT + 2.8)
        ring, val, lab = s["ring"], s["bars"][0]["val"]["box"], s["bars"][0]["lab"]
        assert ring, "the ring is drawn"
        rx, ry = _centre(ring)
        vx, vy = _centre(val)
        assert abs(rx - vx) < 6 and abs(ry - vy) < 6, f"the ring {ring} is centred on the value {val}"
        assert not _meets(ring, lab), f"the ring {ring} crosses the bar's name {lab}"
        assert ring[2] < s["bars"][0]["box"][2] * 1.5 + 60, f"and it is the value's size, not the bar's: {ring}"
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
def test_a_ring_on_a_value_rides_the_bar_a_compare_re_values(tmp_path):
    """After P69 T26a the halving's bar moves to 10 and its value label rides the new top: the ring on that value
    follows it (it reads the label's live box), landing on the moved top."""
    world, _plate = _world("bars", CB.OBJ_20, tmp_path)
    species = copy.deepcopy(CB.FIXTURES["row18-halving"][2]) + [_ring(at=CB.CMP_AT - 1.0, dur=5.0)]
    P = _serve(world, species)
    try:
        before = P.read(CB.CMP_AT - 0.3)
        after = P.read(CB.LAND_T + 0.2)
        assert before["ring"] and after["ring"], (before["ring"], after["ring"])
        _vx0, vy0 = _centre(before["bars"][0]["val"]["box"])
        _vx1, vy1 = _centre(after["bars"][0]["val"]["box"])
        assert vy1 - vy0 > 20, f"the fixture: the value rides the halved bar down ({vy0:.1f} -> {vy1:.1f})"
        _rx, ry1 = _centre(after["ring"])
        assert abs(ry1 - vy1) < 6, f"the ring ({ry1:.1f}) follows the moved value ({vy1:.1f})"
        assert not P.errs, P.errs
    finally:
        P.close()

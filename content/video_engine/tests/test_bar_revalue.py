"""P71 T24 (was P69 T72; the Bravos harvest v2 A48, R28, R30) - BARS RE-VALUED: THEN -> NOW.

Bravos D40 11:43-11:52 (measured in P71 T24 step (0), `u70oUWgVoYU` at 30 fps): the 6-week bill's $94B bar drops to
its 2016 average ($47B) in 0.83 s, HOLDS 3.5 s, and grows back to today in 0.70 s, a dashed level left at each top it
is not standing at - and the height is the number at every frame (5.79 px a billion at 47 and at 94).

Ours is the TWO-KEY PATH of `chart_to compare`: a compare that names `from` (the old value, SOURCED: `from.src`) and
`metric` (the bar's own value today) re-values its bar then -> now on the compare's own clock - the bar shrinks to
`from.value`, holds, and grows back to `metric.value`, landing as the window closes. The figure at the bar's top counts
WITH the bar (C14: the number at the top, never on the rule), a dashed UNLABELLED level stands at the top the bar has
left (the E53 addendum), and `from.label` is written beneath the figure while the bar stands at then.

  (1) THE GRAMMAR     `from` is validated by name: a bare number or a `from` with no source is refused (BRAVOS-USE-WHEN
                      A48's don't: "the old value is unsourced"); the path's two states are `from` and `metric`, so a
                      comparator / inputs / derive / form / then / hold / ghost beside it is refused by name; a printed
                      text whose numeral is not its value, a `from` equal to today or across zero, and a `from` off a
                      bars page are refused (a value drawn wrong is an untruth - s109 (c), E28).
  (2) THEN -> NOW     the bar stands at the built value before the word, at `from.value` through the hold, and back at
                      today after the window - monotone on each move, a pure function of t (a cold seek is the play).
  (3) M26             at every sampled instant the number printed at the bar's top is the height drawn, on the page's
                      own scale, within the print's own rounding. The layout probe's M26 is run over the same instants
                      and never FAILs (its reading of the figure is the stop condition this slice reports).
  (4) THE LEVELS      a dashed level at the top the bar has left: today's while the bar is down, the old value's once
                      it has grown back; none before the word; never through the figure.
  (5) ABSENT `from`   a compare without it validates and paints exactly as before (test_bar_value_morph's golden and the
                      H door are the byte proof).
  (6) THE GOLDEN      `bar-revalue-then-now`: H row 16's issuance - "twenty-eight" -> "a hundred and fifty" - at rest,
                      the bar back at $150B with the $28B level across it; the values read off the page's series file.
  (7) THE RECIPES     `recipe:revalue-then-the-ratio` (R28) and `recipe:ranked-dim-the-rest` (R30) are candidates
                      carrying their USE-WHEN.

The browser half needs playwright + chromium and is skipped without them.
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import gate_motion_density as GM  # noqa: E402
import probe as PR  # noqa: E402
import render_baseline as RB  # noqa: E402
import test_compare_on_bars as CB  # noqa: E402 - the served harness (R26-351's guarded opener underneath)

ASPECT = CB.ASPECT
GOLDEN = "bar-revalue-then-now"
SERIES = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-debt-issuance-line-v1.series.json"
RECIPES = ROOT / "content/video_engine/effects/recipes"

# ---- the fixture: H row 16's two figures, READ off the page's own series file (never re-typed) ----------------------
_DEBT = json.loads(SERIES.read_text(encoding="utf-8"))
_BY = {s["label"]: s["pts"] for s in _DEBT["series"]}
THEN_V = _BY["issuance"][0][1]            # 28: the 2020-24 annual AVERAGE (drawn flat across 2020-24)
NOW_V = _BY["$150B"][-1][1]               # 150: the top of the 2026 estimate range, "tracking toward a hundred and fifty"
OBJ = {"title": _DEBT["title"],
       "sub": "Hyperscaler bond issuance a year - 2026 is the top of the estimate range ($130-150B), 2020-24 an average",
       "src": _DEBT["src"], "unit": "$", "unit_suffix": "B",
       "bars": [{"label": "2026E, top of the range", "value": NOW_V, "color": "crimson"}]}
OID = "fx-debt-issuance-bars"
PLATE = f"ledger:{OID}:bars"
FIG_AT, FIG_S = 8.0, 1.5                  # the page has built (its bar grows 4.4-7.4 s on a page entered at 0)
AT, DUR = 11.0, 6.0                       # "twenty-eight" -> "a hundred and fifty": the bar lands back as the window closes
NOW_TEXT, THEN_TEXT = "$%gB" % NOW_V, "$%gB" % THEN_V
FIGURE = {"kind": "figure", "at": FIG_AT, "dur": FIG_S, "text": NOW_TEXT, "target": {"kind": "datum", "index": 0}}
REVALUE = {"kind": "chart_to", "at": AT, "dur": DUR, "to": "compare",
           "metric": {"value": NOW_V, "text": NOW_TEXT, "label": "this year, tracking toward"},
           "from": {"value": THEN_V, "text": THEN_TEXT, "label": "a year, 2020-24",
                    "src": "[SOURCE: ev-debt-issuance-line-v1 - the 2020-24 annual average (Morgan Stanley IM, Mellon via the dossier)]"},
           "source": "[SOURCE: ev-debt-issuance-line-v1 - the top of the 2026 projected range (PIMCO, Investing.com/LPL via the dossier)]"}
SPECIES = [FIGURE, REVALUE]


def _rev(**kw) -> dict:
    e = copy.deepcopy(REVALUE)
    for k, v in kw.items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    return e


def _errs(entry: dict, plate: str = PLATE, figure: dict = FIGURE) -> list[str]:
    return B.validate_species([figure, entry], (0, 0, 0), plate)


# ---- (1) the grammar -------------------------------------------------------------------------------------------

def test_a_sourced_then_to_now_compare_compiles():
    assert _errs(REVALUE) == []


@pytest.mark.parametrize("bad, why", [
    (28, "a bare number"),
    ({"value": 28, "text": "$28B"}, "no src"),
    ({"value": 28, "text": "$28B", "src": "  "}, "an empty src"),
    ({"value": 28, "text": "$28B", "src": "the dossier"}, "an untagged src"),
    ("lots", "a string"),
])
def test_a_from_with_no_source_is_refused_by_name(bad, why):
    errs = _errs(_rev(**{"from": bad}))
    assert errs, f"{why}: a `from` the row cannot source is a figure nobody stands behind (A48's don't)"
    assert any("from" in e and ("src" in e or "source" in e) for e in errs), errs


@pytest.mark.parametrize("bad", [{"value": "28"}, {"value": None}, {"value": float("nan")}])
def test_a_from_value_that_is_not_a_number_is_refused(bad):
    f = dict(REVALUE["from"], **bad)
    errs = _errs(_rev(**{"from": f}))
    assert any("from.value" in e for e in errs), errs


def test_a_from_text_that_is_not_its_value_is_refused():
    errs = _errs(_rev(**{"from": dict(REVALUE["from"], text="$38B")}))
    assert any("from.text" in e and "28" in e for e in errs), errs
    errs = _errs(_rev(metric=dict(REVALUE["metric"], text="$140B")), figure=dict(FIGURE, text="$140B"))
    assert any("metric.text" in e for e in errs), errs


def test_a_from_equal_to_today_or_across_zero_is_refused():
    assert any("from" in e and "today" in e for e in _errs(_rev(**{"from": dict(REVALUE["from"], value=150, text="$150B")})))
    assert any("from" in e and "zero" in e for e in _errs(_rev(**{"from": dict(REVALUE["from"], value=-5, text="-$5B")})))


@pytest.mark.parametrize("key, val", [
    ("comparator", {"value": 28, "text": "$28B", "label": "then"}), ("inputs", {"now": 150}), ("derive", "now"),
    ("form", "count"), ("then", "splash"), ("hold", "metric"), ("ghost", "yes")])
def test_the_two_key_path_refuses_the_comparator_paths_keys_by_name(key, val):
    errs = _errs(_rev(**{key: val}))
    assert any(repr(key) in e and "from" in e for e in errs), (key, errs)


def test_from_is_refused_off_a_bars_page():
    errs = _errs(REVALUE, plate="ledger:fx-debt-issuance-line:line")
    assert any("from" in e and "bars" in e for e in errs), errs


def test_the_from_path_still_needs_its_own_source_and_its_written_figure():
    assert any("source" in e for e in _errs(_rev(source=None)))
    assert any("figure" in e for e in B.validate_species([REVALUE], (0, 0, 0), PLATE))


def test_a_compare_without_from_validates_exactly_as_before():
    """(5) the comparator path's refusals are untouched: the halving golden's row is clean, a missing comparator
    is still refused with its old words."""
    assert B.validate_species(copy.deepcopy(G.HALVING_SPECIES), (0, 0, 0), "ledger:fx-index-concentration-bars:bars") == []
    bare = {k: v for k, v in G.HALVING_SPECIES[1].items() if k != "comparator"}
    errs = B.validate_species([G.HALVING_SPECIES[0], bare], (0, 0, 0), "ledger:fx-index-concentration-bars:bars")
    assert any("'comparator' must be" in e for e in errs), errs


# ---- (2)-(4) the player ------------------------------------------------------------------------------------------

needs_browser = CB.needs_browser

READ = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, PF = st.perform || { figures: [] }, S = st.scale || {};
  const stg = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return r.width > 0 ? [r.x - stg.x, r.y - stg.y, r.width, r.height] : null; };
  const eff = (el) => { let o = 1; for (let e = el; e && e.getAttribute; e = e.parentNode) { const a = e.getAttribute('opacity');
    if (a != null && a !== '') o *= +a; const cs = getComputedStyle(e); if (cs.display === 'none') return 0; o *= +cs.opacity; } return o; };
  const b = st.bars[0];
  const fg = (PF.figures || [])[0];
  const cells = fg ? (fg.__compare ? fg.__compare.cells : fg.lg) : [];
  const shown = cells.filter(ts => +(ts.getAttribute('opacity') == null ? 1 : ts.getAttribute('opacity')) > 0.5).map(ts => ts.textContent).join('').replace(/\\u00a0/g, ' ').trim();
  const sub = fg && fg.__compare && fg.__compare.sg ? fg.__compare.sg.map(ts => +(ts.getAttribute('opacity') || 0)) : [];
  const levels = [...st.chart.querySelectorAll('.lp-bar-level')].map(p => { const bb = p.getBBox();
    return { y: bb.y, x0: bb.x, x1: bb.x + bb.width, op: +(p.getAttribute('opacity') || 0), dash: p.getAttribute('stroke-dasharray'),
             stage: R(p), fill: p.getAttribute('fill') }; });
  return { y: +b.bar.getAttribute('y'), h: +b.bar.getAttribute('height'), x: +b.bar.getAttribute('x'), w: +b.bar.getAttribute('width'),
           box: R(b.bar), fig: fg ? { text: shown, box: R(fg.label), eff: eff(fg.g) } : null, sub,
           val: b.val ? { text: b.val.textContent, y: +b.val.getAttribute('y') } : null,
           my0: S.my(0), myNow: S.my(%s), myThen: S.my(%s), levels,
           ghosts: st.chart.querySelectorAll('.lp-bar-ghost').length };
}""" % (NOW_V, THEN_V)

DOWN_END = AT + min(0.83, 0.4 * DUR)
UP_START = AT + DUR - min(0.70, 0.4 * DUR)
LAND = AT + DUR
BEFORE_T = AT - 0.3
DOWN_TS = [round(AT + (DOWN_END - AT) * k / 8, 3) for k in range(1, 8)]
HOLD_TS = [round(DOWN_END + 0.2, 3), round((DOWN_END + UP_START) / 2, 3), round(UP_START - 0.1, 3)]
UP_TS = [round(UP_START + (LAND - UP_START) * k / 8, 3) for k in range(1, 8)]
AFTER_TS = [round(LAND + 0.05, 3), round(LAND + 0.8, 3)]
ALL_TS = [BEFORE_T, *DOWN_TS, *HOLD_TS, *UP_TS, *AFTER_TS]


class _Page(CB._Served):
    def read(self, t: float) -> dict:
        for _ in range(2):   # the probe's warm seek
            self.seek(t)
        return self.page.evaluate(READ)

    def probe(self, ts: list[float]) -> dict:
        insts = []
        for t in ts:
            for _ in range(2):
                self.seek(t)
            dom = self.page.evaluate(PR.READ_DOM)
            insts.append(PR.derive(dom, t, "p71-t24", {}, ASPECT, {}, self.page.evaluate(PR.READ_DOCKS)))
        return {"player_sha256": "x", "instants": insts}


def _world(tmp: Path) -> dict:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{OID}.series.json").write_text(json.dumps(OBJ), encoding="utf-8")
    world = CB._world_at(PLATE, tmp, ASPECT)
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


@pytest.fixture(scope="module")
def played(tmp_path_factory):
    """The re-value served once: every sampled instant in order (a PLAY), a seek back, and the probe's own read."""
    if not CB._chromium_available():
        pytest.skip("playwright chromium not installed")
    world = _world(tmp_path_factory.mktemp("rv"))
    P = _Page(*CB._one_scene(world, copy.deepcopy(SPECIES)))
    try:
        out = {t: P.read(t) for t in ALL_TS}
        out["back"] = P.read(HOLD_TS[1])
        out["back_up"] = P.read(UP_TS[3])
        out["probe"] = P.probe(ALL_TS)
        out["errs"] = list(P.errs)
    finally:
        P.close()
    C = _Page(*CB._one_scene(world, copy.deepcopy(SPECIES)))   # a COLD seek straight into the hold and the grow
    try:
        out["cold"] = C.read(HOLD_TS[1])
        out["cold_up"] = C.read(UP_TS[3])
    finally:
        C.close()
    return out


def _num(text: str) -> tuple[float, int]:
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", text or "")
    assert m, f"no number printed: {text!r}"
    s = m.group(0).replace(",", "")
    return float(s), (len(s) - s.index(".") - 1) if "." in s else 0


UNIT = 0.15      # chart units: a rect's attributes are written to one decimal
PX_UNIT = 0.1    # ... so the drawn value is known to a tenth of a chart unit


@needs_browser
def test_then_to_now_the_bar_stands_at_each_sourced_value_on_its_clock(played):
    assert not played["errs"], played["errs"]
    b = played[BEFORE_T]
    assert abs(b["y"] - b["myNow"]) < UNIT, ("before the word the bar is the built one, at today", b["y"], b["myNow"])
    assert b["fig"]["text"] == NOW_TEXT
    for t in HOLD_TS:
        p = played[t]
        assert abs(p["y"] - p["myThen"]) < UNIT, f"t={t}: through the hold the bar stands at {THEN_V} ({p['myThen']:.1f}), drawn {p['y']}"
        assert abs(p["y"] + p["h"] - p["my0"]) < UNIT, "and still on zero"
        assert p["fig"]["text"] == THEN_TEXT, (t, p["fig"])
        assert p["x"] == b["x"] and p["w"] == b["w"], "only the height moves"
    for t in AFTER_TS:
        p = played[t]
        assert abs(p["y"] - p["myNow"]) < UNIT and p["fig"]["text"] == NOW_TEXT, (t, p["y"], p["fig"])
    assert played[AFTER_TS[-1]]["y"] == b["y"] and played[AFTER_TS[-1]]["h"] == b["h"], "it lands back on the built attributes"


@needs_browser
def test_each_move_is_monotone_and_never_past_either_end(played):
    down = [played[t]["y"] for t in [BEFORE_T, *DOWN_TS, HOLD_TS[0]]]
    up = [played[t]["y"] for t in [HOLD_TS[-1], *UP_TS, AFTER_TS[0]]]
    assert all(b >= a - 1e-6 for a, b in zip(down, down[1:])), ("the shrink only ever lowers the top", down)
    assert all(b <= a + 1e-6 for a, b in zip(up, up[1:])), ("the grow only ever raises it", up)
    lo, hi = played[BEFORE_T]["myNow"], played[BEFORE_T]["myThen"]
    assert all(lo - UNIT <= y <= hi + UNIT for y in down + up), "never past either value"
    assert any(lo + 1 < y < hi - 1 for y in down) and any(lo + 1 < y < hi - 1 for y in up), "and in between mid-move"


@needs_browser
def test_m26_the_printed_number_is_the_drawn_height_at_every_sampled_instant(played):
    """(3) M26 by the chart's own arithmetic: the figure at the top prints the value the rect is drawn to, within
    half the print's last digit."""
    for t in ALL_TS:
        p = played[t]
        drawn = (p["my0"] - p["y"]) / (p["my0"] - p["myNow"]) * NOW_V
        printed, dec = _num(p["fig"]["text"])
        per_unit = NOW_V / (p["my0"] - p["myNow"])   # the value one chart unit of height carries
        tol = 0.5 * 10 ** -dec + PX_UNIT * per_unit   # the print's own rounding + the rect's one decimal
        assert abs(printed - drawn) <= tol, f"t={t}: prints {p['fig']['text']} over a bar drawn to {drawn:.2f} (E28, M26)"
        if p["val"]:
            v, d = _num(p["val"]["text"])
            assert abs(v - drawn) <= 0.5 * 10 ** -d + PX_UNIT * per_unit, \
                f"t={t}: the bar's own value label says {p['val']['text']} over {drawn:.2f}"


@needs_browser
def test_m26_the_layout_probe_never_fails_over_the_morph(played):
    fails, read, _worst = GM._value_faults(played["probe"])
    assert fails == [], fails
    print(f"M26 probe: {read} printed value(s) read over {len(ALL_TS)} instants")   # the figure is not the probe's to read


@needs_browser
def test_a_dashed_unlabelled_level_stands_at_the_top_the_bar_has_left(played):
    b = played[BEFORE_T]
    assert b["ghosts"] == 0, "the T26a ghost is the comparator path's; this path draws its levels"
    assert len(b["levels"]) == 2 and all(lv["op"] == 0 for lv in b["levels"]), ("none before the word", b["levels"])
    hold = played[HOLD_TS[1]]
    now_lv = min(hold["levels"], key=lambda lv: lv["y"])
    then_lv = max(hold["levels"], key=lambda lv: lv["y"])
    assert abs(now_lv["y"] - hold["myNow"]) < 1.5 and now_lv["op"] > 0.4, ("today's level stands where the bar was", now_lv)
    assert then_lv["op"] == 0, "the old value's level waits until the bar has left it"
    assert now_lv["dash"] and now_lv["fill"] == "none"
    assert now_lv["x0"] <= hold["x"] and now_lv["x1"] >= hold["x"] + hold["w"], "across the bar's own width"
    after = played[AFTER_TS[-1]]
    now_lv = min(after["levels"], key=lambda lv: lv["y"])
    then_lv = max(after["levels"], key=lambda lv: lv["y"])
    assert abs(then_lv["y"] - after["myThen"]) < 1.5 and then_lv["op"] > 0.4, ("the old value's level stays across the grown bar", then_lv)
    assert now_lv["op"] == 0, "today's level is gone once the bar stands on it"
    for t in ALL_TS:
        p = played[t]
        for lv in p["levels"]:
            if lv["op"] > 0.05 and lv["stage"] and p["fig"]["box"]:
                s, f = lv["stage"], p["fig"]["box"]
                assert not (s[0] < f[0] + f[2] and f[0] < s[0] + s[2] and s[1] < f[1] + f[3] and f[1] < s[1] + s[3]), \
                    f"t={t}: a level runs through the figure"


@needs_browser
def test_the_old_values_label_is_written_beneath_through_the_hold_and_leaves_on_the_grow(played):
    assert played[HOLD_TS[1]]["sub"] and all(o > 0.99 for o in played[HOLD_TS[1]]["sub"]), played[HOLD_TS[1]]["sub"]
    assert all(o < 0.01 for o in played[AFTER_TS[-1]]["sub"]), played[AFTER_TS[-1]]["sub"]


@needs_browser
def test_the_re_value_is_a_pure_function_of_t(played):
    assert played["back"] == played[HOLD_TS[1]], "a seek back lands the played frame"
    assert played["back_up"] == played[UP_TS[3]]
    assert played["cold"] == played[HOLD_TS[1]] and played["cold_up"] == played[UP_TS[3]], "a cold seek lands the played frame"


# ---- the pure frame (node) -------------------------------------------------------------------------------------

def _node(js: str) -> str:
    src = "import * as C from './content/video_engine/scripts/species/compare.mjs';\n" + js
    r = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, cwd=ROOT, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_the_frame_dials_are_the_measured_reference():
    got = json.loads(_node("console.log(JSON.stringify(C.REVALUE || null))"))
    assert got, "species/compare.mjs exports REVALUE"
    assert got["DOWN_S"] == 0.83 and got["UP_S"] == 0.7, "D40 706.67-707.50 and 711.00-711.70 (step (0), 30 fps)"


# ---- (6) the golden, (7) the recipes -----------------------------------------------------------------------------

def test_the_then_to_now_at_rest_is_a_committed_golden_surface():
    assert GOLDEN in G.SURFACES and GOLDEN in G.FRAME_T
    assert G.FRAME_T[GOLDEN] > LAND, "read at rest, after the bar has grown back"
    tl = json.loads((RB.SOURCES / f"{GOLDEN}.timeline.json").read_text(encoding="utf-8"))
    sp = tl["scenes"][0]["species"]
    assert [e["kind"] for e in sp] == ["figure", "chart_to"] and sp[1]["from"]["value"] == THEN_V and sp[1]["metric"]["value"] == NOW_V
    assert (RB.FRAMES / f"{GOLDEN}.png").exists(), f"render_baseline.py --update {GOLDEN}"


@needs_browser
def test_the_golden_frame_is_unchanged():
    assert RB.check([GOLDEN]) == []


@pytest.mark.parametrize("rid, members", [
    ("revalue-then-the-ratio", {"chart_to:compare", "page_species:bracket"}),
    ("ranked-dim-the-rest", {"page_builder:bars", "page_species:solo"}),
])
def test_both_recipes_are_candidates_with_their_use_when(rid, members):
    p = RECIPES / f"{rid}.json"
    assert p.exists(), f"recipe:{rid}"
    r = json.loads(p.read_text(encoding="utf-8"))
    assert r["id"] == f"recipe:{rid}" and r["status"] == "candidate" and r["count"] == 0
    assert members <= {m["card"] for m in r["members"]}, r["members"]
    assert {"act", "moment", "shape", "use", "dont"} <= set(r["use_when"]), r["use_when"]

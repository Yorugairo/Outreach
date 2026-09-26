"""P71 T25 (was P69 T74; the Bravos harvest v2 A50, A51, R31) - THE SCALE-OUT REVEAL AND THE PROJECTED OVERTAKE.

Bravos D40 15:01-15:30 (measured in P71 T25 step (0), `u70oUWgVoYU` at 30 fps): ONE bar stands alone on its own scale;
on the word the view widens to the whole field in 0.9 s - the neighbours entering at the plot's edges, the scale running
out to the field's - and a pill names its place, "18th Largest Holder" (a rank COMPUTED from the field). Later a new
bar SURGES past the field's leader (0.63 s) and a bracket names the margin.

Ours, on a STORY bars page's object:
  `opens_on: {bar, rank?}`  the page is BORN on that bar alone; `chart_to extend {field: true}` brings the field and the
                            pill writes "<computed ordinal> <phrase>".
  a bar `{label, projected: {value, label, tier, src}}`  a bar whose height IS a sourced projection - no `value` of its
                            own (E77); drawn on `chart_to extend {bar: k}`, DASHED (S3), its label written, a bracket to
                            #1 (the tallest ACTUAL bar) with the computed gap.

  (1) THE GRAMMAR    both keys whole, or refused BY NAME (a projection unlabelled, untiered, unsourced, a bare figure, a
                     `value` beside it, two of them, no field to pass; a rank phrase with a figure or ranking the other
                     way) - truth rules (s106); a projection that does not pass #1, a label with no estimate word and a
                     tie are WARNs.
  (2) THE NUMBERS    the rank, the leader and the gap are computed by ledger_page, never typed.
  (3) THE VERB       `chart_to extend` names `field: true` or `bar: k` on a bars page (refused by name when malformed);
                     the field comes first, each arrives once; a rescale, a form, a datum mark on the estimate and a
                     plate emphasis on it are refused on such a page.
  (4) THE LONE VIEW  born: the subject alone at the one-bar width inside the plot, every other bar outside the plot's
                     x span (clipped), their names and values unwritten.
  (5) THE SCALE-OUT  mid-clock the subject travels toward its slot, sinking into the taller scale, and a neighbour has
                     entered; after it, the field in its slots and the rank pill written.
  (6) THE OVERTAKE   before its word no projected bar; mid-surge it rises monotonically; at rest it stands dashed at its
                     projected height with its label, the bracket from its top to #1's column and the gap written; the
                     printed value is the drawn height (M26); a cold seek is the play.
  (7) THE GOLDEN     `projected-overtake` (H row 16's capex, the 2027 consensus passing the 2026 one) and the recipe.

The browser half needs playwright + chromium and is skipped without them.
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
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as L  # noqa: E402
import test_compare_on_bars as CB  # noqa: E402 - the served harness

ASPECT = CB.ASPECT
GOLDEN = "projected-overtake"
RECIPE = ROOT / "content/video_engine/effects/recipes/scale-out-then-the-overtake.json"
CAPEX = json.loads((ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/"
                    "ev-capex-consensus-v1.series.json").read_text(encoding="utf-8"))
_B = {b["label"]: b for b in CAPEX["bars"]}
START, NOW, NEXT = _B["Start of year"]["value"], _B["2026 consensus"]["value"], _B["2027 consensus"]["value"]   # 480 / 690 / 870, off the file
PSRC = "PIMCO, Figures 2-3 via the evidence dossier (B1) - the 2027 consensus"
OBJ = {"title": CAPEX["title"], "sub": "The five largest hyperscalers' capital spending, US$ billions - consensus estimates",
       "src": CAPEX["src"], "unit": "$", "unit_suffix": "B",
       "bars": [{"label": "Start of year", "value": START, "color": _B["Start of year"]["color"]},
                {"label": "2026 consensus", "value": NOW, "color": _B["2026 consensus"]["color"]},
                {"label": "2027 consensus", "color": _B["2027 consensus"]["color"],
                 "projected": {"value": NEXT, "label": "2027E consensus", "tier": "PLAUSIBLE", "src": PSRC}}]}
OPEN = dict(copy.deepcopy(OBJ), opens_on={"bar": "Start of year", "rank": "largest estimate"})
OID = "fx-capex-out"
PLATE = f"ledger:{OID}:bars"
FIELD = {"kind": "chart_to", "to": "extend", "at": 9.0, "dur": 2.0, "field": True}
SURGE = {"kind": "chart_to", "to": "extend", "at": 13.0, "dur": 2.5, "bar": 2}


def _v(obj: dict) -> list[str]:
    return L.validate(copy.deepcopy(obj), "bars")


def _with(bar: dict, **kw) -> dict:
    o = copy.deepcopy(OBJ)
    o["bars"][2] = dict(bar, **kw) if bar is not None else o["bars"][2]
    return o


def _proj(**kw) -> dict:
    o = copy.deepcopy(OBJ)
    o["bars"][2]["projected"].update(kw)
    return o


def _spec(obj: dict) -> dict:
    return L.build_spec(copy.deepcopy(obj), "bars", None, "right", builder="story")


# ---- (1) + (2) the object's grammar and its numbers --------------------------------------------------------------------
def test_a_projected_bar_validates_and_its_numbers_are_computed():
    assert _v(OBJ) == []
    sp = _spec(OBJ)
    assert sp["values"] == [START, NOW, NEXT], "the projected bar's height IS its projection"
    assert sp["projected"] == [None, None, {"label": "2027E consensus", "tier": "PLAUSIBLE", "src": PSRC}]
    assert sp["projected_to"] == {"index": 2, "lead": 1, "gap": float(NEXT - NOW), "text": "+$%gB" % (NEXT - NOW)}
    assert PSRC in sp["source"] and sp["source"].startswith(CAPEX["src"]), "the source line names the projection (s93)"
    assert "opens_on" not in sp and not any("WARN" in w for w in sp.get("warnings") or [])


@pytest.mark.parametrize("mut, needle", [
    (lambda o: o["bars"][2].__setitem__("projected", 870), "is an object"),
    (lambda o: o["bars"][2]["projected"].__setitem__("guess", 1), "`guess` is not a projected bar's key"),
    (lambda o: o["bars"][2]["projected"].pop("label"), "no `label`"),
    (lambda o: o["bars"][2]["projected"].__setitem__("label", "$870B"), "label"),
    (lambda o: o["bars"][2]["projected"].__setitem__("tier", "HOPE"), "`tier`"),
    (lambda o: o["bars"][2]["projected"].pop("src"), "no `src`"),
    (lambda o: o["bars"][2]["projected"].pop("value"), "is not a number"),
    (lambda o: o["bars"][2]["projected"].__setitem__("value", "lots"), "is not a number"),
    (lambda o: o["bars"][2]["projected"].__setitem__("value", -5), "surges UP"),
    (lambda o: o["bars"][2].__setitem__("value", 870), "no `value` beside it"),
    (lambda o: o["bars"][1].__setitem__("projected", {"value": 700, "label": "2026E", "tier": "PLAUSIBLE", "src": "x"}) or o["bars"][1].pop("value"), "ONE projected bar"),
    (lambda o: o.__setitem__("bars", [o["bars"][2]]), "no #1"),
    (lambda o: o["bars"][0].__setitem__("value", [400, 520]), "range"),
    (lambda o: o.__setitem__("overflow", "burst"), "breakthrough"),
])
def test_a_malformed_projection_is_refused_by_name(mut, needle):
    o = copy.deepcopy(OBJ)
    mut(o)
    errs = _v(o)
    assert any(needle in e for e in errs), errs
    assert not any("unknown key(s) ['projected']" in e for e in errs), "refused BY NAME, never as an unknown key"


def test_a_projection_on_a_panel_is_refused():
    o = {"title": "t", "src": "s", "panels": [{"sub": "a", "builder": "bars", "unit": "$", "bars": [
        {"label": "a", "value": 1}, {"label": "b", "projected": {"value": 2, "label": "2027E", "tier": "PLAUSIBLE", "src": "x"}}]}]}
    assert any("a page's OWN field" in e for e in L.validate(o, "line"))


def test_opens_on_validates_and_its_rank_is_computed():
    assert _v(OPEN) == []
    sp = _spec(OPEN)
    assert sp["opens_on"] == {"index": 0, "rank": 2, "of": 2, "text": "2nd largest estimate"}, sp["opens_on"]
    no_phrase = dict(copy.deepcopy(OPEN), opens_on={"bar": "2026 consensus"})
    assert _spec(no_phrase)["opens_on"] == {"index": 1, "rank": 1, "of": 2}, "no phrase: the rank is computed, no pill"


@pytest.mark.parametrize("oo, needle", [
    ("Start of year", "an object"),
    ({"bar": "Start of year", "sort": "desc"}, "`sort` is not an opens_on key"),
    ({"bar": "Nowhere"}, "is not a bar on this page"),
    ({"bar": "2027 consensus"}, "is the projection"),
    ({"bar": "Start of year", "rank": "18th largest"}, "carries a figure"),
    ({"bar": "Start of year", "rank": "smallest estimate"}, "ranks the other way"),
    ({"bar": "Start of year", "rank": ""}, "non-empty string"),
])
def test_a_malformed_opens_on_is_refused_by_name(oo, needle):
    o = dict(copy.deepcopy(OBJ), opens_on=oo)
    assert any(needle in e for e in _v(o)), _v(o)


def test_opens_on_is_refused_beside_a_rule_and_on_a_one_bar_field():
    assert any("comparator rule" in e for e in _v(dict(copy.deepcopy(OPEN), hlines=[{"y": 600, "label": "x"}])))
    one = {"title": "t", "src": "s", "bars": [{"label": "a", "value": 3}], "opens_on": {"bar": "a"}}
    assert any("no field to open onto" in e for e in _v(one))


def test_the_advice_is_a_warn_not_a_refusal():
    under = _proj(value=600)
    assert _v(under) == []
    assert any("does not pass the leader" in w for w in _spec(under)["warnings"])
    plain = _proj(label="Hyperscalers next year")
    assert _v(plain) == [] and any("no estimate word" in w for w in _spec(plain)["warnings"])
    tie = copy.deepcopy(OPEN)
    tie["bars"][1]["value"] = START
    assert _v(tie) == [] and any("ties" in w for w in _spec(tie)["warnings"])


def test_the_ordinal_is_english():
    assert [L._ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 18, 21, 22, 23, 101, 111, 112)] == \
        ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "18th", "21st", "22nd", "23rd", "101st", "111th", "112th"]


def test_a_page_naming_neither_key_is_the_object_it_was():
    plain = {"title": "t", "src": "s", "bars": [{"label": "a", "value": 1}, {"label": "b", "value": 2}]}
    assert L.with_projected_values(plain) is plain
    assert not {"opens_on", "projected", "projected_to"} & set(_spec(plain))


# ---- (3) the verb ----------------------------------------------------------------------------------------------------
def _errs(sp: dict) -> list[str]:
    return B.validate_species([sp], (0, 0, 0), PLATE)


def test_the_bars_extend_grammar():
    assert _errs(SURGE) == [] and _errs(FIELD) == []
    assert any("field is true or absent" in e for e in _errs(dict(FIELD, field=False)))
    assert any("is the index" in e for e in _errs(dict(SURGE, bar=-1)))
    assert any("is the index" in e for e in _errs(dict(SURGE, bar="2")))
    assert any("not both" in e for e in _errs(dict(SURGE, field=True)))
    assert any("to_index is the LINE's extend" in e for e in _errs(dict(SURGE, to_index=3)))
    line = {"kind": "chart_to", "to": "extend", "at": 1.0, "dur": 1.0}
    assert _errs(line) == ["chart_to extend: name exactly one of to_index (the datum the window grows to) or series "
                           "(a later: true series to draw on)"], "the line's extend reads as it did"


def _derive(obj: dict, species: list[dict], plate: str = PLATE) -> dict:
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / f"evidence/objects/{OID}.series.json").write_text(json.dumps(obj), encoding="utf-8")
        saved = B.ASPECT
        B.ASPECT = ASPECT
        try:
            world = B.world_for_plate(plate, (0, 0, 0), ep)
            B.stamp_full_stage(world["page"])
            B.derive_rescale_states(world, species, plate, ep)
        finally:
            B.ASPECT = saved
    return world


def test_the_field_then_the_projection_derive_two_flagged_states():
    sps = [copy.deepcopy(FIELD), copy.deepcopy(SURGE)]
    w = _derive(OPEN, sps)
    st = w["page_states"]
    assert [(s.get("opened"), s.get("projected_shown"), s.get("derived")) for s in st] == \
        [(True, False, "extend"), (True, True, "extend")]
    assert [sp["state"] for sp in sps] == [1, 2]
    assert "opened" not in w["page"] and w["page"]["opens_on"]["index"] == 0


def test_a_page_with_only_a_projection_derives_one_state():
    w = _derive(OBJ, [copy.deepcopy(SURGE)])
    assert [(s.get("projected_shown"), "opened" in s) for s in w["page_states"]] == [(True, False)]


@pytest.mark.parametrize("obj, species, needle", [
    (OBJ, [dict(SURGE, bar=0)], "is not a projected bar"),
    (OBJ, [SURGE, dict(SURGE, at=16.0)], "drawn already"),
    (OBJ, [FIELD], "does not open on one bar"),
    (OPEN, [SURGE], "the field"),
    (OPEN, [FIELD, dict(FIELD, at=11.5)], "already stands"),
    (OPEN, [FIELD, {"kind": "chart_to", "to": "rescale", "at": 12.0, "dur": 1.0, "ymax": 1000}], "moves by `extend`"),
    (OBJ, [SURGE, {"kind": "figure", "at": 16.0, "dur": 1.0, "text": "$870B", "target": {"kind": "datum", "index": 2}}], "is the projection"),
    ({"title": "t", "src": "s", "bars": [{"label": "a", "value": 1}, {"label": "b", "value": 2}]}, [SURGE], "names neither"),
])
def test_the_page_refuses_what_its_keys_cannot_carry(obj, species, needle):
    with pytest.raises(ValueError, match=re.escape(needle)):
        _derive(obj, copy.deepcopy(species))


def test_a_plate_emphasis_on_the_projection_is_refused():
    with pytest.raises(ValueError, match="count an estimate"):
        _derive(OBJ, [copy.deepcopy(SURGE)], plate=f"ledger:{OID}:bars:2")


def test_an_undrawn_projection_is_a_warn(capsys):
    _derive(OBJ, [])
    assert "no `chart_to extend {bar: 2}` draws it" in capsys.readouterr().out


# ---- (4)-(6) served ----------------------------------------------------------------------------------------------------
needs_browser = CB.needs_browser

READ = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const root = w.__lp, sts = root.states || [root];
  const op = (el) => { if (!el) return null; if (getComputedStyle(el).display === 'none') return 0; const a = el.getAttribute('opacity'); return a == null || a === '' ? 1 : +a; };
  const txt = (el) => el ? { text: (el.textContent || '').replace(/\\u00a0/g, ' '), op: op(el) } : null;
  const ln = (el) => el ? { x1: +el.getAttribute('x1'), x2: +el.getAttribute('x2'), y1: +el.getAttribute('y1'), y2: +el.getAttribute('y2'), op: op(el) } : null;
  return { active: root.active | 0, states: sts.map(S => ({
    chart: +(S.chart.style.opacity === '' ? 1 : S.chart.style.opacity), x0: (S.scale || {}).x0, x1: (S.scale || {}).x1,
    my: S.scale && S.scale.my ? [S.scale.my(0), S.scale.my(%s)] : null,
    bars: (S.bars || []).map(b => { const cs = getComputedStyle(b.bar); return { i: b.i, x: +b.bar.getAttribute('x'), w: +b.bar.getAttribute('width'),
      y: +b.bar.getAttribute('y'), h: +b.bar.getAttribute('height'), proj: b.bar.classList.contains('lp-bar-proj'), tf: b.bar.style.transform,
      clip: b.bar.getAttribute('clip-path'), dash: cs.strokeDasharray, fill: cs.fill, val: txt(b.val), lab: txt(b.lab) }; }),
    rank: S.out && S.out.rank ? { op: op(S.out.rank.g), text: S.out.rank.g.querySelector('text').textContent, box: S.out.rank.box } : null,
    proj: S.out && S.out.proj ? { tag: txt(S.out.proj.tag), lvl: ln(S.out.proj.lvl), drop: ln(S.out.proj.drop), gap: txt(S.out.proj.gapT) } : null })) };
}""" % NEXT


class _Page(CB._Served):
    def read(self, t: float) -> dict:
        for _ in range(2):
            self.seek(t)
        return self.page.evaluate(READ)


def _world_for(obj: dict, species: list[dict], tmp: Path) -> dict:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{OID}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        world = B.world_for_plate(PLATE, (0, 0, 0), tmp)
        B.stamp_full_stage(world["page"])
        B.derive_rescale_states(world, species, PLATE, tmp)
    finally:
        B.ASPECT = saved
    return world


T_ALONE, T_MID_OPEN, T_FIELD = 8.6, 9.45, 11.6
T_BEFORE, T_SURGES, T_REST = 12.8, [13.35, 13.5, 13.65, 13.8, 13.95], 16.5


@pytest.fixture(scope="module")
def played(tmp_path_factory):
    if not CB._chromium_available():
        pytest.skip("playwright chromium not installed")
    species = [copy.deepcopy(FIELD), copy.deepcopy(SURGE)]
    world = _world_for(copy.deepcopy(OPEN), species, tmp_path_factory.mktemp("so"))
    P = _Page(*CB._one_scene(world, copy.deepcopy(species)))
    try:
        out = {t: P.read(t) for t in [T_ALONE, T_MID_OPEN, T_FIELD, T_BEFORE, *T_SURGES, T_REST]}
        out["back"] = P.read(T_SURGES[2])
        out["errs"] = list(P.errs)
    finally:
        P.close()
    C = _Page(*CB._one_scene(world, copy.deepcopy(species)))
    try:
        out["cold"] = C.read(T_SURGES[2])
    finally:
        C.close()
    return out


def _vis(frame: dict, k: int) -> dict:
    return frame["states"][k]


@needs_browser
def test_born_alone_the_subject_stands_in_the_plot_and_the_field_outside_it(played):
    A = _vis(played[T_ALONE], 0)
    subj = next(b for b in A["bars"] if b["i"] == 0)
    others = [b for b in A["bars"] if b["i"] != 0]
    lo, hi = A["x0"] - 20, A["x1"] + 20
    assert lo <= subj["x"] and subj["x"] + subj["w"] <= hi, subj
    assert all(b["x"] >= hi or b["x"] + b["w"] <= lo for b in others), [(b["x"], b["w"]) for b in others]
    assert all(b["clip"] for b in A["bars"]), "every bar of the lone view is clipped to the plot"
    assert all(b["val"]["op"] == 0 and b["lab"]["op"] == 0 for b in others), "a bar outside the plot writes nothing"
    assert subj["val"]["op"] == 1 and subj["lab"]["op"] == 1
    assert not any(b["i"] == 2 for b in A["bars"]), "the projection is not drawn before its word"
    F = _vis(played[T_FIELD], 1)
    assert subj["w"] >= next(b for b in F["bars"] if b["i"] == 0)["w"] - 0.05, "alone, the bar stands at the one-bar width (the cap: never narrower than its slot)"


@needs_browser
def test_the_scale_out_carries_the_subject_to_its_slot_and_brings_the_field_in(played):
    A0, Am, F = _vis(played[T_ALONE], 0), _vis(played[T_MID_OPEN], 0), _vis(played[T_FIELD], 1)
    xs = lambda S, i: next(b for b in S["bars"] if b["i"] == i)["x"]
    assert min(xs(F, 0), xs(A0, 0)) + 1 < xs(Am, 0) < max(xs(F, 0), xs(A0, 0)) - 1, "mid-clock the subject travels between its lone place and its slot"
    lo, hi = Am["x0"] - 20, Am["x1"] + 20
    assert any(lo < b["x"] + b["w"] and b["x"] < hi for b in Am["bars"] if b["i"] != 0), "a neighbour has entered the plot"
    assert [b["i"] for b in F["bars"]] == [0, 1] and F["chart"] == 1
    assert all(b["val"]["op"] == 1 for b in F["bars"]), "the field's values are written"
    assert F["rank"] and F["rank"]["text"] == "2nd largest estimate" and F["rank"]["op"] == 1, F["rank"]
    y = lambda S, i: next(b for b in S["bars"] if b["i"] == i)["y"]
    assert y(A0, 0) < y(Am, 0) < y(F, 0), "the subject sinks into the field's taller scale"


@needs_browser
def test_the_projection_surges_dashed_labelled_and_bracketed_to_the_leader(played):
    B1 = _vis(played[T_BEFORE], 1)
    assert not any(b["proj"] for b in B1["bars"]) and B1["rank"]["op"] == 1
    ks = []
    for t in T_SURGES:
        S = _vis(played[t], 2)
        pb = next(b for b in S["bars"] if b["i"] == 2)
        m = re.search(r"scaleY\(([\d.]+)\)", pb["tf"])
        ks.append(float(m.group(1)) if m else 1.0)
    assert all(a <= b + 1e-9 for a, b in zip(ks, ks[1:])) and 0 < ks[0] < 1, ks
    R = _vis(played[T_REST], 2)
    pb = next(b for b in R["bars"] if b["i"] == 2)
    assert pb["proj"] and pb["dash"] not in ("none", "") and "rgba" in pb["fill"], pb
    assert pb["val"]["text"] == "$%gB" % NEXT and pb["val"]["op"] == 1
    assert R["proj"]["tag"] == {"text": "2027E consensus", "op": 1}
    lead = next(b for b in R["bars"] if b["i"] == 1)
    assert abs(R["proj"]["lvl"]["y1"] - pb["y"]) < 0.6 and abs(R["proj"]["lvl"]["x2"] - (lead["x"] + lead["w"])) < 0.6, "the level runs to #1's near edge"
    assert abs(R["proj"]["drop"]["y1"] - pb["y"]) < 0.6 and abs(R["proj"]["drop"]["y2"] - lead["y"]) < 0.6, "the drop spans the gap: the projection's top to #1's"
    assert R["proj"]["gap"] == {"text": "+$%gB" % (NEXT - NOW), "op": 1}
    assert R["rank"] is None, "the rank pill belongs to the field, not the overtake"


@needs_browser
def test_m26_the_projection_is_drawn_to_its_printed_value(played):
    R = _vis(played[T_REST], 2)
    my0, myv = R["my"]
    pb = next(b for b in R["bars"] if b["i"] == 2)
    assert abs(pb["y"] - myv) < 0.15 and abs(pb["h"] - (my0 - myv)) < 0.2, (pb, R["my"])


@needs_browser
def test_a_cold_seek_is_the_play_and_nothing_errs(played):
    assert played["cold"] == played[T_SURGES[2]] == played["back"]
    assert not played["errs"], played["errs"]


# ---- (7) the golden and the recipe -------------------------------------------------------------------------------------
def test_the_golden_and_the_recipe_are_registered():
    assert GOLDEN in G.SURFACES
    r = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert r["id"] == "recipe:scale-out-then-the-overtake" and r["status"] == "candidate" and r.get("use_when")

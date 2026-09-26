"""P73 T1 - A CLAIMED FIGURE ON A CHART.

A bars page may carry a figure that is SOMEONE'S CLAIM, not a sourced value, and draw it so no viewer mistakes it for
one. The author writes the bar's datum as usual (a value, or a RANGE `[lo, hi]`) and adds
`claim: {by, said, evidence, src, standing?}`:
  by        who said it ("Dylan Patel")                          - required, a name (no figure in it)
  standing  who they are ("SemiAnalysis")                        - optional; the label credits it (the operator,
                                                                   2026-09-26: the story's weight IS who said it)
  said      when (YYYY-MM-DD or YYYY-MM)                         - required
  evidence  "none" | an http(s) URL                              - required: what the speaker attached
  src       where it was said ("his post on X")                  - required: THAT he said it is the confirmed fact
                                                                   the page draws (E99 s93: an unsourced figure never
                                                                   draws; an attributed statement is sourced)
The page's own dials: `claim_form: outline | hatch` (the claim's body; default outline - measured, see NOTES) and
`claim_audit: true` (the attribution adds "no evidence attached" when evidence is "none"; off by default - the operator:
the label credits the speaker, the audit wording is for a page whose job is the audit).

  (1) THE GRAMMAR     refused by name: a claim that is not an object, an unknown key, no by / said / evidence / src, a
                      figure in `by`, a malformed date, evidence neither "none" nor a URL; a claim beside `projected`,
                      `members` or `segments`; a claim on a panel's or a tier's bar, or on a page that is not a story
                      bars page; a form (extruded / gauge) or a breakthrough on a page carrying one; the page dials
                      malformed, or named on a page with no claim.
  (2) THE SPEC        `claims` (per bar: None or {by, standing?, said, evidence, text[, audit]}), `claim_form`, and the
                      source line naming the speaker; a page with no claim gains not one key (byte-identical).
  (3) THE TRUTH       a claim is never an input to a computed label unless the label is marked (it says "claim" or
                      names the speaker): a bracket or level join from / to a claim bar, a compare whose figure stands
                      on a claim bar or whose comparator IS a claim, an equation term read off a claim (its result's
                      label), and the page's counting pill (a plate emphasis on a claim bar).
  (4) THE FRAME       at rest a claim bar is its series ink as an OUTLINE (no filled body), its figure quoted and its
                      speaker written over it inside its own slot, never over a neighbour's figure; `hatch` fills it
                      with a hatch in its ink; a solo on the claim at its word keeps its speaker lit and mutes the rest.
  (5) THE GOLDEN      `claim-bar` (the AMD RFSoC price page) + `claim-bar@proof-word` (the solo on "$1k" at its word).

The browser half needs playwright + chromium and is skipped without them.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as L  # noqa: E402
import render_baseline as RB  # noqa: E402
import test_compare_on_bars as CB  # noqa: E402 - the served harness

GOLDEN = "claim-bar"
# THE STORY'S PRICE PAGE - every figure off the research pack (P73 `amd-rfsoc/research/RESEARCH.md` s3), never typed
# from memory: DigiKey qty-1 prices for the part Patel linked and the part on Puzhi's board (sources/03, /06, CONFIRMED),
# the board itself on Crowd Supply (sources/02, CONFIRMED), AMD's own academic RFSoC board (sources/08, CONFIRMED) - and
# Patel's two figures from his post (sources/01: CONFIRMED that he said them; the figures carry no evidence).
PATEL = {"by": "Dylan Patel", "standing": "SemiAnalysis", "said": "2026-09-19", "evidence": "none",
         "src": "his post on X"}
OBJ = {"title": "One chip, six prices",
       "sub": "Thousands of US dollars - AMD's XCZU47DR RFSoC, and two boards built on an RFSoC",
       "src": "DigiKey qty 1 $35,979.02 (XCZU47DR-2FSVG1517I) and $31,354.40 (-2FFVE1156I), Crowd Supply $8,749 "
              "(PZSDR P047), Real Digital $2,499 (RFSoC 4x2, academic), all 2026-09-26",
       "unit": "$", "unit_suffix": "k", "readability": "longform",
       "bars": [{"label": "DigiKey list", "value": 36.0, "color": "crimson"},
                {"label": "The board's chip", "value": 31.4, "color": "crimson"},
                {"label": "Puzhi's board", "value": 8.75, "color": "cobalt"},
                {"label": "AMD's own board", "value": 2.5, "color": "cobalt"},
                {"label": "US volume", "value": [4, 5], "color": "amber", "claim": dict(PATEL, quote="$4-5k")},
                {"label": "China quote", "value": 1, "color": "amber", "claim": dict(PATEL, quote="$1k")}]}
NEG = {"title": "A claimed fall", "sub": "Percent change - a fixture, not a figure about the world", "src": "fixture",
       "unit": "%", "bars": [{"label": "a", "value": -8}, {"label": "b", "value": -20, "color": "crimson",
                                                           "claim": dict(PATEL, quote="-20")},
                             {"label": "c", "value": -5}]}
OID = "fx-rfsoc-prices"
PLATE = f"ledger:{OID}:bars"
CLAIM_AT = 12.0   # the claim's word in the golden: "...getting quoted a thousand dollars in China"
SOLO = {"kind": "solo", "at": CLAIM_AT, "dur": 0.6, "bar": 5}


def _v(obj: dict) -> list[str]:
    return L.validate(copy.deepcopy(obj), "bars")


def _spec(obj: dict, emphasize: int | None = None) -> dict:
    return L.build_spec(copy.deepcopy(obj), "bars", emphasize, "right")


def _claim(**kw) -> dict:
    o = copy.deepcopy(OBJ)
    for k, v in kw.items():
        if v is None:
            o["bars"][5]["claim"].pop(k, None)
        else:
            o["bars"][5]["claim"][k] = v
    return o


# ---- (1) the grammar ---------------------------------------------------------------------------------------------
def test_the_story_price_page_validates():
    assert _v(OBJ) == []
    assert L.CLAIM_KEY in L.BAR_FIELDS, "a claim is a bar's own key, never an unknown one"


@pytest.mark.parametrize("mut, needle", [
    (lambda o: o["bars"][5].__setitem__("claim", "Patel"), "is an object"),
    (lambda o: o["bars"][5]["claim"].__setitem__("guess", 1), "`guess` is not a claim's key"),
    (lambda o: o["bars"][5]["claim"].pop("by"), "no `by`"),
    (lambda o: o["bars"][5]["claim"].__setitem__("by", "Patel 1k"), "`by`"),
    (lambda o: o["bars"][5]["claim"].pop("said"), "no `said`"),
    (lambda o: o["bars"][5]["claim"].__setitem__("said", "last week"), "`said`"),
    (lambda o: o["bars"][5]["claim"].pop("evidence"), "no `evidence`"),
    (lambda o: o["bars"][5]["claim"].__setitem__("evidence", "trust me"), "`evidence`"),
    (lambda o: o["bars"][5]["claim"].pop("src"), "no `src`"),
    (lambda o: o["bars"][5]["claim"].__setitem__("standing", 7), "`standing`"),
    (lambda o: o["bars"][5]["claim"].__setitem__("quote", "about $1k"), "`quote`"),
    (lambda o: o["bars"][5]["claim"].__setitem__("quote", "$2k"), "does not read"),
    (lambda o: o["bars"][5]["claim"].__setitem__("quote", "$1000"), "magnitude"),
    (lambda o: o["bars"][5]["claim"].__setitem__("quote", "$1-2k"), "is a range"),
    (lambda o: o["bars"][4]["claim"].__setitem__("quote", "$4k"), "is one figure"),
    (lambda o: o["bars"][5].__setitem__("members", [{"name": "a"}, {"name": "b"}]), "membership"),
    (lambda o: o["bars"][5].__setitem__("segments", [{"label": "a", "value": 500}, {"label": "b", "value": 500}]), "stacked"),
    (lambda o: o.__setitem__("form", "extruded_bar"), "form"),
    (lambda o: o.__setitem__("overflow", "burst"), "breakthrough"),
    (lambda o: o.__setitem__("claim_form", "ghost"), "claim_form"),
    (lambda o: o.__setitem__("claim_audit", "yes"), "claim_audit"),
])
def test_a_malformed_claim_is_refused_by_name(mut, needle):
    o = copy.deepcopy(OBJ)
    mut(o)
    errs = _v(o)
    assert any(needle in e for e in errs), errs
    assert not any("unknown key(s) ['claim']" in e for e in errs), "refused BY NAME, never as an unknown key"


def test_a_claim_beside_a_projection_is_refused():
    o = copy.deepcopy(OBJ)
    o["bars"][5] = {"label": "China quote", "claim": dict(PATEL),
                    "projected": {"value": 1000, "label": "2027E", "tier": "PLAUSIBLE", "src": "x"}}
    assert any("projected" in e and "claim" in e for e in _v(o)), _v(o)


def test_the_page_dials_on_a_page_with_no_claim_are_refused():
    o = copy.deepcopy(OBJ)
    for b in o["bars"]:
        b.pop("claim", None)
    for key, val in (("claim_form", "hatch"), ("claim_audit", True)):
        errs = _v(dict(o, **{key: val}))
        assert any(key in e and "no claim" in e for e in errs), errs


def test_a_claim_on_a_panel_or_a_tier_bar_is_refused():
    panel = {"title": "t", "src": "s", "panels": [{"sub": "a", "builder": "bars", "unit": "$", "bars": [
        {"label": "a", "value": 1}, {"label": "b", "value": 2, "claim": dict(PATEL)}]}]}
    assert any("not a panel's" in e for e in L.validate(panel, "line")), L.validate(panel, "line")


def test_a_claim_on_a_line_page_is_refused_by_name():
    line = {"title": "t", "src": "s", "unit": "$", "series": [{"name": "a", "pts": [[2020, 1], [2021, 2], [2022, 3]],
                                                             "claim": dict(PATEL)}]}
    errs = L.validate(line, "line")
    assert any("claim" in e and "bars page" in e for e in errs), errs


# ---- (2) the spec -----------------------------------------------------------------------------------------------------
def test_the_spec_carries_each_claim_and_the_source_names_the_speaker():
    sp = _spec(OBJ)
    assert sp["values"][4:] == [4, 1], "a range claim draws to its near end, as every range does (P69 T8d)"
    assert sp["ranges"][4] == [4, 5]
    assert sp["claims"][:4] == [None] * 4
    want = {"by": "Dylan Patel", "standing": "SemiAnalysis", "said": "2026-09-19", "evidence": "none",
            "text": "Dylan Patel, SemiAnalysis"}
    assert sp["claims"][4] == want and sp["claims"][5] == want, sp["claims"]
    assert sp["claim_form"] == "outline", "the default form"
    assert sp["value_strings"][4:] == ["4\u20135", "1"], "a quoted figure is written as he wrote it (the page adds its $ and k)"
    assert sp["value_strings"][:4] == ["36.0", "31.4", "8.75", "2.5"], "a sourced figure is the page's own"
    assert sp["source"].startswith(OBJ["src"]), "the page's own source line stands first"
    tail = sp["source"][len(OBJ["src"]):]
    assert "Dylan Patel" in tail and "SemiAnalysis" in tail and "2026-09-19" in tail and "his post on X" in tail, tail
    assert "US volume" in tail and "China quote" in tail, "the clause names which bars are his"
    assert "evidence" not in tail, "the audit wording is a dial, off by default (the operator, 2026-09-26)"


def test_the_audit_dial_writes_that_no_evidence_is_attached():
    sp = _spec(dict(copy.deepcopy(OBJ), claim_audit=True))
    assert sp["claims"][5]["audit"] == L.CLAIM_AUDIT_TEXT
    assert L.CLAIM_AUDIT_TEXT in sp["source"]
    linked = _claim(evidence="https://example.org/quote.pdf")
    linked["claim_audit"] = True
    sp2 = _spec(linked)
    assert "audit" not in sp2["claims"][5], "a claim with evidence attached carries no audit line"


def test_the_hatch_dial_and_the_standing_is_optional():
    sp = _spec(dict(copy.deepcopy(OBJ), claim_form="hatch"))
    assert sp["claim_form"] == "hatch"
    bare = _spec(_claim(standing=None))
    assert bare["claims"][5]["text"] == "Dylan Patel" and "standing" not in bare["claims"][5]


def test_a_page_with_no_claim_gains_not_one_key():
    o = copy.deepcopy(OBJ)
    for b in o["bars"]:
        b.pop("claim", None)
    sp = _spec(o)
    assert "claims" not in sp and "claim_form" not in sp and sp["source"] == OBJ["src"]


# ---- (3) the truth: a claim never feeds a computed label unmarked -------------------------------------------------------
def test_a_label_is_marked_by_the_word_claim_or_the_speakers_name():
    c = [_spec(OBJ)["claims"][5]]
    assert L.claim_label_marked("claimed vs listed", c)
    assert L.claim_label_marked("36x on Patel's figure", c)
    assert not L.claim_label_marked("36x", c)
    assert not L.claim_label_marked("", c) and not L.claim_label_marked(None, c)


def _world(obj: dict = OBJ, emphasize: str = "", aspect: str = "16:9") -> tuple[dict, Path]:
    import tempfile
    td = Path(tempfile.mkdtemp())
    (td / "evidence/objects").mkdir(parents=True)
    (td / f"evidence/objects/{OID}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        return B.world_for_plate(PLATE + emphasize, (0, 0, 0), td), td
    finally:
        B.ASPECT = saved


@pytest.mark.parametrize("sp", [
    {"kind": "bracket", "at": 3.0, "dur": 1.0, "from": 0, "to": 5, "label": "36x"},
    {"kind": "level_join", "at": 3.0, "dur": 1.0, "from": 5, "to": 0, "label": "36x"},
])
def test_a_bracket_or_level_join_on_a_claim_bar_needs_a_marked_label(sp):
    world, _ = _world()
    with pytest.raises(ValueError, match="claim"):
        B.check_claims(world, [dict(sp)])
    B.check_claims(world, [dict(sp, label="36x on Patel's figure")])   # marked: it stands
    B.check_claims(world, [dict(sp, to=1) if sp["kind"] == "bracket" else dict(sp, **{"from": 1})])   # two sourced bars


def test_a_compare_on_a_claim_reads_claimed_vs_listed():
    world, _ = _world()
    fig = {"kind": "figure", "at": 2.0, "dur": 1.0, "text": "$1k", "target": {"kind": "datum", "index": 5}}
    cmp_ = {"kind": "chart_to", "at": 4.0, "dur": 3.0, "to": "compare",
            "metric": {"value": 1, "text": "$1k", "label": "China"},
            "comparator": {"value": 36.0, "text": "$36.0k", "label": "DigiKey"},
            "inputs": {}, "derive": "36.0", "source": "[SOURCE: DigiKey]"}
    with pytest.raises(ValueError, match="claimed vs listed"):
        B.check_claims(world, [fig, cmp_])
    ok = copy.deepcopy(cmp_)
    ok["metric"]["label"] = "claimed"
    ok["comparator"]["label"] = "listed"
    B.check_claims(world, [fig, ok])
    # the other way: a SOURCED bar's figure compared to the claim's value
    fig0 = dict(fig, text="$36.0k", target={"kind": "datum", "index": 0})
    rev = {"kind": "chart_to", "at": 4.0, "dur": 3.0, "to": "compare",
           "metric": {"value": 36.0, "text": "$36.0k", "label": "DigiKey"},
           "comparator": {"value": 1, "text": "$1k", "label": "China"},
           "inputs": {}, "derive": "1", "source": "[SOURCE: x]"}
    with pytest.raises(ValueError, match="claimed vs listed"):
        B.check_claims(world, [fig0, rev])


def test_at_9x16_a_source_line_that_would_drop_the_speaker_is_refused():
    cut = dict(copy.deepcopy(OBJ), src="DigiKey; Crowd Supply; Real Digital, 2026-09-26")
    with pytest.raises(ValueError, match="unattributed"):
        _world(cut, aspect="9:16")
    _world(cut)                      # at 16:9 the whole line is written
    _world(OBJ, aspect="9:16")       # no ';': the speaker survives the portrait cut


def test_the_counting_pill_never_stands_on_a_claim():
    with pytest.raises(ValueError, match="claim"):
        _world(emphasize=":5")
    world, _ = _world(emphasize=":0")   # a sourced bar's pill stands
    assert world["page"]["emphasize"] == 0


def test_the_row_check_runs_where_the_page_species_are_checked():
    world, td = _world()
    with pytest.raises(ValueError, match="claim"):
        B.derive_rescale_states(world, [{"kind": "bracket", "at": 3.0, "dur": 1.0, "from": 0, "to": 5, "label": "36x"}],
                                PLATE, td)


def test_an_equation_term_read_off_a_claim_needs_its_result_marked():
    _, td = _world()
    oid = "ev-rfsoc-prices"
    (td / f"evidence/objects/{oid}.series.json").write_text(json.dumps(OBJ), encoding="utf-8")
    eq = {"kind": "equation", "at": 1.0, "dur": 6.0, "target": {"kind": "region", "x0": 0.1, "y0": 0.1, "x1": 0.9, "y1": 0.3},
          "terms": [{"text": "$35,979", "value": 35979, "at": 1.0, "src": oid, "tier": "CONFIRMED"},
                    {"text": "$1,000", "value": 1000, "at": 2.0, "src": oid, "tier": "CONFIRMED"}],
          "ops": ["\u00f7"], "result": {"text": "36x", "value": 36, "at": 3.0}}
    dirs = (td / "evidence/objects",)
    errs = B.equation_claim_errors(eq, dirs)
    assert errs and "claim" in errs[0] and "term 2" in errs[0], errs
    marked = copy.deepcopy(eq)
    marked["result"]["label"] = "on Patel's figure"
    assert B.equation_claim_errors(marked, dirs) == []
    sourced = copy.deepcopy(eq)
    sourced["terms"][1] = {"text": "$8,749", "value": 8749, "at": 2.0, "src": oid, "tier": "CONFIRMED"}
    assert B.equation_claim_errors(sourced, dirs) == []


# ---- (4) the frame -----------------------------------------------------------------------------------------------------
READ = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const S = w.__lp, R = (el) => { if (!el) return null; const r = el.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; };
  const op = (el) => { let a = 1; for (let n = el; n && n.nodeType === 1; n = n.parentNode) { const cs = getComputedStyle(n);
    a *= (+cs.opacity) * (n.getAttribute('fill-opacity') != null ? +n.getAttribute('fill-opacity') : 1) * (+(cs.fillOpacity || 1)); } return +a.toFixed(3); };
  return { bars: S.bars.map(b => { const cs = getComputedStyle(b.bar);
    return { i: b.i, claim: b.bar.classList.contains('lp-bar-claim'), fill: cs.fill, stroke: cs.stroke, sw: cs.strokeWidth,
      dash: cs.strokeDasharray, fig: R(b.val.querySelector('.lp-claim-fig')), val: b.val.textContent, shown: getComputedStyle(b.val).display !== "none", box: R(b.val), bar: R(b.bar), op: op(b.val), barOp: +cs.opacity,
      by: Array.from(b.val.querySelectorAll('.lp-claim-by')).map(t => ({ text: t.textContent, box: R(t),
        fs: parseFloat(getComputedStyle(t).fontSize) })) }; }),
    src: (w.querySelector('.lp-src') || {}).textContent || '' };
}"""


def _one_scene(world: dict, species: list[dict], aspect: str = "16:9") -> tuple[dict, dict]:
    """The served timeline - the long form's page takes its Inter faces (longform_assets), as the golden does."""
    tl, uris = CB._one_scene(world, species, aspect)
    return tl, dict(uris, **B.longform_assets(tl))


class _Page(CB._Served):
    def read(self, t: float) -> dict:
        for _ in range(2):
            self.seek(t)
        return self.page.evaluate(READ)


REST = 8.0
T_WORD = CLAIM_AT + 0.8


@pytest.fixture(scope="module")
def played():
    if not CB._chromium_available():
        pytest.skip("playwright chromium not installed")
    out = {}
    dials = {"outline": {}, "hatch": {"claim_form": "hatch"}, "audit": {"claim_audit": True}}
    for form, keys in dials.items():
        obj = dict(copy.deepcopy(OBJ), **keys)
        world, _ = _world(obj)
        B.stamp_full_stage(world["page"])
        P = _Page(*_one_scene(world, [copy.deepcopy(SOLO)]))
        try:
            out[form] = {"rest": P.read(REST), "word": P.read(T_WORD), "errs": list(P.errs)}
        finally:
            P.close()
    world, _ = _world(copy.deepcopy(NEG))   # a claimed FALL: the figure hangs under its bar, the speaker under it
    B.stamp_full_stage(world["page"])
    P = _Page(*_one_scene(world, []))
    try:
        out["fall"] = {"rest": P.read(REST), "errs": list(P.errs)}
    finally:
        P.close()
    world, _ = _world(copy.deepcopy(OBJ), aspect="9:16")   # the portrait page: narrow slots, the thinned row
    P = _Page(*_one_scene(world, [copy.deepcopy(SOLO)], "9:16"), aspect="9:16")
    try:
        out["portrait"] = {"rest": P.read(REST), "errs": list(P.errs)}
    finally:
        P.close()
    return out


def _overlap(a, b) -> bool:
    return a and b and a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


@CB.needs_browser
def test_a_claim_bar_is_an_outline_in_its_ink_and_a_sourced_bar_stays_filled(played):
    rest = played["outline"]["rest"]
    assert not played["outline"]["errs"], played["outline"]["errs"]
    for b in rest["bars"]:
        if b["i"] in (4, 5):
            assert b["claim"] and b["fill"] == "none", b
            assert b["stroke"] not in ("none", "") and float(b["sw"].rstrip("px")) > 0, b
            assert b["dash"] in ("none", ""), "a claim is not dashed - the dash is a projection's (S3 / E77)"
        else:
            assert not b["claim"] and b["fill"] != "none", b


@CB.needs_browser
@pytest.mark.parametrize("dial", ["outline", "audit", "portrait"])
def test_a_claim_figure_is_quoted_and_names_its_speaker_inside_its_slot(played, dial):
    bars = played[dial]["rest"]["bars"]
    for b in bars:
        if b["i"] not in (4, 5):
            assert "\u201c" not in b["val"] and not b["by"], b
            continue
        assert b["shown"], "a claim's figure is never thinned - it carries its speaker"
        assert "\u201c" in b["val"] and "\u201d" in b["val"], b["val"]
        said = " ".join(t["text"] for t in b["by"])
        if dial == "portrait":   # a narrow slot takes the ladder's name rung; the full credit stands on the source line
            assert "Patel" in said, said
        else:
            assert "Dylan Patel" in said and "SemiAnalysis" in said, said
        assert ("no evidence" in said and "attached" in said) == (dial == "audit"), said
        others = [o for o in bars if o["i"] != b["i"]]
        for t in b["by"]:
            em = b["fig"][3] - b["fig"][1]   # the boxes are EM boxes, not ink: the figure's box runs a fifth over its caps
            assert t["box"][3] <= b["fig"][1] + 0.2 * em, "the speaker stands over the figure"
            assert not any(_overlap(t["box"], o["box"]) for o in others), (t, [o["box"] for o in others])
            assert not any(_overlap(t["box"], o["bar"]) for o in others), "never over a neighbour's bar"
        shown = [o for o in others if o["shown"]]
        assert not any(_overlap(b["box"], o["box"]) for o in shown), "the quoted figure meets no neighbour's figure"
    assert "Dylan Patel, SemiAnalysis" in " ".join(played[dial]["rest"]["src"].replace("\xa0", " ").split()), "the source line credits the speaker"


@CB.needs_browser
def test_the_hatch_form_fills_the_claim_with_a_pattern_in_its_ink(played):
    for b in played["hatch"]["rest"]["bars"]:
        if b["i"] in (4, 5):
            assert b["claim"] and b["fill"].startswith("url("), b
        else:
            assert not b["claim"], b


@CB.needs_browser
def test_a_solo_on_the_claim_keeps_its_speaker_lit_and_mutes_the_rest(played):
    word = played["outline"]["word"]["bars"]
    lit = next(b for b in word if b["i"] == 5)
    other = next(b for b in word if b["i"] == 4)
    assert lit["op"] > 0.95 and lit["barOp"] > 0.95, lit
    assert other["op"] < 0.6 and other["barOp"] < 0.6, other


@CB.needs_browser
def test_a_claimed_fall_hangs_its_figure_and_its_speaker_under_the_bar(played):
    b = next(x for x in played["fall"]["rest"]["bars"] if x["i"] == 1)
    assert b["claim"] and b["shown"] and b["by"], b
    assert b["fig"][1] >= b["bar"][3] - 0.5, "the figure hangs under the bar (E28: the side is the sign)"
    assert all(t["box"][1] >= b["fig"][3] - 0.5 for t in b["by"]), "the speaker hangs under the figure"
    assert "-20" in b["val"], b["val"]


# ---- (5) the golden ----------------------------------------------------------------------------------------------------
def test_the_golden_is_listed_and_draws_the_story_page():
    import test_golden_frames as TG
    assert GOLDEN in TG.SURFACES and GOLDEN in G.SURFACES
    assert f"{GOLDEN}@proof-word" in RB.PROOF_FRAMES
    assert G.claim_price_object() == OBJ, "the golden draws the page this file proves"

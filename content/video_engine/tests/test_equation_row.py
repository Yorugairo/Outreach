"""P70 T6 (was P69 T56) - THE EQUATION ROW: the inputs, the relation and the signed result, in spoken order.

The Bravos harvest v2's T38 ("Equation row: inputs, relation, signed result", DOM 09:30-09:39: 3 %, 5 %, "Real Yield"
-2 %) and A60 ("Equation built in spoken order"). The token is a STAGE species:
`{kind: "equation", at, dur, target: region, terms: [{text, value, at, src? | tier?}] (2-3), ops: [x | − | + | ÷]
(one fewer), result: {text, value, at}}`. Each term is written by the hand on its own word, strictly in order with the
result last; the operators spring in between, and "=" lands with the result.

The law and the painter are species/equation.mjs (pinned by tests/kinetics/equation.test.mjs). This file pins the
compiler's grammar and its ARITHMETIC TRUTH RULE (the compiler computes the result left to right; a written result
that disagrees beyond its text's precision is refused, and so is a term whose text is not its value), the gate's
events, the registries, the engine's wiring, the card, and the row read on the SERVED player (the golden
`equation-halving`, H row 18's "a fifth ... fall by half ... erases ten percent").
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import lint_species_choice as L  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
MODULE = ROOT / "content/video_engine/scripts/species/equation.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/species.json"
PAGE = "ledger:ev-index-concentration-bars-v1:bars"
PLATE = "plate-desk"
MINUS = "−"
REGION = {"kind": "region", "x0": 0.06, "y0": 0.15, "x1": 0.72, "y1": 0.29}
ROOM = {"kind": "region", "x0": 0.06, "y0": 0.13, "x1": 0.72, "y1": 0.296}   # the golden's band: a NAMED row fits it
# H row 18 on the take: "At a fifth" 400.18, "fall by half" 402.38, "erases ten percent" 403.62
EQ = {"kind": "equation", "at": 400.18, "dur": 6.0, "target": REGION,
      "terms": [{"text": "20%", "value": 20, "at": 400.18, "src": "ev-index-concentration-bars-v1", "tier": "PLAUSIBLE"},
                {"text": MINUS + "½", "value": -0.5, "at": 402.38, "tier": "scenario"}],
      "ops": ["×"],
      "result": {"text": MINUS + "10%", "value": -10, "at": 403.62}}


def _eq(**patch) -> dict:
    out = json.loads(json.dumps(EQ))
    for k, v in patch.items():
        if v is None:
            out.pop(k, None)
        else:
            out[k] = v
    return out


def _errs(entries, plate=PAGE, ken=(0, 0, 0)):
    return B.validate_species([json.loads(json.dumps(e)) for e in entries], ken, plate)


def _own(errs: list[str]) -> list[str]:
    """The equation's OWN refusals - never the unknown-kind line, whose repr of the entry carries every key's name."""
    return [e for e in errs if e.startswith("equation")]


def _term(text, value, at, **kw):
    return dict({"text": text, "value": value, "at": at, "tier": "scenario"}, **kw)


# ---- the grammar -------------------------------------------------------------------------------------------------


def test_the_token_is_a_stage_species_laid_out_in_a_region():
    assert "equation" in B.SPECIES_KINDS and "equation" not in B.PAGE_SPECIES
    assert B.SPECIES_TARGETS["equation"] == ("region",), "the row's ROOM is declared, as a flow's is"
    assert _errs([EQ]) == []
    assert _errs([EQ], plate=PLATE) == [], "a stage species: a plate takes it as a page does"


def test_three_inputs_and_every_operator_are_the_grammar():
    three = _eq(terms=[_term("2", 2, 400.2), _term("3", 3, 401.0), _term("4", 4, 401.8)], ops=["+", "x"],
                result={"text": "20", "value": 20, "at": 402.6})
    assert _errs([three]) == [], "left to right: (2 + 3) x 4"
    for op, value, text in (("x", -10, MINUS + "10%"), ("×", -10, MINUS + "10%"), ("÷", -40, MINUS + "40%")):
        assert _errs([_eq(ops=[op], result={"text": text, "value": value, "at": 403.62})]) == [], op
    fall = dict(EQ["terms"][1], text=MINUS + "5%", value=-5)   # + and - add ONE unit: a % and a %
    for op, value, text in ((MINUS, 25, "25%"), ("-", 25, "25%"), ("+", 15, "15%")):
        assert _errs([_eq(terms=[EQ["terms"][0], fall], ops=[op], result={"text": text, "value": value, "at": 403.62})]) == [], op
    assert any("ONE unit" in e for e in _own(_errs([_eq(ops=["+"], result={"text": "19.5%", "value": 19.5, "at": 403.62})]))), \
        "20% + (-1/2) adds a % and a plain number (review F2)"


def test_real_yield_the_bravos_row_is_a_difference_of_two_sourced_inputs():
    """The validator checks the SHAPE of an id; that the object exists is `equation_row_checks` in main(), where the
    episode's evidence dir is known (test_a_src_names_an_object_on_disk). These two ids are fixtures, not H's."""
    real = _eq(terms=[_term("3%", 3, 400.2, tier="CONFIRMED", src="ev-fixture-coupon-v1"),
                      _term("5%", 5, 401.4, src="ev-fixture-cpi-v1")],
               ops=[MINUS], result={"text": MINUS + "2%", "value": -2, "at": 402.6})
    assert _errs([real]) == []
    bare = _eq(terms=[_term("3%", 3, 400.2, tier="CONFIRMED"), _term("5%", 5, 401.4, src="ev-fixture-cpi-v1")],
               ops=[MINUS], result={"text": MINUS + "2%", "value": -2, "at": 402.6})
    assert any("grades a source" in e for e in _own(_errs([bare]))), "a bare CONFIRMED is self-certification (F3)"


@pytest.mark.parametrize("patch, needle", [
    ({"terms": [_term("20%", 20, 400.18)], "ops": []}, "2 to 3"),
    ({"terms": [_term("1", 1, 400.2), _term("1", 1, 400.6), _term("1", 1, 401.0), _term("1", 1, 401.4)],
      "ops": ["+", "+", "+"]}, "2 to 3"),
    ({"ops": []}, "one fewer"),
    ({"ops": ["×", "+"]}, "one fewer"),
    ({"ops": ["^"]}, "operator"),
    ({"result": None}, "result"),
    ({"result": {"text": MINUS + "10%", "value": -10}}, "not spoken"),
    ({"result": {"text": MINUS + "10%", "value": -10, "at": 403.62, "src": "ev-x-v1"}}, "computed"),
    ({"target": {"kind": "point", "x": 0.4, "y": 0.2}}, "not allowed"),
    ({"label": "real yield"}, "'label'"),
])
def test_a_malformed_row_is_refused_by_name(patch, needle):
    errs = _errs([_eq(**patch)])
    assert any(needle in e for e in _own(errs)), errs


@pytest.mark.parametrize("term, needle", [
    ({"value": 20, "at": 400.18, "tier": "PLAUSIBLE"}, "'text'"),
    ({"text": "20%", "at": 400.18, "tier": "PLAUSIBLE"}, "'value'"),
    ({"text": "20%", "value": 20, "tier": "PLAUSIBLE"}, "'at'"),
    ({"text": "20%", "value": 20, "at": 400.18}, "src"),                                   # unsourced: the don't
    ({"text": "20%", "value": 20, "at": 400.18, "tier": "UNSOURCED-editorial"}, "tier"),
    ({"text": "20%", "value": 20, "at": 400.18, "src": "index concentration"}, "evidence object"),
    ({"text": "20%", "value": 20, "at": 400.18, "tier": "PLAUSIBLE", "color": "neg"}, "'color'"),
])
def test_a_malformed_term_is_refused_by_name(term, needle):
    errs = _errs([_eq(terms=[term, EQ["terms"][1]])])
    assert any(needle in e for e in _own(errs)), errs


# ---- spoken order (A60) --------------------------------------------------------------------------------------------


@pytest.mark.parametrize("ats, result_at, needle", [
    ((402.38, 400.18), 403.62, "in order"),          # the second input before the first
    ((400.18, 400.18), 403.62, "in order"),          # two inputs on one word
    ((400.18, 402.38), 402.0, "last"),               # the result before the last input
    ((400.18, 402.38), 402.38, "last"),              # ... or on its word
    ((399.0, 402.38), 403.62, "before the row's own at"),
    ((400.18, 402.38), 405.8, "window"),             # the result cannot finish being written before the row leaves
])
def test_each_term_lands_on_its_own_word_in_order_with_the_result_last(ats, result_at, needle):
    terms = [dict(EQ["terms"][0], at=ats[0]), dict(EQ["terms"][1], at=ats[1])]
    errs = _errs([_eq(terms=terms, result=dict(EQ["result"], at=result_at))])
    assert any(needle in e for e in errs), errs


def test_an_operator_needs_room_between_two_words():
    gap = B.EQUATION_OP_LEAD / 2
    terms = [dict(EQ["terms"][0]), dict(EQ["terms"][1], at=EQ["terms"][0]["at"] + gap)]
    errs = _errs([_eq(terms=terms)])
    assert any("operator" in e and "in order" in e for e in errs), errs


# ---- the arithmetic truth rule (hard) ------------------------------------------------------------------------------


@pytest.mark.parametrize("text, value", [("25%", 20), ("20%", 21), ("2.0%", 2.06), ("about twenty", 20),
                                         ("20", -20), (MINUS + "½", 0.5), ("½", 0.25)])
def test_a_term_whose_text_is_not_its_value_is_refused(text, value):
    errs = _errs([_eq(terms=[_term(text, value, 400.18), EQ["terms"][1]])])
    assert any("text" in e and ("is not its value" in e or "does not read as a number" in e) for e in errs), errs


@pytest.mark.parametrize("text, value", [("20%", 20), ("20%", 20.4), ("$1,200B", 1200), ("1.5x", 1.5), ("1/2", 0.5),
                                         ("1½", 1.5), ("+3 pts", 3), (MINUS + "$5B", -5), ("-0.5", -0.5)])
def test_a_term_is_its_value_at_its_written_precision(text, value):
    assert B.equation_reads(text, value), (text, value)


@pytest.mark.parametrize("result, ok", [
    ({"text": MINUS + "10%", "value": -10}, True),
    ({"text": MINUS + "12%", "value": -12}, False),     # untrue: 20 x -1/2 is -10
    ({"text": "10%", "value": 10}, False),              # the sign: a fall written as a rise (E28)
    ({"text": MINUS + "10.0%", "value": -10}, True),
    ({"text": MINUS + "11%", "value": -11}, False),
])
def test_the_compiler_computes_the_result_and_refuses_an_untrue_one(result, ok):
    errs = _errs([_eq(result=dict(result, at=403.62))])
    assert (errs == []) is ok, errs
    if not ok:
        assert any("untrue" in e and MINUS + "10" in e for e in errs), errs


def test_the_result_is_held_to_its_own_written_precision():
    terms = [_term("20.4%", 20.4, 400.18), EQ["terms"][1]]              # 20.4 x -1/2 = -10.2
    assert _errs([_eq(terms=terms, result={"text": MINUS + "10%", "value": -10, "at": 403.62})]) == [], \
        "-10.2 written to the percent is -10%"
    errs = _errs([_eq(terms=terms, result={"text": MINUS + "10.0%", "value": -10, "at": 403.62})])
    assert any("untrue" in e for e in errs), "... but to a tenth it is -10.2%, so -10.0% is untrue"


def test_the_arithmetic_runs_left_to_right_as_it_is_spoken():
    terms = [_term("2", 2, 400.2), _term("3", 3, 401.0), _term("4", 4, 401.8)]
    ok = _eq(terms=terms, ops=["+", "×"], result={"text": "20", "value": 20, "at": 402.6})
    precedence = _eq(terms=terms, ops=["+", "×"], result={"text": "14", "value": 14, "at": 402.6})
    assert _errs([ok]) == []
    assert any("untrue" in e for e in _errs([precedence])), "no precedence: the row is read as it is spoken"
    assert B.equation_compute([2, 3, 4], ["+", "×"]) == 20


def test_a_division_by_zero_is_refused():
    errs = _errs([_eq(terms=[_term("4", 4, 400.2), _term("0", 0, 401.0)], ops=["÷"],
                      result={"text": "0", "value": 0, "at": 402.0})])
    assert any("zero" in e for e in errs), errs


# ---- the registries --------------------------------------------------------------------------------------------------


def test_the_when_says_what_sentence_calls_for_it_and_when_not():
    when = B.SPECIES_WHEN["equation"]
    assert "arithmetic" in when and "never" in when and "spoken" in when and "unsourced" in when
    assert "equation" in L.ACT_SPECIES["EXPLAINS"]


def test_each_term_and_the_result_is_an_event_on_its_word_and_the_operators_are_not():
    assert G.SPECIES_EVENTS["equation"] == ("terms", "result.at")
    scene = {"span": [398.74, 408.6], "species": [EQ]}
    assert sorted(G._species_events([scene])) == [400.18, 402.38, 403.62]
    three = _eq(terms=[_term("2", 2, 400.2), _term("3", 3, 401.0), _term("4", 4, 401.8)], ops=["+", "+"],
                result={"text": "9", "value": 9, "at": 402.6})
    assert sorted(G._species_events([{"span": [398.74, 408.6], "species": [three]}])) == [400.2, 401.0, 401.8, 402.6]
    late = _eq(result=dict(EQ["result"], at=409.0))
    assert 409.0 not in G._species_events([{"span": [398.74, 408.6], "species": [late]}]), "past its scene: no credit"


def test_the_compiler_mirrors_the_module_s_clock():
    src = MODULE.read_text(encoding="utf-8")
    for name, mirror in (("WRITE_S", B.EQUATION_WRITE_S), ("OP_LEAD", B.EQUATION_OP_LEAD), ("OUT_S", B.EQUATION_OUT_S),
                         ("FLOOR_PX", B.EQUATION_FLOOR_PX), ("LABEL_PX", B.EQUATION_LABEL_PX),
                         ("TERM_CAP_K", B.EQUATION_TERM_CAP_K), ("LABEL_CAP_K", B.EQUATION_LABEL_CAP_K),
                         ("STEP", B.EQUATION_STEP), ("DROP_MIN", B.EQUATION_DROP_MIN),
                         ("LABEL_DESC", B.EQUATION_LABEL_DESC), ("GAP_MIN", B.EQUATION_GAP_MIN)):
        m = re.search(rf"\b{name}: ([0-9.]+)", src)
        assert m and float(m.group(1)) == mirror, name
    assert B.EQUATION_FLOOR_PX == 59.08, "the s90 floor (ledger_page.CARD_TYPE_PX)"


def test_the_result_s_ink_is_the_page_s_neg_token_and_the_row_s_chalk_is_the_page_s():
    src, css = MODULE.read_text(encoding="utf-8"), TEMPLATE.read_text(encoding="utf-8")
    neg = re.search(r"--lp-neg: (#[0-9A-Fa-f]{6})", css).group(1)
    chalk = re.search(r"--lp-chalk: (#[0-9A-Fa-f]{6})", css).group(1)
    assert f'NEG: "{neg}"' in src and f'CHALK: "{chalk}"' in src, \
        "the stage layer sits outside .lp, so the module carries the tokens' own hex - pinned to the template here"


# ---- the engine ------------------------------------------------------------------------------------------------------


def test_the_engine_carries_the_module_right_after_the_ruler_and_reads_the_figure_s_hand():
    # the stage regions run freeze -> ruler (P71 T14) -> equation: both landed "right after freeze", the ruler first
    src = ENGINE.read_text(encoding="utf-8")
    begin = src.index("/* KINETICS:BEGIN equation */")
    ruler_end = src.index("/* KINETICS:END */", src.index("/* KINETICS:BEGIN ruler */"))
    assert src.index("/* KINETICS:BEGIN freeze */") < src.index("/* KINETICS:BEGIN ruler */") < begin
    assert src.index("const SPECIES_PAINTERS =") < begin < src.index("const paintSpecies =")
    assert src[ruler_end:begin].strip() == "/* KINETICS:END */", "inserted immediately after the ruler region"
    assert src.index("/* KINETICS:BEGIN figure */") < begin, "it imports figureGlyph - the figure's region is earlier"
    assert 'SPECIES_PAINTERS.equation = paintEquation' in src


def test_the_card_is_a_species_card_with_its_when_pulled_from_the_compiler():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["species:equation"]
    assert card["token"] == "equation" and card["when"] is None and card["serves"] == ["EXPLAINS"]
    assert card["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/equation.mjs",
                             "symbol": "paintEquation"}
    assert card["dials"] == {"module": "content/video_engine/scripts/species/equation.mjs", "object": "EQUATION"}
    assert len(card["does"]) <= 240 and len(card["title"]) <= 40 and card["proof"]["golden"] == "equation-halving"
    assert card["status"] == "wired"


# ---- the row, read on the served player ------------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

READ_ROW = """() => { const c = document.createElement('canvas').getContext('2d');
  return Array.from(document.querySelectorAll('#species .eqrow text')).map((tx) => ({
  role: tx.getAttribute('data-role'), text: tx.textContent, fs: parseFloat(tx.getAttribute('font-size')),
  cap: (c.font = tx.getAttribute('font-weight') + ' ' + tx.getAttribute('font-size') + 'px ' + tx.getAttribute('font-family'),
        c.measureText(tx.textContent.replace(/[^0-9A-Za-z]/g, '') || tx.textContent).actualBoundingBoxAscent),
  x: parseFloat(tx.getAttribute('x')), fill: tx.getAttribute('fill'), transform: tx.getAttribute('transform') || '',
  glyphs: Array.from(tx.querySelectorAll('tspan')).map((ts) => parseFloat(ts.getAttribute('opacity')))})); }"""


def _served(tl: dict, uris: dict, aspect: str, ts: list[float], shots: bool = False) -> list:
    """The row at each t, in ONE page scrubbed in the given order - its DOM read, and its pixels' hash when asked."""
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[aspect]
    out: list = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "equation.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)
                page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1.0).new_page()
                errs: list[str] = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                for t in ts:
                    png = RB.frame_png(page, t, (w, h))
                    row = page.evaluate(READ_ROW)
                    out.append((row, hashlib.sha256(RB.rgb_bytes(png)[1]).hexdigest()) if shots else row)
                br.close()
        finally:
            srv.shutdown()
    assert not errs, errs
    return out


def _items(row: list) -> list:
    return [it for it in row if it["role"] != "label"]


def _written(row: list, role: str) -> list[str]:
    return [it["text"] for it in row if it["role"] == role and it["glyphs"] and min(it["glyphs"]) >= 0.999]


@needs_browser
def test_the_row_is_written_in_spoken_order_and_the_operators_spring_between():
    import build_golden_sources as GS
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface("equation-halving")
    a, b_, r = (e["at"] for e in (*GS.EQUATION_TERMS, GS.EQUATION_RESULT))
    ts = [a - 0.3, a + 0.8, b_ - 0.02, b_ + 0.8, r + 0.8]
    rows = _served(tl, uris, aspect, ts)
    assert rows[0] == [] or all(max(it["glyphs"] or [0]) == 0 for it in rows[0] if it["role"] != "op"), rows[0]
    assert _written(rows[1], "term") == ["20%"] and _written(rows[1], "result") == []
    assert _written(rows[2], "term") == ["20%"], "the second input waits for its word"
    op = [it for it in rows[2] if it["role"] == "op"][0]
    assert "scale(" in op["transform"], "the operator springs in before the second input's word"
    assert _written(rows[3], "term") == ["20%", MINUS + "½"] and _written(rows[3], "result") == []
    assert _written(rows[4], "result") == [MINUS + "10%"]
    assert [it["role"] for it in _items(rows[4])] == ["term", "op", "term", "eq", "result"]
    labels = [it["text"] for it in rows[4] if it["role"] == "label"]
    assert labels == [e.get("label") for e in (*GS.EQUATION_TERMS, GS.EQUATION_RESULT)], "F7: every item named"
    assert all(it["fs"] >= 59.08 for it in rows[4] if it["role"] == "label"), "the labels at the s90 floor"
    xs = [it["x"] for it in _items(rows[4])]
    assert xs == sorted(xs), "the row reads left to right in the order it is spoken"
    assert all(it["fs"] >= 59.08 for it in _items(rows[4])), "the s90 floor"
    caps = [it["cap"] for it in _items(rows[4]) if it["role"] in ("term", "result")]
    label_caps = [it["cap"] for it in rows[4] if it["role"] == "label"]
    assert min(caps) >= 1.4 * max(label_caps), ("round 3: the numbers stand a clear step over their captions, measured "
                                                f"in the served player: {caps} vs {label_caps}")
    res = [it for it in _items(rows[4]) if it["role"] == "result"][0]
    assert res["fill"] == "#FF4D4D" and res["text"].startswith(MINUS), "E28: a fall is written with its minus, in neg"


@needs_browser
def test_the_row_is_seek_safe():
    """A pure function of t: the frame mid-row is the same frame cold, from after the row, and from before it."""
    import build_golden_sources as GS
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface("equation-halving")
    t_in = GS.EQUATION_TERMS[1]["at"] + 0.2
    cold = _served(tl, uris, aspect, [t_in], shots=True)[0]
    back = _served(tl, uris, aspect, [GS.EQUATION_RESULT["at"] + 1.5, t_in], shots=True)[1]
    fwd = _served(tl, uris, aspect, [GS.EQUATION_TERMS[0]["at"] - 2.0, t_in], shots=True)[1]
    assert cold == back == fwd


# ---- the review's round (F1-F5, F7): the row is computed from what is WRITTEN, in its units ---------------------------


def _row(terms, ops, text, value=None, at=402.6, **rkw):
    res = dict({"text": text, "at": at}, **rkw)
    if value is not None:
        res["value"] = value
    return _eq(terms=terms, ops=ops, result=res, dur=8.0, at=400.0)


def _labelled(entry: dict) -> dict:
    out = json.loads(json.dumps(entry))
    out["target"] = dict(ROOM)   # a named row needs the room for its captions under numbers a step larger
    for it, name in zip((*out["terms"], out["result"]), ("AI's weight", "a halving", "the index")):
        it["label"] = name
    return out


def test_the_row_is_computed_from_its_written_text_not_from_value():
    """F1: the viewer reads the text. Values inside each text's precision may not compound into a row that is untrue."""
    ones = _row([_term("1", 1.49, 400.2), _term("1", 1.49, 401.0), _term("1", 1.49, 401.8)], [TIMES, TIMES], "3", 3.3)
    assert any("untrue" in e for e in _own(_errs([ones]))), "1 x 1 x 1 is written, and it is 1"
    rounded = _row([_term("20%", 20.49, 400.2), _term("3", 3.49, 401.0)], [TIMES], "72%", 71.5)
    assert any("untrue" in e for e in _own(_errs([rounded]))), "20% x 3 is written, and it is 60%"


TIMES, DIVIDE, HALF = "\u00d7", "\u00f7", "\u00bd"
TRUE_ROWS = [
    (["20%", "50%"], [TIMES], "10%"),                      # a share of a share is a share
    (["20%", MINUS + "50%"], [TIMES], MINUS + "10%"),
    (["20%", MINUS + HALF], [TIMES], MINUS + "10%"),         # the golden's row
    (["3%", "5%"], [MINUS], MINUS + "2%"),                  # real yield
    (["$1.2B", "$300M"], ["+"], "$1.5B"),                  # the scales scale
    (["$100", "5%"], [TIMES], "$5"),                       # a % of a $ is $
    (["$10", "50%"], [DIVIDE], "$20"),
    (["$6B", "$2B"], [DIVIDE], "3x"),                      # $ / $ is a ratio: a multiple ...
    (["$6B", "$2B"], [DIVIDE], "300%"),                    # ... or a percent
    (["1.5x", "2"], [TIMES], "3x"),
    (["+3 pts", "2 pts"], ["+"], "5 pts"),
]


@pytest.mark.parametrize("texts, ops, result", TRUE_ROWS)
def test_a_true_row_in_its_units_is_accepted(texts, ops, result):
    terms = [_term(tx, B.equation_number(tx)[0], 400.2 + 0.8 * i) for i, tx in enumerate(texts)]
    assert _own(_errs([_row(terms, ops, result)])) == []


FALSE_ROWS = [
    (["20%", "50%"], [TIMES], "1000%", "untrue"),            # % is a hundredth, in the arithmetic
    (["$100", "5%"], [TIMES], "$500", "untrue"),
    (["$1.2B", "$300M"], ["+"], "$301.2B", "untrue"),       # B and M scale: $1.2B + $0.3B
    (["3%", "5%"], [MINUS], MINUS + "2x", "written in"),     # the unit swapped under the result
    (["20%", MINUS + HALF], [TIMES], MINUS + "10 pts", "written in"),
    (["3%", "$5"], ["+"], "$8", "ONE unit"),                 # a sum adds one unit
    (["$2", "$3"], [TIMES], "$6", "no unit"),                # dollars times dollars
    (["20e", MINUS + HALF], [TIMES], MINUS + "10e", "not one the row takes"),   # a closed unit list
    (["$20%", "2"], [TIMES], "$40%", "not one the row takes"),
]


@pytest.mark.parametrize("texts, ops, result, needle", FALSE_ROWS)
def test_an_untrue_or_unit_less_row_is_refused_by_name(texts, ops, result, needle):
    terms = [_term(tx, (B.equation_number(tx) or (1.0, 0))[0], 400.2 + 0.8 * i) for i, tx in enumerate(texts)]
    errs = _own(_errs([_row(terms, ops, result)]))
    assert any(needle in e for e in errs), errs


def test_the_scale_prefixes_scale_and_the_percent_is_a_hundredth():
    assert B.equation_quantity("$1.2B")[0] == pytest.approx(1.2e9) and B.equation_quantity("$1.2B")[2] == "$"
    assert B.equation_quantity("$300M")[0] == pytest.approx(3e8)
    assert B.equation_quantity(MINUS + "10%")[0] == pytest.approx(-0.1) and B.equation_quantity("10%")[2] == "%"
    assert B.equation_quantity("3 pts")[2] == "pts" and B.equation_quantity("2.5x")[2] == "1"
    assert B.equation_quantity("20e") is None and B.equation_number("20e") is None


@pytest.mark.parametrize("tier", ["CONFIRMED", "PLAUSIBLE"])
def test_a_research_tier_grades_a_source_and_only_a_scenario_stands_alone(tier):
    """F3: CONFIRMED and PLAUSIBLE are grades OF a source; with no src they certify themselves."""
    bare = _eq(terms=[_term("20%", 20, 400.18, tier=tier), EQ["terms"][1]])
    assert any("grades a source" in e for e in _own(_errs([bare])))
    assert _errs([_eq(terms=[_term("20%", 20, 400.18, tier=tier, src="ev-index-concentration-bars-v1"),
                             EQ["terms"][1]])]) == []
    assert EQ["terms"][1] == {"text": MINUS + HALF, "value": -0.5, "at": 402.38, "tier": "scenario"}, \
        "the halving is the sentence's own 'if' and stands alone"


def test_a_src_names_an_object_on_disk(tmp_path: Path):
    ev, build = tmp_path / "evidence/objects", tmp_path / "build-h/objects"
    ev.mkdir(parents=True)
    build.mkdir(parents=True)
    (ev / "ev-index-concentration-bars-v1.series.json").write_text("{}", encoding="utf-8")
    (build / "ev-derived-h18-v1.series.json").write_text("{}", encoding="utf-8")
    ok = _eq(terms=[EQ["terms"][0], dict(EQ["terms"][1], src="ev-derived-h18-v1")])
    assert B.equation_missing_sources(ok, (ev, build)) == []
    bad = _eq(terms=[dict(EQ["terms"][0], src="ev-does-not-exist-v9"), EQ["terms"][1]])
    miss = B.equation_missing_sources(bad, (ev, build))
    assert len(miss) == 1 and "ev-does-not-exist-v9" in miss[0], miss
    with pytest.raises(SystemExit, match="ev-does-not-exist-v9"):
        B.equation_row_checks([bad], "shot row 18", tmp_path, tmp_path / "build-h")
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    main = src[src.index("\ndef main() -> int:"):]
    assert main.count("equation_row_checks(row_species,") == 1, "ONE call line in main(), after the species are validated"


def test_a_result_with_no_value_is_its_text():
    """F4: `value` is optional on the result - the text is what is written, and its sign is the ink's."""
    assert _errs([_eq(result={"text": MINUS + "10%", "at": 403.62})]) == []
    assert _errs([_eq(result={"text": "-10%", "at": 403.62})]) == [], "a typed hyphen is a minus (the painter writes U+2212)"


def test_terms_closer_than_one_word_are_a_warn_not_a_refusal():
    """F5 (s106): the words are not bound to the take here, so the pitch ADVISES."""
    close = _labelled(_eq(terms=[dict(EQ["terms"][0], at=400.2), dict(EQ["terms"][1], at=400.32)],
                          result=dict(EQ["result"], at=400.8)))
    assert _errs([close]) == []
    warns = B.equation_advice(close)
    assert any("one word" in w and "0.12" in w for w in warns), warns
    assert B.equation_advice(_labelled(EQ)) == [], "2.2 s and 1.24 s apart: a word each"


def test_labels_name_the_terms_and_a_row_with_none_is_a_warn():
    """F7 (E28, the label is data): an optional caption under each term and the result; none at all WARNs."""
    labelled = _labelled(EQ)
    assert _errs([labelled]) == [] and B.equation_advice(labelled) == []
    assert _errs([EQ]) == [] and any("named" in w for w in B.equation_advice(EQ)), "no labels: a WARN, never a refusal"
    bad = json.loads(json.dumps(labelled))
    bad["terms"][0]["label"] = 7
    assert any("label" in e for e in _own(_errs([bad])))
    long = json.loads(json.dumps(labelled))
    long["result"]["label"] = "the whole of the S&P 500 index today"
    assert any("label" in w and "long" in w for w in B.equation_advice(long))


def test_the_label_ink_is_the_page_s_quiet_ink():
    src, engine = MODULE.read_text(encoding="utf-8"), ENGINE.read_text(encoding="utf-8")
    deemph = re.search(r'const LP_INK = \{[^}]*deemph: "(#[0-9A-Fa-f]{6})"', engine).group(1)
    assert f'LABEL_INK: "{deemph}"' in src, "the page's deemph ink (LP_INK), pinned to the engine's literal"


# ---- round 3: the numbers stand a clear step above their captions -------------------------------------------------------


def test_a_named_row_s_numbers_stand_a_step_above_their_captions():
    """The parent's frame read: 59 px captions read LARGER than the numbers they named. The captions stay at the s90
    floor; the numbers' cap is STEP x the caption's (both faces' caps measured in the served player), never less."""
    step = B.EQUATION_TERM_MIN * B.EQUATION_TERM_CAP_K / (B.EQUATION_LABEL_PX * B.EQUATION_LABEL_CAP_K)
    assert step == pytest.approx(B.EQUATION_STEP) and B.EQUATION_STEP >= 1.4
    assert B.EQUATION_LABEL_PX == B.EQUATION_FLOOR_PX == 59.08, "the captions at the floor, never under it"
    assert B.EQUATION_TERM_MIN > B.EQUATION_LABEL_PX


def test_a_region_that_cannot_hold_a_named_row_at_the_step_is_a_warn_with_numbers():
    tight = _labelled(EQ)
    tight["target"] = dict(REGION)   # 151 px tall: the numbers at the step and their captions need about 170
    assert _errs([tight]) == [], "s106: a placement is advice, never a refusal"
    warns = B.equation_advice(tight)
    room = [w for w in warns if "needs about" in w]
    assert len(room) == 1 and "x 151 px" in room[0] and f"{B.EQUATION_TERM_MIN:.1f} px" in room[0], warns
    assert B.equation_advice(_labelled(EQ)) == [], "the golden's band holds it"
    assert not any("needs about" in w for w in B.equation_advice(EQ)), "an unnamed row keeps its old sizing: no room WARN"
    portrait = B.equation_advice(tight, (1080, 1920))
    assert any("713 x 269 px" in w for w in portrait), ("9:16: the same fractions are taller (269 px) but only 713 px "
                                                         f"wide - the stage's own size is read: {portrait}")

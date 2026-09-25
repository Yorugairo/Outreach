"""P72 T41 (R26-334) - A BALANCE SIDE'S SIGN INK: the per-side `tone` and its pill.

The P70 T7 review (BACKLOG R26-334, hist:941): Bravos labels each pan with a coloured pill - threat red, opportunity
green (CHN shots 113 / 114, 19:10.2-19:15.5) - and ours writes cream Kalam on cream pans. E99 s118 inks a name by its
series and a balance side has none, so a side may declare `tone: neg | pos | neutral`, drawn as a PILL in the palette's
sign inks: `--lp-neg` / `--lp-pos` (E28's sign pair, the chip tab's own), and the neutral `deemph` (LP_INK's explicit
de-emphasis). It is OPT-IN: a balance with no `tone` paints exactly what it painted (the golden `balance-level` holds
byte-identical, test_golden_frames), and a tone outside the three is refused BY NAME (s106: a silent drop is neither
advice nor refusal). The pill's FORM is the module's dial `BALANCE.TONE.FORM`, one of three candidates rendered from one
source for the operator's pick (P72-HG1 item 6); the default form is set only by that pick.

The law and the painter are species/balance.mjs; this file pins the grammar, the inks (against the palette, never a
new ink), the compiler's mirror of the pill's width and room, and the pill read on the SERVED player in every form.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import series_inks as SI  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/balance.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/species.json"
PAGE = "ledger:ev-two-clocks-bars-v1:bars::right:axes:cut"
PLAIN = "plate-plain"
ROOM = {"kind": "region", "x0": 0.735, "y0": 0.22, "x1": 0.985, "y1": 0.80}
BAL = {"kind": "balance", "at": 11.43, "dur": 9.0, "target": ROOM,
       "left": {"label": "MOAT", "icon": "factory", "at": 12.65},
       "right": {"label": "PAPER", "icon": "landmark", "at": 16.56}}
TONES = ("neg", "pos", "neutral")
FORMS = ("filled", "outline", "sans")


def _errs(entries, plate=PAGE):
    return B.validate_species([json.loads(json.dumps(e)) for e in entries], (0, 0, 0), plate)


def _toned(left=None, right=None, base=BAL):
    e = json.loads(json.dumps(base))
    for side, tone in (("left", left), ("right", right)):
        if tone is not None:
            e[side]["tone"] = tone
    return e


def _node(expr: str):
    """A pure read of the module in node (its exports), returned as JSON."""
    src = f"import * as M from {json.dumps(MODULE.as_uri())}; console.log(JSON.stringify({expr}));"
    out = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


# ---- the grammar: opt-in, three tones, a malformed one refused by name -------------------------------------------


def test_a_balance_with_no_tone_compiles_as_it_did():
    assert _errs([BAL]) == []


@pytest.mark.parametrize("tone", TONES)
@pytest.mark.parametrize("side", ["left", "right"])
def test_each_side_may_declare_a_tone(side, tone):
    assert _errs([_toned(**{side: tone})]) == []


def test_both_sides_toned_compile():
    assert _errs([_toned("neg", "pos")]) == []


@pytest.mark.parametrize("tone", ["threat", "opportunity", "red", "NEG", "", 1, True, None, ["neg"]])
def test_a_malformed_tone_is_refused_by_name(tone):
    e = json.loads(json.dumps(BAL))
    e["left"]["tone"] = tone
    errs = _errs([e])
    assert any(x.startswith("balance: left: tone") and "neg|pos|neutral" in x for x in errs), errs


def test_the_compiler_s_tones_are_the_module_s():
    assert tuple(B.BALANCE_TONES) == TONES
    assert tuple(_node("M.BALANCE_TONES")) == TONES
    assert "tone" in B.BALANCE_SIDE_KEYS


# ---- the inks: the palette's own, never invented -------------------------------------------------------------------


def test_the_pill_inks_are_the_palette_s_sign_inks_and_its_neutral():
    pal = SI.palette()
    inks = _node("M.BALANCE.TONE.INK")
    assert inks["neg"].upper() == pal["neg"].upper(), "the template's --lp-neg"
    assert inks["pos"].upper() == pal["pos"].upper(), "the template's --lp-pos"
    assert inks["neutral"].upper() == pal["ink"]["deemph"].upper(), "LP_INK.deemph - the explicit de-emphasis"


LARGE_TEXT = 3.0   # WCAG 2 AA for LARGE text (>= 24 px bold): the word is at the s90 floor, 59.08 px and up, weight 700


def test_the_word_on_a_filled_pill_reads_on_every_fill():
    """The chip tab's rule: charcoal, the ink with the higher contrast on every fill (4.06:1 on --lp-neg, where white is
    lower) - past WCAG's large-text bar."""
    T = _node("M.BALANCE.TONE")
    for tone in TONES:
        c = SI.contrast(T["TEXT"], T["INK"][tone])
        assert c >= LARGE_TEXT and c > SI.contrast("#FFFFFF", T["INK"][tone]), (tone, c)


def test_an_outlined_pill_s_word_reads_on_the_charcoal_page():
    T = _node("M.BALANCE.TONE")
    ground = SI.palette()["ground"]["page"]
    for tone in TONES:
        assert SI.contrast(T["INK"][tone], ground) >= LARGE_TEXT, (tone, SI.contrast(T["INK"][tone], ground))


def test_the_form_is_one_of_the_candidates():
    assert tuple(_node("M.BALANCE_TONE_FORMS")) == FORMS
    assert _node("M.BALANCE.TONE.FORM") in FORMS


# ---- the module's law, pure -------------------------------------------------------------------------------------


def test_a_toned_name_is_fitted_by_its_pill_s_width():
    pad = _node("M.BALANCE.TONE.PAD_PX")
    assert _node("M.balanceNameWidth(300, 'neg')") == pytest.approx(300 + 2 * pad)
    assert _node("M.balanceNameWidth(300, undefined)") == pytest.approx(300 + _node("M.BALANCE.NAME_PAD")), "untoned: as it was"


def test_a_bare_toned_name_s_pill_stands_on_its_rim_and_a_pictured_one_hangs_under_the_bowl():
    g = {"H": 200, "pd": 30}
    bare = _node("M.balanceToneRow({H: 200, pd: 30}, false, 0, 60)")
    pict = _node("M.balanceToneRow({H: 200, pd: 30}, true, 0, 60)")
    B_ = _node("M.BALANCE")
    assert bare["top"] + bare["h"] == pytest.approx(g["H"] - B_["RIM_LIFT"]), "the pill's foot on the rim's lift"
    assert pict["top"] == pytest.approx(g["H"] + g["pd"] + B_["LABEL_GAP"]), "the pill's top under the bowl"
    assert bare["h"] == pytest.approx(B_["TONE"]["H_K"] * 60)
    for r in (bare, pict):   # the word's caps centred in the pill
        cap = B_["TONE"]["CAP_EM"]["kalam"] * 60
        assert r["baseline"] - cap / 2 == pytest.approx(r["top"] + r["h"] / 2)


def test_the_untoned_row_is_unchanged():
    assert _node("M.balanceNameRow({H: 200, pd: 30}, false, 5)") == pytest.approx(200 - 8 + 5)


# ---- the compiler mirrors the pill (advice and the footprint) ---------------------------------------------------------


def test_the_compiler_estimates_a_toned_name_by_its_pill():
    pad = B.BALANCE_TONE_PAD_PX
    L = {"label": "PAPER", "at": 1.0}
    base = B.balance_name_est(L)
    assert base == pytest.approx(B.BALANCE_LABEL_EM * B.BALANCE_LABEL_PX * 5 + B.BALANCE_NAME_PAD)
    assert B.balance_name_est(dict(L, tone="pos")) == pytest.approx(base - B.BALANCE_NAME_PAD + 2 * pad)


def test_the_compiler_s_pill_dials_mirror_the_module_s():
    T = _node("M.BALANCE.TONE")
    assert B.BALANCE_TONE_PAD_PX == T["PAD_PX"] and B.BALANCE_TONE_H_K == pytest.approx(T["H_K"])
    assert B.BALANCE_TONE_FORM == T["FORM"], "the operator's pick sets both"
    assert set(B.BALANCE_TONE_EM) == set(FORMS) and B.BALANCE_TONE_EM["filled"] == B.BALANCE_LABEL_EM


def test_a_tight_room_advises_the_toned_name_it_would_not_have_advised():
    room = {"kind": "region", "x0": 0.735, "y0": 0.22, "x1": 0.985, "y1": 0.80}
    names = {"left": {"label": "CREDIT", "at": 12.65}, "right": {"label": "PAPER", "at": 16.56}}
    e = dict(BAL, target=room, left=names["left"], right=names["right"])
    assert B.balance_advice(e, "16:9") == []
    toned = _toned("neg", "pos", base=e)
    assert any("balance: left name" in w for w in B.balance_advice(toned, "16:9")), B.balance_advice(toned, "16:9")


def test_the_toned_footprint_holds_the_untoned_one():
    """A pill only ever adds to the box (its width, its height); the served test below holds every painted pill inside."""
    plain, toned = B.balance_footprint(BAL, "16:9"), B.balance_footprint(_toned("neg", "pos"), "16:9")
    eps = 0.05   # the footprint is rounded to 0.1 px
    assert toned["x"] <= plain["x"] + eps and toned["y"] <= plain["y"] + eps
    assert toned["x"] + toned["w"] >= plain["x"] + plain["w"] - eps and toned["y"] + toned["h"] >= plain["y"] + plain["h"] - eps


def test_the_card_lists_the_tone():
    cards = {c["token"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    opts = {o["token"]: o for o in cards["balance"]["options"]}
    assert "tone" in opts and opts["tone"]["source_set"] == "BALANCE_TONES"
    assert all(t in opts["tone"]["means"] for t in TONES)
    assert "tone?" in cards["balance"]["author"]["key"]


# ---- the served player: the pill in every form, the untoned balance untouched ---------------------------------------------

PROBE = """() => { const st = document.getElementById('stage').getBoundingClientRect(), k = 1920 / st.width;
  const box = (e) => { const r = e.getBoundingClientRect(); return [(r.left - st.left) * k, (r.top - st.top) * k,
                                                                      (r.right - st.left) * k, (r.bottom - st.top) * k]; };
  const g = document.querySelector('g.balance'); if (!g) return null;
  return { tones: [...g.querySelectorAll('.bal-tone')].map((p) => ({ side: p.closest('.bal-pan').dataset.side,
             tone: p.dataset.tone, form: p.dataset.form, fill: p.getAttribute('fill'), stroke: p.getAttribute('stroke'),
             op: +p.getAttribute('opacity'), box: box(p) })),
           labels: [...g.querySelectorAll('text.bal-label')].map((l) => ({ side: l.closest('.bal-pan').dataset.side,
             text: l.textContent, fill: getComputedStyle(l).fill, font: getComputedStyle(l).fontFamily,
             op: +l.getAttribute('opacity'), box: box(l) })),
           bowls: [...g.querySelectorAll('.bal-pan')].map((p) => [p.dataset.side, box(p.querySelector('.bal-bowl'))]),
           html: g.outerHTML }; }"""


def _engine_with_form(form: str, td: Path) -> Path:
    """The served engine with the pill's FORM dial set to `form` (the proof's one-source mechanism)."""
    src = ENGINE.read_text(encoding="utf-8")
    new, n = re.subn(r'(FORM: )"(filled|outline|sans)"(,\s*/\* THE PILL\'S FORM)', lambda m: f'{m.group(1)}"{form}"{m.group(3)}', src)
    assert n == 1, "the engine carries the pill's FORM dial exactly once"
    p = td / f"engine-{form}.mjs"
    p.write_text(new, encoding="utf-8")
    return p


def _serve(tl: dict, uris: dict, times: list[float], form: str | None = None, order: list[float] | None = None) -> dict:
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE["16:9"]
    out: dict = {}
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        eng = _engine_with_form(form, tdp) if form else RB.ENGINE
        html = tdp / "tone.html"
        html.write_text(RB.instantiate(tl, uris, engine=eng), encoding="utf-8")
        srv, port = RB.serve(tdp)
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch(headless=True)
                page = b.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/tone.html", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                for t in (order or times):
                    RB.frame_png(page, t, (w, h))
                    out.setdefault(t, page.evaluate(PROBE))
                b.close()
        finally:
            srv.shutdown()
    return out


def _golden_toned(left="neg", right="pos"):
    import build_golden_sources as GS
    saved = [json.loads(json.dumps(x)) for x in GS.BAL_SPECIES]
    try:
        for side, tone in (("left", left), ("right", right)):
            if tone:
                GS.BAL_SPECIES[0][side]["tone"] = tone
        return GS.balance_level()
    finally:
        GS.BAL_SPECIES[:] = saved


BARE_AT = (3.0, 5.0)


def _bare_bed(left="neg", right="pos"):
    """Bravos's own beat on a plain plate: THREAT and OPPORTUNITY as bare names (the load IS the name)."""
    import build_golden_sources as GS
    e = {"kind": "balance", "at": 2.0, "dur": 12.0, "target": {"kind": "region", "x0": 0.2, "y0": 0.18, "x1": 0.8, "y1": 0.86},
         "left": {"label": "THREAT", "at": BARE_AT[0]}, "right": {"label": "OPPORTUNITY", "at": BARE_AT[1]}}
    for side, tone in (("left", left), ("right", right)):
        if tone is not None:
            e[side]["tone"] = tone
    assert B.validate_species([dict(e)], (0, 0, 0), PLAIN) == []
    world = {"asset_id": PLAIN, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, GS.RUNTIME], "docks": [], "species": [e]}]
    return GS._timeline("P72 T41: a toned bare balance", scenes, {}, "16:9"), GS._base_uris()


@pytest.fixture(scope="module")
def golden_untoned():
    import build_golden_sources as GS
    tl, uris = GS.SURFACES["balance-level"]()
    t = GS.FRAME_T["balance-level"]
    return _serve(tl, uris, [t])[t]


def test_an_untoned_balance_paints_no_pill(golden_untoned):
    assert golden_untoned["tones"] == [] and "data-tone" not in golden_untoned["html"]


@pytest.fixture(scope="module", params=FORMS)
def toned_reads(request):
    import build_golden_sources as GS
    t = GS.FRAME_T["balance-level"]
    tl, uris = _golden_toned()
    btl, buris = _bare_bed()
    bt = 11.0
    return (request.param, _serve(tl, uris, [t], form=request.param)[t], _serve(btl, buris, [bt], form=request.param)[bt])


def test_each_toned_pan_carries_one_pill_in_its_sign_ink(toned_reads):
    form, pict, bare = toned_reads
    inks = _node("M.BALANCE.TONE.INK")
    for read in (pict, bare):
        got = {p["side"]: p for p in read["tones"]}
        assert sorted(got) == ["left", "right"] and len(read["tones"]) == 2, read["tones"]
        for side, tone in (("left", "neg"), ("right", "pos")):
            p = got[side]
            assert p["tone"] == tone and p["form"] == form, p
            painted = p["stroke"] if form == "outline" else p["fill"]
            assert painted.upper() == inks[tone].upper(), (form, p)


def test_the_word_sits_inside_its_pill(toned_reads):
    _, pict, bare = toned_reads
    for read in (pict, bare):
        pills = {p["side"]: p["box"] for p in read["tones"]}
        for lab in read["labels"]:
            px0, py0, px1, py1 = pills[lab["side"]]
            x0, y0, x1, y1 = lab["box"]
            assert px0 - 0.5 <= x0 and x1 <= px1 + 0.5, (lab, pills[lab["side"]])
            cy, pcy = (y0 + y1) / 2, (py0 + py1) / 2
            assert abs(cy - pcy) < 0.3 * (py1 - py0), (lab, pills[lab["side"]])


def test_the_word_takes_the_form_s_ink_and_face(toned_reads):
    form, pict, _ = toned_reads
    T = _node("M.BALANCE.TONE")
    for lab in pict["labels"]:
        rgb = lab["fill"]
        want = T["INK"]["neg" if lab["side"] == "left" else "pos"] if form == "outline" else T["TEXT"]
        h = want.lstrip("#")
        assert rgb == f"rgb({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)})", (form, lab)
        assert ("Inter" in lab["font"]) == (form == "sans"), (form, lab["font"])


def test_a_bare_pill_rests_on_its_rim_and_a_pictured_one_hangs_under_its_bowl(toned_reads):
    _, pict, bare = toned_reads
    bowls = {s: bx for s, bx in bare["bowls"]}
    for p in bare["tones"]:
        assert p["box"][3] <= bowls[p["side"]][1] + 1.0, ("the pill stands on the rim, never in the solid bowl", p, bowls)
    bowls = {s: bx for s, bx in pict["bowls"]}
    for p in pict["tones"]:
        assert p["box"][1] >= bowls[p["side"]][3] - 1.0, ("the pill hangs under the bowl", p, bowls)


def test_a_pill_stays_on_the_stage_and_off_the_post(toned_reads):
    _, pict, bare = toned_reads
    for read, room in ((pict, ROOM), (bare, {"x0": 0.2, "x1": 0.8})):
        cx = (room["x0"] + room["x1"]) / 2 * 1920
        for p in read["tones"]:
            x0, _, x1, _ = p["box"]
            assert x0 >= B.BALANCE_STAGE_MARGIN - 0.5 and x1 <= 1920 - B.BALANCE_STAGE_MARGIN + 0.5, p
            if p["side"] == "left":
                assert x1 <= cx - B.BALANCE_POST_CLEAR_PX + 0.5, p
            else:
                assert x0 >= cx + B.BALANCE_POST_CLEAR_PX - 0.5, p


def test_the_pill_is_inside_the_published_footprint(toned_reads, monkeypatch):
    form, pict, bare = toned_reads
    monkeypatch.setattr(B, "BALANCE_TONE_FORM", form)   # the compiler's mirror of the form the engine was served with
    tl, _ = _golden_toned()
    sp = [e for e in tl["scenes"][0]["species"] if e["kind"] == "balance"][0]
    btl, _ = _bare_bed()
    bsp = btl["scenes"][0]["species"][0]
    for read, e in ((pict, sp), (bare, bsp)):
        f = B.balance_footprint(e, "16:9")
        for p in read["tones"]:
            x0, y0, x1, y1 = p["box"]
            assert f["x"] - 0.5 <= x0 and f["y"] - 0.5 <= y0 and x1 <= f["x"] + f["w"] + 0.5 and y1 <= f["y"] + f["h"] + 0.5, (p, f)


def test_the_pill_lands_with_its_name_and_a_scrub_is_the_play():
    tl, uris = _bare_bed()
    t = round(BARE_AT[1] + 0.2, 3)   # the right name mid-fade
    fwd = _serve(tl, uris, [t])[t]
    scrub = _serve(tl, uris, [t], order=[12.0, 1.0, BARE_AT[1] - 0.5, t])[t]
    for p in fwd["tones"]:
        lab = [x for x in fwd["labels"] if x["side"] == p["side"]][0]
        assert p["op"] == pytest.approx(lab["op"], abs=1e-3), (p, lab)
    assert fwd["html"] == scrub["html"]


def test_a_neutral_side_wears_the_neutral_ink():
    tl, uris = _bare_bed(left="neutral", right="pos")
    read = _serve(tl, uris, [11.0])[11.0]
    got = {p["side"]: p for p in read["tones"]}
    assert got["left"]["tone"] == "neutral" and got["left"]["fill"].upper() == _node("M.BALANCE.TONE.INK.neutral").upper()


def test_one_toned_side_leaves_the_other_as_it_was():
    tl, uris = _bare_bed(left="neg", right=None)
    read = _serve(tl, uris, [11.0])[11.0]
    assert [p["side"] for p in read["tones"]] == ["left"]
    right = [x for x in read["labels"] if x["side"] == "right"][0]
    assert "Kalam" in right["font"] and right["fill"] == "rgb(244, 230, 199)", right

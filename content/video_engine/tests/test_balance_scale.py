"""P70 T7 (was P69 T59) - THE BALANCE SCALE, AND THE BALANCE TIPS.

The Bravos harvest v2's T27 "Balance scale (a tip, or a flag / scale / flag trio)" (CHN 19:10; JPN 06:41) and its A40
"The balance tips" (CHN 19:10). BRAVOS-USE-WHEN :589 / :643: "two forces weighed ('threat' vs 'opportunity', US vs
Japan)"; "two forces are weighed and the sentence says which way it tips". The don'ts: "one side is unnamed or
unweighed"; :646 "a real balance of figures (use two bars)".

The token is a STAGE species - `{kind: "balance", at, dur, target: region, left: {label, icon? | prop?, at}, right:
{...}, tip?: {at, to: left | right}}`: the beam and the fulcrum draw on `at` (the arms and the hangers GENERATED, so
clothoid segments - doc 42 s42.4), each pan's load lands on its own word (stopaction's landXf), the beam leans to a lone
load on its spring and settles LEVEL once both are weighed, and on `tip.at` it tips to TIP_DEG toward `tip.to` on an
underdamped spring with ONE visible overshoot, the pans hanging plumb all the while. E99 s128: the balance is an object
IN the world, so its base carries T6b's resting hatch (ctx.propHatchLines) and it stands in the page's room.

The law and the painter are species/balance.mjs (pinned by tests/kinetics/balance.test.mjs); this file pins the
compiler's grammar and its TRUTH (a label with a digit is refused, pointing to two bars; an unnamed or unweighed side is
refused), the gate's events, the engine's wiring (the region, the ctx key), the card, and the beat read on the SERVED
player (the golden `balance-level`, H row 18's "Both are true at once"; and the private test bed's tip).
"""
from __future__ import annotations

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

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/balance.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/species.json"
PAGE = "ledger:ev-two-clocks-bars-v1:bars::right:axes:cut"
PLATE = "plate-desk"
ROOM = {"kind": "region", "x0": 0.735, "y0": 0.22, "x1": 0.985, "y1": 0.80}   # the golden's room: 480 px wide, clear of the caption's rail
BAL = {"kind": "balance", "at": 11.43, "dur": 9.0, "target": ROOM,
       "left": {"label": "MOAT", "icon": "factory", "at": 12.65},
       "right": {"label": "PAPER", "icon": "landmark", "at": 16.56}}
TIPPED = dict(BAL, tip={"at": 19.0, "to": "right"})


def _errs(entries, plate=PAGE, ken=(0, 0, 0)):
    return B.validate_species([json.loads(json.dumps(e)) for e in entries], ken, plate)


def _with(**patch):
    e = json.loads(json.dumps(BAL))
    for k, v in patch.items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    return e


def _side(side, **patch):
    e = json.loads(json.dumps(BAL))
    for k, v in patch.items():
        if v is None:
            e[side].pop(k, None)
        else:
            e[side][k] = v
    return e


# ---- the grammar -------------------------------------------------------------------------------------------------


def test_the_token_is_a_stage_species_the_compiler_accepts_on_a_page_and_on_a_plate():
    assert "balance" in B.SPECIES_KINDS and "balance" not in B.PAGE_SPECIES
    assert _errs([BAL]) == []
    assert _errs([TIPPED]) == []
    assert _errs([BAL], plate=PLATE) == [], "a balance stands on any world - it is an object in the room (E99 s128)"


def test_it_names_its_room_as_a_region_and_nothing_else():
    assert B.SPECIES_TARGETS["balance"] == ("region",)
    assert any("not allowed" in e or "region" in e for e in _errs([_with(target={"kind": "point", "x": 0.8, "y": 0.5})]))
    assert any("target" in e for e in _errs([_with(target=None)]))


def test_it_carries_a_when():
    assert "balance" in B.SPECIES_WHEN and "tips" in B.SPECIES_WHEN["balance"]


# ---- the truth: two NAMED, WEIGHED forces, never figures ---------------------------------------------------------


@pytest.mark.parametrize("label", ["20 years", "5%", "$148B", "2x"])
def test_a_label_with_a_digit_is_refused_by_name_pointing_to_two_bars(label):
    errs = _errs([_side("left", label=label)])
    assert any("balance" in e and "digit" in e and "two bars" in e for e in errs), errs


@pytest.mark.parametrize("side", ["left", "right"])
@pytest.mark.parametrize("label", [None, "", "   "])
def test_an_unnamed_side_is_refused(side, label):
    errs = _errs([_side(side, label=label)])
    assert any(f"balance: {side}" in e and "unnamed" in e for e in errs), errs


@pytest.mark.parametrize("side", ["left", "right"])
def test_an_unweighed_side_is_refused(side):
    errs = _errs([_side(side, at=None)])
    assert any(f"balance: {side}" in e and "unweighed" in e for e in errs), errs


@pytest.mark.parametrize("side", ["left", "right"])
def test_a_missing_side_is_refused(side):
    errs = _errs([_with(**{side: None})])
    assert any(f"balance: '{side}'" in e for e in errs), errs


def test_a_load_lands_on_a_pan_that_is_drawn():
    errs = _errs([_side("left", at=BAL["at"] + 0.2)])
    assert any("balance: left" in e and "drawn" in e for e in errs), errs
    assert _errs([_side("left", at=BAL["at"] + B.BALANCE_DRAW_S)]) == []


def test_a_load_that_cannot_finish_landing_in_the_window_is_refused():
    errs = _errs([_side("right", at=BAL["at"] + BAL["dur"] - 0.1)])
    assert any("balance: right" in e and "window" in e for e in errs), errs


def test_both_loads_on_one_word_is_one_weighing():
    assert _errs([_side("right", at=BAL["left"]["at"])]) == []


# ---- the tip ------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("to", ["up", "LEFT", None, 1])
def test_a_tip_names_the_side_that_goes_down(to):
    errs = _errs([dict(BAL, tip={"at": 19.0, "to": to})])
    assert any("balance: tip" in e and "left" in e and "right" in e for e in errs), errs


def test_a_tip_comes_after_both_sides_are_weighed():
    errs = _errs([dict(BAL, tip={"at": 15.0, "to": "right"})])
    assert any("balance: tip" in e and "weighed" in e for e in errs), errs


def test_a_tip_the_window_cannot_show_is_refused():
    errs = _errs([dict(BAL, tip={"at": BAL["at"] + BAL["dur"] - 0.2, "to": "left"})])
    assert any("balance: tip" in e and "window" in e for e in errs), errs


def test_a_tip_with_no_word_is_refused():
    errs = _errs([dict(BAL, tip={"to": "left"})])
    assert any("balance: tip" in e and "at" in e for e in errs), errs


@pytest.mark.parametrize("gap", [0.01, 0.2, 0.61])
def test_a_tip_waits_for_the_later_load_to_land(gap):
    """Review F5: the beam answers a load at its CONTACT (the word + 0.32 s); a tip before the later load has landed
    starts while that load is still in the air. The tip is owed the later word + BALANCE_LAND_S."""
    later = max(BAL["left"]["at"], BAL["right"]["at"])
    errs = _errs([dict(BAL, tip={"at": later + gap, "to": "right"})])
    assert any("balance: tip" in e and "landed" in e and f"{B.BALANCE_LAND_S:g}" in e for e in errs), errs


def test_a_tip_the_moment_the_later_load_has_landed_is_accepted():
    later = max(BAL["left"]["at"], BAL["right"]["at"])
    assert _errs([dict(BAL, tip={"at": later + B.BALANCE_LAND_S, "to": "right"})]) == []


# ---- the loads' pictures and the options ---------------------------------------------------------------------------


def test_a_load_names_a_sourced_glyph_or_a_catalogued_prop_never_both():
    assert _errs([_side("left", icon=None)]) == [], "a label alone is a load: the name lands in the pan"
    assert any("icon" in e for e in _errs([_side("left", icon="no-such-glyph")]))
    assert _errs([_side("left", icon=None, prop="prop-memory-steel-ibeam-v1")]) == []
    assert any("prop" in e for e in _errs([_side("left", icon=None, prop="prop-no-such-thing-v1")]))
    errs = _errs([_side("left", prop="prop-memory-steel-ibeam-v1")])
    assert any("balance: left" in e and "one picture" in e for e in errs), errs


def test_the_loads_pictures_ride_the_asset_map():
    e = _side("right", icon=None, prop="prop-memory-steel-ibeam-v1")
    assert B.species_icons(e) == ["factory"]
    assert B.species_props(e) == ["prop-memory-steel-ibeam-v1"]


@pytest.mark.parametrize("patch, needle", [
    ({"idle": "wobble"}, "idle"),
    ({"ink": "gold"}, "ink"),
    ({"weights": [1, 2]}, "weights"),
])
def test_a_malformed_balance_is_refused_by_name(patch, needle):
    errs = _errs([_with(**patch)])
    assert any(e.startswith("balance") and needle in e for e in errs), errs


# Review F1 (HIGH): a figure reaches the scale through the load's PICTURE. The sourced glyphs, read path by path
# (assets/icons/*.svg): coins carries a "1" in each coin (`M15 6h1v4`, `m6.134 14.768.866-.5 2 3.464`); cpu (pins),
# factory (a roof and three dots), landmark (a pediment and columns) and ship carry none.
def test_the_figure_glyphs_are_the_ones_whose_drawing_carries_a_numeral():
    assert B.BALANCE_FIGURE_ICONS == ("coins",)
    for name in sorted(q.stem for q in B.ICONS_DIR.glob("*.svg")):
        errs = _errs([_side("left", icon=name)])
        if name in B.BALANCE_FIGURE_ICONS:
            assert any("balance: left" in e and name in e and "figure" in e and "two bars" in e for e in errs), errs
        else:
            assert errs == [], (name, errs)


# ... and a catalogued prop whose id, name or tags carry a digit, a % or $, or a date (a calendar): refused by name.
@pytest.mark.parametrize("prop", ["prop-treasury-yield-gauge-5pct-v1", "prop-tech-sp500-concentration-v1",
                                  "prop-hbm-stacked-die-v1", "prop-upcoming-catalysts-calendar-v1",
                                  "prop-triple-witching-opex-v1"])
def test_a_prop_that_carries_a_figure_or_a_date_is_refused_pointing_to_two_bars(prop):
    errs = _errs([_side("left", icon=None, prop=prop)])
    assert any("balance: left" in e and prop in e and "two bars" in e for e in errs), errs


@pytest.mark.parametrize("prop", ["prop-memory-steel-ibeam-v1", "prop-gpu-accelerator-card-v1", "prop-hyperscale-datacenter-v1"])
def test_a_prop_that_carries_no_figure_is_a_load(prop):
    assert _errs([_side("left", icon=None, prop=prop)]) == [], "the version suffix (-v1) is not a figure; 'triple-fan' is not a number"


# Review F3 (MEDIUM): number words and non-digit numerals and signs are figures too - refused by name.
@pytest.mark.parametrize("label, token", [
    ("FIVE TIMES", "five"), ("HALF", "half"), ("TWICE", "twice"), ("A TRILLION", "trillion"), ("ten billion", "ten"),
    ("THRICE", "thrice"), ("DOUBLE", "double"), ("TRIPLE", "triple"), ("A QUARTER", "quarter"), ("TWENTY", "twenty"),
    ("NINETY", "ninety"), ("A HUNDRED", "hundred"), ("THOUSAND", "thousand"), ("MILLION", "million"),
    ("TWELVE", "twelve"), ("ONE", "one"), ("MANY TIMES", "times"), ("PERCENT", "percent"),
    ("%", "%"), ("$", "$"), ("£", "£"), ("€", "€"), ("¥", "¥"), ("½", "½"), ("⅞", "⅞"), ("X²", "²"), ("Ⅻ", "Ⅻ"),
])
def test_a_number_word_a_numeral_or_a_sign_is_a_figure_and_refused_by_name(label, token):
    errs = _errs([_side("right", label=label)])
    assert any("balance: right" in e and "figure" in e and repr(token) in e and "two bars" in e for e in errs), errs


@pytest.mark.parametrize("label", ["MOAT", "PAPER", "STONE", "OFTEN", "BONE", "ONEROUS", "THREATS", "SOMETIMES"])
def test_a_word_that_only_contains_a_number_word_is_a_name(label):
    assert _errs([_side("right", label=label)]) == [], "whole words only: 'stone' is not 'one', 'often' is not 'ten'"


def test_a_load_s_mass_is_a_stopaction_material():
    assert _errs([_side("left", mass="metal")]) == []
    assert any(e.startswith("balance: left") and "mass" in e for e in _errs([_side("left", mass="lead")]))


# Review F2 (HIGH): a name is kept inside its HALF of the room (off the post), and a name that cannot fit its half is a
# WARN with its numbers (E99 s106: advice, never a refusal).
def test_a_name_that_fits_its_half_is_not_advised():
    assert B.balance_advice(BAL, "16:9") == []


def test_a_name_that_can_only_cross_the_post_is_advised_with_its_numbers_and_its_fix_never_refused():
    """E99 s106 (the parent, round 4): a name crossing the post is a PLACEMENT finding, not a truth rule. OPPORTUNITY on
    the RIGHT pan of the 480 px room flush with the stage's right edge has no outward room at the floor, so no placement
    satisfies both rules: the compiler WARNs with its numbers and the fix, and the row compiles (the engine pins it at
    the stage margin - the least-bad frame)."""
    e = _side("right", label="OPPORTUNITY", icon=None)
    assert _errs([e]) == [], "advice, never a refusal (s106): only the truth rules refuse"
    warns = [w_ for w_ in B.balance_advice(e, "16:9") if w_.startswith("balance: right")]
    assert len(warns) == 1, warns
    w0 = warns[0]
    assert "OPPORTUNITY" in w0 and "pinned" in w0 and "across the post's guard" in w0, w0
    assert re.search(r"~\d+ px", w0) and re.search(r"\d+ px from the post's guard to the stage margin", w0), w0
    assert "a wider room, a room away from the stage's edge, or a shorter name" in w0, w0


def test_the_pinned_name_stays_inside_the_stage_on_the_served_player():
    """... and the frame it ships: the flush-right room with the reviewer's names - OPPORTUNITY pinned at the stage
    margin, never outside the stage, its centre in its pan's half."""
    got, sp = _names_served({"left": "THREAT", "right": "OPPORTUNITY"})
    room = sp["target"]
    cx = (room["x0"] + room["x1"]) / 2 * 1920
    op = got["OPPORTUNITY"]
    assert op["step"] == "pinned", op
    assert op["box"][0] >= -0.5 and op["box"][1] <= 1920.5, op                        # 0 px outside the stage
    assert op["box"][1] <= 1920 - B.BALANCE_STAGE_MARGIN + 3.0, op                   # at the margin (the halo's reach)
    assert cx <= (op["box"][0] + op["box"][1]) / 2 <= room["x1"] * 1920, op          # its centre in its pan's half


def test_the_same_name_in_a_room_away_from_the_stage_s_edge_is_a_load():
    e = _side("right", label="OPPORTUNITY", icon=None)
    e["target"] = {"kind": "region", "x0": 0.55, "y0": 0.22, "x1": 0.80, "y1": 0.80}
    assert _errs([e]) == [], "step 2: it overhangs outward, off the post"
    assert any("overhangs OUTWARD" in w_ for w_ in B.balance_advice(e, "16:9"))


def test_a_name_a_hair_too_wide_is_fitted_by_size_to_its_half():
    """Step 1: the size comes down to fit the half, never below the text floor - a 1.5 % band at 60 px over 59.08 px,
    so it is read on the fit itself (whole-letter width estimates step over it)."""
    room = B._balance_room_px(BAL, "16:9")
    half = room["w"] / 2 - B.BALANCE_POST_CLEAR_PX
    fit = B.balance_name_fit("left", half + 2, room, 1920)
    assert fit["step"] == "shrunk" and B.BALANCE_LABEL_FLOOR <= fit["size"] < B.BALANCE_LABEL_PX, fit
    assert abs(fit["w"] - half) < 1e-9 and fit["x1"] <= room["x"] + room["w"] / 2 - B.BALANCE_POST_CLEAR_PX + 1e-9, fit


def test_a_name_too_wide_at_the_floor_is_advised_as_an_overhang():
    """Step 2 on the LEFT of the 480 px room (the side with the stage to overhang into)."""
    room = B._balance_room_px(BAL, "16:9")
    w = B.BALANCE_LABEL_EM * B.BALANCE_LABEL_PX * len("OPPORTUNITY") + B.BALANCE_NAME_PAD
    assert B.balance_name_fit("left", w, room, 1920)["step"] == "overhang"
    warns = B.balance_advice(_side("left", label="OPPORTUNITY", icon=None), "16:9")
    assert len(warns) == 1 and warns[0].startswith("balance: left") and "overhangs OUTWARD" in warns[0], warns


def test_the_compiler_s_name_fit_is_the_module_s():
    """The fit, mirrored: the same step and the same box as species/balance.mjs balanceNameFit on the same widths."""
    import subprocess
    room = B._balance_room_px(BAL, "16:9")
    cases = [("left", 150), ("right", 150), ("left", 222), ("left", 363), ("right", 363), ("right", 225)]
    js = ("import('./content/video_engine/scripts/species/balance.mjs').then((m) => { const b = " + json.dumps(room)
          + "; const cx = b.x + b.w / 2, A = m.BALANCE.ARM_K * b.w; console.log(JSON.stringify("
          + json.dumps(cases) + ".map(([s, w]) => m.balanceNameFit(s, s === 'left' ? cx - A : cx + A, w, b, cx, 1920)))); })")
    got = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
    for (side, w), j in zip(cases, got):
        py = B.balance_name_fit(side, w, room, 1920)
        assert py["step"] == j["step"] and abs(py["size"] - j["size"]) < 1e-9, (side, w, py, j)
        assert abs(py["x0"] - (j["x"] - j["w"] / 2)) < 1e-6 and abs(py["x1"] - (j["x"] + j["w"] / 2)) < 1e-6, (side, w, py, j)


# ---- the gate ------------------------------------------------------------------------------------------------------


def test_the_gate_credits_the_draw_each_load_and_the_tip():
    assert G.SPECIES_EVENTS["balance"] == ("at", "left.at", "right.at", "tip.at")
    assert "balance" in G.POINTING_KINDS
    scenes = [{"span": [10.0, 22.0], "species": [json.loads(json.dumps(TIPPED))]}]
    assert sorted(G._species_events(scenes)) == [11.43, 12.65, 16.56, 19.0]


# ---- the module, the engine, the mirrors ---------------------------------------------------------------------------


def test_the_module_is_inlined_immediately_before_the_ring_region_and_registers_its_painter():
    src = ENGINE.read_text(encoding="utf-8")
    b = src.index("/* KINETICS:BEGIN balance */")
    ring = src.index("/* KINETICS:BEGIN ring */")
    between = src[b:ring]
    assert between.rstrip().endswith("/* KINETICS:END */") and between.count("/* KINETICS:BEGIN") == 1, \
        "the balance region sits IMMEDIATELY before the ring region (the plan's one engine slot)"
    assert "SPECIES_PAINTERS.balance = paintBalance" in MODULE.read_text(encoding="utf-8")
    assert MODULE.read_text(encoding="utf-8").splitlines()[0].strip() == "/* SPACE: stage */"


def test_the_painter_context_exposes_the_prop_hatch():
    src = ENGINE.read_text(encoding="utf-8")
    ctx = src[src.index("const painter = SPECIES_PAINTERS[sp.kind];"):]
    ctx = ctx[:ctx.index("return;")]
    assert "propHatchLines" in ctx, "T6b's hatch reaches a stage painter by name, through the ctx (E99 s128: a prop in the world)"


@pytest.mark.parametrize("surface", ["chip-board", "freeze-trough", "count-array"])
def test_the_new_ctx_key_changes_no_other_stage_painter_s_frame(surface):
    """Review F8: the behaviour, not the text - a stage painter's committed golden renders to the same pixels through
    the engine that now hands every painter `propHatchLines` (the chip, the freeze's light, the count array)."""
    import render_baseline as RB
    assert RB.check([surface]) == []


def _module_dial(name: str) -> float:
    m = re.search(rf"\b{name}:\s*([0-9.]+)", MODULE.read_text(encoding="utf-8"))
    assert m, name
    return float(m.group(1))


def test_the_compiler_s_clocks_mirror_the_module_s():
    assert B.BALANCE_DRAW_S == _module_dial("DRAW_S")
    assert B.BALANCE_LAND_S == _module_dial("LAND_SEEN_S")
    assert B.BALANCE_TIP_SEEN_S == _module_dial("TIP_SEEN_S")
    assert B.BALANCE_TIP_DEG == _module_dial("TIP_DEG")
    assert B.BALANCE_LABEL_PX == _module_dial("LABEL_PX") and B.BALANCE_LABEL_EM == _module_dial("LABEL_EM")
    assert B.BALANCE_POST_CLEAR_PX == _module_dial("POST_CLEAR"), "the advice's half of the room is the engine's"
    assert B.BALANCE_LABEL_FLOOR == _module_dial("LABEL_FLOOR") and B.BALANCE_STAGE_MARGIN == _module_dial("STAGE_MARGIN")
    assert B.BALANCE_NAME_PAD == _module_dial("NAME_PAD"), "a name fits by its painted width, both sides"
    for k, v in B.BALANCE_GEOM.items():   # ANTIC_PX is stopaction's STOP.ANTIC_PX, the rest the balance's own dials
        want = float(re.search(r"\bANTIC_PX:\s*([0-9.]+)", (ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs").read_text(encoding="utf-8")).group(1)) if k == "ANTIC_PX" else _module_dial(k)
        assert v == want, k


def test_the_card_is_the_stage_species_card():
    cards = {c["token"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    c = cards["balance"]
    assert c["id"] == "species:balance" and c["when"] is None and c["status"] == "wired"
    assert c["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/balance.mjs", "symbol": "paintBalance"}
    assert c["proof"]["golden"] == "balance-level"


# ---- the golden and the served player ------------------------------------------------------------------------------


def test_the_golden_is_registered_and_its_source_compiles():
    import build_golden_sources as GS
    assert "balance-level" in GS.SURFACES and "balance-level" in GS.FRAME_T
    tl, _ = GS.SURFACES["balance-level"]()
    sp = [s for s in tl["scenes"][0]["species"] if s["kind"] == "balance"]
    assert len(sp) == 1 and "tip" not in sp[0], "the golden is the LEVEL beat - H has no sentence that tips two unquantified forces"
    assert GS.FRAME_T["balance-level"] > max(sp[0]["left"]["at"], sp[0]["right"]["at"]) + 2.0, "judged once it has settled level"


PROBE = """() => {
  const g = document.querySelector('#species g.balance, #species-under g.balance');
  if (!g) return null;
  const beam = g.querySelector('.bal-beam'), pans = [...g.querySelectorAll('.bal-pan')];
  const labs = [...g.querySelectorAll('text.bal-label')];
  const hatch = g.querySelector('.bal-hatch');
  return { deg: +beam.dataset.deg, pans: pans.map((p) => p.getAttribute('transform')),
           labels: labs.map((l) => [l.textContent, parseFloat(getComputedStyle(l).fontSize), +l.getAttribute('opacity')]),
           hatch: hatch ? [+hatch.getAttribute('opacity'), hatch.querySelectorAll('path').length] : null,
           html: g.outerHTML };
}"""


def _served(tl: dict, uris: dict, times: list[float], order: list[float] | None = None) -> dict[float, dict]:
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    out: dict[float, dict] = {}
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "bal.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch(headless=True)
                page = b.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/bal.html", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                for t in (order or times):
                    RB.frame_png(page, t, (w, h))
                    out.setdefault(t, page.evaluate(PROBE))
                b.close()
        finally:
            srv.shutdown()
    return out


@pytest.fixture(scope="module")
def level_reads():
    import build_golden_sources as GS
    tl, uris = GS.SURFACES["balance-level"]()
    t = GS.FRAME_T["balance-level"]
    forward = _served(tl, uris, [t])
    scrubbed = _served(tl, uris, [t], order=[t + 3.0, 2.0, t - 4.0, t])   # a seek is the play: the frame at t, cold or scrubbed
    return forward[t], scrubbed[t]


def test_the_golden_beat_settles_level_with_both_loads_named(level_reads):
    read, _ = level_reads
    assert read is not None, "the balance paints on the served player"
    assert abs(read["deg"]) < 0.05, f"both sides weighed: the beam settles LEVEL ({read['deg']} deg)"
    assert [lab[0] for lab in read["labels"]] == ["MOAT", "PAPER"]
    assert all(lab[1] >= 59.08 and lab[2] > 0.99 for lab in read["labels"]), read["labels"]   # the s90 phone floor


def test_the_base_rests_on_t6b_s_hatch(level_reads):
    read, _ = level_reads
    assert read["hatch"] is not None and read["hatch"][0] > 0.5 and read["hatch"][1] >= 2, read["hatch"]


def test_the_pans_hang_plumb(level_reads):
    read, _ = level_reads
    assert all(p and "rotate" not in p and "matrix" not in p for p in read["pans"]), read["pans"]


def test_a_scrubbed_frame_is_the_played_frame(level_reads):
    forward, scrubbed = level_reads
    assert forward["html"] == scrubbed["html"]


TIP_AT = 9.0


def _tip_bed() -> tuple[dict, dict]:
    """A NEUTRAL synthetic tip on a plain plate (review F6: no reference beat is committed): two made-up forces, EAST
    weighed on 3.0 and WEST on 5.0, and the balance tips WEST on 9.0."""
    import build_golden_sources as GS
    e = {"kind": "balance", "at": 2.0, "dur": 12.0, "target": {"kind": "region", "x0": 0.2, "y0": 0.18, "x1": 0.8, "y1": 0.86},
         "left": {"label": "EAST", "at": 3.0}, "right": {"label": "WEST", "at": 5.0}, "tip": {"at": TIP_AT, "to": "right"}}
    assert B.validate_species([dict(e)], (0, 0, 0), "plate-plain") == []
    world = {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, GS.RUNTIME], "docks": [], "species": [e]}]
    return GS._timeline("P70 T7: a synthetic tip", scenes, {}, "16:9"), GS._base_uris()


@pytest.fixture(scope="module")
def tip_reads():
    tl, uris = _tip_bed()
    ts = [round(TIP_AT + d, 3) for d in (0.0, 0.15, 0.35, 0.6, 1.2, 2.5)]
    forward = _served(tl, uris, ts)
    probe = round(TIP_AT + 0.35, 3)
    scrubbed = _served(tl, uris, [probe], order=[TIP_AT + 2.5, 3.2, TIP_AT - 1.0, TIP_AT + 0.1, probe])
    return ts, forward, scrubbed[probe]


def test_the_served_tip_reads_the_module_s_law(tip_reads):
    ts, reads, _ = tip_reads
    deg = {round(t - TIP_AT, 3): reads[t]["deg"] for t in ts}
    tip_deg = B.BALANCE_TIP_DEG
    assert abs(deg[0.0]) < 0.05, deg                      # level on the word, then it goes
    assert deg[0.35] > tip_deg + 1.5, deg                 # the ONE visible overshoot, past TIP_DEG toward the right
    assert tip_deg - 1.0 < deg[0.6] < tip_deg, deg        # the swing back is under a degree short of the rest
    assert abs(deg[2.5] - tip_deg) < 0.05, deg            # at rest, tipped
    assert all(p and "rotate" not in p for t in ts for p in reads[t]["pans"]), "the pans hang plumb through the tip"


def test_the_tip_scrubbed_is_the_tip_played(tip_reads):
    """Review F8: the overshoot's frame reached cold, after the rest, the landing and the approach, is the played one."""
    _, forward, scrubbed = tip_reads
    assert scrubbed["html"] == forward[round(TIP_AT + 0.35, 3)]["html"]


LABEL_PROBE = """() => [...document.querySelectorAll('g.balance text.bal-label')].map((l) => {
  const r = l.getBoundingClientRect(), st = document.getElementById('stage').getBoundingClientRect();
  const k = 1920 / st.width;
  return [l.textContent, (r.left - st.left) * k, (r.right - st.left) * k, (r.top - st.top) * k, (r.bottom - st.top) * k]; })"""


def _names_served(names: dict) -> tuple[dict, dict]:
    """The golden's own room (480 px, flush with the stage's right) with NAMES as the loads, read on the served player:
    each name's stage box and its fit step, and the pans' x."""
    import build_golden_sources as GS
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    saved = [json.loads(json.dumps(x)) for x in GS.BAL_SPECIES]
    try:
        for side, name in names.items():
            GS.BAL_SPECIES[0][side].pop("icon", None)
            GS.BAL_SPECIES[0][side]["label"] = name
        tl, uris = GS.balance_level()
        sp = json.loads(json.dumps(GS.BAL_SPECIES[0]))
    finally:
        GS.BAL_SPECIES[:] = saved
    t = GS.FRAME_T["balance-level"]
    w, h = RB.STAGE["16:9"]
    probe = """() => { const st = document.getElementById('stage').getBoundingClientRect(), k = 1920 / st.width;
      const box = (e) => { const r = e.getBoundingClientRect(); return [(r.left - st.left) * k, (r.right - st.left) * k,
                                                                          (r.top - st.top) * k, (r.bottom - st.top) * k]; };
      return [...document.querySelectorAll('g.balance text.bal-label')].map((l) => [l.textContent, box(l), l.dataset.fit,
        parseFloat(getComputedStyle(l).fontSize), box(l.closest('.bal-pan').querySelector('.bal-bowl'))]); }"""
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "names.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch(headless=True)
                page = b.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/names.html", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                RB.frame_png(page, t, (w, h))
                got = {n: {"box": bx, "step": st, "size": fs, "pan": pb} for n, bx, st, fs, pb in page.evaluate(probe)}
                b.close()
        finally:
            srv.shutdown()
    return got, sp


def test_a_name_too_wide_for_its_half_overhangs_outward_under_its_own_pan_never_across_the_post():
    """Round 3, the 480 px room: OPPORTUNITY on the LEFT pan cannot fit its half even at the floor, so it stays centred
    under its OWN pan as near as it can and overhangs OUTWARD - its box never crosses the post's guard, its centre stays
    in its pan's half, it never leaves the stage, and the compiler WARNs it."""
    got, sp = _names_served({"left": "OPPORTUNITY", "right": "THREAT"})
    room = sp["target"]
    cx = (room["x0"] + room["x1"]) / 2 * 1920
    op, th = got["OPPORTUNITY"], got["THREAT"]
    assert op["step"] == "overhang" and abs(op["size"] - B.BALANCE_LABEL_FLOOR) < 0.01, op
    assert op["box"][1] <= cx - B.BALANCE_POST_CLEAR_PX + 0.5, op                    # never across the post's guard
    centre = (op["box"][0] + op["box"][1]) / 2
    assert room["x0"] * 1920 - 0.5 <= centre <= cx, op                             # its centre stays in its pan's half
    assert op["box"][0] >= B.BALANCE_STAGE_MARGIN - 0.5, op                        # ... and on the stage
    assert th["step"] in ("fit", "shrunk") and th["size"] >= B.BALANCE_LABEL_FLOOR and th["box"][0] >= cx + B.BALANCE_POST_CLEAR_PX - 0.5 and th["box"][1] <= room["x1"] * 1920 + 2.5, th   # the room's edge is soft: the hand face's slant sits ~1.6 px right of the advance
    warns = B.balance_advice(sp, "16:9")
    assert [w_.split(":")[1].strip().split()[0] for w_ in warns] == ["left"] and "overhangs OUTWARD" in warns[0], warns


def test_the_reviewer_s_names_in_a_room_away_from_the_edge_keep_off_the_post_on_the_served_player():
    """... and the reviewer's orientation (THREAT left, OPPORTUNITY right) in the same 480 px room moved in from the
    stage's edge: OPPORTUNITY overhangs OUTWARD under its own pan, never across the post, on the stage."""
    import build_golden_sources as GS
    saved = [json.loads(json.dumps(x)) for x in GS.BAL_SPECIES]
    try:
        GS.BAL_SPECIES[0]["target"] = {"kind": "region", "x0": 0.55, "y0": 0.22, "x1": 0.80, "y1": 0.80}
        got, sp = _names_served({"left": "THREAT", "right": "OPPORTUNITY"})
    finally:
        GS.BAL_SPECIES[:] = saved
    room = sp["target"]
    cx = (room["x0"] + room["x1"]) / 2 * 1920
    op, th = got["OPPORTUNITY"], got["THREAT"]
    assert op["step"] == "overhang" and op["box"][0] >= cx + B.BALANCE_POST_CLEAR_PX - 0.5, op
    assert cx <= (op["box"][0] + op["box"][1]) / 2 and op["box"][1] <= 1920 - B.BALANCE_STAGE_MARGIN + 3.0, op
    assert th["box"][1] <= cx - B.BALANCE_POST_CLEAR_PX + 0.5 and th["box"][1] <= op["box"][0], (th, op)   # never meet


# ---- the footprint: published to the caption and to the placers (round 3) --------------------------------------------


def test_the_footprint_is_published_to_every_placer_through_the_reserve():
    foot = B.balance_footprint(BAL, "16:9")
    assert foot and B.balance_boxes([BAL], "16:9") == [foot]
    assert foot in B.newsreel_boxes([BAL], "16:9"), "the reserve every dock / stamp / prop placer is handed"
    assert B.newsreel_boxes([{"kind": "callout", "at": 1.0, "dur": 1.0}], "16:9") == [], "a row with no balance: unchanged"


def test_a_dock_parks_clear_of_the_balance():
    import build_golden_sources as GS
    tl, _ = GS.SURFACES["balance-level"]()
    world = tl["scenes"][0]["world"]
    sp = [e for e in tl["scenes"][0]["species"] if e["kind"] == "balance"]
    foot = B.balance_footprint(sp[0], "16:9")
    place = B.dock_place(world, "16:9", B.newsreel_boxes(sp, "16:9"))
    assert place is not None
    box = {k: place[k] for k in ("x", "y", "w", "h")}
    assert not B._rects_meet(box, foot), (box, foot)


def test_the_caption_takes_the_rail_while_the_balance_s_names_stand():
    scenes = [{"span": [0.0, 30.0], "species": [dict(BAL)]}]
    assert B._readable_species_during(scenes, BAL["at"] + 1.0, BAL["at"] + 2.0)
    assert not B._readable_species_during(scenes, 0.0, BAL["at"] - 0.5), "only while it stands"


def test_the_golden_room_is_clear_of_the_caption_rail():
    import build_golden_sources as GS
    assert B.balance_advice(GS.BAL_SPECIES[0], "16:9") == []


FOOT_PROBE = """() => { const st = document.getElementById('stage').getBoundingClientRect(), k = 1920 / st.width;
  const box = (e) => { const r = e.getBoundingClientRect(); return [(r.left - st.left) * k, (r.top - st.top) * k,
                                                                      (r.right - st.left) * k, (r.bottom - st.top) * k]; };
  /* the PAINTED parts only: the hatch's lines run the whole stage under their mask, so a group's box is the stage's */
  const parts = [...document.querySelectorAll('g.balance :is(.bal-base, .bal-base-fill, .bal-arm, .bal-ring, .bal-pin, '
    + '.bal-hanger, .bal-bowl, .bal-bowl-fill, .bal-glyph, .bal-prop, .bal-label)')].filter((e) => +e.closest('g.balance').getAttribute('opacity') > 0);
  const bs = parts.map(box).filter((b) => b[2] > b[0] && b[3] > b[1]);
  const bal = bs.length ? [Math.min(...bs.map((b) => b[0])), Math.min(...bs.map((b) => b[1])),
                           Math.max(...bs.map((b) => b[2])), Math.max(...bs.map((b) => b[3]))] : null;
  const cap = document.getElementById('caption');
  const words = cap ? [...cap.querySelectorAll('.cw')].filter((w) => w.getBoundingClientRect().width > 0) : [];
  return { bal, cap: words.map(box) }; }"""


def _stamped_like_a_build(tl: dict) -> dict:
    """The caption pages as the compiler's main() stamps them at 16:9 (`:11932-:11938`): a page a readable species
    overlaps takes the anchor and reserves the rail. A golden's `_timeline` does not run that stamping - which is why the
    round-2 bed showed its caption mid-stage over the scale."""
    pages = tl["caption_pages"]
    tl = dict(tl)
    tl["caption_pages"] = [{**pg, **({"cap_mode": "anchor", "cap_reserve": "readable-species"}
                                     if B._readable_species_during(tl["scenes"], pg["s"], B._caption_display_end(pages, i))
                                     else {"cap_mode": "stage"})} for i, pg in enumerate(pages)]
    return tl


@pytest.mark.parametrize("which", ["golden", "tip"])
def test_the_footprint_covers_what_is_painted_and_the_caption_keeps_off_it(which):
    """The published box holds every painted pixel of the balance (its names, both pans at the tip's widest swing, the
    loads falling in) and the caption, placed as a build places it, never meets it."""
    import build_golden_sources as GS
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    if which == "golden":
        tl, uris = GS.SURFACES["balance-level"]()
        ts = [12.5, 12.9, 13.5, 16.5, 17.0, 20.79]
    else:
        tl, uris = _tip_bed()
        ts = [3.2, 5.2, 5.6, TIP_AT + 0.32, TIP_AT + 0.64, TIP_AT + 2.5]
    tl = _stamped_like_a_build(tl)
    sp = [e for e in tl["scenes"][0]["species"] if e["kind"] == "balance"][0]
    f = B.balance_footprint(sp, "16:9")
    w, h = RB.STAGE["16:9"]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "foot.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                b = pw.chromium.launch(headless=True)
                page = b.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/foot.html", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                reads = {}
                for t in ts:
                    RB.frame_png(page, t, (w, h))
                    reads[t] = page.evaluate(FOOT_PROBE)
                b.close()
        finally:
            srv.shutdown()
    fx0, fy0, fx1, fy1 = f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]
    for t, r in reads.items():
        x0, y0, x1, y1 = r["bal"]
        assert fx0 - 0.5 <= x0 and fy0 - 0.5 <= y0 and x1 <= fx1 + 0.5 and y1 <= fy1 + 0.5, (t, r["bal"], f)
        for c in r["cap"]:
            assert c[2] <= fx0 or c[0] >= fx1 or c[3] <= fy0 or c[1] >= fy1, (t, c, f)   # the caption never meets it

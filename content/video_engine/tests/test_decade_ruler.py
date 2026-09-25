"""P71 T14 (was P69 T55; RESCOPED by the BOOM frame verification) - THE DECADE RULER: a scrolling time-passage ground.

The witness is REAL FRAMES (docs/research/runs/bravos-watch/jx3Ll-GJtMY/verify/VERIFY.md row T32, 05:50.5-06:10): a
full-width tick ruler with large faded decade numerals enters at the right edge over the blurred chart and SCROLLS -
1980 / 1990 at 05:51.0 - settling on 2000 / 2010 / 2020 by 05:52; the chips pop in a ROW ABOVE it. There are no year
labels on the chips, no pins and no tick alignment ("cards pinned at their years" was Gemini's invention, retired).

The token is a STAGE species: `{"kind": "ruler", at, dur, from, to, settle: [<decade>, ...], y?, idle?}`. Its law and
painter are species/ruler.mjs (pinned by tests/kinetics/ruler.test.mjs); this file pins the compiler's grammar (every
key refused BY NAME when malformed or misplaced - `settle` was accepted and ignored on every other kind at 7789afa),
the WARN on a chip that prints a year over it (s109 (c) / s106), the gate (the scroll TRAVELS: one event at its word;
the held ruler is ground), the engine's wiring, the card and the recipe, and the scroll read on the SERVED player (the
golden `decade-ruler-scroll`): the settle decades land exactly on their marks, and every frame is a pure function of t.
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
MODULE = ROOT / "content/video_engine/scripts/species/ruler.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/species.json"
RECIPE = ROOT / "content/video_engine/effects/recipes/the-decade-ruler.json"
PLATE = "plate-desk"
RULER = {"kind": "ruler", "at": 50.5, "dur": 10.0, "from": 1980, "to": 2030, "settle": [2000, 2010, 2020]}


def _errs(entries, plate=PLATE, ken=(0, 0, 0)):
    return B.validate_species([dict(e) for e in entries], ken, plate)


def _chip(label: str, at: float = 53.5, dur: float = 6.0) -> dict:
    return {"kind": "chip", "at": at, "dur": dur, "icon": "cpu", "label": label, "target": {"kind": "point", "x": 0.5, "y": 0.3}}


# ---- the grammar -------------------------------------------------------------------------------------------------


def test_the_token_is_a_stage_species_with_no_target_the_compiler_accepts_on_a_plate_and_on_a_page():
    assert "ruler" in B.SPECIES_KINDS and "ruler" not in B.PAGE_SPECIES
    assert B.SPECIES_TARGETS["ruler"] == (), "the ruler is the stage's full width - it points at nothing"
    assert _errs([RULER]) == []
    assert _errs([RULER], plate="ledger:ev-railway-index-v1:line:139:right") == [], "over a page it is a ground too"


@pytest.mark.parametrize("patch", [
    {"settle": [2000, 2010]},
    {"settle": [1990, 2000, 2010, 2020]},
    {"from": 2000, "settle": [2000, 2010]},   # the strip may start on its first settle decade
    {"to": 2020},                             # ... and end on its last (the ruler visibly ends: the author's truth)
    {"y": 0.72},
    {"idle": "drift"},
    {"dur": 1.9},                             # the scroll (1.5 s) and the leave (0.4 s) and not a frame more
])
def test_the_forms_the_grammar_takes(patch):
    assert _errs([dict(RULER, **patch)]) == []


@pytest.mark.parametrize("patch, needle", [
    ({"settle": [2000, 2010, 2040]}, "outside"),         # a settle year the strip does not hold (the plan's constraint)
    ({"settle": [1970, 1980, 1990]}, "outside"),
    ({"settle": [2000, 2005]}, "decade"),
    ({"settle": [2010, 2000]}, "consecutive"),
    ({"settle": [2000, 2020]}, "consecutive"),           # 2010 would print between them: the window names what it shows
    ({"settle": [2000]}, "2-4"),
    ({"from": 1970, "to": 2050, "settle": [1980, 1990, 2000, 2010, 2020]}, "2-4"),
    ({"settle": "2000s"}, "list"),
    ({"settle": [2000.0, 2010]}, "decade"),
    ({"settle": [True, 2010]}, "decade"),
    ({"settle": None}, "settle"),
    ({"from": None}, "from"),
    ({"to": None}, "to"),
    ({"from": 2030}, "before"),
    ({"from": 1980.5}, "year"),
    ({"to": True}, "year"),
    ({"from": 212}, "year"),
    ({"y": 0.02}, "y"),
    ({"y": "low"}, "y"),
    ({"dur": 1.2}, "lands"),
    ({"idle": "wobble"}, "idle"),
])
def test_a_malformed_ruler_is_refused_by_name(patch, needle):
    entry = {k: v for k, v in dict(RULER, **patch).items() if v is not None}
    errs = _errs([entry])
    assert any(e.startswith("ruler:") and needle in e for e in errs), errs


@pytest.mark.parametrize("key", ["pins", "pin", "marks", "labels", "label", "cards", "chips", "tick_at", "leader"])
def test_a_key_that_would_pin_a_card_to_a_year_is_refused_as_what_it_is(key):
    """The ruler implies no date for any chip: no pin, no leader to a tick, no label it did not print (s109 (c)). A key
    that asks for one is refused BY NAME, with the reason - never accepted and ignored."""
    errs = _errs([dict(RULER, **{key: [2007]})])
    assert any(e.startswith("ruler:") and repr(key) in e and "pins nothing" in e for e in errs), errs


@pytest.mark.parametrize("key", ["target", "color", "series", "text"])
def test_any_other_key_is_refused_by_name(key):
    errs = _errs([dict(RULER, **{key: 1})])
    assert any(e.startswith("ruler:") and repr(key) in e and "a ruler takes only" in e for e in errs), errs


@pytest.mark.parametrize("entry", [
    _chip("CHIPS"),
    {"kind": "spotlight", "at": 5.0, "dur": 2.0, "target": {"kind": "point", "x": 0.5, "y": 0.4}},
    {"kind": "span", "at": 5.0, "dur": 2.0, "from": 3, "to": 9, "label": "THE RUN-UP"},
])
def test_settle_off_a_ruler_is_refused_by_name(entry):
    """At 7789afa `settle` on a chip, a spotlight or a flow was ACCEPTED AND IGNORED (the RED probe, R26-307's class)."""
    errs = B._validate_entry(dict(entry, settle=[2000, 2010]))
    assert any("'settle'" in e and "ruler" in e for e in errs), errs


def test_the_when_says_what_sentence_calls_for_it_and_when_not():
    when = B.SPECIES_WHEN["ruler"]
    assert "lag" in when and "decade" in when
    assert "single date" in when and "pins no" in when


def test_the_compiler_s_clock_is_the_module_s():
    src = MODULE.read_text(encoding="utf-8")
    dial = lambda name: float(re.search(rf"\b{name}: ([0-9.]+)", src).group(1))
    assert B.RULER_SCROLL_S == dial("SCROLL_S")
    assert B.RULER_OUT_S == dial("OUT_S")
    assert B.RULER_SETTLE_N == (int(dial("SETTLE_MIN")), int(dial("SETTLE_MAX")))
    assert src.splitlines()[0] == "/* SPACE: stage */"


# ---- the honesty WARN (s109 (c), s106) -----------------------------------------------------------------------------


def test_a_chip_that_prints_a_year_over_a_ruler_is_a_warn_with_its_numbers():
    notes = B.ruler_row_advice([RULER, _chip("SMARTPHONES 2007")])
    assert len(notes) == 1, notes
    assert "2007" in notes[0] and "SMARTPHONES 2007" in notes[0] and "50.5" in notes[0] and "pins nothing" in notes[0]
    assert "WARN" not in B.validate_species([RULER, _chip("SMARTPHONES 2007")], (0, 0, 0), PLATE), "advice, never a refusal"
    assert _errs([RULER, _chip("SMARTPHONES 2007")]) == []


@pytest.mark.parametrize("rows", [
    [RULER, _chip("SMARTPHONES")],                      # no year: the witnessed form
    [RULER, _chip("SMARTPHONES 2007", at=61.0)],        # the chip lands after the ruler has left
    [_chip("SMARTPHONES 2007")],                        # no ruler: a chip's year is its own business
])
def test_no_warn_where_nothing_reads_as_a_pin(rows):
    assert B.ruler_row_advice(rows) == []


# ---- the caption strip (E99 s106) - the line per aspect -----------------------------------------------------------


def test_the_compiler_s_line_and_band_are_the_module_s():
    src = MODULE.read_text(encoding="utf-8")
    dial = lambda name: float(re.search(rf"\b{name}: ([0-9.]+)", src).group(1))
    assert B.RULER_Y_DEFAULT == {"16:9": dial("Y"), "9:16": dial("Y_PORTRAIT")}
    assert B.RULER_BAND_HALF_PX == dial("TICK_DECADE_H") / 2 + dial("NUM_GAP") + dial("NUM_CAP") * dial("NUM_SIZE")


@pytest.mark.parametrize("aspect", ["16:9", "9:16"])
def test_the_default_line_clears_the_caption_strip_on_each_aspect(aspect):
    assert B.ruler_caption_advice([RULER], aspect) == []
    band, home = B.ruler_band_box(RULER, aspect), B.caption_home_box(aspect)
    assert not B._rects_meet(band, home, B.NEWSREEL_STRIP_PAD), (band, home)
    assert 0 <= band["y"] and band["y"] + band["h"] <= B.LPG.STAGE_PX[aspect][1], "on the stage"


@pytest.mark.parametrize("aspect, y", [("16:9", 0.646), ("16:9", 0.45), ("9:16", 0.646), ("9:16", 0.7)])
def test_a_band_on_the_caption_strip_is_a_warn_with_its_numbers_and_a_clear_y(aspect, y):
    entry = dict(RULER, y=y)
    notes = B.ruler_caption_advice([entry], aspect)
    assert len(notes) == 1, notes
    home = B.caption_home_box(aspect)
    band = B.ruler_band_box(entry, aspect)
    assert f"{home['y']}-{home['y'] + home['h']}" in notes[0] and f"{band['y']:g}" in notes[0] and aspect in notes[0]
    fix = float(re.search(r"y ([0-9.]+) clears it", notes[0]).group(1))
    assert B.ruler_caption_advice([dict(RULER, y=fix)], aspect) == [], "the suggested line does clear it"
    assert _errs([entry]) == [], "advice, never a refusal (E99 s106)"


def test_the_caption_warn_is_printed_on_the_row():
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    assert "ruler_row_advice(row_species) + ruler_caption_advice(row_species, ASPECT)" in src


# ---- the ink by the ground (P70 T1c's measured-ground helper) -----------------------------------------------------


def test_the_engine_hands_a_stage_species_the_measured_ground():
    src = ENGINE.read_text(encoding="utf-8")
    assert "groundLum: (pts) => groundLumAt(sc, pts)" in src
    assert "const groundLumAt = (sc, pts) =>" in src and "ringRgbAt(sc, wB," in src.split("const groundLumAt")[1][:700]
    assert '|| (s.species || []).some((e) => e && e.kind === "ruler"))) ringPlate(s.world.asset_id);' in src, \
        "a ruler's plate is decoded up front, so its first frame measures it"


# ---- the gate, the lint ---------------------------------------------------------------------------------------------


def test_the_scroll_is_one_event_at_its_word_and_the_held_ruler_is_ground():
    assert G.SPECIES_EVENTS["ruler"] == ("at",)
    ev = G._species_events([{"span": [45.0, 70.0], "species": [RULER]}])
    assert ev == [50.5]


def test_the_lint_offers_it_for_a_sentence_that_spans():
    assert "ruler" in L.ACT_SPECIES["SPANS"]


# ---- the engine, the card, the recipe -----------------------------------------------------------------------------


def test_the_engine_carries_the_module_after_the_stage_registry():
    src = ENGINE.read_text(encoding="utf-8")
    assert "/* KINETICS:BEGIN ruler */" in src
    assert src.index("const SPECIES_PAINTERS =") < src.index("/* KINETICS:BEGIN ruler */") < src.index("const paintSpecies =")
    assert src.index("/* KINETICS:BEGIN ease */") < src.index("/* KINETICS:BEGIN ruler */"), "it reads hermite"
    assert "SPECIES_PAINTERS.ruler = paintRuler" in src


def test_the_card_is_a_species_card_with_its_when_pulled_from_the_compiler():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["species:ruler"]
    assert card["token"] == "ruler" and card["when"] is None and card["serves"] == ["SPANS"]
    assert card["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/ruler.mjs", "symbol": "paintRuler"}
    assert card["dials"] == {"module": "content/video_engine/scripts/species/ruler.mjs", "object": "RULER"}
    assert len(card["does"]) <= 240 and len(card["title"]) <= 40 and card["proof"]["golden"] == "decade-ruler-scroll"
    assert card["status"] == "wired" and "P71 T14" in card["doctrine"]


def test_the_recipe_is_a_candidate_that_composes_the_ruler_under_a_chip_row():
    r = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert r["id"] == "recipe:the-decade-ruler" and r["status"] == "candidate" and r["count"] == 0
    cards = [m["card"] for m in r["members"]]
    assert cards[0] == "species:ruler" and "species:chip" in cards
    assert r["use_when"]["act"].startswith("SPANS")
    assert "single date" in r["use_when"]["dont"] and "pin" in r["use_when"]["dont"]
    assert RECIPE.read_bytes().count(b"\r") == 0


# ---- the scroll, read on the served player ------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _served(tl: dict, uris: dict, aspect: str, ts: list[float]) -> list[dict]:
    """At each t, in ONE page scrubbed in the given order: the frame's hash and every numeral the ruler drew (its text and
    its x in stage px), so a seek from anywhere is the play and the settle is read off the drawn marks themselves."""
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[aspect]
    out: list[dict] = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "ruler.html"
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
                    nums = page.evaluate("""() => [...document.querySelectorAll('#species g.ruler text')]
                                              .map((n) => [n.textContent, parseFloat(n.getAttribute('x'))])""")
                    out.append({"hash": hashlib.sha256(RB.rgb_bytes(png)[1]).hexdigest(), "nums": nums})
                br.close()
        finally:
            srv.shutdown()
    assert not errs, errs
    return out


@needs_browser
def test_the_ruler_lands_its_settle_decades_exactly_on_their_marks():
    import build_golden_sources as GS
    import render_baseline as RB
    tl, uris, t, aspect = RB.load_surface("decade-ruler-scroll")
    w = RB.STAGE[aspect][0]
    entry = GS.DECADE_RULER
    mid, rest = _served(tl, uris, aspect, [entry["at"] + 0.5, t])
    got = dict(rest["nums"])
    assert sorted(got) == ["2000", "2010", "2020"], rest["nums"]
    src = MODULE.read_text(encoding="utf-8")
    left = float(re.search(r"\bSETTLE_L: ([0-9.]+)", src).group(1))
    right = float(re.search(r"\bSETTLE_R: ([0-9.]+)", src).group(1))
    assert abs(got["2000"] - left * w) < 0.01 and abs(got["2020"] - right * w) < 0.01, got
    assert "1980" in dict(mid["nums"]) or "1990" in dict(mid["nums"]), "mid-scroll the earlier decades pass"
    assert mid["hash"] != rest["hash"]


@needs_browser
@pytest.mark.parametrize("ground, rgb, ink", [("dark", None, "#F4E6C7"), ("cream", (244, 230, 199), "#25313C")])
def test_the_ruler_inks_by_the_ground_it_stands_on(ground, rgb, ink):
    """The golden's beat on its own dark plate, and on a CREAM plate: the ticks and numerals are chalk on the one and
    charcoal on the other, read off the served player at a COLD seek (the first frame measures the decoded plate)."""
    import build_golden_sources as GS
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface("decade-ruler-scroll")
    if rgb:
        uris = dict(uris, **{"plate-plain": GS.uri("image/png", GS.png_solid(64, 36, rgb))})
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "ruler.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)
                page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1.0).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                RB.frame_png(page, GS.DECADE_RULER["at"] + 0.5, (w, h))
                inks = page.evaluate("""() => [...document.querySelectorAll('#species g.ruler path')].map((n) => n.getAttribute('stroke'))
                                          .concat([...document.querySelectorAll('#species g.ruler text')].map((n) => n.getAttribute('style')))""")
                br.close()
        finally:
            srv.shutdown()
    assert inks and all(ink in v for v in inks), (ground, inks)


@needs_browser
def test_the_scroll_is_seek_safe():
    """A pure function of t: the frame mid-scroll is the same frame reached cold, from after it, or from before it."""
    import build_golden_sources as GS
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface("decade-ruler-scroll")
    t_in = GS.DECADE_RULER["at"] + 0.6
    cold = _served(tl, uris, aspect, [t_in])[0]["hash"]
    back = _served(tl, uris, aspect, [GS.DECADE_RULER["at"] + 6.0, t_in])[1]["hash"]
    fwd = _served(tl, uris, aspect, [GS.DECADE_RULER["at"] - 2.0, t_in])[1]["hash"]
    assert cold == back == fwd

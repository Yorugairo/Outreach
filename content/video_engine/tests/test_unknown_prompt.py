"""P71 T18 (was P69 T53): THE "?" AT THE UNKNOWN - a chip's `glyph: "?"`, the NEW `unknown` species (a large "?" landing on
its word at a point or a region, pulsing or held), the collage that recedes under the blur while it rises (F12), and the
predictions board (R13, a recipe).

At 7263013 `unknown` was refused as an unknown species kind by `_validate_entry`, a chip's `glyph` was ACCEPTED AND
IGNORED (review finding 7: no error named it, on the glyph chip or the stamp form) and `recipe:the-predictions-board` did
not exist. These tests pin the grammar and every by-name refusal the slice introduces (rule h, s106), the don't the plan
makes a refusal ("a "?" on a thing the same row states a figure for" - USE-WHEN :792, "where we can state a figure"), the
gate's credit (held = an annotation, 0 events past its landing, s91; a pulse = one event per blink, s99), the compiler's
and the gate's mirrors of the module's dials, the Bravos-measured pop (the SAME pop T17 measured off BOOM's failed-link
disc), the card, the recipe and the golden - and, in the player, that the "?" lands where it was put and that the blur
veil exists only when a row asks for it and clears when the "?" leaves."""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "scripts"))
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests"))
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests" / "golden"))
import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import ledger_page as LPG  # noqa: E402

CHIP_MJS = "./content/video_engine/scripts/species/chip.mjs"
FLOW_MJS = "./content/video_engine/scripts/species/flow.mjs"
ENGINE = ROOT / "docs" / "content-video-engine" / "samples" / "scene-evidence-engine.mjs"
TEMPLATE = ROOT / "docs" / "content-video-engine" / "samples" / "scene-evidence-player.template.html"
CARDS = ROOT / "content" / "video_engine" / "effects" / "cards" / "species.json"
RECIPE = ROOT / "content" / "video_engine" / "effects" / "recipes" / "the-predictions-board.json"
GOLDEN = "unknown-decide"


def chip(**extra) -> dict:
    """The HIS 01:48 shape: a node card the open question sits over (the Lucide `landmark` glyph, a sourced icon)."""
    entry = {"kind": "chip", "at": 5.0, "dur": 8.0, "icon": "landmark", "label": "RETURN ON IT",
             "target": {"kind": "point", "x": 0.5, "y": 0.5}}
    entry.update(extra)
    return entry


def stamp(**extra) -> dict:
    entry = {"kind": "chip", "form": "stamp", "arrive": "stamp", "at": 10.0, "dur": 6.0,
             "icon": "prop-icon-gpu-ai-accelerator-v1", "label": "NVIDIA", "ink": "charcoal",
             "target": {"kind": "point", "x": 0.5, "y": 0.36}}
    entry.update(extra)
    return entry


def unknown(**extra) -> dict:
    """H row 23's "Decide for yourself": the "?" in the newsroom's empty left third."""
    entry = {"kind": "unknown", "at": 5.0, "dur": 4.0, "target": {"kind": "point", "x": 0.13, "y": 0.42}}
    entry.update(extra)
    return entry


def errors(*entries: dict) -> list[str]:
    return B.validate_species(list(entries), (0, 0, 0), "plate-plain")


def node_json(js: str):
    r = subprocess.run(["node", "--input-type=module", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def module(name: str, path: str = CHIP_MJS) -> dict:
    return node_json(f"import {{ {name} }} from '{path}'; console.log(JSON.stringify({name}));")


# ---------------------------------------------------------------- the chip's "?"
@pytest.mark.parametrize("extra", [
    {"glyph": "?"},
    {"glyph": "?", "glyph_at": 8.0},
    {"glyph": "?", "state": "lit"},
    {"glyph": "?", "glyph_at": 6.0, "idle": "breath"},
    {"glyph": "?", "readability": "landscape-phone"},
    {"glyph": "?", "label": "S&P 500"},      # a NAME that carries a digit is a thing, not a figure
    {"glyph": "?", "label": "Q3 GUIDANCE"},
])
def test_a_chip_may_carry_the_question_and_the_entry_is_not_mutated(extra):
    entry = chip(**extra)
    before = copy.deepcopy(entry)
    assert errors(entry) == [], extra
    assert entry == before


@pytest.mark.parametrize("name, extra, needle", [
    ("another glyph", {"glyph": "!"}, "chip: glyph must be \"?\""),
    ("a glyph that is a word", {"glyph": "unknown"}, "chip: glyph must be \"?\""),
    ("a number", {"glyph": 1}, "chip: glyph must be \"?\""),
    ("glyph_at with no glyph", {"glyph_at": 8.0}, "chip: glyph_at times a \"?\""),
    ("glyph_at not a number", {"glyph": "?", "glyph_at": "soon"}, "chip: 'glyph_at' must be a number"),
    ("glyph_at on the chip's own word", {"glyph": "?", "glyph_at": 5.0}, "chip: glyph_at 5.0 is not after at 5.0"),
    ("glyph_at after it left", {"glyph": "?", "glyph_at": 13.5}, "not inside the chip's window"),
    ("with a tick", {"glyph": "?", "tick_at": 8.0}, "chip: glyph and tick_at on one chip"),
    ("with a tab", {"glyph": "?", "tab": "sell"}, "chip: glyph and tab on one chip"),
    ("with a cross", {"glyph": "?", "cross_at": 9.0}, "an open question or a failed claim"),
    ("landing crossed", {"glyph": "?", "state": "crossed"}, "an open question or a failed claim"),
    ("a label that states a figure", {"glyph": "?", "label": "$150-$200 /Barrel"}, "states a figure"),
    ("a label with a percentage", {"glyph": "?", "label": "RETURN 12%"}, "states a figure"),
    ("a label with a multiple", {"glyph": "?", "label": "2x LEVERAGE"}, "states a figure"),
    ("a label with a grouped number", {"glyph": "?", "label": "10,000 JOBS"}, "states a figure"),
])
def test_a_malformed_or_misplaced_question_on_a_chip_is_refused_by_name(name, extra, needle):
    errs = errors(chip(**extra))
    assert any(needle in e for e in errs), (name, errs)


@pytest.mark.parametrize("key, value", [("glyph", "?"), ("glyph_at", 12.0)])
def test_the_stamp_form_refuses_the_question_by_name(key, value):
    errs = errors(stamp(**{key: value}))
    assert any(e.startswith(f"chip stamp: {key} is not supported") for e in errs), errs


def test_glyph_at_on_another_kind_is_refused_by_name():
    errs = errors(unknown(glyph_at=6.0))
    assert any("glyph_at" in e and "chip's" in e for e in errs), errs


# ---------------------------------------------------------------- the unknown species' grammar
def test_the_kind_is_registered_with_its_when_and_its_targets():
    assert B.SPECIES_UNKNOWN == "unknown" and B.SPECIES_UNKNOWN in B.SPECIES_KINDS
    assert B.SPECIES_TARGETS[B.SPECIES_UNKNOWN] == ("point", "region")
    when = B.SPECIES_WHEN[B.SPECIES_UNKNOWN]
    assert "open question" in when and "figure" in when
    import lint_species_choice as L
    assert "unknown" in L.ACT_SPECIES["TURNS"]
    assert B.SPECIES_UNKNOWN not in B.PAGE_SPECIES, "a stage species: it stands in the world's room, not on a chart's data"


@pytest.mark.parametrize("extra", [
    {},
    {"target": {"kind": "region", "x0": 0.02, "y0": 0.2, "x1": 0.28, "y1": 0.7}},
    {"size": 200},
    {"size": 59.08},
    {"ink": "chalk"},
    {"ink": "neg"},
    {"pulse": True},
    {"under": "blur"},
    {"pulse": True, "under": "blur", "size": 285, "ink": "neg"},
])
def test_the_unknown_validates_and_the_entry_is_not_mutated(extra):
    entry = unknown(**extra)
    before = copy.deepcopy(entry)
    assert errors(entry) == [], (extra, errors(entry))
    assert entry == before


@pytest.mark.parametrize("name, extra, needle", [
    ("a datum", {"target": {"kind": "datum", "index": 3}}, "unknown: a datum is a figure the chart states"),
    ("a span", {"target": {"kind": "span", "from": 0, "to": 2}}, "unknown: target kind 'span' not allowed"),
    ("no target", {"target": None}, "unknown: target must be"),
    ("a size under the floor", {"size": 40}, "unknown: size must be"),
    ("a size past the ceiling", {"size": 900}, "unknown: size must be"),
    ("a size that is a word", {"size": "big"}, "unknown: size must be"),
    ("an ink it does not know", {"ink": "gold"}, "unknown: ink must be one of neg | chalk"),
    ("a pulse that is not true", {"pulse": 3}, "unknown: pulse must be true"),
    ("a pulse with no room", {"pulse": True, "dur": 1.0}, "unknown: pulse needs"),
    ("under hover", {"under": "hover"}, "unknown: under must be \"blur\""),
    ("a key it does not take", {"label": "the ROI"}, "unknown: 'label' - an unknown takes only"),
    ("a second glyph", {"glyph": "!"}, "unknown: 'glyph' - an unknown takes only"),
])
def test_a_malformed_or_misplaced_unknown_is_refused_by_name(name, extra, needle):
    entry = unknown(**extra)
    if extra.get("target", 1) is None:
        entry.pop("target")
        needle = "unknown: no declared target"
    errs = errors(entry)
    assert any(needle in e for e in errs), (name, errs)


def test_under_on_another_species_is_refused_by_name():
    errs = errors(chip(under="blur"))
    assert any("'under'" in e and "unknown" in e for e in errs), errs


# ---------------------------------------------------------------- the gate
def scene(*species) -> list[dict]:
    return [{"scene_id": "s-q", "span": [0.0, 40.0], "species": list(species)}]


def test_the_gate_a_held_question_is_one_landing_and_nothing_after():
    assert G._species_events(scene(unknown())) == [5.0], "a held '?' is an annotation after its landing (s91)"
    assert G._species_events(scene(unknown(under="blur"))) == [5.0], "the veil is the same landing's, not a second event"


def test_the_gate_a_pulse_is_one_event_per_blink_onset():
    m = module("QMARK")
    c = module("CHIP")
    ons = [round(5.0 + m["SETTLE_S"] + k * c["PULSE_S"], 2) for k in range(c["PULSE_N"])]
    assert G._species_events(scene(unknown(pulse=True))) == [5.0] + ons
    assert G._species_events(scene(unknown(pulse=True, dur=0.8))) == [5.0, round(5.0 + m["SETTLE_S"], 2)], "no blink after it left (5.9 >= 5.8)"


def test_the_gate_the_chips_question_lands_on_its_word():
    assert G._species_events(scene(chip(glyph="?", glyph_at=8.0))) == [5.0, 8.0]
    assert G._species_events(scene(chip(glyph="?"))) == [5.0], "a '?' with no glyph_at lands with the chip: one landing"


# ---------------------------------------------------------------- the dials, against the module and the reference
def test_the_compiler_and_the_gate_mirror_the_modules_dials():
    m, c = module("QMARK"), module("CHIP")
    assert (B.UNKNOWN_SIZE_DEFAULT, B.UNKNOWN_SIZE_MIN, B.UNKNOWN_SIZE_MAX) == (m["SIZE"], m["SIZE_MIN"], m["SIZE_MAX"])
    assert B.UNKNOWN_SETTLE_S == m["SETTLE_S"] and B.UNKNOWN_INKS == tuple(m["INKS"])
    assert G.UNKNOWN_PULSE == {"settle_s": m["SETTLE_S"], "n": c["PULSE_N"], "s": c["PULSE_S"]}
    assert m["SIZE_MIN"] == round(LPG.CARD_TYPE_PX, 2), "the smallest '?' is a label at the s90 floor"


def test_the_pop_is_booms_the_same_pop_t17_measured_off_the_failed_link_disc():
    q, f = module("QMARK"), module("FLOW", FLOW_MJS)
    assert (q["POP_FROM"], q["MP"], q["POP_S"]) == (f["FAIL_POP_FROM"], f["FAIL_MP"], f["FAIL_POP_S"])
    assert q["INKS"]["neg"] == f["FAIL_INK"], "the crimson T17 matched to Bravos's is the template's --lp-neg"
    assert q["SIZE"] == 122, "BOOM 08:52.5: the settled '?' is 122 px of 1080 (scratchpad p71-t18 measure_q.py)"


def _css_var(name: str) -> str:
    m = re.search(r"--" + re.escape(name) + r":\s*(#[0-9A-Fa-f]{6})", TEMPLATE.read_text(encoding="utf-8"))
    assert m, name
    return m.group(1).upper()


def test_the_inks_are_the_templates():
    q = module("QMARK")
    assert q["INKS"] == {"neg": _css_var("lp-neg"), "chalk": _css_var("lp-chalk")}


def test_the_chips_question_sits_above_the_card_as_his_does():
    """HIS 01:48: the '?' 0.38 of the card tall, its ink 0.146 of the card above the top edge, centred, in the glyph's white."""
    pose = node_json(f"import {{ chipQmarkPose, CHIP }} from '{CHIP_MJS}';"
                     "const sp = {at: 5, dur: 8, glyph: '?', glyph_at: 7};"
                     "console.log(JSON.stringify([chipQmarkPose(sp, 6.9, CHIP.SIZE), chipQmarkPose(sp, 9, CHIP.SIZE),"
                     " chipQmarkPose({at: 5, dur: 8}, 9, CHIP.SIZE), chipQmarkPose({at: 5, dur: 8, glyph: '?'}, 5.0, CHIP.SIZE)]));")
    before, held, none, landing = pose
    assert before["fade"] == 0 and none is None
    assert abs(held["h"] - 0.38 * 168) < 0.05 and abs(held["gap"] - 0.146 * 168) < 0.05
    assert held["scale"] == pytest.approx(1.0, abs=2e-3) and held["fade"] == 1
    assert landing["at"] == 5 and landing["fade"] == 0, "no glyph_at: it lands with the chip"


def test_the_unknowns_pose_pops_holds_pulses_and_leaves():
    js = (f"import {{ unknownPose, QMARK, CHIP }} from '{CHIP_MJS}';"
          "const sp = {at: 5, dur: 4, target: {kind: 'point', x: .1, y: .4}};"
          "const pu = Object.assign({pulse: true}, sp);"
          "const mid = 5 + QMARK.SETTLE_S + CHIP.PULSE_S / 2;"
          "console.log(JSON.stringify({pre: unknownPose(sp, 4.99), peak: unknownPose(sp, 5 + 0.201 * QMARK.POP_S),"
          " held: unknownPose(sp, 7), heldMid: unknownPose(sp, mid), pulsed: unknownPose(pu, mid),"
          " leaving: unknownPose(sp, 8.95), big: unknownPose(Object.assign({size: 285, ink: 'chalk'}, sp), 7)}));")
    p = node_json(js)
    assert p["pre"]["fade"] == 0
    assert p["peak"]["scale"] == pytest.approx(1.21, abs=0.01), "BOOM's first overshoot: 1.2 x the settled size"
    assert p["held"]["scale"] == pytest.approx(1.0, abs=2e-3) and p["held"]["fade"] == 1 and p["held"]["h"] == 122
    assert p["heldMid"]["scale"] == pytest.approx(1.0, abs=0.01), "held: no blink (the pop's last ring is under 1 %)"
    assert p["pulsed"]["scale"] > p["heldMid"]["scale"] + 0.1, "a pulse swells the '?' at the blink's middle"
    assert 0 < p["leaving"]["fade"] < 1, "it leaves on its own curve inside dur"
    assert p["big"]["h"] == 285 and p["big"]["ink"] == "#F2F2F2"


# ---------------------------------------------------------------- the engine carries it
def test_the_engine_carries_the_painter_and_the_veil():
    src = ENGINE.read_text(encoding="utf-8")
    assert "SPECIES_PAINTERS.unknown = paintUnknown" in src
    assert "const paintUnknownVeil" in src and "paintUnknownVeil(sc, t);" in src
    assert src.count("DOCK_VEIL.BLUR") >= 2, "the veil is T15's blur law, not a second dial"


# ---------------------------------------------------------------- the card, the recipe and the golden
def _card(cid: str) -> dict:
    return next(c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"] if c["id"] == cid)


def test_the_cards_name_the_question():
    ch = _card("species:chip")
    assert {"glyph", "glyph_at"} <= {o["token"] for o in ch["options"]} and "P71 T18" in ch["doctrine"]
    un = _card("species:unknown")
    assert un["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/chip.mjs", "symbol": "paintUnknown"}
    assert un["serves"] == ["TURNS"] and un["proof"]["golden"] == GOLDEN
    assert {"pulse", "under", "size", "ink"} <= {o["token"] for o in un["options"]}
    assert any("08:52.5" in b["source"] for b in un["blends"]) and any("CHN" in b["source"] for b in un["blends"])


def test_the_predictions_board_is_a_candidate_recipe_of_sourced_chips_struck_in_turn():
    r = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert r["id"] == "recipe:the-predictions-board" and r["status"] == "candidate" and r["acts"] == ["RETRACTS"]
    cards = [m["card"] for m in r["members"]]
    assert "species:chip" in cards and any(c in ("dock_kind:press", "dock_payload:record") for c in cards), \
        "each prediction names its press card or record (sourced)"
    assert "unsourced" in r["use_when"]["dont"] and "P71 T18" in r["doctrine"]


def test_the_golden_is_row_23s_beat_judged_after_the_settle():
    import build_golden_sources as S
    tl, uris = S.SURFACES[GOLDEN]()
    qs = [sp for s in tl["scenes"] for sp in s["species"] if sp["kind"] == "unknown"]
    assert len(qs) == 1
    sp, t = qs[0], S.FRAME_T[GOLDEN]
    assert sp["at"] + B.UNKNOWN_SETTLE_S <= t < sp["at"] + sp["dur"], "judged on the settled '?', still standing"
    assert errors(sp) == []
    for suffix, payload in (("timeline", tl), ("uris", uris)):
        assert b"\r" not in committed_source_bytes(f"{GOLDEN}.{suffix}.json", payload)


def committed_source_bytes(name: str, payload: dict) -> bytes:
    rel = f"content/video_engine/tests/golden/sources/{name}"
    try:
        r = subprocess.run(["git", "show", f":{rel}"], cwd=ROOT, capture_output=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        r = None
    if r is not None and r.returncode == 0:
        return r.stdout
    return (json.dumps(payload, indent=1, sort_keys=True) + "\n").encode("utf-8")


# ---------------------------------------------------------------- in the player
def _chromium_available() -> bool:
    try:
        import served_player as SP
        with SP.browser() as _b:
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const q = document.querySelector('#species .unknown'), v = document.getElementById('unkveil');
  return { q: !!q, op: q ? +q.getAttribute('opacity') : 0, veil: !!v, blur: v ? (v.style.backdropFilter || '') : null };
}"""


def _serve(tl: dict, uris: dict):
    import render_baseline as RB
    import served_player as SP
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        out = page.evaluate(PROBE)
        out["ink"] = _ink_centre(page.locator("#stage").screenshot())
        return out

    return at, errs, close


def _ink_centre(png: bytes):
    """The "?"'s INK as rendered - the pixels in its crimson (--lp-neg #FF4D4D), their box's centre in stage px."""
    import io
    import numpy as np
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB")
    a = np.asarray(im).astype(int)
    m = (a[..., 0] > 230) & (a[..., 1] < 110) & (a[..., 2] < 110)
    ys, xs = np.nonzero(m)
    if not len(ys):
        return None
    k = 1920 / im.width
    return ((xs.min() + xs.max() + 1) / 2 * k, (ys.min() + ys.max() + 1) / 2 * k, (ys.max() + 1 - ys.min()) * k)


@needs_browser
def test_the_question_lands_on_its_point_and_the_veil_only_when_asked():
    import build_golden_sources as S
    tl, uris = S.SURFACES[GOLDEN]()
    sp = next(x for s in tl["scenes"] for x in s["species"] if x["kind"] == "unknown")
    at, errs, close = _serve(tl, uris)
    try:
        before, held, gone = at(sp["at"] - 0.2), at(sp["at"] + 1.2), at(sp["at"] + sp["dur"] + 0.3)
    finally:
        close()
    assert not errs, errs
    assert not before["q"] and not gone["q"]
    assert held["q"] and held["op"] == 1
    ix, iy, ih = held["ink"]
    assert abs(ix - sp["target"]["x"] * 1920) < 3 and abs(iy - sp["target"]["y"] * 1080) < 3, held   # the INK is centred on its point
    assert abs(ih - sp.get("size", B.UNKNOWN_SIZE_DEFAULT)) < 4, held   # ... and is the ink height it asked for (a glow fringe aside)
    assert not held["veil"], "no row asked for the blur: the player's DOM is the base's"
    tl2 = copy.deepcopy(tl)
    for s in tl2["scenes"]:
        for x in s["species"]:
            if x["kind"] == "unknown":
                x["under"] = "blur"
    at, errs, close = _serve(tl2, uris)
    try:
        before, mid, gone = at(sp["at"] - 0.2), at(sp["at"] + 1.2), at(sp["at"] + sp["dur"] + 0.3)
    finally:
        close()
    assert not errs, errs
    assert mid["veil"] and mid["blur"].startswith("blur(") and before["blur"] in ("", "none") and gone["blur"] in ("", "none"), (before, mid, gone)

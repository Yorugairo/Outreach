"""R26-220 + R26-201 - THE FOCUS ZOOM'S OWN DIAL, AND THE CAPTION THAT YIELDS UNDER A CAMERA MOVE.

Two rows, one door (E99 s80: *"a punch may crop the page - its crop line falls between elements and the
caption yields under it"*).

  R26-220. `focus_zoom` was a FIXED 1.32 (`kinetics/camera.mjs` CAM.FOCUS_SCALE). At 16:9 that zoom cut
  the Steel and Paper H page's title and pushed its y tick column off the frame, so the unit authored a
  1.06 camera KEY pair instead of the move it wanted. The dial is now the author's - `zoom` on the species
  entry, default 1.32 so every frame already rendered is the frame it was - and the compiler refuses one
  the page cannot take, BY NAME and with the reachable number (`page_zoom_ceiling`).

  R26-201. E62's demotion ("the demotion is in POSITION, not in size") was written on DOCK entries only,
  so a page punch had no way to move the caption: Tokyo's cite read 34 px inside the strip at zoom 1.08
  and both punches were dropped. The compiler now writes `caption_yield` per camera window, with E62's
  own band cut against the page WHERE THE FRAME PUTS IT, and the engine reads it exactly as a card's.

WHAT IS MEASURED HERE, and where the numbers come from. The 16:9 subject is the committed golden surface
`ledger-page-mid-build` - the same dense-line page the H unit's s01 draws, so its ceiling IS the H unit's:
the title's top edge binds at 1.089, the y tick column's left edge at 1.102. The 9:16 subject is the page
R26-201 was measured on (Tokyo v3b's s04, the pill-rail page whose row pushed the rail into the strip) -
its INK is quoted here so `assets/page-boxes.v1.json` answers for it exactly as it answers in the cut, and
no test reads a project directory.

BYTE-IDENTITY. Both halves are the COMPILER's: the dial is absent from every timeline on disk (the engine
falls back to CAM.FOCUS_SCALE) and `caption_yield` cannot appear in a timeline compiled before this row.
Every committed golden renders the bytes it rendered; `test_golden_frames` is the proof, not this file.
"""
from __future__ import annotations

import json
import math
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as MG  # noqa: E402
import ledger_page as LPG  # noqa: E402
import measure_page_boxes as MPB  # noqa: E402
import render_baseline as RB  # noqa: E402

SURFACE_16X9 = "ledger-page-mid-build"     # the dense-line golden: the H unit's own page
W9, H9 = LPG.STAGE_PX["16:9"]
W16, H16 = LPG.STAGE_PX["9:16"]
CAMERA_MJS = ROOT / "content/video_engine/scripts/kinetics/camera.mjs"

# THE PAGE R26-201 WAS MEASURED ON - Tokyo v3b s04, "what a Meta share is worth", whose three-badge rail
# is its foot and whose row's punch pushed that rail into the caption strip. Its INK (builder, title, sub,
# source, quiet zone, rail count, ylabel) is the fixture's key `392279b34c508b63`, so `page_boxes` answers
# with the PLAYER's own numbers here exactly as it does in the cut: chart y 450 h 602, plot y 647 h 335 -
# a small chart under a tall heading, which is the shape that leaves the caption a band to move to.
TOKYO_S04 = {
    "schema_version": "ledger_page.v1", "surface": "page", "builder": "story", "variant": "bars",
    "title": "What a Meta share is worth as the 10-year moves",
    "sub": ("The same trailing profit per share ($26.83), priced at each 10-year yield; today's 4.77% gives "
            "the 23.0x multiple and the $617 price. Arithmetic on the discount identity - no growth assumed, "
            "no forecast"),
    "source": "Yahoo Finance · FRED DGS10 · 2026-09",
    "quiet_zone": "right", "src_style": "compact", "unit": "$",
    "values": [665.0, 633.0, 604.0, 577.0], "value_strings": ["665", "633", "604", "577"],
    "labels": ["4%", "4.5%", "5%", "5.5%"], "colors": ["cobalt", "cobalt", "crimson", "crimson"],
    "judge": [], "emphasize": 3,
    "badges": [{"label": "META NOW", "value": "$617", "tag": "23.0x at a 4.77% 10-year", "accent": "cobalt", "inline": False},
               {"label": "AT 5.5%", "value": "-$40", "tag": "a share, -6.5%, same profit", "accent": "crimson", "inline": False},
               {"label": "ON $10,000", "value": "-$647", "tag": "of Meta, at 5.5%", "accent": "crimson", "inline": False}],
}


def _golden_page(**kw) -> dict:
    """The 16:9 golden surface's own page spec, stamped full stage (R26-205) unless told otherwise."""
    tl, _uris, _t, _asp = RB.load_surface(SURFACE_16X9)
    page = json.loads(json.dumps(tl["scenes"][0]["world"]["page"]))
    page.update(full_stage=True, caption="anchor")
    page.update(kw)
    return page


def _world(page: dict) -> dict:
    return {"kind": "ledger", "page": page}


def _look(page: dict, aspect: str) -> tuple[float, float]:
    """The datum's own proxy - the plot's centre, which is what `MG._cam_point` resolves a datum to."""
    plot = LPG.page_boxes(page, aspect)["plot"]
    return (plot["x"] + plot["w"] / 2, plot["y"] + plot["h"] / 2)


def _fz(zoom=None, at=8.0, dur=3.0, target=None) -> dict:
    sp = {"kind": "focus_zoom", "at": at, "dur": dur,
          "target": target or {"kind": "datum", "index": 3, "series": 0}}
    if zoom is not None:
        sp["zoom"] = zoom
    return sp


def _keys(zoom: float, look: dict | list, at=None, t0=8.0) -> dict:
    key = lambda t, z, **kw: {"t": t, "zoom": z, "look": look, **({"at": at} if at else {}), **kw}
    return {"keys": [key(t0, 1.0), key(t0 + 0.4, zoom), key(t0 + 3.0, zoom, ease="hold"), key(t0 + 3.4, 1.0)]}


def _meets(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["w"] and a["x"] + a["w"] > b["x"]
            and a["y"] < b["y"] + b["h"] and a["y"] + a["h"] > b["y"])


# ---- THE DIAL --------------------------------------------------------------------------------------

def test_the_dial_is_a_number_over_one_and_the_focus_zooms_alone():
    ok = B.validate_species([_fz(1.08)], (0, 0, 0), "ledger:x:line")
    assert ok == [], ok
    for bad, says in ((1.0, "does not zoom"), (0.9, "does not zoom"), ("1.1", "must be a number"),
                      (True, "must be a number")):
        errs = B.validate_species([_fz(bad)], (0, 0, 0), "ledger:x:line")
        assert len(errs) == 1 and says in errs[0], (bad, errs)
        assert "1.32" in errs[0], ("the refusal names the default it replaces", errs)


def test_the_dial_is_refused_on_a_species_whose_scale_is_the_engines():
    for kind in ("punch", "pull_back"):
        sp = dict(_fz(1.08), kind=kind)
        errs = B.validate_species([sp], (0, 0, 0), "ledger:x:line")
        assert len(errs) == 1 and "is the focus zoom's dial" in errs[0], errs


def test_a_focus_zoom_with_no_dial_is_exactly_what_it_always_was():
    """The byte-identity of every golden that carries one (`camera-layers`, `page-depth`, `melt-depth`,
    `dock-depth`, `slide-depth`, `plate-alive`): no field, no change."""
    sp = _fz()
    assert "zoom" not in sp
    assert B.validate_species([sp], (0, 0, 0), "ledger:x:line") == []
    assert B.camera_zoom_errors(_world(_golden_page()), [sp], None, "ledger:x:line", "16:9") == []


def test_the_compilers_mirror_of_the_engines_three_dials_is_the_modules_own():
    """`CAMERA_SPECIES_ZOOM` and `FOCUS_ZOOM_DEFAULT` are read off `kinetics/camera.mjs` CAM - one law in
    two languages, pinned against the module itself rather than typed twice."""
    src = CAMERA_MJS.read_text(encoding="utf-8")
    num = lambda name: float(re.search(name + r":\s*([0-9.]+)", src).group(1))
    assert B.FOCUS_ZOOM_DEFAULT == num("FOCUS_SCALE") == 1.32
    assert B.CAMERA_SPECIES_ZOOM == {"punch": num("PUNCH_SCALE"), "focus_zoom": num("FOCUS_SCALE"),
                                     "pull_back": num("PULL_FROM")}


# ---- THE CEILING: the camera's own similarity, as arithmetic ----------------------------------------

def test_the_ceiling_is_the_cameras_own_similarity():
    """`screen = at + s * (p - look)`: a box 100 px from the look point with 400 px of stage beyond it
    reaches the edge at 5.0, and the nearest edge is the one that binds."""
    box = {"x": 400, "y": 300, "w": 200, "h": 100}
    look = (500, 350)
    assert B.zoom_ceiling(box, look, look, 1000, 700) == (5.0, "left")     # 500/(500-400)
    # the same box seen from 450: the left edge would reach 9.0, but the RIGHT edge binds first at 3.67
    assert B.zoom_ceiling(box, (450, 350), (450, 350), 1000, 700) == (pytest.approx(550 / 150), "right")
    # an `at` that LANDS the look 100 px higher lifts the whole frame with it: a box below the look gains
    # that much room at the bottom (7.0 -> 9.0) and loses it at the top - which is the anchor E99 s80 (3)
    # names as the way out when a page's foot will not clear the strip
    below = {"x": 480, "y": 360, "w": 40, "h": 40}
    assert B.zoom_ceiling(below, look, look, 1000, 700) == (pytest.approx(350 / 50), "bottom")
    assert B.zoom_ceiling(below, look, (500, 250), 1000, 700) == (pytest.approx(450 / 50), "bottom")
    assert B.zoom_ceiling({"x": 0, "y": 0, "w": 1000, "h": 700}, look, look, 1000, 700)[0] == 1.0
    assert B.zoom_ceiling({"x": -20, "y": 0, "w": 1020, "h": 700}, look, look, 1000, 700)[0] < 1.0


def test_the_page_glyphs_are_the_ones_the_ruling_names():
    boxes = B.page_glyph_boxes(_golden_page(), "16:9")
    assert set(boxes) >= {"title", "sub", "source", "y tick column", "x tick labels"}
    assert "plot" not in boxes and "chart" not in boxes, "the DATA is the thing a punch moves into"
    plot = LPG.page_boxes(_golden_page(), "16:9")["plot"]
    assert boxes["y tick column"]["x"] < plot["x"] and boxes["x tick labels"]["h"] == LPG.XTICK_H


def test_the_H_units_page_at_16x9_reaches_1_08_and_the_title_is_what_binds_it():
    """The measurement R26-220 asked for, on the page the H unit's s01 draws."""
    page = _golden_page()
    z, element, edge, table = B.page_zoom_ceiling(page, "16:9", _look(page, "16:9"))
    assert (element, edge) == ("title", "top")
    assert z == pytest.approx(1.089, abs=0.001), z
    by = {r["element"]: round(r["zoom"], 3) for r in table}
    assert by["y tick column"] == pytest.approx(1.102, abs=0.001), by
    assert by["sub"] == by["source"] == pytest.approx(1.120, abs=0.001), by
    assert math.floor(z * 100) / 100 == 1.08, "the reachable number is FLOORED - it has to be reachable"


def test_a_glyph_already_off_the_stage_at_rest_is_not_the_moves_fault():
    """The dense-line page's ESTIMATED end tag column runs past the frame (`LAND_TAG_REACH` is an upper
    bound by construction, and the frame measures the widest tag ending at 1896 of 1920). A zoom cannot be
    blamed for it - R26-205's row owns the page's own geometry."""
    page = _golden_page()
    table = {r["element"]: r for r in B.page_zoom_ceiling(page, "16:9", _look(page, "16:9"))[3]}
    assert table["tags"]["at_rest"] is False and table["tags"]["zoom"] < 1.0
    assert B.page_zoom_ceiling(page, "16:9", _look(page, "16:9"))[1] == "title"


# ---- THE REFUSAL -----------------------------------------------------------------------------------

def test_the_engines_own_1_32_is_refused_by_name_with_the_number_at_16x9():
    page = _golden_page()
    errs = B.camera_zoom_errors(_world(page), [_fz(1.32)], None, "ledger:steel:line", "16:9")
    assert len(errs) == 1, errs
    msg = errs[0]
    for bit in ("ledger:steel:line", "focus_zoom zoom 1.32", "reachable zoom 1.08", "title's top edge",
                "1.089", "16:9", "E99 s80 (2)", "never through a glyph"):
        assert bit in msg, (bit, msg)


def test_the_H_units_authored_1_06_holds_and_1_09_does_not():
    page = _golden_page()
    look = {"kind": "datum", "index": 234, "series": 0}
    assert B.camera_zoom_errors(_world(page), [], _keys(1.06, look), "ledger:steel:line", "16:9") == []
    over = B.camera_zoom_errors(_world(page), [], _keys(1.09, look), "ledger:steel:line", "16:9")
    assert len(over) == 2 and "camera key 1" in over[0] and "camera key 2" in over[1], over
    assert "reachable zoom 1.08" in over[0]


def test_a_camera_key_is_measured_by_the_same_law_as_the_species():
    page = _golden_page()
    pt = {"kind": "point", "x": 0.5, "y": 0.5}
    z = B.page_zoom_ceiling(page, "16:9", (W9 / 2, H9 / 2))[0]
    assert B.camera_zoom_errors(_world(page), [], _keys(round(z - 0.01, 3), pt), "p", "16:9") == []
    assert B.camera_zoom_errors(_world(page), [], _keys(round(z + 0.05, 3), pt), "p", "16:9")
    assert B.camera_zoom_errors(_world(page), [_fz(round(z + 0.05, 3), target=pt)], None, "p", "16:9")


def test_a_refusal_under_the_floor_says_the_page_carries_no_move_at_all():
    """E99 s80 (3): "a zoom under ~1.06 is not a move and stays out" - said, never enforced as taste."""
    page = _golden_page()
    corner = {"kind": "point", "x": 0.98, "y": 0.98}   # a look in the frame's far corner: nothing is reachable
    errs = B.camera_zoom_errors(_world(page), [_fz(1.32, target=corner)], None, "p", "16:9")
    assert errs and "carries no move at this anchor" in errs[0], errs
    assert f"~{B.CAMERA_MOVE_FLOOR:.2f}" in errs[0]


def test_nothing_is_claimed_where_the_look_cannot_be_placed():
    page = _golden_page()
    span = {"kind": "span", "from_word": 1, "to_word": 3}
    assert B.camera_zoom_errors(_world(page), [_fz(1.32, target=span)], None, "p", "16:9") == []
    assert B.camera_zoom_errors(_world(page), [], {"keys": [{"t": 1.0, "zoom": 1.32, "look": span}]}, "p", "16:9") == []


def test_a_row_with_no_page_takes_no_ceiling():
    plate = {"asset_id": "plate-desk", "kind": "plate"}
    assert B.camera_zoom_errors(plate, [_fz(1.32)], None, "plate-desk", "16:9") == []
    assert B.camera_zoom_errors(None, [_fz(1.32)], None, "plate-desk", "16:9") == []


def test_the_crop_line_into_the_strip_is_a_16x9_rule_and_names_the_page(monkeypatch):
    """A page whose drawn extent ends ABOVE the anchored strip may not be zoomed until its own bottom edge
    lands inside it - a deckle edge through the caption's band. A full-stage page's ink already runs past
    the strip's foot, so the rule is silent there (which is why the H unit's refusal is the glyph's)."""
    page = _golden_page()
    look = _look(page, "16:9")
    assert B.page_crop_line_ceiling(page, "16:9", look)[0] == math.inf
    assert B.page_crop_line_ceiling(page, "9:16", _look(page, "9:16"))[0] == math.inf, "9:16 yields instead"
    strip = LPG.CAPTION_ANCHOR["16:9"][1]
    short = {k: dict(v) if isinstance(v, dict) else v for k, v in LPG.page_boxes(page, "16:9").items()}
    for k in ("title", "sub", "chart", "plot", "source", "rail", "tags"):
        if isinstance(short.get(k), dict):
            short[k] = dict(short[k], y=min(short[k]["y"], 600), h=min(short[k]["h"], 200))
    monkeypatch.setattr(LPG, "page_boxes", lambda spec, aspect="16:9": short)
    z, name = B.page_crop_line_ceiling(page, "16:9", look)
    bottom = max(short[k]["y"] + short[k]["h"] for k in ("title", "sub", "chart", "plot", "source"))
    assert name == "the page's own bottom edge"
    assert z == pytest.approx((strip - look[1]) / (bottom - look[1])), z


# ---- THE YIELD: E62's own ladder, cut against the page as the frame holds it -------------------------

def _tokyo_scene(zoom=1.08, t0=8.0, span=(0.0, 30.0)) -> dict:
    page = json.loads(json.dumps(TOKYO_S04))
    plot = LPG.page_boxes(page, "9:16")["plot"]
    look = {"kind": "point", "x": (plot["x"] + plot["w"] / 2) / W16, "y": (plot["y"] + plot["h"] / 2) / H16}
    return {"scene_id": "s01", "span": list(span), "world": _world(page), "docks": [],
            "species": [], "camera": _keys(zoom, look, t0=t0)}


def _pages(n=9, step=3.0) -> list[dict]:
    return [{"s": 1.0 + i * step, "e": 3.8 + i * step} for i in range(n)]


def test_the_page_R26_201_was_measured_on_is_the_player_own_numbers():
    """The ink quoted in this file is the fixture's key, or the band below is measured against an estimate
    of a page the player draws somewhere else."""
    boxes = LPG.page_boxes(TOKYO_S04, "9:16")
    assert boxes["measured"] is True, LPG.page_ink_key(TOKYO_S04)
    assert (boxes["plot"]["y"], boxes["plot"]["h"]) == (647, 335), boxes["plot"]
    assert boxes["rail"]["y"] + boxes["rail"]["h"] == 1280, boxes["rail"]


def test_the_caption_yields_to_the_band_the_moved_page_leaves_free():
    sc = _tokyo_scene()
    placed = B.stamp_camera_caption_bands([sc], _pages(), "9:16")
    assert placed == 1
    got = sc[B.CAPTION_YIELD_KEY]
    assert len(got) == 1 and got[0]["from"] == 8.0 and got[0]["to"] == 11.4, got
    band = got[0]["caption_band"]
    assert band["band"] == "above" and band["h"] == B.caption_strip_h(), band
    assert band["y"] == 491, band
    assert "in_strip" not in got[0], got
    # ... and with no camera at all this page's caption has no reason to move: its home is the strip
    assert B.caption_band(TOKYO_S04, "9:16", []) == {"y": 504, "h": 143, "band": "above"}


def test_the_band_is_cut_against_the_page_where_the_frame_puts_it():
    """The whole of R26-201: at rest the band clears the page's ink by 143 px of air; under the move the
    same page's boxes are somewhere else, and a band cut against the page AT REST reads over its sub."""
    sc = _tokyo_scene()
    B.stamp_camera_caption_bands([sc], _pages(), "9:16")
    band = sc[B.CAPTION_YIELD_KEY][0]["caption_band"]
    strip = {"x": 80, "y": band["y"], "w": 800, "h": band["h"]}
    win = B.camera_move_windows(sc, "9:16")[0]
    xf = B.camera_frame_xf(win)
    boxes = LPG.page_boxes(TOKYO_S04, "9:16")
    for key in ("title", "sub", "plot", "source", "rail"):
        moved = xf(boxes[key])
        assert not _meets(strip, moved), (key, strip, moved)
    # and the band is the MOVED plot's own edge, not the resting one: 647 -> 634 under the zoom, and the
    # strip is cut flush above it either way (E45's park edge), so the two answers differ by exactly that
    rest = LPG.page_boxes(TOKYO_S04, "9:16")["plot"]["y"]
    assert band["y"] == xf({"x": 0, "y": rest, "w": 0, "h": 0})["y"] - band["h"]
    assert B.caption_band(TOKYO_S04, "9:16", [])["y"] == rest - band["h"]


def test_where_no_band_holds_the_intrusion_is_named_with_its_number():
    """Tokyo's tall-chart pages have 44 px under the plot and 136 px over it - neither holds a two-line
    strip - so the caption stays at its anchor and the page's own cite is pushed into it. The compiler says
    so with the number and names the two ways out; it does not silently ship the collision."""
    page = _golden_page(full_stage=False)
    page.pop("caption", None)
    plot = LPG.page_boxes(page, "9:16")["plot"]
    look = {"kind": "point", "x": (plot["x"] + plot["w"] / 2) / W16, "y": (plot["y"] + plot["h"] / 2) / H16}
    sc = {"scene_id": "s01", "span": [0.0, 30.0], "world": _world(page), "docks": [], "species": [],
          "camera": _keys(1.08, look)}
    assert B.stamp_camera_caption_bands([sc], _pages(), "9:16") == 0
    win = sc[B.CAPTION_YIELD_KEY][0]
    assert win["caption_band"] is None
    assert win["in_strip"]["element"] == "source" and win["in_strip"]["px"] >= 20, win


def test_the_yield_is_written_only_where_the_caption_holds_the_stage():
    pages = _pages()
    # a 16:9 full-stage page row: its caption is already in the anchored strip (R26-205)
    sc = _tokyo_scene()
    sc["world"]["page"] = _golden_page()
    assert B.stamp_camera_caption_bands([sc], pages, "16:9") == 0 and B.CAPTION_YIELD_KEY not in sc
    # a page that declares the anchor itself (a host plate, C5)
    sc2 = _tokyo_scene()
    sc2["world"]["page"]["caption"] = "anchor"
    assert B.stamp_camera_caption_bands([sc2], pages, "9:16") == 0 and B.CAPTION_YIELD_KEY not in sc2
    # a plate row
    sc3 = _tokyo_scene()
    sc3["world"] = {"asset_id": "plate-desk", "kind": "plate"}
    assert B.stamp_camera_caption_bands([sc3], pages, "9:16") == 0 and B.CAPTION_YIELD_KEY not in sc3
    # a locked camera
    sc4 = _tokyo_scene()
    sc4["camera"] = B.camera_identity()
    assert B.stamp_camera_caption_bands([sc4], pages, "9:16") == 0 and B.CAPTION_YIELD_KEY not in sc4
    # a window with no caption page on screen
    sc5 = _tokyo_scene(t0=20.0)
    assert B.stamp_camera_caption_bands([sc5], [{"s": 1.0, "e": 3.8}], "9:16") == 0
    assert B.CAPTION_YIELD_KEY not in sc5


def test_a_camera_species_window_yields_exactly_as_a_key_window_does():
    sc = _tokyo_scene()
    plot = LPG.page_boxes(TOKYO_S04, "9:16")["plot"]
    pt = {"kind": "point", "x": (plot["x"] + plot["w"] / 2) / W16, "y": (plot["y"] + plot["h"] / 2) / H16}
    sc.pop("camera")
    sc["species"] = [_fz(1.08, at=8.0, dur=3.4, target=pt)]
    assert B.stamp_camera_caption_bands([sc], _pages(), "9:16") == 1
    got = sc[B.CAPTION_YIELD_KEY][0]
    assert (got["from"], got["to"]) == (8.0, 11.4) and got["caption_band"]["y"] == 491, got
    assert "focus_zoom (zoom 1.08)" == got["move"]


def test_a_species_with_no_dial_is_read_at_the_engines_own_zoom():
    sc = _tokyo_scene()
    sc.pop("camera")
    plot = LPG.page_boxes(TOKYO_S04, "9:16")["plot"]
    pt = {"kind": "point", "x": (plot["x"] + plot["w"] / 2) / W16, "y": (plot["y"] + plot["h"] / 2) / H16}
    sc["species"] = [_fz(None, at=8.0, dur=3.4, target=pt)]
    B.stamp_camera_caption_bands([sc], _pages(), "9:16")
    assert sc[B.CAPTION_YIELD_KEY][0]["move"] == f"focus_zoom (zoom {B.FOCUS_ZOOM_DEFAULT})"


def test_the_windows_are_the_moves_own_and_a_held_key_runs_to_the_scenes_end():
    sc = _tokyo_scene()
    sc["camera"] = {"keys": [{"t": 5.0, "zoom": 1.0, "look": [0.5, 0.5]},
                             {"t": 6.0, "zoom": 1.08, "look": [0.5, 0.5]}]}
    win = B.camera_move_windows(sc, "9:16")[0]
    assert (win["from"], win["to"]) == (5.0, 30.0), win     # the last key HOLDS (camKeyState)
    sc["camera"]["keys"].append({"t": 7.0, "zoom": 1.0, "look": [0.5, 0.5]})
    assert B.camera_move_windows(sc, "9:16")[0]["to"] == 7.0


def test_the_frame_transform_rounds_like_the_box_model():
    """A fractional box makes the ladder's flush candidate 0.4 px into the plot and the caption falls to the
    anchor for a pixel nobody can see - measured on this very page while the row was built."""
    win = {"zoom": 1.08, "look": (500.0, 700.0), "at": (500.0, 700.0)}
    got = B.camera_frame_xf(win)({"x": 101, "y": 203, "w": 307, "h": 409})
    assert got == {"x": round(500 + 1.08 * (101 - 500)), "y": round(700 + 1.08 * (203 - 700)),
                   "w": round(307 * 1.08), "h": round(409 * 1.08)}
    assert all(isinstance(v, int) for v in got.values())


def test_the_dock_band_is_untouched_by_the_camera_door():
    """E62's own answer for a card, with no `xf`: the bytes every 9:16 build already compiles."""
    page = _golden_page(full_stage=False)
    page.pop("caption", None)
    card = {"x": 560, "y": 300, "w": 440, "h": 320}
    assert B.caption_band(page, "9:16", [card]) == B.caption_band(page, "9:16", [card], xf=None)
    assert B.caption_band(TOKYO_S04, "9:16", []) == {"y": 504, "h": 143, "band": "above"}
    assert B.caption_band(TOKYO_S04, "9:16", None) is None


# ---- THE FRAMES ------------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

CAP_PROBE = """() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  const c = document.getElementById('caption');
  const r = c.getBoundingClientRect(), cs = getComputedStyle(c);
  return {x: r.x - stg.x, y: r.y - stg.y, w: r.width, h: r.height, cls: c.className,
          fs: parseFloat(cs.fontSize), weight: cs.fontWeight, top: c.style.top,
          stage: c.classList.contains('stage'), quiet: c.classList.contains('quiet')};
}"""


def _frames(timeline: dict, uris: dict, aspect: str, instants: list[float]) -> list[dict]:
    """The served player at each instant: the page's own boxes (the probe the fixture is measured with)
    and the caption's rect, with the camera IN them - a rendered box is where the frame puts it."""
    from playwright.sync_api import sync_playwright
    w, h = LPG.STAGE_PX[aspect]
    td = tempfile.TemporaryDirectory()
    try:
        html = Path(td.name) / "page.html"
        html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        pw = sync_playwright().start()
        br = pw.chromium.launch(headless=True)
        page = br.new_context(viewport={"width": w, "height": h}).new_page()
        errs: list[str] = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
        RB.prepare_page(page, w, h)
        out = []
        for t in instants:
            page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                          "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
            out.append({"t": t, "boxes": page.evaluate(MPB.READ_BOXES), "cap": page.evaluate(CAP_PROBE),
                        "errs": list(errs)})
        br.close(); pw.stop(); srv.shutdown()
        return out
    finally:
        td.cleanup()


FZ_AT, FZ_DUR = 8.0, 3.0
FZ_HELD = FZ_AT + 2.6      # past k = 1/1.8 of the window: the focus zoom is fully in and dead still


# The camera KEY path is behind the kinetics flag (`kin("camera")`, on for every compiled timeline); the
# golden surfaces carry no `kinetics` block, so a key on one of them would be read by the LEGACY `camXf`,
# which knows only the three species. Both paths are rendered here - the dial has to reach the frame on
# each - and `camSpeciesState`'s own 5th argument is the door the flag-on path takes.
KINETICS_ON = {"camera": True}   # this flag ONLY: `idle` or `min_jerk` would move the page's own ink beside the camera


def _sixteen_nine(zoom: float, kinetics: bool = False) -> tuple[dict, dict]:
    tl, uris, _t, _asp = RB.load_surface(SURFACE_16X9)
    tl = json.loads(json.dumps(tl))
    page = tl["scenes"][0]["world"]["page"]
    page.update(full_stage=True, caption="anchor")
    look = _look(page, "16:9")
    tl["scenes"][0]["species"] = [dict(_fz(zoom, at=FZ_AT, dur=FZ_DUR,
                                           target={"kind": "point", "x": look[0] / W9, "y": look[1] / H9}))]
    if kinetics:
        tl["kinetics"] = dict(KINETICS_ON)
    return tl, uris


@pytest.fixture(scope="module")
def frames_16x9():
    page = _golden_page()
    reach = math.floor(B.page_zoom_ceiling(page, "16:9", _look(page, "16:9"))[0] * 100) / 100
    tl_ok, uris = _sixteen_nine(reach)
    tl_bad, _ = _sixteen_nine(B.FOCUS_ZOOM_DEFAULT)
    tl_kin, _ = _sixteen_nine(reach, kinetics=True)
    return {"reach": reach,
            "ok": _frames(tl_ok, uris, "16:9", [FZ_AT - 0.5, FZ_HELD])[-1],
            "bad": _frames(tl_bad, uris, "16:9", [FZ_HELD])[-1],
            "kin": _frames(tl_kin, uris, "16:9", [FZ_HELD])[-1],
            "still": _frames(tl_ok, uris, "16:9", [FZ_AT - 0.5])[0]}


@needs_browser
def test_ON_THE_FRAME_the_reachable_zoom_keeps_the_title_and_the_y_labels_on_stage(frames_16x9):
    """R26-220's own claim, measured: at the reachable zoom the page's type is whole; at the engine's fixed
    1.32 the title leaves the top of the frame and the y tick column leaves its left."""
    assert frames_16x9["reach"] == 1.08, frames_16x9["reach"]
    ok, bad, rest = frames_16x9["ok"], frames_16x9["bad"], frames_16x9["still"]["boxes"]
    assert not ok["errs"] and not bad["errs"], (ok["errs"], bad["errs"])
    # THE ESTIMATE'S OWN y ERROR (R26-27: "the x maths is exact, only y is off"). A 16:9 FULL-STAGE page is
    # never served the measured fixture (`measured_entry` refuses it - R26-205's own open item), so its
    # ceiling is `ledger_page`'s estimate of where the ink lands, and the frame is allowed to be that far
    # out. Measured here rather than assumed, so the number is in the record and shrinks when the fixture
    # is measured: `measure_page_boxes.py --write`, which is outside this lane's write set.
    est = LPG.page_boxes(_golden_page(), "16:9")
    err = {k: est[k]["y"] - rest[k]["y"] for k in ("title", "sub", "source")}
    assert max(err.values()) < 8, ("the estimate is further out than this row can carry", err)
    slack = max(1.0, max(err.values()) * frames_16x9["reach"])
    for key in ("title", "sub", "source"):
        box = ok["boxes"][key]
        assert box["x"] >= 0 and box["y"] >= -slack, (key, box, err)
        assert box["x"] + box["w"] <= W9 + 1 and box["y"] + box["h"] <= H9 + 1, (key, box)
    ycol = ok["boxes"]["axis"]["y"]
    assert ycol and ycol["x"] >= 0, ycol
    # ... and the defect is two orders of magnitude past that slack, at both of the places R26-220 names
    assert bad["boxes"]["title"]["y"] < -100, ("1.32 cut the title", bad["boxes"]["title"])
    assert bad["boxes"]["axis"]["y"]["x"] < -100, ("1.32 pushed the y labels off", bad["boxes"]["axis"]["y"])


@needs_browser
def test_ON_THE_FRAME_the_dial_is_the_zoom_the_player_draws(frames_16x9):
    """The dial has to reach the frame: the page's own plot is `zoom` times the size it is at rest."""
    still, ok = frames_16x9["still"]["boxes"]["plot"], frames_16x9["ok"]["boxes"]["plot"]
    assert ok["w"] / still["w"] == pytest.approx(frames_16x9["reach"], abs=0.005), (still, ok)
    assert frames_16x9["bad"]["boxes"]["plot"]["w"] / still["w"] == pytest.approx(1.32, abs=0.005)
    # ... on BOTH of the engine's camera paths: the legacy `camXf` above (the goldens' own, no kinetics
    # block) and `kinetics/camera.mjs` `camSpeciesState` under the flag, which take the dial by its own
    # 5th argument. A frame that differs between them would be a second law.
    kin = frames_16x9["kin"]["boxes"]["plot"]
    assert not frames_16x9["kin"]["errs"], frames_16x9["kin"]["errs"]
    assert kin["w"] == pytest.approx(ok["w"], abs=0.5) and kin["x"] == pytest.approx(ok["x"], abs=0.5), (ok, kin)


@needs_browser
def test_ON_THE_FRAME_the_16x9_caption_stays_in_its_strip_under_the_move(frames_16x9):
    """The caption is the viewer's layer and never rides the camera (E59): at 16:9 it is anchored, so the
    move does not touch it - which is why the rule at this aspect is the page's crop line, not a yield."""
    x, y, w, h = LPG.CAPTION_ANCHOR["16:9"]
    for key in ("still", "ok"):
        cap = frames_16x9[key]["cap"]
        assert cap["quiet"] and not cap["stage"], cap
        assert cap["x"] >= x - 1 and cap["y"] >= y - 1 and cap["y"] + cap["h"] <= y + h + 1, (key, cap)
    assert frames_16x9["still"]["cap"]["y"] == frames_16x9["ok"]["cap"]["y"]
    assert frames_16x9["still"]["cap"]["fs"] == frames_16x9["ok"]["cap"]["fs"]


@pytest.fixture(scope="module")
def frames_9x16():
    """The page R26-201 was measured on, at 9:16, under a 1.08 key pair - read before, during and after."""
    tl, uris, _t, _asp = RB.load_surface(SURFACE_16X9)
    tl = json.loads(json.dumps(tl))
    tl["aspect"] = "9:16"
    tl["kinetics"] = dict(KINETICS_ON)      # a camera KEY is read by `camNow` only behind the flag every compiled cut carries
    sc = _tokyo_scene(span=(0.0, float(tl["runtime_s"])))
    sc["world"]["ken_burns"] = {"scale": 0, "x": 0, "y": 0}
    tl["scenes"] = [dict(tl["scenes"][0], world=sc["world"], species=[], docks=[], camera=sc["camera"])]
    pages = [{"s": p["s"], "e": p.get("e", p["s"])} for p in tl["caption_pages"]]
    placed = B.stamp_camera_caption_bands(tl["scenes"], pages, "9:16")
    band = tl["scenes"][0][B.CAPTION_YIELD_KEY][0]["caption_band"]
    reads = _frames(tl, uris, "9:16", [FZ_AT - 0.5, FZ_AT + 2.6, FZ_AT + 4.0])
    return {"placed": placed, "band": band, "before": reads[0], "during": reads[1], "after": reads[2]}


@needs_browser
def test_ON_THE_FRAME_the_caption_moves_under_a_camera_key_as_it_moves_under_a_card(frames_9x16):
    """R26-201, on the frame: the caption's box before / during / after the move. The demotion is in
    POSITION, not in size (E62) - the type and the weight do not change, and it goes home afterwards."""
    f = frames_9x16
    assert f["placed"] == 1 and f["band"]["y"] == 491, f["band"]
    before, during, after = f["before"]["cap"], f["during"]["cap"], f["after"]["cap"]
    assert not any(r["errs"] for r in (f["before"], f["during"], f["after"])), [r["errs"] for r in (f["before"], f["during"], f["after"])]
    assert before["y"] > 1200, ("the stage caption's own home on a portrait page", before)
    assert abs(during["y"] - f["band"]["y"]) <= 2, (during, f["band"])
    assert during["fs"] == before["fs"] and during["weight"] == before["weight"], (before, during)
    assert during["stage"] and not during["quiet"], during
    assert abs(after["y"] - before["y"]) <= 1 and after["fs"] == before["fs"], (before, after)
    assert before["y"] - during["y"] > 700, "a yield the viewer can see"


@needs_browser
def test_ON_THE_FRAME_the_moved_page_and_the_yielded_caption_do_not_meet(frames_9x16):
    """What the yield is FOR: at the deepest zoom no page element reads in the caption's strip."""
    during = frames_9x16["during"]
    cap = during["cap"]
    strip = {"x": cap["x"], "y": cap["y"], "w": cap["w"], "h": cap["h"]}
    for key in ("title", "sub", "plot", "source", "rail"):
        box = during["boxes"].get(key)
        if not box or box["h"] <= 0:
            continue
        assert not _meets(strip, box), (key, box, strip)

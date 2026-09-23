"""P69 T26b - A CAMERA PUSH ON A FULL-STAGE PAGE KEEPS THE TITLE AND THE AXES IN FRAME.

Found on T23 / T6d's Fed frame (`scratchpad/p69t6d/frames/t6d-fed-on-v4-held.png`): with the Fed stamped on the
two-eras page, the camera's pull on the landing (`attention: landings`, P69 T4 - ATTN.SCALE 1.06 about the card's
centre) took the title's left edge, the y tick column and the source line off the frame. R26-220 already bounds the
row's KEYS and its `focus_zoom` by the page's glyph boxes (`camera_zoom_errors`); the LANDING pull was never
measured, and neither was an end tag the page draws past its estimated column.

THE LAW, E99 s80 (2): a move may crop the page - its crop line falls between elements, never through a glyph. On a
FULL-STAGE ledger page (the long form's page, R26-205) the compiler now measures:

  (1) THE LANDING PULL  every arriving dock a `landings` camera pulls toward, at the player's own 1.06 about the card's
                        centre, against the page's glyph boxes (`page_glyph_boxes` - the MEASURED title, sub, source,
                        y tick column, x tick labels, rail, key - read from `assets/page-boxes.v1.json` when the page's
                        ink is on file) and its MEASURED end tags (`tag_boxes`, served only when the fingerprint
                        matches), each taken at the held page's IDLE excursion (`page_idle_boxes`: the breath about the
                        centre, the drift - the clamped Fed frame at 1.04 put the title's T flush on x 0 at the breath's
                        peak). Past the reach it is REFUSED BY NAME - unless the row writes `reach: "clamp"` on its
                        camera, and then the pull is clamped to the reach (`landing_zoom`), which the player
                        (camNow's landings branch) and the gate's mirror (`camera_state_at`) both read.
  (2) THE KEYS          a key past the reach set by a MEASURED END TAG alone is REPORTED (a named WARN line, never a
                        refusal): lane A's committed row 1 - zoom 1.06 looking at the divergence page's datum proxy
                        (624, 541) - is reachable only to 1.034 once the drawn "+613%" tag binds it at rest, 1.025 at
                        the page's breath, and lane A re-aims it in T33. A key past a GLYPH's reach is refused exactly as R26-220 refused it; with
                        `reach: "clamp"` it is clamped to the reach instead.
  (3) BYTE-IDENTITY     a camera that clears is returned untouched - no `landing_zoom`, no key rewritten - so every
                        frame it drew it still draws; the player and the gate read `landing_zoom` only where it is.

The 16:9 subject is the committed golden `ledger-page-mid-build` page stamped full-stage - the divergence page the H
unit's row 1 draws, whose ink the fixture measures WITH its four end tags - so no test reads a project directory.
"""
from __future__ import annotations

import copy
import inspect
import json
import math
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import gate_motion_density as MG  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

ASPECT = "16:9"
W, H = LPG.STAGE_PX[ASPECT]
SURFACE = "ledger-page-mid-build"
PLATE = "ledger:ev-divergence-v1:line"
FED_PLACE = {"x": 1363, "y": 577, "w": 250, "h": 230}     # T6d's Fed on the two-eras page (the engine's fit, P69 T5)
CLEAR_PLACE = {"x": 600, "y": 440, "w": 200, "h": 200}    # on the halving page, a card whose pull reaches 1.089 (the title's top) - clear of 1.06
ROW1_LOOK = {"kind": "datum", "series": 0, "index": 10}   # a datum: the compiler reads it at the plot's centre (624, 541)


def _page(**kw) -> dict:
    tl, _uris, _t, _asp = RB.load_surface(SURFACE)
    page = json.loads(json.dumps(tl["scenes"][0]["world"]["page"]))
    page.update(full_stage=True, caption="anchor")
    page.update(kw)
    return page


def _world(page: dict | None = None) -> dict:
    return {"kind": B.SPECIES_LEDGER, "page": page if page is not None else _page()}


def _halving_world(tmp: Path) -> dict:
    """test_compare_on_bars' halving page (a full-stage bars page, its boxes the estimate): the one subject here with
    room for a 1.06 pull - on the divergence page the y tick column (left of x 1024) and the drawn "+613%" tag (right
    of x 1160) leave no centre a 1.06 pull clears."""
    sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
    from test_compare_on_bars import FIXTURES
    oid, obj, _sp, _bar = FIXTURES["row18-halving"]
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        world = B.world_for_plate(f"ledger:{oid}:bars", (0, 0, 0), tmp)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


def _dock(place: dict, arrive: str = "stamp", slide: str = "prop-federal-reserve-building-v1",
          enter: float = 10.0, exit_: float = 20.0) -> dict:
    return {"slide": slide, "enter": enter, "exit": exit_, "place": dict(place), "arrive": arrive}


def _landings(**kw) -> dict:
    return dict({"keys": [], "attention": "landings"}, **kw)


def _row1_keys(zoom: float = 1.06, **kw) -> dict:
    return dict({"keys": [{"t": 8.0, "zoom": 1.0, "look": ROW1_LOOK, "ease": "inout"},
                          {"t": 9.0, "zoom": zoom, "look": ROW1_LOOK, "ease": "inout"},
                          {"t": 12.0, "zoom": 1.0, "look": ROW1_LOOK, "ease": "inout"}],
                 "attention": "locked"}, **kw)


# ---- the page this is measured on --------------------------------------------------------------------------------

def test_the_subject_is_measured_with_its_drawn_end_tags():
    boxes = LPG.page_boxes(_page(), ASPECT)
    assert boxes["measured"] and LPG.full_stage(_page(), ASPECT)
    assert len(boxes[LPG.TAG_BOXES_KEY]) == 4, "the four end tags, each at its drawn rect"


# ---- (1) the landing pull ------------------------------------------------------------------------------------------

def test_the_fed_landing_pull_that_cuts_the_title_and_the_y_ticks_is_refused_by_name():
    errs, notes, cam = B.camera_reach(_world(), [_dock(FED_PLACE)], _landings(), PLATE, ASPECT)
    assert errs, "the compiler accepted the stamp-landing pull that crops the title (T26b)"
    msg = errs[0]
    assert "prop-federal-reserve-building-v1" in msg and "1.06" in msg, msg
    assert "y tick column" in msg or "title" in msg, msg
    assert 'reach: "clamp"' in msg, "the refusal names the row's other choice"


def test_the_row_may_choose_the_clamp_and_the_pull_stops_at_the_reach():
    errs, notes, cam = B.camera_reach(_world(), [_dock(FED_PLACE)], _landings(reach="clamp"), PLATE, ASPECT)
    assert errs == []
    c = (FED_PLACE["x"] + FED_PLACE["w"] / 2, FED_PLACE["y"] + FED_PLACE["h"] / 2)
    z_rest = B.page_zoom_ceiling(_page(), ASPECT, c)[0]
    z, _name = B._page_reach(_page(), ASPECT, B.page_idle_boxes(B.page_reach_boxes(_page(), ASPECT), _world(), ASPECT), c, c)
    assert z < z_rest, "the breath takes some of the room the page has at rest"
    assert cam["landing_zoom"] == math.floor(z * 100) / 100 == 1.03 < MG.ATTN_SCALE, cam
    assert notes and "clamp" in notes[0] and "prop-federal-reserve-building-v1" in notes[0], notes


def test_a_landing_pull_that_clears_writes_nothing(tmp_path):
    src = _landings()
    world = _halving_world(tmp_path)
    assert LPG.full_stage(world["page"], ASPECT)
    errs, notes, cam = B.camera_reach(world, [_dock(CLEAR_PLACE)], src, "ledger:fx-index-concentration-bars:bars", ASPECT)
    assert errs == [] and notes == [] and cam is src and "landing_zoom" not in cam


def test_the_idle_excursion_is_the_breath_about_the_centre_and_the_drift():
    box = {"x": 67.0, "y": 44.0, "w": 100.0, "h": 50.0}
    still = B.page_idle_boxes({"t": box}, {"kind": B.SPECIES_LEDGER, "page": {"idle": "none"}}, ASPECT)["t"]
    breath = B.page_idle_boxes({"t": box}, _world(), ASPECT)["t"]
    live = B.page_idle_boxes({"t": box}, {"kind": B.SPECIES_LEDGER, "page": {}, "idle": "live"}, ASPECT)["t"]
    assert still == box, "a page that holds still is measured at rest"
    assert breath["x"] == pytest.approx(W / 2 + 1.012 * (67 - W / 2)) and breath["w"] == pytest.approx(101.2)
    assert live["x"] == pytest.approx(breath["x"] - 2.0) and live["h"] == pytest.approx(breath["h"] + 2.4)


def test_on_the_divergence_page_no_landing_centre_clears_a_1_06_pull():
    every = B.page_idle_boxes(B.page_reach_boxes(_page(), ASPECT), _world(), ASPECT)
    reach = [B._page_reach(_page(), ASPECT, every, (x, 540.0), (x, 540.0))[0] for x in range(200, 1800, 50)]
    assert max(reach) < MG.ATTN_SCALE, ("row 1's page has no room for the landing pull at all - clamp or lock", max(reach))


def test_only_an_arriving_dock_on_a_landings_camera_pulls():
    locked = {"keys": [], "attention": "locked"}
    assert B.camera_reach(_world(), [_dock(FED_PLACE)], locked, PLATE, ASPECT)[0] == []
    plain = _dock(FED_PLACE, arrive=None)
    assert B.camera_reach(_world(), [plain], _landings(), PLATE, ASPECT)[0] == []


def test_a_page_that_is_not_full_stage_or_not_a_page_takes_no_new_check():
    small = _page(full_stage=False)
    assert B.camera_reach(_world(small), [_dock(FED_PLACE)], _landings(), PLATE, ASPECT) == ([], [], _landings())
    plate = {"kind": "plate", "asset_id": "world-h1-studio-v1"}
    assert B.camera_reach(plate, [_dock(FED_PLACE)], _landings(), "world-h1-studio-v1", ASPECT) == ([], [], _landings())


def test_the_reach_choice_is_named_on_the_camera():
    assert B.CAMERA_REACH == ("refuse", "clamp")
    assert B.validate_camera(_landings(reach="crop"), PLATE, ASPECT), "an unknown choice is refused"
    assert B.validate_camera(_landings(reach="clamp"), PLATE, ASPECT) == []


# ---- (2) the keys ------------------------------------------------------------------------------------------------

def test_row_1s_key_is_reported_by_the_drawn_tag_and_not_refused():
    cam = _row1_keys()
    assert B.camera_zoom_errors(_world(), [], cam, PLATE, ASPECT) == [], "R26-220's glyph law still passes row 1"
    errs, notes, out = B.camera_reach(_world(), [], cam, PLATE, ASPECT)
    assert errs == [], "lane A's committed row 1 compiles (T33 re-aims it)"
    assert out == cam, "a report changes nothing"
    assert len(notes) == 1 and "WARN" in notes[0], notes
    assert "+613%" in notes[0] and "1.02" in notes[0] and "camera key 1" in notes[0], notes[0]


def test_row_1s_key_is_clamped_when_the_row_says_so():
    errs, notes, out = B.camera_reach(_world(), [], _row1_keys(reach="clamp"), PLATE, ASPECT)
    assert errs == []
    assert [k["zoom"] for k in out["keys"]] == [1.0, 1.02, 1.0], out["keys"]
    assert notes and "clamp" in notes[0]


def test_a_key_past_a_glyph_is_refused_as_before_and_clamped_on_the_rows_word():
    far = _row1_keys(zoom=1.2)
    assert B.camera_zoom_errors(_world(), [], far, PLATE, ASPECT), "R26-220 refuses it by name"
    clamped = _row1_keys(zoom=1.2, reach="clamp")
    assert B.camera_zoom_errors(_world(), [], clamped, PLATE, ASPECT) == [], "the row chose the clamp"
    errs, _notes, out = B.camera_reach(_world(), [], clamped, PLATE, ASPECT)
    assert errs == [] and out["keys"][1]["zoom"] == 1.02


def test_a_key_that_clears_keeps_its_camera_untouched():
    cam = _row1_keys(zoom=1.02)
    assert B.camera_reach(_world(), [], cam, PLATE, ASPECT) == ([], [], cam)


def test_the_compile_loop_runs_the_reach_check_on_the_placed_docks():
    src = inspect.getsource(B.main)
    assert "camera_reach(" in src, "main() measures every row's camera against its page once the docks are placed"
    assert src.index("assign_press_stack(docks)") < src.index("camera_reach("), "... after the docks are placed"


# ---- (3) the player and the gate read the clamp alike ------------------------------------------------------------

def _scene(landing_zoom: float | None, arrive: str = "stamp") -> dict:
    cam = _landings(**({"landing_zoom": landing_zoom} if landing_zoom is not None else {}))
    return {"scene_id": "s01", "span": [0.0, 30.0], "camera": cam,
            "docks": [_dock(FED_PLACE, arrive=arrive, enter=10.0, exit_=20.0)], "world": _world(), "species": []}


def test_the_gates_mirror_reads_the_clamp_and_nothing_else_moves():
    held = 10.0 + MG.STAMP_CONTACT_S + 2.0
    assert MG.camera_state_at(_scene(None), held, W, H, None)["s"] == pytest.approx(MG.ATTN_SCALE)
    assert MG.camera_state_at(_scene(1.04), held, W, H, None)["s"] == pytest.approx(1.04)
    moves = MG._attention_moves(_scene(1.04))
    assert moves == MG._attention_moves(_scene(None)), "the pull keeps its clock; only its depth is clamped"


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
def test_the_player_pulls_to_the_clamp_and_agrees_with_the_gate():
    from playwright.sync_api import sync_playwright
    tl0, uris, _t, _asp = RB.load_surface(SURFACE)
    card = RB.load_surface("dock-pair-16x9")   # a committed card to land (the camera reads the dock's data, not its art)
    uris = dict(uris, **{"ev-golden-card-a": card[1]["ev-golden-card-a"]})
    held = 12.5                                # a landing's contact is ~0.5 s after its enter; the pull is held to exit - OUT
    got = {}
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        try:
            for lz in (None, 1.04):
                tl = copy.deepcopy(tl0)
                sc = tl["scenes"][0]
                sc["world"]["page"].update(full_stage=True)
                sc["camera"] = _scene(lz, "land")["camera"]
                sc["docks"] = [B.dock_entry("ev-golden-card-a", 0, 10.0, 20.0, 0, place=dict(FED_PLACE), arrive="land")]
                tl["evidence"] = dict(tl.get("evidence") or {}, **{k: v for k, v in (card[0].get("evidence") or {}).items()
                                                                  if k == "ev-golden-card-a"})
                tl["kinetics"] = dict(tl.get("kinetics") or {}, camera=True)
                with tempfile.TemporaryDirectory() as td:
                    html = Path(td) / "cam.html"
                    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
                    srv, port = RB.serve(html.parent)
                    try:
                        page = br.new_context(viewport={"width": W, "height": H}).new_page()
                        page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                        RB.prepare_page(page, W, H)
                        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", held)
                        got[lz] = page.evaluate("t => window.__camera(t)", held)
                        page.context.close()
                    finally:
                        srv.shutdown()
        finally:
            br.close()
    assert got[None]["zoom"] == pytest.approx(MG.ATTN_SCALE, abs=1e-4), got[None]
    assert got[1.04]["zoom"] == pytest.approx(1.04, abs=1e-4), got[1.04]
    gate = MG.camera_state_at(_scene(1.04, "land"), held, W, H, None)
    assert got[1.04]["zoom"] == pytest.approx(gate["s"], abs=1e-4) and list(got[1.04]["look"]) == pytest.approx(list(gate["look"]), abs=0.01)

"""P69 T26d / E99 s106 - A PROP GOES WHERE THE AUTHOR PUTS IT, AND MOVES AFTER IT LANDS; THE FIT IS A DEFAULT AND ADVISES.

The operator (2026-09-23): *"the engine is being too controlling. the whole point of making our drawing capabilities
using advanced math instead of using remotion or hyperframes was to give us more freedom, we should be able to
manipulate props freely"*. What this file holds the compiler and the engine to:

  (1) AN AUTHORED PLACE   `{"place": {"x", "y", "w"}}` (stage fractions: the PAINTED centre and the painted width; the
                          height is the cutout's own alpha aspect) and `"rot"` (the resting angle, degrees) on any prop
                          dock, `arrive: stamp` included, are honoured exactly; the stamp's ring and approach are drawn
                          around THAT place.
  (2) MOVES               `{"moves": [{"at", "x", "y", "w", "rot", "dur", "ease"}]}` move the prop after it lands, on
                          its own clock: a cold seek lands the frame forward play lands, and the T6b hatch rides the
                          prop's transform (R26-271's case).
  (3) THE DEFAULT FIT     with no authored place, a stamp is fitted to the chart state ON SCREEN at its landing (a
                          `then=` / `chart_to` state's own boxes), never the row's first state (R26-279).
  (4) WARN, DON'T REFUSE  over the data, over a label, under the mark floor, cut by the frame, over the caption: each
                          a WARN with its numbers. The one placement refusal left: a prop wholly off the stage.
  (5) BYTE-IDENTICAL      a dock that authors none of it writes the entry it always wrote (the goldens hold the rest).
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
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
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

SURFACE = "prop-stamp"
ENTER = G.PROP_STAMP_ENTER
SW, SH = 1920, 1080
STAMP = {"prop": True, "arrive": "stamp", "mass": "ink"}
PLAIN = {"asset_id": "plate-plain"}
STOPACTION = ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs"


def _fed() -> dict:
    return B.painted_box(G.PROP_CUTOUT)


def _golden_world() -> dict:
    return copy.deepcopy(G.SURFACES[SURFACE]()[0]["scenes"][0]["world"])


def _fit(world, opts, room=None, reserve=None, where="shot row 1 (0-30s) dock ev-prop-fed"):
    return B.stamp_dock_place(world, "16:9", B.dock_opts(opts), _fed(), room, reserve, where)


def _painted_centre(fit: dict) -> tuple[float, float]:
    x0, y0, x1, y1 = fit["paint"]
    return fit["x"] + fit["w"] * (x0 + x1) / 2, fit["y"] + fit["h"] * (y0 + y1) / 2


# ---- (1) the authored place ------------------------------------------------------------------------------------------


def test_an_authored_place_and_rot_on_a_stamped_prop_are_accepted_by_the_grammar():
    d = B.dock_opts({**STAMP, "place": {"x": 0.865, "y": 0.46, "w": 0.2}, "rot": -4})
    assert d["place"] == {"x": 0.865, "y": 0.46, "w": 0.2} and d["rot"] == -4


def test_an_authored_place_on_a_stamp_is_HONOURED_EXACTLY_centre_and_width():
    """The painted centre is the authored (x, y) and the painted width the authored w, to the rounding of a whole-px
    canvas box; the height is the cutout's own alpha aspect."""
    fit = _fit(_golden_world(), {**STAMP, "place": {"x": 0.865, "y": 0.46, "w": 0.2}})
    cx, cy = _painted_centre(fit)
    pw, ph = fit["painted"]
    fed = _fed()
    assert abs(cx - 0.865 * SW) <= 1.0 and abs(cy - 0.46 * SH) <= 1.0, (cx, cy)
    assert abs(pw - 0.2 * SW) <= 1.5, pw
    aspect = fed["aspect"] * (fed["y1"] - fed["y0"]) / (fed["x1"] - fed["x0"])
    assert abs(ph / pw - aspect) < 0.01, (ph / pw, aspect)
    assert fit["room"] == "authored"


def test_the_ring_and_the_approach_are_drawn_around_the_authored_place():
    """In open ground the source's full 2x ring and 2.1x approach stand around the authored place; in a tight place they
    are capped by the room but never below the ring's floor (just outside the painted edge) or the 1.2x approach."""
    open_fit = _fit(PLAIN, {**STAMP, "place": {"x": 0.5, "y": 0.45, "w": 0.1}}, room={"x": 400, "y": 150, "w": 1100, "h": 700})
    assert open_fit["ring_to"] == 2.0 and open_fit["from_to"] == 2.1, open_fit["why"]
    assert abs(open_fit["centre"][0] - 960) <= 1 and abs(open_fit["centre"][1] - 486) <= 1, "the ring's centre IS the place"
    tight = _fit(_golden_world(), {**STAMP, "place": {"x": 0.865, "y": 0.46, "w": 0.2}})
    assert tight["ring_floor"] <= tight["ring_to"] <= 2.0 and B.STAMP_APPROACH_MIN <= tight["from_to"] <= 2.1


def test_an_authored_rot_is_the_resting_angle_and_the_fit_turns_the_mark_through_it():
    d = B.dock_entry("a", 0, 1, 5, 0, B.DOCK_KIND_PROP, {"x": 1, "y": 2, "w": 3, "h": 4}, "stamp", "ink", True, prop=True, rot=12.5)
    assert d["rot"] == 12.5
    assert B.STAMP_LAND_DEG == -9, "the kinetics' own LAND_DEG (stopaction.mjs STAMP_ARRIVAL) - one dial written twice"
    lo, hi = B.stamp_turns(12.5)
    assert lo < 12.5 < hi and abs((hi - lo) - (B.STAMP_TURN_RANGE[1] - B.STAMP_TURN_RANGE[0])) < 1e-9, "the same swing, about the authored rest"
    assert B.stamp_turns(None) == B.STAMP_TURN_RANGE


def test_an_authored_place_on_a_THROWN_or_sprung_prop_is_honoured_too():
    world = _golden_world()
    for arrive in ("throw", "spring", "land"):
        dopt = B.dock_opts({"prop": True, "arrive": arrive, "place": {"x": 0.865, "y": 0.46, "w": 0.2}})
        pf = B.prop_place_fit(world, "16:9", dopt, _fed(), None, "t")
        cx, cy = _painted_centre(pf)
        assert abs(cx - 0.865 * SW) <= 1.0 and abs(cy - 0.46 * SH) <= 1.0 and abs(pf["painted"][0] - 384) <= 1.5, (arrive, pf)
        assert "ring_to" not in pf, "only a stamp throws a ring"


def test_place_is_a_PROPS_option_and_names_one_place_only():
    with pytest.raises(ValueError, match="place is a PROP's option"):
        B.dock_opts({"place": {"x": 0.5, "y": 0.5, "w": 0.2}})
    with pytest.raises(ValueError, match="place and centre_x"):
        B.dock_opts({**STAMP, "place": {"x": 0.5, "y": 0.5, "w": 0.2}, "centre_x": 0.4})
    with pytest.raises(ValueError, match="place must be"):
        B.dock_opts({**STAMP, "place": {"x": 0.5, "y": 0.5}})
    with pytest.raises(ValueError, match="rot is a PROP's option"):
        B.dock_opts({"rot": 4})


# ---- (4) WARN, don't refuse ------------------------------------------------------------------------------------------


def _warns(fit) -> str:
    return " | ".join(fit.get("warns") or [])


def test_an_authored_place_OVER_THE_DATA_is_a_WARN_with_its_numbers():
    world = _golden_world()
    plot = LPG.page_boxes(world["page"], "16:9")["plot"]
    fit = _fit(world, {**STAMP, "place": {"x": (plot["x"] + plot["w"] / 2) / SW, "y": (plot["y"] + plot["h"] / 2) / SH, "w": 0.15}})
    w = _warns(fit)
    assert "over the data" in w and "px^2" in w, w


def test_an_authored_place_OVER_A_LABEL_and_OVER_THE_CAPTION_and_CUT_BY_THE_FRAME_are_WARNs():
    world = _golden_world()
    boxes = LPG.page_boxes(world["page"], "16:9")
    t = boxes["title"]
    over_title = _fit(world, {**STAMP, "place": {"x": (t["x"] + 60) / SW, "y": (t["y"] + t["h"] / 2) / SH, "w": 0.08}})
    assert "over a label" in _warns(over_title) and "title" in _warns(over_title), _warns(over_title)
    c = boxes["caption_anchor"]
    over_cap = _fit(world, {**STAMP, "place": {"x": (c["x"] + c["w"] / 2) / SW, "y": (c["y"] + c["h"] / 2) / SH, "w": 0.08}})
    assert "over the caption" in _warns(over_cap), _warns(over_cap)
    cut = _fit(world, {**STAMP, "place": {"x": 0.99, "y": 0.5, "w": 0.12}})
    assert "cut by the frame" in _warns(cut) and "right" in _warns(cut), _warns(cut)


def test_a_mark_UNDER_THE_FLOOR_is_a_WARN_never_a_refusal():
    """Was: `stamp_dock_place` raised 'under the 120 px mark floor'. Now the mark is fitted as large as the room holds
    and the build is told, with the numbers."""
    fit = B.stamp_dock_place(PLAIN, "16:9", B.dock_opts(STAMP), _fed(), {"x": 800, "y": 400, "w": 40, "h": 40},
                             [{"x": 700, "y": 520, "w": 400, "h": 20}], "t")
    w = _warns(fit)
    assert "under the mark floor" in w and "120 px" in w, w
    small = _fit(PLAIN, {**STAMP, "place": {"x": 0.5, "y": 0.5, "w": 0.03}}, room={"x": 400, "y": 150, "w": 1100, "h": 700})
    assert "under the mark floor" in _warns(small), _warns(small)


def test_a_plate_stamp_with_NO_ROOM_is_fitted_over_the_frame_and_WARNed():
    fit = _fit(PLAIN, STAMP)
    assert "no room" in _warns(fit), _warns(fit)
    safe = B.FRAME_BANDS["16:9"]["safe"]
    cx, cy = fit["centre"]
    assert safe["x"] <= cx <= safe["x"] + safe["w"] and safe["y"] <= cy <= safe["y"] + safe["h"]


def test_a_page_that_hides_its_end_names_is_fitted_and_WARNed_blind():
    page = LPG.build_spec(LPG.load_series(G.SERIES), "line", 0, "right")   # not full-stage: no measured tags box
    fit = _fit({"kind": "ledger", "page": page}, STAMP)
    w = _warns(fit)
    assert "end names" in w and "tag_units" in w, w


def test_read_and_park_on_a_stamp_are_WARNed_not_refused():
    for other, value in (("read", {"centre_w": 0.3}), ("read_s", 1.0), ("park_s", 0.5), ("centre_band", B.DOCK_BAND_ORDER[0])):
        opts = {**STAMP, other: value, **({"centre": True} if other == "read" else {})}
        fit = _fit(_golden_world(), opts)
        assert other in _warns(fit) and "moves" in _warns(fit), (other, _warns(fit))
    with pytest.raises(ValueError, match="arrive=stamp and embed cannot be combined"):
        B.dock_opts({**STAMP, "embed": "poster"})


def test_a_place_WHOLLY_OFF_THE_STAGE_is_the_one_refusal():
    with pytest.raises(ValueError, match="wholly off the stage"):
        _fit(_golden_world(), {**STAMP, "place": {"x": 1.6, "y": 0.5, "w": 0.1}})
    with pytest.raises(ValueError, match="wholly off the stage"):
        B.prop_place_fit(PLAIN, "16:9", B.dock_opts({"prop": True, "place": {"x": 0.5, "y": -0.5, "w": 0.1}}), _fed(), None, "t")


def test_a_card_over_a_stamp_is_REPORTED_not_refused():
    world = _golden_world()
    fits, taken = B.row_stamp_fits(world, "16:9", [("ev-prop-fed", B.dock_opts(STAMP), _fed())], None, [], "shot row 1 (0-30s)")
    msg = B.stamp_clash_error("shot row 1 (0-30s) dock ev-card", dict(taken[0]), taken)
    assert msg and "stamp" in msg
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    body = src[src.index("_clash = stamp_clash_error("):][:400]
    assert "[WARN]" in body and "SystemExit" not in body, "the loop prints the clash as a WARN"


# ---- (2) moves after landing, compiled ---------------------------------------------------------------------------------


MOVES = [{"at": 14.0, "x": 0.3, "y": 0.5, "w": 0.12, "dur": 1.0, "ease": "minjerk"}, {"at": 16.0, "rot": 8}]


def test_moves_compile_to_whole_boxes_each_key_inheriting_what_it_does_not_name():
    dopt = B.dock_opts({**STAMP, "place": {"x": 0.865, "y": 0.46, "w": 0.2}, "rot": 0, "moves": MOVES})
    fit = _fit(_golden_world(), {**STAMP, "place": {"x": 0.865, "y": 0.46, "w": 0.2}, "rot": 0})
    moves, warns = B.prop_moves(dopt, _fed(), fit, "16:9", ENTER, 26.0, None, "t", _golden_world())
    assert [m["at"] for m in moves] == [14.0, 16.0]
    a, b = moves
    assert set(a) == {"at", "dur", "ease", "x", "y", "w", "rot"} and a["rot"] == 0 and a["ease"] == "minjerk"
    x0, y0, x1, y1 = fit["paint"]
    assert abs(a["x"] + a["w"] * (x0 + x1) / 2 - 0.3 * SW) <= 1 and abs(a["w"] * (x1 - x0) - 0.12 * SW) <= 1.5
    assert (b["x"], b["y"], b["w"]) == (a["x"], a["y"], a["w"]) and b["rot"] == 8 and b["dur"] == B.PROP_MOVE_S
    assert b["ease"] == B.PROP_MOVE_EASES[0]


def test_a_move_may_name_its_word():
    words = [{"w": "a", "start": 9.0}, {"w": "bet", "start": 15.2}, {"w": "on", "start": 15.5}, {"w": "bet", "start": 20.0}]
    dopt = B.dock_opts({**STAMP, "moves": [{"at": "bet on", "x": 0.3}]})
    fit = _fit(_golden_world(), STAMP)
    moves, _w = B.prop_moves(dopt, _fed(), fit, "16:9", ENTER, 26.0, words, "t", _golden_world())
    assert moves[0]["at"] == 15.2
    with pytest.raises(ValueError, match="not in the take"):
        B.prop_moves(B.dock_opts({**STAMP, "moves": [{"at": "never said", "x": 0.3}]}), _fed(), fit, "16:9", ENTER, 26.0, words, "t", _golden_world())


def test_moves_are_refused_only_when_they_cannot_be_played_or_seen():
    fit = _fit(_golden_world(), STAMP)
    for bad, why in (([{"at": 9.0, "x": 0.3}], "before the prop"), ([{"at": 14, "x": 0.3, "dur": 2}, {"at": 15, "x": 0.4}], "overlaps"),
                     ([{"at": 27.0, "x": 0.3}], "after the prop"), ([{"at": 14, "x": 3.0}], "wholly off the stage")):
        with pytest.raises(ValueError, match=why):
            B.prop_moves(B.dock_opts({**STAMP, "moves": bad}), _fed(), fit, "16:9", ENTER, 26.0, None, "t", _golden_world())
    moves, warns = B.prop_moves(B.dock_opts({**STAMP, "moves": [{"at": 14, "x": 0.5, "y": 0.5, "w": 0.2}]}), _fed(), fit,
                                "16:9", ENTER, 26.0, None, "t", _golden_world())
    assert moves and any("over the data" in w for w in warns), warns
    with pytest.raises(ValueError, match="ease"):
        B.dock_opts({**STAMP, "moves": [{"at": 14, "x": 0.3, "ease": "bounce"}]})
    with pytest.raises(ValueError, match="moves"):
        B.dock_opts({"moves": [{"at": 14, "x": 0.3}]})


# ---- (3) R26-279: the default fit reads the state on screen ----------------------------------------------------------


def _two_state_world() -> tuple[dict, list]:
    """The golden's line page, then a bars state recast onto it at 12 s (the H door's row-16 grammar)."""
    world = _golden_world()
    _aspect, B.ASPECT = B.ASPECT, "16:9"   # `stamp_full_stage` reads the compiler's module global (the golden builder's pin)
    try:
        other = B.stamp_full_stage(LPG.build_spec(LPG.load_series(G.SERIES), "line", 0, "left"))
    finally:
        B.ASPECT = _aspect
    world["page_states"] = [other]
    species = [{"kind": "chart_to", "at": 12.0, "dur": 1.2, "to": "recast", "state": 1, "keyed": False}]
    return world, species


def test_R26_279_the_state_on_screen_is_the_last_recast_begun_by_the_landing():
    world, species = _two_state_world()
    assert B.page_on_screen(world, species, 11.9) is world, "before the recast: the row's own world, the same object"
    assert B.page_on_screen(world, species, 12.0)["page"] is world["page_states"][0]
    assert B.page_on_screen(world, species, 20.0)["page"] is world["page_states"][0]
    assert B.page_on_screen({"asset_id": "plate"}, species, 20.0) == {"asset_id": "plate"}


def test_R26_279_a_stamp_landing_after_a_recast_is_fitted_to_THAT_state():
    world, species = _two_state_world()
    first = B.row_stamp_fits(world, "16:9", [("p", B.dock_opts(STAMP), _fed())], None, [], "r")[0][0]
    later = B.row_stamp_fits(world, "16:9", [("p", B.dock_opts(STAMP), _fed())], None, [], "r",
                             worlds={0: B.page_on_screen(world, species, 14.0)})[0][0]
    alone = B.stamp_dock_place({**world, "page": world["page_states"][0]}, "16:9", B.dock_opts(STAMP), _fed(), None, [], "r")
    assert later["centre"] == alone["centre"] and later["painted"] == alone["painted"], "fitted to the state on screen"
    assert later["centre"] != first["centre"], "and not to the row's first state"


# ---- (5) byte-identical --------------------------------------------------------------------------------------------------


def test_a_dock_that_authors_nothing_writes_the_entry_it_always_wrote():
    d = B.dock_entry("a", 0, 1, 5, 0, B.DOCK_KIND_PROP, {"x": 1, "y": 2, "w": 3, "h": 4}, "stamp", "ink", True, prop=True,
                     ring_to=1.5, from_to=2.0, paint=[0, 0, 1, 1])
    assert "rot" not in d and "moves" not in d
    fit = _fit(_golden_world(), STAMP)
    golden = RB.load_surface(SURFACE)[0]["scenes"][0]["docks"][0]
    assert {k: fit[k] for k in ("x", "y", "w", "h")} == golden["place"] and fit["warns"] == []


# ---- (2) moves after landing, ON THE FRAME ---------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const sb = document.getElementById('stage').getBoundingClientRect();
  const d = document.querySelector('.dock[data-slide]'), img = d && d.querySelector('.slide-frame img');
  const cs = d ? getComputedStyle(d) : null, m = cs ? new DOMMatrix(cs.transform === 'none' ? undefined : cs.transform) : null;
  const hv = document.getElementById('dock-hatch-0');
  const r = img ? img.getBoundingClientRect() : null;
  return { left: d ? parseFloat(d.style.left) : null, top: d ? parseFloat(d.style.top) : null, width: d ? parseFloat(d.style.width) : null,
           deg: m ? Math.atan2(m.b, m.a) * 180 / Math.PI : null,
           img: r ? { x: r.left - sb.left, y: r.top - sb.top, w: r.width, h: r.height } : null,
           hatch: hv ? { x: parseFloat(hv.style.left), y: parseFloat(hv.style.top), w: hv.width, h: hv.height, op: +hv.style.opacity } : null };
}"""


class _Player:
    def __init__(self, browser, tl: dict, uris: dict):
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.size = RB.STAGE["16:9"]
        self._srv, port = RB.serve(html.parent)
        self.page = browser.new_context(viewport={"width": self.size[0], "height": self.size[1]}).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, *self.size)

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                           "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def png(self, t: float) -> bytes:
        return RB.frame_png(self.page, t, self.size)

    def close(self) -> None:
        self.page.context.close(); self._srv.shutdown(); self._td.cleanup()


T_MOVE, T_MOVE_DUR = 14.0, 1.0
T_BEFORE, T_MID, T_AFTER, T_TURNED = 13.9, 14.5, 15.3, 17.0


def moved_timeline() -> tuple[dict, dict, dict, list]:
    """The committed `prop-stamp` surface with its Fed stamped at an AUTHORED place and rot, then moved on 14 s and
    turned on 16 s - compiled by the same functions the row loop calls."""
    tl, uris, _t, _a = RB.load_surface(SURFACE)
    tl, uris = copy.deepcopy(tl), dict(uris)
    world = tl["scenes"][0]["world"]
    opts = {**STAMP, "ink": "own", "place": {"x": 0.62, "y": 0.62, "w": 0.12}, "rot": -4,
            "moves": [{"at": T_MOVE, "x": 0.4, "y": 0.66, "w": 0.16, "dur": T_MOVE_DUR, "ease": "minjerk"},
                      {"at": 16.0, "rot": 6, "dur": 0.6}]}
    dopt = B.dock_opts(opts)
    fit = B.stamp_dock_place(world, "16:9", dopt, _fed(), None, None, "t")
    moves, _w = B.prop_moves(dopt, _fed(), fit, "16:9", ENTER, G.PROP_STAMP_EXIT, None, "t", world)
    dock = tl["scenes"][0]["docks"][0]
    new = B.dock_entry(dock["slide"], 0, ENTER, G.PROP_STAMP_EXIT, 0, B.DOCK_KIND_PROP, {k: fit[k] for k in ("x", "y", "w", "h", "room")},
                       "stamp", "ink", True, prop=True, ink="own", ring_to=fit["ring_to"], from_to=fit["from_to"],
                       paint=fit["paint"], rot=dopt["rot"], moves=moves)
    tl["scenes"][0]["docks"] = [new]
    return tl, uris, fit, moves


@contextlib.contextmanager
def _browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        yield br
    finally:
        br.close(); pw.stop()


@pytest.fixture(scope="module")
def moved():
    tl, uris, fit, moves = moved_timeline()
    out = {"fit": fit, "moves": moves, "reads": {}, "png": {}, "cold": {}}
    with _browser() as br:
        fwd = _Player(br, tl, uris)
        try:
            t = ENTER
            while t <= T_TURNED + 1e-9:   # FORWARD PLAY: every 0.1 s from the contact
                r = fwd.at(round(t, 2))
                out["reads"][round(t, 2)] = r
                t += 0.1
            for tt in (T_BEFORE, T_MID, T_AFTER, T_TURNED):
                out["reads"][tt] = fwd.at(tt)
                out["png"][tt] = hashlib.sha256(fwd.png(tt)).hexdigest()
            out["errors"] = list(fwd.errors)
        finally:
            fwd.close()
        for tt in (T_MID, T_AFTER):   # COLD SEEKS: a fresh player straight to the instant
            cold = _Player(br, tl, uris)
            try:
                out["cold"][tt] = hashlib.sha256(cold.png(tt)).hexdigest()
            finally:
                cold.close()
    return out


@needs_browser
def test_the_prop_LANDS_at_its_authored_place_and_RESTS_at_its_authored_angle(moved):
    r, fit = moved["reads"][T_BEFORE], moved["fit"]
    assert moved["errors"] == []
    assert abs(r["left"] - fit["x"]) < 0.01 and abs(r["top"] - fit["y"]) < 0.01 and abs(r["width"] - fit["w"]) < 0.01, r
    assert abs(r["deg"] - (-4)) < 0.3, f"rests at the authored -4 deg, not the stamp's default -9: {r['deg']}"


@needs_browser
def test_the_MOVE_is_painted_on_the_props_own_clock_and_ends_on_its_key(moved):
    a, before, mid, after = moved["moves"][0], moved["reads"][T_BEFORE], moved["reads"][T_MID], moved["reads"][T_AFTER]
    assert abs(after["left"] - a["x"]) < 0.01 and abs(after["top"] - a["y"]) < 0.01 and abs(after["width"] - a["w"]) < 0.01, after
    assert min(before["left"], a["x"]) < mid["left"] < max(before["left"], a["x"]), "mid-move is between the two boxes"
    assert abs(mid["left"] - (before["left"] + (a["x"] - before["left"]) * 0.5)) < 1.0, "min-jerk is half way at half time"
    turned = moved["reads"][T_TURNED]
    assert abs(turned["deg"] - 6) < 0.3 and abs(turned["left"] - a["x"]) < 0.01, "the second key turns it in place"
    xs = [moved["reads"][k]["left"] for k in sorted(k for k in moved["reads"] if isinstance(k, float) and k <= T_TURNED)]
    peak = 1.875 * abs(a["x"] - before["left"]) / T_MOVE_DUR * 0.1   # min-jerk's peak speed (15/8 of the mean) over one 0.1 s step
    assert all(abs(b - c) <= peak + 1.0 for b, c in zip(xs, xs[1:])), f"no jump between 0.1 s steps (peak {peak:.1f} px)"


@needs_browser
def test_a_COLD_SEEK_lands_the_frame_forward_play_lands(moved):
    for tt in (T_MID, T_AFTER):
        assert moved["cold"][tt] == moved["png"][tt], f"at {tt} the cold seek differs from forward play"


@needs_browser
def test_the_HATCH_RIDES_the_props_move(moved):
    """R26-271's case: the hatch's canvas follows the prop's own move - its bounds shift with the mark's box."""
    before, after = moved["reads"][T_BEFORE], moved["reads"][T_AFTER]
    assert before["hatch"] and after["hatch"] and after["hatch"]["op"] > 0, (before["hatch"], after["hatch"])
    dx = after["img"]["x"] - before["img"]["x"]
    assert abs((after["hatch"]["x"] - before["hatch"]["x"]) - dx) <= 4, (before, after)
    assert after["hatch"]["w"] > before["hatch"]["w"], "and grows with it"


# ---- (2b) CHAINED keys pass THROUGH the middle key (the parent's find: kinetics/ease.mjs `hermiteChain`) -----------------


def _chain_timeline(gap: float) -> tuple[dict, dict, list]:
    """The Fed at an authored place, then two keys: 14 -> 15 s to a first box and, `gap` s later, a second box."""
    tl, uris, _t, _a = RB.load_surface(SURFACE)
    tl, uris = copy.deepcopy(tl), dict(uris)
    world = tl["scenes"][0]["world"]
    opts = {**STAMP, "ink": "own", "place": {"x": 0.62, "y": 0.62, "w": 0.12},
            "moves": [{"at": 14.0, "x": 0.45, "dur": 1.0}, {"at": 15.0 + gap, "x": 0.25, "dur": 1.0}]}
    dopt = B.dock_opts(opts)
    fit = B.stamp_dock_place(world, "16:9", dopt, _fed(), None, None, "t")
    moves, _w = B.prop_moves(dopt, _fed(), fit, "16:9", ENTER, G.PROP_STAMP_EXIT, None, "t", world)
    new = B.dock_entry(tl["scenes"][0]["docks"][0]["slide"], 0, ENTER, G.PROP_STAMP_EXIT, 0, B.DOCK_KIND_PROP,
                       {k: fit[k] for k in ("x", "y", "w", "h", "room")}, "stamp", "ink", True, prop=True, ink="own",
                       ring_to=fit["ring_to"], from_to=fit["from_to"], paint=fit["paint"], moves=moves)
    tl["scenes"][0]["docks"] = [new]
    return tl, uris, moves


@pytest.fixture(scope="module")
def chained():
    out = {}
    with _browser() as br:
        for tag, gap in (("chain", 0.0), ("gap", 0.5)):
            tl, uris, moves = _chain_timeline(gap)
            pl = _Player(br, tl, uris)
            try:
                mid = moves[0]["at"] + moves[0]["dur"]
                out[tag] = {"moves": moves, "errors": pl.errors,
                            "v_mid": (pl.at(round(mid + 0.05, 2))["left"] - pl.at(round(mid - 0.05, 2))["left"]) / 0.1,
                            "at_mid": pl.at(round(mid, 2))["left"], "end": pl.at(18.0)["left"],
                            "png": hashlib.sha256(pl.png(15.3)).hexdigest()}
            finally:
                pl.close()
            cold = _Player(br, tl, uris)
            try:
                out[tag]["cold"] = hashlib.sha256(cold.png(15.3)).hexdigest()
            finally:
                cold.close()
    return out


@needs_browser
def test_CHAINED_keys_pass_through_the_middle_key_at_speed_and_a_gap_stops_there(chained):
    c, g = chained["chain"], chained["gap"]
    assert c["errors"] == [] and g["errors"] == []
    a, b = c["moves"]
    assert abs(c["at_mid"] - a["x"]) < 0.5, "the chain passes through the middle key's box"
    assert abs(c["end"] - b["x"]) < 0.01 and abs(g["end"] - chained["gap"]["moves"][1]["x"]) < 0.01, "and settles on the last"
    assert c["v_mid"] < -100, f"through the middle key at speed (px/s): {c['v_mid']:.1f}"
    assert abs(g["v_mid"]) < 30, f"a key after a gap starts from rest - it stops at the middle key: {g['v_mid']:.1f} px/s"
    assert c["cold"] == c["png"] and g["cold"] == g["png"], "a cold seek lands the chain's frame too"


def test_the_authoring_kit_writes_the_grammar_the_compiler_reads():
    from authoring import docks as D
    opts = B.dock_opts({**STAMP, **D.prop_place(0.86, 0.46, 0.2, rot=-3),
                        "moves": [D.prop_move(14, x=0.5), D.prop_move("bet on", rot=4, dur=0.8)]})
    assert opts["place"] == {"x": 0.86, "y": 0.46, "w": 0.2} and opts["rot"] == -3
    assert opts["moves"] == [{"at": 14, "x": 0.5}, {"at": "bet on", "rot": 4, "dur": 0.8}]
    assert "rot" not in D.prop_place(0.5, 0.5, 0.1)
    with pytest.raises(ValueError, match="moves nothing"):
        D.prop_move(14)

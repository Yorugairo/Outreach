"""P47 T1 - STOP-ACTION MECHANICS (operator 2026-09-06, three times: "operationalize stop-action mechanics to be able to
throw things on page or land things with weight").

The math is in tests/kinetics/stopaction.test.mjs (node). Here: the compiler's grammar (`;arrive=`/`;mass=` on a plate
id, the dock tuple's option dict), the gate (a throw or a landing is motion; the M20 cadence note), the template's
wiring behind `kinetics.stop_action`, and the browser proof: a dock declared `arrive: throw` is off its spot mid-flight
and on the spring's spot once landed; a page's pills declared `arrive: land` LIFT before they drop.
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

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import render_baseline as RB  # noqa: E402

TEMPLATE = RB.TEMPLATE
SOURCES = RB.SOURCES
DOCK_IN, DOCK_OUT = 4.0, 20.0


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the compiler ----------------------------------------------------------------------------


def test_plate_options_name_the_idle_the_arrival_and_the_mass():
    assert B.split_plate_opts("ledger:x:line") == ("ledger:x:line", {})
    assert B.split_plate_opts("ledger:x:line;idle=none;arrive=land;mass=metal") == ("ledger:x:line", {"idle": "none", "arrive": "land", "mass": "metal"})
    assert B.split_idle("plate-07;arrive=throw") == ("plate-07", None), "the idle reader ignores the other options"
    with pytest.raises(ValueError, match="arrive 'fling' is not one of"):
        B.split_plate_opts("plate-07;arrive=fling")
    with pytest.raises(ValueError, match="mass 'granite' is not one of"):
        B.split_plate_opts("plate-07;mass=granite")
    with pytest.raises(ValueError, match="plate option 'wobble' is not one of"):
        B.split_plate_opts("plate-07;wobble")


def test_world_for_plate_carries_the_arrival(tmp_path: Path):
    clip = tmp_path / "c.mp4"
    clip.write_bytes(b"\x00" * 64)
    w = B.world_for_plate(f"clip:{clip};arrive=land;mass=ink", (0.0, 0, 0), tmp_path)
    assert w["arrive"] == "land" and w["mass"] == "ink" and w["asset_id"] == "c"
    assert "arrive" not in B.world_for_plate(f"clip:{clip}", (0.0, 0, 0), tmp_path)


def test_dock_options_are_a_dict_of_arrive_and_mass_and_are_written_only_when_named():
    assert B.dock_opts(None) == {} and B.dock_opts({"arrive": "throw"}) == {"arrive": "throw"}
    with pytest.raises(ValueError, match="dock option 'speed' is not one of"):
        B.dock_opts({"speed": 3})
    with pytest.raises(ValueError, match="arrive 'fall' is not one of"):
        B.dock_opts({"arrive": "fall"})
    with pytest.raises(ValueError, match="must be a dict"):
        B.dock_opts("throw")
    plain = B.dock_entry("ev", 0, 4.0, 20.0, 0)
    assert "arrive" not in plain and "mass" not in plain, "an unnamed arrival compiles exactly as before"
    thrown = B.dock_entry("ev", 0, 4.0, 20.0, 0, arrive="throw", mass="paper")
    assert thrown["arrive"] == "throw" and thrown["mass"] == "paper"
    assert B.build_kinetics()["stop_action"] is True, "an authored arrive is the switch; every compiled timeline carries the flag"


# ---- the gate --------------------------------------------------------------------------------


def _tl(docks):
    return {"aspect": "9:16", "runtime_s": 60.0, "caption_pages": [],
            "scenes": [{"scene_id": "s01", "span": [0.0, 30.0], "world": {"asset_id": "p"}, "docks": docks}]}


def test_a_throw_and_a_landing_are_motion_and_m20_names_the_cadence():
    docks = [B.dock_entry("card-a", 0, 4.0, 12.0, 0, arrive="throw", mass="paper", place={"x": 0, "y": 0, "w": 500, "h": 300}),
             B.dock_entry("card-b", 1, 14.0, 20.0, 0, arrive="land", mass="metal")]
    tl = _tl(docks)
    ev = G._arrival_events(tl["scenes"])
    assert ev == [round(4.0 + G.STOP_FLIGHT_S, 2), round(14.0 + G.STOP_LAND_S, 2)]
    gates, _ = G.run(tl, docks, {})
    by = {g.id: g for g in gates}
    assert by["M20"].level == "INFO" and "card-a throw ~" in by["M20"].message and "on 1s" in by["M20"].message
    assert "card-b land (metal)" in by["M20"].message
    assert "M20" not in {g.id for g in G.run(_tl([B.dock_entry("card-a", 0, 4.0, 12.0, 0)]), [], {})[0]}, "no arrival, no note"


# ---- the template ----------------------------------------------------------------------------


def test_the_flag_defaults_off_and_the_arrivals_hang_off_it():
    html = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"const KINETICS_DEFAULTS = Object\.freeze\(\{(.*?)\}\);", html, re.S)
    assert m and re.search(r"\bstop_action:\s*false", m.group(1))
    assert "/* KINETICS:BEGIN stopaction */" in html and "export" not in html.split("/* KINETICS:BEGIN stopaction */")[1].split("/* KINETICS:END */")[0]
    assert 'const arriveOf = (o) => (kin("stop_action") &&' in html
    assert html.count("throwXf(") >= 2 and html.count("landXf(") >= 2, "the dock and the pills both arrive (the definitions are assignments, not calls)"
    assert "lag(t) - d.enter" in html, "HF-2: the shadow reads the clock one frame late"


# ---- the browser -----------------------------------------------------------------------------


def _png(path: Path) -> Path:
    from PIL import Image
    Image.new("RGB", (640, 360), (200, 60, 30)).save(path)
    return path


def _dock_build(tmp_path: Path, arrive: str | None) -> Path:
    tl = json.loads((SOURCES / "ledger-page-mid-build.timeline.json").read_text(encoding="utf-8"))
    uris = json.loads((SOURCES / "ledger-page-mid-build.uris.json").read_text(encoding="utf-8"))
    aid = "card-a"
    tl["evidence"] = {aid: {"title": "a thrown card", "source": "synthetic", "species": "deck", "badges": []}}
    tl["scenes"][0]["docks"] = [B.dock_entry(aid, 0, DOCK_IN, DOCK_OUT, 0, arrive=arrive, mass="paper")]
    tl["scenes"][0]["world"] = dict(tl["scenes"][0]["world"], ken_burns={"scale": 0, "x": 0, "y": 0})
    tl["caption_pages"] = []; tl["captions"] = []
    tl["kinetics"] = {"stop_action": True, "analytic_spring": True, "area_squash": True}
    uris[aid] = B.dock_uri(_png(tmp_path / "card.png"))
    html = tmp_path / f"dock-{arrive or 'spring'}.html"
    html.write_text(RB.instantiate(tl, uris, TEMPLATE), encoding="utf-8")
    return html


class _Browser:
    """One playwright, one server for a directory, a prepared page per html (two sync playwrights in one thread throw)."""
    def __init__(self, directory: Path, aspect: str = "16:9"):
        from playwright.sync_api import sync_playwright
        self.w, self.h = RB.STAGE[aspect]
        self.srv, self.port = RB.serve(directory)
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)

    def open(self, html: Path):
        page = self.browser.new_context(viewport={"width": self.w, "height": self.h}).new_page()
        page.goto(f"http://127.0.0.1:{self.port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(page, self.w, self.h)
        return page

    @staticmethod
    def rect(page, sel: str, t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate("""sel => { const st = document.getElementById('stage').getBoundingClientRect();
            const e = document.querySelector(sel); if (!e) return null; const r = e.getBoundingClientRect();
            return { x: r.x - st.x, y: r.y - st.y, w: r.width, h: r.height, tf: e.style.transform, op: e.style.opacity }; }""", sel)

    def close(self):
        self.browser.close(); self.pw.stop(); self.srv.shutdown()


@needs_browser
def test_a_thrown_dock_is_off_its_spot_in_flight_and_lands_where_the_spring_would_have(tmp_path: Path):
    ha, hb = _dock_build(tmp_path, "throw"), _dock_build(tmp_path, None)
    BR = _Browser(tmp_path)
    try:
        pa, pb = BR.open(ha), BR.open(hb)
        P = type("R", (), {"rect": staticmethod(lambda sel, t: BR.rect(pa, sel, t))})
        Q = type("R", (), {"rect": staticmethod(lambda sel, t: BR.rect(pb, sel, t))})
        flight = P.rect("#dock-1", DOCK_IN + 0.15)
        assert flight and "translate(" in flight["tf"], flight
        landed = P.rect("#dock-1", DOCK_IN + 2.5)
        spring = Q.rect("#dock-1", DOCK_IN + 2.5)
        assert abs(flight["x"] - landed["x"]) > 150 or abs(flight["y"] - landed["y"]) > 60, "mid-flight the card is well off its spot"
        for k in ("x", "y", "w", "h"):
            assert abs(landed[k] - spring[k]) < 1.0, f"landed {k} {landed[k]:.2f} vs the spring's {spring[k]:.2f}: the throw lands where the pop would"
        impact = P.rect("#dock-1", DOCK_IN + 0.46)
        assert "matrix(" in impact["tf"], "the impact squashes (the tensor is on the transform right after the landing)"
        assert P.rect("#dock-1", DOCK_IN + 0.15) == flight, "a seek is the play"
    finally:
        BR.close()


@needs_browser
def test_a_landing_pill_lifts_before_it_drops_and_rests_where_the_pop_rests():
    tl, uris, _t, aspect = RB.load_surface("ledger-soak-page")
    sc = tl["scenes"][0]
    if not (sc["world"].get("page") or {}).get("badges"):
        pytest.skip("the soak golden carries no badges")
    base = dict(tl, caption_pages=[], captions=[], scenes=[dict(sc, world=dict(sc["world"], ken_burns={"scale": 0, "x": 0, "y": 0}))])
    landing = dict(base, kinetics={"stop_action": True}, scenes=[dict(base["scenes"][0], world=dict(base["scenes"][0]["world"], arrive="land", mass="metal"))])
    # the first pill's clock: tb = t - 7.4 (ROLL .7 + SAVOR .8 + FIELD 2.4 + PUNCH .5 + BUILD 3.0), at = LP_BADGE0 0.4 -> t0 = 7.8
    t0 = 7.8
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "land.html", Path(td) / "pop.html"
        a.write_text(RB.instantiate(landing, uris, TEMPLATE), encoding="utf-8")
        b.write_text(RB.instantiate(base, uris, TEMPLATE), encoding="utf-8")
        BR = _Browser(Path(td), aspect)
        try:
            pa, pb = BR.open(a), BR.open(b)
            P = type("R", (), {"rect": staticmethod(lambda sel, t: BR.rect(pa, sel, t))})
            Q = type("R", (), {"rect": staticmethod(lambda sel, t: BR.rect(pb, sel, t))})
            lift = P.rect(".lp-pill", t0 + 0.09)
            rest = P.rect(".lp-pill", t0 + 2.0)
            pop = Q.rect(".lp-pill", t0 + 2.0)
            assert lift and rest and pop
            assert lift["y"] < rest["y"] - 40, f"the pill LIFTS (y {lift['y']:.1f}) above its rest (y {rest['y']:.1f}) before it drops - weight before motion"
            assert abs(rest["x"] - pop["x"]) < 1.0 and abs(rest["y"] - pop["y"]) < 1.0, "it rests exactly where the pop rests"
            drop = P.rect(".lp-pill", t0 + 0.18 + 0.13)
            assert lift["y"] < drop["y"] <= rest["y"] + 0.5, "late in the drop it is nearly down"
        finally:
            BR.close()

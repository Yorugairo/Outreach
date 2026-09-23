"""REVIEW-P69-LANE-B-MERGE-3 - the long form's KEY RAIL (P69 T10), closed on its review's findings.

  M1  a `then=` recast keeps the page's key: the key the page opened with names lines that are gone. Now every state
      keys the names ITS end tags gave up (ledger_page.apply_longform_states keeps each state's `axes.key`), every key
      stands in ONE band over the chart (the page reserves the tallest, `axes.key_w` / `key_h`), and on the recast the
      old key LEAVES over the recast's own seconds while the new one springs in on the badge-ladder clock after that
      state's build. Body row 14's shape - a line recast to bars - and its reverse (bars recast to a keyed line).
  M2  the layout probe never saw the key: now each pill is page ink (`page.key`), a label among the page's labels
      (M28, role `key`) and type the floor reads; a card parked on the key is flagged by the motion gate.
  M3  the untested paths: a page that shortens its tags at `bravos` (the reviewer's lb3 shapes) and a key that WRAPS
      to two rows (the estimate is the engine's own box); the spiral and the melt carry the key; the caption band and
      the camera's glyph ceiling read it.
  L2  nothing checked the key lands inside its row: a four-pill key needs ~6.3 s after its build. The compiler now
      REFUSES a row too short to land its key, by name - the clock is the recipe's and is never shortened.

Fixtures are the longform suite's own SHAPES (test_longform_profile), and the reviewer's long-name shape.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import test_longform_profile as T  # noqa: E402
import gate_motion_density as MG  # noqa: E402
import probe as PR  # noqa: E402

B, G, RB, LPG = T.B, T.G, T.RB, T.LPG
MID = f"{T.OPT}:middle"
LINE_TO_BARS = "ledger:fx-lf-long:line;then=fx-lf-94:bars"   # body row 14's shape: a keyed line recast to bars
BARS_TO_LINE = "ledger:fx-lf-94:bars;then=fx-lf-long:line"   # ... and a bars page recast to a keyed line
RECAST_S = 1.5
# the reviewer's lb3_bravos shape: names long enough that even `bravos` shortens its tags, and a key that wraps
NAMES_LONG = ["MEMORY MAKERS AND EVERY SUPPLIER OF DRAM WORLDWIDE", "SEMICONDUCTOR EQUIPMENT AND FOUNDRY STOCKS",
              "MEGA-CAP TECHNOLOGY STOCKS OF THE UNITED STATES"]
LONGER = dict(copy.deepcopy(T.LONG), series=[dict(s, name=NAMES_LONG[i]) for i, s in enumerate(T.LONG["series"])])


def _compile(plate: str, tmp: Path, series: dict | None = None) -> dict:
    ep = T._episode(tmp)
    if series is not None:
        (ep / "evidence/objects/fx-lf-long.series.json").write_text(json.dumps(series), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = T.ASPECT
    try:
        world = B.world_for_plate(plate, (0, 0, 0), ep)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


def _scene(world: dict, species: list[dict], span=(0.0, None), exit_="cut") -> dict:
    return {"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": exit_,
            "span": [span[0], span[1] if span[1] is not None else G.RUNTIME], "docks": [], "species": species}


def _recast(at: float) -> dict:
    return {"kind": "chart_to", "to": "recast", "state": 1, "at": at, "dur": RECAST_S}


# ---- M1: the compiler keys every state, and the page reserves the band ----------------------------------------------

def test_a_line_state_keeps_its_own_key_and_the_page_reserves_its_band(tmp_path):
    world = _compile(BARS_TO_LINE + MID, tmp_path)
    page, state = world["page"], world["page_states"][0]
    assert "key" not in page["axes"], "the bars page keys nothing of its own"
    assert [k["name"] for k in state["axes"]["key"]] == [s["name"] for s in T.LONG["series"]], "the state keys ITS names"
    col = LPG._longform_ink_col()[1]
    assert page["axes"]["key_h"] >= LPG._longform_key_own(state, col)[1] - 0.1, "the page reserves the state's key band"
    assert LPG.page_boxes(page, T.ASPECT)[LPG.KEY_BOX]["h"] > 0, "the band is in page_boxes, so docks and stamps avoid it"


def test_a_keyed_line_recast_to_bars_keeps_its_key_and_the_bars_state_has_none(tmp_path):
    world = _compile(LINE_TO_BARS + MID, tmp_path)
    assert world["page"]["axes"]["key"] and "key" not in world["page_states"][0]["axes"]
    assert "key_h" not in world["page"]["axes"], "a page whose states key nothing more carries nothing new"


def test_without_the_option_a_then_page_carries_no_key_band(tmp_path):
    for row in (LINE_TO_BARS, BARS_TO_LINE):
        world = _compile(row, tmp_path / row.split(":")[1])
        for p in [world["page"]] + world["page_states"]:
            assert not {"key", "key_px", "key_w", "key_h"} & set(p.get("axes") or {}), p.get("axes")


# ---- L2: a row too short to land its key is refused by name ---------------------------------------------------------

def test_a_row_too_short_to_land_the_pages_key_is_refused_by_name(tmp_path):
    world = _compile("ledger:fx-lf-long:line" + MID, tmp_path)
    n = len(world["page"]["axes"]["key"])
    first, step = LPG.LONGFORM_KEY_CLOCK
    need = MG.PAGE_BUILD_END_S + first + step * (n - 1) + B.KEY_PILL_IN_S
    world["page"]["exit"] = "cut"
    short = _scene(world, [], (0.0, round(need - 0.5, 2)))
    err = B.page_key_span_error(short)
    assert err and "the page's key rail" in err and "never shortened" in err, err
    assert B.page_key_span_error(_scene(world, [], (0.0, round(need + 0.05, 2)))) is None
    with pytest.raises(ValueError, match="key rail"):
        B.validate_page_build_spans([short])


def test_a_recast_whose_key_cannot_land_is_refused_by_name(tmp_path):
    world = _compile(BARS_TO_LINE + MID, tmp_path)
    world["page"]["exit"] = "cut"
    n = len(world["page_states"][0]["axes"]["key"])
    first, step = LPG.LONGFORM_KEY_CLOCK
    land = 9.0 + RECAST_S + MG.LP_BUILD_S + first + step * (n - 1) + B.KEY_PILL_IN_S
    err = B.page_key_span_error(_scene(world, [_recast(9.0)], (0.0, round(land - 1.0, 2))))
    assert err and "state 2's key rail" in err, err
    assert B.page_key_span_error(_scene(world, [_recast(9.0)], (0.0, round(land + 0.05, 2)))) is None


def test_a_page_with_no_key_is_never_refused_for_one(tmp_path):
    world = _compile("ledger:fx-lf-94:bars" + MID, tmp_path)
    assert B.page_key_landings(_scene(world, [], (0.0, 3.0))) == []


# ---- the player -------------------------------------------------------------------------------------------------------

KEYS = """() => {
  const stage = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world')].find(e => e.__lp && e.classList.contains('ledger'));
  if (!w) return null;
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - stage.x, r.y - stage.y, r.width, r.height]; };
  return [...w.querySelectorAll('.lp-key')].map(k => [...k.querySelectorAll('.lp-kpill')].map(p => ({
    name: p.textContent, op: +getComputedStyle(p).opacity, box: R(p), tf: p.style.transform })));
}"""


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


class _Served:
    def __init__(self, browser, scenes: list[dict], tmp: Path, name: str):
        tl = G._timeline("REVIEW-P69-LANE-B-MERGE-3 " + name, scenes, {}, T.ASPECT)
        uris = dict(G._base_uris(), **B.longform_assets(tl))
        html = tmp / f"{name}.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.srv, port = RB.serve(html.parent)
        self.size = RB.STAGE[T.ASPECT]
        self.page = browser.new_context(viewport={"width": self.size[0], "height": self.size[1]}, device_scale_factor=1).new_page()
        self.errors: list[str] = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, *self.size)
        self.page.wait_for_function("document.fonts.status === 'loaded'")

    def at(self, t: float, js: str = KEYS, png: Path | None = None):
        RB.frame_png(self.page, t, self.size)
        self.page.wait_for_timeout(80)
        shot = RB.frame_png(self.page, t, self.size)
        if png:
            png.write_bytes(shot)
        return self.page.evaluate(js)

    def close(self):
        self.page.context.close()
        self.srv.shutdown()


FRAMES = Path(__import__("os").environ.get("P69_KEY_FRAMES") or Path(tempfile.gettempdir()) / "p69-key-rail-frames")   # the frames a reader looks at


@pytest.fixture(scope="module")
def browser():
    FRAMES.mkdir(parents=True, exist_ok=True)
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        yield br
        br.close()


def _up(pills) -> list[str]:
    return [p["name"] for p in pills if p["op"] > 0.95]


@needs_browser
def test_row_14_a_keyed_line_recast_to_bars_sends_its_key_away(browser, tmp_path):
    """Body row 14's shape: the line page's key is up; on the recast it leaves over the recast's seconds; the bars
    state has no key, so none is left naming lines that are gone."""
    world = _compile(LINE_TO_BARS + MID, tmp_path)
    s = _Served(browser, [_scene(world, [_recast(13.0)])], tmp_path, "line-to-bars")
    try:
        before = s.at(12.9, png=FRAMES / "m1-line-to-bars-before.png")
        mid = s.at(13.0 + 0.5 * RECAST_S, png=FRAMES / "m1-line-to-bars-mid.png")
        after = s.at(16.0, png=FRAMES / "m1-line-to-bars-after.png")
    finally:
        s.close()
    assert not s.errors, s.errors
    names = [x["name"] for x in T.LONG["series"]]
    assert len(before) == 1 and _up(before[0]) == names, before
    assert all(0.0 < p["op"] < 0.95 for p in mid[0]), ("the key leaves over the recast", mid)
    assert all(p["op"] == 0 for p in after[0]), ("gone once the page is bars", after)


@needs_browser
def test_a_bars_page_recast_to_a_keyed_line_springs_the_states_key_on_the_ladder(browser, tmp_path):
    world = _compile(BARS_TO_LINE + MID, tmp_path)
    s = _Served(browser, [_scene(world, [_recast(9.0)])], tmp_path, "bars-to-line")
    first, step = LPG.LONGFORM_KEY_CLOCK
    built = 9.0 + RECAST_S + MG.LP_BUILD_S
    try:
        before = s.at(8.9, png=FRAMES / "m1-bars-to-line-before.png")
        one = s.at(round(built + first + 0.4, 2))
        after = s.at(round(built + first + 2 * step + 0.6, 2), png=FRAMES / "m1-bars-to-line-after.png")
        dom = s.page.evaluate(PR.READ_DOM)
        import measure_page_boxes as MPB
        meas = s.page.evaluate(MPB.READ_BOXES)
    finally:
        s.close()
    inst = PR.derive(dom, 20.0, "", {}, T.ASPECT, {})
    assert not [o for o in inst["overlaps"] if "key:" in o["a"] + o["b"]], ("the key clears the STATE's top ink", inst["overlaps"])
    est = LPG.page_boxes(world["page"], T.ASPECT)[LPG.KEY_BOX]
    for d in ("y", "h"):
        assert abs(est[d] - meas["key"][d]) <= T.EST_TOL, (d, est, meas["key"])
    assert not s.errors, s.errors
    names = [x["name"] for x in T.LONG["series"]]
    assert len(before) == 1 and not _up(before[0]), ("no key before the line is on the page", before)
    assert _up(one[0]) == names[:1], ("the first pill springs FIRST_S after the state's build", one)
    assert _up(after[0]) == names, after
    tops = {round(p["box"][1]) for p in after[0]}
    assert len(tops) == 1, "one row, in the band the page reserved"


@needs_browser
def test_the_spiral_carries_the_key(browser, tmp_path):
    """The page declares no exit, so over its last 2 s it goes down the drain - the key's pills with it."""
    world = _compile("ledger:fx-lf-long:line" + MID, tmp_path)
    s = _Served(browser, [_scene(world, [], (0.0, 20.0)), _scene(_compile("ledger:fx-lf-94:bars" + MID, tmp_path / "b"), [], (20.0, None))],
                tmp_path, "spiral")
    try:
        home = s.at(17.8)
        drain = s.at(18.7, png=FRAMES / "m3-spiral-key.png")
    finally:
        s.close()
    assert not s.errors, s.errors
    assert _up(home[0]), home
    moved = [max(abs(a["box"][0] - b["box"][0]), abs(a["box"][1] - b["box"][1])) for a, b in zip(home[0], drain[0])]
    assert all(m > 20 for m in moved) and all("rotate" in p["tf"] or "matrix" in p["tf"] for p in drain[0]), (moved, drain)


MELT_JS = """() => ({ text: [...document.querySelectorAll('.melttext .lp-kpill')].map(p => getComputedStyle(p).visibility),
                      ink: [...document.querySelectorAll('.meltink .lp-kpill')].map(p => getComputedStyle(p).visibility) })"""


@needs_browser
def test_the_melt_carries_the_key_as_words(browser, tmp_path):
    """The melt splits the page into its marks, its words and its board: the key is WORDS - drawn by the text clone,
    never by the marks clone (melt.mjs MELT_CSS)."""
    world = _compile("ledger:fx-lf-long:line" + MID, tmp_path)
    world["page"]["exit"] = "cut"
    scenes = [_scene(world, [], (0.0, 15.0)),
              dict(_scene(_compile("ledger:fx-lf-94:bars" + MID, tmp_path / "b"), [], (15.0, None)), exit="melt")]
    s = _Served(browser, scenes, tmp_path, "melt")
    try:
        got = s.at(15.3, MELT_JS, png=FRAMES / "m3-melt-key.png")
    finally:
        s.close()
    assert not s.errors, s.errors
    assert got["text"] and all(v == "visible" for v in got["text"]), got
    assert got["ink"] and all(v == "hidden" for v in got["ink"]), got


# ---- M2: the probe sees the key; a card on it is flagged --------------------------------------------------------------

@needs_browser
def test_the_probe_reads_the_key_and_the_gate_flags_a_card_parked_on_it(browser, tmp_path):
    world = _compile("ledger:fx-lf-long:line" + MID, tmp_path)
    s = _Served(browser, [_scene(world, [])], tmp_path, "probe")
    try:
        dom = s.at(T.T_FRAME, PR.READ_DOM)
    finally:
        s.close()
    keys = [i for i in dom["items"] if i["k"] == "key"]
    assert len(keys) == len(world["page"]["axes"]["key"]), dom["items"]
    assert [l["text"] for l in dom["labels"] if l["role"] == "key"] == [k["name"] for k in world["page"]["axes"]["key"]]
    inst = PR.derive(dom, T.T_FRAME, "", {}, T.ASPECT, {})
    assert "key" in inst["page"] and any(x["k"] == "key" and x["px"] > 0 for x in inst["texts"]), inst["texts"]
    assert not [o for o in inst["overlaps"] if o["a"].startswith("key:") or o["b"].startswith("key:")], "M28 clean"
    kb = inst["page"]["key"]
    dom["docks"].append({"el": "card", "name": "card", "box": list(kb), "op": 1, "arriving": False, "paper": True})
    place = {"x": kb[0], "y": kb[1], "w": kb[2], "h": kb[3]}
    inst = PR.derive(dom, T.T_FRAME, "", {}, T.ASPECT, {"card": {"place": place}})
    assert any(o["a"] == "card" and o["b"] == "page.key" for o in inst["overlaps"]), inst["overlaps"]
    fails, _warns = MG._layout_faults({"instants": [inst], "aspect": T.ASPECT})
    assert any("the key rail under card" in f for f in fails), fails


# ---- M3: bravos keyed and a wrapping key; captions and the camera read it ---------------------------------------------

def test_bravos_shortens_the_long_names_and_their_key_wraps(tmp_path):
    page = _compile("ledger:fx-lf-long:line" + f"{T.OPT}:bravos", tmp_path, LONGER)["page"]
    ax = page["axes"]
    assert ax["tag_form"] != "full" and [k["name"] for k in ax["key"]] == NAMES_LONG, ax
    assert ax["key_px"] == pytest.approx(LPG.LONGFORM_KEY_MIN_PX), "the one row does not fit: the key sets at its floor"
    _w, h = LPG.longform_key_box(page, LPG._longform_ink_col()[1])
    em = LPG.LONGFORM_KEY_EM
    assert h == pytest.approx(2 * em["h"] * ax["key_px"] + em["row_gap"] * ax["key_px"]), "two rows"


@needs_browser
def test_a_wrapped_bravos_key_is_the_engines_box_and_clean(browser, tmp_path):
    import measure_page_boxes as MPB
    world = _compile("ledger:fx-lf-long:line" + f"{T.OPT}:bravos", tmp_path, LONGER)
    s = _Served(browser, [_scene(world, [])], tmp_path, "bravos")
    try:
        pills = s.at(T.T_FRAME, png=FRAMES / "m3-bravos-wrapped-key.png")
        meas = s.page.evaluate(MPB.READ_BOXES)
        dom = s.page.evaluate(PR.READ_DOM)
    finally:
        s.close()
    assert len({round(p["box"][1]) for p in pills[0]}) == 2, pills
    est = LPG.page_boxes(world["page"], T.ASPECT)[LPG.KEY_BOX]
    for d in ("x", "y", "w", "h"):
        assert abs(est[d] - meas["key"][d]) <= T.EST_TOL, (d, est, meas["key"])
    inst = PR.derive(dom, T.T_FRAME, "", {}, T.ASPECT, {})
    assert not [o for o in inst["overlaps"] if "key:" in o["a"] + o["b"]], inst["overlaps"]


def _meets(a: dict, b: dict) -> bool:
    return a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]


@pytest.mark.parametrize("preset", ["bravos", "middle"])
def test_the_caption_band_and_the_camera_read_the_key(preset, tmp_path):
    page = _compile("ledger:fx-lf-long:line" + f"{T.OPT}:{preset}", tmp_path, LONGER)["page"]
    key = LPG.page_boxes(page, T.ASPECT)[LPG.KEY_BOX]
    assert LPG.KEY_BOX in B.CAPTION_PAGE_INK_KEYS
    for cards in ([], [{"x": 1400, "y": 700, "w": 400, "h": 160}]):
        band = B.caption_band(page, T.ASPECT, cards)
        if band:
            strip = {"x": 0, "y": band["y"], "w": 1920, "h": band["h"]}
            assert not _meets(strip, key), (band, key)
    glyphs = B.page_glyph_boxes(page, T.ASPECT)
    assert glyphs.get(LPG.KEY_BOX) == key, "the camera's glyph ceiling carries the key"
    look = (key["x"] + key["w"] / 2, key["y"] + key["h"] + 40)
    _z, _el, _edge, table = B.page_zoom_ceiling(page, T.ASPECT, look)
    assert any(r["element"] == LPG.KEY_BOX and r["zoom"] < 50 for r in table), table

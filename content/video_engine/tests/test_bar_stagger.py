"""P69 T85 - a bars page with more than six bars FINISHES its build: the stagger scales to the bar count.

Row 22's finding (2026-09-24): the bars law grows bar i over `expoOut(clamp01((cb - i*0.1) / 0.55))` and fades its
name over `clamp01((cb - i*0.1 - 0.3) / 0.2)`, with the build's `cb` capped at 1. On the trim proof's eight bars the
build ENDED with bar 7's name at 0.5, bar 8's name at 0 ("Jul '26" never written) and bar 8 at ~97.7% of its height.

  (1) FINISHED   past its build, every bar of an n-bar page stands at scaleY(1), every name and every value at full
                 ink - for n from 7 to the page's cap (ledger_page.STORY_MAX_VALUES), 16:9 and 9:16
  (2) HELD       a page of six bars or fewer is the base's law to the byte: bar i at expoOut(clamp01((1 - i*0.1)/0.55))
  (3) ORDER      mid-build the bars still grow in reading order (bar i never ahead of bar i-1)
  (4) KIN        the same flaw in the bars' kin: a TIERS band of more than six bars finishes too, a membership
                 stack's tiles on the eighth bar land at full ink (their `ready` reads the same bars law), and a
                 stacked bar's parts and figures (lpSegPaint, P69 T64, mirrors each bar as drawn) stand whole

The combo's bars already step by `COMBO_BARS / nb` and are not touched. The browser half needs playwright + chromium.
"""
from __future__ import annotations

import copy
import json
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

LONG = ";readability=longform:middle"
T_DONE = 20.0     # well past any bars page's build on a page entered at 0 (the build runs ~4.4-7.4 s; a cascade after it)
T_MID = 5.2       # mid-build: the first bars grown, the last still growing
HELD_STEP = 0.1   # the base's step, kept to the byte through six bars

# the trim proof's eight bars (row 22, ev-trim-proof-v1 - the values copied here; the test reads no project file)
TRIM = [("Oct '24", -3.9, "crimson"), ("Dec '24", -12.4, "crimson"), ("Jan '25", -5.3, "crimson"),
        ("Feb '25", -10.5, "crimson"), ("Mar '25", -11.3, "crimson"), ("Jun '25", 10.9, "teal"),
        ("Jul '25", -8.7, "crimson"), ("Jul '26", -13.8, "crimson")]


def _bars_obj(n: int) -> dict:
    """An n-bar page: the trim proof's eight, or a SHAPE of n bars (never a figure about the world)."""
    if n == len(TRIM):
        bars = [{"label": lab, "value": v, "color": c, "note": f"{v:+.0f}%"} for lab, v, c in TRIM]
        return {"title": "If you're so bullish, why trim?", "sub": "The paper's move after each weak print",
                "src": "fixture - the trim proof's eight bars", "unit": "%", "domain": [-20, 20], "bars": bars}
    bars = [{"label": f"B{i + 1}", "value": 3 + (i * 7) % 11} for i in range(n)]
    return {"title": f"{n} bars", "sub": "a shape", "src": "fixture", "unit": "%", "bars": bars}


def _tiers_obj(n: int) -> dict:
    cats = [f"Q{i + 1}" for i in range(n)]

    def band(name: str, k: int) -> dict:
        return {"name": name, "unit": "%", "bars": [{"label": c, "value": 2 + (i * k) % 9} for i, c in enumerate(cats)]}
    return {"title": f"{n} bars a band", "sub": "a shape", "src": "fixture", "tiers": [band("One", 3), band("Two", 5)]}


def _stacked_obj() -> dict:
    o = _bars_obj(10)
    for b in o["bars"]:
        b["segments"] = [{"name": "Paid", "value": b["value"] - 1, "color": "teal"},
                         {"name": "Borrowed", "value": 1, "color": "crimson"}]
    return o


def _members_obj() -> dict:
    o = _bars_obj(8)
    o["member_noun"] = "stock"
    o["bars"][7]["members"] = [{"name": "SK hynix"}, {"name": "Micron"}]
    return o


def _world(oid: str, obj: dict, variant: str, tmp: Path, opt: str, aspect: str) -> dict:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        world = B.world_for_plate(f"ledger:{oid}:{variant}{opt}", (0, 0, 0), tmp)
        if aspect == "16:9":
            B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


# key -> (object, variant, row options, aspect)
CASES = {
    "bars-4": (_bars_obj(4), "bars", LONG, "16:9"),
    "bars-6": (_bars_obj(6), "bars", LONG, "16:9"),
    "bars-7": (_bars_obj(7), "bars", LONG, "16:9"),
    "trim-8": (_bars_obj(8), "bars", LONG, "16:9"),
    "trim-8-portrait": (_bars_obj(8), "bars", "", "9:16"),
    "bars-10": (_bars_obj(10), "bars", LONG, "16:9"),
    f"bars-{LPG.STORY_MAX_VALUES}": (_bars_obj(LPG.STORY_MAX_VALUES), "bars", LONG, "16:9"),
    "tiers-8": (_tiers_obj(8), "tiers", "", "16:9"),
    "members-8": (_members_obj(), "bars", LONG, "16:9"),
    "stacked-10": (_stacked_obj(), "bars", LONG, "16:9"),
}
FINISHED = [k for k in CASES if k.startswith(("bars-", "trim-")) and int(re.search(r"\d+", k).group()) > 6]

PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp;
  const k = (el) => { const m = /scaleY\\(([-\\d.e]+)\\)/.exec(el.style.transform || ''); return m ? +m[1] : null; };
  const op = (el) => (el ? +(el.getAttribute('opacity') ?? 1) : null);
  return {
    bars: (st.bars || []).map(b => ({ k: k(b.bar), lab: op(b.lab), val: op(b.val), name: b.lab ? b.lab.textContent : '' })),
    tiers: st.tiers ? st.tiers.bands.filter(bd => bd.bars.length).map(bd => bd.bars.map(bb => ({ k: k(bb.bar), val: op(bb.val) }))) : null,
    tiles: (st.memberTiles || []).map(r => ({ bar: r.bar, op: op(r.g) })),
    segs: st.segs ? { parts: st.segs.bars.map(b => b.segs.map(s => k(s.el))), figs: st.segs.figs.map(f => op(f.el)) } : null,
  };
}"""


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def painted(tmp_path_factory):
    """Each case served once and read past its build (T_DONE) and mid-build (T_MID)."""
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    from playwright.sync_api import sync_playwright

    tmp = tmp_path_factory.mktemp("stagger")
    out = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for key, (obj, variant, opt, aspect) in CASES.items():
                w, h = RB.STAGE[aspect]
                world = _world("fx-t85-" + key, copy.deepcopy(obj), variant, tmp / key, opt, aspect)
                scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
                           "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
                tl = G._timeline("P69 T85 " + key, scenes, {}, aspect)
                uris = G._base_uris()
                uris.update(B.longform_assets(tl))
                html = tmp / f"{key}.html"
                html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
                srv, port = RB.serve(html.parent)
                page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                errors: list[str] = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                try:
                    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(page, w, h)
                    page.wait_for_function("document.fonts.status === 'loaded'")
                    RB.frame_png(page, T_MID, (w, h))
                    mid = page.evaluate(PROBE)
                    RB.frame_png(page, T_DONE, (w, h))
                    out[key] = {"done": page.evaluate(PROBE), "mid": mid, "errors": errors}
                finally:
                    page.context.close()
                    srv.shutdown()
        finally:
            browser.close()
    return out


def _expo_out(x: float) -> float:
    return 1.0 if x >= 1 else 1 - math.pow(2, -10 * x)


def _clamp01(x: float) -> float:
    return min(1.0, max(0.0, x))


def test_the_page_raises_no_error(painted):
    for key, got in painted.items():
        assert got["errors"] == [], (key, got["errors"])
        assert got["done"] and got["done"]["bars"] or got["done"]["tiers"], key


@pytest.mark.parametrize("key", FINISHED)
def test_every_bar_name_and_value_of_a_page_past_six_bars_finishes(painted, key):
    bars = painted[key]["done"]["bars"]
    n = int(re.search(r"\d+", key).group())
    assert len(bars) == n, (key, len(bars))
    short = [(i, b["name"], b["k"], b["lab"], b["val"]) for i, b in enumerate(bars) if (b["k"], b["lab"], b["val"]) != (1, 1, 1)]
    assert short == [], f"{key}: bars not finished past the build (i, name, scaleY, name ink, value ink): {short}"


def test_the_trim_proof_writes_jul_25_whole_and_its_eighth_name(painted):
    for key in ("trim-8", "trim-8-portrait"):
        by = {b["name"]: b for b in painted[key]["done"]["bars"]}
        assert by["Jul '25"]["lab"] == 1 and by["Jul '25"]["k"] == 1, (key, by["Jul '25"])
        assert by["Jul '26"]["lab"] == 1 and by["Jul '26"]["k"] == 1 and by["Jul '26"]["val"] == 1, (key, by["Jul '26"])


@pytest.mark.parametrize("key", ["bars-4", "bars-6"])
def test_six_bars_or_fewer_keep_the_base_law_to_the_byte(painted, key):
    """The held pages: bar i stands at the base's own expoOut((1 - i * 0.1) / 0.55), written to four places, and its
    name at clamp01((1 - i * 0.1 - 0.3) / 0.2) - the sixth bar's 0.9982 included (their goldens stand)."""
    for i, b in enumerate(painted[key]["done"]["bars"]):
        assert f"{b['k']:.4f}" == f"{_expo_out(_clamp01((1 - i * HELD_STEP) / 0.55)):.4f}", (key, i, b)
        assert f"{b['lab']:.2f}" == f"{_clamp01((1 - i * HELD_STEP - 0.3) / 0.2):.2f}", (key, i, b)


@pytest.mark.parametrize("key", ["bars-6", "trim-8", f"bars-{LPG.STORY_MAX_VALUES}"])
def test_mid_build_the_bars_grow_in_reading_order(painted, key):
    ks = [b["k"] for b in painted[key]["mid"]["bars"]]
    assert ks[0] > 0 and ks[-1] < 1, (key, ks)
    assert all(a >= b for a, b in zip(ks, ks[1:])), (key, ks)


def test_a_tiers_band_past_six_bars_finishes(painted):
    bands = painted["tiers-8"]["done"]["tiers"]
    assert bands and all(len(bd) == 8 for bd in bands), bands
    short = [(bi, i, b) for bi, bd in enumerate(bands) for i, b in enumerate(bd) if (b["k"], b["val"]) != (1, 1)]
    assert short == [], f"tiers bars not finished (band, i, state): {short}"


def test_a_membership_stack_on_the_eighth_bar_lands_whole(painted):
    tiles = painted["members-8"]["done"]["tiles"]
    assert len(tiles) == 2 and all(r["bar"] == 7 for r in tiles), tiles
    assert all(r["op"] == 1 for r in tiles), tiles


def test_a_stacked_bar_past_six_bars_stands_whole_with_its_figures(painted):
    got = painted["stacked-10"]["done"]
    assert len(got["bars"]) == 10 and got["segs"], got["segs"]
    parts = [(bi, j, v) for bi, ps in enumerate(got["segs"]["parts"]) for j, v in enumerate(ps) if v != 1]
    assert parts == [], f"stack parts not at their bar's full height (bar, part, scaleY): {parts}"
    assert got["segs"]["figs"] and all(a == 1 for a in got["segs"]["figs"]), got["segs"]["figs"]

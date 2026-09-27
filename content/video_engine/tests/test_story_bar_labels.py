"""P71 T31 (was P69 T79; the Bravos harvest v2 S5, S6 and R2) - LABELS: the axis-less story page and its category pills,
logos as data labels, and the bar ladder that ends on a membership bar.

  (1) THE AXIS-LESS PAGE   a story bars page may be drawn with no axis (`axes: "none"` on the series file, S5 - BUB
                           0:48-1:36, HIS 11:04-11:16): no tick column, no gridlines, no framed plot, one zero rule under
                           the row. The written values state the scale, so it stays TRUE: the bars stand from zero in
                           true proportion and every value is written (the slice's hard rule)
  (2) THE CATEGORY PILL    a bar may carry `pill: true`: its own label is written in a capsule of the bar's own ink over
                           its stack (the value, the counting pill) - BUB's red pill over the value badge
  (3) REFUSED BY NAME      `axes` other than "none", off a story bars page, beside `left_gutter` (the slice's stop
                           condition: the pair) or any axis's key; a pill off an axis-less page, not `true`, on a bar
                           with no label; a logo that is not a catalogue id, off its page, on a panel's or a tier's bars
                           or lines, beside a projection, on a muted history (s106: a silent drop is neither advice nor
                           refusal - the base ACCEPTED AND IGNORED `axes: none` and a series `logo`)
  (4) LOGOS (S6)           a bar's `logo` is drawn UNDER it, the name kept (in its pill, or under the logo); a line
                           series' `logo` heads its end tag, the name kept in the long form's key rail (a page with no
                           key keeps it in the tag). A logo that is not an operator-approved, render-eligible catalogue
                           cutout is DROPPED with a WARN and the name stands (11-ARCHIVAL s4: "otherwise use text")
  (5) OFF                  a page naming none of it is the page it was: no key in the spec, no element in the chart
  (6) R2 + THE GOLDEN      `recipe:bar-ladder-to-membership` (candidate) and the golden `story-bars-pills` (H row 19's
                           two clocks, drawn axis-less with their pills)

The logo fixture is DRAWN BY THIS TEST (a disc on a transparent square, stdlib PNG) into a temporary catalogue - no logo
image is generated into or committed to the repo. The browser half needs playwright + chromium.
"""
from __future__ import annotations

import copy
import hashlib
import json
import struct
import sys
import tempfile
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CLOCKS_OBJ = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-two-clocks-bars-v1.series.json"
RECIPE = ROOT / "content/video_engine/effects/recipes/bar-ladder-to-membership.json"
LOGO_OK, LOGO_DRAFT, LOGO_ABSENT = "fx-logo-alpha", "fx-logo-draft", "fx-logo-nowhere"


def clocks() -> dict:
    """H row 19's committed two-clocks object, read in place (never re-typed): 1840s railways 20 years, compute 5."""
    obj = json.loads(CLOCKS_OBJ.read_text(encoding="utf-8"))
    assert [b["value"] for b in obj["bars"]] == [20, 5]
    return obj


def axisless(pills: bool = True, **bar_logos) -> dict:
    o = clocks()
    o["axes"] = "none"
    for b in o["bars"]:
        if pills:
            b["pill"] = True
    for j, logo in bar_logos.items():
        o["bars"][int(j[1:])]["logo"] = logo
    return o


LINES = {
    "title": "Two builders, one quarter", "sub": "Synthetic points for the logo fixture; not figures about the world",
    "src": "Synthetic - the label fixture", "unit": "",
    "series": [{"label": "+40%", "name": "ALPHA BUILDERS", "color": "teal",
                "pts": [[2025 + i / 20, round(100 * 1.4 ** (i / 19), 2)] for i in range(20)]},
               {"label": "+10%", "name": "BETA HOLDERS", "color": "crimson",
                "pts": [[2025 + i / 20, round(100 * 1.1 ** (i / 19), 2)] for i in range(20)]}],
}


def lines(logo0: str | None = LOGO_OK) -> dict:
    o = copy.deepcopy(LINES)
    if logo0:
        o["series"][0]["logo"] = logo0
    return o


# ---- the logo fixture: drawn here, catalogued in a temporary catalogue ------------------------------------------------

def _png(size: int = 64) -> bytes:
    """A deterministic RGBA disc on a transparent square - a stand-in mark the test draws, never a real logo."""
    c, r2 = (size - 1) / 2, (size * 0.42) ** 2
    rows = b"".join(b"\x00" + b"".join((b"\x2e\x9c\xf0\xff" if (x - c) ** 2 + (y - c) ** 2 <= r2 else b"\x00\x00\x00\x00")
                                        for x in range(size)) for y in range(size))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)  # noqa: E731
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def _catalogue(tmp: Path) -> Path:
    tmp.mkdir(parents=True, exist_ok=True)
    png = _png()
    (tmp / "fx-logo.png").write_bytes(png)
    sha = hashlib.sha256(png).hexdigest()
    entry = {"kind": "icon", "render_eligible": True, "review_state": "operator_approved", "path": "fx-logo.png", "sha256": sha}
    cat = {"project_root": str(tmp), "assets": [dict(entry, asset_id=LOGO_OK),
                                                dict(entry, asset_id=LOGO_DRAFT, review_state="draft")]}
    path = tmp / "catalogue.json"
    path.write_text(json.dumps(cat), encoding="utf-8")
    return path


@pytest.fixture
def catalogue(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "ICON_CATALOG", _catalogue(tmp_path / "icons"))
    monkeypatch.setattr(B, "_CATALOG_CACHE", None)
    return tmp_path


def _world(obj: dict, tmp: Path, variant: str = "bars", opt: str = "", aspect: str = "16:9", oid: str = "fx-labels") -> dict:
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


# ---- (1) (2) the field -----------------------------------------------------------------------------------------------

def test_an_axis_less_story_page_records_its_mode_and_its_pills():
    o = axisless()
    assert LPG.validate(o, "bars") == []
    spec = LPG.build_spec(o, "bars", 1, "right")
    assert spec["builder"] == "story"
    assert spec[LPG.AXES_MODE_KEY] == "none"
    assert spec[LPG.PILLS_KEY] == [True, True]
    assert LPG.LOGOS_KEY not in spec, "no bar names a logo: no list"
    assert spec["values"] == [20.0, 5.0] and spec["labels"] == ["1840s railways", "Today's compute"]


def test_a_bar_logo_rides_the_spec_by_bar_and_a_bar_without_one_is_null():
    spec = LPG.build_spec(axisless(b1=LOGO_OK), "bars", 1, "right")
    assert spec[LPG.LOGOS_KEY] == [None, LOGO_OK]


def test_a_page_naming_none_of_it_is_the_spec_it_was():
    spec = LPG.build_spec(clocks(), "bars", 1, "right")
    assert not {LPG.AXES_MODE_KEY, LPG.PILLS_KEY, LPG.LOGOS_KEY} & set(spec)
    line = LPG.build_spec(lines(None), "line", None, "right")
    assert all(LPG.LOGO_KEY not in s for s in line["series"])


def test_pill_and_logo_are_bar_fields_and_the_series_logo_is_carried():
    assert LPG.PILL_KEY in LPG.BAR_FIELDS and LPG.LOGO_KEY in LPG.BAR_FIELDS
    assert LPG.validate(lines(), "line") == []
    assert LPG.build_spec(lines(), "line", None, "right")["series"][0][LPG.LOGO_KEY] == LOGO_OK


# ---- (3) refused by name ---------------------------------------------------------------------------------------------

def _pilled_panel() -> dict:
    return {"title": "Two panels", "src": "Synthetic", "panels": [
        {"sub": "a", "builder": "bars", "unit": "%", "bars": [{"label": "A", "value": 1, "pill": True}, {"label": "B", "value": 2}]},
        {"sub": "b", "series": [{"name": "x", "pts": [[2020, 1], [2021, 2]]}]}]}


@pytest.mark.parametrize("patch,variant,pattern", [
    (lambda o: o.update(axes="off"), "bars", r"axes 'off': a series file's `axes` is \"none\""),
    (lambda o: o.update(left_gutter=120), "bars", r"axes: none beside left_gutter"),
    (lambda o: o.update(overflow="burst", domain=[0, 10]), "bars", r"axes: none beside domain, overflow"),
    (lambda o: o.update(ylabel="years"), "bars", r"axes: none beside ylabel"),
    (lambda o: o.update(log=True), "bars", r"axes: none beside log"),
    (lambda o: o["bars"][0].update(pill="yes"), "bars", r"bars\[0\]: pill 'yes' - `pill: true`"),
    (lambda o: o["bars"][0].update(label=""), "bars", r"bars\[0\]: a pill writes the bar's label"),
    (lambda o: o["bars"][1].update(logo="Micron Logo.png"), "bars", r"bars\[1\]: logo 'Micron Logo.png' is not a catalogue id"),
    (lambda o: o["bars"][1].update(logo=LOGO_OK), "progress", r"bars\[1\]: a logo labels a STORY bars page's bar"),
])
def test_an_axis_less_page_refuses_what_it_cannot_draw_by_name(patch, variant, pattern):
    o = axisless()
    patch(o)
    errs = LPG.validate(o, variant)
    assert any(__import__("re").search(pattern, e) for e in errs), errs


def test_the_axis_less_mode_is_a_story_bars_pages():
    o = lines(None)
    o["axes"] = "none"
    assert any("axes: none is a STORY bars page's" in e for e in LPG.validate(o, "line"))


def test_a_pill_is_the_axis_less_pages():
    o = clocks()
    o["bars"][0]["pill"] = True
    assert any("a category pill names a bar on an AXIS-LESS page" in e for e in LPG.validate(o, "bars"))


def test_a_bar_logo_on_a_page_with_axes_is_drawn_and_needs_a_name():
    o = clocks()
    o["bars"][1]["logo"] = LOGO_OK
    assert LPG.validate(o, "bars") == [], "a logo under a bar is S6's, on any story page"
    o["bars"][1]["label"] = " "
    assert any("a logo labels a NAMED bar" in e for e in LPG.validate(o, "bars"))


def test_a_panels_pill_is_refused_by_name():
    errs = LPG.validate(_pilled_panel(), "line")
    assert any("panels[0] bars[0]: pill" in e and "not built on a panel or a tier" in e for e in errs), errs


@pytest.mark.parametrize("patch,variant,pattern", [
    (lambda o: o["series"][0].update(logo="alpha.svg"), "line", r"series\[0\]: logo 'alpha.svg' is not a catalogue id"),
    (lambda o: o["series"][0].update(projection={"label": "2027E", "tier": "PLAUSIBLE", "src": "x"}), "line",
     r"series\[0\]: a logo beside `projection`"),
    (lambda o: o["series"][0].update(muted=True), "line", r"series\[0\]: a logo on a muted history"),
    (lambda o: o["series"][0].update(name="", label=""), "line", r"series\[0\]: a logo labels a NAMED series"),
    (lambda o: None, "race", r"series\[0\]: a series logo labels a LINE's end"),
])
def test_a_series_logo_is_refused_by_name_where_it_cannot_label_a_line_end(patch, variant, pattern):
    o = lines()
    patch(o)
    errs = LPG.validate(o, variant)
    assert any(__import__("re").search(pattern, e) for e in errs), errs


def test_a_panels_series_logo_is_refused_by_name():
    o = _pilled_panel()
    o["panels"][0]["bars"][0].pop("pill")
    o["panels"][1]["series"][0]["logo"] = LOGO_OK
    assert any("panels[1] series[0]: logo" in e for e in LPG.validate(o, "line"))


# ---- (4) the key and the tag's room ------------------------------------------------------------------------------------

def test_a_logo_series_is_keyed_at_every_tag_form_and_its_tag_counts_the_mark():
    spec = LPG.build_spec(dict(lines(), readability="longform"), "line", None, "right")
    assert spec["axes"]["readability"] == "longform"
    key = [k["name"] for k in spec["axes"].get("key") or []]
    assert "ALPHA BUILDERS" in key, "the logo took the tag's name: the key carries it"
    plain = LPG.build_spec(dict(lines(None), readability="longform"), "line", None, "right")
    assert (plain["axes"].get("key") is None) == (plain["axes"]["tag_form"] == "full"), "no logo: the key law it was"
    t = LPG.longform_type(spec)
    for form in LPG.LONGFORM_TAG_FORMS:
        a = LPG.longform_tag_px({"series": [lines()["series"][0]]}, t, form)
        assert a == pytest.approx(len("+40%") * LPG.LONGFORM_TAG_EM["name"] * t["tag"]
                                  + (LPG.LABEL_LOGO_TAG_EM + LPG.LABEL_LOGO_TAG_GAP_EM) * t["tag"]), form


# ---- (4) the compiler: the catalogue's permission, or the name ---------------------------------------------------------

def test_a_catalogued_bar_logo_rides_the_asset_map(catalogue):
    world = _world(axisless(b1=LOGO_OK), catalogue / "ep")
    assert world["page"][LPG.LOGOS_KEY] == [None, LOGO_OK] and "warnings" not in world["page"]
    uris = B.label_logo_assets({"scenes": [{"world": world}]})
    assert list(uris) == [B.PROP_PREFIX + LOGO_OK]
    assert uris[B.PROP_PREFIX + LOGO_OK] == B.catalogue_icon_uri(LOGO_OK), "the file on disk, byte for byte"


@pytest.mark.parametrize("logo", [LOGO_DRAFT, LOGO_ABSENT])
def test_a_bar_logo_without_the_catalogues_permission_is_dropped_and_the_name_kept(catalogue, logo):
    world = _world(axisless(b1=logo), catalogue / "ep")
    assert LPG.LOGOS_KEY not in world["page"], "every bar logo dropped: no list"
    warns = [w for w in world["page"]["warnings"] if w.startswith("WARN label:")]
    assert len(warns) == 1 and logo in warns[0] and "Today's compute" in warns[0] and "keeps its NAME" in warns[0], warns
    assert B.label_logo_assets({"scenes": [{"world": world}]}) == {}


def test_a_series_logo_is_resolved_the_same_way_and_dropped_on_a_portrait_page(catalogue):
    ok = _world(lines(), catalogue / "a", variant="line")
    assert ok["page"]["series"][0][LPG.LOGO_KEY] == LOGO_OK
    assert list(B.label_logo_assets({"scenes": [{"world": ok}]})) == [B.PROP_PREFIX + LOGO_OK]
    bad = _world(lines(LOGO_DRAFT), catalogue / "b", variant="line")
    assert LPG.LOGO_KEY not in bad["page"]["series"][0]
    assert any("'ALPHA BUILDERS' (series 0)" in w for w in bad["page"]["warnings"])
    tall = _world(lines(), catalogue / "c", variant="line", aspect="9:16")
    assert LPG.LOGO_KEY not in tall["page"]["series"][0]
    assert any("portrait's end tag keeps the name" in w for w in tall["page"]["warnings"])


def test_a_page_with_no_logo_carries_no_label_asset_and_no_warning(catalogue):
    world = _world(clocks(), catalogue / "ep")
    assert not {LPG.AXES_MODE_KEY, LPG.PILLS_KEY, LPG.LOGOS_KEY, "warnings"} & set(world["page"])
    assert B.label_logo_assets({"scenes": [{"world": world}]}) == {}


# ---- (5) the player ----------------------------------------------------------------------------------------------------

PROBE = """() => {
  const w = [...document.querySelectorAll('.world')].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp.states ? w.__lp.states[w.__lp.active | 0] : w.__lp;
  const op = (el) => { if (!el) return null; if (getComputedStyle(el).display === 'none') return 0; const a = el.getAttribute('opacity'); return a == null || a === '' ? 1 : +a; };
  const bb = (el) => { try { const r = el.getBBox(); return [r.x, r.y, r.width, r.height]; } catch (e) { return null; } };
  const at = (el) => ['x', 'y', 'width', 'height'].map(k => +el.getAttribute(k));
  const cp = st.callout ? st.callout.querySelector('rect.cpill') : null;
  return {
    grids: st.chart.querySelectorAll('line.grid').length, axes: [...st.chart.querySelectorAll('line.ax')].map(at => +at.getAttribute('y1')),
    ylabels: (st.marks || []).filter(m => m.role === 'ylabel').length, lfPanel: !!st.lfPanel, noAxis: st.noAxis || null,
    pillFit: st.pillFit || null, follow: (st.labelFollow || []).length, catpills: st.chart.querySelectorAll('.lp-catpill').length,
    base: st.scale && st.scale.my ? st.scale.my(0) : null,
    bars: (st.bars || []).map(b => ({ i: b.i, x: +b.bar.getAttribute('x'), y: +b.bar.getAttribute('y'), w: +b.bar.getAttribute('width'),
      h: +b.bar.getAttribute('height'), fill: getComputedStyle(b.bar).fill, tf: b.bar.style.transform,
      val: { text: b.val.textContent, op: op(b.val), box: bb(b.val) },
      lab: { text: b.lab.__wrapText ? b.lab.__wrapText.join(' ') : b.lab.textContent, op: op(b.lab), box: bb(b.lab), fill: getComputedStyle(b.lab).fill },
      pill: b.pill ? { box: at(b.pill), op: op(b.pill), fill: getComputedStyle(b.pill).fill } : null })),
    callout: cp ? { box: at(cp), op: op(st.callout) } : null,
    logos: [...st.chart.querySelectorAll('image.lp-label-logo')].map(im => ({ box: at(im), op: op(im), tag: im.classList.contains('lp-tag-logo'),
      href: (im.getAttribute('href') || '').slice(0, 22) })),
    names: (st.paths || []).filter(pp => !pp.muted).map(pp => ({ si: pp.si, text: pp.name.textContent, x: +pp.name.getAttribute('x'),
      y: +pp.name.getAttribute('y'), op: op(pp.name), box: bb(pp.name) })),
    key: [...w.querySelectorAll('.lp-key .lp-kpill')].map(p => p.textContent),
  };
}"""

T_MID, T_REST = 5.45, 10.0   # the page's build (4.4 s of roll, savor, field and punch, then LP.BUILD 3 s): bar 0's name a quarter in at 5.45; every mark landed by 10.0
LF = ";readability=longform"
CASES = {   # key -> (object, variant, row options, aspect, emphasise)
    "pills": (lambda: axisless(), "bars", LF, "16:9"),
    "pills-short": (lambda: axisless(), "bars", "", "16:9"),
    "pills-portrait": (lambda: axisless(), "bars", "", "9:16"),
    "pills-logo": (lambda: axisless(b1=LOGO_OK), "bars", LF, "16:9"),
    "axes-logo": (lambda: dict(clocks(), bars=[dict(b, logo=LOGO_OK) if j == 1 else b for j, b in enumerate(clocks()["bars"])]), "bars", LF, "16:9"),
    "draft-logo": (lambda: axisless(b1=LOGO_DRAFT), "bars", LF, "16:9"),
    "plain": (lambda: clocks(), "bars", LF, "16:9"),
    "line-logo-lf": (lambda: lines(), "line", LF, "16:9"),
    "line-logo": (lambda: lines(), "line", "", "16:9"),
    "line-plain": (lambda: lines(None), "line", "", "16:9"),
}


@pytest.fixture(scope="module")
def painted(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("labels")
    mp = pytest.MonkeyPatch()
    mp.setattr(B, "ICON_CATALOG", _catalogue(tmp / "icons"))
    mp.setattr(B, "_CATALOG_CACHE", None)
    out = {}
    try:
        for key, (make, variant, opt, aspect) in CASES.items():
            world = _world(make(), tmp / key, variant=variant, opt=opt, aspect=aspect)
            scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
                       "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
            tl = G._timeline("P71 T31 " + key, scenes, {}, aspect)
            uris = dict(G._base_uris(), **B.longform_assets(tl), **B.label_logo_assets(tl))
            html = tmp / key / "page.html"
            html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
            w, h = RB.STAGE[aspect]
            with SP.served(html, w, h) as (page, errs):
                page.wait_for_function("document.fonts.status === 'loaded'")
                got = {"errors": errs, "page": world["page"], "at": {}}
                for t in (T_MID, T_REST):
                    RB.frame_png(page, t, (w, h))
                    got["at"][t] = page.evaluate(PROBE)
                out[key] = got
    finally:
        mp.undo()
    return out


def _inside(a, b, tol=1.0) -> bool:
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[0] + a[2] <= b[0] + b[2] + tol and a[1] + a[3] <= b[1] + b[3] + tol


def _meets(a, b) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


@pytest.mark.parametrize("key", ["pills", "pills-short", "pills-portrait"])
def test_the_axis_less_page_draws_no_axis_and_one_zero_rule(painted, key):
    p = painted[key]["at"][T_REST]
    assert painted[key]["errors"] == []
    assert p["grids"] == 0 and p["ylabels"] == 0 and not p["lfPanel"], "no gridline, no tick label, no framed plot"
    assert len(p["axes"]) == 1 and p["axes"][0] == pytest.approx(p["base"], abs=0.2), "one rule, at zero"


@pytest.mark.parametrize("key", ["pills", "pills-short", "pills-portrait"])
def test_its_bars_stand_from_zero_in_true_proportion_and_every_value_is_written(painted, key):
    p = painted[key]["at"][T_REST]
    rail, compute = p["bars"]
    assert rail["y"] + rail["h"] == pytest.approx(p["base"], abs=0.2) and compute["y"] + compute["h"] == pytest.approx(p["base"], abs=0.2)
    assert rail["h"] / compute["h"] == pytest.approx(20 / 5, rel=0.01), "twenty against five, drawn four to one"
    assert p["noAxis"] == {"restored": 0}
    written = [b["val"]["text"] for b in p["bars"] if b["val"]["op"] > 0.99]
    assert "20 years" in written, "the railways' twenty"
    assert "5 years" in written or (p["callout"] and p["callout"]["op"] > 0.99), "compute's five: its value, or its counting pill"


@pytest.mark.parametrize("key", ["pills", "pills-short", "pills-portrait"])
def test_each_pill_names_its_bar_in_its_ink_over_its_stack(painted, key):
    p = painted[key]["at"][T_REST]
    assert p["catpills"] == 2 and p["pillFit"] == []
    for b in p["bars"]:
        pill, lab = b["pill"], b["lab"]
        assert pill["op"] == 1 and lab["op"] == 1
        assert pill["fill"] == b["fill"], "the pill wears its bar's own ink"
        assert _inside(lab["box"], pill["box"]), (lab, pill)
        cx = pill["box"][0] + pill["box"][2] / 2
        assert cx == pytest.approx(b["x"] + b["w"] / 2, abs=0.6), "centred on its bar"
        stack = [b["y"]] + ([b["val"]["box"][1]] if b["val"]["op"] > 0.99 else [])
        if b["i"] == 1 and p["callout"]:
            stack.append(p["callout"]["box"][1])
        assert pill["box"][1] + pill["box"][3] <= min(stack) + 0.5, "OVER its bar's stack (the value, the counting pill)"
        assert pill["box"][1] >= 0, "on the chart"
        assert lab["fill"] != pill["fill"], "the name reads on the pill"
    a, c = (b["pill"]["box"] for b in p["bars"])
    assert not _meets(a, c)


def test_a_pill_arrives_with_its_name(painted):
    p = painted["pills"]["at"][T_MID]
    for b in p["bars"]:
        assert b["pill"]["op"] == pytest.approx(b["lab"]["op"], abs=0.005)
    assert any(0 < b["lab"]["op"] < 1 for b in p["bars"]), "mid-build: a name still arriving"


def test_a_bar_logo_stands_under_its_bar_and_the_name_is_kept(painted):
    pl, ax = painted["pills-logo"]["at"][T_REST], painted["axes-logo"]["at"][T_REST]
    for p in (pl, ax):
        (logo,) = p["logos"]
        compute = p["bars"][1]
        assert logo["op"] == 1 and logo["href"].startswith("data:image/png"), logo
        assert logo["box"][0] + logo["box"][2] / 2 == pytest.approx(compute["x"] + compute["w"] / 2, abs=0.6)
        assert logo["box"][1] >= p["base"], "under the floor"
        assert logo["box"][2] == logo["box"][3] > 0, "a square mark"
    pilled = pl["bars"][1]
    assert _inside(pilled["lab"]["box"], pilled["pill"]["box"]), "the pilled bar's name stays in its pill, over the bar"
    assert pilled["lab"]["box"][1] < pl["logos"][0]["box"][1]
    lab = ax["bars"][1]["lab"]
    assert lab["op"] == 1 and lab["text"] == "Today's compute"
    assert lab["box"][1] >= ax["logos"][0]["box"][1] + ax["logos"][0]["box"][3] - 0.5, "the name written UNDER its logo"


def test_a_logo_without_permission_draws_nothing_and_the_name_stands(painted):
    p = painted["draft-logo"]["at"][T_REST]
    assert p["logos"] == [] and p["bars"][1]["lab"]["text"] == "Today's compute" and p["bars"][1]["lab"]["op"] == 1


def test_a_series_logo_heads_its_end_tag_and_the_key_keeps_its_name(painted):
    lf = painted["line-logo-lf"]["at"][T_REST]
    (logo,) = lf["logos"]
    alpha = next(n for n in lf["names"] if n["si"] == 0)
    assert logo["tag"] and logo["op"] == alpha["op"] > 0.9, (logo, alpha)
    assert alpha["text"] == "+40%", "the tag writes the label; the name is in the key"
    assert "ALPHA BUILDERS" in lf["key"]
    assert logo["box"][0] + logo["box"][2] <= alpha["box"][0] + 0.5, "the mark heads the tag"
    mid = alpha["box"][1] + alpha["box"][3] / 2
    assert logo["box"][1] <= mid <= logo["box"][1] + logo["box"][3], "on the tag's line"
    short = painted["line-logo"]["at"][T_REST]
    (logo2,) = short["logos"]
    alpha2 = next(n for n in short["names"] if n["si"] == 0)
    assert "ALPHA BUILDERS" in alpha2["text"], "no key rail: the tag keeps the name beside the mark"
    assert logo2["box"][0] + logo2["box"][2] <= alpha2["box"][0] + 0.5


def test_a_tag_logo_arrives_with_its_tag(painted):
    p = painted["line-logo-lf"]["at"][T_MID]
    alpha = next(n for n in p["names"] if n["si"] == 0)
    assert p["logos"][0]["op"] == pytest.approx(alpha["op"], abs=0.005)


@pytest.mark.parametrize("key", ["plain", "line-plain"])
def test_a_page_naming_none_draws_no_label_element(painted, key):
    p = painted[key]["at"][T_REST]
    assert p["catpills"] == 0 and p["logos"] == [] and p["follow"] == 0 and p["noAxis"] is None and p["pillFit"] is None
    assert painted[key]["errors"] == []


# ---- (6) the recipe and the golden -------------------------------------------------------------------------------------

def test_the_ladder_recipe_is_a_candidate_with_its_use_when():
    r = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert r["id"] == "recipe:bar-ladder-to-membership" and r["status"] == "candidate"
    uw = r["use_when"]
    assert "then vs now" in json.dumps(uw) and "tiles carry values" in json.dumps(uw)
    cards = [m.get("card") for m in r["members"]]
    assert "page_builder:bars" in cards and "page_species:member" in cards


def test_the_golden_is_h_row_19s_two_clocks_drawn_axis_less_with_pills():
    assert "story-bars-pills" in G.SURFACES and "story-bars-pills" in G.FRAME_T
    tl, _ = G.SURFACES["story-bars-pills"]()
    page = tl["scenes"][0]["world"]["page"]
    assert page[LPG.AXES_MODE_KEY] == "none" and page[LPG.PILLS_KEY] == [True, True]
    assert page["values"] == [20.0, 5.0] and page["axes"]["readability"] == "longform"


def test_the_engine_names_its_dials_once_and_mirrors_the_compilers():
    import re
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LP_LABEL = Object\.freeze\(\{(.*?)\}\);", src, re.S)
    assert m, "the engine carries the LP_LABEL dial block"
    dials = dict(re.findall(r"([A-Z_]+): ([\d.]+)", m.group(1)))
    assert float(dials["TAG_EM"]) == LPG.LABEL_LOGO_TAG_EM and float(dials["TAG_GAP_EM"]) == LPG.LABEL_LOGO_TAG_GAP_EM
    assert float(dials["LOGO_PX"]) >= 48, "over the membership tile's LOGO_MIN_PX: a smaller cutout reads as a smudge"

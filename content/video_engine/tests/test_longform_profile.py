"""P69 T8 (E99 s97) - THE `longform` PAGE PROFILE, part 1 of 3: the page itself, in three type presets.

The operator (E99 s97): "go much more tighter in [Bravos's] direction ... the chart style in long format is
sharper, more electric, and more professional." The profile is MEASURED (`docs/research/bravos-style/
BRAVOS-LONGFORM-CHART-SPEC.md`, section (b)) and it is a ROW OPTION, `;readability=longform[:bravos|middle|phone]`,
legal on a dense-line page and on a bars (`story`) page. Under it:
  - the ground is flat `#14181E` with no vignette (the spec's t530 read), overriding E22's cream rim, charcoal
    page and deckle ONLY under the option;
  - the plot sits on a lighter panel `#222830` inside a 1.5 px `#696D73` border (t530);
  - no gridline is painted; a 3 px `#675C66` zero rule only when the data crosses zero (t1078);
  - the page's sans text is INTER, loaded from the tracked `Inter-Variable.ttf` (R26-259: the template named
    Inter and never loaded it); the title is Inter Bold in the spec's `#DB8497`; the source is dim `#868A8F`;
    the tick labels take the spec's `#9A9DA2`.
THE SCALE IS THE OPERATOR'S (P69-HG3): E99 s90's phone type and E99 s97's Bravos type conflict, so the type is one of
three named presets (`ledger_page.LONGFORM_TYPE_SCALE`, px as rendered at 1920) - and at EVERY preset the page holds:
the sub never meets the y label or the plot (M28's half-figure of air), every end tag stands inside the stage (a tag
that will not fit is shortened to its value; the long name waits for T10's key), the source stays on the stage.
Absent the option every page is byte-identical: the world a row compiles and the frame it paints.

The fixtures are INLINE: the two H bars objects are the copies `test_compare_on_bars` already carries; the line, the
long-named lines and the zero-crossing bars are synthetic SHAPES (never a figure about the world). The browser half
needs playwright + chromium and is skipped without them.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402
from test_compare_on_bars import OBJ_20, OBJ_94  # noqa: E402

ASPECT = "16:9"
T_FRAME = 14.0                      # every page has built and settled (the build runs 4.4-7.4 s on a page entered at 0)
OPT = ";readability=longform"
PRESETS = LPG.LONGFORM_PRESETS
PHONE_W = 390                       # E99 s90's phone: a 16:9 frame played across a 390-px-wide phone
PHONE_FLOOR = 12.0                  # E99 s90 / T17: "roughly 12.5 px" - the T17 gate's own bar (test_fed_chart_readability)
SIZE_TOL = 0.6                      # rendered px: a size is the preset's to within rounding
SPEC = {"ground": (20, 24, 30), "panel": "rgb(34, 40, 48)", "border": "rgb(105, 109, 115)", "border_px": 1.5,
        "zero": "rgb(103, 92, 102)", "zero_px": 3.0, "tick": "rgb(154, 157, 162)", "title": "rgb(219, 132, 151)",
        "source": "rgb(134, 138, 143)"}
FACE = "Inter Longform"

# SHAPES, not figures: a dense line with one short label, four long-named lines keyed by inline badges (the
# divergence page's shape), and a bars row that crosses zero
LINE = {"title": "Shape of a line", "sub": "Synthetic points for the profile's fixture",
        "src": "Synthetic - the longform fixture", "unit": "",
        "series": [{"label": "741", "color": "crimson",
                    "pts": [[2000 + i / 4, round(1000 + 900 * (i / 39) - 700 * max(0, (i - 26) / 13), 1)]
                            for i in range(40)]}],
        "xticks": [[2001, "2001"], [2004, "2004"], [2007, "2007"]]}
LONG = {"title": "Four long names at the ends of four lines, a title long enough to wrap at the largest type",
        "sub": "Synthetic points for the profile's fixture, a subtitle long enough to wrap onto a second line at the "
               "largest of the three presets",
        "src": "Synthetic - the longform fixture, a source line long enough to wrap at the largest preset of the three",
        "unit": "", "ylabel": "index, synthetic, log scale", "log": True,
        "series": [{"label": f"+{v}%", "name": n, "color": c,
                    "pts": [[2025 + i / 40, round(100 * (1 + v / 100) ** (i / 39), 2)] for i in range(40)]}
                   for v, n, c in ((613, "MEMORY MAKERS (the long name)", "crimson"),
                                   (105, "SEMICONDUCTOR STOCKS", "teal"),
                                   (21, "MEGA-CAP TECH STOCKS", "cobalt"))],
        "badges": [{"label": "MEMORY", "value": "", "tag": "our layer", "accent": "coral"},
                   {"label": "SEMIS", "value": "", "tag": "their divergence", "accent": "teal"},
                   {"label": "MEGA", "value": "", "tag": "matches the market", "accent": "cobalt"}],
        "xticks": [[2025.2, "Mar"], [2025.5, "Jul"], [2025.8, "Oct"]]}
CROSS = {"title": "Shape across zero", "sub": "Synthetic bars that cross zero",
         "src": "Synthetic - the longform fixture", "unit": "%",
         "bars": [{"label": "A", "value": -12}, {"label": "B", "value": 8}, {"label": "C", "value": 15}]}
# REVIEW-P69-LANE-B-MERGE-2 N1: the long page with one badge that keys no line - it goes to the KEY RAIL, as a pill
# under the source (the review's `long2`: at `phone` that pill stood on the source's second line)
RAIL = dict(copy.deepcopy(LONG), badges=LONG["badges"] + [{"label": "KEY", "value": "1", "tag": "", "accent": "sunflower"}])
# P69 T10 (E99 s84): the long page plus a FOURTH line that names itself by its label alone - its end tag loses nothing
# when the others are shortened, so it is the one the key may add to land on an even pill count (4, not 3)
EVEN = dict(copy.deepcopy(LONG), series=LONG["series"] + [
    {"label": "BASELINE", "color": "deemph", "pts": [[2025 + i / 40, 100.0] for i in range(40)]}])
PAGES = {  # name -> (object id, object, variant)
    "94": ("fx-lf-94", OBJ_94, "bars"),
    "halving": ("fx-lf-halving", OBJ_20, "bars"),
    "line": ("fx-lf-line", LINE, "line"),
    "long": ("fx-lf-long", LONG, "line"),
    "cross": ("fx-lf-cross", CROSS, "bars"),
    "rail": ("fx-lf-rail", RAIL, "line"),
    "even": ("fx-lf-even", EVEN, "line"),
}
# N1: the anchored caption's strip - `full_stage_bands`' bottom band begins at its top, and the one-line caption's own
# box ends at its foot (CAPTION_ANCHOR, 878-960 on the 1920 x 1080 stage). The source and the key rail never meet it.
STRIP = (LPG._full_stage_bands(1920, 1080)["bottom"]["y"], LPG.CAPTION_ANCHOR[ASPECT][1] + LPG.CAPTION_ANCHOR[ASPECT][3])
EST_TOL = 2.0   # N3: the estimate's page is the engine's to the full-stage fixture's own 2 px (test_full_stage_page_is_measured.TOL)
# THE PINS - measured at lane B's HEAD 9ffbf60 before this slice, with no option on the row: sha256 of the
# world each row compiles (json, sorted keys) and of the 94 page's frame at T_FRAME (RGB bytes, the golden
# harness's own fresh-browser render). A page that names no profile must compile and paint exactly these.
WORLD_PINS = {
    "94": "f1120a6e935d44831dc47dbbeb32ef2f3c8731c8071fbc190539813d684af35f",
    "halving": "16d1c46dbd12e707d9ccd42867e9afec0cd10d160b91c42068a8ae716f46559f",
    "line": "a4bc296c71783adb5b4b9f6bb7f70dd32d47927e7c6a11056829d4095214ff66",
    "cross": "a4cb3f567a0756c03a81b37c4c2c8d063d36ed252f98fbfed99f206d4d738459",
}
FRAME_94_PIN = "85dc693d401c0cec269e9422911d2afc3276d582ccf0964695788f3532c48921"


def _episode(tmp: Path) -> Path:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    for oid, obj, _variant in PAGES.values():
        (tmp / f"evidence/objects/{oid}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    return tmp


def _world(name: str, tmp: Path, opt: str = "", series: dict | None = None) -> dict:
    """The world the compiler builds for this fixture's row at 16:9 (stamped full-stage, as every 16:9 page is)."""
    oid, obj, variant = PAGES[name]
    ep = _episode(tmp)
    if series is not None:
        (ep / f"evidence/objects/{oid}.series.json").write_text(json.dumps(series), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        world = B.world_for_plate(f"ledger:{oid}:{variant}{opt}", (0, 0, 0), ep)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


def _world_sha(world: dict) -> str:
    return hashlib.sha256(json.dumps(world, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _timeline(world: dict) -> tuple[dict, dict]:
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
    tl = G._timeline("P69 T8 longform", scenes, {}, ASPECT)
    uris = G._base_uris()
    uris.update(B.longform_assets(tl))
    return tl, uris


# ---- the source and the row (no browser) --------------------------------------------------------------------

def test_the_three_presets_are_named_and_stated_in_rendered_px():
    """The table the operator rules on at P69-HG3: three presets, every role sized, `middle` the working default."""
    assert PRESETS == ("bravos", "middle", "phone") and LPG.LONGFORM_DEFAULT_PRESET == "middle"
    roles = {"title", "sub", "tick", "tag", "chip", "value", "src"}
    for preset in PRESETS:
        assert set(LPG.LONGFORM_TYPE_SCALE[preset]) == roles, preset
    ts = LPG.LONGFORM_TYPE_SCALE
    assert ts["middle"] == {"title": 44.0, "sub": 26.0, "tick": 26.0, "tag": 30.0, "chip": 24.0, "value": 34.0, "src": 20.0}
    assert abs(ts["bravos"]["tick"] * 0.727 - 16.5) < 0.1 and abs(ts["bravos"]["title"] * 0.727 - 28) < 0.1, "the spec's digit and cap heights"
    assert abs(ts["phone"]["tick"] - 46 * 1.334) < 0.1 and abs(ts["phone"]["title"] - 52 * LPG.PUNCH_SCALE) < 0.1, "T17's own render"
    assert ts["bravos"]["tick"] < ts["middle"]["tick"] < ts["phone"]["tick"]
    assert LPG.parse_readability("longform") == ("longform", "middle")
    assert LPG.parse_readability("longform:bravos") == ("longform", "bravos")
    assert LPG.parse_readability("landscape-phone") == ("landscape-phone", None)
    assert LPG.parse_readability("longform:huge") is None and LPG.parse_readability("landscape-phone:middle") is None


def test_longform_is_a_closed_profile_legal_on_dense_line_and_bars():
    for obj, variant in ((LINE, "line"), (OBJ_94, "bars")):
        row = dict(copy.deepcopy(obj), readability="longform")
        assert LPG.validate(row, variant) == [], (variant, LPG.validate(row, variant))
        axes = LPG.build_spec(row, variant)["axes"]
        assert axes["readability"] == "longform" and axes["type_scale"] == "middle"
    race = {"title": "t", "src": "s", "periods": ["2024", "2025"],
            "series": [{"label": "A", "values": [1, 2]}, {"label": "B", "values": [2, 1]}], "readability": "longform"}
    errs = LPG.validate(race, "race")
    assert any("longform" in e and "'race'" in e for e in errs), errs


@pytest.mark.parametrize("preset", PRESETS)
@pytest.mark.parametrize("name", sorted(PAGES))
def test_every_page_compiles_under_every_preset(name, preset, tmp_path):
    """No refusal at any preset (the parent, 2026-09-23): the page carries its preset, and a line page the tag form
    that keeps its end tags on the stage."""
    world = _world(name, tmp_path, f"{OPT}:{preset}")
    axes = world["page"]["axes"]
    assert axes["readability"] == "longform" and axes["type_scale"] == preset
    if world["page"]["builder"] == "dense-line":
        assert axes["tag_form"] in LPG.LONGFORM_TAG_FORMS
    else:
        assert "tag_form" not in axes


def test_a_long_end_name_gives_up_its_name_before_the_page_is_refused(tmp_path):
    """The long-named lines keep every name at the smallest preset and shorten them at the larger ones - to the value
    and its chip, then the value alone; the names stay in the spec for T10's key."""
    forms = {p: _world("long", tmp_path / p, f"{OPT}:{p}")["page"]["axes"]["tag_form"] for p in PRESETS}
    order = LPG.LONGFORM_TAG_FORMS
    assert order.index(forms["bravos"]) <= order.index(forms["middle"]) <= order.index(forms["phone"]), forms
    assert forms["phone"] != "full", forms
    page = _world("long", tmp_path / "names", f"{OPT}:phone")["page"]
    assert [s.get("name") for s in page["series"]] == [s["name"] for s in LONG["series"]], "the names are kept for the key"


def test_the_row_option_opts_a_bars_page_in_without_editing_the_object(tmp_path):
    world = _world("94", tmp_path, OPT)
    assert world["page"]["builder"] == "story"
    assert world["page"]["axes"]["readability"] == "longform" and world["page"]["axes"]["type_scale"] == "middle"
    assert "readability" not in json.loads((tmp_path / "evidence/objects/fx-lf-94.series.json").read_text(encoding="utf-8"))


def test_the_row_option_opts_a_dense_line_page_in(tmp_path):
    world = _world("line", tmp_path, OPT)
    assert world["page"]["builder"] == "dense-line"
    assert world["page"]["axes"]["readability"] == "longform"


def test_the_row_option_wins_over_the_series_field(tmp_path):
    phone = dict(copy.deepcopy(LINE), readability="landscape-phone")
    assert _world("line", tmp_path, "", series=phone)["page"]["axes"]["readability"] == "landscape-phone"
    assert _world("line", tmp_path, OPT + ":bravos", series=phone)["page"]["axes"]["type_scale"] == "bravos"
    long_row = dict(copy.deepcopy(LINE), readability="longform:phone")
    back = _world("line", tmp_path, ";readability=landscape-phone", series=long_row)["page"]["axes"]
    assert back["readability"] == "landscape-phone" and "type_scale" not in back and "tag_form" not in back


def test_an_unknown_profile_or_preset_and_another_builder_are_refused_by_name(tmp_path):
    with pytest.raises(ValueError, match="landscape-phone|longform"):
        _world("94", tmp_path, ";readability=bravos")
    with pytest.raises(ValueError, match="bravos\\|middle\\|phone"):
        _world("94", tmp_path, OPT + ":huge")
    fall = {"title": "Shape falling", "sub": "Synthetic start and end", "src": "Synthetic - the longform fixture",
            "unit": "%", "bars": [{"label": "Then", "value": 40}, {"label": "Now", "value": 12}]}
    ep = _episode(tmp_path)
    (ep / "evidence/objects/fx-lf-fall.series.json").write_text(json.dumps(fall), encoding="utf-8")
    assert B.world_for_plate("ledger:fx-lf-fall:decline", (0, 0, 0), ep)["page"]["builder"] == "decline"
    with pytest.raises(ValueError, match=r"longform.*'decline'"):
        B.world_for_plate(f"ledger:fx-lf-fall:decline{OPT}", (0, 0, 0), ep)


def test_without_the_option_every_world_is_byte_identical(tmp_path):
    got = {name: _world_sha(_world(name, tmp_path / name)) for name in WORLD_PINS}
    assert got == WORLD_PINS
    # the long-named fixture was added with the presets (no HEAD pin): its no-option world carries no trace of them
    for name in ("long",):
        axes = _world(name, tmp_path / ("bare-" + name))["page"].get("axes") or {}
        assert not {"readability", "type_scale", "tag_form"} & set(axes), axes


def test_the_inter_face_rides_the_asset_map_only_when_a_page_asks(tmp_path):
    off, _ = _timeline(_world("94", tmp_path / "off"))
    assert B.longform_assets(off) == {}
    on, uris = _timeline(_world("94", tmp_path / "on", OPT))
    assets = B.longform_assets(on)
    assert list(assets) == [B.LONGFORM_FONT_ASSET]
    head, data = assets[B.LONGFORM_FONT_ASSET].split(",", 1)
    assert head == "data:font/ttf;base64"
    assert base64.b64decode(data) == (ROOT / "content/video_engine/src/assets/fonts/Inter-Variable.ttf").read_bytes()


# ---- REVIEW-P69-LANE-B-MERGE-2 (no browser) ----------------------------------------------------------------------
# N2: a `then=` state is drawn in the page's own chart box, viewBox and preset type, so ITS end tags are fitted too -
# against the viewBox the page opened (a line page's is already narrowed to the page's own tags).

THEN_ROWS = {   # the first page -> the state it becomes: bars -> the long line (the review's row), a short line -> it
    "bars-to-line": "ledger:fx-lf-94:bars;then=fx-lf-long:line",
    "line-to-line": "ledger:fx-lf-line:line;then=fx-lf-long:line",
}


def _then_world(row: str, tmp: Path, preset: str | None, aspect: str = ASPECT) -> dict:
    ep = _episode(tmp)
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        world = B.world_for_plate(row + (f"{OPT}:{preset}" if preset else ""), (0, 0, 0), ep)
        if aspect == ASPECT:
            B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


@pytest.mark.parametrize("preset", PRESETS)
@pytest.mark.parametrize("row", sorted(THEN_ROWS))
def test_every_then_state_carries_the_profile_and_its_own_fitted_tag_form(row, preset, tmp_path):
    """The state takes the page's profile and preset and the fullest end-tag form that fits the stage on its OWN
    tags; and the viewBox the page opens (the one the state is drawn in) leaves that form its room - on a line page
    by `axes.tag_room`, the widest tag a state writes, when it is wider than the page's own."""
    world = _then_world(THEN_ROWS[row], tmp_path, preset)
    page, state = world["page"], world["page_states"][0]
    axes = state["axes"]
    assert axes["readability"] == "longform" and axes["type_scale"] == preset, axes
    assert axes["tag_form"] == LPG.longform_tag_form(state, preset), axes
    t, scale = LPG.LONGFORM_TYPE_SCALE[preset], LPG.longform_scale0()
    room = LPG.longform_page_vw(page)   # the viewBox the state is drawn in
    assert LPG._longform_max_vw(LPG.longform_tag_units(state, t, axes["tag_form"], scale), scale) >= room - 1e-6, (
        f"{row} {preset}: the state's {axes['tag_form']!r} tags do not fit the page's {room:.1f}-unit viewBox")
    if page["builder"] == "dense-line":
        assert page["axes"].get("tag_room") == pytest.approx(LPG.longform_tag_px(state, t, axes["tag_form"]), abs=0.1), page["axes"]


def test_without_the_option_a_then_state_is_untouched(tmp_path):
    for row in THEN_ROWS.values():
        state = _then_world(row, tmp_path / row.split(":")[1], None)["page_states"][0]
        assert not {"readability", "type_scale", "tag_form"} & set(state.get("axes") or {}), state.get("axes")


# N3: the estimate wraps the page ink at the face's own advances - the table is the tracked font's, re-read here

def test_the_advance_table_is_the_tracked_inters_own():
    instancer = pytest.importorskip("fontTools.varLib.instancer")
    from fontTools.ttLib import TTFont
    font = ROOT / "content/video_engine/src/assets/fonts/Inter-Variable.ttf"
    for (weight, opsz), want in LPG.LONGFORM_ADVANCES.items():
        inst = instancer.instantiateVariableFont(TTFont(font), {"wght": weight, "opsz": opsz})
        cmap, hmtx = inst.getBestCmap(), inst["hmtx"]
        assert tuple(hmtx[cmap[ord(c)]][0] for c in LPG.LONGFORM_ADV_CHARS) == want, (weight, opsz)
    mid = instancer.instantiateVariableFont(TTFont(font), {"wght": 400, "opsz": 22.41})   # middle's sub: 26 / 1.16
    cmap, hmtx = mid.getBestCmap(), mid["hmtx"]
    for c in "aMW 0%":
        got = LPG.longform_text_px(c, "sub", 26.0) * LPG.LONGFORM_ADV_UPM / 26.0
        assert abs(got - hmtx[cmap[ord(c)]][0]) <= 0.5, (c, got, hmtx[cmap[ord(c)]][0])


# N4: the long form is a 16:9 page profile - the engine never draws it in portrait, so a 9:16 row naming it is refused
# by name, and a 9:16 build never carries the face.

def test_a_portrait_row_naming_the_long_form_is_refused_by_name(tmp_path):
    ep = _episode(tmp_path)
    saved = B.ASPECT
    B.ASPECT = "9:16"
    try:
        with pytest.raises(ValueError, match=r"longform.*16:9"):
            B.world_for_plate(f"ledger:fx-lf-94:bars{OPT}:middle", (0, 0, 0), ep)
        with pytest.raises(ValueError, match=r"longform.*16:9"):
            B.world_for_plate(f"ledger:fx-lf-line:line{OPT}", (0, 0, 0), ep)
    finally:
        B.ASPECT = saved


def test_a_portrait_build_never_carries_the_face(tmp_path):
    world = _world("94", tmp_path, OPT)   # a series file's own long form reaches a 9:16 timeline the same way
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
    assert B.longform_assets(G._timeline("portrait", scenes, {}, "9:16")) == {}
    assert list(B.longform_assets(G._timeline("landscape", scenes, {}, ASPECT))) == [B.LONGFORM_FONT_ASSET]


# N6: a longform page with no face renders in Arial - so a 16:9 timeline that draws one is never instantiated without it

def test_a_longform_page_is_never_instantiated_without_its_face(tmp_path):
    tl, uris = _timeline(_world("94", tmp_path, OPT))
    bare = {k: v for k, v in uris.items() if k != B.LONGFORM_FONT_ASSET}
    with pytest.raises(ValueError, match="font:inter-longform"):
        RB.instantiate(tl, bare)
    assert RB.instantiate(tl, uris), "with the face, the page"
    off, off_uris = _timeline(_world("94", tmp_path / "off"))
    assert RB.instantiate(off, off_uris), "a page with no profile needs no face"


# ---- the browser: the page as the player paints it ------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

# Everything in RENDERED stage px. `sizes` are font sizes (the page ink through the punch, the chart's through its
# screen CTM); `checks` are the three collision reads.
PROBE = """(face) => {
  const stage = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world')].find(e => e.__lp && e.classList.contains('ledger'));
  if (!w) return null;
  const st = w.__lp, page = st.page, chart = st.chart;
  const R = (e) => { const r = e.getBoundingClientRect(); return {x: r.left - stage.left, y: r.top - stage.top, w: r.width, h: r.height}; };
  const painted = (e) => { const c = getComputedStyle(e); if (c.display === 'none' || c.visibility === 'hidden') return false;
    for (let n = e; n && n !== page; n = n.parentElement) if (+getComputedStyle(n).opacity === 0) return false;
    if (e.getAttribute('opacity') === '0') return false;
    const r = e.getBoundingClientRect(); return r.width > 0.1 || r.height > 0.1; };
  const m = chart.getScreenCTM(), k = Math.hypot(m.a, m.b);            /* one chart unit in stage px, this frame */
  const ps = page.getBoundingClientRect().width / page.offsetWidth;    /* the punch on the page's own ink */
  const fs = (e) => parseFloat(getComputedStyle(e).fontSize);
  const texts = [...chart.querySelectorAll('text')].filter(painted);
  const svgText = texts.map(e => ({ text: e.textContent, cls: e.getAttribute('class'), px: fs(e) * k, fill: getComputedStyle(e).fill, rect: R(e) }));
  const ink = ['.lp-title', '.lp-sub', '.lp-src'].map(s => page.querySelector(s)).filter(e => e && e.textContent.trim()).map(e => ({
    text: e.textContent, cls: e.className, px: fs(e) * ps, rect: R(e),
    color: getComputedStyle(e).color, family: getComputedStyle(e).fontFamily, weight: getComputedStyle(e).fontWeight }));
  const panel = chart.querySelector('rect.lp-panel');
  const ticks = (st.marks || []).filter(mk => mk.role === 'ylabel' && mk.el && painted(mk.el)).map(mk => ({
    text: mk.el.textContent, px: fs(mk.el) * k, fill: getComputedStyle(mk.el).fill }));
  const tags = [...chart.querySelectorAll('text.sname')].filter(painted);
  const chips = [...chart.querySelectorAll('tspan.tagchip')].filter(e => e.textContent.trim());
  const one = (sel) => { const e = page.querySelector(sel); return e && e.textContent.trim() ? e : null; };
  const title = one('.lp-title'), sub = one('.lp-sub'), src = one('.lp-src');
  const ylab = (st.marks || []).find(mk => mk.role === 'axislabel' && mk.el && painted(mk.el));
  const tickPx = ticks.length ? Math.max(...ticks.map(t => t.px)) : 0;
  const subBottom = sub ? R(sub).y + R(sub).h : (title ? R(title).y + R(title).h : 0);
  const inStage = (r) => r.x >= -0.5 && r.y >= -0.5 && r.x + r.w <= stage.width + 0.5 && r.y + r.h <= stage.height + 0.5;
  return {
    profile: page.classList.contains('lp-readability-longform'),
    ground: getComputedStyle(page).backgroundColor,
    boardShown: ['.lp-field', '.lp-grain', '.lp-edge'].filter(s => { const e = page.querySelector(s); return e && getComputedStyle(e).display !== 'none'; }),
    panel: panel ? { fill: getComputedStyle(panel).fill, stroke: getComputedStyle(panel).stroke,
                     px: parseFloat(getComputedStyle(panel).strokeWidth) * k, first: panel === chart.querySelector('rect, line, path, text') } : null,
    grids: [...chart.querySelectorAll('line.grid')].filter(painted).length,
    axes: [...chart.querySelectorAll('line.ax')].filter(painted).map(e => ({ stroke: getComputedStyle(e).stroke,
      px: parseFloat(getComputedStyle(e).strokeWidth) * k })),
    fontLoaded: document.fonts.check('700 44px "' + face + '"') && document.fonts.check('400 26px "' + face + '"'),
    ticks, svgText, ink, minPhone: Math.min(...svgText.map(t => t.px * 390 / stage.width), ...ink.map(t => t.px * 390 / stage.width)),
    sizes: { title: title ? fs(title) * ps : null, sub: sub ? fs(sub) * ps : null, src: src ? fs(src) * ps : null,
             tick: tickPx || null, tag: tags.length ? Math.max(...tags.map(e => fs(e) * k)) : null,
             chip: chips.length ? Math.max(...chips.map(e => fs(e) * k)) : null },
    checks: { air: 0.5 * tickPx, subBottom,
              ylabelTop: ylab ? R(ylab.el).y : null, plotTop: panel ? R(panel).y : null,
              tagsOut: [...tags, ...chips].map(R).filter(r => !inStage(r)),
              textOut: svgText.filter(t => !inStage(t.rect)).map(t => t.text),
              source: src ? R(src) : null, sourceIn: src ? inStage(R(src)) : true,
              pills: [...page.querySelectorAll('.lp-rail .lp-pill')].map(R) },
    /* P69 T10: the KEY RAIL - its box, and each pill's name, dot colour, box and opacity; the line each series drew
       (its computed stroke) so a dot can be held to its line's own colour; the title's box */
    key: (() => { const k = page.querySelector('.lp-key'); return k ? R(k) : null; })(),
    keyPills: [...page.querySelectorAll('.lp-key .lp-kpill')].map(e => ({ name: (e.querySelector('.lp-kname') || e).textContent,
      dot: e.querySelector('.lp-kdot') ? getComputedStyle(e.querySelector('.lp-kdot')).backgroundColor : null,
      rect: R(e), opacity: +getComputedStyle(e).opacity, px: fs(e.querySelector('.lp-kname') || e) * ps })),
    lineCols: Object.fromEntries((st.marks || []).filter(mk => mk.role === 'line' && mk.el && !/:h/.test(mk.key))
      .map(mk => [mk.key.replace(/^s/, '').replace(/#.*$/, ''), getComputedStyle(mk.el).stroke])),
    titleRect: title ? R(title) : null,
    /* P69 T9 (3): every x label (a line page's ticks, a bars page's names) against the panel's foot */
    panelFoot: panel ? R(panel).y + R(panel).h : null,
    xlabs: (st.marks || []).filter(mk => (mk.role === 'xtick' || mk.role === 'xlabel') && mk.el && painted(mk.el)).map(mk => ({ text: mk.el.textContent, rect: R(mk.el) })),
    ylabelRect: ylab ? R(ylab.el) : null,
  };
}"""

CASES = [(name, preset) for name in sorted(PAGES) for preset in PRESETS]


@pytest.fixture(scope="module")
def painted(tmp_path_factory):
    """Every fixture page at every preset (and the 94 OFF), probed at T_FRAME from one warm browser."""
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import measure_page_boxes as MPB

    tmp = tmp_path_factory.mktemp("longform")
    out = {}
    w, h = RB.STAGE[ASPECT]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for name, preset in CASES + [("94", None)]:
                key = f"{name}-{preset or 'off'}"
                world = _world(name, tmp / key, f"{OPT}:{preset}" if preset else "")
                tl, uris = _timeline(world)
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
                    RB.frame_png(page, T_FRAME, (w, h))          # the first seek builds the page ...
                    page.wait_for_timeout(120)
                    png = RB.frame_png(page, T_FRAME, (w, h))    # ... and the second reads it settled
                    out[key] = {"probe": page.evaluate(PROBE, FACE), "img": Image.open(io.BytesIO(png)).convert("RGB"),
                                "errors": errors, "page": world["page"],
                                "boxes": page.evaluate(MPB.READ_BOXES)}   # N3: the fixture tool's own read
                finally:
                    page.context.close()
                    srv.shutdown()
        finally:
            browser.close()
    return out


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_the_ground_is_flat_and_the_board_is_gone(painted, name, preset):
    got = painted[f"{name}-{preset}"]
    assert not got["errors"], got["errors"]
    p = got["probe"]
    assert p["profile"], "the page carries the profile's class"
    assert p["ground"] == "rgb(20, 24, 30)", p["ground"]
    assert p["boardShown"] == [], f"E22's field, grain and deckle edge are hidden under the option: {p['boardShown']}"
    img = got["img"]
    for xy in [(4, 4), (1915, 4), (4, 1075), (1915, 1075), (4, 540), (1915, 300)]:   # no vignette
        assert all(abs(a - b) <= 1 for a, b in zip(img.getpixel(xy), SPEC["ground"])), (xy, img.getpixel(xy))


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_the_plot_is_a_framed_panel_with_no_gridlines(painted, name, preset):
    p = painted[f"{name}-{preset}"]["probe"]
    assert p["panel"] is not None, "the plot panel is drawn"
    assert p["panel"]["fill"] == SPEC["panel"] and p["panel"]["stroke"] == SPEC["border"], p["panel"]
    assert p["panel"]["px"] == pytest.approx(SPEC["border_px"], abs=0.05), p["panel"]
    assert p["panel"]["first"], "the panel is the chart's ground: drawn before every mark"
    assert p["grids"] == 0, f"{p['grids']} gridline(s) painted"


@needs_browser
@pytest.mark.parametrize("preset", PRESETS)
def test_a_zero_rule_only_when_the_data_crosses_zero(painted, preset):
    for name in ("94", "halving", "line", "long"):
        assert painted[f"{name}-{preset}"]["probe"]["axes"] == [], (name, painted[f"{name}-{preset}"]["probe"]["axes"])
    rules = painted[f"cross-{preset}"]["probe"]["axes"]
    assert len(rules) == 1, rules
    assert rules[0]["stroke"] == SPEC["zero"] and rules[0]["px"] == pytest.approx(SPEC["zero_px"], abs=0.05), rules


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_inter_is_loaded_and_the_title_ticks_and_source_take_the_spec_colours(painted, name, preset):
    p = painted[f"{name}-{preset}"]["probe"]
    assert p["fontLoaded"], f"{FACE} is loaded from the tracked Inter-Variable.ttf"
    title, src = p["ink"][0], p["ink"][-1]
    assert "lp-title" in title["cls"] and "lp-src" in src["cls"]
    for ink in p["ink"]:
        assert ink["family"].split(",")[0].strip().strip('"') == FACE, ink
    assert title["weight"] == "700" and title["color"] == SPEC["title"], title
    assert src["color"] == SPEC["source"], src
    assert p["ticks"] and all(tk["fill"] == SPEC["tick"] for tk in p["ticks"]), p["ticks"]


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_the_type_is_the_presets_as_rendered(painted, name, preset):
    """Every role the page writes measures its preset's rendered px (the page ink through the punch, the chart's
    through its own scale - which the layout may have shrunk, so the chart's units grow to keep the px)."""
    want, got = LPG.LONGFORM_TYPE_SCALE[preset], painted[f"{name}-{preset}"]["probe"]["sizes"]
    for role in ("title", "sub", "src", "tick", "tag", "chip"):
        if got[role] is None:
            continue
        assert got[role] == pytest.approx(want[role], abs=SIZE_TOL), (role, got[role], want[role])
    if PAGES[name][2] == "line":
        assert got["tag"] is not None, "a line page writes its end tags"


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_nothing_collides_at_any_preset(painted, name, preset):
    """The three reads (the parent, 2026-09-23): the sub's last line stands half a tick figure (M28's air) clear of
    the y label and of the plot; every end tag, and every word the chart writes, is inside the stage; so is the
    source line, wrapped if it must be.
    ... and REVIEW-P69-LANE-B-MERGE-2 N1's two: the source never meets the anchored caption's strip (STRIP), and a key
    rail's pill never meets the source or the strip (at `phone` the source ran 28 px into it and a pill stood on it)."""
    c = painted[f"{name}-{preset}"]["probe"]["checks"]
    assert c["plotTop"] is not None and c["plotTop"] - c["subBottom"] >= c["air"] - 0.5, c
    if c["ylabelTop"] is not None:
        assert c["ylabelTop"] - c["subBottom"] >= c["air"] - 0.5, c
    assert c["tagsOut"] == [], f"end tags off the stage: {c['tagsOut']}"
    assert c["textOut"] == [], f"chart words off the stage: {c['textOut']}"
    assert c["sourceIn"], f"the source leaves the stage: {c['source']}"
    s = c["source"]
    assert s is None or not _meets_strip(s), f"the source runs into the caption strip {STRIP}: {s}"
    for pill in c["pills"]:
        assert not _meets_strip(pill), f"a key pill stands in the caption strip {STRIP}: {pill}"
        assert s is None or not _overlaps(pill, s), f"a key pill stands on the source: {pill} / {s}"
        assert pill["x"] >= -0.5 and pill["y"] + pill["h"] <= 1080.5, f"a key pill leaves the stage: {pill}"
    if name == "rail":
        assert c["pills"], "the rail fixture's badge is drawn as a pill"


def _meets_strip(r: dict) -> bool:
    return r["h"] > 0 and r["y"] < STRIP[1] - 0.5 and r["y"] + r["h"] > STRIP[0] + 0.5


def _overlaps(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["w"] - 0.5 and b["x"] < a["x"] + a["w"] - 0.5
            and a["y"] < b["y"] + b["h"] - 0.5 and b["y"] < a["y"] + a["h"] - 0.5)


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_the_estimate_is_the_engines_page_at_every_preset(painted, name, preset):
    """REVIEW-P69-LANE-B-MERGE-2 N3: `_longform_full_boxes` - the boxes M28 and the stamp fits read for a page the
    fixture never measured - is the page the engine lays out, to EST_TOL, at every preset (the long page at `phone`
    was 73 px off). The title, sub, chart and source to the pixel budget; the rail's top (its width is the column it
    may fill, never less than the pills it holds); the plot to the budget on a line page, and on a bars page a box
    that holds every bar the engine drew (its bars are the data's own height, the estimate is the panel)."""
    got = painted[f"{name}-{preset}"]
    est = LPG._longform_full_boxes(got["page"], 1920, 1080)
    meas = got["boxes"]
    for key in ("title", "sub", "chart", "source"):
        for d in ("x", "y", "w", "h"):
            assert abs(est[key][d] - meas[key][d]) <= EST_TOL, (key, d, est[key], meas[key])
    assert abs(est["rail"]["y"] - meas["rail"]["y"]) <= EST_TOL, (est["rail"], meas["rail"])
    assert est["rail"]["w"] >= meas["rail"]["w"] - EST_TOL, (est["rail"], meas["rail"])
    if meas["rail"]["h"] > 0:
        assert abs(est["rail"]["h"] - meas["rail"]["h"]) <= EST_TOL, (est["rail"], meas["rail"])
    p, m = est["plot"], meas["plot"]
    if got["page"]["builder"] == "dense-line":
        assert all(abs(p[d] - m[d]) <= EST_TOL for d in ("x", "y", "w", "h")), (p, m)
    else:
        assert (p["x"] <= m["x"] + EST_TOL and p["y"] <= m["y"] + EST_TOL and p["x"] + p["w"] >= m["x"] + m["w"] - EST_TOL
                and p["y"] + p["h"] >= m["y"] + m["h"] - EST_TOL), (p, m)


@needs_browser
@pytest.mark.parametrize("name", sorted(PAGES))
def test_the_phone_preset_holds_the_s90_floor(painted, name):
    p = painted[f"{name}-phone"]["probe"]
    assert p["minPhone"] >= PHONE_FLOOR, [t for t in p["svgText"] + p["ink"] if t["px"] * PHONE_W / 1920 < PHONE_FLOOR]


@needs_browser
def test_without_the_option_the_page_paints_as_it_did(painted):
    p = painted["94-off"]["probe"]
    assert not p["profile"] and p["grids"] > 0 and p["panel"] is None
    png = RB.render_frame(_off_html(), T_FRAME, ASPECT)   # the golden harness's own fresh-browser render
    assert hashlib.sha256(RB.rgb_bytes(png)[1]).hexdigest() == FRAME_94_PIN


def _off_html() -> Path:
    td = Path(tempfile.mkdtemp(prefix="lf-off-"))
    tl, uris = _timeline(_world("94", td / "ep"))
    html = td / "off.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    return html


# N2 in the player: the state a recast reaches writes every end tag on the stage, at every preset
STATE_TAGS = """() => {
  const stage = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world')].find(e => e.__lp && e.classList.contains('ledger'));
  if (!w) return null;
  const S = (w.__lp.states || [])[1]; if (!S) return null;
  const shown = +getComputedStyle(S.chart).opacity;
  const out = [];
  for (const e of S.chart.querySelectorAll('text.sname, tspan.tagchip')) {
    if (!e.textContent.trim() || (e.closest('text') || e).getAttribute('opacity') === '0') continue;
    const r = e.getBoundingClientRect();
    out.push({ text: e.textContent, left: r.left - stage.left, right: r.right - stage.left });
  }
  const words = (ink) => ink && ink.div ? ink.div.querySelectorAll('.w').length : 0;
  return { shown, stageW: stage.width, tags: out, subWords: words(S.subInk), srcWords: words(S.srcInk) };
}"""


@needs_browser
@pytest.mark.parametrize("preset", PRESETS)
@pytest.mark.parametrize("row", sorted(THEN_ROWS))
def test_a_then_state_writes_its_end_tags_on_the_stage(row, preset, tmp_path):
    """The review's row (`bars;then=...:line`) put the state's tags at x 2194 on a 1920 stage at `phone`: each state
    now carries its own fitted form, so after the recast every tag it writes ends inside the stage."""
    from playwright.sync_api import sync_playwright

    world = _then_world(THEN_ROWS[row], tmp_path, preset)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": [{"kind": "chart_to", "to": "recast", "state": 1, "at": 9.0, "dur": 1.5}]}]
    tl = G._timeline("P69 N2 then", scenes, {}, ASPECT)
    uris = dict(G._base_uris(), **B.longform_assets(tl))
    html = tmp_path / "then.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[ASPECT]
    srv, port = RB.serve(html.parent)
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            page.wait_for_function("document.fonts.status === 'loaded'")
            RB.frame_png(page, 18.0, (w, h))
            page.wait_for_timeout(120)
            RB.frame_png(page, 18.0, (w, h))
            got = page.evaluate(STATE_TAGS)
            br.close()
    finally:
        srv.shutdown()
    assert got and got["shown"] > 0.99, f"the recast reached the state: {got}"
    assert got["tags"], "the line state writes its end tags"
    out = [t for t in got["tags"] if t["right"] > got["stageW"] + 0.5 or t["left"] < -0.5]
    assert not out, f"{row} {preset}: the state's end tags leave the stage: {out}"
    assert got["subWords"] > 1 and got["srcWords"] > 1, f"the state's sub and source wrap by WORD, as the page's do: {got}"


# ---- P69 T10 (E99 s90 + s84): BADGES AS THE KEY --------------------------------------------------------------------
# A line whose end tag the stage cannot hold gives up its long name for its badge (T8's `axes.tag_form`); that name
# gets a home on the KEY RAIL - one Bravos pill per series (a white capsule, the series' colour dot, the full name),
# in the page's TOP BAND between the sub and the plot (Bravos's own legend band, t170 / t1078), springing on the
# `badge-ladder` recipe's clock after the build and landing on an even pill count where the series allow.

KEY_CLOCK = (2.05, 1.30)   # recipe:badge-ladder - FIRST_BADGE_S, BADGE_GAP_S (the first key 2.05 s in, then 1.30 apart)
KEYED = ("long", "rail", "even")   # the fixtures whose end tags give up their names at the larger presets


def _dropped(page: dict) -> list[str]:
    """The full names this page's end tags gave up (a tag in `badge` or `value` form keeps only its label)."""
    if (page.get("axes") or {}).get("tag_form") in (None, "full"):
        return []
    return [s["name"] for s in page.get("series") or [] if s.get("label") and s.get("name") and not s.get("muted")]


@pytest.mark.parametrize("preset", PRESETS)
@pytest.mark.parametrize("name", sorted(PAGES))
def test_a_shortened_page_keys_every_name_its_tags_gave_up(name, preset, tmp_path):
    """The compiler writes the key onto the page (`axes.key`, one entry per pill: the series' index and its full name):
    every name an end tag gave up is on it, in the series' own order; a page whose tags keep their names has none."""
    page = _world(name, tmp_path, f"{OPT}:{preset}")["page"]
    key, dropped = page["axes"].get("key") or [], _dropped(page)
    names = [k["name"] for k in key]
    assert all(n in names for n in dropped), (name, preset, dropped, key)
    if not dropped:
        assert "key" not in page["axes"], (name, preset, key)
    idx = [k["series"] for k in key]
    assert idx == sorted(idx) and all(page["series"][k["series"]].get("name") == k["name"] or
                                      page["series"][k["series"]].get("label") == k["name"] for k in key), key


def test_a_long_page_at_middle_is_keyed(tmp_path):
    """The working default shortens the long fixture's tags (T8), so the key is not vacuous there."""
    page = _world("long", tmp_path, f"{OPT}:middle")["page"]
    assert page["axes"]["tag_form"] != "full"
    assert [k["name"] for k in page["axes"]["key"]] == [s["name"] for s in LONG["series"]]


@pytest.mark.parametrize("preset", PRESETS)
def test_the_key_lands_on_an_even_pill_count_where_the_series_allow(preset, tmp_path):
    """E99 s84: "prefer to land on even pills (2 or 4)". Three shortened lines and a fourth that keeps its own tag: the
    fourth joins the key (4 pills). Three shortened lines and nothing else to key: three - never an invented pill."""
    even = _world("even", tmp_path / "even", f"{OPT}:{preset}")["page"]
    if _dropped(even):
        key = [k["name"] for k in even["axes"]["key"]]
        assert len(key) == 4 and key[-1] == "BASELINE", key
    long = _world("long", tmp_path / "long", f"{OPT}:{preset}")["page"]
    if _dropped(long):
        assert len(long["axes"]["key"]) == 3, long["axes"]["key"]


def test_without_the_option_a_page_carries_no_key(tmp_path):
    for name in KEYED:
        assert "key" not in (_world(name, tmp_path / name)["page"].get("axes") or {})
    field = _world("long", tmp_path / "field", "", series=dict(copy.deepcopy(LONG), readability="longform:middle"))
    assert field["page"]["axes"]["key"], "a series file's own long form is keyed the same way as the row's"


@needs_browser
@pytest.mark.parametrize("name,preset", [(n, p) for n in KEYED for p in PRESETS])
def test_every_shortened_name_is_written_on_the_stage_in_a_key_pill(painted, name, preset):
    """The RED of T10: a shortened page wrote its full names nowhere. Now each is a pill on the key rail, carrying the
    dot of its OWN line's colour, set at the preset's key size, in the Bravos pill (white capsule, dark type)."""
    got = painted[f"{name}-{preset}"]
    p, page = got["probe"], got["page"]
    written = [kp["name"] for kp in p["keyPills"]]
    for n in _dropped(page):
        assert n in written, f"{n!r} is written nowhere on the stage"
    assert written == [k["name"] for k in (page["axes"].get("key") or [])], (p["keyPills"], page["axes"].get("key"))
    px = page["axes"].get("key_px")
    if written:   # the preset's own size, or the largest at which the row fits one line - never under the spec's pill
        assert LPG.LONGFORM_KEY_MIN_PX <= px <= LPG.LONGFORM_KEY_PX[preset], px
        if px > LPG.LONGFORM_KEY_MIN_PX:
            assert len({round(kp["rect"]["y"]) for kp in p["keyPills"]}) == 1, ("the key is one row", p["keyPills"])
    for k, kp in zip(page["axes"].get("key") or [], p["keyPills"]):
        assert kp["dot"] == p["lineCols"][str(k["series"])], (kp, p["lineCols"])
        assert kp["px"] == pytest.approx(px, abs=SIZE_TOL), kp
        assert kp["rect"]["h"] == pytest.approx(LPG.LONGFORM_KEY_EM["h"] * px, abs=1.5), kp
        assert kp["opacity"] == 1, f"every pill has landed by T_FRAME: {kp}"


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_the_key_rail_stands_in_the_top_band_clear_of_everything(painted, name, preset):
    """The key rail is inside the stage, under the title and M28's air under the sub, M28's air over the chart's
    top ink (the y label, the plot), and never on the source, the legacy rail, the caption strip or a chart word."""
    p = painted[f"{name}-{preset}"]["probe"]
    k, c = p["key"], p["checks"]
    if not p["keyPills"]:
        assert k is None or k["h"] == 0, "a page with nothing to key draws no key"
        return
    air = c["air"]
    assert k["x"] >= -0.5 and k["y"] >= -0.5 and k["x"] + k["w"] <= 1920.5 and k["y"] + k["h"] <= 1080.5, k
    assert k["y"] - c["subBottom"] >= air - 0.5, ("the key stands on the sub", k, c["subBottom"])
    tops = [c["plotTop"]] + ([p["ylabelRect"]["y"]] if p["ylabelRect"] else [])
    assert min(tops) - (k["y"] + k["h"]) >= air - 0.5, ("the key stands on the chart", k, tops)
    for other in [c["source"], *c["pills"], p["titleRect"]]:
        assert other is None or not _overlaps(k, other), ("the key meets", other, k)
    assert not _meets_strip(k), f"the key stands in the caption strip {STRIP}: {k}"
    for kp in p["keyPills"]:
        for t in p["svgText"]:
            assert not _overlaps(kp["rect"], t["rect"]), ("a key pill on a chart word", kp, t)


SWEEP = """() => {
  const s = document.getElementById('scrub'), out = [];
  const lp = () => [...document.querySelectorAll('.world')].find(e => e.__lp && e.classList.contains('ledger'));
  const op = (sel) => [...lp().__lp.page.querySelectorAll(sel)].map(e => +getComputedStyle(e).opacity);
  for (let i = 0; i <= 280; i++) {
    const t = 7 + i * 0.025;
    s.value = t; s.dispatchEvent(new Event('input', {bubbles: true}));
    out.push([t, op('.lp-key .lp-kpill'), op('.lp-rail .lp-pill')]);
  }
  return out;
}"""


def _key_onsets(name: str, preset: str, tmp_path: Path) -> tuple[list, list]:
    """Seek the page from 7 s to 14 s in 0.025 s steps: the first instant each key pill and each legacy rail pill
    shows (opacity > 0)."""
    from playwright.sync_api import sync_playwright

    tl, uris = _timeline(_world(name, tmp_path, f"{OPT}:{preset}"))
    html = tmp_path / "clock.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[ASPECT]
    srv, port = RB.serve(html.parent)
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            page.wait_for_function("document.fonts.status === 'loaded'")
            RB.frame_png(page, T_FRAME, (w, h))
            got = page.evaluate(SWEEP)
            br.close()
    finally:
        srv.shutdown()

    def first(j: int, n: int) -> list:
        return [next((row[0] for row in got if row[1 + j][i] > 0), None) for i in range(n)]
    return first(0, len(got[0][1])), first(1, len(got[0][2]))


@needs_browser
def test_the_key_springs_on_the_badge_ladder_clock(tmp_path):
    """recipe:badge-ladder: the first key pill 2.05 s after the chart has built, every later one 1.30 s behind the last.
    The build's end is read off the page's OWN rail pill, which springs LP_BADGE0 (0.4 s) after it."""
    keys, rail = _key_onsets("rail", "middle", tmp_path)
    assert len(keys) == 3 and len(rail) == 1 and None not in keys + rail, (keys, rail)
    built = rail[0] - 0.4
    step = 0.025 + 1e-6
    assert abs(keys[0] - built - KEY_CLOCK[0]) <= step, (keys, built)
    for a, b in zip(keys, keys[1:]):
        assert abs(b - a - KEY_CLOCK[1]) <= step, keys


@needs_browser
@pytest.mark.parametrize("name,preset", [(n, p) for n in KEYED for p in PRESETS])
def test_the_key_box_is_in_page_boxes_and_docks_and_stamps_avoid_it(painted, name, preset):
    """`page_boxes` reports the key rail (`key`) - the engine's own box to EST_TOL, and the fixture tool reads it too -
    and no free band a dock is placed in reaches into it, and a stamp's ring is fitted around it."""
    got = painted[f"{name}-{preset}"]
    if not got["probe"]["keyPills"]:
        pytest.skip("nothing keyed at this preset")
    est = LPG.page_boxes(got["page"], ASPECT)
    assert LPG.KEY_BOX in est, sorted(est)
    meas = got["boxes"].get("key")
    assert meas is not None, "measure_page_boxes reads the key rail"
    for d in ("x", "y", "w", "h"):
        assert abs(est[LPG.KEY_BOX][d] - meas[d]) <= EST_TOL, (d, est[LPG.KEY_BOX], meas)
    key = est[LPG.KEY_BOX]
    for band in B.free_bands(est):
        assert not _overlaps(band, key), ("a dock's free band reaches into the key", band, key)
    obstacles, _ = B.ring_obstacles(got["page"], ASPECT)
    assert key in obstacles, "a stamp's ring is fitted around the key"


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_the_x_labels_clear_the_panel_by_18_px(painted, name, preset):
    """T9 (3) / E99 s90: the x tick labels (a line page's) and the category names (a bars page's) stand at least 18 px
    clear of the plot's foot line - the panel's border (main measured 18; T17 measured 0; T8's page 7)."""
    p = painted[f"{name}-{preset}"]["probe"]
    assert p["xlabs"], "the page writes its x labels"
    top = min(x["rect"]["y"] for x in p["xlabs"])
    assert top - p["panelFoot"] >= 18.0, (name, preset, top, p["panelFoot"], top - p["panelFoot"])


@needs_browser
@pytest.mark.parametrize("name,preset", CASES)
def test_the_sub_never_meets_the_y_label(painted, name, preset):
    """T9 (2), re-verified with the key in the band between them: the sub's box and the y label's box never meet."""
    p = painted[f"{name}-{preset}"]["probe"]
    sub = next((i["rect"] for i in p["ink"] if "lp-sub" in i["cls"]), None)
    if sub is None or p["ylabelRect"] is None:
        return
    assert not _overlaps(sub, p["ylabelRect"]), (sub, p["ylabelRect"])

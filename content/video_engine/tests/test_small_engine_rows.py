"""P72 T27 - the small engine rows, one section (and one commit) each.

R26-57   the stage-space text at geometric precision (the page's own rule, R26-48, widened to the species' labels)
R26-72   a tiers page draws its same-unit tiers on the shared domain it carries (E79)
R26-73   the 9:16 newsreel default, measured against E84
R26-142  the agenda page's palette in the template's classes
R26-360  the hand (Kalam) served from the committed file, never from Google Fonts
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parents[2]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(TESTS / "golden"))
sys.path.insert(0, str(TESTS))

import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"


def _chromium_available() -> bool:
    try:
        from PIL import Image  # noqa: F401
        with SP.browser():
            return True
    except Exception:
        return False


needs_chromium = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _golden_html(surface: str, td: str) -> tuple[Path, float, tuple[int, int]]:
    tl, uris, t, aspect = RB.load_surface(surface)
    html = Path(td) / f"{surface}.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    return html, t, RB.STAGE[aspect]


# ---- R26-57: the stage-space text at geometric precision ------------------------------------------------------
# R26-48's rule covers the PAGE's glyphs (`.lp text, .lp-chart text`); the stage-space species write their SVG text
# at Chromium's default `auto`, which lets Skia pick hinted advances per raster pass - the warm / cold defect the
# page's labels had. Read off the rendered DOM: each class, as the engine writes it, computes the rule.

STAGE_TEXT = [("species", "lab"), ("species", "chiplab"), ("species", "flowtag"), ("species", "vmstamp"),
              ("species-under", "lab"), ("species-under", "chiplab"), ("species-under", "flowtag"),
              ("species-under", "vmstamp"),
              ("chartbox", "ct"), ("chartbox", "cs"), ("chartbox", "csr"), ("chartbox", "cl")]
PAGE_RULE = "  .lp text, .lp-chart text { text-rendering: geometricPrecision; }"

_TEXT_RENDERING_JS = """(pairs) => {
  const NS = 'http://www.w3.org/2000/svg', out = {};
  let box = document.querySelector('#stage svg.chartbox');
  if (!box) { box = document.createElementNS(NS, 'svg'); box.setAttribute('class', 'chartbox'); document.getElementById('stage').appendChild(box); }
  for (const [host, cls] of pairs) {
    const parent = host === 'chartbox' ? box : document.getElementById(host);
    const el = document.createElementNS(NS, 'text'); el.setAttribute('class', cls); el.textContent = 'x';
    parent.appendChild(el);
    out[host + ' .' + cls] = getComputedStyle(el).textRendering;
    el.remove();
  }
  const page = document.createElementNS(NS, 'svg'); page.setAttribute('class', 'lp-chart');
  const t = document.createElementNS(NS, 'text'); page.appendChild(t); document.getElementById('stage').appendChild(page);
  out['.lp-chart text'] = getComputedStyle(t).textRendering; page.remove();
  out['#caption'] = getComputedStyle(document.getElementById('caption')).textRendering;
  return out;
}"""


@needs_chromium
def test_r26_57_every_stage_space_text_class_computes_geometric_precision():
    with tempfile.TemporaryDirectory() as td:
        html, t, (w, h) = _golden_html("chip-board", td)
        with SP.served(html, w, h) as (page, errs):
            RB.frame_png(page, t, (w, h))   # the board as it is read: every chip landed
            got = page.evaluate(_TEXT_RENDERING_JS, [list(p) for p in STAGE_TEXT])
            written = page.evaluate("() => [...document.querySelectorAll('#species .chiplab')].map(e => getComputedStyle(e).textRendering)")
    wrong = {k: v for k, v in got.items() if k.split(" .")[0] in ("species", "species-under", "chartbox") and v != "geometricprecision"}
    assert not wrong, f"stage-space text still at Chromium's default: {wrong}"
    assert written and set(written) == {"geometricprecision"}, f"the chip board's own labels compute {written}"
    assert got[".lp-chart text"] == "geometricprecision"   # the page's rule (R26-48) stands
    assert got["#caption"] == "auto", "the rule is scoped to the named SVG classes - the caption layer is not in it"


def test_r26_57_the_pages_rule_is_unchanged_and_the_stage_rule_is_its_own_line():
    lines = TEMPLATE.read_text(encoding="utf-8").splitlines()
    assert PAGE_RULE in lines, "R26-48's page rule must stay exactly as it was"
    first = next(ln for ln in lines if "text-rendering: geometricPrecision" in ln)
    assert first == PAGE_RULE, "test_render_determinism reads the FIRST geometricPrecision line as the page's"


# ---- R26-142: the agenda page's palette in the template's classes ---------------------------------------------
# P61 T8 wrote the PAGE form's colours as presentation attributes because the template was outside its write set;
# the house convention keeps a species' palette in the template's species CSS beside `.agnum` / `.agrow`. The page
# paints the same pixels (the four agenda-page goldens stay byte-identical). The 9:16 half of the row is NOT here:
# measured (P72 T27), the page form does not hold on a short - its shares are of the ROW'S HEIGHT only, so a tall
# narrow row takes a 279 px medallion, a 326 px icon over the text and 24.6 px type - a layout row for the parent.

AGENDA_MODULE = ROOT / "content/video_engine/scripts/species/agenda.mjs"
AGENDA_PAGE_CLASSES = {   # class -> the computed style it painted with before the move (the old attributes' values)
    "rect.agplate": {"fill": "rgb(5, 19, 30)"},
    "circle.agmed": {"fill": "none", "stroke": "rgb(245, 183, 46)"},
    "text.agtitle": {"fill": "rgb(242, 242, 242)", "fontWeight": "800", "letterSpacing": "1.5px", "paintOrder": "stroke",
                     "stroke": "rgba(27, 30, 35, 0.85)", "strokeWidth": "9px", "fontFamily": "Inter, Arial, sans-serif"},
    "text.agfig": {"fill": "rgb(245, 183, 46)", "fontWeight": "700", "paintOrder": "stroke",
                   "stroke": "rgba(27, 30, 35, 0.85)", "strokeWidth": "6px", "fontFamily": "Inter, Arial, sans-serif"},
}
HEX = re.compile(r"#[0-9A-Fa-f]{3,8}\b|rgba?\(")


def _module_function(src: str, name: str) -> str:
    start = src.index(f"export function {name}(")
    return src[start: src.index("\n}\n", start) + 2]


def test_r26_142_the_agenda_page_painter_writes_no_colour():
    src = AGENDA_MODULE.read_text(encoding="utf-8")
    body = _module_function(src, "paintAgendaPage")
    code = "\n".join(ln.split("/*")[0] for ln in body.splitlines())   # the painter's code, its comments aside
    assert not HEX.findall(code), f"a colour literal is left in paintAgendaPage: {HEX.findall(code)}"
    for attr in ('fill: AGENDA', 'stroke: AGENDA', '"font-family"', '"paint-order"', '"letter-spacing"'):
        assert attr not in code, f"paintAgendaPage still writes {attr} - the palette lives in the template"
    dials = src[src.index("export const AGENDA"): src.index("});", src.index("export const AGENDA"))]
    for dial in ("PAGE_INK", "PAGE_EDGE", "PAGE_GOLD", "PAGE_CHALK", "PAGE_HALO", "PAGE_FACE"):
        assert f"{dial}:" not in dials, f"AGENDA.{dial} restates a template colour - one line per class in the template"


def test_r26_142_the_template_carries_one_line_per_agenda_page_class():
    lines = TEMPLATE.read_text(encoding="utf-8").splitlines()
    for cls in ("agplate", "agmed", "agtitle", "agfig"):
        rule = [ln for ln in lines if ln.startswith(f"#species .{cls}, #species-under .{cls} {{")]
        assert len(rule) == 1, f"the template has {len(rule)} rules for .{cls}"


@needs_chromium
def test_r26_142_the_agenda_page_paints_the_palette_it_always_did():
    surface = "agenda-page"
    with tempfile.TemporaryDirectory() as td:
        html, t, (w, h) = _golden_html(surface, td)
        with SP.served(html, w, h) as (page, errs):
            RB.frame_png(page, t, (w, h))
            got = page.evaluate("""(spec) => { const out = {};
              for (const [sel, props] of Object.entries(spec)) {
                const el = document.querySelector('#species ' + sel); if (!el) { out[sel] = null; continue; }
                const cs = getComputedStyle(el); out[sel] = Object.fromEntries(Object.keys(props).map(k => [k, cs[k]]));
              } return out; }""", AGENDA_PAGE_CLASSES)
    assert got == AGENDA_PAGE_CLASSES, got


# ---- R26-72: a tiers page draws its same-unit tiers on the shared domain it carries (E79) ----------------------
# ledger_page computes E79's shared domain (`shared_tier_domains`) and WARNs when same-unit tiers differ, but the
# engine's `tierDomain` read only its own band. A page that carries `shared_tier_domains` now draws every tier of
# that unit on the one domain (a bar's pixel height is proportional to its value ACROSS tiers); `independent` on
# the page or the tier keeps its own; a page without the key is the page it always was.

def _tiers_bars_page(shared: bool) -> tuple[dict, dict]:
    import build_golden_sources as G
    import ledger_page as LPG
    series = {"title": "Two banks, one unit", "sub": "synthetic", "src": "Synthetic series; not a figure about the world",
              "tiers": [{"name": "SMALL", "unit": "bn", "bars": [{"label": "A", "value": 10}, {"label": "B", "value": 20}]},
                        {"name": "LARGE", "unit": "bn", "bars": [{"label": "A", "value": 150}, {"label": "B", "value": 300}]}]}
    page = LPG.build_spec(series, "tiers", None, "right")
    if shared:
        page["shared_tier_domains"] = {u: list(d) for u, d in LPG.shared_tier_domains(series).items()}
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": []}]
    return G._timeline("tiers on one scale", scenes, {}, None), G._base_uris()


def _bar_heights(tl: dict, uris: dict) -> list[list[float]]:
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "tiers.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, *RB.STAGE["16:9"]) as (page, errs):
            RB.frame_png(page, 12.0, RB.STAGE["16:9"])
            assert not errs, errs
            return page.evaluate("""() => { const out = {};
              const chart = document.querySelector('.lp-chart');   /* the page as painted once (a world layer may hold a copy) */
              chart.querySelectorAll('rect.bar').forEach(r => {   /* a band's bars share its base line */
                const base = Math.round(+r.getAttribute('y') + +r.getAttribute('height'));
                (out[base] = out[base] || []).push(+r.getAttribute('height')); });
              return Object.keys(out).sort((a, b) => a - b).map(k => out[k]); }""")


def _per_unit(heights: list[list[float]], values=((10, 20), (150, 300))) -> list[float]:
    return [round(h / v, 4) for band, vals in zip(heights, values) for h, v in zip(band, vals)]


@needs_chromium
def test_r26_72_a_page_with_shared_tier_domains_draws_every_tier_on_one_scale():
    heights = _bar_heights(*_tiers_bars_page(shared=True))
    assert len(heights) == 2 and all(len(b) == 2 for b in heights), heights
    k = _per_unit(heights)
    assert max(k) - min(k) < 0.01, f"px per unit differ across the tiers on a shared scale: {k} ({heights})"


@needs_chromium
def test_r26_72_a_page_without_the_key_keeps_each_tiers_own_scale():
    heights = _bar_heights(*_tiers_bars_page(shared=False))
    k = _per_unit(heights)
    assert k[0] > 5 * k[2], f"without the key each band fills its own height (small px/unit >> large): {k}"


@needs_chromium
def test_r26_72_an_independent_tier_leaves_the_shared_scale():
    tl, uris = _tiers_bars_page(shared=True)
    tl["scenes"][0]["world"]["page"]["tiers"][0]["axes"]["independent"] = True   # as _tiers_block carries a tier's key
    k = _per_unit(_bar_heights(tl, uris))
    assert k[0] > 5 * k[2], f"an independent tier keeps its own scale: {k}"


def test_r26_72_tier_shared_reads_the_unit_and_drops_a_malformed_entry_to_the_bands_own():
    import json
    import subprocess
    mod = (ROOT / "content/video_engine/scripts/species/tiers.mjs").as_uri()
    js = (f"import {{ tierShared, tierDomain }} from '{mod}';"
          "const pg = { shared_tier_domains: { bn: [0, 300], bad: [5, 1], nan: ['x', 2] }, axes: {} };"
          "const out = [tierShared(pg, { unit: 'bn', axes: {} }), tierShared(pg, { unit: 'Mb', axes: {} }),"
          " tierShared(pg, { unit: 'bad', axes: {} }), tierShared(pg, { unit: 'nan', axes: {} }),"
          " tierShared({ shared_tier_domains: pg.shared_tier_domains, axes: { independent: true } }, { unit: 'bn', axes: {} }),"
          " tierShared(pg, { unit: 'bn', axes: { independent: true } }), tierShared({}, { unit: 'bn' }),"
          " tierDomain([10, 20], true, [0, 300]), tierDomain([10, 20], true)];"
          "console.log(JSON.stringify(out));")
    got = json.loads(subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True,
                                    check=True).stdout)
    assert got[:7] == [[0, 300], None, None, None, None, None, None], got
    assert got[7] == [0, 300 * 1.08] and got[8] == [0, 20 * 1.08], got


# ---- R26-360: the hand served from the committed faces, never from Google Fonts --------------------------------
# The player fetched Kalam from fonts.googleapis.com / fonts.gstatic.com on every capture, so a dropped request under
# load was a named red (T9's FontsUnsettled) and the face was whatever build Google served that day. The six faces
# are committed beside the template - the bytes Google served on 2026-09-25 - and a capture never leaves the machine.

HAND_DIR = TEMPLATE.parent / "fonts" / "kalam"
HAND_BUILD = {   # the sha256 of each face as fonts.gstatic.com served it (kalam/v18, css2?family=Kalam:wght@400;700)
    "kalam-400-devanagari.woff2": "b79d6614aac600d3bf950ae2d6924f72725366d9b5cfb8e9ff88dbc5152044c0",
    "kalam-400-latin-ext.woff2": "1099e56781c48f97dc66c8df2039a640ded07742acd4c6f2c9dc6350c3e3f324",
    "kalam-400-latin.woff2": "954410601a823f37e219f7930b7446f86afa15621326a7078d56fb9c910135cb",
    "kalam-700-devanagari.woff2": "7deb08192e5f12f885cab3826284b68fb44c44447aa7e6dbafa27160fe90aa5c",
    "kalam-700-latin-ext.woff2": "1fc176f6b1fbc091d4321ef2c9b683a6f512f645b9f22c460c2e2f3d298fcf74",
    "kalam-700-latin.woff2": "252063af6ade8b9a744cde4ddad0fc21ea53b8ba711eed121a0c2e8610ea9c93",
}
GOOGLE = ("fonts.googleapis.com", "fonts.gstatic.com")
HAND_SURFACE = "race-path-eased"   # R26-243's own golden: a title, a sub and a citation in the hand


def test_r26_360_the_committed_faces_are_the_build_google_served_with_their_licence():
    import hashlib
    got = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HAND_DIR.glob("*.woff2"))}
    assert got == HAND_BUILD
    ofl = (HAND_DIR / "OFL.txt").read_text(encoding="utf-8")
    assert "Indian Type Foundry" in ofl and "SIL OPEN FONT LICENSE Version 1.1" in ofl


def test_r26_360_the_template_names_no_font_host():
    src = TEMPLATE.read_text(encoding="utf-8")
    code = re.sub(r"<!--.*?-->|/\*.*?\*/", "", src, flags=re.S)   # a comment may tell the history; the page may not fetch it
    assert not [h for h in GOOGLE if h in code], "the player still names a Google Fonts host"
    faces = re.findall(r"url\((fonts/kalam/[a-z0-9-]+\.woff2)\)", code)
    assert sorted(Path(f).name for f in faces) == sorted(HAND_BUILD), faces


def _capture_offline(html: Path, t: float, size: tuple[int, int]) -> tuple[bytes, list[str], dict]:
    """A capture with every request logged and the two Google hosts refused outright."""
    srv, port = RB.serve(html.parent)
    pw = br = None
    try:
        pw, br = SP.launch()
        page = br.new_context(viewport={"width": size[0], "height": size[1]}).new_page()
        asked: list[str] = []
        page.on("request", lambda r: asked.append(r.url))
        for host in GOOGLE:
            page.route(f"https://{host}/**", lambda r: r.abort())
        page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(page, *size)
        png = RB.frame_png(page, t, size)
        report = page.evaluate("() => window.__fontsSettled()")
        return png, asked, report
    finally:
        SP.closer(pw, br, srv.shutdown)()


def _assert_offline_golden(png: bytes, asked: list[str], report: dict) -> None:
    google = [u for u in asked if any(h in u for h in GOOGLE)]
    assert not google, f"the capture asked Google for the hand: {google}"
    hand = {f["weight"] for f in report["faces"] if f["family"] == "Kalam" and f["status"] == "loaded"}
    assert report["ok"] is True and hand >= {"400", "700"}, report
    golden = RB.rgb_bytes((RB.FRAMES / f"{HAND_SURFACE}.png").read_bytes())[1]
    assert RB.rgb_bytes(png)[1] == golden, "the committed face does not render the golden's bytes"


@needs_chromium
def test_r26_360_a_single_file_capture_never_asks_google_and_is_the_golden():
    with tempfile.TemporaryDirectory() as td:
        html, t, size = _golden_html(HAND_SURFACE, td)
        _assert_offline_golden(*_capture_offline(html, t, size))


@needs_chromium
def test_r26_360_a_split_build_carries_its_faces_and_is_the_golden():
    tl, uris, t, aspect = RB.load_surface(HAND_SURFACE)
    with tempfile.TemporaryDirectory() as td:
        page = RB.write_split(Path(td), tl, uris, f"{HAND_SURFACE}.timeline.json")
        assert sorted(p.name for p in (Path(td) / "fonts" / "kalam").glob("*.woff2")) == sorted(HAND_BUILD)
        _assert_offline_golden(*_capture_offline(page, t, RB.STAGE[aspect]))


# ---- R26-73: the 9:16 whole-reel crawl follows E84 (2) --------------------------------------------------------
# Measured at 4b54f77's parent (P72 T27a step 0): the strip law's default kept the caption on its E62 home (0.676-0.713
# of a 9:16 frame) and sent the crawl BELOW it (0.78-0.92); a crawl on the caption's strip was refused unless the row
# authored `cap_band: "above"` AND docked a card. E84 (2): a crawl across the whole reel sits around the top of the
# bottom third and the captions sit above it. Now an unauthored crawl takes that strip, the caption goes above it by
# default, and it does so with nothing docked (the engine reads the compiler's `caption_crawl` window). An authored
# region and an authored `cap_band` are drawn as authored.

def _bst():
    import build_scene_timeline_f as BST
    return BST


def _reel(**kw) -> dict:
    e = {"kind": "newsreel", "at": 5.0, "dur": 20.0, "headlines": ["A sourced headline off the dossier"]}
    e.update(kw)
    return e


ON_STRIP = {"kind": "region", "x0": 0.0, "y0": 0.675, "x1": 1.0, "y1": 0.815}   # the caption's own strip at 9:16
BELOW = {"kind": "region", "x0": 0.0, "y0": 0.78, "x1": 1.0, "y1": 0.92}        # clear below the caption's home


def test_r26_73_an_unauthored_crawl_takes_the_top_of_the_bottom_third():
    B = _bst()
    (row,) = B.newsreel_defaults([_reel()])
    tgt = row["target"]
    assert tgt["kind"] == "region" and (tgt["x0"], tgt["x1"]) == (0.0, 1.0)
    assert abs(tgt["y0"] - 2 / 3) < 1e-9 and abs(tgt["y1"] - (2 / 3 + B.NEWSREEL_BAND_H)) < 1e-9
    assert B._validate_newsreel(row) == [] and B.validate_species([row], (0, 0, 0), "plate-plain") == []
    authored = _reel(target=dict(BELOW))
    assert B.newsreel_defaults([authored]) == [authored], "an authored region is kept as authored"


def test_r26_73_a_crawl_on_the_captions_strip_puts_the_caption_above_it_by_default_with_nothing_docked():
    B = _bst()
    row = _reel(target=dict(ON_STRIP))
    assert B.validate_newsreel_strip([row], "9:16", False) == [], "the default is E84's, not a refusal"
    band = B.newsreel_caption_band(None, [row], "9:16", 5.0, 9.0)
    box = B.newsreel_region_box(row, "9:16")
    assert band["band"] == "newsreel-above" and band["y"] + band["h"] + B.NEWSREEL_STRIP_PAD <= box["y"]
    authored = _reel(target=dict(ON_STRIP), cap_band="above")   # the authored form still reads the same
    assert B.validate_newsreel_strip([authored], "9:16", False) == []
    assert B.newsreel_caption_band(None, [authored], "9:16", 5.0, 9.0) == band


def test_r26_73_a_crawl_that_leaves_the_caption_no_room_above_is_refused_by_name():
    B = _bst()   # unreachable under the region law (y0 >= NEWSREEL_LOW) at today's stages; the refusal names the numbers anyway
    tall = _reel(target={"kind": "region", "x0": 0.0, "y0": 0.05, "x1": 1.0, "y1": 0.95})
    (err,) = B.validate_newsreel_strip([tall], "9:16", False)
    assert "no room above it for the caption" in err and "E84" in err, err


def test_r26_73_a_crawl_authored_below_the_caption_keeps_the_caption_home():
    B = _bst()
    row = _reel(target=dict(BELOW))
    assert B.validate_newsreel_strip([row], "9:16", False) == []
    home = B.caption_home_box("9:16")
    assert B.newsreel_caption_band(None, [row], "9:16", 5.0, 9.0) == {"y": home["y"], "h": home["h"], "band": "quiet"}
    assert any("already clear" in e for e in B.validate_newsreel_strip([_reel(target=dict(BELOW), cap_band="above")], "9:16", True))
    sc = {"span": [0.0, 30.0], "docks": [], "species": [row]}
    assert B.stamp_crawl_caption_bands([sc], [{"s": 4.0, "e": 12.0}], "9:16") == 0 and "caption_crawl" not in sc


def test_r26_73_the_compiler_writes_the_crawl_window_where_nothing_is_docked():
    B = _bst()
    row = B.newsreel_defaults([_reel()])[0]
    sc = {"span": [0.0, 30.0], "docks": [], "species": [row]}
    assert B.stamp_crawl_caption_bands([sc], [{"s": 4.0, "e": 12.0}], "9:16") == 1
    (win,) = sc["caption_crawl"]
    assert (win["from"], win["to"]) == (5.0, 25.0)
    assert win["caption_band"] == B.newsreel_caption_band(None, [row], "9:16", 5.0, 25.0)
    quiet = {"span": [0.0, 30.0], "docks": [], "species": [row]}
    assert B.stamp_crawl_caption_bands([quiet], [{"s": 26.0, "e": 28.0}], "9:16") == 0, "no caption in the window, nothing written"
    wide = {"span": [0.0, 30.0], "docks": [], "species": [B.newsreel_defaults([_reel()])[0]]}
    assert B.stamp_crawl_caption_bands([wide], [{"s": 4.0, "e": 12.0}], "16:9") == 0, "16:9: the caption's 40 % home is clear"


def _whole_reel_9x16() -> tuple[dict, dict, float]:
    """newsreel-strip-above's own surface with the card, the region and the cap_band taken away: the whole-reel case."""
    B = _bst()
    tl, uris, t, _aspect = RB.load_surface("newsreel-strip-above")
    sc = tl["scenes"][0]
    sc["docks"] = []
    sc["species"] = B.newsreel_defaults([{k: v for k, v in e.items() if k not in ("target", "cap_band")}
                                         for e in sc["species"]])
    B.stamp_crawl_caption_bands(tl["scenes"], tl["caption_pages"], "9:16")
    return tl, uris, t


@needs_chromium
def test_r26_73_the_whole_reel_crawl_renders_under_the_caption_with_nothing_docked():
    tl, uris, t = _whole_reel_9x16()
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "reel.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, *RB.STAGE["9:16"]) as (page, errs):
            RB.frame_png(page, t, RB.STAGE["9:16"])
            m = page.evaluate("""() => { const st = document.getElementById('stage').getBoundingClientRect();
              const b = (e) => { const r = e.getBoundingClientRect(); return [r.top - st.top, r.bottom - st.top]; };
              const words = [...document.getElementById('caption').querySelectorAll('*')].filter(e => e.getBoundingClientRect().height > 0);
              return { cap: words.map(b).reduce((a, c) => [Math.min(a[0], c[0]), Math.max(a[1], c[1])]),
                       band: b(document.querySelector('.nrband')) }; }""")
    assert not errs, errs
    assert abs(m["band"][0] - 1920 * 2 / 3) < 2, m     # the crawl at the top of the bottom third
    assert m["cap"][1] <= m["band"][0], m                # the caption above it, clear
    assert m["cap"][0] > 1920 * 0.5, m                   # ... and still in the lower half, roughly where it lives

"""E67 (operator, 2026-09-12) - THE FIELD'S INK: "we need to use bolder primary, high-contrast line colors for our
default the chart instead of gray. that way our charts can become our thumbnails, i think this is part of why bravos
uses electric colors." Corrected the same day: "the teal is good, the cobalt would be a fine 3rd color. the first 2
colors need to be more electric & high contrast. like the Teal and a Claude orange would work."

Four things the ruling asks of the engine, each with its own test:

1. THE TABLE reads at thumbnail scale - every ink measured as WCAG contrast against the charcoal field (#25313C),
   computed HERE from the hex the engine actually carries, so a future edit that dulls one is a failure and not a taste
   argument. The old table failed this: crimson 4.3:1, teal 3.2:1, and --lp-neg at 1.9:1 was invisible as a line.
2. THE HISTORY of a series that DECLARED its colour is that same hue at .45 - not grey. On the Tokyo holdings page 26
   years of line were rgba(184,196,208,.55). A series drawn in its SIGN colour keeps a neutral history (the 09-05
   rule: "nor the history red").
3. AN UNDECLARED series is never deemph - it takes the electric cycle by index (teal, then the orange).
4. THE BLOOM is a dial: LINE_BLOOM = 0 leaves no halo anywhere.

The table tests are static and always run. The draw tests need playwright + chromium and skip without them.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402

FIELD = "#25313C"        # E22: the charcoal the chart is drawn on - every ratio below is against THIS
LINE_MIN = 4.0           # any ink that paints a line on the field
PRIMARY_MIN = 6.0        # the ones a page reaches for first: teal, cobalt, and a rise
SURFACE = "ledger-soak-page"


# ---- WCAG, computed here (the test owes nobody's arithmetic) ------------------------------------


def _rel_luminance(hex_col: str) -> float:
    h = hex_col.strip().lstrip("#")
    assert len(h) == 6, hex_col
    ch = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        ch.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def _contrast(a: str, b: str = FIELD) -> float:
    la, lb = _rel_luminance(a), _rel_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def test_the_wcag_helper_is_right_on_the_two_ends_of_the_scale():
    assert abs(_contrast("#FFFFFF", "#000000") - 21.0) < 0.01
    assert abs(_contrast(FIELD, FIELD) - 1.0) < 1e-9


# ---- 1. the table ------------------------------------------------------------------------------


def _engine_table(name: str) -> dict:
    """The engine's own LP_INK literal - parsed, never re-typed here."""
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const " + name + r" = \{([^}]*)\};", src)
    assert m, f"{name} is not declared in the engine"
    return {k: v for k, v in re.findall(r"(\w+)\s*:\s*\"(#[0-9A-Fa-f]{6})\"", m.group(1))}


def _sign_vars() -> dict:
    css = TEMPLATE.read_text(encoding="utf-8")
    out = {}
    for tok in ("lp-pos", "lp-neg"):
        m = re.search(r"--" + tok + r":\s*(#[0-9A-Fa-f]{6})", css)
        assert m, f"--{tok} is not declared in the template"
        out[tok] = m.group(1)
    return out


def test_the_field_ink_is_one_table_and_not_a_set_of_copies():
    """E67: LP_PAL, the ledger line's PAL and the species palette all READ LP_INK - a copy would drift."""
    src = ENGINE.read_text(encoding="utf-8")
    assert re.search(r"const LP_PAL = LP_INK;", src), "LP_PAL must be the one table"
    assert re.search(r"const PAL = LP_INK;", src), "the ledger line reads the one table"
    assert re.search(r"const PS_PAL = \{ \.\.\.LP_INK,", src), "the species palette spreads the one table"
    assert len(re.findall(r"const LP_INK = \{", src)) == 1, "LP_INK is declared once"
    for dead in ("#ED6A4A", "#178C83"):   # the old field inks: gone from the engine, not merely shadowed
        assert dead not in src, f"{dead} is still in the engine - a copy of the old table survives"
    # the old cobalt survives in exactly ONE place: the dock tier's TPAL, which reads on #16181c and not on the field
    assert src.count("#8fb3f0") == 1, "the old cobalt is loose in the field's code again"
    # the DOCK tier keeps its own pair of tables (PAL graphic + TPAL text) - it draws on #16181c, not on the field
    assert len(re.findall(r"crimson:\s*\"#", src)) == 3, "only LP_INK and the dock tier's two tables carry a literal"


def test_every_field_ink_keeps_its_token_name_so_object_files_stay_valid():
    ink = _engine_table("LP_INK")
    assert set(ink) == {"crimson", "teal", "cobalt", "amber", "deemph"}, ink


@pytest.mark.parametrize("token", ["crimson", "teal", "cobalt", "amber"])
def test_every_line_ink_clears_the_thumbnail_floor_on_the_charcoal(token):
    ink = _engine_table("LP_INK")
    got = _contrast(ink[token])
    assert got >= LINE_MIN, f"{token} {ink[token]} is {got:.2f}:1 on {FIELD} - under {LINE_MIN}:1 it reads grey small"


@pytest.mark.parametrize("token", ["teal", "cobalt"])
def test_the_primary_inks_clear_the_higher_bar(token):
    ink = _engine_table("LP_INK")
    got = _contrast(ink[token])
    assert got >= PRIMARY_MIN, f"{token} {ink[token]} is {got:.2f}:1 - a primary must clear {PRIMARY_MIN}:1"


def test_both_sign_colours_read_as_lines_and_a_rise_is_a_primary():
    sign = _sign_vars()
    neg, pos = _contrast(sign["lp-neg"]), _contrast(sign["lp-pos"])
    assert neg >= LINE_MIN, f"--lp-neg {sign['lp-neg']} is {neg:.2f}:1 (the old #B0201F was 1.9 - invisible)"
    assert pos >= PRIMARY_MIN, f"--lp-pos {sign['lp-pos']} is {pos:.2f}:1"


def test_the_first_two_inks_are_the_teal_and_the_claude_orange_in_that_order():
    """The operator's correction: teal first, a Claude orange second, cobalt third, amber fourth."""
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LP_CYCLE = \[([^\]]*)\];", src)
    assert m, "LP_CYCLE is not declared"
    cycle = re.findall(r"\"(\w+)\"", m.group(1))
    assert cycle == ["teal", "crimson", "cobalt", "amber"], cycle
    ink = _engine_table("LP_INK")
    assert ink["teal"] == "#34F5C5" and ink["crimson"] == "#FF8A4C", ink
    assert "deemph" not in cycle, "deemph is explicit de-emphasis only - it is never a default"


def test_the_orange_stays_within_a_hue_of_anthropics_own():
    """#D97757 is the brand orange at 4.3:1 - too dull for a 4 px line. The slot takes an electric lift of it."""
    import colorsys
    ink = _engine_table("LP_INK")

    def hue(hex_col):
        h = hex_col.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return colorsys.rgb_to_hls(r, g, b)[0] * 360

    assert abs(hue(ink["crimson"]) - hue("#D97757")) <= 10, "the orange must still read as the brand's hue"
    assert _contrast(ink["crimson"]) > _contrast("#D97757"), "the lift has to actually lift"


def test_the_bloom_is_a_dial_with_a_derived_note():
    src = ENGINE.read_text(encoding="utf-8")
    m = re.search(r"const LINE_BLOOM = ([0-9.]+);\s*/\* \[DERIVED", src)
    assert m, "LINE_BLOOM must be a dial carrying a [DERIVED] note"
    assert 0 < float(m.group(1)) <= 1, m.group(1)


# ---- the draw ----------------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

STROKES = """() => [...document.querySelector('.lp-chart').querySelectorAll('path.ser')].map(p => ({
  muted: p.classList.contains('muted'),
  stroke: p.getAttribute('stroke') || p.style.stroke || '',
  filter: p.style.filter || '',
}))"""


class _Page:
    """One golden surface's page, its series REPLACED with the case under test."""

    def __init__(self, series: list, axes_extra: dict | None = None, engine: Path | None = None):
        from playwright.sync_api import sync_playwright
        tl, uris, _t, aspect = RB.load_surface(SURFACE)
        sc = tl["scenes"][0]
        pg = sc["world"]["page"]
        page_spec = dict(pg, series=series, axes=dict(pg.get("axes") or {}, **(axes_extra or {})))
        scene = dict(sc, species=[], world=dict(sc["world"], page=page_spec, ken_burns={"scale": 0, "x": 0, "y": 0}))
        timeline = dict(tl, scenes=[scene], caption_pages=[], captions=[])
        self.td = tempfile.TemporaryDirectory()
        html = Path(self.td.name) / "ink.html"
        html.write_text(RB.instantiate(timeline, uris, engine=engine or RB.ENGINE), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        self.srv, port = RB.serve(html.parent)
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        self.page = self.browser.new_context(viewport={"width": w, "height": h}).new_page()
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, w, h)

    def strokes(self, t: float = 9.0) -> list:
        self.page.evaluate(
            "t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(STROKES)

    def close(self):
        self.browser.close()
        self.pw.stop()
        self.srv.shutdown()
        self.td.cleanup()


def _pts(n: int = 10, base: float = 100.0) -> list:
    return [[str(2000 + i), str(base + i * 3)] for i in range(n)]


def _rgba(hex_col: str, a: str) -> str:
    h = hex_col.lstrip("#")
    return "rgba(%d,%d,%d,%s)" % (*(int(h[i:i + 2], 16) for i in (0, 2, 4)), a)


@needs_browser
def test_the_muted_history_takes_the_declared_hue_at_45_not_grey():
    ink = _engine_table("LP_INK")
    p = _Page([{"name": "Japan", "color": "teal", "pts": _pts()}], {"highlight_from": "2006"})
    try:
        got = p.strokes()
        muted = [s for s in got if s["muted"]]
        live = [s for s in got if not s["muted"]]
        assert len(muted) == 1 and len(live) == 1, got
        assert muted[0]["stroke"] == _rgba(ink["teal"], "0.45"), muted[0]["stroke"]
        assert live[0]["stroke"] == ink["teal"], live[0]["stroke"]
    finally:
        p.close()


@needs_browser
def test_an_undeclared_lone_series_still_keeps_a_neutral_history():
    """The 09-05 rule stands for the SIGN case: a 26-year line that is up overall must not paint its history green."""
    p = _Page([{"name": "Japan", "pts": _pts()}], {"highlight_from": "2006"})
    try:
        got = p.strokes()
        muted = [s for s in got if s["muted"]]
        assert len(muted) == 1, got
        assert muted[0]["stroke"] == "rgba(184,196,208,.45)", muted[0]["stroke"]
    finally:
        p.close()


@needs_browser
def test_an_undeclared_second_series_is_not_deemph_but_the_next_electric_ink():
    ink = _engine_table("LP_INK")
    p = _Page([{"name": "A", "pts": _pts()}, {"name": "B", "pts": _pts(base=140.0)}])
    try:
        got = [s for s in p.strokes() if not s["muted"]]
        assert len(got) == 2, got
        assert got[0]["stroke"] == ink["teal"], got[0]["stroke"]
        assert got[1]["stroke"] == ink["crimson"], got[1]["stroke"]
        assert all(s["stroke"] != ink["deemph"] for s in got), "an undeclared series is never grey (E67)"
    finally:
        p.close()


@needs_browser
def test_the_live_line_blooms_and_the_history_never_does():
    p = _Page([{"name": "Japan", "color": "teal", "pts": _pts()}], {"highlight_from": "2006"})
    try:
        got = p.strokes()
        live = [s for s in got if not s["muted"]][0]
        muted = [s for s in got if s["muted"]][0]
        ink = _engine_table("LP_INK")
        r, g, b = (int(ink["teal"].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
        assert "drop-shadow" in live["filter"], live["filter"]
        assert f"{r}, {g}, {b}" in live["filter"], f"the halo is the line's own hue: {live['filter']}"
        assert "0.35" in live["filter"], f"LINE_BLOOM is the halo's alpha: {live['filter']}"
        assert "drop-shadow" not in muted["filter"], muted["filter"]
    finally:
        p.close()


@needs_browser
def test_line_bloom_zero_leaves_no_halo_at_all():
    """The dial is real: the engine on disk is never touched - the zero is substituted in a temp copy."""
    src = ENGINE.read_text(encoding="utf-8")
    off = re.sub(r"const LINE_BLOOM = [0-9.]+;", "const LINE_BLOOM = 0;", src, count=1)
    assert off != src, "LINE_BLOOM was not substituted"
    with tempfile.TemporaryDirectory() as td:
        eng = Path(td) / ENGINE.name
        eng.write_text(off, encoding="utf-8")
        p = _Page([{"name": "Japan", "color": "teal", "pts": _pts()}], {"highlight_from": "2006"}, engine=eng)
        try:
            got = p.strokes()
            assert got, "no series on the page"
            assert all("drop-shadow" not in s["filter"] for s in got), [s["filter"] for s in got]
        finally:
            p.close()

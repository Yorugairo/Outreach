"""P69 T86 - the retitle takes a colour key: a page TOKEN, on the whole new title or on its leading span.

Row 22 of Steel and Paper H retitles the monitor page to "The flip: memory breaks while the buildout holds" and the
treatment wants "The flip" in the page's negative ink. The key is the page's own sign token (`neg` | `pos`, the
template's --lp-neg / --lp-pos) - a raw hex, an ink name or anything else is refused naming the allowed tokens - and
`color_span`, when given, is a LEADING substring of the new title that takes it (the rest keeps the title's own
colour); no span colours the whole title. A retitle without the key is the retitle it always was.

The browser half (the real engine through the player, as test_page_performs does) needs playwright + chromium.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_scene_timeline_f as B  # noqa: E402

FLIP = "The flip: memory breaks while the buildout holds"
LEDGER = "ledger:x:line"


def _rt(**kw) -> dict:
    return dict({"kind": "retitle", "at": 1.0, "dur": 1.0, "text": FLIP}, **kw)


def _errs(entry: dict) -> list[str]:
    return B.validate_species([entry], (0.0, 0, 0), LEDGER)


# ---- the compiler -------------------------------------------------------------------------------------------------

def test_the_allowed_colours_are_the_pages_sign_tokens():
    assert B.RETITLE_COLORS == ("neg", "pos")


@pytest.mark.parametrize("entry", [
    _rt(),
    _rt(color="neg"),
    _rt(color="pos"),
    _rt(color="neg", color_span="The flip"),
    _rt(color="neg", color_span=FLIP),
])
def test_a_retitle_takes_a_page_token_on_the_whole_title_or_a_leading_span(entry):
    assert _errs(entry) == []


@pytest.mark.parametrize("color", ["#FF4D4D", "#f00", "red", "crimson", "amber", "acc", "", None, 1])
def test_a_raw_hex_or_an_unknown_name_is_refused_listing_the_allowed_tokens(color):
    errs = _errs(_rt(color=color))
    assert len(errs) == 1 and "retitle: color" in errs[0] and "neg|pos" in errs[0], errs


@pytest.mark.parametrize("span, needle", [
    ("memory", "leading"),                 # occurs, but not at the start
    ("The flop", "leading"),               # never occurs
    (FLIP + " now", "leading"),            # longer than the title
    ("", "non-empty"),
    ("   ", "non-empty"),
    (3, "non-empty"),
])
def test_a_color_span_that_is_not_a_leading_substring_of_the_new_title_is_refused(span, needle):
    errs = _errs(_rt(color="neg", color_span=span))
    assert len(errs) == 1 and "retitle: color_span" in errs[0] and needle in errs[0], errs


def test_a_color_span_without_a_color_is_refused():
    errs = _errs(_rt(color_span="The flip"))
    assert len(errs) == 1 and "color_span" in errs[0] and "needs a color" in errs[0], errs


def test_the_keys_belong_to_the_retitle_only():
    """A note's own fields are untouched: the colour key is the retitle's, not a new generic page-species key."""
    assert B._validate_page_fields("note", {"kind": "note", "at": 1.0, "dur": 1.0, "text": "x"}) == []


# ---- the engine ---------------------------------------------------------------------------------------------------

try:
    from test_page_performs import (_Player, _authored, _line_golden, needs_browser,  # noqa: E402
                                    T_RETITLE, RETITLE_S, T_RELIGHT, RELIGHT_S)
except Exception:  # pragma: no cover - the browser half is skipped when its harness cannot load
    needs_browser = pytest.mark.skip(reason="test_page_performs harness unavailable")

SPAN = "The flip"
COLOURS_JS = """() => {
  const w = [...document.querySelectorAll('.lp-page')].find((e) => getComputedStyle(e).visibility !== 'hidden'
            && +getComputedStyle(e).opacity > 0) || document;
  const col = (e) => getComputedStyle(e).color;
  const home = (w.querySelector('.lp-retitle') || document.body).parentNode;   /* the tokens are declared on the page, not :root */
  const probe = document.createElement('span'); home.appendChild(probe);
  const tok = (v) => { probe.style.color = v; const c = getComputedStyle(probe).color; probe.style.color = ''; return c; };
  const out = { neg: tok('var(--lp-neg)'), pos: tok('var(--lp-pos)'), acc: tok('var(--lp-acc)'),
    title: [...w.querySelectorAll('.lp-title:not(.lp-retitle)')].map((t) => col(t)),
    retitles: [...w.querySelectorAll('.lp-retitle')].map((r) => ({ own: col(r), glyphs: [...r.querySelectorAll('.g')].map((g) => ({ ch: g.textContent, c: col(g) })) })) };
  probe.remove(); return out;
}"""


def _retitled(tl: dict, pts: list, **key) -> dict:
    tl2, _peak, _last = _authored(tl, pts)
    sc = tl2["scenes"][0]
    species = [dict(sp, text=FLIP, **key) if sp["kind"] == "retitle" else sp for sp in sc["species"]]
    species.append({"kind": "relight", "at": T_RELIGHT + 2.0, "dur": RELIGHT_S, "ref": "title"})
    return dict(tl2, scenes=[dict(sc, species=species)])


def _colours(tl: dict, uris: dict, aspect: str, times: list[float]) -> list[dict]:
    P = _Player(tl, uris, aspect)
    try:
        out = []
        for t in times:
            P.probe(t)
            out.append(P.page.evaluate(COLOURS_JS))
        return out
    finally:
        P.close()


def _span_glyphs(glyphs: list[dict]) -> int:
    """The glyphs the leading span owns: every character of it, or only its non-space ones where the title wraps
    (lpGlyphsWrap writes a word per inline block and no glyph for the space)."""
    n = len(SPAN)
    return n if len(glyphs) == len(FLIP) else n - SPAN.count(" ")


@needs_browser
def test_a_keyed_span_paints_the_token_and_the_rest_keeps_the_titles_own_colour():
    _name, tl, uris, aspect, pts = _line_golden()
    settle = T_RETITLE + RETITLE_S + 0.6
    relit = T_RELIGHT + 2.0 + RELIGHT_S / 2
    after = T_RELIGHT + 2.0 + RELIGHT_S - 0.001   # the relight's own last instant: e < 0.02, the colour restored
    [at_settle, at_relit, at_after] = _colours(_retitled(tl, pts, color="neg", color_span=SPAN), uris, aspect,
                                               [settle, relit, after])
    glyphs = at_settle["retitles"][0]["glyphs"]
    k = _span_glyphs(glyphs)
    assert "".join(g["ch"] for g in glyphs[:k]).replace(" ", " ").strip() == SPAN
    assert all(g["c"] == at_settle["neg"] for g in glyphs[:k]), f"the span is the page's neg token: {glyphs[:k]}"
    own = at_settle["retitles"][0]["own"]
    assert own != at_settle["neg"] and all(g["c"] == own for g in glyphs[k:]), \
        "the rest of the title keeps the title's own colour"
    assert all(g["c"] == at_relit["acc"] for g in at_relit["retitles"][0]["glyphs"]), \
        "a relight of the title lights every glyph, the span included"
    assert [g["c"] for g in at_after["retitles"][0]["glyphs"]] == [g["c"] for g in glyphs], \
        "and gives the span its token back when the light goes"


@needs_browser
def test_a_colour_without_a_span_paints_the_whole_title():
    _name, tl, uris, aspect, pts = _line_golden()
    [fr] = _colours(_retitled(tl, pts, color="pos"), uris, aspect, [T_RETITLE + RETITLE_S + 0.6])
    assert all(g["c"] == fr["pos"] for g in fr["retitles"][0]["glyphs"])


@needs_browser
def test_a_retitle_without_the_key_paints_no_glyph_colour():
    _name, tl, uris, aspect, pts = _line_golden()
    [fr] = _colours(_retitled(tl, pts), uris, aspect, [T_RETITLE + RETITLE_S + 0.6])
    own = fr["retitles"][0]["own"]
    assert all(g["c"] == own for g in fr["retitles"][0]["glyphs"]) and own != fr["neg"]


@needs_browser
def test_the_span_counts_the_glyphs_the_face_writes_a_wrapped_title_writes_none_for_a_space():
    """9:16 wraps the title (lpGlyphsWrap: a word per inline block, no glyph for the space), so the span owns its
    non-space characters there and every character on the one-line face; no span owns the whole title."""
    from playwright.sync_api import sync_playwright
    source = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    start = source.index("const rtSpanGlyphs = ")
    body = source[start:source.index("\n", source.index("};", start))]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        got = browser.new_page().evaluate("""(body) => eval(body + `; [
            rtSpanGlyphs({color_span: 'The flip'}, new Array(48), false),
            rtSpanGlyphs({color_span: 'The flip'}, new Array(42), true),
            rtSpanGlyphs({}, new Array(48), false),
            rtSpanGlyphs({color_span: 'The flip: memory breaks while the buildout holds now'}, new Array(48), false)]`)""", body)
        browser.close()
    assert got == [8, 7, 48, 48]

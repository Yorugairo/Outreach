"""P71 T30 (was P69 T78) - THE LONG FORM'S CHROME FINISH: the Bravos harvest v2's S9, S10 and S11.

  S9  "The legend chip turns accent when its series is isolated" (STK 04:14; BOOM 00:55 / 01:04 / 01:07 / 15:32 /
      15:58.5): on a `solo` the named series' KEY PILL fills with the page's accent and its END BADGE (the line-end tag
      with its chip) turns the accent, while the other pills and tags mute with their series - on the solo's own
      clock. Bravos's accent is ONE colour whatever the series (BOOM 00:56: the teal "Dotcom Boom" label in crimson), so
      ours is the page's one accent, `--lp-acc` (the sunflower callout capsule `rect.cpill`, charcoal type - the same
      mapping P71 T9's axis_tag made).
  S10 "Two-line source" (BRAVOS-LONGFORM-CHART-SPEC.md (b): `source: {lines: ["Date: ...", "Source: ..."]}`; STK 04:14,
      BOOM throughout, D40): a series key `source_lines`, the two lines written as two lines, each wrapping inside the
      safe column - never into the anchored caption's strip, never onto the key rail.
  S11 "The chart title sits in an accent capsule" - CORRECTED by BOOM's verify (its chart titles are plain; some SUBTITLES
      sit in a capsule) and decided by D40's step (0): D40 04:16 writes the TITLE "Obligations" in a crimson capsule
      (304 x 79 round 45 px of type: pad 17 v / 22 h) - so the key is the title's, `title_style: "capsule"`, an option
      and never a default, read beside P69 T37c's glowing title.

All three are the LONG FORM's (a series file that names `readability: longform`), refused BY NAME when malformed or
placed off it (the base accepted and ignored all three: logs/red-probe.log), and every page naming none of them is the
page it was, to the byte. The fixtures are synthetic SHAPES (never a figure about the world).
"""
from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as GS  # noqa: E402
import ledger_page as LPG  # noqa: E402
import gate_motion_density as GMD  # noqa: E402
import probe as P  # noqa: E402
import render_baseline as RB  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener
from test_longform_profile import LONG  # noqa: E402 - the keyed long page (SHAPES, never a figure)

ASPECT = "16:9"
MODULE = ROOT / "content/video_engine/scripts/species/solo.mjs"
DIM = float(re.search(r"DIM: ([0-9.]+),", MODULE.read_text(encoding="utf-8")).group(1))
ACCENT = "rgb(245, 183, 46)"      # `--lp-acc` (#F5B72E), the page's one accent (template :61)
CHAR = "rgb(37, 49, 60)"          # `--lp-char` (#25313C), the callout capsule's charcoal type
BADGE_INK = "rgb(30, 31, 34)"     # P72 T46d (R26-396): the lit badge's type on its accent box - the key pill's charcoal (KEY_INK #1E1F22)
T_REST = 14.0                     # every page has built, its key has sprung, and it holds
SOLO_AT, SOLO_DUR, SOLO_SERIES = 15.0, 0.6, 1
UNSOLO_AT, UNSOLO_DUR = 17.0, 0.5
STRIP = (LPG._full_stage_bands(1920, 1080)["bottom"]["y"], LPG.CAPTION_ANCHOR[ASPECT][1] + LPG.CAPTION_ANCHOR[ASPECT][3])
EST_TOL = 2.0                     # test_longform_profile's EST_TOL: the estimate is the engine's page to 2 px
PRESETS = LPG.LONGFORM_PRESETS

# the long page test_longform_profile keys at every preset (three long names its end tags give up to the key rail), in
# the long form by its own file - so the solo has key pills to light
BASE = dict(copy.deepcopy(LONG), readability=LPG.LONGFORM)
LINES = ["Date: January 2025 Through 30th September 2026.", "Source: " + BASE["src"] + "."]
ON = dict(copy.deepcopy(BASE), source_lines=list(LINES), title_style="capsule")


def _errs(series: dict) -> list[str]:
    return LPG.validate(series, "line")


def _world(series: dict, tmp: Path, opt: str = "") -> dict:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / "evidence/objects/fx-chrome.series.json").write_text(json.dumps(series), encoding="utf-8")
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        world = B.world_for_plate(f"ledger:fx-chrome:line{opt}", (0, 0, 0), tmp)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world


# ---- the grammar (no browser) --------------------------------------------------------------------------------------


def test_the_two_keys_ride_the_page_only_when_named():
    on, off = LPG.build_spec(ON, "line"), LPG.build_spec(BASE, "line")
    assert _errs(ON) == [] and on[LPG.SOURCE_LINES_KEY] == LINES and on[LPG.TITLE_STYLE_KEY] == "capsule"
    assert LPG.SOURCE_LINES_KEY not in off and LPG.TITLE_STYLE_KEY not in off
    assert on["source"] == BASE["src"], "the page's source is still its src: every reader of it reads the same words"


@pytest.mark.parametrize("value", ["Date: x", ["only one"], ["Date: x", ""], ["a", "b", "c"], [LINES[0], 7]])
def test_malformed_source_lines_are_refused_by_name(value):
    errs = _errs(dict(BASE, source_lines=value))
    assert any(e.startswith(LPG.SOURCE_LINES_KEY) for e in errs), errs


def test_the_two_lines_carry_the_pages_own_source():
    errs = _errs(dict(BASE, source_lines=["Date: As of September 2026.", "Source: somewhere else"]))
    assert any(LPG.SOURCE_LINES_KEY in e and repr(BASE["src"]) in e for e in errs), errs


@pytest.mark.parametrize("value", ["box", "", True, "Capsule"])
def test_an_unknown_title_style_is_refused_by_name(value):
    errs = _errs(dict(BASE, title_style=value))
    assert any(e.startswith(LPG.TITLE_STYLE_KEY) for e in errs), errs


@pytest.mark.parametrize("key,value", [("source_lines", LINES), ("title_style", "capsule")])
def test_off_the_long_form_either_key_is_refused_by_name(key, value):
    plain = {k: v for k, v in BASE.items() if k != "readability"}
    errs = _errs(dict(plain, **{key: value}))
    assert any(key in e and "long form" in e for e in errs), errs
    phone = dict(plain, readability=LPG.LANDSCAPE_PHONE, **{key: value})
    assert any(key in e and "long form" in e for e in _errs(phone)), _errs(phone)


def test_a_row_that_draws_the_page_off_the_long_form_is_refused_by_name(tmp_path):
    with pytest.raises(ValueError, match=LPG.SOURCE_LINES_KEY):
        _world(ON, tmp_path, ";readability=landscape-phone")
    assert _world(ON, tmp_path / "b", ";readability=longform:bravos")["page"][LPG.TITLE_STYLE_KEY] == "capsule"


def test_the_page_ink_key_moves_only_with_the_options():
    on, off = LPG.build_spec(ON, "line"), LPG.build_spec(BASE, "line")
    assert LPG.page_ink_key(on) != LPG.page_ink_key(off)
    bare = dict(off)
    bare.pop(LPG.SOURCE_LINES_KEY, None)
    assert LPG.page_ink_key(bare) == LPG.page_ink_key(off)


@pytest.mark.parametrize("preset", PRESETS)
def test_the_estimate_makes_the_room_the_two_options_take(preset, tmp_path):
    off = _world(BASE, tmp_path / "off", f";readability=longform:{preset}")["page"]
    on = _world(ON, tmp_path / "on", f";readability=longform:{preset}")["page"]
    a, b = LPG._longform_full_boxes(off, 1920, 1080), LPG._longform_full_boxes(on, 1920, 1080)
    assert b["source"]["h"] > a["source"]["h"], "two lines stand taller than one"
    assert b["title"]["h"] > a["title"]["h"] and b["title"]["x"] < a["title"]["x"], "the capsule pads and outdents"
    assert b["title"]["x"] + b["title"]["w"] <= a["title"]["x"] + a["title"]["w"] + 0.5, "inside the safe column's right"
    assert b["sub"]["y"] > a["sub"]["y"] and b["chart"]["y"] >= a["chart"]["y"]
    assert b["source"]["y"] + b["source"]["h"] <= STRIP[0] or b["source"]["y"] >= STRIP[1], "never in the caption strip"


@pytest.mark.parametrize("preset", PRESETS)
def test_the_options_that_squeeze_the_chart_are_reported_with_their_numbers(preset, tmp_path):
    """Found on the frame: at `phone` this long page's chart box fell from 220 px to 99 under both options and its end
    tags stood on each other. s106 - a WARN with its numbers (never a refusal), on the page only when it is true."""
    on = _world(ON, tmp_path / "on", f";readability=longform:{preset}")["page"]
    off = _world(BASE, tmp_path / "off", f";readability=longform:{preset}")["page"]
    warns = [w for w in on.get("warnings") or [] if w.startswith(LPG.CHROME_WARN)]
    assert not any(w.startswith(LPG.CHROME_WARN) for w in off.get("warnings") or [])
    if preset == "phone":
        assert len(warns) == 1 and "source_lines and title_style" in warns[0] and " px of the " in warns[0], warns
        cap = _world(dict(BASE, title_style="capsule"), tmp_path / "cap", f";readability=longform:{preset}")["page"]
        assert [w for w in cap.get("warnings") or [] if w.startswith(LPG.CHROME_WARN)], "the capsule alone takes 22 %"
    else:
        assert warns == [], warns
    lines = B.page_warning_lines({"page": on}, 7)
    assert all(LPG.CHROME_WARN in ln for ln in lines if "chrome" in ln) and len(lines) == len(warns), lines


# ---- the page, served ----------------------------------------------------------------------------------------------


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
  const stage = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world')].find(e => e.__lp && e.classList.contains('ledger'));
  const st = w.__lp, page = st.page;
  const R = (e) => { const r = e.getBoundingClientRect(); return {x: r.left - stage.left, y: r.top - stage.top, w: r.width, h: r.height}; };
  const cs = (e) => getComputedStyle(e);
  const title = page.querySelector('.lp-title'), src = page.querySelector('.lp-src'), sub = page.querySelector('.lp-sub');
  const lines = [...src.querySelectorAll('.lp-src-line')];
  return {
    title: { rect: R(title), bg: cs(title).backgroundColor, color: cs(title).color, shadow: cs(title).textShadow,
             radius: parseFloat(cs(title).borderTopLeftRadius), padT: parseFloat(cs(title).paddingTop),
             text: title.textContent, style: title.getAttribute('style') },
    src: { rect: R(src), text: src.textContent, lines: lines.map(l => ({ text: l.textContent, rect: R(l) })) },
    sub: sub ? R(sub) : null,
    key: (() => { const k = page.querySelector('.lp-key'); return k && k.querySelector('.lp-kpill') ? R(k) : null; })(),
    pills: [...page.querySelectorAll('.lp-key .lp-kpill')].map(e => ({ name: e.textContent, shadow: cs(e).boxShadow,
      opacity: +cs(e).opacity, style: e.getAttribute('style'), rect: R(e) })),
    tags: (st.paths || []).filter(pp => pp.name).map(pp => ({ si: pp.si | 0, text: pp.name.textContent,
      stroke: cs(pp.name).stroke, width: parseFloat(cs(pp.name).strokeWidth), order: cs(pp.name).paintOrder,
      fill: cs(pp.name).fill, fop: pp.name.getAttribute('fill-opacity'), style: pp.name.getAttribute('style'),
      chip: (() => { const c = pp.name.querySelector('tspan.tagchip'); return c ? { fill: cs(c).fill, style: c.getAttribute('style') } : null; })() })),
  };
}"""


def _timeline(world: dict, species: list | None = None) -> tuple[dict, dict]:
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, GS.RUNTIME], "docks": [], "species": species or []}]
    tl = GS._timeline("P71 T30 the long form's chrome", scenes, {}, ASPECT)
    return tl, dict(GS._base_uris(), **B.longform_assets(tl))


SOLO = [{"kind": "solo", "at": SOLO_AT, "dur": SOLO_DUR, "series": SOLO_SERIES},
        {"kind": "unsolo", "at": UNSOLO_AT, "dur": UNSOLO_DUR}]
READS = {"rest": T_REST, "mid": SOLO_AT + SOLO_DUR / 2, "lit": SOLO_AT + SOLO_DUR + 0.3, "back": UNSOLO_AT + UNSOLO_DUR + 0.3}


@pytest.fixture(scope="module")
def painted(tmp_path_factory):
    """The page OFF and ON at every preset (read at rest, with the fixture tool's own box read), and the ON page with a
    solo read at four instants - one guarded browser each."""
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    import measure_page_boxes as MPB
    tmp = tmp_path_factory.mktemp("chrome")
    out: dict = {}
    w, h = RB.STAGE[ASPECT]
    cases = [("off", BASE, "middle", None)] + [(f"on-{p}", ON, p, None) for p in PRESETS] + [("solo", ON, "middle", SOLO)]
    for name, series, preset, species in cases:
        world = _world(series, tmp / name, f";readability=longform:{preset}")
        if species:
            B.check_solo(world, [dict(s) for s in species])
        tl, uris = _timeline(world, [dict(s) for s in species] if species else None)
        html = tmp / f"{name}.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        page, errs, close = SP.open_served(html, w, h)
        try:
            page.wait_for_function("document.fonts.status === 'loaded'")
            reads = READS if species else {"rest": T_REST}
            got = {}
            for k, t in reads.items():
                RB.frame_png(page, t, (w, h))
                page.wait_for_timeout(120)
                RB.frame_png(page, t, (w, h))
                got[k] = page.evaluate(PROBE)
                got[k]["m28"] = P.derive(page.evaluate(P.READ_DOM), t, "p71-t30", {}, ASPECT, {})   # the gate's own read
            got["boxes"] = page.evaluate(MPB.READ_BOXES)
            out[name] = {"reads": got, "page": world["page"], "errors": list(errs)}
        finally:
            close()
    return out


@needs_browser
def test_the_capsule_and_the_two_line_source_render_off_and_on(painted):
    off, on = painted["off"]["reads"]["rest"], painted["on-middle"]["reads"]["rest"]
    assert not painted["off"]["errors"] and not painted["on-middle"]["errors"]
    assert off["title"]["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and off["title"]["padT"] == 0 and off["src"]["lines"] == []
    assert on["title"]["bg"] == ACCENT and on["title"]["color"] == CHAR and on["title"]["padT"] > 0
    assert on["title"]["shadow"] == "none", "the T37c glow is off inside the capsule (Bravos's capsule type has none)"
    assert on["title"]["text"] == BASE["title"] and 0 < on["title"]["radius"] < 0.2 * on["title"]["rect"]["h"]
    assert [ln["text"] for ln in on["src"]["lines"]] == LINES
    a, b = (ln["rect"] for ln in on["src"]["lines"])
    assert b["y"] >= a["y"] + a["h"] - 0.5, "the second line stands under the first"
    assert abs(a["x"] - b["x"]) < 0.5 and abs(a["x"] - off["src"]["rect"]["x"]) < 0.5, "both at the source's own left"


@needs_browser
@pytest.mark.parametrize("preset", PRESETS)
def test_the_estimate_is_the_engines_page_with_the_options_on(painted, preset):
    got = painted[f"on-{preset}"]
    est, meas = LPG._longform_full_boxes(got["page"], 1920, 1080), got["reads"]["boxes"]
    for key in ("sub", "chart", "source"):
        for d in ("x", "y", "w", "h"):
            assert abs(est[key][d] - meas[key][d]) <= EST_TOL, (preset, key, d, est[key], meas[key])
    for d in ("x", "y", "h"):
        assert abs(est["title"][d] - meas["title"][d]) <= EST_TOL, (preset, "title", d, est["title"], meas["title"])
    assert est["title"]["w"] >= meas["title"]["w"] - EST_TOL, (preset, est["title"], meas["title"])


def _meets(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["w"] - 0.5 and b["x"] < a["x"] + a["w"] - 0.5
            and a["y"] < b["y"] + b["h"] - 0.5 and b["y"] < a["y"] + a["h"] - 0.5)


@needs_browser
@pytest.mark.parametrize("preset", PRESETS)
def test_the_two_lines_stay_in_the_column_clear_of_the_strip_the_key_and_every_word(painted, preset):
    r = painted[f"on-{preset}"]["reads"]["rest"]
    s = r["src"]["rect"]
    assert s["y"] + s["h"] <= STRIP[0] + 0.5 or s["y"] >= STRIP[1] - 0.5, f"the source runs into the caption strip {STRIP}: {s}"
    assert s["x"] + s["w"] <= LPG.LAND_PHONE_SAFE_RIGHT * 1920 + 0.5, "inside the safe column"
    words = {"title": r["title"]["rect"], "sub": r["sub"], "source": s, "key": r["key"]}
    names = [k for k, v in words.items() if v]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert not _meets(words[a], words[b]), f"M28 text on text: {a} {words[a]} on {b} {words[b]}"


@needs_browser
@pytest.mark.parametrize("name", ["off", "on-bravos", "on-middle", "solo"])
def test_m28_is_clean_off_and_on_and_through_the_solo(painted, name):
    """M28 (text on text among the page's own labels), read by the gate's own reader and rule at every instant read. The
    phone page is the WARN's (above): its chart box is squeezed, and the finding is the author's to act on."""
    for k, read in painted[name]["reads"].items():
        if k == "boxes":
            continue
        fails, _warns, pairs = GMD._label_faults({"instants": [read["m28"]]})
        assert pairs > 0 and fails == [], (name, k, fails)


def _tag(read: dict, si: int) -> dict:
    return next(t for t in read["tags"] if t["si"] == si)


@needs_browser
def test_the_solo_lights_its_key_pill_and_its_end_badge_and_the_others_mute(painted):
    reads = painted["solo"]["reads"]
    assert not painted["solo"]["errors"], painted["solo"]["errors"]
    rest, mid, lit, back = reads["rest"], reads["mid"], reads["lit"], reads["back"]
    names = [k["name"] for k in BASE["series"]]
    pill = lambda read, si: next(p for p in read["pills"] if p["name"] == names[si])  # noqa: E731
    keyed = [si for si in range(3) if any(p["name"] == names[si] for p in rest["pills"])]
    assert SOLO_SERIES in keyed and len(keyed) >= 2, ("the fixture keys the named series and another", rest["pills"])
    # before the word: nothing lit, nothing muted - the page it was
    for si in keyed:
        assert pill(rest, si)["shadow"] == "none" and pill(rest, si)["opacity"] == 1
    for t in rest["tags"]:
        assert t["fill"] != ACCENT and t["fop"] is None, t
    # on it: the named pill fills with the accent, the others fade to the solo's dim; the named tag turns the accent
    assert ACCENT in pill(lit, SOLO_SERIES)["shadow"] and pill(lit, SOLO_SERIES)["opacity"] == 1
    for si in keyed:
        if si != SOLO_SERIES:
            assert abs(pill(lit, si)["opacity"] - DIM) < 2e-3 and pill(lit, si)["shadow"] == "none", pill(lit, si)
    named = _tag(lit, SOLO_SERIES)   # P72 T46d (R26-396): its box fills with the accent (test_wave3_page_marks), its type turns charcoal on it
    assert named["fill"] == BADGE_INK and named["stroke"] == "none" and named["fop"] is None, named
    if named["chip"]:
        assert named["chip"]["fill"] == BADGE_INK, named["chip"]
    for t in lit["tags"]:
        if t["si"] != SOLO_SERIES:
            assert t["stroke"] == "none" and abs(float(t["fop"]) - DIM) < 2e-3, t
    # half-way through the word the light is half-way: on the solo's own clock, never a switch
    half = pill(mid, SOLO_SERIES)["shadow"]
    assert half not in ("none", pill(lit, SOLO_SERIES)["shadow"]), half
    assert DIM < pill(mid, keyed[0] if keyed[0] != SOLO_SERIES else keyed[1])["opacity"] < 1
    # the release hands back the page, to the attribute
    for si in keyed:
        assert pill(back, si)["shadow"] == "none" and pill(back, si)["opacity"] == 1
    for t0, t1 in zip(rest["tags"], back["tags"]):
        assert (t1["style"], t1["stroke"], t1["fop"]) == (t0["style"], t0["stroke"], t0["fop"]), (t0, t1)
        assert (t1["chip"] or {}).get("style") == (t0["chip"] or {}).get("style")


@needs_browser
def test_the_solo_on_a_short_page_leaves_its_tags_as_they_were(tmp_path):
    """The accent is the long form's chrome: a short's solo page (no key rail, no long-form type) mutes as it did
    (the `solo-chipmakers` golden is this page) - its end tags never take the capsule."""
    plain = {k: v for k, v in BASE.items() if k != "readability"}
    world = _world(plain, tmp_path)
    B.check_solo(world, [dict(s) for s in SOLO])
    tl, uris = _timeline(world, [dict(s) for s in SOLO])
    html = tmp_path / "short.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[ASPECT]
    page, errs, close = SP.open_served(html, w, h)
    try:
        RB.frame_png(page, READS["lit"], (w, h))
        read = page.evaluate(PROBE)
    finally:
        close()
    assert not errs, errs
    assert all(t["fill"] != ACCENT and "lp-acc" not in (t["style"] or "") for t in read["tags"]), read["tags"]
    assert read["pills"] == []

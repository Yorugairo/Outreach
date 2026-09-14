"""P57 T14 / E90: the caption's LIFE - the pop leads, the stagger's envelope rides under it.

The composition itself (the three settings, the channel-by-channel blend, the lead, the seek test) is pinned in
`tests/kinetics/stagger.test.mjs` - kinetics/stagger.mjs is the source of truth and node tests it. What is pinned
HERE is everything python owns:

  the DEFAULT      `cap_life` is absent unless a build asks. No field, no timeline key, no engine branch taken -
                   which is why every golden and both approved shorts compile and render byte-identical to their
                   pre-slice selves. E90 s1: what Steel and Paper shipped is the base and it is not replaced.
  the DECLARATION  the compiler stamps the life on every caption page and on the timeline, and REFUSES a setting
                   it does not know by name (a typo must not silently ship the base).
  the ENGINE       reads the page's setting, paints it from the MODULE (`lifeAt`), keeps the blur on the word
                   span, and lets a held life page take E49's breath.
  the PIXELS       the three settings are three different frames at one instant, and asking for nothing is the
                   frame the engine painted before the slice (the browser proof; skipped without chromium).
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as BST  # noqa: E402
import render_baseline as RB  # noqa: E402

MODULE = ROOT / "content/video_engine/scripts/kinetics/stagger.mjs"
TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
STEEL = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
LIVES = ("pop", "stagger", "blend")


# ---- the default: nothing is declared, nothing changes -----------------------------------------

def test_the_life_is_absent_by_default_and_only_silence_means_the_base() -> None:
    """Unlike the arrival, "pop" is a real setting and IS written - it is the shipped pop a notch stronger."""
    assert BST.CAPTION_LIFE is None, "the compiler ships with no life declared"
    assert BST.CAPTION_LIVES == LIVES
    keep = BST.CAPTION_LIFE
    try:
        for asked in (None, "", "   "):
            BST.CAPTION_LIFE = asked
            assert BST._caption_life() is None, asked
        for asked in LIVES:
            BST.CAPTION_LIFE = asked
            assert BST._caption_life() == asked
    finally:
        BST.CAPTION_LIFE = keep


@pytest.mark.parametrize("typo", ["blended", "POP", "fade_up", "stagger "])
def test_an_unknown_setting_is_refused_by_name(typo: str) -> None:
    keep = BST.CAPTION_LIFE
    try:
        BST.CAPTION_LIFE = typo
        if typo.strip() in LIVES:
            assert BST._caption_life() == typo.strip(), "surrounding space is not a typo"
            return
        with pytest.raises(SystemExit) as e:
            BST._caption_life()
        assert typo.strip() in str(e.value) and "blend" in str(e.value)
    finally:
        BST.CAPTION_LIFE = keep


def test_the_compiler_stamps_the_page_beside_cap_mode_and_the_timeline_beside_caption_modes() -> None:
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    assert '"cap_life": _caption_life()' in src
    assert '**({"caption_life": _caption_life()} if _caption_life() else {})' in src


def _timelines() -> list[Path]:
    return sorted(TOKYO.glob("build-short*/*.timeline.json")) + sorted(STEEL.glob("build-*/*.timeline.json"))


def test_no_build_on_disk_carries_a_life_so_every_rebuild_is_clock_identical() -> None:
    """The approved cuts and every golden-adjacent build: no page field, no timeline key. If this fails, a build
    the operator approved has been recompiled with the new register turned on (R26-45: never a render)."""
    seen = 0
    for path in _timelines():
        tl = json.loads(path.read_text(encoding="utf-8"))
        if "caption_pages" not in tl:
            continue
        seen += 1
        assert "caption_life" not in tl, path
        assert not [pg for pg in tl["caption_pages"] if "cap_life" in pg], path
    assert seen, "no compiled timeline was found to check"


# ---- the engine ---------------------------------------------------------------------------------

def test_the_engine_reads_the_setting_and_paints_it_from_the_module() -> None:
    src = RB.player_text()
    assert "const lifeKind = (pg && stage) ? (pg.cap_life || TL.caption_life || null) : null;" in src, \
        "the page's setting wins over the timeline's"
    assert "const f = lifeAt(t, x.s, lifeKind), e = f.e;" in src, "the word keeps its own SPOKEN time"
    # the composition is the MODULE's, inlined (no runtime import), and its region sits before the caption block
    assert "/* KINETICS:BEGIN stagger */" in src
    assert src.index("/* KINETICS:BEGIN stagger */") < src.index("const f = lifeAt(t, x.s, lifeKind)")
    assert "const lifeAt = (t, start, kind" in src and "const popAt = (t, start" in src


def test_the_modules_dials_are_the_stated_ones_and_the_engine_carries_them() -> None:
    mod = MODULE.read_text(encoding="utf-8")
    assert "POP_LEAD: 1.22," in mod, "E90 s2 'a little stronger' is ONE number, stated"
    assert "POP_S: 0.20," in mod and "ANTICIP_S: 0.05," in mod
    assert '["pop", "stagger", "blend"]' in mod
    assert set(BST.CAPTION_LIVES) == {"pop", "stagger", "blend"}, "the compiler's settings are the module's"
    assert "POP_LEAD: 1.22," in RB.player_text(), "the inlined copy carries the dial (sync_kinetics --check)"


def test_no_cursor_no_flash_and_the_blur_stays_on_the_word_span() -> None:
    """The caption-energy lessons (2026-09-05): energy is continuous voice-timed motion, never a per-word event
    that pins the eye. The life path adds no class, no marker, no highlight the base did not already have."""
    import re
    src = RB.player_text()
    life = src[src.index("if (lifeKind) {"):src.index("else if (fuStarts) {")]
    code = re.sub(r"/\*.*?\*/", "", life, flags=re.S)   # the CODE, not the prose that names the lessons
    for banned in ("cursor", "flash", "classList.add", "setInterval"):
        assert banned not in code, banned
    assert 'ws[j].style.filter = f.b > 0.01 ? "blur(" + f.b.toFixed(2) + "px)" : "";' in life
    assert "cap.style.filter" not in src, "a filter on the strip would blur the whole caption at once"


def test_a_held_life_page_takes_e49s_breath_and_it_is_the_existing_kind() -> None:
    src = RB.player_text()
    assert 'cap.style.transform = (pg && (lifeKind || !(stage && PHRASE))) ? idleCssFor("caption"' in src
    assert 'caption: "breath"' in src, "the caption's idle kind is the one E49 already named - not a new one"


def test_the_shipped_pop_is_still_there_word_for_word() -> None:
    """The base register is not touched by the new one: the lines that paint it are intact (E90 s1)."""
    src = RB.player_text()
    assert 'const pop = kin("analytic_spring") ? springPop : stagePop;' in src
    assert "const e = pop(clamp01((t + 0.05 - x.s) / STAGE_POP_S));" in src
    assert "const STAGE_POP_S = 0.2;" in src
    assert "RISE_PX: 6" in src and "POP: 1.10" in src, "MARK's dials are unchanged"


# ---- the pixels ---------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

SURFACE = "test-card"   # the plainest golden surface: nothing but the stage and its caption strip moves


def _render(life: str | None) -> str:
    tl, uris, _, aspect = RB.load_surface(SURFACE)
    page = tl["caption_pages"][0]
    tl = dict(tl, caption_modes=["stage", "anchor"],
              caption_pages=[dict(pg, cap_mode="stage") for pg in tl["caption_pages"]])
    if life:
        tl["caption_life"] = life
    t = float(page["t"][1]["s"]) + 0.06      # the second word, mid-arrival: the pop is still above rest
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "life.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        return hashlib.sha256(RB.render_frame(html, t, aspect)).hexdigest()


@needs_browser
def test_a_caption_row_with_each_setting_compiles_and_paints_three_different_frames() -> None:
    shots = {name: _render(name) for name in (None, *LIVES)}
    for name in LIVES:
        assert shots[name] != shots[None], f"{name} painted the frame the base paints"
    assert len({shots[n] for n in LIVES}) == 3, f"the three settings are not three pictures: {shots}"

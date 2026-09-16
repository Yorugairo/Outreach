"""P61 T9: the gallery page is PINNED, so "a faster build" can never mean "renders less".

(b) Three frames of the built page at ONE fixed viewport - the top, one mid-page axis section, the
foot - against the goldens in tests/golden/frames/; any pixel change FAILS and writes
golden | actual | diff under tests/golden/diffs/, exactly as test_golden_frames.py does. Beside them
the assertion the speed work is really judged on: the page still lists EVERY record in
docs/EFFECTS-CATALOG.jsonl - count equal, no card dropped.

(a) The rest pins what made the build 0.48x its old wall clock: the ONE directory listing that
replaced some 300 globs, the local percent-encoder that replaced the urllib import, and the copy
that no longer re-writes 19.3 MB of unchanged PNGs on every run.

Refresh the frames deliberately, never by accident:
    python content/video_engine/scripts/build_effects_gallery.py --pin
"""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_effects_gallery as BEG  # noqa: E402
import render_baseline as RB  # noqa: E402

CATALOG = ROOT / BEG.CATALOG_REL
FRAMES = ROOT / BEG.FRAMES_REL


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> Path:
    """The real catalogue, built into a private directory - never the served copy (a review link is
    a frozen copy, and a test must not move a page out from under a reader)."""
    index, _line = BEG.build(CATALOG, FRAMES, tmp_path_factory.mktemp("gallery-page"))
    return index


@pytest.fixture(scope="module")
def captured(built, tmp_path_factory) -> Path:
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    shots = tmp_path_factory.mktemp("gallery-shots")
    BEG.capture_frames(built.parent, shots)
    return shots


# ---- (b) THE PAGE IS PINNED --------------------------------------------------------------------

def test_the_built_page_lists_every_record_in_the_catalogue(built) -> None:
    """No card dropped: the tile ids ARE the catalogue's ids, and there are exactly as many."""
    import re
    page = built.read_text(encoding="utf-8")
    records = BEG.load_cards(CATALOG)
    tiles = re.findall(r'<article class="tile[^"]*" data-id="([^"]+)"', page)
    assert len(tiles) == len(records), f"{len(records)} records in the catalogue, {len(tiles)} tiles on the page"
    assert sorted(tiles) == sorted(r["id"] for r in records)


def test_the_register_in_test_golden_frames_names_the_same_three_frames() -> None:
    from test_golden_frames import PAGE_SURFACES
    assert sorted(PAGE_SURFACES) == sorted(BEG.PIN_FRAMES) == sorted(_page_sources())


def _page_sources() -> list[str]:
    return [p.name[: -len(".page.json")] for p in RB.SOURCES.glob("gallery-*.page.json")]


@pytest.mark.parametrize("name", list(BEG.PIN_FRAMES))
def test_each_pinned_page_frame_is_unchanged(captured, name: str) -> None:
    golden = RB.FRAMES / f"{name}.png"
    assert golden.is_file(), f"{name}: no golden - run build_effects_gallery.py --pin"
    actual = (captured / f"{name}.png").read_bytes()
    if RB.rgb_bytes(golden.read_bytes())[1] != RB.rgb_bytes(actual)[1]:
        diff = RB.write_diff(name, golden.read_bytes(), actual)
        raise AssertionError(f"{name}: the gallery page changed - see {diff.relative_to(ROOT)}")


def test_the_pinned_frames_are_the_declared_viewport(captured) -> None:
    for name in BEG.PIN_FRAMES:
        assert RB.rgb_bytes((captured / f"{name}.png").read_bytes())[0] == BEG.PIN_VIEWPORT


def test_the_pin_catches_a_one_value_css_change(tmp_path, monkeypatch) -> None:
    """Proven by breaking it, the way test_golden_frames.py proves the engine's harness: the tile
    border, 1px -> 3px, in memory. A pin that cannot catch a one-value change is not a pin."""
    if not _chromium_available():
        pytest.skip("playwright chromium not installed")
    needle = ".tile{background:#fff;border:1px solid #ddd;"
    assert needle in BEG.CSS, "perturbation anchor missing from the gallery's CSS - pick another"
    monkeypatch.setattr(BEG, "CSS", BEG.CSS.replace(needle, needle.replace("1px", "3px"), 1))
    index, _line = BEG.build(CATALOG, FRAMES, tmp_path / "mutated")
    BEG.capture_frames(index.parent, tmp_path / "shots", ["gallery-top"])
    golden = (RB.FRAMES / "gallery-top.png").read_bytes()
    actual = (tmp_path / "shots" / "gallery-top.png").read_bytes()
    assert RB.rgb_bytes(golden)[1] != RB.rgb_bytes(actual)[1], (
        "a one-value CSS change captured identically - the pin is not looking at the page")


# ---- (c) MOTION - an effect a still cannot show -------------------------------------------------

MOTION_CARDS = ["chart_to:compare", "chart_to:remake", "exit:melt"]   # re-derived 2026-09-15 under the rule below: the remake
# (7 phases, 2 instants) now outranks the melt and the stack (5 phases, 1 instant) drops out; the older clips stay beside the page


def test_the_three_motion_cards_are_the_ones_the_rule_picks() -> None:
    """The rule, not taste: a card earns a clip when (1) its `phases` hold MORE THAN ONE phase - a
    composite whose order no single frame can carry - and (2) its golden already needed extra
    `@proof-*` instants pinned beside it, the record's own admission that one frame was not enough.
    Rank the qualifiers by phases, then by pinned instants; the top three are the three."""
    cards, _recipes = BEG.split_recipes(BEG.load_cards(CATALOG))
    index = BEG.FrameIndex(FRAMES)
    ranked = []
    for card in cards:
        main, strip = index.resolve((card.get("proof") or {}).get("golden"))
        if len(card.get("phases") or []) > 1 and main and strip:
            ranked.append((len(card["phases"]), len(strip), card["id"]))
    ranked.sort(reverse=True)
    assert [card_id for _p, _s, card_id in ranked[:3]] == MOTION_CARDS, ranked[:5]


def test_a_clip_beside_the_page_is_carried_as_a_video_by_its_own_card(tmp_path) -> None:
    import json
    records = [{"id": "a:one", "axis": "a", "token": "one", "title": "One", "does": "d", "status": "live",
                "proof": {"golden": None, "test": None}},
               {"id": "a:two", "axis": "a", "token": "two", "title": "Two", "does": "d", "status": "live",
                "proof": {"golden": None, "test": None}}]
    catalog = tmp_path / "cat.jsonl"
    catalog.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    out = tmp_path / "out"
    (out / BEG.FRAMES_SUBDIR).mkdir(parents=True)
    assert BEG.clip_name("a:one") == "a-one.mp4"           # a colon is not a file name on Windows
    (out / BEG.FRAMES_SUBDIR / BEG.clip_name("a:one")).write_bytes(b"stand-in for an mp4")
    index, _line = BEG.build(catalog, tmp_path / "frames", out)
    page = index.read_text(encoding="utf-8")
    assert '<video class="motion" src="frames/a-one.mp4"' in page
    assert page.count("<video") == 1, "the card with no clip must carry no video"


def test_the_pinned_page_carries_no_clip(built) -> None:
    """A golden derives from COMMITTED inputs only. The clips are generated artifacts under the
    gitignored gallery directory, so the page the three frames pin has none - the served page
    carries them on top."""
    assert "<video" not in built.read_text(encoding="utf-8")


@pytest.mark.parametrize("card_id", MOTION_CARDS)
def test_the_clip_of_each_motion_card_is_beside_the_served_page(card_id: str) -> None:
    clip = ROOT / BEG.OUT_REL / BEG.FRAMES_SUBDIR / BEG.clip_name(card_id)
    if not clip.is_file():
        pytest.skip(f"{clip.name} has not been rendered on this checkout (generated, gitignored)")
    assert clip.stat().st_size > 10_000, clip


# ---- (a) WHAT THE SPEED WORK REPLACED ----------------------------------------------------------

def test_the_frame_index_answers_what_the_glob_answered() -> None:
    """One scandir, the old semantics: `<surface>@proof-*` only, sorted, the golden itself excluded."""
    index = BEG.FrameIndex(FRAMES)
    for path in sorted(FRAMES.glob("*.png")):
        stem = path.stem
        surface = stem.split("@", 1)[0]
        expected = sorted(p.stem for p in FRAMES.glob(f"{surface}@proof-*.png") if p.stem != stem)
        assert index.resolve(stem) == (stem, expected), stem
    assert index.resolve("no-such-surface") == (None, [])
    assert index.resolve(None) == (None, [])


def test_the_frame_index_of_a_directory_that_is_not_there_is_empty(tmp_path) -> None:
    assert BEG.FrameIndex(tmp_path / "nothing").resolve("x") == (None, [])


def test_pct_is_urllib_quote_for_every_stem_on_disk() -> None:
    """The page's bytes cannot drift: the hand-rolled encoder is urllib's answer on the real stems."""
    stems = [p.stem for p in FRAMES.glob("*.png")]
    assert stems, "no golden frames to check the encoder against"
    for stem in stems + ["a b", "c/d", "e~f.g", "h%i", "é"]:
        assert BEG.pct(stem) == quote(stem), stem


def test_an_unchanged_frame_beside_the_page_is_not_copied_again(tmp_path) -> None:
    src, dst = tmp_path / "src.png", tmp_path / "dst.png"
    src.write_bytes(b"\x89PNG-one")
    assert BEG.copy_if_stale(src, dst) is True           # not there yet
    assert BEG.copy_if_stale(src, dst) is False          # already beside the page
    assert dst.read_bytes() == b"\x89PNG-one"


def test_a_frame_that_changed_is_copied_again(tmp_path) -> None:
    import os
    src, dst = tmp_path / "src.png", tmp_path / "dst.png"
    src.write_bytes(b"\x89PNG-one")
    BEG.copy_if_stale(src, dst)
    src.write_bytes(b"\x89PNG-two-longer")               # a different size
    assert BEG.copy_if_stale(src, dst) is True
    assert dst.read_bytes() == b"\x89PNG-two-longer"
    src.write_bytes(b"\x89PNG-two-longeR")               # the same size, written later
    os.utime(src, ns=(dst.stat().st_mtime_ns + 10 ** 9,) * 2)
    assert BEG.copy_if_stale(src, dst) is True
    assert dst.read_bytes() == b"\x89PNG-two-longeR"


def test_the_counts_line_build_returns_is_the_line_the_page_carries(tmp_path) -> None:
    """build() tallied the catalogue twice; it now tallies once and hands the line to the page."""
    index, line = BEG.build(CATALOG, FRAMES, tmp_path / "out")
    assert BEG.esc(line) in index.read_text(encoding="utf-8")
    assert line == BEG.counts_line(BEG.compute_counts(BEG.load_cards(CATALOG), BEG.FrameIndex(FRAMES)))


def test_a_build_with_no_flags_does_not_build_a_parser() -> None:
    """The 11 ms argparse costs (shutil + gettext + locale) are not paid by the plain build."""
    args = BEG.parse_args([])
    assert (args.catalog, args.frames, args.out) == (ROOT / BEG.CATALOG_REL, ROOT / BEG.FRAMES_REL,
                                                     ROOT / BEG.OUT_REL)
    assert args.pin is False and args.pin_into is None
    flagged = BEG.parse_args(["--out", str(ROOT / "x"), "--pin"])
    assert flagged.out == ROOT / "x" and flagged.pin is True

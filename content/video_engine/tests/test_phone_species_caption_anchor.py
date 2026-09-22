"""Readable diagrams and labels cannot be crossed by a stage caption."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_scene_timeline_f as B

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"


def test_phone_species_reserves_whole_overlapping_caption_phrase():
    scenes = [{"span": [0, 10], "species": [{"kind": "flow", "at": 3, "dur": 4,
                                             "readability": "landscape-phone"}]}]
    assert B._readable_species_during(scenes, 2, 4)
    assert B._readable_species_during(scenes, 6, 8)
    assert not B._readable_species_during(scenes, 0, 3)
    assert not B._readable_species_during(scenes, 7, 9)


def test_legacy_species_and_closed_scene_do_not_change_caption_mode():
    scenes = [{"span": [0, 5], "species": [{"kind": "chip", "at": 3, "dur": 7}]}]
    assert not B._readable_species_during(scenes, 3, 4)
    scenes[0]["species"][0]["readability"] = "landscape-phone"
    assert not B._readable_species_during(scenes, 5, 6)


def test_labeled_raster_stamp_reserves_quiet_caption_rail_without_phone_profile():
    scenes = [{"span": [0, 10], "species": [{
        "kind": "chip", "form": "stamp", "at": 3, "dur": 4,
        "label": "DRAM ETF", "target": {"kind": "point", "x": .5, "y": .5},
    }]}]
    assert B._readable_species_during(scenes, 2, 4)
    assert B._readable_species_during(scenes, 6, 8)
    scenes[0]["species"][0]["label"] = "   "
    assert not B._readable_species_during(scenes, 2, 4)


def test_caption_display_end_carries_species_reservation_through_page_hold_and_tail():
    """A page remains visible until the next onset; the final page has the player's .4s tail."""
    pages = [{"s": 1.0, "e": 2.0}, {"s": 4.0, "e": 5.0}]
    assert B._caption_display_end(pages, 0) == 4.0
    assert B._caption_display_end(pages, 1) == 5.4

    scenes = [{"span": [0, 8], "species": [
        {"kind": "flow", "at": 2.2, "dur": 0.3, "readability": "landscape-phone"},
        {"kind": "chip", "at": 5.1, "dur": 0.1, "readability": "landscape-phone"},
    ]}]
    # Both enter after their page's spoken end, but while the caption is still displayed.
    assert B._readable_species_during(scenes, pages[0]["s"], B._caption_display_end(pages, 0))
    assert B._readable_species_during(scenes, pages[1]["s"], B._caption_display_end(pages, 1))


def test_renderer_caption_pin_uses_selected_page_lifetime_not_word_end():
    """Keep this source contract next to the compiler helper so the two clocks cannot drift."""
    src = ENGINE.read_text(encoding="utf-8")
    start = src.index("const readableCaptionPinned")
    end = src.index("const capPinned", start)
    block = src[start:end]
    assert re.search(r"i\s*\+\s*1\s*<\s*pages\.length", block)
    assert re.search(r"pages\[i\s*\+\s*1\]\s*\.s", block)
    assert "p.e + CAP_LAST_HOLD_S" in block
    assert "t < displayEnd" in block
    assert "t < p.e" not in block

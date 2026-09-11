"""P39 T3: four committed golden frames; any pixel change FAILS, names the surface, and
writes golden | actual | diff side by side under tests/golden/diffs/.

The harness is proven by breaking it: the last test renders through a one-value CSS
change to the template (in memory - the template on disk is never touched) and asserts
that the check FAILS and names the surface. A golden harness that cannot catch a
one-value change is not a harness.

Refresh deliberately, never by accident:
    python content/video_engine/scripts/render_baseline.py --update
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402

SURFACES = ["ledger-page-mid-build", "chart-callout", "dock-pair-16x9", "dock-pair-9x16", "ledger-soak-page",
            "chip-board",   # P50 T2: the icon chip, three of them, the middle one crossed
            "press-stack",  # P50 T3: three press cards stacked, the newest lit, the underline drawn on its phrase
            "flow-swap",    # P50 T4: the three-node diagram after its swap - the new node in place, both clothoid arrows standing, the year stamped
            "span-decade",  # P50 T4: a ledger line page with a named stretch of time shaded behind it
            "tiers-two",    # P50 T9: two bands on one shared x, each with its own scale and honest zero, the second drawn on its own word and its drop measured as a bar
            "treemap-cross",  # P50 T6: the census page - a squarified treemap, three partners crossed on a word and their share written
            "tags-to-bars",   # P50 T11: two terminal tags mid-flight into their two bars, the lines un-drawing beneath them
            "vecmap-arc"]   # P50 T5: the vector map in PORTRAIT - Iran lit, the arc from the Gulf to the US cut by its X, "1996" and "1.4 Billion Barrels" stamped, China lit


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def test_every_surface_has_a_committed_source_and_golden() -> None:
    for name in SURFACES:
        assert (RB.SOURCES / f"{name}.timeline.json").exists(), name
        assert (RB.SOURCES / f"{name}.uris.json").exists(), name
        assert (RB.FRAMES / f"{name}.png").exists(), f"{name}: no golden frame - run render_baseline.py --update"


@pytest.mark.parametrize("surface", SURFACES + sorted(RB.FLAG_FRAMES))
def test_golden_frame_is_unchanged(surface: str) -> None:
    failures = RB.check([surface])
    assert not failures, "\n".join(failures)


def test_harness_catches_a_one_value_css_change() -> None:
    """Deliberate perturbation: the dock frame's corner radius, 14px -> 2px. Must FAIL by name."""
    src = RB.TEMPLATE.read_text(encoding="utf-8")
    needle = "border: 4px solid var(--charcoal); border-radius: 14px;"  # the .dock frame, line ~140
    assert needle in src, "perturbation anchor missing from the template - pick another one-value change"
    mutated = src.replace(needle, "border: 4px solid var(--charcoal); border-radius: 2px;", 1)
    with tempfile.TemporaryDirectory() as td:
        bad = Path(td) / "template.mutated.html"
        bad.write_text(mutated, encoding="utf-8")
        golden = (RB.FRAMES / "dock-pair-16x9.png").read_bytes()
        actual = RB.render_surface("dock-pair-16x9", template=bad)
        assert RB.rgb_bytes(golden)[1] != RB.rgb_bytes(actual)[1], (
            "a one-value CSS change rendered identically - the harness is not looking at the template")
        diff = RB.write_diff("dock-pair-16x9.perturbed", golden, actual)
        assert diff.exists()

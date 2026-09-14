"""P39 T3: the committed golden frames; any pixel change FAILS, names the surface, and
writes golden | actual | diff side by side under tests/golden/diffs/.

The harness is proven by breaking it: the last test renders through a one-value CSS
change to the template (in memory - the template on disk is never touched) and asserts
that the check FAILS and names the surface. A golden harness that cannot catch a
one-value change is not a harness.

Refresh deliberately, never by accident:
    python content/video_engine/scripts/render_baseline.py --update
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

import render_baseline as RB  # noqa: E402

SURFACES = ["ledger-page-mid-build", "chart-callout", "dock-pair-16x9", "dock-pair-9x16", "ledger-soak-page",
            "chip-board",   # P50 T2: the icon chip, three of them, the middle one crossed
            "press-stack",  # P50 T3: three press cards stacked, the newest lit, the underline drawn on its phrase
            "flow-swap",    # P50 T4: the three-node diagram after its swap - the new node in place, both clothoid arrows standing, the year stamped
            "span-decade",  # P50 T4: a ledger line page with a named stretch of time shaded behind it
            "tiers-two",    # P50 T9: two bands on one shared x, each with its own scale and honest zero, the second drawn on its own word and its drop measured as a bar
            "treemap-cross",  # P50 T6: the census page - a squarified treemap, three partners crossed on a word and their share written
            "tags-to-bars",   # P50 T11: two terminal tags mid-flight into their two bars, the lines un-drawing beneath them
            "data-to-bars",  # E64 / R26-49: the DATA-keyed recast mid-flight (the derived key, the four data in the air, the axes handing over)
            "vecmap-arc",   # P50 T5: the vector map in PORTRAIT - Iran lit, the arc from the Gulf to the US cut by its X, "1996" and "1.4 Billion Barrels" stamped, China lit
            "thread-baseline",   # P50 T15 / HF-16: THE WIRE - the line page's first series still standing under the bars page after the cut, mid-recede
            "art-embed",    # P50 T7: a press card projected onto the plate's declared poster and a still card on its paper - the ART world, the room darkened around them
            "count-array",  # P52 T7: six identical sourced icons on a 2:1 rhombus lattice, the count written as the claim
            "agenda-two",   # P52 T8: two numbered rows revealed one per word, each holding at its own breath
            "ring-dashed-chip",   # P52 T8: the ring's DASHED form round a datum with its flag chip - E56's use, a new form
            "species-proof",      # P52 T7 + T8: the proof page for human gate 3 - the three species on one clock (its other two instants are FLAG_FRAMES)
            "newsreel-band",        # P52 T6: the newsreel band 16:9 - the wire crawling under a docked surface, mid-run
            "melt-page", "melt-splash", "melt-plate",   # P52 T9 / E88: the melt's three endings - the throw at its ball instant (its four @proof-* instants ride PROOF_FRAMES), the chart splash's burst, the plate splash's paint
            "newsreel-strip-9x16",  # P52 T6: 9:16 THE DEFAULT strip law - the caption keeps its E62 band, the crawl runs below it
            "newsreel-strip-above", # P52 T6: 9:16 the ALTERNATIVE (`cap_band: "above"`) - the crawl takes the strip, the caption moves above it
            "occluder-dock",     # P50 T15 / HF-17: a dock BEHIND the plate's foreground layer - the depth cue by occlusion, not blur
            "ledger-extend", "ledger-keyed",   # P48 T3 / T4b: chart_to extend and the keyed recast - on disk since P48, checked from P55 T6 (decision 7)
            "verdict-stack",     # P55 T6: the inline drawStack mid-pile - four cards on their rail spots, the fifth active large near centre (its burst rides PROOF_FRAMES)
            "test-card",         # P55 T6: the inline checklist branch - every question typed, the answers swept by the marker
            "slide-mid", "slide-landed",   # P57 T13 / R26-75: the SLIDE (E87 s3) - one chart page pushing the next onto the stage, read mid-push (the two frames abutting on the stage centre line) and at the landing (the outgoing one exactly off)
            "compare-morph",     # P57 T12 / R26-70b, re-goldened by P57 T12b and again by T12c: the `chart_to compare` verb in its DEFAULT form - E76 s5's BALL: the quoted figure's own outlines (measured by kinetics/contour.mjs, never fetched from a font) sag, ball up, and are carried by morph_a into the comparator's glyphs (its three moving instants ride PROOF_FRAMES)
            "compare-streak",    # P57 T12c: the same row with `form: "streak"` - P57 T12b's TEXT melt, kept whole as a setting and byte-identical to the bytes compare-morph carried before the second correction (its three instants ride PROOF_FRAMES)
            "compare-count",     # P57 T12b: the same row with `form: "count"` - T12's counter, kept whole as a setting and byte-identical to the bytes compare-morph carried before the correction (its mid-count instant rides PROOF_FRAMES)
            "trace-hop",         # P57 T18 / R26-95: the route on a still, pinned BEFORE `trace` became a module - one hop landed with its arrowhead and its stamp, one MID-DRAW, and the plain still-life redraw mid-draw beside them
            "spotlight-hold",    # P57 T19 / R26-96: the light on a datum, pinned BEFORE `spotlight` became a module - the frame dimmed to a feathered hole over a held datum (its two `live`-idle phases ride PROOF_FRAMES)
            "page-figure",       # P57 T20 / R26-98: the written figure, pinned BEFORE `page_species:figure` became a module - E50's number landed at its datum (the peak), written leftward where the page has no room to the right, its sub under it
            "record-typewriter",  # P57 T21 / R26-99: the record document, pinned BEFORE `dock_payload:record` became a module - the quotation mid-type on the NARRATOR's onsets, two characters of its eighth word cut and the cursor after them, one word under the marker with its space outside the stroke (its landing rides PROOF_FRAMES)
            "dip-boundary",      # P57 T23 / R26-100: THE DIP (E47 s1), pinned BEFORE the boundary clock became a module - the BLACK boundary frame between two chart pages, the cut inside it (its ramp's midpoint rides PROOF_FRAMES)
            "spiral-return"]     # P57 T22 / R26-101: THE PAGE VORTEX, pinned BEFORE `page_enter:spiral` became a module - the page coming back UP the drain mid-unwind (uc 0.5), every glyph, mark and series line on its own spiral arm, the charcoal whole behind them (the RETRACT's two phases ride PROOF_FRAMES, off the same surface's first scene)


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


@pytest.mark.parametrize("surface", SURFACES + sorted(RB.FLAG_FRAMES) + sorted(RB.PROOF_FRAMES))   # P52 T7/T8: the proof frames are goldens like any other
def test_golden_frame_is_unchanged(surface: str) -> None:
    failures = RB.check([surface])
    assert not failures, "\n".join(failures)


# ---- P51 T1: THE SPLIT FORM RENDERS THE SAME FRAME ----------------------------------------------
# The engine left the page. The goldens are still captured from the SINGLE-FILE form (inline data,
# inline engine); a build writes the SPLIT form (a shell that imports the engine module and fetches
# the timeline and the asset map beside it). These two prove the split is a delivery format and not
# a render change: the same surface, written the other way, hashes to the same pixels.
SPLIT_PARITY = ["ledger-page-mid-build",   # the ledger world mid-build: the page, its chart, its ink
                "chip-board"]              # + a targeted species, whose painter is inlined by sync_kinetics


def _split_frame(surface: str) -> bytes:
    """Write the surface as a BUILD writes it - player.html + <name>.timeline.json + assets.json +
    a copy of the engine - and capture the golden's instant off the served dir."""
    tl, uris, t, aspect = RB.load_surface(surface)
    with tempfile.TemporaryDirectory() as td:
        page = RB.write_split(Path(td), tl, uris, f"{surface}.timeline.json")
        return RB.render_frame(page, t, aspect)


@pytest.mark.parametrize("surface", SPLIT_PARITY)
def test_the_split_form_hashes_the_same_as_the_single_file(surface: str) -> None:
    golden = (RB.FRAMES / f"{surface}.png").read_bytes()
    actual = _split_frame(surface)
    if RB.rgb_bytes(golden)[1] != RB.rgb_bytes(actual)[1]:
        diff = RB.write_diff(f"{surface}.split", golden, actual)
        raise AssertionError(f"{surface}: the split form renders different pixels - see {diff}")


SPLIT_PAGE_CEILING = 200 * 1024   # the plan's number: a build's page is a page, not an asset bundle
TOKYO_SPLIT = (ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short-t0")


def test_the_split_build_is_small() -> None:
    """A split build holds a page a human can open in an editor, with its data beside it."""
    tl, uris, _t, _a = RB.load_surface("ledger-page-mid-build")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        page = RB.write_split(d, tl, uris, "s.timeline.json")
        assert page.stat().st_size < SPLIT_PAGE_CEILING, page.stat().st_size
        assert (d / RB.ASSETS_NAME).exists() and (d / RB.ENGINE.name).exists()
        manifest = json.loads((d / RB.MANIFEST_NAME).read_text(encoding="utf-8"))
        assert manifest["engine_sha256"] == hashlib.sha256(RB.ENGINE.read_bytes()).hexdigest()
        assert manifest["timeline"] == "s.timeline.json"
    if (TOKYO_SPLIT / "player.html").exists():   # the test bed, when it has been rebuilt since the split
        page = TOKYO_SPLIT / "player.html"
        assert page.stat().st_size < SPLIT_PAGE_CEILING, f"{page}: {page.stat().st_size} bytes"
        assert (TOKYO_SPLIT / RB.ASSETS_NAME).stat().st_size > page.stat().st_size * 10, (
            "the asset map should carry the weight the page used to")


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

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
            "page-life-still", "page-life-live",   # R26-228 / E99 s82 (e), re-rendered by R26-234 / E99 s83: the page's INTERIOR at its idle - one key apart (`world.idle` absent against "live"). The still half is the page every cut has drawn (the row's kind never reached it); the live half carries the ELECTRIC and nothing else - the lead point that stays and sparks, the glow at the approved 9:16 page's share of the frame pulsing on the tip's clock - while every word holds still inside the page's own exterior breath (s83 took the per-word walk out; the bands are read by `test_the_live_page_keeps_its_electric_and_holds_its_words_still`). Their +2 s halves ride PROOF_FRAMES
            "page-build-lines", "page-build-lines-4th",   # R26-226 / E99 s82: A MULTI-LINE PAGE BUILDS LINE BY LINE - the same four-series page as `page-life-*` with `;build=lines:1.2` on the row, read at series 1's midpoint (line 1 whole and labelled, line 2 half drawn, lines 3 and 4 not begun) and at series 3's (three whole and labelled, the fourth drawing). The operator: "draw the first line completely, label it, badge it, draw the 2nd line completely, badge it" - the crawl that stopped is gone and no line pauses mid-draw
            "page-rescale-follow", "page-rescale-follow-yield",   # R26-233 / E99 s82: THE AXIS YIELDS TO THE LINE THAT PUSHES IT - three landed lines on the scale the page was born on and a fourth drawn on its word with `chart_to rescale follow: "Memory"`, read BEFORE the yield (the climb at 225, its extremum with the air still under the standing top: the landed ink has not moved a pixel) and MID-YIELD (the climb at 385.6 asking for 408.7, the live top 408.8, the three tags 33.8 px lower, all five ticks lit). The critic on the H unit: the reveal's rescale slid the landed lines 253 px down beside the line instead of with it
            "plate-drift",  # R26-133, re-authored by P61 T14 to the ruling that closed it (E99 s55): the plate world authored `idle: "drift"`, the dial PAINTING it at `;drift=30` - the amplitude the operator named for long form, after E99 s38 refused the 2 px walk as a motion nobody can see
            "plate-alive",  # P61 T14 / E99 s55: THE ALIVE PLATE under the whole depth stack - the ambient lane's generated harbour water as the background WALL, the split's mid / subject / occluder planes over it, the one camera at each plane's k and the 30 px drift, judged at u 0.28 of the focus zoom and 2.50 s into the water's own loop
            "tiers-two",    # P50 T9: two bands on one shared x, each with its own scale and honest zero, the second drawn on its own word and its drop measured as a bar
            "treemap-cross",  # P50 T6: the census page - a squarified treemap, three partners crossed on a word and their share written
            "tags-to-bars",   # P50 T11: two terminal tags mid-flight into their two bars, the lines un-drawing beneath them
            "data-to-bars",  # E64 / R26-49: the DATA-keyed recast mid-flight (the derived key, the four data in the air, the axes handing over)
            "vecmap-arc",   # P50 T5: the vector map in PORTRAIT - Iran lit, the arc from the Gulf to the US cut by its X, "1996" and "1.4 Billion Barrels" stamped, China lit
            "thread-baseline",   # P50 T15 / HF-16: THE WIRE - the line page's first series still standing under the bars page after the cut, mid-recede
            "art-embed",    # P50 T7: a press card projected onto the plate's declared poster and a still card on its paper - the ART world, the room darkened around them
            "count-array",  # P52 T7: six identical sourced icons on a 2:1 rhombus lattice, the count written as the claim
            "agenda-two",   # P52 T8: two numbered rows revealed one per word, each holding at its own breath
            "agenda-page",  # P61 T8 / E99 s16: the same species' PAGE form - the plate version of the list: the rows filling the board on their own mounts, a title over them, and each row's CATALOGUED icon (E93/E94) stamped on after its sentence (its three moving instants ride PROOF_FRAMES)
            "ring-dashed-chip",   # P52 T8: the ring's DASHED form round a datum with its flag chip - E56's use, a new form
            "species-proof",      # P52 T7 + T8: the proof page for human gate 3 - the three species on one clock (its other two instants are FLAG_FRAMES)
            "newsreel-band",        # P52 T6: the newsreel band 16:9 - the wire crawling under a docked surface, mid-run
            "melt-ball-roll",   # R26-118 / E88 s6-s7: the melt ball with MASS - mid-roll, its own ink mark turned, the living drop surface out of round (its landing and its rest ride PROOF_FRAMES)
            "melt-page", "melt-splash", "melt-plate",   # P52 T9 / E88: the melt's three endings - the throw at its ball instant (its four @proof-* instants ride PROOF_FRAMES), the chart splash's burst, the plate splash's paint
            "melt-gather",      # P61 T6 / E99 s2: THE GATHER - `melt:gather:weight:splash:plate`, the page's marks and words travelling the vortex to ONE point and amassing on it (no blur, no wipe), the point dense and vibrating, the splash painting the committed dock plate up through its stains (its point, its bloom and its landed plate ride PROOF_FRAMES)
            "melt-morph",       # P61 T3 / R26-117: THE HAND-OVER FRAME of `melt:morph` - the ball finished and the next page's page_enter:morph opening on its ring as the prop, one clock, no cut (its ball, its midpoint and its build ride PROOF_FRAMES)
            "morph-planted",    # P48 T5b / R26-16: THE PLANTED SOURCE - the traced silhouette of the plate's own dark form standing on the arriving page's board exactly where it stood, before it deforms (its midpoint rides PROOF_FRAMES)
            "melt-gather-morph",   # P61 T6 proof B / E99 s2: THE GATHER INTO A FULL CHART - `melt:gather:morph`, the two composing by construction; the gather at its midpoint (its point and the chart it becomes ride PROOF_FRAMES)
            "newsreel-strip-9x16",  # P52 T6: 9:16 THE DEFAULT strip law - the caption keeps its E62 band, the crawl runs below it
            "newsreel-strip-above", # P52 T6: 9:16 the ALTERNATIVE (`cap_band: "above"`) - the crawl takes the strip, the caption moves above it
            "occluder-dock",     # P50 T15 / HF-17: a dock BEHIND the plate's foreground layer - the depth cue by occlusion, not blur
            "form-extruded-bar",   # P58 T5 / E98 s3: the EXTRUDED BAR - every bar a prism behind its own face, the same four values `thread-baseline` draws flat (its build and its leaving ride PROOF_FRAMES)
            "form-tilted-line",    # P58 T5 / E98 s3: the TILTED-PLANE LINE - the same page `ledger-page-mid-build` draws flat, its plot projected onto the compiler's four corners, its numbers upright (its build and its leaving ride PROOF_FRAMES)
            "page-depth",        # P58 T4 / E98 s3: the ledger page as a CARD AT A DEPTH - `plane=tilt:14,y` turned by the embed grammar's own homography and `depth=1.15` taking that share of one focus zoom tied to a landing, over the layered dock plate (its build and its leaving ride PROOF_FRAMES)
            "melt-depth",        # P58 T6 (b) / E98 s4: THE BALL AT A PLANE - `melt:weight:depth=1.15`, the ink ball melting, landing and thrown at the `-mid` plane under a landing-tied focus zoom (its ball instant rides PROOF_FRAMES)
            "dock-depth",        # P58 T6 (a) / E98 s4: a DOCK ON A LAYER'S PLANE - `depth=1.15` on the dock row, over the same layered plate and the same landing-tied focus zoom `camera-layers` reads flat (its mid-move instant rides PROOF_FRAMES)
            "camera-layers",     # P58 T3 / E59 + doc 24: ONE eye over four DEPTH PLANES - the dock plate split into -far / -mid / subject / -near, taking the shares 1.0 / 1.15 / 1.275 / 1.40 of one authored focus zoom tied to a landing (its locked instant and its mid-zoom ride PROOF_FRAMES)
            "ledger-extend", "ledger-keyed",   # P48 T3 / T4b: chart_to extend and the keyed recast - on disk since P48, checked from P55 T6 (decision 7)
            "verdict-stack",     # P55 T6: the inline drawStack mid-pile - four cards on their rail spots, the fifth active large near centre (its burst rides PROOF_FRAMES)
            "test-card",         # P55 T6: the inline checklist branch - every question typed, the answers swept by the marker
            "slide-depth",       # P58 T6 (c) / E98 s4: THE SLIDE THROUGH THE DEPTH - `slide:left:depth=0.85,1.15` under a landing-tied focus zoom, the base frame its LANDING (identical to the flat slide's; its mid-slide instant rides PROOF_FRAMES)
            "door-open",         # E98 s7 / R26-134: THE EVIDENCE DOOR - a flat chart page swings open on its left edge onto the plate mounted beneath it; the base frame is its landing (u = 1, the plate alone), its early and mid instants ride PROOF_FRAMES
            "slide-mid", "slide-landed",   # P57 T13 / R26-75: the SLIDE (E87 s3) - one chart page pushing the next onto the stage, read mid-push (the two frames abutting on the stage centre line) and at the landing (the outgoing one exactly off)
            "compare-morph",     # P57 T12 / R26-70b, re-goldened by P57 T12b and again by T12c: the `chart_to compare` verb in its DEFAULT form - E76 s5's BALL: the quoted figure's own outlines (measured by kinetics/contour.mjs, never fetched from a font) sag, ball up, and are carried by morph_a into the comparator's glyphs (its three moving instants ride PROOF_FRAMES)
            "compare-streak",    # P57 T12c: the same row with `form: "streak"` - P57 T12b's TEXT melt, kept whole as a setting and byte-identical to the bytes compare-morph carried before the second correction (its three instants ride PROOF_FRAMES)
            "compare-count",     # P57 T12b: the same row with `form: "count"` - T12's counter, kept whole as a setting and byte-identical to the bytes compare-morph carried before the correction (its mid-count instant rides PROOF_FRAMES)
            "trace-hop",         # P57 T18 / R26-95: the route on a still, pinned BEFORE `trace` became a module - one hop landed with its arrowhead and its stamp, one MID-DRAW, and the plain still-life redraw mid-draw beside them
            "spotlight-hold",    # P57 T19 / R26-96: the light on a datum, pinned BEFORE `spotlight` became a module - the frame dimmed to a feathered hole over a held datum (its two `live`-idle phases ride PROOF_FRAMES)
            "page-figure",       # P57 T20 / R26-98: the written figure, pinned BEFORE `page_species:figure` became a module - E50's number landed at its datum (the peak), written leftward where the page has no room to the right, its sub under it
            "record-typewriter",  # P57 T21 / R26-99: the record document, pinned BEFORE `dock_payload:record` became a module - the quotation mid-type on the NARRATOR's onsets, two characters of its eighth word cut and the cursor after them, one word under the marker with its space outside the stroke (its landing rides PROOF_FRAMES)
            "dip-boundary",      # P57 T23 / R26-100: THE DIP (E47 s1), pinned BEFORE the boundary clock became a module - the BLACK boundary frame between two chart pages, the cut inside it (its ramp's midpoint rides PROOF_FRAMES)
            "remake-line-to-bars", "remake-bars-to-line",   # P61 T2 / E99 s34: THE WHOLE-CHART REMAKE both ways - the whole chart becoming the whole other chart, judged at u 0.50, the instant neither chart is drawable as itself (its quarter and three-quarter instants ride PROOF_FRAMES)
            "spiral-return"]     # P57 T22 / R26-101: THE PAGE VORTEX, pinned BEFORE `page_enter:spiral` became a module - the page coming back UP the drain mid-unwind (uc 0.5), every glyph, mark and series line on its own spiral arm, the charcoal whole behind them (the RETRACT's two phases ride PROOF_FRAMES, off the same surface's first scene)


# P61 T9 (b): THE PAGES. A golden need not be a timeline - the effects gallery is a static review
# page, and "a faster build" must never be allowed to mean "renders less", so its three frames (the
# top, one mid-page axis section, the foot) are pinned exactly like a surface: a committed source
# beside the others (`<name>.page.json`, the capture recipe), a committed frame in tests/golden/
# frames/, and any pixel change FAILS. They are a SIBLING of SURFACES, never a member: every name in
# SURFACES is instantiated by render_baseline through the player template, which a page has no
# #scrub for. The renderer and the comparison live in test_effects_gallery.py - it owns the browser,
# this file owns the register.
#     python content/video_engine/scripts/build_effects_gallery.py --pin       # refresh, deliberately
PAGE_SURFACES = ["gallery-top",            # the header, its counts line and the nav
                 "gallery-axis-kinetics",  # a mid-page axis section: 17 tiles and their copied proofs
                 "gallery-foot"]           # the foot - the last recipe tile the page has to draw


def test_every_page_surface_has_a_committed_source_and_golden() -> None:
    for name in PAGE_SURFACES:
        assert (RB.SOURCES / f"{name}.page.json").exists(), f"{name}: no source - run build_golden_sources.py {name}"
        assert (RB.FRAMES / f"{name}.png").exists(), f"{name}: no golden frame - run build_effects_gallery.py --pin"


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


# ---- R26-234 / E99 s83: THE ELECTRIC CARRIES THE LIFE; THE WORDS HOLD STILL ----------------------
# The operator, on the H bed's copy f: *"way too much interior drift now, it causes us to draw the
# memory line wrong, there's 2 different pointers there, and makes people probably get eye fatigue
# trying to follow, i think we keep the exterior drift, remove the interior drift, keep the
# electric/glow etc let that carry the life instead of drift which just reads as chaos kind of."*
# R26-228 had given the page's interior FOUR lives at once; s83 keeps the two that belong to the line
# (the lead point's spark + halo, the stroke's bloom pulse) and deletes the per-word walk.
#
# The pair is the proof, and it is read as BANDS rather than as one hash, because the halves are not
# the same page in the same place: `live` = breath + drift, so the live half's whole page is offset by
# its own exterior drift (`.lp-page` matrix translate -1.879, -1.137 px at t = 9 and -1.694, -0.070 at
# t = 11 - measured; nothing else differs outside the electric). A word band therefore cannot be
# pixel-identical between the halves; what it CAN be - and now is - is the still band moved rigidly by
# that one page-wide number and nothing more. So each band is matched at every whole-pixel offset
# within +/-8 and asked two questions: which offset fits best, and how much still differs after it.
#   * every band, word or electric, fits best at the PAGE's own drift - one mechanism moves the page.
#     Before s83 the word bands each fitted a DIFFERENT offset (the y ticks -7,-4; the title +4,-1; the
#     citation -4,-1; the sub -1,+1 - each word on its own phase, which is what read as chaos).
#   * a WORD band is then explained: at most 16.3 % of it still differs (measured; the ceiling is 25 %),
#     and that residue is the sub-pixel part of the offset on high-contrast ink.
#   * an ELECTRIC band is NOT explained by any offset: 41.7 % to 79.2 % of it still differs (measured;
#     the floor is 35 %), because the still half has no lead point at all and its bloom is 6 px against
#     the live half's 11.2 - 14.1.
PAGE_LIFE_DRIFT = {"": (-2, -1), "@proof-plus2": (-2, 0)}   # the page's exterior drift at t = 9 / t = 11, to the whole pixel
ELECTRIC_BANDS = {   # (x, y, w, h) in stage px on the 1920x1080 frame
    "lead point / orange": (960, 365, 61, 61),       # the MEMORY MAKERS series' landed tip + its halo
    "lead point / teal": (960, 578, 61, 61),         # SEMICONDUCTORS
    "lead point / blue + grey": (960, 666, 61, 61),   # MEGA-CAP over the S&P, two tips a hair apart
    "the stroke": (300, 690, 400, 50),               # a strip across the two flattest lines: the bloom's own width
}
WORD_BANDS = {
    "y tick labels": (154, 388, 70, 286),
    "x tick labels": (232, 766, 716, 50),
    "end tag / memory makers": (1030, 374, 590, 40),   # from x 1030: clear of the orange tip's halo
    "end tag / semiconductors": (1030, 588, 590, 40),
    "title": (58, 34, 1024, 80),
    "sub": (138, 106, 1102, 48),
    "citation": (134, 958, 522, 56),
}
BAND_PAD = 8            # the offsets tried, in whole px, each way
WORD_CEILING = 25.0     # a word band's share still differing after the best offset (measured max 16.3 %)
ELECTRIC_FLOOR = 35.0   # an electric band's, which no offset explains (measured min 41.7 %)


def _band_fit(still, live, rect: tuple[int, int, int, int]) -> tuple[float, tuple[int, int], float]:
    """(share differing at rest, the best whole-px offset, the share still differing after it)."""
    import numpy as np
    x, y, w, h = rect
    A = still[y:y + h, x:x + w].astype(np.int16)
    rest = 100.0 * (np.abs(A - live[y:y + h, x:x + w].astype(np.int16)).max(axis=2) > 2).sum() / (w * h)
    best = None
    for dy in range(-BAND_PAD, BAND_PAD + 1):
        for dx in range(-BAND_PAD, BAND_PAD + 1):
            B = live[y + dy:y + dy + h, x + dx:x + dx + w].astype(np.int16)
            if B.shape != A.shape:
                continue
            d = np.abs(A - B)
            if best is None or d.mean() < best[0]:
                best = (float(d.mean()), (dx, dy), 100.0 * (d.max(axis=2) > 2).sum() / (w * h))
    return rest, best[1], best[2]


def _page_life_halves(suffix: str):
    import numpy as np
    from PIL import Image
    return [np.asarray(Image.open(RB.FRAMES / f"page-life-{half}{suffix}.png").convert("RGB"))
            for half in ("still", "live")]


@pytest.mark.parametrize("suffix", sorted(PAGE_LIFE_DRIFT))
def test_the_live_page_keeps_its_electric_and_holds_its_words_still(suffix: str) -> None:
    shift = PAGE_LIFE_DRIFT[suffix]
    still, live = _page_life_halves(suffix)
    for name, rect in WORD_BANDS.items():
        rest, fit, after = _band_fit(still, live, rect)
        assert fit == shift, (
            f"{name}{suffix}: fits best at {fit}, not the page's own drift {shift} - something inside "
            f"the page is moving on its own again (E99 s83: the interior word walk is gone)")
        assert after <= WORD_CEILING, (
            f"{name}{suffix}: {after:.2f} % of the band still differs once the page's drift is taken "
            f"out ({rest:.2f} % before it) - the words are not holding still inside the breath")
    for name, rect in ELECTRIC_BANDS.items():
        rest, fit, after = _band_fit(still, live, rect)
        assert rest > 0, f"{name}{suffix}: still and live are identical here - the electric is gone (E99 s83)"
        assert fit == shift, f"{name}{suffix}: fits best at {fit}, not the page's own drift {shift}"
        assert after >= ELECTRIC_FLOOR, (
            f"{name}{suffix}: only {after:.2f} % of the band differs once the page's drift is taken out "
            f"- the lead point's spark / halo and the stroke's bloom pulse are what carry the life now")


# ---- R26-234 / E99 s83, at the REVEAL: a line's pointer is ONE thing ------------------------------
# The bands above read the page LANDED. The ruling's fourth clause is about the page DRAWING - *"a
# line's pointer is ONE thing - the lead point; nothing else on the line moves while it draws"* - and
# that is read off the DOM, because it is a claim about what moves RELATIVE to what: every box is taken
# against `.lp-page`'s own box, so the page's exterior breath and drift are divided out and what is
# left is the interior alone.
PAGE_LIFE_REVEAL = (5.8, 6.0)   # mid-draw on both halves: all four series drawing (stroke-dashoffset 15.7 / 24.5 / 37.3 / 70.9, then 8.1 / 12.6 / 19.3 / 36.6)
REVEAL_WORD_CEILING = 2.5       # px a word may travel between those instants: the page's own BREATH carries it radially (measured max 1.97, and it grows with the word's radius from the page centre - one rigid scale, E99 s65's "attributable" motion)
REVEAL_TIP_FLOOR = 5.0          # px the lead point travels over the same 0.2 s (measured 7.4 - 34.7): the pointer, and the only thing moving on the line
INTERIOR_JS = """
() => {
  const pg = document.querySelector('.lp-page');
  const pb = pg.getBoundingClientRect();
  const rel = (el) => { const b = el.getBoundingClientRect(); return [+(b.x - pb.x).toFixed(3), +(b.y - pb.y).toFixed(3)]; };
  const out = { words: [], tips: [], translates: [] };
  pg.querySelectorAll('.lp-title, .lp-sub, .lp-src').forEach((el) => out.words.push(['div:' + el.className, rel(el)]));
  pg.querySelectorAll('svg text').forEach((el) => { if (!el.getBoundingClientRect().width) return;
    out.words.push(['text:' + (el.getAttribute('class') || '') + ':' + (el.textContent || '').slice(0, 12), rel(el)]); });
  pg.querySelectorAll('*').forEach((el) => { if (el.style && el.style.translate) out.translates.push(el.tagName + ' ' + el.style.translate); });
  pg.querySelectorAll('svg circle').forEach((el) => { if (el.getAttribute('opacity') === '0') return;
    out.tips.push([el.getAttribute('r'), el.style.filter || '', rel(el)]); });
  return out;
}
"""


def _page_interior(surface: str, ts: tuple[float, ...]) -> dict:
    """The page's interior at each t, every box relative to the page's own: {t: {words, tips, translates}}."""
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(surface)
    tl = dict(tl, kinetics={"idle": True})
    w, h = RB.STAGE[aspect]
    out: dict = {}
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"{surface}.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                for t in ts:
                    page.evaluate("t => { const s = document.getElementById('scrub');"
                                  " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                    out[t] = page.evaluate(INTERIOR_JS)
                browser.close()
        finally:
            srv.shutdown()
    return out


def test_at_the_reveal_only_the_lead_point_moves_on_a_live_line() -> None:
    still = _page_interior("page-life-still", PAGE_LIFE_REVEAL)
    live = _page_interior("page-life-live", PAGE_LIFE_REVEAL)
    for t in PAGE_LIFE_REVEAL:
        assert live[t]["translates"] == [], (
            f"t={t}: {live[t]['translates']} - an interior element is walking again; E99 s83 deleted the "
            f"per-word walk (`lpPaintWordLife` / `lpPaintChartLife`), it was not left on a dial")
        assert still[t]["translates"] == [], f"t={t}: {still[t]['translates']}"
        for (kl, pl), (ks, ps) in zip(live[t]["words"], still[t]["words"]):
            assert kl == ks, (kl, ks)
            assert abs(pl[0] - ps[0]) < 0.01 and abs(pl[1] - ps[1]) < 0.01, (
                f"t={t}: {kl} sits at {pl} inside the live page and {ps} inside the still one - the words "
                f"do not hold their place inside the breathing page (E99 s83)")
        assert len(live[t]["tips"]) == 4 and all("drop-shadow" in f for _r, f, _p in live[t]["tips"]), (
            f"t={t}: the drawing lines' lead points lost their halo - the ELECTRIC is what carries the life")
        assert all(f == "" for _r, f, _p in still[t]["tips"]), f"t={t}: the still half grew a halo"
    a, b = (live[t] for t in PAGE_LIFE_REVEAL)
    for (_ka, pa), (_kb, pb) in zip(a["words"], b["words"]):
        assert abs(pa[0] - pb[0]) <= REVEAL_WORD_CEILING and abs(pa[1] - pb[1]) <= REVEAL_WORD_CEILING, (
            f"a word travelled {pa} -> {pb} inside the page between the two instants - more than the page's "
            f"own breath carries it ({REVEAL_WORD_CEILING} px)")
    for (_ra, _fa, pa), (_rb, _fb, pb) in zip(a["tips"], b["tips"]):
        assert ((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2) ** 0.5 >= REVEAL_TIP_FLOOR, (
            f"the lead point moved {pa} -> {pb}: the pointer is the thing that moves on a drawing line")

"""E47 (operator 2026-09-06): the DIP through black and the BLURZOOM, in pixels.

The two world-change transitions the measured reference actually uses (doc 46 s46.5;
docs/research/motion/WEALTH_LOGIC_TRANSITIONS_MEASURED.md - 35 dips at 14 frames, 28
blur-zooms at a median of 8) are proved here the way the golden harness proves anything:
a synthetic 9:16 build with two plates goes through `render_baseline.render_frame`, and
the numbers come off the frames.

  dip       the boundary frame is black - mean luminance under 5% of either plate's - and
            the luminance falls monotonically into it and rises monotonically out of it.
  blur-zoom the frame beside the boundary is SOFTER (lower Laplacian variance) than the
            frame before the transition starts, and a known band on the outgoing plate is
            ~BLURZOOM_SCALE times its steady height at the boundary.
  both      two renders of the same frame in two browsers are byte-identical (P39 T2's law).

The compiler's default rule and the motion gate's credit are unit-tested here too; the
gate's M10 behaviour has its own pair in test_gate_motion_density.py.
"""
from __future__ import annotations

import hashlib
import io
import struct
import sys
import tempfile
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

sys.path.insert(0, str(RB.GOLDEN))
import build_golden_sources as BG  # noqa: E402

BOUNDARY = 6.0          # both builds change world here
RUNTIME = 12.0
ASPECT = "9:16"
GROUND, BAND = (230, 230, 230), (30, 30, 30)
BAND_ROWS = (64, 128)   # of 192: a third of the plate, centred - the "known element" the scale is measured on
PLATE_H = 192


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_chromium = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---------------------------------------------------------------- the synthetic build
def _png_band(w: int, h: int, ground: tuple, band: tuple, y0: int, y1: int) -> bytes:
    """A solid plate with one horizontal band - BG.png_solid with something to measure on it."""
    raw = b"".join(b"\x00" + bytes(band if y0 <= y < y1 else ground) * w for y in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def _build(exit_id: str, banded: bool) -> tuple[dict, dict]:
    """Two plates, one boundary at BOUNDARY carrying `exit_id`, no docks, no captions:
    every pixel that moves in this build belongs to the transition under test."""
    plate_a = (_png_band(108, PLATE_H, GROUND, BAND, *BAND_ROWS) if banded
               else BG.png_solid(108, PLATE_H, GROUND))
    world = lambda aid: {"asset_id": aid, "sha256": "0" * 64, "ken_burns": {"scale": 0.0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world("plate-a"), "exit": "cut",
               "span": [0.0, BOUNDARY], "docks": [], "species": []},
              {"scene_id": "s02", "world": world("plate-b"), "exit": exit_id,
               "span": [BOUNDARY, RUNTIME], "docks": [], "species": []}]
    tl = {"schema_version": "scene_evidence_timeline.v1", "runtime_s": RUNTIME, "aspect": ASPECT,
          "title": "E47", "subtitle": "dip / blur-zoom", "episode_id": "e47", "project_id": "e47",
          "narration": {"canonical_hash": "0" * 64, "words_path": ""},
          "captions": [], "caption_pages": [], "caption_modes": [], "sound": [],
          "evidence": {}, "scenes": scenes}
    uris = {"plate-a": BG.uri("image/png", plate_a),
            "plate-b": BG.uri("image/png", BG.png_solid(108, PLATE_H, (200, 200, 200))),
            "__audio__": BG.uri("audio/wav", BG.silent_wav(2.0))}
    return tl, uris


def _frame(tl: dict, uris: dict, t: float) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "e47.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        return RB.render_frame(html, t, ASPECT)


# ---------------------------------------------------------------- what the frames measure
def _grey(png: bytes):
    from PIL import Image
    return Image.open(io.BytesIO(png)).convert("L")


def _mean_luma(png: bytes) -> float:
    px = _grey(png).tobytes()
    return sum(px) / len(px)


def _laplacian_variance(png: bytes) -> float:
    """Sharpness, the same series the reference was measured with (measure_cut_kinds.py's `S`)."""
    im = _grey(png)
    w, h = im.size
    px = im.load()
    vals = [4 * px[x, y] - px[x - 1, y] - px[x + 1, y] - px[x, y - 1] - px[x, y + 1]
            for y in range(1, h - 1, 4) for x in range(1, w - 1, 4)]
    m = sum(vals) / len(vals)
    return sum((v - m) ** 2 for v in vals) / len(vals)


def _band_height(png: bytes) -> int:
    """The dark band's height down the centre column: the known element the zoom magnifies.
    A symmetric blur moves both of its 50% crossings by the same amount, so the count holds."""
    im = _grey(png)
    w, h = im.size
    px = im.load()
    x = w // 2
    mid = (GROUND[0] + BAND[0]) / 2
    return sum(1 for y in range(h) if px[x, y] < mid)


# ---------------------------------------------------------------- the dip
@needs_chromium
def test_the_dip_puts_a_black_frame_on_the_boundary_and_ramps_into_and_out_of_it():
    tl, uris = _build("dip", banded=False)
    offs = [-0.24, -0.16, -0.08, 0.0, 0.08, 0.16, 0.24]
    luma = [_mean_luma(_frame(tl, uris, BOUNDARY + d)) for d in offs]
    plate = _mean_luma(_frame(tl, uris, 1.0))
    report = ", ".join(f"{d:+.2f}s={v:.1f}" for d, v in zip(offs, luma))
    assert plate > 150, f"the plates are not bright enough to judge a dip: {plate:.1f}"
    assert luma[3] < 0.05 * plate, f"the boundary frame is not black: {luma[3]:.2f} vs plate {plate:.1f} ({report})"
    down = luma[:4]
    up = luma[3:]
    assert all(a > b for a, b in zip(down, down[1:])), f"the ramp into the black is not monotonic: {report}"
    assert all(a < b for a, b in zip(up, up[1:])), f"the ramp out of the black is not monotonic: {report}"
    # the ramp is DIP_S/2 wide on each side: a frame a whole DIP_S before the boundary is untouched
    assert _mean_luma(_frame(tl, uris, BOUNDARY - 0.47)) > 0.98 * plate


# ---------------------------------------------------------------- the blur-zoom
@needs_chromium
def test_the_blurzoom_softens_the_outgoing_plate_and_magnifies_it_by_blurzoom_scale():
    tl, uris = _build("blurzoom", banded=True)
    before = _frame(tl, uris, BOUNDARY - 0.30)      # outside the 0.27s window: the steady plate
    soft = _frame(tl, uris, BOUNDARY - 0.05)        # inside it, past half way
    edge = _frame(tl, uris, BOUNDARY - 0.01)        # the last frame before the switch: full magnification
    # (0.01 is the floor: #scrub carries step="0.01", so a finer t snaps to the boundary itself)
    s_before, s_soft = _laplacian_variance(before), _laplacian_variance(soft)
    assert s_soft < 0.5 * s_before, f"the frame beside the boundary is not softer: S {s_before:.1f} -> {s_soft:.1f}"
    steady, magnified = _band_height(before), _band_height(edge)
    ratio = magnified / steady
    assert 1.30 <= ratio <= 1.40, (
        f"the outgoing plate magnifies {ratio:.3f}x, not ~1.35x (band {steady} -> {magnified} px)")


# ---------------------------------------------------------------- determinism (P39 T2's law)
@needs_chromium
@pytest.mark.parametrize("exit_id,banded,t", [("dip", False, BOUNDARY - 0.10),
                                              ("blurzoom", True, BOUNDARY - 0.05),
                                              ("slide:up", True, BOUNDARY + 0.30),
                                              ("door", True, BOUNDARY + 0.45)])   # E98 s7: mid-swing, the matrix3d a pure function of t
def test_a_transition_frame_renders_identically_in_two_browsers(exit_id: str, banded: bool, t: float):
    tl, uris = _build(exit_id, banded)
    a, b = RB.rgb_bytes(_frame(tl, uris, t)), RB.rgb_bytes(_frame(tl, uris, t))
    assert a[0] == b[0] == RB.STAGE[ASPECT]
    assert hashlib.sha256(a[1]).hexdigest() == hashlib.sha256(b[1]).hexdigest(), (
        f"{exit_id}: two renders of the same frame differ - the transition is not a pure function of t")


# ---------------------------------------------------------------- the slide (E87 s3 / R26-75)
SLIDE_S = 0.6           # build_scene_timeline_f.SLIDE_S and the engine's - the default this build declares none against


def _row_means(png: bytes) -> list[float]:
    """One mean per row of the stage - the profile a vertical push moves through."""
    im = _grey(png)
    w, h = im.size
    px = im.load()
    return [sum(px[x, y] for x in range(0, w, 4)) / len(range(0, w, 4)) for y in range(h)]


def _first_row_below(rows: list[float], lo: float, hi: float, y0: int) -> int:
    """The first row at or after y0 whose mean sits inside (lo, hi) - the incoming plate's own value."""
    return next((y for y in range(y0, len(rows)) if lo < rows[y] < hi), -1)


def _band_rows(rows: list[float]) -> tuple[int, int]:
    """The outgoing plate's band, top and bottom row (-1, -1 once it has left the stage)."""
    dark = [y for y, v in enumerate(rows) if v < 130]
    return (dark[0], dark[-1]) if dark else (-1, -1)


@needs_chromium
def test_the_slide_pushes_both_worlds_together_and_the_two_abut_at_the_seam():
    """E87 s3 (the operator: *"literally pushing out one frame with the next, so that you keep some of that
    congruency"*). `slide:up` on a BANDED outgoing plate: the band is the known element, and a vertical push moves it.

    The stage is 9:16 and the plate is 108x192 - the same aspect, so `cover` crops nothing and the band's rows 64-128
    of 192 sit at 1/3 - 2/3 of the .world box, which spans 1.1 H from -0.05 H (the Ken Burns overhang). At u = 0.5 the
    outgoing box has travelled 0.55 H up, so its trailing edge - and therefore the SEAM - is exactly at mid-stage, and
    the band has moved from 0.353-0.683 H to the top 0.133 H of the frame. Three statements in one frame:
    the outgoing world moved, the incoming world moved by the same distance, and they abut with no gap and no overlap."""
    tl, uris = _build("slide:up", banded=True)
    mid = _row_means(_frame(tl, uris, BOUNDARY + SLIDE_S / 2))
    before = _row_means(_frame(tl, uris, BOUNDARY - 0.10))
    h = len(mid)
    incoming = 200.0     # plate-b's own grey; plate-a is GROUND 230 with a BAND at 30
    # 1. the OUTGOING world moved: the band was nowhere near the top of the frame, and at mid-slide it is there
    assert before[int(0.05 * h)] > 200, f"the band is not where the build put it: row 5% = {before[int(0.05 * h)]:.1f}"
    assert mid[int(0.05 * h)] < 100, f"the outgoing world did not move up: row 5% = {mid[int(0.05 * h)]:.1f}"
    assert mid[int(0.30 * h)] > 200, f"the outgoing plate's ground is not under the band: row 30% = {mid[int(0.30 * h)]:.1f}"
    # 2. the INCOMING world is on stage with it, at its own value
    assert abs(mid[int(0.75 * h)] - incoming) < 3, f"the incoming plate is not on stage: row 75% = {mid[int(0.75 * h)]:.1f}"
    # 3. they ABUT at mid-stage: one distance, opposite ends (a stage-width travel would put the seam 5% early)
    seam = _first_row_below(mid, incoming - 3, incoming + 3, int(0.2 * h))
    assert abs(seam - h / 2) <= 2, f"the seam is at row {seam} of {h}, not at mid-stage - the two worlds do not abut"


@needs_chromium
def test_a_slide_arrives_on_the_cut_and_lands_exactly_at_its_own_length():
    """The congruency the ruling asks for, in pixels: the frame just after the boundary is the frame just before it
    (the incoming world is still wholly off-stage - nothing flashes, nothing is half-arrived), and at SLIDE_S the
    outgoing world is wholly gone. Between them the seam travels one way only."""
    tl, uris = _build("slide:up", banded=True)
    before, after = _row_means(_frame(tl, uris, BOUNDARY - 0.01)), _row_means(_frame(tl, uris, BOUNDARY + 0.01))
    # judged on the band's place and the frame's own mean, not row by row: this build's plate is 192 px shown 11x, so
    # its band edge is a ~10-row ramp, and clipping a layer to the stage rect resamples that ramp's sub-pixel phase
    # (measured 2026-09-14 - a fixture artifact of an upscaled synthetic PNG; a page is DOM and a real plate is full
    # res). A flash, or a world half arrived, moves the band rows and the mean by far more than this.
    assert abs(_band_rows(before)[0] - _band_rows(after)[0]) <= 2 and abs(_band_rows(before)[1] - _band_rows(after)[1]) <= 2, (
        f"the outgoing world is not where it was on the cut: band {_band_rows(before)} -> {_band_rows(after)}")
    assert abs(sum(before) - sum(after)) / len(before) < 0.5, "the boundary frame is not congruent - the slide flashes"
    landed = _row_means(_frame(tl, uris, BOUNDARY + SLIDE_S))
    assert _band_rows(landed) == (-1, -1), f"the outgoing world is still on stage at the landing: band {_band_rows(landed)}"
    assert max(abs(v - 200.0) for v in landed) < 3, "the landed frame is not the incoming plate alone"
    seams = [_first_row_below(_row_means(_frame(tl, uris, BOUNDARY + d)), 197, 203, 0)
             for d in (0.15, 0.30, 0.45)]
    assert seams[0] > seams[1] > seams[2] >= 0, f"the seam does not travel one way: rows {seams}"


# ---------------------------------------------------------------- the compiler's default (E47 #3)
def test_the_mechanical_default_is_dip_when_the_world_changes_and_a_dock_decides_nothing():
    """E47 #3 corrected 2026-09-12 (the operator: "the dip is supposed to be used as an actual transition when the
    scene ACTUALLY changes ... the dip was associated with any DOCK, not the dip being associated to the scene
    change. That's 2 very different things"): a world change dips, the same world cuts, docks are not a factor."""
    assert B.scene_exit(None, True, None, True) == ("dip", None)
    assert B.scene_exit(None, False, None, True) == ("dip", None), "a bare row whose plate changes dips too"
    assert B.scene_exit(None, True, None, False) == ("cut", None), "a dock on the same world never dips"
    assert B.scene_exit(None, False, None, False) == ("cut", None)
    assert B.scene_exit(None, True) == ("cut", None), "with no boundary known, cut"
    assert B.DEFAULT_EXIT_CHANGE == "dip" and B.DEFAULT_EXIT_BARE == "cut"


def test_a_signature_enter_never_dips_by_default_and_an_authored_dip_still_wins():
    """The black flash of 2026-09-12 (Tokyo s04 -> s05): a mount carries the world change on its own clock, so a
    dip in front of it paints black seconds before the plate actually changes - the signatures cut even when the
    world changes; a page arriving built or by the camera onto a different world dips; an authored dip is the author's."""
    for enter in B.SIGNATURE_ENTERS:
        assert B.scene_exit(None, True, enter, True) == ("cut", None), enter
    for enter in ("camera", "built", None):
        assert B.scene_exit(None, False, enter, True) == ("dip", None), enter
    assert B.scene_exit("dip", True, "mount", False) == ("dip", None), "authored wins"
    assert B.scene_exit("dip:0.3", False, "spiral", True) == ("dip:0.3", 0.3)


def test_world_key_tells_a_different_chart_from_the_same_page_returning():
    plate = {"kind": "plate", "asset_id": "plate-x"}
    assert B.world_key(plate) == B.world_key(dict(plate)) and B.world_key(plate) != B.world_key({"asset_id": "plate-y"})
    page = {"kind": B.SPECIES_LEDGER, "page": {"builder": "dense-line", "title": "Our biggest customer is selling", "enter": "mount"}}
    back = {"kind": B.SPECIES_LEDGER, "page": {"builder": "dense-line", "title": "Our biggest customer is selling", "enter": "spiral"}}
    other = {"kind": B.SPECIES_LEDGER, "page": {"builder": "story", "title": "Ten years, a year at a time", "enter": "camera"}}
    assert B.world_key(page) == B.world_key(back) != B.world_key(other)


def test_an_authored_exit_still_wins_and_the_wipe_is_still_reachable_by_name():
    for name in ("wipe_right", "wipe", "cut", "dissolve", "suck:0.5,0.5"):
        assert B.scene_exit(name, True) == (name, None), name


def test_dip_and_blurzoom_may_declare_their_own_length():
    assert B.scene_exit("dip:0.6", False) == ("dip:0.6", 0.6)
    assert B.scene_exit("blurzoom:0.4", True) == ("blurzoom:0.4", 0.4)
    assert B.parse_exit("dip")[1] is None          # a bare dip leaves the player and the gate on DIP_S


def test_a_melt_parses_with_and_without_its_own_length_register_and_point():
    """P52 T9 (R26-15), E88 (R26-76): `melt` | `melt:throw` | `melt:splash:chart` | `melt:splash:plate`, `:<s>`, and on a
    throw `:<x>,<y>`, the suffixes in any order. A bare `melt:splash` is refused - it names no ending since E88. Only a
    bare number is a LENGTH - `melt:0.92,1.18` is the point the ball is thrown to, and reading it as 0.92 s (which
    is what a plain `exit.split(':')[1]` does) would be a melt nobody authored. species/melt.mjs `meltOpts` reads
    the same grammar in the player; these two are one statement made twice."""
    assert B.parse_exit("melt") == ("melt", None)
    assert B.parse_exit("melt:1.2") == ("melt:1.2", 1.2)
    assert B.parse_exit("melt:throw") == ("melt:throw", None)
    assert B.parse_exit("melt:splash:chart") == ("melt:splash:chart", None)
    assert B.parse_exit("melt:0.92,1.18") == ("melt:0.92,1.18", None)
    assert B.parse_exit("melt:1.2:splash:plate") == ("melt:1.2:splash:plate", 1.2)
    assert B.parse_exit("melt:splash:chart:1.2") == ("melt:splash:chart:1.2", 1.2)
    assert B.parse_exit("melt:throw:1.2:0.9,1.1") == ("melt:throw:1.2:0.9,1.1", 1.2)
    assert [B.melt_ending(x) for x in ("melt", "melt:throw", "melt:splash:chart", "melt:1.2:splash:plate", "dip")] ==         ["throw", "throw", "splash:chart", "splash:plate", None]
    assert B.MELT_ENDINGS == ("throw", "splash:chart", "splash:plate")
    assert "melt" in B.SCENE_EXITS and "melt" in B.TIMED_EXITS
    assert B.MELT_S == 1.6, "the default length the player's MELT.S carries too"
    for bad in ("melt:sideways", "melt:-2", "melt:0", "melt:1,2,3", "melt:1,x", "melt:splash", "melt:splash:sideways",
                "melt:chart", "melt:plate", "melt:throw:splash:chart", "melt:splash:plate:0.5,0.5", "melt:1.2:splash"):
        with pytest.raises(ValueError):
            B.parse_exit(bad)


def test_a_melt_may_ask_for_the_weight_phase_and_name_its_material():
    """R26-118 / E88 s6-s7 (the operator, 2026-09-14: *"we need to make sure our ball has real density, and we should
    probably roll it around or manipulate it a bit"*): `weight` is a suffix like any other and may sit anywhere after
    the name, optionally followed by a MATERIAL. It is OPT-IN - no melt on the record changes - and a material this
    engine does not have is refused BY NAME, never silently painted as the default. species/melt.mjs `meltOpts` reads
    the same grammar in the player, and MELT.W_S is the twin of MELT_W_S here."""
    assert B.parse_exit("melt:weight") == ("melt:weight", None)
    assert B.parse_exit("melt:weight:metal") == ("melt:weight:metal", None)
    for mat in B.MELT_MATERIALS:
        assert B.parse_exit(f"melt:weight:{mat}") == (f"melt:weight:{mat}", None)
    assert B.parse_exit("melt:weight:2.8") == ("melt:weight:2.8", 2.8), "a bare number after weight is still the LENGTH"
    assert B.parse_exit("melt:splash:plate:weight:ink") == ("melt:splash:plate:weight:ink", None)
    assert B.melt_ending("melt:weight:ink") == "throw", "the weight phase does not change the ending"
    assert B.melt_ending("melt:splash:chart:weight") == "splash:chart"
    assert B.MELT_MATERIALS == ("metal", "ink", "paper", "liquid"), "species/melt.mjs MELT_MATERIALS"
    assert B.MELT_W_S == 1.15, "the weight phase's own length, the player's MELT.W_S"
    for bad in ("melt:weight:bronze", "melt:weight:steel", "melt:weight:chart"):
        with pytest.raises(ValueError):
            B.parse_exit(bad)


def test_a_melt_may_name_the_plane_it_happens_at_and_is_refused_by_name_outside_it():
    """P58 T6 (b) / E98 s4 (*"the docks, the ball and the slide move THROUGH the depth"*): `depth=<k>` is a suffix
    like `weight`, anywhere after the name - the PLANE the ball melts, lands and is thrown at. It is the dock's own
    vocabulary (`depth_k`: the camera's range, the same words with the ball as the noun), a melt names at most one,
    and absent is the flat clone every melt on the record already is. species/melt.mjs `meltOpts` reads the same
    string, and MELT.DEPTH_MIN / DEPTH_MAX are the twins of DOCK_DEPTH's range."""
    assert B.parse_exit("melt:weight:depth=1.15") == ("melt:weight:depth=1.15", None)
    assert B.parse_exit("melt:weight:metal:depth=1.15:2.0") == ("melt:weight:metal:depth=1.15:2.0", 2.0)
    assert B.melt_depth("melt:weight:depth=1.15") == 1.15
    assert B.melt_depth("melt:depth=1.4:splash:chart") == 1.4 and B.melt_ending("melt:depth=1.4:splash:chart") == "splash:chart"
    assert B.melt_depth("melt:weight") is None and B.melt_depth("dip") is None, "absent is the flat clone"
    assert B.parse_exit("melt:weight:depth=1.15")[0] == "melt:weight:depth=1.15", "the weight lookahead never eats a depth as a material"
    assert (B.DOCK_DEPTH["K_MIN"], B.DOCK_DEPTH["K_MAX"]) == (0.0, 4.0), "species/melt.mjs MELT.DEPTH_MIN / DEPTH_MAX"
    refusals = {"melt:depth=9": "depth 9 is outside 0..4",
                "melt:depth=x": "depth 'x' is not a number - depth=<k>, the share of the camera's move the ball takes",
                "melt:weight:depth=nope": "is not a number - depth=<k>",
                "melt:depth=1.1:depth=1.2": "two depths - a melt happens at ONE plane"}
    for bad, words in refusals.items():
        with pytest.raises(ValueError) as exc:
            B.parse_exit(bad)
        assert words in str(exc.value), (bad, str(exc.value))


def _melt_pair(exit_id: str, prev_page: dict | None, prev_world: dict | None = None) -> list[dict]:
    prev = {"scene_id": "s01", "world": prev_world or {"kind": B.SPECIES_LEDGER, "page": prev_page}, "exit": "cut"}
    nxt = {"scene_id": "s02", "world": {"kind": B.SPECIES_LEDGER, "page": {"builder": "bars"}}, "exit": exit_id}
    return [prev, nxt]


def test_a_melt_at_a_depth_is_refused_on_a_page_that_already_took_the_camera():
    """P58 T6 / R26-132 (1): a page authoring `;depth=` takes the camera onto its own plane (the player writes
    `data-world-pose`), so camDepthSwap has no flat camera to swap and `melt:weight:depth=1.15` would paint the flat
    melt and say nothing. The compiler refuses the pair BY NAME at the boundary, as it refuses `throw=depth` + `depth=`;
    on a flat page (no depth, or depth=1 - the flat plate) the same exit still compiles."""
    with pytest.raises(ValueError) as exc:
        B.stamp_transition_pages(_melt_pair("melt:weight:depth=1.15", {"builder": "line", "depth": 1.4}))
    assert ("exit 'melt:weight:depth=1.15': a melt at a depth on a page that already stands at depth=1.4 - the page took "
            "the camera onto its own plane, so the ball would melt flat; drop one") in str(exc.value), str(exc.value)
    for flat in ({"builder": "line"}, {"builder": "line", "depth": 1.0}):
        B.stamp_transition_pages(_melt_pair("melt:weight:depth=1.15", dict(flat)))   # compiles
    B.stamp_transition_pages(_melt_pair("melt:weight", {"builder": "line", "depth": 1.4}))   # a flat ball on a depth page is the melt that shipped


def test_a_melt_cannot_leave_a_layered_plate_world_at_all():
    """The layered-world half of R26-132 (1): `paintMelt` needs the page's `.lp-page`, and the compiler already refuses
    a melt whose outgoing world is not a ledger page - so a plate that ships in planes never reaches the depth pair."""
    layered = {"kind": "plate", "asset_id": "plate-x", "layers": [{"key": "ly:plate-x:mid", "k": 1.15, "role": "mid"}]}
    with pytest.raises(ValueError) as exc:
        B.stamp_transition_pages(_melt_pair("melt:weight:depth=1.15", None, layered))
    assert "the outgoing world is not a ledger page" in str(exc.value)


def test_a_slide_may_name_the_two_planes_it_moves_through_and_is_refused_by_name_outside_them():
    """P58 T6 (c) / E98 s4: `slide:<dir>[:<s>]:depth=<k_out>,<k_in>` - the dock's and the melt's one depth vocabulary
    and range, TWO numbers (one plane per frame), last. Absent is the flat slide; the engine's SLIDE.DEPTH_* are the
    twins of DOCK_DEPTH's range."""
    assert B.parse_exit("slide:left:depth=0.85,1.15") == ("slide:left:depth=0.85,1.15", None)
    assert B.parse_exit("slide:up:0.9:depth=1,1.4") == ("slide:up:0.9:depth=1,1.4", 0.9)
    assert B.slide_depth("slide:left:depth=0.85,1.15") == (0.85, 1.15)
    assert B.slide_depth("slide:left") is None and B.slide_depth("melt:depth=1.1") is None
    assert B.slide_direction("slide:right:depth=0,4") == "right"
    engine = RB.ENGINE.read_text(encoding="utf-8")
    for key, v in (("DEPTH_MIN", 0), ("DEPTH_MAX", 4), ("DEPTH_FLAT", 1)):
        assert f"    {key}: {v}," in engine.split("const SLIDE = Object.freeze({", 1)[1].split("});", 1)[0], key
    refusals = {"slide:left:depth=x,1": "depth 'x' is not a number - depth=<k>, the share of the camera's move the outgoing frame takes",
                "slide:left:depth=1,9": "depth 9 is outside 0..4",
                "slide:left:depth=1.15": "a slide names TWO depths - depth=<k_out>,<k_in>",
                "slide:left:depth=1,1,1": "a slide names TWO depths",
                "slide:left:depth=1,1:0.6": "depth= comes last and once"}
    for bad, words in refusals.items():
        with pytest.raises(ValueError) as exc:
            B.parse_exit(bad)
        assert words in str(exc.value), (bad, str(exc.value))


def test_a_slide_at_a_depth_is_refused_beside_a_page_or_plate_that_already_took_the_camera():
    """P58 T6 (c): a page at a depth and a layered plate both carry the camera on their own planes, so camDepthSwap has
    nothing to swap and that frame would slide flat in silence - refused by name at the boundary, either side."""
    exit_id = "slide:left:depth=0.85,1.15"
    with pytest.raises(ValueError) as exc:
        B.stamp_transition_pages(_melt_pair(exit_id, {"builder": "line", "depth": 1.4}))
    assert ("a slide at a depth on the outgoing page that already stands at depth=1.4 - the page took the camera onto "
            "its own plane, so that frame would slide flat; drop one") in str(exc.value), str(exc.value)
    layered = {"kind": "plate", "asset_id": "plate-x", "layers": [{"key": "ly:plate-x:mid", "k": 1.15, "role": "mid"}]}
    pair = _melt_pair(exit_id, None, None)
    pair[1]["world"] = layered
    with pytest.raises(ValueError) as exc:
        B.stamp_transition_pages(pair)
    assert "a slide at a depth on the incoming layered plate - the plate took the camera onto its own planes" in str(exc.value)
    B.stamp_transition_pages(_melt_pair(exit_id, {"builder": "line"}))                       # flat pages: compiles
    B.stamp_transition_pages(_melt_pair("slide:left", {"builder": "line", "depth": 1.4}))   # a flat slide off a depth page is today's


@needs_chromium
def test_a_slide_through_the_depth_lands_on_the_flat_slides_own_frame():
    """The u = 1 identity: the landing of `slide:left:depth=0.85,1.15` is the landing of `slide:left`, pixel for pixel -
    under the SAME landing-tied focus zoom, so the camera is moving and the depth is not a no-op on the way there."""
    t = BG.SLIDE_CUT + BG.SLIDE_S
    frames = []
    for exit_id in (None, "slide:left"):
        tl, uris = BG.slide_depth(exit_id)
        frames.append(RB.rgb_bytes(_frame_as(tl, uris, t, str(tl.get("aspect") or "16:9")))[1])
    assert frames[0] == frames[1], "the slide through the depth does not land on the flat slide's frame"


def _frame_as(tl: dict, uris: dict, t: float, aspect: str) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "slide-depth.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        return RB.render_frame(html, t, aspect)


def test_the_mechanical_default_is_never_a_melt():
    """A melt is AUTHORED or it does not happen (E47 as corrected 2026-09-12): it takes the whole world for 1.6 s
    and no rule may reach for it on its own. `scene_exit`'s table is the dip, the cut, and what the row says."""
    for docks in (True, False):
        for enter in (None, "mount", "spiral", "morph", "built"):
            for changed in (True, False):
                assert B.scene_exit(None, docks, enter, changed)[0] != "melt"
    assert B.scene_exit("melt:splash:chart", False, None, True) == ("melt:splash:chart", None), "an authored melt still wins"
    assert B.DEFAULT_EXIT_CHANGE != "melt" and B.DEFAULT_EXIT_BARE != "melt"
    assert "melt" not in B.LEDGER_EXITS, "the page's own retract law is untouched: a melt takes the WORLD"


def test_an_unknown_or_unusable_exit_is_a_build_error():
    for bad in ("slide", "dip:0", "dip:-1", "blurzoom:soon"):
        with pytest.raises(ValueError):
            B.scene_exit(bad, True)


# ---------------------------------------------------------------- THE EVIDENCE DOOR (E98 s7 / R26-134)
DOOR_S = 0.9            # build_scene_timeline_f.DOOR_S and kinetics/transitions.mjs DOOR.S
DOOR_EYE = 1.6          # PAGE_DEPTH["EYE"]: the door's lens is the page's


def _door_u_time(u: float, secs: float = DOOR_S) -> float:
    """The instant (on the 0.01 s scrub) at which the min-jerk clock reaches u - bisected, so the frames are the u named."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if mid ** 3 * (10 - 15 * mid + 6 * mid * mid) < u:
            lo = mid
        else:
            hi = mid
    return round(BOUNDARY + lo * secs, 2)


def _door_far_edge(t: float, W: int = 1080) -> float:
    """Where a LEFT door's far edge stands on the stage's centre row at t - the module's own geometry, in Python."""
    import math
    p = min(1.0, max(0.0, (t - BOUNDARY) / DOOR_S))
    u = p ** 3 * (10 - 15 * p + 6 * p * p)
    open_deg = 180 - math.degrees(math.atan(DOOR_EYE * W / (W / 2)))
    th = math.radians(open_deg * u)
    d = DOOR_EYE * W
    k = d / (d + W * math.sin(th))
    return W / 2 + (W * math.cos(th) - W / 2) * k


def _centre_row(png: bytes) -> list[int]:
    im = _grey(png)
    w, h = im.size
    px = im.load()
    return [px[x, h // 2] for x in range(w)]


def test_a_door_parses_its_hinge_and_length_and_is_refused_by_name():
    """`door[:<hinge>][:<s>]`: the hinge first (left by default), the length inside DOOR_S_MIN..DOOR_S_MAX. The player's
    doorOpts reads the same grammar and treats anything else as a cut, so the refusals are here, by name, with the fix."""
    assert "door" in B.SCENE_EXITS and "door" in B.TIMED_EXITS and "door" in B.WORLD_TAKING_EXITS
    assert (B.DOOR_S, B.DOOR_S_MIN, B.DOOR_S_MAX, B.DOOR_HINGE) == (0.9, 0.45, 1.8, "left")
    assert B.DOOR_HINGES == ("left", "right", "top", "bottom")
    assert B.parse_exit("door") == ("door", None) and B.door_hinge("door") == "left"
    assert B.parse_exit("door:right") == ("door:right", None) and B.door_hinge("door:right") == "right"
    assert B.parse_exit("door:top:1.2") == ("door:top:1.2", 1.2)
    assert B.parse_exit("door:0.6") == ("door:0.6", 0.6) and B.door_hinge("door:0.6") == "left"
    assert B.door_hinge("slide:left") is None
    refusals = {"door:diagonal": "'diagonal' is not a hinge - say door[:left|right|top|bottom][:<s>]",
                "door:": "'' is not a hinge",
                "door:left:0.2": "a door of 0.2 s is outside 0.45..1.8 s",
                "door:left:3": "a door of 3 s is outside 0.45..1.8 s",
                "door:left:0.9:x": "a door carries a hinge and at most a length, in that order",
                "door:0.9:left": "a door carries a hinge and at most a length, in that order"}
    for exit_id, want in refusals.items():
        with pytest.raises(ValueError) as exc:
            B.parse_exit(exit_id)
        assert want in str(exc.value), (exit_id, str(exc.value))


def _door_pair(page: dict | None, docks_out: list | None = None, docks_in: list | None = None) -> list[dict]:
    w_out = {"kind": "ledger", "page": page} if page is not None else {"asset_id": "plate-a"}
    return [{"scene_id": "s06", "world": w_out, "exit": "cut", "span": [0.0, BOUNDARY], "docks": docks_out or []},
            {"scene_id": "s07", "world": {"asset_id": "plate-vault"}, "exit": "door", "span": [BOUNDARY, RUNTIME],
             "docks": docks_in or []}]


def test_a_door_is_refused_out_of_a_page_at_a_depth_or_on_a_plane_and_takes_a_flat_page_whole():
    """E98 s7: *"a card's tilt is a MOTION, not a pose it jumps to"* - the door IS the plane's motion, so a page that
    already stands at a depth or on a plane is refused; a flat page is stamped exit=cut (the door takes the world)."""
    for page in ({"builder": "bars", "depth": 1.15}, {"builder": "bars", "plane": {"kind": "tilt", "deg": 14}}):
        with pytest.raises(ValueError) as exc:
            B.stamp_transition_pages(_door_pair(page))
        assert ("s06 -> s07 (door): exit 'door': a door opens a card that landed flat - drop depth=/plane=, the door is "
                "the plane's motion") in str(exc.value), str(exc.value)
    flat = {"builder": "bars"}
    notes = B.stamp_transition_pages(_door_pair(flat))
    assert flat["exit"] == "cut" and any("door takes must not retract first" in n for n in notes), notes


def test_a_door_is_refused_on_a_boundary_a_dock_is_live_across():
    """Doc 29 Part 6: a decorated transition happens on an EVIDENCE-FREE boundary. The wipe's own rule (the engine's
    allOut): a card leaving within DOOR_DOCK_TOL of the boundary belongs to the outgoing page; anything up across the
    swing is refused by name."""
    leaving = [{"slide": "dock-a", "enter": 2.0, "exit": BOUNDARY + 0.2}]
    B.stamp_transition_pages(_door_pair(None, docks_out=leaving))   # leaves with its page: evidence-free
    late = [{"slide": "dock-b", "enter": BOUNDARY + DOOR_S + 0.1, "exit": RUNTIME}]
    B.stamp_transition_pages(_door_pair(None, docks_in=late))       # lands after the door has opened
    for docks_out, docks_in, side, name in (([{"slide": "dock-c", "enter": 2.0, "exit": BOUNDARY + 1.0}], None, "outgoing", "dock-c"),
                                            (None, [{"slide": "dock-d", "enter": BOUNDARY + 0.3, "exit": RUNTIME}], "incoming", "dock-d")):
        with pytest.raises(ValueError) as exc:
            B.stamp_transition_pages(_door_pair(None, docks_out, docks_in))
        assert (f"a door swings on an evidence-free boundary (doc 29 Part 6) - the {side} dock '{name}' is up across it"
                in str(exc.value)), str(exc.value)


@needs_chromium
def test_the_frame_before_the_door_opens_is_the_outgoing_world_unchanged():
    """u = 0 is the IDENTITY: the cut's own frame writes no matrix and no clip, so it is the frame before the boundary."""
    tl, uris = _build("door", banded=True)
    before, at = RB.rgb_bytes(_frame(tl, uris, BOUNDARY - 0.01)), RB.rgb_bytes(_frame(tl, uris, BOUNDARY))
    assert before == at, "the door's first frame differs from the frame before it - the door jumped instead of opening"


@needs_chromium
def test_the_door_swings_open_on_its_hinge_onto_the_incoming_world():
    """At u 0.25 / 0.5 / 0.75, down the stage's centre row: the hinge column is still the outgoing plate's band (the
    door hangs on its edge), the far edge stands where the module's projection puts it (within 3 px), it travels one way
    toward the hinge, and right of it is the incoming plate's own grey - what the opening shows is the next world."""
    tl, uris = _build("door", banded=True)
    edges = []
    for u in (0.25, 0.5, 0.75):
        t = _door_u_time(u)
        row = _centre_row(_frame(tl, uris, t))
        assert row[1] < 100, f"u {u}: the hinge column is not the outgoing band ({row[1]})"
        edge = next(x for x in range(len(row)) if row[x] > 150)
        want = _door_far_edge(t)
        assert abs(edge - want) <= 3, f"u {u} (t {t}): the far edge is at x {edge}, the projection says {want:.1f}"
        assert all(abs(v - 200) < 4 for v in row[edge + 4:]), f"u {u}: right of the door is not the incoming plate alone"
        edges.append(edge)
    assert edges[0] > edges[1] > edges[2] > 0, f"the door does not close one way toward its hinge: {edges}"


@needs_chromium
def test_a_door_at_its_end_is_the_incoming_world_alone_identical_to_a_cut():
    """u = 1 is edge-on - zero width: the frame at the door's length is the plain cut's frame at the same instant, byte
    for byte (nothing of the card is left to pop)."""
    t = round(BOUNDARY + DOOR_S, 2)
    door_tl, uris = _build("door", banded=True)
    cut_tl, _ = _build("cut", banded=True)
    assert RB.rgb_bytes(_frame(door_tl, uris, t)) == RB.rgb_bytes(_frame(cut_tl, uris, t)), (
        "the landed door is not the cut's frame - something of the outgoing world is left on stage")

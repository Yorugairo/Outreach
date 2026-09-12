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
                                              ("blurzoom", True, BOUNDARY - 0.05)])
def test_a_transition_frame_renders_identically_in_two_browsers(exit_id: str, banded: bool, t: float):
    tl, uris = _build(exit_id, banded)
    a, b = RB.rgb_bytes(_frame(tl, uris, t)), RB.rgb_bytes(_frame(tl, uris, t))
    assert a[0] == b[0] == RB.STAGE[ASPECT]
    assert hashlib.sha256(a[1]).hexdigest() == hashlib.sha256(b[1]).hexdigest(), (
        f"{exit_id}: two renders of the same frame differ - the transition is not a pure function of t")


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
    """P52 T9 (R26-15): `melt` | `melt:<s>` | `melt:splash` | `melt:<x>,<y>`, the suffixes in any order. Only a
    bare number is a LENGTH - `melt:0.92,1.18` is the point the ball is thrown to, and reading it as 0.92 s (which
    is what a plain `exit.split(':')[1]` does) would be a melt nobody authored. species/melt.mjs `meltOpts` reads
    the same grammar in the player; these two are one statement made twice."""
    assert B.parse_exit("melt") == ("melt", None)
    assert B.parse_exit("melt:1.2") == ("melt:1.2", 1.2)
    assert B.parse_exit("melt:splash") == ("melt:splash", None)
    assert B.parse_exit("melt:0.92,1.18") == ("melt:0.92,1.18", None)
    assert B.parse_exit("melt:1.2:splash") == ("melt:1.2:splash", 1.2)
    assert B.parse_exit("melt:splash:1.2") == ("melt:splash:1.2", 1.2)
    assert "melt" in B.SCENE_EXITS and "melt" in B.TIMED_EXITS
    assert B.MELT_S == 1.6, "the default length the player's MELT.S carries too"
    for bad in ("melt:sideways", "melt:-2", "melt:0", "melt:1,2,3", "melt:1,x"):
        with pytest.raises(ValueError):
            B.parse_exit(bad)


def test_the_mechanical_default_is_never_a_melt():
    """A melt is AUTHORED or it does not happen (E47 as corrected 2026-09-12): it takes the whole world for 1.6 s
    and no rule may reach for it on its own. `scene_exit`'s table is the dip, the cut, and what the row says."""
    for docks in (True, False):
        for enter in (None, "mount", "spiral", "morph", "built"):
            for changed in (True, False):
                assert B.scene_exit(None, docks, enter, changed)[0] != "melt"
    assert B.scene_exit("melt:splash", False, None, True) == ("melt:splash", None), "an authored melt still wins"
    assert B.DEFAULT_EXIT_CHANGE != "melt" and B.DEFAULT_EXIT_BARE != "melt"
    assert "melt" not in B.LEDGER_EXITS, "the page's own retract law is untouched: a melt takes the WORLD"


def test_an_unknown_or_unusable_exit_is_a_build_error():
    for bad in ("slide", "dip:0", "dip:-1", "blurzoom:soon"):
        with pytest.raises(ValueError):
            B.scene_exit(bad, True)

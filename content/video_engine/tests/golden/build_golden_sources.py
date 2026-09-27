"""The four golden surfaces (P39 T3): small, synthetic, deterministic timelines that exercise
what P37 and P38 touch - a ledger page mid-build, a chart carrying a callout, a 16:9 dock
pair, a 9:16 dock pair.

Everything is derived from committed inputs (the template, one committed `.series.json`
sidecar, generated solid plates, a two-second silent WAV) so the frames can be re-rendered
on any checkout. No episode assets, no quarantine. Run as a script to (re)write the source
JSON beside this file; the tests read those files, never this module's output at test time,
so a change here is a deliberate golden refresh.
"""
from __future__ import annotations

import base64
import io
import json
import math
import struct
import sys
import wave
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SCRIPTS = REPO / "content/video_engine/scripts"
SERIES = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-divergence-v1.series.json"
SOURCES = HERE / "sources"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import ledger_page as LPG  # noqa: E402

RUNTIME = 30.0
THREAD_CUT = 15.0   # P50 T15 / HF-16: where the `thread-baseline` golden cuts from its line page to its bars page
MELT_CUT = 15.0     # P52 T9: where the `melt-page` golden hands its finished page to a plate - and the page MELTS across it
SLIDE_CUT = 15.0    # P57 T13: where the `slide-*` goldens hand one chart page to the next - and the two SLIDE across it
SLIDE_S = 0.6       # build_scene_timeline_f.SLIDE_S and the engine's: the length this golden declares none against
# the frame each surface is judged at - chosen so the thing under test is on screen and mid-motion
FRAME_T = {
    "ledger-page-mid-build": 6.0,   # field filled, outline drawn, ink and bars building
    "chart-callout": 12.0,          # the line has drawn, all four badges have landed
    "occluder-dock": 12.0,          # P50 T15 / HF-17: the card landed (4.0) and still, its lower half behind the plate's desk edge
    "page-depth": 15.5,             # P58 T4: inside the focus zoom's HOLD (13.6 -> 15.6, at FOCUS_SCALE from 14.71) with the card landed and its badge settled - the page standing as a card at 1.15 on the dock's space, tilted 14 deg about its own vertical axis
    "camera-layers": 7.9,           # P58 T3: inside the focus zoom's HOLD (it reaches FOCUS_SCALE at 6.0 + 2.0/1.8 = 7.11 and stands dead still to 8.0) - the move landed, every plane at its own share of it, and no fractional clock in the frame
    "ledger-soak-page": 2.7,        # mid-soak: stains spreading and overlapping (P43 T3 K-M ink is judged here)
    "dock-pair-16x9": 12.0,         # both cards up, badges landed
    "dock-pair-9x16": 12.0,
    "ledger-extend": 13.05,
    "thread-baseline": 19.9,        # P50 T15 / HF-16: MID-CARRY - the wire from the line page standing while the bars page grows under it. The carried mark lives inside the page's chart <svg>, whose opacity the BUILD drives, so it becomes visible when the chart layer does (scene 2 at 15.0 + ROLL+SAVOR+FIELD+PUNCH = 19.4) and recedes from there over THREAD.FADE_S; 19.9 is half way through that, with two bars grown
    "art-embed": 9.0,               # P50 T7: the press card has landed on the TV (5.0) and settled, the room has finished darkening (7.0 + DARK_S), the underline on its quoted phrase is fully drawn (8.0 + SQUIG_DRAW) and the still card on the desk paper carries both its badges (5.6 + 0.75 + 1.3n)
    "press-stack": 11.4,            # P50 T3: all three cards landed (5.0 / 7.4 / 9.8 + LAND_S), the pile settled, and the underline on the third fully drawn (10.6 + SQUIG_DRAW)
    "chip-board": 11.0,             # P50 T2: all three chips landed (5.0 / 6.2 / 7.4 + LAND_S) and the middle one's X fully drawn (10.0 + CROSS_S) - the board as it is read
    "flow-swap": 12.6,              # P50 T4: the swap is over (11.0 + SWAP_OUT_S + SWAP_IN_S = 11.75), the new node stands where the old one did, both arrows and the year stamp are in
    "vecmap-arc": 12.4,             # P50 T5: all four have landed - IRN lit (5.0), the arc drawn (6.6 + DRAW_S), "1996" stamped (8.4), CHN lit (9.6) with its figure (10.4) - and the X that cuts the flow is fully struck (11.5 + CROSS_S = 11.95)
    "span-decade": 12.6,            # P50 T4: the page has built (3.9 + 0.5 + 3.0), the span's shade is fully in (8.0 + IN_S) and its name fully written (8.45 + dur * WRITE = 12.45)
    "tiers-two": 14.2,              # P50 T9: both bands drawn (the page builds to 8.9, the second band's own word runs 9.5-11.5) and the drop bar in the accent all but finished (12.0 + 0.88 of 2.5) with its label being written
    "treemap-cross": 10.9,          # P50 T6: the census has landed (the build ends at 8.0), the three X's are struck (9.0 + CROSS_S) and the crossed share is written (9.0 + WRITE_AT + 3.0 * WRITE = 10.7)
    "tags-to-bars": 12.2,           # P50 T11: mid-hand-over of the KEYED-TAGS recast (12 s + 2 s): the two terminal tags are halfway to their bars and growing into the bars' own type, the lines have left half their history beneath them, the bars are half grown, and no value has been drawn twice
    "data-to-bars": 13.0,           # E64 / R26-49: dur * 0.5 of the DATA-keyed recast (12 s + 2 s) - the four data in flight between the line and their bars, the bars part-grown beneath them, the old tick labels most of the way un-written and the new ones started
    "melt-page": 15.88,             # P52 T9, E88: MELT_CUT + 0.55 of MELT.S (1.6 s) - THE BALL, formed, solid and at rest on
                                   # its BOARD on the frame the throw's squash starts: the morph is exactly the circle of
                                   # BALL_R, the ink behind it is hidden, and the gooey blur is exactly 0. Mid-morph (0.45) is the livelier picture and is what the
                                   # PROOF frames show, but its mask carries a 9 px blurred edge, and one render in
                                   # eight came back with 15 pixels of that edge off by 2 (a Chromium filter-raster
                                   # flake, measured 2026-09-12) - a golden is a byte-exact pin and takes the instant
                                   # with no fractional band to flake
    "melt-splash": 16.85,           # E88 / R26-76: splash:chart - the BURST: the ball hit the board, flattening
                                   # and fading into its droplets, which are out along their rays toward where they
                                   # land; no stain has opened yet, so no blur is on screen and the pin is byte-exact
    "melt-ball-roll": 16.28,        # R26-118 / E88 s6: MID-ROLL. The window is MELT_CUT + MELT.S + MELT.W_S (2.75 s),
                                   # so the weight phase opens at 15.88 and its beats are LAND to 16.11, ROLL to 16.455,
                                   # NUDGE to 16.846, SETTLE to 16.98. 16.28 is half way through the roll: the ball has
                                   # turned ~100 degrees with its own ink MARK, its shadow rides a frame behind it, and
                                   # its surface is out of round. Its landing and its rest ride PROOF_FRAMES
    # P61 T5b / E99 s42: the two BODY COLOURS, at `melt-ball-roll`'s own base instant so the pair mirrors it exactly.
    # Neither is in test_golden_frames.SURFACES; the frame the operator is asked to judge is the PROOF at 16.98, the
    # settle, the same instant as `melt-ball-roll@proof-settle`, so the three read as one crop. `render_baseline
    # --check` covers these two base frames, which is why each has one.
    "melt-ball-slate": 16.28,
    "melt-ball-reference": 16.28,
    "melt-ball-blend": 16.28,       # P72 T23 / R26-146: the blend ball mid-roll, at the pair's own instant - its settle rides PROOF_FRAMES
    "melt-splash-offscreen": 17.04,  # P72 T23 / R26-157: THE RETURN - the ball thrown back in from off the left edge,
                                    # 0.165 s into its 0.375 s flight on the flatter arc (2766 px/s against the approved
                                    # pitch's 944), its shadow fading in under it. The carry, the empty board and the
                                    # splat ride PROOF_FRAMES
    "melt-plate": 17.21,            # E88 / R26-76: splash:plate - the PAINT: the stains have opened from the
                                   # landed drops and the plate shows through them over the charcoal, springing to rest
    "count-array": 8.0,             # P52 T7: all six icons landed (5.0 + 5 * 0.34 + LAND_S = 7.15) and the count written as the claim (+ CLAIM_LAG + CLAIM_S = 7.73) - the field as it is read
    "agenda-two": 7.2,              # P52 T8: both rows revealed (5.0 and 6.2 + NUM_LEAD + ROW_S = 6.74) and both rules fully drawn - the agenda as it stands
    "agenda-page": 12.0,            # P61 T8: the agenda PAGE at rest - all three rows written, all three catalogued icons stamped and settled (the last at 8.2 + 0.54 + 0.12 + 0.26 + 0.14 = 9.26), the board full and breathing. Its three moving instants ride PROOF_FRAMES (@proof-first-row / @proof-stamp / @proof-full)
    "rings-on-vertices": 13.2,      # P69 T47: the third ring closed (8.4 + DRAW_S), the valley's light landed (10.2 + 0.8 x 1.6 = 11.48) and the trough's figure written (11.5 + 1.4) - all three rings still standing (they hold to 16.0)
    "share-donut-flat": 8.4,        # P69 T48: the flat donut at rest - the sweep closed (3.9 + 0.5 + SHARE_BUILD 3.2 = 7.6) and every slice's name and figure written
    "share-pie-3d": 10.4,           # P69 T48: the tilted, extruded pie with its largest slice EXPLODED - the explode fired on its word (9.0 + 0.8) and settled
    "share-pie-3d-push": 13.2,      # P69 T48: the camera HELD on the largest slice (11.0 -> 12.4 at PIE_PUSH_ZOOM, inout) with the other four receded
    "ring-dashed-chip": 10.6,       # P52 T8: the page has built (3.9 + 0.5 + 3.0), the dashed ellipse has closed round the datum (9.0 + DRAW_S) and the flag chip has landed beside it (+ FLAG_LAG + CHIP.LAND_S = 10.24)
    "species-proof": 12.6,          # P52 T7/T8, HUMAN GATE 3: the proof page's FIRST instant (the ring closed with its flag on the fully built page). Its other two are FLAG_FRAMES entries on the same clock (species-proof@proof-count / @proof-agenda), so the operator reads all three as frames and then plays the one file
    "ledger-keyed": 12.75,          # P48 T4b: mid-phase-2 of the keyed recast (12 s + 2 s; the golden's expoOut clock is half done at u 0.37): the lines have left half their history, their ends and values are in flight to the bar tops, the bars are half grown         # P48 T3: mid-extend - the axis has retargeted (the first 0.45 of the 2 s clock), the nib is ~half through the new tail on the golden's expoOut pen (rescale at 8 s, extend at 12 s)
}


# P52 T6: the newsreel band, judged mid-run - the band open (5.0 + BAR_FOR), the crawl 5.6 s into its run
# (784 px left of its place at the default 140 px/s), the strapline fully written, the surface above landed and
# a caption page live (10.0-12.8) so the STRIP the two share is what the frame shows.
FRAME_T["newsreel-band"] = 11.0          # 16:9: the band in the lower 40 %, the caption at its own 40 % home
FRAME_T["newsreel-strip-9x16"] = 11.0    # 9:16 THE DEFAULT: the caption keeps its E62 band, the crawl goes BELOW it
FRAME_T["newsreel-strip-above"] = 11.0   # 9:16 THE ALTERNATIVE (`cap_band: "above"`): the crawl takes the strip, the caption moves above it
# P55 T6: the two inline dock painters pinned BEFORE T7 lifts them into modules (goldens first).
FRAME_T["compare-morph"] = 14.9   # P57 T12 / R26-70b, re-goldened by T12b and again by T12c: the compare HELD - the DEFAULT
                                  # form is now E76 s5's BALL, so what stands here at 14.9 is the figure's own <text>, which took
                                  # the morph's landed outlines back at u = 1 (14.4), with its label beneath and the quoted metric
                                  # held beside it at COMPARE.GHOST_A. At rest on purpose: its three moving instants are
                                  # @proof-sag, @proof-ball and @proof-050 on PROOF_FRAMES.
FRAME_T["compare-streak"] = 14.9  # P57 T12c: the same row with `form: "streak"` - P57 T12b's TEXT melt, kept whole when the
                                  # default became the ball, and pinned byte-identical to the bytes `compare-morph` carried
                                  # before T12c (its three instants ride PROOF_FRAMES).
FRAME_T["compare-count"] = 14.9   # P57 T12b: the same row and the same instant with `form: "count"` - T12's counter, kept whole
                                  # as a setting and pinned byte-identical to the bytes `compare-morph` carried before T12b.
# P57 T13 / R26-75: THE SLIDE (E87 s3), read at the two instants a push has. The travel is the .world box's own
# span (inset -5%), so at u = 0.5 the two boxes ABUT at mid-stage - the seam is the stage's own centre line.
FRAME_T["slide-mid"] = SLIDE_CUT + SLIDE_S / 2    # MID-SLIDE: both worlds on stage, the outgoing chart half off to the
                                  # left with its seam at the centre, the arriving chart's axes coming in behind it -
                                  # min-jerk is exactly 0.5 at u = 0.5, so the travel is exactly half the box
FRAME_T["slide-landed"] = SLIDE_CUT + SLIDE_S     # THE LANDING: u = 1 - the outgoing box's trailing edge is exactly off
                                  # the stage (a stage-width travel would leave 5% of it showing) and the arriving page
                                  # stands at its own place, 0.6 s into its axes build
FRAME_T["verdict-stack"] = 12.5   # mid-pile: cards 1-4 (3.0 / 5.0 / 7.0 / 9.0) receded to their rail spots (each recede is 1.0 s off the next
                                  # item's `at`), card 5 (at 11.0) fully entered (+0.9) and ACTIVE large near centre, card 6 (13.0) not yet in.
                                  # Its @proof-burst instant (clear_at + 0.25) rides render_baseline.PROOF_FRAMES
FRAME_T["verdict-stack-9x16"] = 13.6   # P61 T7 - THE MOSAIC on a short: proofs 1-7 (2.0 ... 10.6) receded to their rail spots,
                                  # proof 8 (12.2) fully entered and ACTIVE large near the safe box's centre, proof 9 (13.8) not yet in.
                                  # The frame that answers E99 s21: eight cards over the whole height of the box, no two in a band, none a row.
                                  # Its other four phases ride render_baseline.PROOF_FRAMES (@proof-enter / focus / idle / burst)
FRAME_T["test-card"] = 11.4       # tRel = t - enter(2.0) - CARD_IN * 0.6 = 8.95: rows 1-2 (delays 1.0 / 4.0) fully typed and both answers swept;
                                  # row 3 (delay 7.0) typed (17 chars x 0.045 s), its where-cell in (+0.6), its left answer swept (+1.0 + 0.55),
                                  # its right answer fully faded in (+1.6 + 0.35) with the marker 0.64 of the way through its sweep
FRAME_T["test-card-phone"] = 10.65   # P69 T28b: tRel 8.2 on the same clock - rows 1-2 typed and both answers swept; row 3
                                  # (delay 7.0) typed (9 chars x 0.045 s), its steel answer swept (+0.6 + 0.55) and its paper
                                  # answer 0.2 s in (+1.0): 0.57 faded in, the marker 0.74 of the way through its sweep


def png_solid(w: int, h: int, rgb: tuple[int, int, int]) -> bytes:
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


# P61 T8 (E99 s31: an approved cutout never enters git) - THE ICON PROXY. The agenda page's stamps are the
# operator's OWN woodblock cutouts (~300 px square, ~200 KB each); a golden source carrying their bytes whole
# would put three quarters of a megabyte of approved artwork in the tree. The fixture carries a PROXY instead:
# the same picture, box-filtered down to about the size the page draws it at, by INTEGER arithmetic and zlib
# alone - no Pillow, so the bytes are identical on any machine (a golden source that depended on an imaging
# library's version would silently re-baseline four committed frames whenever that library moved).
# THE RECORD IS UNTOUCHED: the compiler still resolves each icon through the catalogue before this is called
# (id, kind, review_state, render_eligible, and the sha256 of the file on disk - build_scene_timeline_f
# .catalogue_icon), and a BUILD still embeds the full-resolution file through catalogue_icon_uri. This is a
# test fixture's proxy, and it says so.
ICON_PROXY_PX = 192      # the longest side a proxy is reduced toward: the page draws a stamp at ~159 px at rest
                         # (AGENDA.PAGE_ICON x the row's height), and reduction is by an INTEGER factor, so the
                         # three cutouts land at 151x159, 142x147 and 160x152 - a hair over the drawn box


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def png_read_rgba(p: Path) -> tuple[int, int, bytearray]:
    """One 8-bit RGBA, non-interlaced PNG as (w, h, pixels) - the standard library alone.

    Anything else (a palette, 16 bits, an interlace) is a ValueError naming the file and what it carries: a
    silent fallback here would be a fixture nobody could reproduce."""
    b = p.read_bytes()
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{p.name}: not a PNG")
    w = h = None
    idat = bytearray()
    i = 8
    while i + 8 <= len(b):
        ln = struct.unpack(">I", b[i:i + 4])[0]
        tag, data = b[i + 4:i + 8], b[i + 8:i + 8 + ln]
        i += 12 + ln
        if tag == b"IHDR":
            w, h, depth, colour, comp, filt, inter = struct.unpack(">IIBBBBB", data)
            if (depth, colour, comp, filt, inter) != (8, 6, 0, 0, 0):
                raise ValueError(f"{p.name}: depth {depth}, colour type {colour}, interlace {inter} - this reader "
                                 "takes an 8-bit RGBA non-interlaced PNG, which is what every cutout is")
        elif tag == b"IDAT":
            idat += data
        elif tag == b"IEND":
            break
    if w is None:
        raise ValueError(f"{p.name}: no IHDR")
    raw = zlib.decompress(bytes(idat))
    stride = w * 4
    out, prev, pos = bytearray(h * stride), bytearray(stride), 0
    for y in range(h):
        f = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        if f == 1:                                     # Sub
            for x in range(4, stride):
                line[x] = (line[x] + line[x - 4]) & 255
        elif f == 2:                                   # Up
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:                                   # Average
            for x in range(stride):
                a = line[x - 4] if x >= 4 else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:                                   # Paeth
            for x in range(stride):
                a = line[x - 4] if x >= 4 else 0
                c = prev[x - 4] if x >= 4 else 0
                up = prev[x]
                pa, pb, pc = abs(up - c), abs(a - c), abs(a + up - 2 * c)
                pred = a if (pa <= pb and pa <= pc) else (up if pb <= pc else c)
                line[x] = (line[x] + pred) & 255
        elif f != 0:
            raise ValueError(f"{p.name}: filter {f} on row {y}")
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, out


def png_rgba(w: int, h: int, px: bytes) -> bytes:
    """An 8-bit RGBA PNG, every row unfiltered - the same writer png_solid uses, with alpha."""
    raw = b"".join(b"\x00" + bytes(px[y * w * 4:(y + 1) * w * 4]) for y in range(h))
    return (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + png_chunk(b"IDAT", zlib.compress(raw, 9)) + png_chunk(b"IEND", b""))


def png_proxy(p: Path, cap: int = ICON_PROXY_PX) -> bytes:
    """A cutout reduced to about `cap` on its longest side by an INTEGER box filter, alpha kept.

    The factor is `round(longest / cap)`, so the reduction is a whole number of source pixels per proxy pixel
    and no interpolation kernel (and no float rounding mode) is in it. The colour is averaged PREMULTIPLIED -
    sum(c x a) / sum(a) - because a cutout's fully transparent pixels carry arbitrary colour, and averaging
    that colour straight is exactly what puts a dark fringe round a woodblock edge. A picture already at or
    under the cap is returned as it is."""
    w, h, px = png_read_rgba(p)
    k = max(1, round(max(w, h) / cap))
    if k == 1:
        return p.read_bytes()
    w2, h2 = w // k, h // k
    out, n = bytearray(w2 * h2 * 4), k * k
    for y in range(h2):
        for x in range(w2):
            sr = sg = sb = sa = 0
            for dy in range(k):
                o = ((y * k + dy) * w + x * k) * 4
                for dx in range(k):
                    q = o + dx * 4
                    a = px[q + 3]
                    sr += px[q] * a
                    sg += px[q + 1] * a
                    sb += px[q + 2] * a
                    sa += a
            j = (y * w2 + x) * 4
            if sa:
                out[j], out[j + 1], out[j + 2] = sr // sa, sg // sa, sb // sa
            out[j + 3] = sa // n
    return png_rgba(w2, h2, bytes(out))


def png_bars(w: int, h: int, rgb: tuple[int, int, int], bars: list[tuple[float, float, float, float]],
             ink: tuple[int, int, int] = (28, 34, 42)) -> bytes:
    """A synthetic HEADLINE: a paper ground with dark bars where the words are, each bar a box in fractions of
    the image. Deterministic and stdlib-only (the same PNG writer png_solid uses), so the golden's card is a
    committed input like every other - press_card.py's own crop has its own test, on its own synthetic page."""
    row = [list(rgb) for _ in range(w)]
    px = [list(row[i]) for i in range(w)]
    raw = bytearray()
    for y in range(h):
        line = bytearray(b"\x00")
        for x in range(w):
            c = rgb
            for (x0, y0, x1, y1) in bars:
                if x0 * w <= x < x1 * w and y0 * h <= y < y1 * h:
                    c = ink
                    break
            line += bytes(c)
        raw += line

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def png_scene(w: int, h: int) -> bytes:
    """A synthetic NARRATIVE PLATE for the melt's plate splash (E88): a dusk sky, a sun, a far and a near hill line.
    Deterministic and stdlib-only, like png_solid - a committed input, not an asset."""
    import math
    sky0, sky1, sun, far, near = (250, 222, 170), (226, 140, 90), (255, 238, 196), (120, 82, 92), (58, 44, 52)
    raw = bytearray()
    for y in range(h):
        line = bytearray(b"\x00")
        for x in range(w):
            k = y / max(1, h - 1)
            c = tuple(int(sky0[i] + (sky1[i] - sky0[i]) * k) for i in range(3))
            if (x - 0.70 * w) ** 2 + (y - 0.36 * h) ** 2 <= (0.12 * h) ** 2:
                c = sun
            if y >= 0.62 * h + 0.06 * h * math.sin(x / w * 2 * math.pi * 1.3 + 0.5):
                c = far
            if y >= 0.80 * h + 0.05 * h * math.sin(x / w * 2 * math.pi * 0.8 + 2.0):
                c = near
            line += bytes(c)
        raw += line

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def silent_wav(seconds: float) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(1); w.setframerate(8000)
        w.writeframes(b"\x80" * int(8000 * seconds))
    return buf.getvalue()


def uri(mime: str, data: bytes) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def _pages() -> list[dict]:
    words = ["the", "frame", "under", "test"]
    return [{"s": 1.0 + 3 * i, "e": 3.8 + 3 * i,
             "t": [{"w": w, "k": j == 1, "s": 1.0 + 3 * i + 0.4 * j, "e": 1.4 + 3 * i + 0.4 * j} for j, w in enumerate(words)]}
            for i in range(9)]


def _timeline(title: str, scenes: list[dict], evidence: dict, aspect: str | None) -> dict:
    pages = _pages()
    tl = {
        "schema_version": "scene_evidence_timeline.v1", "runtime_s": RUNTIME,
        "title": title, "subtitle": "P39 golden surface", "episode_id": "golden", "project_id": "golden",
        "narration": {"canonical_hash": "0" * 64, "words_path": ""},
        "captions": [{"at": p["s"], "until": p["e"], "text": " ".join(t["w"] for t in p["t"])} for p in pages],
        "caption_pages": pages, "caption_modes": ["stage", "anchor"], "sound": [],
        "evidence": evidence, "scenes": scenes,
    }
    if aspect:
        tl["aspect"] = aspect
    return tl


def _base_uris() -> dict:
    return {
        "plate-plain": uri("image/png", png_solid(64, 36, (43, 52, 60))),
        "__audio__": uri("audio/wav", silent_wav(2.0)),
    }


def _badges() -> list[dict]:
    return [{"label": "MAMAA", "value": "+20%", "tag": "matches the index", "accent": "cobalt"},
            {"label": "S&P 500", "value": "+21%", "tag": "12 months", "accent": "ink"},
            {"label": "SEMICONDUCTORS", "value": "+102%", "tag": "their divergence", "accent": "teal"},
            {"label": "MEMORY BUILDERS", "value": "+613%", "tag": "our layer", "accent": "coral"}]


def _dock(aid: str, slot: int, enter: float, exit_: float, n_badges: int) -> dict:
    return {"slide": aid, "slot": slot, "enter": enter, "exit": exit_,
            "badge_at": [round(enter + 0.75 + 1.3 * (n + 1), 2) for n in range(n_badges)]}


def ledger_page_mid_build() -> tuple[dict, dict]:
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    page["field"] = "scribble"
    page["focus"] = {"kind": "callout", "label": "the divergence"}
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0.04, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: ledger page mid-build", scenes, {}, None), _base_uris()


def ledger_soak_page() -> tuple[dict, dict]:
    """The same page with the SOAK field and a badge rail (P43 T6): the surface for km_ink (mid-soak) and area_squash
    (the first rail badge mid-pop at t ~ 7.86: ROLL+SAVOR+FIELD 3.9 + PUNCH 0.5 + BUILD 3.0 + BADGE0 0.4 + a sixth of BADGE_IN)."""
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    page["field"] = "soak"
    page["badges"] = [dict(b, inline=False) for b in page.get("badges", [])] or _badges()
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0.04, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: ledger soak page", scenes, {}, None), _base_uris()


def ledger_extend() -> tuple[dict, dict]:
    """P48 T2/T3: the soak page windowed by a `rescale` (8 s) and grown back to its last datum by an `extend` (12 s). The
    derived states come from the compiler itself (derive_rescale_states), off a temp episode holding the golden series, so
    the golden proves the compiler and the player together; judged mid-extend (FRAME_T 13.4)."""
    import tempfile
    import build_scene_timeline_f as BST
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    page["field"] = "soak"
    page["badges"] = [dict(b, inline=False) for b in page.get("badges", [])] or _badges()
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    n = len(page["series"][0]["pts"])
    species = [{"kind": "chart_to", "at": 8.0, "dur": 1.2, "to": "rescale", "window": [2025.67, 2026.1]},
               {"kind": "chart_to", "at": 12.0, "dur": 2.0, "to": "extend", "to_index": n - 1}]
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td); (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/golden-series.series.json").write_bytes(SERIES.read_bytes())
        BST.derive_rescale_states(world, species, "ledger:golden-series:line", ep)
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: ledger extend", scenes, {}, None), _base_uris()


def ledger_keyed() -> tuple[dict, dict]:
    """P48 T4b: the four-line page becomes its four bars by the KEYED recast (12 s, 2 s) - the legal pair n lines -> n bars
    by series (Bravos 99-105). The bars are each line's last value, DERIVED from the golden series into a temp episode and
    built as a `then=` state by the compiler's own _page_state; judged mid-flight (FRAME_T 13.2)."""
    import json
    import tempfile
    import build_scene_timeline_f as BST
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    page["field"] = "soak"
    page["badges"] = [dict(b, inline=False) for b in page.get("badges", [])] or _badges()
    raw = json.loads(SERIES.read_text(encoding="utf-8"))
    bars = {"title": "Where the four lines end", "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
    species = [{"kind": "chart_to", "at": 12.0, "dur": 2.0, "to": "recast", "state": 1, "keyed": True}]
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td); (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/golden-bars.series.json").write_text(json.dumps(bars), encoding="utf-8")
        world = {"kind": "ledger", "page": page, "page_states": [BST._page_state("golden-bars:bars", ep, "golden")], "ken_burns": {"scale": 0, "x": 0, "y": 0}}
        BST.derive_rescale_states(world, species, "ledger:golden-series:line;then=golden-bars:bars", ep)
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: ledger keyed recast", scenes, {}, None), _base_uris()


def thread_baseline() -> tuple[dict, dict]:
    """P50 T15 / HF-16 - THE WIRE: TWO PAGES, and one element of the first still standing under the second.

    The intake's HF-16 ("the three threads - the wire, the ruler, the protagonist chip - one continuous line as the
    film's spine") against our own persistence rule: ours persists the PAGE, and this persists one MARK across a page
    change. Scene 1 is the line page every other golden uses; scene 2 is a bars page of where those lines end, and its
    plate id names `thread=s0` - the first line survives the cut and lies under the bars as ground, on the same stage
    pixels it was drawn on.

    Both halves are the shipped ones: the page specs are `ledger_page.build_spec`'s, the thread is put through the
    compiler's own `thread_mark_error` against the page before it (the check the shot table would get), and the carry
    is `species/thread.mjs` in the player. Judged MID-CARRY (FRAME_T 15.8): scene 2's roll-out is over, its cream is
    building, it has drawn nothing of its own yet - and the wire is there, receding from the subject it was to the
    ground line it becomes."""
    import json
    import build_scene_timeline_f as BST
    series = LPG.load_series(SERIES)
    page1 = LPG.build_spec(series, "line", None, "right")
    page1["field"] = "scribble"
    raw = json.loads(SERIES.read_text(encoding="utf-8"))
    bars = {"title": "Where the four lines end", "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
    page2 = LPG.build_spec(bars, "bars", None, "right")
    page2["field"] = "scribble"
    world1 = {"kind": "ledger", "page": page1, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    err = BST.thread_mark_error(world1, "s0", "golden thread-baseline")
    assert err is None, err
    page2["thread"] = {"key": "s0", "from": "s01"}   # exactly what `;thread=s0` compiles to on the second row
    scenes = [{"scene_id": "s01", "world": world1, "exit": "cut", "span": [0.0, THREAD_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [THREAD_CUT, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: the wire across a page boundary", scenes, {}, None), _base_uris()


def tags_to_bars() -> tuple[dict, dict]:
    """P50 T11: the KEYED-TAGS recast (Bravos 104-105) - a TWO-line page hands each line's TERMINAL TAG to its bar.
    The tag is the mark that becomes the bar's number: it slides and grows into the bar's own value type while the
    line un-draws by length beneath it, and no value is ever written twice. Two lines, not four, so the two tags are
    legible in the frame; both are the golden series' own, and the bars are their last values, DERIVED into a temp
    episode and built as a `then=` state by the compiler itself (judged mid-slide, FRAME_T 13.0)."""
    import json
    import tempfile
    import build_scene_timeline_f as BST
    raw = json.loads(SERIES.read_text(encoding="utf-8"))
    lasts = [round(float(s["pts"][-1][1]), 1) for s in raw["series"][:2]]
    # the tag IS the bar's number: each line is named "<its last value> <short name>" at its end (E53 s8), so when the
    # tag lands on the bar the NUMBER does not change - only the name drops, to re-appear as the bar's own label
    two = dict(raw, title="Two layers, one year", sub="index, 100 = Aug '25",
               series=[dict(s, label=f"{v}", name=n) for s, v, n in zip(raw["series"][:2], lasts, ("Memory", "Chips"))])
    two.pop("badges", None)
    bars = {"title": "Where the two end", "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": v, "color": sr.get("color", "crimson")}
                     for sr, short, v in zip(raw["series"][:2], ("Memory", "Chips"), lasts)]}
    species = [{"kind": "chart_to", "at": 12.0, "dur": 2.0, "to": "recast", "state": 1, "keyed": "tags"}]
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td); (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/golden-two.series.json").write_text(json.dumps(two), encoding="utf-8")
        (ep / "evidence/objects/golden-two-bars.series.json").write_text(json.dumps(bars), encoding="utf-8")
        plate = "ledger:golden-two:line;then=golden-two-bars:bars"
        world = BST.world_for_plate(plate, (0, 0, 0), ep)
        world["ken_burns"] = {"scale": 0, "x": 0, "y": 0}
        world["page"]["field"] = "soak"
        BST.derive_rescale_states(world, species, plate, ep)
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: tags to bars", scenes, {}, None), _base_uris()


# P50 T9: the two bands of the tiers golden - synthetic reserves, the SHAPE is what is under test
# (a level that holds and then falls against one that falls all along), on ONE x of twenty half-years.
TIERS_X = [2015 + 0.5 * i for i in range(21)]


def data_to_bars() -> tuple[dict, dict]:
    """E64 / R26-49: the DATA-KEYED recast - one line becomes the n bars that ARE its own consecutive changes.

    The fixture is a synthetic MONTHLY balance sheet (36 months; the shape is what is under test, as the tiers
    golden's reserves are), and the bars page is computed FROM it: bar k is the change from month to month over
    the last four, to the tenth the page prints. Nothing here names a key: the row is a PLAIN
    `chart_to recast`, and the compiler derives `keyed: "data"` and its key_map (E64) - so the golden proves the
    derivation, the key map and the painter together.

    Judged at dur * 0.5 (FRAME_T 13.0): the four data are in flight between the line and their bar tops, the bars
    are part-grown beneath them, the line has left its history, the standing tick labels are most of the way
    un-written and the arriving ones have begun."""
    import json
    import tempfile
    import build_scene_timeline_f as BST
    n_months, base = 36, 1200.0
    steps = [0.0, 9.4, -4.2, 12.1, -6.6, 5.3, 14.2, -9.9, 3.7, 11.4, -12.8, 6.9]   # a level that wanders, month by month
    pts, v = [], base
    for i in range(n_months):
        v = round(v + steps[i % len(steps)] + (1.5 if i % 5 else -2.0), 1)
        x = round(2023.25 + i / 12, 4)
        pts.append([x, v])
    last = pts[-5:]
    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    bars = [{"label": months[int(round((p[0] - int(p[0])) * 12)) % 12], "value": round(p[1] - q[1], 1),
             "color": "crimson" if p[1] < q[1] else "teal"} for q, p in zip(last, last[1:])]
    line = {"title": "The pile, month by month", "sub": "holdings, $bn, monthly", "src": "Golden fixture",
            "unit": "$", "ylabel": "$bn", "series": [{"name": "Holdings", "label": "36 months", "color": "crimson", "pts": pts}]}
    page2 = {"title": "The monthly print", "sub": "change in holdings, $bn a month", "src": "Golden fixture",
             "unit": "$", "bars": bars}
    species = [{"kind": "chart_to", "at": 12.0, "dur": 2.0, "to": "recast", "state": 1}]   # NO key: the compiler derives it
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td); (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/golden-pile.series.json").write_text(json.dumps(line), encoding="utf-8")
        (ep / "evidence/objects/golden-prints.series.json").write_text(json.dumps(page2), encoding="utf-8")
        plate = "ledger:golden-pile:line;then=golden-prints:bars"
        world = BST.world_for_plate(plate, (0, 0, 0), ep)
        world["ken_burns"] = {"scale": 0, "x": 0, "y": 0}
        world["page"]["field"] = "soak"
        BST.derive_rescale_states(world, species, plate, ep, sid="s01")
    assert species[0].get("keyed") == "data" and len(species[0].get("key_map") or []) == 4, species[0]
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: data to bars", scenes, {}, None), _base_uris()


def tiers_two() -> tuple[dict, dict]:
    """P50 T9 (R26-24; Bravos shots 35-36's two-panel SPR): N SMALL MULTIPLES on one page - two
    reserves, one unit, one shared x, each band on its own scale with its own honest zero (E53 s4)
    and its own gridlines, the tier titles the series' own names.

    The bands draw IN TURN, which is the page's whole grammar: the first draws on the page's own
    build beat, and the second is held at nothing by a `build_to` at its datum 0 and then drawn on
    its OWN WORD by a second one (`tier: 1` - a tier IS a series index, and this is the word the
    author writes). Then the drop of the second band is MEASURED on a later word by a bracket in its
    `form: "bar"` - the same two data, drawn as a bar in the accent (shot 36).

    The page is `ledger_page.build_spec`'s own, and the row is put through the compiler's
    `validate_species` and `derive_rescale_states` before it is written, so this golden proves the
    builder, the compiler's grammar and the painter together. Judged with the drop bar landing (14.2)."""
    import build_scene_timeline_f as BST
    series = {
        "title": "Two reserves, one decade",
        "sub": "strategic petroleum reserves, each band on its own scale",
        "src": "Synthetic series for the golden surface; not a figure about the world",
        "xticks": [[2015, "2015"], [2020, "2020"], [2025, "2025"]],
        "tiers": [
            {"name": "JAPAN", "unit": "Mb", "color": "cobalt",
             "pts": [[x, round(324 - 0.4 * i - (2.6 * max(0, i - 12)), 1)] for i, x in enumerate(TIERS_X)]},
            {"name": "UNITED STATES", "unit": "Mb", "color": "crimson",
             "pts": [[x, round(695 - 2.0 * i - (14.0 * max(0, i - 10)), 1)] for i, x in enumerate(TIERS_X)]},
        ],
    }
    page = LPG.build_spec(series, "tiers", None, "right")
    page["field"] = "scribble"
    species = [
        {"kind": "build_to", "at": 4.0, "dur": 0.5, "tier": 1, "target": {"kind": "datum", "index": 0}},   # the second band waits: the build beat is spent on this cap
        {"kind": "build_to", "at": 9.5, "dur": 2.0, "tier": 1, "target": {"kind": "datum", "index": len(TIERS_X) - 1}},
        # the drop, MEASURED (Bravos shot 36): 675 Mb at i=10 to 579 at i=16. The bracket stands to the
        # right of the two data it measures, so a span that ends at the LAST datum has no room for its own
        # label - this one ends where the page still has a margin, and the label writes beside the bar.
        {"kind": "bracket", "at": 12.0, "dur": 2.5, "series": 1, "from": 10, "to": 16,
         "label": "-96 Mb", "sub": "the drawdown", "color": "crimson", "form": "bar"},
    ]
    plate = "ledger:golden-tiers:tiers"
    errs = BST.validate_species(species, (0, 0, 0), plate)
    assert not errs, errs
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    BST.derive_rescale_states(world, species, plate, REPO)
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: two tiers on one x", scenes, {}, None), _base_uris()


# P50 T6: the census. The shares are Bravos's own exports-by-partner profile (shots 89-91) rounded to
# the tenth; the page claims BREADTH, and the cross claims the three partners' share as a NUMBER.
TREEMAP_SHARES = [
    ("United States", 16.8), ("Hong Kong", 8.5), ("Japan", 4.7), ("Korea", 4.5), ("Vietnam", 4.1),
    ("India", 3.4), ("Germany", 3.1), ("Netherlands", 3.0), ("Malaysia", 2.5), ("Russia", 2.4),
    ("Brazil", 2.0), ("Australia", 1.9), ("Spain", 1.3), ("Saudi Arabia", 1.2), ("Rest of world", 40.6),
]


def treemap_cross() -> tuple[dict, dict]:
    """P50 T6 (E53 s1's second amendment - the CENSUS exception, ruled 2026-09-10; Bravos shots 89-91):
    a treemap of exports by partner, squarified toward 3:2 by `ledger_page.py` at BUILD time inside
    page_boxes' own plot, labelled only where the research's floors say a label fits (value font
    >= 18 px; nothing under 80 x 36 px) and counting the rest in one legend line.

    On a word three partners take an X and the crossed SHARE is WRITTEN on the page - the two halves
    of the exception, which is why they are one species. The shrink afterwards is P48's park and
    needs nothing new: `lpPaintPark` scales the chart's own svg, and every cell rides it (E58 -
    one affine transform, never a re-layout; Sondag 2018).

    Judged once the X's are struck and the share is written (10.9)."""
    import build_scene_timeline_f as BST
    series = {
        "title": "China's exports, by partner",
        "sub": "share of goods exports, one year",
        "src": "Synthetic census for the golden surface; not a figure about the world",
        "unit": "%",
        "shares": [{"label": label, "value": value} for label, value in TREEMAP_SHARES],
        "total": 100,
    }
    page = LPG.build_spec(series, "treemap", None, "right")
    page["field"] = "scribble"
    species = [{"kind": "cross", "at": 9.0, "dur": 3.0, "cells": ["United States", "Japan", "Korea"],
                "text": "3 partners, 26 % of exports"}]
    plate = "ledger:golden-treemap:treemap"
    errs = BST.validate_species(species, (0, 0, 0), plate)
    assert not errs, errs
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    BST.derive_rescale_states(world, species, plate, REPO)   # the cross's cells are checked against the page's own labels
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the census and its X marks", scenes, {}, None), _base_uris()


def chip_board() -> tuple[dict, dict]:
    """P50 T2: the icon board (Bravos shots 26-28) - three chips land on three words across a bare plate and the
    middle one is crossed out on a later one. The glyphs are the SOURCED icons under content/video_engine/assets/icons
    (Lucide, ISC - assets/icons/SOURCES.md), embedded by the compiler's OWN icon_geometry, so this golden proves the
    asset route and the painter module together. Every chip carries the breath idle (E49): the board holds, it never
    goes still. Judged after all three have landed and the cross has finished drawing (FRAME_T 11.0)."""
    import build_scene_timeline_f as BST
    board = [("factory", "PLANTS", 0.24), ("ship", "FREIGHT", 0.5), ("cpu", "CHIPS", 0.76)]
    species = [{"kind": "chip", "at": 5.0 + 1.2 * i, "dur": 14.0 - 1.2 * i, "icon": icon, "label": label,
                "idle": "breath", "target": {"kind": "point", "x": x, "y": 0.62}}   # below the caption band: the board is read, not stepped on
               for i, (icon, label, x) in enumerate(board)]
    species[1]["cross_at"] = 10.0   # the retraction: the middle prediction did not happen
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    for icon, _label, _x in board:
        uris[BST.ICON_PREFIX + icon] = BST.icon_geometry(icon)
    return _timeline("Golden: the icon board", scenes, {}, None), uris


def flow_swap() -> tuple[dict, dict]:
    """P50 T4: THE FLOW DIAGRAM (Bravos shots 82-86). Three nodes inside a dashed box draw on one word - the
    frame by the nib, the chips on the badge spring, the CLOTHOID arrows between them by length - and on a
    LATER word ONE node swaps (the standing chip's landing run backward, the new one's run forward, in the
    same spot) while the arrows stand. The rhyme.

    The glyphs are the SOURCED icons under content/video_engine/assets/icons (Lucide, ISC - assets/icons/
    SOURCES.md), embedded by the compiler's OWN icon_geometry, so this golden proves the asset route, the
    clothoid fitter and the painter module together. The diagram carries the breath idle (E49): it holds, it
    never goes still. Judged after the swap has finished (FRAME_T 12.6)."""
    import build_scene_timeline_f as BST
    species = [{"kind": "flow", "at": 4.0, "dur": 18.0, "idle": "breath",
                "target": {"kind": "region", "x0": 0.10, "y0": 0.50, "x1": 0.90, "y1": 0.90},   # below the caption band: the diagram is read, not stepped on
                "nodes": [{"id": "plant", "icon": "factory", "label": "PLANTS"},
                          {"id": "freight", "icon": "ship", "label": "FREIGHT"},
                          {"id": "price", "icon": "coins", "label": "PRICE"}],
                "edges": [["plant", "freight"], ["freight", "price"]],
                "swap": {"at": 11.0, "node": "freight", "icon": "cpu", "label": "CHIPS"},
                "tag": "1973"}]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    for name in sorted({n["icon"] for n in species[0]["nodes"]} | {species[0]["swap"]["icon"]}):
        uris[BST.ICON_PREFIX + name] = BST.icon_geometry(name)
    return _timeline("Golden: the flow diagram and its swap", scenes, {}, None), uris


def span_decade() -> tuple[dict, dict]:
    """P50 T4 / R26-25 (the intake's Archetype 5; Bravos 107-110's "Decades"): a ledger LINE page - built
    exactly as `ledger-page-mid-build` builds its page, with no emphasis so every series is drawn and the
    band stands behind all four - carrying a SPAN: the stretch between two data shaded on its word and NAMED
    above it by the hand. The band is re-read from the live points every frame, so it would follow a rescale;
    here it stands on the page's own scale. Judged once the name is written (FRAME_T 12.6)."""
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    species = [{"kind": "span", "at": 8.0, "dur": 8.0, "from": 40, "to": 150,
                "label": "THE RUN-UP", "color": "cobalt"}]
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the span on a ledger page", scenes, {}, None), _base_uris()


# P50 T3: the press stack. Three claims, three words, one pile - Bravos shots 5-10's grammar.
# R26-55: each card carries its pulled phrase as WORDS as well as pixels (the last field), because a crop cannot
# re-line; the card sets the words as live type and keeps the crop as the provenance strip under them.
PRESS_CARDS = [
    ("ev-press-a", 5.0, "THE HERALD, 4 MAR 2026", {"x0": 0.08, "y0": 0.17, "x1": 0.62, "y1": 0.46},
     [(0.06, 0.14, 0.64, 0.44), (0.06, 0.58, 0.88, 0.72), (0.06, 0.80, 0.52, 0.90)],
     "the historic normal was never normal"),
    ("ev-press-b", 7.4, "THE LEDGER, 6 MAR 2026", {"x0": 0.30, "y0": 0.15, "x1": 0.92, "y1": 0.45},
     [(0.28, 0.12, 0.94, 0.43), (0.06, 0.58, 0.70, 0.72), (0.06, 0.80, 0.84, 0.90)],
     "the deficit outlived every plan to close it"),
    ("ev-press-c", 9.8, "THE DISPATCH, 9 MAR 2026", {"x0": 0.12, "y0": 0.16, "x1": 0.55, "y1": 0.47},
     [(0.10, 0.13, 0.57, 0.45), (0.06, 0.58, 0.92, 0.72), (0.06, 0.80, 0.38, 0.90)],
     "the rule changed while the market slept"),
]
PRESS_CROP = (528, 160)   # the headline crop every golden card is cut at - its aspect is what the strip is laid out from


# P50 T5: the vector map. Two declared MAP POINTS (map box units, x = (lon + 180) / 360 * 1000,
# y = (90 - lat) / 180 * 500): the Gulf the oil leaves, and the mid-Atlantic where the year stamps.
VECMAP_GULF = {"kind": "mappoint", "x": 644, "y": 178}      # ~52E 26N
VECMAP_ATLANTIC = {"kind": "mappoint", "x": 430, "y": 100}  # ~25W 54N, clear of the arc it dates (read in the frame: at 40N the year sat under the X)


def vecmap_arc() -> tuple[dict, dict]:
    """P50 T5: THE VECTOR MAP (Bravos shots 57-80) on one clock, in PORTRAIT - the aspect the map has to
    survive, because a 9:16 stage is where a world map is hardest to read.

    Iran LIGHTS on its word (the country's own outline filled to the accent - the spotlight's cousin, never
    a ring: E56); an ARC leaves the Gulf and crosses to the United States, drawn by length with the nib as a
    clothoid that lifts toward the pole, and is CUT by an X at its midpoint on a later word; "1996" STAMPS
    over the Atlantic at the year's size; China lights and takes "1.4 Billion Barrels" at its centroid.

    The world is built by the compiler's OWN world_for_plate off the plate id `vecmap:IRN,USA,CHN`, and the
    map rides the asset map as `map:world-110m` through its OWN world_map_json - so this golden proves the
    data (Natural Earth 110m, public domain), the compiler's route and the painter module together. The map
    carries the breath idle (E49): a held world is never a still image. Judged once the X is struck (12.4)."""
    import build_scene_timeline_f as BST
    world = BST.world_for_plate("vecmap:IRN,USA,CHN", (0, 0, 0), None)
    species = [
        {"kind": "light", "at": 5.0, "dur": 14.0, "idle": "breath", "target": {"kind": "country", "id": "IRN"}},
        {"kind": "arc", "at": 6.6, "dur": 12.0, "crossed": 11.5, "from": VECMAP_GULF, "to": {"kind": "country", "id": "USA"}},
        {"kind": "stamp", "at": 8.4, "dur": 10.0, "size": "year", "text": "1996", "target": VECMAP_ATLANTIC},
        {"kind": "light", "at": 9.6, "dur": 9.0, "idle": "breath", "target": {"kind": "country", "id": "CHN"}},
        {"kind": "stamp", "at": 10.4, "dur": 8.0, "text": "1.4 Billion Barrels", "target": {"kind": "country", "id": "CHN"}},
    ]
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    uris[BST.MAP_PREFIX + world["map"]] = BST.world_map_json(world["map"])
    return _timeline("Golden: the vector map, its arc and its stamps", scenes, {}, "9:16"), uris


def png_cutout(w: int, h: int, rgb: tuple[int, int, int], shapes: list[tuple[float, float, float, float]]) -> bytes:
    """A FOREGROUND LAYER: the named boxes opaque in `rgb`, every other pixel fully transparent (RGBA, colour
    type 6). The alpha is the whole point of the layer, which is why the compiler embeds it raw - `data_uri`'s
    capped path re-encodes through RGB and would flatten it."""
    raw = bytearray()
    for y in range(h):
        line = bytearray(b"\x00")
        for x in range(w):
            hit = any(x0 * w <= x < x1 * w and y0 * h <= y < y1 * h for (x0, y0, x1, y1) in shapes)
            line += bytes((*rgb, 255)) if hit else b"\x00\x00\x00\x00"
        raw += line

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


# P50 T15 / HF-17: the synthetic front of the golden's plate - a desk edge across the foot of the frame and the
# post of a lamp beside it. A SHAPE, deliberately: what is under test is that the plate's front paints over the
# card, not whether this particular cutout is beautiful (the operator judges the cue on a real beat).
OCCLUDER_SHAPES = [(0.0, 0.62, 1.0, 1.0), (0.70, 0.30, 0.78, 0.66)]
OCCLUDER_PLACE = {"x": 620, "y": 300, "w": 900, "h": 560}   # straddles BOTH shapes: the desk edge cuts its foot, the lamp post its right-hand side - one card, two occluders, no blur anywhere


def occluder_dock() -> tuple[dict, dict]:
    """P50 T15 / HF-17 - OCCLUSION IS THE DEPTH CUE: one card docked on a plate, and the plate's own FOREGROUND
    layer painting over it.

    The intake read Bravos's depth as occlusion where doc 29 had proposed a focus rack, and the operator has
    preferred the wash to a rack since 2026-09-06; this is the third reading, built so it can be judged in a
    frame instead of argued. The card lands at OCCLUDER_PLACE, which straddles the desk edge at 0.62 and the
    lamp post beside it: the top of the card is in the room, the bottom is behind the desk. Nothing is blurred,
    nothing is dimmed - the card is simply behind something.

    The dock entry is the compiler's own (`dock_entry(behind=..., fg=...)`), the layer rides the asset map under
    the key the compiler writes (`fg:<plate>:<layer>`), and the player mounts it above the docks and below the
    species and caption layers. Judged with the card landed and still (FRAME_T 12.0)."""
    import build_scene_timeline_f as BST
    aid, layer = "plate-plain", "desk"
    fg_key = f"{BST.FG_PREFIX}{aid}:{layer}"
    dock = BST.dock_entry("ev-occluded-card", 0, 4.0, RUNTIME, 2, BST.DOCK_KIND_IMAGE, OCCLUDER_PLACE,
                          None, None, False, behind=layer, fg=fg_key)
    ev = {"ev-occluded-card": {"title": "The card behind the desk", "source": "P50 T15 HF-17", "species": "deck",
                               "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:2]}}
    scenes = [{"scene_id": "s01", "world": {"asset_id": aid, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [dock], "species": []}]
    uris = _base_uris()
    uris["ev-occluded-card"] = uri("image/png", png_solid(640, 400, (23, 105, 194)))
    uris[fg_key] = uri("image/png", png_cutout(480, 270, (26, 31, 38), OCCLUDER_SHAPES))
    return _timeline("Golden: the dock behind the plate's front", scenes, ev, None), uris


# ---- P58 T3: THE CAMERA OVER PLANES ------------------------------------------------------------
# The plate is the Tokyo customs dock (`world-tokyo-customs-dock-v1`, registered review_only by P58 T2), split by
# P58 T1's b-sam route into four planes and COMMITTED at 480 px / 256 colours under inputs/dock-layers with its own
# `<plate>.layers.json` - a golden's inputs are committed inputs (the same rule that committed the Bessent cutout).
# The world's `layers` and its `ly:` asset keys are the COMPILER'S OWN (`plate_depth_planes` + `LY_PREFIX`), read
# off that sidecar here exactly as a build reads one, so the golden proves the whole route and not a hand-written
# shape. Doc 24's factors come with the roles: -far 1.0, -mid 1.15, subject 1.275 (DERIVED), -near 1.40.
DOCK_LAYERS = HERE / "inputs" / "dock-layers"
DOCK_PLATE = DOCK_LAYERS / "world-tokyo-customs-dock-v1.png"
# the card lands low and right, over the quay - the region the eye then goes to
CAMERA_LAYERS_PLACE = {"x": 1160, "y": 600, "w": 640, "h": 400}
CAMERA_LAYERS_ENTER = 5.0      # the card arrives, stop-action (`land`: ANTIC_S + DROP_S to contact)
CAMERA_LAYERS_AT = 6.0         # ... and the eye follows it in, one focus zoom, 2 s: E51 - a push is tied to a LANDING
CAMERA_LAYERS_DUR = 2.0


def camera_layers() -> tuple[dict, dict]:
    """P58 T3 - ONE EYE, A DEPTH PER LAYER: the camera's move, taken by four planes at four parallax factors.

    The move is the smallest authored one on the record and it has a reason that is not the parallax: a card
    LANDS on the quay at 5.0 and the eye goes to it (E59's second reason, E51's law - a push is tied to a
    landing). Nothing was added to show the depth off; the depth is what that one move does to a plate that
    ships in planes. E49 is why this is the only kind of move allowed to exist here - a drift added to display
    parallax is the crime, not the cure.

    WHAT THE FRAMES SHOW. `@proof-start` is before the move (5.9): the camera is LOCKED, every k has nothing to
    multiply, and the four planes paint the flat composite exactly. `@proof-mid` is mid-zoom (u 0.28). The base
    frame (7.9) is inside the focus zoom's HOLD - the servo law: it reaches FOCUS_SCALE at u = 1/1.8 and then
    stands dead still - so the pin is byte-exact and the lamp (1.40) has led the desk (1.275), which has led the
    containers (1.15), which have led the sky (1.0)."""
    import build_scene_timeline_f as BST
    aid = "plate-dock"
    planes = BST.plate_depth_planes(DOCK_PLATE)
    layers = [{"key": f"{BST.LY_PREFIX}{aid}:{p['role']}", "k": p["depth"], "role": p["role"]} for p in planes]
    dock = BST.dock_entry("ev-quay-card", 0, CAMERA_LAYERS_ENTER, RUNTIME, 2, BST.DOCK_KIND_IMAGE,
                          CAMERA_LAYERS_PLACE, "land")
    ev = {"ev-quay-card": {"title": "The card the eye goes to", "source": "P58 T3", "species": "deck",
                           "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:2]}}
    P = CAMERA_LAYERS_PLACE
    species = [{"kind": "focus_zoom", "at": CAMERA_LAYERS_AT, "dur": CAMERA_LAYERS_DUR,
                "target": {"kind": "region", "x0": P["x"] / 1920, "y0": P["y"] / 1080,
                           "x1": (P["x"] + P["w"]) / 1920, "y1": (P["y"] + P["h"]) / 1080}}]
    scenes = [{"scene_id": "s01",
               "world": {"asset_id": aid, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0},
                         "layers": layers},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [dock], "species": species}]
    uris = _base_uris()
    uris[aid] = BST.data_uri(DOCK_PLATE)                     # the flat plate the compiler always embeds (unpainted here)
    for p, ly in zip(planes, layers):
        uris[ly["key"]] = BST.data_uri(Path(p["file"]))      # RAW, as the compiler writes it: the alpha IS the plane
    uris["ev-quay-card"] = uri("image/png", png_solid(640, 400, (23, 105, 194)))
    tl = _timeline("Golden: one camera, four depth planes", scenes, ev, None)
    tl["kinetics"] = {"camera": True}                        # E59's own module drives the species (camNow), not camXf
    return tl, uris


# ---- P58 T4: THE PAGE AS A CARD AT A DEPTH -----------------------------------------------------
# E98 s3: *"the ledger page is a card at a depth ... the flat page stays the default reading form"*. The page is
# the SAME ledger line page every other golden reads, authoring the two new options and nothing else, over the
# SAME layered dock plate and the SAME kind of move `camera-layers` uses - a focus zoom tied to a card LANDING
# (E51). The plate is the scene BEFORE it: a `card` page's world is transparent (`.world.ledger.cardworld`) and
# the player paints the previous scene into the other buffer, which is how a page stands in a plate's space at
# all. The move is authored on BOTH scenes because both are on screen - the page in one buffer, the plate it
# stands in front of in the other - and one eye moves over both.
PAGE_DEPTH_CUT = 5.0            # the page arrives (a cut: the world change is the page)
PAGE_DEPTH_CARD = 12.6          # ... builds, and a card LANDS on it (stop-action `land`)
PAGE_DEPTH_AT = 13.6            # ... and the eye goes to that landing, one focus zoom, 2 s (E51: never to a thing that just sits there)
PAGE_DEPTH_DUR = 2.0
PAGE_DEPTH_K = 1.15             # the page's own parallax factor - doc 24's `-mid`: the page stands in the dock's space, nearer than the sky and behind the lamp
PAGE_DEPTH_TILT = "tilt:14,y"   # turned 14 deg about its own vertical axis: the ruled lines converge to the right, the near edge is left
PAGE_DEPTH_PLACE = {"x": 1160, "y": 600, "w": 640, "h": 400}


def page_depth() -> tuple[dict, dict]:
    """P58 T4 - THE LEDGER PAGE AS A CARD AT A DEPTH: `;plane=tilt:14,y;depth=1.15` on a page, and nothing else.

    The page is drawn exactly as it is drawn today - the roll-out, the soak, the punch, its chart building on its
    own clock - and then turned onto the plane the compiler resolved (four corners, TL TR BR BL, the ART-embed
    grammar's own shape) and seen by the one camera at its own depth. The flat page is untouched: no option, no
    string, the same bytes.

    WHAT THE FRAMES SHOW. `@proof-build` (10.9) is mid-build: the chart drawing ON the tilted page, so the ink
    lands on the surface rather than in front of it. The base frame (15.5) is the HOLD - the card landed, the eye
    arrived, the page taking 1.15 of that move while the four planes behind it take 1.0 / 1.15 / 1.275 / 1.40:
    the page is a thing standing in the dock's space, and the number on it still reads (E28). `@proof-leave`
    (28.5) is the retract, half way down its drain - a page at a depth leaves the way every page leaves."""
    import build_scene_timeline_f as BST
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    page["card"] = True                                        # `;card=yes`: the page keeps the card's rounded corners and doc 29 s1.2's hard-edge shadow, and the world around it stays visible
    page["depth"] = BST.page_depth_k(str(PAGE_DEPTH_K), "golden")
    page["plane"] = BST.page_plane_spec(PAGE_DEPTH_TILT, "golden")
    assert not BST.page_plane_error(page["plane"], "golden"), BST.page_plane_error(page["plane"], "golden")
    aid = "plate-dock"
    planes = BST.plate_depth_planes(DOCK_PLATE)
    layers = [{"key": f"{BST.LY_PREFIX}{aid}:{p['role']}", "k": p["depth"], "role": p["role"]} for p in planes]
    P = PAGE_DEPTH_PLACE
    species = [{"kind": "focus_zoom", "at": PAGE_DEPTH_AT, "dur": PAGE_DEPTH_DUR,
                "target": {"kind": "region", "x0": P["x"] / 1920, "y0": P["y"] / 1080,
                           "x1": (P["x"] + P["w"]) / 1920, "y1": (P["y"] + P["h"]) / 1080}}]
    dock = BST.dock_entry("ev-desk-card", 0, PAGE_DEPTH_CARD, RUNTIME, 1, BST.DOCK_KIND_IMAGE, P, "land")
    ev = {"ev-desk-card": {"title": "The card the eye goes to", "source": "P58 T4", "species": "deck",
                           "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:1]}}
    scenes = [
        {"scene_id": "s01", "world": {"asset_id": aid, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0},
                                      "layers": layers},
         "exit": "cut", "span": [0.0, PAGE_DEPTH_CUT], "docks": [], "species": list(species)},
        {"scene_id": "s02", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
         "exit": "cut", "span": [PAGE_DEPTH_CUT, RUNTIME], "docks": [dock], "species": list(species)},
    ]
    uris = _base_uris()
    uris[aid] = BST.data_uri(DOCK_PLATE)
    for p, ly in zip(planes, layers):
        uris[ly["key"]] = BST.data_uri(Path(p["file"]))        # RAW, as the compiler writes a plane: the alpha IS the plane
    uris["ev-desk-card"] = uri("image/png", png_solid(640, 400, (23, 105, 194)))
    tl = _timeline("Golden: the page as a card at a depth", scenes, ev, None)
    tl["kinetics"] = {"camera": True}                          # E59's own module drives the species (camNow), as on camera-layers
    return tl, uris


# ---- P58 T5: THE TWO CHART FORMS IN 2.5D ---------------------------------------------------------------------
# Each form is goldened on data that is ALREADY a golden flat, so human gate 3 reads a pair and not a picture:
#   `form-tilted-line`  beside `ledger-page-mid-build` - the same series, the same `build_spec(... "line", 0,
#                       "right")`, the same scribble field; the ONLY difference on the page is `;form=tilted_line`
#   `form-extruded-bar` beside `thread-baseline`'s scene 2 - the same four line-ends as bars, built by the same
#                       `build_spec(bars, "bars", None, "right")`; the only difference is `;form=extruded_bar`
# Both go through the COMPILER's own option (`page_form_spec`), so the golden proves the grammar, the refusal's
# sibling and the painter together, and neither page names a species, a dock or a move: what the frames show is
# the form, and nothing is added to make it visible (E49/E59).
FORM_LINE_T = (6.0, 9.0, 28.5)   # the three instants both forms are read at: mid-BUILD (the same t the flat line page's golden is judged at), the HOLD, and mid-LEAVE


def _form_bars_series() -> dict:
    """The bars object `thread-baseline` builds its second page from: where the four lines end."""
    import json
    raw = json.loads(SERIES.read_text(encoding="utf-8"))
    return {"title": "Where the four lines end", "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}


# ---- P61 T4b / E99 s35 - THE TWO GENERATED LEDGER PLATES ------------------------------------------------------
# The decided ledger-page signature (E22, doc 41): a generated CREAM page and the same page with the charcoal filled
# to its DECKLE, cross-faded over it. Both are quarantine objects of the claim `steel-and-paper-ledger-page-v1` and
# are gitignored - E99 s31: an approved image leaves quarantine, it never enters git - so this fixture READS them
# where they lie and encodes them into the source's `uris`, exactly as the arm-b race build does
# (`build_race_arms.plate_file` / `plate_uri`, the same JPEG q88). Neither file is copied into a tracked path.
#   review/claims/steel-and-paper-ledger-page-v1/objects/world-ledger-blank-page-cream-v1.png
#     1920x1080, sha256 39f98e295c0f85fc8f779904661365dd886f2789e5f5c36b0db2250ff31709f8
#   review/claims/steel-and-paper-ledger-page-v1/objects/world-ledger-inked-deckle-cream-v1.png
#     1920x1080, sha256 6960fa61406cbfabfde9f0b601b62caa54f4f56cbabbe7490009fbf52cb485e7
# The BOARD is the deckle's innermost rectangle, read from the tracked `proofs/ledger/deckle-edge.json` - the chart
# is never drawn over the torn edge.
PLATE_CLAIM = "review/claims/steel-and-paper-ledger-page-v1/objects"
PLATE_BLANK, PLATE_INKED = "world-ledger-blank-page-cream-v1", "world-ledger-inked-deckle-cream-v1"
DECKLE_EDGE = REPO / "content/video_engine/scripts/proofs/ledger/deckle-edge.json"


def _plate_file(pid: str) -> Path:
    """Where the gitignored plate lies - the checkout's own quarantine, or the worktree's. READ only."""
    rels = (Path("content/video_engine") / PLATE_CLAIM / f"{pid}.png", Path(PLATE_CLAIM) / f"{pid}.png")
    roots = (REPO, REPO / ".claude/worktrees/sweet-villani-1c3a16")
    for root in roots:
        for rel in rels:
            if (root / rel).exists():
                return root / rel
    raise SystemExit(f"the generated ledger plate {pid!r} is in neither the checkout nor the worktree "
                     f"({PLATE_CLAIM}) - it is a gitignored quarantine object (E99 s31) and this source cannot be "
                     "rebuilt without it; the committed source and its frames stand until it is back")


def _two_plate_page(page: dict, uris: dict) -> None:
    """Give a page the two-plate cross-fade ground and put the plates in the uris (E99 s35's continuity field)."""
    from PIL import Image
    page["plate"], page["field_plate"] = PLATE_BLANK, PLATE_INKED
    page["board"] = json.loads(DECKLE_EDGE.read_text(encoding="utf-8"))["inner"]
    for pid in (PLATE_BLANK, PLATE_INKED):
        im = Image.open(_plate_file(pid)).convert("RGB")
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=88, optimize=True)
        uris[pid] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def form_extruded_bar() -> tuple[dict, dict]:
    """P58 T5 - THE EXTRUDED BAR (`;form=extruded_bar`): every bar a prism, and not one label moved.

    The page is `thread-baseline`'s own second page - the same four values, the same builder, the same field - and
    the option is the whole difference. Each bar gets three polygons BEHIND its face: a hard-edge cast shadow
    (doc 29 s1.2, clipped at the zero line), the side face and the cap face, both the bar's OWN ink at a darkening
    ratio under the page's one light. The face draws as it always did and the prism grows on the same u.

    WHAT THE FRAMES SHOW. `@proof-build` (6.0) is mid-build: the prisms growing with their faces, each one's mass
    running the way its own value runs. The base frame (9.0) is the HOLD - the page built, the values printed
    exactly where the flat page prints them, the capsule on the emphasised bar untouched. `@proof-leave` (28.5)
    is the retract."""
    import build_scene_timeline_f as BST
    page = LPG.build_spec(_form_bars_series(), "bars", None, "right")
    page["field"] = "soak"   # P61 T4b / E99 s35: this page INTRODUCES the four values - the soak is its transition
    page["form"] = BST.page_form_spec("extruded_bar", page["builder"], "golden")
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: the extruded bar", scenes, {}, None), _base_uris()


def form_tilted_line() -> tuple[dict, dict]:
    """P58 T5 - THE TILTED-PLANE LINE (`;form=tilted_line`): the line drawn ON a plane, its numbers upright.

    The page is `ledger-page-mid-build`'s, to the key, plus the one option. The compiler resolves the plane's four
    corners with `page_plane_quad` - the same closed form `plane=` uses - and the player projects the plot region
    onto them through the ONE homography: the ruled baseline and the gridlines converge to the plane's vanishing
    direction (the monograph s2.4), the series are drawn on the plane, and every number - the tick labels, the
    month labels and the name at each line's end - stands at its projected anchor and is drawn UPRIGHT (E28).

    WHAT THE FRAMES SHOW. `@proof-build` (6.0) is the same instant the FLAT page's golden is judged at, so the two
    frames are read side by side. The base frame (9.0) is the HOLD, all four lines in and named at their ends.
    `@proof-leave` (28.5) is the retract - a formed page leaves the way every page leaves."""
    import build_scene_timeline_f as BST
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    page["form"] = BST.page_form_spec("tilted_line", page["builder"], "golden")
    uris = _base_uris()
    # P61 T4b / E99 s35: this page SPEAKS ACROSS the flat page of the same series (`ledger-page-mid-build`), so its
    # ground is the two-plate CROSS-FADE - continuity, the operator's own division of the two first-class fields.
    _two_plate_page(page, uris)
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: the tilted-plane line", scenes, {}, None), uris


def press_stack() -> tuple[dict, dict]:
    """P50 T3: THREE PRESS CARDS on a bare plate, stacking on three words (Bravos shots 5-10), the third carrying
    the underline on its quoted phrase (E56's one exception, the squiggle law §9.27).

    Each card is a dock of kind `press` with its source line and its phrase box as fractions of the card - exactly
    what the compiler writes from press_card.py's meta - and its place in the pile (`stack_index` / `stack_n`) in
    enter order. The player mounts each one outside the two dock slots and poses the whole pile from
    species/press.mjs. Judged after the third has settled and its underline has finished drawing (FRAME_T 11.4)."""
    evidence, uris, docks = {}, _base_uris(), []
    for i, (aid, enter, src, _phrase, bars, words) in enumerate(PRESS_CARDS):
        evidence[aid] = {"title": f"Press card {i + 1}", "source": src, "species": "press",
                         "document": {"path": "golden", "sha256": "0" * 64}, "badges": []}
        uris[aid] = uri("image/png", png_bars(PRESS_CROP[0], PRESS_CROP[1], (250, 247, 240), bars))
        docks.append({"slide": aid, "slot": 0, "enter": enter, "exit": RUNTIME, "badge_at": [],
                      "kind": "press", "source": src, "phrase": PRESS_CARDS[i][3],
                      # R26-55: the phrase's words and the crop's own aspect, exactly as press_meta writes them
                      "phrase_text": words, "img": round(PRESS_CROP[1] / PRESS_CROP[0], 5),
                      "stack_index": i, "stack_n": len(PRESS_CARDS)})
    species = [{"kind": "callout", "form": "underline", "at": 10.6, "dur": 2.0,
                "target": {"kind": "phrase", "dock": PRESS_CARDS[-1][0]}}]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": species}]
    return _timeline("Golden: the press stack", scenes, evidence, None), uris


# ---- P50 T7: THE ART-EMBED SURFACES -------------------------------------------------------------------
# THE SCREEN's quad is the one MEASURED off the plate the operator approved (channel-assets/money-physics/
# plates/art-embed-study-tv-laptop.layers.json, written by measure_embed_quads.py off the 768 x 1376 still):
# the TV's bright face is one connected component, its four edges fit to sub-pixel residuals and its corners
# are those lines' intersections, as STAGE fractions in TL TR BR BL order. The plate itself stays QUARANTINED
# (the operator approves the frames); the golden paints its own wall with the same quad, so the geometry under
# test is the real one and nothing outside tests/golden is read at test time.
# It replaced the poster's quad here on the second watch (2026-09-12), because what the operator sent this
# slice back for is the SCREEN: "isn't the whole point of the TV to use it as the entire surface?" and "it
# should read as inside of the TV". A poster's geometry stays under test in test_art_embed.py, on the poster
# plate's own measured quad.
ART_TV = [[0.23287, 0.20871], [0.9683, 0.20913], [0.96744, 0.50337], [0.2329, 0.49721]]
# the second surface is SYNTHETIC and stated: the paper on the desk, seen from above - a strong keystone, the
# widest of the two, and the proof that a plate carries a NAMED SET of surfaces rather than one quad. It is a
# PAPER, so it takes none of the screen's treatment: no sheen, no inner falloff, the card's own shadow on it.
ART_PAPER = [[0.1800, 0.7200], [0.8600, 0.7400], [0.9400, 0.9300], [0.0600, 0.9100]]
ART_DARKEN = 7.0   # the second the room dims on (the manifest says the WORD; a golden has no take, so it says the second)
# the lamp's wedge on the glass, in the SCREEN's own unit square (TL TR BR BL): a blank screen is dark glass
# with the room's light falling across it, and that light is what the engine composites back OVER the card it
# displays (the sheen). Painted here so the golden's sheen has real plate pixels to carry, exactly as the
# approved TV plate does.
ART_GLARE = [[0.06, 0.0], [0.52, 0.0], [0.24, 1.0], [0.0, 1.0]]


def _inside(quad: list[list[float]], x: float, y: float) -> bool:
    """Is (x, y) inside the clockwise quad? Every turn the same way round - the compiler's own convexity law."""
    for i in range(4):
        ax, ay = quad[i]
        bx, by = quad[(i + 1) % 4]
        if (bx - ax) * (y - ay) - (by - ay) * (x - ax) < 0:
            return False
    return True


def _grown(quad: list[list[float]], k: float) -> list[list[float]]:
    cx = sum(p[0] for p in quad) / 4
    cy = sum(p[1] for p in quad) / 4
    return [[cx + (p[0] - cx) * k, cy + (p[1] - cy) * k] for p in quad]


COVER_OVERHANG = 0.05   # `.world` is inset -5%: the plate is painted over 110% of the stage


def _on_plate(quad: list[list[float]]) -> list[list[float]]:
    """A quad in STAGE fractions -> the same surface in the PLATE'S own fractions. The player paints the world
    plate on `.world`, which overhangs the stage by 5% on every side under `background-size: cover`, so a surface
    painted at its stage fraction would sit 5% off the place the card is projected onto (55 px at the TV's top
    edge). The three approved plates are measured against that painted placement already - this is the same
    arithmetic in reverse, and it lives here because only the synthetic wall has to paint itself. The golden's
    plate shares the stage's aspect, so `cover` is one scale and no crop enters."""
    k = 1 + 2 * COVER_OVERHANG
    return [[(x + COVER_OVERHANG) / k, (y + COVER_OVERHANG) / k] for x, y in quad]


def _bilinear(quad: list[list[float]], u: float, v: float) -> list[float]:
    """The quad's own (u, v) -> the plate's fractions: TL TR BR BL, u across the top edge, v down the sides."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = ((p[0], p[1]) for p in quad)
    tx, ty = (1 - u) * x0 + u * x1, (1 - u) * y0 + u * y1
    bx, by = (1 - u) * x3 + u * x2, (1 - u) * y3 + u * y2
    return [(1 - v) * tx + v * bx, (1 - v) * ty + v * by]


def png_surfaces(w: int, h: int, wall: tuple[int, int, int], border: tuple[int, int, int],
                 faces: list[tuple[list[list[float]], tuple[int, int, int], list[list[float]] | None]],
                 glare: tuple[int, int, int] = (168, 186, 208), grow: float = 1.05) -> bytes:
    """The synthetic STUDY: a dark wall carrying the declared surfaces, each blank in a thin dark frame - a
    PAPER as blank cream, a SCREEN as dark glass with the room's light falling across it. A shape, deliberately:
    what is under test is that a card lands ON the quad in perspective and is displayed BY it, not whether this
    particular wall is beautiful (the operator judges the plate itself, on the approved stills)."""
    rows = [[wall] * w for _ in range(h)]
    off = (1 / 6, 0.5, 5 / 6)   # 3 x 3 supersampling: a hard edge on a 432 x 768 plate is a staircase at stage size
    for q, face, wedge in faces:
        outer = _grown(q, grow)
        lamp = [_bilinear(q, u, v) for u, v in wedge] if wedge else None
        x0 = max(0, int(min(p[0] for p in outer) * w) - 1); x1 = min(w, int(max(p[0] for p in outer) * w) + 2)
        y0 = max(0, int(min(p[1] for p in outer) * h) - 1); y1 = min(h, int(max(p[1] for p in outer) * h) + 2)
        for y in range(y0, y1):
            row = rows[y]
            for x in range(x0, x1):
                hit = [0, 0, 0, 0]   # face, border, wall, and of the face hits, how many the lamp lights
                for dy in off:
                    fy = (y + dy) / h
                    for dx in off:
                        fx = (x + dx) / w
                        if _inside(q, fx, fy):
                            hit[0] += 1
                            if lamp and _inside(lamp, fx, fy):
                                hit[3] += 1
                        elif _inside(outer, fx, fy):
                            hit[1] += 1
                        else:
                            hit[2] += 1
                if hit[2] == 9:
                    continue
                base = row[x]
                row[x] = tuple(round((face[c] * (hit[0] - hit[3]) + glare[c] * hit[3]
                                      + border[c] * hit[1] + base[c] * hit[2]) / 9) for c in range(3))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + b"".join(bytes(c) for c in row) for row in rows)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def art_embed() -> tuple[dict, dict]:
    """P50 T7 - A CARD IS DISPLAYED BY A PAINTED SURFACE. The plate declares two surfaces by name (`tv` on the
    wall, `paper` on the desk); a PRESS card lands on the TV and a STILL card with its badge rail lies on the
    paper. Both are projected by the planar homography from the surface's four corners - so the masthead, the
    headline, the by-line, the badges and E56's one underline all live in the projected space - and the room
    DARKENS outside the TV on its word, so the surface lights (E33: the painting carries no facts; the
    information layer is composited here).

    THE SECOND WATCH (the operator, 2026-09-12: "isn't the whole point of the TV to use it as the entire
    surface?" / "and yes, it should read as inside of the TV"): each card FILLS its surface corner to corner and
    REFLOWS into it (the masthead at the top, the pulled phrase at the box's full width and its own aspect, the
    by-line at the foot), and the SCREEN displays its card - the plate's own lamp composited back over the card
    as light, the bezel's inner falloff around it, the paper lifted toward that light. The desk paper takes none
    of it: a paper is a paper, and the card lies on it with its own shadow.
    The dock entries are the COMPILER's own (`dock_entry` with `embed=embed_entry(...)`), so the golden proves
    the grammar, the projection and the two treatments together. Judged with everything landed and still
    (FRAME_T 9.0)."""
    import build_scene_timeline_f as BST
    quote, still = "ev-embed-quote", "ev-embed-record"
    source = "THE HERALD, 4 MAR 2026"
    phrase = {"x0": 0.08, "y0": 0.17, "x1": 0.62, "y1": 0.46}
    # R26-55: the card carries the phrase's WORDS too, so the surface's card sets them as live type re-lined to the
    # screen's own shape and keeps the crop beneath as the provenance strip (the limit E66 recorded, closed)
    press = BST.press_meta({"source": source, "phrase": phrase, "phrase_text": PRESS_CARDS[0][5],
                            "card": list(PRESS_CROP)})
    # the picture's own aspect, as the compiler writes it off the file (image_aspect): the press card's
    # headline crop is 528 x 160, the record on the desk 640 x 400
    evidence = {
        quote: {"title": "The claim on the screen", "source": source, "species": "press",
                "document": {"path": "golden", "sha256": "0" * 64}, "badges": []},
        still: {"title": "The record on the desk", "source": "P50 T7", "species": "deck",
                "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:2]},
    }
    # E95: each surface's `fit` is the COMPILER's own `embed_fit` - the press card reflows (E66) and the record on the
    # desk carries two badges, so it stays the card: a card is not a picture (neither entry carries `fit`)
    tv = BST.embed_entry("tv", {"quad": ART_TV, "darken": ART_DARKEN}, card_aspect=160 / 528,
                         fit=BST.embed_fit({"embed": "tv", "press": press}, None, evidence[quote]))
    paper = BST.embed_entry("paper", {"quad": ART_PAPER}, card_aspect=400 / 640,
                            fit=BST.embed_fit({"embed": "paper"}, None, evidence[still]))
    docks = [
        BST.dock_entry(quote, 0, 5.0, RUNTIME, 0, BST.DOCK_KIND_IMAGE, None, "throw", "paper", False,
                       press=press, embed=tv),
        BST.dock_entry(still, 0, 5.6, RUNTIME, 2, BST.DOCK_KIND_IMAGE, None, None, None, False, embed=paper),
    ]
    species = [
        {"kind": "callout", "form": "underline", "at": 8.0, "dur": 2.0, "target": {"kind": "phrase", "dock": quote}},
        # E59 reason 4: the eye may punch into a declared SURFACE by name. After the judged instant on purpose -
        # what this proves in the golden is that the compiler resolved the plate's quad onto the target.
        {"kind": "punch", "at": 12.0, "dur": 1.6, "target": {"kind": "embed", "name": "tv"}},
    ]
    BST.resolve_embed_targets(species, {"tv": {"quad": ART_TV}, "paper": {"quad": ART_PAPER}}, "golden art-embed")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-study", "sha256": "0" * 64,
                                            "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": species}]
    uris = _base_uris()
    uris["plate-study"] = uri("image/png", png_surfaces(432, 768, (31, 38, 48), (22, 26, 32),
                                                        [(_on_plate(ART_TV), (24, 29, 36), ART_GLARE),
                                                         (_on_plate(ART_PAPER), (222, 214, 198), None)]))
    uris[quote] = uri("image/png", png_bars(PRESS_CROP[0], PRESS_CROP[1], (250, 247, 240), PRESS_CARDS[0][4]))
    uris[still] = uri("image/png", png_solid(640, 400, (23, 105, 194)))
    return _timeline("Golden: a card displayed by a painted surface", scenes, evidence, "9:16"), uris

def _chart_evidence() -> dict:
    chart = json.loads(SERIES.read_text(encoding="utf-8"))
    return {"ev-golden-chart": {"title": "Golden chart", "source": "golden series sidecar", "species": "chart",
                                "document": {"path": "golden", "sha256": "0" * 64},
                                "badges": _badges(), "chart": chart}}


def chart_callout() -> tuple[dict, dict]:
    ev = _chart_evidence()
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0.0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME],
               "docks": [_dock("ev-golden-chart", 0, 2.0, RUNTIME, 4)],
               # P72 T48 / R26-367 ("why is the ring completely missing the line?"): the ring names the datum it means - the
               # semiconductor line's (series 1) datum 152, its April '26 climb - on the DOCKED chart, never a hand-typed
               # stage point (0.72, 0.42 sat 40 px above the line)
               "species": [{"kind": "callout", "at": 10.0, "dur": 6.0, "target": {"kind": "datum", "dock": 0, "series": 1, "index": 152}}]}]
    uris = _base_uris(); uris["ev-golden-chart"] = uri("image/png", png_solid(64, 36, (22, 24, 28)))
    return _timeline("Golden: chart with a callout", scenes, ev, None), uris


def _dock_pair(aspect: str | None) -> tuple[dict, dict]:
    ev = {
        "ev-golden-card-a": {"title": "Golden card A", "source": "golden", "species": "deck",
                             "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:2]},
        "ev-golden-card-b": {"title": "Golden card B", "source": "golden", "species": "deck",
                             "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[2:]},
    }
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0.05, "x": 10, "y": -6}},
               "exit": "cut", "span": [0.0, RUNTIME],
               "docks": [_dock("ev-golden-card-a", 0, 2.0, RUNTIME, 2), _dock("ev-golden-card-b", 1, 5.0, RUNTIME, 2)],
               "species": []}]
    uris = _base_uris()
    uris["ev-golden-card-a"] = uri("image/png", png_solid(640, 360, (23, 105, 194)))
    uris["ev-golden-card-b"] = uri("image/png", png_solid(640, 360, (23, 140, 131)))
    return _timeline(f"Golden: dock pair {aspect or '16:9'}", scenes, ev, aspect), uris


def melt_page(ending: str = "throw", weight: bool = False, body: str = "chart", offscreen: bool = False) -> tuple[dict, dict]:
    """P52 T9 / R26-15, reworked to E88 / R26-76 - THE MELT TAKES THE CHART, NOT THE BOARD.

    Scene 1 is the line page every other golden is built from, given the whole 15 s to draw itself, so what melts is a
    chart that has been read. Scene 2's `exit` is the melt - `exit` names the transition INTO the scene it sits on (E47),
    so the melt takes scene 1's CHART INK as scene 2 begins, while scene 1's board (the cream ground, the deckle, the
    charcoal) stays exactly where it is. The three authored endings are three surfaces:
      throw         (`melt-page`)   scene 2 is a bars page of where the lines end, on its axes (the stamp a chart-to-chart
                                    boundary gets): the ink balls up and is thrown off; the bars then draw on the board.
      splash:chart  (`melt-splash`) the same bars page, arriving BUILT (the stamp a chart splash gets): the ball splatters
                                    onto the board and the bars show through the stains.
      splash:plate  (`melt-plate`)  scene 2 is a narrative plate stand-in (a warm ground with dark forms - a synthetic
                                    PNG, a committed input like every other): the splatter paints it up over the board.

    Each is pinned at an instant with no fractional blur band where one exists (the throw's ball at rest, the splash's
    burst), because a golden is a byte-exact pin - the Chromium filter-raster flake measured 2026-09-12. The plate's
    paint cannot be pinned without its stains' gooey edge; it takes the instant the plate is mostly painted.

    R26-118 / E88 s6-s7 adds a fourth surface off the same two pages: `melt-ball-roll`, the throw with `weight` on
    (`melt:weight`, metal by default). Between the ball and the throw the ball LANDS on the board (the receiver's dip,
    the contact shadow tightening, the board's three-frame answer), ROLLS a no-slip 150 px with its own ink mark
    turning, is NUDGED once and SETTLES - and its surface is the living drop (Rayleigh modes, never still). The exit
    declares no length, so it runs MELT_S + MELT_W_S = 2.75 s from the cut."""
    import json
    assert ending in ("throw", "splash:chart", "splash:plate"), ending
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    page["exit"] = "cut"   # LEDGER_EXITS / E40 #5, R26-60: NO RETRACT - the melt is how this chart leaves
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, MELT_CUT], "docks": [], "species": []}]
    uris = _base_uris()
    if ending == "splash:plate":
        # the narrative plate stand-in: a dusk landscape (sky, sun, two hill lines), so the paint reads as a PICTURE arriving
        uris["plate-melt"] = uri("image/png", png_scene(320, 180))
        world2 = {"asset_id": "plate-melt", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    else:
        raw = json.loads(SERIES.read_text(encoding="utf-8"))
        bars = {"title": "Where the four lines end", "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
                "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                         for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
        page2 = LPG.build_spec(bars, "bars", None, "right")
        page2["field"] = "scribble"   # the same board as scene 1's: the board is shared
        page2["enter"] = "axes" if ending == "throw" else "built"   # what stamp_transition_pages writes on this boundary
        world2 = {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    exit_id = "melt" if ending == "throw" else "melt:" + ending
    if weight:
        exit_id += ":weight"   # R26-118: metal, the default - the ball lands, rolls, is nudged and settles first
    if body != "chart":
        # P61 T5b / E99 s42: the two body colours the operator asked to SEE - the ball melting to the board's slate
        # grey and to the blueprint's near-black metal. `chart` writes no token at all, so the default surface's exit
        # string is character for character the one it had and its goldens cannot move.
        import build_scene_timeline_f as BST
        assert body in BST.MELT_BODIES, body
        exit_id += ":body=" + body
    if offscreen:
        # P72 T23 / R26-157 / E99 s56: the splash's pitch picked OFF the frame - a splash's alone (the compiler refuses
        # it anywhere else, by name), so the token is written only when asked and every other surface's string stands.
        import build_scene_timeline_f as BST
        exit_id += ":offscreen"
        assert BST.melt_offscreen(exit_id), exit_id   # the COMPILER's own grammar, not a hand-written string
    scenes.append({"scene_id": "s02", "world": world2, "exit": exit_id,
                   "span": [MELT_CUT, RUNTIME], "docks": [], "species": []})
    return _timeline("Golden: the chart melts off its board and is " + ("rolled in its own weight and " if weight else "")
                     + {"throw": "thrown", "splash:chart": "splashed into the next chart",
                        "splash:plate": "splashed into a plate"}[ending], scenes, {}, None), uris


# ---- P52 T6: THE NEWSREEL BAND, AND THE SURFACE ABOVE IT ---------------------------------------
# The three headlines are the FIRST CUSTOMER's own sourced titles, read off
#   content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/assets/evidence_clips/candidates.json
# (Bloomberg Television x2, Fox Business Clips x1 - E68: a clip's on-screen headline IS its label, and a headline is
# never invented). That file is an episode asset and is not committed, so the strings are LITERALS here - and
# checked against the file whenever a checkout happens to have it (below). The surface above the band is the
# APPROVED Bessent head (E68) docked as a CUTOUT (P53 T7, the operator 2026-09-12: "replace the head"): a trimmed,
# 480 px, 256-colour copy committed at tests/golden/inputs/head_bessent_cutout.png, because a golden's inputs are
# committed inputs and the episode's own 1024 px cutout is untracked.
NEWSREEL_HEADLINES = ["Treasury Secretary Bessent Boosts Buybacks of Long-Dated Debt",
                      "US Treasury to Buy Up to $6 Billion in Long-Dated Debt",
                      "Kevin Warsh: A new regime is needed at the Fed"]
NEWSREEL_SOURCE = ("content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/"
                   "assets/evidence_clips/candidates.json")
NEWSREEL_STRIP_H = 143   # [DERIVED: build_scene_timeline_f.caption_strip_h - two lines at 64 px / 1.12]
NEWSREEL_HEAD = Path(__file__).resolve().parent / "inputs" / "head_bessent_cutout.png"   # P53 T7: the approved cutout, trimmed to its alpha box (source head_bessent.png sha e454a6d92ad84622)
NEWSREEL_HEAD_ASPECT = 637 / 480   # the committed copy's own h / w


def _newsreel_headlines() -> list[str]:
    """The three sourced titles, verified against the episode's `candidates.json` when this checkout has it."""
    f = REPO / NEWSREEL_SOURCE
    if f.exists():
        titles = {c["title"] for cands in json.loads(f.read_text(encoding="utf-8")).values() for c in cands}
        missing = [h for h in NEWSREEL_HEADLINES if h not in titles]
        if missing:
            raise SystemExit(f"newsreel golden: {missing} are not titles in {NEWSREEL_SOURCE} - a headline is never invented")
    return list(NEWSREEL_HEADLINES)


def png_head_standin(w: int, h: int) -> bytes:
    """A synthetic HEAD: a charcoal head-and-shoulders silhouette on cream, drawn as horizontal boxes by the same
    stdlib PNG writer every other golden input uses. A shape, deliberately - the operator judges the real cutouts
    on the episode's own frames; this proves the band runs UNDER a docked surface."""
    rows = []
    for i in range(11):                                   # the head: an ellipse cut into eleven boxes
        v = (i + 0.5) / 11
        r = (1 - (2 * v - 1) ** 2) ** 0.5 * 0.19
        rows.append((0.5 - r, 0.08 + v * 0.44, 0.5 + r, 0.08 + (v + 1 / 11) * 0.44))
    for i in range(6):                                    # ... and the shoulders, widening to the card's edge
        v = i / 6
        r = 0.21 + v * 0.24
        rows.append((0.5 - r, 0.56 + v * 0.44, 0.5 + r, 0.56 + (v + 1 / 6) * 0.44))
    return png_bars(w, h, (244, 230, 199), rows, ink=(37, 49, 60))


def _newsreel_surface(aspect: str | None, band: tuple[float, float], cap_band: dict, above: bool) -> tuple[dict, dict]:
    """One newsreel surface: a plate world, a card docked above, and the band crawling in its declared strip.

    `band` is the region's (y0, y1) in stage fractions; `cap_band` is exactly what the compiler's
    `newsreel_caption_band` stamps on the dock entry for this composition (the player reads the caption's strip
    off the dock, E62) - so the frame shows the strip law as the compiler decides it, not as the golden wishes."""
    head = "ev-newsreel-head"
    reel = {"kind": "newsreel", "at": 5.0, "dur": 20.0, "headlines": _newsreel_headlines(),
            "strap": "the wire, under the surface", "dateline": "SEPT 2026",
            "target": {"kind": "region", "x0": 0.0, "y0": band[0], "x1": 1.0, "y1": band[1]}}
    if above:
        reel["cap_band"] = "above"
    ev = {head: {"title": "Scott Bessent (cutout)", "source": "golden", "species": "deck", "kind": "cutout",
                 "document": {"path": "tests/golden/inputs/head_bessent_cutout.png", "sha256": "0" * 64}, "badges": []}}
    # the card is PLACED above the band, on the left third - the composition the operator described ("a
    # talking news head ... above it"). The placer reserves the band's strip (`newsreel_boxes` -> `free_bands`)
    # on a ledger page; on a plain plate like this one the row places its own card, and the proof is the frame.
    # the box is the HEAD's own aspect now (a cutout has no card to letterbox into)
    place = ({"x": 70, "y": 300, "w": 520, "h": round(520 * NEWSREEL_HEAD_ASPECT)} if aspect == "9:16"
             # 16:9: the bust SITS ON the band (its foot at the band's top edge, 0.78 of 1080 = 842) - a cutout that ends
             # in a hard chest line floating over empty world reads as a sticker; seated, the band crops it like a desk
             else {"x": 150, "y": 842 - round(380 * NEWSREEL_HEAD_ASPECT), "w": 380, "h": round(380 * NEWSREEL_HEAD_ASPECT)})
    dock = dict(_dock(head, 0, 2.0, RUNTIME, 0), place=place, caption_band=dict(cap_band), kind="cutout")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [dock], "species": [reel]}]
    uris = _base_uris()
    uris[head] = uri("image/png", NEWSREEL_HEAD.read_bytes())   # P53 T7: the approved cutout, committed
    tl = _timeline(f"Golden: the newsreel band {aspect or '16:9'}" + (" (caption above the crawl)" if above else ""),
                   scenes, ev, aspect)
    tl["note"] = (f"P52 T6. The headlines are sourced titles read off {NEWSREEL_SOURCE} (Bloomberg Television, "
                  "Fox Business Clips - E68: a clip's on-screen headline is its label). The head is the approved "
                  "Bessent cutout docked as a CUTOUT - no card, no paper (P53 T7). Judge: the band is a STRIP "
                  "under the surface, the crawl has no seam, and the caption and the crawl never share a strip.")
    return tl, uris


def newsreel_band() -> tuple[dict, dict]:
    """P52 T6, 16:9: the band in the lower 40 %, a card docked above it, the caption at its own 40 % home.
    Gate 1's first frame - the composition the operator described: a surface above, the wire below."""
    return _newsreel_surface(None, (0.78, 0.92), {"y": 432, "h": NEWSREEL_STRIP_H, "band": "quiet"}, False)


def newsreel_strip_9x16() -> tuple[dict, dict]:
    """P52 T6, 9:16 - THE DEFAULT this slice ships: the caption keeps its E62 band (its home, 1297-1440) and the
    band goes BELOW it (1498-1767). Gate 1's second frame."""
    return _newsreel_surface("9:16", (0.78, 0.92), {"y": 1297, "h": NEWSREEL_STRIP_H, "band": "quiet"}, False)


def newsreel_strip_above() -> tuple[dict, dict]:
    """P52 T6, 9:16 - THE ALTERNATIVE: `cap_band: "above"`. The crawl takes the caption's own strip (1296-1565)
    and the caption is stamped one strip higher, above it (1145-1288). Gate 1's third frame: the operator rules
    the strip law by eye, on this frame against the one above."""
    return _newsreel_surface("9:16", (0.675, 0.815), {"y": 1145, "h": NEWSREEL_STRIP_H, "band": "newsreel-above"}, True)


# P52 T7: THE ISOMETRIC COUNT ARRAY. Six identical SOURCED icons on a 2:1 rhombus lattice, arriving in reading
# order one per word, the count written under them as the claim.
COUNT_FIELD = {"kind": "count_array", "at": 5.0, "dur": 14.0, "count": 6, "icon": "factory", "idle": "breath",
               "claim": "SIX PLANTS", "target": {"kind": "region", "x0": 0.08, "y0": 0.47, "x1": 0.92, "y1": 0.97}}   # clear of the stage caption band (chip-board's own rule: the board is read, not stepped on)
# P52 T8: THE NUMBERED AGENDA. Tokyo 36.1's own sentence ("Two numbers show where the money went: a Treasury page,
# and your phone"), as one declaration instead of two figures and a note.
AGENDA_BLOCK = {"kind": "agenda", "at": 5.0, "dur": 14.0, "idle": "breath",
                "rows": [{"text": "A Treasury page", "sub": "the sellers"},
                         {"text": "Your phone", "at": 6.2, "sub": "the bill"}],
                "target": {"kind": "region", "x0": 0.30, "y0": 0.50, "x1": 0.95, "y1": 0.95}}   # ... and so is the agenda's block
# P52 T8: THE RING'S DASHED FORM on a datum of a ledger line page, with its flag chip beside it. E56's use, not a
# new one: the target is a DATUM (a point on a chart) and the label is the figure it circles.
RING_DASHED = {"kind": "ring", "at": 9.0, "dur": 9.0, "form": "dashed", "idle": "breath",
               "label": "1,074", "flag": "THE PEAK", "flag_icon": "landmark", "flag_side": "left",   # the room is on the LEFT here: the series' own terminal tag stands to the right of its peak, and a flag over a tag is two labels in one place
               "target": {"kind": "datum", "index": 191}}   # the memory-makers series' OWN peak: pts[191] = 1074.29 (index, 100 = Aug 2025). The label is the value, never a number we made up (E53)


def _line_page():
    """The ledger LINE page `ring-dashed-chip` and the proof page ring a datum on - built exactly as
    `span-decade` builds its own, with no emphasis so every series is drawn."""
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    return page


def count_array() -> tuple[dict, dict]:
    """P52 T7 (EXPLORATION-REVIEW-2026-09-10.md:59, the reference at 7:43 - "the silos"): N identical icons on an
    ISOMETRIC field over a bare plate. The lattice is a 2:1 rhombus and nothing else - no vanishing point, no
    per-row scale, nothing rotated at any t - the icons arrive in reading order one per word on the CHIP's own
    two-spring landing, and the COUNT is written under the field as the claim (the compiler refuses a claim that
    does not say the number). The glyph is the SOURCED icon under content/video_engine/assets/icons (Lucide
    1.45.0, ISC - assets/icons/SOURCES.md + LICENSE.lucide.txt), embedded by the compiler's OWN icon_geometry, so
    this golden proves the asset route and the painter module together. Every cell carries the breath idle (E49),
    each at its own phase: the field holds, it never goes still. Judged once the claim is written (FRAME_T 8.0)."""
    import build_scene_timeline_f as BST
    species = [dict(COUNT_FIELD)]
    assert not BST.validate_species(species, (0, 0, 0), "plate-plain"), BST.validate_species(species, (0, 0, 0), "plate-plain")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    uris[BST.ICON_PREFIX + COUNT_FIELD["icon"]] = BST.icon_geometry(COUNT_FIELD["icon"])
    return _timeline("Golden: the isometric count array", scenes, {}, None), uris


def agenda_two() -> tuple[dict, dict]:
    """P52 T8 (EXPLORATION-REVIEW-2026-09-10.md:58, Bravos's "China's Gameplan 1 | 2"): a numbered agenda of two
    rows, each revealed on its OWN word - the number written, the hairline drawn under the row by the nib, the
    text rising into place - and the block laid out for the full list from the first frame, so the second row
    never pushes the first. Both rows hold at the breath idle (E49), each at its own phase. Judged once both are
    in (FRAME_T 7.2)."""
    import build_scene_timeline_f as BST
    species = [dict(AGENDA_BLOCK)]
    assert not BST.validate_species(species, (0, 0, 0), "plate-plain"), BST.validate_species(species, (0, 0, 0), "plate-plain")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the numbered agenda", scenes, {}, None), _base_uris()


# P61 T8 - THE AGENDA PAGE (E99 s16: *"still need the beautified agenda page, which i think we discussed as
# basically just being the plate version of our list effect."*). The same species, its PAGE form: the block takes
# the whole plate, a title says what the list is, and each row carries one of the OPERATOR'S OWN catalogued
# cutouts (E93 / E94, `finance_icons_catalog.v1.json`, `render_eligible`), stamped on after that row's sentence
# has been read. The icons are chosen by the catalogue's `semantic_tags` against the row's own words:
#   us-treasuries -> prop-icon-us-sovereign-markets-v1, federal-funds-rate -> prop-icon-interest-rates-monetary-policy-v2,
#   cost-of-living -> prop-icon-cpi-inflation-basket-v1.
AGENDA_PAGE_ROWS = [{"text": "A Treasury page", "icon": "prop-icon-us-sovereign-markets-v1"},
                    {"text": "The rate they pay", "at": 6.6, "icon": "prop-icon-interest-rates-monetary-policy-v2"},
                    {"text": "Your bill", "at": 8.2, "sub": "$4,500", "icon": "prop-icon-cpi-inflation-basket-v1"}]
AGENDA_PAGE = {"kind": "agenda", "form": "page", "at": 5.0, "dur": 9.0, "idle": "breath",
               "title": "WHAT THE BILL IS MADE OF", "rows": AGENDA_PAGE_ROWS,
               "target": {"kind": "region", "x0": 0.05, "y0": 0.08, "x1": 0.95, "y1": 0.94}}   # the BOARD: the page's own quiet zone


def agenda_page() -> tuple[dict, dict]:
    """P61 T8 (E99 s16, E93, R26-80): THE AGENDA PAGE - the plate version of the list effect.

    The dock form (`agenda-two`, `species-proof@proof-agenda`) parks its rows in the box it was given and leaves
    the upper two thirds of the plate empty. This is the same declaration with `form: "page"`: the rows divide
    the whole board between them, each on its own mount with its numeral in a medallion, and each row's
    CATALOGUED icon is stamped on PAGE_STAMP_LAG after that row's sentence has been read (E93) - never before.
    No captions: the page form fills the frame, so what the golden reads is the page and not a caption over it
    (the same reason the race arms clear theirs)."""
    import build_scene_timeline_f as BST
    block = dict(AGENDA_PAGE)
    errs = BST.validate_species([block], (0, 0, 0), "plate-plain")
    assert not errs, errs
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": [block]}]
    tl = _timeline("Golden: the agenda PAGE - the plate version of the list", scenes, {}, None)
    tl["captions"], tl["caption_pages"] = [], []
    uris = _base_uris()
    for name in [r["icon"] for r in AGENDA_PAGE_ROWS]:
        # `prop:<asset_id>`: a DOWNSCALED PROXY of the operator's cutout (E99 s31 - an approved cutout does not
        # enter git at full resolution). `catalogue_icon` is what resolves it: the id, the kind, the operator's
        # approval, `render_eligible`, and the sha256 of the file on disk, all checked before a byte is read.
        uris[BST.PROP_PREFIX + name] = uri("image/png", png_proxy(BST.catalogue_icon(name)["file"]))
    return tl, uris


def ring_dashed_chip() -> tuple[dict, dict]:
    """P52 T8 (EXPLORATION-REVIEW-2026-09-10.md:57 #5): the ring's DASHED-ELLIPSE form round a datum of a ledger
    line page, with a flag chip beside it. The form widens, the USE does not - E56 still holds, and this row is
    exactly what it allows: a datum target (a point on a chart) with the figure as its label. The ellipse is cut
    into dashes BY LENGTH and drawn dash by dash by the same hand the callout's circle uses, at the callout's own
    pads, so the two forms ring the same place; the flag is a CHIP (the chip module's card, its sourced glyph and
    its two-spring landing) placed on the side with the room. Judged once the flag has settled (FRAME_T 10.6)."""
    import build_scene_timeline_f as BST
    species = [dict(RING_DASHED)]
    plate = "ledger:golden-line:line"
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": _line_page(), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    uris[BST.ICON_PREFIX + RING_DASHED["flag_icon"]] = BST.icon_geometry(RING_DASHED["flag_icon"])
    return _timeline("Golden: the ring's dashed form and its flag chip", scenes, {}, None), uris


# P69 T47 / E99 s109 (3): RINGS IN TURN ON EVERY VERTEX, AND THE VALLEY LIT - when the sentence is ABOUT the vertices.
# No new grammar: three `ring` species on three datums, each on its own word and held to the row's word, then T36's
# `lit_stretch` from the first peak through the trough to the second, and the trough's `figure`. The page is the REAL
# 20-year Treasury yield (FRED DGS20, american-debt-trap's committed object, status REAL): it topped out near five
# percent three times in 2025 - pts[8] 5.06 (Jan 14), pts[96] 5.08 (May 21), pts[132] 5.02 (Jul 15) - and between the
# first two it fell to pts[64] 4.44 (Apr 4). Every label is the datum's own value (E53). The words: "It hit five percent
# in January [5.8], again in May [7.1], and again in July [8.4] ... in between, it fell [10.2] to four forty-four
# [11.5]" - the ring beat is recipe:trace-callout-ladder's 1.26 s, rounded to 1.3.
# THE WINDOW. On the object's whole run (428 days, Jan 2025 - Sep 2026) May and July stand 36 data = 80 px apart on the
# plot, and two rings (RING.MIN_RX 54: an ellipse at least 108 px wide) overlap and their labels collide - read off this
# golden's first render. So the page shows the object's own first 187 observations (Jan 2 - Sep 30, 2025) and SAYS so:
# the sub names the window, the ticks fall inside it, the LATEST badge (Sep 17, 2026) is outside it and is not drawn.
# No value is changed, added or moved; the indices are the object's own (the window starts at its first datum).
VERTEX_PROJECT = REPO / "content/video_engine/projects/systems-and-blowups/american-debt-trap"
VERTEX_SERIES = VERTEX_PROJECT / "evidence/objects/treasury-20y-yield.series.json"
VERTEX_PLATE = "ledger:treasury-20y-yield:line:427:right"   # the plate the validation reads (a ledger page)
VERTEX_WINDOW = 187        # pts[:187] = 2025-01-02 .. 2025-09-30
VERTEX_HOLD_UNTIL = 16.0   # the row's word: the three rings leave together here; the lit valley and its figure stay


def _vertex_ring(at: float, index: int, label: str) -> dict:
    return {"kind": "ring", "at": at, "dur": round(VERTEX_HOLD_UNTIL - at, 2), "form": "dashed", "label": label,
            "target": {"kind": "datum", "index": index, "series": 0}}


VERTEX_SPECIES = [
    _vertex_ring(5.8, 8, "5.06%"),     # "in January"
    _vertex_ring(7.1, 96, "5.08%"),    # "again in May"
    _vertex_ring(8.4, 132, "5.02%"),   # "and again in July"
    {"kind": "lit_stretch", "at": 10.2, "dur": 1.6, "from": 8, "to": 96, "series": 0},   # "in between, it fell": the valley lit
    {"kind": "figure", "at": 11.5, "dur": 1.4, "target": {"kind": "datum", "index": 64, "series": 0},
     "text": "4.44%", "color": "neg", "dy": 0.9},                                          # "to four forty-four": the trough named
]


def _vertex_page() -> dict:
    """The treasury object's page over its 2025 window (see VERTEX_WINDOW): the object's own values, its title, source
    and axes; the sub, the ticks and the badges say what the window shows."""
    obj = LPG.load_series(VERTEX_SERIES)
    ser = dict(obj["series"][0], pts=obj["series"][0]["pts"][:VERTEX_WINDOW])
    last_x = ser["pts"][-1][0]
    windowed = dict(obj, series=[ser], badges=[],
                    sub="20-year U.S. Treasury constant-maturity yield · Jan 2 → Sep 30, 2025 · daily · percent per annum",
                    xticks=[obj["xticks"][0], ["2025.2465753425", "Apr 2025"], obj["xticks"][1], [last_x, "Sep 30, 2025"]])
    return LPG.build_spec(windowed, "line", None, "right")


def rings_on_vertices() -> tuple[dict, dict]:
    """P69 T47: three near-equal peaks ringed in turn, the valley between the first two lit. Judged at 13.2 s - the
    three rings standing, the light landed on the second peak, the trough's figure written - with no captions, so the
    frame reads the page (the rings' own words are the labels)."""
    import build_scene_timeline_f as BST
    species = [dict(e) for e in VERTEX_SPECIES]
    errs = BST.validate_species(species, (0, 0, 0), VERTEX_PLATE)
    assert not errs, errs
    world = {"kind": "ledger", "page": _vertex_page()}
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    BST.check_target_series(world, species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: rings in turn on the vertices, the valley lit", scenes, {}, "16:9")
    tl["captions"], tl["caption_pages"] = [], []
    return tl, _base_uris()


# P69 T48 / E99 s109 (4) + its amendment: THE PIE AND THE DONUT, FLAT OR 3D EXPLODED, AND THE PUSH ONTO THE LARGEST
# SLICE. The page is the registered DRAM market-share slide (silicon-silent-triopoly s08, `registration.silicon-silent-
# triopoly.json`): Samsung 39 %, SK hynix 26 %, Micron 25 %, CXMT 7 % - 97 of the whole 100. The share check refuses
# that page and NAMES the 3 % it owes; the fifth slice is exactly that remainder, "Other", never a figure invented. The
# same page is drawn three ways: a flat donut, the tilted/extruded pie with Samsung EXPLODED on its word ("Samsung
# alone makes..."), and the push - a camera key on the largest slice while the others recede.
PIE_REGISTRATION = REPO / "content/video_engine/projects/systems-and-blowups/registration/registration.silicon-silent-triopoly.json"
PIE_SLIDE = "silicon-silent-triopoly-s08"
PIE_MAKERS = ("Samsung", "SK hynix", "Micron", "CXMT")
PIE_PLATE = "ledger:golden-dram:share"
PIE_HOLE = 0.55            # the flat donut's hole, a share of the radius
PIE_EXPLODE_AT, PIE_EXPLODE_S = 9.0, 0.8     # "Samsung alone" - the slice leaves the whole on its word
PIE_PUSH_T0, PIE_PUSH_T1, PIE_PUSH_ZOOM = 11.0, 12.4, 1.6   # the push onto the largest slice, then held


def pie_series() -> dict:
    """The slide's four makers, read off the registration (never re-typed), and the remainder the check names."""
    reg = json.loads(PIE_REGISTRATION.read_text(encoding="utf-8"))
    figs = {f["label"]: f["value"] for f in next(s for s in reg["slides"] if s["slide_id"] == PIE_SLIDE)["figures"]}
    vals = [int(figs[f"{n} DRAM market share"].rstrip("%")) for n in PIE_MAKERS]
    shares = [{"label": n, "value": v, "value_string": f"{v}%"} for n, v in zip(PIE_MAKERS, vals)]
    rest = 100 - sum(vals)
    shares.append({"label": "Other", "value": rest, "value_string": f"{rest}%"})
    return {"title": "Who makes the world's DRAM", "sub": "DRAM market share by maker, percent of the whole",
            "src": "silicon-silent-triopoly deck, slide 8 (registered figures); Other = the remainder to 100",
            "unit": "%", "total": 100, "emphasize": 0, "shares": shares,
            "extrude": {"hatch": True}, "explode": {"index": 0}}


def pie_push_camera() -> dict:
    """The push as a row authors it: the look is the largest slice (a `datum` on a share page is a slice), the chrome
    rides the screen so the title and the source stay whole while the plot is pushed (T26f)."""
    look = {"kind": "datum", "index": 0}
    return {"keys": [{"t": PIE_PUSH_T0, "zoom": 1.0, "look": look, "ease": "inout"},
                     {"t": PIE_PUSH_T1, "zoom": PIE_PUSH_ZOOM, "look": look, "ease": "inout"}],
            "attention": "locked", "chrome": "screen"}


def _pie_timeline(title: str, series: dict, species: list, camera: dict | None) -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    errs = BST.validate_species(species, (0, 0, 0), PIE_PLATE)
    assert not errs, errs
    assert LPG.validate(series, "share") == [], LPG.validate(series, "share")
    page = LPG.build_spec(series, "share")
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scene = {"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}
    if camera is not None:
        assert BST.validate_camera(camera, PIE_PLATE, "16:9") == []
        assert BST.share_slice_errors(world, camera, PIE_PLATE) == []
        scene["camera"], _notes = BST.compile_chrome(camera, None, (0.0, RUNTIME), PIE_PLATE, world, "16:9")
    tl = _timeline(title, [scene], {}, "16:9")
    tl["captions"], tl["caption_pages"] = [], []
    if camera is not None:
        tl["kinetics"] = {"camera": True}   # E59's own module drives the keys (camNow), as on camera-layers
    return tl, _base_uris()


def share_donut_flat() -> tuple[dict, dict]:
    """P69 T48: the flat donut - the same five slices at their true angles, every figure written on its slice."""
    s = pie_series()
    for k in ("extrude", "explode"):
        s.pop(k)
    s["hole"] = PIE_HOLE
    return _pie_timeline("Golden: the flat donut", s, [], None)


def share_pie_3d(push: bool = False) -> tuple[dict, dict]:
    """P69 T48: the tilted, extruded pie; the largest slice explodes out on its word; with `push`, the camera pushes
    onto it and holds while the other four recede."""
    species = [{"kind": "explode", "at": PIE_EXPLODE_AT, "dur": PIE_EXPLODE_S}]
    return _pie_timeline("Golden: the 3D pie" + (", pushed onto its largest slice" if push else ", exploded"),
                         pie_series(), species, pie_push_camera() if push else None)


def species_proof() -> tuple[dict, dict]:
    """P52 T7 + T8, THE PROOF PAGE FOR HUMAN GATE 3: all three of the last Bravos species on ONE clock, one per
    scene, so the operator reads each at its own instant and then plays the single file end to end.

      0 - 18 s   a ledger LINE page, built to its last series (the memory makers draw at their own 9.5 s delay);
                 the dashed ellipse closes round the series' OWN peak at 11.0 and its flag chip lands beside it
                 (`species-proof` / `@proof-ring`, t = 12.6, before the page's own retract takes it)
     18 - 24 s   a bare plate; six identical sourced icons arrive in reading order on the isometric field and
                 the count is written under them (`@proof-count`, t = 22.5)
     24 - 30 s   a bare plate; three numbered rows are revealed one per word and hold (`@proof-agenda`, t = 28.5)

    The three instants are FLAG_FRAMES entries with `idle` ON - the one flag that is honest here, because what it
    turns on is the WORLD's own breath under the species (E49: every held thing carries a named subtle idle), and
    the species' own idles run either way. So the proof frames are the frames the operator should judge: the page
    breathing under a closed ring, a field holding, an agenda standing."""
    import build_scene_timeline_f as BST
    ring = dict(RING_DASHED, at=11.0, dur=4.0)
    field = dict(COUNT_FIELD, at=18.6, dur=5.4)
    block = dict(AGENDA_BLOCK, at=24.4, dur=5.6,
                 rows=[{"text": "A Treasury page"}, {"text": "Your phone", "at": 25.6}, {"text": "The bill", "at": 26.8, "sub": "$4,500"}])
    for sp, plate in ((ring, "ledger:golden-line:line"), (field, "plate-plain"), (block, "plate-plain")):
        errs = BST.validate_species([sp], (0, 0, 0), plate)
        assert not errs, errs
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": _line_page(), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, 18.0], "docks": [], "species": [ring]},
              {"scene_id": "s02", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [18.0, 24.0], "docks": [], "species": [field]},
              {"scene_id": "s03", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [24.0, RUNTIME], "docks": [], "species": [block]}]
    uris = _base_uris()
    for name in sorted({field["icon"], ring["flag_icon"]}):
        uris[BST.ICON_PREFIX + name] = BST.icon_geometry(name)
    return _timeline("Golden: the last three Bravos species, one clock (P52 human gate 3)", scenes, {}, None), uris


# ---- P55 T6: THE VERDICT STACK AND THE TEST CARD, AS THE INLINE ENGINE DRAWS THEM TODAY -------------------
# Goldens first: T7 lifts `drawStack` and the `C.checklist` branch of `drawChart` out of scene-evidence-engine.mjs into
# species modules, and these frames are what that refactor must keep byte-identical.
SEVEN_SEG = {"a": (0.0, 0.0, 1.0, 0.12), "b": (0.84, 0.0, 1.0, 0.54), "c": (0.84, 0.46, 1.0, 1.0),
             "d": (0.0, 0.88, 1.0, 1.0), "e": (0.0, 0.46, 0.16, 1.0), "f": (0.0, 0.0, 0.16, 0.54),
             "g": (0.0, 0.44, 1.0, 0.56)}
DIGIT_SEGS = {1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc", 5: "afgcd", 6: "afgedc",
              7: "abc", 8: "abcdefg", 9: "abcdfg"}   # P61 T7: 7-9, so the SHORT's nine-proof wall is read by number too
STACK_COLOURS = [(196, 58, 64), (38, 110, 196), (30, 150, 120), (214, 150, 20), (128, 72, 176), (226, 110, 150)]
STACK_ITEMS_AT = [3.0, 5.0, 7.0, 9.0, 11.0, 13.0]
STACK_CLEAR_AT = 20.0
# P61 T7 - THE SHORT's wall: NINE proofs, the count Steel and Paper's own verdict beat carries (`ev-holds-stack-v1`,
# 702.87-723.69 s), on a short's clock - 1.4-1.6 s a proof instead of 2-3 s, and a pivot line 2.7 s after the last.
STACK9_COLOURS = STACK_COLOURS + [(84, 140, 200), (188, 96, 52), (60, 132, 96)]
STACK9_ITEMS_AT = [2.0, 3.5, 5.0, 6.4, 7.8, 9.2, 10.6, 12.2, 13.8]
STACK9_CLEAR_AT = 16.5


def png_numbered_card(n: int, rgb: tuple[int, int, int]) -> bytes:
    """A synthetic stack MEMBER: a coloured ground carrying its big seven-segment number on the left and three
    headline bars on the right, in the card's own 1056:480 aspect (the `.stackcard` box) - so a frame read tells the
    six cards apart by colour AND by number. Stdlib-only, via png_bars."""
    box = (0.07, 0.14, 0.30, 0.86)
    segs = [(box[0] + (box[2] - box[0]) * x0, box[1] + (box[3] - box[1]) * y0,
             box[0] + (box[2] - box[0]) * x1, box[1] + (box[3] - box[1]) * y1)
            for x0, y0, x1, y1 in (SEVEN_SEG[s] for s in DIGIT_SEGS[n])]
    lines = [(0.40, 0.22, 0.93, 0.34), (0.40, 0.46, 0.86, 0.58), (0.40, 0.70, 0.72, 0.80)]
    return png_bars(264, 120, rgb, segs + lines, ink=(250, 247, 240))


def verdict_stack() -> tuple[dict, dict]:
    """P55 T6 - THE VERDICT STACK (dock payload `stack`, doc 29 s9.24 / s9.24b), drawn by the inline `drawStack`.

    Six numbered members, the shape of Steel and Paper build-f `ev-holds-stack-v1` (`stack.items[{id, at}]` and
    `clear_at`), on one host dock that is a lifecycle anchor only. All five phases are on this clock: ENTER one at a
    time from depth on each `at`, FOCUS large near centre, RECEDE to a rail spot when the next beat lands, IDLE drift,
    BURST radially on `clear_at`. The dock entry is the COMPILER's own `dock_entry`, and the exit sits at clear_at +
    0.65 as the shipped row does. Judged mid-pile (FRAME_T 12.5) and at the burst (PROOF_FRAMES @proof-burst)."""
    import build_scene_timeline_f as BST
    host = "ev-golden-verdict-stack"
    items = [{"id": f"ev-golden-stack-{i + 1}", "at": at} for i, at in enumerate(STACK_ITEMS_AT)]
    evidence = {host: {"title": "Everything we checked holds", "source": "golden", "species": "stack",
                       "document": {"path": "golden", "sha256": "0" * 64}, "badges": [],
                       "stack": {"items": items, "clear_at": STACK_CLEAR_AT}}}
    docks = [BST.dock_entry(host, 0, 2.0, round(STACK_CLEAR_AT + 0.65, 2), 0)]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": []}]
    uris = _base_uris()
    uris[host] = uri("image/png", png_solid(64, 29, (22, 24, 28)))
    for i, it in enumerate(items):
        uris[it["id"]] = uri("image/png", png_numbered_card(i + 1, STACK_COLOURS[i]))
    return _timeline("Golden: the verdict stack", scenes, evidence, None), uris


def verdict_stack_9x16() -> tuple[dict, dict]:
    """P61 T7 - THE VERDICT STACK ON A SHORT (dock payload `stack`, form 9:16; doc 29 s9.24 / s9.24b, BACKLOG R26-82).

    The same payload as `verdict-stack` on a 1080x1920 stage, with NINE members (Steel and Paper's own count) and the
    layout `species/verdict.mjs` VERDICT_9X16 re-lays for a short: nine asymmetric rail spots down the whole height of
    G-l's safe box x[80,880] y[280,1340], a focus card 63.9 % of the stage width near the box's centre, a named E49
    idle on the rails, and a burst thrown radially from the MOSAIC's centre on the portrait frame's own axes.

    Its window comes from `stack_entry`, so the beats and the host dock's life are ONE fact (doc 29 s9.24's 0.77 s
    dimming drift). Judged at the MOSAIC (FRAME_T 13.6); its other four phases ride PROOF_FRAMES."""
    import build_scene_timeline_f as BST
    host = "ev-golden-verdict-stack-9x16"
    items = [{"id": f"ev-golden-stack9-{i + 1}", "at": at} for i, at in enumerate(STACK9_ITEMS_AT)]
    stack, enter, exitt = BST.stack_entry(items, STACK9_CLEAR_AT, form="9:16")
    evidence = {host: {"title": "Everything we checked holds", "source": "golden", "species": "stack",
                       "document": {"path": "golden", "sha256": "0" * 64}, "badges": [], "stack": stack}}
    docks = [BST.dock_entry(host, 0, enter, exitt, 0)]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": []}]
    uris = _base_uris()
    uris[host] = uri("image/png", png_solid(64, 29, (22, 24, 28)))
    for i, it in enumerate(items):
        uris[it["id"]] = uri("image/png", png_numbered_card(i + 1, STACK9_COLOURS[i]))
    return _timeline("Golden: the verdict stack on a short", scenes, evidence, "9:16"), uris


def test_card() -> tuple[dict, dict]:
    """P55 T6 - THE TEST CARD (chart-dock form `checklist`), drawn by the `if (C.checklist)` branch of `drawChart`.

    The shape of Steel and Paper build-f `ev-test-scorecard-v1` (a head of four, three rows of four cells, each row
    keyed by `delay`), with synthetic words. On a hold of 12 s or more a row lands at its own delay and its cells run
    the long offsets: the question TYPES (0.045 s a character), the where-cell fades at +0.6, the two answer cells take
    the marker sweep at +1.0 and +1.6. The delays are literal (the compiler's `narration_key_delays` needs a take's
    words; a golden has none). Judged with every question typed and the answers swept (FRAME_T 11.4)."""
    import build_scene_timeline_f as BST
    card = "ev-golden-test-card"
    chart = {"title": "THE TEST - three questions", "sub": "Left: what holds.  Right: what is believed.",
             "src": "golden - the three-question test",
             "checklist": {"head": ["Ask", "Where to look", "Holds", "Believed"],
                           "rows": [{"cells": ["1  Scarce?", "the order book", "sold out", "abundant"], "delay": 1.0},
                                    {"cells": ["2  Cash or paper?", "the share count", "earns cash", "issues paper"], "delay": 4.0},
                                    {"cells": ["3  Used tomorrow?", "the product", "still used", "needs a story"], "delay": 7.0}]}}
    evidence = {card: {"title": "THE TEST", "source": "golden", "species": "data",
                       "document": {"path": "golden", "sha256": "0" * 64},
                       "badges": [{"label": "THE TEST", "value": "30 seconds", "tag": "a holding", "accent": "sunflower"}],
                       "chart": chart}}
    docks = [BST.dock_entry(card, 0, 2.0, RUNTIME, 1)]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": []}]
    uris = _base_uris()
    uris[card] = uri("image/png", png_solid(64, 29, (22, 24, 28)))
    return _timeline("Golden: the test card", scenes, evidence, None), uris


# P69 T28b / R26-300: THE TEST CARD THAT READS ON A PHONE - row 20's card, at the right 0.60 of the stage so the host
# stays visible at left, on the checklist's `profile: "phone"` (species/checklist.mjs CHECKLIST_PROFILES.phone).
PHONE_CARD = {"centre_w": 0.60, "centre_x": 0.68, "centre_y": 0.46}   # the right ~60 % (1152 px), clear of the caption
PHONE_CARD_ASPECT = 480 / 1056                                       # the chart dock's own canvas, unchanged by the profile
# THE WIDTH BUDGET at the floor (MEASURED, Segoe UI 600 at the profile's 58 px): the canvas' usable span is 1000 px, the
# three columns' air 108, so a row's three LONGEST cells (one per column) share 892 px, about 30 characters - these fit
# unsqueezed (233 + 274 + 351 = 858). Row 20's full questions do not: "3  Used tomorrow?" alone is 484 px, and the
# answers beside it would squeeze to 0.64 (the question column types, so it never squeezes - FIT_KEEP_Q).
PHONE_CHECKLIST = {"profile": "phone", "head": ["Ask", "Steel", "Paper"],
                   "rows": [{"cells": ["1  Scarce?", "sold out", "on belief"], "delay": 1.0},
                            {"cells": ["2  Cash?", "earns cash", "issues paper"], "delay": 4.0},
                            {"cells": ["3  Lasts?", "still used", "needs a story"], "delay": 7.0}]}


def test_card_phone(plate_uri: str | None = None) -> tuple[dict, dict]:
    """P69 T28b - the test card on the checklist's PHONE profile: a head of three (the question and its two answers - the
    chips already said where to look), three rows of short cells, no sub (the title carries it, as the T10c card
    profile), docked at the right 0.60 of the stage. The profile sets the type (cells and head at the long-form phone
    floor as displayed), the row pitch and the highlighter band together, and fills the canvas: row 1 at PT + 130,
    pitch 90, the last row's baseline in the canvas' lower third. Judged MID-FILL (FRAME_T): rows 1-2 swept, row 3 typed,
    its steel answer swept and its paper answer mid-sweep. `plate_uri` swaps the plain plate for a real one (the
    test-bed frame read on row 20's desk); the golden is the plain plate."""
    import build_scene_timeline_f as BST
    card = "ev-golden-test-card-phone"
    chart = {"title": "The test - 30 seconds a holding", "src": "golden - the three-question test",
             "checklist": json.loads(json.dumps(PHONE_CHECKLIST))}   # the compiler's check: test_checklist_phone_profile.py
    evidence = {card: {"title": "THE TEST", "source": "golden", "species": "chart",
                       "document": {"path": "golden", "sha256": "0" * 64}, "badges": [], "chart": chart}}
    place = BST.centred_place(None, None, PHONE_CARD_ASPECT, None, PHONE_CARD["centre_w"], None,
                              PHONE_CARD["centre_y"], PHONE_CARD["centre_x"])
    docks = [BST.dock_entry(card, 0, 2.0, RUNTIME, 0, BST.DOCK_KIND_IMAGE, place, None, None, True)]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": []}]
    uris = _base_uris()
    if plate_uri:
        uris["plate-plain"] = plate_uri
    uris[card] = uri("image/png", png_solid(64, 29, (22, 24, 28)))
    return _timeline("Golden: the test card on a phone", scenes, evidence, None), uris


SURFACES = {
    "ledger-page-mid-build": ledger_page_mid_build,
    "chart-callout": chart_callout,
    "ledger-soak-page": ledger_soak_page,
    "dock-pair-16x9": lambda: _dock_pair(None),
    "dock-pair-9x16": lambda: _dock_pair("9:16"),
    "ledger-extend": ledger_extend,
    "ledger-keyed": ledger_keyed,
    "occluder-dock": occluder_dock,
    "camera-layers": camera_layers,   # P58 T3: one camera, four depth planes
    "page-depth": page_depth,         # P58 T4: the ledger page as a card at a depth, on a plane the homography turns
    "thread-baseline": thread_baseline,
    "tags-to-bars": tags_to_bars,
    "data-to-bars": data_to_bars,
    "chip-board": chip_board,
    "press-stack": press_stack,
    "art-embed": art_embed,
    "flow-swap": flow_swap,
    "span-decade": span_decade,
    "vecmap-arc": vecmap_arc,
    "tiers-two": tiers_two,
    "treemap-cross": treemap_cross,
    "count-array": count_array,          # P52 T7
    "agenda-two": agenda_two,            # P52 T8
    "agenda-page": agenda_page,          # P61 T8: the plate version of the list (E99 s16)
    "ring-dashed-chip": ring_dashed_chip,   # P52 T8
    "rings-on-vertices": rings_on_vertices,   # P69 T47 / E99 s109 (3): three peaks ringed in turn, the valley lit
    "share-donut-flat": share_donut_flat,            # P69 T48 / E99 s109 (4): the flat donut, true angles, every figure written
    "share-pie-3d": share_pie_3d,                    # P69 T48: the tilted, extruded pie, its largest slice exploded on its word
    "share-pie-3d-push": lambda: share_pie_3d(True),  # P69 T48: ... and the camera pushed onto that slice, the others receded
    "species-proof": species_proof,      # P52 T7 + T8: the proof page for human gate 3
    "melt-page": melt_page,                                  # E88: the throw
    "melt-splash": lambda: melt_page("splash:chart"),        # E88: the splatter forms the next chart
    "melt-plate": lambda: melt_page("splash:plate"),         # E88: the splatter paints a narrative plate
    "melt-ball-roll": lambda: melt_page("throw", weight=True),  # R26-118 / E88 s6-s7: the ball with MASS - it lands, rolls, is nudged and settles before the throw
    # P61 T5b / E99 s42: the same ball at the same instants, in the two body colours the operator asked to see
    # ("I would be interested in seeing it just melt to the slate gray or the reference color also to see what that
    # looks like"). Neither is a SURFACE: each carries one PROOF frame, the settle, so the three-way crop beside
    # `melt-ball-roll@proof-settle` is one instant read three ways.
    "melt-ball-slate": lambda: melt_page("throw", weight=True, body="slate"),          # the BOARD's own ink (--lp-char #25313C)
    "melt-ball-reference": lambda: melt_page("throw", weight=True, body="reference"),  # the blueprint's near-black metal (s3.3)
    # P72 T23 / R26-146 / E99 s49 (2): the ball's inks MERGED - the page's four series mixed by Kubelka-Munk, each one
    # swirling through the mix - off the same two pages and at the same instants as the pair above, so the operator
    # reads it beside the reference ball (P72-HG1 (3)); a candidate, authored only by name
    "melt-ball-blend": lambda: melt_page("throw", weight=True, body="blend"),
    # P72 T23 / R26-157 / E99 s56: `melt-splash` with its pitch picked OFF the frame and thrown back in faster -
    # the numbers (the carry, the beat of nothing, the return's chord and speed against the approved pitch and throw)
    # ride sources/melt-splash-offscreen.sidecar.json, and melt.test.mjs proves them current
    "melt-splash-offscreen": lambda: melt_page("splash:chart", offscreen=True),
}


SURFACES.update({   # P52 T6: the newsreel band and the two readings of the bottom strip (gate 1's three frames)
    "newsreel-band": newsreel_band,
    "newsreel-strip-9x16": newsreel_strip_9x16,
    "newsreel-strip-above": newsreel_strip_above,
})
SURFACES.update({   # P55 T6: the two inline dock painters, pinned before T7 promotes them
    "verdict-stack": verdict_stack,
    "test-card": test_card,
})
SURFACES.update({   # P69 T28b / R26-300: the test card on the checklist's phone profile, at the right 0.60 of the stage
    "test-card-phone": test_card_phone,
})
SURFACES.update({   # P61 T7 / R26-82: the same five phases on a SHORT - the mosaic is the base frame, the rest ride PROOF_FRAMES
    "verdict-stack-9x16": verdict_stack_9x16,
})
SURFACES.update({   # P58 T5: the two 2.5D chart forms, each beside a flat golden of the same data (human gate 3)
    "form-extruded-bar": form_extruded_bar,
    "form-tilted-line": form_tilted_line,
})
FRAME_T.update({   # both are read at the HOLD; their build and their leave ride PROOF_FRAMES
    "form-extruded-bar": FORM_LINE_T[1],
    "form-tilted-line": FORM_LINE_T[1],
})


# ---- P57 T12 / R26-70b: THE COMPARE (E76) -----------------------------------------------------------------
# The row the compiler's own grammar test authors (test_metric_comparator.py:32): a forward P/E of 24.8x against a
# 21.5x history, derived into "15 % dearer" and carrying its provenance. The page WRITES the quoted figure at its
# datum first (E50 - the compiler refuses a compare whose metric no `figure` species on the page carries), and the
# compare turns that written number into the one the viewer feels.
COMPARE_FIGURE = {"kind": "figure", "at": 6.0, "dur": 2.0, "text": "24.8x", "series": 0, "dy": -7,
                  "target": {"kind": "datum", "index": 20}}   # the page's own empty band, above the rising line and under the unit caption: the comparator is a LONGER string than the metric and takes a sub with it, and a figure is never written over drawn ink (M34)
COMPARE_ROW = {"kind": "chart_to", "at": 12.0, "dur": 2.4, "to": "compare", "hold": "metric",
               "metric": {"value": 24.8, "text": "24.8x", "label": "forward P/E"},
               "comparator": {"value": 0.1535, "text": "15 % dearer", "label": "dearer than its own history"},
               "inputs": {"pe": 24.8, "hist": 21.5}, "derive": "pe / hist - 1",
               "source": "[DERIVED: from the golden's own two synthetic figures, pe / hist - 1]"}


def compare_morph() -> tuple[dict, dict]:
    """P57 T12 / R26-70b (E76: *"showing the P/E and then morphing it to a more visual number would be a great
    repeatable mechanism"*): the sixth `chart_to` verb, PAINTED. A dense ledger LINE page - `span-decade`'s own,
    every series drawn - writes "24.8x" at a datum by the hand (6.0), and at 12.0 that written figure becomes
    "15 % dearer" over 2.4 s: the numeral counts on min-jerk, the words either side cross through zero at the
    swap, the comparator's label is written beneath, and the quoted metric holds beside it (`hold: "metric"`).

    P57 T12c re-goldened it onto the DEFAULT form as the operator corrected it a second time (E76 s5: *"melt it into
    a ball, then we either throw it off the page, splatter it back on to the canvas and build the chart/graph from
    that, or morph it from the ball into the chart"*, and *"it's just math"*). The row names no `form` and no `then`,
    so the quoted figure's own OUTLINES - measured off the page's ink by kinetics/contour.mjs, never fetched from a
    font - sag on melt.mjs's law over the first 0.30 of the window, BALL UP into one disc that holds the ink's own
    area by 0.55, and are then carried by morph_a into the comparator's glyph rings, which the figure's own <text>
    replaces at u = 1 exactly.

    The numbers are the golden's own synthetic ones, not a figure about the world; the ARITHMETIC is authored and
    the compiler checks it here, as it would on any shot row (E77). Four instants are read: the ink mid-SAG
    (`@proof-sag`), the BALL formed (`@proof-ball`), the morph's own half-way point (`@proof-050` - neither a ball
    nor a number), and the landed frame - the comparator with its label and the metric ghosted beside it
    (FRAME_T 14.9). T12b's text melt is the `compare-streak` surface, the counter T12 shipped the `compare-count`."""
    import build_scene_timeline_f as BST
    species = [dict(COMPARE_FIGURE), dict(COMPARE_ROW)]
    plate = "ledger:golden-line:line"
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": _line_page(), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the quoted metric becomes its comparator", scenes, {}, None), _base_uris()


def compare_streak() -> tuple[dict, dict]:
    """P57 T12c: THE SAME ROW, authoring `form: "streak"` - the text melt P57 T12b shipped as the default, kept whole
    when the operator's second correction (E76 s5: *"melt it into a ball, then we either throw it off the page,
    splatter it back on to the canvas ... or morph it from the ball into the chart"*) made the BALL the default. The
    glyphs still drip where they stand, on melt.mjs's own run and stepped clock under its words' streak filter, and the
    hand still re-writes the comparator at the same datum. This surface is what says the rename changed no pixel: its
    four frames are byte-identical to the ones `compare-morph` carried before T12c. Nothing but the `form` key differs
    from compare_morph()."""
    import build_scene_timeline_f as BST
    species = [dict(COMPARE_FIGURE), dict(COMPARE_ROW, form="streak")]
    plate = "ledger:golden-line:line"
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": _line_page(), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the quoted metric becomes its comparator", scenes, {}, None), _base_uris()


def compare_count() -> tuple[dict, dict]:
    """P57 T12b: THE SAME ROW, authoring `form: "count"` - E60's counter, the form T12 shipped and the operator
    corrected (*"just collapse or melt then re-draw"*). It is kept whole as a setting, because a number becoming
    another number by counting is still the honest form where the two are the same KIND of number, and this surface is
    what says so in pixels: its frames are byte-identical to the ones `compare-morph` carried before T12b re-goldened
    it onto the melt. Nothing but the `form` key differs from compare_morph()."""
    import build_scene_timeline_f as BST
    species = [dict(COMPARE_FIGURE), dict(COMPARE_ROW, form="count")]
    plate = "ledger:golden-line:line"
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": _line_page(), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the quoted metric becomes its comparator", scenes, {}, None), _base_uris()


SURFACES.update({   # P57 T12: the compare verb's paint (species/compare.mjs) - T12b/T12c: one surface per FORM
    "compare-morph": compare_morph,
    "compare-streak": compare_streak,
    "compare-count": compare_count,
})


# ---- P57 T13 / R26-75: THE SLIDE (E87 s3) -----------------------------------------------------------------
def slide_pages() -> tuple[dict, dict]:
    """E87 s3 (the operator, 2026-09-13: *"We should also have a push/slide option ... basically literally pushing out
    one frame with the next, so that you keep some of that congruency"*) - ONE CHART PUSHES THE NEXT ONTO THE STAGE.

    The same two pages the melt golden hands over between, so the two transitions are read on the same evidence: the
    line page every other golden is built from takes the whole 15 s to draw itself, and at SLIDE_CUT the bars page of
    where those lines end pushes it off to the LEFT. `exit` names the transition INTO the scene it sits on (E47), so
    the slide is scene 2's. Its page arrives on its AXES - the stamp a chart-to-chart boundary gets, and the stamp a
    slide gets, because a slide hands the world over and never takes it (it is not in WORLD_TAKING_EXITS).

    Both worlds are mounted and both move: the outgoing box travels -u * its own span and the incoming (1 - u) * the
    same span, so they abut at every instant. Two instants are read - mid-slide (FRAME_T slide-mid, the seam on the
    stage's centre line) and the landing (slide-landed)."""
    import json
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    page["exit"] = "cut"   # LEDGER_EXITS / E40 #5: no retract - the slide is how this chart leaves
    raw = json.loads(SERIES.read_text(encoding="utf-8"))
    bars = {"title": "Where the four lines end", "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
    page2 = LPG.build_spec(bars, "bars", None, "right")
    page2["field"] = "scribble"
    page2["enter"] = "axes"   # what stamp_transition_pages writes on this boundary: chart to chart, never empty cream
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, SLIDE_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "slide:left", "span": [SLIDE_CUT, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: the next chart pushes this one off the stage", scenes, {}, None), _base_uris()


SURFACES.update({   # P57 T13: the slide's two instants
    "slide-mid": slide_pages,
    "slide-landed": slide_pages,
})


# ---- P57 T15 / R26-78: THE RACE'S TWO PATH SETTINGS (E91 s1) ----------------------------------------------
# The operator, human gate 5 of P52: *"both Arm A and B look good to me, Arm A is smoother, but Arm B has more
# dynamism/energy to it. seems like 2 settings to me, not a discard situation."* The PAIR is the same race page
# at the same instant under the two settings, so the only thing a diff between them can show is the path a mark
# takes BETWEEN two period knots - the clock, the knots, the ranks and every label are identical in both.
#
# The data are the A/B's own five synthetic rows (`tokyo-tea-break/build-short-t17/build_race_arms.py`), which is
# the evidence E91 was ruled on. Synthetic, and said to be synthetic on the page: this surface measures a MOTION
# LAW, and a figure about the world has no business in a test rig (the research gate - UNSOURCED never ships).
RACE_PERIODS = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
RACE_ROWS = [
    ("ALPHA", [100, 118, 131, 140, 152, 168, 181]),
    ("BETA", [92, 108, 126, 148, 171, 190, 212]),      # passes ALPHA and CHI mid-run
    ("CHI", [118, 122, 125, 129, 133, 138, 142]),      # opens as the leader, is passed twice
    ("DELTA", [64, 79, 96, 118, 142, 149, 155]),
    ("EPS", [51, 57, 66, 78, 86, 95, 103]),
]
RACE_LEAD = 3.9        # LP.ROLL 0.7 + LP.SAVOR 0.8 + LP.FIELD 2.4: the page's lead before its build clock starts
RACE_IN = 0.6          # LPX.RACE_IN: the grow-in into period 0, so the bars are full height at every instant below
RACE_PERIOD_S = 1.2    # LPX.RACE_PERIOD: one period, the same in both settings by construction
RACE_U = 0.5           # MID-PERIOD in the FIRST segment (2019 -> 2020), where the two paths differ most and NO
                       # rank swap is in flight in either setting - so the pair reads the PATH and nothing else
                       # (measured: the clothoid carries ALPHA 4.9 px and BETA 4.1 px off their lanes and CHI
                       # 2.4 px the other way, with every bar's width off by up to 0.9 px; at u = 0 and u = 1 the
                       # two settings agree to the last bit, because a clothoid segment's ends ARE its knots)


def race_t(u: float) -> float:
    """Scene seconds at period fraction `u` - the same clock in both settings (E91 s1)."""
    return round(RACE_LEAD + RACE_IN + u * RACE_PERIOD_S, 3)


FRAME_T["race-path-eased"] = race_t(RACE_U)
FRAME_T["race-path-clothoid"] = race_t(RACE_U)


def race_series() -> dict:
    return {"title": "Five rows, seven periods",
            "sub": "a synthetic race - the motion law under test, not a figure about the world",
            "src": "Synthetic series for the P57 T15 race-path pair (E91 s1); not a claim",
            "periods": list(RACE_PERIODS),
            "series": [{"name": name, "values": list(values)} for name, values in RACE_ROWS]}


def race_page(path: str) -> dict:
    """The race page with its PATH setting named. `eased` is the engine's default written out loud; the compiler's
    own grammar for the key is `ledger:<series>:race;path=<setting>` (build_scene_timeline_f.RACE_PATHS)."""
    page = LPG.build_spec(race_series(), "race", None, "right")
    page["field"] = "scribble"
    page["path"] = path
    return page


def race_path_surface(path: str) -> tuple[dict, dict]:
    """One arm of the pair. No captions and no Ken Burns: the only thing that moves on this page is the race."""
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": race_page(path), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    tl = _timeline(f"Golden: the race on its {path} path", scenes, {}, None)
    tl["captions"], tl["caption_pages"] = [], []
    return tl, _base_uris()


def race_path_eased() -> tuple[dict, dict]:
    return race_path_surface("eased")


def race_path_clothoid() -> tuple[dict, dict]:
    return race_path_surface("clothoid")


SURFACES.update({   # P57 T15: the two settings, one instant, one page
    "race-path-eased": race_path_eased,
    "race-path-clothoid": race_path_clothoid,
})


# ---- P57 T16 / R26-79: THE RANK SWAP (E91 s2) --------------------------------------------------------------
# E91 s2: *"whichever setting, rows pass each other cleanly: at a rank swap two labels or two values never
# print on top of each other"*. The failure was measured on these very rows - arm B at 7.5 s printed BETA and
# ALPHA in one row ("ALBETA") with "136" over "138" - because at the crossing the two rows ARE at the same row
# position, so their names sit on one baseline and their values, equal there by definition, print on one
# another. This surface is the SAME five rows at that instant, on the DEFAULT path (the setting that ships);
# test_race_swap.py reads the clothoid arm at the same instant through the player.


def _inv_smooth(s: float) -> float:
    """smoothstep's inverse, closed form - the engine's own `lpInvSmooth`."""
    return 0.5 - math.sin(math.asin(1 - 2 * min(max(s, 0.0), 1.0)) / 3)


def race_crossing(a: str, b: str) -> float:
    """u (in period units) where rows `a` and `b` cross, solved exactly as `buildLedgerRace` solves it: the
    segment whose ends disagree about the order, then the eased difference's own root. The engine centres
    that pair's swap window here, so this is the instant the two rows are on top of each other."""
    rows = dict(RACE_ROWS)
    A, B = rows[a], rows[b]
    for i in range(len(RACE_PERIODS) - 1):
        if (A[i] > B[i]) == (A[i + 1] > B[i + 1]):
            continue
        den = (A[i + 1] - A[i]) - (B[i + 1] - B[i])
        return i + (_inv_smooth((B[i] - A[i]) / den) if den else 0.0)
    raise AssertionError(f"{a} and {b} never cross in this fixture")


RACE_SWAP_PAIR = ("ALPHA", "BETA")     # the pair the operator's still caught: BETA takes second place off ALPHA
RACE_SWAP_U = race_crossing(*RACE_SWAP_PAIR)   # 2.4225 periods: mid-segment 2021 -> 2022, the crossing itself

FRAME_T["race-swap"] = race_t(RACE_SWAP_U)     # 7.407 s - and the gate's own "the chart's landing" instant is 7.40


def race_swap() -> tuple[dict, dict]:
    """The race at the crossing of its two middle rows. The page is the path pair's page and the clock is
    the path pair's clock: only the instant differs, so a diff against `race-path-eased` is the swap."""
    return race_path_surface("eased")


SURFACES.update({   # P57 T16: the crossing itself - two rows, two names, two numbers, none on another
    "race-swap": race_swap,
})


# ---- P57 T18 / R26-95: THE ROUTE ON A STILL, PINNED BEFORE `trace` BECOMES A MODULE -----------------------
# The golden FIRST: `species:trace` is lifted out of the engine's body into species/trace.mjs, and this frame is
# what that lift has to keep byte-identical. It carries BOTH forms the painter has, so neither can move unseen:
#   the HOP      the opt-in bowed crossing (2026-09-08, the crossings map), drawn once over `draw_s` and HELD -
#                one hop landed with its arrowhead, one MID-DRAW, the shape the approved Japan short ships at
#                t 9.22 (`from` / `to` as stage fractions, `bow` the arc's height as a fraction of the chord).
#   the TRACE    the plain still-life redraw: a seeded zigzag down the region's diagonal, drawn by dash over
#                TRACE_DRAW, held, faded, and again every TRACE_PERIOD - caught mid-draw on its second pass.
# The STAMP the `when` names ("stamps stack at them") is the Japan short's own pairing: a callout's label at the
# point the first hop lands, at rest by this instant.
TRACE_A = [0.18, 0.62]    # the route's three named points, as stage fractions
TRACE_B = [0.52, 0.30]
TRACE_C = [0.82, 0.56]
TRACE_AT = 5.0            # the first hop's `at` - the plain trace starts with it
TRACE_HOP2_AT = 8.0       # the second hop's, drawn over 0.9 s
FRAME_T["trace-hop"] = TRACE_HOP2_AT + 0.54   # 8.54: hop 2 exactly 0.6 through its draw (mid-flight, its head not
                                  # yet landed), hop 1 drawn and HELD with its arrowhead, and the plain trace 0.309
                                  # into the draw of its second period ((8.54 - 5.0) / TRACE_PERIOD 3.2 = 1.106)


def _trace_region(p: list[float], q: list[float]) -> dict:
    """The REGION the targeting law (s9.27) needs on a trace: the box the hop crosses. A hop's own coordinates
    are stage fractions and never read it - but a species with no declared target does not fire."""
    return {"kind": "region", "x0": min(p[0], q[0]), "y0": min(p[1], q[1]), "x1": max(p[0], q[0]), "y1": max(p[1], q[1])}


def trace_hop() -> tuple[dict, dict]:
    """P57 T18 - THE ROUTE: two bowed hops across a narrative still, the plain redraw beside them, and the
    figure stamped where the first hop lands. One plate scene, one clock, judged at FRAME_T 8.54."""
    import build_scene_timeline_f as BST
    species = [
        {"kind": "trace", "at": TRACE_AT, "dur": 12.0, "color": "#B0201F", "target": _trace_region(TRACE_A, TRACE_B),
         "hop": {"from": TRACE_A, "to": TRACE_B, "bow": 0.16, "draw_s": 0.55, "width": 9}},
        {"kind": "callout", "at": 6.0, "dur": 8.0, "label": "25%", "pad": 22, "label_scale": 2.2,
         "target": {"kind": "point", "x": TRACE_B[0], "y": TRACE_B[1]}},
        {"kind": "trace", "at": TRACE_HOP2_AT, "dur": 9.0, "color": "#B0201F", "target": _trace_region(TRACE_B, TRACE_C),
         "hop": {"from": TRACE_B, "to": TRACE_C, "bow": -0.2, "draw_s": 0.9, "width": 7}},
        {"kind": "trace", "at": TRACE_AT, "dur": 12.0, "color": "#25313C",
         "target": {"kind": "region", "x0": 0.30, "y0": 0.68, "x1": 0.72, "y1": 0.86}},
    ]
    errs = BST.validate_species(species, (0, 0, 0), "plate-trace")
    assert not errs, errs
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-trace", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    uris["plate-trace"] = uri("image/png", png_scene(320, 180))   # a picture to cross: the melt's own committed stand-in
    return _timeline("Golden: the route hops across a still", scenes, {}, None), uris


SURFACES.update({   # P57 T18: the hop mid-draw, the hop landed, the plain redraw and the stamp
    "trace-hop": trace_hop,
})


# ---- P57 T19 / R26-96: THE LIGHT ON A DATUM, PINNED BEFORE `spotlight` BECOMES A MODULE -------------------
# The golden FIRST: `species:spotlight` is lifted out of the engine's body into species/spotlight.mjs, and these
# three frames are what that lift has to keep byte-identical. Together they carry every branch the painter has:
#   the DIM       the frame darkened to SPOT_DIM everywhere except a feathered hole (E56: a picture's focus is
#                 the LIGHT, never a ring) - read on the base frame, the light settled on its first datum.
#   `dur: hold`   the operator's own 2026-09-08 ruling on this species ("right now we flash it on, and really,
#                 it should hold until it has a reason not to"), resolved by the compiler's rule (:4086-4094).
#   the GLIDE     the hole travelling between the two DECLARED targets over GLIDE_S on the io ease - the proof
#                 frames are taken after it has landed on `target2`, so the second target is pinned too.
#   the IDLE      `idle: "live"` (E49, R26-93's restored branch): the hole's radius BREATHES by the idle's scale
#                 and its centre DRIFTS by the idle's offset. The life check runs on the addition's OWN region
#                 (E56), which is why the two proof frames are the proof: the same surface, the same landed
#                 glide, the same dim - and 2.0 s apart, exactly HALF the breath's 4.0 s period, so whatever
#                 phase the seeded hash hands this species the two sit at opposite ends of one inhale.
SPOT_AT = 6.0             # the light lands - 0.4 s of fade-in, then it holds
SPOT_GLIDE_AT = 3.0       # ... and at at + this (9.0) it starts its 0.6 s glide to the second datum
SPOT_FROM = 60            # the datum it lands on: a point on the line page's first series ...
SPOT_TO = 191             # ... and the peak it walks to (the same datum `ring-dashed-chip` rings: pts[191])

FRAME_T["spotlight-hold"] = 8.0   # HELD on the first datum: the fade-in is over and the glide has not begun
                                  # (8.0 - 6.0 - 3.0 < 0, so the ease clamps to 0 and the hole sits on `target`)


def _hold(entry: dict, row_end: float) -> dict:
    """`dur: "hold"` resolved as the COMPILER resolves it (build_scene_timeline_f.py:4086-4094): held until the
    next event on the row, or the row's end. A golden is written straight from authored scenes, so the rule is
    applied here rather than assumed - and `held` is written beside it, as the compiler writes it."""
    import build_scene_timeline_f as BST
    assert entry["dur"] == "hold", entry
    dur = round(max(0.05, row_end - float(entry["at"])), 2)
    assert dur >= BST.HOLD_MIN_S, f"a held light with no room is a flash, and a flash is a glitch: {dur}"
    return {**entry, "dur": dur, "held": True}


def spotlight_hold() -> tuple[dict, dict]:
    """P57 T19 - THE LIGHT: the frame dimmed except a feathered hole over a declared datum of a ledger line page,
    held (`dur: "hold"`), gliding to a second datum at SPOT_GLIDE_AT, and breathing on the `live` idle the whole
    time. One ledger scene, one clock; judged at FRAME_T 8.0 and at the two PROOF_FRAMES instants."""
    import build_scene_timeline_f as BST
    species = [{"kind": "spotlight", "at": SPOT_AT, "dur": "hold", "idle": "live", "glide_at": SPOT_GLIDE_AT,
                "target": {"kind": "datum", "index": SPOT_FROM}, "target2": {"kind": "datum", "index": SPOT_TO}}]
    species = [_hold(species[0], RUNTIME)]   # no later event on the row: the light holds to the row's end
    errs = BST.validate_species(species, (0, 0, 0), "ledger:golden-line:line")   # ... and validate_species reads the RESOLVED row, as the compiler hands it one
    assert not errs, errs
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": _line_page(), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the light holds on a datum and glides", scenes, {}, None), _base_uris()


SURFACES.update({   # P57 T19: the dim, the lit datum, the held light (its two idle phases ride PROOF_FRAMES)
    "spotlight-hold": spotlight_hold,
})


# ---- P57 T20 / R26-98: THE WRITTEN FIGURE, PINNED BEFORE `page_species:figure` BECOMES A MODULE ------------
# The golden FIRST: `paintFigure` and R26-71's step-off are lifted out of the engine's body into
# species/figure.mjs, and this frame is what that lift has to keep byte-identical. It carries the branches the
# painter has:
#   E50           the number the sentence turns to, WRITTEN BY THE HAND at its datum's spot (P47 T6) - glyph by
#                 glyph over the first 0.6 of the word, the sub under it over the remaining 0.4, both fully in
#                 at the judged instant, so the frame is the LANDED figure and not a phase of the write.
#   the PLACE     the authored place: beside the datum, the baseline `dy` lines of the figure's own size above
#                 it, in its own series' ink (E67). The peak stands where the chart has no room to its RIGHT
#                 (`fits` false: D[0] + BRACKET_GAP + BRACKET_ROOM > the page's W), so the number is written
#                 LEFTWARD from it, anchored `end` - the branch a figure at the right of a page always takes.
#   R26-71        the step-off: the box is measured on the WRITTEN glyphs and, where it meets the stroke of its
#                 OWN series, steps away in quanta of PS.FIGURE_STEP. Above a PEAK there is nothing to step off,
#                 which is what this frame pins - the clear case moves by nothing, and the frame proves it.
FIG_AT, FIG_DUR = 12.0, 2.0      # the word: the page has long since built (its last series draws at its own 9.5 s)
FIG_SERIES, FIG_INDEX = 0, 191   # the memory makers' OWN peak - the datum `ring-dashed-chip` rings: pts[191] = 1074.29

FRAME_T["page-figure"] = 14.4    # LANDED: the figure is fully written (its last glyph is in at 12.0 + 0.69 * 2.0)
                                 # and the sub has taken the rest of the word - its own last glyph holding at the
                                 # 0.625 the inline write clock has always left it at, which this frame pins too


def page_figure() -> tuple[dict, dict]:
    """P57 T20 - THE FIGURE: the number the sentence turns to, written by the hand at its datum's spot on a
    ledger LINE page (`span-decade`'s own page, no emphasis so every series is drawn), with its sub beneath it
    and its baseline lifted by the authored `dy`. One ledger scene, one clock; judged at FRAME_T 14.4, by which
    both the figure and its sub are fully written. The text is the page's OWN datum (series 0, index 191 =
    1074.29 on the index its y axis names - `ring-dashed-chip`'s peak), never a number we made up (E53)."""
    import build_scene_timeline_f as BST
    species = [{"kind": "figure", "at": FIG_AT, "dur": FIG_DUR, "text": "1,074 index",
                "sub": "the peak", "color": "crimson", "dy": -0.9,
                "series": FIG_SERIES, "target": {"kind": "datum", "index": FIG_INDEX}}]
    errs = BST.validate_species(species, (0, 0, 0), "ledger:golden-line:line")
    assert not errs, errs
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": _line_page(), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the figure written at its datum", scenes, {}, None), _base_uris()


SURFACES.update({   # P57 T20: the written number landed at its datum, its sub under it (E50)
    "page-figure": page_figure,
})


# ---- P57 T21 / R26-99: THE RECORD DOCUMENT, PINNED BEFORE `dock_payload:record` BECOMES A MODULE ----------
# The golden FIRST: `drawRecord` is lifted out of the engine's body into species/record.mjs, and these two
# frames are what that lift has to keep byte-identical. Between them they carry every branch the painter has:
#   the TYPE clock   each word appears whole on its own onset; the word being spoken is SLICED by a string cut
#                    (never a per-character opacity) over 0.72 of its own gap to the next onset, so the stroke
#                    is the NARRATOR's (CAPABILITIES "Record-document species"), not a constant characters/s.
#   the HIGHLIGHTER  the pulled phrase (`hl`, one word here) takes the marker, whose background-size sweeps
#                    0 -> 100 % over 0.2 s on a cubic-out from that word's own onset - swept long before the
#                    judged instant, so the base frame pins the stroke at rest and the cursor mid-word.
#   the SPACE        `hl[1]`'s trailing space is a text node OUTSIDE the stroke (Tokyo 2026-09-10,
#                    "yen($65 billion)"), which the phrase's one word makes visible in the frame.
#   the LANDING      the attribution at end + 0.15 and the source line at end + 0.45 - the @proof-attr frame's
#                    two toggles, with the quotation whole and the cursor parked after its last word.
REC_WORDS = [("The", 5.00), ("record", 5.34), ("types", 5.72), ("its", 6.06), ("quotation", 6.30),
             ("word", 6.88), ("by", 7.22), ("word,", 7.50), ("on", 7.90), ("the", 8.12),
             ("narrator's", 8.36), ("own", 8.90), ("clock.", 9.16)]
REC_HL = [4, 4]          # ONE word under the marker: "quotation" (`hl` is inclusive at both ends)
REC_END = 9.66           # the quotation's last instant - the attribution and the source line hang off it

FRAME_T["record-typewriter"] = 7.62   # MID-TYPE: words 0-6 stand whole, the marker at rest on "quotation" with its
                                      # space outside the stroke, and word 7 ("word,") is 0.417 through its own
                                      # 0.288 s span (0.72 * the 0.4 s to the next onset) - two of its five
                                      # characters cut, the block cursor after them. Chosen 0.1 clear of the
                                      # nearest rounding boundary of Math.round(len * p), so the pin is a
                                      # character count no float can flip


def record_typewriter() -> tuple[dict, dict]:
    """P57 T21 - THE RECORD DOCUMENT (dock payload `record`, doc 29 / CAPABILITIES "Record-document species"),
    drawn by the inline `drawRecord`.

    One host dock carrying the payload the kit authors ({hdr, kicker, words, hl, end, attr, src} - the shape of
    Tokyo's pledge record), with a SYNTHETIC quotation that describes the mechanism rather than the world (a
    golden never carries a claim about anyone). The word onsets ARE this golden's narration: the engine's type
    clock reads them straight off `words`. Judged mid-type (FRAME_T 7.62) and after the landing (PROOF_FRAMES
    @proof-attr)."""
    import build_scene_timeline_f as BST
    rec = "ev-golden-record"
    record = {"hdr": ["The Golden Register", "14 September 2026"],
              "kicker": "A synthetic quotation - the record's own clock, not a claim about the world",
              "words": [[w, ts] for w, ts in REC_WORDS], "hl": list(REC_HL), "end": REC_END,
              "attr": "The golden surface, typed by the narrator's own onsets",
              "src": "golden - tests/golden/build_golden_sources.py, not a document about the world"}
    evidence = {rec: {"title": "The record", "source": "golden", "species": "record",
                      "document": {"path": "golden", "sha256": "0" * 64}, "badges": [], "record": record}}
    docks = [BST.dock_entry(rec, 0, 2.0, RUNTIME, 0)]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": []}]
    uris = _base_uris()
    uris[rec] = uri("image/png", png_solid(64, 29, (22, 24, 28)))
    return _timeline("Golden: the record document", scenes, evidence, None), uris


SURFACES.update({   # P57 T21: the typewriter mid-word, the marker at rest on the pulled phrase (R26-99)
    "record-typewriter": record_typewriter,
})


# ---- P57 T22 / R26-101: THE PAGE VORTEX, PINNED BEFORE `page_enter:spiral` BECOMES A MODULE ----------------
# The golden FIRST: `lpSpiral` (+ `lpVortex`, `lpParticles`) is lifted out of the engine's body into
# species/spiral.mjs, and these three frames are what that lift has to keep byte-identical. ONE geometry runs
# BOTH directions (doc 29 s9.31, CAPABILITIES "The page VORTEX"), so the surface carries both on one clock:
#   the RETRACT   scene 1's page does not declare `exit: "cut"`, so over its last COLOURS + CHARCOAL (1.0 + 1.0 s)
#                 every colour on the page goes down the drain at the board centre - phase one the ink, the
#                 marks and the series line (@proof-retract, uc 0.5), phase two the crisp charcoal fading to the
#                 FIELD it settled over, which follows it down (@proof-fade, uc 1, uf 0.5 - on this page's
#                 scribble field that is the strokes at half opacity; a soak page's stains take the same map).
#   the RETURN    scene 2 is the same page declared `enter: "spiral"`: the SAME map run backwards over IN
#                 (1.6 s) with no wipe, no roll, no soak and no build - a chart that comes back is never drawn
#                 like new (E25). The base frame is judged mid-unwind.
# Between them they carry every branch the painter has: both clocks, both phases, the CSS particles (the page's
# glyphs), the SVG ones (the chart's marks), the series line re-drawn from its mapped points, and the fade.
SPIRAL_CUT = 15.0        # where the page retracts and comes back: scene 1's end, scene 2's start
SPIRAL_IN = 1.6          # the engine's LP_RETRACT.IN - the length of the return this golden reads against

FRAME_T["spiral-return"] = SPIRAL_CUT + 0.70 * SPIRAL_IN   # MID-UNWIND (ui 0.70): the colours are exactly half
                                  # way back out of the drain (uc = 1 - (ui - 0.4) / 0.6 = 0.5) - every glyph,
                                  # pill and chart mark at half its home radius, 1.5 of the vortex's 3 turns
                                  # still to unwind, the series line curled toward the centre like a noodle -
                                  # and the field has already surfaced (uf 0 from ui 0.55), so the charcoal is
                                  # whole behind them. No blurred band in the frame: the pin is byte-exact


def spiral_return() -> tuple[dict, dict]:
    """P57 T22 - THE PAGE VORTEX, both ways on one clock (doc 29 s9.31; operator 2026-09-05: "a true spiral of
    everything getting sucked back into the cream as if a vortex / whirlpool", "a way tighter vortex, almost
    celestial").

    The ledger LINE page every other golden is built from takes the first 15 s to draw itself and then leaves by
    the RETRACT (its page declares no `exit`, so the vortex runs over its last 2.0 s). Scene 2 is that same page
    declared `enter: "spiral"` - it ARRIVES by the same map run backwards, with no wipe at the boundary
    (`spiralIn` suppresses it), no roll-out, no soak and no build. Judged mid-unwind (FRAME_T), with the
    retract's two phases on PROOF_FRAMES."""
    import copy
    page = _line_page()
    page2 = copy.deepcopy(page)
    page2["enter"] = "spiral"   # E25 / E40: the transition IS the spiral - the page comes back, it is not drawn again
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, SPIRAL_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [SPIRAL_CUT, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: the page goes down the vortex and comes back up it", scenes, {}, None), _base_uris()


SURFACES.update({   # P57 T22: the vortex mid-unwind on the way back (its two retract phases ride PROOF_FRAMES)
    "spiral-return": spiral_return,
})


# ---- P57 T23 / R26-100: THE DIP (E47 s1) ------------------------------------------------------------------
DIP_CUT = 15.0   # P57 T23: where the `dip-boundary` golden hands one chart page to the next - and the frame DIPS across it
DIP_S = 0.47     # the engine's DIP_S and gate_motion_density's: the length this golden declares none against
# THE BOUNDARY FRAME. Both halves of the ramp reach 1 at the boundary, so this frame is BLACK and the cut happens
# inside it (E47 s1). It is the pin the promotion needs: any change to which scene owns which half, or to where the
# clock is centred, moves this frame off black. The ramp's own shape is pinned by `@proof-ramp` on PROOF_FRAMES.
FRAME_T["dip-boundary"] = DIP_CUT


def dip_pages() -> tuple[dict, dict]:
    """E47 s1 (the operator, 2026-09-06) - THE DIP: a plain LINEAR ramp to black over the last DIP_S/2 of the
    outgoing scene and back over the first DIP_S/2 of the incoming one, the cut inside the black.

    The same two pages the slide golden hands over between, so the two transitions are read on one piece of
    evidence: the line page draws itself over the first 15 s and at DIP_CUT the bars page of where those lines end
    takes the world. `exit` names the transition INTO the scene it sits on (E47), so the dip is scene 2's, and it
    STRADDLES the boundary - which is the whole reason two frames are pinned here and not one.

    The incoming page declares no `enter`: a dip is a world-taking transition, so the new page builds from its own
    cream the way a cut's does. The outgoing page declares `exit: "cut"` (LEDGER_EXITS / E40 #5), so the only
    motion across the boundary is the dip's own veil."""
    import json
    page = _line_page()
    page["exit"] = "cut"   # no retract: the dip is how this chart leaves
    raw = json.loads(SERIES.read_text(encoding="utf-8"))
    bars = {"title": "Where the four lines end", "sub": "index at the last point, 100 = Aug \'25", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
    page2 = LPG.build_spec(bars, "bars", None, "right")
    page2["field"] = "scribble"
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, DIP_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "dip", "span": [DIP_CUT, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: the frame dips to black between two charts", scenes, {}, None), _base_uris()


SURFACES.update({   # P57 T23: the dip's black boundary frame (its ramp's midpoint rides PROOF_FRAMES)
    "dip-boundary": dip_pages,
})


# ---- P58 T6 (a): THE DOCK AT A DEPTH -----------------------------------------------------------
# E98 s4: *"the docks, the ball and the slide move THROUGH the depth"*. The scene is `camera-layers`' own - the
# same layered dock plate, the same card landing on the quay at 5.0, the same focus zoom tied to that landing
# (E51; nothing is added to make the parallax visible, E49/E59) - and the ONLY difference is `depth=1.15` on the
# dock's options. So a diff between the two goldens is the card's plane and nothing else: at `camera-layers` the
# card is pinned to the screen while the plate's planes move under it; here it rides the plane the containers
# ride, between the sky (1.0) and the lamp (1.40).
DOCK_DEPTH_K = 1.15   # doc 24's `-mid`: the card stands in the dock's own space - nearer than the sky, behind the lamp - and 1.15 <= DOCK_DEPTH["BEHIND_K"], so it could also name `behind`


def dock_depth() -> tuple[dict, dict]:
    """P58 T6 (a) - THE DOCK AT A DEPTH: `{"depth": 1.15}` on a dock row, and nothing else.

    The card arrives, lands and parks exactly as E45 has it - the arrival, the badges and the settle are the
    choreography they were - and the ONE camera move the scene already had now reaches it: the card takes the
    share 1.15 of the eye's translation and of its zoom, the same share the `-mid` plane takes, instead of
    standing still in screen space while the world moves behind it.

    The option goes through the COMPILER'S own validator (`dock_opts`), so the golden proves the grammar, its
    refusals' sibling and the paint together. Read at the HOLD (FRAME_T 7.9, inside the focus zoom's dead-still
    tail) and mid-move (`@proof-move` 6.56, the instant `camera-layers@proof-mid` is read at, so the two frames
    are directly comparable)."""
    import build_scene_timeline_f as BST
    aid = "plate-dock"
    planes = BST.plate_depth_planes(DOCK_PLATE)
    layers = [{"key": f"{BST.LY_PREFIX}{aid}:{p['role']}", "k": p["depth"], "role": p["role"]} for p in planes]
    opts = BST.dock_opts({"arrive": "land", "depth": DOCK_DEPTH_K})   # the row's own options, validated as a build's are
    dock = BST.dock_entry("ev-quay-card", 0, CAMERA_LAYERS_ENTER, RUNTIME, 2, BST.DOCK_KIND_IMAGE,
                          CAMERA_LAYERS_PLACE, opts.get("arrive"), depth=opts.get("depth"))
    ev = {"ev-quay-card": {"title": "The card on the mid plane", "source": "P58 T6", "species": "deck",
                           "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:2]}}
    P = CAMERA_LAYERS_PLACE
    species = [{"kind": "focus_zoom", "at": CAMERA_LAYERS_AT, "dur": CAMERA_LAYERS_DUR,
                "target": {"kind": "region", "x0": P["x"] / 1920, "y0": P["y"] / 1080,
                           "x1": (P["x"] + P["w"]) / 1920, "y1": (P["y"] + P["h"]) / 1080}}]
    scenes = [{"scene_id": "s01",
               "world": {"asset_id": aid, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0},
                         "layers": layers},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [dock], "species": species}]
    uris = _base_uris()
    uris[aid] = BST.data_uri(DOCK_PLATE)
    for p, ly in zip(planes, layers):
        uris[ly["key"]] = BST.data_uri(Path(p["file"]))        # RAW, as the compiler writes a plane: the alpha IS the plane
    uris["ev-quay-card"] = uri("image/png", png_solid(640, 400, (23, 105, 194)))
    tl = _timeline("Golden: the dock on a layer's plane", scenes, ev, None)
    tl["kinetics"] = {"camera": True}                          # E59's own module drives the species (camNow), as on camera-layers
    return tl, uris


SURFACES.update({   # P58 T6 (a): the card that stands on a plane instead of on the screen
    "dock-depth": dock_depth,
})
FRAME_T["dock-depth"] = FRAME_T["camera-layers"]   # the same instant camera-layers is judged at: the move landed, the eye dead still


# ---- P58 T6 (b): THE MELT'S BALL AT A DEPTH -----------------------------------------------------
# E98 s4: *"the docks, the ball and the slide move THROUGH the depth"*. The two pages are `melt-ball-roll`'s own -
# the line page every golden is built from, melting into the bars page of where its lines end, with `weight` on so
# the ball LANDS, rolls, is nudged and settles - and the two things added are a card that lands on the page at
# MELT_DEPTH_CARD and the one focus zoom tied to that landing (E51/E59: the move already had a reason; nothing here
# was added to make the parallax visible, E49). The exit then names the plane: `melt:weight:depth=1.15`.
#   What that changes is ONE string: the melt's ink clone, its words' clone and the overlay that carries the ball,
# its drips and its ending take the camera at 1.15 instead of at 1.0, so the ball melts, lands and is thrown IN the
# space in front of the board rather than on the glass. The board itself is untouched - it is the outgoing world's
# own element, at the camera it always had.
MELT_DEPTH_K = 1.15           # doc 24's `-mid`: the ball hangs in front of the board, not on it
MELT_DEPTH_CARD = 13.0        # the card lands on the page (stop-action `land`) ...
MELT_DEPTH_AT = 14.0          # ... and the eye goes to that landing, one focus zoom (E51)
MELT_DEPTH_DUR = 4.0          # ... long enough that the eye is still in its hold at the ending, so the base frame is a dead-still pin
MELT_DEPTH_PLACE = {"x": 1210, "y": 640, "w": 600, "h": 375}


def melt_depth() -> tuple[dict, dict]:
    """P58 T6 (b) - THE BALL MELTS AT A PLANE: `melt:weight:depth=1.15`, and nothing else.

    WHAT THE FRAMES SHOW. `@proof-ball` (15.88) is the instant the ball is formed and the weight phase opens - the
    same u `melt-page` is judged at - with the eye mid-move: the ball stands at 1.15 of that move while the board
    it came off stands at 1.0, so the two have parted. The base frame (17.34) is inside the ending, the throw in
    flight, with the eye in its hold - dead still, so the pin is byte-exact - and the ball leaves from the plane it
    melted on. R26-118 is unchanged: the highlight sits on the light, the ink mark turns with the roll."""
    import json as _json
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    page["exit"] = "cut"   # LEDGER_EXITS / E40 #5, R26-60: NO RETRACT - the melt is how this chart leaves
    raw = _json.loads(SERIES.read_text(encoding="utf-8"))
    bars = {"title": "Where the four lines end", "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
    page2 = LPG.build_spec(bars, "bars", None, "right")
    page2["field"] = "scribble"      # the same board as scene 1's: the board is shared
    page2["enter"] = "axes"          # what stamp_transition_pages writes on a chart-to-chart boundary
    import build_scene_timeline_f as BST
    P = MELT_DEPTH_PLACE
    species = [{"kind": "focus_zoom", "at": MELT_DEPTH_AT, "dur": MELT_DEPTH_DUR,
                "target": {"kind": "region", "x0": P["x"] / 1920, "y0": P["y"] / 1080,
                           "x1": (P["x"] + P["w"]) / 1920, "y1": (P["y"] + P["h"]) / 1080}}]
    dock = BST.dock_entry("ev-melt-card", 0, MELT_DEPTH_CARD, MELT_CUT, 1, BST.DOCK_KIND_IMAGE, P, "land")
    ev = {"ev-melt-card": {"title": "The card the eye goes to", "source": "P58 T6", "species": "deck",
                           "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:1]}}
    exit_id = "melt:weight:depth=" + f"{MELT_DEPTH_K:g}"
    assert BST.melt_depth(exit_id) == MELT_DEPTH_K, exit_id       # the COMPILER's own grammar, not a hand-written string
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, MELT_CUT], "docks": [dock], "species": list(species)},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": exit_id, "span": [MELT_CUT, RUNTIME], "docks": [], "species": list(species)}]
    uris = _base_uris()
    uris["ev-melt-card"] = uri("image/png", png_solid(600, 375, (23, 105, 194)))
    tl = _timeline("Golden: the chart's ink balls up and is thrown at a depth", scenes, ev, None)
    tl["kinetics"] = {"camera": True}   # E59's own module drives the species (camNow), as on camera-layers
    return tl, uris


SURFACES.update({   # P58 T6 (b): the ball that melts, lands and is thrown at the `-mid` plane
    "melt-depth": melt_depth,
})
FRAME_T["melt-depth"] = 17.34   # THE ENDING: the window is MELT_CUT + MELT.S + MELT.W_S (2.75 s), so the weight phase
                                # runs 15.88 -> 16.98 and the throw takes what is left; 17.34 is 0.46 through the
                                # throw, with the eye inside its hold (14.0 + 4.0/1.8 = 16.22) - a dead-still pin


# ---- P61 T6 / E99 s2: THE MELT GATHERS TO ONE POINT AND SPLASHES INTO A WORLD PLATE --------------
# The operator (OPERATOR-RULINGS.md:2912): *"it should be closer to the swirl except for instead of a whirlpool,
# vortexing around a single point, it collects and amasses into a single point, that single point should be dense,
# heavy, and vibrating with energy, and when it splashes, it should splash into a scenic, high-resolution world plate
# or fully assembled chart."* This is PROOF A - the world plate, which the ruling names first and which needs no
# chart work at all. Two things differ from `melt-plate`, and nothing else does:
#   the EXIT     `melt:gather:weight:splash:plate` - the gather takes the sag's place (every mark travels to the
#                ball's own centre and amasses on it, no blur and no wipe), the weight phase gives the point T5's
#                material to wear, and the splash is the ink-splat -> ink-bloom route already on disk (MELT.STAIN_RAG,
#                INTAKE-INK-BLOOM-2026-09-08) painting the incoming world up through its stains.
#   the PLATE    the committed TOKYO CUSTOMS DOCK plate (`DOCK_PLATE`, the one `camera-layers` and `dock-depth` are
#                built on), not `melt-plate`'s 320x180 synthetic dusk stand-in: "scenic, high-resolution" is the
#                acceptance, and a stand-in cannot carry it.
# The window is MELT_CUT + MELT.S + MELT.W_S + MELT.G_S = 3.65 s, so the phases are
#   gather 15.00 -> 15.75, ball 15.75 -> 16.375, weight 16.375 -> 17.525, splash 17.525 -> 18.65
# and the four instants read as frames are the gather's midpoint (the base), the point, mid-bloom and the landed
# plate. E99 s34: `gather` is authored HERE and nowhere near the approved Japan short.
MELT_GATHER_S = 3.65
MELT_GATHER_EXIT = "melt:gather:weight:splash:plate"


def melt_gather() -> tuple[dict, dict]:
    """P61 T6 - THE GATHER, AND THE SPLASH INTO A WORLD PLATE (proof A of the card r26-76-melt-endings-in-motion).

    Scene 1 is `melt_page`'s own line page, given the whole 15 s to draw itself, so what gathers is a chart that has
    been read. Scene 2's world is the committed dock plate and its `exit` is the melt, so - E47, an exit names the
    transition INTO the scene it sits on - the gather takes scene 1's chart ink as scene 2 begins and the plate is
    what grows through the splatter. No cut anywhere: the plate is on the board as the bloom clears."""
    import build_scene_timeline_f as BST
    assert BST.melt_gather(MELT_GATHER_EXIT), MELT_GATHER_EXIT     # the COMPILER's own grammar, not a hand-written string
    assert BST.melt_ending(MELT_GATHER_EXIT) == "splash:plate", MELT_GATHER_EXIT
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    page["exit"] = "cut"   # LEDGER_EXITS / E40 #5, R26-60: NO RETRACT - the melt is how this chart leaves
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, MELT_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"asset_id": "plate-dock", "sha256": "0" * 64,
                                            "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": MELT_GATHER_EXIT, "span": [MELT_CUT, RUNTIME], "docks": [], "species": []}]
    uris = _base_uris()
    uris["plate-dock"] = BST.data_uri(DOCK_PLATE)   # the scenic, high-resolution world plate the ruling asks for
    return _timeline("Golden: the chart gathers to one dense vibrating point and splashes into a world plate",
                     scenes, {}, None), uris


SURFACES.update({   # P61 T6 / E99 s2: the gather, the point, the splash and the plate
    "melt-gather": melt_gather,
})
FRAME_T["melt-gather"] = 15.375   # THE GATHER at its midpoint (0.5 of 15.00 -> 15.75): the page's marks and words out
                                  # on the vortex's arms, each one turned along its own flow and part way to the point,
                                  # the board whole behind them - and not one blurred pixel (MELT.G_* / meltBlur = 0)


# ---- P61 T3 / R26-117: THE BALL BECOMES THE NEXT FULL CHART, and P48 T5b's PLANTED SOURCE ---------
# Two surfaces off one mechanism - `world.morph` is either the melt's own ball or a planted element's
# traced outline, and the arriving page cannot tell them apart.
#
# `melt-morph`   Scene 1 is `melt_page`'s own four-series line page, given the whole 15 s to draw itself, so what
#                melts is a chart that has been read. Scene 2's `exit` is `melt:morph` - E47, an exit names the
#                transition INTO the scene it sits on - so the melt takes scene 1's chart ink as scene 2 begins, the
#                ink balls up, and AT the ball the ring is handed to scene 2's page as the prop its `page_enter:morph`
#                deforms into the area under its own series. Scene 2 is a FULL dense-line chart of the same four
#                series over their LAST TWO YEARS - real data, a real sub-window of the same file, a different shape -
#                so what arrives is a whole chart built to T2/T2b's standard, its axes and labels written by the
#                engine's own hand as the build runs out of the morph. The exit declares no length, so the window is
#                MELT.S + MELT.M_S = 2.9 s from the cut: sag 15.00 -> 15.87, ball 15.87 -> 16.595, HAND 16.595 ->
#                17.90, and the page's own build from 17.90. E99 s34: `morph` is authored HERE and nowhere near the
#                approved Japan short.
# `morph-planted` The same page arriving by the same morph, from a PLANTED ELEMENT instead of a ball (P48 T5b /
#                R26-16: "a real element of the outgoing world at its last frame, never a shape conjured over the
#                clip"). Scene 1 is a narrative plate whose one dark form is PLANTED_BLOB below; scene 2's
#                `world.morph` is that form's own silhouette, traced off the same raster by our own marching squares
#                (kinetics/contour.mjs contourSilhouette), in stage fractions. Nothing is conjured: the poly is the
#                shape the frame held, and `test_melt_morph.py` re-traces it and refuses a drift.
MORPH_CUT = 15.0        # both surfaces hand over here, the cut every melt golden uses
MORPH_TAIL = 9          # the last N points of each series: scene 2's window, a real sub-window of the same file
MORPH_EXIT = "melt:morph"
# THE PLANTED ELEMENT, defined once and used twice: `png_planted` rasters it into the plate, and the node tracer
# rasters the same shape the same way and walks its 0.5 level. A star-shaped lobed blob - star-shaped so `polyStrip`
# describes it column by column without a fold, lobed so its silhouette is plainly not a circle or a named prop.
PLANTED_W, PLANTED_H = 320, 180
PLANTED_C = (144.0, 92.0)
PLANTED_R = 30.0


def planted_inside(x: float, y: float) -> bool:
    """Is image pixel-centre (x, y) inside the planted form? The tracer's own `inside`, to the digit."""
    dx, dy = x - PLANTED_C[0], y - PLANTED_C[1]
    th = math.atan2(dy, dx)
    r = PLANTED_R * (1 + 0.22 * math.cos(3 * th + 0.6) + 0.12 * math.sin(5 * th - 0.3))
    return math.hypot(dx, dy) <= r


def png_planted(w: int = PLANTED_W, h: int = PLANTED_H) -> bytes:
    """The PLATE that plants the element: a cream ground under a soft warm wash, with one dark lobed form on it."""
    ground, wash, ink = (238, 230, 214), (214, 200, 178), (46, 42, 44)
    raw = bytearray()
    for y in range(h):
        line = bytearray(b"\x00")
        for x in range(w):
            k = y / max(1, h - 1)
            c = tuple(int(ground[i] + (wash[i] - ground[i]) * k) for i in range(3))
            if planted_inside(x, y):
                c = ink
            line += bytes(c)
        raw += line

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


# THE POLY, traced - not drawn. Produced by `kinetics/contour.mjs contourSilhouette` over the bitmap
# `planted_inside` makes (320 x 180, the 0.5 level, Douglas-Peucker at 0.6 sample px), then carried out of sample
# space: sample (i, j) is the CENTRE of pixel (i, j), so the image fraction is ((i + 0.5)/W, (j + 0.5)/H), and a
# `.world` is inset -5% under `background-size: cover`, so the STAGE fraction is that * 1.1 - 0.05. Committed as a
# literal the way the newsreel headlines are, and `test_melt_morph.py` re-runs the tracer and refuses any drift.
PLANTED_BLOB = [[0.37281, 0.31361], [0.39859, 0.31056], [0.40203, 0.31667], [0.40891, 0.31667], [0.45703, 0.39],
                [0.46734, 0.39], [0.48797, 0.37167], [0.51891, 0.37167], [0.53266, 0.38389], [0.54469, 0.41139],
                [0.55156, 0.43583], [0.555, 0.46639], [0.56188, 0.48472], [0.56188, 0.50306], [0.56531, 0.50917],
                [0.56531, 0.55194], [0.56188, 0.55806], [0.56188, 0.57028], [0.54984, 0.59167], [0.53609, 0.60389],
                [0.52578, 0.60389], [0.52234, 0.61], [0.49141, 0.61], [0.47938, 0.6375], [0.47938, 0.65583],
                [0.46563, 0.71083], [0.43984, 0.75056], [0.41922, 0.75056], [0.39688, 0.71694], [0.38656, 0.68028],
                [0.38313, 0.64972], [0.37281, 0.61306], [0.36594, 0.60083], [0.35563, 0.55806], [0.35563, 0.5275],
                [0.3625, 0.49694], [0.3625, 0.4725], [0.35906, 0.46639], [0.35906, 0.44806], [0.35219, 0.4175],
                [0.35219, 0.35639], [0.35563, 0.35028], [0.35563, 0.33806]]
MORPH_KINETICS = {"arap_morph": True, "min_jerk": True}   # the morph and its clock. `arap_morph` is what P47 T3 put the
#   page-enter morph behind and `build_kinetics` turns on for every compiled timeline; `min_jerk` is the morph's own
#   clock (paintMorph: minJerk under the flag, expoOut without it, and expoOut is 93 % done by the halfway frame, which
#   would make every mid-morph proof a frame of the finished shape). Nothing else - the melt's ball is `melt-page`'s.


def _morph_target_page(field: str | None = None) -> dict:
    """Scene 2's FULL chart: the same four series over their last MORPH_TAIL points - a real sub-window."""
    raw = json.loads(SERIES.read_text(encoding="utf-8"))
    tail = {"title": "The same four, their last two years", "sub": raw.get("sub", ""), "src": raw.get("src", ""),
            "unit": raw.get("unit", ""),
            "series": [dict(sr, pts=sr["pts"][-MORPH_TAIL:]) for sr in raw["series"]]}
    page = LPG.build_spec(tail, "line", None, "right")
    # P61 T3b / E99 s52 - THE FIELD. A PLANTED morph page names none, so `stamp_transition_pages` stamps the soak
    # on it: the ground has to arrive, and the entry it arrives by is the one a prop that is already ink spreads
    # out of. A HANDED page names scene 1's own field, because its board NEVER LEFT (E88: a melt takes the chart's
    # ink and leaves the board) - the field it carries is the board it is continuing, and saying anything else
    # would swap the layer under an unchanged board. Before T3b every morph page said `scribble` and none of it
    # was read: `b` was pinned to 1, so the board was the finished rect on the page's first frame.
    if field is not None:
        page["field"] = field
    return page


def melt_morph() -> tuple[dict, dict]:
    """P61 T3 / R26-117 - THE BALL BECOMES THE NEXT FULL CHART, on one clock, with no cut between."""
    import build_scene_timeline_f as BST
    assert BST.melt_ending(MORPH_EXIT) == "morph", MORPH_EXIT     # the COMPILER's own grammar, not a hand-written string
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    page["exit"] = "cut"   # LEDGER_EXITS / E40 #5, R26-60: NO RETRACT - the melt is how this chart leaves
    page2 = _morph_target_page(page["field"])   # the HANDED page carries scene 1's own field: its board never left
    page2["enter"] = "morph"   # what _melt_boundary stamps on this boundary, written out so the fixture says it
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, MORPH_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": MORPH_EXIT, "span": [MORPH_CUT, RUNTIME], "docks": [], "species": []}]
    BST.stamp_transition_pages(scenes)   # the compiler's own boundary rules run over the fixture, refusals and all
    tl = _timeline("Golden: the melt's ball becomes the next full chart", scenes, {}, None)
    tl["kinetics"] = dict(MORPH_KINETICS)
    return tl, _base_uris()


def morph_planted() -> tuple[dict, dict]:
    """P48 T5b / R26-16 - THE PLANTED SOURCE: the page morphs out of a real element of the world before it."""
    import build_scene_timeline_f as BST
    err = BST.morph_poly_error(PLANTED_BLOB, "morph-planted: world.morph")
    assert err is None, err     # the COMPILER's own three refusals run over the fixture before it is written
    page2 = _morph_target_page()
    page2["enter"] = "morph"
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-planted", "sha256": "0" * 64,
                                            "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, MORPH_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "morph": {"poly": PLANTED_BLOB},
                                            "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [MORPH_CUT, RUNTIME], "docks": [], "species": []}]
    BST.stamp_transition_pages(scenes)
    uris = _base_uris()
    uris["plate-planted"] = uri("image/png", png_planted())
    tl = _timeline("Golden: the page morphs out of a planted element's own silhouette", scenes, {}, None)
    tl["kinetics"] = dict(MORPH_KINETICS)
    return tl, uris


SURFACES.update({   # P61 T3 / E99 s1, s34, s39: the hand-over, and the planted source it shares its door with
    "melt-morph": melt_morph,
    "morph-planted": morph_planted,
})
FRAME_T["melt-morph"] = 16.60      # THE HAND-OVER FRAME, 0.005 s past it: the ball finished and the page's morph at
                                   # u ~ 0.004 - the ring is the prop, the prop is the ring, and the page's own ink
                                   # has not begun to rise under it (hk = u / MELT.M_FADE)
FRAME_T["morph-planted"] = 15.02   # THE SOURCE AS PLANTED, u 0.01 of MORPH.S (2.0 s from the cut at 15.0): the traced
                                   # silhouette standing on the page's board exactly where the plate's own dark form
                                   # stood one frame earlier - same place, same size, same lobes (R26-16)


# P61 T6 proof B (E99 s2, HG6) - THE GATHER INTO A FULLY ASSEMBLED CHART. E99 s2 asks for two landings, *"a
# scenic, high-resolution world plate or fully assembled chart"*; T6 shipped the first (`melt-gather`, the dock
# plate) and left the second owed on `r26-76-melt-endings-in-motion` until T3 could build a full chart to land in.
# The two COMPOSE BY CONSTRUCTION: `gather` is a PHASE token and `morph` an ENDING, read in different branches of
# the same two parsers, so `melt:gather:morph` needs no new code at all - the page's marks travel the vortex and
# amass on the point, and the point is then handed to the next page as its prop and becomes the chart.
# Its own surface rather than a `melt-gather@proof-*` key, because a proof frame rides ITS SURFACE's timeline and
# `melt-gather`'s exit is `melt:gather:weight:splash:plate` - a different landing is a different exit string.
# Window: MELT.S + MELT.G_S + MELT.M_S = 3.8 s from the cut - gather 15.00 -> 16.14, point 16.14 -> 17.09,
# HAND 17.09 -> 18.80, and the page's own build from there.
GATHER_MORPH_EXIT = "melt:gather:morph"


def melt_gather_morph() -> tuple[dict, dict]:
    """P61 T6 proof B - the gather amasses into ONE point and that point becomes the next FULL chart."""
    import build_scene_timeline_f as BST
    assert BST.melt_gather(GATHER_MORPH_EXIT) and BST.melt_ending(GATHER_MORPH_EXIT) == "morph", GATHER_MORPH_EXIT
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    page["exit"] = "cut"
    page2 = _morph_target_page(page["field"])   # the HANDED page carries scene 1's own field: its board never left
    page2["enter"] = "morph"
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, MORPH_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": GATHER_MORPH_EXIT, "span": [MORPH_CUT, RUNTIME], "docks": [], "species": []}]
    BST.stamp_transition_pages(scenes)
    tl = _timeline("Golden: the melt gathers to one point and that point becomes the next full chart", scenes, {}, None)
    tl["kinetics"] = dict(MORPH_KINETICS)
    return tl, _base_uris()


SURFACES.update({"melt-gather-morph": melt_gather_morph})
FRAME_T["melt-gather-morph"] = 15.57   # THE GATHER at its own midpoint (15.00 -> 16.14): the four series curled
                                       # into one spiral converging on the point, the page's words streaming in
                                       # after them - T6's own mechanism, now on its way to a CHART. Its point
                                       # and the chart it becomes ride PROOF_FRAMES.


# ---- P72 T24: THE MORPH'S TWO UNTESTED GOLDENS (R26-148, R26-152) --------------------------------------------------
# `melt-morph-two-inks` (R26-148) - `melt-morph` with ONE difference: the arriving page's area is the series the row
#                names (`world.morph_series` 1, R26-149's key - the compiler's own page check runs over it), so the ball
#                is painted in the OUTGOING chart's own inks (the melt's mix of all four marks) and hands its ring to an
#                area in the INCOMING series' teal, not the crimson the one-file goldens always carried on both sides.
#                Judged half way through the hand (17.25, `melt-morph@proof-050`'s instant): the one shape carrying
#                both paints, the only frame a hue change as well as an alpha one could show.
# `morph-planted-plates` (R26-152) - `morph-planted` with ONE difference: the arriving page names `field: plates` (E99
#                s35's continuity field, the two generated plates `_two_plate_page` puts on a page), so its ground
#                arrives as the inked plate cross-fading over the blank one on the morph's own ground clock (`b`,
#                MORPH.GROUND of the 2.0 s), under the planted prop - where the soak spreads out of the splotch.
#                Judged at 15.15, a tenth of the ground's window: the inked plate half over the cream (expoOut 0.5).
TWO_INKS_SERIES = 1   # the teal series (SEMICONDUCTOR STOCKS) - the page's second, a different ink from scene 1's first


def melt_morph_two_inks() -> tuple[dict, dict]:
    """P72 T24 / R26-148 - the ball hands its ring to a page whose area is a DIFFERENT ink from the chart it left."""
    import build_scene_timeline_f as BST
    tl, uris = melt_morph()
    page2 = tl["scenes"][1]["world"]["page"]
    err = BST.morph_series_page_error(page2, TWO_INKS_SERIES, "melt-morph-two-inks: s02")
    assert err is None, err     # the COMPILER's own refusal for `morph_series` runs over the fixture before it is written
    assert page2["series"][TWO_INKS_SERIES]["color"] != tl["scenes"][0]["world"]["page"]["series"][0]["color"]
    tl["scenes"][1]["world"]["morph_series"] = TWO_INKS_SERIES
    tl["title"] = "Golden: the melt's ball becomes the next full chart in another series' ink"
    return tl, uris


def morph_planted_plates() -> tuple[dict, dict]:
    """P72 T24 / R26-152 - the planted morph page whose ground arrives by the two-plate cross-fade."""
    import build_scene_timeline_f as BST
    tl, uris = morph_planted()
    page2 = tl["scenes"][1]["world"]["page"]
    _two_plate_page(page2, uris)
    page2["field"] = BST.page_field_spec("plates", page2, "morph-planted-plates: s02")   # the COMPILER's own refusal
    tl["title"] = "Golden: the page morphs out of a planted element over the two-plate ground"
    return tl, uris


SURFACES.update({"melt-morph-two-inks": melt_morph_two_inks, "morph-planted-plates": morph_planted_plates})
FRAME_T["melt-morph-two-inks"] = 17.25    # HALF WAY THROUGH THE HAND (16.595 -> 17.90). Since P72 T23 / R26-389 the page's
                                          # teal has TAKEN the ball's orange by now (a front across the ball, never a mix):
                                          # the one shape in the page's ink, the ball's paint still fading over the area
FRAME_T["morph-planted-plates"] = 15.15   # a TENTH of the ground's 1.5 s: the inked plate half over the blank one


# ---- P58 T6 (c): THE SLIDE THROUGH THE DEPTH -----------------------------------------------------
# E98 s4: *"the docks, the ball and the slide move THROUGH the depth"*. The two pages are `slide-mid`'s own, and the
# two things added are `melt-depth`'s: a card that lands on the outgoing page and the one focus zoom tied to that
# landing (E51/E59 - under a LOCKED camera a depth has nothing to multiply, and nothing here was added to make the
# parallax visible, E49). The exit then names the two planes: `slide:left:depth=0.85,1.15` - the outgoing board
# recedes to the far side of the plate as it leaves, the incoming one arrives from in front of it.
SLIDE_DEPTH_K = (0.85, 1.15)


def slide_depth(exit_id: str | None = None) -> tuple[dict, dict]:
    """P58 T6 (c) - THE SLIDE THROUGH THE DEPTH: `slide:left:depth=0.85,1.15`, and nothing else.

    `@proof-mid` (SLIDE_CUT + SLIDE_S / 2) is the seam on the centre line with the eye moving: the outgoing board at
    0.925 of the move, the incoming at 1.075. The base frame is the LANDING (u = 1), which is the flat slide's own
    landing bit for bit - `exit_id` lets the test build the same surface with the flat `slide:left` to prove it."""
    import json as _json
    import build_scene_timeline_f as BST
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    page["exit"] = "cut"   # LEDGER_EXITS / E40 #5: no retract - the slide is how this chart leaves
    raw = _json.loads(SERIES.read_text(encoding="utf-8"))
    bars = {"title": "Where the four lines end", "sub": "index at the last point, 100 = Aug '25", "src": raw.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, short in zip(raw["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}
    page2 = LPG.build_spec(bars, "bars", None, "right")
    page2["field"] = "scribble"
    page2["enter"] = "axes"   # what stamp_transition_pages writes on this boundary
    P = MELT_DEPTH_PLACE
    species = [{"kind": "focus_zoom", "at": MELT_DEPTH_AT, "dur": MELT_DEPTH_DUR,
                "target": {"kind": "region", "x0": P["x"] / 1920, "y0": P["y"] / 1080,
                           "x1": (P["x"] + P["w"]) / 1920, "y1": (P["y"] + P["h"]) / 1080}}]
    dock = BST.dock_entry("ev-slide-card", 0, MELT_DEPTH_CARD, SLIDE_CUT, 1, BST.DOCK_KIND_IMAGE, P, "land")
    ev = {"ev-slide-card": {"title": "The card the eye goes to", "source": "P58 T6", "species": "deck",
                            "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:1]}}
    if exit_id is None:
        exit_id = "slide:left:depth=" + ",".join(f"{k:g}" for k in SLIDE_DEPTH_K)
        assert BST.slide_depth(exit_id) == SLIDE_DEPTH_K, exit_id   # the COMPILER's own grammar
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, SLIDE_CUT], "docks": [dock], "species": list(species)},
              {"scene_id": "s02", "world": {"kind": "ledger", "page": page2, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": exit_id, "span": [SLIDE_CUT, RUNTIME], "docks": [], "species": list(species)}]
    BST.stamp_transition_pages(scenes)   # the boundary refusals a build runs (a depth page / a layered plate)
    uris = _base_uris()
    uris["ev-slide-card"] = uri("image/png", png_solid(600, 375, (23, 105, 194)))
    tl = _timeline("Golden: the next chart pushes this one off, through the depth", scenes, ev, None)
    tl["kinetics"] = {"camera": True}   # E59's own module drives the move (camNow), as on melt-depth
    return tl, uris


SURFACES.update({   # P58 T6 (c): the slide whose two boards move through the depth
    "slide-depth": slide_depth,
})
FRAME_T["slide-depth"] = SLIDE_CUT + SLIDE_S   # THE LANDING (u = 1): the flat slide's own landing, bit for bit


# ---- E98 s7 / R26-134: THE EVIDENCE DOOR ---------------------------------------------------------------------
# The operator, 2026-09-14: *"zoom in or cut-in on to the tariff bill card all the way flat so its just like a regular
# plate, then we open that door and behind it is the vault plate."* A FLAT chart page - the line page every other golden
# is built from, standing as a plate after its 15 s build - and at DOOR_CUT the transition INTO scene 2 is `door`: the
# page swings open on its LEFT edge, away from the viewer, onto `melt-plate`'s own painted plate mounted beneath it.
DOOR_CUT = 15.0
DOOR_S = 0.9    # build_scene_timeline_f.DOOR_S and kinetics/transitions.mjs DOOR.S


def door_open() -> tuple[dict, dict]:
    """E98 s7 - THE EVIDENCE DOOR: `door` (hinge left, 0.9 s), and nothing else.

    The compiler's own boundary pass runs on the two scenes (stamp_transition_pages): the door takes the world, so the
    outgoing page is stamped exit=cut (it swings away with its chart on it and never retracts first), and the flat page
    passes the door's refusals (no depth=, no plane=, no dock across the boundary). The instants: `@proof-early` (u 0.25)
    and `@proof-mid` (u 0.5) on PROOF_FRAMES, and the base frame at the door's LENGTH (u = 1: edge-on, the plate alone)."""
    import build_scene_timeline_f as BST
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    still = {"scale": 0, "x": 0, "y": 0}
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": dict(still)},
               "exit": "cut", "span": [0.0, DOOR_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"asset_id": "plate-melt", "sha256": "0" * 64, "ken_burns": dict(still)},
               "exit": "door", "span": [DOOR_CUT, RUNTIME], "docks": [], "species": []}]
    assert BST.parse_exit("door") == ("door", None) and BST.door_hinge("door") == "left"   # the COMPILER's own grammar
    BST.stamp_transition_pages(scenes)
    assert page["exit"] == "cut", page.get("exit")
    uris = _base_uris()
    uris["plate-melt"] = uri("image/png", png_scene(320, 180))   # melt-plate's painted plate - an existing golden input
    return _timeline("Golden: the flat chart opens like a door onto the plate behind it", scenes, {}, None), uris


SURFACES.update({   # E98 s7: the door's landing (its two moving instants ride render_baseline.PROOF_FRAMES)
    "door-open": door_open,
})
FRAME_T["door-open"] = DOOR_CUT + DOOR_S   # u = 1: edge-on, the plate alone - the plain cut's frame at this instant


# ---- R26-133: A PLATE WORLD AT ITS `drift` IDLE ------------------------------------------------
# The smallest surface that can answer the operator's question ("Plate idle should probably paint, but would have
# to see what it looks like", 2026-09-14): ONE plate world, nothing docked, nothing drawn over it, no caption - a
# COMMITTED photographic plate (the Tokyo customs dock `camera-layers` splits into planes, read flat here) authored
# `idle: "drift"`. HELD and PAINTED are the SAME source: only the `plate_idle_paints` dial differs between the two
# renders, so the pair proves the dial and nothing else. The captions are cleared on purpose - a caption page moving
# over the plate is the one motion the eye must NOT be reading while it judges a 2 px walk (E49's DRIFT_PX).
# The `idle` flag is ON in the source because without it `idleOf` returns "none" and there is no idle to paint at
# all (the engine's IDLE_CLASS / idleOf); the flag alone still renders a still plate - that is the HELD frame.
PLATE_DRIFT_RUNTIME = 4.0   # a short hold: the four proof frames are its seconds 0, 1, 2, 3
PLATE_DRIFT_PX = 20.0       # E99 s63: the named LONG-FORM amplitude, amending s55's 30 ("30 px drift might still be too much, maybe 20 px drift"); 30-40 is the shorts range - build_scene_timeline_f.PLATE_DRIFT_LONG


def plate_drift() -> tuple[dict, dict]:
    """R26-133, re-authored by P61 T14 to the ruling that CLOSED it (E99 s55) and re-cut by T14b to the ruling that
    AMENDED it (E99 s63): a plate authored `;idle=drift`, the dial PAINTING it, at the amplitude the operator named
    on the watch - `;drift=20`, the long-form setting ("also 30 px drift might still be too much, maybe 20 px
    drift"). 30-40 is the shorts range; the difference clip at 30 is the beat's second timeline, not this golden.

    What the first pin proved and E99 s38 then refused: at IDLE.DRIFT_PX (2.0) the walk is 2.3 px of excursion at
    about eight frames per pixel, and the operator could not judge it - *"i don't even notice it while i'm watching
    ... it's not realy a visible shift"*. So the dial the cure needed was never the boolean alone; it is the
    AMPLITUDE, and it is authored per scene. At 30 the same walk - the same two rates, the same Lissajous, so it can
    never become jitter - moves the whole plate about seven px a second.

    `drift` opens at [0, 0] and walks +-`idle_drift_px` in x, +-0.6 of it in y, on two rates whose common period is
    100 s, so four seconds carries four different poses and none of them repeats. Judged at 2.0 - a second clear of
    the rest it opens from (FRAME_T)."""
    import build_scene_timeline_f as BST
    aid = "plate-drift"
    scenes = [{"scene_id": "s01",
               "world": {"asset_id": aid, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0},
                         "idle": "drift", "idle_drift_px": PLATE_DRIFT_PX},
               "exit": "cut", "span": [0.0, PLATE_DRIFT_RUNTIME], "docks": [], "species": []}]
    uris = _base_uris()
    uris[aid] = BST.data_uri(DOCK_PLATE)      # the same committed input camera-layers reads, flat
    tl = _timeline("Golden: a plate world at its drift idle, 20 px", scenes, {}, None)
    tl["runtime_s"] = PLATE_DRIFT_RUNTIME
    tl["captions"], tl["caption_pages"] = [], []   # nothing on the stage but the plate
    # E49's switch, and E99 s55's two: the walk PAINTS (R26-133's cure) at the authored amplitude. The amplitude is
    # on the WORLD, not here - `plate_idle_drift_px` in the kinetics map is the build-wide fallback, and this golden
    # authors the row's own so the pair reads the grammar an episode actually writes.
    tl["kinetics"] = {"idle": True, "plate_idle_paints": True}
    return tl, uris


SURFACES.update({   # R26-133: the drift plate, held (this source) and painted (the `plate_idle_paints` dial)
    "plate-drift": plate_drift,
})
FRAME_T["plate-drift"] = 2.0


# ---- P61 T14 / E99 s55: THE ALIVE PLATE, WITH THE WHOLE DEPTH STACK OVER IT ---------------------
# The operator, 2026-09-16, closing R26-133: *"i think we need both the drift painted as an option and the alive.
# Maybe we need the ken burns + alive or parallax+ alive or maybe we need a slightly smaller drift (maybe 30 px?)
# AND the alive water."* - and, when the drift lane's three-way proof had run VACE over the flat still alone:
# *"when you ran vace did you also run the rest of our depth stack etc?"* It had not. This surface is the answer,
# and it is a COMPOSITION of four things the record already holds, not a new mechanism:
#   CAPABILITIES:143  the mask-pinned ambient lane - the harbour water, generated (Wan 2.1 VACE 1.3B), pinned to
#                     the still outside its own mask, here re-composited over the depth split's `-far` layer so the
#                     alive region IS the background wall
#   CAPABILITIES:145-146  the layered plate and its sidecar - the mid containers, the clerk's desk, the hanging
#                     lamp, the same four planes `camera-layers` reads, over that wall
#   CAPABILITIES:147  the camera over layers - ONE authored move, each plane at its own k, and the move has the
#                     only reason E51 allows: a card LANDS on the quay and the eye goes to it
#   E99 s55 / s63 / E49  the drift, painted, at 20 px (s63 amended s55's 30 on the watch) - the plate's own idle,
#                     shared per plane at its own share of k
# The frame is judged at the instant where BOTH halves of the claim are on screen: the water has moved off its
# first frame AND the near planes have led the far one. Nothing here is a fixture: it is a beat a short could carry.
DOCK_ALIVE = HERE / "inputs" / "dock-alive"
ALIVE_PLATE = DOCK_ALIVE / "world-tokyo-customs-dock-v1-alive.png"   # the committed input set, as `camera-layers` reads dock-layers
PLATE_ALIVE_RUNTIME = 10.0
PLATE_ALIVE_T = 6.56   # u 0.28 of the focus zoom (the instant `camera-layers@proof-mid` reads the parallax at), and 2.50 s into the water's own loop


def plate_alive() -> tuple[dict, dict]:
    """P61 T14 / E99 s55 - THE ALIVE PLATE: a layered plate whose BACKGROUND WALL is a clip, with the parallax
    planes, the one camera and the 20 px drift composing over it (E99 s63 amended s55's 30 on the watch).

    The plate is `world-tokyo-customs-dock-v1-alive` - the same Tokyo customs dock every layered golden reads, its
    `-far` layer replaced by the ambient lane's generated harbour water (everything outside the life mask is that
    committed layer, pixel for pixel). The mid / subject / occluder planes are the flat plate's own.
    """
    import build_scene_timeline_f as BST
    aid = "plate-alive"
    planes = BST.plate_depth_planes(ALIVE_PLATE)
    layers = [{"key": f"{BST.LY_PREFIX}{aid}:{p['role']}", "k": p["depth"], "role": p["role"],
               **({"clip": True} if p.get("clip") else {})} for p in planes]
    dock = BST.dock_entry("ev-quay-card", 0, CAMERA_LAYERS_ENTER, PLATE_ALIVE_RUNTIME, 2, BST.DOCK_KIND_IMAGE,
                          CAMERA_LAYERS_PLACE, "land")
    ev = {"ev-quay-card": {"title": "The card the eye goes to", "source": "P61 T14", "species": "deck",
                           "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:2]}}
    P = CAMERA_LAYERS_PLACE
    species = [{"kind": "focus_zoom", "at": CAMERA_LAYERS_AT, "dur": CAMERA_LAYERS_DUR,
                "target": {"kind": "region", "x0": P["x"] / 1920, "y0": P["y"] / 1080,
                           "x1": (P["x"] + P["w"]) / 1920, "y1": (P["y"] + P["h"]) / 1080}}]
    scenes = [{"scene_id": "s01",
               "world": {"asset_id": aid, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0},
                         "idle": "drift", "idle_drift_px": PLATE_DRIFT_PX, "layers": layers},
               "exit": "cut", "span": [0.0, PLATE_ALIVE_RUNTIME], "docks": [dock], "species": species}]
    uris = _base_uris()
    uris[aid] = BST.data_uri(ALIVE_PLATE)                    # the flat still the compiler always embeds (unpainted: the planes ARE the picture)
    for pl, ly in zip(planes, layers):
        uris[ly["key"]] = BST.data_uri(Path(pl["file"]))     # RAW - the alpha IS the plane, and an mp4 is embedded whole
    uris["ev-quay-card"] = uri("image/png", png_solid(640, 400, (23, 105, 194)))
    tl = _timeline("Golden: the alive plate under the whole depth stack", scenes, ev, None)
    tl["runtime_s"] = PLATE_ALIVE_RUNTIME
    tl["captions"], tl["caption_pages"] = [], []             # nothing on the stage but the plate and the card it is judged by
    tl["kinetics"] = {"idle": True, "plate_idle_paints": True, "camera": True, "stop_action": True}
    return tl, uris


SURFACES.update({   # P61 T14 / E99 s55: the alive wall, the planes, the camera and the drift, composing
    "plate-alive": plate_alive,
})


# ---- R26-228 / E99 s82 (e): THE PAGE'S INTERIOR AT ITS IDLE --------------------------------------
# The operator, 2026-09-18, on frozen copy d: *"You also missed the sparking lead points from the line chart
# reference, which add chart life ... our chart lines have no glow/pulse ... We also have no ken burns or drift or
# life/breathing going on"*, and the ruling drawn from it: *"LIFE IS SEEN, NOT PASSED: a page's `idle=live` must
# render the tip spark (E67's live ink), the line's glow/pulse and the labels' breath"* (OPERATOR-RULINGS:3286).
# The pair below is ONE key apart - `world.idle` absent against `"live"` - and it is the whole of R26-228's proof:
#   * the STILL half is the page every cut has drawn. The row's `;idle=live` was written as `world["idle"]` by the
#     compiler and read as `world.page.idle` by the engine, a key nothing writes, so every page in every cut has
#     held at IDLE_CLASS.page ("breath"): ONE rigid scale about the page's centre, the drift half writing
#     translate(0.00px,0.00px) at every t (measured at both aspects - tests/R26-228-NOTE.md).
#   * the LIVE half is the same page with the kind the row authored: the lead point STAYS at the drawn end of each
#     live series and sparks, and the stroke's glow is the share of the frame the approved 9:16 page draws, pulsing
#     on the tip's own clock. R26-234 / E99 s83 took the fourth life away: the title, sub, citation, tick labels and
#     end tags no longer walk at their own phases - *"remove the interior drift, keep the electric/glow etc let that
#     carry the life instead of drift which just reads as chaos"* - so the only thing that separates the halves
#     INSIDE the page is the electric, and the only thing that separates them at all besides it is the page's own
#     exterior drift (`live` = breath + drift). That is what the pair's bands are read against in
#     `test_golden_frames.test_the_live_page_keeps_its_electric_and_holds_its_words_still`: every band, word or
#     electric, fits the SAME page-wide offset, and only the electric bands carry a difference no offset explains.
# `ken_burns` is ZERO on both, so the world contributes nothing and the pair isolates the page's own life; the
# instants are the page LANDED (the state the divergence page holds for ~45 of its 54.9 s) and the same page 2 s
# later - the two tiles the ruling asks a life to be visible across.
PAGE_LIFE_T = 9.0     # roll + savor + field 3.9 + punch 0.5 + build 3.0 = 7.4: every series drawn and standing
PAGE_LIFE_T2 = 11.0   # ... and 2 s on (render_baseline.PROOF_FRAMES carries this half of each pair)


def _page_life(idle: str | None) -> tuple[dict, dict]:
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    world: dict = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    if idle:
        world["idle"] = idle
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    tl = _timeline("Golden: the page's interior at its idle", scenes, {}, None)
    tl["kinetics"] = {"idle": True}   # E49 is ON for every compiled timeline; a golden source has to say so (`plate-drift` says the same), and `idleOf` answers "none" when it does not
    return tl, _base_uris()


def page_life_still() -> tuple[dict, dict]:
    """R26-228 - the STILL half: no `world.idle`, so the page holds at the class default and nothing inside it moves
    against anything else. This is the frame the operator read as dead."""
    return _page_life(None)


def page_life_live() -> tuple[dict, dict]:
    """R26-228 - the LIVE half: `world.idle = "live"`, the kind the shot row authors and the engine never read."""
    return _page_life("live")


SURFACES.update({   # R26-228 / E99 s82 (e): the page's interior, still and live - one key apart
    "page-life-still": page_life_still,
    "page-life-live": page_life_live,
})
FRAME_T["page-life-still"] = PAGE_LIFE_T
FRAME_T["page-life-live"] = PAGE_LIFE_T


# ---- R26-226 / E99 s82: A MULTI-LINE PAGE BUILDS LINE BY LINE -------------------------------------
# The same four-series page `page-life-*` and `ledger-page-mid-build` draw, with the ROW's build mode on it:
# `;build=lines:1.2` (`build_scene_timeline_f.page_build_spec`, which writes exactly the two keys below - the
# mode and the page's whole build, 4 x 1.2 s). Series 0 draws over 4.4-5.6, series 1 over 5.6-6.8, series 2
# over 6.8-8.0 and series 3 over 8.0-9.2, each WHOLE, its end tag and inline badge chip landing with it.
# `idle: "live"` is on the row because the ruling's own next line is the lead point that STAYS on a landed
# live line (R26-228): the frame is the sequence AND what each landed line keeps.
PAGE_BUILD_LINES_S = 1.2       # one SERIES' seconds, as the row authors them
# The two instants, MEASURED not guessed: the build's easing is `expoOut` (the pen law `strokeFrac` answers null
# unless `curvature_stroke` is on) and it is heavily front-loaded - at HALF of a series' own window the line is
# already 96.9 % drawn (1 - 2^-5; measured on the served page, dashoffset 37 of 1183). A line reads as DRAWING at
# u = 0.125 of its window, 1 - 2^-1.25 = 0.580 of its length, which is 0.15 s into a 1.2 s series window.
PAGE_BUILD_LINES_T = 5.75      # inside SERIES 1's window (5.6-6.8): series 0 landed and tagged, series 1 0.58 drawn
                               # with no tag, series 2 and 3 not begun - the ruling in one frame
PAGE_BUILD_LINES_T4 = 8.15     # inside SERIES 3's window (8.0-9.2): three lines landed and tagged, the fourth drawing


def _page_build_lines() -> tuple[dict, dict]:
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", 0, "right")
    page["build"] = "lines"      # the two keys the token writes; test_page_builds_line_by_line pins them to the compiler
    page["build_s"] = round(PAGE_BUILD_LINES_S * len(page["series"]), 3)
    world = {"kind": "ledger", "page": page, "idle": "live", "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    tl = _timeline("Golden: the page builds line by line", scenes, {}, None)
    tl["kinetics"] = {"idle": True}   # as `page-life-live`: E49 is on for every compiled timeline, and a source says so
    return tl, _base_uris()


def page_build_lines() -> tuple[dict, dict]:
    """R26-226 - at SERIES 1's midpoint: line 1 whole and labelled, line 2 half drawn, lines 3 and 4 not begun."""
    return _page_build_lines()


def page_build_lines_4th() -> tuple[dict, dict]:
    """R26-226 - the same page at SERIES 3's midpoint: three lines whole and labelled, the fourth drawing.

    The same timeline as `page-build-lines`, read 2.4 s later. Two SURFACES rather than one surface and a
    second instant because a second instant of one surface lives in `render_baseline.PROOF_FRAMES`, which
    R26-226's write set does not include."""
    return _page_build_lines()


SURFACES.update({
    "page-build-lines": page_build_lines,
    "page-build-lines-4th": page_build_lines_4th,
})
FRAME_T["page-build-lines"] = PAGE_BUILD_LINES_T
FRAME_T["page-build-lines-4th"] = PAGE_BUILD_LINES_T4
FRAME_T["plate-alive"] = PLATE_ALIVE_T


# ---- R26-233 / E99 s82: THE AXIS YIELDS TO THE LINE THAT PUSHES IT -------------------------------
# The H unit's own shape, on a page of its own so the claim is readable in one frame: THREE lines that
# land on the scale the page is born on (`;domain=80,320`, R26-223) and a FOURTH - "Memory" - held at
# nothing through the build by a `build_to` at index 0 (R26-226's own reading: a cap at 0 draws
# nothing) and then drawn WHOLE on its word, climbing to 600, far above the standing top. The reveal's
# `chart_to rescale` opens the domain to [80, 630] over that same window with `follow: "Memory"`, so
# the top is the drawn extremum x 1.06 frame by frame and the landed ink yields exactly as the climb
# passes 320 - never before it (the operator, E99 s82: *"the movement on screen drags down the values
# somehow at 0:05, that can't happen"*).
#   Both instants are INSIDE the followed line's own window, and both are measured: the cap runs on
# `segEase`, which is minimum-jerk here (the flag every compiled cut carries), so the climb is slow at
# each end and quickest in the middle. FOLLOW_T is the frame where the memory line is climbing and the
# domain has NOT begun to open - the landed lines standing exactly where they landed - and FOLLOW_T2 is
# mid-yield: the top opened by the line, the three tags lower, the low ticks still lit and re-spaced.
FOLLOW_ID = "ev-follow-v1"
FOLLOW_BORN = [80.0, 320.0]      # the scale the three landed lines are read on
FOLLOW_TARGET = [80.0, 630.0]    # ... and the one the memory line pushes to (600 x 1.06 = 636, so it reaches it)
FOLLOW_AT = 11.0                 # the word: the cap and the rescale open together
FOLLOW_S = 2.2                   # ... on ONE clock - the memory line's own draw (the H unit's own 2.2 s)
FOLLOW_OBJECT = {
    "title": "The layer it never drew",
    "sub": "index, 100 = the first period",
    "src": "the test bed",
    "unit": "",
    "series": [
        {"name": "Steel", "color": "crimson", "pts": [[2020, 100], [2021, 118], [2022, 132], [2023, 146], [2024, 150]]},
        {"name": "Paper", "color": "cobalt", "pts": [[2020, 100], [2021, 140], [2022, 175], [2023, 198], [2024, 210]]},
        {"name": "Rails", "color": "amber", "pts": [[2020, 100], [2021, 165], [2022, 205], [2023, 240], [2024, 260]]},
        {"name": "Memory", "color": "teal", "pts": [[2020, 100], [2021, 150], [2022, 205], [2023, 300], [2024, 600]]},
    ],
}
# the memory line held at nothing while the other three build (the first cap is the level the build lands
# at - never a draw), then drawn whole on its word. `follow_draw_windows` reads the SECOND cap alone.
FOLLOW_HOLD = {"kind": "build_to", "at": 4.4, "dur": 0.4, "series": 3,
               "target": {"kind": "datum", "index": 0, "series": 3}}
FOLLOW_DRAW = {"kind": "build_to", "at": FOLLOW_AT, "dur": FOLLOW_S, "series": 3,
               "target": {"kind": "datum", "index": 4, "series": 3}}
FOLLOW_RESCALE = {"kind": "chart_to", "at": FOLLOW_AT, "dur": FOLLOW_S, "to": "rescale",
                  "ymin": FOLLOW_TARGET[0], "ymax": FOLLOW_TARGET[1], "follow": "Memory"}
FOLLOW_T = 11.95    # MEASURED (tests/R26-233-NOTE.md): the memory line 0.374 drawn and climbing at 225, its extremum
                    # with the air (238.5) still under the standing top - the domain has not moved one pixel and the
                    # three landed lines' paths are byte-for-byte the ones they landed as
FOLLOW_T2 = 12.30   # ... and MID-YIELD (u 0.479): the climb at 385.6 asks for 408.7 and the live top IS 408.8 - the
                    # tip on screen because the ceiling gave way to it, the landed tag 33.8 px lower, all five ticks lit


def _page_rescale_follow() -> tuple[dict, dict]:
    import copy
    import json
    import tempfile
    import build_scene_timeline_f as BST
    plate = "ledger:%s:line;domain=%g,%g" % (FOLLOW_ID, FOLLOW_BORN[0], FOLLOW_BORN[1])
    species = [copy.deepcopy(e) for e in (FOLLOW_HOLD, FOLLOW_DRAW, FOLLOW_RESCALE)]
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / ("evidence/objects/%s.series.json" % FOLLOW_ID)).write_text(json.dumps(FOLLOW_OBJECT), encoding="utf-8")
        world = BST.world_for_plate(plate, (0, 0, 0), ep)
        BST.derive_rescale_states(world, species, plate, ep, sid="s01")   # the derived state AND `follow`'s own index
    world["ken_burns"] = {"scale": 0, "x": 0, "y": 0}   # nothing of the world moves: the frame is the page's own
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: the domain follows the line that pushes it", scenes, {}, None)
    tl["kinetics"] = {"idle": True, "min_jerk": True}   # both flags a compiled cut carries; `segEase` is the cap's clock
    return tl, _base_uris()


def page_rescale_follow() -> tuple[dict, dict]:
    """R26-233 - the followed rescale BEFORE the yield: the memory line drawing under the standing top, the three
    landed lines exactly where they landed, every tick of the born scale in its place."""
    return _page_rescale_follow()


def page_rescale_follow_yield() -> tuple[dict, dict]:
    """R26-233 - the same page MID-YIELD: the domain opened by the climb itself, the landed ink lower than it was
    and the low ticks still lit and re-spaced.

    The same timeline as `page-rescale-follow`, read 0.35 s later. Two SURFACES rather than one surface at two
    instants because a second instant of one surface lives in `render_baseline.PROOF_FRAMES`, which R26-233's
    write set does not include (R26-226's pair was split for the same reason)."""
    return _page_rescale_follow()


SURFACES.update({
    "page-rescale-follow": page_rescale_follow,
    "page-rescale-follow-yield": page_rescale_follow_yield,
})
FRAME_T["page-rescale-follow"] = FOLLOW_T
FRAME_T["page-rescale-follow-yield"] = FOLLOW_T2


# ---- P61 T9 (b): THE EFFECTS GALLERY'S OWN PAGE ------------------------------------------------
# The gallery is not a timeline. It is the static review page `build_effects_gallery.py` generates
# from docs/EFFECTS-CATALOG.jsonl, so it has no (timeline, uris) pair and it is deliberately NOT a
# member of SURFACES - render_baseline instantiates every one of those through the player template
# and would try to seek a #scrub the page does not have. What is committed beside the engine's
# sources is the RECIPE each page frame is captured by (the page, the viewport, the anchor), so the
# three frames can be re-taken on any checkout:
#     python content/video_engine/scripts/build_effects_gallery.py --pin
# The frames themselves live in tests/golden/frames/ with every other golden; the checker is
# content/video_engine/tests/test_effects_gallery.py, and test_golden_frames.py lists the three in
# PAGE_SURFACES beside SURFACES.
PAGE_SURFACES = ("gallery-top", "gallery-axis-kinetics", "gallery-foot")


def page_source(name: str) -> dict:
    """The capture recipe of one page frame, read off the builder itself so it can never drift."""
    import build_effects_gallery as BEG
    width, height = BEG.PIN_VIEWPORT
    return {"kind": "page",
            "page": "content/video_engine/effects/gallery/index.html",
            "built_by": "content/video_engine/scripts/build_effects_gallery.py",
            "built_from": "docs/EFFECTS-CATALOG.jsonl",
            "viewport": {"width": width, "height": height, "device_scale_factor": 1},
            "anchor": BEG.PIN_FRAMES[name],
            "settle_ms": BEG.PIN_SETTLE_MS,
            "capture": "build_effects_gallery.capture_frames",
            "refresh": "python content/video_engine/scripts/build_effects_gallery.py --pin",
            "pinned_without": ("the generated .mp4 motion examples (P61 T9 (c)) - a golden derives "
                               "from committed inputs only, and the gallery directory is gitignored; "
                               "the served page carries them on top of this"),
            "checked_by": "content/video_engine/tests/test_effects_gallery.py"}


def write_page_source(name: str) -> list[Path]:
    """Write ONE page frame's source - the recipe, beside the engine surfaces' timelines."""
    SOURCES.mkdir(parents=True, exist_ok=True)
    p = SOURCES / f"{name}.page.json"
    p.write_text(json.dumps(page_source(name), indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")   # R26-323: LF on every platform
    return [p]


# ---- P61 T2 / E99 s34 - THE WHOLE-CHART REMAKE, both ways round ---------------------------------
# One fixture read twice: six monthly prints of a level as a LINE, and the six bars that ARE those
# prints. The compiler derives the correspondence itself (`remake_mark_map`, keyed on `level`: bar k
# IS datum k), so these goldens prove the derivation, the mark map, the ring pairing and the painter
# together - exactly as `data-to-bars` does for E64's change key.
REMAKE_AT, REMAKE_S = 12.0, 2.4   # the row's own clock; the instants below are shares of it


BARS_N = 5   # the bars ARE the line's last five prints: a long line and a few bars is this family's own idiom (`data-to-bars` is 36 months -> 4)


def _remake_pages() -> tuple[dict, dict]:
    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    steps = [0.0, 9.4, -4.2, 12.1, -6.6, 5.3, 14.2, -9.9, 3.7, 11.4, -12.8, 6.9, 4.1, -7.3, 10.6]   # a level that wanders, month by month
    pts, v = [], 1180.4
    for i, s in enumerate(steps):
        v = round(v + s, 1)
        pts.append([round(2025 + i / 12, 4), v])
    tail = pts[-BARS_N:]
    line = {"title": "The pile, month by month", "sub": "holdings, $bn, monthly", "src": "Golden fixture",
            "unit": "$", "ylabel": "$bn",
            "series": [{"name": "Holdings", "label": "fifteen months", "color": "crimson", "pts": pts}]}
    bars = {"title": "Where it stood, month by month", "sub": "holdings, $bn, at each print",
            "src": "Golden fixture", "unit": "$",
            "bars": [{"label": months[int(round((pt[0] - int(pt[0])) * 12)) % 12], "value": pt[1], "color": "teal"}
                     for pt in tail]}
    return line, bars


def _remake(order: str) -> tuple[dict, dict]:
    """`order` is "line-to-bars" or "bars-to-line": which page the row STARTS on. Everything else - the
    fixture, the clock, the derivation - is the same, so the pair reads as one mechanism run both ways."""
    import json
    import tempfile
    import build_scene_timeline_f as BST
    line, bars = _remake_pages()
    first, second = ("line", "bars") if order == "line-to-bars" else ("bars", "line")
    species = [{"kind": "chart_to", "at": REMAKE_AT, "dur": REMAKE_S, "to": "remake", "state": 1}]
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td); (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/golden-level.series.json").write_text(json.dumps(line), encoding="utf-8")
        (ep / "evidence/objects/golden-prints.series.json").write_text(json.dumps(bars), encoding="utf-8")
        ids = {"line": "golden-level:line", "bars": "golden-prints:bars"}
        plate = f"ledger:{ids[first]};then={ids[second]}"
        world = BST.world_for_plate(plate, (0, 0, 0), ep)
        world["ken_burns"] = {"scale": 0, "x": 0, "y": 0}
        world["page"]["field"] = "soak"
        BST.derive_rescale_states(world, species, plate, ep, sid="s01")
    assert len(species[0].get("mark_map") or []) == BARS_N and species[0].get("keyed_on") == "level", species[0]
    assert species[0].get("line_at") == ("from" if first == "line" else "to"), species[0]
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline(f"Golden: remake {order}", scenes, {}, None), _base_uris()


def remake_line_to_bars() -> tuple[dict, dict]:
    """THE WHOLE-CHART REMAKE, line -> bars (P61 T2; the bar is E99 s34's two readings).

    The line page's six monthly data become the six bars that ARE them, on ONE clock: each datum's own
    column of the area under the line morphs into its bar (morph_a's pairing rule on two rings built
    column by column), the datum marks travel to their bars' tops, the axes hand over through
    lpAxisHandOver (never the whole-layer crossfade E99 s1 refused), every tick label and the page's
    TITLE are re-written by the hand that already re-writes a recast's labels, and a label that changes
    neither string nor place is held whole instead of being re-written for nothing.

    Judged at the morph's own half-way point (u 0.50): the instant a jump cannot fake - the line is
    gone into its columns, the bars have not been drawn, and what stands is six shapes that are neither.
    Its quarter and three-quarter instants ride PROOF_FRAMES."""
    return _remake("line-to-bars")


def remake_bars_to_line() -> tuple[dict, dict]:
    """THE OTHER RUN, re-choreographed by E99 s39 (P61 T2b) - bars -> line is NOT the twin read backwards.

    The operator: *"for bars-> line I'd like to see it all collapse to the single apex point and then draw
    the line back to the root instead of sliding and snapping together and the whole line is formed."* So
    every bar hands its rectangle to its ring, the rings COLLAPSE into one point at the apex (the highest
    bar's top, the farthest leaving first so they land together), the point carries itself to where the
    arriving line's own apex datum stands, and the page's own stroke DRAWS from there back to the root.

    Judged mid-GATHER (u 0.15): five rings in flight that are no longer the bars and are not yet the point -
    the frame the collapse cannot be faked at. Its other three beats ride PROOF_FRAMES, and @proof-050 is the
    ruling's own instant: the point, and a partial stroke."""
    return _remake("bars-to-line")


SURFACES.update({
    "remake-line-to-bars": remake_line_to_bars,
    "remake-bars-to-line": remake_bars_to_line,
})
FRAME_T["remake-line-to-bars"] = REMAKE_AT + 0.50 * REMAKE_S   # 13.2 - THE INVARIANT INSTANT: neither chart is drawable
# as itself there, so no cut can produce the frame (this run is E99 s39's "taken as built" half - untouched by T2b).
FRAME_T["remake-bars-to-line"] = REMAKE_AT + 0.15 * REMAKE_S   # 12.36 - P61 T2b: this run's own instant is MID-GATHER (the
# rings collapsing toward the apex). Its u 0.50 - the point and the partial stroke E99 s39 asks for - is pinned beside it
# as `remake-bars-to-line@proof-050`, so the two are four distinct frames over the three beats rather than one twice.




# ---- R26-20's other half / E99 s87: THE STAMPED PROP -------------------------------------------
# The operator, 2026-09-22: *"for props, it doesnt make sense to put them in a card, the whole point of a prop is
# for it to get added to the world; we would either stamp it or throw it on."* So the surface is a PROP - one of
# the 24 catalogued cutouts - landing BARE on a built ledger page by the ported badge-stamp arrival: the clamped
# scale spring settling while the free rotation spring is still unwinding under it, the impact ring on its split
# shock curves, and the exit E50 owes the landed mark (authored here, at 26.0, so the frame can prove it).
# WHERE it lands is the compiler's own answer, not a hand-written box: `stamp_dock_place`, the door the row loop
# calls (send-back #2), searching E65's room for the centre its ring fits round. `centre: True` holds it at that
# box from its first frame - a stamp never pops and slides to a park.
# THE INK IS THE OPEN QUESTION (E99 s87, the operator's own): the prop in its own colour, or laid down in the
# page's own ink the way a real impression would be. Both are surfaces here, identical in every other byte, so the
# two frames are a straight comparison and the operator picks on the frame.
# THE PICTURE IS A PROXY, for the reason the icon proxy is one (E99 s31: an approved cutout never enters git) -
# the same integer box filter, at a cap well under the drawn size, and it says so. A BUILD still embeds the
# full-resolution file through `catalogue_icon_uri` / `dock_uri`; this is a test fixture's proxy.
PROP_CUTOUT = REPO / "content/video_engine/assets/props/cutouts/prop-federal-reserve-building-v1.png"
PROP_PROXY_PX = 160         # the file is 282x259 RGBA; at cap 160 the integer factor is 2 and the proxy is 141x129
PROP_STAMP_ENTER = 10.0     # the page is built by ~7.4 s (ROLL+SAVOR+FIELD 3.9 + PUNCH 0.5 + BUILD 3.0), so the mark lands on a page that has been read
PROP_STAMP_EXIT = 26.0      # ... and it is told to leave here, on its own ease-IN cubic over STAMP_ARRIVAL.EXIT_S (0.5333 s)


def _prop_stamp(ink: str) -> tuple[dict, dict]:
    """R26-20 send-back #2: the stamp is placed by the COMPILER'S OWN DOOR, the one the row loop calls -
    `stamp_dock_place` - on the page a real 16:9 build compiles (`stamp_full_stage`, which is what makes the page
    report its measured end-name box), with the PICTURE's own PAINTED box (`painted_box` of the cutout, as the loop reads
    it off the dock's asset). No hand-clipped room and no `extra`: the first two cuts carried both, and the reviewer
    showed the real row loop answering a box whose ring ran through all four end names. The entry is then written
    exactly as the loop writes it - `centre: True` (a stamp lands at its fitted box from its first frame), and the
    fitted `ring_to` / `from_to`."""
    import build_scene_timeline_f as BST
    aid = "ev-prop-fed"
    series = LPG.load_series(SERIES)
    # the page a real 16:9 row compiles - with the compiler's ASPECT PINNED, because `stamp_full_stage` reads that
    # module global and every earlier compile in the process leaves it set (`authoring.table.compile_timeline`); a
    # 9:16 short compiled first left it "9:16", the page stayed unstamped, reported no end-name box and the stamp was
    # refused - in the full suite only (the same pin as `measure_page_boxes.full_stage_variant`, R26-235)
    _aspect, BST.ASPECT = BST.ASPECT, "16:9"
    try:
        page = BST.stamp_full_stage(LPG.build_spec(series, "line", 0, "right"))
    finally:
        BST.ASPECT = _aspect
    page["field"] = "scribble"
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    opts = BST.dock_opts({"prop": True, "arrive": "stamp", "mass": "ink", "ink": ink})   # the row's options, validated as a build's are
    fit = BST.stamp_dock_place(world, "16:9", opts, BST.painted_box(PROP_CUTOUT), None, None, "golden prop-stamp")   # the PAINTED mark, as the loop reads it off the dock's asset
    place = {k: fit[k] for k in ("x", "y", "w", "h", "room")}
    dock = BST.dock_entry(aid, 0, PROP_STAMP_ENTER, PROP_STAMP_EXIT, 0, BST.DOCK_KIND_PROP, place,
                          opts.get("arrive"), opts.get("mass"), True,
                          prop=bool(opts.get("prop")), ink=opts.get("ink"), ring_to=fit["ring_to"], from_to=fit["from_to"], paint=fit["paint"])
    ev = {aid: {"title": "The Federal Reserve", "source": "the operator's own cutout", "species": "prop",
                "document": {"path": str(PROP_CUTOUT.relative_to(REPO)), "sha256": "0" * 64}, "badges": [],
                "kind": BST.DOCK_KIND_PROP}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME],
               "docks": [dock], "species": []}]
    uris = _base_uris()
    uris[aid] = uri("image/png", png_proxy(PROP_CUTOUT, PROP_PROXY_PX))
    tl = _timeline(f"Golden: the stamped prop ({ink} ink)", scenes, ev, None)
    tl["kinetics"] = {"stop_action": True}   # P47 T1's switch: an authored `arrive` is the row's intent, the flag guards the goldens
    return tl, uris


SURFACES.update({
    "prop-stamp": lambda: _prop_stamp("own"),        # E99 s87: the woodblock in its own colour
    "prop-stamp-ink": lambda: _prop_stamp("page"),   # ... and laid down in the page's own ink
})
FRAME_T.update({
    # THE SETTLED FRAME: 1.30 s after the contact, past the rotation spring's own rest (6 / (zeta w0) = 1.0909 s).
    # Both springs are done and the mark stands OFF-SQUARE at -8.99 deg of its -9 deg landing - a stamp never lands
    # square, and that residual angle is the tell. The ring is long gone (its life is 0.4667 s).
    "prop-stamp": PROP_STAMP_ENTER + 1.30,
    "prop-stamp-ink": PROP_STAMP_ENTER + 1.30,
})


# ---- P70 T1 (was P69 T12): THE CHIP LANDS AS A STAMP - `arrive: "stamp"` on the stamp form, rendered both ways -------
# Steel and Paper H row 7's chip, recast: "... and it isn't Nvidia" (take `isn't Nvidia` 58.35-59.60; the door's
# NVIDIA_CHIP lands at 58.60 as the Lucide `cpu` glyph). Here it is the chip's stamp FORM on the icons catalogue's GPU
# cutout (E94, approved; a PROXY, as every catalogued cutout in a golden is - E99 s31), label NVIDIA in charcoal, at the
# stamp form's default size, breathing as the door's does (E49).
# WHY A PLATE AND NOT ROW 7'S PAGE (the send-back): the stamped chip's painted extent is its mark AND its label, and the
# arrival is fitted by the dock stamp's own law (`chip_stamp_ring_fit`: stamp_fit's ring and approach, `_stamp_floors`).
# On the divergence page no point clears at any size the form allows (180-260, searched over the page's right half,
# scratchpad/p70-t1/NOTES.md) - the fit WARNs everywhere, and a golden pins a clean arrival. On a CREAM plate (so the
# charcoal ring reads, as it does on every light ground) the fit answers with its law at work and no finding: the ring
# capped at 1.7508x and the approach at 1.9904x by the safe box's top. The page case rides the test bed, WARNs and all.
# ONE source, two surfaces: they differ only in `arrive` - and in what the compiler's own door writes because of it,
# `ring_to`, `from_to` and `paint`. Both are judged at the CONTACT + 0.10 s, the stamp's rotation still off its rest.
from gate_motion_density import STAMP_CONTACT_S as _STAMP_CONTACT_S  # noqa: E402

CHIP_STAMP_ENTRY = {"kind": "chip", "form": "stamp", "at": 10.0, "dur": 6.0, "icon": "prop-icon-gpu-ai-accelerator-v1",
                    "label": "NVIDIA", "ink": "charcoal", "idle": "breath", "target": {"kind": "point", "x": 0.5, "y": 0.36}}
CHIP_STAMP_PLATE = "plate-cream"
CHIP_STAMP_CREAM = (244, 230, 199)   # CHIP_STAMP.INK.cream, the long form's ground


# P70 T1b (E99 s121, s123): THE SEAL WITH ITS RING TEXT, GOLD ON THE DARK GROUND - the same source with `ring_text` /
# `ring_text_bottom` on the stamped chip: the top arc "AI ACCELERATOR", the bottom arc "GPU", both read left to right, at
# the source's proportion of the seal (it never widens it). The words are the icon's own catalogue name
# (`prop-icon-gpu-ai-accelerator-v1`), plainly generic and true of the drawn thing (s113: intentional, verified). It
# stands on a CHARCOAL plate with the name's ink `cream` - the reference's look, the seal's gold as it is; the arrival
# golden above stays on the cream, where the gold is darkened until it reads.
CHIP_STAMP_RING_TEXT = {"ring_text": "AI ACCELERATOR", "ring_text_bottom": "GPU", "ink": "cream"}
CHIP_STAMP_DARK_PLATE = "plate-charcoal"
CHIP_STAMP_CHARCOAL = (37, 49, 60)   # CHIP_SEAL.GROUND.dark, the template's --charcoal


def _chip_stamp(arrive: bool, ring: bool = False, ground: tuple[str, bytes] | None = None) -> tuple[dict, dict]:
    """`ground` (P72 T11): a plate id and its PNG in place of the flat cream / charcoal plate - the same source otherwise."""
    import build_scene_timeline_f as BST
    plate = ground[0] if ground else (CHIP_STAMP_DARK_PLATE if ring else CHIP_STAMP_PLATE)
    world = {"asset_id": plate, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    entry = dict(CHIP_STAMP_ENTRY, **({"arrive": "stamp"} if arrive else {}), **(CHIP_STAMP_RING_TEXT if ring else {}))
    errs = BST.validate_species([entry], (0, 0, 0), plate)
    assert not errs, errs
    compiled, asset = BST._with_stamp_catalogue(entry)   # the compiled entry carries its catalogue, as the row loop writes it
    compiled, notes = BST.chip_stamp_ring_fit(compiled, world, "16:9", BST.painted_box(asset["file"]), [],
                                              "golden chip-stamp")
    # the one finding a golden may carry is the s90 advice on its ring text (drawn at the seal's proportion, s106)
    assert all("under the E99 s90 phone floor" in n for n in notes), notes
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": [compiled]}]
    tl = _timeline("Golden: the chip's stamp form - on its spring, or landing as a stamp (P70 T1)", scenes, {}, None)
    # no captions: a build moves them to the quiet bottom rail while a labelled stamp chip is up
    # (`_readable_species_during`); the harness's hand-written stage captions do not, and sat across the chip
    tl["captions"], tl["caption_pages"] = [], []
    uris = _base_uris()
    uris[plate] = uri("image/png", ground[1] if ground else png_solid(64, 36, CHIP_STAMP_CHARCOAL if ring else CHIP_STAMP_CREAM))
    uris[BST.PROP_PREFIX + entry["icon"]] = uri("image/png", png_proxy(asset["file"]))
    return tl, uris


SURFACES.update({
    "chip-stamp-pop": lambda: _chip_stamp(False),       # the stamp form on the chip's spring, as it has always landed
    "chip-stamp-arrival": lambda: _chip_stamp(True),    # ... and with `arrive: "stamp"`: stopaction's stampXf
    "chip-stamp-seal-text": lambda: _chip_stamp(True, ring=True),   # P70 T1b: ... landed as a SEAL, its ring text on two arcs
})
FRAME_T.update({
    # CONTACT + 0.10 s (10.254): the stamp's scale spring clamped at 1 since 10.154 while the free rotation is still
    # 1.39 deg past its -9 deg rest (-10.39) and the capped ring radiates at 0.54 of its life round the mark and its
    # name; the pop is 0.46 of its LAND_S into the spring, its label at 48 px, under the floor.
    "chip-stamp-pop": round(CHIP_STAMP_ENTRY["at"] + _STAMP_CONTACT_S + 0.10, 3),
    "chip-stamp-arrival": round(CHIP_STAMP_ENTRY["at"] + _STAMP_CONTACT_S + 0.10, 3),
    # P70 T1b: the seal AT REST, 1.30 s after the enter (as prop-stamp's): both springs done, the ring spent, the ink eased
    # back to 0.86 - the two rings and the two arcs as they stay, the mark off-square at its -9 deg rest
    "chip-stamp-seal-text": round(CHIP_STAMP_ENTRY["at"] + 1.30, 3),
})


# ---- P72 T11 (E99 s130 (2)): A SEAL ON A PHOTO ADJUSTS ITS GOLD -------------------------------------------------------
# The operator: "yes, a seal on a photo should adjust its gold". chip-stamp-seal-text's source exactly (the ring text, the
# name's ink `cream`, the seal at rest 1.30 s after the enter) on a MID-TONE PHOTO PLATE instead of the charcoal: the
# gold reads the luminance MEASURED under the seal (the engine's groundLumAt at each of chip.mjs's sealGroundSamples -
# 64 points on the name's band, the top arc, the inner and the outer ring), not the row's authored ink. ONE GOLD PER SEAL,
# THE DARKEST GROUND WINS: it holds CONTRAST_MIN at the worst of the 64 (here the darkest, 0.280 of a 0.280-0.373 spread).
# #E8B86D reads 1.56:1 on this ground (the parent's finding, 1.55:1); the gold that holds is its channels scaled down,
# #544227 (lightening cannot reach 3:1 on a mid-tone). The plate is a PROXY of a photograph (E99 s31: no approved
# picture enters a golden): a warm mid-grey with a soft two-octave value noise and a fine grain, deterministic and
# stdlib-only like png_scene, so its pixels are identical on any machine and the ground under the seal is a photo's
# texture rather than one flat colour.
SEAL_PHOTO_PLATE = "plate-photo-mid"
SEAL_PHOTO_BASE = (158, 154, 146)   # the photo's mean: a warm mid-grey, WCAG luminance ~0.32 (#9A9A9A's)
SEAL_PHOTO_AMP = (14, 3)            # the texture: +-14 levels of soft value noise (8 x 6 cells), +-3 of grain


def png_photo(w: int, h: int, base: tuple[int, int, int], amp: tuple[int, int] = SEAL_PHOTO_AMP, seed: int = 7) -> bytes:
    """A deterministic PHOTO PROXY: `base` plus a bilinear value noise on an 8 x 6 lattice (+-amp[0] levels, smoothstep
    between lattice points) plus a per-pixel grain (+-amp[1]); the hash is integer arithmetic, so no library enters."""
    def hv(x: int, y: int, k: int) -> float:   # a lattice value in [-1, 1]
        n = (x * 374761393 + y * 668265263 + k * 2147483647 + seed * 144269504) & 0xFFFFFFFF
        n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 32767.5 - 1.0
    cx, cy = 8, 6
    raw = bytearray()
    for y in range(h):
        raw += b"\x00"
        fy = y / h * cy
        y0, ty = int(fy), fy - int(fy)
        ty = ty * ty * (3 - 2 * ty)
        for x in range(w):
            fx = x / w * cx
            x0, tx = int(fx), fx - int(fx)
            tx = tx * tx * (3 - 2 * tx)
            a = hv(x0, y0, 0) * (1 - tx) + hv(x0 + 1, y0, 0) * tx
            b = hv(x0, y0 + 1, 0) * (1 - tx) + hv(x0 + 1, y0 + 1, 0) * tx
            v = (a * (1 - ty) + b * ty) * amp[0] + hv(x, y, 1) * amp[1]
            raw += bytes(max(0, min(255, int(round(c + v)))) for c in base)
    return (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + png_chunk(b"IEND", b""))


SURFACES["seal-on-photo"] = lambda: _chip_stamp(True, ring=True, ground=(SEAL_PHOTO_PLATE, png_photo(240, 135, SEAL_PHOTO_BASE)))
FRAME_T["seal-on-photo"] = FRAME_T["chip-stamp-seal-text"]   # the seal at rest, as its charcoal twin is read


# ---- P69 T26a / R26-273: A BAR CHANGES ITS OWN VALUE (E28) ---------------------------------------------------------
# The halving beat test_compare_on_bars compiles (row 18 of Steel and Paper H): one bar at 20 on a full-stage bars
# page, its figure written at its top (8.0), and a `chart_to compare` (melt, then splash) at 11.0 over 2.4 s that turns
# "20%" into "10%" - which now moves the BAR to 10 on the page's own scale, the figure riding its top. The object's
# values are COPIED from the evidence object (`ev-index-concentration-bars-v1`) exactly as the test copies them, so the
# golden never reads an untracked series; the comparator's arithmetic is authored and checked by the compiler here.
HALVING_OBJ = {"title": "One bet, a fifth of the index",
               "sub": "AI builders as a share of the S&P 500 - today, against their historical two-to-four percent",
               "src": "Figures via Bravos Research - S&P 500 weighting (attributed)",
               "unit": "%",
               "hlines": [{"y": 4, "label": "historically 2-4%", "color": "deemph"}, {"y": 2, "color": "deemph"}],
               "bars": [{"label": "AI builders, share of the S&P 500 today", "value": 20, "note": "20%", "color": "crimson"}]}
HALVING_SPECIES = [
    {"kind": "figure", "at": 8.0, "dur": 1.5, "text": "20%", "target": {"kind": "datum", "index": 0}},
    {"kind": "chart_to", "at": 11.0, "dur": 2.4, "to": "compare", "form": "melt", "then": "splash", "hold": "metric",
     "metric": {"value": 20, "text": "20%", "label": "of the S&P 500"},
     "comparator": {"value": 10, "text": "10%", "label": "of the market, if they halve"},
     "inputs": {"share": 20}, "derive": "share / 2",
     "source": "[DERIVED: from ev-index-concentration-bars-v1, a fifth of the index falling by half, share / 2]"},
]


def bar_value_morph() -> tuple[dict, dict]:
    """P69 T26a (E28: the geometry says what the number says): the halving AT REST after the morph - the bar standing at
    10 on the 0-20 scale it was built on, "10%" written over its new top with "20%" held beside it and the comparator's
    label beneath. Before T26a this frame printed "10%" over a bar still drawn to 20%."""
    import tempfile
    import build_scene_timeline_f as BST
    plate = "ledger:fx-index-concentration-bars:bars"
    species = [dict(e) for e in HALVING_SPECIES]
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/fx-index-concentration-bars.series.json").write_text(json.dumps(HALVING_OBJ), encoding="utf-8")
        saved = BST.ASPECT
        BST.ASPECT = "16:9"
        try:
            world = BST.world_for_plate(plate, (0, 0, 0), ep)
            BST.stamp_full_stage(world["page"])
        finally:
            BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: a bar changes its own value (the halving)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"bar-value-morph": bar_value_morph})
FRAME_T.update({"bar-value-morph": 14.4})   # at rest: the window closed at 13.4 (the bar landed at 11.0 + 0.72 x 2.4), the comparator's label written whole


# ---- P69 T26e / E99 s107: PROPS, PAGES AND CHARTS MORPH INTO EACH OTHER - one golden each way ---------------------
# The operator: "we should also be able to morph/transform to/from props to pages and charts." The Steel and Paper H
# beat is the pair: the data centre BECOMES the $690 capex bar it costs, and the capex page COLLAPSES back into the
# data centre. Both are compiled here by the functions the row loop calls (`prop_morph_row`, the stamp/place fit,
# `dock_entry`, `finish_prop_morphs`) on a two-bar page copied from the capex object's own values - so the golden
# never reads an untracked series - with the data centre as a PROXY of the catalogued cutout (E99 s31: an approved
# cutout never enters git; `png_proxy`'s integer box filter, as the stamped-prop goldens do).
#   prop-morph-bar   the data centre stamped at an authored place in the page's right margin (9.0), then on 14.0 the
#                    verb `chart_to {to: morph, from: prop:<id>, mark: b:1}` over 2.0 s: judged at u 0.50 - the
#                    prop's own pixels on the ARAP strip, half way between its silhouette and the bar's rectangle,
#                    the bar itself not yet drawn (it is the prop's to become).
#   prop-morph-page  the same page; on 12.0 `chart_to {to: prop, prop: <id>, mark: page, place}` over 2.0 s: judged at
#                    u 0.50 - the page carved to the shape it is becoming, the prop's pixels arriving on it.
PROP_DC = "prop-hyperscale-datacenter-v1"
PROP_DC_CUTOUT = REPO / "content/video_engine/assets/props/cutouts" / f"{PROP_DC}.png"
PROP_MORPH_OBJ = {"title": "Hyperscaler capital spending, consensus estimates",
                  "sub": "The five largest hyperscalers' 2026 capital spending, US$ billions",
                  "src": "Values copied from ev-capex-consensus-v2 (PIMCO, consensus estimates, not actuals)",
                  "unit": "$",
                  "bars": [{"label": "Start of year", "value": 480, "note": "$480"},
                           {"label": "Consensus now", "value": 690, "note": "$690", "color": "crimson"}]}
PROP_MORPH_STAMP = 9.0      # the page is built by ~7.4 s; the data centre is stamped on a page that has been read
PROP_MORPH_IN_AT = 14.0     # ... and becomes the bar on this word
PROP_MORPH_OUT_AT = 12.0    # the page becomes the data centre on this word
PROP_MORPH_DUR = 2.0


def _prop_morph_world():
    import tempfile
    import build_scene_timeline_f as BST
    plate = "ledger:fx-capex-bars:bars"
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/fx-capex-bars.series.json").write_text(json.dumps(PROP_MORPH_OBJ), encoding="utf-8")
        saved = BST.ASPECT
        BST.ASPECT = "16:9"
        try:
            world = BST.world_for_plate(plate, (0, 0, 0), ep)
            BST.stamp_full_stage(world["page"])
        finally:
            BST.ASPECT = saved
    return dict(world, ken_burns={"scale": 0, "x": 0, "y": 0})


def _prop_morph(way: str) -> tuple[dict, dict]:
    """One row compiled as the row loop compiles it: the verbs read off (`prop_morph_row`), the docks placed (the
    authored place, the stamp's fit), the entries written (`dock_entry`, `handed` / `arrive: morph`), and the morphs
    finished against the state on screen (`finish_prop_morphs`)."""
    import build_scene_timeline_f as BST
    world, where = _prop_morph_world(), "golden prop-morph"
    if way == "in":
        ds = [(PROP_DC, 0, PROP_MORPH_STAMP, RUNTIME, {"prop": True, "arrive": "stamp", "mass": "ink", "ink": "own",
                                                       "place": {"x": 0.84, "y": 0.47, "w": 0.2}})]
        species = [{"kind": "chart_to", "to": "morph", "from": f"prop:{PROP_DC}", "at": PROP_MORPH_IN_AT,
                    "dur": PROP_MORPH_DUR, "mark": "b:1", "id": "s01.species.0"}]
    else:
        ds = []
        species = [{"kind": "chart_to", "to": "prop", "prop": PROP_DC, "at": PROP_MORPH_OUT_AT, "dur": PROP_MORPH_DUR,
                    "mark": "page", "place": {"x": 0.5, "y": 0.5, "w": 0.3}, "id": "s01.species.0"}]
    r = BST.prop_morph_row(species, ds, None, 0.0, RUNTIME, where, sid="s01")
    docks = []
    for n, (aid, slot, enter, exitt, raw) in enumerate(r["ds"]):
        opts = BST.dock_opts(raw)
        if n in r["born"]:
            opts = {**opts, "arrive": "morph"}
        paint = BST.painted_box(PROP_DC_CUTOUT)
        fit = BST.stamp_dock_place(world, "16:9", opts, paint, None, None, where) if opts.get("arrive") == "stamp" \
            else BST.prop_place_fit(world, "16:9", opts, paint, None, where)
        place = {k: fit[k] for k in ("x", "y", "w", "h", "room")}
        stamped = opts.get("arrive") == "stamp"
        docks.append(BST.dock_entry(aid, slot, enter, exitt, 0, BST.DOCK_KIND_PROP, place, opts.get("arrive"), opts.get("mass"),
                                    True, prop=True, ink=opts.get("ink"), ring_to=fit.get("ring_to") if stamped else None,
                                    from_to=fit.get("from_to") if stamped else None, paint=fit.get("paint") if stamped else None,
                                    rot=opts.get("rot"), handed=n in r["handed"]))
    morphs, _warns = BST.finish_prop_morphs(r["morphs"], docks, world, r["species"], "16:9", where, lambda aid: PROP_DC_CUTOUT)
    ev = {PROP_DC: {"title": "A hyperscale data centre", "source": "the operator's own cutout", "species": "prop",
                    "document": {"path": str(PROP_DC_CUTOUT.relative_to(REPO)), "sha256": "0" * 64}, "badges": [],
                    "kind": BST.DOCK_KIND_PROP}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": docks,
               "species": r["species"], BST.PROP_MORPH_KEY: morphs}]
    uris = _base_uris()
    uris[PROP_DC] = uri("image/png", png_proxy(PROP_DC_CUTOUT, PROP_PROXY_PX))
    tl = _timeline(f"Golden: the prop morph ({'the data centre becomes the bar' if way == 'in' else 'the page becomes the data centre'})",
                   scenes, ev, "16:9")
    tl["kinetics"] = {"stop_action": True}   # the stamp's own switch (P47 T1), as the stamped-prop goldens carry it
    return tl, uris


SURFACES.update({
    "prop-morph-bar": lambda: _prop_morph("in"),     # E99 s107: the data centre becomes the $690 bar
    "prop-morph-page": lambda: _prop_morph("out"),   # ... and the capex page collapses into the data centre
})
FRAME_T.update({
    "prop-morph-bar": PROP_MORPH_IN_AT + PROP_MORPH_DUR * 0.5,    # u 0.50: the pixels on the mesh, half way to the bar
    "prop-morph-page": PROP_MORPH_OUT_AT + PROP_MORPH_DUR * 0.5,  # u 0.50: the page carved to the shape, the pixels arriving
})


# ---- P69 T8b (E99 s104, amended twice): THE LEDGER PAGE DRAWS PANELS ---------------------------------------------------
# Two pages, both put through the compiler's own doors (`validate_species`, then `derive_rescale_states`, which runs
# `check_panels` and normalises every focus state) and stamped full-stage as a 16:9 row is:
#   panels-two-eras   `ev-tnx-two-eras-v3` - the panels object the card's `chart_dock:panels` draws and no page could -
#                     as a PAGE: two plots on ONE scale (E79), each with its sub, its axes, its value tag, the reference
#                     rules named once on the panel with room; read once both panels have built on their own turns
#   panels-quad-grow  four panels in a QUAD, then one `panel_focus` on a word: panel 2 grows to the page while 1, 3 and 4
#                     recede (scaled back, dimmed, blurred) - read at the transition's midpoint (u 0.50), every box in
#                     flight on the one clock
PANELS_V3 = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-tnx-two-eras-v3.series.json"
PANELS_GROW_AT, PANELS_GROW_DUR = 17.0, 1.2   # the four panels have built on their own turns by 4.4 + 4 x 3.0 = 16.4


def _panels_four() -> dict:
    """Four synthetic line charts - a SHAPE for the golden, not figures about the world."""
    xs = [2016 + i / 4 for i in range(33)]

    def pts(f):
        return [[round(x, 2), round(f(i), 2)] for i, x in enumerate(xs)]
    return {
        "title": "Four gauges of one boom", "sub": "Synthetic panels for the golden surface; not figures about the world",
        "src": "Synthetic series for the golden surface", "yunit": "%", "independent": True,
        "xticks": [[2016, "2016"], [2018, "2018"], [2020, "2020"], [2022, "2022"], [2024, "2024"]],
        "panels": [
            {"sub": "Capex growth", "series": [{"name": "CAPEX", "label": "+38%", "color": "teal", "pts": pts(lambda i: 4 + 0.03 * i * i)}]},
            {"sub": "Memory prices", "series": [{"name": "DRAM", "label": "+61%", "color": "crimson", "pts": pts(lambda i: 20 + 12 * ((i % 11) / 10) + i)}]},
            {"sub": "Credit spreads", "series": [{"name": "IG OAS", "label": "0.9%", "color": "cobalt", "pts": pts(lambda i: 1.6 - 0.02 * i)}]},
            {"sub": "Power demand", "series": [{"name": "GRID LOAD", "label": "+12%", "color": "amber", "pts": pts(lambda i: 2 + 0.3 * i)}]},
        ],
    }


def _panels_page(series: dict, species: list, title: str) -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    page = BST.stamp_full_stage(LPG.build_spec(series, "line", None, "right"))
    plate = "ledger:golden-panels:line"
    errs = BST.validate_species(species, (0, 0, 0), plate)
    assert not errs, errs
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    BST.derive_rescale_states(world, species, plate, REPO)
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline(title, scenes, {}, None), _base_uris()


def panels_two_eras() -> tuple[dict, dict]:
    return _panels_page(LPG.load_series(PANELS_V3), [], "Golden: the two-era panels page")


def panels_quad_grow() -> tuple[dict, dict]:
    grow = {"kind": "panel_focus", "at": PANELS_GROW_AT, "dur": PANELS_GROW_DUR, "layout": "row", "active": [1]}
    return _panels_page(_panels_four(), [grow], "Golden: a quad, panel 2 growing while the rest recede")


SURFACES.update({"panels-two-eras": panels_two_eras, "panels-quad-grow": panels_quad_grow})
FRAME_T.update({
    "panels-two-eras": 12.0,                                     # both panels built (4.4 + 2 x 3.0 = 10.4), the tags landed
    "panels-quad-grow": PANELS_GROW_AT + PANELS_GROW_DUR * 0.5,  # u 0.50: panel 2 half grown, 1 / 3 / 4 half receded
})


# ---- P69 T8c (E99 s104, amended): A PANEL'S BOX CHANGES SHAPE, AND ITS CHART RE-LAYS OUT ----------------------------------
#   panels-resize     the two-era page standing as ONE chart over the whole region (panel 2 hidden, the state it arrives
#                     in), then on a word the row: panel 1 SHRINKS into its slot, its plot re-projected to the box's width
#                     every frame with its words at their size, while panel 2 builds in beside it - read at u 0.50. The
#                     timeline carries the leave too (panel 1 goes, the survivor GROWS back to the whole region)
PANELS_RESIZE_AT, PANELS_RESIZE_DUR, PANELS_LEAVE_AT = 9.0, 1.2, 16.0   # panel 1 alone has built by 4.4 + 3.0 = 7.4


def panels_resize() -> tuple[dict, dict]:
    fs = [{"kind": "panel_focus", "at": 0.0, "dur": 0.05, "layout": "row", "active": [0], "hidden": [1]},
          {"kind": "panel_focus", "at": PANELS_RESIZE_AT, "dur": PANELS_RESIZE_DUR, "layout": "row", "active": [0, 1]},
          {"kind": "panel_focus", "at": PANELS_LEAVE_AT, "dur": PANELS_RESIZE_DUR, "layout": "row", "active": [1], "hidden": [0]}]
    return _panels_page(LPG.load_series(PANELS_V3), fs, "Golden: one chart shrinks into its slot while the second builds in")


SURFACES.update({"panels-resize": panels_resize})
FRAME_T.update({"panels-resize": PANELS_RESIZE_AT + PANELS_RESIZE_DUR * 0.5})   # u 0.50: panel 1 half way to its slot


# ---- P69 T8d (E99 s104 amended x2): A PANEL MAY BE BARS, AND A BAR MAY CARRY A RANGE ----------------------------------
#   panels-mixed-grow  row 21's shape as a quad - two line panels and two BARS panels (the wafer ratio, 1x vs 3x; the
#                      contract prices, one of them the range "+55–60%") - then one `panel_focus` on a word: the wafer
#                      bars grow to the page while the other three recede, read at u 0.50. The bars hold Bravos's 196 px
#                      on the stage as their panel grows (rebuilt at the pose's scale), each value on its bar
#   bars-range         a bars page whose first bar is a RANGE: the bar at +55, a lighter band to +60 with a dashed edge,
#                      "+55–60%" written over the band - never the 57.5 midpoint `ev-dram-contract-v1` printed
# The figures are COPIED from `ev-hbm-wafer-ratio-bars-v1` and `ev-dram-contract-v1` (whose note "+55-60%" is the
# range restated); the two lines are `_panels_four`'s synthetic shapes. Surfaces, not claims about the world.
T8D_WAFER = [{"label": "Standard DRAM", "value": 1, "color": "deemph"}, {"label": "HBM (stacked dies)", "value": 3, "color": "crimson"}]
T8D_DRAM = [{"label": "Conventional DRAM", "value": ["+55", "60"], "color": "deemph"},
            {"label": "Server DRAM", "value": "+60", "color": "deemph"}, {"label": "Consumer DRAM", "value": "+89", "color": "crimson"}]
T8D_DRAM_SRC = "TrendForce - Counterpoint - quarterly contract price change (copied from ev-dram-contract-v1 for the golden)"
MIXED_GROW_AT, MIXED_GROW_DUR = 17.0, 1.2   # the four panels have built on their own turns by 4.4 + 4 x 3.0 = 16.4


def _panels_mixed() -> dict:
    four = _panels_four()
    lines = four["panels"]
    return dict(four, title="Two lines and two bars, one page",
                panels=[lines[0], {"sub": "Wafer capacity per gigabyte", "builder": "bars", "unit": "x", "bars": json.loads(json.dumps(T8D_WAFER))},
                        lines[2], {"sub": "Memory contract prices, quarter over quarter", "builder": "bars", "unit": "%",
                                   "bars": json.loads(json.dumps(T8D_DRAM))}])


def panels_mixed_grow() -> tuple[dict, dict]:
    grow = {"kind": "panel_focus", "at": MIXED_GROW_AT, "dur": MIXED_GROW_DUR, "layout": "row", "active": [1]}
    return _panels_page(_panels_mixed(), [grow], "Golden: a mixed quad, the wafer bars growing while the rest recede")


def bars_range() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    series = {"title": "Memory contract prices, quarter over quarter", "sub": "2026 - HBM, DRAM and NAND essentially sold out for the year",
              "src": T8D_DRAM_SRC, "unit": "%", "bars": json.loads(json.dumps(T8D_DRAM))}
    page = BST.stamp_full_stage(LPG.build_spec(series, "bars", None, "right"))
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: a range bar - the bar at +55, the band to +60, the range written", scenes, {}, None), _base_uris()


SURFACES.update({"panels-mixed-grow": panels_mixed_grow, "bars-range": bars_range})
FRAME_T.update({"panels-mixed-grow": MIXED_GROW_AT + MIXED_GROW_DUR * 0.5,   # u 0.50: the wafer bars half grown, the rest half receded
                "bars-range": 9.0})                                           # the bars built (4.4 + 3.0), the values landed


# ---- P69 T45 (E99 s101; s109 (2)): THE MEMBERSHIP STACK - equal tiles naming who is in ONE bar ---------------------------
#   membership-builders  the five biggest builders' cash capital spending in Q1 2026, ONE bar of $148.4B divided into its
#                        five members' equal tiles, bottom-up, landed one per member after the bar stood (the default
#                        cascade), the total written and "each tile = one company" beside it. No tile carries a logo:
#                        the operator's catalogue carries no mark for any of the five, so each tile is its NAME
#   membership-basket    the calendar project's hynix + Micron basket, INTO the print and AFTER it - two membership bars
#                        whose Micron tile is the catalogue's own cutout (prop-icon-micron-memory-orbit-v1, tagged
#                        `micron-technology`) and whose SK hynix tile is its name: a logo where one exists, a name where not
# Both are READ off the objects on disk (the five tickers and the Q1 '26 point of ev-capex-funding-v1; the two bars of
# ev-into-vs-after-v1), never re-typed. Surfaces, not new claims about the world.
MEMBERS_OBJECTS = REPO / "content/video_engine/projects/systems-and-blowups"
MEMBERS_FUNDING = MEMBERS_OBJECTS / "steel-and-paper/evidence/objects/ev-capex-funding-v1.series.json"
MEMBERS_BASKET = MEMBERS_OBJECTS / "memory-trades-the-calendar/evidence/objects/ev-into-vs-after-v1.series.json"
MEMBERS_TICKERS = {"MSFT": "Microsoft", "AMZN": "Amazon", "GOOGL": "Alphabet", "META": "Meta", "ORCL": "Oracle"}
MEMBERS_QUARTER = 2026.125   # Q1 '26 on the object's own decimal-year x
MEMBERS_MICRON = "prop-icon-micron-memory-orbit-v1"


def _members_page(series: dict, title: str) -> tuple[dict, dict]:
    """A bars page through the compiler's own membership path: the spec, the stamp, the logos resolved against the
    catalogue - and the asset map that carries them."""
    import build_scene_timeline_f as BST
    assert LPG.validate(series, "bars") == [], LPG.validate(series, "bars")
    page = BST.stamp_full_stage(LPG.build_spec(series, "bars", 0, "right"))
    assert BST.resolve_member_logos(page) == [], "every logo in a golden is the catalogue's"
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    tl = _timeline(title, scenes, {}, None)
    return tl, dict(_base_uris(), **BST.member_assets(tl))


def membership_builders() -> tuple[dict, dict]:
    obj = json.loads(MEMBERS_FUNDING.read_text(encoding="utf-8"))
    capex = next(s for s in obj["series"] if s.get("name") == "CASH CAPEX")
    value = next(y for x, y in capex["pts"] if abs(x - MEMBERS_QUARTER) < 1e-9)
    tickers = [t.strip() for t in obj["src"].split(" - ")[1].split(";")[0].split(",")]
    assert tickers == list(MEMBERS_TICKERS), tickers
    series = {"title": "Five companies, one quarter's bill",
              "sub": "Cash capital spending, Q1 2026, US$ billions - the five biggest builders together",
              "src": obj["src"].split(";")[0] + " (copied from ev-capex-funding-v1 for the golden)",
              "unit": "$", "member_noun": "company",
              "bars": [{"label": "Q1 2026", "value": value, "color": "crimson",
                        "members": [{"name": MEMBERS_TICKERS[t]} for t in tickers]}]}
    return _members_page(series, "Golden: the membership stack - five companies' tiles in one $148.4B bar")


def membership_basket() -> tuple[dict, dict]:
    obj = json.loads(MEMBERS_BASKET.read_text(encoding="utf-8"))
    members = [{"name": "SK hynix"}, {"name": "Micron", "logo": MEMBERS_MICRON}]
    series = {"title": obj["title"], "sub": obj["sub"], "src": obj["src"], "unit": "%", "member_noun": "stock",
              "bars": [dict({k: b[k] for k in ("label", "value", "color")}, members=json.loads(json.dumps(members)))
                       for b in obj["bars"]]}
    return _members_page(series, "Golden: the membership stack - a catalogued logo where one exists, a name where not")


SURFACES.update({"membership-builders": membership_builders, "membership-basket": membership_basket})
FRAME_T.update({"membership-builders": 10.5,   # the cascade over: 4.4 + 3.0 + 0.25 + 4 x 0.34 + 0.45 = 9.46, every tile standing
                "membership-basket": 10.0})    # 4.4 + 3.0 + 0.25 + 0.34 + 0.45 = 8.44 on both bars, the key written


# ---- P69 T36 / E99 s99: THE LIT STRETCH - a light that TRAVELS down the fall on its word -----------------------------
# Steel and Paper H row 5's own page (`ledger:ev-railway-index-v1:line:139:right`, `idle=live`, full stage, 16:9) and
# its own sentence: "Railways in the 1840s drew a quarter-billion pounds ... then crashed by nearly two-thirds." The
# H take's words, shifted by -67.46 s so the page has built first: "crashed" 77.46 -> 10.00 (row 5's own build_to to
# the trough, 1.2 s), "nearly" 78.08 -> 10.62 (the light leaves the PEAK, datum 53, and runs the fall to the TROUGH,
# datum 139, over "nearly two-thirds." to its end at 79.64 -> 12.18) and the figure "−64%" lands at the trough as the
# light arrives (the harvest's R18: ring the peak, light the fall, land the % at the trough). The object is the
# COMMITTED evidence sidecar, read in place. Judged mid-travel (u 0.50 of the head's run): the comet head half way
# down the fall, the stretch behind it lit, the rest of the line in its own ink, the page's live lead point sparking at
# the trough the light is running to.
LIT_PROJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
LIT_PLATE = "ledger:ev-railway-index-v1:line:139:right;idle=live"
LIT_FALL_AT, LIT_AT, LIT_DUR = 10.0, 10.62, 1.56
LIT_SPECIES = [
    {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": {"kind": "datum", "index": 53}},   # the build beat draws to the peak
    {"kind": "build_to", "at": LIT_FALL_AT, "dur": 1.2, "series": 0, "target": {"kind": "datum", "index": 139}},   # "crashed": the fall draws
    {"kind": "lit_stretch", "at": LIT_AT, "dur": LIT_DUR, "from": 53, "to": 139, "comet": True},               # "nearly two-thirds": the light runs it
    {"kind": "figure", "at": round(LIT_AT + LIT_DUR * 0.8, 2), "dur": 1.4, "target": {"kind": "datum", "index": 139, "series": 0},
     "text": "−64%", "color": "neg", "dy": -0.9},                                                        # ... and the % lands where it arrives
]


def lit_stretch_crash() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    species = [dict(e) for e in LIT_SPECIES]
    assert not BST.validate_species(species, (0, 0, 0), LIT_PLATE), BST.validate_species(species, (0, 0, 0), LIT_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(LIT_PLATE, (0, 0, 0), LIT_PROJECT)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the light travels down the fall (lit_stretch)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"lit-stretch-crash": lit_stretch_crash})


# ---- P69 T49 / E99 s99: THE FREEZE BEAT - everything stops and one light comes on -----------------------------------
# The same railway page (H row 5, `idle=live`, full stage, 16:9) and the same sentence, one beat later: the fall has
# drawn on "crashed" (10.0-11.2), the hand has written "−64%" at the trough (11.2-11.8), and on the TURN - the number the
# row builds to - the stage STOPS for 1.0 s while one light comes on at the trough (12.0-13.0); then the page's life
# resumes. The page LIVES (E49's switch is on: the source says so, as `page-life-live` does), so the stopped frame is a
# real stop and not a page that was still anyway. Judged in the beat's held middle (12.5): the light on, the spark and
# the drift held where they stopped. The beat's two ramps and life resuming are read by test_freeze_beat on the served
# player, not pinned as frames.
FREEZE_AT, FREEZE_DUR = 12.0, 1.0
FREEZE_SPECIES = [
    {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": {"kind": "datum", "index": 53}},        # the build beat draws to the peak
    {"kind": "build_to", "at": LIT_FALL_AT, "dur": 1.2, "series": 0, "target": {"kind": "datum", "index": 139}},   # "crashed": the fall draws
    {"kind": "figure", "at": 11.2, "dur": 0.6, "target": {"kind": "datum", "index": 139, "series": 0},
     "text": "−64%", "color": "neg", "dy": -0.9},                                                                # the number is written ...
    {"kind": "freeze", "at": FREEZE_AT, "dur": FREEZE_DUR, "target": {"kind": "datum", "index": 139, "series": 0}},   # ... and the stage stops on it
]


def freeze_trough() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    species = [dict(e) for e in FREEZE_SPECIES]
    assert not BST.validate_species(species, (0, 0, 0), LIT_PLATE), BST.validate_species(species, (0, 0, 0), LIT_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(LIT_PLATE, (0, 0, 0), LIT_PROJECT)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: the stage stops on the trough and one light comes on (freeze)", scenes, {}, "16:9")
    tl["kinetics"] = {"idle": True}   # E49 is ON for every compiled timeline; the beat's subject is that life stopping
    return tl, _base_uris()


SURFACES.update({"freeze-trough": freeze_trough})
FRAME_T.update({"freeze-trough": FREEZE_AT + FREEZE_DUR * 0.5})
FRAME_T.update({"lit-stretch-crash": round(LIT_AT + 0.5 * LIT_DUR * 0.8, 3)})   # u 0.50 of the head's run (TRAVEL 0.8 of the word): 11.244


# ---- P69 T37: SOLO - on "Chipmakers" the chips keep their ink and every other line mutes to E67's dim ----------------
# Steel and Paper H row 10's own page and its own sentence: the verified divergence page (`ev-divergence-v1`, the four
# lines - memory makers, semiconductors, mega-cap tech, the S&P 500 - the page row 10 recasts to under the sell ticket)
# and "Chipmakers doubling while their customers sit flat at the index is textbook profit-taking." The H take's words
# (`vo-h-scratch/scratch-kokoro.words.json`), shifted by -82.675 s so the page has built first: "Chipmakers" 94.675 ->
# 12.00 (the chips' solo, over the word, 0.71 s), "customers" 96.263 -> 13.59 (the mute hands over to the mega-cap line,
# 0.58 s) and "textbook" 98.338 -> 15.66 (unsolo: the comparison is the claim again, 0.54 s). The object is the
# COMMITTED evidence sidecar, read in place; the harvested frame is JPN 05:23.5 (`docs/research/runs/bravos-watch/
# nB1eXWQlW58/luna-recovery/focus-05-treasury-holdings/frames/frame_0008.jpg`). Judged once the chips' mute has
# landed and holds (13.11): the semiconductor line, its lead point and its tag at full ink, the other three at 0.45.
SOLO_PLATE = "ledger:ev-divergence-v1:line;idle=live"
SOLO_SHIFT = -82.675
SOLO_CHIPS, SOLO_CUSTOMERS = 1, 2        # ev-divergence-v1's SEMICONDUCTOR STOCKS and MEGA-CAP TECH STOCKS
SOLO_CHIPS_AT, SOLO_CHIPS_DUR = 12.0, 0.71            # "Chipmakers" 94.675-95.388
SOLO_CUSTOMERS_AT, SOLO_CUSTOMERS_DUR = 13.59, 0.58   # "customers" 96.263-96.838
SOLO_UNSOLO_AT, SOLO_UNSOLO_DUR = 15.66, 0.54         # "textbook" 98.338-98.875
SOLO_SPECIES = [
    {"kind": "solo", "at": SOLO_CHIPS_AT, "dur": SOLO_CHIPS_DUR, "series": SOLO_CHIPS},            # "Chipmakers doubling"
    {"kind": "solo", "at": SOLO_CUSTOMERS_AT, "dur": SOLO_CUSTOMERS_DUR, "series": SOLO_CUSTOMERS},  # "... while their customers sit flat"
    {"kind": "unsolo", "at": SOLO_UNSOLO_AT, "dur": SOLO_UNSOLO_DUR},                               # "... is textbook profit-taking"
]


def solo_chipmakers() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    series = LPG.load_series(SERIES)
    names = [s.get("name", "") for s in series["series"]]
    assert names[SOLO_CHIPS].startswith("SEMICONDUCTOR") and names[SOLO_CUSTOMERS].startswith("MEGA-CAP"), names
    species = [dict(e) for e in SOLO_SPECIES]
    assert not BST.validate_species(species, (0, 0, 0), SOLO_PLATE), BST.validate_species(species, (0, 0, 0), SOLO_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(SOLO_PLATE, (0, 0, 0), LIT_PROJECT)
        BST.stamp_full_stage(world["page"])
        BST.check_target_series(world, species)
        BST.check_solo(world, species)
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: on 'Chipmakers' the chips keep their ink and the rest mute (solo)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"solo-chipmakers": solo_chipmakers})
FRAME_T.update({"solo-chipmakers": round(SOLO_CHIPS_AT + SOLO_CHIPS_DUR + 0.4, 3)})   # the chips' mute landed and holding: 13.11


# ---- P69 T66 (E99 s111): THE BROKEN CROSS-ERA AXIS ------------------------------------------------------------------------
#   broken-axis-two-eras  ONE x axis across two eras, the years between them cut out and the cut DRAWN: a `//` across the
#                         axis, the gap written in the eras' own years ("2001 // 2021"), each era named over its own
#                         stretch, both stretches on the same years-per-pixel, the one y (the 10-year yield, %) from zero
#                         for both. The claim is the LEVEL (s111): the yield stands where the dot-com era's stood.
# The data is the committed two-era object's own (`ev-tnx-two-eras-v3`, Yahoo Finance ^TNX): its two panels' points
# verbatim as two series, its rules, its unit and its source. No railway-era share-of-GDP SERIES is committed (only the
# 7 % peak tile, `ev-railway-gdp-tile-v1`), so the railway page waits for its sourced series - none is invented here.
# The end tags are v4's honest values (v4's provenance note: 5.078 -> "5.1%"); the eras' names are v4's, the years
# left to the ticks. `;build=lines` (R26-226): the dot-com era draws whole, then the AI era.
BROKEN_BUILD_T0 = 4.4    # ROLL 0.7 + SAVOR 0.8 + FIELD 2.4 + PUNCH 0.5: the page's build begins
BROKEN_SERIES_S = 1.5    # the page's BUILD 3.0 over its two series (the bare `lines` mode divides the page's own window)
BROKEN_BUILD_S = 2 * BROKEN_SERIES_S
BROKEN_ERAS = ("DOT-COM ERA", "AI ERA")
BROKEN_TAGS = ("5.1%", "4.7%")   # ev-tnx-two-eras-v4's series labels (the last value of each era, rounded honestly)


def broken_axis_series() -> dict:
    """v3's two eras as ONE line page on ONE broken x axis - every value read off the committed object."""
    v3 = LPG.load_series(PANELS_V3)
    era = [p["series"][0] for p in v3["panels"]]
    return {"title": v3["title"],
            "sub": "One scale, one axis - the nineteen years between the eras cut out, not drawn",
            "src": v3["src"], "yunit": v3["yunit"], "ylabel": "10-year yield, %", "from_zero": True,
            "hlines": v3["hlines"], "xticks": v3["xticks"], "claim": "level",
            "break": {"after": era[0]["pts"][-1][0], "before": era[1]["pts"][0][0], "eras": list(BROKEN_ERAS)},
            "series": [{"label": tag, "color": col, "pts": s["pts"]}
                       for s, tag, col in zip(era, BROKEN_TAGS, ("teal", "crimson"))]}


def broken_axis_two_eras() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    series = broken_axis_series()
    assert LPG.validate(series, "line") == [], LPG.validate(series, "line")
    page = BST.stamp_full_stage(LPG.build_spec(series, "line", None, "right"))
    page["build"] = "lines"   # the one key `;build=lines` writes (page_build_spec's bare mode)
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    BST.check_broken_axis(world, [])
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: one line across two eras on a broken axis", scenes, {}, None), _base_uris()


SURFACES.update({"broken-axis-two-eras": broken_axis_two_eras})
FRAME_T.update({"broken-axis-two-eras": BROKEN_BUILD_T0 + BROKEN_BUILD_S + 1.6})   # both eras drawn and tagged (7.4), held


# ---- P69 T64 / E99 s110 (1): THE STACKED BAR OF VALUES, AND THE STACKED-BAR-PLUS-LINE COMBO ---------------------------
#   stacked-combo-funding  Steel and Paper H's row 17 ("the arithmetic"): the five biggest builders' operating cash in the
#                          first quarter of each year, each bar STACKED - what cash capital spending took, and what was
#                          left - with the capex share of that cash as ONE line over the stacks on its OWN labelled right
#                          axis (%, in the line's colour; the bars' axis in US$ billions): 44 % -> 65 % -> 94 %
#   stacked-outlays        a bars page of ONE stacked bar: federal outlays, October-August of fiscal 2026 - what revenue
#                          paid for and what was borrowed (the deficit), the total written over the bar
# Both are READ off committed objects, never re-typed: ev-capex-funding-v1's two filed series (Epoch AI - "what was left"
# and "the share" are those two series' arithmetic, said in the source line) and cbo-interest-revenue's CBO facts. No
# revenue or debt-funded split exists on disk for the builders (the plan's "cash-funded / debt-funded with the revenue
# line"), so the golden draws the nearest real pair and the source line says what was computed.
STACKED_FUNDING = MEMBERS_FUNDING
STACKED_OUTLAYS = MEMBERS_OBJECTS / "american-debt-trap/evidence/objects/cbo-interest-revenue.series.json"
STACKED_QUARTERS = ((2024.125, "Q1 2024"), (2025.125, "Q1 2025"), (2026.125, "Q1 2026"))   # the first quarter of each year


def stacked_funding_series() -> dict:
    obj = json.loads(STACKED_FUNDING.read_text(encoding="utf-8"))
    by = {s.get("name"): {round(x, 3): y for x, y in s["pts"]} for s in obj["series"] if s.get("name")}
    ocf, capex = by["CASH FROM OPERATIONS"], by["CASH CAPEX"]
    bars, share = [], []
    for x, label in STACKED_QUARTERS:
        cash, spent = ocf[x], capex[x]
        bars.append({"label": label, "value": cash, "color": "deemph",
                     "segments": [{"name": "Cash capex", "value": spent, "color": "crimson"},
                                  {"name": "Left over", "value": round(cash - spent, 1), "color": "deemph"}]})
        share.append([x, round(100 * spent / cash)])
    return {"title": "Who pays for the steel",
            "sub": "The five biggest builders' cash from operations, first quarter of each year: what capital spending "
                   "took, what was left - and the share it took",
            "src": "Epoch AI (Jun 2026), filings: " + obj["src"].split(" - ")[1].split(";")[0] + "; the rest: our arithmetic",
            "unit": "$", "ylabel": "US$ billions per quarter", "line_unit": "%", "line_label": "capex, % of cash",
            "bars": bars, "series": [{"name": "CAPEX SHARE", "label": "", "color": "teal", "pts": share}]}


def stacked_outlays_series() -> dict:
    f = json.loads(STACKED_OUTLAYS.read_text(encoding="utf-8"))["facts"]
    return {"title": "Where the spending came from",
            "sub": "Federal outlays, October-August of fiscal 2026, US$ billions: what revenue paid for, and what was borrowed",
            "src": "CBO Monthly Budget Review, September 9, 2026, Tables 1 and 3 (preliminary)",
            "unit": "$",
            "bars": [{"label": "Outlays", "value": f["outlays_usd_billions"], "color": "deemph",
                      "segments": [{"name": "Paid by revenue", "value": f["revenue_usd_billions"], "color": "teal"},
                                   {"name": "Borrowed", "value": f["deficit_usd_billions"], "color": "crimson"}]}]}


def _stacked_page(series: dict, emphasize: int | None, title: str) -> tuple[dict, dict]:
    """A stacked page through the compiler's own path: validated, built, stamped full stage."""
    import build_scene_timeline_f as BST
    assert LPG.validate(series, "bars") == [], LPG.validate(series, "bars")
    page = BST.stamp_full_stage(LPG.build_spec(series, "bars", emphasize, "right"))
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    BST.check_segments(world, [])
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline(title, scenes, {}, None), _base_uris()


def stacked_combo_funding() -> tuple[dict, dict]:
    return _stacked_page(stacked_funding_series(), None,
                         "Golden: stacked bars of operating cash with the capex share on its own labelled axis")


def stacked_outlays() -> tuple[dict, dict]:
    return _stacked_page(stacked_outlays_series(), 0, "Golden: one stacked bar - what revenue paid for, what was borrowed")


SURFACES.update({"stacked-combo-funding": stacked_combo_funding, "stacked-outlays": stacked_outlays})
FRAME_T.update({"stacked-combo-funding": 12.0,   # the stacks stood (7.4), the line drawn and its three shares written, held
                "stacked-outlays": 12.0})        # the bar stood, both parts' figures, the total's pill and the key written, held


# ---- P70 T4 (was P69 T52; harvest v2 T39): COMPANION BARS BESIDE A HELD LINE --------------------------------------------
#   companion-railway-yardstick  Steel and Paper H row 14's yardstick as a PANELS page that stands as its LINE alone
#                     (tech's share of all US private investment, quarterly since 1970; the bars panel hidden), then on
#                     "railways took roughly half" a `row` focus state makes both panels active: the line shrinks into
#                     its slot and the bars build beside it - Britain's railways at ~50 against US tech's 28 - on the
#                     line's ONE scale (E79 apply 1: one measure, one unit); on "closest run" the line stands alone again
# READ from two committed objects, never re-typed: `ev-capital-formation-v1` (panel 0; its railway hline is dropped
# because the bars panel carries the 50 - a value is drawn once, E53 addendum) and `ev-rail-vs-yardstick-bars-v1`
# (panel 1), RE-EXPRESSED in the line's unit: cents per dollar ARE percent, so 50 and 28 carry over unchanged and the
# source line says so (our arithmetic, E77). Its `domain` and `overflow: burst` stay off (a panel's scale is its unit
# group's, E79). Both panels name the one `measure` (the line's own ylabel); compiled WITHOUT the re-expression ("¢"
# bars) the page prints the E79 / E53 s4 WARN, with it none. The world carries the row's `idle=live`; the golden is
# drawn in the PLAIN profile, as every panels golden is - the row's `;readability=longform` would inline the 1.17 MB
# long-form face into the committed uris - and `test_companion_bars` plays the same page long-form for the s90 floor.
# The golden's clock is the take's shifted by COMPANION_SHIFT: the reveal at 9.0 (the line alone has built by
# 4.4 + 3.0 = 7.4, as on `panels-resize`) and the leave 7.2 s later, as spoken.
COMPANION_OBJECTS = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects"
COMPANION_LINE = COMPANION_OBJECTS / "ev-capital-formation-v1.series.json"
COMPANION_BARS = COMPANION_OBJECTS / "ev-rail-vs-yardstick-bars-v1.series.json"
COMPANION_SHIFT = 176.16   # vo-h-scratch/scratch-kokoro.words.json: "railways" 185.16 -> 9.0 on the golden's clock
COMPANION_REVEAL_AT = round(185.16 - COMPANION_SHIFT, 2)   # "railways took roughly half"
COMPANION_LEAVE_AT = round(192.36 - COMPANION_SHIFT, 2)    # "... and this is the closest run at it"
COMPANION_DUR = 1.2                                          # the focus move (T8c's panels-resize dur)
COMPANION_UNITS = ("¢", "%")   # the bars object's unit and the line's: cents per dollar written as percent


def companion_series(re_express: bool = True) -> dict:
    """The companion page's panels object, composed from the two committed objects. `re_express=False` keeps the bars
    in the object's own cents - one measure in two units, the page E79 / E53 s4 WARNs on."""
    line, bars = LPG.load_series(COMPANION_LINE), LPG.load_series(COMPANION_BARS)   # the tokens verbatim, as a door reads them
    measure = line["ylabel"]
    unit = line["yunit"] if re_express else bars["unit"]
    cents, pct = COMPANION_UNITS
    bar_rows = [dict(b, note=b["note"].replace(cents, pct)) if re_express else dict(b) for b in bars["bars"]]
    src = line["src"] + ("; cents per dollar written as percent: our arithmetic" if re_express else "")
    return {"title": line["title"], "sub": line["sub"], "src": src, "yunit": line["yunit"],
            "ymin": line["ymin"], "ymax": line["ymax"], "xticks": line["xticks"],
            "panels": [
                {"sub": "US computing and software, quarterly since 1970", "measure": measure,
                 "ylabel": line["ylabel"], "marks": line["marks"], "series": line["series"]},
                {"sub": "One technology at its peak, against tech today", "builder": "bars", "unit": unit,
                 "measure": measure, "bars": bar_rows}]}


COMPANION_FOCUS = [
    {"kind": "panel_focus", "at": 0.0, "dur": 0.05, "layout": "row", "roles": ["active", "hidden"]},       # the line alone
    {"kind": "panel_focus", "at": COMPANION_REVEAL_AT, "dur": COMPANION_DUR, "layout": "row", "roles": ["active", "active"]},
    {"kind": "panel_focus", "at": COMPANION_LEAVE_AT, "dur": COMPANION_DUR, "layout": "row", "roles": ["active", "hidden"]},
]


def companion_page(re_express: bool = True, longform: bool = False) -> tuple[dict, list]:
    """(the world, its species) through the compiler's own doors: validated, built, stamped full stage (drawn in the
    row's long form when `longform`, as the row path applies it), then `derive_rescale_states` (which runs
    `check_panels` and normalises every focus state)."""
    import build_scene_timeline_f as BST
    series = companion_series(re_express)
    assert LPG.validate(series, "line") == [], LPG.validate(series, "line")
    species = [dict(e) for e in COMPANION_FOCUS]
    plate = "ledger:golden-panels:line"
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        page = BST.stamp_full_stage(LPG.build_spec(series, "line", None, "right"))
        if longform:
            LPG.apply_longform(page, LPG.parse_readability(LPG.LONGFORM)[1])   # the row's `;readability=longform`
        world = {"kind": "ledger", "page": page, "idle": "live", "ken_burns": {"scale": 0, "x": 0, "y": 0}}
        BST.derive_rescale_states(world, species, plate, REPO)
    finally:
        BST.ASPECT = saved
    return world, species


def companion_railway_yardstick() -> tuple[dict, dict]:
    world, species = companion_page()
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: companion bars beside the held line - one measure, one unit", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"companion-railway-yardstick": companion_railway_yardstick})
FRAME_T.update({"companion-railway-yardstick": 14.5})   # both panels active, the bars built on their word (9.0) and valued, held


# P71 T11 (was P69 T43): THE LOOP - a flow laid as a RING, money moving on its arrows (the Bravos loop BUB frame_0058 / RST
# 9:30; A27's tokens DOM 03:30, BOOM 08:19). A TEST-BED beat, labelled as one: H row 16 ("who is paying") is the
# candidate the parent confirms on the frame; no H row adopts the move before HG1 (rule f).
LOOP_NODES = [("lenders", "landmark", "LENDERS"), ("builders", "factory", "BUILDERS"),
              ("chips", "cpu", "CHIPS"), ("profits", "coins", "PROFITS")]
LOOP_AT, LOOP_TOKENS_AT = 4.0, 7.2   # the four arrows are drawn by 7.105 s (flowClock); the money starts on the next word


def flow_loop_tokens() -> tuple[dict, dict]:
    """P71 T11: four nodes on the ring inscribed in the box - the first at 12 o'clock, clockwise - their four clothoid
    arrows leaving each card along the ring, and from `tokens.from_at` two plain DOTS in the arrow's ink riding every
    arrow by arc length (A2a: never a generated coin). Judged mid-run (FRAME_T 9.0: 1.8 s of travel)."""
    import build_scene_timeline_f as BST
    ids = [n[0] for n in LOOP_NODES]
    species = [{"kind": "flow", "at": LOOP_AT, "dur": 18.0, "idle": "breath", "layout": "ring",
                "target": {"kind": "region", "x0": 0.68, "y0": 0.06, "x1": 0.98, "y1": 0.94},   # the right third, clear of the golden's centred caption: a loop beside where a chart parks
                "nodes": [{"id": i, "icon": icon, "label": label} for i, icon, label in LOOP_NODES],
                "edges": [[a, b] for a, b in zip(ids, ids[1:] + ids[:1])],
                "tokens": {"from_at": LOOP_TOKENS_AT, "n": 2}}]
    assert not BST.validate_species(species, (0, 0, 0), "plate-plain"), BST.validate_species(species, (0, 0, 0), "plate-plain")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    for name in sorted(BST.species_icons(species[0])):
        uris[BST.ICON_PREFIX + name] = BST.icon_geometry(name)
    return _timeline("Golden: the loop - a flow laid as a ring, tokens on its arrows (test-bed beat)", scenes, {}, None), uris


SURFACES.update({"flow-loop-tokens": flow_loop_tokens})
FRAME_T.update({"flow-loop-tokens": 9.0})   # the loop drawn (7.105), the tokens 1.8 s into their run - mid-run on every arrow


# ---- P71 T9 (was P69 T38): THE AXIS TAG - the named year becomes an accent pill on the x axis ---------------------------
# Steel and Paper H row 9's own page, the one its door recasts to on "the internet": `ev-equip-ipp-gdp-v2` (v1's data,
# byte for byte, with the decade x ticks R26-262 added - v1 has no x ticks, so 2000 is only a TICK on v2), full stage,
# 16:9, live. The H take's words, shifted by -70.49 s so the page has built first: "the internet crossed" 80.49 -> 10.00
# (the GDP page is on screen from that word; "two thousand" at 79.80 is spoken over the railway page, which has no
# 2000), to "seven percent"'s start 81.42 -> 10.93. The tag names 2000 - a tick AND the series' Q1-2000 datum (index
# 120, 11.494 %) - so the "2000" tick springs into the pill and the dotted guide drops to it from that datum. The
# object is the COMMITTED evidence sidecar, read in place. Judged at 80.49 + 0.4 s (the plan's instant): the pill and
# its guide have landed (POP_S 0.25; GUIDE_AT 0.1 + GUIDE_S 0.28), the 2000 tick is under the pill, 1990 and 2010 stand.
AXTAG_PROJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
AXTAG_PLATE = "ledger:ev-equip-ipp-gdp-v2:line:225:right;idle=live"
AXTAG_AT, AXTAG_DUR = 10.0, 0.93
AXTAG_SPECIES = [{"kind": "axis_tag", "at": AXTAG_AT, "dur": AXTAG_DUR, "x": 2000}]


def axis_tag_two_thousand() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    species = [dict(e) for e in AXTAG_SPECIES]
    assert not BST.validate_species(species, (0, 0, 0), AXTAG_PLATE), BST.validate_species(species, (0, 0, 0), AXTAG_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(AXTAG_PLATE, (0, 0, 0), AXTAG_PROJECT)
        BST.stamp_full_stage(world["page"])
        assert BST.check_axis_tags(world, species) == [], "2000 is a tick and a datum of the page: no finding"
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the named year becomes a pill on the axis (axis_tag)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"axis-tag-two-thousand": axis_tag_two_thousand})
FRAME_T.update({"axis-tag-two-thousand": round(AXTAG_AT + 0.4, 3)})   # the plan's 80.49 + 0.4 s: pill and guide landed


# ---- P71 T10 (was P69 T39; harvest v2 A9): THE LEVEL JOIN - a dashed level from one datum to another --------------------
#   level-join-half-a-point  Steel and Paper H row 14's yardstick page (`ledger:ev-capital-formation-v1:line:225:right`,
#                     `idle=live`, full stage, 16:9, the PLAIN profile - the row's `;readability=longform` would inline the
#                     1.17 MB long-form face into the committed uris, so `test_level_join` plays the same page long-form for
#                     the s90 floor) and its own sentence: "At the dot-com peak it hit twenty-three cents on the dollar.
#                     Today it's twenty-eight, the most it has ever been." The take's words shifted by -170.0 s so the page
#                     has built first, as the row builds it (the scale line held at nothing, the tech line climbing to the
#                     dot-com peak on "hit", the page's own 23% written there on "twenty-three", the last twenty-five years
#                     drawn on "Today it's" landing on "twenty-eight"); then on "the most it has ever been" (181.625 -
#                     183.338 -> 11.63 - 13.34) the dashed level runs from the dot-com high (datum 124, 23.028) to today
#                     (datum 225, 28.184), a ring at each end, and "+5 pts" - the page's own arithmetic, 5.156 - is written
#                     beside today's ring, off the rule. The plan's row-15 beat ("the Fed back above five and a half") has no
#                     datum at the level it speaks (5.5 is a rule, not a point), so the golden takes row 14's (the plan's
#                     own fallback); the name is the plan's. Judged at the figure's write end.
LEVEL_PROJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
LEVEL_PLATE = "ledger:ev-capital-formation-v1:line:225:right;idle=live"
LEVEL_SHIFT = 170.0
LEVEL_AT = round(181.625 - LEVEL_SHIFT, 2)                   # "the most it has ever been"
LEVEL_DUR = round(183.338 - 181.625, 2)                      # ... to the end of "been."
LEVEL_SPECIES = [
    {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": {"kind": "datum", "index": 0}},    # the page lands on its axes
    {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 1, "target": {"kind": "datum", "index": 0}},    # the scale line held at nothing
    {"kind": "build_to", "at": 2.0, "dur": round(178.512 - LEVEL_SHIFT - 2.0, 2), "series": 0,
     "target": {"kind": "datum", "index": 124}},                                                          # the pen climbs to the dot-com peak on "hit"
    {"kind": "figure", "at": round(178.512 - LEVEL_SHIFT, 2), "dur": 1.4, "target": {"kind": "datum", "index": 124, "series": 0},
     "text": "23%"},                                                                                      # "twenty-three": the object's own mark
    {"kind": "build_to", "at": round(180.438 - LEVEL_SHIFT, 2), "dur": 0.5, "series": 0,
     "target": {"kind": "datum", "index": 225}},                                                          # "Today it's" -> "twenty-eight"
    {"kind": "level_join", "at": LEVEL_AT, "dur": LEVEL_DUR, "from": 124, "to": 225, "label": "+5 pts"},   # "the most it has ever been"
]


def level_join_half_a_point(extra: list | None = None, longform: bool = False) -> tuple[dict, dict]:
    """The golden's timeline; `extra` species (a probe's rescale or undraw) and `longform` (the row's own profile) are for
    test_level_join's reads only - the committed golden is the plain call."""
    import build_scene_timeline_f as BST
    species = [dict(e) for e in LEVEL_SPECIES] + [dict(e) for e in (extra or [])]
    plate = LEVEL_PLATE + (";readability=longform" if longform else "")
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(plate, (0, 0, 0), LEVEL_PROJECT)
        BST.stamp_full_stage(world["page"])
        BST.derive_rescale_states(world, species, plate, LEVEL_PROJECT)   # the compiler's own page checks: check_level_join's truth
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: a dashed level from the dot-com high to today (level_join)", scenes, {}, "16:9")
    return tl, (dict(_base_uris(), **BST.longform_assets(tl)) if longform else _base_uris())


SURFACES.update({"level-join-half-a-point": level_join_half_a_point})
FRAME_T.update({"level-join-half-a-point": round(LEVEL_AT + LEVEL_DUR, 2)})   # the figure's write end: 13.34


# ---- P71 T32 (was P69 T80; harvest v2 A57): THE LENS - a magnifier glass travels to the soft month --------------------
#   lens-over-the-line  Steel and Paper H row 22's long customs line - the memory monitor's COMMITTED source object
#                     (`ledger:ev-memory-monitor-v1:line:42:right`, `idle=live`, full stage, 16:9, the plain profile; H's
#                     row page is the derived `ev-memory-monitor-row22-v1`, DRAM and HBM-CLASS verbatim, which lives in
#                     lane A: the source carries the same two lines and its dashed TRIGGER beside them). 43 monthly
#                     prints on a log scale from $7.6k to $95k/kg, and the sentence "one soft month in June" (652.69 -
#                     653.73 in the H take, shifted by -640.0 s so the page has built first): the June print is 74,686
#                     against May's 77,558, -3.7 % - on this scale a step of about a hundredth of the plot's height.
#                     On the word the glass rises onto the May print (datum 40), travels to June (41) and leaves before
#                     the row's recast (655.31), magnifying 2x (the row's authored zoom; Bravos's own glass is 1.0,
#                     measured). Judged mid-travel: the glass between May and June, the dip twice its size inside.
LENS_PLATE = "ledger:ev-memory-monitor-v1:line:42:right;idle=live"
LENS_SHIFT = 640.0
LENS_AT = round(652.69 - LENS_SHIFT, 2)                       # "one soft month in June"
LENS_DUR = round(655.31 - 0.1 - 652.69, 2)                    # ... to 0.1 s before the row's recast (the trim proof)
LENS_SPECIES = [
    {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": si, "target": {"kind": "datum", "index": 42}} for si in (0, 1, 2)
] + [{"kind": "lens", "at": LENS_AT, "dur": LENS_DUR, "series": 0, "from": 40, "to": 41, "zoom": 2}]


def lens_over_the_line() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    species = [dict(e) for e in LENS_SPECIES]
    assert not BST.validate_species(species, (0, 0, 0), LENS_PLATE), BST.validate_species(species, (0, 0, 0), LENS_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(LENS_PLATE, (0, 0, 0), LEVEL_PROJECT)
        BST.stamp_full_stage(world["page"])
        assert BST.check_lens(world, species) == []   # the compiler's own page check: a line page, data it has
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: a magnifier glass travels to the soft month (lens)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"lens-over-the-line": lens_over_the_line})
FRAME_T.update({"lens-over-the-line": round(LENS_AT + 0.25 + (LENS_DUR - 0.25 - 0.3) / 2, 3)})   # mid-travel (LENS.IN_S / OUT_S): 13.925


# ---- P70 T3 (was P69 T51): THE FILL GAUGE - one share of one whole fills a capsule -----------------------------------
#   gauge-94   Steel and Paper H row 17's own object, READ where it is committed (`ev-capex-ocf-94-bars-v1`: PIMCO Fig. 3,
#              94 % of operating cash flow, the 100 rule named "every dollar from operations"), compiled as the PROGRESS
#              page with `;form=gauge` through the compiler's own world_for_plate: the capsule IS the whole, the fill
#              stands at 94 of it, the figure written at the fill line in the bar's ink. Flat type (the long form's face
#              would put the 0.9 MB Inter file in the uris; the long form + bar_style=soft composition is held by
#              test_fill_gauge on the served player). Read at the HOLD (9.0: the build lands ~5.9 s).
GAUGE_PLATE = "ledger:ev-capex-ocf-94-bars-v1:progress::right;form=gauge"


def gauge_94() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(GAUGE_PLATE, (0, 0, 0), LIT_PROJECT)
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: the fill gauge - 94 of every dollar from operations", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"gauge-94": gauge_94})
FRAME_T.update({"gauge-94": 9.0})


# ---- P72 T6 (R26-319): THE HORIZONTAL FILL GAUGE - the same 94 page, the capsule on its side -----------------------
#   gauge-94-h  gauge-94's object and page under `;form=gauge:h`: the capsule lies from 0 at its left to the whole at its
#               right, filled to 94 of it; "0%" and "100%" over the stubs above it, the category naming it from its left,
#               the whole ("every dollar from operations") past the ceiling, "94%" under the fill's end in the bar's ink.
#               Flat type, as gauge-94's. Read at the HOLD (9.0), where M26 reads the fill as a WIDTH.
GAUGE_H_PLATE = GAUGE_PLATE + ":h"


def gauge_94_h() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(GAUGE_H_PLATE, (0, 0, 0), LIT_PROJECT)
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: the horizontal fill gauge - 94 of every dollar from operations", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"gauge-94-h": gauge_94_h})
FRAME_T.update({"gauge-94-h": 9.0})


# ---- P70 T2 (was P69 T46) / E99 s109 (1): THE SCHEMATIC - a shape drawn with no data, the light walking peak -> trough --
# Steel and Paper H row 12's sentence: "And that isn't the peak of inflated expectations. It's the trough already doing
# its job" (SHOT-TABLE-H #6, 104.31-147.82). A SCHEMATIC needs no data (s109 (1)): the object is words only - the title,
# the source line naming the model ("Shape: Gartner's hype cycle - a schematic, no data") and Gartner's five phase names
# over x-fractions of the shape - so it is written here, never read from a series on disk; the curve is GENERATED by
# ledger_page.schematic_series. The H take's words (vo-h-scratch/scratch-kokoro.words.json), shifted by -124.0 s so the
# page has built first: "peak" 133.688 -> 9.688, "expectations." ends 136.100 -> 12.100, and "It's the trough" 136.100-
# 136.838 -> 12.100-12.838 - the light leaves the PEAK (the shape's highest point) and walks to the TROUGH (its lowest
# after the peak) on those words, the lit_stretch's two x-fractions read off the generated curve, never typed. The page
# is H's own form - full stage, `idle=live` - in the ledger's own face (a `;readability=longform` row is proved on the
# served player by test_schematic_page; its 1.17 MB face is not carried in a golden's uris). Judged mid-walk (u 0.50 of
# the head's run): no number anywhere on the page, the tag under the axis, the five phases named in the line's ink, the
# comet half way down from the peak.
SCHEMATIC_ID = "ev-hype-cycle-schematic"
SCHEMATIC_PLATE = f"ledger:{SCHEMATIC_ID}:line::right;idle=live"
SCHEMATIC_OBJECT = {
    "title": "The hype cycle",
    "sub": "How a new technology's reputation moves - a model, not a measurement",
    "src": "Shape: Gartner's hype cycle - a schematic, no data",
    "ylabel": "Expectations",
    "schematic": {"shape": "hype", "phases": [   # Gartner's five phases by their short names: at the s90 floor (59 px) the
        {"name": "Trigger", "from": 0.0, "to": 0.12},   # full names are five two-line blocks - s120 (3): few words on the plot
        {"name": "Peak of inflated expectations", "from": 0.12, "to": 0.3},   # ... but the one the sentence SAYS, whole
        {"name": "Trough", "from": 0.3, "to": 0.48},
        {"name": "Slope", "from": 0.48, "to": 0.72},
        {"name": "Plateau", "from": 0.72, "to": 1.0}]},
}
SCHEMATIC_SHIFT = -124.0
SCHEMATIC_LIT_AT, SCHEMATIC_LIT_DUR = round(136.100 + SCHEMATIC_SHIFT, 3), round(136.838 - 136.100, 3)   # "It's the trough"


def schematic_peak_trough() -> tuple[float, float]:
    """The generated curve's peak x and the lowest x after it - where the light leaves and where it lands."""
    pts = LPG.schematic_series(SCHEMATIC_OBJECT["schematic"])["pts"]
    peak = max(pts, key=lambda p: p[1])
    trough = min((p for p in pts if p[0] > peak[0]), key=lambda p: p[1])
    return float(peak[0]), float(trough[0])


def schematic_species() -> list[dict]:
    peak, trough = schematic_peak_trough()
    return [{"kind": "lit_stretch", "at": SCHEMATIC_LIT_AT, "dur": SCHEMATIC_LIT_DUR, "from": peak, "to": trough, "comet": True}]


def schematic_hype_trough() -> tuple[dict, dict]:
    """P70 T2: the hype cycle drawn with no data through the compiler's own path (validated, built, stamped, checked)."""
    import tempfile
    import build_scene_timeline_f as BST
    species = schematic_species()
    assert not BST.validate_species(species, (0, 0, 0), SCHEMATIC_PLATE), BST.validate_species(species, (0, 0, 0), SCHEMATIC_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{SCHEMATIC_ID}.series.json").write_text(json.dumps(SCHEMATIC_OBJECT), encoding="utf-8")
            world = BST.world_for_plate(SCHEMATIC_PLATE, (0, 0, 0), Path(td))
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    BST.check_schematic(world, species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the hype cycle drawn with no data, the light walking from the peak to the trough (schematic)",
                     scenes, {}, "16:9"), _base_uris()


SURFACES.update({"schematic-hype-trough": schematic_hype_trough})
FRAME_T.update({"schematic-hype-trough": round(SCHEMATIC_LIT_AT + 0.5 * SCHEMATIC_LIT_DUR * 0.8, 3)})   # u 0.50 of the head's run (TRAVEL 0.8): 12.395


# ---- P71 T20 (was P69 T62) / E99 s109 (1): ILLUSTRATIONS DRAWN AS SCHEMATICS ----------------------------------------------
#   schematic-candles  THE CANDLES (the Bravos harvest v2 T8, BUB 04:47.3 "The stock can theoretically go up and up and
#                      up"): a TEST-BED beat - T8 serves no H row (BRAVOS-USE-WHEN :574), so it is built for the catalogue
#                      on s109 (1). The page draws the ghost wave to its first peak on the build, and the rest of it on
#                      the word (8.0 s, 2.4 s); each candle prints as the pen crosses it. Judged half way through the
#                      word: the candles along the wave up to the pen and none past it, green up / red down, the ghost
#                      grey and unbloomed, no number anywhere, the tag under the axis.
#   schematic-motif    THE MOTIF (T46, JPN 09:09 "Market") with an X at each named vertex (A14): H row 24's words - "More
#                      bullish: builders with sold-out order books are not a house of cards" - shifted by -710.0 s so the
#                      page has built first; on "not" (719.55 -> 9.55) an X lands on each of the rising wave's four
#                      TROUGHS, left to right (the dips were not the collapse the sentence refuses). One word names the
#                      line ("Memory", the page's title); no axis rule, no tick, no label; the tag stays. Judged with every
#                      X struck and settled.
CANDLES_ID = "ev-candles-schematic"
CANDLES_PLATE = f"ledger:{CANDLES_ID}:line::right;idle=live"
CANDLES_OBJECT = {
    "title": "Price action",
    "sub": "How a stock moves - an illustration, not a chart",
    "src": "Shape: candlesticks along a wave - a schematic, no data",
    "schematic": {"shape": "candles"},
}
CANDLES_WORD_AT, CANDLES_WORD_DUR = 8.0, 2.4   # the test-bed's word: the rest of the wave draws, and its candles print


def schematic_candles() -> tuple[dict, dict]:
    """P71 T20: the candles along the ghost wave, through the compiler's own path (validated, built, stamped, checked)."""
    import tempfile
    import build_scene_timeline_f as BST
    peak = LPG.schematic_vertices(CANDLES_OBJECT["schematic"])[0]   # the ghost's first peak - where the build beat stops
    last = len(LPG.schematic_series(CANDLES_OBJECT["schematic"])["pts"]) - 1
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": {"kind": "datum", "index": peak}},
               {"kind": "build_to", "at": CANDLES_WORD_AT, "dur": CANDLES_WORD_DUR, "series": 0,
                "target": {"kind": "datum", "index": last}}]
    assert not BST.validate_species(species, (0, 0, 0), CANDLES_PLATE), BST.validate_species(species, (0, 0, 0), CANDLES_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{CANDLES_ID}.series.json").write_text(json.dumps(CANDLES_OBJECT), encoding="utf-8")
            world = BST.world_for_plate(CANDLES_PLATE, (0, 0, 0), Path(td))
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    BST.check_schematic(world, species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: candlesticks printed along a ghost wave, a shape and not a series (schematic, test-bed)",
                     scenes, {}, "16:9"), _base_uris()


MOTIF_ID = "ev-memory-motif"
MOTIF_PLATE = f"ledger:{MOTIF_ID}:line::right;idle=live"
MOTIF_OBJECT = {
    "title": "Memory",
    "src": "Shape: a rising wave - a schematic, no data",
    "schematic": {"shape": "motif"},
}
MOTIF_SHIFT = -710.0
MOTIF_BADGE_AT = round(719.55 + MOTIF_SHIFT, 3)           # "not" (H take 719.55)
MOTIF_BADGE_DUR = round(720.925 - 719.55, 3)             # "not a house of cards." (719.55-720.925, the H take)
MOTIF_VERTICES = [1, 3, 5, 7]                            # the four troughs (vertex 0 is the first peak)


def schematic_motif() -> tuple[dict, dict]:
    """P71 T20: the axis-free motif with an X on each named vertex, through the compiler's own path."""
    import tempfile
    import build_scene_timeline_f as BST
    species = [{"kind": "datum_badge", "at": MOTIF_BADGE_AT, "dur": MOTIF_BADGE_DUR, "glyph": "cross",
                "target": [{"kind": "vertex", "index": k} for k in MOTIF_VERTICES]}]
    assert not BST.validate_species(species, (0, 0, 0), MOTIF_PLATE), BST.validate_species(species, (0, 0, 0), MOTIF_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{MOTIF_ID}.series.json").write_text(json.dumps(MOTIF_OBJECT), encoding="utf-8")
            world = BST.world_for_plate(MOTIF_PLATE, (0, 0, 0), Path(td))
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    BST.check_datum_badge(world, species)
    BST.check_schematic(world, species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the axis-free motif, an X landing on each named trough (schematic + datum_badge)",
                     scenes, {}, "16:9"), _base_uris()


SURFACES.update({"schematic-candles": schematic_candles, "schematic-motif": schematic_motif})
FRAME_T.update({"schematic-candles": round(CANDLES_WORD_AT + 0.125 * CANDLES_WORD_DUR, 3),   # an eighth into the word (the pen law is front-loaded - 22 of 30 printed): 8.3
                "schematic-motif": round(MOTIF_BADGE_AT + 1.25, 3)})                        # every X struck and settled: 10.8


# ---- P71 T39 (was P69 T46 (3)) / E99 s125: THE SHAPE MEETS THE DATA - a real series laid over a schematic -----------------
#   schematic-meets-the-data  A TEST-BED beat, labelled REFERENCE: H row 12's trough sentence ties no committed measured
#                             series to the shape (SCRIPT-H-VO.txt :27 - its trough is the AI budgets, in words), so the
#                             beat lays a SOURCED series from disk over P70 T2's own hype cycle (SCHEMATIC_OBJECT, read):
#                             the Campbell & Turner railway index, 1843-1850 (ev-railway-index-v1 - its points, its source,
#                             its ink, its unit's words and its dates READ from the committed object, never re-typed), on its
#                             own right axis and its own dates. The claim sits at the shape's own TROUGH (read off the
#                             generated curve, schematic_peak_trough) in the script's own words for the railway's fall
#                             (SCRIPT-H-VO.txt :21, "crashed by nearly two-thirds"). The shape builds with the page; the
#                             index draws on its word (8.0 s over 2.4 s, the T20 test bed's word) and the claim lands at
#                             11.0 s. Judged 1.0 s after the claim: the shape tagged "a shape, not a series", its phases,
#                             the measured line on its own labelled axis and dates, the ring on the trough with its words.
MEETS_ID = "ev-hype-meets-railway"
MEETS_PLATE = f"ledger:{MEETS_ID}:line::right;idle=live"
MEETS_SERIES = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-railway-index-v1.series.json"
MEETS_OVERLAY_AT, MEETS_OVERLAY_DUR = 8.0, 2.4   # the test bed's word: the measured line draws over the standing shape
MEETS_CLAIM_AT = 11.0                            # ... and then the claim, on its own word
MEETS_CLAIM_TEXT = "crashed by nearly two-thirds"   # SCRIPT-H-VO.txt :21 - the railway's own words
MEETS_UNIT = "pts"                               # an index is read in points (the object's sub: "January 1843 = 1,000")
MEETS_PHASES = ("Peak of inflated expectations", "Trough")   # the two phases the beat names (s120 (3): few words on the plot)


def meets_object() -> dict:
    """P70 T2's hype cycle with the railway index laid over it - the index's points, source, ink, label and dates read from
    the committed object."""
    rail = json.loads(MEETS_SERIES.read_text(encoding="utf-8"))
    ser = rail["series"][0]
    obj = json.loads(json.dumps(SCHEMATIC_OBJECT))
    obj["sub"] = "A model of reputation, and the railway mania measured over it - a reference beat"
    obj["schematic"]["phases"] = [p for p in obj["schematic"]["phases"] if p["name"] in MEETS_PHASES]   # s120 (3): the two it names
    obj["schematic"]["overlay"] = {
        "series": {"name": "Railway shares", "pts": ser["pts"], "src": rail["src"], "tier": "CONFIRMED", "color": ser["color"]},
        "axis": {"unit": MEETS_UNIT, "label": rail["ylabel"]}, "xticks": rail["xticks"],
        "at": MEETS_OVERLAY_AT, "dur": MEETS_OVERLAY_DUR,
        "claim": {"at": MEETS_CLAIM_AT, "x": schematic_peak_trough()[1], "text": MEETS_CLAIM_TEXT}}
    return obj


def schematic_meets_the_data() -> tuple[dict, dict]:
    """P71 T39: a measured series over the hype cycle on its own axes, and the claim of where it sits (s125)."""
    import tempfile
    import build_scene_timeline_f as BST
    species: list = []
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{MEETS_ID}.series.json").write_text(json.dumps(meets_object()), encoding="utf-8")
            world = BST.world_for_plate(MEETS_PLATE, (0, 0, 0), Path(td))
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    BST.check_schematic(world, species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: a measured series laid over the hype cycle on its own axes, the claim at the trough (reference)",
                     scenes, {}, "16:9"), _base_uris()


SURFACES.update({"schematic-meets-the-data": schematic_meets_the_data})
FRAME_T.update({"schematic-meets-the-data": round(MEETS_CLAIM_AT + 1.0, 3)})   # the claim landed and its words written: 12.0


# ---- P70 T13: THE DRIFT-HOLD on a real held card -------------------------------------------------------------------
#   drift-hold-tripwire  Steel and Paper H row 22's board (dock-h-tripwire-board) as the chart card it is: the committed
#                        object's own checklist (ev-tripwire-board-v1 - read, never re-typed), thrown (paper) into the
#                        right 0.60 of the stage exactly as the H row places it (TRIPWIRE_SLOT), holding on `idle: hold`,
#                        which the compiler grades WHISPER (a card carrying a chart). Its held span is the H card's own
#                        length (605.83 -> 615.32 = 9.49 s), and a FREEZE BEAT stops the stage BEFORE the card enters, as
#                        H's 549.12 freeze precedes it: the hold runs on the LIFE clock, so a span handed over in wall
#                        time would be phase-shifted by the frozen 0.7 s - the golden pins the handover. Read at u 0.25
#                        of the hold: the card turned, breathing, the light band across the board's middle columns.
HOLD_CARD_OBJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-tripwire-board-v1.series.json"
HOLD_CARD_SLOT = {"centre": True, "centre_w": 0.60, "centre_x": 0.685, "centre_y": 0.50, "card_aspect": round(480 / 1056, 4)}   # H's TRIPWIRE_SLOT
HOLD_ENTER, HOLD_LEN = 3.0, round(615.32 - 605.83, 2)   # the H card's own held span, 9.49 s
HOLD_FREEZE = {"kind": "freeze", "at": 1.0, "dur": 0.7, "target": {"kind": "region", "x0": 0.05, "y0": 0.2, "x1": 0.3, "y1": 0.6}}   # H's own beat length (0.7 s), before the card


def drift_hold_tripwire() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    card = "ev-golden-tripwire-board"
    chart = json.loads(HOLD_CARD_OBJECT.read_text(encoding="utf-8"))
    evidence = {card: {"title": chart["title"], "source": chart["src"], "species": "chart",
                       "document": {"path": "golden", "sha256": "0" * 64}, "badges": [], "chart": chart}}
    opts = BST.dock_opts(dict(HOLD_CARD_SLOT, arrive="throw", mass="paper", idle="hold"))   # the row's own options, validated
    idle = BST.dock_idle(opts, evidence[card])
    assert idle == "hold:whisper", idle   # a card carrying a chart holds at a whisper
    place = BST.centred_place(None, None, opts["card_aspect"], None, opts["centre_w"], None, opts["centre_y"], opts["centre_x"])
    docks = [BST.dock_entry(card, 0, HOLD_ENTER, HOLD_ENTER + HOLD_LEN, 0, BST.DOCK_KIND_IMAGE, place, opts["arrive"],
                            opts["mass"], True, idle=idle)]
    species = [dict(HOLD_FREEZE)]
    assert not BST.validate_species(species, (0, 0, 0), "plate-plain")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": species}]
    uris = _base_uris()
    uris[card] = uri("image/png", png_solid(64, 29, (22, 24, 28)))   # the static fallback: the card is DRAWN from its object
    tl = _timeline("Golden: the drift-hold on a held chart card", scenes, evidence, None)
    tl["kinetics"] = {"idle": True, "stop_action": True}   # E49 is on for every compiled timeline; the throw is P47 T1's switch
    return tl, uris


SURFACES.update({"drift-hold-tripwire": drift_hold_tripwire})
FRAME_T.update({"drift-hold-tripwire": round(HOLD_ENTER + 0.25 * HOLD_LEN, 4)})   # u 0.25 of the hold (H: 608.20)


# P71 T12 (was P69 T42; A59): THE SELL TAB - H row 10's "sell" (the head-fake: "So the obvious move looks obvious: sell
# the steel", take `sell` 91.72-92.00) on the NVIDIA / hynix chip board (P70 T1's NVIDIA_CHIP, the Lucide `cpu` glyph, as
# the door lands it). The board is recast on the golden's clock (the word at 8.0 = take - 83.72); the tab lands 0.1 s
# into the word, on the badge spring, on ONE chip: SELL in the negative ink on NVIDIA's top edge, its word at the s90
# floor. No H row adopts the move before HG1 (rule f).
STATES_BOARD = [("cpu", "NVIDIA", 0.36), ("cpu", "SK HYNIX", 0.64)]
STATES_SELL_WORD = 8.0
STATES_TAB_AT = round(STATES_SELL_WORD + 0.1, 3)


def chip_states_sell() -> tuple[dict, dict]:
    """P71 T12: two chips land on two words, then on "sell" a SELL tab lands on the first one's top edge. Judged with the
    tab settled on its spring (FRAME_T = tab_at + LAND_S + 0.3), both chips breathing (E49)."""
    import build_scene_timeline_f as BST
    species = [{"kind": "chip", "at": 5.0 + 1.2 * i, "dur": 10.0 - 1.2 * i, "icon": icon, "label": label,
                "idle": "breath", "target": {"kind": "point", "x": x, "y": 0.62}}   # below the caption band, as chip-board's
               for i, (icon, label, x) in enumerate(STATES_BOARD)]
    species[0].update(tab="sell", tab_at=STATES_TAB_AT)
    for sp in species:
        assert not BST.validate_species([sp], (0, 0, 0), "plate-plain"), BST.validate_species([sp], (0, 0, 0), "plate-plain")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    uris[BST.ICON_PREFIX + "cpu"] = BST.icon_geometry("cpu")
    return _timeline("Golden: on 'sell' a SELL tab lands on the chip's edge (P71 T12)", scenes, {}, None), uris


SURFACES.update({"chip-states-sell": chip_states_sell})
FRAME_T.update({"chip-states-sell": round(STATES_TAB_AT + 0.55 + 0.3, 3)})   # the tab settled (LAND_S 0.55) and holding: 8.95


# ---- P71 T14 (was P69 T55; RESCOPED by the BOOM frame verification): THE DECADE RULER - time scrolls past ---------------
#   decade-ruler-scroll  A REFERENCE test-bed beat on a bare dark plate (no approved cut carries it; the parent confirms
#                     an H beat): the witness's own ruler (VERIFY.md row T32, BOOM 05:50.5-05:52.0) - the strip enters at
#                     the right edge on its word (5.0), scrolls 1980 / 1990 past and lands framed on 2000 / 2010 / 2020
#                     at 6.5, walking on the named drift idle - then three chips pop in a ROW ABOVE it, one per word
#                     (the row at 0.22 and the line at the 16:9 default 0.74, the stage caption between them),
#                     (7.0 / 8.0 / 9.0; the chip board's own sourced icons and labels), with no year, no pin, no leader.
#                     Judged when the third chip has landed (9.0 + LAND_S = 9.55): the settled ruler under the chip row,
#                     beside BOOM 05:55.5. Its mid-scroll instant (0.5 s in, beside BOOM 05:51.0) rides PROOF_FRAMES.
DECADE_RULER = {"kind": "ruler", "at": 5.0, "dur": 20.0, "from": 1980, "to": 2030, "settle": [2000, 2010, 2020],
                "idle": "drift"}   # the line at the 16:9 DEFAULT (0.74), not the witness's 0.646: our stage caption's home
                                   # is 432-575 px, so the chips go above it and the ruler's band below it
DECADE_RULER_CHIPS = [("factory", "PLANTS", 0.335), ("ship", "FREIGHT", 0.5), ("cpu", "CHIPS", 0.665)]   # BOOM's row x


def decade_ruler_scroll() -> tuple[dict, dict]:
    """The ruler first (the ground, painted beneath), then the row of chips above it - composed by the author, as the
    recipe `the-decade-ruler` composes them; the ruler draws none of them and dates none of them."""
    import build_scene_timeline_f as BST
    species = [dict(DECADE_RULER)] + [
        {"kind": "chip", "at": 7.0 + i, "dur": 18.0 - i, "icon": icon, "label": label, "idle": "breath",
         "target": {"kind": "point", "x": x, "y": 0.22}}
        for i, (icon, label, x) in enumerate(DECADE_RULER_CHIPS)]
    assert not BST.validate_species(species, (0, 0, 0), "plate-plain"), BST.validate_species(species, (0, 0, 0), "plate-plain")
    assert not BST.ruler_row_advice(species), "no chip over the ruler prints a year"
    assert not BST.ruler_caption_advice(species, "16:9"), "the default line clears the caption's home strip"
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    for icon, _label, _x in DECADE_RULER_CHIPS:
        uris[BST.ICON_PREFIX + icon] = BST.icon_geometry(icon)
    return _timeline("Golden: the decade ruler scrolls, lands, and a row of chips stands above it", scenes, {}, "16:9"), uris


SURFACES.update({"decade-ruler-scroll": decade_ruler_scroll})
FRAME_T.update({"decade-ruler-scroll": 11.0})   # the ruler landed (6.5), the third chip landed (9.55) and at rest

# ---- P70 T6 (was P69 T56): THE EQUATION ROW - the inputs, the relation and the signed result, in spoken order ------------
# Steel and Paper H row 18's own arithmetic, on the halving page it precedes (`bar-value-morph`'s page, HALVING_OBJ - the
# evidence object's values copied as that golden copies them, so no untracked series is read): the bar stands at 20, and
# in the empty band above it the row is built on the take's words, shifted by
# -390.18 s: "At a fifth" 400.18 -> 10.00 ("20%", the page's own figure, `src` + PLAUSIBLE), "fall by half" 402.38 ->
# 12.20 ("−½", the sentence's own "if": a scenario), "erases ten percent" 403.62 -> 13.44 ("−10%", computed
# by the compiler: 20 x -1/2). The "x" springs in just before 12.20, the "=" just before 13.44. Judged at 14.2: all
# five items written whole, the result in the page's neg red. The compare that follows it on H is its own golden.
# Review round (F7, E28 - the label is data): each term and the result carry a caption naming the number, under it at
# the floor in the page's quiet ink. The labels take a line of their own, so the `figure` bar-value-morph writes at the
# bar's top is left off here (the review's frame note: the same number twice in one column); the region is the band
# between the subtitle and the bar's own "20%" (its `note`), which a labelled row at the floor just fits.
EQUATION_SHIFT = 390.18
EQUATION_TERMS = [
    {"text": "20%", "value": 20, "at": round(400.18 - EQUATION_SHIFT, 2), "src": "ev-index-concentration-bars-v1",
     "tier": "PLAUSIBLE", "label": "AI's weight"},
    {"text": "−½", "value": -0.5, "at": round(402.38 - EQUATION_SHIFT, 2), "tier": "scenario", "label": "a halving"},
]
EQUATION_RESULT = {"text": "−10%", "value": -10, "at": round(403.62 - EQUATION_SHIFT, 2), "label": "the index"}
EQUATION_SPECIES = [
    {"kind": "equation", "at": EQUATION_TERMS[0]["at"], "dur": 6.0,
     "target": {"kind": "region", "x0": 0.06, "y0": 0.13, "x1": 0.72, "y1": 0.296},   # the band between the subtitle and the bar's own "20%"
     "terms": EQUATION_TERMS, "ops": ["×"], "result": EQUATION_RESULT},
]


def equation_halving() -> tuple[dict, dict]:
    import tempfile
    import build_scene_timeline_f as BST
    plate = "ledger:fx-index-concentration-bars:bars"
    species = json.loads(json.dumps(EQUATION_SPECIES))
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    assert BST.equation_advice(species[0]) == [], BST.equation_advice(species[0])   # named, a word apart: no WARN
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/fx-index-concentration-bars.series.json").write_text(json.dumps(HALVING_OBJ), encoding="utf-8")
        saved = BST.ASPECT
        BST.ASPECT = "16:9"
        try:
            world = BST.world_for_plate(plate, (0, 0, 0), ep)
            BST.stamp_full_stage(world["page"])
        finally:
            BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the equation row - a fifth, halved, erases ten percent", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"equation-halving": equation_halving})
FRAME_T.update({"equation-halving": 14.2})   # the result written whole (13.44 + WRITE_S x 0.69) and the "=" landed

# ---- P70 T5 (was P69 T58; harvest v2 T24, Bravos RST 05:40): THE DECOMPOSITION BRACE - one total braced into its parts --
#   brace-funding     Steel and Paper H row 17 (SHOT-TABLE-H #12): the Q1 2026 bar of T64's `stacked-combo-funding` - the
#                     five biggest builders' cash from operations, stacked into cash capex and what was left - on a BARS
#                     page of its own (the combo's share line is not this beat's). READ through `stacked_funding_series()`
#                     (ev-capex-funding-v1's two filed series; "Left over" is their arithmetic, as the source line says),
#                     never re-typed. The take (vo-h-scratch/scratch-kokoro.words.json) shifted by BRACE_SHIFT so the page
#                     has built first (its bars grow 4.4-7.4 s): the brace draws on "every dollar these companies generate
#                     from operations." (329.025-332.212) and writes the whole's name; "Left over" is written on
#                     "investing its surplus" (334.10 - the plan's 333.45 is "not", the clause's first word; the name
#                     lands on the word that means it) and "Cash capex" on "spending all of it" (336.325). Judged once
#                     both names are written and the key has handed them over.
BRACE_SHIFT = 321.0
BRACE_AT = round(329.025 - BRACE_SHIFT, 2)                   # "every dollar these companies generate from operations."
BRACE_DUR = round(332.212 - 329.025, 2)                      # ... to the end of "operations."
BRACE_PARTS_AT = [round(336.325 - BRACE_SHIFT, 2),           # part 0, Cash capex: "spending all of it"
                  round(334.10 - BRACE_SHIFT, 2)]            # part 1, Left over: "investing its surplus"
BRACE_SPECIES = [{"kind": "bracket", "form": "brace", "at": BRACE_AT, "dur": BRACE_DUR, "bar": 0,
                  "label": "Cash from operations", "parts_at": BRACE_PARTS_AT}]


def brace_funding_series() -> dict:
    """The Q1 2026 bar of `stacked_funding_series()`, alone on a bars page: its title and sub say what it is."""
    s = stacked_funding_series()
    return {"title": "Spending all of it",
            "sub": "The five biggest builders' cash from operations, first quarter of 2026: what capital spending took, "
                   "and what was left",
            "src": s["src"], "unit": s["unit"], "ylabel": s["ylabel"], "bars": [s["bars"][-1]]}


def brace_funding(extra: list | None = None, longform: str | None = None) -> tuple[dict, dict]:
    """The golden's timeline; `extra` species (a probe's park) and `longform` (a preset: the row's own `middle`, or
    `phone`) are for test_decomposition_brace's reads only - the committed golden is the plain call."""
    import build_scene_timeline_f as BST
    series = brace_funding_series()
    assert LPG.validate(series, "bars") == [], LPG.validate(series, "bars")
    species = [dict(e) for e in BRACE_SPECIES] + [dict(e) for e in (extra or [])]
    plate = "ledger:golden-brace:bars"
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        page = BST.stamp_full_stage(LPG.build_spec(series, "bars", None, "right"))
        if longform:
            LPG.apply_longform(page, longform)   # the row's `;readability=longform[:<preset>]`
        world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
        BST.check_segments(world, species)
        BST.check_brace(page, species)   # the compiler's own truth: the bar has parts, the label names its whole
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: one total braced into its named parts (bracket form=brace)", scenes, {}, "16:9")
    return tl, (dict(_base_uris(), **BST.longform_assets(tl)) if longform else _base_uris())


SURFACES.update({"brace-funding": brace_funding})
FRAME_T.update({"brace-funding": round(BRACE_PARTS_AT[0] + 1.0, 2)})   # both names written (the last at 15.33), the key handed over

# ---- P70 T7 (was P69 T59; harvest v2 T27 / A40): THE BALANCE SCALE - two named forces weighed, settled LEVEL ----------
#   balance-level    Steel and Paper H row 18's two-clocks page (`ledger:ev-two-clocks-bars-v1:bars::right:axes:cut`,
#                    `idle=live`, full stage, 16:9, the PLAIN profile - the row's `;readability=longform` would inline the
#                    long-form face into the committed uris; test_balance_scale reads the served beat) and its own
#                    sentences: "Different demand, different clock. The moat under the builders runs deeper than the paper
#                    holders can see. And the paper stacked on top runs taller than the builders admit. Both are true at
#                    once." The take's words shifted by -440.0 s: the balance draws in the page's ROOM (the right quarter
#                    of the stage, clear of the plot - E99 s128: an object in the world stands in its room) on "clock."
#                    (451.43), "MOAT" - the builders' plant, a sourced glyph - lands in the left pan on "moat" (452.76) and
#                    the beam leans to it; "PAPER" - the bank's columns, the paper holders - lands in the right on "paper" (456.65) and the beam settles
#                    LEVEL; judged on "Both are true at once" + 0.5 s (460.79), both sides weighed, the beam level, its
#                    base on T6b's resting hatch. H has no sentence that tips two UNQUANTIFIED forces (row 16's "the bills
#                    got bigger than the cash" is a balance of figures: two bars), so the tip is the private test bed's.
BAL_PROJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BAL_PLATE = "ledger:ev-two-clocks-bars-v1:bars::right:axes:cut;idle=live"
BAL_SHIFT = 440.0
BAL_SPECIES = [
    {"kind": "balance", "at": round(451.43 - BAL_SHIFT, 2), "dur": round(463.95 - 451.43, 2), "idle": "breath",
     "target": {"kind": "region", "x0": 0.735, "y0": 0.22, "x1": 0.985, "y1": 0.80},       # the page's room, clear of the plot and of the caption's rail
     "left": {"label": "MOAT", "icon": "factory", "at": round(452.76 - BAL_SHIFT, 2)},     # "The moat under the builders"
     "right": {"label": "PAPER", "icon": "landmark", "at": round(456.65 - BAL_SHIFT, 2)}},   # "And the paper stacked on top"
]


def balance_level() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    species = [json.loads(json.dumps(e)) for e in BAL_SPECIES]
    assert not BST.validate_species(species, (0, 0, 0), BAL_PLATE), BST.validate_species(species, (0, 0, 0), BAL_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(BAL_PLATE, (0, 0, 0), BAL_PROJECT)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = dict(_base_uris(), **{BST.ICON_PREFIX + n: BST.icon_geometry(n) for e in species for n in BST.species_icons(e)})
    return _timeline("Golden: two named forces weighed and settled level (balance)", scenes, {}, "16:9"), uris


SURFACES.update({"balance-level": balance_level})
FRAME_T.update({"balance-level": round(460.29 + 0.5 - BAL_SHIFT, 2)})   # "Both are true at once" + 0.5 s: 20.79

# ---- P70 T8 (was P69 T69; harvest v2 A35): THE POOF - a prop appears at its place inside a ring of seeded puffs --------
#   prop-poof    Steel and Paper H row 17's anaphora, "The steel kept building. The paper just got heavier." (SHOT-TABLE-H #13,
#                338.44-363.38; take "The steel" 350.70, "The paper" 352.30), the take shifted by -340.0 s: the catalogue's
#                steel I-beam (`prop-memory-steel-ibeam-v1`, a PROXY as every catalogued cutout in a golden is - E99 s31)
#                POOFS IN on "steel" (350.81 -> 10.81) at its AUTHORED place (s106: the author puts a prop; the fit only
#                advises), bare on the plain charcoal plate. Read 0.30 s after its enter: the prop whole at its own size
#                (the pop landed at 0.30), the cloud opened into its ring of eight lobes in the ground's chalk, fading
#                (alpha 0.72) - Bravos BUB 11:58.7, the ball whole inside the lobes. The load ("the paper") is the rig's,
#                and waits on its claim's approval at P70-HG1; this golden proves the arrival alone.
POOF_CUTOUT = REPO / "content/video_engine/assets/props/cutouts/prop-memory-steel-ibeam-v1.png"
POOF_SHIFT = 340.0
POOF_ENTER = round(350.81 - POOF_SHIFT, 2)    # "steel" (350.812): the thing named appears on its noun
POOF_EXIT = round(363.38 - POOF_SHIFT, 2)     # the row's end
POOF_PLACE = {"x": 0.5, "y": 0.44, "w": 0.2}  # the painted centre and painted width, stage fractions (authored)


def prop_poof() -> tuple[dict, dict]:
    """The poof is placed by the compiler's own door for an AUTHORED prop (`prop_place_fit`, the one the row loop
    calls), with the cutout's own PAINTED box, and the entry is written as the loop writes it (`dock_entry`, the painted
    extent riding the poof so its puff centres on the art)."""
    import build_scene_timeline_f as BST
    aid = "ev-prop-ibeam"
    world = {"asset_id": "plate-plain", "ken_burns": {"scale": 0, "x": 0, "y": 0}, "sha256": "0" * 64}
    opts = BST.dock_opts({"prop": True, "arrive": "poof", "place": dict(POOF_PLACE)})   # validated as a build's are
    fit = BST.prop_place_fit(None, "16:9", opts, BST.painted_box(POOF_CUTOUT), [], "golden prop-poof", [])
    place = {k: fit[k] for k in ("x", "y", "w", "h", "room")}
    dock = BST.dock_entry(aid, 0, POOF_ENTER, POOF_EXIT, 0, BST.DOCK_KIND_PROP, place, opts["arrive"], opts.get("mass"), True,
                          prop=True, paint=fit["paint"], authored_place=opts["place"])
    ev = {aid: {"title": "Memory Structural I-Beam", "source": "the props catalogue (prop-memory-steel-ibeam-v1)",
                "species": "prop", "document": {"path": str(POOF_CUTOUT.relative_to(REPO)), "sha256": "0" * 64},
                "badges": [], "kind": BST.DOCK_KIND_PROP}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [dock], "species": []}]
    uris = _base_uris()
    uris[aid] = uri("image/png", png_proxy(POOF_CUTOUT, PROP_PROXY_PX))
    tl = _timeline("Golden: the poofed prop (arrive: poof)", scenes, ev, None)
    tl["kinetics"] = {"stop_action": True}   # P47 T1's switch, as prop-stamp's
    return tl, uris


SURFACES.update({"prop-poof": prop_poof})
FRAME_T.update({"prop-poof": round(POOF_ENTER + 0.30, 2)})   # 11.11: the prop whole, the cloud opened into its ring


# ---- P71 T15 (was P69 T40; E99 s124 AS AMENDED): A DOCK OVER A CHART CHOOSES BY INTENT -----------------------------------
#   dock-hover-over-ledger  the divergence line page (the committed ev-divergence-v1 object, built by its own clock) with
#                           the golden chart card centred OVER its plot, naming `under: "hover"`: the card lifts 10 px, grows
#                           its 3.5 % step, casts drift-hold's drop shadow and holds on the drift-hold (graded whisper - a
#                           card carrying a chart); the chart under it is untouched - no veil, no wash. Read mid-hold.
#   dock-blur-over-plate    a PICTURE plate of a larger chart (synthetic bars, a committed input) with the same card over it
#                           naming `under: "blur"`: the veil between the plate and the docks blurs the chart while the small
#                           evidence card makes its point (s124 (2)); read at the same instant.
UNDER_ENTER, UNDER_EXIT = 12.0, 24.0
UNDER_CARD = "ev-golden-chart"
UNDER_SLOT = {"centre": True, "centre_w": 0.34, "centre_x": 0.66, "centre_y": 0.50, "card_aspect": 0.62}
UNDER_SHARP_REGION = (180, 330, 820, 800)   # the chart beside the card (stage px): the left of the plot / the plate's bars
UNDER_PLATE_BARS = [(0.08 + 0.105 * i, 0.82 - (0.12 + 0.07 * ((i * 5) % 8)), 0.08 + 0.105 * i + 0.07, 0.82) for i in range(8)] \
    + [(0.06, 0.82, 0.94, 0.83), (0.06, 0.12, 0.062, 0.82)]   # eight bars on a baseline, and the y axis


def dock_under_surface(under: str | None, world: str, dock: bool = True, life: bool | None = None) -> tuple[dict, dict]:
    """The P71 T15 bench: `world` "ledger" (a line page) or "plate" (a picture of a chart); the card naming `under` (or
    none: the dock as it always was), or no dock at all (`dock=False`: the chart alone, the reference the hover's
    untouched-outside-the-card read compares against). `life` turns E49's switch on (default: when the dock holds), so a
    comparison frame can carry the same page life as the hover it is compared with."""
    import build_scene_timeline_f as BST
    ev = _chart_evidence()
    ev[UNDER_CARD] = dict(ev[UNDER_CARD], badges=[])   # no rail: the card is the evidence and nothing lands on it
    opts = BST.dock_opts(dict(UNDER_SLOT, **({"under": under} if under else {})))   # the row's own options, validated
    idle = BST.dock_idle(opts, ev[UNDER_CARD])
    place = BST.centred_place(None, None, opts["card_aspect"], None, opts["centre_w"], None, opts["centre_y"], opts["centre_x"])
    docks = [BST.dock_entry(UNDER_CARD, 0, UNDER_ENTER, UNDER_EXIT, 0, BST.DOCK_KIND_IMAGE, place, None, None, True,
                            idle=idle, under=opts.get("under"))] if dock else []
    uris = _base_uris()
    uris[UNDER_CARD] = uri("image/png", png_solid(64, 40, (22, 24, 28)))   # the static fallback: the card is DRAWN from its series
    if world == "ledger":
        page = LPG.build_spec(LPG.load_series(SERIES), "line", 0, "right")
        w = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    else:
        uris["plate-chart"] = uri("image/png", png_bars(480, 270, (238, 229, 208), UNDER_PLATE_BARS, (30, 64, 96)))
        w = {"asset_id": "plate-chart", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": w, "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": []}]
    tl = _timeline(f"Golden: a dock over a chart, under {under or 'unnamed'} ({world})", scenes, ev, None)
    if (idle if life is None else life):   # a HOVER holds on the drift-hold, a dock's own idle (test_idle_e49's DOCK_IDLE_IS_THE_SUBJECT); blur holds none
        tl["kinetics"] = {"idle": True}
    return tl, uris


def dock_hover_over_ledger() -> tuple[dict, dict]:
    return dock_under_surface("hover", "ledger")


def dock_blur_over_plate() -> tuple[dict, dict]:
    return dock_under_surface("blur", "plate")


SURFACES.update({"dock-hover-over-ledger": dock_hover_over_ledger, "dock-blur-over-plate": dock_blur_over_plate})
FRAME_T.update({"dock-hover-over-ledger": round(UNDER_ENTER + 3.0, 2),   # the hover risen (contact 0.45 + 0.30 + 0.50) and holding
                "dock-blur-over-plate": round(UNDER_ENTER + 3.0, 2)})    # the veil up (0.45 s) and holding


# ---- P71 T19 (was P69 T60; the Bravos harvest v2 T26 / R14 / A14 / A59): VERDICT TILES ON THEIR WORDS -------------------
#   verdict-tiles-three-questions  A REFERENCE beat on Steel and Paper H's "Take any holding and ask it three questions"
#                     (the take, vo-h-scratch/scratch-kokoro.words.json, shifted by VT_SHIFT so "One:", the word after
#                     the ask, lands at 0.3 s): two CHART CARDS side by side (Bravos STK 10:22's "Your Portfolio" pair; R14's two
#                     panels), each drawn LIVE from its own sourced series (committed objects, never re-typed) - the first
#                     lands on "One:" (what memory costs leaving Korea, ev-memory-monitor-v1: the scarcity question), the
#                     second on "Two:" (SK hynix's share price against its own operating profit, ev-hynix-steel-v1: the
#                     cash question) - and each TICKS on its answer's word: "sold" ("Scarcity shows up in the order book -
#                     sold out") and "positive" ("If cash flow is positive ..."). The third question ("used tomorrow
#                     morning?") has no sourced series on disk to draw a tile from, and the dock has two slots, so it has
#                     no tile. No H row adopts the move before HG1 (rule f). Read with both ticks landed.
VT_TAKE = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/vo-h-scratch/scratch-kokoro.words.json"
VT_OBJECTS = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects"
VT_TILES = ("ev-memory-monitor-v1", "ev-hynix-steel-v1")
VT_WORDS = ((("one is what", 0), ("order book sold", 2)),        # (the tile's enter word, its verdict's word): a phrase and
            (("two does it", 0), ("if cash flow is positive", 4)))   # the index of the word in it - "One:" / "sold", "Two:" / "positive"
VT_SLOT = {"centre": True, "centre_w": 0.40, "centre_y": 0.46, "card_aspect": 0.62}
VT_X = (0.27, 0.73)   # the two tiles' centres: side by side, 116 px apart at 0.40 of the stage each
VT_PARK = {"x": 1180.0, "y": 150.0, "w": 480.0}   # the bench's parked box (stage px) for the park read


def _vt_word(phrase: str, k: int = 0) -> float:
    """The take's second for word `k` of the first `phrase` past 460 s (P71 T19): read off the words file, never re-typed."""
    words = json.loads(VT_TAKE.read_text(encoding="utf-8"))["words"]
    norm = [w["w"].lower().strip(".,:;?!—–-") for w in words]
    toks = phrase.lower().split()
    for i in range(len(norm) - len(toks) + 1):
        if norm[i:i + len(toks)] == toks and words[i]["start_s"] > 460.0:
            return float(words[i + k]["start_s"])
    raise SystemExit(f"verdict tiles: {phrase!r} is not in the take")


VT_SHIFT = round(_vt_word(*VT_WORDS[0][0]) - 0.3, 2) if VT_TAKE.exists() else 468.64   # "One:" at 0.3 s, right after the ask


def _vt_evidence(aid: str) -> dict:
    chart = json.loads((VT_OBJECTS / f"{aid}.series.json").read_text(encoding="utf-8"))
    return {"title": chart["title"], "source": chart["src"], "species": "chart",
            "document": {"path": f"evidence/objects/{aid}.series.json", "sha256": "0" * 64}, "badges": [], "chart": chart}


def verdict_tiles_surface(states: tuple = ("tick", "tick"), ats: tuple | None = None, park: bool = False,
                          words: bool = False) -> tuple[dict, dict]:
    """The P71 T19 bench: one or two chart tiles side by side (VT_TILES, in slot order), tile n naming `states[n]` at
    `ats[n]` (None: no verdict - the dock as it always was). `words`: the golden's clock - enters and verdicts off the take
    (VT_WORDS). `park`: ONE tile that reads centred and parks to VT_PARK, the stop condition's read. Every dock's options
    are the row's own, through `dock_opts`, and every verdict passes the compiler's `verdict_tile_error`."""
    import build_scene_timeline_f as BST
    ev, docks, uris = {}, [], _base_uris()
    for n, state in enumerate(states):
        aid = VT_TILES[n]
        ev[aid] = _vt_evidence(aid)
        uris[aid] = uri("image/png", png_solid(64, 40, (22, 24, 28)))   # the static fallback: the tile is DRAWN from its series
        if words:
            enter = round(_vt_word(*VT_WORDS[n][0]) - VT_SHIFT, 2)
            at = round(_vt_word(*VT_WORDS[n][1]) - VT_SHIFT, 2)
        else:
            enter, at = 2.0 + 1.5 * n, (ats[n] if ats else None)
        verdict = {"state": state, "at": at} if state else None
        opts = BST.dock_opts(dict(VT_SLOT, centre_x=VT_X[n] if len(states) > 1 else 0.5,
                                  **({"verdict": verdict} if verdict else {})))
        place = BST.centred_place(None, None, opts["card_aspect"], None, opts["centre_w"], None, opts["centre_y"],
                                  opts["centre_x"])
        if verdict:
            assert BST.verdict_tile_error(ev[aid], verdict, enter, RUNTIME) is None
        if park:
            h = round(VT_PARK["w"] * opts["card_aspect"], 2)
            docks.append(BST.dock_entry(aid, n, enter, RUNTIME, 0, BST.DOCK_KIND_IMAGE, dict(VT_PARK, h=h), None, None, False,
                                        read_place=place, verdict=opts.get("verdict")))
        else:
            docks.append(BST.dock_entry(aid, n, enter, RUNTIME, 0, BST.DOCK_KIND_IMAGE, place, None, None, True,
                                        verdict=opts.get("verdict")))
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": []}]
    return _timeline("Golden: verdict tiles on their words (P71 T19)", scenes, ev, None), uris


def verdict_tiles_three_questions() -> tuple[dict, dict]:
    return verdict_tiles_surface(("tick", "tick"), words=True)


SURFACES.update({"verdict-tiles-three-questions": verdict_tiles_three_questions})
FRAME_T.update({"verdict-tiles-three-questions": round(_vt_word(*VT_WORDS[1][1]) - VT_SHIFT + 0.55 + 0.6, 2)
                if VT_TAKE.exists() else 29.0})   # the second tick landed (LAND_S 0.55) and drawn, held


# ---- P71 T13 (was P69 T43b; R26-307, E99 s102): A SECOND AXIS, AND AN INVERTED ONE, FOR A CO-MOVEMENT CLAIM -------------
#   dual-axis-inverted  A REFERENCE beat (no H row: SCRIPT-H says no "these move together"): Bravos's own pairing (JPN 06:38,
#                     "Foreign Holdings of US Treasuries & US 30-Year Treasury Yield") on two sourced series in unlike units
#                     READ off committed files, never re-typed - Japan's holdings of US Treasuries (Tokyo's
#                     `ev-japan-holdings-v1`, TIC Table 5, $bn, monthly) on the LEFT and the US 10-year yield (Tokyo's
#                     `fred-DGS10.csv`, the month's mean of the daily prints, %) on its OWN right axis, INVERTED, from
#                     January 2020: as the yield climbed from 1.8% to 4.5%, Japan's holdings fell from their 2021 top
#                     (the monthly correlation over the window is -0.83), so on the inverted axis the two lines fall
#                     together - the co-movement the claim names (`claim: "comove"`, s102 (a)). Each axis names its unit
#                     and the inverted one says so on the page (s102 (b)); each axis's ticks wear their line's ink
#                     (s102 (c)). Compiled through the compiler's own path (world_for_plate over a temporary object,
#                     check_y2); judged built and held.
DUAL_TOKYO = MEMBERS_OBJECTS / "tokyo-tea-break/evidence"
DUAL_HOLDINGS = DUAL_TOKYO / "objects/ev-japan-holdings-v1.series.json"
DUAL_YIELD = DUAL_TOKYO / "sources/fred-DGS10.csv"
DUAL_FROM = 2020.0            # January 2020: the window the claim is read over
DUAL_ID = "ref-japan-holdings-vs-10y"
DUAL_PLATE = f"ledger:{DUAL_ID}:line::right"
DUAL_YEARS = tuple(range(2020, 2027))


def _month_of(x: float) -> tuple[int, int]:
    """A TIC holdings x (year + (month - 1) / 12: 2000.1667 is March 2000, the object's `series_from`) -> (year, month)."""
    y = int(math.floor(x + 1e-6))
    return y, int(round((x - y) * 12)) + 1


def _dgs10_monthly() -> dict[tuple[int, int], float]:
    """FRED DGS10's daily prints, averaged per calendar month (a blank print skipped); the file is read, never re-typed."""
    import csv
    by: dict[tuple[int, int], list[float]] = {}
    with DUAL_YIELD.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            v = (row.get("DGS10") or "").strip()
            if v and v != ".":
                y, m, _d = row["observation_date"].split("-")
                by.setdefault((int(y), int(m)), []).append(float(v))
    return {k: sum(v) / len(v) for k, v in by.items()}


def dual_axis_series() -> dict:
    """The reference page's object, composed from the two committed sources (their months matched one to one)."""
    obj = json.loads(DUAL_HOLDINGS.read_text(encoding="utf-8"))
    held = [[x, v] for x, v in obj["series"][0]["pts"] if x >= DUAL_FROM - 1e-6]
    yields = _dgs10_monthly()
    ylds = [[x, round(yields[_month_of(x)], 2)] for x, _v in held]
    return {"title": "Japan sells as the yield climbs",
            "sub": "Reference beat: monthly since 2020, the yield inverted",
            "src": "US Treasury TIC Table 5; FRED DGS10, monthly mean: our arithmetic",
            "ylabel": "Japan's holdings, $bn", "claim": "comove",
            "xticks": [[float(y), str(y)] for y in DUAL_YEARS],
            "series": [{"name": "JAPAN'S HOLDINGS", "label": f"${held[-1][1]:,.0f}bn", "color": "teal", "pts": held},
                       {"name": "US 10-YEAR YIELD", "label": f"{ylds[-1][1]:.2f}%", "color": "amber", "pts": ylds}],
            "y2": {"series": [1], "unit": "%", "label": "10-year yield", "invert": True}}


def dual_axis_inverted(longform: bool = False) -> tuple[dict, dict]:
    """The golden's timeline (the plain profile; `longform` re-profiles the page as a `;readability=longform` row
    compiles it, for test_dual_axis's reads only - the committed golden is the plain call)."""
    import tempfile
    import build_scene_timeline_f as BST
    series = dual_axis_series()
    assert LPG.validate(series, "line") == [], LPG.validate(series, "line")
    plate = DUAL_PLATE + (";readability=longform" if longform else "")
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{DUAL_ID}.series.json").write_text(json.dumps(series), encoding="utf-8")
            world = BST.world_for_plate(plate, (0, 0, 0), Path(td))
            BST.stamp_full_stage(world["page"])
            BST.derive_rescale_states(world, [], plate, Path(td))   # the compiler's own page checks: check_y2
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    return _timeline("Golden: Japan's Treasuries against the 10-year on its own inverted right axis (y2)",
                     scenes, {}, "16:9"), _base_uris()


SURFACES.update({"dual-axis-inverted": dual_axis_inverted})
FRAME_T.update({"dual-axis-inverted": 12.0})   # both lines drawn and tagged, both axes written, held


# ---- P71 T16 (was P69 T41; harvest v2 A17 / T23 / S3; E77, E99 s93): `project` - A LABELLED DASHED CONTINUATION --------
#   project-issuance-2026e  Steel and Paper H row 16's own sentence, "Last year: a hundred and twenty-one billion. This
#                     year they're tracking toward a hundred and fifty" - the ONE point the script speaks of the 2026E
#                     range (the plan's rule: "if the consensus is a RANGE, the wedge recipe is the form and T16's golden
#                     uses the single point the script speaks"; the capex words 480 / 690 are a REVISION of two 2026
#                     estimates, no actual to continue). The object is the COMMITTED `ev-debt-issuance-line-v1`, read in
#                     place, never re-typed: its issuance line (the 2020-24 average drawn flat, 121 in 2025) and its
#                     `$150B` series as the projection - `later: true`, from the 2025 actual, labelled "2026E", its tier
#                     the object's own `research_tier`, its source the object's dossier proof for the range. The row's
#                     plate (the long form, live - rule (g)), the take's words shifted by -258.61 s: "tracking toward"
#                     266.61 -> 8.00, the extend's pen landing as "fifty" is said + 0.4 (267.79 -> 9.18). The 2026E x
#                     tick is not on the page (the standing state ends at 2025; the tag names the year). Judged 1.0 s
#                     after the landing: dashed from the last actual, the tag "2026E" whole, the actual the primary.
PROJ_PROJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
PROJ_OBJECT = PROJ_PROJECT / "evidence/objects/ev-debt-issuance-line-v1.series.json"
PROJ_ID = "ref-issuance-2026e"
PROJ_PLATE = f"ledger:{PROJ_ID}:line::right;idle=live;readability=longform"
PROJ_SHIFT = 258.61
PROJ_AT, PROJ_DUR = round(266.61 - PROJ_SHIFT, 2), round(267.79 - 266.61, 2)


def projection_series() -> dict:
    """The golden's object, composed from the committed debt object: its actual and its spoken 2026E point."""
    obj = json.loads(PROJ_OBJECT.read_text(encoding="utf-8"))
    actual = next(s for s in obj["series"] if s.get("label") == "issuance")
    hi = next(s for s in obj["series"] if s.get("label") == "$150B")
    rng = next(p for p in obj["proof"] if "est_2026_high_usd_b" in (p.get("values") or {}))
    lo_v, hi_v = rng["values"]["est_2026_low_usd_b"], rng["values"]["est_2026_high_usd_b"]
    assert hi["pts"][-1][1] == hi_v and hi["pts"][0] == actual["pts"][-1], "the $150B series leaves the 2025 actual"
    last = actual["pts"][-1][0]
    return {"title": obj["title"],
            "sub": "Hyperscaler bond issuance, US$ billions a year; 2020-24 is an average; the dashed line an estimate",
            "src": obj["src"], "ylabel": obj["ylabel"], "ymin": obj["ymin"],
            "xticks": [t for t in obj["xticks"] if t[0] <= last],
            "series": [{"label": actual["label"], "color": actual["color"], "pts": actual["pts"]},
                       {"color": actual["color"], "later": True, "pts": hi["pts"],
                        "projection": {"label": "2026E", "tier": obj["research_tier"],
                                       "src": f"the top of the ${lo_v}–{hi_v}B projected range"}}]}


def project_issuance_2026e() -> tuple[dict, dict]:
    import tempfile
    import build_scene_timeline_f as BST
    series = projection_series()
    assert LPG.validate(series, "line") == [], LPG.validate(series, "line")
    species = [{"kind": "chart_to", "at": PROJ_AT, "dur": PROJ_DUR, "to": "extend", "series": 1}]
    assert not BST.validate_species(species, (0, 0, 0), PROJ_PLATE), BST.validate_species(species, (0, 0, 0), PROJ_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{PROJ_ID}.series.json").write_text(json.dumps(series), encoding="utf-8")
            world = BST.world_for_plate(PROJ_PLATE, (0, 0, 0), Path(td))
            BST.stamp_full_stage(world["page"])
            BST.derive_rescale_states(world, species, PROJ_PLATE, Path(td))   # the extend's derived state; check_projection
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: the dashed 2026E continuation from the last actual (project)", scenes, {}, "16:9")
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


SURFACES.update({"project-issuance-2026e": project_issuance_2026e})
FRAME_T.update({"project-issuance-2026e": round(PROJ_AT + PROJ_DUR + 1.0, 2)})   # landed 1.0 s: dashed, tagged, held


# ---- P70 T9 (was P69 T61, A34; BUB 12:22-15:06): THE CHAPTER PILL, HELD OVER AN ACT ------------------------------------
#   chapter-held     Steel and Paper H's act "The turn" across the cut from row 14 into row 15, the take's words shifted by
#                    -360.0 s: the pill lands on "It was never the AI stocks" (363.38 -> 3.38) over the reset plate (the
#                    plain plate stands in for the press - a golden embeds no project plate), holds across the cut, and
#                    stands over row 15's own page (`ledger:ev-index-concentration-bars-v1:bars::right:axes:cut`,
#                    `idle=live;readability=longform;bar_style=soft` - the row's plate string, the LONG FORM, because only
#                    a long-form page makes room: the face rides the uris with the chapter, as it rides every compiled
#                    build that has one). The page arrives at 384.12 (24.12) with its title moved down by the room, the
#                    pill standing in the band Bravos keeps for it (BUB 12:35: the pill, 16 px, the title). Judged 3.0 s
#                    after the cut: the page's ink written, the pill held since 3.74 without landing again. Every piece is
#                    the compiler's own: `collect_chapters`, `chapter_page_room`, `timeline_chapters`, `compiled_chapter`.
CHAPTER_SHIFT = 360.0
CHAPTER_PAGE = "ledger:ev-index-concentration-bars-v1:bars::right:axes:cut;idle=live;readability=longform;bar_style=soft"
CHAPTER_PROJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
CHAPTER_ENTRY = {"kind": "chapter", "at": round(363.38 - CHAPTER_SHIFT, 2), "until": RUNTIME, "text": "The turn"}
CHAPTER_CUT = round(384.12 - CHAPTER_SHIFT, 2)


def chapter_held() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    entry = dict(CHAPTER_ENTRY, id="s01.species.0")
    assert not BST.validate_species([dict(entry)], (0, 0, 0), "plate-plain"), BST.validate_species([dict(entry)], (0, 0, 0), "plate-plain")
    plan = [(0.0, CHAPTER_CUT, "plate-plain", (0, 0, 0), [], "cut", [entry]),
            (CHAPTER_CUT, RUNTIME, CHAPTER_PAGE, (0, 0, 0), [], "cut", [])]
    chapters = BST.collect_chapters(plan, RUNTIME)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(CHAPTER_PAGE, (0, 0, 0), CHAPTER_PROJECT)
        BST.stamp_full_stage(world["page"])
        assert BST.chapter_page_room(world, BST.chapters_over(chapters, CHAPTER_CUT, RUNTIME)) == []   # the page makes room
    finally:
        BST.ASPECT = saved
    plate = {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": plate, "exit": "cut", "span": [0.0, CHAPTER_CUT], "docks": [],
               "species": [BST.compiled_chapter(entry)]},
              {"scene_id": "s02", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [CHAPTER_CUT, RUNTIME], "docks": [], "species": []}]
    tl = _timeline("Golden: the chapter pill held over an act, across the cut (chapter)", scenes, {}, "16:9")
    tl["chapters"] = BST.timeline_chapters(chapters)   # flagless (test_idle_e49): the pill's life is not this golden's subject
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


SURFACES.update({"chapter-held": chapter_held})


# ---- P70 T10 (was P69 T61, A44; BOOM 02:26.47-02:27.35): THE IN-PLACE SWAP on the chapter pill ------------------------
#   chapter-swap     Steel and Paper H's own rename of the act's subject, the take's words shifted by -360.0 s: "It was
#                    never the AI stocks. The bubble isn't in the steel. It's in the PAPER wrapped around the steel." -
#                    the pill "The bubble" lands on the act's first word (363.38 -> 3.38) and is swapped in place to "The
#                    paper" on "paper" (367.38 -> 7.38): the same period renamed (BRAVOS-USE-WHEN A44), the pill never
#                    moving. Over the plain plate (the press stands in) - the swap is the pill's own motion, whatever
#                    world it stands over. Judged MID-OPEN, as BOOM's own witness frame (02:27.0, "st Dec"): the old name
#                    gone, the box half sprung from its slot, the new name half written. The beat is PROPOSED for the
#                    parent to name (the plan: "the parent names the H beat once the BOOM frame is read").
SWAP_ENTRY = {"kind": "chapter", "at": round(363.38 - CHAPTER_SHIFT, 2), "until": RUNTIME, "text": "The bubble",
              "swap": [{"at": round(367.38 - CHAPTER_SHIFT, 2), "text": "The paper"}]}


def chapter_swap() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    entry = dict(json.loads(json.dumps(SWAP_ENTRY)), id="s01.species.0")
    assert not BST.validate_species([json.loads(json.dumps(entry))], (0, 0, 0), "plate-plain")
    chapters = BST.collect_chapters([(0.0, RUNTIME, "plate-plain", (0, 0, 0), [], "cut", [entry])], RUNTIME)
    plate = {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": plate, "exit": "cut", "span": [0.0, RUNTIME], "docks": [],
               "species": [BST.compiled_chapter(entry)]}]
    tl = _timeline("Golden: the chapter pill renamed in place (chapter swap)", scenes, {}, "16:9")
    tl["chapters"] = BST.timeline_chapters(chapters)   # flagless (test_idle_e49), as chapter-held
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


SURFACES.update({"chapter-swap": chapter_swap})
FRAME_T.update({"chapter-swap": round(SWAP_ENTRY["swap"][0]["at"] + 0.43 + 0.21, 2)})   # mid-open: 8.02
FRAME_T.update({"chapter-held": round(CHAPTER_CUT + 3.0, 2)})   # after the cut: the page's ink written under the held pill (27.12)


# P71 T22 (was P69 T63): THE ROUTE MAP - routes lighting IN TURN with money on them, and the one ping as a place lands
# (BOOM 04:06-04:08.5: nodes pop, routes grow out of them staggered, FLAT - the tilt is dropped; A37 as CHN 02:21.1 and
# D40 13:56.5 show it: one pulse, never a repeating sonar). A TEST-BED beat, labelled as one: H row 22 ("what memory
# costs leaving Korea, by the kilo, straight off customs export data", take 625.02-626.94) is the candidate the parent
# confirms on the frame. The three DESTINATIONS are the test bed's, NOT sourced (research gate: UNSOURCED-editorial) -
# a body row names its routes from the customs data itself. No H row adopts the move before HG1 (rule f).
ROUTE_AT = (6.0, 6.3, 6.6)          # the three routes leave Korea one after another (BOOM's stagger, on their words)
ROUTE_TO = ("CHN", "VNM", "TWN")
ROUTE_TOKENS_AT = 7.5               # "by the kilo": the money starts as the last route is drawn (6.6 + DRAW_S = 7.5); the earlier two wait for it


def vecmap_route_tokens() -> tuple[dict, dict]:
    """P71 T22: Korea LIGHTS and pings as it lands (5.0); three routes leave it in turn (6.0 / 6.3 / 6.6), each a
    clothoid drawn by length; the last route's destination lights on the word the route lands and pings (7.5 - D40's
    arrival form); from 7.5 two plain DOTS in the route's ink - T11's token look - ride every route by arc length.
    Judged at 8.3: Taiwan's pulse half way out (u 0.52) and the money 0.8 s into its run on all three routes."""
    import build_scene_timeline_f as BST
    world = BST.world_for_plate("vecmap:KOR,CHN,VNM,TWN", (0, 0, 0), None)
    kor = {"kind": "country", "id": "KOR"}
    species = [{"kind": "light", "at": 5.0, "dur": 14.0, "idle": "breath", "ping": True, "target": kor}]
    species += [{"kind": "arc", "at": at, "dur": 12.0, "from": kor, "to": {"kind": "country", "id": to},
                 "tokens": {"from_at": ROUTE_TOKENS_AT, "n": 2}} for at, to in zip(ROUTE_AT, ROUTE_TO)]
    species += [{"kind": "light", "at": 7.5, "dur": 10.0, "idle": "breath", "ping": True,
                 "target": {"kind": "country", "id": "TWN"}}]
    errs = BST.validate_species(species, (0, 0, 0), "vecmap:KOR,CHN,VNM,TWN")
    assert not errs, errs
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    uris[BST.MAP_PREFIX + world["map"]] = BST.world_map_json(world["map"])
    tl = _timeline("Golden: the route map - routes in turn, tokens on them, the ping (test-bed beat)", scenes, {}, None)
    tl["captions"], tl["caption_pages"] = [], []   # the map frames its places at the stage's centre, where the harness's caption sits
    return tl, uris


SURFACES.update({"vecmap-route-tokens": vecmap_route_tokens})
FRAME_T.update({"vecmap-route-tokens": 8.3})   # TWN's ping at u 0.52 (7.5 + 0.35 -> + 0.67), the tokens 0.8 s into their run - spread along every route


# P71 T17 (was P69 T57): HUB AND SPOKE - one institution to many (v2 T31, Bravos DOM 04:30: the IMF, dashed spokes to six
# governments) - and A LINK THAT FAILS (A26, BOOM 04:41 "Investors X Utility Companies"). A TEST-BED beat, labelled as
# one: H row 16 ("bond market" 273.45-274.56 / "who is paying" 244.72-245.43) is the candidate the parent confirms on the
# frame - the bond market the hub, the borrowers its rim; no H row adopts the move before HG1 (rule f).
HUB_NODES = [("market", "landmark", "BOND MARKET", None), ("cloud", "cpu", "CLOUD", 5.4), ("builders", "factory", "BUILDERS", 5.8),
             ("utilities", "factory", "UTILITIES", 6.2), ("shippers", "ship", "SHIPPERS", 6.6), ("chips", "cpu", "CHIPS", 7.0)]
HUB_AT, HUB_TOKENS_AT, HUB_FAIL_AT = 4.0, 7.5, 8.6   # each rim lands on its own word (the last spoke drawn by 7.34 s); the
                                                     # money leaves the market on the next; the utilities' link breaks on its word


def hub_spoke_fail() -> tuple[dict, dict]:
    """P71 T17: the bond market at the centre and five borrowers on T11's ring round it, each STRAIGHT spoke drawn on its
    borrower's word and the borrower landing at its end; one plain dot per spoke carrying the money out (T11's tokens);
    then the link to UTILITIES FAILS - a neg-ink disc with a white X springs in at its middle, the spoke reddens and its
    halves retract, the node stays. Judged 1.0 s after the failure (FRAME_T 9.6): the disc settled, both strokes struck."""
    import build_scene_timeline_f as BST
    species = [{"kind": "flow", "at": HUB_AT, "dur": 18.0, "idle": "breath", "layout": "hub",
                "target": {"kind": "region", "x0": 0.06, "y0": 0.03, "x1": 0.94, "y1": 0.97},   # the whole stage, as DOM 04:30 gives it
                "nodes": [dict({"id": i, "icon": icon, "label": label}, **({"at": w} if w is not None else {}))
                          for i, icon, label, w in HUB_NODES],
                "edges": [["market", n[0]] for n in HUB_NODES[1:]],
                "tokens": {"from_at": HUB_TOKENS_AT, "n": 1},
                "fail": {"edge": ["market", "utilities"], "at": HUB_FAIL_AT}}]
    assert not BST.validate_species(species, (0, 0, 0), "plate-plain"), BST.validate_species(species, (0, 0, 0), "plate-plain")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    for name in sorted(BST.species_icons(species[0])):
        uris[BST.ICON_PREFIX + name] = BST.icon_geometry(name)
    tl = _timeline("Golden: hub and spoke - one institution to many, and a link that fails (test-bed beat)", scenes, {}, None)
    tl["captions"], tl["caption_pages"] = [], []   # the harness's centred caption would sit on the hub: the diagram is the frame
    return tl, uris


SURFACES.update({"hub-spoke-fail": hub_spoke_fail})
FRAME_T.update({"hub-spoke-fail": 9.6})   # the spokes drawn (7.34), the money on them, the failure 1.0 s old - disc settled, X struck


# ---- P71 T23 (was P69 T67; harvest v2 A19 / R4): A CARD JOINS ITS DATE ------------------------------------------------
#   card-reads-in-the-empty-room  Steel and Paper H row 9's railway page (the committed ev-railway-index-v1 object, full
#                                 stage, 16:9: the rise drawn to the peak, then the fall, as H's "crashed" beat draws it)
#                                 with a headline card naming `park_at: {datum: 53}` (the peak, 6 Oct 1845 - A19's "a card
#                                 docks onto the plot at its peak") and `under: "hover"`: it READS in the plot's empty room
#                                 at the date's side (E65's own read_in_room: the upper right, over the fall's empty
#                                 room), lifted - read mid-read.
#   card-parks-at-its-date        the same beat after the park: the card shrunk to a chip at E45's floor width right of the
#                                 peak and the leader drawn from it to a dashed ring on the datum (BOOM 00:45's form). The
#                                 compiler's mask reads the chip's corner in one cell the rise's ink touches (a WARN with
#                                 its numbers, s106); the probe measures the chip clear of the ink (test_card_at_its_date).
# The card is a synthetic headline (paper, a headline's bars over a photo block), a committed input like every other.
DATE_PLATE = LIT_PLATE
DATE_CARD = "ev-golden-headline"
DATE_CARD_PX = (528, 300)
DATE_CARD_ASPECT = 0.6657   # the CARD's h / w at the chip's width (the row's `card_aspect` is the card's, chrome and all): the
                            # picture's 300/528 in a frame 38 px narrower than the card, plus 45 px of chrome
                            # (DOCK_CARD_CHROME_W / _H): ((240 - 38) * 300 / 528 + 45) / 240 [DERIVED]
DATE_DATUM = DATE_PEAK = 53
DATE_ENTER, DATE_EXIT, DATE_READ_S = 4.0, 16.0, 2.0   # the author's read_s: a headline's words take two seconds to read
DATE_RESCALE_AT, DATE_RESCALE_S = 10.0, 1.2
DATE_RESCALE = {"kind": "chart_to", "at": DATE_RESCALE_AT, "dur": DATE_RESCALE_S, "to": "rescale", "window": [1844.5, 1850.21]}
DATE_OVER_INK_READ = {"centre_w": 0.36, "centre_x": 0.30, "centre_y": 0.50}   # the author's read over the rise's own ink (s124 (3))
DATE_BLUR_REGION = (940, 300, 1100, 820)   # the plot beside that read (stage px): the fall's ink and its rules, which the veil blurs
DATE_SPECIES = [
    {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": {"kind": "datum", "index": DATE_PEAK}},   # the rise to the peak
    {"kind": "build_to", "at": 2.0, "dur": 1.2, "series": 0, "target": {"kind": "datum", "index": 139}},   # "crashed": the fall draws
]


def card_at_date_surface(under: str | None = "hover", read: dict | None = None, rescale: bool = False,
                         datum: int = DATE_DATUM) -> tuple[dict, dict]:
    """The P71 T23 bench, compiled the way the row loop compiles it: `park_at_place` (the chip), the read box (the row's own
    `read`, else the card's solo box), E63's `read_over_build`, then `park_at_read` (E65's room at the date's side) and
    `dock_entry`. `under` the author's choice (hover by default here, as acceptance 1 names it); `read` an authored reading
    box (with `under`, it stands over the ink - s124 (3)); `rescale` a chart_to rescale after the park (the chip follows);
    `datum` the date joined (the peak)."""
    import build_scene_timeline_f as BST
    species = [dict(e) for e in DATE_SPECIES] + ([dict(DATE_RESCALE)] if rescale else [])
    assert not BST.validate_species(species, (0, 0, 0), DATE_PLATE), BST.validate_species(species, (0, 0, 0), DATE_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(DATE_PLATE, (0, 0, 0), LIT_PROJECT)
        BST.stamp_full_stage(world["page"])
        if rescale:   # the derived chart state the rescale moves to, as the compiler derives it
            BST.derive_rescale_states(world, species, DATE_PLATE, LIT_PROJECT, sid="s01")
        opts = BST.dock_opts({"park_at": {"datum": datum}, "card_aspect": DATE_CARD_ASPECT, "read_s": DATE_READ_S,
                              **({"under": under} if under else {}), **({"read": dict(read)} if read else {})})
        page = world["page"]
        pk = BST.park_at_place(world, opts["park_at"], "16:9", DATE_CARD_ASPECT)
        chip = {k: pk[k] for k in ("x", "y", "w", "h", "room")}
        rd = opts.get("read") or {}
        rplace = BST.centred_place(BST.dock_place(world, "16:9"), "16:9", DATE_CARD_ASPECT, page, rd.get("centre_w"), None,
                                   rd.get("centre_y"), rd.get("centre_x")) if rd else None
        read_box = BST.dock_read_box("16:9", rplace, DATE_CARD_ASPECT)
        e63 = BST.read_over_build(chip, read_box, page, "16:9", DATE_ENTER, DATE_ENTER + DATE_READ_S,
                                  BST.page_build_windows(world, species, 0.0), DATE_CARD_ASPECT, [], under=opts.get("under")) or {}
        e63, _note = BST.park_at_read(world, pk, read_box, "16:9", DATE_CARD_ASPECT, e63, opts, [])
    finally:
        BST.ASPECT = saved
    ev = {DATE_CARD: {"title": "Golden headline card", "source": "golden", "species": "deck",
                      "document": {"path": "golden", "sha256": "0" * 64}, "badges": []}}
    docks = [BST.dock_entry(DATE_CARD, 0, DATE_ENTER, DATE_EXIT, 0, BST.DOCK_KIND_IMAGE, chip,
                            read_place=e63.get("read_place") or rplace, read_s=DATE_READ_S,
                            read_moved=e63.get("read_moved"), read_deferred=bool(e63.get("read_deferred")),
                            under=opts.get("under"),
                            park_at={"datum": datum, "series": 0, "side": pk["side"], "anchor": pk["ay"]})]
    uris = _base_uris()
    uris[DATE_CARD] = uri("image/png", png_bars(DATE_CARD_PX[0], DATE_CARD_PX[1], (250, 247, 240),
                                                [(0.06, 0.08, 0.90, 0.20), (0.06, 0.24, 0.62, 0.34), (0.06, 0.42, 0.30, 0.46),
                                                 (0.12, 0.54, 0.88, 0.96)]))   # two headline lines, a dateline, a photo block
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": species}]
    tl = _timeline(f"Golden: a card joins its date (park_at, under {under or 'unnamed'})", scenes, ev, "16:9")
    tl["captions"], tl["caption_pages"] = [], []   # the harness's caption would sit on the plot: the join is the frame
    return tl, uris


def card_reads_in_the_empty_room() -> tuple[dict, dict]:
    return card_at_date_surface()


def card_parks_at_its_date() -> tuple[dict, dict]:
    return card_at_date_surface()


SURFACES.update({"card-reads-in-the-empty-room": card_reads_in_the_empty_room, "card-parks-at-its-date": card_parks_at_its_date})
FRAME_T.update({"card-reads-in-the-empty-room": round(DATE_ENTER + 1.6, 2),   # the pop settled (0.45) and the hover risen (0.45 + 0.30 + 0.50): reading
                "card-parks-at-its-date": round(DATE_ENTER + DATE_READ_S + 0.7 + 0.35 + 0.6, 2)})   # the park (0.7) and the leader (0.35) done, held 0.6 s


# ---- P71 T24 (was P69 T72; the Bravos harvest v2 A48, D40 11:43-11:52): BARS RE-VALUED, THEN -> NOW ---------------
# Steel and Paper H row 16's issuance, "twenty-eight" (the 2020-24 annual average) -> "a hundred and fifty" (the top of
# the 2026 estimate range): one bar on a full-stage bars page, built at today's $150B with its figure written at its top
# (8.0), and a `chart_to compare` that names `from` (the two-key path) at 11.0 over 6.0 s - the bar shrinks to $28B in
# REVALUE.DOWN_S, holds, and grows back to $150B landing at 17.0, the figure counting with it. BOTH values are READ off
# the page's own committed series file (`ev-debt-issuance-line-v1`: the issuance series' flat 2020-24 point and the
# $150B series' 2026 point), never re-typed; the bar is labelled an estimate (E77). Read at rest after the grow: the bar
# back at $150B, "$150B" on its top, the $28B level dashed across its face.
REVALUE_SERIES = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-debt-issuance-line-v1.series.json"


def revalue_issuance() -> tuple[dict, list[dict]]:
    """(the bars object, the species) for the re-value golden - the values off the series file."""
    debt = json.loads(REVALUE_SERIES.read_text(encoding="utf-8"))
    by = {s["label"]: s["pts"] for s in debt["series"]}
    then_v, now_v = by["issuance"][0][1], by["$150B"][-1][1]
    obj = {"title": debt["title"],
           "sub": "Hyperscaler bond issuance a year - 2026 is the top of the estimate range ($130-150B), 2020-24 an average",
           "src": debt["src"], "unit": "$", "unit_suffix": "B",
           "bars": [{"label": "2026E, top of the range", "value": now_v, "color": "crimson"}]}
    now_t, then_t = "$%gB" % now_v, "$%gB" % then_v
    species = [
        {"kind": "figure", "at": 8.0, "dur": 1.5, "text": now_t, "target": {"kind": "datum", "index": 0}},
        {"kind": "chart_to", "at": 11.0, "dur": 6.0, "to": "compare",
         "metric": {"value": now_v, "text": now_t, "label": "this year, tracking toward"},
         "from": {"value": then_v, "text": then_t, "label": "a year, 2020-24",
                  "src": "[SOURCE: ev-debt-issuance-line-v1 - the 2020-24 annual average (Morgan Stanley IM, Mellon via the dossier)]"},
         "source": "[SOURCE: ev-debt-issuance-line-v1 - the top of the 2026 projected range (PIMCO, Investing.com/LPL via the dossier)]"},
    ]
    return obj, species


def bar_revalue_then_now() -> tuple[dict, dict]:
    """P71 T24: the re-value AT REST after the grow (E28: the height is the number at every frame)."""
    import tempfile
    import build_scene_timeline_f as BST
    plate = "ledger:fx-debt-issuance-bars:bars"
    obj, species = revalue_issuance()
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/fx-debt-issuance-bars.series.json").write_text(json.dumps(obj), encoding="utf-8")
        saved = BST.ASPECT
        BST.ASPECT = "16:9"
        try:
            world = BST.world_for_plate(plate, (0, 0, 0), ep)
            BST.stamp_full_stage(world["page"])
        finally:
            BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: a bar re-valued, then to now (H row 16's issuance)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"bar-revalue-then-now": bar_revalue_then_now})
FRAME_T.update({"bar-revalue-then-now": 17.8})   # at rest: the grow landed at 17.0 (11.0 + 6.0), the $28B level at full ink



# ---- P71 T21 (was P69 T73; harvest v2 A46 / R29 / A45): FILLS TO A LEVEL - a spread that keeps one side of its rule --
#   fill-below-zero  A REFERENCE BEAT (no H row carries a signed series: row 22's customs line is a level, its soft
#                    month a dip under the PRIOR print - A45's form): fed-liquidity-pressure's COMMITTED DERIVED object
#                    `fed-assets-reserves-history` (FRED H.4.1: the change in bank reserves since 1 June 2022, weekly,
#                    read in place), total assets held at nothing, a zero rule named on the page (`axes.hlines: [{y: 0}]`,
#                    D40 12:54's zero is a plain rule too), and on the word the spread from the last print at zero
#                    (datum 116, 2024-08-21, +$0.002T) keeps only what lies BELOW the rule - the autumn 2024 slide, the
#                    year-end record low (-$0.465T, 2025-01-01) and the spring 2025 dip - and leaves the February-April
#                    hump over zero unfilled, in the neg ink, with P72 T49's glow round the clipped fill. At rest (7.0).
#   fill-underwater  Steel and Paper H row 5's railway index (`ledger:ev-railway-index-v1:line:139:right`, the lit
#                    stretch's page and its clock): the fall drawn on "crashed" (10.0-11.2), then the underwater fill
#                    under the October 1845 high - the rule at datum 53's own value (2057.5, READ from the series here,
#                    never typed; the compiler checks it) and unlabelled (A45's don't: C14) - from the peak to the end of
#                    the record, which never regains it; its time under water COMPUTED by the compiler ("4+ years", the
#                    last print 4.46 years on) and written over the fill. Judged with the label written (14.0).
FILL_FED_PROJECT = REPO / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
FILL_FED_PLATE = "ledger:fed-assets-reserves-history:line;idle=live;domain=-0.5,0.3"
FILL_AT, FILL_DUR = 4.0, 2.0
FILL_WATER_AT, FILL_WATER_DUR = 11.4, 2.0


def _fill_world(plate: str, project: Path) -> dict:
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(plate, (0, 0, 0), project)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    return world


def fill_below_zero() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    world = _fill_world(FILL_FED_PLATE, FILL_FED_PROJECT)
    world["page"].setdefault("axes", {})["hlines"] = [{"y": 0, "color": "deemph"}]   # the page's zero, named as a rule
    d = lambda i, s: {"kind": "datum", "index": i, "series": s}  # noqa: E731
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": s, "target": d(0, s)} for s in (0, 1)]
    species += [{"kind": "build_to", "at": 0.6, "dur": 2.4, "series": 1, "target": d(158, 1)},
                {"kind": "spread", "at": FILL_AT, "dur": FILL_DUR, "from": 1, "to_rule": 0, "side": "below", "from_index": 116}]
    assert not BST.validate_species(species, (0, 0, 0), FILL_FED_PLATE), BST.validate_species(species, (0, 0, 0), FILL_FED_PLATE)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden (reference beat): the dip below zero, filled to the rule (spread side)", scenes, {}, "16:9"), _base_uris()


def fill_underwater() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    world = _fill_world(LIT_PLATE, LIT_PROJECT)
    peak = float(world["page"]["series"][0]["pts"][53][1])   # the October 1845 high, READ off the datum
    axes = world["page"].setdefault("axes", {})
    axes["hlines"] = [dict(axes["hline"]), {"y": peak, "color": "deemph"}]   # the 1843 level (the object's) + the peak's
    species = [dict(e) for e in LIT_SPECIES[:2]] + [
        {"kind": "spread", "at": FILL_WATER_AT, "dur": FILL_WATER_DUR, "from": 0, "to_rule": 1, "side": "below", "peak": True,
         "from_index": 53, "label": "{years} years below the peak"}]
    assert not BST.validate_species(species, (0, 0, 0), LIT_PLATE), BST.validate_species(species, (0, 0, 0), LIT_PLATE)
    assert BST.check_spread_levels(world, species) == []   # the compiler's own page check: the peak's level, the duration
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: under water since the 1845 high (spread side + peak)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"fill-below-zero": fill_below_zero, "fill-underwater": fill_underwater})
FRAME_T.update({"fill-below-zero": 7.0,     # at rest: the bleed and the deepen landed at 6.0, the glow round the dip
                "fill-underwater": 14.0})   # the label written whole (the word ends 13.4), the fill and its glow at rest


# ---- P71 T18 (was P69 T53; Bravos A61): THE "?" AT THE UNKNOWN - H row 23's own beat --------------------------------------
# Steel and Paper H row 23c: dip 9 into HOST WINDOW 3, the newsroom, on "Decide for yourself which of those you believe"
# (the take 743.04-744.10, shifted by -735.04 so "Decide" lands at 8.00). The open question IS the sentence: a large "?"
# lands on "Decide" in the room's EMPTY LEFT THIRD (the H plate world-h3-newsroom-v1 is black there, the host stands
# right of centre with the certificate) - BOOM 08:52.5's crimson "?", placed where Bravos places it, beside the subject,
# never on it - and holds (an annotation, s91) until the certificate is thrown on "is the certificate". The H plate is a
# GENERATED image (gitignored, E99 s31), so the golden paints a STAND-IN: the room's dark blue, its black left third, a
# figure in the host's suit right of centre. Judged at 9.0: the pop settled (+0.4 s) and standing.
UNKNOWN_SHIFT = 735.04
UNKNOWN_DECIDE = {"kind": "unknown", "at": round(743.04 - UNKNOWN_SHIFT, 2), "dur": 3.0, "size": 240,
                  "target": {"kind": "point", "x": 0.13, "y": 0.42}}   # size: the row's - the room's empty third takes a
                                                                         # "?" twice BOOM's chart-side 122 (the frame read on the H plate)
NEWSROOM_STANDIN = [(0.0, 0.0, 0.245, 1.0),                                   # the black left third (the H plate's)
                    (0.66, 0.06, 0.70, 0.15), (0.63, 0.15, 0.73, 0.55),      # the host's head and suit
                    (0.64, 0.55, 0.675, 0.93), (0.685, 0.55, 0.72, 0.93),    # ... his legs
                    (0.30, 0.52, 0.52, 0.60), (0.80, 0.52, 1.0, 0.60)]       # the desks either side


def png_newsroom_standin(w: int, h: int) -> bytes:
    """The newsroom as shapes: a dark blue room, a black left third, the host and two desks - a committed input, not art."""
    import struct as _s
    room, black, suit, desk = (36, 48, 66), (8, 10, 14), (46, 70, 140), (58, 64, 74)
    inks = [black, suit, suit, suit, suit, desk, desk]
    raw = bytearray()
    for y in range(h):
        line = bytearray(b"\x00")
        for x in range(w):
            c = room
            for (x0, y0, x1, y1), ink in zip(NEWSROOM_STANDIN, inks):
                if x0 * w <= x < x1 * w and y0 * h <= y < y1 * h:
                    c = ink
                    break
            line += bytes(c)
        raw += line

    def chunk(tag: bytes, data: bytes) -> bytes:
        return _s.pack(">I", len(data)) + tag + data + _s.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", _s.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def unknown_decide() -> tuple[dict, dict]:
    """The "?" on "Decide for yourself": one `unknown`, held, in the newsroom stand-in's empty third."""
    import build_scene_timeline_f as BST
    species = [dict(UNKNOWN_DECIDE)]
    assert not BST.validate_species(species, (0, 0, 0), "plate-newsroom"), BST.validate_species(species, (0, 0, 0), "plate-newsroom")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-newsroom", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    uris["plate-newsroom"] = uri("image/png", png_newsroom_standin(320, 180))
    return _timeline("Golden: the \"?\" lands on \"Decide for yourself\" in the room's empty third", scenes, {}, "16:9"), uris


SURFACES.update({"unknown-decide": unknown_decide})
FRAME_T.update({"unknown-decide": 9.0})   # "Decide" at 8.0: the pop settled (+0.4) and the "?" standing (it leaves at 11.0)


# ---- P71 T27 (was P69 T75; harvest v2 A53): THE LEAD-LAG BRACKET - a bracket across two series, its label the lag -----
#   lead-lag-bracket  A REFERENCE beat (the plan's H row 9 - "seven percent" in 2000 to AI's "eight" - has no object on
#                     disk that carries a 7 or an 8: the H door's own page_rail docstring, BODY_DEPARTURES row 9, E77; and
#                     ev-bravos-original-v1 is SOURCES-TO-VERIFY, the operator's "re-read the source before this file is
#                     cited for anything"). Two series READ off the VERIFIED divergence object (ev-divergence-v1, H's own
#                     OPEN_PAGE, names corrected 2026-09-03), never re-typed, composed into a two-line page of their own
#                     (T13's precedent: a temporary object through the compiler's own path) on H's hook domain (80 ..
#                     1.06 x the pair's max, the door's own read): the semiconductor stocks topped at 261.08 on datum 188
#                     (x 2026.4709) and the mega-caps at 123.16 on datum 217 (x 2026.5886), 43 days later. The semis' top
#                     is ringed (the `ring` species' dashed form - E56: a datum on a chart), then BOOM's ELBOW (16:27.0)
#                     runs from under that ring down to the mega-caps' level and across to their top, and the compiler
#                     WRITES the lag it computes from the two x - "6 weeks" (check_lead_lag; no label is typed). Judged
#                     landed and held. `form` / `extra` are for test_lead_lag's reads only (the level form, a relight) -
#                     the committed golden is the plain call.
LAG_OBJECT = LEVEL_PROJECT / "evidence/objects/ev-divergence-v1.series.json"
LAG_FROM_SERIES = (1, 2)                # the object's SEMICONDUCTOR STOCKS and MEGA-CAP TECH STOCKS ...
LAG_TOPS = (188, 217)                   # ... and their tops (each series' own maximum, checked below)
LAG_ID = "ref-semis-lead-megacaps"
LAG_PLATE = f"ledger:{LAG_ID}:line::right;idle=live;domain=%g,%g"
LAG_AT, LAG_DUR, LAG_RING_AT = 8.0, 1.6, 6.6
LAG_RISE_PX = 30                        # the engine's LPLAG.RISE_PX (BOOM 16:13.0) - the level form's read in test_lead_lag
RING_MIN_RY_PX = 40                     # species/ring.mjs RING.MIN_RY: the ring on a bare datum the elbow's tip clears


def lead_lag_series() -> dict:
    """The reference page's object: the two lines off the committed file, their tops asserted, their words the file's."""
    obj = json.loads(LAG_OBJECT.read_text(encoding="utf-8"))
    lines = []
    for si, top in zip(LAG_FROM_SERIES, LAG_TOPS):
        s = obj["series"][si]
        assert max(range(len(s["pts"])), key=lambda j: s["pts"][j][1]) == top, (si, top)
        lines.append({k: s[k] for k in ("name", "label", "color", "pts")})
    return {"title": "The chips topped first", "sub": "Reference beat: " + lines[0]["name"].lower() + " against "
            + lines[1]["name"].lower() + ", 100 = Aug '25, log scale", "src": obj["src"], "log": True,
            "ylabel": obj["ylabel"], "xticks": obj["xticks"], "series": lines}


def lead_lag_bracket(form: str | None = None, extra: list | None = None) -> tuple[dict, dict]:
    import tempfile
    import build_scene_timeline_f as BST
    series = lead_lag_series()
    assert LPG.validate(series, "line") == [], LPG.validate(series, "line")
    plate = LAG_PLATE % (80.0, float(round(max(v for s in series["series"] for _x, v in s["pts"]) * 1.06)))
    last = len(series["series"][0]["pts"]) - 1
    species = [
        {"kind": "build_to", "at": 0.5, "dur": 5.0, "series": 0, "target": {"kind": "datum", "index": last}},
        {"kind": "build_to", "at": 0.5, "dur": 5.0, "series": 1, "target": {"kind": "datum", "index": last}},
        {"kind": "ring", "at": LAG_RING_AT, "dur": round(RUNTIME - LAG_RING_AT, 2), "form": "dashed",
         "target": {"kind": "datum", "index": LAG_TOPS[0], "series": 0}},
        {"kind": "bracket", "at": LAG_AT, "dur": LAG_DUR, "from": {"series": 0, "datum": LAG_TOPS[0]},
         "to": {"series": 1, "datum": LAG_TOPS[1]}, "form": form or "elbow"},
    ] + [dict(e) for e in (extra or [])]
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{LAG_ID}.series.json").write_text(json.dumps(series), encoding="utf-8")
            world = BST.world_for_plate(plate, (0, 0, 0), Path(td))
            BST.stamp_full_stage(world["page"])
            BST.derive_rescale_states(world, species, plate, Path(td))   # the compiler's own checks: check_lead_lag writes the lag
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the semis topped six weeks before the mega-caps (a lead-lag bracket)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"lead-lag-bracket": lead_lag_bracket})
FRAME_T.update({"lead-lag-bracket": round(LAG_AT + LAG_DUR + 0.4, 2)})   # landed and held: the elbow, its heads and "6 weeks"


# ---- P71 T25 (was P69 T74; the Bravos harvest v2 A51, D40 15:16-15:30): THE PROJECTED OVERTAKE -----------------------
# Steel and Paper H row 16's capex consensus: the $480B the year opened on, the $690B consensus now, and the 2027
# consensus ($870B) as a PROJECTED bar - a bar whose height IS a sourced estimate (E77: no `value` of its own), drawn on
# `chart_to extend {bar: 2}` at 11.0 over 2.5 s: the field makes room, the bar surges DASHED, "2027E consensus" is
# written over its value, and the bracket runs from its top to #1's column (the tallest ACTUAL bar, the $690B) with the
# computed gap, "+$180B". Every figure is READ off the committed series file (`ev-capex-consensus-v1`), never re-typed;
# the colours are the file's. Read at rest after the bracket has landed.
OVERTAKE_SERIES = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-capex-consensus-v1.series.json"
OVERTAKE_SRC = "PIMCO, Figures 2-3 via the evidence dossier (B1) - the 2027 consensus"


def overtake_capex(opens_on: bool = False) -> dict:
    """The capex field with its 2027 bar a PROJECTION (P71 T25) - the values and colours off the series file; with
    `opens_on`, the page is born on the year's opening estimate alone and its rank is written in the field."""
    cap = json.loads(OVERTAKE_SERIES.read_text(encoding="utf-8"))
    by = {b["label"]: b for b in cap["bars"]}
    nxt = by["2027 consensus"]
    obj = {"title": cap["title"],
           "sub": "The five largest hyperscalers' capital spending, US$ billions - consensus estimates, 2027 projected",
           "src": cap["src"], "unit": "$", "unit_suffix": "B",
           "bars": [{"label": k, "value": by[k]["value"], "color": by[k]["color"]} for k in ("Start of year", "2026 consensus")]
                   + [{"label": "2027 consensus", "color": nxt["color"],
                       "projected": {"value": nxt["value"], "label": "2027E consensus", "tier": "PLAUSIBLE", "src": OVERTAKE_SRC}}]}
    if opens_on:
        obj["opens_on"] = {"bar": "Start of year", "rank": "largest estimate"}
    return obj


def projected_overtake() -> tuple[dict, dict]:
    """P71 T25: the projected overtake AT REST - the dashed 2027E bar past the $690B leader, its bracket and its gap."""
    import tempfile
    import build_scene_timeline_f as BST
    plate = "ledger:fx-capex-overtake:bars"
    species = [{"kind": "chart_to", "to": "extend", "at": 11.0, "dur": 2.5, "bar": 2}]
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/fx-capex-overtake.series.json").write_text(json.dumps(overtake_capex()), encoding="utf-8")
        saved = BST.ASPECT
        BST.ASPECT = "16:9"
        try:
            world = BST.world_for_plate(plate, (0, 0, 0), ep)
            BST.stamp_full_stage(world["page"])
            BST.derive_rescale_states(world, species, plate, ep)
        finally:
            BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the projected overtake (H row 16's capex, the 2027 consensus)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"projected-overtake": projected_overtake})
FRAME_T.update({"projected-overtake": 14.2})   # at rest: the extend ends at 13.5 (11.0 + 2.5), the bracket and its gap landed



# ---- P71 T28 (was P69 T76; the Bravos harvest v2 A41 and A21): THE LINE PAINTER ------------------------------------
# Both on Steel and Paper H's railway page - the COMMITTED `ev-railway-index-v1` object, read in place, never re-typed
# (its one crimson series, 442 railway companies 1843-1850, the peak at datum 53 and the trough at 139) - in the long
# form, live, on a full stage, as H draws it.
#   enter-trace     A41 "trace first, furniture after" (Bravos HIS 00:00-00:06): the page ENTERS BY ITS TRACE - the
#                   railway mania's shape (the climb and the crash) draws on the bare charcoal over the page's build
#                   (3.0 s), and only then does the furniture land: the frame, the tick labels, the title written, the
#                   end tag, the key. Judged 0.3 s past the trace (3.30): the whole line drawn, its frame landed, its
#                   tick labels arriving, the title a third written, the tag and the key still to come - the order, in one frame.
#   ink-from-crash  A21 "the line changes ink at a point" (HIS 05:58 "red after the peak"): H row 9's own sentence, the
#                   take's words shifted by -67.46 s as the lit-stretch golden's are ("crashed" 77.46 -> 10.00): the
#                   build beat draws the climb to the PEAK (datum 53), and on "crashed" (1.2 s) the fall draws from
#                   it in the fall's own ink (`ink_from: {x: the peak's x}` - no colour named, so the stretch's SIGN:
#                   it falls, so blood red, E28), glowing in the new ink (T37b's layers). Judged 0.5 s after the landing.
TRACE_OBJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-railway-index-v1.series.json"
TRACE_OPTS = ";idle=live;readability=longform"
TRACE_PLATE = f"ledger:ref-rail-trace:line::right:trace{TRACE_OPTS}"
INK_PLATE = f"ledger:ref-rail-ink:line:139:right:axes{TRACE_OPTS}"
TRACE_KINETICS = {"idle": True, "min_jerk": True, "curvature_stroke": True}   # the flags a compiled cut carries that these
#   frames read (build_kinetics; the H timeline's own): the trace's PACE is the pen law (curvature_stroke - without it the
#   build falls back to expoOut, 80 % of the line down in its first half-second), the caps' clock (min_jerk), the page's life
INK_SHIFT = 67.46
INK_CRASH_AT, INK_CRASH_S = round(77.46 - INK_SHIFT, 2), 1.2   # "crashed", RAIL_CRASH_S (build_episode_h.py)
INK_SPECIES = [
    {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": 0, "target": {"kind": "datum", "index": 53}},   # the build beat draws to the peak
    {"kind": "build_to", "at": INK_CRASH_AT, "dur": INK_CRASH_S, "series": 0, "target": {"kind": "datum", "index": 139}},   # "crashed"
]


def rail_series(ink_from: bool = False) -> dict:
    """The committed railway object, as a page reads it; with `ink_from`, the stroke re-inks from its PEAK (the datum
    the object's own max is, read off its points) and names no colour - the stretch's sign draws it."""
    obj = json.loads(TRACE_OBJECT.read_text(encoding="utf-8"))
    if ink_from:
        pts = obj["series"][0]["pts"]
        peak = max(range(len(pts)), key=lambda i: pts[i][1])
        assert peak == 53, peak
        obj["series"][0]["ink_from"] = {"x": pts[peak][0]}
    return obj


def _rail_surface(plate: str, obj: dict, species: list, title: str) -> tuple[dict, dict]:
    import tempfile
    import build_scene_timeline_f as BST
    assert LPG.validate(obj, "line") == [], LPG.validate(obj, "line")
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{plate.split(':')[1]}.series.json").write_text(json.dumps(obj), encoding="utf-8")
            world = BST.world_for_plate(plate, (0, 0, 0), Path(td))
            BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline(title, scenes, {}, "16:9")
    tl["kinetics"] = dict(TRACE_KINETICS)
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


def trace_surface(enter: str = "trace") -> tuple[dict, dict]:
    """The railway page entering by `enter` (the test's control is `axes`: the same page with its furniture on frame 0)."""
    return _rail_surface(TRACE_PLATE.replace(":trace", ":" + enter), rail_series(), [],
                         f"Golden: the line traces before its furniture (enter={enter})")


def enter_trace() -> tuple[dict, dict]:
    return trace_surface()


def ink_from_crash() -> tuple[dict, dict]:
    return _rail_surface(INK_PLATE, rail_series(ink_from=True), [dict(e) for e in INK_SPECIES],
                         "Golden: the line changes ink at the peak - red after it (ink_from)")


SURFACES.update({"enter-trace": enter_trace, "ink-from-crash": ink_from_crash})
FRAME_T.update({"enter-trace": 3.3,   # the trace done (the build, 3.0 s), the frame landed (0.33), the labels arriving, the title a third written
                "ink-from-crash": round(INK_CRASH_AT + INK_CRASH_S + 0.5, 2)})   # 11.70: the fall landed red 0.5 s ago



# ---- P71 T29 (was P69 T77; harvest v2 F2, BUB #3): GLOW EDGES - a glow outline on the named bar -----------------------
#   glow-outline-bar  Steel and Paper H row 18b's concentration page - the row's own plate string (CHAPTER_PAGE: one
#                     bar, 20 (%), the long form, live, soft-shouldered) and its own figure ("20%" written as the bar
#                     grows, the row's `figure` on the page's word) - with the take's words shifted by -384.12 s so
#                     the page lands at 0.0. On "twenty percent" (385.21 -> 1.09) the 20 bar is LIT: a glow outline
#                     lands on it - an edge in its crimson burning near-white round the bar, the fill glow's two halos
#                     in that edge's light (BUB #3's lit region, the one glow system: lpFillGlow on the outline's
#                     stroke). No body row adopts it before HG1 (common rule (f)); this is the beat the plan names.
#                     Judged at 4.0: the bar stood (the page draws 0.0-3.0), the glow held (an annotation, 0 events -
#                     no `pulse`).
GLOW_SHIFT = 384.12
GLOW_AT = round(385.21 - GLOW_SHIFT, 2)          # "twenty percent"
GLOW_DUR = round(385.89 - 385.21, 2)             # ... the word
GLOW_SPECIES = [
    {"kind": "figure", "at": 0.0, "dur": 1.2, "target": {"kind": "datum", "index": 0}, "text": "20%"},   # the row's own: "20%" as it stands
    {"kind": "glow", "at": GLOW_AT, "dur": GLOW_DUR, "bar": 0},                                       # "twenty percent": the 20 bar lit
]


def glow_outline_bar(glow: dict | None = None, extra: list | None = None) -> tuple[dict, dict]:
    """The golden's timeline; `glow` (the glow row's keys, or {} for NO glow) and `extra` species are test_glow_edges'
    reads only - the committed golden is the plain call."""
    import build_scene_timeline_f as BST
    species = [dict(GLOW_SPECIES[0])]
    if glow != {}:
        species.append(dict(GLOW_SPECIES[1], **(glow or {})))
    species += [dict(e) for e in (extra or [])]
    assert not BST.validate_species([dict(e) for e in species], (0, 0, 0), CHAPTER_PAGE),         BST.validate_species([dict(e) for e in species], (0, 0, 0), CHAPTER_PAGE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(CHAPTER_PAGE, (0, 0, 0), CHAPTER_PROJECT)
        BST.stamp_full_stage(world["page"])
        BST.derive_rescale_states(world, species, CHAPTER_PAGE, CHAPTER_PROJECT)   # the compiler's own page checks: check_glow's truth
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: the named bar lit - a glow outline on the 20 (glow)", scenes, {}, "16:9")
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


SURFACES.update({"glow-outline-bar": glow_outline_bar})
FRAME_T.update({"glow-outline-bar": 4.0})   # the bar stood (its page draws 0.0-3.0), the glow held since 1.09 + its fade



# P73 T4: THE SUPPLY-CHAIN ICONS on a route - the AMD RFSoC story's chain as a ROW flow, every node a SOURCED Lucide glyph
# the intake added (assets/icons/SOURCES.md): the maker (building), the distributor (warehouse), the reseller (store),
# the board maker in China (factory), the crowdfunding storefront (store) and its backers (user); one dot of the part
# riding each arrow, and the link INTO CHINA - the one an export licence governs - FAILING (T17's disc and X). A TEST-BED
# beat: six nodes because FLOW_NODES caps a row at six (the slice's seven-stop route merges "Hong Kong / China" into the
# board maker's node); the route is the MECHANISM Tom's names (PLAUSIBLE), no figure on it, so no tier is owed on screen.
SUPPLY_ROUTE_NODES = [("amd", "building", "AMD"), ("distributor", "warehouse", "DISTRIBUTOR"), ("reseller", "store", "RESELLER"),
               ("puzhi", "factory", "PUZHI, CHINA"), ("crowd", "store", "CROWD SUPPLY"), ("backers", "user", "BACKERS")]
SUPPLY_ROUTE_AT, SUPPLY_ROUTE_TOKENS_AT, SUPPLY_ROUTE_FAIL_AT = 4.0, 8.0, 8.8   # the five arrows are drawn by 7.845 s (flowClock); the part
                                                           # starts down them on the next word; the licence link breaks on its


def flow_supply_route() -> tuple[dict, dict]:
    """P73 T4: the supply route as six chips in a row, each clothoid arrow drawn by length, one dot of the part riding
    each; then the reseller -> China link FAILS - the neg-ink disc with a white X at its middle, the arrow reddened and its
    halves retracted, both nodes standing. Judged 1.0 s after the failure (FRAME_T 9.8): the disc settled, the X struck."""
    import build_scene_timeline_f as BST
    species = [{"kind": "flow", "at": SUPPLY_ROUTE_AT, "dur": 18.0, "idle": "breath",
                "target": {"kind": "region", "x0": 0.04, "y0": 0.28, "x1": 0.96, "y1": 0.78},   # the stage's width: six chips need it
                "nodes": [{"id": i, "icon": icon, "label": label} for i, icon, label in SUPPLY_ROUTE_NODES],
                "edges": [[a[0], b[0]] for a, b in zip(SUPPLY_ROUTE_NODES, SUPPLY_ROUTE_NODES[1:])],
                "tokens": {"from_at": SUPPLY_ROUTE_TOKENS_AT, "n": 1},
                "fail": {"edge": ["reseller", "puzhi"], "at": SUPPLY_ROUTE_FAIL_AT}}]
    assert not BST.validate_species(species, (0, 0, 0), "plate-plain"), BST.validate_species(species, (0, 0, 0), "plate-plain")
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    for name in sorted(BST.species_icons(species[0])):
        uris[BST.ICON_PREFIX + name] = BST.icon_geometry(name)
    tl = _timeline("Golden: the supply route - sourced supply-chain glyphs, the part on its arrows, the licence link failing (test-bed beat)",
                   scenes, {}, None)
    tl["captions"], tl["caption_pages"] = [], []   # the harness's centred caption would sit on the row: the diagram is the frame
    return tl, uris


SURFACES.update({"flow-supply-route": flow_supply_route})
FRAME_T.update({"flow-supply-route": 9.8})   # the arrows drawn (7.845), the part on them, the failure 1.0 s old - disc settled, X struck


# ---- P73 T1: A CLAIMED FIGURE ON A CHART - the AMD RFSoC episode's price page -------------------------------------------
# Every figure off the P73 research pack (`amd-rfsoc/research/RESEARCH.md` s3), never typed from memory: DigiKey's qty-1
# prices for the part Patel linked ($35,979.02, sources/03) and the part on Puzhi's board ($31,354.40, sources/06), the
# board itself on Crowd Supply ($8,749, sources/02) and AMD's own academic RFSoC board ($2,499, sources/08) - all
# CONFIRMED - and Dylan Patel's two figures from his post of 2026-09-19 (sources/01: CONFIRMED that he said them; no
# evidence attached): "$4-5k to US companies at volume" (a RANGE) and "getting quoted $1k in China". On a LINEAR axis the
# $1k is a sliver - the honest picture. The base frame is the page at rest (every bar built, both claims drawn as his:
# outlined in their ink, quoted, "Dylan Patel, SemiAnalysis" over each); the proof instant is the claim's word, a solo
# on the $1k (the rest muted, his name lit with his figure).
CLAIM_PATEL = {"by": "Dylan Patel", "standing": "SemiAnalysis", "said": "2026-09-19", "evidence": "none",
               "src": "his post on X"}


def claim_price_object() -> dict:
    """The price page's object - test_claim_figure proves this same page. In THOUSANDS (`unit_suffix: "k"`, three
    significant figures on the bars) so every figure is written at the page's width, and Patel's quotes are his own
    words ("$4-5k", "$1k"); the exact DigiKey / Crowd Supply / Real Digital prices are on the source line."""
    return {"title": "One chip, six prices",
            "sub": "Thousands of US dollars - AMD's XCZU47DR RFSoC, and two boards built on an RFSoC",
            "src": "DigiKey qty 1 $35,979.02 (XCZU47DR-2FSVG1517I) and $31,354.40 (-2FFVE1156I), Crowd Supply $8,749 "
                   "(PZSDR P047), Real Digital $2,499 (RFSoC 4x2, academic), all 2026-09-26",
            "unit": "$", "unit_suffix": "k", "readability": "longform",
            "bars": [{"label": "DigiKey list", "value": 36.0, "color": "crimson"},
                     {"label": "The board's chip", "value": 31.4, "color": "crimson"},
                     {"label": "Puzhi's board", "value": 8.75, "color": "cobalt"},
                     {"label": "AMD's own board", "value": 2.5, "color": "cobalt"},
                     {"label": "US volume", "value": [4, 5], "color": "amber", "claim": dict(CLAIM_PATEL, quote="$4-5k")},
                     {"label": "China quote", "value": 1, "color": "amber", "claim": dict(CLAIM_PATEL, quote="$1k")}]}


CLAIM_WORD_AT = 12.0   # "...getting quoted a thousand dollars in China" - the solo on the $1k


def claim_bar() -> tuple[dict, dict]:
    """P73 T1: the claims at rest (the base frame) and at the claim's word (the proof instant)."""
    import tempfile
    import build_scene_timeline_f as BST
    plate = "ledger:fx-rfsoc-prices:bars"
    species = [{"kind": "solo", "at": CLAIM_WORD_AT, "dur": 0.6, "bar": 5}]
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/fx-rfsoc-prices.series.json").write_text(json.dumps(claim_price_object()), encoding="utf-8")
        saved = BST.ASPECT
        BST.ASPECT = "16:9"
        try:
            world = BST.world_for_plate(plate, (0, 0, 0), ep)
            BST.stamp_full_stage(world["page"])
            BST.derive_rescale_states(world, species, plate, ep)
        finally:
            BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: a claimed figure on a chart (the AMD RFSoC price page)", scenes, {}, "16:9")
    return tl, dict(_base_uris(), **BST.longform_assets(tl))   # the long form's page: its Inter faces


SURFACES.update({"claim-bar": claim_bar})
FRAME_T.update({"claim-bar": 8.0})   # at rest: every bar built and written, both claims his; the solo waits for 12.0


# ---- P73 T2: THE DATED EVENT TIMELINE PAGE (the AMD RFSoC episode's beat 5) -------------------------------------------
# The research pack's section 2 (`scratchpad/amd-rfsoc/research/RESEARCH.md`), each date at its stated precision and
# tier: the control (FR 2017-16904), the chip family announced (Xilinx, 2019-02-20), the campaign live by June 2026
# (PLAUSIBLE - CNX), its end (Crowd Supply), Patel's post (X), the article (Tom's Hardware, its feed date), and the ship
# date Tom's reported (2026-11-06, PLAUSIBLE) that the Crowd Supply page now shows as 6 May 2027 (CONFIRMED).
TIMELINE_STORY = {
    "title": "From the rule to the post",
    "sub": "The dates this story turns on - to scale inside each stretch; the empty years between are cut",
    "src": "Federal Register 2017-16904; Xilinx (2019-02-20); CNX; Crowd Supply; X (Patel); Tom's Hardware (2026-09-24)",
    "today": "2026-09-26",
    "events": [
        {"date": "2017-08-15", "label": "US control on RFSoC-type chips (3A001.a.14)", "tier": "CONFIRMED"},
        {"date": "2019-02-20", "label": "Xilinx announces Gen 3 RFSoC", "tier": "CONFIRMED"},
        {"date": "2026-06", "label": "Puzhi board on Crowd Supply", "tier": "PLAUSIBLE"},
        {"date": "2026-08-27", "label": "Campaign ends", "tier": "CONFIRMED"},
        {"date": "2026-09-19", "label": "Patel's post on X", "tier": "CONFIRMED"},
        {"date": "2026-09-24", "label": "Tom's Hardware, AMD's reply", "tier": "CONFIRMED"},
        {"date": "2026-11-06", "label": "Board ships", "tier": "PLAUSIBLE",
         "moved_to": {"date": "2027-05-06", "label": "Ships now", "tier": "CONFIRMED"}},
    ],
}
# one `build_to` per event on its word (the ship date named twice: its landing, then its move)
TIMELINE_WORDS = [{"kind": "build_to", "at": at, "dur": 0.5, "target": {"kind": "datum", "index": i}}
                  for i, at in ((0, 6.2), (1, 7.4), (2, 8.6), (3, 9.8), (4, 11.0), (5, 12.2), (6, 13.4), (6, 14.8))]
# (the page's build opens at ~4.4 s - the roll, the savour and the field - and its axis is drawn by ~5.8 s: the first word
# comes after it, as a row's first event does)
TIMELINE_PLATE = "ledger:amd-rfsoc-timeline:timeline"


def _event_timeline(aspect: str) -> tuple[dict, dict]:
    """P73 T2: the story's dates on one axis - two stretches (a tick a year, a tick a month) and the seven empty years
    between them cut and written, today marked, each event landing on its word and lit, the ship date struck and moved.
    Built as an episode row builds it: at 16:9 the page is the plate (`stamp_full_stage`)."""
    import build_scene_timeline_f as BST
    page = LPG.build_spec(TIMELINE_STORY, "timeline", None, "right")
    page["field"] = "scribble"
    species = [dict(w) for w in TIMELINE_WORDS]
    errs = BST.validate_species(species, (0, 0, 0), TIMELINE_PLATE)
    assert not errs, errs
    saved = BST.ASPECT
    BST.ASPECT = aspect
    try:
        BST.stamp_full_stage(page)
        world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
        BST.derive_rescale_states(world, species, TIMELINE_PLATE, REPO)
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the dated event timeline", scenes, {}, aspect if aspect != "16:9" else None), _base_uris()


SURFACES.update({"event-timeline": lambda: _event_timeline("16:9"),
                 "event-timeline-9x16": lambda: _event_timeline("9:16")})
FRAME_T.update({"event-timeline": 17.0,         # every event landed, the ship date struck at 14.8 and moved, "Ships now" lit
                "event-timeline-9x16": 17.0})   # the same instant on the portrait page: the axis upright, the column beside it


# ---- P73 T3: THE POST CARD - a press card whose header is a social post -----------------------------------------
# Proved on the AMD RFSoC story's post (research sources/01, retrieved 2026-09-26 through the public embed API): Dylan
# Patel, @dylan522p, 2026-09-19 16:41 UTC, 392,513 views at retrieval, the post's own words. The CROPS are stand-ins
# DRAWN here by the bars writer (the text lines as ink bars) - no screenshot of the real post or article is committed
# (generated images stay out of git). AMD's reply lands AFTER it as the second card of a PRESS STACK: the spokesperson's
# words as Tom's Hardware printed them (sources/04, PLAUSIBLE - the recipient's own report) under that paper's masthead.
# The reply is a press card and not a `record` because a record dock is a SLOT dock: at 16:9 every slot box intersects
# the press card's centre box and the post card paints over the typed words (P73 T3's finding) - the pile of two is
# the composition the grammar has.
POST_SLIDE = "ev-post-patel"
POST_CROP = PRESS_CROP                    # the default headline crop's aspect - the post card asks no new dock geometry
POST_PAPER = (253, 253, 251)              # a post's own white, not the newsprint cream the masthead cards are cut on
POST_BARS = [(0.05, 0.14, 0.62, 0.40), (0.645, 0.14, 0.95, 0.40), (0.05, 0.58, 0.93, 0.84)]   # line 1: the phrase, then the rest; line 2
POST_PHRASE = {"x0": 0.04, "y0": 0.1, "x1": 0.63, "y1": 0.44}
POST_META = {"kind": "press", "source": "X / @dylan522p, 19 Sep 2026",
             "phrase": POST_PHRASE, "phrase_text": "AMD needs to be investigated for treason.",
             "card": list(POST_CROP), "style": "post",
             "post": {"name": "Dylan Patel", "handle": "@dylan522p", "posted": "2026-09-19T16:41Z",
                      "counts": [{"label": "views", "value": 392513, "as_of": "2026-09-26"}],
                      "url": "https://x.com/dylan522p/status/2101350877932212621"}}
POST_UNDERLINE_AT = 7.0                   # the word "treason" on the golden's own clock
REPLY_SLIDE = "ev-press-amd-reply"
REPLY_ENTER = 11.0
REPLY_UNDERLINE_AT = 11.6                 # the word "unrelated"
REPLY_BARS = [(0.05, 0.12, 0.40, 0.36), (0.42, 0.12, 0.93, 0.36), (0.05, 0.50, 0.66, 0.74), (0.05, 0.84, 0.48, 0.96)]
REPLY_META = {"kind": "press", "source": "Tom's Hardware, 24 Sep 2026",
              "phrase": {"x0": 0.40, "y0": 0.08, "x1": 0.95, "y1": 0.40},
              "phrase_text": "This recent instance is unrelated to any direct AMD sales or shipments.",
              "card": list(POST_CROP)}
FRAME_T["press-post"] = 9.0               # the post card landed (5.0 + LAND_S) and held, its underline under the phrase fully drawn (7.0 + SQUIG_DRAW); the reply not yet entered


def press_post() -> tuple[dict, dict]:
    """P73 T3: ONE POST CARD on a bare plate - the press card with `style: post`, its header the poster's row (name,
    handle) over the post's date and its dated view count, the crop under the pulled phrase as provenance, the
    underline under the phrase on its word - then AMD's reply as the SECOND card of the pile (`press-post@proof-reply`):
    the post pushed one step back and dimmed, its post header still read above the reply. The press keys are the
    compiler's own (press_meta + dock_entry + assign_press_stack), so the golden is what two rows write."""
    import build_scene_timeline_f as BST
    evidence, uris, docks = {}, _base_uris(), []
    for aid, enter, meta, bars, paper in ((POST_SLIDE, 5.0, POST_META, POST_BARS, POST_PAPER),
                                          (REPLY_SLIDE, REPLY_ENTER, REPLY_META, REPLY_BARS, (250, 247, 240))):
        press = BST.press_meta(meta)
        evidence[aid] = {"title": press["source"], "source": press["source"], "species": "press",
                         "document": {"path": "golden", "sha256": "0" * 64}, "badges": []}
        uris[aid] = uri("image/png", png_bars(POST_CROP[0], POST_CROP[1], paper, bars))
        d = BST.dock_entry(aid, 0, enter, RUNTIME, 0, press=press, stack=True)
        d["badge_at"] = []
        docks.append(d)
    BST.assign_press_stack(docks)
    species = [{"kind": "callout", "form": "underline", "at": POST_UNDERLINE_AT, "dur": 2.0,
                "target": {"kind": "phrase", "dock": POST_SLIDE}},
               {"kind": "callout", "form": "underline", "at": REPLY_UNDERLINE_AT, "dur": 2.0,
                "target": {"kind": "phrase", "dock": REPLY_SLIDE}}]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": species}]
    return _timeline("Golden: the post card and the reply, a pile of two", scenes, evidence, None), uris


SURFACES.update({"press-post": press_post})


# ---- P73 T5: MAP POINTS - Hong Kong and Singapore on the vector map (the AMD RFSoC episode's beat 4) ------------------
# Hong Kong has no shape at 1:110m; it is a NAMED POINT from the gazetteer (assets/maps/places.json - Natural Earth 1:10m
# populated places at the world map's own commit, blob-verified), resolved onto the target by the compiler's OWN
# resolve_place_targets. The route is the MECHANISM BIS names ("Sometimes, a US export is routed through Hong Kong to avoid
# US export regulations." - RESEARCH-2 C2, CONFIRMED): no figure on the map, so no tier is owed on screen. United States ->
# Hong Kong -> China, framed `;fit=tight` on the two countries (the tightest box that holds the arc's origin - the map has
# no central meridian, so the US sits at the left edge and the route crosses Europe and Asia).
TRANSSHIP_USA_AT, TRANSSHIP_ROUTE_AT = 4.0, 5.0            # the maker lights; the route leaves it on the next word
TRANSSHIP_HK_AT = TRANSSHIP_ROUTE_AT + 0.9                 # Hong Kong lights and pings on the word the route LANDS on it (+ ARC.DRAW_S)
TRANSSHIP_ONWARD_AT, TRANSSHIP_CHN_AT = 7.2, 8.1           # the second leg leaves Hong Kong; China lights as it lands
TRANSSHIP_TOKENS_AT = 8.4                                  # the part starts down both legs once the route is whole


def _map_surface(plate: str, species: list[dict], title: str) -> tuple[dict, dict]:
    """A vector-map golden through the compiler's own route: the world off the plate id, the species validated, every named
    place resolved (resolve_place_targets), the map data under its one key. Captions off: the map frames its places at the
    stage's centre, where the harness's caption sits (vecmap-route-tokens' rule)."""
    import build_scene_timeline_f as BST
    world = BST.world_for_plate(plate, (0, 0, 0), None)
    errs = BST.validate_species(species, (0, 0, 0), plate)
    assert not errs, errs
    BST.resolve_place_targets(species)
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    uris = _base_uris()
    uris[BST.MAP_PREFIX + world["map"]] = BST.world_map_json(world["map"])
    tl = _timeline(title, scenes, {}, None)
    tl["captions"], tl["caption_pages"] = [], []
    return tl, uris


def vecmap_transship() -> tuple[dict, dict]:
    """P73 T5: the United States lights (4.0); the route leaves it (5.0) and lands on HONG KONG - a named point, lit as a
    dot and its name and pinging as the route lands (5.9); the second leg leaves Hong Kong (7.2) and China lights as it
    lands (8.1); one dot of the part rides each leg from 8.4. Judged at 9.4: both legs drawn, the three places lit, the
    part on the route; the ping rides PROOF_FRAMES (@proof-ping, 6.6 - its pulse half way out)."""
    usa, chn, hkg = {"kind": "country", "id": "USA"}, {"kind": "country", "id": "CHN"}, {"kind": "place", "id": "HKG"}
    species = [{"kind": "light", "at": TRANSSHIP_USA_AT, "dur": 20.0, "idle": "breath", "target": dict(usa)},
               {"kind": "arc", "at": TRANSSHIP_ROUTE_AT, "dur": 20.0, "from": dict(usa), "to": dict(hkg),
                "tokens": {"from_at": TRANSSHIP_TOKENS_AT, "n": 1}},
               {"kind": "light", "at": TRANSSHIP_HK_AT, "dur": 20.0, "idle": "breath", "ping": True, "target": dict(hkg)},
               {"kind": "arc", "at": TRANSSHIP_ONWARD_AT, "dur": 20.0, "from": dict(hkg), "to": dict(chn),
                "tokens": {"from_at": TRANSSHIP_TOKENS_AT, "n": 1}},
               {"kind": "light", "at": TRANSSHIP_CHN_AT, "dur": 20.0, "idle": "breath", "target": dict(chn)}]
    return _map_surface("vecmap:USA,CHN;fit=tight", species,
                        "Golden: map points - the United States -> Hong Kong -> China transshipment route")


def vecmap_place_singapore() -> tuple[dict, dict]:
    """P73 T5: the second place, framed TIGHT on its region - Southeast Asia to Taiwan (`vecmap:MYS,THA,VNM,TWN;fit=tight`):
    SINGAPORE lights and pings on its word (5.0) at the foot of the peninsula, and HSINCHU (Taiwan's science-park city, a
    third named point) lights on a later one (6.4). A TEST-BED beat: two places on their words, no route and no figure
    claimed. Judged at 7.5, both lit; Singapore's ping rides PROOF_FRAMES (@proof-ping, 5.7)."""
    species = [{"kind": "light", "at": 5.0, "dur": 20.0, "idle": "breath", "ping": True, "target": {"kind": "place", "id": "SGP"}},
               {"kind": "light", "at": 6.4, "dur": 20.0, "idle": "breath", "target": {"kind": "place", "id": "HSINCHU"}}]
    return _map_surface("vecmap:MYS,THA,VNM,TWN;fit=tight", species, "Golden: map points - Singapore and Hsinchu lit (test-bed beat)")


SURFACES.update({"vecmap-transship": vecmap_transship, "vecmap-place-singapore": vecmap_place_singapore})
FRAME_T.update({"vecmap-transship": 9.4,         # both legs drawn (8.1), USA / Hong Kong / China lit, the part 1.0 s down each leg
                "vecmap-place-singapore": 7.5})  # Singapore and Hsinchu lit, both past their pop


def vecmap_pacific() -> tuple[dict, dict]:
    """P73 T6 (R26-406): the transshipment route on a PACIFIC-CENTRED map (`vecmap:USA,CHN;meridian=150;fit=tight`) - the
    same row as vecmap-transship on the same clock, only the plate's meridian changed: the United States lights (4.0) at
    the frame's right, the route leaves it WEST across the Pacific (5.0) and lands on Hong Kong (5.9, lit + ping), the
    second leg runs on to China (7.2) and China lights as it lands (8.1); one dot of the part on each leg from 8.4.
    Russia stands whole across 180 (Natural Earth's cut joined), the seam at 30 W off the frame. Hong Kong's name is
    written BELOW its dot (`side`, the author's): the route now ARRIVES from the east, where the auto order's first
    choice (right) would put the name on the line. Judged at 9.4."""
    tl, uris = vecmap_transship()
    species = tl["scenes"][0]["species"]
    for sp in species:
        if sp["kind"] == "light" and sp["target"].get("id") == "HKG":
            sp["target"]["side"] = "below"
    return _map_surface("vecmap:USA,CHN;meridian=150;fit=tight", species,
                        "Golden: a Pacific-centred map - the United States -> Hong Kong -> China route across the Pacific")


SEAM_SPLIT_RUS_AT = 4.0   # Russia lights on its word


def vecmap_seam_split() -> tuple[dict, dict]:
    """P73 T6 (R26-406): a country the SEAM cuts, rendered clean - the whole world centred on the Americas
    (`vecmap;meridian=-90`), so the seam runs down 90 E through Russia, China, India and Antarctica. Russia lights (4.0)
    and lights as TWO halves, one at each edge of the map - no ring streaks across the frame, no fill leaks between them;
    the old seam (180, the Bering Strait) sits inside the frame with Chukotka joined to the mainland. A test-bed beat: no
    route and no figure claimed. Judged at 5.0, lit."""
    species = [{"kind": "light", "at": SEAM_SPLIT_RUS_AT, "dur": 20.0, "idle": "breath", "target": {"kind": "country", "id": "RUS"}}]
    return _map_surface("vecmap;meridian=-90", species, "Golden: the seam - Russia cut at 90 E on an Americas-centred map, lit clean")


SURFACES.update({"vecmap-pacific": vecmap_pacific, "vecmap-seam-split": vecmap_seam_split})
FRAME_T.update({"vecmap-pacific": 9.4,      # the transship's instant: both legs drawn across the Pacific, the three places lit
                "vecmap-seam-split": 5.0})  # Russia's two halves lit, one at each edge


# ---- P71 T31 (was P69 T79; the Bravos harvest v2 S5): THE AXIS-LESS STORY PAGE AND ITS CATEGORY PILLS ------------------
#   story-bars-pills   Steel and Paper H row 19's two clocks - the COMMITTED `ev-two-clocks-bars-v1` object, read in place
#                      (1840s railways 20 years, today's compute 5; never re-typed) - drawn with NO AXIS (`axes: "none"`)
#                      and each bar's name in its CATEGORY PILL over it (`pill: true`), as H draws the page: the long
#                      form, live, full stage, compute the emphasised bar ("about five years", its counting pill). BUB
#                      0:48-1:12: the red capsule over the value badge, no tick, no gridline, one rule under the row.
#                      Judged at rest (6.0 s, the build landed): the twenty stands four times the five from one zero, both
#                      values written, each name in its bar's own ink over its stack.
PILLS_OBJECT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-two-clocks-bars-v1.series.json"
PILLS_PLATE = "ledger:ref-two-clocks-pills:bars:1:right:axes:cut;idle=live;readability=longform"


def clocks_axisless() -> dict:
    """The committed two-clocks object with `axes: "none"` and every bar's `pill` - nothing else moves."""
    obj = json.loads(PILLS_OBJECT.read_text(encoding="utf-8"))
    assert [b["value"] for b in obj["bars"]] == [20, 5], obj["bars"]
    obj["axes"] = "none"
    for b in obj["bars"]:
        b["pill"] = True
    return obj


def story_bars_pills() -> tuple[dict, dict]:
    import tempfile
    import build_scene_timeline_f as BST
    obj = clocks_axisless()
    assert LPG.validate(obj, "bars") == [], LPG.validate(obj, "bars")
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{PILLS_PLATE.split(':')[1]}.series.json").write_text(json.dumps(obj), encoding="utf-8")
            world = BST.world_for_plate(PILLS_PLATE, (0, 0, 0), Path(td))
            BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": []}]
    tl = _timeline("Golden: the axis-less story page and its category pills (H row 19's two clocks)", scenes, {}, "16:9")
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


SURFACES.update({"story-bars-pills": story_bars_pills})
FRAME_T.update({"story-bars-pills": 6.0})   # at rest: the build (3.0 s) landed, both names in their pills


# ---- P72 T46g (R26-407; Bravos A56, BOOM 17:55.5-17:58.5): THE BOX ROUND THE LAST MOVE -------------------------------------
#   box-the-last-move  `span-decade`'s own page (the memory-makers line and its three peers, no emphasis) carrying a span in
#                      the BOX form round the memory-makers' LAST MOVE - its fall from the Aug 2025 peak (datum 191, the
#                      1,074 the `ring-dashed-chip` golden rings) to today (234): a dashed rectangle round that series' own
#                      ink over the stretch, x from..to and y the stretch's own min..max, both padded - never the plot, never
#                      the other three lines. Drawn round by length on its word (8.0 + DRAW_S), standing for its `dur` (3.0),
#                      then leaving for the dated rule. Judged standing whole (9.2 s), the page built (7.4) and the box closed.
BOX_SPAN = {"kind": "span", "form": "box", "at": 8.0, "dur": 3.0, "from": 191, "to": 234}


def box_the_last_move() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    species = [dict(BOX_SPAN)]
    assert not BST._validate_entry(species[0]), BST._validate_entry(species[0])   # the grammar's own word: a box, no name
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: the box round the last move (A56)", scenes, {}, None), _base_uris()


SURFACES.update({"box-the-last-move": box_the_last_move})
FRAME_T.update({"box-the-last-move": 9.2})   # the box drawn whole (8.0 + DRAW_S) and standing - its leave begins at 10.65


# ---- P72 T53 (f) / R26-413 (a): A CARD KEEPS ITS SOURCE AT ANY SIZE ------------------------------------------------------
#   card-keeps-its-source   Steel and Paper H row 9's railway index (the COMMITTED `ev-railway-index-v1` object, its
#                           points and its own citation read in place) drawn as a CHART CARD for 672 displayed px - 0.35
#                           of the stage, P71 T33's stack twin (BOOM 08:48) - by chart_card's own `card` profile
#                           (`chart_card.card_timeline`, the path every card takes: the whole stage is the card). Two
#                           changes, both P71 T33's twin's: the era as the title ("Railway shares, 1845"; the object's
#                           own headline wraps to two lines at this width) and its "1843 level" rule dropped. The source's
#                           first clause ("Campbell & Turner railway share index") will not fit one line at the floor,
#                           so it is ELLIPSISED ("Campbell & Turner..."), and at the floor it would cost the plot
#                           PLOT_MIN, so it stands at the citation's size (LP_CARD.SRC_CITE_X) - before R26-413 this
#                           card cited nothing - and its shorter plot still states its scale in two ticks (1000, 2000: a
#                           card's axis takes a phone panel's divisions, E28). Judged at the card's landing (LAND_T).
CARD_SOURCE_OBJECT = LIT_PROJECT / "evidence/objects/ev-railway-index-v1.series.json"
CARD_SOURCE_W = 672.0   # proof_t33 FORMS["stack"].w x 1920


def card_keeps_its_source() -> tuple[dict, dict]:
    import tempfile
    import chart_card as CC
    obj = json.loads(CARD_SOURCE_OBJECT.read_text(encoding="utf-8"))
    assert obj["src"].startswith("Campbell & Turner") and obj.get("hline"), (obj["src"], obj.get("hline"))
    obj["title"] = "Railway shares, 1845"
    obj.pop("hline")
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "ev-railway-index-v1.series.json"
        path.write_text(json.dumps(obj), encoding="utf-8")
        tl, uris, _aspect = CC.card_timeline(path, "line", card_w=CARD_SOURCE_W)
    page = tl["scenes"][0]["world"]["page"]
    assert page["source"].startswith("Campbell & Turner") and page["source"].endswith(LPG.CARD_SOURCE_ELLIPSIS), page["source"]
    return dict(tl, title="Golden: a chart card keeps its source at any size (672 px, P71 T33's stack twin)"), uris


SURFACES.update({"card-keeps-its-source": card_keeps_its_source})
FRAME_T.update({"card-keeps-its-source": 8.6})   # chart_card.LAND_T: the card's own landing - the instant every card is drawn at



# ---- P72 T53 (h) / R26-414 (a): THE LEADER - the total points back at the bar it dwarfs ------------------------------------
#   leader-points-back   Steel and Paper H row 16's own three bars (P71 T34's derived page: the dossier's "rebuild as three
#                        bars", EVIDENCE-DOSSIER.md C1), every value READ off the committed `ev-debt-issuance-line-v1`: the
#                        2020-24 year's $28B, 2025's $121B and the top of 2026E's range, $150B. The total is written at its
#                        bar ("$150B", "the total" - the figure takes the bar's own number's place, R26-284), then a LEADER
#                        arcs from that figure back to the 2020-24 bar's printed "$28B" and rings it, and the multiple the
#                        page computes (150 / 28 -> "5.4x", `multiple: true`) pops on the arc: the Bravos STK 0:08 pointer
#                        back (R35). Flat profile, 16:9. Judged when the leader has landed.
LEADER_DEBT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-debt-issuance-line-v1.series.json"
LEADER_OID = "lab-issuance-three-bars"
LEADER_FIG_AT, LEADER_AT, LEADER_DUR = 8.5, 11.0, 1.6


def leader_three_bars() -> dict:
    """The derived page's object (proof_t34.ratio_object's, rebuilt here from the committed file so the golden reads it)."""
    debt = json.loads(LEADER_DEBT.read_text(encoding="utf-8"))
    by = {s["label"]: s["pts"] for s in debt["series"]}
    return {"title": debt["title"],
            "sub": "Hyperscaler bond issuance, US$ billions a year - 2020-24 an average; 2026E the top of the $130-150B range",
            "src": debt["src"], "unit": "$", "unit_suffix": "B",
            "bars": [{"label": "2020-24, a year", "value": by["issuance"][0][1], "color": "deemph"},
                     {"label": "2025", "value": by["issuance"][-1][1], "color": "deemph"},
                     {"label": "2026E, top of range", "value": by["$150B"][-1][1], "color": "crimson"}]}


LEADER_SPECIES = [
    {"kind": "figure", "at": LEADER_FIG_AT, "dur": 1.4, "target": {"kind": "datum", "index": 2}, "text": "$150B",
     "sub": "the total"},                                                                                  # "a hundred and fifty"
    {"kind": "leader", "at": LEADER_AT, "dur": LEADER_DUR, "from": {"kind": "figure", "text": "$150B"},
     "to": {"kind": "datum", "index": 0, "part": "value"}, "ring": True, "multiple": True},               # "It is big enough"
]


def leader_points_back(extra: list | None = None, aspect: str = "16:9", species: list | None = None,
                       obj: dict | None = None, opts: str = "") -> tuple[dict, dict]:
    """The golden's timeline; `extra` / `species` / `aspect` / `obj` / `opts` (plate options) are test_leader's reads
    only - the committed golden is the plain call. The compiler's own page checks run (check_leader writes the multiple)."""
    import tempfile
    import build_scene_timeline_f as BST
    species = [dict(e) for e in (species if species is not None else LEADER_SPECIES)] + [dict(e) for e in (extra or [])]
    plate = f"ledger:{LEADER_OID}:bars{opts}"
    assert not BST.validate_species(species, (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / f"evidence/objects/{LEADER_OID}.series.json").write_text(json.dumps(obj or leader_three_bars()), encoding="utf-8")
        saved = BST.ASPECT
        BST.ASPECT = aspect
        try:
            world = BST.world_for_plate(plate, (0, 0, 0), ep)
            BST.stamp_full_stage(world["page"])
            BST.derive_rescale_states(world, species, plate, ep)
        finally:
            BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: the total points back at the bar it dwarfs (leader)", scenes, {}, aspect)
    return tl, (dict(_base_uris(), **BST.longform_assets(tl)) if "longform" in opts else _base_uris())


SURFACES.update({"leader-points-back": leader_points_back})
FRAME_T.update({"leader-points-back": round(LEADER_AT + LEADER_DUR + 0.6, 2)})   # landed: the arc, its head, the ring, the 5.4x


# ---- P72 T53 (b) + (e) (R26-412 (b), (e); P71 T34's ratio beat): THE GROUP BRACKET AND THE LEVEL TO A FAR BAR -------
#   bracket-level-across  Steel and Paper H row 16's issuance as the dossier's own three bars (C1: 2020-24 a year, 2025,
#                         2026E the top of the range), every value READ off the committed `ev-debt-issuance-line-v1`
#                         (REVALUE_SERIES). On "It is big enough" the bracket from the 2020-24 bar to 2026E writes the
#                         multiple, COMPUTED (150 / 28 -> 5.4x). The span stands beside the 2026E bar; the 28 bar is two
#                         bars away, so its level runs DASHED from the span's foot across to the 28 bar's side, broken
#                         behind the 2025 and 2026E bars it passes (Bravos STK 2:16). Judged whole: 8.0 + 1.8 + 0.4.
#   bracket-group         The same page; on "Last year ... This year" ONE span over the 2025 and 2026E bars under one
#                         label - the sentence's own words - its ticks dropping toward the group, clear over the two
#                         printed values (A16, CHN 18:18 "Decades"). Judged whole at the same instant.
GROUP_AT, GROUP_S = 8.0, 1.8


def issuance_three_bars() -> dict:
    """The dossier's three bars (EVIDENCE-DOSSIER C1), every value READ off the committed issuance series."""
    debt = json.loads(REVALUE_SERIES.read_text(encoding="utf-8"))
    by = {s["label"]: s["pts"] for s in debt["series"]}
    return {"title": debt["title"],
            "sub": "Hyperscaler bond issuance, US$ billions a year - 2020-24 an average; 2026E the top of the $130-150B range",
            "src": debt["src"], "unit": "$", "unit_suffix": "B",
            "bars": [{"label": "2020-24, a year", "value": by["issuance"][0][1], "color": "deemph"},
                     {"label": "2025", "value": by["issuance"][-1][1], "color": "deemph"},
                     {"label": "2026E, top of range", "value": by["$150B"][-1][1], "color": "crimson"}]}


def _issuance_bars_timeline(title: str, species: list[dict]) -> tuple[dict, dict]:
    import tempfile
    import build_scene_timeline_f as BST
    plate = "ledger:fx-issuance-three-bars:bars"
    assert not BST.validate_species([dict(e) for e in species], (0, 0, 0), plate)
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/fx-issuance-three-bars.series.json").write_text(json.dumps(issuance_three_bars()), encoding="utf-8")
        saved = BST.ASPECT
        BST.ASPECT = "16:9"
        try:
            world = BST.world_for_plate(plate, (0, 0, 0), ep)
            BST.stamp_full_stage(world["page"])
            BST.check_brace(world["page"], [dict(e) for e in species], "16:9")   # the group's page check
        finally:
            BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": [dict(e) for e in species]}]
    return _timeline(title, scenes, {}, "16:9"), _base_uris()


def bracket_level_across() -> tuple[dict, dict]:
    bars = issuance_three_bars()["bars"]
    mult = "%.1fx" % (bars[2]["value"] / bars[0]["value"])   # computed off the two bars, never typed
    return _issuance_bars_timeline("Golden: the bracket's far level runs across to its bar (STK 2:16)",
                                   [{"kind": "bracket", "at": GROUP_AT, "dur": GROUP_S, "from": 0, "to": 2, "label": mult,
                                     "sub": "2026E on the 2020-24 year"}])


def bracket_group() -> tuple[dict, dict]:
    return _issuance_bars_timeline("Golden: one span over a group of bars under one label (A16)",
                                   [{"kind": "bracket", "form": "group", "at": GROUP_AT, "dur": GROUP_S, "from": 1, "to": 2,
                                     "label": "last year and this"}])


SURFACES.update({"bracket-level-across": bracket_level_across, "bracket-group": bracket_group})
FRAME_T.update({"bracket-level-across": round(GROUP_AT + GROUP_S + 0.4, 2),   # 10.2: drawn whole, the level across
                "bracket-group": round(GROUP_AT + GROUP_S + 0.4, 2)})         # 10.2: drawn whole, the label written


# ---- P72 T53 (c) (R26-412 (c); P71 T34's epoch walk): A SPAN'S NAME CLEARS THE PAGE'S PEAK RULE -----------------------
#   span-clears-the-rule  Steel and Paper H row 9's GDP page - the COMMITTED `ev-equip-ipp-gdp-v2` (equipment and IP
#                         investment, % of GDP, its own "Q2 2000 peak - 11.54%" rule), full stage, live - and T34's two
#                         eras, their edges READ off the data (1998-2003, 2020-today): "DOT-COM" and "AI". The chart fills
#                         its box, so each name is written inside its band's top - where the peak rule stands: before T53
#                         both names sat ON its dashes (the base frame, 10.86 s). "DOT-COM" now stands just above the rule
#                         (clear of its label); "AI", whose "above" is the rule's label, just below it. Judged with both
#                         written: 9.0.
SPAN_RULE_PLATE = "ledger:ev-equip-ipp-gdp-v2:line:225:right:axes:cut;idle=live"
SPAN_RULE_OBJECT = LIT_PROJECT / "evidence/objects/ev-equip-ipp-gdp-v2.series.json"


def span_clears_the_rule() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    obj = json.loads(SPAN_RULE_OBJECT.read_text(encoding="utf-8"))
    assert obj.get("hline", {}).get("label", "").startswith("Q2 2000 peak"), obj.get("hline")
    pts = obj["series"][0]["pts"]
    near = lambda x: min(range(len(pts)), key=lambda k: abs(pts[k][0] - x))   # noqa: E731
    species = [{"kind": "span", "at": 4.0, "dur": 2.0, "from": near(1998.0), "to": near(2003.0), "label": "DOT-COM"},
               {"kind": "span", "at": 6.5, "dur": 2.0, "from": near(2020.0), "to": len(pts) - 1, "label": "AI"}]
    assert not BST.validate_species([dict(e) for e in species], (0, 0, 0), SPAN_RULE_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(SPAN_RULE_PLATE, (0, 0, 0), LIT_PROJECT)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    return _timeline("Golden: a span's name clears the page's peak rule (T34's epoch walk)", scenes, {}, "16:9"), _base_uris()


SURFACES.update({"span-clears-the-rule": span_clears_the_rule})
FRAME_T.update({"span-clears-the-rule": 9.0})   # both eras shaded and named (6.5 + 0.45 + 1.0 written)


# ---- P72 T53 (d) (R26-412 (d); P71 T34's isolate beat, draft 1): THE SOLO'S BADGE BOX WAITS FOR ITS TAG --------------
#   solo-badge-waits  Steel and Paper H row 14's capital-formation page - the COMMITTED `ev-capital-formation-v1`, the
#                     long form (T46d's end-badge box) - built to the dot-com high the page's own mark names (2001, the
#                     cap READ off the data; T34's `build_to` at 0), then T34's draft-1 order: the tech line's solo on "Today" (4.0) and the
#                     lines carried on to today after it (build_to the last print, 6.0 over 2.0 s). While the tech tag
#                     waits for its line the accent box is NOT drawn (before T53 it stood filled and EMPTY at the plot's
#                     right - logs/base-badge-timeline.log); it fills round the tag as the tag arrives with the carry.
#                     Judged after the solo, the tag not yet on the page: SOLO_WAIT_T's first instant (5.0); the second
#                     (8.6) is the tag landed, read by test_span_name_and_solo_badge.
SOLO_WAIT_OBJECT = LIT_PROJECT / "evidence/objects/ev-capital-formation-v1.series.json"
SOLO_WAIT_T = (5.0, 8.6)
SOLO_WAIT_SERIES = next(i for i, s in enumerate(json.loads(SOLO_WAIT_OBJECT.read_text(encoding="utf-8"))["series"])
                        if (s.get("name") or s.get("label") or "").startswith("COMPUTERS"))   # the tech line, by its own name


def solo_badge_waits() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    obj = json.loads(SOLO_WAIT_OBJECT.read_text(encoding="utf-8"))
    tech = SOLO_WAIT_SERIES
    pts = obj["series"][tech]["pts"]
    high = min(range(len(pts)), key=lambda k: abs(pts[k][0] - obj["marks"][0]["x"]))   # the dot-com high, the page's own mark
    plate = f"ledger:ev-capital-formation-v1:line:{high}:right:axes:cut;idle=live;readability=longform"
    species = [{"kind": "build_to", "at": 0.0, "dur": 0.4, "series": si, "target": {"kind": "datum", "index": high}}
               for si in range(len(obj["series"]))] + [{"kind": "solo", "at": 4.0, "dur": 0.7, "series": tech}] + [
        {"kind": "build_to", "at": 6.0, "dur": 2.0, "series": si, "target": {"kind": "datum", "index": len(s["pts"]) - 1}}
        for si, s in enumerate(obj["series"])]
    assert not BST.validate_species([dict(e) for e in species], (0, 0, 0), plate), BST.validate_species(species, (0, 0, 0), plate)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(plate, (0, 0, 0), LIT_PROJECT)
        BST.stamp_full_stage(world["page"])
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: the solo's end-badge box waits for its tag (long form)", scenes, {}, "16:9")
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


SURFACES.update({"solo-badge-waits": solo_badge_waits})
FRAME_T.update({"solo-badge-waits": SOLO_WAIT_T[0]})


# ---- P72 T53 (a) (R26-412 (a); Bravos BUB 0:00-0:48, harvest T1 / A33 / R1): THE ICEBERG STAGE ----------------------------
#   iceberg-tip       Steel and Paper H row 16's two stocks as the COMMITTED `ev-leases-iceberg-v1` (derive_iceberg.py: $261B of
#                     bonds, the issuance series' 2020-25 points summed, over $822B of lease commitments, the leases record's
#                     "Latest filings" row), the long form, full stage: ONE stacked bar, the leases at the base under the
#                     water rule "the balance sheet" (`water: true`). The camera stands RAISED by ICE_BY until ICE_AT: the
#                     frame opens on the page's own sky (before T53: the stage's navy void and the world's cream mount), the
#                     tip - the bonds, $261B - over the waterline, the base under the water. Judged raised: 4.5.
#   iceberg-base-lit  The same page after the pedestal (ICE_AT over ICE_S, one move down to the identity): the base in true
#                     proportion under the water, "$822B" written on it, and on ICE_GLOW_AT the light on the HIDDEN part only
#                     (`glow {bar: 0, segment: 0}`) - before T53 the glow edged the whole bar. Judged lit and held: 12.0.
ICE_OBJECT_ID = "ev-leases-iceberg-v1"
ICE_PLATE = f"ledger:{ICE_OBJECT_ID}:bars::right:axes:cut;idle=live;readability=longform"
ICE_AT, ICE_S, ICE_BY, ICE_GLOW_AT = 6.0, 2.4, 0.45, 10.0


def iceberg_stage() -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    species = [{"kind": "glow", "at": ICE_GLOW_AT, "dur": 0.68, "bar": 0, "segment": 0}]
    camera = {"keys": [], "pedestal": {"at": ICE_AT, "dur": ICE_S, "by": ICE_BY}}
    assert not BST.validate_species([dict(e) for e in species], (0, 0, 0), ICE_PLATE)
    assert not BST.validate_camera_row(camera, [dict(e) for e in species], "iceberg"), BST.validate_camera_row(camera, species, "iceberg")
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        world = BST.world_for_plate(ICE_PLATE, (0, 0, 0), LIT_PROJECT)
        BST.stamp_full_stage(world["page"])
        assert BST.check_glow(world, [dict(e) for e in species]) == []   # the part it lights is the bar's own
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "camera": camera,
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: the iceberg stage - the tip over the water, the base below, the hidden part lit", scenes, {}, "16:9")
    tl["kinetics"] = {"camera": True}   # the persistent camera, ON for every compiled timeline (the pedestal rides it)
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


SURFACES.update({"iceberg-tip": iceberg_stage, "iceberg-base-lit": iceberg_stage})
FRAME_T.update({"iceberg-tip": 4.5, "iceberg-base-lit": 12.0})


# ---- P72 T53 (i) / R26-415 (Bravos A56, BOOM 18:00.5): THE DATED RULE ------------------------------------------------------
#   dated-rule  `project-issuance-2026e`'s own page (H row 16's issuance and its dashed 2026E, composed off the committed
#               `ev-debt-issuance-line-v1`) with the committed object's own [2026, "2026E"] tick put back, so the axis
#               carries the projected year labelled as the estimate it is. The extend draws the dashed estimate; as it
#               lands the 2026E tick springs into the accent pill and a DASHED rule drops the plot's full height at 2026 -
#               hung from the date, not from a datum (the estimate's is refused as data, E77) - and the estimate's own
#               "2026E" end tag yields to the pill: the date is printed once. Judged with the rule landed.
DATED_RULE_TICK = 2026


def dated_rule_series() -> dict:
    """projection_series() with the committed object's own estimate tick ([2026, '2026E'] - read, never typed)."""
    obj = projection_series()
    committed = json.loads(PROJ_OBJECT.read_text(encoding="utf-8"))
    est = [t for t in committed["xticks"] if t[0] == DATED_RULE_TICK]
    assert est and str(est[0][1]).endswith("E"), committed["xticks"]   # the committed tick names itself an estimate
    obj["xticks"] = obj["xticks"] + est
    return obj


DATED_RULE_AT = round(PROJ_AT + PROJ_DUR, 2)   # the pill pops when the extended page stands
DATED_RULE_SPECIES = [{"kind": "chart_to", "at": PROJ_AT, "dur": PROJ_DUR, "to": "extend", "series": 1},
                      {"kind": "axis_tag", "at": DATED_RULE_AT, "dur": round(RUNTIME - DATED_RULE_AT - 1.0, 2),
                       "x": DATED_RULE_TICK, "guide": "rule"}]


def dated_rule(species: list | None = None) -> tuple[dict, dict]:
    import tempfile
    import build_scene_timeline_f as BST
    series = dated_rule_series()
    assert LPG.validate(series, "line") == [], LPG.validate(series, "line")
    species = [dict(e) for e in (species if species is not None else DATED_RULE_SPECIES)]
    assert not BST.validate_species(species, (0, 0, 0), PROJ_PLATE), BST.validate_species(species, (0, 0, 0), PROJ_PLATE)
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{PROJ_ID}.series.json").write_text(json.dumps(series), encoding="utf-8")
            world = BST.world_for_plate(PROJ_PLATE, (0, 0, 0), Path(td))
            BST.stamp_full_stage(world["page"])
            BST.derive_rescale_states(world, species, PROJ_PLATE, Path(td))
            BST.check_axis_tags(world, species)   # the tag's truth: 2026 is a tick the page carries (s109)
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, RUNTIME], "docks": [], "species": species}]
    tl = _timeline("Golden: the dated rule at the projected year (A56)", scenes, {}, "16:9")
    return tl, dict(_base_uris(), **BST.longform_assets(tl))


SURFACES.update({"dated-rule": dated_rule})
FRAME_T.update({"dated-rule": round(DATED_RULE_AT + 1.0, 2)})   # the pill popped, the rule landed (GUIDE_AT + RULE_S = 0.6 s)


def write_surface(name: str) -> list[Path]:
    """Write ONE surface's two source files - a new golden never rewrites another lane's sources."""
    if name in PAGE_SURFACES:
        return write_page_source(name)
    SOURCES.mkdir(parents=True, exist_ok=True)
    tl, uris = SURFACES[name]()
    out = []
    for suffix, payload in (("timeline", tl), ("uris", uris)):
        p = SOURCES / f"{name}.{suffix}.json"
        p.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")   # R26-323: LF on every platform
        out.append(p)
    return out


def write_sources(names: list[str] | None = None) -> list[Path]:
    """Every surface's sources, or only the named ones (`python build_golden_sources.py verdict-stack test-card`)."""
    out = []
    for name in (names or [*SURFACES, *PAGE_SURFACES]):
        out += write_surface(name)
    return out


if __name__ == "__main__":
    unknown = [n for n in sys.argv[1:] if n not in SURFACES and n not in PAGE_SURFACES]
    if unknown:
        raise SystemExit(f"unknown surface(s): {unknown}; known: {sorted([*SURFACES, *PAGE_SURFACES])}")
    for p in write_sources(sys.argv[1:] or None):
        print(f"{p.stat().st_size:>9,}  {p.relative_to(REPO)}")

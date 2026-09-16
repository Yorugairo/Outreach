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
    "melt-splash": 16.08,           # E88 / R26-76: splash:chart at u 0.675 - the BURST: the ball hit the board, flattening
                                   # and fading into its droplets, which are out along their rays toward where they
                                   # land; no stain has opened yet, so no blur is on screen and the pin is byte-exact
    "melt-ball-roll": 16.28,        # R26-118 / E88 s6: MID-ROLL. The window is MELT_CUT + MELT.S + MELT.W_S (2.75 s),
                                   # so the weight phase opens at 15.88 and its beats are LAND to 16.11, ROLL to 16.455,
                                   # NUDGE to 16.846, SETTLE to 16.98. 16.28 is half way through the roll: the ball has
                                   # turned ~100 degrees with its own ink MARK, its shadow rides a frame behind it, and
                                   # its surface is out of round. Its landing and its rest ride PROOF_FRAMES
    "melt-plate": 16.44,            # E88 / R26-76: splash:plate at u 0.90 - the PAINT: the stains have opened from the
                                   # landed drops and the plate shows through them over the charcoal, springing to rest
    "count-array": 8.0,             # P52 T7: all six icons landed (5.0 + 5 * 0.34 + LAND_S = 7.15) and the count written as the claim (+ CLAIM_LAG + CLAIM_S = 7.73) - the field as it is read
    "agenda-two": 7.2,              # P52 T8: both rows revealed (5.0 and 6.2 + NUM_LEAD + ROW_S = 6.74) and both rules fully drawn - the agenda as it stands
    "agenda-page": 12.0,            # P61 T8: the agenda PAGE at rest - all three rows written, all three catalogued icons stamped and settled (the last at 8.2 + 0.54 + 0.12 + 0.26 + 0.14 = 9.26), the board full and breathing. Its three moving instants ride PROOF_FRAMES (@proof-first-row / @proof-stamp / @proof-full)
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
               "species": [{"kind": "callout", "at": 10.0, "dur": 6.0, "target": {"kind": "point", "x": 0.72, "y": 0.42}}]}]
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


def melt_page(ending: str = "throw", weight: bool = False) -> tuple[dict, dict]:
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
    "species-proof": species_proof,      # P52 T7 + T8: the proof page for human gate 3
    "melt-page": melt_page,                                  # E88: the throw
    "melt-splash": lambda: melt_page("splash:chart"),        # E88: the splatter forms the next chart
    "melt-plate": lambda: melt_page("splash:plate"),         # E88: the splatter paints a narrative plate
    "melt-ball-roll": lambda: melt_page("throw", weight=True),  # R26-118 / E88 s6-s7: the ball with MASS - it lands, rolls, is nudged and settles before the throw
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


def plate_drift() -> tuple[dict, dict]:
    """R26-133: a plate authored `;idle=drift` - the case the player read for its `.scale` alone, so it held
    perfectly still. `drift` opens at [0, 0] and walks a bounded Lissajous of +-DRIFT_PX (2.0 stage px) x, +-0.6 of
    it in y, on two rates whose common period is 100 s, so four seconds carries four different poses and none of
    them repeats. Judged at 2.0 - a second clear of the rest it opens from (FRAME_T)."""
    import build_scene_timeline_f as BST
    aid = "plate-drift"
    scenes = [{"scene_id": "s01",
               "world": {"asset_id": aid, "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0},
                         "idle": "drift"},
               "exit": "cut", "span": [0.0, PLATE_DRIFT_RUNTIME], "docks": [], "species": []}]
    uris = _base_uris()
    uris[aid] = BST.data_uri(DOCK_PLATE)      # the same committed input camera-layers reads, flat
    tl = _timeline("Golden: a plate world at its drift idle", scenes, {}, None)
    tl["runtime_s"] = PLATE_DRIFT_RUNTIME
    tl["captions"], tl["caption_pages"] = [], []   # nothing on the stage but the plate
    tl["kinetics"] = {"idle": True}                # E49's switch: without it there is no idle to read
    return tl, uris


SURFACES.update({   # R26-133: the drift plate, held (this source) and painted (the `plate_idle_paints` dial)
    "plate-drift": plate_drift,
})
FRAME_T["plate-drift"] = 2.0


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
    p.write_text(json.dumps(page_source(name), indent=1, sort_keys=True) + "\n", encoding="utf-8")
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



def write_surface(name: str) -> list[Path]:
    """Write ONE surface's two source files - a new golden never rewrites another lane's sources."""
    if name in PAGE_SURFACES:
        return write_page_source(name)
    SOURCES.mkdir(parents=True, exist_ok=True)
    tl, uris = SURFACES[name]()
    out = []
    for suffix, payload in (("timeline", tl), ("uris", uris)):
        p = SOURCES / f"{name}.{suffix}.json"
        p.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
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

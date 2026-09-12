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
# the frame each surface is judged at - chosen so the thing under test is on screen and mid-motion
FRAME_T = {
    "ledger-page-mid-build": 6.0,   # field filled, outline drawn, ink and bars building
    "chart-callout": 12.0,          # the line has drawn, all four badges have landed
    "occluder-dock": 12.0,          # P50 T15 / HF-17: the card landed (4.0) and still, its lower half behind the plate's desk edge
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
    "melt-page": 15.88,             # P52 T9: MELT_CUT + 0.55 of MELT.S (1.6 s) - THE BALL, formed and still at rest on
                                   # the frame the flight starts: the morph is exactly the circle of BALL_R, and the
                                   # gooey blur is exactly 0. Mid-morph (0.45) is the livelier picture and is what the
                                   # PROOF frames show, but its mask carries a 9 px blurred edge, and one render in
                                   # eight came back with 15 pixels of that edge off by 2 (a Chromium filter-raster
                                   # flake, measured 2026-09-12) - a golden is a byte-exact pin and takes the instant
                                   # with no fractional band to flake
    "melt-splash": 16.2,            # P52 T9: the OTHER register, at 0.75 of the same window - the ball flattened on
                                   # the stepped clock and the ring of K-M ink droplets thrown outward over the paper
                                   # (the throw's own 0.75 is `melt-page@proof-075`). The blur is 0 through the whole
                                   # phase, so this instant is a byte-exact pin like the other.
    "count-array": 8.0,             # P52 T7: all six icons landed (5.0 + 5 * 0.34 + LAND_S = 7.15) and the count written as the claim (+ CLAIM_LAG + CLAIM_S = 7.73) - the field as it is read
    "agenda-two": 7.2,              # P52 T8: both rows revealed (5.0 and 6.2 + NUM_LEAD + ROW_S = 6.74) and both rules fully drawn - the agenda as it stands
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


def png_solid(w: int, h: int, rgb: tuple[int, int, int]) -> bytes:
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


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
    tv = BST.embed_entry("tv", {"quad": ART_TV, "darken": ART_DARKEN}, card_aspect=160 / 528)
    paper = BST.embed_entry("paper", {"quad": ART_PAPER}, card_aspect=400 / 640)
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
    evidence = {
        quote: {"title": "The claim on the screen", "source": source, "species": "press",
                "document": {"path": "golden", "sha256": "0" * 64}, "badges": []},
        still: {"title": "The record on the desk", "source": "P50 T7", "species": "deck",
                "document": {"path": "golden", "sha256": "0" * 64}, "badges": _badges()[:2]},
    }
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


def melt_page(splash: bool = False) -> tuple[dict, dict]:
    """P52 T9 / R26-15 - THE MELT: a finished ledger page hands the stage to a plate, and MELTS across the boundary.

    Scene 1 is the line page every other golden is built from, given the whole 15 s to draw itself, so what melts is a
    page that has been read. Scene 2 is a plain plate whose `exit` is `melt` - `exit` names the transition INTO the
    scene it sits on (the player's law, E47), so the melt takes scene 1's world as scene 2 begins: the page's card box
    sags into drips under the gooey threshold, balls up on 2s about its own centroid, and the ball is thrown off the
    lower right of the stage, leaving the plate alone. The default register is the THROW; the splash is asked for by
    name (`melt:splash`) and is rendered as its own proof frame.

    Judged at the BALL instant (FRAME_T 15.72 = the cut + 0.45 of the 1.6 s window), where the two halves that could
    fail are both on screen: the morph has to be a solid ink ball of BALL_R, and the blur that fused the drips has to
    be gone."""
    series = LPG.load_series(SERIES)
    page = LPG.build_spec(series, "line", None, "right")
    page["field"] = "scribble"
    page["exit"] = "cut"   # LEDGER_EXITS / E40 #5: NO RETRACT. A page whose world is about to melt must not spiral its
    # ink back into the cream first - the melt IS how this page leaves, and the vortex would have emptied it two seconds
    # before the boundary (measured: without this the melt sagged a blank cream sheet, and so does the shipped suck).
    scenes = [{"scene_id": "s01", "world": {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, MELT_CUT], "docks": [], "species": []},
              {"scene_id": "s02", "world": {"asset_id": "plate-melt", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "melt", "span": [MELT_CUT, RUNTIME], "docks": [], "species": []}]
    # the incoming world is PAPER, not the shared slate plate: the thing that melts is ink (the page's charcoal field,
    # and the K-M droplets of the splash are ink over cream by the model), and ink on slate is one dark on another -
    # the four proof frames a human reads have to show the silhouette, the ball and the droplets, not guess them.
    uris = _base_uris()
    uris["plate-melt"] = uri("image/png", png_solid(64, 36, (232, 220, 195)))
    if splash:
        scenes[1]["exit"] = "melt:splash"
    return _timeline("Golden: the page melts, balls up and is " + ("splashed" if splash else "thrown"), scenes, {}, None), uris


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


SURFACES = {
    "ledger-page-mid-build": ledger_page_mid_build,
    "chart-callout": chart_callout,
    "ledger-soak-page": ledger_soak_page,
    "dock-pair-16x9": lambda: _dock_pair(None),
    "dock-pair-9x16": lambda: _dock_pair("9:16"),
    "ledger-extend": ledger_extend,
    "ledger-keyed": ledger_keyed,
    "occluder-dock": occluder_dock,
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
    "ring-dashed-chip": ring_dashed_chip,   # P52 T8
    "species-proof": species_proof,      # P52 T7 + T8: the proof page for human gate 3
    "melt-page": melt_page,
    "melt-splash": lambda: melt_page(splash=True),
}


SURFACES.update({   # P52 T6: the newsreel band and the two readings of the bottom strip (gate 1's three frames)
    "newsreel-band": newsreel_band,
    "newsreel-strip-9x16": newsreel_strip_9x16,
    "newsreel-strip-above": newsreel_strip_above,
})


def write_sources() -> list[Path]:
    SOURCES.mkdir(parents=True, exist_ok=True)
    out = []
    for name, fn in SURFACES.items():
        tl, uris = fn()
        for suffix, payload in (("timeline", tl), ("uris", uris)):
            p = SOURCES / f"{name}.{suffix}.json"
            p.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            out.append(p)
    return out


if __name__ == "__main__":
    for p in write_sources():
        print(f"{p.stat().st_size:>9,}  {p.relative_to(REPO)}")

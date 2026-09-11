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
# the frame each surface is judged at - chosen so the thing under test is on screen and mid-motion
FRAME_T = {
    "ledger-page-mid-build": 6.0,   # field filled, outline drawn, ink and bars building
    "chart-callout": 12.0,          # the line has drawn, all four badges have landed
    "ledger-soak-page": 2.7,        # mid-soak: stains spreading and overlapping (P43 T3 K-M ink is judged here)
    "dock-pair-16x9": 12.0,         # both cards up, badges landed
    "dock-pair-9x16": 12.0,
    "ledger-extend": 13.05,
    "press-stack": 11.4,            # P50 T3: all three cards landed (5.0 / 7.4 / 9.8 + LAND_S), the pile settled, and the underline on the third fully drawn (10.6 + SQUIG_DRAW)
    "chip-board": 11.0,             # P50 T2: all three chips landed (5.0 / 6.2 / 7.4 + LAND_S) and the middle one's X fully drawn (10.0 + CROSS_S) - the board as it is read
    "flow-swap": 12.6,              # P50 T4: the swap is over (11.0 + SWAP_OUT_S + SWAP_IN_S = 11.75), the new node stands where the old one did, both arrows and the year stamp are in
    "vecmap-arc": 12.4,             # P50 T5: all four have landed - IRN lit (5.0), the arc drawn (6.6 + DRAW_S), "1996" stamped (8.4), CHN lit (9.6) with its figure (10.4) - and the X that cuts the flow is fully struck (11.5 + CROSS_S = 11.95)
    "span-decade": 12.6,            # P50 T4: the page has built (3.9 + 0.5 + 3.0), the span's shade is fully in (8.0 + IN_S) and its name fully written (8.45 + dur * WRITE = 12.45)
    "tiers-two": 14.2,              # P50 T9: both bands drawn (the page builds to 8.9, the second band's own word runs 9.5-11.5) and the drop bar in the accent all but finished (12.0 + 0.88 of 2.5) with its label being written
    "treemap-cross": 10.9,          # P50 T6: the census has landed (the build ends at 8.0), the three X's are struck (9.0 + CROSS_S) and the crossed share is written (9.0 + WRITE_AT + 3.0 * WRITE = 10.7)
    "tags-to-bars": 12.2,           # P50 T11: mid-hand-over of the KEYED-TAGS recast (12 s + 2 s): the two terminal tags are halfway to their bars and growing into the bars' own type, the lines have left half their history beneath them, the bars are half grown, and no value has been drawn twice
    "ledger-keyed": 12.75,          # P48 T4b: mid-phase-2 of the keyed recast (12 s + 2 s; the golden's expoOut clock is half done at u 0.37): the lines have left half their history, their ends and values are in flight to the bar tops, the bars are half grown         # P48 T3: mid-extend - the axis has retargeted (the first 0.45 of the 2 s clock), the nib is ~half through the new tail on the golden's expoOut pen (rescale at 8 s, extend at 12 s)
}


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
PRESS_CARDS = [
    ("ev-press-a", 5.0, "THE HERALD, 4 MAR 2026", {"x0": 0.08, "y0": 0.17, "x1": 0.62, "y1": 0.46},
     [(0.06, 0.14, 0.64, 0.44), (0.06, 0.58, 0.88, 0.72), (0.06, 0.80, 0.52, 0.90)]),
    ("ev-press-b", 7.4, "THE LEDGER, 6 MAR 2026", {"x0": 0.30, "y0": 0.15, "x1": 0.92, "y1": 0.45},
     [(0.28, 0.12, 0.94, 0.43), (0.06, 0.58, 0.70, 0.72), (0.06, 0.80, 0.84, 0.90)]),
    ("ev-press-c", 9.8, "THE DISPATCH, 9 MAR 2026", {"x0": 0.12, "y0": 0.16, "x1": 0.55, "y1": 0.47},
     [(0.10, 0.13, 0.57, 0.45), (0.06, 0.58, 0.92, 0.72), (0.06, 0.80, 0.38, 0.90)]),
]


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


def press_stack() -> tuple[dict, dict]:
    """P50 T3: THREE PRESS CARDS on a bare plate, stacking on three words (Bravos shots 5-10), the third carrying
    the underline on its quoted phrase (E56's one exception, the squiggle law §9.27).

    Each card is a dock of kind `press` with its source line and its phrase box as fractions of the card - exactly
    what the compiler writes from press_card.py's meta - and its place in the pile (`stack_index` / `stack_n`) in
    enter order. The player mounts each one outside the two dock slots and poses the whole pile from
    species/press.mjs. Judged after the third has settled and its underline has finished drawing (FRAME_T 11.4)."""
    evidence, uris, docks = {}, _base_uris(), []
    for i, (aid, enter, src, _phrase, bars) in enumerate(PRESS_CARDS):
        evidence[aid] = {"title": f"Press card {i + 1}", "source": src, "species": "press",
                         "document": {"path": "golden", "sha256": "0" * 64}, "badges": []}
        uris[aid] = uri("image/png", png_bars(528, 160, (250, 247, 240), bars))
        docks.append({"slide": aid, "slot": 0, "enter": enter, "exit": RUNTIME, "badge_at": [],
                      "kind": "press", "source": src, "phrase": PRESS_CARDS[i][3],
                      "stack_index": i, "stack_n": len(PRESS_CARDS)})
    species = [{"kind": "callout", "form": "underline", "at": 10.6, "dur": 2.0,
                "target": {"kind": "phrase", "dock": PRESS_CARDS[-1][0]}}]
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
               "exit": "cut", "span": [0.0, RUNTIME], "docks": docks, "species": species}]
    return _timeline("Golden: the press stack", scenes, evidence, None), uris


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


SURFACES = {
    "ledger-page-mid-build": ledger_page_mid_build,
    "chart-callout": chart_callout,
    "ledger-soak-page": ledger_soak_page,
    "dock-pair-16x9": lambda: _dock_pair(None),
    "dock-pair-9x16": lambda: _dock_pair("9:16"),
    "ledger-extend": ledger_extend,
    "ledger-keyed": ledger_keyed,
    "tags-to-bars": tags_to_bars,
    "chip-board": chip_board,
    "press-stack": press_stack,
    "flow-swap": flow_swap,
    "span-decade": span_decade,
    "vecmap-arc": vecmap_arc,
    "tiers-two": tiers_two,
    "treemap-cross": treemap_cross,
}


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

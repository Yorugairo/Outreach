"""Memory trades the calendar - the short (ONE-SHOT #3, the Fable parent's own pass; E99 s66, 2026-09-16), built from the
take on the authoring kit exactly as the Japan short is (`scripts/authoring/`, P51 T0).

One take, one part (`vo-short/audio/scene_1-tight.words.json` is the clock - the Chirp scratch take with doc 37 s14's dead
space killed by retime_take.py, word-timed locally by align_take_whisper.py). The shot table is AUTHORED in `shot_table()`
from the words: `ledger:<series>:<variant>:<emphasize>:<quiet_zone>[:mount=<s>|:spiral|:snap=<dock>][:cut]` places a LEDGER
PAGE from `evidence/objects/<series>.series.json`; a plain id is a plate (this story's own stills, generated 2026-09-16 on the
bound HollowStickMike - omni-video/stills/); `clip:<path>` a clip. Cuts land at 0.8 of the >= 0.30 s gap before the next
phrase (M13); mounts, snaps and docks land ON a word.

    python build_short.py            # -> build-oneshot-3/player.html + calendar-short.timeline.json + GATES-MOTION.md + SELF-WATCH.md

The BEAT PLAN (E96 / E99 s66: written by the intelligence doing the one-shot, before the rows) is `plan_beats()` and lands
in <build>/BEAT-PLAN.jsonl for M41.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))
SIBLING = HERE.parent / "tokyo-tea-break"        # the channel assets the other shorts document: the outro card
JAPAN = HERE.parent / "japan-tariff-trick"       # the host's two-fingers clip (E48: the callback is a thread - "In finance, we call this ...")
KOREA = HERE.parent / "korea-memory-toll"        # the approved Korea stills (the fallback world if a Flow still is refused)

from authoring import Project                                             # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W      # noqa: E402

SCRIPT = HERE / "SCRIPT-SHORT-VO.txt"
TAKE = HERE / "vo-short/audio"
BUILD = HERE / os.environ.get("CALENDAR_BUILD_DIR", "build-oneshot-3")
STILLS = HERE / "omni-video/stills"
TAKE_STEM = sys.argv[sys.argv.index("--take") + 1] if "--take" in sys.argv else "scene_1-tight"
EP = Project(here=HERE, build=BUILD, take=TAKE, take_stem=TAKE_STEM, script_name=SCRIPT.name, episode_id="memory-trades-the-calendar")
TITLE = "Memory stocks trade the calendar, not the news"

# the outro and the brand line are channel assets (the other shorts' builds document both); reused by path, not copied
OUTRO = SIBLING / "outro/outro-v2.mov"                     # 6.2 s, the dark card: "It's not magic. It's mechanics."
BRAND_LINE = HERE.parents[2] / "channel-assets/money-physics/outro/vo/audio/brand-line-paced.mp3"
BRAND_GAP, BRAND_TAIL = 0.7, 1.0
OUTRO_S, OUTRO_LEAD = 6.2, 0.1

# the beds (the channel's, sound/SOURCES.md) at the youtube level (Japan's numbers, the operator's 2026-09-08 +6 dB ruling)
BED_LU = {"youtube": -20.0, "facebook": -20.0}
BED_SWELL_DB = 4.0
PLATFORM = "youtube"
VO_LUFS = -21.5
BEDS = {"suno-hook-A.mp3": -13.2, "suno-hook-B.mp3": -13.0, "suno-pivot-A.mp3": -13.0, "suno-pivot-B.mp3": -13.0}
bed_gain = lambda f: A.bed_gain(VO_LUFS, BED_LU[PLATFORM], BEDS[f])

# the ledger page's own clock (mirrored from the player's LP block, as the other shorts mirror it)
PAGE_BUILD_END_S, PAGE_BUILD_START_S, PAGE_BUILD_S, LP_ROLL_S = 7.4, 4.4, 3.0, 0.7
SNAP_S = 0.45        # the player's SNAP_S: a landed card grows to the stage in this long
CARD_LEAD_S = 1.0    # a chart card is thrown onto the previous scene this long before its page snaps up from it
KEN = (0.06, 6, -4)  # the PLATES' lean; E99 s65: a held plate's life is DIRECTIONAL - a Ken Burns lean plus the drift (shorts 30-40 px)
DRIFT = 35
STILL = (0, 0, 0)    # a ledger page or a clip is the world already - no lean under it (s9.28 C3: a punch and a Ken Burns never share a window)

# THE WORLDS - this story's stills (omni-video/stills/<id>.png, 768x1376, Nano Banana Pro on HollowStickMike, 2026-09-16; the
# operator: "Flow is up if you need any stills or clips"). A still the parent refused (still-b v1 drew a human face) falls
# back to the approved Korea still of the same place.
PLATE_FILES = {
    "plate-customs": [STILLS / "still-a-customs-calendar.png"],                                            # the customs office: the calendar's 15th circled, the metronome, the ledger, the port in the window
    "plate-desk": [STILLS / "still-b-trading-desk-print-v2.png", KOREA / "omni-video/stills/approved/still-05-trading-desk-terminal.png"],   # the desk where the stocks trade the print
    "plate-dock": [STILLS / "still-c-soft-print-dock.png"],                                                # the dock at dawn: the July page, the soft print on the wet concrete
}
WORLD_CLIPS = {
    "clip-two-fingers.mp4": SIBLING / "omni-video/stills/clip-g-two-fingers-v2.mp4",   # StickMike to camera, two fingers up (10.0 s): "In finance, we call this ..."
}
SERIES = {   # dock id -> (series, variant): the chart CARDS - each rendered once at its landing as the portrait card its page becomes
    "dock-b-calendar": ("ev-trade-the-calendar-v1", "line"),
    "dock-m-metronome": ("ev-print-metronome-v1", "line"),
}
DOCK_FILES = {   # the host as a card - a crop (top, height) of this story's own stills (E45: springs to reading size, then parks)
    "dock-f-desk-host": ("plate-desk", (0.40, 0.55)),    # the host at the terminal, one finger up - counting the prints
    "dock-g-july-host": ("plate-dock", (0.56, 0.40)),    # the host on the quay with July's page in his hand
}
SRC_OP = "Operator backtest 2026-08-30 (EPISODE-SEEDS act three) - 25 prints, Aug '24 - Aug '26"
DOCK_META = [   # four badges a card = the rail the compiler stamps at 2.05 / 3.35 / 4.65 / 5.95 s after the landing (the badge ladder; an event every 1.3 s)
    {"asset": "dock-b-calendar", "title": "They trade the calendar", "source": "Yahoo Finance 000660.KS, MU; Korean customs HS 8542.32 via SCML", "species": "chart", "badges": []},   # B3 (Tokyo): a chart card carries no badge rail - its page\'s own pills are the layer (M27)
    {"asset": "dock-m-metronome", "title": "One soft print, and the stocks dropped", "source": "Yahoo Finance 000660.KS, MU; Korean customs HS 8542.32 via SCML", "species": "chart", "badges": []},   # B3 (Tokyo): a chart card carries no badge rail - its page\'s own pills are the layer (M27)
    {"asset": "dock-f-desk-host", "title": "Counting the strong prints", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},   # B3, generalised on the portrait stage: a badge rail\'s pills sit at 13 stage px (M25)
    {"asset": "dock-g-july-host", "title": "July's page", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},   # B3, generalised on the portrait stage: a badge rail\'s pills sit at 13 stage px (M25)
]
# THE VERDICT STACK on the short's form (E99 s21 / s61: VERDICT_9X16 - reading bands, the gather, the centre card last): the
# four charts of this short re-presented one per phrase over the host's line, and burst on the pivot "So you don't have to"
STACK_META = {"asset": "dock-stack", "species": "stack", "title": "Good news is priced before it lands", "source": "the two charts of this short that were docked, each shown with its own source above",
              "anchor": "In finance, we call this asymmetry", "anchor_kind": "claim", "badges": []}

# the data indices the rows point at (asserted in main so a moved object cannot move a light)
CAL_JAN_PRINT_IDX, CAL_STEEL_LAST_IDX, CAL_PAPER_LAST_IDX = 1, 7, 177     # ev-trade-the-calendar-v1: the steel's January print (149.7), its last point (366.6), the paper's last (348.1)
MET_JULY_IDX, MET_TWO_WEEKS_IDX, MET_AUG_IDX = 47, 57, 68   # (v2: the metronome is a CARD - these pin the object, no row points at them)                # ev-print-metronome-v1: the day the July print landed (150.4), two weeks on (121.6), the August print's day (141.1)
WEAK_EXCEPTION_IDX, WEAK_LATEST_IDX = 5, 7                              # ev-weak-prints-v1: Jun '25 (+10.9, the one that rose), Jul '26 (-14, the latest)
INTO_IDX = 0
CAL_15_POINT = (0.20, 0.52)
CAL_LEDGER_POINT = (0.20, 0.82)   # the stamped customs ledger on the desk
CAL_PORT_POINT = (0.80, 0.42)     # the cranes in the window
QUAY_SHEET_POINT = (0.42, 0.82)   # the print sheet on the wet concrete (still-c)
QUAY_PAGE_POINT = (0.14, 0.80)    # July's page in the host's hand
DESK_STRIP = {"kind": "region", "x0": 0.09, "y0": 0.43, "x1": 0.41, "y1": 0.58}   # the terminal SCREEN above the PRINT strip (still-b v2) - the figures flicker on the screen, never over the word
DESK_LINE_POINT = (0.26, 0.50)   # the rising line on the terminal screen   # the circled 15th on the customs-office still, as fractions of the frame (measured on the still: the ring at x 155 / 768, y 720 / 1376)


def chart_dock_card(aid: str) -> str:
    series, variant = SERIES[aid]
    return D.chart_card(aid, HERE / "evidence/objects" / f"{series}.series.json", BUILD, variant, "9:16")   # PORTRAIT: a wide card on the portrait stage put its pills under 11 px (v3); the verdict wall clips a portrait card to its header - a wall finding for the backlog


def card_aspect(aid: str) -> float:
    return D.card_aspect(aid, BUILD)


def plate_path(aid: str) -> Path:
    for p in PLATE_FILES[aid]:
        if p.exists():
            return p
    raise SystemExit(f"missing still {aid}: none of {[str(p) for p in PLATE_FILES[aid]]}")


def still_aspect(aid: str) -> float:
    plate, crop = DOCK_FILES[aid]
    return D.still_card_aspect(plate_path(plate), crop)


def register_assets() -> None:
    for aid in PLATE_FILES:
        D.register(aid, plate_path(aid))
    for aid, (plate, crop) in DOCK_FILES.items():
        D.register(aid, D.still_card(aid, plate_path(plate), crop, BUILD))
    for aid in SERIES:
        chart_dock_card(aid)                                        # renders the card and registers the id itself (it returns the id, not the path)
    D.register("dock-stack", BUILD / "docks" / "dock-b-calendar.png")   # the stack paints its ITEMS; its own document is the first card


def shot_table(ws: list[dict], runtime_s: float, t_outro: float) -> list[tuple]:
    """v3 - the second pass's frames and gates answered (see the patch's docstring). Every world plate holds six seconds and
    something moves on it every 2.5 s (M44 / M16); every card carries a badge rail; a host card reads only after the chart has
    parked to the top (E63 / E65); the quay's chart card leaves inside six seconds (M12); the cards are wide, as the verdict
    wall's boxes are."""
    at = lambda phrase: W.at(ws, phrase)
    cut = lambda phrase: W.cut_before(ws, phrase, rule="gap")
    datum = lambda i, s=0: {"kind": "datum", "index": i, "series": s}
    point = lambda xy: {"kind": "point", "x": xy[0], "y": xy[1]}
    mount_len = lambda t_row, phrase: round(at(phrase) + LP_ROLL_S - t_row, 2)

    t_card = round(max(0.05, at("the news") - 0.2), 2)               # the card is thrown as the hook's first sentence ends
    t_fifteenth = at("fifteenth")
    t_prints = at("prints the price")
    t_border = at("crossing its border")
    t_page1 = cut("If you own")
    t_retitle = at("Hynix and Micron")
    t_not_after = at("not after it")
    t_desk = cut("But here's")
    t_headline = at("headline")
    t_gain = at("gain")
    t_into = at("In the half-month into")   # no M13 gap before it in the take: the boundary is the word's ONSET (E47 / TR-2)
    t_into_land = round(t_into + 0.4, 2)
    t_six = at("six point eight")
    t_after = at("In the half-month after")
    t_move = at("The move is")
    t_strong = cut("A strong print")
    t_read_desk = at("Already paid for")   # the host's card reads a sentence earlier (M16: nothing else moves on the page until the light on the slice)
    t_three = at("three point four")
    t_peel = at("Eight of fourteen")
    t_coin = at("A coin flip")
    t_weak = cut("But now")
    t_read_july = at("Eight of them")
    t_seven = at("After seven")
    t_avg = at("minus six point nine")
    t_latest = cut("The latest")
    t_met_card = round(at("One soft print") - 0.55, 2)   # thrown a beat later so the light on July's page has its second (the landing is the event M16 counts)
    t_met_land = round(t_met_card + 0.55, 2)
    t_fourteen = at("fourteen percent")
    t_sixteen = at("Sixteen percent")
    t_finance = cut("In finance")
    t_met_exit = at("The chip price")   # the card leaves as the question is asked (4.5 s on screen - M12); the light then answers on July's page
    t_good = at("Good news")
    t_bad = at("Bad news")
    t_so = cut("So you")
    t_clear = round(max(at("only surprise"), t_bad + 0.95), 2)
    t_read = at("read the print")
    t_know = at("know the calendar")
    t_lands = at("the day the print lands")

    plate = lambda aid: f"{aid};idle=drift;drift={DRIFT}"
    rows = [
        # 1 THE HOOK AND THE PRINT (0:00-0:10) - the customs office; the wide calendar card thrown as the hook's first line ends and READ
        #   through the print (its badge rail stamps the print, the chip price, the stocks, the clock); the light on the circled 15th on "fifteenth"
        (0.0, t_page1, plate("plate-customs"), KEN, [
            ("dock-b-calendar", 0, t_card, t_page1, {"arrive": "throw", "mass": "paper", "centre": True, "card_aspect": card_aspect("dock-b-calendar")}),
        ], "dip", [
            {"kind": "spotlight", "at": t_fifteenth, "dur": "hold", "until": t_prints, "target": point(CAL_15_POINT)},
            {"kind": "spotlight", "at": t_prints, "dur": "hold", "until": t_border, "target": point(CAL_LEDGER_POINT)},   # "prints the price" - the stamped ledger
            {"kind": "spotlight", "at": t_border, "dur": "hold", "until": t_page1, "target": point(CAL_PORT_POINT)},     # "crossing its border" - the port in the window
        ]),
        # 2 THE PAGE ON THE HOOK (E44): snaps up from the card by 0:10; the January print lit as it lands and held to the cut (M11); retitled on
        #   "Hynix and Micron move around it"; the light moves to the stocks' last point on "not after it"
        (t_page1, t_desk, f"ledger:ev-trade-the-calendar-v1:line:{CAL_JAN_PRINT_IDX}:right:snap=dock-b-calendar:cut" + ";idle=live", STILL, [], "dip", [
            {"kind": "spotlight", "at": round(t_page1 + SNAP_S + 0.4, 2), "dur": "hold", "until": round(t_desk + 0.5, 2), "target": datum(CAL_JAN_PRINT_IDX)},   # held PAST the cut (the proven light)
            {"kind": "retitle", "at": t_retitle, "dur": 1.4, "text": "They move around the print"},
            {"kind": "spotlight", "at": t_not_after, "dur": "hold", "until": t_desk, "target": datum(CAL_PAPER_LAST_IDX, 1)},
        ]),
        # 3 THE DESK - "But here's the part the headline hides: when does the month's gain actually land? Twenty-five months of prints ..." -
        #   the light on the PRINT strip on "headline"; the terminal's figures tick over the strip from "gain" to the cut (STILL LIFE)
        (t_desk, t_into, plate("plate-desk"), KEN, [], "dip", [
            {"kind": "spotlight", "at": t_headline, "dur": "hold", "until": t_gain, "target": point((0.27, 0.645))},
            {"kind": "ticker", "at": t_gain, "dur": round(t_into - t_gain - 0.1, 2), "target": dict(DESK_STRIP), "density": 0.22, "paper": "#16222E", "tilt": 0},
        ]),
        # 4 THE INTO / AFTER BARS arrive BUILT on "In the half-month into the print"; the INTO bar lit as they appear; +6.8 % written at it on
        #   its number; the light moves to the AFTER bar on its sentence; the quoted +6.8 % MELTS into 3x on "The move is front-run" (E76)
        (t_into, t_strong, f"ledger:ev-into-vs-after-v1:bars:{INTO_IDX}:right:built:cut" + ";idle=live", STILL, [], "cut", [
            {"kind": "spotlight", "at": t_into_land, "dur": "hold", "until": t_after, "target": datum(INTO_IDX)},
            {"kind": "figure", "at": round(t_six + 0.4, 2), "dur": 1.2, "target": datum(INTO_IDX), "text": "+6.8%", "sub": "into the print", "color": "pos", "dy": -0.9},
            {"kind": "spotlight", "at": t_after, "dur": "hold", "until": t_move, "target": datum(1)},
            {"kind": "chart_to", "at": t_move, "dur": 0.9, "to": "compare", "form": "melt", "then": "splash", "hold": "gone",
             "metric": {"value": 6.8, "text": "+6.8%", "label": "into the print"},
             "comparator": {"value": 3.0909, "text": "3x", "label": "the gain before the news, against the gain after it"},
             "inputs": {"into": 6.8, "after": 2.2}, "derive": "into / after",
             "source": "[DERIVED: from the operator's backtest (EPISODE-SEEDS act three, 2026-08-30) - the mean half-month move into the print over the mean move after it, 6.8 / 2.2]"},
        ]),
        # 5 THE STRONG PRINTS - the share page MOUNTS on "A strong print? Already paid for."; the chart PARKS to the top and the host's card reads
        #   below it on "After the fourteen strong prints" (its badge rail counts the 14, the 8, the 6, the +3.4 %); the UP slice lit on "three
        #   point four", peeled on "Eight of fourteen up"; the page retitled on "A coin flip with drift"
        (t_strong, t_weak, f"ledger:ev-strong-prints-v1:share:0:right:built:cut" + ";idle=live", STILL, [
            ("dock-f-desk-host", 0, t_read_desk, t_weak, {"centre": True, "centre_x": 0.80, "centre_y": 0.34, "centre_w": 0.28, "card_aspect": still_aspect("dock-f-desk-host")}),   # reads BELOW the parked chart, clear of its sub and source (E63 / E65)
        ], "cut", [
            {"kind": "spotlight", "at": round(t_strong + 0.4, 2), "dur": "hold", "until": t_three, "target": datum(0)},   # the UP slice lit as the page appears (M11)
            {"kind": "spotlight", "at": t_three, "dur": "hold", "until": t_peel, "target": datum(0)},
            {"kind": "peel", "at": t_peel, "dur": 1.6},
            {"kind": "retitle", "at": t_coin, "dur": 1.2, "text": "A coin flip with drift"},
        ]),
        # 6 THE WEAK PRINTS arrive BUILT on "But now the weak prints"; the ONE print that rose lit as they appear; the chart PARKS to the top
        #   and the host with July's page reads below on "Eight of them" (its rail: the 8, the 7, -6.9 %, -13.8 %); retitled on "After seven of
        #   the eight"; the average written on "minus six point nine"
        (t_weak, t_latest, f"ledger:ev-weak-prints-v1:bars:{WEAK_LATEST_IDX}:right:built:cut" + ";idle=live", STILL, [], "dip", [
            {"kind": "spotlight", "at": round(t_weak + 0.4, 2), "dur": "hold", "until": t_seven, "target": datum(WEAK_EXCEPTION_IDX)},
            {"kind": "spotlight", "at": round(t_seven + 1.0, 2), "dur": "hold", "until": t_avg, "target": datum(WEAK_LATEST_IDX)},   # "the stocks fell" - the light moves to the latest bar
            {"kind": "retitle", "at": t_seven, "dur": 1.4, "text": "Seven of the eight fell"},
            {"kind": "figure", "at": t_avg, "dur": 1.4, "target": datum(WEAK_LATEST_IDX), "text": "avg \u22126.9%", "sub": "the half-month after a weak print", "color": "neg", "dy": -0.9},
        ]),
        # 7 THE QUAY AT DAWN - "The latest landed in July." - holds through the July beat; the wide daily-line card is thrown on "One soft
        #   print", READ (its rail: the July print -3.7 %, two weeks on -14 %, the August print +16.4 %) and gone inside six seconds (M12)
        (t_latest, t_finance, plate("plate-dock"), KEN, [
            ("dock-m-metronome", 0, t_met_card, t_met_exit, {"arrive": "throw", "mass": "paper", "centre": True, "centre_y": 0.38, "card_aspect": card_aspect("dock-m-metronome")}),
        ], "dip", [
            {"kind": "spotlight", "at": round(t_latest + 0.15, 2), "dur": "hold", "until": t_met_land, "target": point(QUAY_PAGE_POINT)},   # "The latest landed in July" - the page in his hand
            {"kind": "spotlight", "at": t_fourteen, "dur": "hold", "until": t_sixteen, "target": point(QUAY_SHEET_POINT)},   # "fourteen percent" - the print on the concrete
            {"kind": "spotlight", "at": t_sixteen, "dur": "hold", "until": t_finance, "target": point(QUAY_PAGE_POINT)},     # "Sixteen percent higher" - July's page
        ]),
        # 8 THE REFLECTION - two fingers: "In finance, we call this asymmetry" - THE VERDICT STACK re-presents the two docked cards, the calendar
        #   on "Good news", the soft print on "Bad news" (centre, last: the gather), and BURSTS on "the only surprise left"
        (t_finance, t_so, "clip:" + D.seekable_clip("clip-two-fingers.mp4", WORLD_CLIPS["clip-two-fingers.mp4"], BUILD).as_posix(), STILL, [
            ("dock-stack", 0, round(t_good - 0.5, 2), t_so),
        ], "dip", [
            {"kind": "life", "at": t_finance, "dur": round(t_so - t_finance, 2)},
        ]),
        # 9 THE RING - the office returns: the light on the ledger on "read the print", the punch on the calendar on "know the calendar", the
        #   light on the circled 15th from "the day the print lands" to the end (E56: a picture's focus is the light)
        (t_so, t_outro, plate("plate-customs"), STILL, [
            ("dock-g-july-host", 0, t_lands, t_outro, {"centre": True, "centre_y": 0.30, "centre_w": 0.34, "card_aspect": still_aspect("dock-g-july-host")}),   # the host with July's page returns above the calendar - the print landing, as a card (E48)
        ], "dip", [
            {"kind": "spotlight", "at": t_read, "dur": "hold", "until": t_know, "target": point(CAL_LEDGER_POINT)},
            {"kind": "punch", "at": t_know, "dur": 1.1, "target": point(CAL_15_POINT)},
            {"kind": "spotlight", "at": round(t_lands + 0.6, 2), "dur": "hold", "until": t_outro, "idle": "live", "target": point(CAL_15_POINT)},
        ]),
        # 10 the outro card, dissolving in over the office
        (t_outro, runtime_s, "clip:" + D.seekable_clip("outro-v2.mp4", OUTRO, BUILD).as_posix(), STILL, [], "dip", [
            {"kind": "life", "at": t_outro, "dur": round(runtime_s - t_outro, 2)},
        ]),
    ]
    STACK_META["stack"] = {"items": [{"id": "dock-b-calendar", "at": t_good}, {"id": "dock-m-metronome", "at": t_bad}], "clear_at": t_clear}
    return rows


ROW_PLAN = [   # per row: (act, compared_to, capabilities, recipe | None, why_none | None)
    ("hook / the claim + NAMES the print", "the news (what everyone watches) against the calendar (what the stocks watch); the chip price against the stocks on the card", ["the customs-office still on the bound host (the 15th circled, the metronome)", "Ken Burns + the 35 px drift (E99 s65)", "the chart card thrown onto the world and READ while the print is explained", "the light hops with the sentence: the circled 15th, the ledger, the port"], None, "card-becomes-the-chart is proven on a 3-5 s plate (the dip 1.8-5.1 s after the idle starts); M44 now asks six seconds of a plate carrying a card, so the proven timing cannot fire - the beat carries the same four members on a six-second plate"),
    ("EXPLAINS the mechanism (the page is the world by 0:10)", "the chip price (+267 %) against the stocks (-34 % off peak) on the same print calendar", ["the ledger page as the world (E22), snapped up from the landed card", "spotlight on the January print, held to the cut (E25 / M11)", "retitle on the sentence that renames the page"], "recipe:spotlight-held-past-the-cut", None),
    ("the turn (rehook) + SPANS the 25 months", "the headline (the print's number) against where the month's gain actually lands", ["the trading-desk still on the bound host, held 8 s (M44)", "the light on the PRINT strip on 'headline'", "the terminal's figures tick over the strip from 'gain' to the cut (STILL LIFE, ticker)"], None, "a world plate carrying the turn, alive by its own still-life species; its evidence arrives on the next page, built, so the plate holds its six seconds (M44) without a card on it"),
    ("COMPARES (into vs after) + TURNS on 3x", "the half-month INTO the print against the half-month AFTER it (same stocks, same 25 prints)", ["bars page arriving BUILT with its own badge (FRONT-RUN 3x)", "spotlight on the INTO bar as it appears, then on the AFTER bar on its sentence", "figure written at the datum", "chart_to compare: +6.8 % melts and splashes into 3x (E76 / E99 s56)"], None, "emphasized-bar-lit is proven with the light landing 7.55 s after a page that BUILDS; this page arrives built and is lit at once (M11), so the proven timing does not fire - the beat carries the same three members on the built page's own clock"),
    ("DIVIDES a whole (8 of 14) + the reflection line", "the 8 strong prints the stocks rose after against the 6 they fell after (the same 14)", ["share page (the donut exception, E53 s1) by the mount signature", "the host's card reads beside the donut, in the page's own room (E65, never over the ink)", "the UP slice lit, then peeled on its word", "retitle on the sentence that renames the page"], "recipe:badge-ladder", None),
    ("COUNTS a set (7 of 8) + TURNS on -6.9", "the 8 weak prints against each other - the ONE that rose lit, the 7 that fell counted by the badge", ["bars page arriving built (one bar per weak print, the selection rule on the page)", "spotlight on the exception", "the light moves to the latest bar on 'the stocks fell'", "retitle on 'After seven of the eight'", "figure at the latest bar", "the page's own badges"], "recipe:badge-ladder", None),
    ("the instance's world + SPANS two weeks + TURNS on +16.4", "the stocks' -14 % in the two weeks after the July print against the chip price's +16.4 % a month later", ["the quay-at-dawn still on the bound host, held 9 s", "the daily-line card thrown, READ under six seconds (M12) and gone - its page carries the two badges (-14 % in two weeks; the August print +16.4 %)", "the light on July's page, then on the print sheet on the concrete"], None, "a world plate carrying a read card; plate-dock-wipe needs the wipe exit and this world leaves by the dip (E47), and a badge rail is illegible at 9:16 (B3) - no proven recipe fires honestly"),
    ("the reflection (the host to camera)", "good news (the calendar card) against bad news (the soft print's card, centre and last)", ["the host's two-fingers clip (E48 callback: 'In finance, we call this ...')", "THE VERDICT STACK on 9:16 (E99 s61): two docked proofs enter one per phrase, gather on the centre card, burst on the pivot"], None, "the verdict stack is a dock payload with no recipe card yet (P55 T7 built it, E99 s61 approved the vertical form) - this beat IS the capability under test"),
    ("THE RING (the office returns)", "you against the market (reading the print faster); the calendar's circled date against the print's landing", ["the customs-office still returns (E48: the callback is a thread)", "the light on the ledger on 'read the print'", "punch on the calendar on 'know the calendar'", "the host with July's page returns above the calendar on 'the day the print lands' (the landing, as a card)", "the light holds on the circled 15th to the end, breathing (E56: a picture's focus is the light)"], None, "punch-then-callout needs a spiral page and a ring on a chart; the ring returns to the WORLD and a picture takes the light, not a ring (E56)"),
    ("the outro card", "the brand line against the story just told", ["the outro clip's own life", "the dip"], "recipe:outro-clip-life", None),
]


def plan_beats(rows: list[tuple]) -> list[dict]:
    """E96 / E99 s66: the comparator, the capabilities and the recipe per BEAT - a beat is one of the take's sentences (the
    floor's own unit), and each sentence carries the plan of the row it is spoken over. Authored before the rows were timed."""
    import lint_species_choice as LSC
    sents = LSC.load_sentences(BUILD / "timeline.json")
    assert len(ROW_PLAN) == len(rows), (len(ROW_PLAN), len(rows))
    out = []
    for i, sent in enumerate(sents):
        k = max((j for j, r in enumerate(rows) if float(r[0]) <= sent["start"] + 1e-6), default=0)
        act, compared, caps, recipe, why = ROW_PLAN[k]
        out.append({"beat": i + 1, "t0": round(sent["start"], 2), "t1": round(sent["end"], 2), "sentence": sent["text"], "row": k + 1,
                    "act": act, "comparator": {"compared_to": compared}, "capabilities": caps, "recipe": recipe, "why_none": why,
                    "plate": rows[k][2].split(";")[0][:60]})
    return out


# the sound map (the other shorts', verbatim): a spiral entry is the warped whoosh at 0.12; mounts are silent; every page exits by cut
ACCENT = 0.12
SPIRAL_IN = {"A": "fs-whoosh-3-spiral-in.mp3", "B": "fs-whoosh-3-648729.mp3", "C": "fs-swirl-in-478722.mp3"}
SNAP_IN = {"A": "fs-whoosh-3-648729.mp3", "B": "fs-riserhit-754771.mp3", "C": "fs-whoosh-1-706679.mp3"}
TURN_SERIES = "ev-weak-prints-v1"   # the turn: "But now the weak prints" - the pivot bed fades in under it


def sound_cues(rows: list[tuple]) -> list[dict]:
    cues: list[dict] = []
    for i, r in enumerate(rows):
        page = A.page_transitions(r[2])
        if page["ledger"] and page["spiral"]:
            cues.append({"slot": f"page enter {i + 1} (spiral)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0, "variants": dict(SPIRAL_IN)})
        if page["ledger"] and (page["snap"] or page["camera"]):
            cues.append({"slot": f"page enter {i + 1} (snap)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0, "variants": dict(SNAP_IN)})
    t_turn = next(r[0] for r in rows if TURN_SERIES in r[2])
    env = A.bed_envelope(rows, BED_SWELL_DB, SNAP_S, fallback_end=lambda d: float(d[3]) + SNAP_S)
    cues.append({"slot": "hook bed", "at": 0.0, "gain": bed_gain("suno-hook-B.mp3"), "fade_in": 1.5, "env": env,
                 "variants": {"A": "suno-hook-B.mp3", "B": "suno-hook-A.mp3"}, "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO ({VO_LUFS} LUFS)"})
    cues.append({"slot": "turn bed", "at": round(t_turn, 2), "gain": bed_gain("suno-pivot-A.mp3"), "fade_in": 3.0,
                 "variants": {"A": "suno-pivot-A.mp3", "B": "suno-pivot-B.mp3"}, "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO; fades in under the weak prints"})
    return cues


def main() -> int:
    ws = W.take_words(EP)
    EP.mkdirs()
    shutil.copy2(TAKE / f"{TAKE_STEM}.mp3", EP.audio_master)
    t_vo_end = round(A.probe_duration(EP.audio_master), 3)
    line_s = A.probe_duration(BRAND_LINE)
    t_outro, t_line, runtime_s = A.outro_clock(t_vo_end, line_s, outro_lead=OUTRO_LEAD, outro_s=OUTRO_S, brand_gap=BRAND_GAP, brand_tail=BRAND_TAIL)
    A.stitch_brand_line(EP.audio_master, BRAND_LINE, BRAND_GAP, runtime_s)
    W.write_timeline(EP, ws, runtime_s)
    print(f"  take {t_vo_end:.2f}s; brand line {line_s:.2f}s at {t_line:.2f}s; card at {t_outro:.2f}s; runtime {runtime_s:.2f}s")

    obj = HERE / "evidence/objects"
    cal = json.loads((obj / "ev-trade-the-calendar-v1.series.json").read_text(encoding="utf-8"))["series"]
    assert cal[0]["pts"][CAL_JAN_PRINT_IDX][1] == 149.7 and cal[0]["pts"][CAL_STEEL_LAST_IDX][1] == 366.6 and cal[1]["pts"][CAL_PAPER_LAST_IDX][1] == 348.1, "the calendar object moved under the shot table"
    met = json.loads((obj / "ev-print-metronome-v1.series.json").read_text(encoding="utf-8"))["series"][0]["pts"]
    assert met[MET_JULY_IDX] == [2026.5339, 150.4] and met[MET_TWO_WEEKS_IDX][1] == 121.6 and met[MET_AUG_IDX] == [2026.616, 141.1], "the metronome object moved under the shot table"
    weak = json.loads((obj / "ev-weak-prints-v1.series.json").read_text(encoding="utf-8"))["bars"]
    assert weak[WEAK_EXCEPTION_IDX]["value"] == 10.9 and weak[WEAK_LATEST_IDX]["label"] == "Jul '26", "the weak-prints object moved under the shot table"
    register_assets()
    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META + [STACK_META], indent=1), encoding="utf-8")

    T.caption_pages(BUILD, char_budget=28, max_words=6)

    rows = shot_table(ws, runtime_s, t_outro)
    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META + [STACK_META], indent=1), encoding="utf-8")   # the stack's items are timed by the rows
    T.hold_until(rows, ws)
    plan_path = HERE / "sound/SOUND-PLAN.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["cues"] = sound_cues(rows)
    plan_path.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    T.write_shot_table(HERE / "SHOT-TABLE-SHORT.py", rows,
                       '"""Memory trades the calendar short - AUTHORED shot table, timed from the take by build_short.py. Do not hand-edit; edit build_short.shot_table."""\n')
    T.print_rows(rows, show_docks=True)
    beats = plan_beats(rows)
    (BUILD / "BEAT-PLAN.jsonl").write_text("".join(json.dumps(b, ensure_ascii=False) + "\n" for b in beats), encoding="utf-8")
    print(f"  beat plan: {len(beats)} sentence beats over {len(rows)} rows, {sum(1 for b in beats if b['recipe'])} on a row with a proven recipe")

    rc = T.compile_timeline(
        HERE, BUILD,
        timeline_name="calendar-short.timeline.json",
        shot_table_file="SHOT-TABLE-SHORT.py",
        title=TITLE, subtitle="Money Physics - short", episode_id="memory-trades-the-calendar",
        aspect="9:16",
        caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False, "curvature_stroke": True},
        render=True)
    if os.environ.get("SELF_WATCH", "1") == "1":
        import self_watch as SW
        rc = rc or SW.main([str(BUILD), "--project", str(HERE), "--script", "SCRIPT-SHORT"])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

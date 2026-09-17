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
    "plate-reflect": [STILLS / "still-d-asymmetry.png", STILLS / "still-a-customs-calendar.png"],            # the reflection: the host with the small good-news sheet up and the big bad-news sheet down (E99 s67: no borrowed footage)
}
WORLD_CLIPS = {
    "clip-two-fingers.mp4": SIBLING / "omni-video/stills/clip-g-two-fingers-v2.mp4",   # StickMike to camera, two fingers up (10.0 s): "In finance, we call this ..."
}
SERIES = {}   # v9b (E99 s67): no chart CARD is thrown - a chart is a page, entered by its own signature
DOCK_FILES = {   # the evidence docks: crops (top, height) of this story's own stills (E45: springs to reading size, then parks)
    "dock-h-calendar-wall": ("plate-customs", (0.28, 0.40)),   # the wall calendar, the 15th circled
    "dock-f-desk-host": ("plate-desk", (0.40, 0.55)),          # the host at the terminal, one finger up - counting the prints
    "dock-g-july-host": ("plate-dock", (0.56, 0.40)),          # the host on the quay with July's page in his hand
}
SRC_OP = "Operator backtest 2026-08-30 (EPISODE-SEEDS act three) - 25 prints, Aug '24 - Aug '26"
DOCK_META = [   # no badge rails at 9:16 (B3, generalised)
    {"asset": "dock-h-calendar-wall", "title": "The print lands mid-month", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-f-desk-host", "title": "Counting the strong prints", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-g-july-host", "title": "July's page", "source": "HollowStickMike - Money Physics", "species": "deck", "badges": []},
]
# THE VERDICT STACK on the short's form (E99 s21 / s61: VERDICT_9X16 - reading bands, the gather, the centre card last): the
# four charts of this short re-presented one per phrase over the host's line, and burst on the pivot "So you don't have to"
STACK_META = {"asset": "dock-stack", "species": "stack", "title": "Good news is priced before it lands", "source": "the two charts of this short that were docked, each shown with its own source above",
              "anchor": "In finance, we call this asymmetry", "anchor_kind": "claim", "badges": []}

# the data indices the rows point at (asserted in main so a moved object cannot move a light)
CAL_JAN_PRINT_IDX, CAL_STEEL_LAST_IDX, CAL_PAPER_LAST_IDX = 1, 7, 177     # ev-trade-the-calendar-v1: the steel's January print (149.7), its last point (366.6), the paper's last (348.1)
MET_JULY_IDX, MET_TWO_WEEKS_IDX, MET_AUG_IDX, MET_LAST_IDX = 47, 57, 68, 77   # ev-print-metronome-v1: the day the July print landed (150.4), two weeks on (121.6), the August print's day (141.1), the last point                # ev-print-metronome-v1: the day the July print landed (150.4), two weeks on (121.6), the August print's day (141.1)
WEAK_EXCEPTION_IDX, WEAK_LATEST_IDX = 5, 7                              # ev-weak-prints-v1: Jun '25 (+10.9, the one that rose), Jul '26 (-14, the latest)
INTO_IDX = 0
CAL_15_POINT = (0.20, 0.52)
CAL_LEDGER_POINT = (0.20, 0.82)   # the stamped customs ledger on the desk
CAL_METRONOME_POINT = (0.17, 0.72)   # the metronome on the desk (still-a)
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


def shot_table(ws: list[dict], runtime_s: float, t_outro: float) -> list[tuple]:
    """v9b - E99 s67. THE OPEN IS THE CHART: the calendar page is the first frame, on its axes, its two lines drawing under the hook
    (P53 T1); the January print lit on "prints"; the page holds built through "crossing its border". The office takes the frame on "If
    you own the stocks" - the metronome lit on its word. The desk on "But here's": the PRINT strip lit on "headline", the terminal's
    figures ticking from "gain". The into/after bars ENTER ON THEIR AXES on "In the half-month into" and GROW while the sentence runs;
    the INTO bar lit after the build as "six point eight" is said, +6.8 % written, the light to the AFTER bar on its sentence, the
    quoted figure melted into 3x on "front-run" (E76); the wall calendar reads beside the bars as evidence. The strong-print share
    page enters on its axes on "A strong print?", its slices arriving; the host's card reads after the build; the UP slice lit on
    "three point four", peeled on "Eight of fourteen", the page retitled on "A coin flip". The weak prints enter on their axes on
    "But now" and GROW as "Eight of them in twenty-five months" is said; the one that rose lit on "seven of the eight"; retitled;
    the average written. The quay on "The latest landed in July"; the daily line enters on its axes on "One soft print" and DRAWS to
    the day the July print landed, the two weeks after it shaded on "two weeks", the line carried on to August on "The chip price",
    +16.4 % written on "Sixteen"; the host with July's page reads beside it. The two fingers on "In finance": the calendar reads on
    "Good news", July's page on "Bad news". The office returns on "So you don't"; the calendar page RETURNS BY THE SPIRAL on "You have
    to know the calendar", the punch on the last print on "the day the print lands", the ring round the stocks' last point on "the
    stocks trade it" (E56: a ring's one use)."""
    at = lambda phrase: W.at(ws, phrase)
    cut = lambda phrase: W.cut_before(ws, phrase, rule="gap")
    datum = lambda i, s=0: {"kind": "datum", "index": i, "series": s}
    point = lambda xy: {"kind": "point", "x": xy[0], "y": xy[1]}
    card = lambda aid, y, w, x=None: {"centre": True, "centre_y": y, "centre_w": w, "card_aspect": still_aspect(aid), **({"centre_x": x} if x else {})}

    t_prints = at("prints the price")
    t_office = cut("If you own")
    t_metronome = at("metronome")
    t_retitle = at("Hynix and Micron")
    t_desk = cut("But here's")
    t_headline = at("headline")
    t_gain = at("gain")
    t_into = at("In the half-month into")   # no M13 gap before it in the take: the boundary is the word's ONSET (E47 / TR-2)
    t_turn = cut("when does")
    t_into_built = round(at("when does") + PAGE_BUILD_END_S + 0.15, 2)   # the mount's bars land 7.4 s after the page's clock starts (the roll ends on the word)
    t_six = at("six point eight")
    t_after = at("In the half-month after")
    t_move = at("The move is")
    t_strong = cut("A strong print")
    t_strong_built = round(t_strong + PAGE_BUILD_S + 0.3, 2)
    t_three = at("three point four")
    t_peel = at("Eight of fourteen")
    t_coin = at("A coin flip")
    t_weak = cut("But now")
    t_weak_built = round(t_weak + PAGE_BUILD_S + 0.3, 2)
    t_seven = at("After seven")
    t_avg = at("minus six point nine")
    t_latest = cut("The latest")
    t_soft = at("One soft print")
    t_two_weeks = at("two weeks")
    t_chip = at("The chip price")
    t_sixteen = at("Sixteen percent")
    t_finance = cut("In finance")
    t_good = at("Good news")
    t_bad = at("Bad news")
    t_so = cut("So you")
    t_know = at("know the calendar")
    t_lands = at("the day the print lands")
    t_stocks = at("the stocks trade it")

    plate = lambda aid: f"{aid};idle=drift;drift={DRIFT}"
    rows = [
        # 1 THE OPEN IS THE CHART (E99 s67 / P53 T1): the calendar page on its axes, its lines drawing under the hook; the January print lit on "prints"
        (0.0, t_office, f"ledger:ev-trade-the-calendar-v1:line:{CAL_JAN_PRINT_IDX}:right:axes:cut" + ";idle=live", STILL, [], "dip", [
            {"kind": "spotlight", "at": round(PAGE_BUILD_S + 0.3, 2), "dur": "hold", "until": t_office, "target": datum(CAL_JAN_PRINT_IDX)},   # the print lit as the lines finish drawing (M11), held through "prints the price"
        ]),
        # 2 THE OFFICE - "If you own the stocks, that print is your metronome. Hynix and Micron move around it, not after it." - the metronome lit on its word
        (t_office, t_desk, plate("plate-customs"), KEN, [], "dip", [
            {"kind": "spotlight", "at": t_metronome, "dur": "hold", "until": t_desk, "target": point(CAL_METRONOME_POINT)},
        ]),
        # 3 THE DESK - "But here's the part the headline hides: when does the month's gain actually land? Twenty-five months of prints ..."
        (t_desk, t_turn, plate("plate-desk"), KEN, [], "cut", [
            {"kind": "spotlight", "at": t_headline, "dur": "hold", "until": t_turn, "target": point((0.27, 0.645))},   # the sentence points at the headline
        ]),
        # 4 THE INTO / AFTER BARS enter on their axes and GROW under the sentence; the INTO bar lit after the build as its number is said;
        #   +6.8 % written; the light to the AFTER bar on its sentence; the quoted figure MELTS into 3x on "The move is front-run" (E76);
        #   the wall calendar reads beside the bars - the print, as evidence
        (t_turn, t_strong, f"ledger:ev-into-vs-after-v1:bars:{INTO_IDX}:right:mount={round(at('when does') + LP_ROLL_S - t_turn, 2)}:cut" + ";idle=live", STILL, [   # THE MOUNT (the signature): the cream rises over the desk on "when does", the bars DRAW under "Twenty-five months ..." and land as "In the half-month into" begins
            ("dock-h-calendar-wall", 0, round(t_into_built + 1.1, 2), t_strong, card("dock-h-calendar-wall", 0.68, 0.30)),   # reads as "+6.8 %" is written, beside the bars
        ], "suck:0.5,0.5", [   # the page collapses into a point (Tokyo's exit) and the share page opens on its axes
            {"kind": "spotlight", "at": t_into_built, "dur": "hold", "until": t_after, "target": datum(INTO_IDX)},
            {"kind": "figure", "at": max(round(t_six + 0.6, 2), round(t_into_built + 1.2, 2)), "dur": 1.2, "target": datum(INTO_IDX), "text": "+6.8%", "sub": "into the print", "color": "pos", "dy": -0.9},
            {"kind": "spotlight", "at": t_after, "dur": "hold", "until": t_move, "target": datum(1)},
            {"kind": "chart_to", "at": t_move, "dur": 0.9, "to": "compare", "form": "melt", "then": "splash", "hold": "gone",
             "metric": {"value": 6.8, "text": "+6.8%", "label": "into the print"},
             "comparator": {"value": 3.0909, "text": "3x", "label": "the gain before the news, against the gain after it"},
             "inputs": {"into": 6.8, "after": 2.2}, "derive": "into / after",
             "source": "[DERIVED: from the operator's backtest (EPISODE-SEEDS act three, 2026-08-30) - the mean half-month move into the print over the mean move after it, 6.8 / 2.2]"},
        ]),
        # 5 THE STRONG PRINTS - the share page enters on its axes, its slices arriving; the host's card reads beside it after the build;
        #   the UP slice lit on "three point four", peeled on "Eight of fourteen up"; the page retitled on "A coin flip with drift"
        (t_strong, t_weak, f"ledger:ev-strong-prints-v1:share:0:right:axes:cut" + ";idle=live", STILL, [
            ("dock-f-desk-host", 0, round(t_strong_built + 0.3, 2), t_weak, card("dock-f-desk-host", 0.34, 0.28, 0.80)),
        ], "cut", [
            {"kind": "spotlight", "at": max(t_three, t_strong_built), "dur": "hold", "until": t_peel, "target": datum(0)},
            {"kind": "peel", "at": t_peel, "dur": 1.6},
            {"kind": "retitle", "at": t_coin, "dur": 1.2, "text": "A coin flip with drift"},
        ]),
        # 6 THE WEAK PRINTS enter on their axes and GROW as "Eight of them in twenty-five months" is said; the one that rose lit on "seven of
        #   the eight"; the page retitled; the average written at the latest bar
        (t_weak, t_latest, f"ledger:ev-weak-prints-v1:bars:{WEAK_LATEST_IDX}:right:axes:cut" + ";idle=live", STILL, [], "dip", [
            {"kind": "spotlight", "at": max(t_seven, t_weak_built), "dur": "hold", "until": t_avg, "target": datum(WEAK_EXCEPTION_IDX)},
            {"kind": "retitle", "at": round(t_seven + 1.2, 2), "dur": 1.4, "text": "Seven of the eight fell"},
            {"kind": "figure", "at": t_avg, "dur": 1.4, "target": datum(WEAK_LATEST_IDX), "text": "avg \u22126.9%", "sub": "the half-month after a weak print", "color": "neg", "dy": -0.9},
        ]),
        # 7 THE QUAY AT DAWN - "The latest landed in July." (the plate's own idle; the page follows on the next sentence)
        (t_latest, t_soft, plate("plate-dock"), KEN, [], "cut", None),
        # 8 THE DAILY LINE enters on its axes on "One soft print" and DRAWS to the day the July print landed; the two weeks after it shaded on
        #   "two weeks"; the line carried on to August on "The chip price itself?"; +16.4 % written at the August print on "Sixteen"; the host
        #   with July's page reads beside the line after the first build
        (t_soft, t_finance, f"ledger:ev-print-metronome-v1:line:{MET_JULY_IDX}:right:axes:cut" + ";idle=live", STILL, [
            ("dock-g-july-host", 0, round(t_soft + 2.6, 2), t_finance, card("dock-g-july-host", 0.70, 0.30)),
        ], "dip", [
            {"kind": "build_to", "at": round(t_soft + 0.1, 2), "dur": 2.0, "target": datum(MET_JULY_IDX)},
            {"kind": "span", "at": max(t_two_weeks, round(t_soft + 2.3, 2)), "dur": 1.4, "from": MET_JULY_IDX, "to": MET_TWO_WEEKS_IDX, "label": "\u221214% in two weeks", "color": "neg"},
            {"kind": "build_to", "at": t_chip, "dur": 1.2, "target": datum(MET_LAST_IDX)},
            {"kind": "figure", "at": max(t_sixteen, round(t_chip + 1.4, 2)), "dur": 1.4, "target": datum(MET_AUG_IDX), "text": "+16.4%", "sub": "the August print", "color": "pos", "dy": -0.9},
        ]),
        # 9 THE REFLECTION - two fingers: "In finance, we call this asymmetry." - the calendar reads on "Good news", July's page on "Bad news"
        (t_finance, t_so, plate("plate-reflect"), KEN, [
            ("dock-h-calendar-wall", 0, round(t_finance + 0.5, 2), t_so, card("dock-h-calendar-wall", 0.24, 0.32, 0.28)),   # the calendar reads from "In finance" (the mechanism, as evidence)
            ("dock-g-july-host", 1, t_bad, t_so, card("dock-g-july-host", 0.24, 0.32, 0.72)),
        ], "dip", None),
        # 10 THE OFFICE RETURNS - "So you don't have to read the print faster than the market." (E48: the callback is a thread)
        (t_so, t_know, plate("plate-customs"), KEN, [], None, None),
        # 11 THE RING - the calendar page RETURNS BY THE SPIRAL on "You have to know the calendar"; the punch on the last print on "the day
        #    the print lands"; the ring round the stocks' last point on "the stocks trade it" (E56's one use)
        (t_know, t_outro, f"ledger:ev-trade-the-calendar-v1:line:{CAL_STEEL_LAST_IDX}:right:spiral:cut" + ";idle=live", STILL, [], "cut", [
            {"kind": "spotlight", "at": t_lands, "dur": "hold", "until": t_stocks, "target": datum(CAL_STEEL_LAST_IDX)},   # the last print lit on "the day the print lands" (a punch cut the title - M43)
            {"kind": "callout", "at": t_stocks, "dur": 1.3, "target": datum(CAL_PAPER_LAST_IDX, 1)},
        ]),
        # 12 the outro card, dissolving in over the ring page
        (t_outro, runtime_s, "clip:" + D.seekable_clip("outro-v2.mp4", OUTRO, BUILD).as_posix(), STILL, [], "dip", [
            {"kind": "life", "at": t_outro, "dur": round(runtime_s - t_outro, 2)},
        ]),
    ]
    return rows


ROW_PLAN = [   # per row: (act, compared_to, capabilities, recipe | None, why_none | None)
    ("hook / the claim - THE OPEN IS THE CHART", "the news (what everyone watches) against the calendar (what the stocks watch); the chip price against the stocks on the page", ["the ledger page as the first frame, on its axes, its two lines DRAWING under the hook (P53 T1, E99 s67)", "the January print lit on 'prints' and held (E25)"], None, "hook-opens-on-the-axes is a candidate recipe (axes + build_to + pull_back + ring + focus_zoom); this open takes its first two members - the answer draws under the question - and not the camera pair"),
    ("EXPLAINS the mechanism", "the print (the metronome on the desk) against the stocks that move around it", ["the customs-office still on the bound host, held six seconds (M44)", "Ken Burns + the 35 px drift (E99 s65)", "the metronome lit on its word (E56: a picture's focus is the light)"], None, "a world plate with one motivated light; no recipe claims it"),
    ("the turn (rehook) + SPANS the 25 months", "the headline (the print's number) against where the month's gain actually lands", ["the trading-desk still on the bound host - a two-second turn, as Japan's ship", "the light on the PRINT strip on 'headline'"], None, "a turn plate under the mount that follows"),
    ("COMPARES (into vs after) + TURNS on 3x", "the half-month INTO the print against the half-month AFTER it (same stocks, same 25 prints)", ["bars page by THE MOUNT (the signature): the cream rises over the desk on 'when does', the bars DRAW under 'Twenty-five months' and land as the number sentence begins - then stand for the number (E99 s67); the page's own badge (FRONT-RUN 3x)", "spotlight on the INTO bar after the build, then on the AFTER bar", "figure at the datum", "chart_to compare: +6.8 % melts and splashes into 3x (E76 / E99 s56)", "the wall calendar as an evidence dock beside the bars (E45: reads, then parks)"], "recipe:emphasized-bar-lit", None),
    ("DIVIDES a whole (8 of 14) + the reflection line", "the 8 strong prints the stocks rose after against the 6 they fell after (the same 14)", ["share page (the donut exception, E53 s1) entering on its axes - the slices arrive, then stand", "the host's card reads beside the donut after the build (E63 / E65)", "the UP slice lit, then peeled on its word", "retitle on the sentence that renames the page"], None, "dock-lands-page-renames is proven on a MOUNT with the read at +8.2 s; this page enters on its axes and reads at +3.6 s - the same three members on the axes' own clock"),
    ("COUNTS a set (7 of 8) + TURNS on -6.9", "the 8 weak prints against each other - the ONE that rose lit, the 7 that fell counted by the badge", ["bars page entering on its axes - the eight bars GROW as 'Eight of them' is said (E99 s67)", "spotlight on the exception after the build", "retitle on 'After seven of the eight'", "figure at the latest bar", "the page's own badges (7 of 8; -13.8 %)"], "recipe:emphasized-bar-lit", None),
    ("the instance's world change", "July's page in the host's hand against the print on the concrete", ["the quay-at-dawn still on the bound host (a two-second turn, as Japan's ship)", "the plate idle"], None, "a two-second world change into the page that follows; no recipe claims a bare turn plate"),
    ("SPANS two weeks + TURNS on +16.4", "the stocks' -14 % in the two weeks after the July print against the chip price's +16.4 % a month later", ["dense line page entering on its axes: build_to the day the July print landed (the line DRAWS to it under the sentence)", "span: the two weeks shaded and named (P50 T4)", "build_to the end on 'The chip price itself?'", "figure at the August print", "the host with July's page reads beside the line (E48: the thread from the quay)"], None, "read-park-build-write is proven with two dock reads before the build; here one card reads after the first build - the same build_to and figure members on the axes' clock"),
    ("the reflection (the host to camera)", "good news (the calendar, read on its phrase) against bad news (July's page, read on its phrase)", ["the reflection's own still on the bound host: the small good-news sheet up, the big bad-news sheet down (E99 s67: no borrowed footage)", "two evidence docks reading in turn on their phrases (E45)"], None, "a world plate hosting two still docks; the verdict wall was dropped (nothing it could honestly re-present was docked)"),
    ("the ring's set-up", "you against the market (reading the print faster) - the office returns", ["the customs-office still returns (E48: the callback is a thread)", "the plate idle"], None, "a three-second return to the world before the ring page spirals in; the spiral is the next beat's signature"),
    ("THE RING (the calendar returns)", "the print's landing (the chip price's last print) against the stocks' last point - the same page as the open, returned", ["the page VORTEX return (spiral) - Japan's return", "the last print lit on its word", "callout ring on the stocks' last point (E56: a ring's one use)"], None, "punch-then-callout needs the punch, and the punch cut the page title off the frame (M43) - the light takes its place"),
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
    assert met[MET_JULY_IDX] == [2026.5339, 150.4] and met[MET_TWO_WEEKS_IDX][1] == 121.6 and met[MET_AUG_IDX] == [2026.616, 141.1] and len(met) == MET_LAST_IDX + 1, "the metronome object moved under the shot table"
    weak = json.loads((obj / "ev-weak-prints-v1.series.json").read_text(encoding="utf-8"))["bars"]
    assert weak[WEAK_EXCEPTION_IDX]["value"] == 10.9 and weak[WEAK_LATEST_IDX]["label"] == "Jul '26", "the weak-prints object moved under the shot table"
    register_assets()
    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META, indent=1), encoding="utf-8")

    T.caption_pages(BUILD, char_budget=28, max_words=6)

    rows = shot_table(ws, runtime_s, t_outro)
    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META, indent=1), encoding="utf-8")
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

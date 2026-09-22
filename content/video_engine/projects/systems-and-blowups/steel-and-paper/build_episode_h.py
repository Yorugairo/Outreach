"""Steel and Paper H - the LONG FORM's door (P68 T5, the 1:30 unit of proof).

    python build_episode_h.py               # -> build-h/  (the unit: 0:00-1:30, treatment rows 1-9)

The first long-form build that runs through the AUTHORING KIT (`scripts/authoring/`, CAPABILITIES:90 -
"the next long's door is the kit itself"). It is written BESIDE ep1's legacy door: `build_scene_evidence_cut.py`,
`SHOT-TABLE-F.py`, `build-f/`, `vo-f/`, `vo/`, every `SCRIPT-*` file, `REBUILD-TREATMENT-H.md`, `evidence/`,
`sound/`, `host/` and `vo-h-scratch/` are READ ONLY and are asserted so below (`_assert_read_only`); every write
this module makes lands inside `build-h/` (and `SHOT-TABLE-H.md`, the human-readable table, beside this file).

THE ROWS ARE THE TREATMENT'S (`REBUILD-TREATMENT-H.md` rows 1-9), anchored on WORDS - `at(ws, phrase)` off the
scratch take, never a typed second. Each departure from the treatment is a NAMED CONSTANT with its cite (R26-197):

  OPEN_PAGE / OPEN_ENTER   row 1 opens ON ITS AXES at 0.00 (E73) on THEIR two lines - `ev-bravos-original-v1`,
        the giants against the chip index - because `ev-divergence-v1` carries the memory line already and the
        page's own series `delay` (9.5 s, anchored to SCRIPT G's sentence) would draw "the layer it never drew"
        at 0:10, twenty seconds before the payoff says it. See LAYER_RECAST.
  LAYER_RECAST             row 4: the page RECASTS to `ev-divergence-v1` on "Here's the layer it never drew"
        (`;then=`, E58/E64) - the memory line arrives as the sentence names it, and the three end figures land
        on "twenty-one" / "a hundred and five" / "six hundred and thirteen".
  CAMERA_613               camera 1 - the row's ONE focus_zoom, on the +613 datum, on the words that name it
        (E99 s76; CAPABILITIES:85 one camera per timeline, :124 the declared target).
  CERT_CROP                the 1845 certificate cut out of `world-certificate-wall-v1` as ONE certificate
        (a PIXEL crop, x and y - `docks.still_card` crops a full-width BAND only; the departure is in the notes).
  AGENDA_ROWS_H            row 6: the numbered agenda (CAPABILITIES:43) in the room the page's park frees.
  HOST_PLATE               row 7: HOST WINDOW 1 - the Flow plate `host/H-1-studio.png` as the landing surface
        (`;use=landing;idle=drift;drift=20` + the ken push), the Bravos card thrown onto the desk's clear left
        third on "Not Bravos Research", the caption in STAGE mode.
  CAPITAL_FLOW             row 7: the flow diagram `capital -> value` on "Capital arriving faster" (CAPABILITIES:99).
  RAIL_PAGE / GDP_RECAST   rows 8-9: the dip back to the page, the railway index building on its own figures,
        then the recast to `ev-equip-ipp-gdp-v1`. THE 7 % AND 8 % TICKS THE TREATMENT NAMES DO NOT EXIST ON DISK
        (the object is share-of-GDP, 11.54 % at the Q2-2000 peak): the page rings ITS OWN data and the departure
        is written in `build-h/BUILD-NOTES-H.md`. No figure is invented (E77).
  RAIL_DROP                "-64%", the railway object's own arithmetic (2,062 -> 741), never the treatment's -66.
  BED_LU                   -28 LU under the voice: the LONG FORM's calibration, the project's own locked plan
        (`sound/SOUND-PLAN.json` "Bed gains at VO-28 LU"), not the short's -20 (E55).
  UNIT_CUT_PHRASE          the unit is the take's own clock to the cut before "So the obvious move" (~1:30).

## Recall

- Recall(package): content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/TITLE-CANDIDATES.md:54 "The AI Bubble Is Real. What Survives Is Steel." (the locked title; the unit's first sentence answers the thumbnail - E27 / E24)
- Recall(script): content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-H-VO.txt:1 "The AI bubble is real. Just not in the steel." (the gate-clean script; every row below is anchored on its words, never on a second)
- Recall(voice): content/video_engine/projects/systems-and-blowups/steel-and-paper/vo-h-scratch/SCRATCH-INDEX.md:1 "SCRATCH INDEX - jump points for the ear pass" (the scratch take is the build clock and is re-made as the script moves; HG3 auditions the voice on this 1:30)
- Recall(world): docs/portable/OPERATOR-RULINGS.md:3248 "A plate's life is DIRECTIONAL" (E99 s65 - the host plate carries the ken push and the 20 px drift, the long-form setting)
- Recall(evidence): content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/EVIDENCE-DOSSIER.md:120 "seven percent of GDP in two thousand" (the dossier routes this sentence to the PIMCO equipment-and-software series - the page rings its own numbers, never a 7 or an 8 that is not in the data)
- Recall(motion): docs/content-video-engine/CAPABILITIES.md:44 "THE NUMBERED AGENDA (P52 T8)" (row 6 - two to four numbered rows revealed one per word, in the room the park frees)
- Recall(sound): content/video_engine/scripts/authoring/audio.py:429 "the cues the frame plays, the cues dropped" (R26-198 - the cues are bound to what the compiled timeline fires BEFORE the gate report is stamped)
- Recall(publish): docs/portable/OPERATOR-RULINGS.md:3280 "1440p confirmed" (E99 s81 - this build renders nothing and serves nothing; the frozen copy, the link and the render are the parent's)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:2342 "The hook opens on its axes" (E73 - row 1 is the page on its axes from the first frame)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:1494 "Nothing ever goes truly still" (E49 - `;idle=live` on every page row, `;idle=drift;drift=20` on the plate)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3278 "A second card takes the outgoing card's slot" (E99 s80 - the certificate card hands its slot to the Bravos chart card)
- Recall(rulings): docs/content-video-engine/CAPABILITIES.md:93 "The AUTHORING KIT - one door for both formats, WIRED" (R26-17 step 0 - this door imports the kit and nothing from the F door)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project                                             # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W      # noqa: E402
import gate_motion_density as MG                                          # noqa: E402
import lab_build as LB                                                    # noqa: E402

BUILD_DIR = os.environ.get("STEEL_H_BUILD_DIR", "build-h")
BUILD = HERE / BUILD_DIR
TAKE = HERE / "vo-h-scratch"
TAKE_STEM = "scratch-kokoro"
SCRIPT = HERE / "SCRIPT-H-VO.txt"
TIMELINE_NAME = "steel-and-paper-h.timeline.json"
TABLE_NAME = "SHOT-TABLE-H.py"      # the compiled literal, in the PRIVATE build (the .md beside the project is the read)
EPISODE_ID = "steel-and-paper-h"
TITLE = "The AI Bubble Is Real. What Survives Is Steel."
SUBTITLE = "Money Physics - long form"
ASPECT = "16:9"
# The long form's caption: the kit's page builder default (34 chars / 6 words - `build_caption_pages.CHAR_BUDGET`,
# raised to 34 on the operator's watch 2026-09-01) and NO `caption_style`: "phrase" is the SHORT's mode (the page
# lands as one readable phrase, only k-words punctuated - build_scene_timeline_f.py:65). The long form keeps the
# per-word caption the STAGE mode was built on (CAPABILITIES:23).
CAPTION_BUDGET, CAPTION_MAX_WORDS, CAPTION_STYLE = 34, 6, None
PLATE_DRIFT_PX = 20.0    # E99 s65 / R26-228: the long form's plate drift, and the dial that makes it paint

EP = Project(here=HERE, build=BUILD, take=TAKE, take_stem=TAKE_STEM,
             script_name=SCRIPT.name, episode_id=EPISODE_ID, take_name="vo-h-scratch")

# ---------------------------------------------------------------- THE READ-ONLY WALL (R26-197, the v3 pattern)

READ_ONLY = ("build-f", "SHOT-TABLE-F.py", "SHOT-TABLE-F.md", "build_scene_evidence_cut.py", "vo-f", "vo",
             "vo-h-scratch", "REBUILD-TREATMENT-H.md", "SCRIPT-H-VO.txt", "SCRIPT-H-GATES.md", "evidence",
             "sound", "host", "packaging")


def _digest(path: Path) -> str:
    """A path's fingerprint - a file's bytes, a directory's (name, size) listing."""
    h = hashlib.sha256()
    if path.is_file():
        h.update(path.read_bytes())
    elif path.is_dir():
        for p in sorted(path.rglob("*")):
            if p.is_file():
                h.update(f"{p.relative_to(path).as_posix()}|{p.stat().st_size}".encode())
    else:
        return "absent"
    return h.hexdigest()


def _read_only_state() -> dict:
    return {rel: _digest(HERE / rel) for rel in READ_ONLY}


def _assert_read_only(before: dict) -> None:
    """Nothing outside `build-h/` moved. The v3 rule: every write outside the build dir is redirected or asserted."""
    moved = [rel for rel, d in _read_only_state().items() if d != before[rel]]
    if moved:
        raise SystemExit("FAIL: this build wrote into a READ-ONLY path: " + ", ".join(moved))


# ---------------------------------------------------------------- THE UNIT (the treatment's rows 1-9, to 1:30)

# THE 30-SECOND BED (E99 s82 (b)): the first world row only - 0:00 to the dip into the studio. The rows
# after it (the host window, the railway page) are T6's; this build proves the page.
UNIT_CUT_PHRASE = "The three questions read"   # the dip into the studio; the bed stops at the cut BEFORE it
UNIT_TAIL_S = 0.6                           # ... and the last sentence is allowed to land before the cut ends

# ---------------------------------------------------------------- THE EVIDENCE (every figure off its own object)

OBJECTS = HERE / "evidence/objects"
# ROW 1 OPENS ON THE VERIFIED OBJECT (the director-critic's attribution row, 2026-09-18).
# `ev-bravos-original-v1` carries `status: "SOURCES-TO-VERIFY"` and the operator's own note ("re-read the
# source before this file is cited for anything"), so it is neither the world nor a card in this cut. The
# page is `ev-divergence-v1` - names corrected 2026-09-03, +21 % / +105 % / +613 % verified - from 0.00,
# and the memory line is STAGED on it: see MEMORY_STAGED.
OPEN_PAGE = "ev-divergence-v1"           # row 1 AND row 4: one verified page, staged
LAYER_PAGE = "ev-divergence-v1"
RAIL_PAGE = "ev-railway-index-v1"        # row 9: the 442-company railway index, 1843-1850
GDP_PAGE = "ev-equip-ipp-gdp-v1"         # row 9: equipment + IP investment, share of GDP


def _series(name: str) -> dict:
    return json.loads((OBJECTS / (name + ".series.json")).read_text(encoding="utf-8"))


def _last_index(obj: dict, i: int = 0) -> int:
    return len(obj["series"][i]["pts"]) - 1


def _nearest(obj: dict, i: int, x: float) -> int:
    pts = obj["series"][i]["pts"]
    return min(range(len(pts)), key=lambda k: abs(pts[k][0] - x))


DIVERGENCE = _series(LAYER_PAGE)
# the divergence object's series order, read off the file (never typed): memory, semis, mega-cap, S&P
DIV_NAMES = [s.get("name", "") for s in DIVERGENCE["series"]]
DIV_MEMORY = next(i for i, n in enumerate(DIV_NAMES) if n.startswith("MEMORY"))
DIV_SEMIS = next(i for i, n in enumerate(DIV_NAMES) if n.startswith("SEMICONDUCTOR"))
DIV_MEGA = next(i for i, n in enumerate(DIV_NAMES) if n.startswith("MEGA"))
DIV_LAST = _last_index(DIVERGENCE, DIV_MEMORY)
DIV_LABEL = {i: DIVERGENCE["series"][i]["label"] for i in (DIV_MEMORY, DIV_SEMIS, DIV_MEGA)}   # +613% / +105% / +21%

ORIGINAL = DIVERGENCE          # one page now: the verified object is the world from 0.00
ORIG_SEMIS = DIV_SEMIS
ORIG_LAST = DIV_LAST
ORIG_MAMAA = DIV_MEGA
# M11 / E24: the first chart is annotated ON ITS DIVERGENCE - the datum where the two lines first part by
# DIVERGE_PTS index points, computed off the data, never eyeballed.
DIVERGE_PTS = 20.0
ORIG_DIVERGE = next(i for i, (a, b) in enumerate(zip(ORIGINAL["series"][ORIG_SEMIS]["pts"],
                                                     ORIGINAL["series"][ORIG_MAMAA]["pts"]))
                    if a[1] - b[1] >= DIVERGE_PTS)
# the CHIP line BUILDS ACROSS THE CERTIFICATE BEAT (E21 / M16: the frame lives while a card holds) - the
# page performs on the sentence's own phrases (P47 T2), four steps from the divergence to the last print
ORIG_STEPS = [round(ORIG_DIVERGE + (ORIG_LAST - ORIG_DIVERGE) * k / 4) for k in (1, 2, 3, 4)]
# ... and THE MEMORY LINE IS HELD AT ITS FIRST DATUM until the sentence names it. A page species may name
# the series it performs on, so "the layer it never drew" is genuinely not drawn until 0:30 - on the
# VERIFIED page, with no second object and no hand-over.
MEMORY_STAGED = True
# THE HOOK'S CHART IS BRAVOS' CHART, ON BRAVOS' SCALE (the director-critic's hook row). The object is
# log-scaled for a line that ends at 712, so with the memory line staged the two lines the hook is ABOUT
# sat flat under the bottom tick: measured on the frames before this change, the drawn ink filled 62 px of
# a 471 px plot at 0:03 (13 %) and 70 px of 301 px at 0:16. THE DOOR EXISTS: `chart_to rescale` takes a
# per-state Y DOMAIN - `ymin` / `ymax` on the species, carried into the derived state as `axes.domain`
# (build_scene_timeline_f.py:2356-2357, `rescale_state`) - so the page opens on a scale that fits the two
# lines and the AXIS RESCALES when the memory line is staged in, which is the operator's own named
# mechanic (CAPABILITIES:86's rescale, here on a line page). Both bounds are read off the data.
HOOK_SERIES = (DIV_SEMIS, DIV_MEGA)       # Bravos' two lines - the S&P rides with them (same values)
_hook_max = max(v for i in (DIV_SEMIS, DIV_MEGA, 3) for _x, v in DIVERGENCE["series"][i]["pts"])
# THE HOOK'S DOMAIN PRINTS TWO TICKS. The engine's log axis ticks at DOUBLINGS of a power of ten, starting
# at 10^floor(log10(ymin)) (scene-evidence-engine.mjs:8717-8722): from ymin 95 the sequence is
# 10-20-40-80-160-320, so the only tick inside [95, 277] was 160 - one tick for 24 s, which is the critic's
# row 3. The sequence reaches 100 only when ymin >= 100, and the mega-cap line's own low is 93.94, so a
# domain that prints 100 would CLIP the data - a lie of the other kind. The honest pick is the widest
# domain that clips nothing and prints two: [80, 1.06 x the hook's max] -> the ticks 80 and 160, with the
# lines filling 12.8 %-94.5 % of the plot's height (measured off the data on the log scale).
_hook_min = min(v for i in (DIV_SEMIS, DIV_MEGA, 3) for _x, v in DIVERGENCE["series"][i]["pts"])
HOOK_YMIN, HOOK_YMAX = 80.0, float(round(_hook_max * 1.06))
_all_max = max(v for sr in DIVERGENCE["series"] for _x, v in sr["pts"])
# the followed top is the line's own reach: the memory series tops at 1074.29 and the page keeps x1.06 of
# air above its data, so the highest a follow can push is 1138.75 - a ymax above it would be reached after
# the line had stopped, which is the drag the follow exists to end (the compiler refuses it by name).
FULL_YMIN, FULL_YMAX = 95.0, float(int(_all_max * 1.06 * 100) / 100)    # ... and the scale the memory line needs, off the data
                                                              # (a rescale must NAME its bounds: the compiler refuses
                                                              # `chart_to rescale` with neither domain nor window)
STAGED_SERIES = (DIV_SEMIS, DIV_MEGA, 3)  # every line the hook draws is STAGED, so no end tag prints at 0:03:
                                          # a tag lands when its own line lands, and these land together at 0:17

RAIL = _series(RAIL_PAGE)
RAIL_PEAK = _nearest(RAIL, 0, RAIL["marks"][0]["x"])
RAIL_TROUGH = _nearest(RAIL, 0, RAIL["marks"][1]["x"])
# the drop the page's OWN marks measure: 2,062 -> 741. The treatment says "-66%" and the object says -64.1 %;
# the object wins (E77: no figure is invented, and the page's own title reads "fell 64% from their peak").
RAIL_STEPS = [round(RAIL_PEAK * k / 4) for k in (1, 2, 3)]   # the 1843-45 climb, three steps before the peak
RAIL_DROP = "−%d%%" % abs(round(100 * (RAIL["marks"][1]["y"] / RAIL["marks"][0]["y"] - 1)))
# the capital raised is NOT on this chart's axis (the axis is an index of share prices): it is the page's own
# handwriting in the quiet zone, never a figure written at a datum that means something else (E52 / E28)
RAIL_NOTE = "Railways, 1845: £250m raised - over $1T in today's money"

GDP = _series(GDP_PAGE)
GDP_PEAK = _nearest(GDP, 0, 2000.25)          # the Q2-2000 peak the object's own hline names
GDP_LAST = _last_index(GDP)
GDP_PEAK_LABEL = GDP["hline"]["label"]        # "Q2 2000 peak - 11.54%", the object's own words
GDP_TITLE = GDP["title"]                      # ... and its own title: a recast carries the OLD page's title across
GDP_SUB = GDP["sub"]                          # (measured on the sheet at 0:84-0:90 - the railway title stood over
# ... and the two stretches the sentence NAMES (a span names time, a bracket measures two data -
# build_scene_timeline_f.py:456). MEASURED: a span of nine quarters drew as a narrow vertical BAR, which reads as
# a bar chart's bar and not as a period, so each names its own era end to end.
GDP_DOTCOM_FROM, GDP_DOTCOM_TO = _nearest(GDP, 0, 1998.0), _nearest(GDP, 0, 2003.0)
GDP_AI_FROM = _nearest(GDP, 0, 2020.0)

# ---------------------------------------------------------------- THE CARDS

CERT_PLATE = REPO / ("content/video_engine/projects/systems-and-blowups/review/claims/"
                     "steel-and-paper-plates-wave-1/objects/world-certificate-wall-v1.png")
# ONE certificate, cut by PIXELS off the plate (x and y, not only a height). `docks.still_card` / `docks.dock_png`
# crop a full-width BAND ((top, height) fractions - authoring/docks.py:85), which on this plate is five certificates
# and the blue shaft; `docks.dock_still(..., still=True, frame_crop=(w, h, x, y))` (authoring/docks.py:70) is the
# kit's only x-aware crop and it reads a PNG as happily as a clip. MEASURED on the plate's own 1536x1024 frame.
# ONE WHOLE CERTIFICATE WITH ITS PRINTED FACE (the critic's read of copy e: the old rectangle took an
# empty cartouche and a neighbour's corner). Picked by eye off the plate's own 1536x1024 frame and checked
# for the blue light shaft pixel by pixel: this is the ONLY certificate on the wall whose four borders,
# crest medallion, ruled signature line and engraved vignette are all visible at once. The plate's blue
# light shaft clips its lower-left corner - that is the plate's own light, not the crop's edge.
CERT_CROP = (282, 238, 296, 146)              # w, h, x, y
CERT_ASPECT = round(CERT_CROP[1] / CERT_CROP[0], 4)
CERT_CARD = "dock-h-certificate-1845"
# THE ROOM A FULL-STAGE PAGE LEAVES, measured on this build's own probe at 11.15 s: the chart's box is
# [45, 193, 1350, 756], its ink [137, 289, 964, 465], its three end tags run x 1110-1883 at y 372 / 612 /
# 649, and the anchored caption strip starts at y 919. The free rectangle is therefore x 1400-1900,
# y 700-910 - right of the plot, under the lowest tag, above the strip. The PLACER could not find it (it
# took the emptiest corner at the legibility floor, 101 x 102 px), so the row names it: 0.12 of the stage
# wide at (0.80, 0.745) -> x 1420-1880, y 700-910. A card at full stage is SMALL, and that is the
# geometric consequence of R26-205, not a choice - the notes carry the number.
CERT_ROOM = {"centre": True, "centre_w": 0.12, "centre_x": 0.80, "centre_y": 0.733}   # 0.745 clipped the caption strip by 505 px
# "his fourth copy of the same chart" is a card of the TWO-LINE chart - the page as it stands at that
# instant - never the finished four-line png (the critic's spoiler row: `ev-divergence-v1.png` carries the
# memory line, its legend and +613 %, five seconds before the sentence that reveals them). The kit's door
# is `docks.chart_card` -> `chart_card.render_card`, which renders a PAGE from a series object: so the
# build derives one - the verified object with the staged series dropped, written into the BUILD dir,
# every number copied, none typed - and renders the card from that.
BRAVOS_CARD = "dock-h-two-line-copy"
HOOK_OBJECT_ID = "ev-divergence-hook-v1"      # the derived object, in build-h/objects/ and nowhere else
HOOK_CARD_TITLE = "Two lines, one warning"    # the sentence's own words - the card IS the guy's copy
HOOK_CARD_SUB = "Mega-cap tech against the chip industry. 100 = Aug '25, log scale"
BRAVOS_ASPECT = 0.5625                        # the rendered page's own 16:9 (1080 / 1920)

# THE SLOT (E99 s80: a second card takes the outgoing card's slot; the chart never stands aside). Both cards on the
# page land in ONE room - the page's own low-right quiet zone. Measured against the 1920x1080 stage: the plot runs
# to about y 820 with its source line under it, so a card 0.30 of the stage wide centred at (0.735, 0.615) clears it.
# MEASURED on this build's own probe (`layout-probe.json`): at 16:9 with the page's quiet zone on the right the
# STAGE CAPTION's box is [1111, 432, 692, 144] - the same room a card wants. A card that crosses it leaves the
# compiler no band and the caption falls to the quiet anchor (E62 / CAPABILITIES:24 - the demotion is a POSITION,
# and a shrunk caption is the fault that ruling closed). So the slot sits UNDER that band: 0.20 of the stage wide,
# centred at (0.78, 0.76) - the certificate's box lands y 646-996, seventy pixels clear of the caption and clear of
# the page's source line on the left.
SLOT = {"centre": True, "centre_w": 0.17, "centre_x": 0.79, "centre_y": 0.737}
# ... and the second card LANDS instead of flying: a throw enters from the side the engine alternates
# (`d.side = flip++ % 2`), and MEASURED on this build the second card's flight crossed the page's data and
# its series names at 0:22 (M27, 12,672 px). The certificate keeps the throw - it is the named thing
# ARRIVING (E99 s71) - and the hand-off drops into the same slot from above, over nobody's ink.
SLOT_HANDOFF_ARRIVE = "land"

HOST_PLATE_ID = "world-h1-studio-v1"          # the Flow order H-1 still, registered by id (find_asset -> STAMPED)
HOST_PLATE_FILE = HERE / "host/H-1-studio.png"
HOST_KEN = (0.05, -12, 6)                     # the ken PUSH (E99 s65: Ken Burns + the 20 px drift IS the long form's plate life)
HOST_PLATE = HOST_PLATE_ID + ";use=landing"   # E61 the use. E99 s84: KEN BURNS ALONE - the operator, "the drift is too random,
#                                                  i think we should use ken burns instead of drift"; the 20 px drift of s65 is withdrawn for long form (R26-236)

DOCK_META = [
    {"asset": CERT_CARD, "title": "An 1845 railway certificate",
     "source": "Money Physics - plate world-certificate-wall-v1", "species": "deck", "badges": []},
    {"asset": BRAVOS_CARD, "title": HOOK_CARD_TITLE,
     "source": "Yahoo Finance - pairing after Bravos Research", "species": "chart", "badges": []},
]

# ---------------------------------------------------------------- THE PAGE ROWS

IDLE_LIVE = ";idle=live"                      # E49 on every page row: the board, its titles, labels and figures live
PAGE_EXIT_CUT = ":cut"                        # the page never retracts here - the DIP is the world change (E47)
OPEN_ENTER = "axes"                           # E73: the page lands with its ground, its ruled line, its title and its AXES
LAYER_RECAST = 1                              # the `;then=` state index row 4's recast moves to
GDP_RECAST = 1                                # ... and row 9's


# THE PAGE IS BORN ON THE HOOK'S DOMAIN (R26-223) and DRAWS LINE BY LINE (R26-226). Both are plate-id
# options now, so the two workarounds they replace are gone: the 0:04 `chart_to rescale` (ink that moved
# while no word named a move - E99 s82) and the per-phrase `build_to` staging (the crawl that stops).
PAGE_DOMAIN = ";domain=%g,%g"
PAGE_BUILD = ";build=lines:%g"
# <s> is ONE series' seconds and the page's build is s x N (R26-226-NOTE.md). Each line gets 1.2 s of pen -
# five times the 0.25 s floor - and the measured windows are in the notes: the last hook line lands well
# before "This certificate".
LINE_BUILD_S = 1.2


def page_open() -> str:
    """Rows 1-6's world: the VERIFIED divergence page on its axes at 0.00, one state, no recast.

    THE MEMORY LINE IS STAGED ON THE PAGE ITSELF (MEMORY_STAGED): a page species may name the SERIES it
    performs on (the engine's perform layer filters by `sp.series ?? sp.tier ?? sp.target.series`,
    scene-evidence-engine.mjs:11362), so the line the sentence calls "the layer it never drew" is held at
    its first datum from 0.00 and drawn on the words that name it. That is better than the recast it
    replaces: one page, one attribution, and no label hand-over."""
    return ("ledger:%s:line:%d:right:%s%s%s%s%s"
            % (OPEN_PAGE, ORIG_LAST, OPEN_ENTER, PAGE_EXIT_CUT, IDLE_LIVE,
               PAGE_DOMAIN % (HOOK_YMIN, HOOK_YMAX), PAGE_BUILD % LINE_BUILD_S))


def page_rail() -> str:
    """Rows 8-9's world: the railway index on its axes, and it stays that page to the end of the unit.

    THE SHARE-OF-GDP PAGE IS NOT SHOWN UNDER THOSE WORDS (the parent's read, 2026-09-18). The dossier
    routes "the internet crossed seven percent of GDP ... AI spending just crossed eight" to the PIMCO
    equipment-and-software series (`evidence/EVIDENCE-DOSSIER.md:120`) and that series IS
    `ev-equip-ipp-gdp-v1` - but what it measures is equipment + IP investment as a share of GDP:
    11.539 % at the Q2-2000 peak, 11.505 % today (the dossier's own correction, `:250`). A chart whose
    numbers read 11.5 while the sentence says seven and eight is a different measure on screen than in
    the words, so it is not shown: the railway page holds, and the object the sentence actually needs -
    AI / tech spending as a share of GDP on Bravos' math - IS MISSING FROM DISK. HG3's row."""
    return ("ledger:%s:line:%d:right:%s%s%s"
            % (RAIL_PAGE, RAIL_TROUGH, OPEN_ENTER, PAGE_EXIT_CUT, IDLE_LIVE))


# the numbered agenda's rows (CAPABILITIES:43): the test the promise names, one row per word
AGENDA_ROWS_H = [{"n": 1, "text": "Scarce?"}, {"n": 2, "text": "Cash or paper?"}, {"n": 3, "text": "Used tomorrow?"}]
# ... and the agenda's room is measured the same way: the caption's band ends at y 576 and the parked chart holds
# x 140-708 (probe at 52.02 s), so the block sits in the right room BELOW the caption. The first build put it at
# y 0.26-0.72 and the caption was written straight through the rows (read on the sheet at 0:48-0:54) - fixed here,
# not noted (R26-191).
AGENDA_BOX = {"kind": "region", "x0": 0.58, "y0": 0.585, "x1": 0.96, "y1": 0.90}
# THE CHART MELTS AND THE AGENDA LANDS ON THE BOARD (R26-229 b, the operator's own shape). The agenda's
# rows were landing on the parked page's end tags; a page parks for nothing, so the page does not park at
# all - on "One test" the whole chart MELTS TO A BALL and is thrown off (`melt:throw`, E88 / CAPABILITIES:37,
# the row's EXIT because a melt takes the world), and the board it clears for is the SLATE WITH THREE
# NOTCHES - build-f's own plate at this beat, dark enough for white type and literally the three questions
# as an object. The agenda lands CENTRED on its face, one row per word, on nothing but slate.
# A ROW'S `exit` IS THE TRANSITION **INTO** THAT ROW (the law: `door_boundary_error`'s own docstring,
# "may the door INTO `sc` open here?", build_scene_timeline_f.py:2186, with the predecessor passed beside
# it). The melt was authored on the PAGE row, which has no predecessor, so nothing melted and the slate's
# empty exit fell to the mechanical DIP - near-black at the boundary with the agenda's first row firing in
# it (the critic's read of copy e). It belongs to the SLATE row: the page melts to the ball, the ball is
# thrown, the slate lands.
# ... and the ENDING is the one the engine names for this boundary: a THROW hands the board to the next
# CHART, so into a plate it is refused by name ("a throw hands the same board to the next chart (E88) - the
# incoming world is not a ledger page; say melt:splash:plate to paint a plate"). The ball splashes onto the
# slate - the operator's own second ending (E76 s5: "splatter it back on to the canvas").
MELT_EXIT = "melt:splash:plate:%g"
MELT_S_H = 1.0            # the melt's own length: it opens on "One test," and the board is there on "three questions"
SLATE_PLATE = "world-three-notch-slate-v1;use=landing"   # E61 the use; E99 s84 - the plate's life is its ken push alone (R26-236)
SLATE_KEN = (0.04, 10, -6)   # the ken push - and under s84 it is the WHOLE of this plate's life, so its direction is the sentence's
# the slate's own face, measured on the plate: x 0.17-0.72, y 0.07-0.68 of the frame. The block sits inside it.
# ... and ABOVE the caption: on a PLATE row the caption is back in STAGE mode (the anchored strip is the
# page rule, R26-205), box [192, 432, 1535, 72] measured - so the block sits in the slate's upper face,
# y 0.10-0.37 (108-400 px), thirty-two pixels clear of the caption's top edge.
AGENDA_SLATE_BOX = {"kind": "region", "x0": 0.21, "y0": 0.10, "x1": 0.69, "y1": 0.37}
# NO VALUE STAMP beside the rows: the `stamp` species is admitted for the VECTOR MAP's three species alone
# (build_scene_timeline_f.py:671, SPECIES_TARGETS), so there is no stamp at hand for a list on a plate.
PARK_SCALE, PARK_ANCHOR = 0.80, "left"   # the ONE park in the bed - the agenda's breath (E61), ~20 % (the
                                        # operator). A page never parks for a caption or for a card that fits        # the chart parks KEEPING ITS LEFT, and the agenda lands in the room
# THE TAGS AND THE CAPTION SHARE ONE ROOM AT 16:9, AND THE PARK IS THE ONLY DOOR. Measured on this build's
# own probe: the stage caption's box is [1111, 432, 692, 144] and the page's terminal tags start at x 1005
# and run to x 1527 ("+613% MEMORY MAKERS (hynix+Micron)", 518 px) - so from the moment the lines finish
# drawing, the caption is written across them. Nothing on a row can shorten a tag (the names live in the
# evidence object and `PLATE_OPTS` has no label option - build_scene_timeline_f.py:111), and nothing can
# move a page row's caption to the anchored strip (`ledger_page.CAPTION_ANCHOR` 16:9 = (145, 878, 1630, 82)
# exists, and only a live DOCK demotes a caption to it). What a row CAN do is make the page smaller: a park
# scales the chart AND its tags about the box's left edge (measured at the 0.52 park: the 518 px tag became
# 271 px). The tag's right edge is 140 + (1527 - 140) * scale, so it clears the caption's left edge minus one
# line (1111 - 72) at any scale under 0.648 - hence 0.64, the largest park that clears.
PARK_TAGS_SCALE = 0.64
MEMORY_DRAW_S = 2.2   # the memory line's own build window on "Here's the layer it never drew"
RESCALE_S = MEMORY_DRAW_S   # R26-233: the axis yields to the line as it draws - ONE clock, not a hand-over
# ... and  is the door that lane built: the domain yields exactly as the followed series - the
# one this row stages with a  - climbs past the born top, so the landed ink does not move at all
# until the memory line exceeds 277 (the hook domain's own top), and then tracks the climb to the digit.
                            # beside it. The rescale's `dur` is the only dial a row has here, so it is set to
                            # the memory `build_to`'s own window and both open on t_layer; the drop is measured
                            # in the notes. A rescale whose EASING is the line's own climb is the row's.
_RESCALE_S_WAS = 1.0       # the axis hand-over's own length: while it runs, BOTH tick sets are on the page (the
                      # engine writes the arriving axis before the standing one has left), so the shorter it
                      # is the shorter that overlap - measured at 1.6 s it peaked at 13 ticks, at 1.0 s the
                      # critic's four instants are all inside one axis' worth
UNPARK_LEAD_S = 0.9   # the park is released this far before the rescale: a derived state that arrives on a
                      # parked page draws its axis full-width UNDER the parked one (measured, the critic's row 2)

# the flow diagram (CAPABILITIES:99): capital arriving faster than the value it is chasing. The glyphs are the
# SOURCED icons on disk (`content/video_engine/assets/icons`): coins for the capital, the factory for the value.
CAPITAL_FLOW = {"nodes": [{"id": "capital", "icon": "coins", "label": "CAPITAL"},
                          {"id": "value", "icon": "factory", "label": "VALUE"}],
                "edges": [["capital", "value"]]}
FLOW_BOX = {"kind": "region", "x0": 0.06, "y0": 0.06, "x1": 0.47, "y1": 0.40}     # the studio's dark monitor wall
# "and it isn't Nvidia" - THE CHIP, landing on its word and CROSSED OUT on the next (species/chip.mjs's own use:
# a sourced glyph, a label, the claim retracted). It sits on the desk wood left of the host, clear of the flow's
# box above and of the parked card below; the cross is what the sentence does to it.
NVIDIA_CHIP = {"kind": "chip", "icon": "cpu", "label": "NVIDIA",
               "target": {"kind": "point", "x": 0.47, "y": 0.59}}
CHIP_CROSS_S = 1.2
BRAVOS_ON_DESK = {"centre": True, "centre_w": 0.30, "centre_x": 0.215, "centre_y": 0.70,
                  "card_aspect": BRAVOS_ASPECT}   # the clear left third of the desk (the plate's own room)
# THE CARD READS, THEN IT IS PUT DOWN (E63 / the Tokyo pledge row's `read` + `park_s`): thrown big over the dark
# wall while the sentence says whose chart it is, then parked onto the desk's clear third on "and it isn't
# Nvidia". Two beats instead of one - the 3.9 s hole M16 found on this plate, filled with the card's own move.
# THE CARD CANNOT BE PLACED ON A PICTURE PLATE, so it is not docked on the host window at all.
# `dock_place` (build_scene_timeline_f.py:4005-4011) returns None unless the world is a LEDGER PAGE -
# E45's "a dock on a plain plate keeps the solo card" - so `centre`, `centre_w/x/y`, `read`, `read_s` and
# `park_s` are all dropped for a card on a plate. MEASURED on the first build of this window: the compiled
# dock entry carried `arrive` and `mass` and no `place`, and the engine's solo card landed at
# [758, 167, 1068, 515] - across the host's face, in the exact frames the Flow order kept his left third
# clear for. The parent's ruling is that a card never lands on the host, and there is no door to put it
# where the order reserved, so the window carries the plate, the chip and the flow instead. THE DOOR THAT
# IS MISSING: a placement for a dock on a plate (the plate's own declared room, as a page has).
HOST_CARD_REFUSED = "dock_place returns None on a plain plate (build_scene_timeline_f.py:4005-4011)"

CARD_READ_S = 5.5   # E25 / M12: a chart card proves its sentence and leaves - under the 6 s homework ceiling
CARD_CLEAR_S = 1.2  # ... and it is GONE before the page recasts, so the hand-over happens on a clear page
# CAMERA 1 (E99 s76; CAPABILITIES:85 - the row's optional 8th element). NOT a `focus_zoom` species: that species
# is the engine's own FOCUS_SCALE 1.32 (scene-evidence-engine.mjs:4884) and at 16:9 it cut the y-axis tick labels
# off the frame - MEASURED on this build's first probe (tick boxes at x -86 while the move held). The treatment's
# own row says a zoom at this aspect must be measured before it stays, so the move is AUTHORED as keys at
# CAMERA_ZOOM and released back to identity.
CAMERA_ZOOM, CAMERA_IN_S, CAMERA_HOLD_S = 1.06, 1.2, 2.4   # 1.10 cut the page title by 9 px (M43, measured)


def shot_table(ws: list, unit_end: float) -> list:
    """The treatment's rows 1-9, timed from the take. THREE worlds, ZERO cuts, TWO dips (E99 s74: a cut or a dip is
    the last resort) - the ledger page from 0.00, the host plate for the studio window, the page again."""
    at = lambda p: T.at(ws, p)
    cut = lambda p: W.cut_before(ws, p, exit="dip")

    def any_at(*phrases: str) -> float:
        """The first of these wordings the TAKE carries. Script H is still moving under the build (the scratch take
        was re-made three times while this module was written, and P04's opening went from "Somewhere a guy is
        watching his fourth copy" to "A guy is on his fourth copy"), and a row is anchored on its BEAT, not on one
        spelling of it. Every candidate names the same instant; a beat none of them matches still refuses by name."""
        for ph in phrases:
            try:
                return T.at(ws, ph)
            except SystemExit:
                continue
        raise SystemExit("no anchor in the take for this beat: " + " | ".join(repr(p) for p in phrases))

    def datum(i, s=None):
        d = {"kind": "datum", "index": i}
        if s is not None:
            d["series"] = s
        return d

    t_chips = at("Not the chips")                       # row 1 - the first annotation, on the divergence (M11)
    t_cert = cut("This certificate")                    # row 2 - the certificate card is thrown ON THE CUT
    # BEFORE the sentence, not on its first word: a caption page is stamped stage/anchor by whether a dock is
    # live AT THE PAGE'S START (`_dock_live_at`), so a card that arrives one word late has the whole first
    # page written across it - which is what the parent read at 0:10 ("This certificate" over the flying card).
    t_sold = at("paper sold as safety")                 # ... and the line keeps building under it, phrase by phrase
    t_paid = at("while the steel")
    t_trains = at("still carrying trains")
    t_hold = at("Hold an index fund")                   # ... the certificate's sentence is over here
    t_halves = at("you own both halves")
    t_copy = any_at("A guy is", "Somewhere a guy")                   # row 3 - the certificate's sentence is over
    t_fourth = any_at("fourth copy", "his fourth copy")                  # ... and the slot is handed to their own chart
    t_two_lines = at("two lines")                       # ... the callout on the two lines
    t_1845 = at("AI is 1845 again")                     # ... the retitle stroke
    t_layer = at("Here's the layer")                    # row 4 - the recast: the layer it never drew
    t_21 = at("up twenty-one percent")
    t_105 = at("a hundred and five")
    t_613 = at("six hundred and thirteen")
    t_warning = at("The warning is right")              # row 5 - the callout on the chip line ...
    t_address = at("The address is wrong")              # ... moves to the memory line
    t_test = at("One test")                             # row 6 - the park and the agenda
    t_three_q = at("three questions")
    t_thirty = at("thirty seconds")
    # the boundary is one MELT_S_H before "three questions", so the melt RUNS over "One test," and ENDS as
    # the slate lands on the word the first row fires on - the row never fires inside the transition
    t_melt = round(t_three_q - MELT_S_H, 2)
    t_sorts = at("and it sorts")                        # ... and the third row lands on the clause that sorts
    t_top_five = at("By the end")                       # ... and the note under it
    # (the bed stops at the dip into the studio: the host window and the railway page are T6's, and their
    # anchors live past this build's own words, so they are not read here.)

    return [
        # -- ROWS 1-6: THE PAGE IS THE WORLD (E58 / E61). One world, two chart states, two cards in one slot.
        (0.0, t_melt, page_open(), (0, 0, 0), [
            # THE 1845 CERTIFICATE ARRIVES - a thrown still card in the page's OWN room (E99 s71, E65).
            # THE PLACER CHOOSES IT: the authored slot was the caption workaround's companion, and with the
            # page full stage (R26-205) and the caption in the anchored strip the page's own measured empty
            # room is free. The notes carry the measurement (0 px on the ink, 0 px on the tags).
            (CERT_CARD, 0, t_cert, t_hold,
             dict(CERT_ROOM, arrive="throw", mass="paper", card_aspect=CERT_ASPECT)),
            # (NO CARD AT 0:21-0:29. The operator, E99 s82: a docked card of the same chart is nonsense -
            # the page IS the chart; the retitle "AI is 1845 again" carries the beat and the certificate's
            # slot stays empty after it leaves.)
        ], None, [
            # THE MEMORY LINE IS STILL THE REVEAL, and it is the ONE authored stop the ruling keeps.
            # `;build=lines` draws the four series in the PAGE'S OWN ORDER (R26-226-NOTE.md: `;order=` is
            # not built and the object is read-only), and memory is series 0 - so without this the page
            # would open on the very line the payoff is about. A `build_to` naming datum 0 caps that series
            # at nothing through its own window; the other three draw WHOLE in turn, each with its tag and
            # its badge as it lands; and the memory line draws whole on "Here's the layer it never drew".
            # Its window is the first of the four, so the build's first LINE_BUILD_S seconds draw nothing -
            # the axes, the title and the ruled line are the open (E73) and the first line arrives as the
            # first sentence lands.
            {"kind": "build_to", "at": 0.0, "dur": 0.4, "series": DIV_MEMORY, "target": datum(0)},
            # (NO RESCALE AT 0:04 and NO PARK AT 0:10 - E99 s82 amended: ink never moves unless the sentence
            # moves it, and a page parks only for something that needs its room. The page is BORN on the
            # hook's domain and stays full stage; the agenda's breath at 0:44 is the bed's one park.)
            {"kind": "retitle", "at": t_1845, "dur": 2.4, "text": "AI is 1845 again"},
            # row 4: THE LAYER IT NEVER DREW - the page becomes the divergence (E58 / E64), then the three ends write
            # THE AXIS RESCALES AS THE LAYER ARRIVES: the ticks open from the hook's scale to the memory
            # line's on the same clock the line draws on - the rescale the operator named, on a line page.
            {"kind": "chart_to", "at": t_layer, "dur": RESCALE_S, "to": "rescale",
             "ymin": FULL_YMIN, "ymax": FULL_YMAX, "follow": True},
            {"kind": "build_to", "at": t_layer, "dur": MEMORY_DRAW_S, "series": DIV_MEMORY, "target": datum(DIV_LAST)},
            # THE THREE ENDS, each on its own word - AND THE ENGINE CAN POINT AT ONLY ONE LINE. MEASURED twice on
            # this build's own frames (36.6 s and 39.6 s, `build-h/logs/`): a mark whose target names `series: 2`
            # or `series: 1` is drawn on SERIES 0's stroke - the page's `linePts` carries one series, so
            # `resolveTarget` clamps (scene-evidence-engine.mjs:12365). A ring on the wrong line is a wrong number
            # at a place, so the two lines that are NOT series 0 are never rung: the page writes their numbers at
            # their own ends (+21% / +105%, its own terminal tags), the GAP between the giants and memory BLEEDS
            # on "the giants, up twenty-one percent" (E56's own alternative - the divergence IS the argument), the
            # hand re-titles on "a hundred and five", and the one mark this page can aim lands on memory's end.
            {"kind": "spread", "at": t_21, "dur": 2.0, "from": DIV_MEGA, "to": DIV_MEMORY},
            {"kind": "retitle", "at": t_105, "dur": 2.4, "text": "The layer it never drew"},
            {"kind": "figure", "at": t_613, "dur": 2.2, "target": datum(DIV_LAST, DIV_MEMORY),
             "text": DIV_LABEL[DIV_MEMORY], "dy": -0.9},
            # row 5: the warning is right - the address is wrong. The hand writes the verdict as the title, and
            # THEN the ring lands on the address itself: the memory line, which is the one line a mark can name.
            {"kind": "retitle", "at": t_warning, "dur": 2.0, "text": "Right warning. Wrong address."},
            # (and no ring on "The address is wrong": the sentence names the MEMORY line and the engine drew
            # the ring on the S&P / mega-cap tip - the parent read it on the frame at 0:42)
            # (the page neither parks nor carries the list any more: the chart melts on "One test" and the
            # agenda lands on the slate - the row below.)
        ], {"keys": [
            {"t": round(t_613 - 0.2, 2), "zoom": 1.0, "look": datum(DIV_LAST, DIV_MEMORY), "ease": "inout"},
            {"t": round(t_613 + CAMERA_IN_S, 2), "zoom": CAMERA_ZOOM, "look": datum(DIV_LAST, DIV_MEMORY), "ease": "inout"},
            {"t": round(t_613 + CAMERA_IN_S + CAMERA_HOLD_S, 2), "zoom": 1.0, "look": datum(DIV_LAST, DIV_MEMORY), "ease": "inout"},
        ]}),
        # -- THE BOARD: the slate the melt clears for, and the three questions on it, one row per word.
        (t_melt, unit_end, SLATE_PLATE, SLATE_KEN, [], MELT_EXIT % MELT_S_H, [
            {"kind": "agenda", "at": t_three_q, "dur": round(unit_end - t_three_q - 0.4, 2),
             "target": AGENDA_SLATE_BOX,
             "rows": [dict(AGENDA_ROWS_H[0], at=t_three_q), dict(AGENDA_ROWS_H[1], at=t_thirty),
                      dict(AGENDA_ROWS_H[2], at=t_sorts)]},
        ]),
        # (-- ROWS 7-9 are T6's: the host window and the railway page. The bed is the page.)
    ]


# ---------------------------------------------------------------- THE SOUND (this episode's cue map)

# The project's own locked files and levels (`sound/SOURCES.md`, `sound/SOUND-PLAN.json`): every accent file meters
# about -14 LUFS, so an accent gain of 0.12 sits it ~14 dB under a voice at the same level. The scratch take is
# QUIET (-28.0 LUFS, measured 2026-09-18, untoned), so the bed is derived against that measurement, not a remembered one.
ROLL, STROKE, WHOOSH = "fs-page-roll-464302.mp3", "fs-page-stroke-447925.mp3", "fs-whoosh-3-648729.mp3"
BED_HOOK_A, BED_HOOK_B = "suno-hook-B.mp3", "suno-hook-A.mp3"
ACCENT, ENTER_GAIN = 0.12, 0.12
BED_LU = -28.0        # the LONG FORM's calibration (sound/SOUND-PLAN.json: "Bed gains at VO-28 LU"); -20 is the short's (E55)
VO_LUFS = -28.0       # vo-h-scratch/scratch-kokoro.mp3, measured with ffmpeg ebur128 on 2026-09-18
BED_LUFS = -13.3      # sound/suno-hook-B.mp3, measured the same way
BED_SWELL_DB, SNAP_S_BED = 4.0, 0.45


def sound_cues(rows: list) -> list:
    """Which file plays where, and how loud - over the kit's own reading of the rows' transitions and arrivals."""
    stop = A.stop_dials()
    cues = []
    for i, r in enumerate(rows):
        page = A.page_transitions(r[2])
        if page["ledger"] and not page["mount"] and not page["spiral"]:
            # the slot names the ENTRY the compiled timeline actually plays (`authoring.audio.page_entry`):
            # an `axes` page fires `page enter (axes)`, never the cream roll-out, and a cue that claims the
            # wrong one is dropped by the binder (R26-198)
            cues.append({"slot": "page enter %d (%s)" % (i + 1, OPEN_ENTER), "at": round(r[0], 2),
                         "gain": ENTER_GAIN, "fade_in": 0.0, "variants": {"A": ROLL}})
        for d, opts in A.row_arrivals(r):
            arrive = opts["arrive"]
            contact = A.landing_contact(d[2], arrive, stop)
            cues.append({"slot": "landing %d (%s, %s)" % (i + 1, arrive, opts.get("mass", "paper")),
                         "at": round(contact - 1 / 24, 2), "gain": ACCENT, "fade_in": 0.0,
                         "variants": {"A": STROKE, "B": ROLL},
                         "note": "contact at %.2fs, the cue one frame early (the weight report Q5)" % contact})
        if r[5] == "dip":   # the world change's own accent (E47)
            cues.append({"slot": "dip %d" % (i + 1), "at": round(r[1] - 0.35, 2), "gain": ACCENT,
                         "fade_in": 0.0, "variants": {"A": WHOOSH}})
    env = A.bed_envelope(rows, BED_SWELL_DB, SNAP_S_BED, fallback_end=lambda d: float(d[2]) + 1.2)
    cues.append({"slot": "hook bed", "at": 0.0, "gain": A.bed_gain(VO_LUFS, BED_LU, BED_LUFS), "fade_in": 1.5,
                 "env": env, "variants": {"A": BED_HOOK_A, "B": BED_HOOK_B},
                 "note": "%+.0f LU under the VO (%.1f LUFS measured); the long form's calibration" % (BED_LU, VO_LUFS)})
    return cues


# ---------------------------------------------------------------- THE BUILD

def _take_audio(unit_end: float) -> None:
    """The take into the build - the UNIT's seconds only, so the clock the gates measure is the cut's own.
    `vo-h-scratch/` is read and never written."""
    src = TAKE / (TAKE_STEM + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-t", "%.3f" % unit_end,
                    "-c:a", "libmp3lame", "-q:a", "2", str(EP.audio_master)], check=True)


def _hook_object() -> Path:
    """The verified object with the STAGED series dropped, written into the build dir - the source of the
    two-line card. Every number is copied from `ev-divergence-v1.series.json`; the title and the sub are the
    card's own words, and the source line is the object's, unchanged."""
    import copy
    obj = copy.deepcopy(DIVERGENCE)
    obj["series"] = [sr for i, sr in enumerate(DIVERGENCE["series"]) if i != DIV_MEMORY]
    obj["badges"] = [b for b in (DIVERGENCE.get("badges") or []) if not str(b.get("label", "")).startswith("MEMORY")]
    obj["title"], obj["sub"] = HOOK_CARD_TITLE, HOOK_CARD_SUB
    obj.pop("names_note", None)
    out = BUILD / "objects" / (HOOK_OBJECT_ID + ".series.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    return out


def _shot_table_md(rows: list) -> str:
    """SHOT-TABLE-H.md - the table a human reads: one row per window, its world, its use and idle, what fires."""
    out = ["# SHOT TABLE H - the 1:30 unit (P68 T5)", "",
           "GENERATED by `build_episode_h.py` from `%s/%s.words.json`. Do not hand-edit -" % (TAKE.name, TAKE_STEM),
           "edit `build_episode_h.shot_table`. Every anchor is a PHRASE off the take (`authoring.words.at`).", "",
           "| # | window | world | options | cards | what fires |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(rows):
        bare, _, opts = str(r[2]).partition(";")
        cards = ", ".join("`%s` %.2f-%.2f" % (d[0], d[2], d[3]) for d in (r[4] or [])) or "-"
        species = "; ".join("%s @%.2f" % (e["kind"], e["at"]) for e in (r[6] or []) if isinstance(e, dict)) or "-"
        out.append("| %d | %.2f-%.2f | `%s` | `%s` | %s | %s |"
                   % (i + 1, r[0], r[1], bare, opts or "-", cards, species))
    idle = [(i + 1, str(r[2]).partition(";")[2]) for i, r in enumerate(rows) if ";idle=" in str(r[2])]
    out += ["", "**Idle tokens: %d of %d rows** - " % (len(idle), len(rows))
            + "; ".join("row %d `%s`" % (n, o) for n, o in idle) + " (E49; E99 s65 the 20 px long-form drift).",
            "", "**Flow count (E99 s74):** 0 cuts, %d dips, each at a world change (E47): a chart cannot recast "
            "into a photograph plate and a plate cannot recast into a chart."
            % sum(1 for r in rows if r[5] == "dip"), ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--whole", action="store_true", help="the whole table (T6) - rows 10-24 are not authored yet")
    args, _ = ap.parse_known_args()
    if args.whole:
        raise SystemExit("FAIL: the whole table is T6's - this module authors the treatment's rows 1-9 (the 1:30 unit)")

    read_only = _read_only_state()
    EP.mkdirs()
    ws_all = W.take_words(EP)
    # THE UNIT ENDS ON A WHOLE SENTENCE (the critic's tail row: the trim left an orphan caption "So" on
    # the last frame). The cut before P12 is the boundary; the unit keeps every word up to the last HARD
    # STOP before it, and the audio runs UNIT_TAIL_S past that word so the line closes instead of snapping.
    boundary = W.cut_before(ws_all, UNIT_CUT_PHRASE, exit="dip")
    spoken = [w for w in ws_all if w["start_s"] < boundary]
    last_stop = max(i for i, w in enumerate(spoken) if w["w"].rstrip().rstrip('"\u201d')[-1:] in W.HARD_STOPS)
    ws = spoken[:last_stop + 1]
    unit_end = round(ws[-1]["end_s"] + UNIT_TAIL_S, 2)
    _take_audio(unit_end)
    W.write_timeline(EP, ws, unit_end)
    print("  take        : %s - the unit is 0.00-%.2fs (%d of %d words)"
          % (TAKE_STEM, unit_end, len(ws), len(ws_all)))

    T.caption_pages(BUILD, char_budget=CAPTION_BUDGET, max_words=CAPTION_MAX_WORDS)

    # the cards: the certificate cut out of its plate, their chart copied as a screenshot (no `.series.json` beside
    # it, so the compiler docks a STILL and never re-draws our own page inside their card)
    D.dock_still(CERT_CARD, CERT_PLATE, BUILD, still=True, frame_crop=CERT_CROP)
    D.chart_card(BRAVOS_CARD, _hook_object(), BUILD, "line")   # the TWO-LINE page, rendered from the derived object
    D.register(HOST_PLATE_ID, HOST_PLATE_FILE)   # the Flow plate by id (build_render_f.find_asset checks STAMPED first)

    rows = shot_table(ws, unit_end)
    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META, indent=1), encoding="utf-8")
    table = BUILD / TABLE_NAME
    T.write_shot_table(table, rows,
                       '"""Steel and Paper H - the 1:30 unit, GENERATED by build_episode_h.py. Do not hand-edit."""\n')
    (HERE / "SHOT-TABLE-H.md").write_text(_shot_table_md(rows), encoding="utf-8")
    T.print_rows(rows, show_docks=True)

    # R26-197: the receipt for this cut is THIS module's `## Recall` block (the project carries no PRODUCTION-LEDGER)
    import recall_verify as RV
    _inner = RV.resolve_ledger
    RV.resolve_ledger = lambda target: Path(__file__) if Path(target).resolve() == HERE else _inner(target)
    rc = T.compile_timeline(
        HERE, BUILD, timeline_name=TIMELINE_NAME, shot_table_file=os.path.relpath(table, HERE),
        title=TITLE, subtitle=SUBTITLE, episode_id=EPISODE_ID,
        aspect=ASPECT, caption_style=CAPTION_STYLE,
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False,
                  "curvature_stroke": True,
                  # R26-228: an authored `;drift=` paints 0 px unless this dial is on. The bed carries no
                  # plate, but the dial is set here so the whole cut inherits it (E99 s65: 20 px long form).
                  "plate_idle_paints": False})   # E99 s84 / R26-236: Ken Burns alone; the painted drift is off for long form
    if rc:
        return rc

    # R26-198: the cues are BOUND to what the compiled timeline fires, and only then is the report stamped
    cues = sound_cues(rows)
    plan_path = BUILD / "SOUND-PLAN.json"
    plan_path.write_text(json.dumps(
        {"note": "derived by build_episode_h.py; the project's sound/SOUND-PLAN.json is untouched", "cues": cues},
        indent=1), encoding="utf-8")
    for note in LB.embed_cues(sys.modules[__name__], BUILD, cues, TIMELINE_NAME):
        print("  [sound] " + note)
    for note in LB.bind_embedded_cues(BUILD, plan_path, TIMELINE_NAME):
        print("  [sound] " + note)
    tl = json.loads((BUILD / TIMELINE_NAME).read_text(encoding="utf-8"))
    print("  cues        : %d bound of %d derived" % (len(tl.get("sound") or []), len(cues)))
    for note in A.unsounded(list(tl.get("sound") or []), tl):
        print("  [silent] " + note)

    report, n_fail = MG.write_report(BUILD, TIMELINE_NAME)
    print("  motion gate : %s - %d FAIL" % (report.name, n_fail))
    idle = [i + 1 for i, r in enumerate(rows) if ";idle=" in str(r[2])]
    print("  idle tokens : %d of %d rows (%s)" % (len(idle), len(rows), ", ".join(str(i) for i in idle)))
    _assert_read_only(read_only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

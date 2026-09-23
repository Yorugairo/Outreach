"""Steel and Paper H - the LONG FORM's door (P68 T5, the 1:30 unit of proof).

    python build_episode_h.py               # -> build-h/  (the unit: 0:00-1:30, treatment rows 1-9)

The first long-form build that runs through the AUTHORING KIT (`scripts/authoring/`, CAPABILITIES:90 -
"the next long's door is the kit itself"). It is written BESIDE ep1's legacy door: `build_scene_evidence_cut.py`,
`SHOT-TABLE-F.py`, `build-f/`, `vo-f/`, `vo/`, every `SCRIPT-*` file, `REBUILD-TREATMENT-H.md`, `evidence/`,
`sound/`, `host/`, `vo-h-scratch/` and `REFERENCE-F.md` are READ ONLY and are asserted so below (`_assert_read_only`); every write
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
        (`;use=landing` + the ken push ALONE - E99 s84 withdrew the 20 px drift for long form, R26-236), opened on
        the promise (HOST_FROM_PHRASE, M44's six seconds); their chart card thrown on "Bravos Research".
  CARD_LEAD_S / page_snap  row 7 (P69 T15b): THE CARD BECOMES THE CHART - one second after the throw the camera pushes
        the card to the stage and the page shows at the match (throw-then-push, `camera=`; E99 s71); read full size.
  CAPITAL_FLOW             row 7: the flow diagram `capital -> value` on "capital arriving faster" (CAPABILITIES:99),
        in the page's own empty room; the NVIDIA chip lands on the page on "Nvidia" and is crossed.
  RAIL_PAGE / GDP_RECAST   rows 8-9: the dip back to the page, the railway index building on its own figures,
        then the recast to `ev-equip-ipp-gdp-v2`. THE 7 % AND 8 % TICKS THE TREATMENT NAMES DO NOT EXIST ON DISK
        (the object is share-of-GDP, 11.54 % at the Q2-2000 peak): the page rings ITS OWN data and the departure
        is written in `build-h/BUILD-NOTES-H.md`. No figure is invented (E77).
  RAIL_DROP                "-64%", the railway object's own arithmetic (2,062 -> 741), never the treatment's -66.
  BED_LU                   -28 LU under the voice: the LONG FORM's calibration, the project's own locked plan
        (`sound/SOUND-PLAN.json` "Bed gains at VO-28 LU"), not the short's -20 (E55).
  UNIT_CUT_PHRASE          the build is the take's own clock to the cut before the NEXT row's first words: P69 T15
        moved it past row 7 to "But capital that fast" (row 8, T16's), P69 T16 past row 8 to "Every transformative"
        (row 9, T17's), P69 T17 past row 9 to "So the obvious move" (row 10, T18's), P69 T18 past row 10 to
        "But walk Bravos'" (row 11, T19's); each body row moves it on.
  HOST_DIP_WHY             row 7's dip INTO the studio, and the transform it refused by name (E47, E99 s74).
  SNAP_WHY / RAIL_MELT_WHY row 7's throw-then-zoom into THEIR chart (P69 T15b) and row 8's melt into the railway
        index - each boundary's transform TAKEN and every one it refused, by name (E47, E99 s71, s74).
  RAIL_CLIMB               row 8: the index starts on its axes (E73) and CLIMBS through the paper trail - one
        continuous pen from the dip, never the stop-and-go crawl R26-226 retired.
  SELL_CARD / DIV_RECAST   row 10 (P69 T18, T18b): the sell ticket - the order form's FACE cut out of
        `world-sell-ticket-v1` (clear of the plate's rubber stamp, E99 s92) with SELL STAMPED across it - thrown on
        "the obvious move", read in the page's right room, parked; the page RECASTS under it (E64), memory held.
  MEMO_PLATE / RECORD_SLOT rows 11-12 (P69 T19b, T20): the divergence MELTS onto the memo desk; Karp's record, the Uber
        chart, the COO's line and the three-manias table take one slot in turn, the mug's steam the desk's life.
  VIADUCT_PLATE            row 13 (P69 T21): RESET 1 - dip 2 to the 1849 viaduct, Ken Burns and the stack's steam.
  YARD_PAGE / YARD_BARS    row 14 (P69 T22): dip 3 to the yardstick page in the long form's profile (LONGFORM), camera 2
        on the 28 as it lands (YARD_CAM_*, a point look - the datum look runs away when panned), and the recast to the
        breakthrough bars, the railways' 50 bursting the stated [0, 30] scale (E60).
  TNX_PAGE / FED_PROP      row 15 (P69 T23): the bars melt and are thrown (E88) and the 10-year yield draws in its two
        eras on one page (`ev-tnx-two-eras-v4`, ordinary series - v3's panels never draw on a ledger page), the Fed's
        6.5% and their 5.5% its RULES (E53 s5); PROP 1 the Fed STAMPED on its word into the page's biggest room (P69
        T5), bare of paper with its hatch (E99 s92); the BoE and the concession written on the same page.

THE BODY'S PREFLIGHT (P69 T14, rows 7-24) is three constant tables, read before any body row is authored:
  BODY_ASSETS          every page object (with its builder), card, plate, prop, host still, cue file and outro part
        a row names, resolved on disk (`P69-T14-INVENTORY.md`, re-checked). Row 16's debt issuance is the LINE page
        `ev-debt-issuance-line-v1` with its 2026E range as a spread + figure (DEBT_SPREAD / DEBT_RANGE_*), row 19
        is `ev-two-clocks-bars-v1`; neither falls back to a PNG.
  BODY_DEPARTURES      (row, item, fallback) for everything the treatment names that is NOT on disk
        (`build-h/P69-DATA-DEPARTURES.md`, folded into `build-h/BUILD-NOTES-H.md` section 9).
  TREATMENT_SUPERSEDED the rulings that overrule the treatment's wording (E99 s84, s83, s91, E47, E50), quoted.
The cue map's landing slot names the arrival's MASS through `A.arrival_mass` (`landing N (stamp, ink)` unless the
row names one), and HOST_CARD_DOOR records that a card CAN now stand on a picture plate (R26-221).

## Recall

- Recall(package): content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/TITLE-CANDIDATES.md:54 "The AI Bubble Is Real. What Survives Is Steel." (the locked title; the unit's first sentence answers the thumbnail - E27 / E24)
- Recall(script): content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-H-VO.txt:1 "The AI bubble is real. Just not in the steel." (the gate-clean script; every row below is anchored on its words, never on a second)
- Recall(voice): content/video_engine/projects/systems-and-blowups/steel-and-paper/vo-h-scratch/SCRATCH-INDEX.md:1 "SCRATCH INDEX - jump points for the ear pass" (the scratch take is the build clock and is re-made as the script moves; HG3 auditions the voice on this 1:30)
- Recall(world): docs/portable/OPERATOR-RULINGS.md:3248 "A plate's life is DIRECTIONAL" (E99 s65 - the host plate carries the ken push and the 20 px drift, the long-form setting)
- Recall(evidence): content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/EVIDENCE-DOSSIER.md:120 "seven percent of GDP in two thousand" (the dossier routes this sentence to the PIMCO equipment-and-software series - the page rings its own numbers, never a 7 or an 8 that is not in the data)
- Recall(motion): docs/content-video-engine/CAPABILITIES.md:44 "THE NUMBERED AGENDA (P52 T8)" (row 6 - two to four numbered rows revealed one per word, in the room the park frees)
- Recall(sound): content/video_engine/scripts/authoring/audio.py:471 "the cues the frame plays, the cues dropped" (R26-198 - the cues are bound to what the compiled timeline fires BEFORE the gate report is stamped)
- Recall(publish): docs/portable/OPERATOR-RULINGS.md:3280 "1440p confirmed" (E99 s81 - this build renders nothing and serves nothing; the frozen copy, the link and the render are the parent's)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:2342 "The hook opens on its axes" (E73 - row 1 is the page on its axes from the first frame)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:1494 "Nothing ever goes truly still" (E49 - `;idle=live` on every page row, `;idle=drift;drift=20` on the plate)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3278 "A second card takes the outgoing card's slot" (E99 s80 - the certificate card hands its slot to the Bravos chart card)
- Recall(rulings): docs/content-video-engine/CAPABILITIES.md:94 "The AUTHORING KIT - one door for both formats, WIRED" (R26-17 step 0 - this door imports the kit and nothing from the F door)
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
             "sound", "host", "packaging", "REFERENCE-F.md")   # P69 T14 (6): ep1's reference note joins build-f/


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

# THE BUILD GROWS ONE BODY ROW AT A TIME (P69 T15-T32). The 30-second bed (E99 s82 (b)) stopped at the cut before
# "The three questions read"; P69 T15 authors row 7 (the studio) and moves the cut past it, to the first words of
# row 8 - the dip back to the page, which is T16's. Each body slice moves this phrase to its own row's end.
# P69 T16 authors row 8 (the rehook) and moved it to row 9's first words; P69 T17 authors row 9 (the railway index and
# the GDP recast) and moves it on to row 10's first words (the head-fake, T18's). P69 T18 authors row 10 (the sell
# ticket thrown over the recast) and moves it on to row 11's first words (the adjuster's walk, T19's). P69 T19 authors
# row 11 (one slot, three records) and moves it on to row 12's first words (the trough, T20's). P69 T20 authors row 12
# (the trough, on the same desk) and T21 row 13 (reset 1, the dip to 1849), and they move it to row 14's first words.
# P69 T22 authors row 14 (the yardstick) and moved it to row 15's first words (the trigger, T23's); P69 T23 authors row 15
# (the trigger, the concession and PROP 1) and moves it to row 16's first words (who is paying, T24's).
UNIT_CUT_PHRASE = "But here's the question"   # row 16's first words; the build stops at the cut BEFORE them
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
GDP_PAGE = "ev-equip-ipp-gdp-v2"         # row 9: equipment + IP investment, share of GDP (v2 = v1 + year ticks + y label, E28, R26-262)


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
# ROW 8's CLIMB (P69 T16). The index opens on its axes (E73) and the build beat - which a line page spends on its
# FIRST cap (scene-evidence-engine.mjs BUILD-ON: "the build beat is spent on the first cap") - draws it to the
# first quarter of the climb as the page lands; then ONE pen carries it on from "paper trail" to the half-way
# point, arriving as the next sentence begins, where row 9 (T17) picks the same stroke up. Two caps, continuous,
# never the stop-and-go per-phrase crawl the bed retired (R26-226, E99 s82).
RAIL_OPEN_CAP, RAIL_TRAIL_CAP = RAIL_STEPS[0], RAIL_STEPS[1]
RAIL_JOIN_LEAD_S = 0.1   # the trail's cap lands this far before the next sentence's first word (the row's own end)
# ROW 9 (P69 T17): THE SAME STROKE CARRIES ON to the October 1845 peak, landing as "a quarter-billion" is said (the
# treatment's anchor), and the crash draws on "crashed"; the drop is written at the trough as the object's own
# arithmetic (RAIL_DROP, -64%), red and BELOW the point - E28: a drop goes down, and 741 sits under the page's own
# 1843-level rule (1,000), so the number stays on the rule's under side.
RAIL_CRASH_S = 1.2       # the crash's own draw, "crashed by nearly" - it lands before "two-thirds" ends
RAIL_DROP_DY = -0.9      # the figure's baseline, in its own LINEs, over the trough and still UNDER the 1,000 rule:
                         # draft1 wrote it at +1.1 (below the point) and the trough is the plot's floor, so "-64%"
                         # landed on the x axis' own "1850" (p69t17/draft1 79.30)
RAIL_DROP_S = 1.4
# THE RECAST (E58 / E64, CAPABILITIES:28 - the plain hand-over: the railway line un-draws by its own law, the title,
# sub and source rewrite in the hand, the share-of-GDP line draws on). It fires on "the internet" - the sentence's
# subject - so the crash and its -64% stand from their landing to the new era's first noun. Its own numbers only
# (BODY_DEPARTURES row 9): no 7 % tick, no 8 % datum (neither is on the object, E77).
GDP_RECAST_S = 2.0
# ... and the ring (E56: a ring circles a point on a chart) lands on the page's OWN datum: the Q2-2000 peak, 11.54 %,
# on "then the tower came down" - the top before the fall, named by the sentence, and NOT under the seven / eight
# words (the departure: the page's numbers are another measure than the voice's, so nothing of it is rung there).
GDP_RING_S = 3.0
# NO LABEL on the ring: the page's own rule already writes "Q2 2000 peak - 11.54%" beside that very point, and a
# "Q2 2000" label wrote across it (p69t17/draft1 84.20) - the ring points, the page says it once (M28).
# THE RECAST KEEPS THE RAILWAY TITLE (measured, draft1 82.60-88.50: the sub and source rewrote, the title
# "British railway shares fell 64% from their peak" stood over the US GDP line) - the 2026-09-18 unit's lesson,
# still true of the plain hand-over - so the hand writes the arriving object's OWN title as the recast runs.
# THE GDP LINE LANDS AT THE RAILWAY'S LAST CAP: a build_to caps a SERIES INDEX on the page, and every state's
# series 0 reads the same caps, so the recast draws the share-of-GDP line to index RAIL_TROUGH (Q4 2004) - the
# dot-com peak and the fall after it, which is what "then the tower came down" names. Its last twenty years draw on
# "AI spending just crossed": the line climbs back to its 2000 peak (the page's own title: "back at its dot-com
# peak"), landing on "eight." (FLAGGED: its end tag reads the page's 11.51 %, another measure than the voice's 8.)
GDP_CLIMB_S = 2.0
RETITLE_AFTER_S = 0.1   # the retitle belongs to the ARRIVING page: one written ON the recast's own word is the page
                        # being replaced, and the compiler drops it (R26-219 (c), "nothing to write" - t17-door2.log)
# RAIL_NOTE (the treatment's "250m pounds, then $1T+ today") IS NOT WRITTEN: neither figure is on disk - a search for
# "250m" finds only the treatment and this door, and EVIDENCE-DOSSIER.md carries no railway capital figure (a
# research-gate UNSOURCED figure never draws, E77). The caption carries the script's words; the departure is noted.
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

# ROW 10 (P69 T18): THE SELL TICKET, a DOCUMENT card cut out of its plate the way the certificate is (`dock_still`
# with an x-aware pixel crop). The plate `world-sell-ticket-v1` is a desk: two book stacks, a mug, a second sheet, a
# RUBBER STAMP and the ruled order form. A prop is never on a card (E99 s92), and the stamp's base stands at plate x
# 985+ beside the form's right edge, so no rectangle takes the whole form without the stamp, the neighbouring sheet or
# the desk. The crop is therefore the form's OWN FACE - its ruled columns and rows, every pixel paper - measured
# on the plate's 1536x1024 frame inside the four edges (top-left (660, 568), top-right (948, 506), bottom-right
# (1020, 782), bottom-left (716, 832)). A blank form is only a ticket once it says so: its badge reads SELL - the
# sentence's own verb - and the words it sells ("the steel"). No numeral, so no document owes one (the B3 rule).
SELL_PLATE = REPO / ("content/video_engine/projects/systems-and-blowups/review/claims/"
                     "steel-and-paper-plates-wave-3/objects/world-sell-ticket-v1.png")
SELL_CROP = (250, 226, 712, 562)              # w, h, x, y - the form's face, inside its edges, clear of the stamp
SELL_ASPECT = round(SELL_CROP[1] / SELL_CROP[0], 4)
SELL_CARD = "dock-h-sell-ticket"
# THE WORD IS STAMPED ON THE TICKET (the parent on T18's tiles, 2026-09-23: "it reads as a blank ruled pad with a tiny
# 'ORDER SELL the steel' badge in its corner. The whole point of the beat is the word SELL ... the SELL must be the
# largest thing on the card while it's read"). The 9-26 px badge is GONE; the card IS the form's face with SELL stamped
# across its centre as a rubber-stamp impression - a ruled border, the word, a slight tilt, the ink's own grain -
# in the brand's NEGATIVE ink (`channel-assets/money-physics/brand-tokens.json` "coral" #ED6A4A, "negative / alarm":
# the accent sunflower vanishes on cream paper). Composed by the door at build (`_sell_ticket_card`, deterministic:
# a fixed grain seed), from the plate crop and the repo's own Inter (Black). MEASURED: the word spans SELL_SPAN of
# the card, so at the 0.30 read (576 px) its cap height is ~150 px and parked at 0.20 ~100 px - never under 72.
SELL_SCALE = 4                                 # the 250 px crop is drawn at 4x, so the stamp is not upscaled type
SELL_FONT = REPO / "content/video_engine/src/assets/fonts/Inter-Variable.ttf"
SELL_INK = (0xED, 0x6A, 0x4A)                  # brand-tokens.json color.coral = color.negative
SELL_SPAN = 0.66                               # the word's width over the card's
SELL_TILT = -7.0                               # degrees: a hand stamp lands a little off-square (the stamp species' own rest)
SELL_INK_ALPHA = 0.88
SELL_GRAIN_SEED = 1845
# THE TICKET'S ROOM, measured on both pages it stands over (T17's tile at 88.50 s; T15b's divergence at 59-63 s): on the
# share-of-GDP page the title ends at x 0.57 and the end tag "11.51%" at x 0.64 (y 0.25-0.28); on the divergence page,
# memory held, the end tags start at y 0.345 and the upper right x 0.55-0.97, y 0.07-0.36 is empty (the chip and the
# flow stood there). So the ticket lands at x 0.74-0.89, y 0.07-0.30 - right of every tag, above the divergence's end
# tags, and over nobody's ink on either page. It is a blank form: the card is read at a glance, and its badge carries
# the word; no chart is ever read at this size (the operator on T15, E99 s71). MEASURED on draft 4: with memory held the
# divergence's three lines and their tags sit at y 0.50-0.75, so the whole upper band is empty and the parked ticket
# takes 0.20 of the stage (x 0.72-0.92, y 0.07-0.45) - at 0.15 its SELL pill read at 9 px.
TICKET_ROOM = {"centre": True, "centre_w": 0.20, "centre_x": 0.82, "centre_y": 0.26}

# ROW 11 (P69 T19, re-cut by the parent's read 2026-09-23): ONE SLOT, THREE RECORDS (E99 s80) - three quotes, one box,
# on ONE world of their own. EVERY ONE IS READ AT THE READING SIZE: no card of words or of a chart is read at card size
# (the operator on T15, E99 s71). The parent on T19's tiles: after the divergence unwound, "a bare chart skeleton (ticks,
# dates, grid) sits behind Karp, Uber and the COO for ~20 s. It reads as a broken chart. The records need a clean
# ground." So the records stand on a PLATE (MEMO_PLATE, below): no axis under any card, and the slot is centred in the
# plate's free box above the anchored caption strip (y 878). The two document cards at 0.70 (a 0.4545 card draws its
# picture plus ~31 px of frame: 1344 x 642 -> y 145-787), the Uber chart at 0.90 (1728 x 622, its labels ~28-44 px).
RECORD_SLOT = {"centre": True, "centre_x": 0.365, "centre_y": 0.43}
RECORD_W, UBER_W = 0.64, 0.90
COO_W = RECORD_W
UBER_SLOT = dict(RECORD_SLOT, centre_x=0.5)
# THE DESK'S LIFE (M05 / M16, T19b draft 1: the plate row FAILed both - "6.8s with no visual event at 2:00", gaps 1:47+6.7s,
# 1:56+4.4s, 2:00+6.8s. A record's typing and a PNG card's hold earn no event on a picture plate, and a live dock sends the
# caption to the anchored strip, which a plate row is not credited for). The desk's own mug breathes STEAM (still life,
# E49; E99 s38 "plate life = the ambient lane") - so the two DOCUMENTS stand in the slot's left 0.64 (x 0.045-0.685) and
# the mug keeps the room right of them: its rim MEASURED on the bare plate at 106.40 s (`p69t19b/mug-grid.png`) at x
# 0.72-0.83, y 0.35-0.40. The Uber CHART takes the slot's whole width (a chart is never read small) and covers the mug,
# so the steam runs only where it is SEEN - never across the Uber window, whose life is its own three badges, each a
# figure printed on the card (B3), springing on the compiler's badge clock through "burned their entire annual AI budget".
MUG_STEAM = {"kind": "region", "x0": 0.73, "y0": 0.35, "x1": 0.83, "y1": 0.39}
# (1) KARP - a RECORD dock (CAPABILITIES:19, live type on paper): the transcript types on the narrator's words and the
# highlighter lands on "paying for tokens that create no value" AS THE NARRATOR SAYS IT (`D.record_words`). The words,
# header, kicker, attribution and source line are the record's own, copied from build-f's payload
# (`build-f/evidence-dock.json`, `ev-doc-karp`) and the object `evidence/objects/ev-doc-karp.png` (the same text).
KARP_CARD = "dock-h-karp-record"
KARP_QUOTE = ("“Something has gone completely wrong. Every single enterprise in this country — these people "
              "are livid. They are paying for tokens that create no value.”")
KARP_HL = ("paying", "for", "tokens", "that", "create", "no", "value.”")
KARP_SYNC = {"paying": "paying", "for": "for", "tokens": "tokens", "that": "that", "create": "create", "no": "no",
             "value.”": "value"}      # the stroke lands per word on the narrator's own (the take's "value,")
KARP_ANCHOR = "paying for tokens"
KARP_TYPE_LEAD_S = 0.4   # the type starts this far after the throw - the eighteen words before the phrase (0.1 s each)
#                          finish by the narrator's "paying"
KARP_ASPECT = 0.4545     # the object's own page, 2112 x 960 - the record paper is drawn at the document's proportion
KARP_RECORD = {"hdr": ["CNBC · Squawk Box", "1 July 2026"], "kicker": "Palantir CEO Alex Karp, on how AI is sold:",
               "attr": "Alex Karp, Chief Executive Officer, Palantir Technologies",
               "src": "Transcript — CNBC Squawk Box, 1 July 2026 · PLTR closed +8–9% that session"}
# (2) UBER - a PNG CARD (BODY_DEPARTURES row 11: the object has no series). IT IS A CHART - the adoption dumbbell 32% ->
# 84% with the budget line in its source ("Uber exhausted its full-year 2026 AI budget by April") - so it is never read
# small: it takes the slot at 0.90 of the stage, the widest the plate's free box holds (its labels ~28-44 px on 1920).
# No series exists on disk (`evidence/objects` has the PNG only), so there is no page to render instead. Its badge says
# the sentence's claim in the document's own words ("April", "2026" are on the card; B3); build-f's "4 months" is the
# script's arithmetic, not the document's, and is not carried.
UBER_CARD = "dock-h-uber-adoption"
UBER_PNG = OBJECTS / "ev-uber-adoption-v1.png"
UBER_ASPECT = 0.36       # the PNG's 0.303 plus its badge rail under it (the ticket's rail measured ~0.2 of its card)
# (3) THE COO - a PNG CARD (BODY_DEPARTURES row 11: `ev-doc-macdonald` has no record payload); the anchored caption
# strip carries the narrator's words under it. The document is the Verge interview's quote with its own highlighter.
COO_CARD = "dock-h-coo-line"
COO_PNG = OBJECTS / "ev-doc-macdonald.png"
COO_ASPECT = 0.4545      # 2112 x 960

# ROW 12 (P69 T20): THE THREE MANIAS, A TABLE READ AT FULL WIDTH. `ev-three-manias` is a PNG only - a 4x3 comparison TABLE
# (BODY_DEPARTURES row 12: a card, not a page). Whole, at 2112 x 1140 (0.54), a centred card is capped by CENTRE_MAX_H at
# 626 px tall - 1160 wide, its cells at ~16 px (7 phone css): a table read small, the fault the operator named on T15
# (E99 s71). So the card is COMPOSED from the object's own pixel bands (`_manias_card`, nothing redrawn, nothing
# retyped): the title, the column heads and their rule, the three rows the sentence turns on ("What the market priced",
# "What actually arrived", "How the paper ended") and the source line. MEASURED on the PNG (rules at y 372-375, 519,
# 665, 810, 1040). CUT: the subtitle and the "Capital committed" row - its "~7% of US GDP" / "~8% of US GDP per Bravos
# Research" are the capital-to-GDP measures row 9 keeps off screen (BODY_DEPARTURES row 9, the parent's 11.51%-vs-"eight"
# flag), and a row the sentence does not read is height the table's cells cannot spare. The result reads at ~0.76 of
# the stage, its cells ~24 px. THE PEAK-TO-TROUGH MOVE (T14's departure: "a callout on its own cell"): no callout can
# mark a still card (a callout's inner target is a PRESS card's phrase alone, and E56's ring is a chart's), so the move
# is carried by the card's own red "64%" and by its BADGES, each a phrase printed on the card (B3), springing on the
# compiler's badge clock (enter + 2.05 s, then every 1.3 s) - "fell 64% / peak to trough" lands on "trough".
MANIAS_CARD = "dock-h-three-manias"
MANIAS_PNG = OBJECTS / "ev-three-manias.png"
MANIAS_BANDS = ((80, 165), (290, 380), (522, 1000), (1030, 1140))   # title | heads + rule | three rows | source
MANIAS_ASPECT = 0.43     # the composed 2112 x 763 (0.361) plus its two-line badge rail
MANIAS_W = 0.90          # the slot's full width; CENTRE_MAX_H takes it down to what fits (1456 x 626)
# ROW 13 (P69 T21): RESET 1 - THE DIP TO 1849. The world changes from the desk to the steel (E61 `use=reset`): the
# viaduct plate, its life the KEN PUSH ALONE (E99 s84 - the treatment's `;idle=drift;drift=20` is superseded,
# TREATMENT_SUPERSEDED) and the locomotive's own STACK breathing (still life, E49: the train that "ran straight through
# the crash" is running). The anaphora is spoken in caption STAGE mode (no dock on the row, so the caption is the stage
# register, E21 "captions are the motion"); the treatment's "on the plate's quiet zone" HAS NO DOOR - a picture plate
# places cards (`;room=`), never its caption (T15's finding), so the caption stands stage-centred. Named, not faked.
VIADUCT_PLATE = "world-viaduct-train-rain-v1;use=reset"
VIADUCT_KEN = (0.05, -12, 4)   # the push into the train, toward the viaduct's left (the steel), away from the paper
VIADUCT_DIP_WHY = ("the memo desk -> the 1849 viaduct, plate to plate: the pair the dip is FOR (E47, a WORLD change - the "
                   "desk of 2026 quotes to the steel of 1849); refused: the thread (no page mark on either side), the "
                   "edge arrival (two unrelated pictures, not one stage - HF-15 pans inside one), the occluder (none "
                   "declared, HF-17), the melt (E88 melts a chart's ink; the desk carries none), the recast (the "
                   "treatment's own: a page cannot recast into a train - and neither world is a page)")

# ROW 14 (P69 T22): THE YARDSTICK. Dip 3 at the world change (the 1849 viaduct -> the 2026 investment page, E47); the
# tech line climbs through the sentence that defines it to the dot-com peak it names; camera 2 pushes on the 28 as the
# line LANDS there (E51, E99 s76); on "In the 1840s railways" the page recasts to the BREAKTHROUGH bars (E60), the
# railways' half bursting the stated [0, 30] scale. EVERY PAGE FROM HERE ON IS DRAWN IN THE LONG FORM'S PROFILE (E99 s97,
# P69 T8): `;readability=longform`, plain = the `middle` preset - the working default until the operator's pick at
# P69-HG3. End tags shorten full -> badge -> value where they do not fit; the key rail with the full names is T10's
# and NOT BUILT (the notes name it).
LONGFORM = ";readability=longform"
YARD_PAGE = "ev-capital-formation-v1"        # tech's share of ALL US private investment, BEA via FRED, 1970 - 2026 Q2
YARD_BARS = "ev-rail-vs-yardstick-bars-v1"   # PLAUSIBLE, drawn by E99 s93: the railways' ~50 beside today's 28, [0, 30] stated
YARD = _series(YARD_PAGE)
YARD_BARS_OBJ = _series(YARD_BARS)
YARD_NAMES = [s.get("name", "") for s in YARD["series"]]
YARD_TECH = next(i for i, n in enumerate(YARD_NAMES) if n.startswith("COMPUTERS"))     # the yardstick's own line (28%)
YARD_SCALE = next(i for i, n in enumerate(YARD_NAMES) if n.startswith("ALL EQUIPMENT"))  # "(for scale)", 65%
YARD_PEAK = _nearest(YARD, YARD_TECH, YARD["marks"][0]["x"])   # the object's own "dot-com high" mark: 2001 Q1, 23.03
YARD_LAST = _last_index(YARD, YARD_TECH)                        # 2026 Q2, 28.18 - the series' own maximum ("the most")
YARD_23 = YARD["marks"][0]["label"]                             # "23%", the object's own words at that datum
# THE SCALE LINE IS HELD AT NOTHING: "ALL EQUIPMENT + IP (for scale)" ends at 65% and no sentence names it - its end tag
# would be a number on screen the voice never says, and it is not "everything the country invests" (that is 100). The
# page's own 50% railway rule stands from the landing: it IS the yardstick the page is named for.
YARD_OPEN_S = 0.4
YARD_TODAY_S = 0.5      # the last twenty-five years draw on "Today it's", landing on "twenty-eight" (E51's landing)
YARD_FIG_S = 1.4
# CAMERA 2 (E99 s76: only where the sentence names the thing; E51: a push is tied to a landing): the line lands on its
# 2026 Q2 datum and the camera pushes on it through "the most it has ever been", then releases before the recast. The
# zoom is row 1's measured 1.06 (a key pair, not a focus_zoom species - the fixed 1.32 cut the page at 16:9).
# A PUSH IN PLACE CANNOT REACH IT HERE: the long form's title and sub start at x 42 (probe, draft 1 at 181.6 s) and the
# engine resolves the 28 datum at (1168, 609), so a zoom about the datum takes the title's left edge off the stage at
# 1.037 (the compiler refused 1.06 by name, `logs/t22-door2.log`). The datum is therefore LANDED right and down of
# where it stands - `at` (0.6344, 0.5833) = (1218, 630) px - inside the only window that keeps both the page's glyphs
# and its own edges: the title's left edge >= 1194 px / top >= 612 px (else a glyph leaves the stage), and the PAGE's
# left edge <= 1238 px / top <= 645 px (else the ground beyond the page shows - MEASURED on the T22 build at (1260,
# 660): a 22 px cream strip left and 14 px on top at 182.6 s). At (1218, 630) the title keeps ~24 px and the page
# overhangs the stage ~20 / ~15 px.
# THE LOOK IS A POINT, NOT THE DATUM: MEASURED on drafts 2-3, a `datum` look with `at` != look RUNS AWAY - the engine
# resolves the datum on the camera-moved frame each instant, so the look walks with the pan it causes (look 1183 ->
# 1116 px over 1.9 s at a constant 1.06; the title's left edge -7 then -62 px). An engine defect, named for the parent;
# a datum is stable only zoomed in place. So the look is the 28 datum's own REST position, read off the probe at
# 181.6 s (camera identity): (1168, 609) px.
YARD_CAM_ZOOM, YARD_CAM_IN_S, YARD_CAM_OUT_S = 1.06, 1.1, 0.8
YARD_CAM_LOOK = {"kind": "point", "x": 0.6083, "y": 0.5639}
YARD_CAM_AT = [0.6344, 0.5833]
# THE BREAKTHROUGH (E60, CAPABILITIES:90 - `overflow: burst` on the object): the recast lands the two bars at the
# comparator's level (28, the tallest honest bar on the stated [0, 30]), holds, and the railways' bar SHOOTS to 50 while
# the scale rewrites - the frame is not broken, its scale changes to hold the number. The recast opens on "In the
# 1840s" so the burst runs on "railways took roughly half".
YARD_RECAST = 1
YARD_RECAST_S = 1.2
# THE LINE UNWINDS BEFORE THE BARS ARRIVE (row 10's lesson, MEMORY_HOLD): MEASURED on draft 4, the recast's arriving
# "50¢" value label stood ON the tech line at 3:05 (the gate's M34, `logs/t22-gate.log`) - a plain recast draws the
# arriving state over the outgoing ink. The line undraws over "1840s" and is gone 0.1 s before the recast opens.
YARD_UNDRAW_S = 0.8
YARD_DIP_WHY = ("the 1849 viaduct -> the 2026 yardstick page, plate to page (a WORLD change, E47 - the steel of 1849 to "
                "the investment of today); TAKEN the dip, the last resort (E99 s74): this page names no arrival that could "
                "carry it - refused: the snap / throw-then-zoom / throw-then-push (no card is thrown on the viaduct; nothing "
                "on it names the yardstick), object-becomes-chart (the train is not the page's data), the spiral return (a "
                "first page, not a returning one), the mount (E47: a mount lays the page on the picture it grows from - the "
                "yardstick does not belong to 1849's plate), the melt (E88 melts a chart's ink; the plate carries none), "
                "recast / rescale / morph (a plate is not a chart)")
YARD_RECAST_WHY = ("the tech line -> the breakthrough bars, on one board: TAKEN the recast (E64's plain hand-over - one "
                   "measure, one technology's share of a country's investment, in the other form: the line's last datum "
                   "IS the 28 bar); refused: the dip and the cut (no world changes, E47), rescale / extend (the railways' "
                   "50 is not on this series), morph (another frame, not a strip of this one), remake (needs the same "
                   "data whole - the 50 is Britain's), the melt (it would clear the board the 28 stands on)")

# ROW 15 (P69 T23): THE TRIGGER AND THE CONCESSION, on ONE page - the 10-year yield in its two eras - and PROP 1, the
# Fed, STAMPED on the word that names it (E99 s87: a DIRECT match for the word only; bare of paper, E99 s92, its
# cross-hatch resting shadow the engine's own, P69 T6b). The stamp takes the page's biggest room (P69 T5, s88) - the
# engine's fit chooses it, nothing is hard-coded here; its cue is `landing N (stamp, ink)` (A.arrival_mass); it leaves
# WITH the page (R26-219: the dock's exit is the row's end).
# THE PAGE IS v4 (the parent's unblock, 2026-09-23): `ev-tnx-two-eras-v3` keeps its data as two PANELS and a ledger page
# never draws panels (v3 compiled to `dense-line` with 0 series and refused the Fed at 46 px - `logs/t23-door1.log`,
# `t23-door2.log`). v4 holds the SAME values as two ordinary series on a shared "years from each era's start" x axis -
# the dot-com era in teal, the AI era in crimson - with a y label and year ticks. The Fed's 6.5% and Bravos' 5.5% Fed
# tripwire are the page's RULES: E53 s5, "a policy rate is a RULE" - the right form on a yield page, not a unit mix.
TNX_PAGE = "ev-tnx-two-eras-v4"
TNX = _series(TNX_PAGE)
TNX_NAMES = [s.get("name", "") for s in TNX["series"]]
TNX_DOT = next(i for i, n in enumerate(TNX_NAMES) if n.startswith("DOT-COM"))     # teal, 1998-2001, its tag "5.1%"
TNX_AI = next(i for i, n in enumerate(TNX_NAMES) if n.startswith("AI ERA"))       # crimson, 2021-today, its tag "4.7%"
_DOT_PTS = TNX["series"][TNX_DOT]["pts"]
TNX_DOT_PEAK = max(range(len(_DOT_PTS)), key=lambda k: _DOT_PTS[k][1])   # Jan 2000, the era's high - read off the data
TNX_DOT_LAST = _last_index(TNX, TNX_DOT)
TNX_AI_LAST = _last_index(TNX, TNX_AI)
# THE LINE CROSSES BACK ABOVE WHERE ITS BORROWING BEGAN, ON THOSE WORDS: the dot-com yield opens at its first print,
# falls through the 1998 dip and climbs back above that first print during 1999, on to the January 2000 high. The first
# pen draws the dip and most of the recovery (to TNX_DOT_LEG1_X years, still UNDER the first print) while the narrator
# talks about risk charts; the second leg starts on "It dies when" and crosses above the first print as "cross back
# above" is said, landing on its high on "began". Both indices read off the data, never typed.
TNX_DOT_LEG1_X = 1.2
TNX_DOT_LEG1 = _nearest(TNX, TNX_DOT, TNX_DOT_LEG1_X)
assert _DOT_PTS[TNX_DOT_LEG1][1] < _DOT_PTS[0][1] < _DOT_PTS[TNX_DOT_PEAK][1], "the crossing must lie in the second leg"
TNX_OPEN_S = 0.4
# THE PAGE LANDS WITH INK (M31, chart to chart): MEASURED on draft 6 (`logs/t23-gate.log` then), both eras held at
# nothing left the stage with no page ink 195.82-196.02 under the melt - the gate's "empty cream" FAIL. The dot-com
# yield lands on its first prints instead (row 8's RAIL_OPEN_CAP, the first cap as the page lands), a stub of 1998.
TNX_OPEN_CAP = 3
TNX_ROLL_S = 1.5      # the rollover draws on "the internet trade rolled over", landing on "over"
TNX_AI_S = 1.9        # the AI era draws on "for this cycle", landing as "above five" is said - under their 5.5% rule
# THE FIGURES THE PAGE DOES NOT CARRY TWICE (M28): the page's own rules already write the Fed's 6.5% ("Fed funds peak,
# 2000 - 6.5%") and their 5.5% ("their tripwire - 5.5%"), so neither is written again and NO RING lands on the yield
# line at 6.5 - the sentence's 6.5 is the FED FUNDS rate, and the 10-year's own January 2000 high (6.7) is a different
# measure (E99 s94: read a figure on the basis its sentence states). The BoE's 6% has no rule and no series on a US
# page: it is SAID, not drawn (below) - Bravos Research, accepted as a primary source for this format
# (docs/content-video-engine/briefs/ANSWER-BRAVOS-HYPE-CYCLE.md:525 "BoE 6% trigger ... attributed", :532).
# NO NOTE: MEASURED on draft 4 (`scratchpad/p69t23/notes/notes.log`), both `note`s
# were placed by the engine's "no free column" fallback UNDER the source line - y 1142 and 1222 px on a 1080 px stage,
# off the frame for their whole life (the right column is under the engine's 22% floor once the long-form end tags
# take it; `scene-evidence-engine.mjs` the NOTES block). No row option moves a note, so the hand writes each claim as
# the title instead (row 1's own verdict retitles). THE TITLE STATES WHAT THIS PAGE SHOWS (the parent's frame read,
# 2026-09-23): a BoE title over a US page with no 6% line sent the eye looking for a rule that is not there, so the
# title holds the page's own name through the BoE sentence and is rewritten on "The Fed at six and a half" to the
# sentence's claim, read off the page's own rule (6.5%, 2000) - no new figure. The BoE's 6% is therefore SAID and not
# drawn (no note: a note lands off the stage, above). The concession is rewritten on "Put my agreement".
# Engine gap, named for the parent: a note on a full-stage page has nowhere on the stage to go.
TNX_FED_TITLE = "The Fed at 6.5% in 2000: the internet trade rolled over"
TNX_AGREE_TITLE = "Agreed: the cycle is real, and so is the threshold"
TNX_TITLE_S = 2.0
# CUT (unsourced, named): "My own tripwire is stricter than theirs" - the script gives no figure for it, so no rule, no
# note and no number is drawn for the narrator's own tripwire; and "don't try to call the top" is not written (a quote
# with no line in the sourcing table, ANSWER-BRAVOS-HYPE-CYCLE.md:520-530).
FED_PROP = "prop-federal-reserve-building-v1"
FED_PROP_FILE = REPO / "content/video_engine/assets/props/cutouts" / (FED_PROP + ".png")
FED_OPTS = {"prop": True, "arrive": "stamp"}   # mass unset: a stamp lands at `ink` (the engine's stampXf default)
# THE STAMP WAITS ON ONE MEASUREMENT (P69 T23, 2026-09-23 - NOT in this slice's write set). The v4 page is not in the
# page-boxes fixture (`content/video_engine/assets/page-boxes.v1.json`), so the compiler fits the Fed against the
# ESTIMATED boxes: the whole plot solid (no `data_mask`) and the end-tag COLUMN solid from the plot's top to its bottom
# (x 1329-1880, y 250-808 - `ledger_page._landscape_full_boxes`; the fixture never measures tags). The largest mark left
# is 61 px, under the 120 px floor, and the door FAILs by name (`build-h/logs/t23-door3.log`). MEASURED IN A SCRATCH
# COPY of the fixture (`scratchpad/p69t23/fitsim/`), the same fit takes the plot's lower-right EMPTY room - mark 186 x
# 171 painted px at centre (1136, 672). The unblock, the parent's: `python content/video_engine/scripts/
# measure_page_boxes.py --write --project content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h`
# (it reads THIS build's compiled timeline, which is why the row is built first with the stamp withheld), then
# FED_STAMPED = True and the door re-run. Withheld, the row compiles everything else and the build notes say so.
# TWO MORE BLOCKERS, both the engine's (BUILD-NOTES-H.md section 14): (a) the right margin level with the rules (the
# parent's placement) is refused at every authored centre - the end-tag column above is kept even on a measured page
# (`ledger_page.page_boxes`); (b) a dock prop is embedded as JPEG (`build_scene_timeline_f.dock_uri` -> `data_uri`'s
# RGB convert), so the Fed paints on a BLACK SQUARE with the hatch cast by the square - a card, which E99 s92 forbids.
FED_STAMPED = False
TNX_MELT_S = 1.0     # the yardstick bars melt over "Bravos' sharpest" and the yields' board is there on "line is about"
TNX_MELT_LEAD_S = 0.5   # ... opened in the breath before the sentence, so the melt's empty instant falls under no word
TNX_MELT_WHY = ("the breakthrough bars -> the 10-year yield in two eras, page to page: TAKEN the melt's throw (E88) - the "
                "bars ball up and are thrown off, the yields draw on the same board as the sentence turns to the trigger; "
                "refused: the dip (two pages are one kind of world, E47 - no world change), a recast (a third state would "
                "be the yardstick page's, and the stamp is fitted to its page's OWN room, P69 T5, which must be the "
                "yields'; a different argument is a different page, E58), rescale / extend (not the same series), morph "
                "(another frame, not a strip of this one), melt:splash:chart and melt:morph (the yields would arrive "
                "built - every page builds on screen, E99 s67)")

DOCK_META = [
    {"asset": CERT_CARD, "title": "An 1845 railway certificate",
     "source": "Money Physics - plate world-certificate-wall-v1", "species": "deck", "badges": []},
    {"asset": BRAVOS_CARD, "title": HOOK_CARD_TITLE,
     "source": "Yahoo Finance - pairing after Bravos Research", "species": "chart", "badges": []},
    {"asset": SELL_CARD, "title": "A sell ticket",
     "source": "Money Physics - plate world-sell-ticket-v1", "species": "deck",
     "badges": []},   # the word is ON the card now (_sell_ticket_card); the badge was a 9-26 px pill
    {"asset": KARP_CARD, "title": "Alex Karp, Palantir", "source": "CNBC · Squawk Box, 1 July 2026",
     "species": "record", "badges": []},     # `record` is filled at build from the take (karp_record)
    {"asset": UBER_CARD, "title": "Uber's AI budget", "source": "The Information, April 2026", "species": "chart",
     "badges": [{"label": "ANNUAL AI BUDGET", "value": "spent by April", "tag": "2026"},
                {"label": "ADOPTION", "value": "32% \u2192 84%", "tag": "Uber engineering"},
                {"label": "PER ENGINEER", "value": "$500\u2013$2,000", "tag": "per month"}]},
    {"asset": COO_CARD, "title": "Andrew Macdonald, Uber COO", "source": "The Verge, May 2026", "species": "deck",
     "badges": []},
    {"asset": MANIAS_CARD, "title": "Three manias, measured the same way",
     "source": "Campbell & Turner railway index; Bravos Research", "species": "deck",
     "badges": [{"label": "THE MARKET PRICED", "value": "returns inside three years", "tag": "1840s"},
                {"label": "THE PAPER", "value": "fell 64%", "tag": "peak to trough", "accent": "neg"},
                {"label": "THE RETURNS", "value": "took twenty years", "tag": "1840s railways"},
                {"label": "2024\u201326 AI BUILD", "value": "still open", "tag": "AI build"}]},
    {"asset": FED_PROP, "title": "The Federal Reserve", "source": "Money Physics - prop cutout " + FED_PROP,
     "species": "prop", "badges": []},     # E99 s87 / s92: art added to the world, bare of paper - no rail, no badge
]


def _manias_card() -> Path:
    """The three-manias TABLE card: MANIAS_BANDS of the object's own PNG stacked in order, nothing redrawn. Written to
    <build>/docks/<MANIAS_CARD>.png and registered."""
    from PIL import Image
    src = Image.open(MANIAS_PNG).convert("RGB")
    bands = [src.crop((0, a, src.width, b)) for a, b in MANIAS_BANDS]
    out_im = Image.new("RGB", (src.width, sum(b.height for b in bands)), src.getpixel((5, 5)))
    y = 0
    for b in bands:
        out_im.paste(b, (0, y))
        y += b.height
    out = BUILD / "docks" / (MANIAS_CARD + ".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    out_im.save(out)
    D.register(MANIAS_CARD, out)
    return out


def _sell_ticket_card() -> Path:
    """The ticket card: the order form's face (SELL_CROP of SELL_PLATE) at SELL_SCALE, SELL stamped across its centre in
    the negative ink with a ruled border and the stamp's grain. Written to <build>/docks/<SELL_CARD>.png and registered."""
    import random
    from PIL import Image, ImageDraw, ImageFont
    w, h, x, y = SELL_CROP
    face = Image.open(SELL_PLATE).convert("RGB").crop((x, y, x + w, y + h))
    face = face.resize((w * SELL_SCALE, h * SELL_SCALE), Image.LANCZOS)
    fw, fh = face.size
    font = ImageFont.truetype(str(SELL_FONT), 100)
    try:
        font.set_variation_by_name("Black")
    except (OSError, ValueError):
        pass
    probe = font.getbbox("SELL")
    size = round(100 * SELL_SPAN * fw / (probe[2] - probe[0]))
    font = font.font_variant(size=size)
    try:
        font.set_variation_by_name("Black")
    except (OSError, ValueError):
        pass
    l, t, r, b = font.getbbox("SELL")
    pad, rule = round(0.16 * (b - t)), max(6, round(0.07 * (b - t)))
    mw, mh = (r - l) + 2 * (pad + rule), (b - t) + 2 * (pad + rule)
    mask = Image.new("L", (mw, mh), 0)
    dr = ImageDraw.Draw(mask)
    dr.rectangle([rule // 2, rule // 2, mw - 1 - rule // 2, mh - 1 - rule // 2], outline=255, width=rule)
    dr.text((pad + rule - l, pad + rule - t), "SELL", font=font, fill=255)
    rnd = random.Random(SELL_GRAIN_SEED)          # the rubber's grain: the ink misses in small flecks
    for _ in range(mw * mh // 170):
        gx, gy, gr = rnd.randrange(mw), rnd.randrange(mh), rnd.choice((1, 1, 2, 3))
        dr.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=0)
    mask = mask.rotate(SELL_TILT, resample=Image.BICUBIC, expand=True)
    mask = mask.point(lambda v: round(v * SELL_INK_ALPHA))
    full = Image.new("L", (fw, fh), 0)
    full.paste(mask, ((fw - mask.width) // 2, (fh - mask.height) // 2))
    face = Image.composite(Image.new("RGB", (fw, fh), SELL_INK), face, full)
    out = BUILD / "docks" / (SELL_CARD + ".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    face.save(out)
    D.register(SELL_CARD, out)
    return out


def karp_record(ws: list, t_karp: float) -> None:
    """The Karp record's payload: a placeholder asset (a record is live type, never an image) and the META's `record`
    filled from the take's own word times (the Tokyo short's `record_dock`, CAPABILITIES:92)."""
    D.record_asset(KARP_CARD, BUILD)
    typed, hl, end = D.record_words(KARP_QUOTE, round(t_karp + KARP_TYPE_LEAD_S, 2), ws, KARP_ANCHOR, KARP_SYNC, KARP_HL)
    D.meta_set(DOCK_META, KARP_CARD, "record", dict(KARP_RECORD, words=typed, hl=hl, end=end))

# ---------------------------------------------------------------- THE PAGE ROWS

IDLE_LIVE = ";idle=live"                      # E49 on every page row: the board, its titles, labels and figures live
PAGE_EXIT_CUT = ":cut"                        # the page never retracts here - the DIP is the world change (E47)
OPEN_ENTER = "axes"                           # E73: the page lands with its ground, its ruled line, its title and its AXES
LAYER_RECAST = 1                              # the `;then=` state index row 4's recast moves to
GDP_RECAST = 1                                # ... and row 9's
DIV_RECAST = 2                                # ... and row 10's: the rail page's THIRD state (STATE_MAX 3), the divergence


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
    """Rows 8-9's world: the railway index on its axes, entered by row 8's melt (P69 T16), and its ONE other state -
    the share-of-GDP page it RECASTS to on "the internet" (P69 T17, `;then=`, GDP_RECAST).

    THE GDP PAGE RINGS ITS OWN NUMBER (P69 T17 / BODY_DEPARTURES row 9, which supersede the 2026-09-18 read
    below): it is shown, it states what it measures in its own title and sub, and the one mark on it is its own
    Q2-2000 peak (11.54 %), rung under "then the tower came down" - never a 7 % tick or an 8 % datum, and nothing
    rung under the seven / eight words. The 2026-09-18 read, kept for the record: THE SHARE-OF-GDP PAGE IS NOT
    SHOWN UNDER THOSE WORDS (the parent's read, 2026-09-18). The dossier
    routes "the internet crossed seven percent of GDP ... AI spending just crossed eight" to the PIMCO
    equipment-and-software series (`evidence/EVIDENCE-DOSSIER.md:120`) and that series IS
    `ev-equip-ipp-gdp-v1` - but what it measures is equipment + IP investment as a share of GDP:
    11.539 % at the Q2-2000 peak, 11.505 % today (the dossier's own correction, `:250`). A chart whose
    numbers read 11.5 while the sentence says seven and eight is a different measure on screen than in
    the words, so it is not shown: the railway page holds, and the object the sentence actually needs -
    AI / tech spending as a share of GDP on Bravos' math - IS MISSING FROM DISK. HG3's row.

    ROW 10 (P69 T18): the THIRD state (DIV_RECAST, STATE_MAX 3) - the verified divergence page the head-fake reads off
    ("Chipmakers doubling while their customers sit flat at the index"), recast UNDER the thrown sell ticket (E64)."""
    return ("ledger:%s:line:%d:right:%s%s%s;then=%s:line;then=%s:line"
            % (RAIL_PAGE, RAIL_TROUGH, OPEN_ENTER, PAGE_EXIT_CUT, IDLE_LIVE, GDP_PAGE, LAYER_PAGE))



def page_snap() -> str:
    """Row 7's second world (P69 T15b): THEIR chart, pushed to the stage out of the card thrown on their name.

    `camera=<dock>` (page_enter:camera, THROW-THEN-PUSH - the `card-becomes-the-chart` family, E99 s71): the card lands
    on the studio, the camera zooms the studio and the card together until the card fills the stage, and the page
    shows at the match - the arrival IS the transition, so the row's exit is `cut`. NOT the snap (throw-then-zoom,
    `snap=`): MEASURED on this build (`p69t15b/seq-play`), a 16:9 full-stage page grown by the snap lands OFFSET
    (+137, +100 px, cream showing top-left) and stays there for the whole row when the player plays forward frame by
    frame (every seek from 57.38 s on), while a cold seek paints it at identity - a seek-purity defect in the engine's
    snap (`paintLedger`'s `snapBoard`, scene-evidence-engine.mjs:13286), outside this door; the camera arrival
    settles at identity both ways (`p69t15b/seq-cam`). The
    page is the verified divergence object on the hook's own domain, the memory line held at nothing (the card is
    that object with memory dropped), live (E49)."""
    return ("ledger:%s:line:%d:right:camera=%s:cut%s%s%s"
            % (LAYER_PAGE, DIV_LAST, BRAVOS_CARD, IDLE_LIVE, PAGE_DOMAIN % (HOOK_YMIN, HOOK_YMAX), SNAP_CARD))


def page_yard() -> str:
    """Row 14's world (P69 T22): the yardstick page - tech's share of all US private investment - on its axes (E73),
    live (E49), in the long form's profile (E99 s97), and its ONE other state, the breakthrough bars it RECASTS to on
    "railways took roughly half" (`;then=`, YARD_RECAST)."""
    return ("ledger:%s:line:%d:right:%s%s%s%s;then=%s:bars"
            % (YARD_PAGE, YARD_LAST, OPEN_ENTER, PAGE_EXIT_CUT, IDLE_LIVE, LONGFORM, YARD_BARS))


def page_tnx() -> str:
    """Row 15's world (P69 T23): the 10-year yield in its two eras, on its axes (E73), live (E49), in the long form's
    profile (E99 s97, the middle preset) - the page PROP 1 is stamped onto. One state: no recast."""
    return ("ledger:%s:line:%d:right:%s%s%s%s"
            % (TNX_PAGE, TNX_DOT_LAST, OPEN_ENTER, PAGE_EXIT_CUT, IDLE_LIVE, LONGFORM))

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
# "and it isn't Nvidia" - THE CHIP, landing on its word and CROSSED OUT on the next (species/chip.mjs's own use:
# a sourced glyph, a label, the claim retracted). It stays the SVG chip (the cpu glyph on its card): no
# `form: stamp` - P69-HG1 decides future chips (P69 T15). The cross is what the sentence does to it.
NVIDIA_CHIP = {"kind": "chip", "icon": "cpu", "label": "NVIDIA", "idle": "breath"}   # E49: a held chip breathes
CHIP_CROSS_S = 1.2
# THE CARD CAN STAND ON A PICTURE PLATE (P69 T14 (7)): R26-221 `plate_dock_place` (build_scene_timeline_f.py:6053,
# called at :7609 when `place is None`) places a card from the row's own `centre` / `centre_x` / `centre_y` /
# `centre_w` (+ `card_aspect`), and a card never lands on the host (the parent's ruling, 2026-09-18).
HOST_CARD_DOOR = ("plate_dock_place places a card on a picture plate from the row's centre fields or the "
                  "plate's ;room= (R26-221, build_scene_timeline_f.py:6053, used at :7609)")
# ROW 7, CORRECTED (P69 T15b, 2026-09-23). The operator on T15's tiles: "Those charts still seem tough to read to me."
# T15 threw their chart card, read it at a third of the frame (6-8 px labels) and PUT IT DOWN on the desk - the fault
# E99 s71 names (OPERATOR-RULINGS.md:3260): "if we are throwing a full-screen card then we should throw-then-zoom or
# throw-then-push to make it full screen ... What you did ... left it floating over the world plate". So the card
# BECOMES THE PAGE: `recipe:card-becomes-the-chart` (proven, count 2; effects/recipes/card-becomes-the-chart.json) -
# the card thrown with a paper mass onto the studio, and one second later the ledger page grows out of that card's
# own rectangle to the stage. The engine carries two arrivals for it (authoring/shapes.py `_arrival_name`): the snap
# (`snap=`, throw-then-zoom) and the camera (`camera=`, throw-then-push); this row takes the PUSH - see page_snap for the
# snap's measured defect. No chart is ever read at card size: the card is on the ground for its landing beat only,
# and the chart is READ at the page's own type.
BRAVOS_READ = {"centre_w": 0.34, "centre_x": 0.26, "centre_y": 0.25}   # the dark LEFT monitor - never Mike (x 0.60-0.76)
CARD_LEAD_S = 1.0     # the card lands, then the page snaps up out of it one second after the throw (the recipe's
                      # own offsets, +0.82 -> +1.82; japan-tariff-trick build_short.py CARD_LEAD_S)
# THE PAGE IT BECOMES is the VERIFIED divergence page (the card's source, `_hook_object`, is that object with the
# memory series dropped; the compiler reads a page only from `evidence/objects/`, which is read-only here) - on the
# hook's own domain, with the MEMORY LINE HELD AT NOTHING, so the page carries exactly the card's three lines. It is
# a returning page and "a returning page arrives retitled" (SPECIES_WHEN retitle): the hand writes the card's own
# title over the object's as the snap lands, so the card and the page say one thing.
SNAP_RETITLE_S = 1.2
# THE PAGE'S LIFE (E50): it arrives BUILT (the snap), so its clock starts on arrival and 6 s is its floor; it holds to
# the rehook, where it melts (row 8). The throw-then-zoom is the standard for a thrown full-page card (E99 s71).
# THE STUDIO FIRST NEEDS ITS SIX SECONDS (M44, `gate_motion_density.PLATE_MIN_S`: a world plate under 6 s carrying a
# dock FAILS). From "The three questions read" to the snap is 3.7 s, so the host window opens on the sentence before
# it - the promise, "By the end you'll run it on your own top five", said by the host to camera - and the slate keeps
# the three questions to the end of the sentence that sorts them (7.4 s; the agenda's three rows all land by 45.62).
HOST_FROM_PHRASE = "By the end"
# ... AND ON THE PAGE, THE REST OF THE SENTENCE, AT FULL SIZE: the chip lands on "Nvidia" in the page's own empty room
# and is crossed as the sentence turns, and the flow `capital -> value` draws on "capital arriving faster" beside it -
# the chart is never parked small (the operator: "Those charts still seem tough to read to me"). MEASURED on the
# T15b drafts (`p69t15b/draft1`, `cold/tile-58.90`): at full size the end tags run y 0.40 (semis) and 0.58-0.62
# (S&P / mega-cap) from x 0.58 to the right edge, the sub ends at x 0.48, and the semis peak stands at (0.47, 0.25) -
# so the page's empty room is the upper right, x 0.55-0.97, y 0.07-0.36. A chip at (0.80, 0.60) landed ON
# "+21% S&P 500", and at (0.84, 0.25) its NVIDIA label dropped onto "+105% SEMICONDUCTOR STOCKS"; a 0.64 park that
# made room for the flow printed the chart's labels at 8.3-9.1 phone px (the probe's M25 INFO) - so there is no park.
CHIP_ON_PAGE = {"kind": "point", "x": 0.91, "y": 0.13}
FLOW_ON_PAGE = {"kind": "region", "x0": 0.60, "y0": 0.06, "x1": 0.85, "y1": 0.32}   # draft3: at x0 0.55 / y1 0.35 the
# dashed frame touched the semis line's last prints and sat on its tag's top edge (63.75)
SNAP_CARD = ";card=no"   # the arriving page is a PAGE, full stage like every other page in the cut - never a card at
                         # full size (the snap's default; read on draft1 at 57.3-63.2)
# THE DIP INTO THE STUDIO (row 7), and what it refused - E99 s74: a cut or a dip is the last resort and its why names
# the transform refused. The boundary is plate -> plate (the three-notch slate -> the studio), the pair the dip is FOR
# (E47), and every transform the kit carries for that pair is refused by name (`authoring/shapes.py`'s plate->plate
# chain): no mark threads across (`;thread=` carries a PAGE's mark, and neither world is a page); the studio does not
# arrive from the slate's frame edge (two unrelated photographs, one stage each - HF-15 is a pan inside one stage);
# the slate declares no foreground occluder (HF-17); and the melt is a CHART's ink (E88) - the slate carries an
# agenda, not a chart, so there is nothing to melt.
HOST_DIP_WHY = ("slate -> studio is plate to plate, the pair the dip is FOR (E47); refused: the thread (no page mark "
                "on either side), the edge arrival (two photographs, not one stage), the occluder (none declared), "
                "the melt (E88 melts a chart's ink; the slate carries an agenda)")
# ROW 7's SECOND BOUNDARY (P69 T15b): studio -> their chart, carried by the ARRIVAL. The card thrown on "Bravos Research"
# grows to the stage (throw-then-zoom), so no dip and no cut is owed: the snap IS the transition (E99 s74 Apply 1;
# authoring/shapes.py plate->page: "the page arrives out of the plate on its own clock, so the arrival IS the
# transition and no dip is owed").
SNAP_WHY = ("TAKEN throw-then-push (`camera=`, the card-becomes-the-chart family): the card thrown on their name is "
            "pushed to the stage and the page shows at the match, so the arrival IS the transition - no dip, no cut "
            "owed (E99 s71, s74); the snap (throw-then-zoom) refused: on this build it lands the 16:9 page offset in "
            "forward play (an engine seek-purity defect, named in the notes)")
# ROW 8, THE REHOOK (P69 T16, re-cut by T15b). Row 7 now ENDS ON A PAGE (their chart), so the boundary into the railway
# index is page -> page, and the treatment's "dip 1" (studio -> page) no longer exists: E47 refuses a dip between two
# pages ("two pages are one kind of world, and the dip means the WORLD changed" - authoring/shapes.py page->page). The
# transform TAKEN is the melt's throw (E88, CAPABILITIES:38): their pairing's ink sags, balls up in its own weight and
# is thrown off, and the railway index draws on the SAME board - capital that fast, leaving a paper trail. Refused by
# name for this pair (E99 s74 Apply 1, the page->page chain):
#  - recast (E64): their pairing and the 1840s index share no data - a different argument is a different page (E58);
#  - rescale / extend: the same series at another scale / more of it - the railway index is neither;
#  - morph (E58's table): a filled strip of the SAME frame into another series; this is another frame, another century;
#  - melt:splash:chart would make the index arrive BUILT out of the splatter, and melt:morph would land its whole
#    area at once out of the ball - both refuse the climb, and every page BUILDS on screen (E99 s67 (2));
#  - the dip: two pages are one kind of world (E47).
RAIL_EXIT = "melt:throw:%g"
RAIL_MELT_S = 1.0     # the melt runs over "But capital that fast" and the index draws on "leaves a paper trail"
RAIL_MELT_WHY = ("their chart -> the railway index, page to page: TAKEN the melt's throw (E88) - their pairing's ink "
                 "balls up and is thrown off, the index draws on the same board; refused: the dip (two pages are one "
                 "kind of world, E47), recast (no shared data - a different argument, E58/E64), rescale / extend (not "
                 "the same series), morph (another frame, not a strip of this one), melt:splash:chart and melt:morph "
                 "(the index would arrive built / whole - every page builds on screen, E99 s67)")
# ROW 10, THE HEAD-FAKE (P69 T18). The share-of-GDP line's last data mark lands at "eight." (88.5 s); the page RECASTS
# to the divergence on "catches up with it" (93.3 s) - the same board, the plain hand-over of row 9 (E58 / E64), under
# the ticket thrown on "the obvious move". The recast is 1.2 s and the arriving page draws line by line (`build=lines`,
# 1.2 s each, memory held), so the chips draw ON "Chipmakers doubling" and mega-cap and the S&P on "their customers sit
# flat at the index" - MEASURED on draft 4, a recast on "Chipmakers" itself (2.0 s) drew nothing until "sit flat" was
# over and the spread bled onto an empty plot. The GDP page's deployed life is 4.9 s (E50's 6-8 s is an average, and a
# floor only for a page that arrives built). What the transform took and refused (E99 s74):
DIV_RECAST_S = 1.2
DIV_RECAST_WHY = ("GDP share -> the divergence, on one board under a live card: TAKEN the recast (E64 - a recast under "
                  "a card is the treatment's own row); refused: the melt (it would take the ticket's board with it, and "
                  "the ticket stands over the hand-over), the dip and the cut (no world changes - E47), rescale / extend "
                  "(another series, not more of this one), morph (a strip of this frame into another series), remake "
                  "(the whole chart changing on one clock needs shared data - these share none)")
# the title the recast writes is the SENTENCE'S (the object's own reads the four lines, and memory is held): a
# returning page arrives retitled (SPECIES_WHEN retitle), and a retitle on the recast's own word is dropped (R26-219 c)
HEADFAKE_TITLE = "Chipmakers doubling. Customers flat."
# NO SPREAD ON THIS STATE: the gap between mega-cap and the chips was authored to bleed on "textbook profit-taking", and
# it painted nothing (draft 5, `p69t18/spread/` 98.20-100.10). On a page with chart STATES "a bracket or spread is built
# on the page's own geometry and waits while a derived state stands" (scene-evidence-engine.mjs:11498-11501) - state 0
# is the railway index, one series, so `from: 2` has no line and the spread is dropped. The page's own end tags write
# +105% and +21% as the lines land. Owner if it is wanted: the engine (a spread that reads the ACTIVE state's lines).
# THE MEMORY LINE IS HELD, AND A build_to CANNOT HOLD IT HERE: a cap is per SERIES INDEX across the page's states, series
# 0's cap is the GDP line's last datum (row 9), and a build_to only carries a line FORWARD - MEASURED on draft 1
# (`p69t18/draft1` 96.90): a `build_to` to datum 0 at the recast left memory drawn whole, its "+613%" tag under the
# ticket. So series 0 is UNDRAWN to nothing BEFORE the recast opens - the GDP line unwinds on "before the paper catches
# up" (E50's own leave: "then it un-draws or becomes the next thing") - and the divergence's memory line arrives at
# nothing, as the card of row 7 carried it. MEASURED on draft 5 (`p69t18/onset` 93.40): an undraw that STARTED with the
# recast let the arriving memory line draw to the GDP cap for its first half second, "+613% MEMORY" flashing under the
# ticket (the probe's M25 at 93.34-93.44).
MEMORY_HOLD_S = 0.8
MEMORY_HOLD_GAP_S = 0.1   # ... and it has landed this far before the recast's first frame
# THE PAGE LANDS ON THE OBJECT'S OWN DOMAIN (log, sized for memory's 1,074), so the three lines it draws fill the plot's
# lower ~40% and the held memory's room stands empty above them. A recast carries no domain, and a `chart_to rescale`
# after it is REFUSED by name ("4 chart states is past STATE_MAX (3): a fourth chart is a new page or a card" - draft 2,
# `logs/t18-door2.log`). The other door - row 10 as its own page on `;domain=80,277` - would trade the recast UNDER the
# card (E64, the treatment's row) for a page-to-page transform across a live dock. Named for the parent (HG4 / T33).
# THE TICKET IS READ, THEN PARKS (the dock's `read` box, 2026-09-10): thrown on "sell" at reading size (its badge SELL is
# legible there - at the parked 0.15 it measured a 9 px pill on draft 1), held while the sentence finishes, and parked
# into TICKET_ROOM just before the page recasts under it on "Chipmakers". The reading box stands in the GDP page's RIGHT
# ROOM, off the plot: a read centred on the stage was DEFERRED to the parked box by E63 ("a card never reads over the
# plot", draft 3), and the GDP page's plot ends at x 0.57 with the stage empty from x 0.65 to the edge (T17's 88.50).
TICKET_READ = {"centre_w": 0.30, "centre_x": 0.815, "centre_y": 0.47}
TICKET_PARK_S = 0.7
# THE TRANSFORMS INSIDE A ROW (a table row is a world; its chart_to / undraw / card hand-offs change the board without a
# boundary) - each names what it took and refused (E99 s74), printed in SHOT-TABLE-H.md beside the boundaries' whys.
# ROW 11, THE ADJUSTER'S WALK (P69 T19, re-cut 2026-09-23): A WORLD CHANGE. The divergence's last line lands at ~98.1 s;
# on "like a claims adjuster" (104.3 s, E50's 6.2 s) the sentence LEAVES the chart's argument and the next three things
# are quotes, so the chart MELTS and splashes onto a desk plate where the records land (the parent's option (b)). THE
# PARENT'S FIRST CHOICE, (a) - the page recedes, its axes and title dimmed or undrawn, the records on the bare charcoal -
# HAS NO DOOR: `undraw` takes a page's LINES and never its axes (measured, T19 draft 3: ticks, the unit label and the
# dates stood under every card), no species dims or retracts a page's furniture (SPECIES_KINDS), and the dock `#wash` is
# a fixed 0.18-0.34 gradient scrim (scene-evidence-player.template.html:250-262) that no row can deepen. Engine gap,
# named for the parent: "a page recedes to its ground under a card" (an undraw of the axes, or a row-level wash depth).
MEMO_PLATE = "world-internal-memo-v1;use=landing"
# the locomotive's stack MOUTH, measured on this build's frames across the ken push (p69t21/stack-148.40, -161.00: the
# stack top stands at x 0.397-0.424, y 0.150-0.165) - a thin band at the mouth, the steam's own source (the Tokyo form)
STACK_STEAM = {"kind": "region", "x0": 0.398, "y0": 0.148, "x1": 0.426, "y1": 0.168}   # wave 3: a lamp, a desk, one memo with a seal - a plain DOCUMENT plate
MEMO_KEN = (0.04, 8, -6)                            # E99 s84: the ken push ALONE is a long-form plate's life
MEMO_MELT_S = 1.0     # the melt runs over "like a claims adjuster", the plate is there on "and it gets strange"
MEMO_MELT_WHY = ("the divergence -> the memo desk, page to plate (a WORLD change, E47): TAKEN the melt's splash onto the plate "
                 "(E88; row 2's own ending, E76 s5) - the chart the sentence leaves balls up and splashes onto the desk the "
                 "records land on; refused: the page receding under the records (no door - undraw takes lines, never axes; "
                 "no species dims a page; the dock wash is a fixed scrim), the dip (a dip is the last resort, s74 - the melt "
                 "IS a transform for this pair and E88 melts a chart's ink), the thread (no mark of the page belongs on a "
                 "desk), recast / remake (the next thing is a quote, not a chart - and STATE_MAX is spent), a park (a chart "
                 "held small behind a record is the 'broken chart' the parent read)")
SLOT_WHY = ("the ticket -> Karp -> Uber -> the COO: TAKEN the slot hand-off (E99 s80 - each card takes the outgoing card's "
            "box, the chart never stands aside); Karp THROWN on his name (s71), Uber and the COO LAND into the same box "
            "(SLOT_HANDOFF_ARRIVE); refused: a dip per quote (no world changes between them, E47), three worlds "
            "(build-f's memo / burndown / racks plates - the G31 listing risk the treatment closes on screen). The ticket "
            "leaves with its page at the melt; its corner box is NOT the records' slot (a record there types at ~8 px)")
IN_ROW_WHY = (
    ("row 5 recast 3 (P69 T18, 'catches up with it')", DIV_RECAST_WHY),
    ("row 6 the one slot (P69 T19, 'Alex Karp' / 'Uber's CTO' / 'And their COO')", SLOT_WHY),
    ("row 8 the recast to the breakthrough bars (P69 T22, 'railways took roughly')", YARD_RECAST_WHY),
)
# (the P69 T16 first cut, before T15b, is kept for the record: it entered the index from the STUDIO by dip 1 and
# refused recast / rescale / morph, the melt, the snap / throw-then-zoom / throw-then-push, object-becomes-chart, the
# spiral return, the mount and the thread by name. T15b moved their chart onto the page, which removed that boundary.)
BOUNDARY_WHY = {HOST_PLATE: HOST_DIP_WHY,   # a row's world -> the why of the transition INTO it, in SHOT-TABLE-H.md
                page_snap(): SNAP_WHY,
                page_rail(): RAIL_MELT_WHY,
                MEMO_PLATE: MEMO_MELT_WHY,
                VIADUCT_PLATE: VIADUCT_DIP_WHY,
                page_yard(): YARD_DIP_WHY,
                page_tnx(): TNX_MELT_WHY,
                SLATE_PLATE: ("page -> slate: TAKEN the melt's splash onto the plate (E88; the operator's own second "
                              "ending, E76 s5) - the chart melts to a ball that splashes onto the slate (R26-229 b)")}

CARD_READ_S = 5.5   # E25 / M12: a chart card proves its sentence and leaves - under the 6 s homework ceiling
CARD_CLEAR_S = 1.2  # ... and it is GONE before the page recasts, so the hand-over happens on a clear page
# CAMERA 1 (E99 s76; CAPABILITIES:85 - the row's optional 8th element). NOT a `focus_zoom` species: that species
# is the engine's own FOCUS_SCALE 1.32 (scene-evidence-engine.mjs:4884) and at 16:9 it cut the y-axis tick labels
# off the frame - MEASURED on this build's first probe (tick boxes at x -86 while the move held). The treatment's
# own row says a zoom at this aspect must be measured before it stays, so the move is AUTHORED as keys at
# CAMERA_ZOOM and released back to identity.
CAMERA_ZOOM, CAMERA_IN_S, CAMERA_HOLD_S = 1.06, 1.2, 2.4   # 1.10 cut the page title by 9 px (M43, measured)


def shot_table(ws: list, unit_end: float) -> list:
    """The treatment's rows 1-11, timed from the take (P69 T15-T19 grow it one body row at a time). A cut or a dip is
    the last resort (E99 s74); each boundary and each transform inside a row names what it took and refused."""
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
    # -- row 7 (P69 T15, corrected T15b): HOST WINDOW 1. The world changes on the cut before the promise, so the studio
    # holds its six seconds (M44) before their chart becomes the page.
    t_host = cut(HOST_FROM_PHRASE)                      # the dip INTO the studio (a row's exit is the door into it)
    t_bravos = at("Bravos Research")                    # the card ARRIVES on the name (E99 s71) ...
    t_snap = round(t_bravos + CARD_LEAD_S, 2)           # ... and the camera pushes it to the page a second later
    t_nvidia = at("Nvidia")                             # the chip lands on its word, on the page ...
    t_its = at("It's capital")                          # ... is crossed as the sentence turns ...
    t_capital = at("capital arriving faster")           # ... and the flow draws on the mechanism, in the page's room
    # -- row 8 (P69 T16): THE REHOOK. Their chart melts (E88) on "But capital that fast" and the railway index draws on
    # the same board - page to page, no dip (E47; RAIL_MELT_WHY).
    t_rail = at("But capital that fast")                # the melt starts on the word: the boundary IS the melt's start
    t_trail = at("paper trail")                         # the index climbs on the trail it names ...
    t_over = at("Every transformative")                 # ... to the half-way cap, as row 9's first sentence begins
    t_join = round(t_over - RAIL_JOIN_LEAD_S, 2)
    # -- row 9 (P69 T17): the same page - the climb, the crash, the recast, the ring.
    t_peak = at("pounds, more than")                    # the peak lands as "a quarter-billion" ends, on "pounds"
    t_crashed = at("crashed by nearly")                 # the crash draws on its verb
    t_drop = at("nearly two-thirds")                    # the drop is written as its size is said
    t_internet = at("the internet crossed")             # the recast on the new era's subject
    t_tower = at("then the tower came down")            # the ring on the peak before the fall
    t_ai = at("AI spending just crossed")               # the share-of-GDP line climbs back on the AI sentence
    # -- row 10 (P69 T18): THE HEAD-FAKE, the same page - the ticket thrown on its verb, the page recast under it.
    t_move = at("obvious move")                         # the ticket ARRIVES on the move it is (E99 s71), its SELL badge
    #                                                     springing 2.05 s later (the compiler's badge clock) on "sell"
    t_catch = at("catches up with")                     # the page recasts to the divergence under it (E64), so the
    #                                                     chips draw on "Chipmakers doubling" and their customers after
    # -- row 11 (P69 T19, re-cut): THE ADJUSTER'S WALK - the chart melts onto a desk, three records take one slot.
    t_memo = at("like a claims")                        # the divergence MELTS as the sentence leaves it (E50, E88): the
    #                                                     boundary is the melt's start, the desk is there on "and it gets"
    t_karp = at("Alex Karp")                            # the record is thrown on his name (E99 s71)
    t_uber = at("Uber's CTO")                           # the Uber card takes its slot (s80) ...
    t_coo = at("And their COO")                         # ... and the COO's line takes the Uber card's
    # -- row 12 (P69 T20): THE TROUGH, on the same desk - "that line" is the COO's, still standing; then the table.
    t_isnt = at("And that isn't the peak")              # the three-manias table takes the COO's slot (s80) ...
    t_flips = at("Which flips the question")            # ... and leaves as the question flips; the desk and its steam
    # -- row 13 (P69 T21): RESET 1 - the dip to 1849 at the world change (E47), on the cut before the sentence
    t_1849 = cut("And in 1849")
    # -- row 14 (P69 T22): THE YARDSTICK - dip 3 at the world change, on the cut before the sentence
    t_yard = cut("So I built")
    t_counts = at("It counts every")                    # the tech line climbs through the sentence that defines it ...
    t_dotcom = at("dot-com peak")                       # ... to the peak the next sentence names
    t_23 = at("twenty-three cents")                     # the 23 written at its datum as it is said
    t_today = at("Today it's")                          # the last twenty-five years draw on "Today it's" ...
    t_28 = round(t_today + YARD_TODAY_S, 2)             # ... landing on "twenty-eight" - camera 2's landing (E51)
    t_1840s = at("railways took roughly")               # the recast to the breakthrough bars: MEASURED on draft 1, a
    #                                                     recast on "In the 1840s" (183.78) burst before "roughly" was
    #                                                     said (185.2); on "railways" the 50 lands on "roughly half"
    yard_peak_end = at("peak it hit")                   # the peak lands as "peak" is said
    # -- row 15 (P69 T23): THE TRIGGER AND THE CONCESSION - the bars melt on the sentence's turn (the boundary IS the
    # melt's start), the yields draw on their words, and the Fed is STAMPED on its name
    # the melt opens TNX_MELT_LEAD_S before the sentence, inside the breath after "eighty years.": MEASURED on draft 5
    # (`logs/t23-stagegaps.log` then), a melt opened ON "Bravos'" left the stage empty 196.32-196.52 under the word
    t_trigger = round(at("Bravos' sharpest") - TNX_MELT_LEAD_S, 2)
    t_ends = at("what actually ends")                   # the dot-com yield starts drawing as the trigger is named ...
    t_pointing = at("They fail by pointing")            # ... its first leg (the dip and most of the way back) lands here
    t_dies = at("It dies when")                         # ... and it crosses back above its first print on the words
    t_began = at("borrowing began")                     # ... landing on its January 2000 high as "began" ends
    t_fed = at("Fed at six and")                        # PROP 1 lands on the word that names it (E99 s87)
    t_trade = at("internet trade rolled")               # the dot-com yield rolls over on its words ...
    t_cycle = at("for this cycle")                      # ... and the AI era draws on "this cycle", under their 5.5%
    t_agree = at("Put my agreement")                    # the concession, written on the same page
    t_row9_end = unit_end

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
        (t_melt, t_host, SLATE_PLATE, SLATE_KEN, [], MELT_EXIT % MELT_S_H, [
            {"kind": "agenda", "at": t_three_q, "dur": round(t_host - t_three_q - 0.4, 2),
             "target": AGENDA_SLATE_BOX,
             "rows": [dict(AGENDA_ROWS_H[0], at=t_three_q), dict(AGENDA_ROWS_H[1], at=t_thirty),
                      dict(AGENDA_ROWS_H[2], at=t_sorts)]},
        ]),
        # -- ROW 7a (P69 T15b): HOST WINDOW 1 - the studio (E61 landing surface; E99 s81 the host), its life the ken push
        # ALONE (E99 s84). Mike says the promise to camera; THEIR CHART ARRIVES ON THEIR NAME (E99 s71: thrown, never
        # spotlit) onto the dark left monitor, and lands - it is on the ground for its landing beat only.
        (t_host, t_snap, HOST_PLATE, HOST_KEN, [
            (BRAVOS_CARD, 0, t_bravos, t_snap,
             dict(BRAVOS_READ, centre=True, card_aspect=BRAVOS_ASPECT, arrive="throw", mass="paper")),
        ], "dip", []),
        # -- ROW 7b (P69 T15b): THE CARD BECOMES THE CHART (the card-becomes-the-chart family). The camera pushes the card
        # to the stage and the page shows at the match (the arrival IS the transition: SNAP_WHY); READ at its own type. The hand writes
        # the card's title over the object's (a returning page arrives retitled); the chip lands on "Nvidia" in the
        # page's own room and is crossed as the sentence turns; the flow draws beside it - the chart stays full size.
        (t_snap, t_rail, page_snap(), (0, 0, 0), [], "cut", [
            {"kind": "build_to", "at": t_snap, "dur": 0.4, "series": DIV_MEMORY, "target": datum(0)},
            {"kind": "retitle", "at": t_snap, "dur": SNAP_RETITLE_S, "text": HOOK_CARD_TITLE},
            dict(NVIDIA_CHIP, at=t_nvidia, dur=round(t_rail - t_nvidia, 2), target=CHIP_ON_PAGE,
                 cross_at=round(t_nvidia + CHIP_CROSS_S, 2)),
            dict(CAPITAL_FLOW, kind="flow", at=t_capital, dur=round(t_rail - t_capital, 2), target=FLOW_ON_PAGE),
        ]),
        # -- ROW 8 (P69 T16): THE REHOOK - their chart MELTS and is thrown off (E88), and the railway index draws on the
        # same board (RAIL_MELT_WHY: page to page, no dip). It opens ON ITS AXES (E73), `;idle=live` (E49), and CLIMBS:
        # the build beat draws it to its first cap as it lands, and one pen carries it on from "paper trail"
        # (RAIL_CLIMB) - "paper you can read" is the line being written.
        # -- ROW 9 (P69 T17), the SAME page: the stroke carries on to the 1845 peak, the crash draws on its verb and
        # the drop is written under the trough; on "the internet" the page RECASTS to the share-of-GDP line (E58/E64),
        # and on "then the tower came down" the ring lands on its own Q2-2000 peak (E56) - no 7, no 8 (E77).
        # -- ROW 10 (P69 T18), the SAME page: the sell ticket is THROWN on "sell" (E99 s71, `mass: paper`) into the room
        # right of every tag; on "Chipmakers doubling" the page RECASTS under it to the divergence (E64, its third
        # state), the memory line held at nothing - the head-fake reads the two lines the card of row 7 carried - the
        # chips drawn on "Chipmakers doubling" and their customers on "sit flat" (`build=lines`, each whole with its
        # tag). DIV_RECAST_WHY names what the recast took and refused.
        (t_rail, t_memo, page_rail(), (0, 0, 0), [
            (SELL_CARD, 0, t_move, t_memo,
             dict(TICKET_ROOM, card_aspect=SELL_ASPECT, arrive="throw", mass="paper",
                  read=dict(TICKET_READ, card_aspect=SELL_ASPECT), park_s=TICKET_PARK_S,
                  read_s=round(t_catch - t_move - TICKET_PARK_S, 2))),
        ], RAIL_EXIT % RAIL_MELT_S, [
            {"kind": "build_to", "at": t_rail, "dur": 0.4, "series": 0, "target": datum(RAIL_OPEN_CAP)},
            {"kind": "build_to", "at": t_trail, "dur": round(t_join - t_trail, 2),
             "series": 0, "target": datum(RAIL_TRAIL_CAP)},
            {"kind": "build_to", "at": t_join, "dur": round(t_peak - t_join, 2), "series": 0, "target": datum(RAIL_PEAK)},
            {"kind": "build_to", "at": t_crashed, "dur": RAIL_CRASH_S, "series": 0, "target": datum(RAIL_TROUGH)},
            {"kind": "figure", "at": t_drop, "dur": RAIL_DROP_S, "target": datum(RAIL_TROUGH, 0), "text": RAIL_DROP,
             "color": "neg", "dy": RAIL_DROP_DY},
            {"kind": "chart_to", "at": t_internet, "dur": GDP_RECAST_S, "to": "recast", "state": GDP_RECAST},
            {"kind": "retitle", "at": round(t_internet + RETITLE_AFTER_S, 2), "dur": GDP_RECAST_S, "text": GDP_TITLE},
            {"kind": "callout", "at": t_tower, "dur": GDP_RING_S, "target": datum(GDP_PEAK, 0)},
            {"kind": "build_to", "at": t_ai, "dur": GDP_CLIMB_S, "series": 0, "target": datum(GDP_LAST)},
            # row 10: the recast under the ticket, the memory line held, the title the sentence's own, the gap bleeding
            {"kind": "chart_to", "at": t_catch, "dur": DIV_RECAST_S, "to": "recast", "state": DIV_RECAST},
            {"kind": "undraw", "at": round(t_catch - MEMORY_HOLD_S - MEMORY_HOLD_GAP_S, 2), "dur": MEMORY_HOLD_S,
             "series": DIV_MEMORY, "target": datum(0)},
            {"kind": "retitle", "at": round(t_catch + RETITLE_AFTER_S, 2), "dur": DIV_RECAST_S,
             "text": HEADFAKE_TITLE},
        ]),
        # -- ROW 11 (P69 T19, re-cut): THE MEMO DESK - the divergence melts and splashes onto it (MEMO_MELT_WHY); one slot,
        # three records, every one at the reading size on a clean ground (RECORD_SLOT); the plate's life is its ken push.
        (t_memo, t_1849, MEMO_PLATE, MEMO_KEN, [
            (KARP_CARD, 0, t_karp, t_uber,
             dict(RECORD_SLOT, centre_w=RECORD_W, card_aspect=KARP_ASPECT, arrive="throw", mass="paper")),
            (UBER_CARD, 0, t_uber, t_coo,
             dict(UBER_SLOT, centre_w=UBER_W, card_aspect=UBER_ASPECT, arrive=SLOT_HANDOFF_ARRIVE, mass="paper")),
            (COO_CARD, 0, t_coo, t_isnt,
             dict(RECORD_SLOT, centre_w=COO_W, card_aspect=COO_ASPECT, arrive=SLOT_HANDOFF_ARRIVE, mass="paper")),
            # -- ROW 12 (P69 T20): the table takes the COO's slot at the slot's full width, its badges carrying the move
            (MANIAS_CARD, 0, t_isnt, t_flips,
             dict(UBER_SLOT, centre_w=MANIAS_W, card_aspect=MANIAS_ASPECT, arrive=SLOT_HANDOFF_ARRIVE, mass="paper")),
        ], MELT_EXIT % MEMO_MELT_S, [
            {"kind": "steam", "at": round(t_memo + MEMO_MELT_S, 2), "dur": round(t_uber - t_memo - MEMO_MELT_S, 2),
             "target": MUG_STEAM},
            {"kind": "steam", "at": t_coo, "dur": round(t_isnt - t_coo, 2), "target": MUG_STEAM},
            {"kind": "steam", "at": t_flips, "dur": round(t_1849 - t_flips, 2), "target": MUG_STEAM},
        ]),
        # -- ROW 13 (P69 T21): RESET 1 - the viaduct, 1849 (dip 2 at the world change; VIADUCT_DIP_WHY). Ken Burns alone
        # (E99 s84) and the locomotive's stack breathing (E49); the anaphora in caption STAGE mode (no dock on the row).
        (t_1849, t_yard, VIADUCT_PLATE, VIADUCT_KEN, [], "dip", [
            {"kind": "steam", "at": t_1849, "dur": round(t_yard - t_1849, 2), "target": STACK_STEAM},
        ]),
        # -- ROW 14 (P69 T22): THE YARDSTICK - dip 3 back to the page (YARD_DIP_WHY), on its axes, in the long form's
        # profile. The tech line is held at nothing through the sentence that names the measure, then ONE pen climbs it
        # through the definition to the dot-com peak; the page's own 23% is written there; the last twenty-five years draw
        # on "Today it's" and land on "twenty-eight" (its end tag writes 28%), where camera 2 pushes (E51). On "In the
        # 1840s" the page RECASTS to the breakthrough bars (YARD_RECAST_WHY) and the railways' half bursts the scale.
        (t_yard, t_trigger, page_yard(), (0, 0, 0), [], "dip", [
            {"kind": "build_to", "at": t_yard, "dur": YARD_OPEN_S, "series": YARD_TECH, "target": datum(0)},
            {"kind": "build_to", "at": t_yard, "dur": YARD_OPEN_S, "series": YARD_SCALE, "target": datum(0)},
            {"kind": "build_to", "at": t_counts, "dur": round(yard_peak_end - t_counts, 2), "series": YARD_TECH,
             "target": datum(YARD_PEAK)},
            {"kind": "figure", "at": t_23, "dur": YARD_FIG_S, "target": datum(YARD_PEAK, YARD_TECH), "text": YARD_23},
            {"kind": "build_to", "at": t_today, "dur": YARD_TODAY_S, "series": YARD_TECH, "target": datum(YARD_LAST)},
            {"kind": "undraw", "at": round(t_1840s - YARD_UNDRAW_S - MEMORY_HOLD_GAP_S, 2), "dur": YARD_UNDRAW_S,
             "series": YARD_TECH, "target": datum(0)},
            {"kind": "chart_to", "at": t_1840s, "dur": YARD_RECAST_S, "to": "recast", "state": YARD_RECAST},
            {"kind": "retitle", "at": round(t_1840s + RETITLE_AFTER_S, 2), "dur": YARD_RECAST_S,
             "text": YARD_BARS_OBJ["title"]},
        ], {"keys": [
            {"t": t_28, "zoom": 1.0, "look": YARD_CAM_LOOK, "ease": "inout"},
            {"t": round(t_28 + YARD_CAM_IN_S, 2), "zoom": YARD_CAM_ZOOM, "look": YARD_CAM_LOOK, "at": YARD_CAM_AT,
             "ease": "inout"},
            {"t": round(t_1840s - YARD_CAM_OUT_S - 0.1, 2), "zoom": YARD_CAM_ZOOM, "look": YARD_CAM_LOOK,
             "at": YARD_CAM_AT, "ease": "inout"},
            {"t": round(t_1840s - 0.1, 2), "zoom": 1.0, "look": YARD_CAM_LOOK, "ease": "inout"},
        ]}),
        # -- ROW 15 (P69 T23): THE TRIGGER - the bars melt and are thrown (TNX_MELT_WHY) and the 10-year yield page lands
        # on its axes, both eras held at nothing; the dot-com yield draws on "what actually ends a mania" through the 1998
        # dip, and crosses back above its first print on "It dies when rates cross back above", landing on its January
        # 2000 high on "began"; the BoE's 6% is said, not drawn (no series or rule of its own here, BODY_DEPARTURES row
        # 15); on "Fed" the title becomes the sentence's claim off the page's own 6.5% rule and PROP 1 the Fed is STAMPED
        # (FED_STAMPED) into the page's biggest room (the engine's fit, P69 T5) and leaves with the
        # page; the dot-com yield rolls over on its words and the AI era draws on "this cycle", ending under their 5.5%
        # rule; the concession is written on the SAME page (no bare plate 2:45-6:04). The camera pulls on the stamp's
        # contact (P69 T4, `attention: landings`, E51).
        (t_trigger, t_row9_end, page_tnx(), (0, 0, 0), [
            (FED_PROP, 0, t_fed, t_row9_end, dict(FED_OPTS)),
        ] if FED_STAMPED else [], RAIL_EXIT % TNX_MELT_S, [
            {"kind": "build_to", "at": t_trigger, "dur": TNX_OPEN_S, "series": TNX_DOT, "target": datum(TNX_OPEN_CAP)},
            {"kind": "build_to", "at": t_trigger, "dur": TNX_OPEN_S, "series": TNX_AI, "target": datum(0)},
            {"kind": "build_to", "at": t_ends, "dur": round(t_pointing - t_ends, 2), "series": TNX_DOT,
             "target": datum(TNX_DOT_LEG1)},
            {"kind": "build_to", "at": t_dies, "dur": round(t_began + 0.5 - t_dies, 2), "series": TNX_DOT,
             "target": datum(TNX_DOT_PEAK)},
            {"kind": "retitle", "at": t_fed, "dur": TNX_TITLE_S, "text": TNX_FED_TITLE},
            {"kind": "build_to", "at": t_trade, "dur": TNX_ROLL_S, "series": TNX_DOT, "target": datum(TNX_DOT_LAST)},
            {"kind": "build_to", "at": t_cycle, "dur": TNX_AI_S, "series": TNX_AI, "target": datum(TNX_AI_LAST)},
            {"kind": "retitle", "at": t_agree, "dur": TNX_TITLE_S, "text": TNX_AGREE_TITLE},
        ], {"keys": [], "attention": "landings"}),
        # (-- ROWS 16-24 are T24-T32's, one row per slice; UNIT_CUT_PHRASE moves with each.)
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
            # an `axes` page fires `page enter (axes)`, never the cream roll-out, a snapped page `(snap)` (P69 T15b),
            # and a cue that claims the wrong one is dropped by the binder (R26-198)
            entry = "snap" if page["snap"] else "camera" if page["camera"] else OPEN_ENTER
            cues.append({"slot": "page enter %d (%s)" % (i + 1, entry), "at": round(r[0], 2),
                         "gain": ENTER_GAIN, "fade_in": 0.0, "variants": {"A": ROLL}})
        for d, opts in A.row_arrivals(r):
            arrive = opts["arrive"]
            contact = A.landing_contact(d[2], arrive, stop)
            # the slot names the MASS the engine lands at (P69 T14 (5)): the row's own `mass`, else `ink` for a
            # stamp (the engine's `stampXf(d.mass || "ink")`) and `paper` for a throw or a land - never a stamp
            # read as paper because the row named nothing
            cues.append({"slot": "landing %d (%s, %s)" % (i + 1, arrive, A.arrival_mass(opts)),
                         "at": round(contact - 1 / 24, 2), "gain": ACCENT, "fade_in": 0.0,
                         "variants": {"A": STROKE, "B": ROLL},
                         "note": "contact at %.2fs, the cue one frame early (the weight report Q5)" % contact})
        if r[5] == "dip":   # the world change's own accent (E47) - AT THE ROW'S START: a row's exit is the door INTO
            # it (the engine's `dipIn` reads `sc.exit` against the scene before, transitions.mjs:96 /
            # build_scene_timeline_f.py:2660). P69 T15 fixed `r[1]`, which sounded the whoosh at the row's END.
            cues.append({"slot": "dip %d" % (i + 1), "at": round(r[0] - 0.35, 2), "gain": ACCENT,
                         "fade_in": 0.0, "variants": {"A": WHOOSH}})
    env = A.bed_envelope(rows, BED_SWELL_DB, SNAP_S_BED, fallback_end=lambda d: float(d[2]) + 1.2)
    cues.append({"slot": "hook bed", "at": 0.0, "gain": A.bed_gain(VO_LUFS, BED_LU, BED_LUFS), "fade_in": 1.5,
                 "env": env, "variants": {"A": BED_HOOK_A, "B": BED_HOOK_B},
                 "note": "%+.0f LU under the VO (%.1f LUFS measured); the long form's calibration" % (BED_LU, VO_LUFS)})
    return cues


# ---------------------------------------------------------------- THE BODY'S PREFLIGHT (P69 T14, rows 7-24)

# Read before a body row is authored; nothing here is compiled into the bed (the bed's timeline and table are
# byte-identical with and without this block). Paths are repo-relative; `find_asset` resolves every plate id.
_PROJ = "content/video_engine/projects/systems-and-blowups/steel-and-paper/"
_OBJ = _PROJ + "evidence/objects/"
_PLATES = "content/video_engine/projects/systems-and-blowups/review/claims/steel-and-paper-plates-wave-"
_PROPS = "content/video_engine/assets/props/cutouts/"
_ICONS = "content/video_engine/assets/icons/"
_SND = _PROJ + "sound/"
_OUTRO = "content/video_engine/channel-assets/money-physics/outro/"   # gitignored media: present here since 2026-09-22 21:01 (copied from main)

# ROW 16's RANGE IS A RANGE (E53 / E77): 2026E is two estimate series that both leave the 2025 actual, and the
# wedge between them is a `spread`; the figure writes the range, never a midpoint. The series are read off the
# object by their own labels, never typed as indices. The old PNG (`vals=[28, 121, 140]`,
# evidence/build_railway_documents.py:153) draws a 140 midpoint and is NOT a fallback.
DEBT_PAGE = "ev-debt-issuance-line-v1"
_DEBT = _series(DEBT_PAGE)
_DEBT_LABELS = [s["label"] for s in _DEBT["series"]]
DEBT_SPREAD = {"kind": "spread", "from": _DEBT_LABELS.index("$150B"), "to": _DEBT_LABELS.index("$130B")}
DEBT_RANGE_TEXT, DEBT_RANGE_SUB = "$130–150B", "2026E"
TWO_CLOCKS_PAGE = "ev-two-clocks-bars-v1"   # row 19: about 20 years vs about 5 years (RAILWAY-LAG-20Y-FINDINGS.md)

# (kind, item, what it resolves to). Builders: `ledger_page.pick_builder` on the series at the row's variant.
# PLAUSIBLE pages (H1-H5, row 16, row 19) DRAW - the operator, 2026-09-22: "yes draw plausible pages" (E99 s?? (b));
# each object carries its tier and proof, and UNSOURCED / REJECTED still never draw.
BODY_ASSETS = {
    7: (("host", HOST_PLATE_ID, _PROJ + "host/H-1-studio.png - quarantined until approved (E10); supersedes "
                                "the treatment's world-broadcast-set-v2 (the host amendment)"),
        ("card", BRAVOS_CARD, "build-h/objects/%s.series.json -> docks.chart_card (re-derived by _hook_object)"
                              % HOOK_OBJECT_ID),
        ("card", "flow capital -> value", _ICONS + "coins.svg, factory.svg (CAPITAL_FLOW)"),
        ("card", "NVIDIA chip", _ICONS + "cpu.svg (NVIDIA_CHIP)"),
        ("cue", "landing / dip", _SND + STROKE + ", " + ROLL + ", " + WHOOSH)),
    8: (("page", RAIL_PAGE, _OBJ + RAIL_PAGE + ".series.json - dense-line"),
        ("cue", "dip 1", _SND + WHOOSH)),
    9: (("page", RAIL_PAGE, "dense-line; the drop is RAIL_DROP (-64%)"),
        ("page", GDP_PAGE, _OBJ + GDP_PAGE + ".series.json - dense-line (hline 'Q2 2000 peak - 11.54%')"),
        ("card", "RAIL_NOTE", "NOT DRAWN (P69 T17): the dossier carries no railway capital figure - see BODY_DEPARTURES")),
    10: (("card", SELL_CARD, _PLATES + "3/objects/world-sell-ticket-v1.png - the form's face (SELL_CROP) with SELL "
                              "stamped across it (`_sell_ticket_card`, P69 T18b; the treatment's plate is a CARD)"),
         ("page", LAYER_PAGE, _OBJ + LAYER_PAGE + ".series.json - dense-line (the recast, state 3, memory held)")),
    11: (("plate", "world-internal-memo-v1", _PLATES + "3/objects/world-internal-memo-v1.png - the records' desk "
                                           "(P69 T19b, the parent's FIX 2)"),
         ("card", KARP_CARD, _OBJ + "ev-doc-karp.png - RECORD dock, live type (P69 T19: the payload's words copied "
                              "from build-f/evidence-dock.json into KARP_*, timed off the take by karp_record)"),
         ("card", UBER_CARD, _OBJ + "ev-uber-adoption-v1.png - PNG card read at 0.83 of the stage (a chart, never small)"),
         ("card", COO_CARD, _OBJ + "ev-doc-macdonald.png - PNG card; the caption strip carries the words")),
    12: (("card", MANIAS_CARD, _OBJ + "ev-three-manias.png - the table COMPOSED from its own bands (`_manias_card`, "
                                "MANIAS_BANDS), read at ~0.76 of the stage (P69 T20)"),
         ("plate", "world-internal-memo-v1", "the same desk as row 11 (no world change inside rows 11-12)")),
    13: (("plate", "world-viaduct-train-rain-v1", _PLATES + "1/objects/world-viaduct-train-rain-v1.png - "
                                                "`use=reset`, Ken Burns + the stack's steam (P69 T21)"),
         ("cue", "dip 2", _SND + WHOOSH)),
    14: (("page", "ev-capital-formation-v1", _OBJ + "ev-capital-formation-v1.series.json - dense-line"),
         ("page", "ev-rail-vs-yardstick-bars-v1", _OBJ + "ev-rail-vs-yardstick-bars-v1.series.json - story (H1)")),
    15: (("page", "ev-tnx-two-eras-v3", _OBJ + "ev-tnx-two-eras-v3.series.json - dense-line, two panels"),
         ("prop", "prop-federal-reserve-building-v1", _PROPS + "prop-federal-reserve-building-v1.png"),
         ("cue", "prop stamp", _SND + STROKE + " / " + ROLL + " - slot `landing N (stamp, ink)` (A.arrival_mass)")),
    16: (("page", DEBT_PAGE, _OBJ + DEBT_PAGE + ".series.json - dense-line + DEBT_SPREAD + figure "
                             "DEBT_RANGE_TEXT / DEBT_RANGE_SUB (no PNG fallback)"),
         ("page", "ev-ig-credit-weighting-v1", _OBJ + "ev-ig-credit-weighting-v1.series.json - story (bars, "
                                               "not the treatment's :line)"),
         ("page", "ev-capex-consensus-v1", _OBJ + "ev-capex-consensus-v1.series.json - story"),
         ("card", "ev-doc-leases", _OBJ + "ev-doc-leases.png - record dock; its payload is NOT authored "
                                   "(CAPABILITIES:19), so the PNG until it is"),
         ("prop", "prop-hyperscale-datacenter-v1", _PROPS + "prop-hyperscale-datacenter-v1.png")),
    17: (("page", "ev-capex-ocf-94-bars-v1", _OBJ + "ev-capex-ocf-94-bars-v1.series.json - story (H2)"),
         ("card", "badge 'PIMCO, Figure 3'", "text (the PIMCO record departs)")),
    18: (("plate", "world-paper-and-steel-press-v1", _PLATES + "6/objects/world-paper-and-steel-press-v1.png"),
         ("card", CERT_CARD, "CERT_PLATE + CERT_CROP; its figure is a badge at RAIL_DROP"),
         ("page", "ev-index-concentration-bars-v1", _OBJ + "ev-index-concentration-bars-v1.series.json - story (H3; "
                                                    "2-4% as two hlines)"),
         ("card", "world-target-date-envelope-v1", _PLATES + "3/objects/world-target-date-envelope-v1.png"),
         ("prop", "prop-tech-sp500-concentration-v1", _PROPS + "prop-tech-sp500-concentration-v1.png")),
    19: (("page", TWO_CLOCKS_PAGE, _OBJ + TWO_CLOCKS_PAGE + ".series.json - story (no PNG fallback)"),
         ("card", "pill 'sold out'", "engine species; source EVIDENCE-DOSSIER.md E1")),
    20: (("host", "H-2 (no id constant yet)", _PROJ + "host/H-2-desk.png - quarantined; supersedes the "
                                              "treatment's world-spike-desk-v1"),
         ("card", "ev-test-scorecard-v1", _OBJ + "ev-test-scorecard-v1.series.json - checklist dock"),
         ("page", LAYER_PAGE, "dense-line (returns)"),
         ("cue", "dip 6", _SND + WHOOSH)),
    21: (("page", "ev-hynix-steel-v1", _OBJ + "ev-hynix-steel-v1.series.json - dense-line"),
         ("page", "ev-hbm-wafer-ratio-bars-v1", _OBJ + "ev-hbm-wafer-ratio-bars-v1.series.json - story (H4)"),
         ("page", "ev-dram-contract-v1", _OBJ + "ev-dram-contract-v1.series.json - story (bars, not :line)"),
         ("card", "ev-test-scorecard-v1", "checklist dock (the ticks)"),
         ("prop", "prop-hbm-stacked-die-v1", _PROPS + "prop-hbm-stacked-die-v1.png"),
         ("prop", "prop-silicon-wafer-semiconductor-v1", _PROPS + "prop-silicon-wafer-semiconductor-v1.png")),
    22: (("card", "ev-tripwire-board-v1", _OBJ + "ev-tripwire-board-v1.png - PNG card / checklist dock"),
         ("page", "ev-memory-monitor-v1", _OBJ + "ev-memory-monitor-v1.series.json - dense-line (its June mark)"),
         ("page", "ev-june-print-v1", _OBJ + "ev-june-print-v1.series.json - dense-line, marks []"),
         ("card", "ev-trim-proof-v1", _OBJ + "ev-trim-proof-v1.series.json -> docks.chart_card (story)"),
         ("card", CERT_CARD, "returns; badge at RAIL_DROP"),
         ("prop", "prop-dram-memory-module-v1", _PROPS + "prop-dram-memory-module-v1.png")),
    23: (("plate", "world-spike-certificate-ring-v2", _PLATES + "1b/objects/world-spike-certificate-ring-v2.png"),
         ("card", CERT_CARD, "the card + a badge at RAIL_DROP, the ring on the badge"),
         ("card", "ev-memory-arithmetic-v1", _OBJ + "ev-memory-arithmetic-v1.png - PNG card / checklist dock"),
         ("page", "ev-weight-check-bars-v1", _OBJ + "ev-weight-check-bars-v1.series.json - story (H5); also the "
                                             "newsroom desk card via docks.chart_card"),
         ("host", "H-3 (no id constant yet)", _PROJ + "host/H-3-newsroom.png - RE-ROLL before HG4 (H7)")),
    24: (("page", LAYER_PAGE, "dense-line (one last time)"),
         ("card", "agenda", "AGENDA_ROWS_H (species agenda)"),
         ("outro", "outro clip", _OUTRO + "landscape/outro-yt-1920x1080-24fps.mov - gitignored, on disk"),
         ("outro", "brand line", _OUTRO + "vo/audio/brand-line-paced.mp3 - gitignored, on disk; text "
                                 + _OUTRO + "BRAND-LINE.txt"),
         ("outro", "recipe", "content/video_engine/effects/recipes/outro-clip-life.json (exit: dip)"),
         ("cue", "the close bed", _SND + "suno-close-A.mp3 / suno-close-B.mp3 / mix-close-A.mp3 / mix-close-B.mp3")),
}

# What the treatment names that is NOT on disk, and what the row does instead (P69-DATA-DEPARTURES.md).
# Rows 16 (debt issuance) and 19 (the two clocks) are RESOLVED as pages and are not here.
# Row 22's end figures are NOT a departure (E99 s?? (c), the operator: "I think you're reading hbm/dram pricing wrong"):
# on ev-memory-monitor-v1's own points DRAM is +16.4% on the July print (86970 vs 74686, the bounce off June's -3.7%)
# and HBM-class +13.9% over the last two prints (95408 vs 83784) - each figure is drawn WITH its basis.
MEMORY_FIGURES = (("DRAM", "+16%", "on the July print"), ("HBM-class", "+14%", "over the last two prints"))
BODY_DEPARTURES = (
    (9, "7% tick / 8% datum on ev-equip-ipp-gdp-v2", "cut - the page rings its own 11.54% (not shown under the 7/8 words)"),
    (9, "the note / figures '£250m' then '$1T+ today' (RAIL_NOTE; the treatment's row 9)",
     "cut (P69 T17) - no source on disk (UNSOURCED, never drawn); the caption carries the script's words"),
    (10, "the ticket 'reads SELL over the chip line's tip' (the crop carries no word)",
     "SELL STAMPED across the card's face in the negative ink (`_sell_ticket_card`, P69 T18b - the T18 badge was a 9-26 px "
     "pill); the ticket reads at 0.30 in the page's right room and parks right of the tags, never on ink"),
    (10, "'any adviser would sign it' - a signature stroke ON the ticket",
     "cut (P69 T18): no species draws on a still card (the callout's `phrase` target is a PRESS card's alone, a squiggle "
     "is a caption word's); the caption carries the words"),
    (10, "the recast page on the hook's scale (the three lines at full height)",
     "the object's own domain (a rescale after the recast is a 4th state, past STATE_MAX 3); the lines fill the plot's "
     "lower ~40%"),
    (10, "the chips-vs-customers gap as a spread on the recast page",
     "cut (P69 T18): a spread on a stated page reads state 0's lines (the railway, one series); the end tags carry it"),
    (11, "'no world change' (the treatment's one slot on the page)",
     "the records stand on the memo desk (P69 T19b, the parent's FIX 2): the page cannot recede under a card (no door), "
     "so the chart melts onto a plate - one slot, three records, one world of their own"),
    (11, "ev-uber-adoption-v1 burndown (PNG only)", "PNG card ev-uber-adoption-v1.png"),
    (11, "the COO line as a record (ev-doc-macdonald has no payload)", "PNG card ev-doc-macdonald.png; the caption strip"),
    (12, "ev-three-manias peak and trough markers (a 4x3 table, PNG only)",
     "CARD composed from its own bands (P69 T20); the peak-to-trough move is the card's own red 64% and its badge "
     "'THE PAPER / fell 64% / peak to trough' landing on 'trough' - no callout can mark a still card"),
    (12, "the 'Capital committed' row of ev-three-manias (~7% / ~7% / ~8% of GDP)",
     "cut from the composed card: the capital-to-GDP measures row 9 keeps off screen, and height the cells need"),
    (12, "'he's reaching for the third question' - the agenda's third row as a callback",
     "not drawn: the agenda's dock form writes white on a dark ground (the desk wall is cream) and its page form "
     "takes the frame; the COO's card - 'that line' - holds through the sentence. Option for HG4"),
    (13, "the anaphora 'on the plate's quiet zone'",
     "caption STAGE mode, stage-centred: a picture plate places cards (`;room=`), never its caption (no door)"),
    (15, "BoE 6% / Fed 6.5% rings, Bravos 5.5% tripwire on ev-tnx-two-eras-v3 (a 10-year page)",
     "badge - the attributed figures as text, no ring (E53: one unit)"),
    (17, "the Epoch '94 cents' mark on ev-capex-funding-v1 (a different claim)", "cut from row 17's bar beat"),
    (17, "the PIMCO record (the treatment's 'ev-doc-macdonald' is the Uber COO)", "badge 'PIMCO, Figure 3'"),
    (18, "the certificate card's '-66%' figure (the crop carries none)", "badge reading RAIL_DROP (-64%)"),
    (20, "the phone card (no phone icon, cutout or prop)", "cut until an asset is generated (H6)"),
    (22, "chart_to ev-tripwire-board-v1 (a checklist, refused as a page)", "PNG card / its checklist dock"),
    (22, "the June datum ringed on ev-june-print-v1 (marks [])", "re-target: ring ev-memory-monitor-v1's own June mark"),
    (22, "the certificate's '-66%' (returns)", "badge reading RAIL_DROP (-64%)"),
    (23, "ev-memory-arithmetic-v1:bars (two units; 'doubles' vs 80 -> 192 GB)", "PNG card or its checklist dock"),
    (23, "the certificate's '-66%' ringed", "badge reading RAIL_DROP (-64%), the ring on the badge"),
)

# THE RULINGS THAT OVERRULE THE TREATMENT'S WORDING (REBUILD-TREATMENT-H.md predates them; a row obeys these).
# (ruling, where, the operator's words, the treatment's wording it supersedes, what a row does)
TREATMENT_SUPERSEDED = (
    ("E99 s84", "docs/portable/OPERATOR-RULINGS.md:3296",
     "the drift is too random, i think we should use ken burns instead of drift.",
     "REBUILD-TREATMENT-H.md:54 'every plate the ken tuple plus `;idle=drift;drift=20`' (rows 7, 13, 18, 20, 23)",
     "a long-form plate row carries the ken push ALONE; no `;idle=drift;drift=20`; `plate_idle_paints` off (R26-236)"),
    ("E99 s83", "docs/portable/OPERATOR-RULINGS.md:3294",
     "keep the exterior drift, remove the interior drift, keep the electric/glow etc let that carry the life",
     "REBUILD-TREATMENT-H.md:54 'Every page `;idle=live`' - read as the interior word walk too",
     "`;idle=live` is the page's exterior breath + the electric; titles, ticks, tags hold still (R26-234); "
     "a line's pointer is ONE thing, the lead point"),
    ("E99 s91", "docs/portable/OPERATOR-RULINGS.md:3313",
     "The view is a light as an annotation/highlight, not as motion.",
     "REBUILD-TREATMENT-H.md:169 the events/min targets (35.0 vs a 46.5 median)",
     "a spotlight credits 0 motion events; a row's density comes from arrivals, builds and transforms, "
     "never a light (and s71: a named thing arrives, never a spotlight)"),
    ("E47", "docs/portable/OPERATOR-RULINGS.md:1419, amended :1444",
     "Our dip is supposed to be used as an actual transition when the scene ACTUALLY changes.",
     "REBUILD-TREATMENT-H.md:156 'Dips: 10, each at a world change (E47)' - E47 as first written (`docks -> dip`)",
     "a dip only where the world ACTUALLY changes (page <-> plate), never for a dock and never into a mount "
     "(a mount replaces the cold transition); each dip names the transform it refused (E99 s74)"),
    ("E50", "docs/portable/OPERATOR-RULINGS.md:1520, amended :1533",
     "A chart's deployed life: 6-8 s from its LAST data point on average, 12 s at most; then it un-draws or "
     "becomes the next thing",
     "REBUILD-TREATMENT-H.md:24 'the 6 s ceiling on a held dock' (E25) and :75 'the page holds the concession'",
     "the clock starts at the last data mark: 6-8 s, 12 s max, then undraw / recast / chart_to; the 6 s is a "
     "FLOOR only for a page that arrives built"),
)


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
    out = ["# SHOT TABLE H - the bed (P68 T5) and the body, grown one P69 slice at a time (T15-T32); a row is a world",
           "",
           "GENERATED by `build_episode_h.py` from `%s/%s.words.json`. Do not hand-edit -" % (TAKE.name, TAKE_STEM),
           "edit `build_episode_h.shot_table`. Every anchor is a PHRASE off the take (`authoring.words.at`).", "",
           "| # | window | world | options | cards | what fires |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(rows):
        bare, _, opts = str(r[2]).partition(";")
        cards = ", ".join("`%s` %.2f-%.2f" % (d[0], d[2], d[3]) for d in (r[4] or [])) or "-"
        species = "; ".join("%s @%.2f" % (e["kind"], e["at"]) for e in (r[6] or []) if isinstance(e, dict)) or "-"
        out.append("| %d | %.2f-%.2f | `%s` | `%s` | %s | %s |"
                   % (i + 1, r[0], r[1], bare, opts or "-", cards, species))
    life = T.life_tokens(rows)   # R26-245: the ken counts as life and the row says which (E99 s84)
    out += ["", "**Life: %d of %d rows** - " % (len(life), len(rows))
            + "; ".join("row %d `%s`" % (n, what) for n, what in life)
            + " (E49 nothing goes truly still; E99 s84 KEN BURNS ALONE on a long-form plate).",
            "", "**Flow count (E99 s74):** %d cut(s), %d dip(s) (each at a world change, E47), %d arrival(s) carrying "
            "a boundary, %d transform(s) - each boundary names the transform it took or refused:" % _flow_count(rows)]
    out += ["- row %d `%s` (`%s` INTO it at %.2f): %s" % (i + 1, str(r[2]).partition(";")[0], r[5], r[0],
                                                               BOUNDARY_WHY.get(r[2], "UNNAMED - E99 s74 owes a why"))
            for i, r in enumerate(rows) if r[5]]
    out += ["", "**Transforms inside a row (E99 s74):**"] + ["- %s: %s" % (what, why) for what, why in IN_ROW_WHY]
    out += ["", "**Table rows -> treatment rows (`REBUILD-TREATMENT-H.md`):** "
            + "; ".join("row %d = %s" % (i + 1, TABLE_TREATMENT.get(i + 1, "?")) for i in range(len(rows))) + "."]
    return "\n".join(out + [""])


# a table row is a WORLD; a treatment row is a beat - the map the parent reads the two tables by (P69 T16)
TABLE_TREATMENT = {1: "treatment rows 1-5 (the page, 0:00-0:42)", 2: "treatment row 6 (the slate)",
                   3: "treatment row 7, the studio (P69 T15b)", 4: "treatment row 7, their chart (P69 T15b)",
                   5: "treatment rows 8-10, the rehook, the railway index, the GDP recast and the sell ticket over the "
                      "divergence (P69 T16, T17, T18)",
                   6: "treatment rows 11-12, the memo desk: the three records in one slot, then the three-manias table "
                      "(P69 T19, T20)",
                   7: "treatment row 13, reset 1 - the viaduct, 1849 (P69 T21)",
                   8: "treatment row 14, the yardstick: dip 3, camera 2, the breakthrough bars (P69 T22)",
                   9: "treatment row 15, the trigger and the concession: PROP 1 the Fed stamped (P69 T23)"}


def _flow_count(rows: list) -> tuple[int, int, int, int]:
    """(cuts, dips, arrivals, transforms) over the rows' own exits - the transition INTO each row. A `cut` INTO a
    page that arrives by snap / camera is the ARRIVAL's boundary (the snap IS the transition), not a cut."""
    arrivals = sum(1 for r in rows if r[5] == "cut" and (":snap=" in r[2] or ":camera=" in r[2]))
    cuts = sum(1 for r in rows if r[5] == "cut") - arrivals
    dips = sum(1 for r in rows if r[5] == "dip")
    transforms = sum(1 for r in rows if r[5] and r[5] not in ("cut", "dip"))
    return cuts, dips, arrivals, transforms


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
    _sell_ticket_card()   # row 10: the order form's face with SELL stamped across it
    D.register(UBER_CARD, UBER_PNG)   # row 11: the two PNG cards, by id (BODY_DEPARTURES row 11)
    D.register(COO_CARD, COO_PNG)
    D.register(FED_PROP, FED_PROP_FILE)          # row 15: PROP 1, the catalogued cutout, by id
    _manias_card()   # row 12: the table, composed from its own bands
    D.chart_card(BRAVOS_CARD, _hook_object(), BUILD, "line")   # the TWO-LINE page, rendered from the derived object
    D.register(HOST_PLATE_ID, HOST_PLATE_FILE)   # the Flow plate by id (build_render_f.find_asset checks STAMPED first)
    rows = shot_table(ws, unit_end)
    karp_record(ws, T.at(ws, "Alex Karp"))   # row 11: the record's words are filled BEFORE the META is written
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
    # R26-245: a KEN is life (E99 s84 - it is the whole of a long-form plate's life), so the counter
    # reads the ken tuple as well as the `;idle=` token and NAMES which carries each row.
    life = T.life_tokens(rows)
    print("  life        : %d of %d rows (%s)"
          % (len(life), len(rows), "; ".join("row %d %s" % (n, what) for n, what in life) or "NONE - E49"))
    _assert_read_only(read_only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Tokyo Tea Break, v3 - THE SECOND LOOK (E99 s79; `REBUILD-TREATMENT-V2.md` "## v3 - the second look").

    python build_short_v3.py            # -> build-v3/

The operator on the v2 render, with VidIQ's pre-publish read beside it: *"we actually are missing a lot of the life
mechanics - the charts don't have life, the titles/labels don't have life, we aren't using much/if any pans/camera
work/kens burns. also, the short should probably open on the chart axes, we can easily dock the tea clip in the
chart's empty space."* Measured on v2's own table: ONE idle token in the whole cut.

This is `build_short_v2.py` EXACTLY - which is `build_short.py` exactly - with v3's four changes and nothing else, in
the same pattern: the module below is IMPORTED, its `main()` is never called, its live rows are patched, and every
write outside this build dir is redirected or asserted. `build-short/`, `build-v2*/` (including the served frozen
copies and the file of record `build-v2-frozen-c/`), `sound/`, `SHOT-TABLE-SHORT.py`, `build_short.py` are READ ONLY.

THE CHANGES, one named constant each, with the treatment's row and its cite:

  rows 1+2 -> ONE   OPEN_ENTER / TEA_CARD - the holdings page OPENS ON ITS AXES at 0.00 (E73) and the tea clip is
          DOCKED over it as a VIDEO CARD in the plot's own room until "The Fed hasn't moved" (E44's video dock, E65's
          room). The mount goes; so does the separate clip row.
  every page  IDLE_LIVE - `;idle=live` on all four page rows: the board and its titles, labels and figures live (E49).
  the camera  FOCUS_* - a `focus_zoom` on the datum the sentence NAMES (E99 s76; CAPABILITIES:85 the camera, :124 the
          declared targets). The engine allows ONE camera move per row, so the four the treatment lists resolve to
          three taken and one yielded - see FOCUS_YIELDED.
  the captions  unchanged tokens; the axes open puts the opening captions on the charcoal page.

## Recall

- Recall(package): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/REBUILD-TREATMENT-V2.md:32 "the hook's clip; the page mounts over it at 1.99" (v2's row 1, the row v3 folds into the page - the package's first frame becomes the chart with the cup on it)
- Recall(script): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/SCRIPT-90S-VO.claude.txt:17 "So, the second number: it's on your phone. Pull up Meta and find its price-to-earnings multiple" (the script does not move in v3 either; every instant is the take's)
- Recall(voice): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/REBUILD-TREATMENT-V2.md:56 "The take (`scene_1` - Tokyo's take was never tightened" (the recorded take stands; v3 changes no word and no caption token)
- Recall(world): docs/portable/OPERATOR-RULINGS.md:2342 "The hook opens on its axes and is answered on the ledger" (E73 - the open; the calendar cut's row 1 carries the `:axes` syntax)
- Recall(evidence): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/evidence/objects/ev-japan-holdings-v1.series.json:2 "Our biggest customer is selling" (the page that is now the first frame; its series declares crimson at :36, which E67 paints #FF8A4C)
- Recall(motion): docs/portable/OPERATOR-RULINGS.md:1494 "Nothing ever goes truly still: every held thing carries a named subtle idle" (E49 - `;idle=live` on every page row; the desk plate keeps its drift and its Ken Burns)
- Recall(sound): content/video_engine/scripts/authoring/audio.py:429 "the cues the frame plays, the cues dropped" (the cues are re-derived from the v3 rows and bound to what the compiled timeline plays)
- Recall(publish): docs/portable/OPERATOR-RULINGS.md:3268 "a build is FROZEN AS A COPY the moment it is served for a card" (v3 serves nothing and cards nothing; `build-v2-frozen-c` stays the file of record until the operator says otherwise)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3276 "the short opens on the chart's axes with the tea clip docked in the chart's empty room" (E99 s79 - the brief for this build)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3270 "a light with nothing specific to point at is not applied" (E99 s76 - and its converse here: the camera goes only where the sentence names the thing)
- Recall(rulings): docs/content-video-engine/CAPABILITIES.md:85 "one persistent 2D similarity per timeline" (the camera; `kinetics/camera.mjs`, the state the focus moves)
- Recall(rulings): docs/content-video-engine/CAPABILITIES.md:124 "the targeting law as code" (CAPABILITIES:124 - a pointing species carries a DECLARED target, so a focus names its datum)
- Recall(rulings): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py:139 "use the chart plate/ledger AND THEN DOCK the animation videos" (E44, the operator 2026-09-06; :141-142 - a dock asset that resolves to an .mp4 becomes a VIDEO dock in the compiler)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:2120 "the page's own room" (E65 - the tea card lands in the plot's own room, never on the axes or the title)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3248 "A plate's life is DIRECTIONAL" (E99 s65 - the desk plate's Ken Burns and drift stand, unchanged from v2)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:1361 "the mount is the transition into a full-page ledger" (E45 - the mount v3 retires, and the rule that the approved and frozen dirs are never written)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

BUILD_DIR = "build-v3"
_ASKED = os.environ.setdefault("TOKYO_BUILD_DIR", BUILD_DIR)
if _ASKED != BUILD_DIR:
    raise SystemExit(f"FAIL: the v3 rebuild builds {BUILD_DIR} only (TOKYO_BUILD_DIR={_ASKED!r})")
os.environ.setdefault("SELF_WATCH", "0")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[4] / "content/video_engine/scripts"))

import build_short_v2 as V2   # noqa: E402  v3 takes v2's rows the way v2 takes the approved script's
import lab_build as LB        # noqa: E402

B = V2.B
TIMELINE_NAME = V2.TIMELINE_NAME

# ---------------------------------------------------------------- THE CHANGES (the treatment's v3 table, row by row)

# ROWS 1 + 2 -> ONE ROW (treatment v3 row "1 + 2"; E73 `OPERATOR-RULINGS.md:2342`, E44, E65).
# v2 opened on the counter clip for 1.99 s and mounted the page over it; VidIQ's first note and the operator's own
# read are the same - start on the core visual. So the page IS the first frame, on its axes (the calendar cut's row 1
# carries the syntax: `ledger:<series>:<variant>:<emph>:<quiet>:axes:cut;idle=live`), and the clip becomes a VIDEO
# CARD docked over it. The `:mount=<s>` token goes with the row it belonged to.
OPEN_ENTER = "axes"
OPEN_AT = 0.0
TEA_CARD = "dock-a-counter-tea"          # the hook's own clip, docked instead of taking the frame
TEA_CLIP = "clip-a-counter-tab-v2.mp4"
TEA_OUT_PHRASE = "The Fed hasn't moved"  # 5.18 - the card leaves with its sentence, as the treatment says
TEA_META = {"asset": TEA_CARD, "title": "Tokyo took a tea break", "source": "@StickMike · Money Physics",
            "species": "deck", "badges": []}
# THE CARD'S PLACEMENT is the PLACER's, not mine: the dock carries no `centre`, so the compiler puts it in a room it
# measured off the page's own DOM (`ledger_page.page_boxes` / `card place ... empty [...]` in the build log), which is
# E65's rule and the one the treatment names. Reported on the frame, never assumed.
TEA_PLACE: dict = {}
# The clip's own AUDIO is not used anywhere: a video dock is muted in the player and the episode's only sound is the
# take plus `sound/SOUND-PLAN.json`'s cues - nothing in this module touches either.

# THE PANEL CARD'S ROOM (the parent's ruling on the first v3 build's M27, 2026-09-18; fix (a), the same move that
# cleared the Fed card on row 5). v2 parked row 1's chart top-LEFT and landed the panel in the right room, and that
# held while the panel flew in from the right. v3 adds the tea dock, and the engine assigns a dock's entry side by an
# alternation it owns (`d.side = paired ? "pair" : (flip++ % 2 === 0 ? "r" : "l")`, scene-evidence-engine.mjs:6179 -
# not an authored dial, and the count runs over the timeline's docks, so no row-level ordering reaches it): the panel
# flipped to the LEFT and its 0.46 s flight crossed the page (M27 at 0:09, measured `moving [-137, 306, 624, 254]`
# over the sub and an axis label). So the ROOM moves to meet the flight: the chart parks keeping its RIGHT side
# (`anchor: "right"`, PARK_ANCHORS) and the card lands in the left room the park frees, by the placer's own measure.
# The THROW stays (E99 s71 - the throw is signature); the engine is untouched.
# ================= v3b: THE SLOT - a card follows a card, the chart never stands aside =================
# The operator, 2026-09-18: *"There's no reason that we should make the chart stand aside, when we could simply dock
# the 'blue ties' card in the same slot as the outgoing card."* So row 1 carries NO park at all - the chart is whole
# from 0.00 to 38.96 - and every card on that row lands in the ONE room the placer measured for the first of them.
# THE BOX IS HANDED ON, never re-chosen (the `read-park-build-write` shape): the tea clip card's landed rect, read
# off this build's own placer (`card place : s01.dock-a-counter-tea empty [479, 937, 328, 208]`), is the slot; the
# tea card ends at 5.18, the panel takes that rect at 9.09, the two-fingers card takes it at 36.58.
SLOT_RECT = (479, 937, 328, 208)      # x, y, w, h in stage px - the room the placer chose at 0.00, measured
STAGE_W, STAGE_H = 1080, 1920
# THE ASPECTS DIFFER, so the footprint is kept and each card is FITTED INSIDE it (the brief's own rule). Measured:
# the tea card's box is 328 x 208 (1.58:1 - the room, not the clip: a video dock carries no card_aspect and the
# player covers the box); the PANEL is 4:3, NOT 16:9 - `build_short.DOCK_STILLS` crops its clip to 720 x 540, so
# h/w = 0.750; the two-fingers card is 660/720 = 0.9167 (v2's own authored value). Fitted to the slot's height each
# is 277 x 208 and 227 x 208, centred on the slot's own centre.
# THE SLOT IS THE PANEL'S ONLY, and the measurement is why. The first build of this change handed it to the
# TWO-FINGERS card as well and dropped row 1's second park (36.18, v2's own) with the first: M25 then FAILed -
# *"a bracket label under dock-g-two-fingers at 0:36, 8,264 px, 88 % of the ink; dock-g-two-fingers over the chart's
# data at 0:36, 6,272 px, 18 % of the card"*. By 36.58 the page has RESCALED to the February-June window and its line
# and figures run straight through the slot - the room the placer measured at 0.00 is not a room any more. And the
# operator's line is about a card following a card: at 36.58 the panel has been gone 17 s, so the two-fingers card
# follows nothing. It keeps v2's own measured placement and its own park, exactly as the approved cut has them.
SLOT_ASPECTS = {"dock-c-blue-ties-panel": 0.750}
PANEL_WINDOW_END = 20.0   # the parks this row loses are the ones inside the PANEL's life; v2's 36.18 park stands


def _slot_place(aspect: float) -> dict:
    """The handed-on box: the slot's centre, the card fitted inside its footprint at the card's own aspect."""
    x, y, w, h = SLOT_RECT
    fit_w = min(w, h / aspect)
    return {"centre": True, "card_aspect": aspect,
            "centre_w": round(fit_w / STAGE_W, 4),
            "centre_x": round((x + w / 2) / STAGE_W, 4),
            "centre_y": round((y + h / 2) / STAGE_H, 4)}
# THE SAME FLIP, THE SAME FIX, one row later: the tea dock shifts the alternation for EVERY dock after it, so the
# meta-yield card on row 3 flipped left too and its flight crossed the chart at 66.41 (measured `moving
# [-77, 459, 719, 639]` over the plot and the data). Row 3's park - v2's own, at 66.01 - keeps its RIGHT side and the
# card lands in the left room. Its size and height stay v2's measured ones; only the side of the stage moves.
META_PARK_ANCHOR = "right"
META_PLACE_LEFT = {"centre_x": 0.22}
# ... and ONE ROW FURTHER, the same flip again, this time back the other way: v2 fixed the Fed card by parking the
# meta page RIGHT and landing the card LEFT, because in v2 that card flew in from the left. With the tea dock in the
# count it flies from the RIGHT (measured at 75.79: `moving [609, 407, 322, 530]` across the right-parked chart), so
# v3 puts the meta page's park back on its TOP anchor and the Fed card in the RIGHT room - the mirror of v2's slot,
# same width, same height. Three cards, one rule: the room is made on the side the flight comes from.
FED_PARK_ANCHOR = "top"
FED_PLACE_RIGHT = {"centre_x": 0.75}

# THE 21.5x, AND WHY IT IS NOT A FIGURE (the parent's read of tokyo-v3.16.png; BACKLOG R26-190). The punch at 72.82
# pointed at nothing, and the record says why: *"the engine drops EVERY figure on a `builder story / variant bars`
# page because `buildPerform` (`scene-evidence-engine.mjs:10545`, `if (!pts.length) return null`) needs the page's
# `linePts`, which a bars page never has"*. So v2's `figure 21.5x` on the meta page was in the table and never on the
# frame - in v2 either. It is REMOVED here, and the named thing arrives the way this page CAN render it: the page's
# own ring, with the number as its label, on the bar the multiple belongs to (E56 - a ring circles a NUMBER or a point
# on a chart; the row's other callout is authored exactly so). The page's badges are not a route: they live in the
# evidence object, which this build asserts UNCHANGED (E99 s31 - no image or object reaches the compiler from a row).
MULTIPLE_RING = {"kind": "callout", "dur": 2.4, "pad": -50}   # pad as the row's other ring, to clear the tick band
# A RING IS NOT A LANDING. MEASURED on the first build of this fix: the ring drew and wrote its label (the probe at
# 72.35 carries mark m0 on the 5.5 % bar, `tg: ["pill:$577", "val:$577"]`, with the label "21.5x" at [813, 678, 75,
# 33]) - and at 72.95, the ring's own end, `marks: []`: it had LEFT, so a push anchored on its landing pointed at an
# empty bar, the parent's fault over again. A mark's life is its window, not its end, so the push lands one ring-draw
# after it opens (`RING.DRAW_S` 0.55, scene-evidence-engine.mjs:14400 - mirrored, not invented) and releases before
# the ring closes. The ring's own length grows to 2.4 s so both are on screen together.
RING_DRAW_S = 0.55
MULTIPLE_BAR = "5.5%"        # the emphasised bar - the yield the page is built around
DEAD_FIGURE = "21.5x"        # the species removed, by its text

# THE LIFE (treatment v3 row "every page"; E49 `OPERATOR-RULINGS.md:1494`). v2's table carries ONE idle token - the
# desk plate's drift. The door cut and the calendar cut carry `;idle=live` on EVERY page; Tokyo's rows predate E49 and
# the rebuild carried them as approved. Every ledger row gets it; the desk plate keeps `idle=drift;drift=35` + ken.
IDLE_LIVE = ";idle=live"

# THE CAMERA (treatment v3 row "the camera"; E99 s76, CAPABILITIES:85 + :124).
# THE LAW THAT SHAPES THIS: `validate_species` allows AT MOST ONE camera move (punch | focus_zoom | pull_back) PER ROW
# (`build_scene_timeline_f.py:1562`), and none over an authored Ken Burns. The treatment names four focuses; two of
# them ("Since February"'s bracket at 45.00 and the $1,116.7B print at 50.30-54.09) are on the SAME row, so one of the
# two must yield whatever else is true - and the print yields for a second, independent reason (below).
# Each focus is anchored on the MARK THE SENTENCE NAMES - the row's own species, read out of the table, never typed -
# and holds for that mark's own `dur`, capped so it releases before the next move on that page.
FOCUS_RELEASE_S = 0.10   # the air between the camera's release and the next move on the same page
# THE KIND is the PUNCH, not the focus_zoom, and the frame is why: MEASURED on the first v3 build, a focus_zoom's
# landed frame (the engine's FOCUS_SCALE 1.32) cut the page's own title partway - 57 px off its right edge on row 1,
# 51 px off its left on row 4 - and M43 refuses a cropped word by name ("fully inside reads, fully outside is a choice
# the author made; half of a sentence hanging off the frame edge is neither"). A 9:16 page's title is full width, so
# at 1.32 there is no anchor on the plot that keeps it whole. The punch is the same move at PUNCH_SCALE 1.14 and it
# is E51's own word for it ("a push-in is only used tied to something").
# ... and the MOVE is an AUTHORED CAMERA KEY PAIR, not a camera species, because a species' zoom is not authorable.
# THE RULE (the parent, 2026-09-18, on tokyo-v3-fix.10.png): a push on a page keeps the WHOLE page inside the stage -
# no glyph of the title, sub, cite, axis or pill cropped - and lets no page element enter the caption strip at ANY
# instant of the move. MEASURED with the probe across both punches' lives, at the engine's own PUNCH_SCALE 1.14:
#     s01 (the June print, 27.16-28.66): 26.86 HOLDS | 27.50 title/sub/source/chart OFF by 29 px | 28.10 OFF by 28 px
#                                        | 28.40 source IN-CAPTION | 28.66 HOLDS
#     s04 (the 21.5x, 71.90-73.65):      71.90 HOLDS | 72.10 OFF by 8 px | 72.35 OFF by 21 px | 73.00 OFF by 18 px
#                                        | 73.42 HOLDS
# and the CEILING measured off each page's own DOM box, looking at the datum with the look held in place:
#     s01 page box x 75-998, y 141-1284, caption top 1354 -> the left edge binds at S_MAX 1.110
#     s04 page box x 74-925, y 140-1284, caption top 1368 -> the left edge binds at S_MAX 1.106
#     (centred on the page instead of the datum the ceilings are 1.122 and 1.147, bound by the caption band - the
#      meta page's pill rail ends 5 px above the strip, so no page-centred zoom is worth having either)
# So the zoom is the smaller ceiling with a margin, authored on the row's own camera (`{keys: [{t, zoom, look, ease}]}`,
# where `look` may be a DECLARED TARGET - `validate_camera`:623-630), and the species is dropped: keys and a camera
# species never share a window (s9.28 C3). The clock mirrors the engine's own punch (PUNCH_IN 0.42, PUNCH_OUT 0.5).
CAMERA_ZOOM = 1.09          # under both STAGE-EDGE ceilings - and still over the CAPTION-BAND ones, which bind
# THE SECOND MEASUREMENT, at CAMERA_ZOOM 1.09, is why both pushes are DROPPED. The stage-edge crop went away; the
# CAPTION BAND did not, because the band MOVES: it stands at y 1368 between the moves and at **1297** under a
# two-line caption, and every Tokyo page's own foot is at y 1284 - **13 px of air**. Re-measured across both lives:
#     s01: 27.16 HOLDS | 27.50 source IN-CAPTION | 27.76 source + chart IN-CAPTION | 28.40 source IN-CAPTION
#     s04: 72.10 HOLDS | 72.35 rail IN-CAPTION | 72.70 rail IN-CAPTION | 73.00 rail IN-CAPTION
# and the ceiling that actually binds, looking at the datum against a caption top of 1297:
#     s01 (June datum low on the rescaled plot, y ~1105): s <= (1297-1105)/(1284-1105) = **1.073**
#     s04 (the 5.5 % bar, y ~841):                        s <= (1297- 841)/(1284- 841) = **1.029**
# A 3 % zoom is not a move, and a 7 % zoom costs a mechanism for something a viewer cannot name. So the pushes go and
# the RINGS stay: the named thing still ARRIVES (E99 s71 - the spotlight on the June datum at 19.71, the ring that
# writes 21.5x at 71.35), and s76 is satisfied by the callout, which is what it asks for. NOT a silent drop.
# ================= v3b: THE PUNCH, UNDER THE CORRECTED RULE (the operator, 2026-09-18) =================
# *"why does a punch need to keep the whole page on stage?"* - it does not. A punch is a move INTO the chart and may
# leave the page's edges. The two real faults at 72.35 were a crop line THROUGH A GLYPH ("Vhat", "he same", "ahoo",
# "MET") and the pill row pushed INTO the caption strip. So the rule is:
#   (A) every GLYPH element - title, sub, cite, pill row, every axis tick, value and capsule - is wholly inside the
#       stage or wholly outside it at every instant; the chart's own ink may be cropped, it is what we push into;
#   (B) no page element goes DEEPER into the caption strip than it already sits with no camera at all.
# (B) is written incrementally because it must be: MEASURED at zoom 1.00 with NO camera, the shipped cut already has
# the cite 2 px inside the strip's box on s01 and the pill rail + all three capsules 2 px inside on s04 - identical in
# `build-v2/` and in the posted `build-short/`. An absolute rule would forbid a camera this cut cannot have.
# THE CAPTION HAS NO DOOR FOR THIS. E62's demotion (CAPABILITIES:24 - "the demotion is in POSITION, not in size") is
# written by the compiler on every DOCK entry that carries a caption (`caption_band: {y, h, band}`, the `below` /
# `above` / `quiet` ladder off `free_bands` / `page_boxes`); there is no key for a SPECIES window or a CAMERA key -
# `_dock_live_at` and the band writer both walk `scene["docks"]` only. So the punch anchors instead, which is the
# brief's own fallback.
# SOLVED off each page's own DOM boxes, sweeping zoom 1.00-1.40 and the landing 0-120 px above the look:
#     s01 (look: the June print at 760, 1114; strip 1282-1440) -> largest zoom 1.10, the look landed 40 px up
#     s04 (look: the 5.5 % bar at 790, 688;  strip 1282-1440) -> largest zoom 1.10, the look landed 80 px up
#     for reference, in place and under the ABSOLUTE rule: 1.06 puts the cite/rail in the strip, 1.14 crops the title,
#     1.32 crops the sub (s01) / the title (s04) - which is the parent's read, to the pixel.
# 1.10 is over the brief's ~1.06 floor, so the punches are KEPT. The anchor is the measured landing, as stage
# fractions (`validate_camera`:623-630 takes [x, y] 0..1 or a declared target); the look is the declared datum.
# THE ANCHOR IS THE LOOK ITSELF - no `at`. The first v3b build supplied the measured landing as stage fractions and
# M43 read the frustum at `-189,-165-793,1580`: the DATUM does not resolve where the solver assumed (it took a line
# page's datum as its data box's right edge), so an authored `at` moved the frame 450 px off and cropped the title by
# 205 px. A key with no `at` ZOOMS IN PLACE about whatever world point the engine resolves the datum to
# (`build_scene_timeline_f.py:501`) - which is the one anchor that cannot be measured wrong. The zoom is then found by
# BUILDING and re-measuring every glyph box at every instant of the move, below.
# THE ANCHOR, MEASURED THE ONLY WAY IT CAN BE: off the engine's own resolved camera. `window.__camera(t)` on the
# 1.08 in-place build reports the datum the key looks at as s01 (813.1, 619.5) and s04 (773.8, 836.0) - NOT where a
# solver reading the page's plot box guesses (it put s01's line datum at 760, 1114, 450 px out, which is why the first
# v3b build's frustum read -189,-165-793,1580 and M43 cut the title by 205 px). With the true look in hand the LANDING
# lifts the page just enough to carry the cite / the pill row clear of the strip:
#     s01: in place at 1.08 the cite sits 34 px inside the strip and the title has 102 px of headroom -> land the look
#          45 px high: the cite clears by 11 px, the title keeps 57 px. at = (813.1/1080, 574.5/1920)
#     s04: in place at 1.08 the pill rail sits 21 px inside and the title has 84 px -> land it 30 px high: the rail
#          clears by 9 px, the title keeps 54 px.                      at = (773.8/1080, 806.0/1920)
# 1.08 is over the brief's ~1.06 floor, so both punches are KEPT. Every number here was read off a build and is
# re-read after this one (the per-element table in the report).
PUNCH_S01 = {"zoom": 1.08, "at": [0.753, 0.299], "in_s": 0.40, "out_s": 0.40}
PUNCH_S04 = {"zoom": 1.08, "at": [0.717, 0.420], "in_s": 0.42, "out_s": 0.50}

PUNCH_VERDICT = [
    ("rule (A), the crop line between elements", "SATISFIED at zoom 1.08 with the key zooming IN PLACE about the "
     "engine's own resolved datum: every one of the 9 glyph boxes on s01 and the 18 on s04 is wholly inside the stage "
     "at 26.86 / 27.16 / 27.46 / 27.76 / 28.20 / 28.66 and 71.90 / 72.35 / 72.90 / 73.42 / 73.65 - CROPPED: none, "
     "everywhere, and M43 PASSes. The operator's 'Vhat / he same / ahoo / MET' is gone at 1.08."),
    ("rule (B), nothing deeper into the strip", "NOT SATISFIED above ~1.01. In place at 1.08 the s01 cite sits 34 px "
     "inside the strip and the s04 pill rail + all three capsules 21 px (they already touch it by 2 px with no "
     "camera at all, in v2 and in the posted cut). The depth falls ~2.6-4.3 px per 0.01 of zoom, so it reaches 3 px "
     "at about 1.01."),
    ("the caption's door", "THERE IS NONE for a camera move. E62's demotion (CAPABILITIES:24) is written by the "
     "compiler on every DOCK entry that carries a caption - `caption_band: {y, h, band}` off the below/above/quiet "
     "ladder - and both the band writer and `_dock_live_at` walk `scene['docks']` only. No species window and no "
     "camera key can declare it."),
    ("the anchor", "TRIED TWICE AND MEASURED, and it moves the frame the wrong way. With the landing solved off the "
     "page's plot box M43 read the frustum at -189,-165-793,1580 and the title was cut by 205 px; with the landing "
     "solved off the engine's OWN resolved look (`window.__camera`: s01 813.1,619.5 / s04 773.8,836.0) lifting 45 px "
     "/ 30 px took s04 from 21 px into the strip to 31 and pulled the s01 tick row in as well."),
    ("THE VERDICT", "the largest zoom that satisfies BOTH is ~1.01, under the brief's ~1.06 floor, so - the brief's "
     "own instruction - it is said and the punch stays DROPPED. A zoom that is not a move stays out."),
]
CAMERA_DROPPED_V3A = [
    ("s01, the June print at 27.16", "the page's foot is 13 px above the caption strip; the largest zoom that keeps "
     "every page box out of the band is 1.073, and at the engine's own 1.14 the title, sub, cite and chart left the "
     "stage by 29 px and the cite entered the strip"),
    ("s04, the 21.5x at 71.90", "the same 13 px, and the meta page's pill rail is its foot: the ceiling is 1.029 - "
     "not a move. At 1.14 the page left the stage by 21 px (the parent's read: 'Vhat a Meta share', 'MET')"),
]
# What WOULD let a push hold on this cut, for the record and not for this pass: a page that is PARKED (shorter) under
# the move, or a caption band that yields to a camera move the way a dock's read does (E62). Both are rulings.
CAMERA_IN_S, CAMERA_OUT_S = 0.42, 0.5
FOCUS_KIND = "punch"        # the species this module BUILDS and then converts to keys (so the anchor logic is one)
# THE INSTANT is the named mark's own LANDING, not its onset (E51 / M22: "a push lands ON a thing that just landed";
# the gate ties a push to a landing inside (at - 1.5 s, at + 0.3 s) and counts a build_to / bracket / figure / note
# landing, never a light). Read off the row, never typed.
FOCUS_LENDER = ("figure", "$1,116.7B")  # row 1: the JUNE PRINT - datum 315, the same datum "our biggest lender"
#   names at 19.71 and the light holds. The push cannot sit at 19.71: the only landing near it is the build_to's at
#   20.15 and the page's next move (the un-park into the rescale) is at 20.49, which leaves 0.34 s - a twitch, not a
#   move. It sits instead where the same datum is WRITTEN and its figure lands (27.16), with the sentence still on it
#   ("...and it's been selling since February") and 6 s of air before the retitle. Named, not silently moved.
FOCUS_MULTIPLE = ("callout", None)      # row 4: the ring that WRITES the multiple, at its own landing
# YIELDED, and why - the treatment's fourth focus, the $1,116.7B print over "The Treasury prints the new total
# monthly" (50.30-54.09): (1) its row already spends its ONE camera move on the bracket; (2) at 50.30 the row fires
# `chart_to recast` - the line becomes the monthly bars over 1.4 s - and a camera move inside a chart transform fights
# it; (3) what the sentence names is written as a NOTE in the page's quiet zone, not at a datum (v2's own comment: a
# figure at the June bar crossed the May bar at every dy the plot allows), and a focus takes a DECLARED target
# (CAPABILITIES:124) - there is no datum there to name. Recorded, not silently dropped.
FOCUS_YIELDED = [
    ("the -$122.6B bracket (the treatment says 45.00; nothing is drawn there - the page is 0.12 s into its spiral "
     "arrival and the bracket draws at 46.72)",
     "its row ALREADY SPENDS its camera: attention=landings pulls the eye onto the meta-yield card as it lands at "
     "66.87 and carries it into the snap - the throw-then-zoom's own eye path (E99 s71, Tokyo's signature). "
     "validate_camera_row refuses both on one row BY NAME: 'attention landings and a focus_zoom species on one row - "
     "the landing IS the camera's move (E51, s9.28 C3)'. The signature keeps the row."),
    ("the $1,116.7B print, 50.30-54.09",
     "three reasons, any one enough: its row's one camera move is already spoken for (above); a chart_to recast fires "
     "at 50.30 and a camera move inside a chart transform fights it; and what the sentence names is written as a NOTE "
     "in the page's quiet zone, not at a datum - a focus takes a DECLARED target (CAPABILITIES:124) and there is none "
     "there to name."),
]
# (The first v3 build made row 1's `attention: landings` yield to a focus species; with the pushes dropped there is
# nothing to yield to and the pull stands as the approved cut authored it.)


def _guard(rows: list[list]) -> None:
    """v3 was authored on v2's own table; if v2's rows moved underneath, stop (v2's guard, one level up)."""
    if len(rows) != 7:
        raise SystemExit(f"FAIL: v2's table has {len(rows)} rows, v3 was authored on 7")
    if not str(rows[0][2]).startswith("clip:") or ":mount=" not in str(rows[1][2]):
        raise SystemExit(f"FAIL: v2's rows 1-2 are {str(rows[0][2])[:40]!r} / {str(rows[1][2])[:60]!r}, "
                         "expected the counter clip and the mounting holdings page")


def _species(row: list, kind: str, text: str | None = None) -> dict:
    """One species of a row, by kind (and by its text where a row carries more than one of a kind)."""
    hits = [s for s in (row[6] or []) if s.get("kind") == kind and (text is None or s.get("text") == text)]
    if len(hits) != 1:
        raise SystemExit(f"FAIL: row expected exactly one {kind}{'' if text is None else ' ' + text!r}, found {len(hits)}")
    return hits[0]


def _focus(row: list, kind: str, text: str | None = None) -> dict:
    """A `focus_zoom` on the mark the sentence names: its instant and its target are that mark's, its length that
    mark's own `dur` capped so the camera releases before the next move on the page (the treatment's rule)."""
    hits = [sp for sp in (row[6] or []) if sp.get("kind") == kind and (text is None or sp.get("text") == text)]
    mark = hits[-1] if len(hits) > 1 and text is None else _species(row, kind, text)
    # a mark that LANDS (build_to, bracket, figure, note) is pushed into at its landing (E51 / M22); a RING lives for
    # its window and is gone at its end, so its push lands one draw after it opens, while it is still on the page.
    at = round(float(mark["at"]) + (RING_DRAW_S if kind == "callout" else float(mark.get("dur") or 0.0)), 2)
    later = [float(s["at"]) for s in (row[6] or []) if float(s["at"]) > at + 1e-6]
    room = (min(later) - at - FOCUS_RELEASE_S) if later else (float(row[1]) - at - FOCUS_RELEASE_S)
    life = float(mark.get("dur") or 1.0) - (RING_DRAW_S if kind == "callout" else 0.0) - FOCUS_RELEASE_S
    dur = round(min(max(0.4, life), max(0.4, room)), 2)
    # a mark with a declared target lends it; a BRACKET declares none - it spans two data, and what the sentence
    # lands on is its far end ("...has sold a hundred and twenty-two billion dollars of it, a tenth of the pile"),
    # so the camera takes that datum. Never a coordinate this module invented (CAPABILITIES:124).
    target = mark.get("target") or {"kind": "datum", "index": int(mark["to"])}
    return {"kind": FOCUS_KIND, "at": round(at, 2), "dur": dur, "target": dict(target)}


def _camera(move: dict, dial: dict) -> dict:
    """The row camera that a camera SPECIES would have been: in over the engine's own PUNCH_IN, held for the move's
    window, out over its PUNCH_OUT, looking at the same DECLARED target, at a zoom measured to keep the whole page on
    the stage and out of the caption strip (CAMERA_ZOOM). The species is not emitted - keys and a species never share
    a window (`validate_camera_row`, s9.28 C3)."""
    t0, t1, look = float(move["at"]), round(float(move["at"]) + float(move["dur"]), 2), move["target"]
    z, at, i_s, o_s = dial["zoom"], dial.get("at"), dial["in_s"], dial["out_s"]
    key = lambda t, zoom, ease: {"t": round(t, 2), "zoom": zoom, "look": dict(look), "ease": ease,
                                 **({"at": list(at)} if at else {})}
    return {"keys": [{"t": round(t0, 2), "zoom": 1.0, "look": dict(look), "ease": "cubic"},
                     key(t0 + i_s, z, "cubic"), key(t1 - o_s, z, "hold"),
                     {"t": t1, "zoom": 1.0, "look": dict(look), "ease": "cubic"}]}


def shot_table(ws: list[dict], runtime_s: float, t_outro: float) -> list[tuple]:
    """v2's rows with v3's four changes patched in, and nothing else touched."""
    rows = [list(r) for r in V2.shot_table(ws, runtime_s, t_outro)]
    _guard(rows)

    # --- THE OPEN: rows 1 and 2 become one row that starts on the page's axes, with the clip docked over it
    page = rows[1]
    page[0] = OPEN_AT
    page[2] = re.sub(r":mount=[0-9.]+:", f":{OPEN_ENTER}:", str(page[2]), count=1)
    page[5] = rows[0][5]                         # the first row takes no transition INTO it (v2's row 1 carried None)
    clip = B.D.seekable_clip(TEA_CLIP, B.CLIPS / TEA_CLIP, B.BUILD)   # the same bytes v2's row 1 played, keyframed
    tea = (B.D.dock_still(TEA_CARD, clip, B.BUILD, still=False), 0, OPEN_AT, B.W.at(ws, TEA_OUT_PHRASE), dict(TEA_PLACE))
    # THE TEA CARD GOES LAST in the row's dock list, and the frame is why: the engine assigns a dock's ENTRY SIDE
    # by its position in that list (`d.side = paired ? "pair" : (flip++ % 2 === 0 ? "r" : "l")`,
    # scene-evidence-engine.mjs:6179 - not an authored dial). Put first, it flipped the PANEL's throw from the
    # right to the left and its flight crossed the whole page at 9.09 (M27, measured on the first v3 build:
    # moving box [-137, 306, 624, 254] over the sub and an axis label). Last, the panel and the fingers keep the
    # sides they had in v2 and the tea card - which springs, and takes no side - is unaffected.
    page[4] = [tuple(d) for d in page[4]] + [tea]
    # the page's own build now runs on the AXES clock (the engine's own offset - `gate_motion_density._page_land_offset`:
    # "P53 T1: the page is there on frame 0 and the DATA is what builds"), so the authored `build_to` to the February
    # peak moves with it and the two stay one build, exactly as they were under the mount. Never a typed instant.
    axes_land = B.MG._page_land_offset({"world": {"kind": "ledger", "page": {"enter": OPEN_ENTER}}})
    peak_build = _species(page, "build_to", None) if False else next(
        s for s in page[6] if s.get("kind") == "build_to" and s["target"]["index"] == B.PEAK_IDX)
    peak_build["at"] = round(OPEN_AT + axes_land - B.PAGE_BUILD_S, 2)
    del rows[0]

    # --- THE SLOT: row 1 loses every park, and each card after the tea clip takes the tea clip's own rect
    page[6] = [sp for sp in page[6]
               if not (sp.get("kind") == "chart_to" and sp.get("to") == "park" and float(sp["at"]) < PANEL_WINDOW_END)]
    page[4] = [tuple(list(d[:4]) + [dict(d[4], **_slot_place(SLOT_ASPECTS[d[0]]))]) if d[0] in SLOT_ASPECTS else tuple(d)
               for d in page[4]]

    # --- THE META CARD'S ROOM: row 3's park keeps its RIGHT side and the card lands in the left room
    spiral = rows[2]
    for sp in spiral[6]:
        if sp.get("kind") == "chart_to" and sp.get("to") == "park" and float(sp["at"]) > 60.0:
            sp["anchor"] = META_PARK_ANCHOR
    spiral[4] = [tuple(list(d[:4]) + [dict(d[4], **META_PLACE_LEFT)]) if d[0] == "dock-l-meta-phone" else tuple(d)
                 for d in spiral[4]]

    # --- THE FED CARD'S ROOM: the meta page's park goes back to its top anchor, the card to the right room
    meta_row = rows[3]
    for sp in meta_row[6]:
        if sp.get("kind") == "chart_to" and sp.get("to") == "park":
            sp["anchor"] = FED_PARK_ANCHOR
    meta_row[4] = [tuple(list(d[:4]) + [dict(d[4], **FED_PLACE_RIGHT)]) if d[0] == "dock-h-fed-vs-yields" else tuple(d)
                   for d in meta_row[4]]

    # --- THE MULTIPLE: the dead figure out, the page's own ring in (R26-190; E56)
    facts = json.loads((HERE / "evidence/objects/ev-meta-yield-v1.series.json").read_text(encoding="utf-8"))
    bar = next(i for i, b in enumerate(facts["bars"]) if b["label"] == MULTIPLE_BAR)
    label = f"{facts['facts']['implied_pe'][MULTIPLE_BAR]}x"
    keep = [sp for sp in meta_row[6] if not (sp.get("kind") == "figure" and sp.get("text") == DEAD_FIGURE)]
    if len(keep) == len(meta_row[6]):
        raise SystemExit(f"FAIL: no dead `figure {DEAD_FIGURE}` on the meta row - v2's table moved under this fix")
    ring_at = max(round(float(sp["at"]) + float(sp.get("dur") or 0.0), 2)
                  for sp in keep if sp.get("kind") == "callout")      # after the row's first ring closes
    meta_row[6] = keep + [{**MULTIPLE_RING, "at": ring_at, "target": {"kind": "datum", "index": bar}, "label": label}]

    # --- THE LIFE: `;idle=live` on every page row (E49); the desk plate keeps its drift and its Ken Burns
    for r in rows:
        if str(r[2]).startswith("ledger:") and IDLE_LIVE not in str(r[2]):
            r[2] = str(r[2]) + IDLE_LIVE

    # --- THE CAMERA: one focus per page row, on the mark the sentence names
    pages = [r for r in rows if str(r[2]).startswith("ledger:")]
    holdings, meta = pages[0], pages[2]
    # v3b VERDICT: BOTH PUNCHES STAY DROPPED, by the brief's own floor - see PUNCH_VERDICT. Rule (A) is satisfiable
    # (1.08 in place crops no glyph at any instant); rule (B) is not (the strip caps the zoom at ~1.01, under 1.06),
    # the caption has no door for a camera move, and the anchor makes it worse, measured twice. Row 1 keeps
    # `attention: landings` - v2's own, with no camera species to yield to.
    _ = holdings, meta, PUNCH_S01, PUNCH_S04, _camera
    return [tuple(r) for r in rows]


def main() -> int:
    EP, BUILD = B.EP, B.BUILD
    if BUILD.resolve() != (HERE / BUILD_DIR).resolve():
        raise SystemExit(f"FAIL: build_short resolved its build to {BUILD}, not {HERE / BUILD_DIR}")
    A, T, W = B.A, B.T, B.W

    ws = W.take_words(EP)
    EP.mkdirs()
    shutil.copy2(B.TAKE / "scene_1.mp3", EP.audio_master)
    W.write_timeline(EP, ws, A.probe_duration(EP.audio_master))
    tl_built = W.apply_edit_pauses(EP, B.EDIT_PAUSES)
    ws = W.shifted_words(EP)
    line_s = A.probe_duration(B.BRAND_LINE)
    t_outro, t_line, runtime_s = A.outro_clock(tl_built["runtime_s"], line_s, outro_lead=B.OUTRO_LEAD,
                                               outro_s=B.OUTRO_S, brand_gap=B.BRAND_GAP, brand_tail=B.BRAND_TAIL)
    audio = BUILD / tl_built.get("paused_audio", "audio/episode.mp3")
    A.stitch_brand_line(audio, B.BRAND_LINE, B.BRAND_GAP, runtime_s)
    tl_built["runtime_s"] = runtime_s
    W.save_timeline(EP, tl_built)
    print(f"  v3 rebuild  : card at {t_outro:.2f}s; runtime {runtime_s:.2f}s; build {BUILD}")

    V2._assert_evidence_unchanged()
    T.caption_pages(BUILD, char_budget=28, max_words=6)
    rows = shot_table(ws, runtime_s, t_outro)
    for meta in (V2.CARD_META, TEA_META):
        if not any(m["asset"] == meta["asset"] for m in B.DOCK_META):
            B.DOCK_META.append(dict(meta))
    (BUILD / "evidence-dock.json").write_text(json.dumps(B.DOCK_META, indent=1), encoding="utf-8")

    table = BUILD / "SHOT-TABLE-SHORT.py"
    T.write_shot_table(table, rows,
                       '"""Tokyo short, v3 - GENERATED by build_short_v3.py. Do not hand-edit."""\n'
                       "# E99 s79: the axes open with the tea clip docked, idle=live on every page, the camera on the named things\n")
    T.print_rows(rows, show_docks=True)
    idles = [(i + 1, str(r[2]).partition(";")[2]) for i, r in enumerate(rows) if ";idle=" in str(r[2])]
    print(f"  idle tokens : {len(idles)} of {len(rows)} rows carry one - " +
          "; ".join(f"row {n} {o}" for n, o in idles))
    print("  camera      : v3b - both punches DROPPED (" + PUNCH_VERDICT[-1][1][:96] + ")" +
          " | YIELDED: " + "; ".join(w for w, _why in FOCUS_YIELDED))

    V2._receipt_is_this_module()
    import recall_verify as RV
    _inner = RV.resolve_ledger
    RV.resolve_ledger = lambda target: Path(__file__) if Path(target).resolve() == HERE else _inner(target)
    rc = T.compile_timeline(
        HERE, BUILD, timeline_name=TIMELINE_NAME, shot_table_file=os.path.relpath(table, HERE),
        title="Tokyo Tea Break", subtitle="Money Physics · short", episode_id="tokyo-tea-break",
        aspect="9:16", caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False,
                  "curvature_stroke": True})
    if rc:
        return rc

    plan_path, cues = LB.write_cue_plan(B, BUILD, rows, table)
    for note in LB.embed_cues(B, BUILD, cues, TIMELINE_NAME):
        print(f"  [sound] {note}")
    print(f"  cue plan    : {len(cues)} cues re-derived into {plan_path.name} and embedded in {TIMELINE_NAME}")
    print(f"  beat plan   : {V2._restamp_beat_plan(BUILD, rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

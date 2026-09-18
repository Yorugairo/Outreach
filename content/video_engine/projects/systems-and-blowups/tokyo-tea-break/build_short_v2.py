"""Tokyo Tea Break, v2 - THE REBUILD, built by hand from `REBUILD-TREATMENT-V2.md` (E99 s77 Apply 7).

    python build_short_v2.py            # -> build-v2/

The operator: *"we made tokyo tea before we had polished capabilities, but we know the structure is better than the
one-shot."* So this is `build_short.py` EXACTLY - the same take, script, captions, seven worlds, seven rows, plates,
beds and outro - with today's polish applied row by row, in the pattern `japan-tariff-trick/build_short_door.py` set
("the same script with two changes"): the approved module is IMPORTED, its `main()` is never called, its live rows are
patched, and every write it would make outside the build dir is redirected, asserted or switched off. The approved
`build-short/`, `sound/`, `SHOT-TABLE-SHORT.py` and `build_short.py` are READ ONLY (E45).

THE CHANGES, one named constant each, with the treatment's row and its cite (nothing else moves):

  row 2   PANEL_PARK / PANEL_PLACE - the panel card keeps its throw and now lands in the page's own ROOM: the chart
          PARKS to make it (E65) and un-parks into the rescale; the card leaves at the rescale.
  row 3   MELT (into row 3) / PLATE_KEN + PLATE_DRIFT / PHONE_POINT - the suck becomes `melt:splash:plate` (E88), the
          desk plate goes directional-alive (E99 s65) and the light lands on the phone the sentence names (E99 s76).
  rows 4->5  CARD / SNAP_TRANSITION - the dip into a mount is gone: the meta-yield page's own chart card is THROWN
          onto the held row 4 at "it's on your phone" and the page SNAPS up out of it at "Pull up Meta"
          (`card-becomes-the-chart` as amended by E99 s72 - throw, land, snap, no veil). `mount=2.43` goes.
  row 5   YIELD_FIGURE_BAR - the multiple at the emphasised bar lands as a `figure`, read out of the object's facts.
  rows 1, 6, 7 and every other species, dock, dial and cue: UNCHANGED.

WHAT THIS FILE NEVER WRITES. `build_short.main` writes the episode's `SHOT-TABLE-SHORT.py` and `sound/SOUND-PLAN.json`
and re-copies `evidence/objects/`; all three are the approved cut's. Here the shot table is written INSIDE the build,
the cue plan is re-derived into the build's private `SOUND-PLAN.json` and embedded into the build's own timeline
(`lab_build.write_cue_plan` / `embed_cues` - the lab's own door, since the compiler reads the EPISODE's plan), and the
evidence objects are asserted identical instead of re-copied. `SELF_WATCH` is off.

## Recall

- Recall(package): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/REBUILD-TREATMENT-V2.md:32 "the hook's clip; the page mounts over it at 1.99" (row 1 is UNCHANGED - the package, the hook bed and the open on the clip are the approved cut's)
- Recall(script): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/SCRIPT-90S-VO.claude.txt:17 "So, the second number: it's on your phone. Pull up Meta and find its price-to-earnings multiple" (the two sentences the 4->5 change is cut on; the script itself does not move)
- Recall(voice): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/REBUILD-TREATMENT-V2.md:56 "The take (`scene_1` - Tokyo's take was never tightened" (the recorded take stands as recorded; every instant here is measured off it)
- Recall(world): docs/content-video-engine/CAPABILITIES.md:37 "THE MELT EXIT, REWORKED TO E88: THE CHART MELTS, THE BOARD STAYS" (E88's `melt:splash:plate` - the desk plate grows through the stains where the suck was)
- Recall(evidence): content/video_engine/projects/systems-and-blowups/tokyo-tea-break/evidence/objects/ev-japan-holdings-v1.series.json:2 "Our biggest customer is selling" (the holdings object the page draws; its series declares the colour crimson at :36, which E67 paints the Claude orange #FF8A4C - so the page reads E67 by its own file, no row change owed)
- Recall(motion): content/video_engine/scripts/build_scene_timeline_f.py:2187 "names the transition INTO the scene it sits on" (so the melt is written on ROW 3's column, not row 2's)
- Recall(sound): content/video_engine/scripts/authoring/audio.py:429 "the cues the frame plays, the cues dropped" (the cues are re-derived from the v2 rows and then BOUND to what the compiled timeline actually plays)
- Recall(publish): docs/portable/OPERATOR-RULINGS.md:3268 "a build is FROZEN AS A COPY the moment it is served for a card" (this build serves nothing and cards nothing; the frozen copy is the parent's step)
- Recall(rulings): docs/content-video-engine/CAPABILITIES.md:34 "THE CHART'S INKS ARE ELECTRIC; THE CHART IS THE THUMBNAIL (E67)" (the inks are the default; a series declares a colour only to say something)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3248 "A plate's life is DIRECTIONAL" (E99 s65 - the Ken Burns lean plus the drift on the desk plate, shorts 30-40 px)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3260 "the throw is a signature event and a thrown full-page card zooms or pushes to full screen" (E99 s71 - the meta card is thrown and then becomes the page)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3262 "We don't do a fade/dip before what is already it's own transition." (E99 s72 - the dip into the meta mount goes; the snap is the arrival)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3266 "the whole point of creating them was to improve our ability to live with less cuts" (E99 s74 - the melt and the snap replace a suck and a dip)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:3270 "a light with nothing specific to point at is not applied" (E99 s76 - the only new light is on the phone the sentence names)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:2120 "the page's own room" (E65 - the panel card lands in the room the park makes, never on the ink)
- Recall(rulings): docs/portable/OPERATOR-RULINGS.md:1361 "the mount is the transition into a full-page ledger" (E45 - row 1->2 is unchanged, and the approved build dir is never touched)
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

BUILD_DIR = "build-v2"
if os.environ.setdefault("TOKYO_BUILD_DIR", BUILD_DIR) != BUILD_DIR:
    raise SystemExit(f"FAIL: the v2 rebuild builds {BUILD_DIR} only (TOKYO_BUILD_DIR={os.environ['TOKYO_BUILD_DIR']!r})")
os.environ.setdefault("SELF_WATCH", "0")   # the one-shot bar is the parent's read here; this module compiles and gates

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[4] / "content/video_engine/scripts"))

import build_short as B      # noqa: E402  the approved module: its rows, take, docks, captions, cues and dials
import lab_build as LB       # noqa: E402  the private cue plan + the embed into the build's own timeline

TIMELINE_NAME = "tokyo-short.timeline.json"

# ---------------------------------------------------------------- THE CHANGES (the treatment's table, row by row)

# ROW 2 (treatment row 2; E65 + E99 s71 / s72 Apply 2). The panel card already ARRIVES by a throw with a paper mass in
# the approved cut - what it lacked was a ROOM: it was thrown at 9.09 onto a full-size, finished chart. So the page
# PARKS to make the room (the same mechanism and dials the approved row 4 parks with at 56.7 and row 2's own park at
# 36.18: scale 0.55, anchor top), the card lands in that room - the slot row 2's own two-fingers card was MEASURED
# into on the P48 build ("the card at 0.42 of the stage sits centred at (0.76, 0.316), clear of the sub above
# (242-342) and the parked plot, over nothing") - and it leaves at the RESCALE, where the page un-parks and takes the
# whole stage back for the February-June window.
PANEL_PARK_LEAD_S = 0.4          # the park begins this long before the card is thrown (row 2's own park lead)
PANEL_PARK = {"kind": "chart_to", "dur": 0.9, "to": "park", "scale": 0.55, "anchor": "top"}
PANEL_UNPARK = {"kind": "chart_to", "dur": 0.5, "to": "park", "scale": 1.0, "anchor": "top"}
PANEL_UNPARK_LEAD_S = 0.6        # ... and the page is full again before the rescale's 1.4 s begins
# MEASURED on the first v2 probe (`build-v2/layout-probe.json`, 2026-09-17): the card rests at [591, 434, 459, 282]
# and the un-parked page's chart is [77, 373, 803, 855] - they overlap for the 0.6 s the page takes to grow. So the
# card LEAVES INTO the rescale: its retract begins a second before the un-park's onset, and the page grows onto a
# bare sheet (M25 / M27 are fixed on the frame, never named - E99 s75 Apply 1).
PANEL_OUT_LEAD_S = 1.6           # the card's retract begins this long before the rescale (the un-park is at -0.6)
PANEL_PLACE = {"centre": True, "card_aspect": 0.75,   # the panel clip's own crop, 540/720 (build_short.DOCK_STILLS)
               "centre_w": 0.42, "centre_x": 0.76, "centre_y": 0.316}

# ROW 3's ENTRY (treatment row 2->3; E88, CAPABILITIES:37; the convention - the column names the move INTO the row)
MELT = "melt:splash:plate"       # the ink balls up and the desk paints up through the stains (was `suck:0.49,0.55`)
# ROW 3 (treatment row 3; E99 s65 - the calendar cut's own dials, `memory-trades-the-calendar/build_short.py:61-62`)
PLATE_KEN = (0.06, 6, -4)        # the PLATES' lean: a held plate's life is DIRECTIONAL
PLATE_DRIFT = 35                 # shorts walk 30-40 px
PLATE_IDLE = f";idle=drift;drift={PLATE_DRIFT}"
# ... and the light on the phone (E99 s76: the sentence names it). MEASURED on the plate's own still
# (`omni-video/stills/still-p1-viewers-desk-raw-2.png`, 768x1376): the phone is x 78-210, y 518-690 - the same box the
# approved `trace` species already draws the red line inside (x 0.117-0.26, y 0.39-0.485). Its centre is the point.
PHONE_POINT = {"kind": "point", "x": 0.189, "y": 0.437}
PHONE_LIGHT_S = 1.0
PHONE_WORD = ("and your phone", "phone")   # the light lands as the word finishes (41.08 - the treatment's instant)

# ROWS 4 -> 5 (treatment row 4->5; E99 s71 + s72, E47; `effects/recipes/card-becomes-the-chart.json` as amended).
# The approved cut DIPPED into the meta page's mount - a dip into a mount, the one thing E47 forbids, and a veil before
# a transition that is its own door (s72). Instead the NAMED THING ARRIVES: row 4 holds through "the money went home,
# and the tab stayed here." and "So, the second number:"; at "it's on your phone" the meta-yield page's own chart card
# is THROWN onto the held page (paper, the recipe's `arrival:throw`); it lands ~0.8 s later; and at "Pull up Meta and
# find its price-to-earnings multiple:" the page SNAPS up out of that card's own rectangle and IS the world.
CARD = "dock-l-meta-phone"       # the meta-yield page rendered once as a portrait card (D.chart_card, as dock-h is)
CARD_THROW_WORD = "it's on your phone"      # 66.41 - the throw
SNAP_WORD = "Pull up Meta"                  # 67.82 - the snap; row 5 begins here, row 4 ends here
# MEASURED on the first v2 probe: thrown onto the UN-PARKED page the card rested at [478, 929, 328, 574], across the
# ten-year bars' data, the source line and an axis label (M25 + M27). So row 4 PARKS to make the room, exactly as
# row 2 now does for the panel (E65; E99 s72 Apply 2 - a card is placed scene-aware, never over the ink): the parked
# chart holds x 30-502, y 353-855, and the card takes the room to its right, clear of the sub above (242-342) and of
# the source line below (1249). Its aspect is the rendered card's own (`D.card_aspect`), never guessed.
CARD_PARK_LEAD_S = 0.4
CARD_PARK = {"kind": "chart_to", "dur": 0.9, "to": "park", "scale": 0.55, "anchor": "top"}
# ... and the SLOT is sized by the throw's own overshoot, measured on the second v2 probe: at the settle (66.91) the
# card stretches to 1.22x its resting height about its foot, so its rest must sit low enough that the stretched top
# clears the page's sub (y 338) and its foot high enough to clear the stage caption (y 1297). 0.38 of the stage is
# the widest slot that satisfies both: w 410, h 728, resting y 542-1270, x 605-1015 - clear of the parked chart
# (x 75-520), of the parked source line (x 75-454, y 857-875) and of the caption band.
CARD_PLACE = {"arrive": "throw", "mass": "paper",   # the door cut's row-1 syntax, and row 5's own Fed card's
              "centre": True, "centre_w": 0.38, "centre_x": 0.75, "centre_y": 0.472}
CARD_META = {"asset": CARD, "title": "What a Meta share is worth as the 10-year moves",
             "source": "Yahoo Finance · FRED DGS10 · 2026-09", "species": "chart", "badges": []}
SNAP_TRANSITION = "cut"          # the snap is this row's own transition, in its plate id (japan's rows 2 and 6)

# ROW 5's OWN CARD, THE FIX PASS (the parent's read, 2026-09-17; E63 / M27 / E99 s72 Apply 2). The approved cut throws
# `dock-h-fed-vs-yields` with NO placement, so the placer rests it at [135, 264, 808, 1455] - all but the whole stage,
# across the Meta page's plot, its data, its three pills, its title, its sub, its source line and the caption band. The
# Meta page has NO lower room to land it in: MEASURED at 76.25 the page fills title 153-307, sub 323-424, chart 456-1062,
# source 1086-1118, rail (the pills) 1142-1292 and the caption 1297-1455, so there is no band between the cite and the
# caption at all. The room is MADE, the way rows 2 and 4 now make theirs: the Meta page PARKS before the throw and the
# Fed card lands in the room the park frees. The camera push (row 6's `camera=dock-h-fed-vs-yields`) follows the card
# wherever it lands - it zooms from the card's own rect.
# THE SLOT, MEASURED on the parked page (probe at 76.25): the chart parks to x 81-524 / y 456-790 and its cite to
# y 803-821, but the RAIL of three pills does NOT park - it stays at [81, 1142, 806, 150]. So the room is the band to
# the RIGHT of the parked chart and ABOVE the rail, and the card's own throw overshoot (1.22x its height about its
# foot, measured at 76.29) must still clear the page's sub at y 424. Solving both: h < 588 and the foot < 1142 ->
# 0.28 of the stage, w 302, h 555, resting x 659-961 / y 573-1128. The park also runs 1.2 s EARLY so the page has
# finished parking before the card flies in (at a 0.4 s lead the card entered across a chart still shrinking).
FED_PARK_LEAD_S = 1.2
# ... and the park keeps the RIGHT side (`anchor: "right"`, PARK_ANCHORS), not the top: the dock's throw enters from
# the LEFT here (the engine alternates a dock's entry side itself - `d.side = flip++ % 2 === 0 ? "r" : "l"`, not an
# authored dial), so a top-left park put the flight straight across the parked chart. Parked right, the chart keeps
# the right of the stage and the card flies into the room on the LEFT it never crosses.
FED_PARK = {"kind": "chart_to", "dur": 0.9, "to": "park", "scale": 0.55, "anchor": "right"}
# the slot re-measured on the parked-RIGHT page (probe at 76.25): the chart keeps x 443-888 / y 456-789 but the page's
# SOURCE LINE does not park - it stays at [80, 1086, 459, 32] under the left room, and the rail of pills at y 1142. So
# the card's foot must clear 1086 and its 1.22x throw overshoot must still clear the sub at y 424: w 270, h 496,
# resting x 135-405 / y 580-1076, 47 px of air above the sub and 10 below the cite.
FED_PLACE = {"centre": True, "centre_w": 0.25, "centre_x": 0.25, "centre_y": 0.431}

# ROW 5's CALLOUT, THE FIX PASS (M34; the operator, C09-R003: "the callout owns its position"). MEASURED at 70.35: the
# ring's ellipse is `e: [309, 818, 76, 194]` - its half-height is the BAR's (`ry = b.h/2 + RY_PAD`, the engine's
# `ringEllipse`), so it reaches y 1012 and crosses the "4%" tick at [280, 1004, 58, 44] by 8 px. The ring's own target
# is the VALUE ($665, `tg: ["val:$665"]`), not the bar's foot, so the fix is the ring's own pad: `pad` enters
# `ringEllipse` as `rx + pad` and `ry + pad * 0.4`, and -50 lifts the ellipse's foot 20 px clear of the tick band while
# rx floors on MIN_RX 54 and the ring stays married to the $665 it circles (E56 - a ring circles a NUMBER).
CALLOUT_PAD = -50

# ROW 5 (treatment row 5; E50 - a figure with its sentence). At "that's the share of the price that's profit not yet
# earned, and a higher yield discounts it." (71.22) the multiple AT THE EMPHASISED BAR - the 5.5 % yield the page is
# built around - writes as a figure. The number is read out of the object's own facts (`implied_pe`), never typed, and
# it is a MULTIPLE where all three badges carry dollars, so it repeats nothing the page already says.
YIELD_FIGURE_SENTENCE = "that's the share of the price"   # 71.22
YIELD_FIGURE_BAR = "5.5%"
YIELD_FIGURE_S = 1.6


def _word_end(ws: list[dict], phrase: str, word: str) -> float:
    """The instant a word FINISHES (the treatment's 41.08 is the end of "phone."), off the take's own clock."""
    t0 = B.W.word_in(ws, phrase, word)
    for w in ws:
        if abs(float(w["start_s"]) - t0) < 1e-6:
            return round(float(w["end_s"]), 2)
    raise SystemExit(f"FAIL: no word starting at {t0} for {word!r} in {phrase!r}")


def _meta_facts() -> dict:
    return json.loads((HERE / "evidence/objects/ev-meta-yield-v1.series.json").read_text(encoding="utf-8"))


def _refuse_if_rows_moved(rows: list[list]) -> None:
    """The v2 changes were authored on THESE rows; if the approved table moved underneath, stop (the door cut's guard)."""
    if len(rows) != 7:
        raise SystemExit(f"FAIL: the live table has {len(rows)} rows, the v2 rebuild was authored on 7")
    checks = [(1, "ledger:ev-japan-holdings-v1:line:", "cut"), (2, "plate-p-viewers-desk", "suck:0.49,0.55"),
              (3, "ledger:ev-japan-holdings-v1:line:", "cut"), (4, "ledger:ev-meta-yield-v1:bars:3:right:mount=", None),
              (5, "ledger:ev-fed-vs-yields-v1:line:", "cut"), (6, "clip:", "dip")]
    for i, world, exit_id in checks:
        if not str(rows[i][2]).startswith(world) or rows[i][5] != exit_id:
            raise SystemExit(f"FAIL: live row {i + 1} is {str(rows[i][2])[:60]!r} by {rows[i][5]!r}, "
                             f"expected {world!r} by {exit_id!r} - the approved table moved under this rebuild")


def shot_table(ws: list[dict], runtime_s: float, t_outro: float) -> list[tuple]:
    """The approved rows with the treatment's changes patched in, and nothing else touched."""
    rows = [list(r) for r in B.shot_table(ws, runtime_s, t_outro)]
    _refuse_if_rows_moved(rows)
    at = lambda phrase: B.W.at(ws, phrase)
    t_panel, t_rescale = at("Three men in blue ties"), at("The Treasury's table")

    # --- ROW 2: the park that makes the room, the card in it, the un-park into the rescale
    docks = [list(d) for d in rows[1][4]]
    panel = next(d for d in docks if d[0] == "dock-c-blue-ties-panel")
    panel[3] = round(t_rescale - PANEL_OUT_LEAD_S, 2)            # it leaves INTO the rescale, not on "watching"
    panel[4] = {**panel[4], **PANEL_PLACE}                       # the throw and the paper mass stay; the ROOM is new
    rows[1][4] = [tuple(d) for d in docks]
    rows[1][6] = ([{**PANEL_PARK, "at": round(t_panel - PANEL_PARK_LEAD_S, 2)}] + list(rows[1][6])
                  + [{**PANEL_UNPARK, "at": round(t_rescale - PANEL_UNPARK_LEAD_S, 2)}])

    # --- ROW 3: the melt INTO it, the plate alive, the light on the phone
    rows[2][2] = str(rows[2][2]) + PLATE_IDLE
    rows[2][3] = PLATE_KEN
    rows[2][5] = MELT
    rows[2][6] = list(rows[2][6]) + [{"kind": "spotlight", "at": _word_end(ws, *PHONE_WORD),
                                      "dur": PHONE_LIGHT_S, "target": dict(PHONE_POINT)}]

    # --- ROWS 4 -> 5: row 4 holds to the snap and carries the thrown card; row 5 IS that card, grown
    t_throw, t_snap = at(CARD_THROW_WORD), at(SNAP_WORD)
    card = B.dock_chart(CARD, "ev-meta-yield-v1", variant="bars", aspect="9:16")
    rows[3][1] = t_snap
    rows[3][4] = list(rows[3][4]) + [(card, 0, t_throw, t_snap,
                                     {**CARD_PLACE, "card_aspect": B.D.card_aspect(CARD, B.BUILD)})]
    rows[3][6] = list(rows[3][6]) + [{**CARD_PARK, "at": round(t_throw - CARD_PARK_LEAD_S, 2)}]
    meta_id = str(rows[4][2])
    head, _, tail = meta_id.partition(":mount=")
    rows[4][0] = t_snap
    rows[4][2] = f"{head}:snap={CARD}:" + tail.partition(":")[2]   # `mount=2.43` goes - the snap is the arrival
    rows[4][5] = SNAP_TRANSITION

    # --- ROW 5: the Fed card into the room the park makes, and the callout off the tick band
    docks5 = [list(d) for d in rows[4][4]]
    fed = next(d for d in docks5 if d[0] == "dock-h-fed-vs-yields")
    t_fed = float(fed[2])
    fed[4] = {**fed[4], **FED_PLACE, "card_aspect": B.D.card_aspect("dock-h-fed-vs-yields", B.BUILD)}
    rows[4][4] = [tuple(d) for d in docks5]
    species5 = [dict(x) for x in rows[4][6]]
    for x in species5:
        if x.get("kind") == "callout":
            x["pad"] = CALLOUT_PAD
    rows[4][6] = species5 + [{**FED_PARK, "at": round(t_fed - FED_PARK_LEAD_S, 2)}]

    # --- ROW 5: the multiple at the emphasised bar, off the object's own facts
    facts = _meta_facts()
    bar = next(i for i, b in enumerate(facts["bars"]) if b["label"] == YIELD_FIGURE_BAR)
    rows[4][6] = list(rows[4][6]) + [
        {"kind": "figure", "at": at(YIELD_FIGURE_SENTENCE), "dur": YIELD_FIGURE_S,
         "target": {"kind": "datum", "index": bar},
         "text": f"{facts['facts']['implied_pe'][YIELD_FIGURE_BAR]}x"}]
    return [tuple(r) for r in rows]


BEAT_PLAN = "BEAT-PLAN.jsonl"


def _restamp_beat_plan(build: Path, rows: list[tuple]) -> str:
    """THE PLAN'S WORLD FIELDS, RE-STAMPED FROM THIS CUT'S OWN TABLE (the director-critic, 2026-09-17).

    `build-short/BEAT-PLAN.jsonl` is the approved cut READ BACK (P66 T7) and is the seed for this build's plan;
    `derive_beat_moves.py` then fills each record's `moves` from the compiled timeline and TOUCHES NOTHING ELSE - so
    the frozen `row` / `plate` fields still named the approved cut's worlds at every row v2 changed (beat 12's plate
    carried no `;idle=drift`, beats 19-23 still carried `mount=2.43`). This stamps `row`, `plate` and `exit` off THIS
    table, by the beat's own t0, and says so in `source`.

    What it does NOT do: rewrite the prose `capabilities` / `act` / `comparator`. Those are the AUTHOR's (E99 s66 keeps
    the plan's intelligence with an agent or the operator), and a tool that paraphrased them would be inventing a plan,
    not transcribing one. Where the prose still describes the approved cut's mechanism the record now carries
    `v2_changed` naming the row's real world and transition, so nothing in the file reads as v2's without being v2's.
    `derive_beat_moves.py` is UNCHANGED - this runs in the build that owns the plan."""
    path = build / BEAT_PLAN
    if not path.is_file():
        src = HERE / "build-short" / BEAT_PLAN
        if not src.is_file():
            return f"no {BEAT_PLAN} to stamp (and none to seed from at {src})"
        path.write_bytes(src.read_bytes())
    spans = [(float(r[0]), float(r[1]), str(r[2]), r[5]) for r in rows]
    out, changed = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        t0 = float(rec.get("t0") or 0.0)
        i = next((n for n, (a, b, _p, _e) in enumerate(spans) if a - 1e-6 <= t0 < b), len(spans) - 1)
        a, b, plate, exit_id = spans[i]
        was = (rec.get("row"), rec.get("plate"))
        rec["row"], rec["plate"], rec["exit"] = i + 1, plate, exit_id
        if was != (rec["row"], rec["plate"]):
            changed += 1
            rec["v2_changed"] = (f"row {was[0]} -> {rec['row']}; plate {was[1]!r} -> {plate!r}; the transition INTO "
                                 f"this row is {exit_id!r}. The prose fields above are the APPROVED cut's read-back.")
        rec["source"] = ("read back from the approved cut (P66 T7); row/plate/exit re-stamped from build_short_v2.py's "
                         "own table, moves from the compiled v2 timeline (derive_beat_moves.py)")
        out.append(json.dumps(rec, ensure_ascii=False))
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return f"{BEAT_PLAN}: {len(out)} records, {changed} re-stamped off the v2 table"


def _assert_evidence_unchanged() -> None:
    """`build_short.main` re-copies `evidence/<s>.series.json` into `evidence/objects/`; nothing outside the build is
    written here, so the copy is ASSERTED instead (the door cut's step)."""
    for s in B.SERIES:
        src, dst = HERE / "evidence" / f"{s}.series.json", HERE / "evidence/objects" / f"{s}.series.json"
        if src.read_bytes() != dst.read_bytes():
            raise SystemExit(f"FAIL: evidence/objects/{s}.series.json differs from its source - "
                             "run build_short.py's copy, not this")


def _receipt_is_this_module() -> None:
    """P67 T2: the compile door reads the project's `PRODUCTION-LEDGER.md`; THIS cut's receipt is the `## Recall` block
    in this module's own docstring (the brief's write set is this file and its build dir - the project's ledger is not
    ours to write). The verifier is unchanged and re-reads every span off disk; only WHICH file it opens moves, and the
    compile manifest records that file by name."""
    import recall_verify as RV
    inner = RV.resolve_ledger
    RV.resolve_ledger = lambda target: Path(__file__) if Path(target).resolve() == HERE else inner(target)


def main() -> int:
    EP, BUILD = B.EP, B.BUILD
    if BUILD.resolve() != (HERE / BUILD_DIR).resolve():
        raise SystemExit(f"FAIL: build_short resolved its build to {BUILD}, not {HERE / BUILD_DIR}")
    A, T, W = B.A, B.T, B.W

    # the take, the pauses and the outro clock - `build_short.main`'s own steps, unchanged
    ws = W.take_words(EP)
    EP.mkdirs()
    shutil.copy2(B.TAKE / "scene_1.mp3", EP.audio_master)
    W.write_timeline(EP, ws, A.probe_duration(EP.audio_master))
    tl_built = W.apply_edit_pauses(EP, B.EDIT_PAUSES)
    ws = W.shifted_words(EP)
    t_vo_end = tl_built["runtime_s"]
    line_s = A.probe_duration(B.BRAND_LINE)
    t_outro, t_line, runtime_s = A.outro_clock(t_vo_end, line_s, outro_lead=B.OUTRO_LEAD, outro_s=B.OUTRO_S,
                                               brand_gap=B.BRAND_GAP, brand_tail=B.BRAND_TAIL)
    audio = BUILD / tl_built.get("paused_audio", "audio/episode.mp3")
    A.stitch_brand_line(audio, B.BRAND_LINE, B.BRAND_GAP, runtime_s)
    tl_built["runtime_s"] = runtime_s
    W.save_timeline(EP, tl_built)
    print(f"  v2 rebuild  : brand line {line_s:.2f}s at {t_line:.2f}s; card at {t_outro:.2f}s; "
          f"runtime {runtime_s:.2f}s; build {BUILD}")

    _assert_evidence_unchanged()
    T.caption_pages(BUILD, char_budget=28, max_words=6)
    rows = shot_table(ws, runtime_s, t_outro)
    if not any(m["asset"] == CARD for m in B.DOCK_META):
        B.DOCK_META.append(dict(CARD_META))
    (BUILD / "evidence-dock.json").write_text(json.dumps(B.DOCK_META, indent=1), encoding="utf-8")

    table = BUILD / "SHOT-TABLE-SHORT.py"
    T.write_shot_table(table, rows,
                       '"""Tokyo short, v2 REBUILD - GENERATED by build_short_v2.py. Do not hand-edit."""\n'
                       "# the treatment: REBUILD-TREATMENT-V2.md; the approved cut's table is untouched\n")
    T.print_rows(rows, show_docks=True)

    _receipt_is_this_module()
    rc = T.compile_timeline(
        HERE, BUILD,
        timeline_name=TIMELINE_NAME,
        shot_table_file=os.path.relpath(table, HERE),
        title="Tokyo Tea Break", subtitle="Money Physics · short", episode_id="tokyo-tea-break",
        aspect="9:16", caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False,
                  "curvature_stroke": True})
    if rc:
        return rc

    # THE CUES (E99 s72): re-derived from the v2 rows by the BED's own writer, into the PRIVATE plan, embedded into
    # this build's own timeline (the compiler reads the EPISODE's approved plan, which is never written here), then
    # BOUND to what the compiled timeline actually plays. `generate_base_table.py --bind-cues` is the CLI door.
    plan_path, cues = LB.write_cue_plan(B, BUILD, rows, table)
    for note in LB.embed_cues(B, BUILD, cues, TIMELINE_NAME):
        print(f"  [sound] {note}")
    print(f"  cue plan    : {len(cues)} cues re-derived into {plan_path.name} and embedded in {TIMELINE_NAME}")
    print(f"  beat plan   : {_restamp_beat_plan(BUILD, rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

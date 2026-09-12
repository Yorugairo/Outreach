"""Normal For Which Bridge - the SHORT's build (stages 6-8 for `SCRIPT-SHORT-VO.txt`, v1).

THE ONE-SHOT (the operator, 2026-09-12: "try to one-shot a short to test our current settings and capabilities" /
"we haven't tested new creation"). A NEW project, written and built in one pass with the engine as it stands after
P52 - no clips, no docks, no beds: three LEDGER PAGES and the species the sentences ask for, so what is under test
is the page, the chart, the species vocabulary and the caption strip rather than an asset library.

THE CLOCK IS A SCRATCH, and that is a declared deviation: `scratch_take.py --engine kokoro` (local, free) wrote
`vo-short/audio/scene_1.words.json`, and doctrine says scratch timings never touch a build (the paid take is the
clock). Nothing here ships: no master render, no publish. Kokoro reads ~154 wpm against the real voice's ~180, so
every window in this build is ~15% long.

    python build_short.py            # builds build-short/ and runs the motion gate + the self-watch
    BRIDGE_BUILD_DIR=build-short-x   # a side build, never over a served one
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project                                          # noqa: E402
from authoring import audio as A, table as T, words as W               # noqa: E402

SCRIPT = HERE / "SCRIPT-SHORT-VO.txt"
TAKE = HERE / "vo-short/audio"
BUILD = HERE / os.environ.get("BRIDGE_BUILD_DIR", "build-short")
EP = Project(here=HERE, build=BUILD, take=TAKE, take_stem="scene_1",
             script_name=SCRIPT.name, episode_id="normal-for-which-bridge")
LOAD, LONG, BILL = "ev-federal-load-v1", "ev-long-end-2026-v1", "ev-interest-bill-v1"
CAP_ARRIVE = os.environ.get("BRIDGE_CAP_ARRIVE") or None
OPEN_ENTER = os.environ.get("BRIDGE_OPEN_ENTER", "axes")   # P53 T1 / gate 1: the hook's register - "axes" lands the charcoal page on its axes and draws the chart from the first frame; "built" lands the whole page, still; "" takes the default roll-out
   # P52 T10 / gate 4: "fade_up" is the staggered arrival, a side build only


def facts(series: str) -> dict:
    import json
    return json.loads((HERE / f"evidence/objects/{series}.series.json").read_text(encoding="utf-8"))["facts"]


LOAD_F, LONG_F, BILL_F = facts(LOAD), facts(LONG), facts(BILL)
IDX81, LOAD_LAST = int(LOAD_F["idx_1981q4"]), int(LOAD_F["last_idx"])
IDX_AUG, LONG_LAST = int(LONG_F["idx_aug26"]), int(LONG_F["last_idx"])
BILL_LAST = int(BILL_F["last_idx"])
# the 2022 turn on the interest bill: the stretch "the load just went up" names
IDX_2022 = next(i for i, p in enumerate(
    __import__("json").loads((HERE / f"evidence/objects/{BILL}.series.json").read_text(encoding="utf-8"))["series"][0]["pts"])
    if float(p[0]) >= 2022.0)


def shot_table(ws: list[dict], runtime_s: float) -> list[tuple]:
    """The rows, anchored on PHRASES and timed from the take. Cuts land at 0.8 of the >= 0.30 s gap before the next
    beat's first word (M13's `gap` rule, the pin the two approved shorts carry).

    FIVE worlds for three pages: the bridge opens, the number interrupts it, the bridge returns with its two loads,
    the bill lands, and the bridge comes back for the ring. That shape is not a preference - M05's 20 s hold ceiling
    wants two docks over any longer plate, and a pages-only short has none, so the argument itself has to keep
    moving (the v1 table held the bridge 29 s and failed)."""
    at = lambda phrase: W.at(ws, phrase)
    cut = lambda phrase: W.cut_before(ws, phrase, rule="gap")

    t_num = cut("Start with the number")
    t_load = cut("Now put that number")
    t_bill = cut("And the load sends")
    t_ring = cut("So when someone calls")

    rows: list[tuple] = [
        # ---- the bridge, opened at its apex: the hook, the mechanism, and the light on today's load
        (0.0, t_num, f"ledger:{LOAD}:line:{LOAD_LAST}:right:{OPEN_ENTER}:cut", (0, 0, 0), [], "suck:0.5,0.52", [
            # M11 + the Apex Chart Read (2026-09-12 research): on the AXES register the line finishes at 3.0 s, so
            # the light goes on the latest datum inside the 1.5 s after THAT - on the word that says a yield is a
            # weight, which is the sentence the light is illustrating (it used to sit on "heavier." at 7.9 s, which
            # was inside the old roll-out's window and four seconds late for this one)
            {"kind": "callout", "at": at("But a yield"), "dur": 2.6, "pad": 24,
             "target": {"kind": "datum", "index": LOAD_LAST}, "label": "123% of GDP today"},
            {"kind": "note", "at": at("Every price"), "dur": 2.4,
             "text": "every price you own is divided by that number"},
        ]),
        # ---- the number: what the long end pays, two weeks apart
        (t_num, t_load, f"ledger:{LONG}:line:{IDX_AUG}:right::cut", (0, 0, 0), [], "cut", [
            {"kind": "build_to", "at": at("Two weeks ago"), "dur": 1.6,
             "target": {"kind": "datum", "index": IDX_AUG}},
            {"kind": "figure", "at": at("four point six"), "dur": 1.6, "text": "4.66%",
             "target": {"kind": "datum", "index": IDX_AUG}, "dy": -0.8},
            {"kind": "build_to", "at": at("By Tuesday"), "dur": 1.6,
             "target": {"kind": "datum", "index": LONG_LAST}},
            {"kind": "callout", "at": at("highest since"), "dur": 2.2, "pad": 24,
             "target": {"kind": "datum", "index": LONG_LAST}, "label": "4.83% - highest since Oct 2023"},
        ]),
        # ---- the bridge returns by the vortex, already drawn, and takes its two loads one at a time
        (t_load, t_bill, f"ledger:{LOAD}:line:{LOAD_LAST}:right:spiral:cut", (0, 0, 0), [], "melt", [
            {"kind": "build_to", "at": at("In nineteen"), "dur": 2.0,
             "target": {"kind": "datum", "index": IDX81}},
            {"kind": "figure", "at": at("thirty-one percent"), "dur": 1.6, "text": "31% of GDP",
             "target": {"kind": "datum", "index": IDX81}, "dy": -0.8},
            {"kind": "build_to", "at": at("Today that same"), "dur": 2.4,
             "target": {"kind": "datum", "index": LOAD_LAST}},
            {"kind": "span", "at": at("that same load"), "dur": 2.6, "from": IDX81, "to": LOAD_LAST,
             "label": "1981 to today"},
            {"kind": "figure", "at": at("one hundred twenty-three"), "dur": 1.8, "text": "123%",
             "target": {"kind": "datum", "index": LOAD_LAST}, "color": "neg", "dy": -1.0},
        ]),
        # ---- what the load costs
        (t_bill, t_ring, f"ledger:{BILL}:line:{BILL_LAST}:right::cut", (0, 0, 0), [], "cut", [
            {"kind": "build_to", "at": at("Federal interest runs"), "dur": 2.6,
             "target": {"kind": "datum", "index": BILL_LAST}},
            {"kind": "figure", "at": at("one point two"), "dur": 1.8, "text": "$1.25T a year",
             "target": {"kind": "datum", "index": BILL_LAST}, "color": "neg", "dy": -1.0},
            {"kind": "note", "at": at("The thirty-year carries"), "dur": 2.2,
             "text": "the 30-year: 5.28% - every new bond prices off it"},
            # no span on the reflect sentence: M28 caught its label under the figure's own pill at 0:53, and
            # "nothing defaulted" is not a claim about a stretch of time - it was motion for motion's sake
        ]),
        # ---- the ring: the bridge page returns again and is asked the question the hook opened
        (t_ring, round(runtime_s, 3), f"ledger:{LOAD}:line:{LOAD_LAST}:right:spiral:cut", (0, 0, 0), [], None, [
            {"kind": "retitle", "at": at("normal for which"), "dur": 2.4, "text": "Normal for which bridge?"},
            {"kind": "figure", "at": at("Nineteen eighty-one carried"), "dur": 1.8, "text": "31%",
             "target": {"kind": "datum", "index": IDX81}, "dy": -0.8},
            {"kind": "ring", "at": at("This one carries"), "dur": 2.4, "form": "dashed", "label": "123%",
             "target": {"kind": "datum", "index": LOAD_LAST},
             "flag": "today", "flag_icon": "landmark"},
        ]),
    ]
    return T.hold_until(rows, ws)


def main() -> int:
    ws = W.take_words(EP)
    EP.mkdirs()
    shutil.copy2(TAKE / "scene_1.mp3", EP.audio_master)
    tl = W.write_timeline(EP, ws, A.probe_duration(EP.audio_master))
    runtime_s = float(tl["runtime_s"])
    print(f"  take        : {len(ws)} words, {runtime_s:.2f}s (SCRATCH - kokoro, a declared deviation)")

    # a page holds a phrase of 3-6 words on TWO lines at most: the portrait strip is 800 px at 64 px type
    T.caption_pages(BUILD, char_budget=28, max_words=6)

    rows = shot_table(ws, runtime_s)
    T.write_shot_table(HERE / "SHOT-TABLE-SHORT.py", rows,
                       '"""Normal For Which Bridge - AUTHORED shot table, timed from the take by build_short.py.\n'
                       'Do not hand-edit; edit build_short.shot_table."""\n')
    T.print_rows(rows)

    if CAP_ARRIVE:
        import build_scene_timeline_f as _C
        _C.CAPTION_ARRIVE = CAP_ARRIVE
        print(f"  caption     : arrival {CAP_ARRIVE} (BRIDGE_CAP_ARRIVE) - gate 4's candidate, a private register")
    rc = T.compile_timeline(
        HERE, BUILD,
        timeline_name="bridge-short.timeline.json",
        shot_table_file="SHOT-TABLE-SHORT.py",
        title="Normal For Which Bridge", subtitle="Money Physics · short",
        episode_id="normal-for-which-bridge",
        aspect="9:16",
        caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True,
                  "km_ink": False, "curvature_stroke": True})
    if os.environ.get("SELF_WATCH", "1") == "1":
        import self_watch as SW
        rc = rc or SW.main([str(BUILD), "--project", str(HERE), "--script", "SCRIPT-SHORT"])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

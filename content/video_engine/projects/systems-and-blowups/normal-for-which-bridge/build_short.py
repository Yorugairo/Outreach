"""Normal For Which Bridge - the SHORT's build (stages 6-8 for `SCRIPT-SHORT-VO.txt`, v1).

THE ONE-SHOT (the operator, 2026-09-12: "try to one-shot a short to test our current settings and capabilities" /
"we haven't tested new creation"). A NEW project, written and built in one pass with the engine as it stands after
P52 - no clips, no docks, no beds: three LEDGER PAGES and the species the sentences ask for, so what is under test
is the page, the chart, the species vocabulary and the caption strip rather than an asset library.

THE CLOCK is the Chirp take (E70: Chirp ships on Facebook; the Kokoro take is kept beside it for the YouTube cut),
loudnormed to -17.2 LUFS, its words forced-aligned to the script (align_take.py --script, 155/155). One narrative
plate (Flow, E72) holds the sentence the chart cannot draw; two Suno beds at -20 LU and the CC0 page cues are the sound.

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
from authoring import audio as A, docks as D, table as T, words as W   # noqa: E402

SCRIPT = HERE / "SCRIPT-SHORT-VO.txt"
TAKE = HERE / "vo-short/audio"
BUILD = HERE / os.environ.get("BRIDGE_BUILD_DIR", "build-short")
EP = Project(here=HERE, build=BUILD, take=TAKE, take_stem="scene_1",
             script_name=SCRIPT.name, episode_id="normal-for-which-bridge")
LOAD, LONG, BILL = "ev-federal-load-v1", "ev-long-end-2026-v1", "ev-interest-bill-v1"
PLATE_BRIDGE = "plate-bridge-load"   # omni-video/stills/plate-bridge-load.png - Flow, Nano Banana Pro, zero credit (E72)

# THE SOUND (E54: the bed at -20 LU under the voice, no louder). Measured 2026-09-12: the Chirp take at -17.2 LUFS after
# loudnorm; both beds at -13.0 LUFS (the Tokyo copies of the Money Physics Suno Pro beds). gain = 10^((VO - LU - bed) / 20).
VO_LUFS, BED_LU, BED_LUFS = -17.2, 20.0, -13.03
ROLL, STROKE, SWIRL_IN = "fs-page-roll-464302.mp3", "fs-page-stroke-447925.mp3", "fs-swirl-in-478722.mp3"
ACCENT, ENTER_GAIN = 0.12, 0.10
TURN_BED_AT = 21.0   # the turn bed fades in under the hook bed at the TURN sentence, as Tokyo's did at its turn
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
    t_81 = cut("In nineteen")
    t_bill = cut("And the load sends")
    plate = D.register(PLATE_BRIDGE, HERE / "omni-video/stills/plate-bridge-load.png")
    t_ring = cut("So when someone calls")

    rows: list[tuple] = [
        # ---- the bridge, opened at its apex: the hook, the mechanism, and the light on today's load
        (0.0, t_num, f"ledger:{LOAD}:line:{LOAD_LAST}:right:{OPEN_ENTER}:cut", (0, 0, 0), [], "suck:0.5,0.52", [
            # M11 + the Apex Chart Read (2026-09-12 research): on the AXES register the line finishes at 3.0 s, so
            # the light goes on the latest datum inside the 1.5 s after THAT - on the word that says a yield is a
            # weight, which is the sentence the light is illustrating (it used to sit on "heavier." at 7.9 s, which
            # was inside the old roll-out's window and four seconds late for this one)
            # review 2: a spotlight, not a callout - the callout's ring sat on the series' own tag at the line's tip; and no
            # note - it typed the caption word for word and was still typing when the page left
            {"kind": "spotlight", "at": at("weight,"), "dur": 2.6, "target": {"kind": "datum", "index": LOAD_LAST}},
        ]),
        # ---- the number: what the long end pays, two weeks apart
        (t_num, t_load, f"ledger:{LONG}:line:{IDX_AUG}:right:axes:cut", (0, 0, 0), [], "cut", [
            {"kind": "build_to", "at": at("Two weeks ago"), "dur": 1.6,
             "target": {"kind": "datum", "index": IDX_AUG}},
            # review 2: no "4.66%" figure - it sat on the 10-year line under the tag and the 4.83% ring landed on both
            {"kind": "build_to", "at": at("By Tuesday"), "dur": 1.6,
             "target": {"kind": "datum", "index": LONG_LAST}},
            {"kind": "callout", "at": at("highest since"), "dur": 2.2, "pad": 24,
             "target": {"kind": "datum", "index": LONG_LAST}, "label": "4.83%"},   # review 1: the sub carries both dates; the long label was clipped at the edge
        ]),
        # ---- the bridge returns by the vortex, already drawn, and takes its two loads one at a time
        # E40: a returning page UNWINDS from its point, it never redraws - the first cut walked this page's line back to
        # 1981 with build_to and the second visit showed LESS than the first (read at 28-38 s, 2026-09-12). The page
        # arrives drawn by the vortex; the sentences mark the two loads on the line that is already there.
        # ---- THE TURN, on the one picture the chart cannot draw: the bridge, bending under the load (E61 use=bridge)
        (t_load, t_81, f"{plate};use=bridge", (0.04, 0, -10), [], None, []),
        (t_81, t_bill, f"ledger:{LOAD}:line:{LOAD_LAST}:right:spiral:cut", (0, 0, 0), [], "melt", [
            # review 1: no callout on 1981 - it fired inside the spiral (M25) and its ring sat on the figure below
            {"kind": "figure", "at": at("thirty-one percent"), "dur": 1.6, "text": "31% of GDP",
             "target": {"kind": "datum", "index": IDX81}, "dy": -0.8},
            # review 2: no span - its shade read as a grey block over the whole line; the two figures name the two loads
            {"kind": "figure", "at": at("one hundred twenty-three"), "dur": 1.8, "text": "123%",
             "target": {"kind": "datum", "index": LOAD_LAST}, "color": "neg", "dy": -1.0},
        ]),
        # ---- what the load costs
        (t_bill, t_ring, f"ledger:{BILL}:line:{BILL_LAST}:right::cut", (0, 0, 0), [], "cut", [
            {"kind": "build_to", "at": at("Federal interest runs"), "dur": 2.6,
             "target": {"kind": "datum", "index": BILL_LAST}},
            # review 1: no figure here - "$1.25T a year" stood over the series' own "$1.25T Interest paid" tag
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


def sound_cues(rows: list[tuple]) -> list[dict]:
    """The cue map over the kit's transition readings: a page roll on a ledger page's ordinary arrival, a swirl on a
    spiral return, nothing on a mount (the mount's own cream is silent) or an axes arrival (the stroke of the first
    line is the cue), and the two beds."""
    import json
    gain = round(10 ** ((VO_LUFS - BED_LU - BED_LUFS) / 20), 4)
    cues: list[dict] = []
    for i, r in enumerate(rows):
        page = A.page_transitions(r[2])
        if not page["ledger"]:
            continue
        if page["spiral"]:
            cues.append({"slot": f"page enter {i + 1} (spiral)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0,
                         "variants": {"A": SWIRL_IN}})
        elif ":axes" in r[2] or i == 0:
            cues.append({"slot": f"page enter {i + 1} (axes - the first line)", "at": round(r[0] + 0.05, 2), "gain": ACCENT,
                         "fade_in": 0.0, "variants": {"A": STROKE}})
        elif not page["mount"]:
            cues.append({"slot": f"page enter {i + 1}", "at": round(r[0], 2), "gain": ENTER_GAIN, "fade_in": 0.0,
                         "variants": {"A": ROLL}})
    cues.append({"slot": "hook bed", "at": 0.0, "gain": gain, "fade_in": 1.5, "variants": {"A": "suno-hook-B.mp3"},
                 "note": f"-{BED_LU:.0f} LU under the VO ({VO_LUFS} LUFS): {gain}"})
    cues.append({"slot": "turn bed", "at": TURN_BED_AT, "gain": gain, "fade_in": 3.0, "variants": {"A": "suno-pivot-A.mp3"},
                 "note": f"-{BED_LU:.0f} LU under the VO; fades in at the turn"})
    plan = {"note": "normal-for-which-bridge - written by build_short.sound_cues; do not hand-edit",
            "transient_gain": ACCENT, "cues": cues, "page_cues": [], "page_cues_note": "none yet"}
    (HERE / "sound/SOUND-PLAN.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    return cues


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
    print(f"  sound       : {len(sound_cues(rows))} cues written to sound/SOUND-PLAN.json")
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

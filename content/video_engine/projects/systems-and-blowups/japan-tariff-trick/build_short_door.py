"""Japan tariff trick - E98 s7, THE EVIDENCE DOOR's first instance: a NEW private short beside the approved one, never a
rebuild (E45 / review-link-frozen-copy).

    python build_short_door.py          # -> build-p58-door/

The operator, 2026-09-14: *"zoom in or cut-in on to the tariff bill card all the way flat so its just like a regular
plate, then we open that door and behind it is the vault plate."* It is `build_short.py` exactly - the same script, take,
docks, captions, sound and kinetics - with TWO changes and nothing else:
  1. row 6, the receipt page, arrives by its APPROVED `snap` ("all the way flat so it's just like a regular plate") -
     no `depth=`, no `plane=` (TARIFF_CHART_ARRIVAL is pinned to snap here, whatever the shell says).
  2. row 7, the vault (`plate-vault;idle=drift`), enters by `door:<HINGE>` instead of `dip`.
Every write `build_short.main` makes OUTSIDE the build dir is redirected, compared or switched off, as build_short_p58.py
does: the shot table is written inside the build; the sound plan is derived and COMPARED with the approved
`sound/SOUND-PLAN.json` (never rewritten - a difference is REPORTED, and the compiler embeds the approved file); the
evidence objects are asserted identical, never re-copied; SELF_WATCH is off. The approved `build-short/` and every other
`build-short*` / `build-p58-2-5d` directory is read only.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

BUILD_DIR = "build-p58-door"
# THE HINGE, read off the frame (the receipt page at 45.40 s, the last frame of row 6): the eye is on the spotlit Detroit
# bar and its $6240 pill, the RIGHT half of the page. The door opens AWAY from where the eye is, so it hangs on the RIGHT:
# Detroit stays beside the hinge, where the swing moves least and it is the last thing to leave, and the vault opens
# from the left, on the far side of the page from it. (A left hinge would throw the free edge - Detroit's bar - first.)
HINGE = "right"
if os.environ.setdefault("TARIFF_BUILD_DIR", BUILD_DIR) != BUILD_DIR:
    raise SystemExit(f"FAIL: the door cut builds {BUILD_DIR} only (TARIFF_BUILD_DIR={os.environ['TARIFF_BUILD_DIR']!r})")
os.environ["TARIFF_CHART_ARRIVAL"] = "snap"                                            # change 1: the approved arrival, flat

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_short as B   # noqa: E402

RECEIPT = "ledger:ev-tariff-receipt-v1:bars:1:right:snap=dock-g-receipt:cut;idle=live"
VAULT = "plate-vault;idle=drift"
DOOR = f"door:{HINGE}"                                                                  # change 2

_live_shot_table = B.shot_table


def shot_table(ws: list[dict], runtime_s: float, t_outro: float) -> list[tuple]:
    """The live table with change 2; refuses if the live rows moved under it (or if row 6 is not the flat snap)."""
    rows = [list(r) for r in _live_shot_table(ws, runtime_s, t_outro)]
    if len(rows) != 12:
        raise SystemExit(f"FAIL: the live table has {len(rows)} rows, the door cut was authored on 12")
    if rows[5][2] != RECEIPT:
        raise SystemExit(f"FAIL: row 6's world is {rows[5][2]!r}, expected the flat snap {RECEIPT!r}")
    if "depth=" in rows[5][2] or "plane=" in rows[5][2]:
        raise SystemExit("FAIL: row 6 carries depth=/plane= - the door opens a card that landed flat")
    if rows[6][2] != VAULT or rows[6][5] != "dip":
        raise SystemExit(f"FAIL: row 7 is {rows[6][2]!r} by {rows[6][5]!r}, expected {VAULT!r} by 'dip'")
    rows[6][5] = DOOR
    return [tuple(r) for r in rows]


def main() -> int:
    """`build_short.main`, with every write outside the build redirected or refused (see the module docstring)."""
    EP, BUILD, HERE_B = B.EP, B.BUILD, B.HERE
    if BUILD.resolve() != (HERE_B / BUILD_DIR).resolve():
        raise SystemExit(f"FAIL: build_short resolved its build to {BUILD}, not {HERE_B / BUILD_DIR}")
    ws = B.W.take_words(EP)
    EP.mkdirs()
    shutil.copy2(B.TAKE / f"{B.TAKE_STEM}.mp3", EP.audio_master)
    t_vo_end = round(B.A.probe_duration(EP.audio_master), 3)
    line_s = B.A.probe_duration(B.BRAND_LINE)
    t_outro, t_line, runtime_s = B.A.outro_clock(t_vo_end, line_s, outro_lead=B.OUTRO_LEAD, outro_s=B.OUTRO_S,
                                                 brand_gap=B.BRAND_GAP, brand_tail=B.BRAND_TAIL)
    B.A.stitch_brand_line(EP.audio_master, B.BRAND_LINE, B.BRAND_GAP, runtime_s)
    B.W.write_timeline(EP, ws, runtime_s)
    print(f"  E98 s7 door cut: hinge {HINGE}; arm {B.ARM}; take {t_vo_end:.2f}s; runtime {runtime_s:.2f}s; build {BUILD}")

    (BUILD / "evidence-dock.json").write_text(json.dumps(B.DOCK_META, indent=1), encoding="utf-8")
    for s in B.SERIES:   # the approved build's copy step, asserted instead of re-run: nothing outside the build is written
        src, dst = HERE_B / "evidence" / f"{s}.series.json", HERE_B / "evidence/objects" / f"{s}.series.json"
        if src.read_bytes() != dst.read_bytes():
            raise SystemExit(f"FAIL: evidence/objects/{s}.series.json differs from its source - run build_short.py's copy, not this")
    B.register_assets()
    B.T.caption_pages(BUILD, char_budget=28, max_words=6)

    rows = shot_table(ws, runtime_s, t_outro)
    B.T.hold_until(rows, ws)
    approved_plan = json.loads((HERE_B / "sound/SOUND-PLAN.json").read_text(encoding="utf-8"))
    plan = dict(approved_plan, cues=B.sound_cues(rows))
    (BUILD / "sound").mkdir(exist_ok=True)
    (BUILD / "sound/SOUND-PLAN.derived.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    if plan["cues"] != approved_plan.get("cues"):
        print("  SOUND: the derived cues DIFFER from the approved sound/SOUND-PLAN.json (REPORTED, not changed - the "
              f"compiler embeds the approved file); compare {BUILD / 'sound/SOUND-PLAN.derived.json'}")
    else:
        print(f"  sound plan: {len(plan['cues'])} derived cues IDENTICAL to the approved sound/SOUND-PLAN.json (not rewritten)")
    B.T.write_shot_table(BUILD / "SHOT-TABLE-SHORT.py", rows,
                         '"""Japan tariff trick short - E98 s7 evidence-door cut, GENERATED by build_short_door.py. Do not hand-edit."""\n'
                         f"# arm: {B.ARM}; door: {DOOR}\n")
    B.T.print_rows(rows, show_docks=True)
    return B.T.compile_timeline(
        HERE_B, BUILD,
        timeline_name="japan-short.timeline.json",
        shot_table_file=os.path.relpath(BUILD / "SHOT-TABLE-SHORT.py", HERE_B),
        title="How Japan Tricked Trump", subtitle="Money Physics - short", episode_id="japan-tariff-trick",
        aspect="9:16", caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False, "curvature_stroke": True},
        render=True)


if __name__ == "__main__":
    raise SystemExit(main())

"""The BREAKTHROUGH bars proof (2026-09-10): bonds 1.52 % a year against chips 36.59 % a year over ten years, the scale stated to
8 % and the chips bar breaking through it. Writes steel-and-paper/build-f/breakthrough-proof.html (:8739/breakthrough-proof.html).

FOUR ROWS (P50 T10 + T13, 2026-09-11):
  burst      E60's ruled default - the bar shoots while the scale rewrites under it (Bravos 8:02)
  stack      the operator's A - the scale holds and the bar grows one comparator per step, off the page
  furniture  the burst with BOTH of T10's options on: the grey "?" track until the number is spoken, and the
             value capsule mounted on the AXIS under the bar's end with a dotted leader
  stop       the burst on stopaction's cadence (T13, R26-30, E60's blend): the shoot, the counter, the rescale
             and the ticks' crossing all step together, the glow hits on the landing step

    RENDER_ASPECT=9:16 python content/video_engine/scripts/proof_breakthrough.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("RENDER_ASPECT", "9:16")

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

REPO = HERE.parents[2]
EP = REPO / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
OUT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/breakthrough-proof.html"
PLATE = "ledger:ev-bonds-vs-chips-10y-v1:bars:1:right"
RUNTIME = 16.0

# name -> (the axes the page declares on top of the object's, the title's tail)
ROWS = {
    "burst": ({"overflow": "burst"}, "the scale rewrites under the shoot"),
    "stack": ({"overflow": "stack"}, "one comparator per step, off the page"),
    "furniture": ({"overflow": "burst", "overflow_placeholder": "?", "overflow_capsule": "axis"},
                  'the "?" track until the number is spoken, the capsule on the axis'),
    "stop": ({"overflow": "burst", "break_cadence": "stop"}, "the blend: the shoot stepped on stopaction's cadence"),
}


def out_for(mode: str) -> Path:
    return OUT if mode == "burst" else OUT.with_name(f"breakthrough-{mode}-proof.html")


def main() -> int:
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    sys.path.insert(0, str(REPO / "content/video_engine/tests/golden"))
    from build_golden_sources import silent_wav, uri  # noqa: E402
    uris = dict(uris, __audio__=uri("audio/wav", silent_wav(RUNTIME + 0.5)))
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    for mode, (axes, why) in ROWS.items():
        w = json.loads(json.dumps(world))
        w["page"]["axes"].update(axes)
        scene = dict(tl["scenes"][0], species=[], span=[0.0, RUNTIME], world=dict(w, ken_burns={"scale": 0, "x": 0, "y": 0}))
        timeline = dict(tl, aspect="9:16", runtime_s=RUNTIME, scenes=[scene], caption_pages=[], captions=[],
                        title=f"The breakthrough ({mode}): bonds 1.52 % a year vs chips 36.59 % a year, the scale stated to 8 % - {why}")
        timeline["kinetics"] = dict(timeline.get("kinetics") or {}, min_jerk=True, idle=True)
        out = out_for(mode)
        out.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        print(out, round(out.stat().st_size / 1e6, 1), "MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

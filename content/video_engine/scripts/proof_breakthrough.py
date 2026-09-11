"""The BREAKTHROUGH bars proof (2026-09-10): bonds 1.52 % a year against chips 36.59 % a year over ten years, the scale stated to
8 % and the chips bar breaking through it. Writes steel-and-paper/build-f/breakthrough-proof.html (:8739/breakthrough-proof.html).

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


def main() -> int:
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    sys.path.insert(0, str(REPO / "content/video_engine/tests/golden"))
    from build_golden_sources import silent_wav, uri  # noqa: E402
    uris = dict(uris, __audio__=uri("audio/wav", silent_wav(RUNTIME + 0.5)))
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    # two mechanics, one page each: burst (Bravos - the scale rewrites under the shoot) and stack (one comparator per step, off the page)
    for mode, out in (("burst", OUT), ("stack", OUT.with_name("breakthrough-stack-proof.html"))):
        w = json.loads(json.dumps(world)); w["page"]["axes"]["overflow"] = mode
        scene = dict(tl["scenes"][0], species=[], span=[0.0, RUNTIME], world=dict(w, ken_burns={"scale": 0, "x": 0, "y": 0}))
        timeline = dict(tl, aspect="9:16", runtime_s=RUNTIME, scenes=[scene], caption_pages=[], captions=[],
                        title="The breakthrough (" + mode + "): bonds 1.52 % a year vs chips 36.59 % a year, the scale stated to 8 %")
        timeline["kinetics"] = dict(timeline.get("kinetics") or {}, min_jerk=True, idle=True)
        out.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        print(out, round(out.stat().st_size / 1e6, 1), "MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""P48 HG1 - the proof page for the chart transitions, watched in the player: the Tokyo holdings page rescales to its
Feb-Jun window at 8 s and extends back to its last datum at 13 s. Writes steel-and-paper/build-f/chart-transitions-proof.html
(served by the `chart-transitions-proof` launch entry on :8739). The house pattern: build-f/ledger-species-proof.html.

    RENDER_ASPECT=9:16 python content/video_engine/scripts/proof_chart_transitions.py
"""
from __future__ import annotations

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
OUT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/chart-transitions-proof.html"
PLATE = "ledger:ev-japan-holdings-v1:line"
RESCALE_AT, RESCALE_S, WINDOW = 8.0, 1.4, [2025.9, 2026.3]
EXTEND_AT, EXTEND_S = 13.0, 2.0
PARK_AT, PARK_S = 17.5, 1.0
RUNTIME = 26.0


def main() -> int:
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    # the golden's clock is a 2 s silent wav (a golden is scrubbed, never played): a WATCHED proof needs a clock the length of
    # its runtime, or the player stops at 0:02 with the field mid-soak (the operator, 2026-09-10: "a blurred ink coming in for
    # 0:02 then it just freezes")
    sys.path.insert(0, str(REPO / "content/video_engine/tests/golden"))
    from build_golden_sources import silent_wav, uri  # noqa: E402
    uris = dict(uris, __audio__=uri("audio/wav", silent_wav(RUNTIME + 0.5)))
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    n = len(world["page"]["series"][0]["pts"])
    species = [{"kind": "chart_to", "at": RESCALE_AT, "dur": RESCALE_S, "to": "rescale", "window": WINDOW},
               {"kind": "chart_to", "at": EXTEND_AT, "dur": EXTEND_S, "to": "extend", "to_index": n - 1},
               {"kind": "chart_to", "at": PARK_AT, "dur": PARK_S, "to": "park", "scale": 0.72, "anchor": "top"}]   # T2b: the chart makes room (Bravos 91)
    B.derive_rescale_states(world, species, PLATE, EP)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, RUNTIME], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=RUNTIME, scenes=[scene], caption_pages=[], captions=[],
                    title="P48 proof: rescale at 8 s, extend at 13 s, park at 17.5 s - the Tokyo holdings page")
    timeline["kinetics"] = dict(timeline.get("kinetics") or {}, min_jerk=True, curvature_stroke=True, idle=True)
    OUT.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    print(OUT, round(OUT.stat().st_size / 1e6, 1), "MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

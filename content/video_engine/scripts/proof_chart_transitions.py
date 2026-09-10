"""P48 HG1 - the proof page for the chart transitions, watched in the player: the Tokyo holdings page rescales to its
Feb-Jun window at 8 s, extends back to its last datum at 13 s and parks at 17.5 s; then (T4b) the four-line divergence page
becomes its four bars by the KEYED recast at 35 s; then (T5) the holdings line MORPHS into the Fed-vs-yields line at 50 s.
Writes steel-and-paper/build-f/chart-transitions-proof.html
(served by the `chart-transitions-proof` launch entry on :8739). The house pattern: build-f/ledger-species-proof.html.

    RENDER_ASPECT=9:16 python content/video_engine/scripts/proof_chart_transitions.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("RENDER_ASPECT", "9:16")

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

REPO = HERE.parents[2]
EP = REPO / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
OUT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/chart-transitions-proof.html"
PLATE = "ledger:ev-japan-holdings-v1:line"
RESCALE_AT, RESCALE_S, WINDOW = 8.0, 1.4, [2025.9, 2026.3]
EXTEND_AT, EXTEND_S = 13.0, 2.0
PARK_AT, PARK_S = 17.5, 1.0
SCENE_1_END = 26.0
# T4b: the legal keyed pair - n lines -> n bars by series (Bravos 99-105). The bars are each line's LAST value, derived from the
# series on disk into a scratch episode dir; nothing is invented, and the bars page says what it shows.
LINES_SERIES = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-divergence-v1.series.json"
KEYED_AT, KEYED_S = 35.0, 2.2
SCENE_2_END = 44.0
# T5: morph_to - the area under the holdings line becomes the area under the Fed-vs-yields line by ARAP (two different series
# on disk, dense-line both; no key correspondence pretended: it is a change of shape)
MORPH_PLATE = "ledger:ev-japan-holdings-v1:line;then=ev-fed-vs-yields-v1:line"
MORPH_AT, MORPH_S = 50.0, 2.0
RUNTIME = 62.0


def lines_to_bars_episode(tmp: Path) -> tuple[Path, str]:
    """A scratch episode: the four-line page and a bars object of the lines' last values, one bar per series."""
    src = json.loads(LINES_SERIES.read_text(encoding="utf-8"))
    last_x = max(float(sr["pts"][-1][0]) for sr in src["series"])
    bars = {"title": "Where the four lines end", "sub": f"index at the last point ({LPG.decimal_year_label(last_x)}), 100 = Aug '25",
            "src": src.get("src", ""), "unit": "",
            "bars": [{"label": short, "value": round(float(sr["pts"][-1][1]), 1), "color": sr.get("color", "crimson")}
                     for sr, short in zip(src["series"], ("Memory", "Chips", "Mega-cap", "S&P 500"))]}   # the lines' names, short enough for four portrait bars
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / "evidence/objects/ev-lines-v1.series.json").write_text(json.dumps(src), encoding="utf-8")
    (tmp / "evidence/objects/ev-bars-v1.series.json").write_text(json.dumps(bars), encoding="utf-8")
    return tmp, "ledger:ev-lines-v1:line;then=ev-bars-v1:bars"


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
    scene = dict(tl["scenes"][0], species=species, span=[0.0, SCENE_1_END], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    with tempfile.TemporaryDirectory() as td:
        ep2, plate2 = lines_to_bars_episode(Path(td))
        world2 = B.world_for_plate(plate2, (0, 0, 0), ep2)
        species2 = [{"kind": "chart_to", "at": KEYED_AT, "dur": KEYED_S, "to": "recast", "state": 1, "keyed": True}]
        B.derive_rescale_states(world2, species2, plate2, ep2)
    scene2 = dict(tl["scenes"][0], scene_id="s02-keyed", species=species2, span=[SCENE_1_END, SCENE_2_END], world=dict(world2, ken_burns={"scale": 0, "x": 0, "y": 0}))
    world3 = B.world_for_plate(MORPH_PLATE, (0, 0, 0), EP)
    species3 = [{"kind": "chart_to", "at": MORPH_AT, "dur": MORPH_S, "to": "morph", "state": 1}]
    B.derive_rescale_states(world3, species3, MORPH_PLATE, EP)
    scene3 = dict(tl["scenes"][0], scene_id="s03-morph", species=species3, span=[SCENE_2_END, RUNTIME], world=dict(world3, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=RUNTIME, scenes=[scene, scene2, scene3], caption_pages=[], captions=[],
                    title="P48 proof: rescale 8 s, extend 13 s, park 17.5 s (the Tokyo holdings page); the keyed recast at 35 s (four lines -> four bars); the morph at 50 s (the holdings line -> the Fed-vs-yields line)")
    timeline["kinetics"] = dict(timeline.get("kinetics") or {}, min_jerk=True, curvature_stroke=True, idle=True, arap_morph=True)   # T5: the morph rides the flag a compiled timeline carries
    OUT.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    print(OUT, round(OUT.stat().st_size / 1e6, 1), "MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""The MORPH METHOD proof (P50 T12, 2026-09-11): one pair of line pages, morphed BY EACH METHOD, so the two can be
read side by side (doc 43 s43.5: A is the vertex lerp of two corresponded rings, B is the ARAP triangle solve).

  morph-a-proof.html       method: "a"    - ring-normalise, resample, rotational alignment, vertex lerp, cubic ring
  morph-a-arap-proof.html  method: "arap" - the shipped Method B, for the same pair at the same instants

The pair is the steel-and-paper divergence page (four lines) handing its shape to a one-line page of its first series -
the same pair test_chart_transitions.py morphs. The compiler measures it (centroid 0.4 % W, axis 0.4 deg, area 1.00)
and would choose A by doc 43's rule; the second page names `method: "arap"` so the two can be compared at one t.

R26-16 (the morph's source is a PLANTED element - the tie on the outgoing frame) is NOT what this proves: that needs
`morph_from: {scene, outline}` across a scene boundary, which is its own slice. This proves the METHOD.

    RENDER_ASPECT=9:16 python content/video_engine/scripts/proof_morph_a.py
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
import render_baseline as RB  # noqa: E402

REPO = HERE.parents[2]
SERIES = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-divergence-v1.series.json"
OUT = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/morph-a-proof.html"
RUNTIME = 16.0
MORPH_AT, MORPH_S = 6.0, 2.0


def out_for(method: str) -> Path:
    return OUT if method == "a" else OUT.with_name("morph-a-arap-proof.html")


def main() -> int:
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    sys.path.insert(0, str(REPO / "content/video_engine/tests/golden"))
    from build_golden_sources import silent_wav, uri  # noqa: E402
    uris = dict(uris, __audio__=uri("audio/wav", silent_wav(RUNTIME + 0.5)))
    src = json.loads(SERIES.read_text(encoding="utf-8"))
    one = dict(src, title="The memory makers alone", sub="index, 100 = Aug '25", series=[dict(src["series"][0])])
    one.pop("badges", None)
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/ev-lines-v1.series.json").write_text(json.dumps(src), encoding="utf-8")
        (ep / "evidence/objects/ev-one-v1.series.json").write_text(json.dumps(one), encoding="utf-8")
        plate = "ledger:ev-lines-v1:line;then=ev-one-v1:line"
        for method in ("a", "arap"):
            world = B.world_for_plate(plate, (0, 0, 0), ep)
            species = [{"kind": "chart_to", "at": MORPH_AT, "dur": MORPH_S, "to": "morph", "state": 1, "method": method}]
            B.derive_rescale_states(world, species, plate, ep)
            inv = species[0]["invariants"]
            scene = dict(tl["scenes"][0], species=species, span=[0.0, RUNTIME],
                         world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
            timeline = dict(tl, aspect="9:16", runtime_s=RUNTIME, scenes=[scene], caption_pages=[], captions=[],
                            title=(f"The morph by method {method} (doc 43 s43.5) - four lines' area into one line's, "
                                   f"measured centroid {100 * inv['centroid_shift']:.1f} % W, axis {inv['axis_deg']:.1f} deg, "
                                   f"area {inv['area_ratio']:.2f}"))
            timeline["kinetics"] = dict(timeline.get("kinetics") or {}, min_jerk=True, idle=True, arap_morph=True)
            out = out_for(method)
            out.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
            print(out, round(out.stat().st_size / 1e6, 1), "MB", "method", method)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""P58 T5 - THE PRIVATE BUILD: four pages, one data set, flat beside formed.

    s01  flat bars      s02  extruded bars      s03  flat line      s04  tilted line

The bars are the four line-ends of the SAME series the two line pages draw, so every row of
`probe.py --gate` compares a form against the flat page of its own data at the same instant.
Nothing else is on the page: no dock, no species, no camera - a form is what is measured.

    python build_t5.py            # writes the build dir, then probe --gate and the motion gate are run by hand
"""
import sys
from pathlib import Path

REPO = Path("C:/Users/Snipe/Downloads/Outreach Program")
BUILD = REPO / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-p58-t5"
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))
sys.path.insert(0, str(REPO / "content/video_engine/tests/golden"))
import build_golden_sources as G  # noqa: E402
import build_scene_timeline_f as BST  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

SPAN = 10.0   # a page per scene, its whole build and its hold inside its own span


def page(kind: str, form: str | None) -> dict:
    if kind == "bars":
        spec = LPG.build_spec(G._form_bars_series(), "bars", None, "right")
    else:
        spec = LPG.build_spec(LPG.load_series(G.SERIES), "line", 0, "right")
    spec["field"] = "scribble"
    if form:
        spec["form"] = BST.page_form_spec(form, spec["builder"], f"t5 {kind}")
    return spec


def main() -> int:
    rows = [("s01", "bars", None), ("s02", "bars", "extruded_bar"),
            ("s03", "line", None), ("s04", "line", "tilted_line")]
    scenes = []
    for i, (sid, kind, form) in enumerate(rows):
        scenes.append({"scene_id": sid,
                       "world": {"kind": "ledger", "page": page(kind, form), "ken_burns": {"scale": 0, "x": 0, "y": 0}},
                       "exit": "cut", "span": [i * SPAN, (i + 1) * SPAN], "docks": [], "species": []})
    tl = G._timeline("P58 T5: the two chart forms beside their flat pages", scenes, {}, None)
    tl["runtime_s"] = len(rows) * SPAN
    out = RB.write_split(BUILD, tl, G._base_uris(), "t5-forms.timeline.json")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Steel and Paper — Script F motion plan and preview render.

Motion values are doc 29's, not invented. Settles are slow, moves are fast:
every arrival uses expo-out at 0.65-0.75s, every wipe is 0.62s quart-in-out.
Evidence enters at scale 0.88 -> 1.00 (never from zero — scale-from-zero with
bounce reads cartoon), and the world plate drifts 1.00 -> 1.04 underneath
while the evidence holds locked, so the eye separates world from data with
no labelling.

Audio is the two chained parts played as one: part two starts at the join
offset, which is part one's last word plus a 1.2s settle. The 5.18s of
trailing silence the provider left on part one is NOT used — doc 37 puts
silence over 1.2s in the editor's timeline.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BUILD = EP / "build-f"
CLAIMS = REPO / "content/video_engine/projects/systems-and-blowups/review/claims"
DECKS = Path(r"C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\sources\decks")

# doc 29 — the reference durations, in seconds
M = {
    "dock_in": 0.75, "dock_out": 0.72, "wash": 0.75, "pill": 0.65,
    "wipe": 0.62, "plate_alone": 1.7, "settle": 1.1, "savour": 2.2,
    "scale_from": 0.88, "parallax_to": 1.04,
    "expo_out": "cubic-bezier(.16,1,.3,1)",
    "quart_io": "cubic-bezier(.77,0,.175,1)",
}


STAMPED = json.loads((BUILD / "stamped-index.json").read_text(encoding="utf-8"))     if (BUILD / "stamped-index.json").exists() else {}


def find_asset(name: str) -> Path | None:
    # Teacher-stamped visuals are stored by slide path, keyed by image_id.
    if name in STAMPED and Path(STAMPED[name]).exists():
        return Path(STAMPED[name])
    # claims include borrowed registers, not just this episode's waves
    for wave in sorted(CLAIMS.glob("*plate*")):
        p = wave / "objects" / f"{name}.png"
        if p.exists():
            return p
    for p in EP.glob(f"evidence/objects/{name}.*"):
        return p
    for p in DECKS.rglob(f"{name}.png"):
        return p
    return None


def main() -> int:
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    plan = json.loads((BUILD / "plate-plan.json").read_text(encoding="utf-8"))
    dock = json.loads((BUILD / "evidence-dock.json").read_text(encoding="utf-8"))

    missing = []
    for p in plan:
        if not find_asset(p["plate"]):
            missing.append(("plate", p["plate"]))
    for d in dock:
        if not find_asset(d["asset"]):
            missing.append(("evidence", d["asset"]))

    # Motion plan: every cue with its doctrine-sourced curve and duration.
    # Plates TILE CONTINUOUSLY. The allocation sized them against bare
    # stretches — that is the density question — but a plate is the world
    # layer and it persists underneath evidence, drifting while the evidence
    # holds locked (doc 29 §1.4). Each plate therefore runs until the next
    # one starts, not until its allocated slot ends.
    plan = sorted(plan, key=lambda x: x["start"])
    for i, p in enumerate(plan):
        p["end"] = plan[i + 1]["start"] if i + 1 < len(plan) else tl["runtime_s"]
        p["hold"] = round(p["end"] - p["start"], 2)

    cues = []
    for p in plan:
        cues.append({
            "kind": "plate", "asset": p["plate"],
            "in": p["start"], "out": p["end"],
            "enter": {"type": "wipe", "dur": M["wipe"], "ease": M["quart_io"]},
            "hold": {"parallax_scale": [1.00, M["parallax_to"]]},
        })
    for d in dock:
        cues.append({
            "kind": "evidence", "asset": d["asset"], "species": d["species"],
            "in": round(d["at"] - 0.25, 2),
            "out": round(max(d["end"], d["at"] + 6.0) + M["settle"], 2),
            "enter": {"type": "dock", "dur": M["dock_in"], "ease": M["expo_out"],
                      "translateY": 32, "scale": [M["scale_from"], 1.0]},
            "exit": {"dur": M["dock_out"], "ease": M["expo_out"]},
            "wash": {"dur": M["wash"]},
            "anchor": d["anchor"],
        })
    cues.sort(key=lambda c: c["in"])
    (BUILD / "motion-plan.json").write_text(json.dumps({
        "runtime_s": tl["runtime_s"], "join": tl["join"],
        "durations": M, "cues": cues,
    }, indent=1), encoding="utf-8")

    print(f"MOTION PLAN — {len(cues)} cues "
          f"({sum(1 for c in cues if c['kind']=='plate')} plate, "
          f"{sum(1 for c in cues if c['kind']=='evidence')} evidence)")
    print(f"  durations from doc 29: dock-in {M['dock_in']}s expo-out, "
          f"wipe {M['wipe']}s quart-in-out, parallax 1.00->{M['parallax_to']}")
    if missing:
        print(f"\n  {len(missing)} ASSETS NOT FOUND ON DISK:")
        for k, n in missing[:12]:
            print(f"    {k:<9} {n}")
    else:
        print(f"  every asset resolved on disk")

    # Coverage: no frame without something on it.
    gaps, prev = [], 0.0
    for c in sorted((c for c in cues if c["kind"] == "plate"),
                    key=lambda c: c["in"]):
        if c["in"] - prev > 0.3:
            gaps.append((prev, c["in"]))
        prev = max(prev, c["out"])
    if tl["runtime_s"] - prev > 0.3:
        gaps.append((prev, tl["runtime_s"]))
    print(f"\n  uncovered frames: {len(gaps)} "
          f"{'(none — every second carries a plate)' if not gaps else gaps[:3]}")
    print(f"  wrote {BUILD / 'motion-plan.json'}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

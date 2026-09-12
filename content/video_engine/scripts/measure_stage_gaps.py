"""THE EMPTY STAGE, measured (P53 T2, BACKLOG R26-66).

A transition that TAKES the world leaves the stage with nothing on it while the narration keeps talking. Read frame
by frame on the first pages-only short: the suck at 13.8 s, the melt at 40.5 s and the vortex return at 58.5 s each
left cream and a caption for seconds under a live sentence. This measures it instead of describing it, per
transition kind, so a rule can be written on numbers.

WHAT IT MEASURES. At each scene boundary the player is seeked across a window and asked what is ON STAGE - the
same DOM the layout gate reads (`probe.derive`: the page's own title / sub / source / plot / data boxes, and every
paper dock). An instant with no page box and no dock is an EMPTY instant. The gap is the run of empty instants
around the boundary, and the words spoken inside it come from the build's own `timeline.json`.

    python measure_stage_gaps.py <build> [--step 0.1] [--lead 0.6] [--tail 3.0] [--json <path>]

Writes `<build>/stage-gaps.json` (the gate's input) and prints one line per boundary. The dip is the one
transition that MAY empty the stage (a dip is a world change), so it is measured and reported, never faulted.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import probe as P                     # noqa: E402
import gate_motion_density as G       # noqa: E402

EMPTY_KEYS = ("title", "sub", "source", "rail", "note", "plot", "data", "chart")
DIP_KINDS = ("dip",)                  # the transition that may empty the stage on purpose


def kind_of(exit_id) -> str:
    """The transition's family name: `suck:0.5,0.52` -> suck, `melt:splash` -> melt, None -> none."""
    return str(exit_id or "none").split(":")[0]


def on_stage(doc: dict) -> bool:
    """Is any world painted at this instant - a page's own ink, or a paper dock?"""
    page = doc.get("page") or {}
    if any(page.get(k) for k in EMPTY_KEYS):
        return True
    return bool(doc.get("docks"))


def words_in(tl: dict, a: float, b: float) -> list[str]:
    out = []
    for w in tl.get("narration", {}).get("words", []) if isinstance(tl.get("narration"), dict) else []:
        if a <= float(w.get("s", w.get("start", -1))) < b:
            out.append(str(w.get("w", "")))
    if out:
        return out
    for pg in tl.get("caption_pages", []) or []:
        for tok in pg.get("t") or []:
            s = tok.get("s")
            if s is not None and a <= float(s) < b:
                out.append(str(tok.get("w", "")))
    return out


def measure(build: Path, step: float, lead: float, tail: float) -> dict:
    tl = json.loads(G._timeline_path(build, None).read_text(encoding="utf-8"))
    scenes = tl.get("scenes", [])
    runtime = float(tl.get("runtime_s") or 0.0)
    bounds = []
    for i, s in enumerate(scenes):
        z = float(s["span"][1])
        if z >= runtime - 1e-6:
            continue
        bounds.append((z, kind_of(s.get("exit")), str(s.get("scene_id", "?")),
                       str(((scenes[i + 1].get("world") or {}).get("page") or {}).get("enter") or "none")
                       if i + 1 < len(scenes) else "none"))
    rows, empty_total = [], 0.0
    with P.Probe(build) as p:
        for at, kind, sid, nxt_enter in bounds:
            ts, flags = [], []
            t = max(0.0, at - lead)
            while t <= at + tail + 1e-9:
                ts.append(round(t, 3))
                flags.append(on_stage(p.at(t, why=f"stage-gap {sid}")))
                t += step
            # the run of empty instants that CONTAINS or TOUCHES the boundary
            gap_a = gap_b = None
            for t, ok in zip(ts, flags):
                if ok:
                    if gap_a is not None and gap_b is not None and gap_a <= at <= gap_b + step:
                        break
                    gap_a = gap_b = None
                    continue
                gap_a = t if gap_a is None else gap_a
                gap_b = t
            gap = 0.0 if gap_a is None else round(gap_b - gap_a + step, 2)
            spoken = words_in(tl, gap_a, gap_b + step) if gap_a is not None else []
            empty_total += gap
            rows.append({"at": at, "scene": sid, "exit": kind, "next_enter": nxt_enter,
                         "gap_s": gap, "from": gap_a, "to": None if gap_b is None else round(gap_b + step, 2),
                         "spoken": spoken, "licensed": kind in DIP_KINDS})
    return {"build": build.name, "runtime_s": runtime, "step": step,
            "empty_total_s": round(empty_total, 2),
            "empty_share": round(empty_total / runtime, 4) if runtime else 0.0,
            "boundaries": rows}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="the empty stage at every transition (P53 T2 / R26-66)")
    ap.add_argument("build", type=Path)
    ap.add_argument("--step", type=float, default=0.1)
    ap.add_argument("--lead", type=float, default=0.6)
    ap.add_argument("--tail", type=float, default=3.0)
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args(argv)
    doc = measure(a.build, a.step, a.lead, a.tail)
    out = a.json or (a.build / "stage-gaps.json")
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(f"stage gaps: {doc['empty_total_s']:.1f}s of {doc['runtime_s']:.1f}s "
          f"({100 * doc['empty_share']:.1f}% of the runtime) with no world on stage -> {out.name}")
    for r in doc["boundaries"]:
        tag = "licensed (a dip is a world change)" if r["licensed"] else ("SPOKEN OVER" if r["spoken"] else "silent")
        said = (" \"" + " ".join(r["spoken"][:8]) + ("..." if len(r["spoken"]) > 8 else "") + "\"") if r["spoken"] else ""
        print(f"  {r['at']:6.2f}  {r['scene']} exit={r['exit']:<6} -> enter={r['next_enter']:<6} "
              f"empty {r['gap_s']:4.1f}s  {tag}{said}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

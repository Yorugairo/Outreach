"""THE EMPTY STAGE, measured (P53 T2, BACKLOG R26-66; a picture plate is a world on stage, P58 2026-09-14).

A transition that TAKES the world leaves the stage with nothing on it while the narration keeps talking. Read frame
by frame on the first pages-only short: the suck at 13.8 s, the melt at 40.5 s and the vortex return at 58.5 s each
left cream and a caption for seconds under a live sentence. This measures it instead of describing it, per
transition kind, so a rule can be written on numbers.

WHAT COUNTS AS ON STAGE. At each scene boundary the player is seeked across a window, and an instant is ON STAGE when
EITHER
  ink / dock  the probe's record (`probe.derive`, the DOM the layout gate reads) holds a page's own title / sub /
              source / plot / data boxes, or a paper dock - exactly as before; OR
  picture     the scene the TIMELINE holds at t has a picture world (a plate, a clip, a vecmap: whatever
              `measure_spoken_visuals.on_stage_at` reports that is neither a ledger page nor `none`), and t is not
              inside a dip's black ramp [boundary - dip_s/2, boundary + dip_s/2].
The probe cannot see a plate world, so before the picture reason every plate read as an empty stage (the door into
the Treasury vault at 45.42 s read 2.2 s empty while the vault filled every frame). A ledger page with no ink painted
yet still reads EMPTY, so a suck or a melt into a page is still measured until its ink lands. The gap is the run of
empty instants around the boundary, and the words spoken inside it come from the build's own `timeline.json`.

THE DIP is the one transition that MAY empty the stage (a dip is a world change): its row takes the same rule, so it
measures the dip's black ramp, and it is reported licensed, never faulted. `picture_s` on each row is the time inside the
window that counts as on stage only because of its picture world.

    python measure_stage_gaps.py <build> [--step 0.1] [--lead 0.6] [--tail 3.0] [--json <path>]

Writes `<build>/stage-gaps.json` (the gate's input) and prints one line per boundary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import gate_motion_density as G       # noqa: E402
import measure_seam_frames as SF      # noqa: E402  (exit_parts, DIP_S: the dip's own window, one reading)
import measure_spoken_visuals as V    # noqa: E402  (on_stage_at: what the timeline puts on stage at t)

EMPTY_KEYS = ("title", "sub", "source", "rail", "note", "plot", "data", "chart")
DIP_KINDS = ("dip",)                  # the transition that may empty the stage on purpose
NOT_PICTURE = ("none", V.PAGE_KIND)   # a world kind that is not a picture: nothing, or a ledger page (ink decides)


def kind_of(exit_id) -> str:
    """The transition's family name: `suck:0.5,0.52` -> suck, `melt:splash` -> melt, None -> none."""
    return str(exit_id or "none").split(":")[0]


def probe_reason(doc: dict) -> str | None:
    """Why the probe's record counts as on stage: a page's own ink, a paper dock, or nothing."""
    page = doc.get("page") or {}
    if any(page.get(k) for k in EMPTY_KEYS):
        return "ink"
    return "dock" if doc.get("docks") else None


def on_stage(doc: dict) -> bool:
    """Is any world painted at this instant in the probe's record - a page's own ink, or a paper dock?"""
    return probe_reason(doc) is not None


def dip_windows(tl: dict) -> list[tuple[float, float]]:
    """Every dip's black ramp, symmetric about its boundary (measure_seam_frames' reading of the engine's dipA)."""
    scenes, out = tl.get("scenes", []), []
    for i in range(len(scenes) - 1):
        name, secs = SF.exit_parts(scenes[i + 1].get("exit"))
        if name in DIP_KINDS:
            at, half = float(scenes[i]["span"][1]), (secs or SF.DIP_S) / 2
            out.append((at - half, at + half))
    return out


def picture_on_stage(tl: dict, t: float, dips: list[tuple[float, float]]) -> bool:
    """Does the timeline hold a picture world (plate, clip, vecmap) at t, outside every dip's black ramp?"""
    if any(a <= t <= z for a, z in dips):
        return False
    return V.on_stage_at(tl, t)["world"] not in NOT_PICTURE


def boundaries(tl: dict) -> list[tuple[float, str, str, str]]:
    """(at, exit kind, outgoing scene id, the next page's enter) for every boundary before the runtime's end."""
    scenes = tl.get("scenes", [])
    runtime = float(tl.get("runtime_s") or 0.0)
    out = []
    for i, s in enumerate(scenes):
        z = float(s["span"][1])
        if z >= runtime - 1e-6 or i + 1 >= len(scenes):
            continue
        # E47: `exit` names the transition INTO the scene it sits on - the boundary at scenes[i]'s end is scenes[i+1].exit
        nxt = scenes[i + 1]
        page = (nxt.get("world") or {}).get("page")
        out.append((z, kind_of(nxt.get("exit")), str(s.get("scene_id", "?")),
                    str((page.get("enter") if isinstance(page, dict) else None) or "none")))
    return out


def gap_run(ts: list[float], flags: list[bool], at: float, step: float) -> tuple[float | None, float | None]:
    """The run of empty instants that CONTAINS or TOUCHES the boundary."""
    gap_a = gap_b = None
    for t, ok in zip(ts, flags):
        if ok:
            if gap_a is not None and gap_b is not None and gap_a <= at <= gap_b + step:
                break
            gap_a = gap_b = None
            continue
        gap_a = t if gap_a is None else gap_a
        gap_b = t
    return gap_a, gap_b


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


def measure_timeline(tl: dict, probe_at: Callable[[float, str], dict], step: float, lead: float, tail: float) -> dict:
    """Pure over the timeline and a probe callable `probe_at(t, scene_id) -> record` (the browser in `measure`)."""
    runtime = float(tl.get("runtime_s") or 0.0)
    dips = dip_windows(tl)
    rows, empty_total = [], 0.0
    for at, kind, sid, nxt_enter in boundaries(tl):
        licensed = kind in DIP_KINDS
        ts, flags, picture_n = [], [], 0
        t = max(0.0, at - lead)
        while t <= at + tail + 1e-9:
            tr = round(t, 3)
            ink = on_stage(probe_at(tr, sid))
            pic = not ink and picture_on_stage(tl, tr, dips)
            ts.append(tr)
            flags.append(ink or pic)
            picture_n += pic
            t += step
        gap_a, gap_b = gap_run(ts, flags, at, step)
        gap = 0.0 if gap_a is None else round(gap_b - gap_a + step, 2)
        spoken = words_in(tl, gap_a, gap_b + step) if gap_a is not None else []
        empty_total += gap
        rows.append({"at": at, "scene": sid, "exit": kind, "next_enter": nxt_enter,
                     "gap_s": gap, "from": gap_a, "to": None if gap_b is None else round(gap_b + step, 2),
                     "picture_s": round(picture_n * step, 2), "spoken": spoken, "licensed": licensed})
    return {"runtime_s": runtime, "step": step,
            "empty_total_s": round(empty_total, 2),
            "empty_share": round(empty_total / runtime, 4) if runtime else 0.0,
            "boundaries": rows}


def measure(build: Path, step: float, lead: float, tail: float) -> dict:
    import probe as P                 # the browser, only when a build is measured
    tl = json.loads(G._timeline_path(build, None).read_text(encoding="utf-8"))
    with P.Probe(build) as p:
        doc = measure_timeline(tl, lambda t, sid: p.at(t, why=f"stage-gap {sid}"), step, lead, tail)
    return {"build": build.name, **doc}


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
              f"empty {r['gap_s']:4.1f}s  picture {r['picture_s']:3.1f}s  {tag}{said}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

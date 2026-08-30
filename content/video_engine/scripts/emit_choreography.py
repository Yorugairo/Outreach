"""Emit the CHOREOGRAPHY STATEMENT and gate it, slot by slot.

The operator's diagnosis (2026-08-29): the reference builds were auditable
because the timeline was DATA - every visual state a declarative row. Our
player derives state per-frame from dock intervals plus implicit rules, so
no artifact existed that a person could verify slot by slot, and every
motion defect this session was found by the operator's eye instead of a
gate.

This script mirrors the player's four derivation rules and materializes the
result as an explicit, time-ordered event ledger - what enters, what exits,
how it leaves, which side it holds, when light rises and falls - then runs
the gates. The ledger ships with every build; a FAIL blocks it.

THE CONSTANTS MIRROR THE PLAYER. If a rule changes in the template it
changes here in the same commit, or the ledger lies.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BUILD = EP / "build-f"

# player constants (scene-evidence-player.template.html)
DOCK_JOIN, SNAP, WASH_BRIDGE, EXIT, WIPE = 2.5, 1.4, 1.2, 0.72, 0.62


def load_model():
    sp = importlib.util.spec_from_file_location("shot", EP / "SHOT-TABLE-F.py")
    shot = importlib.util.module_from_spec(sp); sp.loader.exec_module(shot)
    plan = sorted(r[:5] for r in shot.W)
    exits = {r[0]: (r[5] if len(r) > 5 else None) for r in shot.W}
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    scenes = []
    for i, (a, b, plate, ken, ds) in enumerate(plan):
        b2 = plan[i + 1][0] if i + 1 < len(plan) else tl["runtime_s"]
        scenes.append({"i": i + 1, "span": (a, b2), "plate": plate,
                       "exit": exits.get(a) or ("wipe" if ds else "cut"),
                       "docks": [{"slide": d[0], "slot": d[1],
                                  "enter": d[2], "exit": d[3]} for d in ds]})
    # mirror rule 1: coalesce same-slide docks. GROUP BY SLIDE first -
    # consecutive-only merging breaks when a DIFFERENT slide interleaves
    # the time sort (this gate caught it: pairing the scorecard between
    # two ladder rows made the ladder "re-enter").
    by_slide: dict = {}
    for sc2 in scenes:
        for d in sc2["docks"]:
            by_slide.setdefault(d["slide"], []).append(dict(d))
    out = []
    for slide, ds2 in by_slide.items():
        ds2.sort(key=lambda d: d["enter"])
        cur = None
        for d in ds2:
            if cur is not None and d["enter"] - cur["exit"] <= DOCK_JOIN:
                cur["exit"] = max(cur["exit"], d["exit"])
            else:
                cur = d
                out.append(d)
    out.sort(key=lambda d: d["enter"])
    # mirror rule 2: snap near-boundary exits
    bounds = [s["span"][0] for s in scenes]
    for d in out:
        for b in bounds:
            if d["enter"] < b and 0.05 < b - d["exit"] <= SNAP:
                d["exit"] = b; break
    # mirror rule 3: stable side per solo dock
    flip = 0
    for d in out:
        paired = any(o is not d and o["enter"] < d["exit"] and
                     o["exit"] > d["enter"] for o in out)
        d["side"] = "pair" if paired else ("r" if flip % 2 == 0 else "l")
        if not paired: flip += 1
    # mirror rule 4: wash intervals bridge sub-WASH_BRIDGE gaps
    washes = []
    for d in out:
        if washes and d["enter"] - washes[-1][1] < WASH_BRIDGE:
            washes[-1][1] = max(washes[-1][1], d["exit"])
        else:
            washes.append([d["enter"], d["exit"]])
    return scenes, out, washes, tl["runtime_s"]


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def main() -> int:
    scenes, docks, washes, runtime = load_model()
    ev, fails = [], []
    for s in scenes:
        ev.append((s["span"][0], f"SCENE  s{s['i']:02d}  {s['plate']}"
                   f"  ({s['span'][1]-s['span'][0]:.1f}s, exit {s['exit']})"))
    for d in docks:
        boundary = any(abs(d["exit"] - b) < 0.05 for b in
                       [s["span"][0] for s in scenes])
        how = "carried by the wipe front" if boundary else "fades in place"
        ev.append((d["enter"], f"ENTER  {d['slide']}  slot {d['slot']} "
                   f"side {d['side']}  holds {d['exit']-d['enter']:.1f}s"))
        ev.append((d["exit"], f"EXIT   {d['slide']}  {how}"))
    for a, b in washes:
        ev.append((a, f"LIGHT  wash rises (side of first card)"))
        ev.append((b + EXIT, f"LIGHT  wash falls"))
    ev.sort()

    # ---- gates, per slot ----
    for d in docks:
        sc = next(s for s in scenes
                  if s["span"][0] <= d["enter"] < s["span"][1])
        plate_len = sc["span"][1] - sc["span"][0]
        hold = d["exit"] - d["enter"]
        if hold < 2.2:
            fails.append(f"{mmss(d['enter'])} {d['slide']}: {hold:.1f}s hold "
                         f"< 2.2s - drop it rather than flash it (doc 29 8.9)")
        if plate_len < 8 and hold < plate_len * 0.8:
            fails.append(f"{mmss(d['enter'])} {d['slide']}: drive-by - "
                         f"{hold:.1f}s dock on a {plate_len:.1f}s plate "
                         f"(cadence: under ~8s, one piece or none)")
        for b in [s["span"][0] for s in scenes]:
            if 0.05 < b - d["exit"] <= SNAP:
                fails.append(f"{mmss(d['exit'])} {d['slide']}: exit in the "
                             f"awkward zone {b - d['exit']:.2f}s before a "
                             f"boundary - snap failed")
    for i in range(1, len(washes)):
        gap = washes[i][0] - washes[i - 1][1]
        if gap < WASH_BRIDGE:
            fails.append(f"{mmss(washes[i][0])}: wash gap {gap:.2f}s "
                         f"should have merged")
    # a slide must never re-enter moments after exiting - coalesce or space it
    seen = {}
    for d in docks:
        if d["slide"] in seen and d["enter"] - seen[d["slide"]] < 8.0:
            fails.append(f"{mmss(d['enter'])} {d['slide']}: re-enters "
                         f"{d['enter'] - seen[d['slide']]:.1f}s after exiting "
                         f"- coalesce it or space it")
        seen[d["slide"]] = d["exit"]
    covered = sum(b - a for a, b in washes)

    lines = ["# CHOREOGRAPHY STATEMENT - Steel and Paper (build F)",
             "",
             f"{len(scenes)} scenes - {len(docks)} coalesced docks - "
             f"{len(washes)} wash intervals covering {covered/runtime*100:.0f}% "
             f"of {runtime:.0f}s",
             "",
             "Every entering and exiting element, in order. Verify any slot",
             "by reading its lines; the gates below run on every build.",
             ""]
    lines += [f"  {mmss(t):>7}  {msg}" for t, msg in ev]
    lines += ["", "## Gates", ""]
    lines += [f"  FAIL  {f}" for f in fails] or ["  all slots clean"]
    (BUILD / "CHOREOGRAPHY.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"choreography: {len(ev)} events -> build-f/CHOREOGRAPHY.md")
    for f in fails:
        print(f"  FAIL  {f}")
    if not fails:
        print("  all slots clean")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

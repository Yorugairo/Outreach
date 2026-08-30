"""Retime the shot table onto a NEW take's clock - stage 6 of the chain.

Every dock carries a VERBATIM anchor in the script (the alignment pass
made this true), so a dock's new enter time is simply its anchor's word
time in the new timeline - deterministic, no ear needed. Plate windows
and unanchored dock instances (a slide's second appearance) warp through
piecewise-linear interpolation over all anchored control points.

Rewrites SHOT-TABLE-F.py IN PLACE textually - only the numbers change,
comments and structure survive. Shifts the Karp record payload by its
dock's delta. Idempotent only via git: rerun after reverting the table.

    python retime_to_take.py          # report, no writes
    python retime_to_take.py --write
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
LEAD = 0.20   # dock enters this far before its anchor's first word


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def main() -> int:
    write = "--write" in sys.argv
    tl = json.loads((EP / "build-f/timeline.json").read_text(encoding="utf-8"))
    words = tl["words"]
    # a hyphenated take word ("twenty-eight") is ONE entry but TWO anchor
    # tokens - flat-map each word into its normalized sub-tokens
    wt = [(t, w) for w in words for t in norm(w["w"]).split()]
    wtoks = [t for t, _ in wt]

    def anchor_time(text: str) -> float | None:
        toks = norm(text).split()
        n = len(toks)
        for i in range(len(wtoks) - n + 1):
            # some stored anchors are truncated mid-word ("when rates c") -
            # the last token matches as a prefix
            if (wtoks[i:i + n - 1] == toks[:-1]
                    and wtoks[i + n - 1].startswith(toks[-1])):
                return wt[i][1]["start"]
        return None

    docks_meta = {e["asset"]: e for e in json.loads(
        (EP / "build-f/evidence-dock.json").read_text(encoding="utf-8"))}
    sp = importlib.util.spec_from_file_location("shot", EP / "SHOT-TABLE-F.py")
    shot = importlib.util.module_from_spec(sp); sp.loader.exec_module(shot)
    rows = sorted(shot.W, key=lambda r: r[0])
    old_end = rows[-1][1]
    new_end = tl["runtime_s"]
    scale = new_end / old_end

    # assign each asset's anchor to the dock instance that lands nearest
    # under a provisional uniform scale (a slide's OTHER appearances warp)
    insts = [(r[0], d) for r in rows for d in r[4]]
    pins = {}   # id(dock tuple) -> new_enter
    ctrl = []
    misses = []
    by_asset: dict = {}
    for _, d in insts:
        by_asset.setdefault(d[0], []).append(d)
    for asset, ds in by_asset.items():
        meta = docks_meta.get(asset)
        anc = meta.get("anchor") if meta else None
        if not anc:
            misses.append(f"{asset}: NO ANCHOR - warps")
            continue
        at = anchor_time(anc)
        if at is None:
            misses.append(f"{asset}: anchor not in take - warps")
            continue
        tgt = at - LEAD
        best = min(ds, key=lambda d: abs(d[2] * scale - tgt))
        pins[id(best)] = tgt
        ctrl.append((best[2], tgt))

    ctrl += [(0.0, 0.0), (old_end, new_end)]
    ctrl.sort()
    mono = []
    for o, n in ctrl:
        if not mono or (o > mono[-1][0] and n > mono[-1][1]):
            mono.append([o, n])
    xs = [c[0] for c in mono]; ys = [c[1] for c in mono]

    def warp(t: float) -> float:
        for i in range(1, len(xs)):
            if t <= xs[i]:
                f = (t - xs[i-1]) / (xs[i] - xs[i-1])
                return ys[i-1] + f * (ys[i] - ys[i-1])
        return ys[-1] + (t - xs[-1])

    print(f"{len(ctrl)-2} anchored control points; old {old_end:.1f}s -> "
          f"new {new_end:.1f}s (x{scale:.3f})")
    for m in misses:
        print("  ", m)

    # PASS 1: final dock times in data - pin or warp, clamp to plate,
    # then stitch same-slide gaps that the stretch pushed into the
    # 2.5-8s awkward band (they were one coalesced hold on the old clock)
    final = {}
    for r in rows:
        a = warp(r[0])
        for d in r[4]:
            ne = pins.get(id(d), warp(d[2]))
            ne = max(a, ne)
            # exits are TOPIC-authored (E12): they warp with the
            # narration and are NEVER clamped to the host plate - a
            # cross-plate hold is legal and load-bearing
            nx = max(warp(d[3]), ne + 2.2)
            final[id(d)] = [ne, nx]
    by_slide2: dict = {}
    for _, d in insts:
        by_slide2.setdefault(d[0], []).append(d)
    for ds in by_slide2.values():
        ds.sort(key=lambda d: final[id(d)][0])
        for prev, nxt in zip(ds, ds[1:]):
            gap = final[id(nxt)][0] - final[id(prev)][1]
            if 0 < gap < 8.0:
                final[id(prev)][1] = final[id(nxt)][0]
    # PASS 1.6: standing fixes for the two classes every retime recreates
    # (a) same-slot overlap -> sequential handoff: pinned enters are the
    #     truth; the earlier dock's exit trims to the later's enter
    all_d = [d for _, d in insts]
    for i, d in enumerate(all_d):
        for o in all_d:
            if o is d or o[1] != d[1]:
                continue
            if (final[id(d)][0] < final[id(o)][0] < final[id(d)][1]):
                final[id(d)][1] = final[id(o)][0]
    # (b) a sub-8s plate's dock either fills the plate or leaves it -
    #     0.8*plate is the drive-by line; short holds stretch full-plate.
    #     TWO docks on such a plate become a PAIR (slots 0/1, both full):
    #     sequential handoff cannot fit under 8 seconds.
    slot_override = {}
    for r in rows:
        a, b = warp(r[0]), warp(r[1])
        if b - a >= 8.0 or not r[4]:
            continue
        short = any(final[id(d)][1] - final[id(d)][0] < 0.8 * (b - a)
                    for d in r[4])
        if not short:
            continue
        for i, d in enumerate(r[4][:2]):
            final[id(d)] = [a, b]
            slot_override[id(d)] = i

    # (a2) handoff again AFTER the stretch - (b) can re-create overlap
    for i, d in enumerate(all_d):
        for o in all_d:
            if o is d or o[1] != d[1]:
                continue
            if (final[id(d)][0] < final[id(o)][0] < final[id(d)][1]):
                final[id(d)][1] = final[id(o)][0]

    dropped = []
    for _, d in insts:
        ne, nx = final[id(d)]
        if nx - ne < 2.2:
            dropped.append(f"{d[0]} at {ne:.1f}s (hold {nx-ne:.1f}s)")
    if dropped:
        print("SUB-MINIMUM HOLDS (fix by hand or drop):")
        for x in dropped:
            print("  ", x)

    # PASS 2: textual rewrite - window floats + dock tuple floats,
    # comments intact
    src = (EP / "SHOT-TABLE-F.py").read_text(encoding="utf-8")
    out_lines = []
    ri = 0
    row_by_key = {(r[0], r[1], r[2]): r for r in rows}
    win_re = re.compile(r"^(\(\s*)([\d.]+)(,\s*)([\d.]+)(,\s*\"([^\"]+)\")")
    dock_re = re.compile(r"\(\"([^\"]+)\",\s*(\d+),\s*([\d.]+),\s*([\d.]+)\)")
    for line in src.splitlines():
        m = win_re.match(line.strip())
        if m and (float(m.group(2)), float(m.group(4)), m.group(6)) in row_by_key:
            row = row_by_key[(float(m.group(2)), float(m.group(4)), m.group(6))]
            a, b = warp(row[0]), warp(row[1])
            def sub_win(mm):
                return f"{mm.group(1)}{a:.1f}{mm.group(3)}{b:.1f}{mm.group(5)}"
            newline = win_re.sub(sub_win, line.strip(), count=1)
            indent = line[:len(line) - len(line.lstrip())]
            def sub_dock(mm):
                name, slot = mm.group(1), mm.group(2)
                oe, ox = float(mm.group(3)), float(mm.group(4))
                match = next((d for d in row[4]
                              if d[0] == name and abs(d[2] - oe) < 0.01), None)
                if match is None:
                    return mm.group(0)
                ne, nx = final[id(match)]
                slot = str(slot_override.get(id(match), int(slot)))
                return f'("{name}",{slot},{ne:.1f},{nx:.1f})'
            newline = dock_re.sub(sub_dock, newline)
            out_lines.append(indent + newline)
            ri += 1
        else:
            out_lines.append(line)
    print(f"retimed {ri}/{len(rows)} rows, {len(pins)} docks pinned to anchors")

    # Karp record payload: shift by its dock's delta
    karp = docks_meta.get("ev-doc-karp")
    kd = next((d for _, d in insts if d[0] == "ev-doc-karp"), None)
    if karp and karp.get("record") and kd:
        delta = (pins.get(id(kd), warp(kd[2]))) - kd[2]
        r = karp["record"]
        r["words"] = [[w, round(t + delta, 2)] for w, t in r["words"]]
        if "end" in r:
            r["end"] = round(r["end"] + delta, 2)
        print(f"karp record shifted {delta:+.2f}s")

    if not write:
        print("dry run - re-run with --write")
        return 0
    (EP / "SHOT-TABLE-F.py").write_text("\n".join(out_lines) + "\n",
                                        encoding="utf-8")
    (EP / "build-f/evidence-dock.json").write_text(
        json.dumps(list(docks_meta.values()), indent=1), encoding="utf-8")
    print("written: SHOT-TABLE-F.py + evidence-dock.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

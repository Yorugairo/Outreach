"""MOTION-DENSITY GATE - the screen never goes still (ruling E21, doc 29 s9.25).

Runs on a BUILT episode directory (stage 7/8 output): the compiled
`*.timeline.json` (scenes, docks, caption pages, runtime), `evidence-dock.json`
(scheduled docks - read ONLY when the timeline carries no docks: P35 T0 found
the dock file on an older clock than the timeline, divergence 26.4 vs 50.4)
and `motion-plan.json` (cues). It is the check the
hand-authored shot table never had: doc 29 s8.19's 12s gap-fill lived in the
five-minute cut builder and printed a number; Steel and Paper shipped with
23% of its runtime in stretches over 12s where nothing moved but the Ken
Burns and a lower-third caption, and its opening minute was the thinnest
minute of the video.

What counts as a VISUAL EVENT (doc 29 s9.25): a scene boundary, a dock
entering or leaving, a badge/pill reveal, captions in STAGE mode, or a
LEDGER PAGE building (s9.28 C5 / D1: roll-out, field, outline, build start,
build complete - the hold after that is still). A page START is an
EVIDENCE ENTRY (D2). Ken Burns and lower-third (anchor-mode) captions do
NOT count - they are what a viewer reads as stillness.

  M01  no stretch > 12s without a visual event            FAIL   (s8.19 / s9.25)
  M02  stretches > 8s (working target)                    WARN
  M03  evidence enters at least every 45s, every phase    FAIL   ("evidence every 15-45s")
  M04  distinct plates >= runtime / 12s                   WARN   (s9.13)
  M05  no plate held > 20s unless two docks sit over it   FAIL   (s9.13 hard ceiling)
  M06  caption cadence: 4-6 words a page, >= 20 pages/min WARN   (s9.15 r7 / build_caption_pages)
  M07  the opening minute is not the thinnest minute      FAIL   (E21: P1 densest, never thinnest)
  M08  stage-mode captions declared on every still stretch FAIL once the timeline carries cap_mode;
       until then INFO listing where stage captions are REQUIRED + a JUDGE row
  J01  savor beats keep their picture (card up, badge lit) JUDGE

    python gate_motion_density.py <build-dir> [--timeline NAME.timeline.json]
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from dataclasses import dataclass
from pathlib import Path

STILL_FAIL_S = 12.0        # doc 29 s8.19 MAX_BARE, s9.25 ceiling
STILL_WARN_S = 8.0         # s9.25 working target
EVIDENCE_GAP_MAX_S = 45.0  # doc 29: evidence every 15-45s
PLATE_SECONDS = 12.0       # s9.13: runtime / 12s distinct plates
PLATE_HOLD_MAX_S = 20.0    # s9.13 hard ceiling, unless two docks over it
CAP_WORDS = (4, 6)         # build_caption_pages: MAX_WORDS 6, 4-6 target
CAP_PAGES_PER_MIN_MIN = 20.0
OPENING_S = 60.0           # E21: the opening minute
WINDOW_S = 60.0

# LEDGER PAGE beats (doc 29 s9.26 / s9.28 C5, D1, D2; P35 T3 template `const LP`):
# ROLL 0.6 the cream unrolls, BLEED 2.8 the charcoal field bleeds in, OUTLINE 0.8
# the clean edge draws, BUILD 3.0 the chart lands. Each boundary is a visual
# event from the scene start; the start itself is an evidence entry; the hold
# after BUILD completes is still (C5) and needs a dock, plate life, or stage
# captions past 12s. Keep in step with the template's LP constants.
LP_ROLL_S, LP_BLEED_S, LP_OUTLINE_S, LP_BUILD_S = 0.6, 2.8, 0.8, 3.0
PAGE_BEAT_OFFSETS = (0.0, LP_ROLL_S, LP_ROLL_S + LP_BLEED_S,
                     LP_ROLL_S + LP_BLEED_S + LP_OUTLINE_S,
                     LP_ROLL_S + LP_BLEED_S + LP_OUTLINE_S + LP_BUILD_S)   # 0, 0.6, 3.4, 4.2, 7.2
DOCK_SOURCE_TIMELINE = "timeline"            # scenes[].docks enter/exit/badge_at - the player's own clock
DOCK_SOURCE_FILE = "evidence-dock.json"      # fallback only: a timeline that carries no docks at all


@dataclass(frozen=True)
class Gate:
    id: str
    level: str
    message: str
    src: str


def _load(build: Path, timeline_name: str | None) -> tuple[dict, list[dict], dict]:
    tl_path = build / timeline_name if timeline_name else next(iter(sorted(build.glob("*.timeline.json"))), None)
    if not tl_path or not tl_path.exists():
        raise SystemExit(f"no *.timeline.json in {build}")
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    docks_p = build / "evidence-dock.json"
    docks = json.loads(docks_p.read_text(encoding="utf-8")) if docks_p.exists() else []
    mp_p = build / "motion-plan.json"
    mp = json.loads(mp_p.read_text(encoding="utf-8")) if mp_p.exists() else {"cues": []}
    return tl, docks, mp


def _dock_span(d: dict) -> tuple[float, float] | None:
    a = d.get("at", d.get("start", d.get("enter")))
    z = d.get("end", d.get("exit", d.get("until")))
    return (float(a), float(z)) if isinstance(a, (int, float)) and isinstance(z, (int, float)) else None


def _is_page(scene: dict) -> bool:
    return scene.get("world", {}).get("kind") == "ledger"


def _plate_id(scene: dict) -> str | None:
    """A plate's asset id; a ledger page is its own plate (s9.28 C5: a page holds like a plate)."""
    w = scene.get("world", {})
    return w.get("asset_id") or (f"ledger:{scene.get('scene_id', '?')}" if _is_page(scene) else None)


def _dock_clock(scenes: list[dict], docks: list[dict]) -> tuple[list[tuple[float, float]], list[float], str]:
    """(dock spans, badge reveal times, source). The TIMELINE's own docks win;
    `evidence-dock.json` is read only when no scene carries a dock (P35 T0)."""
    tl_docks = [d for s in scenes for d in s.get("docks", [])]
    if tl_docks:
        spans = [x for x in (_dock_span(d) for d in tl_docks) if x]
        badges = [float(b) for d in tl_docks for b in d.get("badge_at", [])]
        return spans, badges, DOCK_SOURCE_TIMELINE
    return [x for x in (_dock_span(d) for d in docks) if x], [], DOCK_SOURCE_FILE


def _page_events(scenes: list[dict]) -> tuple[list[float], list[float]]:
    """(visual events, evidence entries) contributed by ledger pages (s9.28 C5, D1, D2)."""
    starts = [float(s["span"][0]) for s in scenes if _is_page(s)]
    beats = [round(a + off, 2) for a in starts for off in PAGE_BEAT_OFFSETS]
    return beats, starts


def _collect_events(tl: dict, mp: dict, spans: list, badges: list, page_beats: list, stage_rows: list) -> set[float]:
    events: set[float] = set()
    for s in tl.get("scenes", []):
        events.add(float(s["span"][0])); events.add(float(s["span"][1]))
    for a, z in spans:
        events.add(a); events.add(z)
    events.update(badges); events.update(page_beats)
    for c in mp.get("cues", []):
        if c.get("kind") != "plate":
            events.add(float(c["in"])); events.add(float(c.get("out", c["in"])))
    for r in stage_rows:
        events.add(float(r["t"]))
    return events


def _per_minute(runtime: float, ev: list[float], entries: list[float]) -> list[tuple[float, float, float]]:
    dens = []
    for m in range(int(runtime // WINDOW_S) + 1):
        lo, hi = m * WINDOW_S, min((m + 1) * WINDOW_S, runtime)
        if hi - lo < 20:
            continue
        n = sum(1 for t in ev if lo <= t < hi) / ((hi - lo) / 60)
        nd = sum(1 for a in entries if lo <= a < hi) / ((hi - lo) / 60)
        dens.append((lo, n, nd))
    return dens


def analyse(tl: dict, docks: list[dict], mp: dict) -> dict:
    runtime = float(tl.get("runtime_s") or max(s["span"][1] for s in tl["scenes"]))
    scenes = tl.get("scenes", [])
    pages = tl.get("caption_pages", [])
    spans, badges, dock_source = _dock_clock(scenes, docks)
    page_beats, page_starts = _page_events(scenes)
    # stage-mode captions count as events when the timeline declares them
    tl_rows = tl.get("rows", tl.get("timeline", []))
    stage_rows = [r for r in tl_rows if isinstance(r, dict) and r.get("cap_mode") == "stage"]
    events = _collect_events(tl, mp, spans, badges, page_beats, stage_rows)
    ev = sorted(t for t in events if 0.0 <= t <= runtime)
    if not ev or ev[0] > 0:
        ev.insert(0, 0.0)
    if ev[-1] < runtime:
        ev.append(runtime)
    still = sorted(((a, b - a) for a, b in zip(ev, ev[1:])), key=lambda x: -x[1])
    # evidence entry gaps, whole runtime: a dock entering or a page starting (D2)
    entries = sorted([a for a, _ in spans] + page_starts)
    pts = [0.0] + entries + [runtime]
    ev_gaps = sorted(((a, b - a) for a, b in zip(pts, pts[1:])), key=lambda x: -x[1])
    # plates: a page is its own plate and holds like one (C5)
    plate_ids = [_plate_id(s) for s in scenes]
    holds = [(float(s["span"][0]), float(s["span"][1]) - float(s["span"][0]), _plate_id(s)) for s in scenes]
    over_hold = []
    for a, d, pid in holds:
        if d > PLATE_HOLD_MAX_S:
            n = sum(1 for x, z in spans if x < a + d and z > a)
            if n < 2:
                over_hold.append((a, d, pid, n))
    wc = [len(p.get("t", [])) for p in pages]
    return {"runtime": runtime, "events": ev, "still": still, "ev_gaps": ev_gaps, "plates": plate_ids,
            "over_hold": over_hold, "wc": wc, "pages": pages, "dens": _per_minute(runtime, ev, entries),
            "spans": spans, "dock_source": dock_source, "n_pages": len(page_starts),
            "has_cap_mode": bool(stage_rows) or any(isinstance(r, dict) and "cap_mode" in r for r in tl_rows)}


def run(tl: dict, docks: list[dict], mp: dict) -> tuple[list[Gate], dict]:
    A = analyse(tl, docks, mp)
    R = A["runtime"]
    mm = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    g: list[Gate] = []
    add = lambda i, lvl, m, s: g.append(Gate(i, lvl, m, s))
    still_fail = [(a, d) for a, d in A["still"] if d > STILL_FAIL_S]
    still_warn = [(a, d) for a, d in A["still"] if d > STILL_WARN_S]
    tot = sum(d for _, d in still_fail)
    add("M01", "FAIL" if still_fail else "PASS",
        (f"{len(still_fail)} stretches > {STILL_FAIL_S:.0f}s with no visual event beyond Ken Burns/anchor captions "
         f"({tot:.0f}s = {100 * tot / R:.0f}% of runtime); worst {still_fail[0][1]:.1f}s at {mm(still_fail[0][0])}") if still_fail
        else f"longest still stretch {A['still'][0][1]:.1f}s at {mm(A['still'][0][0])}",
        "doc 29 s8.19 / s9.25 stillness ceiling")
    add("M02", "WARN" if still_warn else "PASS", f"{len(still_warn)} stretches > {STILL_WARN_S:.0f}s (working target)", "doc 29 s9.25")
    gap = A["ev_gaps"][0] if A["ev_gaps"] else (0.0, 0.0)
    add("M03", "FAIL" if gap[1] > EVIDENCE_GAP_MAX_S else "PASS",
        f"longest wait for evidence to enter: {gap[1]:.0f}s from {mm(gap[0])}" + (" (no docks at all)" if not A["spans"] else ""),
        "doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)")
    n_plates = len(set(p for p in A["plates"] if p))
    want = int(R / PLATE_SECONDS)
    add("M04", "WARN" if n_plates < want else "PASS", f"{n_plates} distinct plates; target runtime/12s = {want}", "doc 29 s9.13 plate density")
    oh = A["over_hold"]
    add("M05", "FAIL" if oh else "PASS",
        f"{len(oh)} plates held > {PLATE_HOLD_MAX_S:.0f}s without two docks over them; worst {oh[0][2]} {oh[0][1]:.0f}s at {mm(oh[0][0])}" if oh else "no plate over the 20s hold ceiling",
        "doc 29 s9.13 hard ceiling")
    if A["wc"]:
        ppm = len(A["pages"]) / (R / 60)
        mean_w = st.mean(A["wc"])
        ok = CAP_WORDS[0] <= mean_w <= CAP_WORDS[1] and ppm >= CAP_PAGES_PER_MIN_MIN
        add("M06", "PASS" if ok else "WARN", f"{len(A['pages'])} caption pages = {ppm:.0f}/min, {mean_w:.1f} words/page", "s9.15 r7 / build_caption_pages 4-6 words")
    if dens := A["dens"]:
        opening = [d for d in dens if d[0] < OPENING_S][0]
        ranked = sorted(dens, key=lambda x: x[1])
        rank = [d[0] for d in ranked].index(opening[0]) + 1
        med = st.median(d[1] for d in dens)
        add("M07", "FAIL" if opening[1] < med else "PASS",
            f"opening minute: {opening[1]:.1f} events/min, {opening[2]:.1f} docks/min - rank {rank}/{len(dens)} from the bottom; episode median {med:.1f}/min",
            "E21: the opening is the densest minute, never the thinnest")
    req = [(a, d) for a, d in A["still"] if d > STILL_WARN_S]
    if A["has_cap_mode"]:
        add("M08", "PASS", "timeline carries cap_mode; stage rows counted as events above", "doc 29 s9.25 caption STAGE mode")
    else:
        add("M08", "INFO", f"timeline carries no cap_mode yet - stage captions REQUIRED on {len(req)} stretches: "
            + ", ".join(f"{mm(a)}+{d:.0f}s" for a, d in sorted(req)[:12]) + (" ..." if len(req) > 12 else ""),
            "doc 29 s9.25 caption STAGE mode (player template pending)")
        add("J02", "JUDGE", "captions on the still stretches above are centred, large, per-word explosive - not the lower-third anchor", "doc 29 s9.25 #2")
    add("J01", "JUDGE", "every savor beat holds its picture (card up, badge lit), never a bare plate with a drift", "doc 29 s9.25 #3")
    return g, _stats(A, tot)


def _stats(A: dict, still_total: float) -> dict:
    R = A["runtime"]
    mm = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"
    return {"runtime": mm(R), "visual_events": f"{len(A['events'])} ({len(A['events']) / (R / 60):.1f}/min)",
            "docks": len(A["spans"]), "dock_source": A["dock_source"], "ledger_pages": A["n_pages"],
            "still_over_12s_share": f"{100 * still_total / R:.0f}%",
            "per_minute": " ".join(f"{mm(lo)}:{n:.0f}/{nd:.0f}" for lo, n, nd in A["dens"])}


REPORT_NAME = "GATES-MOTION.md"  # written beside the timeline by the build (P34 T4); consulted by render_episode.py
LEVEL_ORDER = {"FAIL": 0, "WARN": 1, "PASS": 2, "INFO": 3, "JUDGE": 4}


def fail_count(gates: list[Gate]) -> int:
    return sum(1 for x in gates if x.level == "FAIL")


def report_text(gates: list[Gate], stats: dict, build_dir: Path) -> str:
    """The gate's stdout, verbatim: header, stats, gates sorted by level, RESULT line."""
    lines = [f"=== MOTION DENSITY GATE: {build_dir} ==="]
    lines += [f"  {k:>20}: {v}" for k, v in stats.items()]
    lines.append("")
    for x in sorted(gates, key=lambda x: (LEVEL_ORDER[x.level], x.id)):
        lines.append(f"  [{x.level:5}] {x.id} {x.message}\n          {x.src}")
    n = lambda lvl: sum(1 for x in gates if x.level == lvl)
    lines.append(f"\nRESULT: {n('FAIL')} FAIL / {n('WARN')} WARN / {n('PASS')} PASS / {n('JUDGE')} JUDGE / {n('INFO')} INFO")
    return "\n".join(lines)


def write_report(build_dir: Path, timeline_name: str | None = None) -> tuple[Path, int]:
    """Run the gate on a build dir and write `<build_dir>/GATES-MOTION.md`.

    The report is the gate's stdout inside a fenced block, headed by the
    build dir name and closed by a `VERDICT: PASS|FAIL (<n> FAIL)` line that
    `render_episode.py` reads before a full render (E21 / doc 29 s9.25).
    Returns the report path and the FAIL count.
    """
    build_dir = Path(build_dir)
    tl, docks, mp = _load(build_dir, timeline_name)
    gates, stats = run(tl, docks, mp)
    n_fail = fail_count(gates)
    verdict = "FAIL" if n_fail else "PASS"
    body = (f"# MOTION GATE — {build_dir.name}\n\n```text\n{report_text(gates, stats, build_dir)}\n```\n\n"
            f"VERDICT: {verdict} ({n_fail} FAIL)\n")
    out = build_dir / REPORT_NAME
    out.write_text(body, encoding="utf-8")
    return out, n_fail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("build", type=Path, help="episode build dir (build-f)")
    ap.add_argument("--timeline", help="timeline file name inside the build dir")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tl, docks, mp = _load(args.build, args.timeline)
    gates, stats = run(tl, docks, mp)
    print(report_text(gates, stats, args.build))
    return 1 if fail_count(gates) else 0


if __name__ == "__main__":
    raise SystemExit(main())

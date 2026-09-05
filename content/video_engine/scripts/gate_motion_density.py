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
LEDGER PAGE building (s9.28 C5 / D1: roll-out, field, punch, build start,
build complete - the hold after that is still), or a TARGETED SPECIES
firing on a scene (s9.27 MOTION MENU "Gate treatment" column: a punch at
its punch, a focus zoom at departure and arrival, plate life stepping at
10 fps, ...). A page START is an EVIDENCE ENTRY (D2). Ken Burns and
lower-third (anchor-mode) captions do NOT count - they are what a viewer
reads as stillness.

  M01  no stretch > 12s without a visual event            FAIL   (s8.19 / s9.25)
  M02  stretches > 8s (working target)                    WARN
  M03  evidence enters at least every 45s, every phase    FAIL   ("evidence every 15-45s")
  M04  distinct plates >= runtime / 12s                   WARN   (s9.13)
  M05  no plate held > 20s unless two docks sit over it   FAIL   (s9.13 hard ceiling)
  M06  caption cadence: 4-6 words a page, >= 20 pages/min WARN   (s9.15 r7 / build_caption_pages)
  M07  the opening minute is not the thinnest minute      FAIL   (E21: P1 densest, never thinnest)
  M08  stage-mode captions declared on every still stretch FAIL once the timeline carries cap_mode;
       until then INFO listing where stage captions are REQUIRED + a JUDGE row
  M09  one camera move per window: no scene stacks two of   FAIL   (s9.27 precedence / s9.28 C3)
  M14  a camera move never overlaps an evidence build      FAIL   (47 s2 G-a / doc 07 Pillar 4)
       punch | focus_zoom | pull_back, or one over Ken Burns
  M10  opening stillness: no still stretch > 6s begins      FAIL   (E24 / s9.29: 4-6s in the first 30-60s)
       in the first 60s
  M11  the first chart: enters 0:08-0:20, annotated by a    FAIL   (E24 / s9.29; sound cue absent = WARN)
       spotlight/callout/punch/focus_zoom within 1.5s
  M12  a chart is the proof, not the homework: a chart dock FAIL   (E25 / s9.30)
       never spans a scene boundary; hold <= 10s anywhere,
       <= 6s inside the opening minute (re-enter it instead)
  J01  savor beats keep their picture (card up, badge lit) JUDGE

    python gate_motion_density.py <build-dir> [--timeline NAME.timeline.json]
"""
from __future__ import annotations

import argparse
import hashlib
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

# LEDGER PAGE beats (doc 29 s9.26, E22 addendum 6 / s9.28 C5, D1, D2; the template's
# `const LP = { ROLL: 0.7, SAVOR: 0.8, FIELD: 2.4, PUNCH: 0.5, INK: 2.0, BUILD: 3.0 }`,
# operator 2026-09-03): ROLL the cream unrolls, SAVOR the half-savor, FIELD the charcoal
# fills to the deckle (E22 addendum 7: no outline - the deckle is the edge), PUNCH the
# punch-in, BUILD the chart lands, and the FOCUS action fires at the build's end. Each
# boundary is a visual event from the scene start; the start itself is an evidence
# entry; the hold after the focus is still (C5) and needs a dock, plate life, or stage
# captions past 12s. Keep in step with the template's LP constants.
LP_ROLL_S, LP_SAVOR_S, LP_FIELD_S, LP_PUNCH_S, LP_BUILD_S = 0.7, 0.8, 2.4, 0.5, 3.0
PAGE_BEAT_OFFSETS = (0.0, LP_ROLL_S, LP_ROLL_S + LP_SAVOR_S,
                     LP_ROLL_S + LP_SAVOR_S + LP_FIELD_S,
                     LP_ROLL_S + LP_SAVOR_S + LP_FIELD_S + LP_PUNCH_S,
                     LP_ROLL_S + LP_SAVOR_S + LP_FIELD_S + LP_PUNCH_S + LP_BUILD_S)
# = (0.0, 0.7, 1.5, 3.9, 4.4, 7.4): roll-out, savor start, field start, punch, build start, build end + focus
LP_BADGE0_S, LP_BADGE_STEP_S = 0.4, 0.9   # page badges spring in after the build: build end + 0.4 + 0.9k (template LP.BADGE0 / BADGE_STEP)
DOCK_SOURCE_TIMELINE = "timeline"            # scenes[].docks enter/exit/badge_at - the player's own clock
DOCK_SOURCE_FILE = "evidence-dock.json"      # fallback only: a timeline that carries no docks at all

# TARGETED SPECIES events (doc 29 s9.27 MOTION MENU, "Gate treatment" column;
# P35 T7). A scene's `species` rows are {"kind", "at", "dur", "target"}; the
# table says which edges of each are visual events: "at" = one event at the
# firing, "end" = one at at+dur. Camera punch: "one event at the punch". Scribble
# callout: "event at draw". Focus zoom: "event at departure and arrival".
# Feathered spotlight: "events per glide" (each glide is a row). Pull-back
# reveal: "events across the pull" (departure and arrival). Beat-freeze exit:
# "events at hit and cut". Radial reveal: "scene event". Push hand-off: "event".
# "stepping" = plate life, "events while stepping": the stop-motion cadence is
# quantized to 10 fps, so one event every 1/10 s across its duration - plate
# life fills a bare plate. Squiggle marks "count as a caption event in stage
# mode only": the stage page under them already counts (M08), so they add no
# event of their own for now.
SPECIES_EVENTS = {"punch": ("at",), "callout": ("at",), "focus_zoom": ("at", "end"),
                  "spotlight": ("at", "end"), "squiggle": (), "pull_back": ("at", "end"),
                  "plate_life": "stepping", "beat_freeze": ("at", "end"),
                  "radial": ("at",), "push": ("at",)}
PLATE_LIFE_STEP_S = 0.1    # s9.27 plate life: quantize t to 10 fps; each step is an event
# s9.27 precedence / s9.28 C3: punch, focus zoom, pull-back and Ken Burns are
# mutually exclusive per window. M09 mirrors the builder's validate_species so a
# hand-edited timeline is caught too.
CAMERA_MOVES = ("punch", "focus_zoom", "pull_back")

# OPENING-MINUTE gates (ruling E24 / doc 29 s9.29 - the analyst's drop-off review the
# operator verified against analytics) and the chart-hold rule (ruling E25 / s9.30).
OPENING_STILL_MAX_S = 6.0        # E24 / doc 29 s9.29: 4-6s in the first 30-60s - the opening's own stillness ceiling
PARADOX_S = 8.0                  # E24 / doc 29 s9.29: the first chart enters only after the 8s paradox is paid
FIRST_CHART_MAX_S = 20.0         # E24 / doc 29 s9.29: ... and no later than 0:20
CHART_SPECIES = ("chart", "data")  # E24 / doc 29 s9.29: the evidence species that count as "the first chart"
ANNOTATED_KINDS = ("spotlight", "callout", "punch", "focus_zoom")  # E24 / doc 29 s9.29: the chart's divergence is pointed at
ANNOTATE_TOL_S = 1.5             # E24 / doc 29 s9.29: the targeted species fires with the enter, not later
CUE_TOL_S = 1.5                  # E24 / doc 29 s9.29: a sound cue lands with the enter (absent = WARN)
CHART_HOLD_MAX_S = 10.0          # E25 / doc 29 s9.30: the chart is the proof, not the homework - hold ceiling anywhere
OPENING_CHART_HOLD_MAX_S = 6.0   # E25 / doc 29 s9.30: ... and inside the opening minute
SRC_M10 = "E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s"
SRC_M11 = "E24 / doc 29 s9.29: the first chart enters 0:08-0:20, annotated on its divergence, with a sound cue"
SRC_M12 = "E25 / doc 29 s9.30: the chart is the proof, not the homework"
DOCK_BUILD_S = 1.5               # 47 s2 G-a: a card's entrance - the wipe / fly-in - is a build the eye must be free to read
BADGE_SETTLE_S = 0.6             # ... and each badge reveal is one too, settling ~0.6s after badge_at
CAMERA_MOVE_S = 1.2              # a camera species with no declared dur is credited this long
SRC_M14 = "47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move"


@dataclass(frozen=True)
class Gate:
    id: str
    level: str
    message: str
    src: str


def _timeline_path(build: Path, timeline_name: str | None) -> Path:
    tl_path = build / timeline_name if timeline_name else next(iter(sorted(build.glob("*.timeline.json"))), None)
    if not tl_path or not tl_path.exists():
        raise SystemExit(f"no *.timeline.json in {build}")
    return tl_path


def _load(build: Path, timeline_name: str | None) -> tuple[dict, list[dict], dict]:
    tl_path = _timeline_path(build, timeline_name)
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
    """(visual events, evidence entries) contributed by ledger pages (s9.28 C5, D1, D2).
    A beat past the page's own scene end never happened - a short page credits only
    the beats it had time to play (never motion inside the scene after it)."""
    starts, beats = [], []
    for s in scenes:
        if not _is_page(s):
            continue
        a, z = float(s["span"][0]), float(s["span"][1])
        starts.append(a)
        beats += [round(a + off, 2) for off in PAGE_BEAT_OFFSETS if a + off < z]
        # inline badges ride their line's draw-complete (already a build event); only rail pills are extra reveals
        n_badges = sum(1 for b in ((s.get("world", {}).get("page") or {}).get("badges") or []) if not b.get("inline"))
        beats += [round(a + PAGE_BEAT_OFFSETS[-1] + LP_BADGE0_S + LP_BADGE_STEP_S * k, 2) for k in range(n_badges)
                  if a + PAGE_BEAT_OFFSETS[-1] + LP_BADGE0_S + LP_BADGE_STEP_S * k < z]
    return beats, starts


def _species_events(scenes: list[dict]) -> list[float]:
    """Visual events contributed by targeted species rows, per SPECIES_EVENTS (s9.27)."""
    out: list[float] = []
    for s in scenes:
        a, z = (float(s["span"][0]), float(s["span"][1])) if s.get("span") else (None, None)
        for sp in s.get("species", []):
            edges = SPECIES_EVENTS.get(sp.get("kind"), ())
            at, dur = float(sp.get("at", 0.0)), float(sp.get("dur", 0.0))
            # a species that runs past its scene stops with the scene: no event is credited beyond span end
            inside = a is not None and a <= at <= z
            keep = (lambda t: t <= z) if inside else (lambda t: True)
            if edges == "stepping":
                steps = int(round(dur / PLATE_LIFE_STEP_S))
                out += [round(at + k * PLATE_LIFE_STEP_S, 2) for k in range(steps + 1) if keep(at + k * PLATE_LIFE_STEP_S)]
                continue
            if "at" in edges:
                out.append(round(at, 2))
            if "end" in edges and keep(at + dur):
                out.append(round(at + dur, 2))
    return out


def _camera_clashes(scenes: list[dict]) -> list[tuple[str, str]]:
    """(scene_id, why) for every scene that stacks two camera moves, or one over
    a Ken Burns drift (scale > 0) - s9.27 precedence / s9.28 C3."""
    out = []
    for s in scenes:
        moves = [sp.get("kind") for sp in s.get("species", []) if sp.get("kind") in CAMERA_MOVES]
        scale = float(s.get("world", {}).get("ken_burns", {}).get("scale", 0) or 0)
        sid = s.get("scene_id", "?")
        if len(moves) > 1:
            out.append((sid, " + ".join(moves)))
        elif moves and scale > 0:
            out.append((sid, f"{moves[0]} over Ken Burns scale {scale:g}"))
    return out


def _build_windows(scenes: list[dict], docks: list[dict]) -> list[tuple[str, float, float]]:
    """(slide, start, end) for every evidence BUILD: the card's entrance plus its badge reveals.
    The timeline's own docks win; the evidence-dock.json shape is the fallback (P35 T0)."""
    tl_docks = [d for s in scenes for d in s.get("docks", [])]
    out = []
    for d in (tl_docks or docks):
        span = _dock_span(d)
        if not span:
            continue
        a = span[0]
        z = max(a + DOCK_BUILD_S, *[float(b) + BADGE_SETTLE_S for b in d.get("badge_at", [])] or [a])
        out.append((str(d.get("slide", d.get("asset", "?"))), a, min(z, span[1])))
    return out


def _build_clashes(scenes: list[dict], docks: list[dict]) -> list[tuple[str, str]]:
    """(scene_id, why) for every camera move whose window intersects an evidence build window
    anywhere on the clock - M14 (47 s2 G-a). M09 is about stacking moves; this is about moving
    while the viewer is supposed to be reading a build."""
    builds = _build_windows(scenes, docks)
    out = []
    for s in scenes:
        for sp in s.get("species", []):
            if sp.get("kind") not in CAMERA_MOVES:
                continue
            at = float(sp.get("at", 0.0)); end = at + float(sp.get("dur", CAMERA_MOVE_S) or CAMERA_MOVE_S)
            for slide, a, z in builds:
                if at < z and a < end:
                    out.append((s.get("scene_id", "?"), f"{sp['kind']} {at:.1f}-{end:.1f}s over {slide} build {a:.1f}-{z:.1f}s"))
    return out


def _build_gate(clashes: list[tuple[str, str]]) -> Gate:
    if clashes:
        msg = (f"{len(clashes)} camera moves land on an evidence build: " + ", ".join(f"{sid} ({why})" for sid, why in clashes[:12])
               + (" ..." if len(clashes) > 12 else ""))
    else:
        msg = "no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal"
    return Gate("M14", "FAIL" if clashes else "PASS", msg, SRC_M14)


def _collect_events(tl: dict, mp: dict, spans: list, badges: list, page_beats: list, stage_rows: list,
                    species_events: list = ()) -> set[float]:
    events: set[float] = set()
    for s in tl.get("scenes", []):
        events.add(float(s["span"][0])); events.add(float(s["span"][1]))
    for a, z in spans:
        events.add(a); events.add(z)
    events.update(badges); events.update(page_beats); events.update(species_events)
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
    # P34 T5: the build declares the mode per caption page (cap_mode at the page's first word);
    # a stage page is a visual event at its start (s9.25 #1: "captions in stage mode")
    stage_rows = [r for r in tl_rows if isinstance(r, dict) and r.get("cap_mode") == "stage"]
    stage_rows += [{"t": pg["s"]} for pg in pages if isinstance(pg, dict) and pg.get("cap_mode") == "stage"]
    # P35 T7: targeted species fire as tabled in SPECIES_EVENTS (s9.27 gate column)
    events = _collect_events(tl, mp, spans, badges, page_beats, stage_rows, _species_events(scenes))
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
            "camera_clashes": _camera_clashes(scenes),
            "has_cap_mode": bool(stage_rows) or any(isinstance(r, dict) and "cap_mode" in r for r in tl_rows)
                            or any(isinstance(pg, dict) and "cap_mode" in pg for pg in pages)}


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
    else:
        add("M06", "INFO", "no caption pages in the build - M06 not run (no silent skip: build caption-pages.json first)", "s9.15 r7")
    if dens := A["dens"]:
        opening = [d for d in dens if d[0] < OPENING_S][0]
        ranked = sorted(dens, key=lambda x: x[1])
        rank = [d[0] for d in ranked].index(opening[0]) + 1
        med = st.median(d[1] for d in dens)
        add("M07", "FAIL" if opening[1] < med else "PASS",
            f"opening minute: {opening[1]:.1f} events/min, {opening[2]:.1f} docks/min - rank {rank}/{len(dens)} from the bottom; episode median {med:.1f}/min",
            "E21: the opening is the densest minute, never the thinnest")
    else:
        add("M07", "INFO", f"runtime {R:.0f}s has no full minute to rank - M07 not run (no silent skip)", "E21")
    req = [(a, d) for a, d in A["still"] if d > STILL_WARN_S]
    if A["has_cap_mode"]:
        # ENFORCED (P34 T5): stage pages already count as events, so any stretch still over the
        # ceiling is one the captions did not take - the shot table must author stage rows there
        bare = [(a, d) for a, d in A["still"] if d > STILL_FAIL_S]
        add("M08", "FAIL" if bare else "PASS",
            (f"{len(bare)} still stretches > {STILL_FAIL_S:.0f}s carry no stage-mode caption: "
             + ", ".join(f"{mm(a)}+{d:.0f}s" for a, d in sorted(bare)[:12]) + (" ..." if len(bare) > 12 else "")) if bare
            else "timeline declares cap_mode; every stretch over the ceiling carries stage captions (counted as events above)",
            "doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves)")
    else:
        add("M08", "INFO", f"timeline carries no cap_mode yet - stage captions REQUIRED on {len(req)} stretches: "
            + ", ".join(f"{mm(a)}+{d:.0f}s" for a, d in sorted(req)[:12]) + (" ..." if len(req) > 12 else ""),
            "doc 29 s9.25 caption STAGE mode (player template pending)")
        add("J02", "JUDGE", "captions on the still stretches above are centred, large, per-word explosive - not the lower-third anchor", "doc 29 s9.25 #2")
    g.append(_camera_gate(A["camera_clashes"]))
    g.append(_build_gate(_build_clashes(tl.get("scenes", []), docks)))   # M14 (P37 T1)
    # E24 / E25: the opening minute and the chart-as-proof rule
    g += [_opening_still_gate(A["still"]), _first_chart_gate(tl, docks, mp), _chart_hold_gate(tl, docks)]
    add("J01", "JUDGE", "every savor beat holds its picture (card up, badge lit), never a bare plate with a drift", "doc 29 s9.25 #3")
    return g, _stats(A, tot)


def _mm(s: float) -> str:
    return f"{int(s // 60)}:{int(s % 60):02d}"


def _scene_at(scenes: list[dict], t: float) -> dict | None:
    return next((s for s in scenes if float(s["span"][0]) <= t < float(s["span"][1])), None)


def chart_docks(tl: dict, docks: list[dict]) -> tuple[list[dict], bool]:
    """Every CHART dock as {enter, exit, asset, scene}, by enter time, plus whether the
    species was known. The timeline's own docks win (P35 T0); the evidence map's species
    filters to CHART_SPECIES - a timeline with no evidence map treats EVERY dock as a
    chart candidate (E24 M11 says so in its message)."""
    scenes = tl.get("scenes", [])
    evidence = tl.get("evidence") or {}
    known = bool(evidence)
    tl_docks = [(d, s) for s in scenes for d in s.get("docks", [])]
    pairs = tl_docks if tl_docks else [(d, None) for d in docks]
    out = []
    for d, s in pairs:
        span = _dock_span(d)
        if not span:
            continue
        asset = d.get("slide") or d.get("asset") or d.get("asset_id") or "?"
        if known and evidence.get(asset, {}).get("species") not in CHART_SPECIES:
            continue
        out.append({"enter": span[0], "exit": span[1], "asset": asset, "scene": s or _scene_at(scenes, span[0])})
    return sorted(out, key=lambda x: x["enter"]), known


def _cue_near(t: float, tl: dict, mp: dict) -> bool | None:
    """True/False: a non-plate motion-plan cue or a timeline `sound` entry within CUE_TOL_S;
    None when the build carries neither structure (E24 M11: 'no sound structure to check')."""
    if not mp.get("cues") and "sound" not in tl:
        return None
    ats = [float(c["in"]) for c in mp.get("cues", []) if c.get("kind") != "plate"]
    ats += [float(x["at"]) for x in tl.get("sound", []) or []
            if isinstance(x, dict) and isinstance(x.get("at"), (int, float))]
    return any(abs(a - t) <= CUE_TOL_S for a in ats)


def _opening_still_gate(still: list[tuple[float, float]]) -> Gate:
    """M10 (E24): no still stretch over OPENING_STILL_MAX_S begins inside the opening minute."""
    bad = sorted((a, d) for a, d in still if a < OPENING_S and d > OPENING_STILL_MAX_S)
    if bad:
        return Gate("M10", "FAIL", f"{len(bad)} still stretches > {OPENING_STILL_MAX_S:.0f}s begin in the first "
                    f"{OPENING_S:.0f}s: " + ", ".join(f"{_mm(a)}+{d:.0f}s" for a, d in bad), SRC_M10)
    return Gate("M10", "PASS", f"no still stretch > {OPENING_STILL_MAX_S:.0f}s begins in the first {OPENING_S:.0f}s", SRC_M10)


def _first_chart_gate(tl: dict, docks: list[dict], mp: dict) -> Gate:
    """M11 (E24): the first chart (chart/data dock, or ledger page) enters 8-20s, carries a
    targeted species within ANNOTATE_TOL_S, and a sound cue within CUE_TOL_S (WARN)."""
    charts, known = chart_docks(tl, docks)
    pages = [{"enter": float(s["span"][0]), "asset": f"ledger:{s.get('scene_id', '?')}", "scene": s}
             for s in tl.get("scenes", []) if _is_page(s)]
    cands = sorted(charts + pages, key=lambda x: x["enter"])
    if not cands:
        return Gate("M11", "FAIL", "no chart enters at all - no chart/data dock and no ledger page in the timeline", SRC_M11)
    t, asset, scene = cands[0]["enter"], cands[0]["asset"], cands[0]["scene"]
    why = []
    if not PARADOX_S <= t <= FIRST_CHART_MAX_S:
        why.append(f"first chart {asset} enters at {t:.1f}s - outside {PARADOX_S:.0f}-{FIRST_CHART_MAX_S:.0f}s")
    hits = [sp for sp in (scene or {}).get("species", [])
            if sp.get("kind") in ANNOTATED_KINDS and abs(float(sp.get("at", -1e9)) - t) <= ANNOTATE_TOL_S]
    if not hits:
        why.append("first chart enters full and unannotated - declare a spotlight/callout/punch on its divergence")
    cue = _cue_near(t, tl, mp)
    sound = "" if cue else ("; WARN no sound structure to check" if cue is None
                            else f"; WARN no sound cue within {CUE_TOL_S:.1f}s of the enter at {t:.1f}s")
    note = "" if known else " (no evidence species in the timeline - every dock treated as a chart candidate)"
    if why:
        return Gate("M11", "FAIL", "; ".join(why) + sound + note, SRC_M11)
    msg = f"first chart {asset} enters at {t:.1f}s with {hits[0]['kind']} at {float(hits[0]['at']):.1f}s"
    return Gate("M11", "PASS" if cue else "WARN", msg + sound + note, SRC_M11)


def _chart_hold_offences(tl: dict, docks: list[dict]) -> list[str]:
    """E25 M12: a chart dock that straddles a later scene's start, or holds past the ceiling."""
    scenes = tl.get("scenes", [])
    out = []
    for d in chart_docks(tl, docks)[0]:
        enter, exit_, hold = d["enter"], d["exit"], d["exit"] - d["enter"]
        crossed = [s for s in scenes if enter < float(s["span"][0]) < exit_]
        ceiling = OPENING_CHART_HOLD_MAX_S if enter < OPENING_S else CHART_HOLD_MAX_S
        why = []
        if crossed:
            plates = [_plate_id(d["scene"]) or "?"] if d["scene"] else []
            plates += [_plate_id(s) or "?" for s in crossed]
            why.append(f"crosses {len(crossed)} scene boundaries ({' -> '.join(plates)})")
        if hold > ceiling:
            why.append(f"hold {hold:.1f}s > {ceiling:.0f}s" + (" (opening minute)" if enter < OPENING_S else ""))
        if why:
            out.append(f"{d['asset']} {_mm(enter)}-{_mm(exit_)} " + ", ".join(why))
    return out


def _chart_hold_gate(tl: dict, docks: list[dict]) -> Gate:
    bad = _chart_hold_offences(tl, docks)
    if bad:
        return Gate("M12", "FAIL", f"{len(bad)} chart docks held as homework: " + "; ".join(bad[:12])
                    + (" ..." if len(bad) > 12 else "") + " - re-enter the chart spotlit on the new datum rather than hold", SRC_M12)
    return Gate("M12", "PASS", f"no chart dock spans a scene boundary or holds past {CHART_HOLD_MAX_S:.0f}s "
                f"({OPENING_CHART_HOLD_MAX_S:.0f}s in the opening minute)", SRC_M12)


def _camera_gate(clashes: list[tuple[str, str]]) -> Gate:
    """M09 (P35 T7): one camera move per window - mirrors build_scene_timeline_f.validate_species
    so a hand-edited timeline (two moves on a scene, or a move over Ken Burns) is caught too."""
    if clashes:
        msg = (f"{len(clashes)} scenes stack camera moves: " + ", ".join(f"{sid} ({why})" for sid, why in clashes[:12])
               + (" ..." if len(clashes) > 12 else ""))
    else:
        msg = "no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns"
    return Gate("M09", "FAIL" if clashes else "PASS", msg, "doc 29 s9.27 precedence / s9.28 C3: one camera move per window")


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
    tl_path = _timeline_path(build_dir, timeline_name)
    gates, stats = run(tl, docks, mp)
    n_fail = fail_count(gates)
    verdict = "FAIL" if n_fail else "PASS"
    # the timeline hash keys the report to the build it measured; render_episode refuses a
    # full render when the timeline on disk no longer hashes to it (a stale report is no report)
    digest = hashlib.sha256(tl_path.read_bytes()).hexdigest()
    body = (f"# MOTION GATE — {build_dir.name}\n\n```text\n{report_text(gates, stats, build_dir)}\n```\n\n"
            f"TIMELINE: {tl_path.name} sha256:{digest}\n"
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

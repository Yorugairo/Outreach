"""P51 T4 - THE DETERMINISM CHECK: what the preview shows is what the render will make.

The documented killer of every live-edit loop (the grill ledger, 2026-09-11; Remotion's own docs
name it): a change that looks right in the preview and dies in the render, because the preview
arrived at the frame by PLAYING into it and the render arrives COLD. So every instant a change
touches is rendered twice from the same build:

    WARM   the page a scrub session leaves behind - one browser page, the instants walked in
           order, each approached by seeks from just before it, as play would arrive;
    COLD   a fresh page per instant, seeking straight to it - what render_episode does.

The two frames' RGB bytes are hashed and compared. A mismatch means the frame is a function of
history, not of t; it is printed with both PNGs written beside the build and the check exits 1.

    python determinism_check.py <build>                          # every gate instant is --all's job; this needs instants
    python determinism_check.py <build> --instants 55.31 59.57
    python determinism_check.py <build> --against <old>.timeline.json    # the instants ITS diff names
    python determinism_check.py <build> --all                     # every instant the layout gate looks at

The one known exception is R26-21: a cold seek into the 0.45 s `snap` window shows the page full
for one frame, because the snapped page reads its card box from the dock loop's layout offsets.
The check NAMES that class where it fires (it never hides it); `--strict` fails on it anyway.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import gate_motion_density as G  # noqa: E402
import probe as P  # noqa: E402
import render_baseline as RB  # noqa: E402

WARM_LEAD = (0.60, 0.30, 0.12)   # the approach to an instant: three seeks, as play would arrive
SNAP_S = 0.45                    # the engine's SNAP_S - R26-21's window (scene-evidence-engine.mjs)
OUT_DIR = "determinism"          # <build>/determinism/<t>-warm.png, -cold.png
TICK = 50                        # instants are deduped to 1/50 s, as the probe's gate instants are


# ---- the diff: which instants a change touched -------------------------------------------------------------------

def _keyed(items: list[dict], key: str) -> dict[str, dict]:
    return {f"{i}:{it.get(key, '?')}": it for i, it in enumerate(items or [])}


def _num(v) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _species_instants(sp: dict) -> list[float]:
    """Every instant one species entry declares: its `at`, the end of its run, and the later
    moments a species can name - a chip's `cross_at`, a flow node's `swap.at`, a held light's
    `until`. (`crossed` is a state, not a clock: a chip that lands already crossed moves nothing
    but its own `at`.)"""
    out = []
    at = _num(sp.get("at"))
    if at is not None:
        out.append(at)
        dur = _num(sp.get("dur"))
        if dur is not None:
            out.append(at + dur)
    for k in ("cross_at", "until"):
        v = _num(sp.get(k))
        if v is not None:
            out.append(v)
    swap = sp.get("swap")
    if isinstance(swap, dict):
        v = _num(swap.get("at"))
        if v is not None:
            out.append(v)
    return out


def changed_instants(old: dict, new: dict) -> list[tuple[float, str]]:
    """The instants that differ between two compiled timelines: scene by scene, dock by dock,
    species by species. A changed dock gives its enter and its exit, a changed species its own
    moments, a changed scene its span's ends - the same rule the probe's `gate_instants` follows,
    that the instants come from the timeline and are never guessed."""
    runtime = float(new.get("runtime_s") or max((s["span"][1] for s in new.get("scenes") or []), default=0.0))
    out: dict[int, tuple[float, str]] = {}

    def add(t: float | None, why: str) -> None:
        if t is None:
            return
        t = max(0.0, min(float(t), max(0.0, runtime - 0.01)))
        out.setdefault(int(round(t * TICK)), (round(t, 3), why))

    O = {str(s.get("scene_id")): s for s in old.get("scenes") or []}
    N = {str(s.get("scene_id")): s for s in new.get("scenes") or []}

    for sid, s in N.items():
        span = s.get("span") or [0.0, runtime]
        o = O.get(sid)
        if o is None:
            add(span[0], f"{sid} new scene")
            add(span[1], f"{sid} new scene end")
            continue
        if any(o.get(k) != s.get(k) for k in ("span", "world", "exit", "camera")):
            add(span[0], f"{sid} scene changed")
            add(span[1], f"{sid} span end")
        od, nd = _keyed(o.get("docks"), "slide"), _keyed(s.get("docks"), "slide")
        for k, d in nd.items():
            if od.get(k) != d:
                name = d.get("slide", k)
                add(_num(d.get("enter")) if d.get("enter") is not None else span[0], f"{sid} dock {name} enter")
                add(_num(d.get("exit")) if d.get("exit") is not None else span[1], f"{sid} dock {name} exit")
        for k, d in od.items():
            if k not in nd:
                add(_num(d.get("enter")) or span[0], f"{sid} dock {d.get('slide', k)} gone")
        osp, nsp = _keyed(o.get("species"), "kind"), _keyed(s.get("species"), "kind")
        for k, sp in nsp.items():
            if osp.get(k) != sp:
                for t in _species_instants(sp) or [span[0]]:
                    add(t, f"{sid} species {sp.get('kind', k)}")
        for k, sp in osp.items():
            if k not in nsp:
                for t in _species_instants(sp) or [span[0]]:
                    add(t, f"{sid} species {sp.get('kind', k)} gone")

    for sid, s in O.items():
        if sid not in N:
            add((s.get("span") or [0.0])[0], f"{sid} scene gone")

    # anything OUTSIDE the scenes (the kinetics flags, the caption style, the sound plan) can move
    # any frame of the runtime: name it on every scene's first instant rather than pretend to know.
    for k in set(old) | set(new):
        if k in ("scenes", "runtime_s") or old.get(k) == new.get(k):
            continue
        for sid, s in N.items():
            add((s.get("span") or [0.0])[0], f"{sid} {k} changed")

    return [v for _k, v in sorted(out.items())]


def snap_windows(tl: dict) -> list[tuple[float, float, str]]:
    """R26-21's windows: a page that enters by `snap`/`camera` grows from a landed card's LAYOUT
    box, which a cold seek into the first 0.45 s has not recorded yet."""
    out = []
    for s in tl.get("scenes") or []:
        pg = (s.get("world") or {}).get("page") or {}
        if pg.get("snap_from") and str(pg.get("enter", "")).split("=")[0] in ("snap", "camera"):
            a = float((s.get("span") or [0.0])[0])
            out.append((a, a + SNAP_S, str(s.get("scene_id"))))
    return out


def known_class(t: float, windows: list[tuple[float, float, str]]) -> str | None:
    for a, b, sid in windows:
        if a <= t <= b:
            return f"KNOWN R26-21 (a cold seek into {sid}'s {SNAP_S:.2f} s snap window)"
    return None


# ---- the two arrivals --------------------------------------------------------------------------------------------

class Frames:
    """One served build, one browser: a WARM page kept across the instants and a COLD page per
    instant. The page preparation is render_baseline's, so both frames are the renderer's frames."""

    def __init__(self, build: Path, timeline_name: str | None = None, html_name: str = "player.html"):
        from playwright.sync_api import sync_playwright
        self.build = Path(build)
        self.tl_path = G._timeline_path(self.build, timeline_name)
        self.tl = json.loads(self.tl_path.read_text(encoding="utf-8"))
        self.aspect = str(self.tl.get("aspect") or "16:9")
        self.w, self.h = P.stage_size(self.aspect)
        self.html = self.build / html_name
        if not self.html.exists():
            raise SystemExit(f"no {html_name} in {self.build} - build the episode first")
        self.srv, self.port = RB.serve(self.build)
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch(headless=True)
        self.errs: list[str] = []
        self.warm_page = self._open()

    def _open(self):
        page = self.br.new_context(viewport={"width": self.w, "height": self.h}).new_page()
        page.on("pageerror", lambda e: self.errs.append(str(e)))
        page.goto(f"http://127.0.0.1:{self.port}/{self.html.name}", wait_until="networkidle", timeout=300000)
        RB.prepare_page(page, self.w, self.h)
        return page

    def _seek(self, page, t: float) -> None:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t;"
                      " s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        page.evaluate("() => window.__clipsSeeked ? window.__clipsSeeked() : null")

    def warm(self, t: float) -> bytes:
        """As play arrives: the same page as the last instant, walked in from just before this one."""
        for lead in WARM_LEAD:
            self._seek(self.warm_page, max(0.0, t - lead))
        return RB.frame_png(self.warm_page, t, (self.w, self.h))

    def cold(self, t: float) -> bytes:
        """As the renderer arrives: a page that has never been anywhere else."""
        page = self._open()
        try:
            return RB.frame_png(page, t, (self.w, self.h))
        finally:
            page.context.close()

    def close(self) -> None:
        self.br.close()
        self.pw.stop()
        self.srv.shutdown()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


def _hash(png: bytes) -> str:
    return hashlib.sha256(RB.rgb_bytes(png)[1]).hexdigest()


def run(build: Path, instants: list[tuple[float, str]], timeline_name: str | None = None,
        strict: bool = False, max_instants: int = 0, log=print) -> dict:
    """Render every instant warm and cold and compare. Returns the report; writes the two PNGs of
    any mismatch to <build>/determinism/."""
    build = Path(build)
    instants = sorted(instants, key=lambda x: x[0])
    truncated = 0
    if max_instants and len(instants) > max_instants:
        truncated = len(instants) - max_instants
        instants = instants[:max_instants]
    rows: list[dict] = []
    if not instants:
        return {"build": str(build), "instants": [], "ok": True, "mismatches": 0, "known": 0,
                "truncated": 0, "summary": "ok (no instant to check)"}
    with Frames(build, timeline_name) as F:
        windows = snap_windows(F.tl)
        log(f"determinism_check {build.name}  ({F.tl_path.name}, {F.aspect}, {len(instants)} instant(s))")
        for t, why in instants:
            warm, cold = F.warm(t), F.cold(t)
            hw, hc = _hash(warm), _hash(cold)
            row = {"t": t, "why": why, "warm": hw, "cold": hc, "match": hw == hc, "known": None}
            if hw != hc:
                row["known"] = known_class(t, windows)
                d = build / OUT_DIR
                d.mkdir(parents=True, exist_ok=True)
                (d / f"{t:.2f}-warm.png").write_bytes(warm)
                (d / f"{t:.2f}-cold.png").write_bytes(cold)
                row["frames"] = [str(d / f"{t:.2f}-warm.png"), str(d / f"{t:.2f}-cold.png")]
                log(f"  [MISMATCH] {t:7.2f}  {why}  warm {hw[:12]} cold {hc[:12]}"
                    + (f"  {row['known']}" if row["known"] else "")
                    + f"\n             frames: {row['frames'][0]}  {row['frames'][1]}")
            else:
                log(f"  [ ok      ] {t:7.2f}  {why}  {hw[:12]}")
            rows.append(row)
        if F.errs:
            log(f"  page errors: {F.errs[:3]}")
    hard = [r for r in rows if not r["match"] and (strict or not r["known"])]
    known = [r for r in rows if not r["match"] and r["known"] and not strict]
    summary = ("mismatch at " + ", ".join(f"{r['t']:.2f}" for r in hard)) if hard else (
        f"ok ({len(known)} known R26-21 at " + ", ".join(f"{r['t']:.2f}" for r in known) + ")" if known else "ok")
    if truncated:
        summary += f" [+{truncated} instant(s) not checked]"
    log(f"determinism: {sum(1 for r in rows if r['match'])} ok, {len(hard)} mismatch, {len(known)} known"
        + (f", {truncated} not checked" if truncated else ""))
    return {"build": str(build), "instants": rows, "ok": not hard, "mismatches": len(hard),
            "known": len(known), "truncated": truncated, "summary": summary}


def instants_for(build: Path, against: Path | None, explicit: list[float] | None,
                 every: bool, timeline_name: str | None = None) -> list[tuple[float, str]]:
    """The instants to check: named, or the diff against an older compiled timeline, or every
    instant the layout gate looks at (`probe.gate_instants`)."""
    tl_path = G._timeline_path(Path(build), timeline_name)
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    if explicit:
        return [(float(t), "named") for t in explicit]
    if every:
        return P.gate_instants(tl)
    if against:
        old = json.loads(Path(against).read_text(encoding="utf-8"))
        return changed_instants(old, tl)
    return []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="render the changed instants warm and cold and compare (P51 T4)")
    ap.add_argument("build", type=Path)
    ap.add_argument("--against", type=Path, help="an older compiled timeline: its diff names the instants")
    ap.add_argument("--instants", type=float, nargs="*", help="the instants to check, in seconds")
    ap.add_argument("--all", action="store_true", help="every instant the layout gate looks at")
    ap.add_argument("--timeline", help="the compiled timeline's file name (default: the only one in the build)")
    ap.add_argument("--strict", action="store_true", help="fail on the known R26-21 class too")
    ap.add_argument("--max", type=int, default=0, help="check at most N instants (0: all of them)")
    ap.add_argument("--json", action="store_true", help="the report as JSON on stdout")
    a = ap.parse_args(argv)
    instants = instants_for(a.build, a.against, a.instants, a.all, a.timeline)
    if not instants:
        print("no instant to check - pass --instants, --against <old timeline> or --all")
        return 0
    rep = run(a.build, instants, a.timeline, strict=a.strict, max_instants=a.max,
              log=(lambda *_a, **_k: None) if a.json else print)
    if a.json:
        print(json.dumps(rep, indent=1))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

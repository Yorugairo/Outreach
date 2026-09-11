"""SELF-WATCH - the one-shot bar as a build artifact (P51 T3, 2026-09-11).

The operator's watch begins only when this file is clean (the grill of 2026-09-11: "we don't come close enough to a
first pass, then we spend a lot of time improving and iterating"). The runner is a pure function of the build: it runs
the numbers first - the layout probe (M25's input), the motion gate, the species-by-sentence lint, the viewer's and the
script gates' last verdicts - then grabs the OPENING as contact sheets (0:60 on a short, 3:00 on a long, at 2 s steps,
12 tiles a sheet) and writes `<build>/SELF-WATCH.md`:

  section 1  the mechanical rows, every verdict filled by the tools (a FAIL here ends the report: NOT CLEAN)
  section 2  the ten O-rows the AGENT fills by reading the sheets (Read on the PNGs, one sheet at a time) - the runner
             writes them as TODO with the tile list; it never fills a read it did not do
  section 3  ONE verdict line: `NOT CLEAN - <the first failing row>`, or `TODO - the agent reads the sheets and fills
             O1-O10`. CLEAN is the agent's word, written after the read; a build handed to the operator carries CLEAN.

    python content/video_engine/scripts/self_watch.py <build> --project <project dir> --script <report stem> [--long|--short] [--step 2] [--tile 360]

Exit 1 when section 1 carries a FAIL (the report is still written), 0 otherwise. The checklist itself is the parent's
(SELF-WATCH-CHECKLIST, P51 T3); human gate 1 is the operator's first read of a real report.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint_species_choice as L  # noqa: E402
import probe as P  # noqa: E402

HERE = Path(__file__).resolve().parent
GATE = HERE / "gate_motion_density.py"
REPORT_NAME = "SELF-WATCH.md"
SHEET_DIR = "self-watch"
LONG_FORM_S = 180.0                       # the script gates' route: a measured clock under 3:00 is a short
OPENING_S = {"short": 60.0, "long": 180.0}   # the operator: "the first 3 minutes on long format, first 60 seconds on shorts"
STEP_S, TILE_PX, PER_SHEET = 2.0, 360, 12
ROW_RE = re.compile(r"^\s*\[(PASS |FAIL |WARN |INFO |JUDGE)\]\s*(\S+)\s*(.*)$")
DETAIL_W = 420

# The O-rows (the checklist, verbatim): the agent's read of the sheets. The runner writes them as TODO.
O_ROWS = (
    ("O1", "the package is answered on sentence 1 (E24 / E27): the first frame and the first sentence deliver the title's claim"),
    ("O2", "the promise lands by 0:45 (G09; a short: the mechanism by 0:10)"),
    ("O3", "the first chart enters 0:08-0:20 lit (M11) and reads at a glance (E28: sign is geometry, the scale printed)"),
    ("O4", "every sentence-act with an available species has a row, or the bridge is deliberate (each `no row` line answered: bridge / the light holds / cut)"),
    ("O5", "no dead band: no 2 s tile pair identical to the eye inside the opening; nothing held still past its sentence (E21, E49)"),
    ("O6", "no overlap the probe could not see: a card over ink, a label under a card, paper in the strip (M25 read against the tiles)"),
    ("O7", "the citations readable at the phone scale (>= 11 CSS px; the source line clear of every card)"),
    ("O8", "the captions read as phrases, never chased (shorts: PHRASE captions; the strip never covers a figure)"),
    ("O9", "every card lands on its word and leaves at the turn (E25 / E50): the landing tile and the exit tile named"),
    ("O10", "the chart is the world (E61): every plate row in the opening names its use; a plate that proves nothing and docks nothing is a bridge, said so"),
)


# ---------------------------------------------------------------- the numbers
def parse_gate(text: str) -> dict:
    """The motion gate's rows and RESULT line -> {rows, fails, warns, m25, result, verdict}."""
    rows: list[dict] = []
    result = ""
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if m:
            rows.append({"level": m.group(1).strip(), "id": m.group(2), "text": m.group(3).strip()})
        elif line.startswith("RESULT:"):
            result = line.strip()
    fails = [r for r in rows if r["level"] == "FAIL"]
    warns = [r for r in rows if r["level"] == "WARN"]
    m25 = next((r for r in rows if r["id"] == "M25"), None)
    return {"rows": rows, "fails": fails, "warns": warns, "m25": m25, "result": result,
            "verdict": "FAIL" if fails else ("WARN" if warns else ("PASS" if rows else "absent"))}


def run_gate(build: Path) -> dict:
    r = subprocess.run([sys.executable, str(GATE), str(build)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return parse_gate((r.stdout or "") + "\n" + (r.stderr or ""))


def verdict_line(path: Path) -> str:
    """The LAST verdict line of a report (`VERDICT: PASS`, `**Verdict** ...`), `absent` when there is no file."""
    if not path.is_file():
        return "absent"
    lines = [l.strip() for l in path.read_text(encoding="utf-8", errors="replace").splitlines()]
    for l in reversed(lines):
        if re.match(r"^\W*verdict\b", l, re.I):
            return re.sub(r"\*+", "", l).strip("# ").strip()
    return "present, no verdict line"


def level_of(line: str) -> str:
    u = line.upper()
    if line == "absent":
        return "absent"
    for lv in ("FAIL", "WARN", "PASS"):
        if lv in u:
            return lv
    return "INFO"


def trim(s: str, w: int = DETAIL_W) -> str:
    s = " ".join(s.split())
    return s if len(s) <= w else s[:w - 1] + "…"


def cell(s: str) -> str:
    return s.replace("|", "\\|")


# ---------------------------------------------------------------- the sheets
def opening_instants(runtime_s: float, fmt: str, step: float) -> list[float]:
    end = min(OPENING_S[fmt], runtime_s)
    return [round(i * step, 2) for i in range(int(end / step + 1e-9))]


def opening_sheets(p: P.Probe, out_dir: Path, ts: list[float], tile: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("opening*.png"):
        old.unlink()
    return P.contact_sheet([(t, p.png(t)) for t in ts], out_dir / "opening.png", tile, PER_SHEET)


# ---------------------------------------------------------------- the report
def section1(gate: dict, lint_lines: list[str], lint_counts: dict, viewer: str, sgates: str, fmt: str) -> list[tuple[str, str, str]]:
    """(row, verdict, detail) - every verdict filled by a tool."""
    g_detail = "; ".join(f"[{r['level']}] {r['id']} {trim(r['text'], 200)}" for r in gate["fails"] + gate["warns"]) or "no FAIL, no WARN"
    rows = [("motion gate (M01-M24)", gate["verdict"], trim(g_detail + " · " + gate["result"], 900))]
    m25 = gate["m25"]
    rows.append(("M25 layout", m25["level"] if m25 else "absent", trim(m25["text"], 600) if m25 else "the gate printed no M25 row"))
    no_row = [l for l in lint_lines if l.endswith("· no row")]
    counts = (f"{lint_counts['sentences']} sentences · {lint_counts['with_act']} carry an act · {lint_counts['with_row']} have a row firing"
              f" · {lint_counts['no_row']} have an available species and no row")
    rows.append(("species by sentence", "INFO", trim(counts + (" · " + " ‖ ".join(trim(l[5:], 160) for l in no_row) if no_row else ""), 1400)))
    if fmt == "long":
        warns = [l for l in lint_lines if l.startswith("WARN")]
        rows.append(("E61 plates (long)", "WARN" if warns else "PASS",
                     trim(" ‖ ".join(trim(l[5:], 160) for l in warns) if warns else f"{lint_counts.get('plates', 0)} plate row(s), every one names its use", 900)))
    else:
        rows.append(("E61 plates (long only)", "n/a", "a short"))
    rows.append(("the viewer (P36)", level_of(viewer), trim(viewer)))
    rows.append(("the script gates", level_of(sgates), trim(sgates)))
    return rows


def verdict(rows: list[tuple[str, str, str]]) -> str:
    bad = next(((name, detail) for name, lv, detail in rows if lv == "FAIL"), None)
    if bad:
        return f"NOT CLEAN - {bad[0]}: {trim(bad[1], 240)}"
    return "TODO - the agent reads the sheets and fills O1-O10; CLEAN is written after the read"


def render(build: Path, project: Path, stem: str, fmt: str, sha: str, tl_name: str, runtime_s: float, aspect: str,
           rows: list[tuple[str, str, str]], sheets: list[Path], ts: list[float], date: str) -> str:
    m, s = divmod(int(round(runtime_s)), 60)
    out = [f"# SELF-WATCH - {project.name} - {build.name} - {date} - {fmt} ({OPENING_S[fmt] / 60:g} min opening)",
           f"player.html sha256 {sha} - timeline {tl_name} - runtime {m}:{s:02d} - aspect {aspect} - script {stem}",
           "",
           "## 1. The gates (mechanical - a FAIL here ends the report)",
           "",
           "| row | verdict | detail |", "|---|---|---|"]
    out += [f"| {cell(n)} | {lv} | {cell(d)} |" for n, lv, d in rows]
    names = ", ".join(p.name for p in sheets)
    out += ["",
            "## 2. The opening, read (the agent fills these by reading the sheets - never by the gates alone)",
            "",
            f"sheets: {SHEET_DIR}/ {names} ({len(ts)} tiles at {STEP_S:g} s steps from 0:00 to {int(ts[-1] // 60)}:{int(ts[-1] % 60):02d}, {TILE_PX} px, {PER_SHEET} per sheet)",
            "",
            "| # | check | verdict | evidence (t, what the tile shows) |", "|---|---|---|---|"]
    out += [f"| {k} | {cell(text)} | TODO | {cell(names)} |" for k, text in O_ROWS]
    out += ["", "## 3. Verdict", "", verdict(rows), ""]
    return "\n".join(out)


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("build", type=Path)
    ap.add_argument("--project", type=Path, required=True, help="the episode dir (SHOT-TABLE-SHORT.py, the script reports)")
    ap.add_argument("--script", required=True, help="the script report stem: <stem>-VIEWER.md and <stem>-GATES.md in the project dir")
    ap.add_argument("--long", action="store_true")
    ap.add_argument("--short", action="store_true")
    ap.add_argument("--step", type=float, default=STEP_S)
    ap.add_argument("--tile", type=int, default=TILE_PX)
    ap.add_argument("--timeline", default=None, help="the compiled timeline's file name inside the build")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    build, project = args.build.resolve(), args.project.resolve()
    words = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    runtime_s = float(words.get("runtime_s") or 0.0)
    fmt = "long" if args.long else ("short" if args.short or runtime_s < LONG_FORM_S else "long")
    ts = opening_instants(runtime_s, fmt, args.step)
    with P.Probe(build, args.timeline) as p:
        P.write_gate(build, args.timeline, probe=p)                       # M25's input, keyed to this player
        sheets = opening_sheets(p, build / SHEET_DIR, ts, args.tile)
        sha, tl_name, aspect = hashlib.sha256(p.html.read_bytes()).hexdigest()[:12], p.tl_path.name, p.aspect
    gate = run_gate(build)
    lint_lines, lint_counts = L.report(project, build=build.name, long=(fmt == "long"))
    viewer = verdict_line(project / f"{args.script}-VIEWER.md")
    sgates = verdict_line(project / f"{args.script}-GATES.md")
    rows = section1(gate, lint_lines, lint_counts, viewer, sgates, fmt)
    text = render(build, project, args.script, fmt, sha, tl_name, runtime_s, aspect, rows, sheets, ts,
                  _dt.date.today().isoformat())
    (build / REPORT_NAME).write_text(text, encoding="utf-8")
    print(f"{build / REPORT_NAME}")
    for n, lv, d in rows:
        print(f"  {lv:6s} {n}: {trim(d, 160)}")
    print(f"  {verdict(rows)}")
    return 1 if verdict(rows).startswith("NOT CLEAN") else 0


if __name__ == "__main__":
    raise SystemExit(main())

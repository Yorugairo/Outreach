"""Script-gate runner - PIPELINE.md stages 3-4 as ONE command.

Runs, in order, the four checkers CHECK-RESPONSIBILITIES s2 tables:

    lint_script_pattern -> audit_script_doctrine -> gate_opening_structure
    -> enumerate_strength_screens

Each runs IN-PROCESS through its own main(), so the exit status and the
counts are the tool's own (rule R1: a tool's mechanical verdict is final;
this runner cites, it never re-derives). It writes <script>-GATES.md beside
the script with the s5 TOOLS block, every tool's stdout verbatim, and the
canonical hash of the SPOKEN text. The recorders import `check_report` and
refuse a script whose report is missing, stale (hash mismatch) or FAIL -
PRP P34 Human Gate 3: hard refuse; `--force "<reason>"` overrides and the
reason lands in the take manifest.

    python run_script_gates.py <script> [--pivot "<line>"] [--ring <t>]
        [--counterparty <n>] [--timeline <path>] [--opening-s N]

Exit 1 if any tool FAILed (lint failures > 0, audit FAIL > 0, opening gate
FAIL > 0, or a checker crashed), else 0. The screens file only enumerates.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import re
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_script_doctrine as A          # noqa: E402
import beat_tags                            # noqa: E402
import enumerate_strength_screens as S      # noqa: E402
import gate_opening_structure as G          # noqa: E402
import lint_script_pattern as L             # noqa: E402

# CHECK-RESPONSIBILITIES s5: the report lives beside the script, named by the
# same rule enumerate_strength_screens uses for <script>-SCREENS.md.
REPORT_SUFFIX = "-GATES.md"
SCREENS_SUFFIX = "-SCREENS.md"
VO_SUFFIX = "-VO"
# doc 37 s1: delivery marks compile to breaks and are never spoken - the
# recorders' spoken() strips exactly this, so the hash keys the same text.
PAUSE_MARK_RE = re.compile(r"`?\[(?:pre|post)-key\]`?")
HASH_LINE_RE = re.compile(r"^script_hash:\s*([0-9a-f]{64})\s*$", re.M)
VERDICT_PASS_RE = re.compile(r"^VERDICT: PASS\s*$", re.M)
# Each tool's own summary line - the runner parses these, it does not count.
LINT_RESULT_RE = re.compile(r"^RESULT: (?:(clean)|(\d+) failure)", re.M)
AUDIT_RESULT_RE = re.compile(r"^RESULT: (\d+) FAIL, (\d+) WARN", re.M)
GATE_RESULT_RE = re.compile(r"^RESULT: (\d+) FAIL / (\d+) WARN / (\d+) PASS / (\d+) JUDGE", re.M)
GATE_TIMING_RE = re.compile(r"^\s*timing: (measured|estimated)", re.M)   # stats["timing"], as printed
SCREENS_RESULT_RE = re.compile(r"^(\S+): X1=(\d+) deixis=(\d+) junctions=(\d+) anchors=(\d+)", re.M)
CRASH_EXIT = 2
RUNNER_CMD = "python content/video_engine/scripts/run_script_gates.py"


@dataclass(frozen=True)
class ToolResult:
    name: str
    exit: int
    stdout: str
    counts: dict = field(default_factory=dict)   # parsed from the tool's RESULT line
    summary: str = ""                             # the TOOLS-block fragment

    @property
    def failing(self) -> bool:
        return self.exit != 0 or self.counts.get("fail", 0) > 0


# ---- the canonical hash (shared with the recorders) ----------------------

def spoken_text(text: str) -> str:
    """What reaches the voice: no beat tags, no pause marks, one space."""
    t = PAUSE_MARK_RE.sub("", beat_tags.strip_beat_tags(text))
    return re.sub(r"\s+", " ", t).strip()


def script_hash(text: str) -> str:
    return hashlib.sha256(spoken_text(text).encode("utf-8")).hexdigest()


def report_path(script: Path) -> Path:
    return script.with_name(script.stem.replace(VO_SUFFIX, "") + REPORT_SUFFIX)


def screens_path(script: Path) -> Path:
    return script.with_name(script.stem.replace(VO_SUFFIX, "") + SCREENS_SUFFIX)


def check_report(script: Path) -> tuple[str, str]:
    """('ok'|'missing'|'stale'|'fail', report path). Stale = hash mismatch."""
    path = report_path(script)
    if not path.exists():
        return "missing", str(path)
    body = path.read_text(encoding="utf-8")
    m = HASH_LINE_RE.search(body)
    current = script_hash(script.read_text(encoding="utf-8"))
    if not m or m.group(1) != current:
        return "stale", str(path)
    return ("ok" if VERDICT_PASS_RE.search(body) else "fail"), str(path)


# ---- the recorders' gate line ----------------------------------------------

def force_reason(argv: list[str]) -> tuple[bool, str]:
    """`--force "<reason>"`: the reason is the NEXT argv item, never a flag."""
    if "--force" not in argv:
        return False, ""
    i = argv.index("--force")
    nxt = argv[i + 1] if i + 1 < len(argv) else ""
    return True, ("" if nxt.startswith("--") else nxt.strip())


def recording_preflight(script: Path, argv: list[str], fails: list[str]) -> dict | None:
    """Print the recorders' gates line; return take-manifest fields, or None
    to refuse. P34 Human Gate 3: missing / stale / FAIL all refuse, and a
    `--force` without a reason is itself a FAIL."""
    state, path = check_report(script)
    forced, reason = force_reason(argv)
    if state == "ok":
        print(f"  [ok] gates report current, VERDICT: PASS ({Path(path).name})")
        return {"gates_report": path,
                "gates_hash": script_hash(script.read_text(encoding="utf-8"))}
    if not forced:
        print(f"  [FAIL] gates report {state}: {path}")
        print(f"         produce it: {RUNNER_CMD} {script} --ring <token> "
              f"--counterparty <name> [--pivot \"<line>\"] [--timeline <build>/timeline.json]")
        fails.append(f"gates report {state}: {path}")
        return None
    if not reason:
        print("  [FAIL] --force needs a reason (--force \"<reason>\")")
        fails.append("--force needs a reason")
        return None
    print(f"  [FORCED] gates report {state} - reason: {reason}")
    return {"gates_forced": {"state": state, "report": path, "reason": reason}}


# ---- running a checker through its own main() -----------------------------

def _call_main(prog: str, fn, argv: list[str]) -> tuple[int, str]:
    """Run a checker's main() with argv patched and stdout captured verbatim.
    A crash is a failing checker (exit 2) with the traceback in its block."""
    buf = io.StringIO()
    saved = sys.argv
    sys.argv = [prog, *argv]
    try:
        with contextlib.redirect_stdout(buf):
            try:
                code = fn()
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
            except Exception:                      # noqa: BLE001
                buf.write(traceback.format_exc())
                code = CRASH_EXIT
    finally:
        sys.argv = saved
    return int(code or 0), buf.getvalue()


def run_lint(script: Path) -> ToolResult:
    argv = [str(script)]
    code, out = _call_main("lint_script_pattern.py", lambda: L.main(argv), argv)
    m = LINT_RESULT_RE.search(out)
    fails = 0 if (m and m.group(1)) else int(m.group(2)) if m else -1
    return ToolResult("lint_script_pattern.py", code, out, {"fail": fails},
                      f"lint: exit {code}, {_n(fails)} fails")


def run_audit(script: Path, pivot: str | None) -> ToolResult:
    argv = [str(script)] + (["--pivot", pivot] if pivot else [])
    code, out = _call_main("audit_script_doctrine.py", A.main, argv)
    m = AUDIT_RESULT_RE.search(out)
    fails, warns = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
    timing = re.search(r"^\s*timing_source: (measured|estimated)", out, re.M)
    counts = {"fail": fails, "warn": warns,
              "timing": timing.group(1) if timing else "unknown"}
    return ToolResult("audit_script_doctrine.py", code, out, counts,
                      f"audit: exit {code}, {_n(fails)}/{_n(warns)}, timing={counts['timing']}")


def run_opening_gate(script: Path, args: argparse.Namespace) -> ToolResult:
    argv = [str(script)]
    for flag in ("timeline", "counterparty", "ring"):
        if getattr(args, flag):
            argv += [f"--{flag}", str(getattr(args, flag))]
    if args.opening_s is not None:
        argv += ["--opening-s", str(args.opening_s)]
    code, out = _call_main("gate_opening_structure.py", G.main, argv)
    m = GATE_RESULT_RE.search(out)
    f, w, p, j = (int(x) for x in m.groups()) if m else (-1, -1, -1, -1)
    t = GATE_TIMING_RE.search(out)                # the gate's stats["timing"]
    counts = {"fail": f, "warn": w, "pass": p, "judge": j,
              "timing": t.group(1) if t else "unknown"}
    return ToolResult("gate_opening_structure.py", code, out, counts,
                      f"opening gate: exit {code}, {_n(f)}/{_n(w)}/{_n(p)}/{_n(j)}")


def run_screens(script: Path) -> ToolResult:
    argv = [str(script)]
    code, out = _call_main("enumerate_strength_screens.py", S.main, argv)
    m = SCREENS_RESULT_RE.search(out)
    items = sum(int(x) for x in m.groups()[1:]) if m else -1
    name = m.group(1) if m else screens_path(script).name
    # the screens file enumerates only - it never carries a FAIL
    return ToolResult("enumerate_strength_screens.py", code, out,
                      {"fail": 0, "items": items}, f"screens: {name}, {_n(items)} items")


def _n(count: int) -> str:
    return "?" if count < 0 else str(count)


def run_all(script: Path, args: argparse.Namespace) -> list[ToolResult]:
    return [run_lint(script), run_audit(script, args.pivot),
            run_opening_gate(script, args), run_screens(script)]


# ---- the report ---------------------------------------------------------

def tools_block(results: list[ToolResult]) -> str:
    """The s5 TOOLS line, in the contract's exact two-line shape."""
    lint, audit, gate, screens = (r.summary for r in results)
    return (f"TOOLS      {lint} | {audit} |\n"
            f"           {gate} | {screens}")


def verdict_line(results: list[ToolResult]) -> str:
    failing = sum(1 for r in results if r.failing)
    return "VERDICT: PASS" if not failing else f"VERDICT: FAIL ({failing} failing tools)"


def render_report(script: Path, results: list[ToolResult], timing: str,
                  stamp: str | None = None) -> str:
    stamp = stamp or datetime.now(timezone.utc).isoformat(timespec="seconds")
    text = script.read_text(encoding="utf-8")
    out = [f"# SCRIPT GATES - {script.name}", "",
           f"script: {script.name}", f"generated: {stamp}",
           f"script_hash: {script_hash(text)}", f"timing_source: {timing}", "",
           tools_block(results), ""]
    for r in results:
        out += [f"## {r.name}", f"exit {r.exit}", "", "```",
                r.stdout.rstrip("\n"), "```", ""]
    out += [verdict_line(results), ""]
    return "\n".join(out)


def write_report(script: Path, results: list[ToolResult]) -> Path:
    timing = results[2].counts.get("timing", "unknown")   # opening gate's stats["timing"]
    path = report_path(script)
    path.write_text(render_report(script, results, timing), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("--pivot", help="verbatim P4 pivot anchor (audit pin 45-55%%)")
    ap.add_argument("--ring", help="the ring token object, e.g. spike")
    ap.add_argument("--counterparty", help="named counterparty, e.g. Bravos")
    ap.add_argument("--timeline", type=Path, help="build-f/timeline.json (measured word times)")
    ap.add_argument("--opening-s", type=float, default=None)
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not args.script.exists():
        print(f"ERROR: script not found: {args.script}")
        return CRASH_EXIT
    results = run_all(args.script, args)
    path = write_report(args.script, results)
    print(f"=== SCRIPT GATES: {args.script.name} ===")
    print(tools_block(results))
    for r in results:
        print(f"  {r.name}: exit {r.exit}")
    print(f"  report: {path}")
    print(verdict_line(results))
    return 1 if any(r.failing for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())

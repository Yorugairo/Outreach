"""Script-gate runner - PIPELINE.md stages 3-4 as ONE command.

Runs, in order, the four checkers CHECK-RESPONSIBILITIES s2 tables:

    lint_script_pattern -> audit_script_doctrine -> gate_opening_structure
    -> enumerate_strength_screens

Each runs IN-PROCESS through its own main(), so the exit status and counts
remain the tool's own. The runner keeps those raw diagnostics separate from
the complete source-bound review receipt. It writes MECHANICAL, REVIEW
COMPLETENESS and stage-scoped CLEARANCE lines; it never emits an unqualified
PASS. Final recorders accept only current recording clearance and revalidate
its receipt, map, viewer, measured clock and scratch custody before spending.

    python run_script_gates.py <script> [--pivot "<line>"] [--ring <t>]
        [--counterparty <n>] [--timeline <path>] [--opening-s N]
        [--title "<locked title>"] [--thumb "<thumbnail words>"] [--thumb-file <png>]

Diagnostic exits 1 on mechanical failure and may exit 0 while review is
INCOMPLETE. Text-review, prefix-preview and recording exit nonzero unless
CLEAR. The screens file only enumerates.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import re
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_script_doctrine as A          # noqa: E402
import enumerate_strength_screens as S      # noqa: E402
import gate_opening_structure as G          # noqa: E402
import lint_script_pattern as L             # noqa: E402
import script_review as R                    # noqa: E402
import script_review_contract as SRC         # noqa: E402

# CHECK-RESPONSIBILITIES s5: the report lives beside the script, named by the
# same rule enumerate_strength_screens uses for <script>-SCREENS.md.
REPORT_SUFFIX = "-GATES.md"
SCREENS_SUFFIX = "-SCREENS.md"
VO_SUFFIX = "-VO"
# doc 37 s1: delivery marks compile to breaks and are never spoken - the
# recorders' spoken() strips exactly this, so the hash keys the same text.
HASH_LINE_RE = re.compile(r"^script_hash:\s*([0-9a-f]{64})\s*$", re.M)
CLEARANCE_RE = re.compile(r"^CLEARANCE\[([^]]+)\]:\s*(CLEAR|INCOMPLETE|FAIL|EXCEPTION)\s*$", re.M)
MECHANICAL_RE = re.compile(r"^MECHANICAL:\s*(PASS|FAIL)\s*$", re.M)
REVIEW_COMPLETENESS_RE = re.compile(r"^REVIEW COMPLETENESS:\s*(COMPLETE|INCOMPLETE)\s*$", re.M)
REVIEW_RECEIPT_RE = re.compile(r"^review_receipt:\s*(.+?)\s*$", re.M)
NARRATIVE_MAP_RE = re.compile(r"^narrative_map:\s*(.+?)\s*$", re.M)
WORD_TIMELINE_RE = re.compile(r"^word_timeline:\s*(.+?)\s*$", re.M)
SCRATCH_TAKE_RE = re.compile(r"^scratch_take:\s*(.+?)\s*$", re.M)
VIEWER_ARTIFACT_RE = re.compile(r"^viewer_artifact:\s*(.+?)\s*$", re.M)
VIEWER_WINDOWS_RE = re.compile(r"^viewer_windows:\s*(.+?)\s*$", re.M)
VIEWER_REPORTS_RE = re.compile(r"^viewer_reports:\s*(.+?)\s*$", re.M)
SCREENS_ARTIFACT_RE = re.compile(r"^screens_artifact:\s*(.+?)\s*$", re.M)
# Each tool's own summary line - the runner parses these, it does not count.
LINT_RESULT_RE = re.compile(r"^RESULT: (?:(clean)|(\d+) failure)", re.M)
AUDIT_RESULT_RE = re.compile(r"^RESULT: (\d+) FAIL, (\d+) WARN", re.M)
GATE_RESULT_RE = re.compile(r"^RESULT: (\d+) FAIL / (\d+) WARN / (\d+) PASS / (\d+) JUDGE", re.M)
GATE_TIMING_RE = re.compile(r"^\s*timing: (measured|estimated)", re.M)   # stats["timing"], as printed
SCREENS_RESULT_RE = re.compile(r"^(\S+): X1=(\d+) deixis=(\d+) junctions=(\d+) anchors=(\d+)", re.M)
FORM_LINE_RE = re.compile(r"^form:\s*(short|long)\s*$", re.M)
SHORT_MODE_RE = re.compile(r"^\s*mode:\s*short\b", re.M)
SHORT_ROWS_RE = re.compile(r"\b(?:S0[1-8]|J50|J51)\b")
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
        # -1 = the tool's RESULT line did not parse: nothing was measured, so it cannot be a PASS
        return self.exit != 0 or self.counts.get("fail", 0) != 0


# ---- the canonical hash (shared with the recorders) ----------------------

def spoken_text(text: str) -> str:
    """What reaches the voice: no beat tags, no pause marks, one space."""
    return SRC.canonical_spoken(text)


def script_hash(text: str) -> str:
    return SRC.spoken_hash(text)


def report_path(script: Path) -> Path:
    return script.with_name(script.stem.replace(VO_SUFFIX, "") + REPORT_SUFFIX)


def screens_path(script: Path) -> Path:
    return script.with_name(script.stem.replace(VO_SUFFIX, "") + SCREENS_SUFFIX)


def check_report(script: Path, required_stage: str = "recording") -> tuple[str, str]:
    """Return the current stage-scoped report state and path.

    A legacy ``VERDICT: PASS`` is intentionally not accepted.  Recording
    clearance must name the stage and retain live custody of the receipt and
    narrative map that produced it.
    """
    path = report_path(script)
    if not path.exists():
        return "missing", str(path)
    body = path.read_text(encoding="utf-8")
    m = HASH_LINE_RE.search(body)
    current = script_hash(script.read_text(encoding="utf-8"))
    if not m or m.group(1) != current:
        return "stale", str(path)
    clearance = {stage: status for stage, status in CLEARANCE_RE.findall(body)}
    status = clearance.get(required_stage)
    if status != "CLEAR":
        return ("fail" if status == "FAIL" else "incomplete"), str(path)
    receipt_match = REVIEW_RECEIPT_RE.search(body)
    map_match = NARRATIVE_MAP_RE.search(body)
    timeline_match = WORD_TIMELINE_RE.search(body)
    scratch_match = SCRATCH_TAKE_RE.search(body)
    viewer_match = VIEWER_ARTIFACT_RE.search(body)
    viewer_windows_match = VIEWER_WINDOWS_RE.search(body)
    viewer_reports_match = VIEWER_REPORTS_RE.search(body)
    screens_match = SCREENS_ARTIFACT_RE.search(body)
    form = report_form(body)
    if (not receipt_match or not map_match or not timeline_match or not scratch_match or
            not viewer_match or not viewer_windows_match or not viewer_reports_match or not screens_match or
            form not in {"short", "long"}):
        return "incomplete", str(path)
    receipt_path = Path(receipt_match.group(1).strip())
    map_path = Path(map_match.group(1).strip())
    timeline_path = Path(timeline_match.group(1).strip())
    scratch_path = Path(scratch_match.group(1).strip())
    viewer_path_ = Path(viewer_match.group(1).strip())
    viewer_windows_path_ = Path(viewer_windows_match.group(1).strip())
    viewer_reports_path_ = Path(viewer_reports_match.group(1).strip())
    screens_path_ = Path(screens_match.group(1).strip())
    if not all(path.is_file() for path in (receipt_path, map_path, timeline_path, scratch_path,
                                           viewer_path_, viewer_windows_path_, viewer_reports_path_, screens_path_)):
        return "incomplete", str(path)
    review = R.validate_receipt(
        script, receipt_path, narrative_map=map_path,
        requested_stage=required_stage, requested_form=form,
        timeline=timeline_path, scratch_take=scratch_path,
        viewer_artifact=viewer_path_,
        viewer_windows=viewer_windows_path_,
        viewer_reports=viewer_reports_path_,
        screens=screens_path_,
    )
    return ("ok" if review.ok else review.status.lower()), str(path)


def opening_review_required(body: str) -> bool:
    """Long-form opening rows identify this contract; short-form gates stay separate."""
    return bool(re.search(r"\b(?:G37|J13|J14)\b", body))


def report_form(body: str) -> str | None:
    """Read an explicit report form, with a safe legacy short-mode fallback.

    A report without a form is never inferred to be long or short.  The
    legacy ``mode: short`` or short-only S/J rows are accepted only as a
    positive short marker; absence of those markers remains unknown rather
    than silently becoming long.
    """
    match = FORM_LINE_RE.search(body)
    if match:
        return match.group(1)
    if SHORT_MODE_RE.search(body):
        return "short"
    if SHORT_ROWS_RE.search(body):
        return "short"
    if opening_review_required(body):
        return "long"
    return None


def requested_form(argv: list[str]) -> str | None:
    """Return an explicit caller form, or ``None`` when the caller is silent."""
    short = "--short" in argv
    long = "--long" in argv
    if short and long:
        return "conflict"
    if short:
        return "short"
    if long:
        return "long"
    return None


def opening_review_block(script: Path, required: bool) -> list[str]:
    if not required:
        return []
    from opening_review import validate_opening_review
    review = validate_opening_review(script)
    if review.estimated_draft_ready:
        return ["OPENING REVIEW: PASS (human draft review; measured timing still required)",
                f"opening_review: {review.sidecar}"]
    return ["OPENING REVIEW: FAIL (human consequence / useful stay promise)",
            *[f"  {error}" for error in review.errors]]


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
    state, path = check_report(script, "recording")
    forced, reason = force_reason(argv)
    caller_form = requested_form(argv)
    report_body = ""
    report_exists = Path(path).is_file()
    if report_exists:
        report_body = Path(path).read_text(encoding="utf-8")
    stored_form = report_form(report_body) if report_exists else None

    # Preserve the pre-existing force contract: a missing reason fails before
    # any other expensive or human-review check.  A reason still cannot waive
    # a required human review below.
    if forced and not reason:
        print("  [FAIL] --force needs a reason (--force \"<reason>\")")
        fails.append("--force needs a reason")
        return None

    if caller_form == "conflict":
        message = "recording form conflict: --short and --long cannot both be supplied"
        print(f"  [FAIL] {message}")
        fails.append(message)
        return None
    if caller_form and stored_form and caller_form != stored_form:
        message = f"recording form conflict: caller requested {caller_form}, report says {stored_form}"
        print(f"  [FAIL] {message}")
        fails.append(message)
        return None
    if stored_form == "short" and opening_review_required(report_body):
        message = "recording form conflict: short report carries long-form opening rows"
        print(f"  [FAIL] {message}")
        fails.append(message)
        return None

    if state == "ok":
        print(f"  [ok] gates report current, CLEARANCE[recording]: CLEAR ({Path(path).name})")
        return {"gates_report": path,
                "gates_hash": script_hash(script.read_text(encoding="utf-8"))}
    # Missing, stale, incomplete review custody and mechanical failures are not
    # forceable by free text.  A future exception path must validate an actual
    # operator decision, exact occurrence, source hash, scope and expiry; until
    # that signed artifact exists, fail closed before provider work.
    review_complete = bool(REVIEW_COMPLETENESS_RE.search(report_body) and
                           REVIEW_COMPLETENESS_RE.search(report_body).group(1) == "COMPLETE")
    if state == "fail" and review_complete:
        receipt_match = REVIEW_RECEIPT_RE.search(report_body)
        map_match = NARRATIVE_MAP_RE.search(report_body)
        timeline_match = WORD_TIMELINE_RE.search(report_body)
        scratch_match = SCRATCH_TAKE_RE.search(report_body)
        viewer_match = VIEWER_ARTIFACT_RE.search(report_body)
        viewer_windows_match = VIEWER_WINDOWS_RE.search(report_body)
        viewer_reports_match = VIEWER_REPORTS_RE.search(report_body)
        screens_match = SCREENS_ARTIFACT_RE.search(report_body)
        custody_paths = [Path(match.group(1).strip()) for match in
                         (receipt_match, map_match, timeline_match, scratch_match, viewer_match,
                          viewer_windows_match, viewer_reports_match, screens_match) if match]
        if len(custody_paths) != 8 or not all(item.is_file() for item in custody_paths):
            review_complete = False
        else:
            (receipt_path, map_path, timeline_path, scratch_path, viewer_path_,
             viewer_windows_path_, viewer_reports_path_, screens_path_) = custody_paths
            custody = R.validate_receipt(
                script, receipt_path, narrative_map=map_path,
                requested_stage="recording", requested_form=stored_form,
                timeline=timeline_path, scratch_take=scratch_path,
                viewer_artifact=viewer_path_,
                viewer_windows=viewer_windows_path_,
                viewer_reports=viewer_reports_path_,
                screens=screens_path_,
            )
            review_complete = custody.ok
    if state != "fail" or not review_complete:
        print(f"  [FAIL] recording clearance {state}: {path}")
        print(f"         produce it: {RUNNER_CMD} {script} --stage recording --review <receipt.json> "
              "--narrative-map <narrative-map.json> --viewer-artifact <script-VIEWER.md> "
              "[--timeline <word-clock.json> --scratch-take <scratch.mp3>]")
        fails.append(f"recording clearance {state}: {path}")
        return None
    print(f"  [FAIL] mechanical gates failed: {path}")
    if forced:
        print("         --force free text cannot authorize recording; attach a validated scoped operator exception")
    fails.append(f"mechanical gates failed: {path}")
    return None


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


def is_short(args: argparse.Namespace) -> bool:
    """G2 (2026-09-05): --short / --long decide; otherwise a MEASURED clock under the gate's SHORT_MAX_S is a short -
    the same rule the opening gate applies, decided once here so the audit and the gate agree."""
    if getattr(args, "short", None) is not None:
        return bool(args.short)
    if not getattr(args, "timeline", None):
        return False
    try:
        tl = G.load_timeline(Path(args.timeline))
    except Exception:                      # noqa: BLE001 - an unreadable timeline is the gate's finding, not the router's
        return False
    return bool(tl) and float(tl[-1].get("e", 0.0)) < G.SHORT_MAX_S


def run_audit(script: Path, pivot: str | None, short: bool = False) -> ToolResult:
    # --defer-opening: this runner writes the gates report that owns doc 38 beats 1-4 (R1) - the audit runs first, so
    # without the flag a FRESH script had the audit restating beats the gate was about to rule on (red since 2026-09-03)
    argv = [str(script), "--defer-opening"] + (["--pivot", pivot] if pivot else []) + (["--short"] if short else [])
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
    # E24: --title / --thumb / --thumb-file pass straight through to G45 / J12
    for flag in ("timeline", "scenes", "counterparty", "ring", "title", "thumb", "thumb_file"):   # E44: --scenes reaches S02
        if getattr(args, flag):
            argv += [f"--{flag.replace('_', '-')}", str(getattr(args, flag))]
    if args.opening_s is not None:
        argv += ["--opening-s", str(args.opening_s)]
    argv += ["--short" if is_short(args) else "--long"]        # G2: decided once, the audit got the same answer
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
    return [run_lint(script), run_audit(script, args.pivot, is_short(args)),
            run_opening_gate(script, args), run_screens(script)]


# ---- the report ---------------------------------------------------------

def tools_block(results: list[ToolResult]) -> str:
    """The s5 TOOLS line, in the contract's exact two-line shape."""
    lint, audit, gate, screens = (r.summary for r in results)
    return (f"TOOLS      {lint} | {audit} |\n"
            f"           {gate} | {screens}")


def mechanical_line(results: list[ToolResult], viewer_fails: int = 0) -> str:
    failing = sum(1 for r in results if r.failing)
    if not failing and not viewer_fails:
        return "MECHANICAL: PASS"
    parts = ([f"{failing} failing tools"] if failing else []) + ([f"{viewer_fails} viewer"] if viewer_fails else [])
    return f"MECHANICAL: FAIL ({', '.join(parts)})"


def review_result(script: Path, receipt: Path | None, narrative_map: Path | None,
                  stage: str, form: str, timeline: Path | None = None,
                  scratch_take: Path | None = None,
                  viewer_artifact: Path | None = None,
                  screens: Path | None = None,
                  viewer_windows: Path | None = None,
                  viewer_reports: Path | None = None) -> R.ReviewResult | None:
    """Validate one source-bound receipt; absence is explicit incompleteness."""
    if receipt is None or narrative_map is None:
        return None
    return R.validate_receipt(
        script, receipt, narrative_map=narrative_map,
        requested_stage=stage, requested_form=form,
        timeline=timeline, scratch_take=scratch_take,
        viewer_artifact=viewer_artifact,
        viewer_windows=viewer_windows,
        viewer_reports=viewer_reports,
        screens=screens,
    )


def clearance_status(results: list[ToolResult], viewer_fails: int,
                     review: R.ReviewResult | None) -> str:
    if any(result.failing for result in results) or viewer_fails:
        return "FAIL"
    if review is None:
        return "INCOMPLETE"
    return review.status


def review_complete(review: R.ReviewResult | None) -> bool:
    """Completeness is orthogonal to a fully reviewed FAIL/WARN outcome."""
    return bool(review is not None and not review.errors and not review.missing and
                not review.unexpected and not review.stale and not review.deferred)


# Compatibility name for callers that imported the old helper.  It no longer
# emits an unqualified PASS, which is the fail-open condition this PRP removes.
def verdict_line(results: list[ToolResult], viewer_fails: int = 0) -> str:
    return mechanical_line(results, viewer_fails)


VIEWER_SUFFIX = "-VIEWER.md"          # viewer_score.py writes it beside the script (P36)
VIEWER_ROW_RE = re.compile(r"^\s*\[(FAIL |WARN |PASS |INFO )\]\s+(V\d\d)\s+(.*)$", re.M)


def viewer_path(script: Path) -> Path:
    return script.with_name(script.stem.replace(VO_SUFFIX, "") + VIEWER_SUFFIX)


def viewer_windows_path(script: Path) -> Path:
    return script.with_name(script.stem.replace(VO_SUFFIX, "") + "-VIEWER-WINDOWS.json")


def viewer_reports_path(script: Path) -> Path:
    return script.with_name(script.stem.replace(VO_SUFFIX, "") + "-VIEWER-REPORTS.json")


def viewer_rows(script: Path) -> list[tuple[str, str, str]]:
    """(level, id, message) from `<script>-VIEWER.md`, or [] when the viewer never ran.

    The viewer is the THIRD role (gates mechanical, judge doctrinal, viewer blind).
    Its rows are reported but do NOT move the VERDICT until the ep1 calibration
    passes P36 Human Gate 1; `--viewer-gate` is the promotion switch.
    """
    path = viewer_path(script)
    if not path.exists():
        return []
    text = path.read_text(encoding='utf-8')
    return [(m.group(1).strip(), m.group(2), m.group(3).strip()) for m in VIEWER_ROW_RE.finditer(text)]


def viewer_block(script: Path, gating: bool) -> tuple[list[str], int, int]:
    """The VIEWER block for the report and stdout, plus (fails, warns) it would carry.

    Advisory by default: every row is printed at its own level for the reader, but the
    counts returned are zero unless `gating` - so a viewer finding never blocks a
    recording before the operator has promoted the instrument.
    """
    rows = viewer_rows(script)
    if not rows:
        # NOT RUN is legal, and loud (CHECK-RESPONSIBILITIES s5: only with a reason the operator can rule on).
        # It does not block: the viewer costs a live model pass, and the work order - not the runner -
        # decides which scripts must carry one.
        return (["VIEWER     NOT RUN - `viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py` (P36; a re-script"
                 "            names the VIEWER block in its own acceptance)"], 0, 0)
    out = [f"VIEWER     {viewer_path(script).name}"
           + ("" if gating else "  (advisory: --no-viewer-gate - these rows do not change the VERDICT)")]
    for lvl, rid, msg in rows:
        shown = lvl if gating else "INFO"
        out.append(f"  [{shown:5}] {rid} {msg}")
    if not gating:
        return (out, 0, 0)
    return (out, sum(1 for l, _, _ in rows if l == "FAIL"), sum(1 for l, _, _ in rows if l == "WARN"))


def render_report(script: Path, results: list[ToolResult], timing: str,
                  stamp: str | None = None, viewer: list[str] | None = None,
                  viewer_fails: int = 0, form: str | None = None,
                  stage: str = "diagnostic", review: R.ReviewResult | None = None,
                  receipt: Path | None = None, narrative_map: Path | None = None,
                  timeline: Path | None = None, scratch_take: Path | None = None,
                  viewer_artifact: Path | None = None,
                  viewer_windows: Path | None = None,
                  viewer_reports: Path | None = None,
                  screens: Path | None = None) -> str:
    stamp = stamp or datetime.now(timezone.utc).isoformat(timespec="seconds")
    text = script.read_text(encoding="utf-8")
    out = [f"# SCRIPT GATES - {script.name}", "",
           f"script: {script.name}", f"generated: {stamp}",
           f"script_hash: {script_hash(text)}",
           f"annotated_script_hash: {SRC.annotated_hash(text)}",
           f"timing_source: {timing}", f"stage: {stage}"]
    if form in {"short", "long"}:
        out.append(f"form: {form}")
    out += ["",
           tools_block(results), ""]
    if viewer:
        out += viewer + [""]
    out += opening_review_block(script, any(opening_review_required(r.stdout) for r in results))
    out += [""]
    if receipt is not None:
        out.append(f"review_receipt: {receipt.resolve()}")
    if narrative_map is not None:
        out.append(f"narrative_map: {narrative_map.resolve()}")
    if timeline is not None:
        out.append(f"word_timeline: {timeline.resolve()}")
    if scratch_take is not None:
        out.append(f"scratch_take: {scratch_take.resolve()}")
    if viewer_artifact is not None:
        out.append(f"viewer_artifact: {viewer_artifact.resolve()}")
    if viewer_windows is not None:
        out.append(f"viewer_windows: {viewer_windows.resolve()}")
    if viewer_reports is not None:
        out.append(f"viewer_reports: {viewer_reports.resolve()}")
    if screens is not None:
        out.append(f"screens_artifact: {screens.resolve()}")
    if receipt is not None or narrative_map is not None:
        out.append("")
    if review is None:
        out += ["## Complete review", "", "NOT RUN - supply both --review and --narrative-map.", ""]
    else:
        out += ["## Complete review", "", f"status: {review.status}"]
        out += [f"  - {error}" for error in review.errors]
        out.append("")
    for r in results:
        out += [f"## {r.name}", f"exit {r.exit}", "", "```",
                r.stdout.rstrip("\n"), "```", ""]
    status = clearance_status(results, viewer_fails, review)
    out += [mechanical_line(results, viewer_fails),
            f"REVIEW COMPLETENESS: {'COMPLETE' if review_complete(review) else 'INCOMPLETE'}",
            f"CLEARANCE[{stage}]: {status}", ""]
    return "\n".join(out)


def write_report(script: Path, results: list[ToolResult],
                 viewer: list[str] | None = None, viewer_fails: int = 0,
                 form: str | None = None, stage: str = "diagnostic",
                 review: R.ReviewResult | None = None, receipt: Path | None = None,
                 narrative_map: Path | None = None, timeline: Path | None = None,
                 scratch_take: Path | None = None,
                 viewer_artifact: Path | None = None,
                 viewer_windows: Path | None = None,
                 viewer_reports: Path | None = None,
                 screens: Path | None = None) -> Path:
    timing = results[2].counts.get("timing", "unknown")   # opening gate's stats["timing"]
    path = report_path(script)
    path.write_text(render_report(script, results, timing, viewer=viewer,
                                  viewer_fails=viewer_fails, form=form, stage=stage,
                                  review=review, receipt=receipt,
                                  narrative_map=narrative_map, timeline=timeline,
                                  scratch_take=scratch_take,
                                  viewer_artifact=viewer_artifact,
                                  viewer_windows=viewer_windows,
                                  viewer_reports=viewer_reports,
                                  screens=screens), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("--pivot", help="verbatim P4 pivot anchor (audit pin 45-55%%)")
    ap.add_argument("--ring", help="the ring token object, e.g. spike")
    ap.add_argument("--counterparty", help="named counterparty, e.g. Bravos")
    ap.add_argument("--timeline", type=Path, help="build-f/timeline.json (measured word times)")
    ap.add_argument("--scenes", type=Path, default=None,
                    help="the build's scene timeline (<build>/<slug>.timeline.json) for the opening gate's S02 (E44: the first ledger page carries the mechanism); default: found beside --timeline")
    ap.add_argument("--opening-s", type=float, default=None)
    ap.add_argument("--title", help="the locked title - opening gate G45 packaging echo (E24)")
    ap.add_argument("--thumb", help="the thumbnail's words, when recorded in text (E24 G45)")
    ap.add_argument("--thumb-file", help="the FINAL thumbnail path the opening gate's J12 prints (E24)")
    ap.add_argument("--stage", choices=SRC.STAGES, default="diagnostic",
                    help="clearance stage (default diagnostic; recording requires a complete receipt)")
    ap.add_argument("--review", type=Path,
                    help="script_review.v1 JSON receipt bound to this script and stage")
    ap.add_argument("--narrative-map", type=Path,
                    help="narrative_map.v1 JSON used by the review receipt")
    ap.add_argument("--scratch-take", type=Path,
                    help="aligned scratch audio bound by a recording-stage receipt")
    ap.add_argument("--viewer-artifact", type=Path,
                    help="complete source-bound <script>-VIEWER.md used by the receipt")
    ap.add_argument("--short", dest="short", action="store_true", default=None,
                    help="G2: judge by the shorts shape (doc 51 s51.2) - S01-S08 + J50/J51; default: a measured clock under 3:00")
    ap.add_argument("--long", dest="short", action="store_false", help="force the long-form geometry")
    # P36 Human Gate 1 GRANTED (operator, 2026-09-03, on the ep1 calibration): the viewer binds.
    # V01 beat recall is a FAIL, V04 confusion a WARN; V05 information gain stays INFO with no
    # authority because it read GREEN on the episode whose retention curve we hold.
    ap.add_argument("--no-viewer-gate", dest="viewer_gate", action="store_false", default=True,
                    help="report the VIEWER rows without binding them to the VERDICT (they bind by default since P36 HG1)")
    ap.add_argument("--viewer-gate", dest="viewer_gate", action="store_true",
                    help=argparse.SUPPRESS)   # accepted and redundant: gating is the default
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not args.script.exists():
        print(f"ERROR: script not found: {args.script}")
        return CRASH_EXIT
    if args.stage == "prefix-preview" and args.short is None:
        # A timed excerpt of a long episode is still the long-form contract.
        # Actual shorts must opt in explicitly with --short.
        args.short = False
    form = "short" if is_short(args) else "long"
    results = run_all(args.script, args)
    vblock, vfail, _vwarn = viewer_block(args.script, args.viewer_gate)
    review = review_result(args.script, args.review, args.narrative_map, args.stage, form,
                           args.timeline, args.scratch_take, args.viewer_artifact,
                           screens_path(args.script), viewer_windows_path(args.script),
                           viewer_reports_path(args.script))
    path = write_report(args.script, results, vblock, vfail, form=form, stage=args.stage,
                        review=review, receipt=args.review, narrative_map=args.narrative_map,
                        timeline=args.timeline, scratch_take=args.scratch_take,
                        viewer_artifact=args.viewer_artifact,
                        viewer_windows=viewer_windows_path(args.script),
                        viewer_reports=viewer_reports_path(args.script),
                        screens=screens_path(args.script))
    print(f"=== SCRIPT GATES: {args.script.name} ===")
    print(tools_block(results))
    for line in vblock:
        print(line)
    for r in results:
        print(f"  {r.name}: exit {r.exit}")
    print(f"  report: {path}")
    status = clearance_status(results, vfail, review)
    print(mechanical_line(results, vfail))
    print(f"REVIEW COMPLETENESS: {'COMPLETE' if review_complete(review) else 'INCOMPLETE'}")
    print(f"CLEARANCE[{args.stage}]: {status}")
    mechanical_failed = any(r.failing for r in results) or bool(vfail)
    if mechanical_failed:
        return 1
    if args.stage in {"text-review", "prefix-preview", "recording"} and status != "CLEAR":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""run_full_suite.py - the whole video-engine suite, every test file in its own process, one after another.

    python content/video_engine/scripts/run_full_suite.py [--skip-goldens] [--out DIR] [--timeout S]

What it runs: every `content/video_engine/tests/test_*.py` (`python -m pytest`, one process per file) and every
`content/video_engine/tests/kinetics/*.test.mjs` (`node --test`, one process per file). It walks only those two
globs - nothing else in the tree - and it runs IN the checkout it lives in (or `--repo`), so the gitignored inputs
that checkout carries are all present: there is no export (P72 T51: a scratch export lost about a dozen of them,
and 31 files failed on environment, not on code).

A failing file is rerun alone once. Failing again is a FAILURE; passing is a FLAKE, reported apart and not counted
as a failure. `--skip-goldens` leaves out `test_golden_frames.py` (the slowest file, and pinned by its own recipe).

It writes `<out>/logs/<file>.log` per file, `<out>/rerun/<file>.log` per rerun, `<out>/SUMMARY.md` (files run /
passed / failed / flaked, and each failing test id with its assertion's first line) and `<out>/summary.json`.
The default `<out>` is `content/video_engine/runtime/suite/<UTC stamp>/` (gitignored). Exit 1 on a real failure.

It never kills a process it did not start. A file over `--timeout` has its OWN child ended: `taskkill /PID <the pid
it launched> /T /F` on Windows (that child and the processes it spawned), the process group it created on POSIX.
Nothing is killed by name or by command line - other agents' runs share this machine (P72 T22, P71 T18).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TESTS_REL = "content/video_engine/tests"
PY_GLOB = "test_*.py"
NODE_GLOB = "kinetics/*.test.mjs"
GOLDENS = "test_golden_frames.py"
OUT_REL = "content/video_engine/runtime/suite"
TIMEOUT_S = 1800            # the sweep's per-file ceiling (2026-09-26): the slowest file took ~10 min
MESSAGE_MAX = 300           # a failure's first line, as SUMMARY.md prints it
PYTEST_COLUMNS = "4000"     # pytest cuts its short-summary line to the terminal width; a child has no terminal

PYTEST_SUMMARY = re.compile(r"^(FAILED|ERROR) (.+?)(?: - (.*))?$")
TAP_SUBTEST = re.compile(r"^(\s*)# Subtest: (.*)$")
TAP_NOT_OK = re.compile(r"^(\s*)not ok \d+ - (.*)$")
TAP_KEY = re.compile(r"^\s*(error|failureType): ?(.*)$")
BLOCK_SCALAR = ("|", "|-", "|+", ">", ">-", ">+")


@dataclass
class Attempt:
    log: str
    rc: int | None
    seconds: float
    pid: int
    timed_out: bool = False
    failures: list[list[str]] = field(default_factory=list)   # [test id, the assertion's first line]


@dataclass
class FileResult:
    path: str
    kind: str                   # "pytest" | "node"
    status: str = "pass"        # "pass" | "fail" | "flake"
    runs: list[Attempt] = field(default_factory=list)


# --- what runs ----------------------------------------------------------------------------------------------

def discover(repo: Path, skip_goldens: bool = False) -> list[str]:
    """Repo-relative test files: the pytest files, then the node files, each sorted. Only the two globs."""
    tests = repo / TESTS_REL
    py = sorted(p for p in tests.glob(PY_GLOB) if p.is_file() and not (skip_goldens and p.name == GOLDENS))
    node = sorted(p for p in tests.glob(NODE_GLOB) if p.is_file())
    return [p.relative_to(repo).as_posix() for p in py + node]


def kind_of(rel: str) -> str:
    return "node" if rel.endswith(".mjs") else "pytest"


def command(rel: str, python: str, node: str) -> list[str]:
    if kind_of(rel) == "node":
        return [node, "--test", "--test-reporter=tap", rel]
    return [python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rfE", rel]


# --- one process per file -----------------------------------------------------------------------------------

def end_own_child(proc: subprocess.Popen) -> None:
    """End the child THIS runner launched, with the processes it spawned - never anything else."""
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)   # the group start_new_session made: pgid == this child's pid
        except ProcessLookupError:                # it ended between the poll and the kill
            pass
    proc.wait()


def run_file(repo: Path, rel: str, log: Path, timeout: float, python: str, node: str) -> Attempt:
    """Run one file in its own process, its output straight into its own log (unpiped, nothing buffered)."""
    log.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", COLUMNS=PYTEST_COLUMNS)
    spawn = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
             else {"start_new_session": True})
    start = time.monotonic()
    with log.open("wb") as out:
        proc = subprocess.Popen(command(rel, python, node), cwd=repo, env=env, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=subprocess.STDOUT, **spawn)
        timed_out = False
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            end_own_child(proc)
        except BaseException:           # Ctrl+C or a crash here: our child does not outlive us
            end_own_child(proc)
            raise
    seconds = round(time.monotonic() - start, 1)
    if timed_out:
        with log.open("a", encoding="utf-8") as out:
            out.write(f"\nrun_full_suite: TIMEOUT after {timeout:g} s - this file's own process was ended\n")
    return Attempt(log=log.as_posix(), rc=None if timed_out else proc.returncode, seconds=seconds,
                   pid=proc.pid, timed_out=timed_out)


# --- what failed --------------------------------------------------------------------------------------------

def pytest_failures(text: str) -> list[list[str]]:
    """[id, first line] from pytest's `-rfE` short summary: `FAILED <id> - <the assertion's first line>`."""
    out = []
    for line in text.splitlines():
        m = PYTEST_SUMMARY.match(line.rstrip())
        if m:
            out.append([m.group(2), (m.group(3) or m.group(1)).strip()[:MESSAGE_MAX]])
    return out


def tap_failures(text: str) -> list[list[str]]:
    """[id, first line] per failing node test: the subtest path joined by ' > ', its `error:` first line.
    A suite that failed only because a subtest did (`failureType: 'subtestsFailed'`) is not repeated."""
    lines, names, out = text.splitlines(), {}, []
    for i, line in enumerate(lines):
        sub = TAP_SUBTEST.match(line)
        if sub:
            depth = len(sub.group(1)) // 4
            names = {d: n for d, n in names.items() if d < depth} | {depth: sub.group(2).strip()}
            continue
        bad = TAP_NOT_OK.match(line)
        if not bad:
            continue
        depth = len(bad.group(1)) // 4
        kind, message = _tap_block(lines, i + 1)
        if kind == "subtestsFailed":
            continue
        path = [names[d] for d in sorted(names) if d < depth] + [bad.group(2).strip()]
        out.append([" > ".join(path), message[:MESSAGE_MAX]])
    return out


def _tap_block(lines: list[str], start: int) -> tuple[str, str]:
    """(failureType, the error's first line) from the YAML block that follows a `not ok` line."""
    kind, message = "", ""
    for j in range(start, len(lines)):
        stripped = lines[j].strip()
        if stripped == "...":
            break
        m = TAP_KEY.match(lines[j])
        if not m:
            continue
        value = m.group(2).strip()
        if m.group(1) == "failureType":
            kind = value.strip("'\"")
        elif value in BLOCK_SCALAR:
            message = next((ln.strip() for ln in lines[j + 1:] if ln.strip()), "")
        else:
            message = value.strip("'\"")
    return kind, message


def failures_of(attempt: Attempt, kind: str) -> list[list[str]]:
    """What failed in one attempt; a nonzero exit with nothing parsed is reported by its last line."""
    text = Path(attempt.log).read_text(encoding="utf-8", errors="replace")
    found = tap_failures(text) if kind == "node" else pytest_failures(text)
    if attempt.timed_out:
        return found + [["(timeout)", f"no result within the timeout ({attempt.seconds} s)"]]
    if attempt.rc not in (0, None) and not found:
        tail = next((ln.strip() for ln in reversed(text.splitlines()) if ln.strip()), "(no output)")
        return [[f"(exit {attempt.rc})", tail[:MESSAGE_MAX]]]
    return found


def passed(attempt: Attempt) -> bool:
    return attempt.rc == 0 and not attempt.timed_out


# --- the run ------------------------------------------------------------------------------------------------

def run_suite(repo: Path, out: Path, files: list[str], timeout: float, python: str, node: str,
              rerun: bool = True) -> list[FileResult]:
    results = []
    for n, rel in enumerate(files, 1):
        result = FileResult(path=rel, kind=kind_of(rel))
        name = Path(rel).name + ".log"
        first = run_file(repo, rel, out / "logs" / name, timeout, python, node)
        first.failures = failures_of(first, result.kind)
        result.runs.append(first)
        if not passed(first):
            result.status = "fail"
            if rerun:
                again = run_file(repo, rel, out / "rerun" / name, timeout, python, node)
                again.failures = failures_of(again, result.kind)
                result.runs.append(again)
                result.status = "flake" if passed(again) else "fail"
        print(f"[{n}/{len(files)}] {result.status.upper():5} {first.seconds:7.1f}s {rel}", flush=True)
        results.append(result)
    return results


def head_of(repo: Path) -> str:
    got = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    return got.stdout.strip() or "n/a (not a git checkout)"


def summary_md(results: list[FileResult], meta: dict) -> str:
    fails = [r for r in results if r.status == "fail"]
    flakes = [r for r in results if r.status == "flake"]
    lines = ["# Full suite - SUMMARY", "",
             f"- repo: `{meta['repo']}` at `{meta['head']}`", f"- started: {meta['started']}  seconds: {meta['seconds']}",
             f"- command: `{meta['argv']}`", "",
             f"files run {len(results)} / passed {len(results) - len(fails) - len(flakes)} / "
             f"failed {len(fails)} / flaked {len(flakes)}", ""]
    for title, group in (("Failed (failed again when rerun alone)", fails), ("Flaked (passed when rerun alone)", flakes)):
        lines += [f"## {title}", ""] + (["- none"] if not group else [])
        for r in group:
            last = r.runs[-1] if r.status == "fail" else r.runs[0]
            lines.append(f"- `{r.path}` (exit {last.rc}, log `{last.log}`)")
            lines += [f"  - `{test}` - {message}" for test, message in last.failures]
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", type=Path, default=REPO, help="the checkout to run in (default: this script's own)")
    ap.add_argument("--out", type=Path, help=f"where logs and SUMMARY go (default: <repo>/{OUT_REL}/<UTC stamp>)")
    ap.add_argument("--skip-goldens", action="store_true", help=f"leave out {GOLDENS}")
    ap.add_argument("--timeout", type=float, default=TIMEOUT_S, help="seconds per file before its process is ended")
    ap.add_argument("--no-rerun", action="store_true", help="do not rerun a failing file alone")
    ap.add_argument("--python", default=sys.executable, help="the interpreter for pytest (default: this one)")
    ap.add_argument("--node", default="node", help="the node executable")
    args = ap.parse_args(argv)
    repo = args.repo.resolve()
    if not (repo / TESTS_REL).is_dir():
        ap.error(f"no {TESTS_REL} under {repo}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = (args.out or repo / OUT_REL / stamp).resolve()
    files = discover(repo, args.skip_goldens)
    print(f"run_full_suite: {len(files)} files in {repo} -> {out}", flush=True)
    start = time.monotonic()
    results = run_suite(repo, out, files, args.timeout, args.python, args.node, rerun=not args.no_rerun)
    meta = {"repo": repo.as_posix(), "head": head_of(repo), "started": stamp,
            "seconds": round(time.monotonic() - start, 1),
            "argv": " ".join(["run_full_suite.py", *(sys.argv[1:] if argv is None else argv)])}
    counts = {s: sum(1 for r in results if r.status == s) for s in ("pass", "fail", "flake")}
    out.mkdir(parents=True, exist_ok=True)
    (out / "SUMMARY.md").write_text(summary_md(results, meta) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(
        dict(meta, run=len(results), **counts, files=[asdict(r) for r in results]), indent=1) + "\n",
        encoding="utf-8")
    print(f"run_full_suite: files run {len(results)} / passed {counts['pass']} / failed {counts['fail']} / "
          f"flaked {counts['flake']} - {out / 'SUMMARY.md'}", flush=True)
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())

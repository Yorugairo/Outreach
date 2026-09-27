"""run_full_suite.py - the whole video-engine suite, every test file in its own process, one after another.

    python content/video_engine/scripts/run_full_suite.py [--skip-goldens] [--out DIR] [--timeout S]
                                                          [--inputs-from CHECKOUT | --no-stage] [--path-limit N]

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

THE INPUTS (P72 T52, R26-405). A lane worktree lacks the gitignored inputs the main checkout holds (audio masters,
cutouts, side builds, review claims, the Blender profile): 25 of the 30 failures at d1099fc lacked one, and 19 of
them needed nothing else. `run_full_suite.inputs.json` declares, per test file, the gitignored paths it reads
(`inputs`: a file, or a directory ending in `/` - every file git ignores under it in the source).
Before the run each absent one is STAGED from `--inputs-from` (default: the main checkout of this repo, read-only):
copied only when git IGNORES it in the target (`git check-ignore`, fed bytes), never over an existing file, and
listed in SUMMARY.md and `<out>/staged-inputs.txt`. A file whose input is absent here and in the source, or present
there but not ignored here, is SKIPPED with the reason - a SKIP, never a pass. `--no-stage` stages nothing.

THE PATH LIMIT. Blender 5.2 opens assets by absolute path and is not long-path aware: from a 68-character lane root
the generalization scene's 194-character asset path is 262 characters and the compile worker exits 17 (T52 measured:
an 81-character root fails, a 40-character root passes). A junction or a `subst` drive does not help - every modeling
test and `scene.py` take their root from `Path(__file__).resolve()`, which follows both back to the real root
(measured, all three fail). So a file's declared `path_limit` directories are measured from this checkout, and a
read past `--path-limit` (259, MAX_PATH less its NUL) skips the file with the length and the root it needs.

THE GENERATED LAYERS (P72 T52b, R26-411 (e)). Some inputs are not copied, they are BUILT: the manifest's `generated`
names gitignored outputs - the first output of each of the twelve docs layers, `docs/EFFECTS-CATALOG.jsonl` among
them - and the builder that writes each; a checkout that lacks one runs its builder once, from the checkout root with
`--repo <checkout>` appended, after the staging and before the first test file - never over one already here. Each
is built through the layer table (`build_docs_layers.py --ensure --only <layer>`: upstream first, the digests
stamped, so no reader starts a background refresh mid-run); the catalogue's builder alone, with no docs index,
resolves 93 of 819 cites. A builder that fails is reported with its exit and last line in SUMMARY.md; the run goes
on and the readers fail on their own.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[3]
TESTS_REL = "content/video_engine/tests"
PY_GLOB = "test_*.py"
NODE_GLOB = "kinetics/*.test.mjs"
GOLDENS = "test_golden_frames.py"
OUT_REL = "content/video_engine/runtime/suite"
TIMEOUT_S = 1800            # the sweep's per-file ceiling (2026-09-26): the slowest file took ~10 min
MESSAGE_MAX = 300           # a failure's first line, as SUMMARY.md prints it
PYTEST_COLUMNS = "4000"     # pytest cuts its short-summary line to the terminal width; a child has no terminal
INPUTS_REL = "content/video_engine/scripts/run_full_suite.inputs.json"
INPUTS_SCHEMA = "run_full_suite.inputs.v1"
PATH_LIMIT = 259            # MAX_PATH (260) less its NUL - Blender 5.2 is not long-path aware (T52: 262 fails)
NAMES_MAX = 8               # a skip reason names this many paths, then counts the rest
STAGED_LISTED = 60          # SUMMARY.md lists this many staged paths; staged-inputs.txt has them all

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
    status: str = "pass"        # "pass" | "fail" | "flake" | "skip"
    runs: list[Attempt] = field(default_factory=list)
    reason: str = ""            # why a "skip" never ran


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


# --- the inputs: staged from the source checkout, or the file skipped with the reason ---------------------------

@dataclass
class Staging:
    source: str | None                                      # the checkout inputs were staged from, or None
    staged: list[str] = field(default_factory=list)         # repo-relative, sorted
    skips: dict[str, str] = field(default_factory=dict)     # test file -> why it does not run


def _inside(rel: str) -> bool:
    """A declared path is repo-relative, POSIX, and never leaves the checkout."""
    parts = PurePosixPath(rel).parts
    return bool(rel) and not rel.startswith("/") and ":" not in rel and "\\" not in rel and ".." not in parts


def _manifest(repo: Path) -> dict:
    """`run_full_suite.inputs.json`, schema-checked; {} when the checkout has none."""
    path = repo / INPUTS_REL
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema") != INPUTS_SCHEMA:
        raise ValueError(f"{INPUTS_REL}: schema is {doc.get('schema')!r}, not {INPUTS_SCHEMA!r}")
    return doc


def load_needs(repo: Path) -> dict[str, dict]:
    """`run_full_suite.inputs.json`'s `files`: test file -> {"inputs": [...], "path_limit": [...], "why": ...}."""
    files = _manifest(repo).get("files") or {}
    for test, need in files.items():
        for rel in [*need.get("inputs", []), *need.get("path_limit", [])]:
            if not _inside(rel):
                raise ValueError(f"{INPUTS_REL}: {test}: {rel!r} - a declared path stays inside the checkout "
                                 "(repo-relative, forward slashes, no '..', no drive)")
    return files


def load_generated(repo: Path) -> dict[str, dict]:
    """The manifest's `generated`: output path -> {"build": [script, *args], "why": ...}, both inside the checkout."""
    generated = _manifest(repo).get("generated") or {}
    for rel, spec in generated.items():
        build = spec.get("build") if isinstance(spec, dict) else None
        if not _inside(rel) or not isinstance(build, list) or not build or not _inside(str(build[0])):
            raise ValueError(f"{INPUTS_REL}: generated {rel!r}: the output and its builder script ({build!r}) stay "
                             "inside the checkout (repo-relative, forward slashes, no '..', no drive)")
    return generated


def main_checkout(repo: Path) -> Path | None:
    """The main checkout of `repo`'s repository (the worktree that owns the common .git), or None."""
    got = subprocess.run(["git", "-C", str(repo), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                         capture_output=True, text=True, check=False)
    if got.returncode != 0 or not got.stdout.strip():
        return None
    common = Path(got.stdout.strip())
    return common.parent.resolve() if common.name == ".git" else None


def _listed(checkout: Path, rel_dir: str) -> list[str]:
    """The files git ignores under `rel_dir` in `checkout` (read-only: `git ls-files` walks that directory only)."""
    if not (checkout / rel_dir).is_dir():
        return []
    got = subprocess.run(["git", "-C", str(checkout), "ls-files", "-z", "--others", "--ignored", "--exclude-standard",
                          "--", rel_dir], capture_output=True, check=False)
    return sorted(n.decode("utf-8") for n in got.stdout.split(b"\0") if n) if got.returncode == 0 else []


def ignored_in(repo: Path, rels: list[str]) -> set[str]:
    """The subset of `rels` git ignores in `repo`. Fed as BYTES, NUL-separated: a text-mode pipe on Windows sends
    `\\r\\n`, and `x.png\\r` never matches `*.png`. A tracked path is never reported (check-ignore skips the index)."""
    if not rels:
        return set()
    got = subprocess.run(["git", "-C", str(repo), "check-ignore", "--stdin", "-z"],
                         input=b"\0".join(r.encode("utf-8") for r in rels) + b"\0", capture_output=True, check=False)
    if got.returncode not in (0, 1):
        raise RuntimeError(f"git check-ignore failed in {repo}: {got.stderr.decode('utf-8', 'replace').strip()}")
    return {n.decode("utf-8") for n in got.stdout.split(b"\0") if n}


def _make_parents(repo: Path, rels: list[str]) -> list[Path]:
    """Each parent directory made before check-ignore (a directory-only rule like `**/review/` matches a directory
    git can see); returns the ones made, deepest first, so the unused ones are removed again."""
    made: list[Path] = []
    for rel in rels:
        missing = [p for p in (repo / rel).parents if p != repo and repo in p.parents and not p.exists()]
        for directory in reversed(missing):
            directory.mkdir()
            made.append(directory)
    return sorted(made, key=lambda p: len(p.parts), reverse=True)


def _prune(made: list[Path]) -> None:
    for directory in made:
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def _copy_new(src: Path, dst: Path) -> bool:
    """Copy `src` to `dst` only when `dst` does not exist (`xb`: never an overwrite, even in a race)."""
    try:
        with src.open("rb") as reader, dst.open("xb") as writer:
            shutil.copyfileobj(reader, writer)
    except FileExistsError:
        return False
    shutil.copystat(src, dst)
    return True


def _names(rels: list[str]) -> str:
    more = len(rels) - NAMES_MAX
    return ", ".join(rels[:NAMES_MAX]) + (f" (+{more} more)" if more > 0 else "")


def _wanted(repo: Path, source: Path | None, inputs: list[str]) -> tuple[list[str], list[str]]:
    """(the absent files the source can supply, the declared inputs absent here and there)."""
    want, absent = [], []
    for rel in inputs:
        if rel.endswith("/"):
            there = [f for f in _listed(source, rel) if not (repo / f).exists()] if source else []
            if not (repo / rel).is_dir() and not there:
                absent.append(rel)
            want += there
        elif not (repo / rel).exists():
            (want if source and (source / rel).is_file() else absent).append(rel)
    return want, absent


def stage_inputs(repo: Path, source: Path | None, needs: dict[str, dict], files: list[str]) -> Staging:
    """Stage every declared input absent here from `source` (only what git ignores here), then name the files
    that still lack one. `source` is only ever read."""
    per_test = {rel: _wanted(repo, source, needs[rel].get("inputs", [])) for rel in files if rel in needs}
    candidates = sorted({f for want, _ in per_test.values() for f in want})
    made = _make_parents(repo, candidates)
    ok = ignored_in(repo, candidates)
    staged = [rel for rel in candidates if rel in ok and _copy_new(source / rel, repo / rel)]
    _prune(made)
    result = Staging(source=source.as_posix() if source else None, staged=staged)
    for test, (want, absent) in per_test.items():
        refused = [rel for rel in want if rel not in ok]
        why = []
        if absent:
            where = f"and in {source.as_posix()}" if source else "(staging is off)"
            why.append(f"input absent here {where}: {_names(absent)}")
        if refused:
            why.append(f"input absent here and not ignored here (never staged): {_names(refused)}")
        if why:
            result.skips[test] = "; ".join(why)
    return result


def path_limit_reason(repo: Path, dirs: list[str], limit: int = PATH_LIMIT, source: Path | None = None) -> str | None:
    """None when every file under the declared paths fits `limit` characters from this checkout's real root; else
    the reason, naming the longest path and the root length that would fit. A directory counts what is here AND
    what the source would stage into it (a tool can leave a short stray file in a staged directory - MPFB writes
    its logs into the profile - and the long paths the next staging brings back must still count)."""
    root = repo.resolve()
    rels = set()
    for rel in dirs:
        base = root / rel
        if base.is_file():
            rels.add(rel)
            continue
        if base.is_dir():
            rels.update((Path(d) / f).relative_to(root).as_posix() for d, _, fs in os.walk(base) for f in fs)
        if source:
            rels.update(_listed(source, rel))
    if not rels:
        return None
    longest = min(rels, key=lambda r: (-len(r), r))
    size = len(str(root)) + 1 + len(longest)
    if size <= limit:
        return None
    return (f"a declared read is {size} characters from this checkout (limit {limit}): {longest} - the checkout "
            f"root must be at most {len(str(root)) - (size - limit)} characters (a junction or subst does not "
            f"shorten it: the tests resolve() back to the real root)")


def plan_inputs(repo: Path, source: Path | None, files: list[str], limit: int = PATH_LIMIT) -> Staging:
    """The path-limit skips first (their inputs are not staged), then the staging for the rest."""
    needs = load_needs(repo)
    too_long = {rel: why for rel in files if rel in needs
                for why in [path_limit_reason(repo, needs[rel].get("path_limit", []), limit, source)] if why}
    staging = stage_inputs(repo, source, needs, [f for f in files if f not in too_long])
    staging.skips.update(too_long)
    return staging


# --- the generated layers: built once before the run when absent ------------------------------------------------

@dataclass
class Generated:
    path: str
    status: str                 # "present" | "built" | "failed"
    detail: str = ""            # a failure's exit code and the builder's last line


def build_generated(repo: Path, python: str, generated: dict[str, dict]) -> list[Generated]:
    """Run each absent output's builder from the checkout root, `--repo <checkout>` appended; never one already here."""
    done = []
    for rel in sorted(generated):
        if (repo / rel).exists():
            done.append(Generated(rel, "present"))
            continue
        script, *args = generated[rel]["build"]
        got = subprocess.run([python, str(repo / script), *args, "--repo", str(repo)], cwd=str(repo),
                             capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        lines = [line.strip() for line in (got.stdout + got.stderr).splitlines() if line.strip()]
        if got.returncode == 0 and (repo / rel).exists():
            done.append(Generated(rel, "built"))
            continue
        why = (lines[-1] if lines else "(no output)") if got.returncode else f"{rel} was not written"
        done.append(Generated(rel, "failed", f"exit {got.returncode}: {why}"[:MESSAGE_MAX]))
    return done


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
              rerun: bool = True, skips: dict[str, str] | None = None) -> list[FileResult]:
    results = []
    for n, rel in enumerate(files, 1):
        result = FileResult(path=rel, kind=kind_of(rel))
        if rel in (skips or {}):
            result.status, result.reason = "skip", skips[rel]
            print(f"[{n}/{len(files)}] SKIP  {'':>8} {rel} - {result.reason}", flush=True)
            results.append(result)
            continue
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


def counts_of(results: list[FileResult]) -> dict[str, int]:
    counts = {s: sum(1 for r in results if r.status == s) for s in ("pass", "fail", "flake", "skip")}
    return dict(counts, run=len(results) - counts["skip"])


def summary_md(results: list[FileResult], meta: dict, staging: Staging | None = None,
               generated: list[Generated] | None = None) -> str:
    fails = [r for r in results if r.status == "fail"]
    flakes = [r for r in results if r.status == "flake"]
    c = counts_of(results)
    lines = ["# Full suite - SUMMARY", "",
             f"- repo: `{meta['repo']}` at `{meta['head']}`", f"- started: {meta['started']}  seconds: {meta['seconds']}",
             f"- command: `{meta['argv']}`", "",
             f"files run {c['run']} / passed {c['pass']} / failed {c['fail']} / flaked {c['flake']} / "
             f"skipped {c['skip']}", ""]
    for title, group in (("Failed (failed again when rerun alone)", fails), ("Flaked (passed when rerun alone)", flakes)):
        lines += [f"## {title}", ""] + (["- none"] if not group else [])
        for r in group:
            last = r.runs[-1] if r.status == "fail" else r.runs[0]
            lines.append(f"- `{r.path}` (exit {last.rc}, log `{last.log}`)")
            lines += [f"  - `{test}` - {message}" for test, message in last.failures]
        lines.append("")
    return "\n".join(lines + _skip_lines(results) + _staged_lines(staging) + _generated_lines(generated))


def _skip_lines(results: list[FileResult]) -> list[str]:
    skipped = [r for r in results if r.status == "skip"]
    return (["## Skipped (never run: an input absent, or a read past the path limit - never a pass)", ""]
            + ([f"- `{r.path}` - {r.reason}" for r in skipped] or ["- none"]) + [""])


def _staged_lines(staging: Staging | None) -> list[str]:
    if staging is None:
        return []
    if staging.source is None:
        return ["## Staged inputs (staging is off)", ""]
    listed = [f"- `{rel}`" for rel in staging.staged[:STAGED_LISTED]]
    more = len(staging.staged) - STAGED_LISTED
    return ([f"## Staged inputs ({len(staging.staged)}, from `{staging.source}`)", ""] + (listed or ["- none"])
            + ([f"- ... and {more} more (all in staged-inputs.txt)"] if more > 0 else []) + [""])


def _generated_lines(generated: list[Generated] | None) -> list[str]:
    if not generated:
        return []
    return (["## Generated (built before the run when absent)", ""]
            + [f"- `{g.path}` - {g.status}" + (f" ({g.detail})" if g.detail else "") for g in generated] + [""])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", type=Path, default=REPO, help="the checkout to run in (default: this script's own)")
    ap.add_argument("--out", type=Path, help=f"where logs and SUMMARY go (default: <repo>/{OUT_REL}/<UTC stamp>)")
    ap.add_argument("--skip-goldens", action="store_true", help=f"leave out {GOLDENS}")
    ap.add_argument("--timeout", type=float, default=TIMEOUT_S, help="seconds per file before its process is ended")
    ap.add_argument("--no-rerun", action="store_true", help="do not rerun a failing file alone")
    ap.add_argument("--python", default=sys.executable, help="the interpreter for pytest (default: this one)")
    ap.add_argument("--node", default="node", help="the node executable")
    ap.add_argument("--inputs-from", type=Path,
                    help="the checkout gitignored inputs are staged from, read-only (default: this repo's main checkout)")
    ap.add_argument("--no-stage", action="store_true", help="stage nothing; a file missing an input is skipped")
    ap.add_argument("--path-limit", type=int, default=PATH_LIMIT,
                    help=f"the longest declared read, in characters from this checkout (default {PATH_LIMIT})")
    args = ap.parse_args(argv)
    repo = args.repo.resolve()
    if not (repo / TESTS_REL).is_dir():
        ap.error(f"no {TESTS_REL} under {repo}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = (args.out or repo / OUT_REL / stamp).resolve()
    source = None if args.no_stage else (args.inputs_from or main_checkout(repo))
    if source is not None:
        if not source.is_dir():
            ap.error(f"--inputs-from {source} is not a directory")
        source = source.resolve()
    files = discover(repo, args.skip_goldens)
    staging = plan_inputs(repo, source, files, args.path_limit)
    generated = build_generated(repo, args.python, load_generated(repo))
    out.mkdir(parents=True, exist_ok=True)
    (out / "staged-inputs.txt").write_text("".join(f"{rel}\n" for rel in staging.staged), encoding="utf-8")
    print(f"run_full_suite: {len(files)} files in {repo} -> {out}; staged {len(staging.staged)} inputs from "
          f"{staging.source or '(staging is off)'}, {len(staging.skips)} files skipped; generated: "
          f"{', '.join(f'{g.path} {g.status}' for g in generated) or 'none declared'}", flush=True)
    start = time.monotonic()
    results = run_suite(repo, out, files, args.timeout, args.python, args.node, rerun=not args.no_rerun,
                        skips=staging.skips)
    meta = {"repo": repo.as_posix(), "head": head_of(repo), "started": stamp,
            "seconds": round(time.monotonic() - start, 1),
            "argv": " ".join(["run_full_suite.py", *(sys.argv[1:] if argv is None else argv)])}
    counts = counts_of(results)
    (out / "SUMMARY.md").write_text(summary_md(results, meta, staging, generated) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(
        dict(meta, **counts, staged={"from": staging.source, "files": staging.staged},
             generated=[asdict(g) for g in generated], files=[asdict(r) for r in results]), indent=1) + "\n",
        encoding="utf-8")
    print(f"run_full_suite: files run {counts['run']} / passed {counts['pass']} / failed {counts['fail']} / "
          f"flaked {counts['flake']} / skipped {counts['skip']} - {out / 'SUMMARY.md'}", flush=True)
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())

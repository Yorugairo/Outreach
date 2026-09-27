"""run_full_suite.py - the whole suite, every test file in its own process (P72 T51c).

A synthetic checkout pins the contract: only `tests/test_*.py` and `tests/kinetics/*.test.mjs` run (a nested test,
a helper module and a test outside `tests/` never do); each file gets its own log; a failing file is rerun alone
once, a pass on the rerun is a FLAKE and does not fail the run; SUMMARY.md carries the counts and each failing test
id with its assertion's first line; `--skip-goldens` leaves out test_golden_frames.py; a file over the timeout has
its OWN process tree ended and nothing else - a bystander process the runner did not start is still alive after.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import run_full_suite as RFS  # noqa: E402

T = RFS.TESTS_REL
NODE = shutil.which("node")

FILES = {
    f"{T}/test_pass.py": "def test_ok():\n    assert True\n",
    f"{T}/test_fail.py": 'def test_it():\n    assert 1 == 2, "the first line\\nthe second line"\n',
    f"{T}/test_flaky.py": textwrap.dedent('''\
        from pathlib import Path
        MARK = Path(__file__).with_name("flaky.mark")
        def test_once():
            first = not MARK.exists()
            MARK.write_text("ran", encoding="utf-8")
            assert not first, "fails the first time only"
        '''),
    f"{T}/test_golden_frames.py": 'def test_pinned():\n    assert False, "the goldens ran"\n',
    f"{T}/helper_module.py": 'raise SystemExit("a helper is never run")\n',
    f"{T}/nested/test_nested.py": 'def test_nested():\n    assert False, "a nested test ran"\n',
    "content/video_engine/scripts/test_outside.py": 'def test_out():\n    assert False, "outside ran"\n',
    f"{T}/kinetics/ok.test.mjs": "import test from 'node:test';\ntest('fine', () => {});\n",
    f"{T}/kinetics/bad.test.mjs": textwrap.dedent('''\
        import test, { describe } from 'node:test';
        describe('group', () => {
          test('inner bad', () => { throw new Error('boom here\\nsecond'); });
          test('inner ok', () => {});
        });
        '''),
    f"{T}/kinetics/helper.mjs": "throw new Error('a helper is never run');\n",
    "pytest.ini": "[pytest]\n",
}


def _tree(tmp_path: Path, only: tuple[str, ...] | None = None) -> Path:
    repo = tmp_path / "repo"
    for rel, text in FILES.items():
        if only is None or rel in only or rel == "pytest.ini":
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text(text, encoding="utf-8")
    return repo


def _summary(out: Path) -> dict:
    return json.loads((out / "summary.json").read_text(encoding="utf-8"))


def _alive(pid: int) -> bool:
    if os.name == "nt":
        import ctypes
        kernel = ctypes.windll.kernel32
        handle = kernel.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        kernel.GetExitCodeProcess(handle, ctypes.byref(code))
        kernel.CloseHandle(handle)
        return code.value == 259                                   # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def test_it_walks_only_the_two_globs_and_skips_the_goldens_on_request(tmp_path: Path) -> None:
    repo = _tree(tmp_path)

    every = RFS.discover(repo)
    skipped = RFS.discover(repo, skip_goldens=True)

    assert every == [f"{T}/test_fail.py", f"{T}/test_flaky.py", f"{T}/test_golden_frames.py", f"{T}/test_pass.py",
                     f"{T}/kinetics/bad.test.mjs", f"{T}/kinetics/ok.test.mjs"]
    assert skipped == [f for f in every if not f.endswith("test_golden_frames.py")]
    assert RFS.command(f"{T}/test_pass.py", "py", "nd")[:3] == ["py", "-m", "pytest"]
    assert RFS.command(f"{T}/kinetics/ok.test.mjs", "py", "nd")[:2] == ["nd", "--test"]


@pytest.mark.skipif(NODE is None, reason="node is not installed")
def test_a_run_logs_each_file_reruns_a_failure_once_and_exits_nonzero_on_a_real_failure(tmp_path: Path) -> None:
    repo, out = _tree(tmp_path), tmp_path / "out"

    rc = RFS.main(["--repo", str(repo), "--out", str(out), "--skip-goldens"])

    got = _summary(out)
    status = {Path(f["path"]).name: f["status"] for f in got["files"]}
    assert rc == 1
    assert (got["run"], got["pass"], got["fail"], got["flake"]) == (5, 2, 2, 1)
    assert status == {"test_fail.py": "fail", "test_flaky.py": "flake", "test_pass.py": "pass",
                      "bad.test.mjs": "fail", "ok.test.mjs": "pass"}
    by_name = {Path(f["path"]).name: f for f in got["files"]}
    assert by_name["test_fail.py"]["runs"][-1]["failures"] == [
        [f"{T}/test_fail.py::test_it", "AssertionError: the first line"]]
    assert by_name["bad.test.mjs"]["runs"][-1]["failures"] == [["group > inner bad", "boom here"]]
    assert len(by_name["test_flaky.py"]["runs"]) == 2 and len(by_name["test_pass.py"]["runs"]) == 1
    assert sorted(p.name for p in (out / "logs").iterdir()) == sorted(f"{name}.log" for name in status)
    assert sorted(p.name for p in (out / "rerun").iterdir()) == [
        "bad.test.mjs.log", "test_fail.py.log", "test_flaky.py.log"]
    summary = (out / "SUMMARY.md").read_text(encoding="utf-8")
    assert "files run 5 / passed 2 / failed 2 / flaked 1" in summary
    assert f"`{T}/test_fail.py::test_it` - AssertionError: the first line" in summary
    assert "`group > inner bad` - boom here" in summary
    assert "the goldens ran" not in summary          # the nested / outside / helper files: `status` has the five


def test_the_goldens_run_unless_skipped_and_a_flake_alone_does_not_fail_the_run(tmp_path: Path) -> None:
    only = (f"{T}/test_pass.py", f"{T}/test_flaky.py", f"{T}/test_golden_frames.py")
    with_goldens = RFS.main(["--repo", str(_tree(tmp_path / "a", only)), "--out", str(tmp_path / "a/out")])
    skipping = RFS.main(["--repo", str(_tree(tmp_path / "b", only)), "--out", str(tmp_path / "b/out"),
                         "--skip-goldens"])

    assert with_goldens == 1
    assert [f["status"] for f in _summary(tmp_path / "a/out")["files"]
            if f["path"].endswith(RFS.GOLDENS)] == ["fail"]
    assert skipping == 0
    got = _summary(tmp_path / "b/out")
    assert (got["run"], got["pass"], got["fail"], got["flake"]) == (2, 1, 0, 1)


def test_a_file_over_the_timeout_has_only_its_own_process_tree_ended(tmp_path: Path) -> None:
    repo = _tree(tmp_path, ())
    grandchild_pid = repo / "grandchild.pid"
    (repo / T).mkdir(parents=True)
    (repo / T / "test_sleeps.py").write_text(textwrap.dedent(f'''\
        import subprocess, sys, time
        def test_sleeps():
            child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
            open({str(grandchild_pid)!r}, "w").write(str(child.pid))
            time.sleep(120)
        '''), encoding="utf-8")
    bystander = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])   # not the runner's
    try:
        rc = RFS.main(["--repo", str(repo), "--out", str(tmp_path / "out"), "--timeout", "8", "--no-rerun"])

        run = _summary(tmp_path / "out")["files"][0]["runs"][0]
        assert rc == 1 and run["timed_out"] is True and run["rc"] is None
        assert run["failures"][-1][0] == "(timeout)"
        assert not _alive(run["pid"])
        assert grandchild_pid.is_file() and not _alive(int(grandchild_pid.read_text()))
        assert bystander.poll() is None and _alive(bystander.pid)
    finally:
        bystander.kill()          # the test's own process, by its handle
        bystander.wait()


def test_the_parsers_read_the_first_line_and_skip_a_suite_failed_only_by_its_subtest() -> None:
    pytest_text = textwrap.dedent('''\
        =========================== short test summary info ===========================
        FAILED a/test_x.py::test_p[a b] - AssertionError: assert 'a b' == 'c'
        ERROR a/test_y.py - ImportError: no module named z
        ''')
    tap = textwrap.dedent('''\
        # Subtest: bad one
        not ok 1 - bad one
          ---
          failureType: 'testCodeFailure'
          error: |-
            Expected values to be strictly equal:

          ...
        # Subtest: group
            # Subtest: inner bad
            not ok 1 - inner bad
              ---
              failureType: 'testCodeFailure'
              error: 'boom'
              ...
        not ok 2 - group
          ---
          failureType: 'subtestsFailed'
          error: '1 subtest failed'
          ...
        ''')

    assert RFS.pytest_failures(pytest_text) == [["a/test_x.py::test_p[a b]", "AssertionError: assert 'a b' == 'c'"],
                                                ["a/test_y.py", "ImportError: no module named z"]]
    assert RFS.tap_failures(tap) == [["bad one", "Expected values to be strictly equal:"],
                                     ["group > inner bad", "boom"]]


# --- P72 T52: the gitignored inputs, staged or skipped with the reason ------------------------------------------

GIT = shutil.which("git")
needs_git = pytest.mark.skipif(GIT is None, reason="git is not installed")
IGNORE = "*.bin\n**/review/\nprofile/\n__pycache__/\n"
READS = "from pathlib import Path\nROOT = Path(__file__).resolve().parents[3]\n"


def _git(cwd: Path, *args: str) -> str:
    done = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "user.name=t52",
                           "-c", "user.email=t52@example.invalid", *args],
                          cwd=cwd, capture_output=True, text=True, check=True)
    return done.stdout


def _checkout(root: Path, files: dict[str, bytes | str]) -> Path:
    """A git checkout carrying the ignore rules and `files` (the tracked ones are committed)."""
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q")
    (root / ".gitignore").write_text(IGNORE, encoding="utf-8")
    for rel, body in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(body if isinstance(body, bytes) else body.encode("utf-8"))
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    return root


def _needs_text(needs: dict) -> str:
    return json.dumps({"schema": RFS.INPUTS_SCHEMA, "files": needs}, indent=1)


def _needs(repo: Path, needs: dict) -> None:
    path = repo / RFS.INPUTS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_needs_text(needs), encoding="utf-8")


def _pair(tmp_path: Path, tests: dict[str, str], needs: dict) -> tuple[Path, Path]:
    """A target checkout with `tests` and the declared needs, and a source checkout holding the ignored inputs."""
    target = _checkout(tmp_path / "target", {"pytest.ini": "[pytest]\n", "data/present.bin": b"the target's own",
                                             RFS.INPUTS_REL: _needs_text(needs),
                                             **{f"{T}/{name}": body for name, body in tests.items()}})
    source = _checkout(tmp_path / "source", {"pytest.ini": "[pytest]\n", "notes/plain.txt": "tracked in the source"})
    for rel, body in {"data/a.bin": b"alpha\r\n", "data/present.bin": b"the source's copy",
                      "x/review/deep/b.png": b"png", "kit/profile/p/q/r.dat": b"deep", "kit/profile/s.dat": b"s",
                      "loose/untracked.txt": b"neither tracked nor ignored"}.items():
        (source / rel).parent.mkdir(parents=True, exist_ok=True)
        (source / rel).write_bytes(body)
    return target, source


@needs_git
def test_absent_ignored_inputs_are_staged_from_the_source_never_overwriting_and_reported(tmp_path: Path) -> None:
    body = READS + textwrap.dedent('''\
        def test_reads():
            assert (ROOT / "data/a.bin").read_bytes() == b"alpha\\r\\n"
            assert (ROOT / "x/review/deep/b.png").read_bytes() == b"png"
            assert (ROOT / "kit/profile/p/q/r.dat").read_bytes() == b"deep"
            assert (ROOT / "data/present.bin").read_bytes() == b"the target's own"
        ''')
    needs = {f"{T}/test_reads.py": {"inputs": ["data/a.bin", "x/review/deep/b.png", "kit/profile/", "data/present.bin"]}}
    target, source = _pair(tmp_path, {"test_reads.py": body}, needs)
    out = tmp_path / "out"

    rc = RFS.main(["--repo", str(target), "--out", str(out), "--inputs-from", str(source)])

    got = _summary(out)
    assert rc == 0 and (got["run"], got["pass"], got["skip"]) == (1, 1, 0)
    staged = ["data/a.bin", "kit/profile/p/q/r.dat", "kit/profile/s.dat", "x/review/deep/b.png"]
    assert got["staged"] == {"from": source.resolve().as_posix(), "files": staged}
    assert (target / "data/a.bin").read_bytes() == b"alpha\r\n"                      # bytes, not text
    assert (target / "data/present.bin").read_bytes() == b"the target's own"        # never overwritten
    assert _git(target, "status", "--porcelain") == ""                                # every staged file is ignored
    summary = (out / "SUMMARY.md").read_text(encoding="utf-8")
    assert f"## Staged inputs (4, from `{source.resolve().as_posix()}`)" in summary
    assert "- `x/review/deep/b.png`" in summary


@needs_git
def test_an_input_absent_everywhere_or_not_ignored_here_skips_its_file_with_the_reason(tmp_path: Path) -> None:
    tests = {"test_nowhere.py": "def test_x():\n    assert True\n",
             "test_unignored.py": "def test_y():\n    assert True\n",
             "test_plain.py": "def test_z():\n    assert True\n"}
    needs = {f"{T}/test_nowhere.py": {"inputs": ["data/nowhere.bin", "gone/review/"]},
             f"{T}/test_unignored.py": {"inputs": ["loose/untracked.txt", "notes/plain.txt"]}}
    target, source = _pair(tmp_path, tests, needs)
    out = tmp_path / "out"

    rc = RFS.main(["--repo", str(target), "--out", str(out), "--inputs-from", str(source)])

    got = _summary(out)
    by_name = {Path(f["path"]).name: f for f in got["files"]}
    assert rc == 0 and (got["run"], got["pass"], got["fail"], got["skip"]) == (1, 1, 0, 2)
    assert by_name["test_plain.py"]["status"] == "pass"
    assert by_name["test_nowhere.py"]["status"] == "skip" and by_name["test_nowhere.py"]["runs"] == []
    assert by_name["test_nowhere.py"]["reason"] == (
        f"input absent here and in {source.resolve().as_posix()}: data/nowhere.bin, gone/review/")
    assert by_name["test_unignored.py"]["reason"] == (
        "input absent here and not ignored here (never staged): loose/untracked.txt, notes/plain.txt")
    assert not (target / "loose").exists() and not (target / "notes").exists() and not (target / "gone").exists()
    assert got["staged"]["files"] == []
    summary = (out / "SUMMARY.md").read_text(encoding="utf-8")
    assert "files run 1 / passed 1 / failed 0 / flaked 0 / skipped 2" in summary
    assert f"- `{T}/test_nowhere.py` - input absent here and in" in summary


@needs_git
def test_without_a_source_nothing_is_staged_and_a_missing_input_skips(tmp_path: Path) -> None:
    needs = {f"{T}/test_reads.py": {"inputs": ["data/a.bin"]}}
    target, _source = _pair(tmp_path, {"test_reads.py": "def test_x():\n    assert True\n"}, needs)
    out = tmp_path / "out"

    rc = RFS.main(["--repo", str(target), "--out", str(out), "--no-stage"])

    got = _summary(out)
    assert rc == 0 and got["skip"] == 1 and got["staged"] == {"from": None, "files": []}
    assert got["files"][0]["reason"] == "input absent here (staging is off): data/a.bin"
    assert not (target / "data/a.bin").exists()


@needs_git
def test_the_default_source_is_the_main_checkout_of_a_linked_worktree(tmp_path: Path) -> None:
    main = _checkout(tmp_path / "main", {"a.txt": "a"})
    linked = tmp_path / "wt"
    _git(main, "worktree", "add", "-q", "--detach", str(linked))

    assert RFS.main_checkout(linked) == main.resolve()
    assert RFS.main_checkout(main) == main.resolve()
    assert RFS.main_checkout(tmp_path) is None


def test_a_declared_read_past_the_path_limit_from_this_checkout_skips_with_the_length(tmp_path: Path) -> None:
    repo = _tree(tmp_path, (f"{T}/test_pass.py",))
    deep = repo / "assets/native/a-rather-long-directory-name/model.blend"
    deep.parent.mkdir(parents=True)
    deep.write_bytes(b"blend")
    _needs(repo, {f"{T}/test_pass.py": {"path_limit": ["assets/native/"]}})
    longest = len(str(deep.resolve()))
    out = tmp_path / "out"

    fits = RFS.path_limit_reason(repo, ["assets/native/"], limit=longest)
    over = RFS.path_limit_reason(repo, ["assets/native/"], limit=longest - 1)
    rc = RFS.main(["--repo", str(repo), "--out", str(out), "--no-stage", "--path-limit", str(longest - 1)])

    assert fits is None
    assert over == (f"a declared read is {longest} characters from this checkout (limit {longest - 1}): "
                    f"assets/native/a-rather-long-directory-name/model.blend - the checkout root must be at most "
                    f"{len(str(repo.resolve())) - 1} characters (a junction or subst does not shorten it: the "
                    f"tests resolve() back to the real root)")
    got = _summary(out)
    assert rc == 0 and got["skip"] == 1 and got["files"][0]["reason"] == over


@needs_git
def test_a_path_limit_dir_already_here_is_measured_with_what_the_source_would_stage_into_it(tmp_path: Path) -> None:
    """A tool can leave a stray file in a staged directory (MPFB writes its logs into the profile): the directory is
    then HERE but short, and the long paths the next staging brings back must still count."""
    target, source = _pair(tmp_path, {"test_x.py": "def test_x():\n    assert True\n"}, {})
    (target / "kit/profile").mkdir(parents=True)
    (target / "kit/profile/log.txt").write_bytes(b"a stray log")
    longest = len(str(target.resolve() / "kit/profile/p/q/r.dat"))

    with_source = RFS.path_limit_reason(target, ["kit/profile/"], limit=longest - 1, source=source)
    here_only = RFS.path_limit_reason(target, ["kit/profile/"], limit=longest - 1)

    assert with_source is not None and "kit/profile/p/q/r.dat" in with_source
    assert here_only is None


def test_a_needs_entry_that_leaves_the_checkout_is_refused(tmp_path: Path) -> None:
    repo = _tree(tmp_path, (f"{T}/test_pass.py",))
    for bad in ("../outside.bin", "C:/abs.bin", "/abs.bin", "a/../../b.bin"):
        _needs(repo, {f"{T}/test_pass.py": {"inputs": [bad]}})
        with pytest.raises(ValueError, match="stays inside the checkout"):
            RFS.load_needs(repo)

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

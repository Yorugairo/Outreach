"""The docs stack is ordered, so these pin the order, the skip and the exit code.

Every layer after `build_docs_index.py` reads the index it writes, which is exactly why a docs
pass that rebuilds one layer and forgets the next ships something stale that still looks fresh.
The wrapper's whole job is that order plus an honest exit code, so the unit tests replace the
subprocess boundary (`run_script`) with a recorder and drive a stubbed layer list: the order the
tools run in, the audit running in `--write` only, a tool that is not in this checkout being
SKIPPED with a printed note instead of failing, and the digest `--check` naming the FIRST stale
layer and stopping there.

`--check` no longer runs the tools: a layer is stale when the digest of its INPUTS is not the one
stamped in `docs/.layers/<name>.digest` (P63 T1, `docs_layers.py`), which is the difference between
91 s and under 2 s. `--write` is unchanged - every builder, then each tool's own byte check - and
stamps the digests afterwards. The last test is the real thing: the stack over the committed tree.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_docs_layers as BDL  # noqa: E402
import docs_layers as DL  # noqa: E402

STUB_LAYERS = (
    BDL.Layer("first", "stub_first.py", outputs=("docs/first.jsonl",)),
    BDL.Layer("second", "stub_second.py", outputs=("docs/second.jsonl",), depends_on=("first",)),
    BDL.Layer("absent", "stub_absent.py", outputs=("docs/absent.jsonl",)),
    BDL.Layer("report", "stub_report.py", outputs=("docs/R.md",), write_args=("--report", "docs/R.md"),
              check_args=None, repo_flag="--root"),
)


class Recorder:
    """Stands in for the subprocess boundary: records every call, returns canned exit codes."""

    def __init__(self, codes: dict[str, int] | None = None) -> None:
        self.calls: list[tuple[str, tuple[str, ...]]] = []
        self.codes = codes or {}

    def __call__(self, script: Path, args: tuple[str, ...], repo: Path) -> tuple[int, str]:
        name = Path(script).name
        self.calls.append((name, tuple(args)))
        code = self.codes.get(f"{name} {args[0]}", self.codes.get(name, 0))
        return code, f"{name}: line one\n{name} said {args[0]}\n"

    def names(self, flag: str | None = None) -> list[str]:
        return [n for n, args in self.calls if flag is None or args[0] == flag]


@pytest.fixture()
def stubbed(tmp_path: Path, monkeypatch) -> Path:
    """The stub layer list, with every script but `stub_absent.py` present in a fake scripts dir."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for layer in STUB_LAYERS:
        if layer.name != "absent":
            (scripts / layer.script).write_text("# stub\n", encoding="utf-8")
    # `docs_layers.SENTINEL`: its presence is what tells `ensure` this is a scripts directory and
    # not a hand-written fixture tree. No stub layer names it, so it is never run.
    (scripts / DL.SENTINEL).write_text("# stub\n", encoding="utf-8")
    monkeypatch.setattr(BDL, "SCRIPTS", scripts)
    monkeypatch.setattr(BDL, "LAYERS", STUB_LAYERS)
    return tmp_path


# --- order --------------------------------------------------------------------------------

def test_write_runs_the_layers_in_order_then_rechecks(stubbed, monkeypatch):
    recorder = Recorder()
    monkeypatch.setattr(BDL, "run_script", recorder)

    assert BDL.main(["--write", "--repo", str(stubbed)]) == 0

    assert recorder.names("--write") == ["stub_first.py", "stub_second.py"]
    assert recorder.names("--report") == ["stub_report.py"]        # write only, and last
    assert recorder.names("--check") == ["stub_first.py", "stub_second.py"]
    assert [n for n, _ in recorder.calls] == ["stub_first.py", "stub_second.py", "stub_report.py",
                                              "stub_first.py", "stub_second.py"]


def test_write_stamps_a_digest_for_every_layer_it_built(stubbed, monkeypatch):
    monkeypatch.setattr(BDL, "run_script", Recorder())

    assert BDL.main(["--write", "--repo", str(stubbed)]) == 0

    stamped = sorted(p.name for p in (stubbed / DL.CACHE_REL).iterdir())
    assert stamped == ["first.digest", "report.digest", "second.digest"]   # not the absent tool
    assert BDL.main(["--check", "--repo", str(stubbed)]) == 0              # and the check is now clean


def test_each_tool_is_told_the_repository_root_in_its_own_flag(stubbed, monkeypatch):
    recorder = Recorder()
    monkeypatch.setattr(BDL, "run_script", recorder)

    assert BDL.main(["--write", "--repo", str(stubbed)]) == 0

    args = dict(recorder.calls)
    assert args["stub_first.py"] == ("--check", "--repo", str(stubbed.resolve()))
    assert args["stub_report.py"] == ("--report", "docs/R.md", "--root", str(stubbed.resolve()))


# --- the missing tool ------------------------------------------------------------------------

def test_a_tool_that_is_not_in_this_checkout_is_skipped_with_a_note(stubbed, monkeypatch, capsys):
    recorder = Recorder()
    monkeypatch.setattr(BDL, "run_script", recorder)

    assert BDL.main(["--write", "--repo", str(stubbed)]) == 0

    out = capsys.readouterr().out
    assert "stub_absent.py" not in [n for n, _ in recorder.calls]
    assert "SKIP" in out and "absent" in out and "stub_absent.py not in this checkout yet" in out


# --- the exit code -----------------------------------------------------------------------------

def test_check_runs_no_tool_at_all_and_fails_on_a_layer_never_built(stubbed, monkeypatch, capsys):
    recorder = Recorder()
    monkeypatch.setattr(BDL, "run_script", recorder)

    assert BDL.main(["--check", "--repo", str(stubbed)]) == 1
    assert BDL.main(["--repo", str(stubbed)]) == 1                 # no flag is --check

    assert recorder.calls == []                                    # the digest answers, not the tools
    out = capsys.readouterr().out
    assert "STALE" in out and "never built in this checkout" in out


def test_check_names_the_first_stale_layer_and_stops_there(stubbed, monkeypatch, capsys):
    monkeypatch.setattr(BDL, "run_script", Recorder())
    assert BDL.main(["--write", "--repo", str(stubbed)]) == 0      # stamps every digest
    capsys.readouterr()

    script = stubbed / "scripts/stub_first.py"                     # an input of `first`: its builder
    script.write_text("# stub, edited\n", encoding="utf-8")

    assert BDL.main(["--check", "--repo", str(stubbed)]) == 1

    out = capsys.readouterr().out
    assert "STALE" in out and "first is stale" in out and "--write" in out
    assert "second" not in out                                     # the pass stopped at the first


def test_a_layer_that_fails_to_build_stops_the_write_before_the_recheck(stubbed, monkeypatch, capsys):
    recorder = Recorder({"stub_second.py --write": 2})
    monkeypatch.setattr(BDL, "run_script", recorder)

    assert BDL.main(["--write", "--repo", str(stubbed)]) == 1

    out = capsys.readouterr().out
    assert recorder.names() == ["stub_first.py", "stub_second.py"]  # no report, no re-check
    assert "FAILED" in out and "second" in out
    assert not (stubbed / DL.CACHE_REL).exists()                    # nothing stamped from a failed pass


def test_the_summary_line_carries_the_tool_own_last_line(stubbed, monkeypatch, capsys):
    monkeypatch.setattr(BDL, "run_script", Recorder())

    assert BDL.main(["--write", "--repo", str(stubbed)]) == 0

    out = capsys.readouterr().out
    assert "stub_first.py said --check" in out                     # the last line, not the first
    assert out.count("stub_first.py: line one") == 0
    assert len([line for line in out.splitlines() if line.startswith("build_docs_layers:")]) == 8


def test_last_line_of_a_silent_tool_is_named_not_blank():
    assert BDL.last_line("") == "(no output)"
    assert BDL.last_line("one\n\ntwo\n\n") == "two"


# --- ensure ---------------------------------------------------------------------------------------

def test_ensure_rebuilds_only_what_is_stale_and_says_so(stubbed, monkeypatch, capsys):
    """`--ensure` drives `docs_layers.ensure`, which runs the builder, not the check."""
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake(script: Path, args: tuple[str, ...], repo: Path) -> tuple[int, str]:
        calls.append((Path(script).name, tuple(args)))
        return 0, "stub: built\n"

    monkeypatch.setattr(DL, "run_script", fake)

    assert BDL.main(["--ensure", "--repo", str(stubbed)]) == 0
    assert [name for name, _ in calls] == ["stub_first.py", "stub_second.py", "stub_report.py"]
    assert "rebuilt first, second, report" in capsys.readouterr().out

    assert BDL.main(["--ensure", "--repo", str(stubbed)]) == 0      # nothing moved
    assert len(calls) == 3
    assert "every layer already current" in capsys.readouterr().out


def test_ensure_only_takes_a_layer_and_its_upstream(stubbed, monkeypatch, capsys):
    calls: list[str] = []
    monkeypatch.setattr(DL, "run_script",
                        lambda script, args, repo: (calls.append(Path(script).name), (0, "ok\n"))[1])

    assert BDL.main(["--ensure", "--only", "second", "--repo", str(stubbed)]) == 0
    assert calls == ["stub_first.py", "stub_second.py"]             # `second` depends on `first`


def test_ensure_reports_a_failing_builder_with_its_last_line(stubbed, monkeypatch, capsys):
    monkeypatch.setattr(DL, "run_script",
                        lambda script, args, repo: (1, "stub: trying\nstub: the source is malformed\n"))

    assert BDL.main(["--ensure", "--repo", str(stubbed)]) == 1
    assert "FAILED to build first - stub: the source is malformed" in capsys.readouterr().out


# --- the real tree --------------------------------------------------------------------------------

def test_the_committed_tree_passes_check():
    """The stack really runs: every tool that is stale, over this checkout, in order."""
    assert [layer.script for layer in BDL.LAYERS] == [
        "build_docs_index.py", "build_capabilities_index.py", "build_asset_index.py",
        "build_research_ledger.py", "build_effects_catalog.py",
        "build_docs_manifest.py", "build_topic_index.py",
        "build_gates_registry.py",
        "build_animation_registry.py",
        "build_craft_map.py",
        "report_doc_overlap.py", "audit_docs_standard.py"]
    DL.ensure(None, ROOT)                    # a no-op when nothing moved; the honest cost when it did
    assert BDL.main(["--check", "--repo", str(ROOT)]) == 0

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


# --- the real tree ---------------------------------------------------------------------------------
#
# R26-162: this test used to `ensure` over the LIVE checkout, so another lane's half-done working-tree edit (P61 T14's
# in-flight `dials.note` on the plate-idle card) failed it, and it rewrote the live generated layers as a side effect.
# It now rebuilds a SCRATCH COPY of what HEAD holds: the committed tree is what it names, and a dirty card, an untracked
# file or a stale live layer cannot move its answer. The live layers and digests only SEED the copy (read, never
# written), so a layer whose committed inputs match the live stamp is not rebuilt; any other layer is, honestly.

BINARY_EXT = frozenset(("png", "jpg", "jpeg", "webp", "gif", "mp4", "webm", "mov", "wav", "mp3", "m4a", "flac",
                        "ttf", "otf", "woff", "woff2", "zip", "pdf"))
WHOLE_ROOTS = ("docs/", "content/video_engine/scripts/", "content/video_engine/effects/",
               "content/video_engine/configs/", "content/video_engine/sources/")


def layer_input(rel: str) -> bool:
    """A superset of what `docs_layers.LAYERS` reads (their globs, widened to whole roots), minus media."""
    name = rel.rsplit("/", 1)[-1]
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if rel == "AGENTS.md" or rel.startswith((".claude/PRPs/plans/", "content/video_engine/assets/")):
        return True                                       # the asset index LISTS every file there, media too
    if ext in BINARY_EXT:
        return False
    if rel.startswith(WHOLE_ROOTS):
        return True
    if rel.startswith("content/video_engine/tests/"):
        return ext in ("py", "mjs", "js")
    return rel.startswith("content/video_engine/projects/") and ext == "md"


def committed_tree(root: Path, dest: Path, wanted=layer_input) -> Path:
    """Every file HEAD holds that `wanted` keeps, written under `dest` from git's own blobs - never the working tree."""
    import subprocess

    listing = subprocess.run(["git", "ls-tree", "-r", "-z", "HEAD"], cwd=root, capture_output=True, check=True).stdout
    blobs: list[tuple[str, str]] = []
    for entry in filter(None, listing.split(b"\0")):
        meta, rel = entry.split(b"\t", 1)
        kind, sha = meta.split()[1:3]
        if kind == b"blob" and wanted(rel.decode("utf-8")):
            blobs.append((sha.decode(), rel.decode("utf-8")))
    batch = subprocess.run(["git", "cat-file", "--batch"], cwd=root, check=True, capture_output=True,
                           input="".join(f"{sha}\n" for sha, _rel in blobs).encode()).stdout
    at = 0
    for _sha, rel in blobs:
        header_end = batch.index(b"\n", at)
        size = int(batch[at:header_end].split()[2])
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(batch[header_end + 1:header_end + 1 + size])
        at = header_end + 1 + size + 1
    return dest


def seed_layers(live: Path, copy: Path) -> None:
    """The live checkout's generated layers and their stamps, copied in so an unmoved layer is not rebuilt."""
    import shutil

    for layer in DL.LAYERS:
        for rel in layer.outputs:
            if (live / rel).is_file():
                (copy / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(live / rel, copy / rel)
    (copy / DL.CACHE_REL).mkdir(parents=True, exist_ok=True)
    for stamp_file in (live / DL.CACHE_REL).glob("*.digest"):
        shutil.copy2(stamp_file, copy / DL.CACHE_REL / stamp_file.name)


def is_git_checkout(root: Path) -> bool:
    import subprocess

    try:
        return subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], cwd=root,
                              capture_output=True).returncode == 0
    except OSError:
        return False


def test_the_committed_copy_is_heads_bytes_not_the_working_trees(tmp_path):
    """R26-162's mechanism on a tiny repository: a dirty edit and an untracked file never reach the copy."""
    import subprocess

    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs/a.md").write_bytes(b"committed\n")
    (repo / "docs/pic.png").write_bytes(b"\x89PNG media")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.autocrlf=false"]
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
        subprocess.run([*git, *args], cwd=repo, check=True, capture_output=True)
    (repo / "docs/a.md").write_bytes(b"another lane's half-done edit\n")
    (repo / "docs/b.md").write_bytes(b"untracked\n")

    copy = committed_tree(repo, tmp_path / "copy")

    assert (copy / "docs/a.md").read_bytes() == b"committed\n"
    assert not (copy / "docs/b.md").exists() and not (copy / "docs/pic.png").exists()


def test_the_committed_tree_passes_check(tmp_path, monkeypatch):
    """The stack really runs: every tool that is stale, over a scratch copy of HEAD, in order (R26-162)."""
    assert [layer.script for layer in BDL.LAYERS] == [
        "build_docs_index.py", "build_capabilities_index.py", "build_asset_index.py",
        "build_research_ledger.py", "build_effects_catalog.py",
        "build_docs_manifest.py", "build_topic_index.py",
        "build_gates_registry.py",
        "build_animation_registry.py",
        "build_craft_map.py",
        "report_doc_overlap.py", "audit_docs_standard.py"]
    if not is_git_checkout(ROOT):
        pytest.skip("not a git checkout: there is no committed tree to copy")
    copy = committed_tree(ROOT, tmp_path / "committed")
    seed_layers(ROOT, copy)
    DL.ensure(None, copy)                    # the copy's own builders; the live checkout is only read
    monkeypatch.setattr(BDL, "SCRIPTS", copy / DL.SCRIPTS_REL)
    # the committed tree's layers are the subject; this machine's live memories are not (R26-188's step has its own tests)
    assert BDL.main(["--check", "--repo", str(copy), "--no-memory-mirror"]) == 0


# --- --refresh, --status and the child's --then-recheck (P64 T1) ----------------------------------

import os    # noqa: E402


def test_refresh_returns_at_once_and_says_what_it_started(stubbed, monkeypatch, capsys):
    """`--refresh` is what a write hook calls: it must never build in-process and never fail."""
    # Arrange
    started: list = []
    monkeypatch.setattr(DL, "start_refresh",
                        lambda repo, names, scripts=None: started.append(list(names)) or 4242)
    monkeypatch.setattr(DL, "run_script", lambda *a, **k: pytest.fail("--refresh built in-process"))

    # Act
    assert BDL.main(["--refresh", "--repo", str(stubbed)]) == 0

    # Assert
    assert started == [["first", "second", "report"]]           # every stub layer, none built here
    assert "refreshing first, second, report in the background (pid 4242" in capsys.readouterr().out


def test_refresh_does_nothing_while_a_live_lock_holds_the_checkout(stubbed, monkeypatch, capsys):
    # Arrange: a lock held by this very process - certainly alive
    DL.write_lock(stubbed, os.getpid(), ["first"])
    monkeypatch.setattr(DL, "start_refresh", lambda *a, **k: pytest.fail("a second refresh started"))

    # Act
    assert BDL.main(["--refresh", "--repo", str(stubbed)]) == 0

    # Assert
    assert f"already running (pid {os.getpid()}" in capsys.readouterr().out
    DL.clear_lock(stubbed, os.getpid())


def test_status_prints_the_stale_set_the_lock_and_the_last_line_without_building(stubbed, monkeypatch,
                                                                                 capsys):
    # Arrange
    monkeypatch.setattr(DL, "run_script", lambda *a, **k: pytest.fail("--status built something"))
    DL.write_lock(stubbed, os.getpid(), ["first"])
    DL.log_path(stubbed).write_text("build_docs_layers: rebuilt first\n", encoding="utf-8")

    # Act
    assert BDL.main(["--status", "--repo", str(stubbed)]) == 0

    # Assert
    out = capsys.readouterr().out
    assert "stale: first, second, report" in out
    assert f"refresh: running, pid {os.getpid()}" in out
    assert "last line: build_docs_layers: rebuilt first" in out
    DL.clear_lock(stubbed, os.getpid())


def test_the_child_goes_again_when_a_write_lands_during_its_pass_and_stops_after_three_rounds(
        stubbed, monkeypatch, capsys):
    """A write landing WHILE a layer is rebuilt would otherwise wait for the next write to be noticed."""
    # Arrange: every "build" rewrites a builder script - an input - so the tree is never current
    rounds: list = []

    def churn(script, args, repo):
        """Every build rewrites the OTHER layer's script - the write that lands mid-pass."""
        rounds.append(Path(script).name)
        other = "stub_second.py" if Path(script).name == "stub_first.py" else "stub_first.py"
        (Path(stubbed) / "scripts" / other).write_text(f"# {len(rounds)}\n", encoding="utf-8")
        return 0, "stub: line\n"

    monkeypatch.setattr(DL, "run_script", churn)
    DL.write_lock(stubbed, os.getpid(), ["first"])

    # Act
    assert BDL.main(["--ensure", "--then-recheck", "--repo", str(stubbed)]) == 0

    # Assert: it goes again, it is BOUNDED, it says so - and it takes its own lock off on the way out
    out = capsys.readouterr().out
    assert out.count("going again") == DL.REFRESH_ROUNDS - 1
    assert f"stopped after {DL.REFRESH_ROUNDS} rounds, still stale:" in out
    assert not DL.lock_path(stubbed).exists()


def test_the_child_stops_at_the_first_clean_recheck_and_clears_the_lock(stubbed, monkeypatch, capsys):
    # Arrange: a well-behaved build - nothing moves under it
    monkeypatch.setattr(DL, "run_script", Recorder())
    DL.write_lock(stubbed, os.getpid(), ["first"])

    # Act
    assert BDL.main(["--ensure", "--then-recheck", "--repo", str(stubbed)]) == 0

    # Assert
    out = capsys.readouterr().out
    assert "refresh done in 1 round(s), every layer current" in out and "going again" not in out
    assert not DL.lock_path(stubbed).exists()


def test_only_takes_a_comma_separated_list_and_ensure_without_recheck_is_unchanged(stubbed, monkeypatch,
                                                                                   capsys):
    recorder = Recorder()
    monkeypatch.setattr(DL, "run_script", recorder)

    assert BDL.main(["--ensure", "--only", "first,second", "--repo", str(stubbed)]) == 0

    assert recorder.names("--write") == ["stub_first.py", "stub_second.py"]
    assert "rebuilt first, second" in capsys.readouterr().out


# --- R26-188's mirror (P72 T28): the operator-memory mirror is one step of --check ---------------------------------

MIRROR_REL = "docs/agent-memory/operator"   # `sync_operator_memory.DEFAULT_DST`, repo-relative

def _memory(name: str, body: str) -> bytes:
    return f"---\r\nname: {name}\r\ndescription: test\r\n---\r\n\r\n{body}\r\n".encode("utf-8")


@pytest.fixture()
def mirrored(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    """A repo whose layers are current (the digest pass is not this step's subject) and a memory folder with its
    mirror exported by the real `sync_operator_memory.py`."""
    repo, src = tmp_path / "repo", tmp_path / "memory"
    src.mkdir()
    (src / "MEMORY.md").write_bytes(b"- [Alpha](alpha-file.md) - index line\r\n")
    (src / "alpha-file.md").write_bytes(_memory("alpha", "See [[beta]]."))
    (src / "beta-file.md").write_bytes(_memory("beta", "Back to [[alpha]]."))
    dst = repo / MIRROR_REL
    import sync_operator_memory as som
    assert som.main(["--export", "--src", str(src), "--dst", str(dst)]) == 0
    monkeypatch.setattr(BDL, "digest_pass", lambda *_a, **_k: [])
    return repo, src


def test_check_passes_when_the_memory_mirror_is_in_sync(mirrored, capsys):
    repo, src = mirrored
    assert BDL.main(["--check", "--repo", str(repo), "--memory-src", str(src)]) == 0
    out = capsys.readouterr().out
    assert "ok      memory-mirror" in out and "in sync (3 files)" in out


def test_check_fails_naming_the_mirror_when_a_copy_is_stale(mirrored, capsys):
    repo, src = mirrored
    (repo / MIRROR_REL / "beta-file.md").write_bytes(_memory("beta", "an older copy."))   # planted stale
    assert BDL.main(["--check", "--repo", str(repo), "--memory-src", str(src)]) == 1
    out = capsys.readouterr().out
    assert "STALE   memory-mirror" in out and "drifted: beta-file.md" in out
    assert "sync_operator_memory.py --export" in out


def test_check_fails_when_a_memory_has_no_copy_yet(mirrored, capsys):
    repo, src = mirrored
    (src / "gamma-file.md").write_bytes(_memory("gamma", "new today."))
    assert BDL.main(["--check", "--repo", str(repo), "--memory-src", str(src)]) == 1
    assert "missing: gamma-file.md" in capsys.readouterr().out


def test_the_mirror_step_is_skipped_and_said_where_there_is_nothing_to_compare(mirrored, tmp_path, capsys):
    repo, src = mirrored
    assert BDL.main(["--check", "--repo", str(repo), "--memory-src", str(tmp_path / "no-memory-here")]) == 0
    assert "SKIP    memory-mirror   no operator memory on this machine" in capsys.readouterr().out
    assert BDL.main(["--check", "--repo", str(repo), "--memory-src", str(src), "--no-memory-mirror"]) == 0
    assert "SKIP    memory-mirror   --no-memory-mirror" in capsys.readouterr().out
    bare = tmp_path / "bare-repo"
    bare.mkdir()
    assert BDL.main(["--check", "--repo", str(bare), "--memory-src", str(src)]) == 0
    assert "carries no mirror" in capsys.readouterr().out

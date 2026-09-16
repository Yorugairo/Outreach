"""The layers are build output: these pin the table, the digest and `ensure`.

Two halves. The first reads the REAL table against this checkout - every layer's input globs
resolve to files that are here, its outputs are named, and the declared dependencies really are a
dependency order - because an input glob that resolves to nothing is a builder input someone moved,
and an input that is MISSING from the table is worse: the layer would read as fresh while its
source changed, which is the exact lie the digest exists to prevent.

The third part (P64 T1) drives the BACKGROUND refresh over that same miniature repo, with a fake
`build_docs_layers.py` that sleeps: `refresh` spawns a detached process, writes
`docs/.layers/REBUILD.lock`, refuses to start a second one while that one is live, takes over a lock
whose pid is dead or whose start time is older than ten minutes, and `status` answers a reader
without building anything.

The second half builds a miniature repo in `tmp_path` with fake builders (a tiny script that reads
its inputs, writes its output and prints a line) and drives `ensure` over it: one rebuild, then
none, then one more after an input is touched; a failing builder raising `LayerError` with the
builder's own last line; and the dependency order - a downstream layer rebuilding when only its
upstream's artifact moved. No real builder runs here: those cost four minutes, and what is under
test is the table, not them.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import docs_layers as DL  # noqa: E402

# `build_animation_registry.py:189-192` accepts .py, .mjs AND .js test files; this tree has no .js
# test yet. An empty glob is allowed only when the builder's own line says the kind is supported.
ALLOWED_EMPTY = {"content/video_engine/tests/**/*.js"}


# --- the real table against this checkout ---------------------------------------------------------

def present(layer: DL.Layer) -> bool:
    return DL.script_path(layer, ROOT / DL.SCRIPTS_REL).is_file()


@pytest.mark.parametrize("layer", DL.LAYERS, ids=[one.name for one in DL.LAYERS])
def test_every_input_glob_resolves_to_files_that_are_here(layer):
    if not present(layer):
        pytest.skip(f"{layer.script} is not in this checkout")
    cache: dict = {}
    resolved = {one.pattern: one.paths(ROOT, cache) for one in layer.inputs}
    empty = [pattern for pattern, paths in resolved.items()
             if not paths and pattern not in ALLOWED_EMPTY]
    assert not empty, f"{layer.name}: input glob(s) resolve to nothing: {empty}"
    assert sum(len(paths) for paths in resolved.values()) > 0


@pytest.mark.parametrize("layer", DL.LAYERS, ids=[one.name for one in DL.LAYERS])
def test_every_output_is_a_named_artifact_under_docs(layer):
    assert layer.outputs, f"{layer.name} declares no output"
    for rel in layer.outputs:
        assert not Path(rel).is_absolute() and rel.startswith("docs/")
        assert (ROOT / rel).parent.is_dir()
        if DL.stored_digest(ROOT, layer.name) is not None:   # it has been built in this checkout
            assert (ROOT / rel).is_file(), f"{layer.name}: {rel} is stamped but not on disk"


def test_no_two_layers_claim_the_same_artifact():
    seen: dict[str, str] = {}
    for layer in DL.LAYERS:
        for rel in layer.outputs:
            assert rel not in seen, f"{layer.name} and {seen[rel]} both write {rel}"
            seen[rel] = layer.name


def test_the_order_is_a_dependency_order_upstream_first():
    order = [one.name for one in DL.ordered()]
    assert set(order) == {one.name for one in DL.LAYERS} and len(order) == len(DL.LAYERS)
    for layer in DL.LAYERS:
        for dep in layer.depends_on:
            assert order.index(dep) < order.index(layer.name)
    # the edge the table's own order hides: docs/CAPABILITIES-INDEX.md is indexed by the docs index
    assert order.index("capabilities-index") < order.index("docs-index")


def test_an_upstream_artifact_is_an_input_of_its_dependents():
    patterns = {one.pattern for one in DL.inputs_of(DL.BY_NAME["docs-manifest"])}
    assert "docs/DOCS-INDEX.jsonl" in patterns          # the manifest folds the index
    animation = {one.pattern for one in DL.inputs_of(DL.BY_NAME["animation-registry"])}
    assert {"docs/DOCS-INDEX.jsonl", "docs/DOCS-CITATIONS.jsonl"} <= animation


def test_selection_pulls_in_the_upstream_and_nothing_else():
    assert [one.name for one in DL.selection(["docs-manifest"])] == [
        "capabilities-index", "docs-index", "docs-manifest"]
    assert [one.name for one in DL.selection("capabilities-index")] == ["capabilities-index"]
    with pytest.raises(KeyError):
        DL.selection(["no-such-layer"])


# --- the miniature repo ----------------------------------------------------------------------------

BUILDER = '''"""A fake builder: reads its inputs, writes its output, prints one line."""
import sys
from pathlib import Path

repo = Path(sys.argv[sys.argv.index("--repo") + 1])
name = Path(__file__).stem
src = sorted((repo / "src").glob("*.txt")) + sorted((repo / "docs").glob("*.jsonl"))
body = "".join(path.read_text(encoding="utf-8") for path in src if path.name != f"{name}.jsonl")
out = repo / "docs" / f"{name}.jsonl"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(body, encoding="utf-8")
with (repo / "builds.log").open("a", encoding="utf-8") as log:
    log.write(name + "\\n")
print(f"{name}: wrote {out.name}")
'''

FAILING = '''import sys
print("fake: starting")
print("fake: the input is malformed", file=sys.stderr)
sys.exit(2)
'''


@pytest.fixture()
def mini(tmp_path: Path):
    """A tree with two fake builders: `up` (the sentinel name) and `down`, which reads up's file."""
    scripts = tmp_path / DL.SCRIPTS_REL
    scripts.mkdir(parents=True)
    (scripts / DL.SENTINEL).write_text(BUILDER, encoding="utf-8")      # the "up" builder
    (scripts / "build_down.py").write_text(BUILDER, encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/one.txt").write_text("one\n", encoding="utf-8")
    up = DL.Layer("up", DL.SENTINEL, inputs=(DL.Input("src/*.txt"),),
                  outputs=(f"docs/{Path(DL.SENTINEL).stem}.jsonl",))
    down = DL.Layer("down", "build_down.py", inputs=(DL.Input("src/*.txt"),),
                    outputs=("docs/build_down.jsonl",), depends_on=("up",))
    return tmp_path, (up, down)


def builds(repo: Path) -> list[str]:
    log = repo / "builds.log"
    return log.read_text(encoding="utf-8").split() if log.is_file() else []


# --- the digest -------------------------------------------------------------------------------------

def test_the_digest_moves_when_an_input_file_changes(mini):
    repo, layers = mini
    before = DL.digest(layers[0], repo, layers=layers)
    assert DL.digest(layers[0], repo, layers=layers) == before        # deterministic
    (repo / "src/one.txt").write_text("one and a half\n", encoding="utf-8")
    assert DL.digest(layers[0], repo, layers=layers) != before


def test_the_digest_moves_when_an_input_file_appears(mini):
    repo, layers = mini
    before = DL.digest(layers[0], repo, layers=layers)
    (repo / "src/two.txt").write_text("two\n", encoding="utf-8")
    assert DL.digest(layers[0], repo, layers=layers) != before


def test_the_digest_moves_when_the_builder_itself_changes(mini):
    repo, layers = mini
    before = DL.digest(layers[0], repo, layers=layers)
    script = repo / DL.SCRIPTS_REL / DL.SENTINEL
    script.write_text(script.read_text(encoding="utf-8") + "# a comment\n", encoding="utf-8")
    assert DL.digest(layers[0], repo, layers=layers) != before


def test_the_digest_moves_when_an_upstream_artifact_changes(mini):
    repo, layers = mini
    up, down = layers
    (repo / "docs").mkdir(exist_ok=True)
    (repo / up.outputs[0]).write_text("built\n", encoding="utf-8")
    before = DL.digest(down, repo, layers=layers)
    assert DL.digest(up, repo, layers=layers) != before               # different layers, different digests
    (repo / up.outputs[0]).write_text("rebuilt\n", encoding="utf-8")
    assert DL.digest(down, repo, layers=layers) != before


def test_a_listing_input_is_not_hashed_but_still_notices_a_new_file(mini):
    repo, _ = mini
    tree = DL.Layer("tree", DL.SENTINEL, inputs=(DL.listing("src/**/*"),), outputs=("docs/t.jsonl",))
    body = DL.digest_body(tree, repo, layers=(tree,))
    fields = {line.split()[0]: line.split() for line in body.strip().splitlines()}
    assert fields["src/one.txt"][2].startswith("m")           # an mtime, not a 64-character sha
    assert len(fields[f"builder:{DL.SENTINEL}"][2]) == 64     # the builder itself IS hashed
    before = DL.digest(tree, repo, layers=(tree,))
    (repo / "src/two.txt").write_text("two\n", encoding="utf-8")
    assert DL.digest(tree, repo, layers=(tree,)) != before


# --- ensure -------------------------------------------------------------------------------------------

def test_ensure_is_a_no_op_on_a_fixture_tree_with_no_builders(tmp_path):
    """`test_docs_find.py` hand-writes layer records into a tmp tree; it must never be rebuilt."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/DOCS-INDEX.jsonl").write_text('{"path": "a.md"}\n', encoding="utf-8")
    assert DL.ensure(None, tmp_path) == []
    assert DL.ensure(["docs-index"], tmp_path) == []
    assert not (tmp_path / DL.CACHE_REL).exists()


def test_ensure_builds_once_then_not_again_then_again_after_a_touch(mini):
    repo, layers = mini
    scripts = repo / DL.SCRIPTS_REL

    assert DL.ensure(["up"], repo, scripts, layers=layers) == ["up"]
    assert builds(repo) == ["build_docs_index"]
    assert (repo / layers[0].outputs[0]).is_file()
    assert DL.digest_path(repo, "up").is_file()

    assert DL.ensure(["up"], repo, scripts, layers=layers) == []      # current: no build
    assert builds(repo) == ["build_docs_index"]

    (repo / "src/one.txt").write_text("changed\n", encoding="utf-8")
    assert DL.ensure(["up"], repo, scripts, layers=layers) == ["up"]
    assert builds(repo) == ["build_docs_index"] * 2


def test_ensure_rebuilds_a_downstream_layer_when_only_the_upstream_artifact_moved(mini):
    repo, layers = mini
    scripts = repo / DL.SCRIPTS_REL

    assert DL.ensure(None, repo, scripts, layers=layers) == ["up", "down"]   # upstream first
    assert DL.ensure(None, repo, scripts, layers=layers) == []

    (repo / layers[0].outputs[0]).write_text("someone edited the artifact\n", encoding="utf-8")
    assert DL.ensure(["down"], repo, scripts, layers=layers) == ["down"]
    assert builds(repo) == ["build_docs_index", "build_down", "build_down"]


def test_ensure_selecting_a_downstream_layer_builds_its_upstream_first(mini):
    repo, layers = mini
    scripts = repo / DL.SCRIPTS_REL
    assert DL.ensure(["down"], repo, scripts, layers=layers) == ["up", "down"]


def test_a_failing_builder_raises_LayerError_with_its_last_line(mini):
    repo, layers = mini
    scripts = repo / DL.SCRIPTS_REL
    (scripts / "build_down.py").write_text(FAILING, encoding="utf-8")

    with pytest.raises(DL.LayerError) as caught:
        DL.ensure(["down"], repo, scripts, layers=layers)

    assert caught.value.layer == "down"
    assert caught.value.detail == "fake: the input is malformed"
    assert not DL.digest_path(repo, "down").is_file()        # not stamped: the next call tries again
    assert DL.digest_path(repo, "up").is_file()              # the upstream that DID build is stamped


def test_a_layer_whose_builder_is_absent_is_skipped_not_failed(mini):
    repo, layers = mini
    scripts = repo / DL.SCRIPTS_REL
    (scripts / "build_down.py").unlink()
    assert DL.ensure(None, repo, scripts, layers=layers) == ["up"]


def test_stamp_writes_every_digest_without_building(mini):
    repo, layers = mini
    scripts = repo / DL.SCRIPTS_REL
    assert DL.stamp(None, repo, scripts, layers=layers) == ["up", "down"]
    assert builds(repo) == []
    assert DL.stale(None, repo, scripts, layers=layers) == []

def test_every_layer_output_is_build_output_ignored_and_untracked() -> None:
    """P63 T4 (2026-09-16): the layers are build output. Every output path is gitignored and none is tracked, so no
    commit can be blocked or conflicted by a generated layer; docs/DOCS-INDEX.config.json is an INPUT and stays tracked."""
    import subprocess
    repo = Path(__file__).resolve().parents[3]
    if not (repo / ".git").exists():
        pytest.skip("not a git checkout")
    outputs = [o for layer in DL.LAYERS for o in layer.outputs]
    ignored = subprocess.run(["git", "check-ignore", "--", *outputs], cwd=repo, capture_output=True, text=True)
    assert sorted(ignored.stdout.split()) == sorted(outputs), "an output is not ignored"
    tracked = subprocess.run(["git", "ls-files", "--", *outputs], cwd=repo, capture_output=True, text=True)
    assert tracked.stdout.strip() == "", f"tracked build output: {tracked.stdout}"
    cfg = subprocess.run(["git", "ls-files", "--", "docs/DOCS-INDEX.config.json"], cwd=repo, capture_output=True, text=True)
    assert cfg.stdout.strip() == "docs/DOCS-INDEX.config.json"


# --- the background refresh: the WRITE refreshes, the READ never rebuilds (P64 T1) ----------------

import json    # noqa: E402
import os      # noqa: E402
import subprocess  # noqa: E402
import time    # noqa: E402

# A stand-in for `build_docs_layers.py --ensure --then-recheck`: it sleeps for as long as the tree's
# `sleep.txt` says (so a test can catch it running), records the argv it was handed, prints the line a
# reader is meant to see, and removes the lock iff the lock is ITS OWN - the real child's contract.
FAKE_REFRESH = '''import json, os, sys, time
from pathlib import Path

repo = Path(sys.argv[sys.argv.index("--repo") + 1])
naptime = repo / "sleep.txt"
lock = repo / "docs/.layers/REBUILD.lock"
print("fake refresh: starting")
sys.stdout.flush()
held = json.loads(lock.read_text(encoding="utf-8"))          # the real child takes the lock over in
held["pid"] = os.getpid()                                    # its OWN pid: Popen's may be a shim's
lock.write_text(json.dumps(held), encoding="utf-8")
time.sleep(float(naptime.read_text(encoding="utf-8")) if naptime.is_file() else 0.0)
with (repo / "refreshes.log").open("a", encoding="utf-8") as log:
    log.write(" ".join(sys.argv[1:]) + "\\n")
print("build_docs_layers: rebuilt up")
try:
    if json.loads(lock.read_text(encoding="utf-8")).get("pid") == os.getpid():
        lock.unlink()
except OSError:
    pass
'''


@pytest.fixture()
def refreshable(mini):
    """The miniature repo plus a fake `build_docs_layers.py` for `refresh` to spawn, sleeping 3 s."""
    repo, layers = mini
    (repo / DL.SCRIPTS_REL / "build_docs_layers.py").write_text(FAKE_REFRESH, encoding="utf-8")
    (repo / "sleep.txt").write_text("3", encoding="utf-8")
    return repo, layers


def refreshes(repo: Path) -> list[str]:
    log = repo / "refreshes.log"
    return log.read_text(encoding="utf-8").splitlines() if log.is_file() else []


def wait_for(predicate, timeout: float = 25.0) -> bool:
    """Poll for what the detached child brings about; no test here ever sleeps blind."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.05)
    return False


def dead_pid() -> int:
    """A pid that is certainly not running: a process we started, waited for and reaped."""
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    return proc.pid


def test_refresh_starts_one_detached_child_and_writes_the_lock(refreshable):
    repo, layers = refreshable
    scripts = repo / DL.SCRIPTS_REL

    # Act
    state = DL.refresh(repo, ["up"], scripts, layers)

    # Assert: it returned AT ONCE with a pid, and the lock names that pid and what it is building
    assert state["stale"] == ["up"] and isinstance(state["started"], int)
    lock = json.loads((repo / DL.LOCK_REL).read_text(encoding="utf-8"))
    assert lock["pid"] == state["started"] and lock["names"] == ["up"] and lock["started"]
    assert DL.live_lock(repo) == lock
    assert refreshes(repo) == []                       # still sleeping: nothing was waited on here

    # Assert: the child really runs, takes the layers it was given, and removes its own lock
    assert wait_for(lambda: refreshes(repo))
    argv = refreshes(repo)[0]
    assert argv.startswith("--ensure --then-recheck --repo ") and argv.endswith(" --only up")
    assert wait_for(lambda: not (repo / DL.LOCK_REL).exists())
    assert DL.last_log_line(repo) == "build_docs_layers: rebuilt up"


def test_a_second_refresh_while_one_is_live_starts_nothing_and_reports_the_running_one(refreshable):
    repo, layers = refreshable
    scripts = repo / DL.SCRIPTS_REL
    DL.refresh(repo, ["up"], scripts, layers)

    # Act: the second write lands while the first refresh is still going
    second = DL.refresh(repo, ["up"], scripts, layers)

    # Assert: ONE refresh per checkout at a time
    assert second["started"] is None and second["stale"] == ["up"]
    assert second["running"]["names"] == ["up"]      # the one the first refresh is working on
    assert DL.pid_alive(second["running"]["pid"])
    assert wait_for(lambda: refreshes(repo))
    assert len(refreshes(repo)) == 1


def test_a_lock_whose_pid_is_dead_is_taken_over(refreshable):
    repo, layers = refreshable
    scripts = repo / DL.SCRIPTS_REL
    gone = dead_pid()
    DL.write_lock(repo, gone, ["up"])

    # Assert: a dead pid is not a live lock, so the next refresh takes it over
    assert not DL.pid_alive(gone) and DL.live_lock(repo) is None
    state = DL.refresh(repo, ["up"], scripts, layers)
    assert state["started"] not in (None, gone)
    assert json.loads((repo / DL.LOCK_REL).read_text(encoding="utf-8"))["pid"] == state["started"]
    assert wait_for(lambda: refreshes(repo))


def test_a_lock_older_than_ten_minutes_is_taken_over_even_with_a_live_pid(refreshable):
    repo, _ = refreshable
    old = {"pid": os.getpid(),                       # alive, certainly - it is this test
           "started": datetime.fromtimestamp(time.time() - DL.LOCK_MAX_AGE_S - 60).isoformat(
               timespec="seconds"),
           "names": ["up"]}
    (repo / DL.LOCK_REL).parent.mkdir(parents=True, exist_ok=True)
    (repo / DL.LOCK_REL).write_text(json.dumps(old), encoding="utf-8")

    # Assert
    assert DL.pid_alive(os.getpid()) and DL.read_lock(repo) == old
    assert DL.live_lock(repo) is None
    assert DL.lock_age_s(old) > DL.LOCK_MAX_AGE_S


def test_clear_lock_only_removes_our_own(refreshable):
    repo, _ = refreshable
    DL.write_lock(repo, 4242, ["up"])
    assert DL.clear_lock(repo, 99) is False and (repo / DL.LOCK_REL).exists()
    assert DL.clear_lock(repo, 4242) is True and not (repo / DL.LOCK_REL).exists()
    assert DL.clear_lock(repo, 4242) is False


def test_status_reports_the_stale_set_and_the_last_line_and_builds_nothing(refreshable):
    repo, layers = refreshable
    scripts = repo / DL.SCRIPTS_REL
    DL.log_path(repo).parent.mkdir(parents=True, exist_ok=True)
    DL.log_path(repo).write_text("fake refresh: starting\nbuild_docs_layers: rebuilt up\n",
                                 encoding="utf-8")

    # Act
    state = DL.status(repo, None, scripts, layers)

    # Assert: it answered, and nothing was built and no refresh was started
    assert state["stale"] == ["up", "down"] and state["running"] is None
    assert state["last_line"] == "build_docs_layers: rebuilt up"
    assert builds(repo) == [] and refreshes(repo) == [] and not (repo / DL.LOCK_REL).exists()


def test_the_readers_line_says_who_is_rebuilding_or_that_nobody_is():
    running = {"stale": ["docs-index"], "running": {"pid": 123, "started": "2026-09-16T21:04:11",
                                                    "names": ["docs-index"]}, "last_line": None}
    idle = {"stale": ["docs-index", "gates-registry"], "running": None, "last_line": None}
    failed = {**idle, "last_line": "build_docs_layers: FAILED to build gates-registry - boom"}

    assert DL.stale_note({"stale": [], "running": None, "last_line": "x"}) is None
    assert DL.stale_note(running) == ("[layers] stale: docs-index "
                                      "(a refresh is running, pid 123, started 21:04:11)")
    assert DL.stale_note(idle) == ("[layers] stale: docs-index, gates-registry "
                                   "(no refresh running - run build_docs_layers.py --refresh)")
    assert DL.stale_note(failed).endswith("; last: build_docs_layers: FAILED to build "
                                          "gates-registry - boom)")


def test_status_reuses_one_digest_pass_for_max_age_seconds(refreshable):
    """The player server's catalogue route asks on every GET; it must not hash the tree every time."""
    repo, layers = refreshable
    scripts = repo / DL.SCRIPTS_REL
    DL._STATUS_CACHE.clear()
    assert DL.status(repo, None, scripts, layers, max_age=30.0)["stale"] == ["up", "down"]

    # Act: build everything, then ask again inside the window and outside it
    DL.ensure(None, repo, scripts, layers=layers)
    assert DL.status(repo, None, scripts, layers, max_age=30.0)["stale"] == ["up", "down"]  # the memo
    assert DL.status(repo, None, scripts, layers)["stale"] == []                            # a fresh pass


def test_ensure_with_wait_false_hands_the_work_to_the_background(refreshable):
    repo, layers = refreshable
    scripts = repo / DL.SCRIPTS_REL

    # Act
    assert DL.ensure(["up"], repo, scripts, layers=layers, wait=False) == []

    # Assert: nothing was built in this process; a detached child has the lock
    assert builds(repo) == [] and DL.live_lock(repo) is not None
    assert wait_for(lambda: refreshes(repo))


def test_refresh_on_a_current_tree_starts_nothing(refreshable):
    repo, layers = refreshable
    scripts = repo / DL.SCRIPTS_REL
    DL.ensure(None, repo, scripts, layers=layers)

    # Act
    state = DL.refresh(repo, None, scripts, layers)

    # Assert
    assert state == {"stale": [], "started": None, "running": None}
    assert not (repo / DL.LOCK_REL).exists() and refreshes(repo) == []

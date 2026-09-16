"""The layers are build output: these pin the table, the digest and `ensure`.

Two halves. The first reads the REAL table against this checkout - every layer's input globs
resolve to files that are here, its outputs are named, and the declared dependencies really are a
dependency order - because an input glob that resolves to nothing is a builder input someone moved,
and an input that is MISSING from the table is worse: the layer would read as fresh while its
source changed, which is the exact lie the digest exists to prevent.

The second half builds a miniature repo in `tmp_path` with fake builders (a tiny script that reads
its inputs, writes its output and prints a line) and drives `ensure` over it: one rebuild, then
none, then one more after an input is touched; a failing builder raising `LayerError` with the
builder's own last line; and the dependency order - a downstream layer rebuilding when only its
upstream's artifact moved. No real builder runs here: those cost four minutes, and what is under
test is the table, not them.
"""
from __future__ import annotations

import sys
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

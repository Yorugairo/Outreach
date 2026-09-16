"""The layer table: what each docs layer READS, what it writes, and whether it is current.

The twelve retrieval layers are build output, not source. A layer is current when the digest of its
inputs - every file its builder actually reads, plus its upstream layers' artifacts, plus the
builder script itself - equals the digest stamped beside it in `docs/.layers/<name>.digest`
(gitignored). That makes "is this stale?" a question about the INPUTS, answered by hashing a few
megabytes, instead of a question answered by re-running twelve builders for 91 s.

    from docs_layers import LAYERS, digest, ensure
    ensure(["docs-index"], repo)        # rebuild it and its upstream iff their inputs moved
    ensure(None, repo)                  # the whole stack, in dependency order

Three rules the table obeys, because a wrong input is a lie in a different direction each way:

* Over-inclusion is cheap (a needless rebuild), under-inclusion is a LIE (a stale layer that reads
  as fresh), so every glob is a superset of what its builder reads, never a subset. Each tuple
  cites the builder line the root came from, so the next reader can check it against the source.
* A LISTING input (`listing(...)`) is a tree the builder reads the NAMES and stat of, never the
  bytes - `build_research_ledger.py:95-110` dates a run by its newest mtime. Its key is
  (path, size, mtime_ns): the 159 MB of `docs/research/runs/` cost 0.11 s instead of 0.96 s.
* `ensure` is a NO-OP on a tree with no builders in it (`content/video_engine/scripts/
  build_docs_index.py` absent). Every test fixture hand-writes its layer records into a `tmp_path`,
  and a fixture tree must never trigger a rebuild from the real repo.

Standard library only; the builders run as subprocesses of this interpreter, so they see the same
Python. Bytes are hashed exactly as they sit on disk (this repo's `.gitattributes` rewrites line
endings on checkout; the digest is local to the checkout, so that is the honest thing to compare).
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]

SCRIPTS_REL = "content/video_engine/scripts"
CACHE_REL = "docs/.layers"          # one `<name>.digest` per layer, gitignored: build output's receipt
LOCK_REL = "docs/.layers/REBUILD.lock"   # {pid, started, names} while ONE background refresh runs
LOG_REL = "docs/.layers/REBUILD.log"     # that refresh's stdout+stderr; its last line is what a reader prints
LOCK_MAX_AGE_S = 600.0              # a lock older than this is taken over, pid alive or not (P64 T1)
REFRESH_ROUNDS = 3                  # --then-recheck: at most three passes, then it stops and says so
LAST_LINE_CHARS = 140               # how much of a failing builder's last line a reader's ONE line carries
SENTINEL = "build_docs_index.py"    # no builders under SCRIPTS_REL => a fixture tree => ensure() is a no-op
REPORT_REL = "docs/DOCS-STANDARD.md"

GLOB_MAGIC = re.compile(r"[*?\[]")
CHUNK = 1 << 20


class LayerError(RuntimeError):
    """A builder exited non-zero during `ensure`. Carries the builder's own last output line."""

    def __init__(self, layer: str, detail: str) -> None:
        super().__init__(f"{layer}: {detail}")
        self.layer = layer
        self.detail = detail


# --- what a layer reads -------------------------------------------------------------------------

def matches(rel_path: str, pattern: str) -> bool:
    """`fnmatch` on a forward-slash path: `*` crosses `/`, a leading `**/` is optional, and a
    pattern with no glob magic also covers everything beneath it.

    Copied from `build_docs_index.py:391-399` on purpose - the exclusion rule of the index IS the
    exclusion rule of every layer that folds the index, so the two must not drift apart."""
    for pat in ((pattern, pattern[3:]) if pattern.startswith("**/") else (pattern,)):
        if fnmatch.fnmatchcase(rel_path, pat):
            return True
        if not GLOB_MAGIC.search(pat) and rel_path.startswith(pat.rstrip("/") + "/"):
            return True
    return False


@dataclass(frozen=True)
class Input:
    """One repo-relative glob (or literal path) a builder reads.

    `content=False` is a LISTING input: the builder reads names and stat, never the bytes."""
    pattern: str
    content: bool = True
    exclude: tuple[str, ...] = ()

    def paths(self, repo: Path, cache: dict | None = None) -> list[Path]:
        """Every existing file the pattern names, excluded patterns dropped, sorted.

        The `cache` is one run's memory: seven layers share `INDEXED_DOCS`, and walking the three
        roots once instead of seven times is most of the difference between 1.7 s and 0.6 s."""
        repo = Path(repo)
        key = ("paths", self.pattern, self.exclude, str(repo))
        if cache is not None and key in cache:
            return cache[key]
        pattern = self.pattern.replace("\\", "/").strip().rstrip("/")
        if not pattern:
            return []
        found = sorted(repo.glob(pattern)) if GLOB_MAGIC.search(pattern) else [repo / pattern]
        out: list[Path] = []
        for path in found:
            if not path.is_file():
                continue
            try:
                rel = path.relative_to(repo).as_posix()
            except ValueError:               # outside the repo: not addressable as an input
                continue
            if any(matches(rel, pat) for pat in self.exclude):
                continue
            out.append(path)
        if cache is not None:
            cache[key] = out
        return out


def listing(pattern: str, exclude: tuple[str, ...] = ()) -> Input:
    """A tree whose NAMES and mtimes the builder reads, not its bytes."""
    return Input(pattern, content=False, exclude=exclude)


@dataclass(frozen=True)
class Layer:
    """One tool in the stack, with what it reads and what it writes.

    `check_args` is None for a layer that only writes a report (it is still digested - the report
    goes stale like anything else); `repo_flag` is the flag that tool names the repository root
    with; `depends_on` names the upstream layers whose OUTPUTS are inputs of this one."""
    name: str
    script: str
    inputs: tuple[Input, ...] = ()
    outputs: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    write_args: tuple[str, ...] = ("--write",)
    check_args: tuple[str, ...] | None = ("--check",)
    repo_flag: str = "--repo"


# --- the shared doc corpus ----------------------------------------------------------------------
# `build_docs_index.py:40-45` names the defaults (roots `docs`, exclude `docs/research/runs/**` and
# `**/node_modules/**`); `docs/DOCS-INDEX.config.json` (its `CONFIG_REL`, :40) overrides them in this
# checkout with three roots and 29 exclusions. The config file is itself an input below, so a change
# to it rebuilds the index even before this copy of its exclusions is updated.
DOC_EXCLUDE = (
    "docs/research/runs/**",                      # build_docs_index.py:42 DEFAULT_EXCLUDE
    "**/node_modules/**",
    CACHE_REL + "/**",                            # this cache - never an input to anything
    # the generated twins, from the config's exclude list (DOCS-INDEX.* is dropped by the tool
    # itself, build_docs_index.py:406-409). CAPABILITIES-INDEX.md is deliberately NOT here: the
    # config does not exclude it, so the index really does index it - the docs-index ->
    # capabilities-index edge in `depends_on` below.
    "docs/DOCS-INDEX.md", "docs/DOCS-MANIFEST.md", "docs/DOCS-TOPICS.md", "docs/DOCS-STANDARD.md",
    "docs/GATES-REGISTRY.md", "docs/ANIMATION-REGISTRY.md", "docs/CRAFT-MAP.md",
    "docs/DOC-OVERLAP.md", "docs/EFFECTS-CATALOG.md", "docs/RESEARCH-LEDGER.md",
    "docs/ASSETS-INDEX.md",
    # the projects tree's own build output, from the config's exclude list
    "content/video_engine/projects/**/build-*/**",
    "content/video_engine/projects/**/*-GATES.md",
    "content/video_engine/projects/**/*-SCREENS.md",
    "content/video_engine/projects/**/*-VIEWER*.md",
    "content/video_engine/projects/**/vo*/**",
    "content/video_engine/projects/**/omni-video/**",
    "content/video_engine/projects/**/plates/**",
    "content/video_engine/projects/**/review/**",
)

# The indexed corpus: the three roots of `docs/DOCS-INDEX.config.json`, walked for `*.md`
# (`build_docs_index.py:425-435` candidate_files -> `rglob("*.md")`). Every layer that folds the
# index also opens the documents themselves, so they share this tuple.
INDEXED_DOCS = (
    Input("docs/**/*.md", exclude=DOC_EXCLUDE),
    Input("content/video_engine/sources/reference_analyses/**/*.md", exclude=DOC_EXCLUDE),
    Input("content/video_engine/projects/**/*.md", exclude=DOC_EXCLUDE),
    Input("docs/DOCS-INDEX.config.json"),                       # build_docs_index.py:40 CONFIG_REL
)

# The four documents a gate id may cite (build_gates_registry.py:315-318).
GATE_DOCS = (
    Input("docs/content-video-engine/patterns/FULL-VIDEO-MAP.md"),
    Input("docs/content-video-engine/patterns/phase-guides/*.md"),
    Input("docs/portable/OPERATOR-RULINGS.md"),
    Input("docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md"),
)

# The documents an effect card's `doctrine` cite may name (build_effects_catalog.py:73-84).
CARD_DOCS = (
    Input("docs/content-video-engine/CAPABILITIES.md"),
    Input("docs/content-video-engine/BACKLOG.md"),
    Input("docs/content-video-engine/SPECIES-BY-SENTENCE.md"),
    Input("docs/portable/MOTION-GRAMMAR.md"),
    Input("docs/content-video-engine/patterns/SHORT-FORM-SHAPE.md"),
    Input("docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md"),
    Input("docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md"),
    Input("docs/agent-memory/operator/*.md"),                   # build_effects_catalog.py:84 MEMORY_REL
)


LAYERS = (
    Layer("docs-index", "build_docs_index.py",
          inputs=INDEXED_DOCS,
          outputs=("docs/DOCS-INDEX.jsonl", "docs/DOCS-INDEX.md"),
          # docs/CAPABILITIES-INDEX.md is NOT in the config's exclude list, so the index indexes it:
          # a real edge the table's order hides (the wrapper runs the index first).
          depends_on=("capabilities-index",)),
    Layer("capabilities-index", "build_capabilities_index.py",
          # build_capabilities_index.py:35 CAP_REL, :328 - one document, parsed; nothing else is read
          inputs=(Input("docs/content-video-engine/CAPABILITIES.md"),),
          outputs=("docs/CAPABILITIES-INDEX.jsonl", "docs/CAPABILITIES-INDEX.md")),
    Layer("asset-index", "build_asset_index.py",
          inputs=(Input("content/video_engine/assets/*/manifest.json"),     # :48-52, :72-77 catalog_files
                  Input("content/video_engine/assets/*/*catalog*.json"),
                  Input("content/video_engine/assets/*/CATALOGUE.md"),      # :92-96 catalogue_rows
                  Input("content/video_engine/assets/*/SOURCES.md"),        # :198-202 glyph_records
                  Input("content/video_engine/assets/*/*.svg"),             # :198-212 the glyph bytes are hashed into the record
                  listing("content/video_engine/assets/**/*")),             # asset_record: `on_disk` is the listing
          outputs=("docs/ASSETS-INDEX.jsonl", "docs/ASSETS-INDEX.md")),
    Layer("research-ledger", "build_research_ledger.py",
          inputs=(listing("docs/research/runs/**/*"),                       # :95-110 run_files + newest_date: names and mtimes
                  Input("docs/content-video-engine/BACKLOG.md"),            # :42, :113-124
                  Input(".claude/PRPs/plans/*.md"),                         # :43, :126-129
                  Input("docs/**/*.md", exclude=DOC_EXCLUDE),               # :44, :131-136 every doc that can cite a run
                  Input("docs/DOCS-INDEX.config.json")),                    # :45, :70-75 generated_docs reads the config
          outputs=("docs/RESEARCH-LEDGER.jsonl", "docs/RESEARCH-LEDGER.md")),
    Layer("effects-catalog", "build_effects_catalog.py",
          inputs=(Input("content/video_engine/effects/cards/*.json"),       # :52, :119
                  Input("content/video_engine/effects/recipes/*.json"),     # :53, :163
                  Input("content/video_engine/configs/effect_card.schema.json"),    # :54, :116
                  Input("content/video_engine/configs/effect_recipe.schema.json"),  # :55, :160
                  Input(f"{SCRIPTS_REL}/build_scene_timeline_f.py"),        # :60 COMPILER - the pulled `when` tables, :212
                  Input(f"{SCRIPTS_REL}/kinetics/*.mjs"),                   # :271-277 dial_values reads the card's own module
                  Input(f"{SCRIPTS_REL}/species/*.mjs"),                    # (the cards name both directories)
                  Input(f"{SCRIPTS_REL}/build_animation_registry.py"),      # :270 the object-literal parser it imports
                  Input(f"{SCRIPTS_REL}/animation_registry_chain.py"),
                  Input(f"{SCRIPTS_REL}/build_gates_registry.py"),          # :264 BGR.CITE_RE / BGR._resolve
                  *CARD_DOCS),
          outputs=("docs/EFFECTS-CATALOG.jsonl", "docs/EFFECTS-CATALOG.md"),
          depends_on=("docs-index",)),                                      # :278-282 cites resolve through the index
    Layer("docs-manifest", "build_docs_manifest.py",
          inputs=INDEXED_DOCS,                                              # :75-77, :488 reads every document head
          outputs=("docs/DOCS-MANIFEST.jsonl", "docs/DOCS-MANIFEST.md"),
          depends_on=("docs-index",)),
    Layer("topic-index", "build_topic_index.py",
          inputs=INDEXED_DOCS,                                              # :34-37, :286 reads every document text
          outputs=("docs/DOCS-TOPICS.jsonl", "docs/DOCS-TOPICS.md", "docs/DOCS-CITATIONS.jsonl"),
          depends_on=("docs-index",)),
    Layer("gates-registry", "build_gates_registry.py",
          inputs=(Input(f"{SCRIPTS_REL}/gate_*.py"),                        # :56, :66-73 FAMILY, :508 parsed by ast
                  Input(f"{SCRIPTS_REL}/audit_script_doctrine.py"),
                  Input(f"{SCRIPTS_REL}/lint_script_pattern.py"),
                  Input(f"{SCRIPTS_REL}/viewer_score.py"),
                  Input(f"{SCRIPTS_REL}/run_script_gates.py"),              # :76 RUNNER - the Composition block
                  Input(f"{SCRIPTS_REL}/build_topic_index.py"),             # the resolver it imports
                  Input("content/video_engine/tests/**/*.py"),              # :57, :417-422 tests rglob("*.py")
                  *GATE_DOCS),
          outputs=("docs/GATES-REGISTRY.jsonl", "docs/GATES-REGISTRY.md"),
          depends_on=("docs-index",)),                                      # :58, :322-325
    Layer("animation-registry", "build_animation_registry.py",
          inputs=(Input(f"{SCRIPTS_REL}/kinetics/*.mjs"),                   # :69, :182 Corpus.modules
                  Input("docs/content-video-engine/samples/scene-evidence-engine.mjs"),  # :70 TEMPLATE_REL, :183-188
                  Input("content/video_engine/tests/**/*.py"),              # :71, :189-192 tests, suffix .py/.mjs/.js
                  Input("content/video_engine/tests/**/*.mjs"),
                  Input("content/video_engine/tests/**/*.js"),
                  Input(f"{SCRIPTS_REL}/gate_*.py"),                        # :193-194 Corpus.gates
                  Input(f"{SCRIPTS_REL}/animation_registry_chain.py"),      # the chain / render halves it imports
                  Input(f"{SCRIPTS_REL}/animation_registry_render.py"),
                  Input(f"{SCRIPTS_REL}/build_topic_index.py"),
                  # animation_registry_chain.py:31-36 (DOCS_DIR rows, RESEARCH-INDEX, EXTRA_DOCS) and
                  # :204-213 formula_files (docs 29 and 42-53, the finding, the brief, the reference analyses)
                  Input("docs/content-video-engine/**/*.md", exclude=DOC_EXCLUDE),
                  Input("content/video_engine/sources/reference_analyses/**/*.md")),
          outputs=("docs/ANIMATION-REGISTRY.jsonl", "docs/ANIMATION-REGISTRY.md"),
          depends_on=("docs-index", "topic-index")),                        # :67-68 INDEX_REL + CITATIONS_REL
    Layer("craft-map", "build_craft_map.py",
          inputs=(Input("docs/content-video-engine/patterns/CRAFT-DEVICES.md"),  # :57 SEED_REL, :209
                  *INDEXED_DOCS),                                           # :319 the exemplar is found in its own document
          outputs=("docs/CRAFT-MAP.jsonl", "docs/CRAFT-MAP.md"),
          depends_on=("docs-index", "gates-registry")),                     # :58-59 GATES_REL + DOCS_INDEX_REL
    Layer("doc-overlap", "report_doc_overlap.py",
          inputs=(Input("AGENTS.md"),                                       # :77 AGENTS_REL
                  Input(f"{SCRIPTS_REL}/build_docs_index.py"),              # it imports BDI line splitting
                  *INDEXED_DOCS),                                           # :346, :581 reads each document
          outputs=("docs/DOC-OVERLAP.jsonl", "docs/DOC-OVERLAP.md"),
          depends_on=("docs-index",)),                                      # :76 INDEX_REL
    Layer("docs-standard", "audit_docs_standard.py",
          inputs=INDEXED_DOCS,                                              # :43-44, :141-152 reads each document
          outputs=(REPORT_REL,),
          depends_on=("docs-index",),
          write_args=("--report", REPORT_REL), check_args=None, repo_flag="--root"),
)

BY_NAME = {layer.name: layer for layer in LAYERS}


# --- the subprocess boundary --------------------------------------------------------------------

def run_script(script: Path, args: tuple[str, ...], repo: Path) -> tuple[int, str]:
    """(exit code, combined output) of the tool, run by this interpreter from the repo root."""
    proc = subprocess.run([sys.executable, str(script), *args], cwd=str(repo),
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def last_line(output: str) -> str:
    """The tool's own summary - its last non-empty line - or a stand-in when it printed nothing."""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[-1] if lines else "(no output)"


def script_path(layer: Layer, scripts_dir: Path = SCRIPTS) -> Path:
    return Path(scripts_dir) / layer.script


def scripts_of(repo: Path, scripts_dir: Path | None = None) -> Path:
    """Where this repository builders live - the caller may override for a fixture tree."""
    return Path(scripts_dir) if scripts_dir is not None else Path(repo) / SCRIPTS_REL


def has_builders(repo: Path, scripts_dir: Path | None = None) -> bool:
    """False for a tree with no builders in it: a fixture, which `ensure` must never rebuild."""
    return (scripts_of(repo, scripts_dir) / SENTINEL).is_file()


# --- the digest ----------------------------------------------------------------------------------

def file_key(path: Path, rel: str, content: bool, cache: dict | None = None) -> str:
    """One line of the digest body: `<relative path> <size> <sha256 | mtime_ns>`.

    Cached for the run, so a file that feeds seven layers is opened and hashed once. `ensure`
    clears the cache after every build, because a build rewrites files."""
    key = ("key", str(path), rel, content)
    if cache is not None and key in cache:
        return cache[key]
    stat = path.stat()
    if content:
        sha = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(CHUNK), b""):
                sha.update(chunk)
        line = f"{rel} {stat.st_size} {sha.hexdigest()}"
    else:
        line = f"{rel} {stat.st_size} m{stat.st_mtime_ns}"
    if cache is not None:
        cache[key] = line
    return line


def inputs_of(layer: Layer, layers: tuple[Layer, ...] = LAYERS) -> tuple[Input, ...]:
    """The layer own globs PLUS every direct upstream layer artifacts."""
    by_name = {one.name: one for one in layers}
    upstream = tuple(Input(out) for dep in layer.depends_on
                     for out in by_name[dep].outputs)
    return (*layer.inputs, *upstream)


def digest_body(layer: Layer, repo: Path, scripts_dir: Path | None = None,
                cache: dict | None = None,
                layers: tuple[Layer, ...] = LAYERS) -> str:
    """The sorted `path size hash` lines the digest hashes - the readable form, for a diff."""
    repo = Path(repo).resolve()
    seen: set[str] = set()
    entries: list[str] = []
    for one in inputs_of(layer, layers):
        for path in one.paths(repo, cache):
            rel = path.relative_to(repo).as_posix()
            if rel in seen:
                continue
            seen.add(rel)
            entries.append(file_key(path, rel, one.content, cache))
    script = script_path(layer, scripts_of(repo, scripts_dir))
    if script.is_file():                          # the builder itself: its code decides the output
        entries.append(file_key(script, f"builder:{layer.script}", True, cache))
    return "\n".join(sorted(entries)) + "\n"


def digest(layer: Layer | str, repo: Path = REPO, scripts_dir: Path | None = None,
           cache: dict | None = None, layers: tuple[Layer, ...] = LAYERS) -> str:
    """sha256 over every input file of the layer: (relative path, size, content sha256), sorted."""
    one = BY_NAME[layer] if isinstance(layer, str) else layer
    body = digest_body(one, repo, scripts_dir, cache, layers)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def digest_path(repo: Path, name: str) -> Path:
    return Path(repo) / CACHE_REL / f"{name}.digest"


def stored_digest(repo: Path, name: str) -> str | None:
    """The digest the layer was last built from, or None when it has never been built here."""
    path = digest_path(repo, name)
    try:
        return path.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def write_digest(repo: Path, name: str, value: str) -> Path:
    """Stamp the digest beside the layer (LF, no BOM). The cache directory is gitignored."""
    path = digest_path(repo, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((value + "\n").encode("utf-8"))
    return path


# --- the order -----------------------------------------------------------------------------------

def ordered(layers: tuple[Layer, ...] = LAYERS) -> list[Layer]:
    """The table in dependency order, upstream first; the table own order breaks every tie."""
    by_name = {one.name: one for one in layers}
    out: list[Layer] = []
    done: set[str] = set()

    def visit(one: Layer, stack: tuple[str, ...]) -> None:
        if one.name in done:
            return
        if one.name in stack:
            raise ValueError(f"docs_layers: dependency cycle {' -> '.join((*stack, one.name))}")
        for dep in one.depends_on:
            if dep not in by_name:
                raise ValueError(f"docs_layers: {one.name} depends on unknown layer {dep!r}")
            visit(by_name[dep], (*stack, one.name))
        done.add(one.name)
        out.append(one)

    for one in layers:
        visit(one, ())
    return out


def selection(names, layers: tuple[Layer, ...] = LAYERS) -> list[Layer]:
    """The named layers plus everything they depend on, in dependency order; None means all."""
    if names is None:
        return ordered(layers)
    if isinstance(names, str):
        names = [names]
    wanted = set(names)
    by_name = {one.name: one for one in layers}
    unknown = sorted(wanted - set(by_name))
    if unknown:
        raise KeyError(f"docs_layers: unknown layer(s) {', '.join(unknown)}")
    frontier = list(wanted)
    while frontier:                                # pull in the upstream, transitively
        one = by_name[frontier.pop()]
        for dep in one.depends_on:
            if dep not in wanted:
                wanted.add(dep)
                frontier.append(dep)
    return [one for one in ordered(layers) if one.name in wanted]


# --- is it current, and make it so ----------------------------------------------------------------

def is_current(layer: Layer, repo: Path, scripts_dir: Path | None = None,
               cache: dict | None = None,
               layers: tuple[Layer, ...] = LAYERS) -> bool:
    """True when the stamped digest equals the digest of the inputs as they are on disk now."""
    stored = stored_digest(repo, layer.name)
    return stored is not None and stored == digest(layer, repo, scripts_dir, cache, layers)


def stale(names=None, repo: Path = REPO, scripts_dir: Path | None = None,
          layers: tuple[Layer, ...] = LAYERS) -> list[str]:
    """Every selected layer whose builder is in this checkout and whose digest is not current."""
    repo = Path(repo).resolve()
    scripts = scripts_of(repo, scripts_dir)
    cache: dict = {}
    return [one.name for one in selection(names, layers)
            if script_path(one, scripts).is_file()
            and not is_current(one, repo, scripts, cache, layers)]


def ensure(names=None, repo: Path = REPO, scripts_dir: Path | None = None,
           layers: tuple[Layer, ...] = LAYERS, wait: bool = True) -> list[str]:
    """Rebuild every selected layer whose inputs moved, upstream first; return what was rebuilt.

    A no-op returning [] on a tree with no builders (a fixture). A builder that exits non-zero
    raises `LayerError` carrying its last output line - the digest is NOT stamped, so the next
    call tries again.

    `wait=True` (the default, and the only behaviour before P64 T1) BLOCKS until every stale layer
    is rebuilt: the caller that must be current - a record slice, a strict gate, a test. `wait=False`
    hands the work to `refresh` (one detached builder behind a lock) and returns [] at once, because
    nothing HAS been rebuilt by the time it returns."""
    if not wait:
        refresh(repo, names, scripts_dir, layers)
        return []
    repo = Path(repo).resolve()
    scripts = scripts_of(repo, scripts_dir)
    if not has_builders(repo, scripts):
        return []
    cache: dict = {}
    rebuilt: list[str] = []
    for one in selection(names, layers):
        script = script_path(one, scripts)
        if not script.is_file():                   # a layer this checkout has not grown yet
            continue
        if is_current(one, repo, scripts, cache, layers):
            continue
        code, output = run_script(script, (*one.write_args, one.repo_flag, str(repo)), repo)
        if code != 0:
            raise LayerError(one.name, last_line(output))
        cache.clear()                              # the build rewrote files: every hash may be stale
        write_digest(repo, one.name, digest(one, repo, scripts, cache, layers))
        rebuilt.append(one.name)
    return rebuilt


def stamp(names=None, repo: Path = REPO, scripts_dir: Path | None = None,
          layers: tuple[Layer, ...] = LAYERS) -> list[str]:
    """Stamp the current digest of every selected layer whose builder is here (after a --write)."""
    repo = Path(repo).resolve()
    scripts = scripts_of(repo, scripts_dir)
    cache: dict = {}
    done: list[str] = []
    for one in selection(names, layers):
        if not script_path(one, scripts).is_file():
            continue
        write_digest(repo, one.name, digest(one, repo, scripts, cache, layers))
        done.append(one.name)
    return done


# --- the background refresh: the WRITE refreshes, the READ never rebuilds (P64 T1) ----------------
#
# The rule the operator set: "can't we move to a system where the agents are able to keep progressing
# while the system updates" and "i think docs_find doesnt need to rebuild the stale layer every
# answer". So `ensure` - blocking, and minutes of it after a CAPABILITIES edit - is off the read path.
# A WRITE calls `refresh`, which starts ONE detached builder behind `docs/.layers/REBUILD.lock`; a
# READ calls `status`, which hashes the inputs (0.6 s over the whole stack here) and never builds.
# Every checkout - every worktree - carries its own `docs/.layers/`, so a refresh in one never
# touches another.

def lock_path(repo: Path) -> Path:
    return Path(repo) / LOCK_REL


def log_path(repo: Path) -> Path:
    return Path(repo) / LOG_REL


def read_lock(repo: Path) -> dict | None:
    """The lock as it sits, or None when there is none (or it is not the JSON object we wrote)."""
    try:
        data = json.loads(lock_path(repo).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) and isinstance(data.get("pid"), int) else None


def pid_alive(pid: int) -> bool:
    """Is that process still running? Stdlib only, and never a signal on Windows.

    `os.kill(pid, 0)` on Windows does NOT probe - it calls TerminateProcess with the signal as the
    exit code, i.e. it would KILL the very refresh we are asking about - so Windows goes through
    OpenProcess / GetExitCodeProcess by ctypes instead."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        import ctypes                                    # Windows only, and only here
        PROCESS_QUERY_LIMITED_INFORMATION, STILL_ACTIVE = 0x1000, 259
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            ok = kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
            return bool(ok) and code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:                              # someone else's process: alive, not ours
        return True
    return True


def lock_age_s(lock: dict) -> float | None:
    """Seconds since the lock was written, by its own ISO `started`; None when that is unreadable."""
    try:
        return max(0.0, time.time() - datetime.fromisoformat(str(lock.get("started"))).timestamp())
    except (TypeError, ValueError):
        return None


def live_lock(repo: Path) -> dict | None:
    """The lock of a refresh that is really running, or None - a lock whose pid is dead or that is
    older than ten minutes is TAKEN OVER, so a crashed or killed builder wedges nothing."""
    lock = read_lock(repo)
    if lock is None:
        return None
    age = lock_age_s(lock)
    if age is not None and age > LOCK_MAX_AGE_S:
        return None
    return lock if pid_alive(lock["pid"]) else None


def write_lock(repo: Path, pid: int, names) -> dict:
    """Stamp {pid, started, names} beside the layers and return it."""
    lock = {"pid": int(pid), "started": datetime.now().isoformat(timespec="seconds"),
            "names": list(names or [])}
    path = lock_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(lock) + "\n", encoding="utf-8")
    return lock


def clear_lock(repo: Path, pid: int | None = None) -> bool:
    """Remove the lock - only if it is OURS when `pid` is given. True when one was removed."""
    lock = read_lock(repo)
    if lock is None or (pid is not None and lock.get("pid") != pid):
        return False
    try:
        lock_path(repo).unlink()
    except OSError:
        return False
    return True


def last_log_line(repo: Path) -> str | None:
    """The refresh log's last non-empty line - the builder's own summary, for the next reader."""
    try:
        text = log_path(repo).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else None


def start_refresh(repo: Path, names, scripts_dir: Path | None = None) -> int | None:
    """Start ONE detached `build_docs_layers.py --ensure --only ... --then-recheck`; return its pid.

    Detached on purpose: it must outlive the hook, the CLI or the reader that started it. Its stdout
    and stderr go to `docs/.layers/REBUILD.log`, truncated per refresh so the last line is THIS
    refresh's. The lock is written immediately after the spawn - the child needs ~150 ms to boot
    before it could possibly clear it, and if it ever won that race the lock's pid would then be
    dead, which the next `live_lock` takes over. None when this checkout has no builder to run."""
    repo = Path(repo).resolve()
    script = scripts_of(repo, scripts_dir) / "build_docs_layers.py"
    if not script.is_file():
        return None
    log = log_path(repo)
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(script), "--ensure", "--then-recheck", "--repo", str(repo)]
    if names:
        cmd += ["--only", ",".join(names)]
    kwargs: dict = {}
    if os.name == "nt":
        DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP = 0x00000008, 0x00000200
        kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    handle = log.open("wb")
    try:
        proc = subprocess.Popen(cmd, cwd=str(repo), stdin=subprocess.DEVNULL, stdout=handle,
                                stderr=subprocess.STDOUT, close_fds=True, **kwargs)
    finally:
        handle.close()
    write_lock(repo, proc.pid, names)
    return proc.pid


def refresh(repo: Path = REPO, names=None, scripts_dir: Path | None = None,
            layers: tuple[Layer, ...] = LAYERS) -> dict:
    """Start a background rebuild of whatever is stale and RETURN AT ONCE. Never raises.

    `{"stale": [...], "started": pid | None, "running": {pid, started, names} | None}`. ONE refresh
    per checkout at a time: when one is already live the stale set is not re-hashed - that is the
    running child's `--then-recheck` job, and this sits on a write hook's path, where it must cost
    nothing - so the set reported is the one that refresh is working on.

    Note the argument order: `repo` FIRST, unlike `ensure` / `stale` / `stamp`, because a caller of
    this one almost never names layers; it says "this checkout was written to, get on with it"."""
    repo = Path(repo).resolve()
    scripts = scripts_of(repo, scripts_dir)
    running = live_lock(repo)
    if running is not None:
        return {"stale": list(running.get("names") or []), "started": None, "running": running}
    behind = stale(names, repo, scripts, layers)
    if not behind:
        return {"stale": [], "started": None, "running": None}
    pid = start_refresh(repo, behind, scripts)
    return {"stale": behind, "started": pid, "running": read_lock(repo) if pid else None}


_STATUS_CACHE: dict = {}          # (repo, names) -> (monotonic stamp, stale names): the TTL memo


def status(repo: Path = REPO, names=None, scripts_dir: Path | None = None,
           layers: tuple[Layer, ...] = LAYERS, max_age: float | None = None) -> dict:
    """What a READER is allowed to know: `{"stale": [...], "running": {...} | None, "last_line": str | None}`.

    It NEVER builds and never starts anything. The stale set costs one digest pass (0.6 s over the
    whole stack on this repo); a long-lived reader answering the same question on every request
    passes `max_age` to reuse the last pass for that many seconds - the lock and the log are re-read
    every time either way, being two small files."""
    repo = Path(repo).resolve()
    scripts = scripts_of(repo, scripts_dir)
    key = (str(repo), None if names is None else tuple(sorted(
        [names] if isinstance(names, str) else names)))
    cached = _STATUS_CACHE.get(key)
    if max_age is not None and cached is not None and (time.monotonic() - cached[0]) < max_age:
        behind = cached[1]
    else:
        behind = stale(names, repo, scripts, layers)
        _STATUS_CACHE[key] = (time.monotonic(), behind)
    return {"stale": behind, "running": live_lock(repo), "last_line": last_log_line(repo)}


def stale_note(state: dict) -> str | None:
    """The ONE line a reader prints when a layer it just read is behind - None when none is.

    `[layers] stale: a, b (a refresh is running, pid 123, started 21:04:11)`, or `... (no refresh
    running - run build_docs_layers.py --refresh)`; when the last refresh FAILED, its own last line
    is carried along, because the reader after a failure is the one who needs to see why."""
    behind = state.get("stale") or []
    if not behind:
        return None
    running = state.get("running")
    if running:
        started = str(running.get("started") or "")
        clock = started.split("T")[-1] or started
        note = f"a refresh is running, pid {running.get('pid')}, started {clock}"
    else:
        note = "no refresh running - run build_docs_layers.py --refresh"
        last = state.get("last_line") or ""
        if "FAILED" in last:                     # a builder's own line runs to hundreds of characters
            note += f"; last: {last[:LAST_LINE_CHARS]}" + ("..." if len(last) > LAST_LINE_CHARS else "")
    return f"[layers] stale: {', '.join(behind)} ({note})"


def report_stale(repo: Path = REPO, names=None, scripts_dir: Path | None = None,
                 layers: tuple[Layer, ...] = LAYERS, stream=None,
                 max_age: float | None = None) -> str | None:
    """Print `stale_note` on stderr - stdout is the answer, and a recall receipt quotes stdout."""
    note = stale_note(status(repo, names, scripts_dir, layers, max_age))
    if note:
        print(note, file=stream if stream is not None else sys.stderr)
    return note

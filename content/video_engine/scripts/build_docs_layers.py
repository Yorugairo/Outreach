"""One command for the whole docs retrieval stack: build every layer, or prove none is stale.

The layers are separate tools on purpose - each owns one artifact - but they are ordered: the
manifest, the topic index and the gates registry all read `docs/DOCS-INDEX.jsonl`, so a docs pass
that rebuilds one and forgets the next ships a stale layer that still looks fresh. This runs them
in dependency order, in one process tree, and prints one summary line per layer.

    python content/video_engine/scripts/build_docs_layers.py --check   # digests: exit 1 on the first stale
    python content/video_engine/scripts/build_docs_layers.py --ensure  # rebuild only what went stale (BLOCKS)
    python content/video_engine/scripts/build_docs_layers.py --refresh # start that rebuild in the BACKGROUND, return now
    python content/video_engine/scripts/build_docs_layers.py --status  # who is rebuilding what, and the last line
    python content/video_engine/scripts/build_docs_layers.py --write   # regenerate everything, then re-check

Since P64 T1 the WRITE refreshes and the READ never rebuilds. `--refresh` is what a write hook (Edit,
Write, a commit) calls: it returns at once, having started ONE detached `--ensure --then-recheck`
behind `docs/.layers/REBUILD.lock` with its output in `docs/.layers/REBUILD.log`, or having found one
already running. `--then-recheck` is the child's own flag: when its pass ends it re-computes the stale
set and goes again if a write landed while it was building, at most REFRESH_ROUNDS times, then stops
and says so. Readers (`docs_find.py` and the five runtime readers) only ever call `docs_layers.status`.

The table itself - what each layer reads, what it writes, what it depends on - lives in
`docs_layers.py`, because the readers (`docs_find.py` and the runtime readers) ensure their own
layers from it. Three passes, three different questions:

* `--check` asks the DIGEST question: for every layer, is the sha256 of its inputs (the files its
  builder reads, its upstream layers' artifacts, and the builder script) the one stamped in
  `docs/.layers/<name>.digest`? No builder runs; the whole pass is under 2 s.
* `--ensure` rebuilds exactly the layers whose digest moved, upstream first (`docs_layers.ensure`).
* `--write` is unchanged: every builder, in the table's order, then the byte `--check` pass each
  tool implements, and then every digest is stamped from what is now on disk.

    | order | layer          | tool                    | artifact                            |
    |-------|----------------|-------------------------|-------------------------------------|
    | 1     | docs-index     | build_docs_index.py     | docs/DOCS-INDEX.jsonl + .md         |
    | 1     | capabilities-index | build_capabilities_index.py | docs/CAPABILITIES-INDEX.jsonl + .md (docs_find searches it first) |
    | 1     | asset-index    | build_asset_index.py    | docs/ASSETS-INDEX.jsonl + .md (props, icons, glyphs; searched second) |
    | 2     | research-ledger | build_research_ledger.py | docs/RESEARCH-LEDGER.jsonl + .md (the ingestion gate) |
    | 2     | effects-catalog | build_effects_catalog.py | docs/EFFECTS-CATALOG.jsonl + .md (cites via the index) |
    | 3     | docs-manifest  | build_docs_manifest.py  | docs/DOCS-MANIFEST.jsonl + .md      |
    | 4     | topic-index    | build_topic_index.py    | docs/DOCS-TOPICS.* + DOCS-CITATIONS |
    | 5     | gates-registry | build_gates_registry.py | docs/GATES-REGISTRY.jsonl + .md     |
    | 6     | animation-registry | build_animation_registry.py | docs/ANIMATION-REGISTRY.jsonl + .md |
    | 7     | craft-map      | build_craft_map.py      | docs/CRAFT-MAP.jsonl + .md          |
    | 8     | doc-overlap    | report_doc_overlap.py   | docs/DOC-OVERLAP.jsonl + .md        |
    | 8     | docs-standard  | audit_docs_standard.py  | docs/DOCS-STANDARD.md               |

A tool that is not in the tree yet is SKIPPED with a printed note, never silently: the stack grows
a layer at a time and a missing script is a fact about this checkout, not a failure. The audit
writes a report rather than a checkable artifact, so its TOOL runs in `--write` only - its digest
is checked like everyone else's. Standard library only; every tool runs as a subprocess of this
interpreter, so it sees the same Python.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from docs_layers import (  # noqa: E402  (the table and the digest live there; the readers share them)
    LAYERS, REFRESH_ROUNDS, REPORT_REL, Layer, LayerError, clear_lock, digest, ensure, last_line,
    last_log_line, live_lock, lock_path, log_path, read_lock, refresh, run_script, script_path,
    stale, stamp, stored_digest, write_lock)

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]


def run_layer(layer: Layer, args: tuple[str, ...], repo: Path, scripts_dir: Path) -> tuple[int, str]:
    """The tool, told which repository root it is working on in its own flag."""
    return run_script(script_path(layer, scripts_dir), (*args, layer.repo_flag, str(repo)), repo)


def report(status: str, layer: Layer, detail: str) -> None:
    print(f"build_docs_layers: {status:<7} {layer.name:<15} {detail}")


def pass_over(layers, phase: str, repo: Path, scripts_dir: Path) -> list[str]:
    """Run one phase ("write" or "check") over the layers; return the failures, in order."""
    failures: list[str] = []
    for layer in layers:
        args = layer.write_args if phase == "write" else layer.check_args
        if args is None:
            continue
        if not script_path(layer, scripts_dir).is_file():
            report("SKIP", layer, f"{layer.script} not in this checkout yet")
            continue
        code, output = run_layer(layer, args, repo, scripts_dir)
        if code == 0:
            report("ok", layer, last_line(output))
            continue
        failures.append(layer.name)
        report("STALE" if phase == "check" else "FAILED", layer, last_line(output))
        break            # the first bad layer stops the pass: the ones after it read its artifact
    return failures


def digest_pass(layers, repo: Path, scripts_dir: Path) -> list[str]:
    """The cheap check: one line per layer, stopping at the first whose input digest moved.

    One hash cache for the whole pass, so a document that feeds seven layers is read once."""
    behind: list[str] = []
    cache: dict = {}
    for layer in layers:
        if not script_path(layer, scripts_dir).is_file():
            report("SKIP", layer, f"{layer.script} not in this checkout yet")
            continue
        stored = stored_digest(repo, layer.name)
        current = digest(layer, repo, scripts_dir, cache, tuple(layers))
        if stored == current:
            report("ok", layer, f"digest current ({current[:12]})")
            continue
        behind.append(layer.name)
        report("STALE", layer, "never built in this checkout"
               if stored is None else f"inputs moved: {stored[:12]} -> {current[:12]}")
        break            # the first stale layer stops the pass: the ones after it read its artifact
    return behind


def ensure_pass(repo: Path, names, scripts_dir: Path, layers, then_recheck: bool = False) -> int:
    """The blocking rebuild - and, as the background child, the re-check that follows it.

    A write that lands WHILE a layer is being rebuilt would otherwise be invisible until the next
    write: the child's pass ends, the lock comes off, and the tree is stale with nobody coming. So
    the child re-computes the stale set over the WHOLE stack when its pass ends and goes again, at
    most REFRESH_ROUNDS times - bounded, because a tree being written to continuously must not hold
    one process forever.

    The lock is TAKEN OVER in this process's own pid first, and removed only if it is still ours
    (`clear_lock(pid=...)`). `refresh` had to stamp it with the pid `Popen` returned, which on a
    venv whose `python.exe` is a redirector is the shim, not this interpreter (measured: Popen said
    30568, the child was 11460) - so the pid a reader probes for liveness is the one really doing
    the work, and the removal at the end cannot take a newer refresh's lock off by accident."""
    if then_recheck:
        prior = read_lock(repo) or {}
        write_lock(repo, os.getpid(), names or prior.get("names") or [])
    try:
        for round_n in range(1, (REFRESH_ROUNDS if then_recheck else 1) + 1):
            try:
                rebuilt = ensure(names, repo, scripts_dir, layers=layers)
            except LayerError as exc:
                print(f"build_docs_layers: FAILED to build {exc.layer} - {exc.detail}")
                return 1
            print(f"build_docs_layers: rebuilt {', '.join(rebuilt)}" if rebuilt
                  else "build_docs_layers: every layer already current")
            if not then_recheck:
                return 0
            names = stale(None, repo, scripts_dir, layers=layers)
            if not names:
                print(f"build_docs_layers: refresh done in {round_n} round(s), every layer current")
                return 0
            if round_n == REFRESH_ROUNDS:
                break
            print(f"build_docs_layers: a write landed during round {round_n} - "
                  f"{', '.join(names)} went stale, going again")
        print(f"build_docs_layers: stopped after {REFRESH_ROUNDS} rounds, still stale: "
              f"{', '.join(names or [])} - the tree is being written to faster than it builds")
        return 0
    finally:
        if then_recheck:
            clear_lock(repo, os.getpid())


def refresh_pass(repo: Path, names, scripts_dir: Path, layers) -> int:
    """What a write hook calls: one line, exit 0, nothing waited on. Never fails a commit or an edit."""
    state = refresh(repo, names, scripts_dir, layers)
    if state["started"]:
        print(f"build_docs_layers: refreshing {', '.join(state['stale'])} in the background "
              f"(pid {state['started']}, log {log_path(repo).as_posix()})")
    elif state["running"]:
        running = state["running"]
        print(f"build_docs_layers: a refresh is already running (pid {running['pid']}, started "
              f"{running['started']}, {', '.join(running.get('names') or [])})")
    elif state["stale"]:
        print(f"build_docs_layers: {', '.join(state['stale'])} stale and no builder here to run")
    else:
        print("build_docs_layers: every layer in sync (nothing to refresh)")
    return 0


def status_pass(repo: Path, names, scripts_dir: Path, layers) -> int:
    """The reader's question, answered without building anything: exit 0 either way."""
    running = live_lock(repo)
    behind = stale(names, repo, scripts_dir, layers=layers)
    last = last_log_line(repo)
    print(f"build_docs_layers: stale: {', '.join(behind) if behind else '(none)'}")
    print(f"build_docs_layers: refresh: " + (
        f"running, pid {running['pid']}, started {running['started']}, "
        f"{', '.join(running.get('names') or [])}" if running else "none running"))
    print(f"build_docs_layers: last line: {last if last else '(no log yet)'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 naming the first layer whose input digest moved (default)")
    ap.add_argument("--write", action="store_true", help="regenerate every layer, then re-check")
    ap.add_argument("--ensure", action="store_true",
                    help="rebuild only the layers whose inputs moved, upstream first (blocks)")
    ap.add_argument("--refresh", action="store_true",
                    help="start that rebuild in the background behind the lock and return at once")
    ap.add_argument("--status", action="store_true",
                    help="what is stale, what is rebuilding it and its last line - builds nothing")
    ap.add_argument("--then-recheck", action="store_true", dest="then_recheck",
                    help="with --ensure (the background child): re-check after the pass and go again "
                         f"if a write landed meanwhile, at most {REFRESH_ROUNDS} rounds")
    ap.add_argument("--only", metavar="LAYER[,LAYER...]", default=None,
                    help="with --ensure/--refresh: these layers and their upstream, not the whole stack")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    scripts_dir = SCRIPTS
    layers = LAYERS

    names = [one.strip() for one in a.only.split(",") if one.strip()] if a.only else None

    if a.refresh:
        return refresh_pass(repo, names, scripts_dir, layers)

    if a.status:
        return status_pass(repo, names, scripts_dir, layers)

    if a.ensure:
        return ensure_pass(repo, names, scripts_dir, layers, a.then_recheck)

    if a.write:
        failed = pass_over(layers, "write", repo, scripts_dir)
        if failed:
            print(f"build_docs_layers: FAILED to build {failed[0]} - fix it before the re-check")
            return 1
        stale_layers = pass_over(layers, "check", repo, scripts_dir)
        if stale_layers:
            print(f"build_docs_layers: {stale_layers[0]} is stale - "
                  f"run build_docs_layers.py --write")
            return 1
        stamped = stamp(None, repo, scripts_dir, layers=layers)
        print(f"build_docs_layers: every layer in sync ({len(layers)} layers, "
              f"{len(stamped)} digests stamped)")
        return 0

    behind = digest_pass(layers, repo, scripts_dir)
    if behind:
        print(f"build_docs_layers: {behind[0]} is stale - "
              f"run build_docs_layers.py --ensure (or --write for a full pass)")
        return 1
    print(f"build_docs_layers: every layer in sync ({len(layers)} layers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

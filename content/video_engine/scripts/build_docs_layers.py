"""One command for the whole docs retrieval stack: build every layer, or prove none is stale.

The layers are separate tools on purpose - each owns one artifact - but they are ordered: the
manifest, the topic index and the gates registry all read `docs/DOCS-INDEX.jsonl`, so a docs pass
that rebuilds one and forgets the next ships a stale layer that still looks fresh. This runs them
in dependency order, in one process tree, and prints one summary line per layer.

    python content/video_engine/scripts/build_docs_layers.py --check   # exit 1 on the first stale
    python content/video_engine/scripts/build_docs_layers.py --write   # regenerate, then re-check

    | order | layer          | tool                    | artifact                            |
    |-------|----------------|-------------------------|-------------------------------------|
    | 1     | docs-index     | build_docs_index.py     | docs/DOCS-INDEX.jsonl + .md         |
    | 2     | docs-manifest  | build_docs_manifest.py  | docs/DOCS-MANIFEST.jsonl + .md      |
    | 3     | topic-index    | build_topic_index.py    | docs/DOCS-TOPICS.* + DOCS-CITATIONS |
    | 4     | gates-registry | build_gates_registry.py | docs/GATES-REGISTRY.jsonl + .md     |
    | 5     | docs-standard  | audit_docs_standard.py  | docs/DOCS-STANDARD.md               |

A tool that is not in the tree yet is SKIPPED with a printed note, never silently: the stack grows
a layer at a time and a missing script is a fact about this checkout, not a failure. The audit
writes a report rather than a checkable artifact, so it runs in `--write` only. Standard library
only; every tool runs as a subprocess of this interpreter, so it sees the same Python.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]

REPORT_REL = "docs/DOCS-STANDARD.md"


@dataclass(frozen=True)
class Layer:
    """One tool in the stack. `check_args` is None for a layer that only writes a report;
    `repo_flag` is the flag that tool names the repository root with."""
    name: str
    script: str
    write_args: tuple[str, ...] = ("--write",)
    check_args: tuple[str, ...] | None = ("--check",)
    repo_flag: str = "--repo"


LAYERS = (
    Layer("docs-index", "build_docs_index.py"),
    Layer("docs-manifest", "build_docs_manifest.py"),
    Layer("topic-index", "build_topic_index.py"),
    Layer("gates-registry", "build_gates_registry.py"),
    Layer("docs-standard", "audit_docs_standard.py",
          write_args=("--report", REPORT_REL), check_args=None, repo_flag="--root"),
)


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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 naming the first stale layer (default)")
    ap.add_argument("--write", action="store_true", help="regenerate every layer, then re-check")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    a = ap.parse_args(argv)
    repo = Path(a.repo).resolve()
    scripts_dir = SCRIPTS

    if a.write:
        failed = pass_over(LAYERS, "write", repo, scripts_dir)
        if failed:
            print(f"build_docs_layers: FAILED to build {failed[0]} - fix it before the re-check")
            return 1
    stale = pass_over(LAYERS, "check", repo, scripts_dir)
    if stale:
        print(f"build_docs_layers: {stale[0]} is stale - "
              f"run build_docs_layers.py --write")
        return 1
    print(f"build_docs_layers: every layer in sync ({len(LAYERS)} layers)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

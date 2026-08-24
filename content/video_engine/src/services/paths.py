"""The path contract: a file's durability class is readable from its path alone.

This module is the single owner of the class layout. Services never build a
class-root path by hand — a structural test enforces that — so backup tooling,
cleanup tooling and ``.gitignore`` can each act on a path prefix and be right.

Layout, per project root (single source of truth):

    <project_root>/
      canonical/   catalogue-referenced assets. Must survive hardware death;
                   synced to the content-addressed store on promote.
      review/      in-flight deliveries and claim output. Losable but annoying.
      runtime/     disposable derived artifacts — previews, quarantine renders,
                   composed props. Regenerable on demand; allowed to vanish.

The rule generalised here already existed in embryo: ``composite_preview``
refused any output not under a ``runtime`` directory. ``is_runtime_path`` is
that check with an owner.

No I/O happens here beyond ``mkdir`` when a caller asks for it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

#: Ordered by durability: what must survive first.
DURABILITY_CLASSES = ("canonical", "review", "runtime")

#: Quarantine subpath for never-publishable preview renders. Owned here;
#: ``hyperframes_render`` imports it. The location (under a job's render dir)
#: is unchanged from before the contract — relocation would be a semantics
#: change, and the quarantine tests must pass verbatim.
QUARANTINE_DIR = "renders/quarantine"

#: Where generation request packs export, relative to the engine root. Owned
#: here; ``console/routes/generate.py`` imports it.
EXPORT_SUBPATH = ("runtime", "generation-requests")

#: Composite preview frames rendered for the console stage, engine-relative.
CONSOLE_PREVIEWS_SUBPATH = ("runtime", "console-previews")

#: Pipeline job directories the runs view reads, engine-relative.
RUNS_SUBPATH = ("runtime", "jobs")

#: Console-owned process state (Studio pid file, stderr log), engine-relative.
CONSOLE_STATE_SUBPATH = ("runtime", "console-state")

#: Headless editor render output, engine-relative.
EDITOR_RENDERS_SUBPATH = ("runtime", "editor-renders")


class PathContractError(Exception):
    """A path that escapes, or names no durability class."""

    def __init__(self, errors: Sequence[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def _segments(parts: Sequence[str]) -> list[str]:
    """Split and validate the caller's parts into plain path segments."""

    errors: list[str] = []
    segments: list[str] = []
    for part in parts:
        text = str(part)
        if not text:
            errors.append("empty path part")
            continue
        if "\\" in text or ":" in text or text.startswith("/"):
            errors.append(f"path part {text!r} must be a relative forward-slash path")
            continue
        for segment in text.split("/"):
            if segment in ("", ".", ".."):
                errors.append(f"path part {text!r} contains {segment or 'an empty segment'!r}")
                break
            segments.append(segment)
    if errors:
        raise PathContractError(errors)
    return segments


def _class_dir(project_root: str | Path, cls: str, parts: Sequence[str], ensure: bool) -> Path:
    root = Path(project_root).expanduser().resolve()
    target = root.joinpath(cls, *_segments(parts))
    if ensure:
        target.mkdir(parents=True, exist_ok=True)
    return target


def canonical_dir(project_root: str | Path, *parts: str, ensure: bool = False) -> Path:
    """Catalogue-referenced assets: survives hardware death, synced on promote."""

    return _class_dir(project_root, "canonical", parts, ensure)


def review_dir(project_root: str | Path, *parts: str, ensure: bool = False) -> Path:
    """In-flight deliveries and claim output."""

    return _class_dir(project_root, "review", parts, ensure)


def runtime_dir(project_root: str | Path, *parts: str, ensure: bool = False) -> Path:
    """Disposable derived artifacts; allowed to vanish."""

    return _class_dir(project_root, "runtime", parts, ensure)


def class_of(path: str | Path, project_root: str | Path) -> str:
    """The durability class a path belongs to, read from the path alone.

    Relative paths resolve against the project root. A path outside the
    project, or whose first component is not a class root, is refused — the
    contract classifies; it never guesses.
    """

    root = Path(project_root).expanduser().resolve()
    candidate = Path(path)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        raise PathContractError([f"{resolved} is outside the project root {root}"])
    if not relative.parts:
        raise PathContractError([f"{resolved} is the project root itself, not a classed path"])
    head = relative.parts[0]
    if head not in DURABILITY_CLASSES:
        raise PathContractError([
            f"{relative.as_posix()!r} starts with {head!r}, which is not a "
            f"durability class {DURABILITY_CLASSES}"
        ])
    return head


def is_runtime_path(path: str | Path) -> bool:
    """True when the path lives under any ``runtime`` directory.

    The generalisation of ``composite_preview``'s output guard: derived,
    disposable artifacts must be recognisable as such from the path.
    """

    return "runtime" in Path(path).parts

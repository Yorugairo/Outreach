"""The path contract is enforced, not documented.

A service that builds a class-root path by hand re-creates the sprawl this
contract exists to end. This sweep fails naming the offender — the same shape
as the console's motion-arithmetic test, which has already proven that a
structural grep catches drift that review misses.
"""

from __future__ import annotations

import re
from pathlib import Path

_ENGINE = Path(__file__).resolve().parents[1]
_SWEPT = sorted(
    p
    for base in (_ENGINE / "src" / "services", _ENGINE / "console")
    for p in base.rglob("*.py")
    if p.name != "paths.py"
)

#: A quoted class name used in path construction. Prose mentions ('a runtime
#: directory') and dict keys (``manifest.get("review")``) do not match;
#: ``Path("runtime")``, ``joinpath("review", ...)``, ``root / "canonical"``
#: and tuple subpaths ``= ("runtime", ...)`` do — the tuple form requires an
#: assignment or nesting context so a function call's string argument is not
#: mistaken for a path.
_CLASS_IN_PATH = re.compile(
    r"""(?:Path\(|joinpath\(|\.join\(|/\s*|[=,\[]\s*\(\s*)["'](canonical|review|runtime)["']"""
)

#: Subpath literals the contract owns outright.
_OWNED_LITERALS = ("renders/quarantine", "generation-requests", "console-previews")

#: Lines that match textually but not semantically, each with its reason.
_ALLOWLIST = {
    # "canonical" audio is the render clock — a concept older than the path
    # contract and unrelated to the canonical durability class.
    ("src/services/history_narration.py", 'root / "audio" / "canonical"'),
}


def _allowlisted(path: Path, line: str) -> bool:
    rel = path.relative_to(_ENGINE).as_posix()
    return any(rel == f and fragment in line for f, fragment in _ALLOWLIST)


def test_no_service_or_console_module_hand_builds_a_class_root_path():
    offenders: list[str] = []
    for path in _SWEPT:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if _allowlisted(path, line):
                continue
            if _CLASS_IN_PATH.search(line):
                offenders.append(f"{path.relative_to(_ENGINE)}:{number}: {stripped}")
            elif any(lit in line for lit in _OWNED_LITERALS) and "_paths" not in line:
                offenders.append(f"{path.relative_to(_ENGINE)}:{number}: {stripped}")
    assert not offenders, (
        "class-root paths must resolve through services/paths.py; hand-built:\n"
        + "\n".join(offenders)
    )


def test_the_sweep_is_watching_a_real_tree():
    """An empty file list would make the test above pass vacuously."""

    assert len(_SWEPT) > 20, f"only {len(_SWEPT)} files swept — wrong root?"

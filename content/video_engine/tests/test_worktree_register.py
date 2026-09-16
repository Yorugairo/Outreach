"""THE WORKTREE REGISTER: the rulings ledger numbers each ruling once, and every live worktree is named by a register row.

The pins: `^**E99 s<n> - ` never repeats a number (the message lists the duplicates); `git worktree list --porcelain`
names only checkouts that appear as a backticked path in a `docs/WORKTREE-REGISTER.md` table row (the message lists the
unnamed ones). A register row may name a path that is no longer a worktree - that is allowed. Nothing is written.
"""
from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
RULINGS = ROOT / "docs/portable/OPERATOR-RULINGS.md"
REGISTER = ROOT / "docs/WORKTREE-REGISTER.md"
RULING_RE = re.compile(r"^\*\*E99 s(\d+) - ", re.M)
BACKTICKED_RE = re.compile(r"`([^`\n]+)`")


def _key(path: str) -> str:
    return str(Path(path).resolve()).casefold()


def test_every_ruling_number_appears_once() -> None:
    numbers = [int(n) for n in RULING_RE.findall(RULINGS.read_text(encoding="utf-8"))]
    duplicates = sorted(n for n, count in Counter(numbers).items() if count > 1)
    assert numbers, f"no '**E99 s<n> - ' rulings found in {RULINGS}"
    assert not duplicates, f"E99 ruling numbers used twice in {RULINGS}: {duplicates}"


def test_every_worktree_has_a_register_row() -> None:
    try:
        proc = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
    except OSError as exc:  # git not installed
        pytest.skip(f"git worktree list unavailable: {exc}")
    if proc.returncode != 0:
        pytest.skip(f"git worktree list failed ({proc.returncode}): {proc.stderr.strip()}")

    worktrees = [line[len("worktree ") :].strip() for line in proc.stdout.splitlines() if line.startswith("worktree ")]
    assert worktrees, "git worktree list --porcelain named no worktree"

    assert REGISTER.exists(), "docs/WORKTREE-REGISTER.md missing - P62 T2 writes it"
    registered = {
        _key(cell)
        for cell in BACKTICKED_RE.findall(REGISTER.read_text(encoding="utf-8"))
        if Path(cell).is_dir()
    }
    unnamed = [path for path in worktrees if _key(path) not in registered]
    assert not unnamed, f"worktrees with no row in {REGISTER}: {unnamed}"

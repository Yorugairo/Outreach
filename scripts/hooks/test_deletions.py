"""THE TEST-DELETION RECEIPT (operator, 2026-09-16): a commit that REMOVES a test says so in its message.

The defect that earned it: an agent rewrote `content/video_engine/tests/test_authoring_kit.py`, appended
nineteen tests and silently dropped the file's last ten - HEAD lines 234-323, a contiguous tail across four
unrelated subjects (the shot table, plate `use` options, the kit's module list, the TR13 gap rules). The
count went 36 -> 45, so "45 passed" read as success. A passing suite CANNOT see a test that no longer
exists; nothing else cited those behaviours; the only thing that noticed was `build_docs_layers.py`, because
an effects card named `test_a_plate_may_name_its_use` as its on-disk proof and the proof had gone.

So this is a receipt, like the recall one beside it: deletions are allowed, silence about them is not. A
removed `def test_*` that survives ELSEWHERE in the staged tree is a move or a rename and passes untouched -
only a name that exists nowhere afterwards has to be named in the message:

    Tests-removed: test_a_plate_may_name_its_use - the plate `use` option was retired in this commit

Install (chained after the recall receipt in .git/hooks/commit-msg):
    python scripts/hooks/test_deletions.py "$1"           (the message file)
    or by hand:  python scripts/hooks/test_deletions.py --message "<msg>" --staged

Exit 0 = pass, 1 = refused (the reason is printed), 2 = usage.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEF_RE = re.compile(r"^def\s+(test_[A-Za-z0-9_]+)")
MARKER_RE = re.compile(r"^\s*Tests-removed:\s*(.+?)\s*$", re.M)


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout   # the diff is UTF-8; the Windows locale default (cp1252) killed the reader and .stdout came back None (2026-09-16)


def removed_names(diff: str) -> set[str]:
    """Test functions whose `def` line the staged diff deletes."""
    out = set()
    for line in diff.splitlines():
        if line.startswith("-") and not line.startswith("---"):
            m = DEF_RE.match(line[1:])
            if m:
                out.add(m.group(1))
    return out


def survivors(names: set[str], blobs: dict[str, str]) -> set[str]:
    """Of `names`, the ones still defined somewhere in the tree AS IT WILL BE after this commit - a move
    between files or a rename-in-place is not a deletion and is not this gate's business."""
    return {n for n in names if any(re.search(rf"^def\s+{re.escape(n)}\b", t, re.M) for t in blobs.values())}


def staged_tree() -> dict[str, str]:
    """Every staged python file's post-commit content, by path."""
    out = {}
    for path in (p.strip() for p in _git("diff", "--cached", "--name-only").splitlines() if p.strip()):
        if path.endswith(".py"):
            out[path] = _git("show", f":{path}")
    return out


def check(message: str, diff: str, blobs: dict[str, str]) -> tuple[bool, str]:
    removed = removed_names(diff)
    if not removed:
        return True, "no test removed"
    gone = sorted(removed - survivors(removed, blobs))
    if not gone:
        return True, f"{len(removed)} test def(s) moved or renamed, none lost"
    declared = "\n".join(m.group(1) for m in MARKER_RE.finditer(message))
    undeclared = [n for n in gone if n not in declared]
    if undeclared:
        return False, ("REFUSED: this commit deletes " + str(len(gone)) + " test(s) that exist nowhere afterwards, and "
                       + str(len(undeclared)) + " go unnamed in the message:\n  "
                       + "\n  ".join(undeclared)
                       + "\n\nA passing suite cannot see a test that no longer exists, and a rising test COUNT hides "
                         "deletions (36 -> 45 hid ten, 2026-09-16). If the removal is deliberate, say so:\n"
                         "  Tests-removed: <name> - <why>\n"
                         "If it is not, restore them: git show HEAD:<file> is the copy you want.")
    return True, f"test-deletion receipt ok: {len(gone)} declared"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--message":
        message = argv[1]
    else:
        message = Path(argv[0]).read_text(encoding="utf-8")
    ok, why = check(message, _git("diff", "--cached", "-U0"), staged_tree())
    print(why if ok else why, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

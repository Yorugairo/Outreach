"""The RECALL RECEIPT (operator, 2026-09-08): a commit that changes a MECHANISM must cite the record it integrates.

    "how come you just now found all of that research/doc information? the whole point of making this information
     retrieval cheap and easy was to get you to use it. How do we gate for that or make it part of your standardized
     processes?"

The gate is a receipt, not a reminder. When a commit touches the player template, the kinetics, the timeline compiler or
a short's shot table, its message must carry at least one `Recall:` line naming a path in the record (a docs/ file, a
research blueprint, a ruling) that EXISTS - the docs_find hit the change was designed from - or the explicit
`Recall: docs_find 0 hits for <term>` when the record truly has nothing. A commit with neither is refused.

Install (the operator's call - a standing process change):
    commit-msg hook:  python scripts/hooks/recall_receipt.py "$1"        (the message file)
    or by hand:       python scripts/hooks/recall_receipt.py --message "<msg>" --staged

Exit 0 = pass, 1 = refused (the reason is printed), 2 = usage.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MECHANISM_PATHS = (
    "docs/content-video-engine/samples/scene-evidence-player.template.html",
    "content/video_engine/scripts/kinetics/",
    "content/video_engine/scripts/build_scene_timeline_f.py",
    "content/video_engine/scripts/gate_motion_density.py",
)
MECHANISM_GLOBS = ("build_short.py", "build_scene_timeline")
RECALL_RE = re.compile(r"^\s*Recall:\s*(.+?)\s*$", re.M)
ZERO_RE = re.compile(r"docs_find\s+0\s+hits?\s+for\s+\S+", re.I)


def staged_paths() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=REPO, capture_output=True, text=True)
    return [p.strip() for p in out.stdout.splitlines() if p.strip()]


def touches_mechanism(paths: list[str]) -> list[str]:
    hit = []
    for p in paths:
        q = p.replace("\\", "/")
        if any(q.startswith(m) or q == m for m in MECHANISM_PATHS) or any(g in q for g in MECHANISM_GLOBS):
            hit.append(q)
    return hit


def check(message: str, paths: list[str]) -> tuple[bool, str]:
    mech = touches_mechanism(paths)
    if not mech:
        return True, "no mechanism touched"
    recalls = [m.group(1) for m in RECALL_RE.finditer(message)]
    if not recalls:
        return False, ("REFUSED: this commit changes a mechanism (" + ", ".join(mech[:3]) + (", ..." if len(mech) > 3 else "")
                       + ") and carries no `Recall:` line. Run docs_find on the mechanism's nouns first and cite the hit "
                         "(`Recall: <path>:<line>`), or state `Recall: docs_find 0 hits for <term>`.")
    for r in recalls:
        if ZERO_RE.search(r):
            continue
        path = r.split(":")[0].strip().strip("`")
        if (REPO / path).exists():
            continue
        return False, f"REFUSED: `Recall: {r}` names a path that does not exist in the record: {path}"
    return True, f"receipt ok: {len(recalls)} recall line(s) for {len(mech)} mechanism path(s)"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--message":
        message = argv[1]
        paths = staged_paths() if "--staged" in argv else [a for a in argv[2:] if a != "--staged"]
    else:
        message = Path(argv[0]).read_text(encoding="utf-8")
        paths = staged_paths()
    ok, why = check(message, paths)
    print(why)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

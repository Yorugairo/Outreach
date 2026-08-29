"""Survey every worktree and emit STATE-OF-WORK.md - the sprawl ledger.

The operator's diagnosis (2026-08-29): "we just now have a half dozen
worktrees of partially completed episodes... everything is scattered...
we're losing everything we do." A snapshot document goes stale the day it
is written; this script regenerates the ledger from git and the filesystem
so recall cannot rot. Run it whenever the question is "where is X" or
"what is unfinished."

    python content/video_engine/scripts/survey_worktrees.py
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

MAIN = Path(r"C:\Users\Snipe\Downloads\Outreach Program")
CODEX = Path(r"C:\Users\Snipe\.codex\worktrees")
OUT = Path(__file__).resolve().parents[3] / "docs/STATE-OF-WORK.md"


def git(cwd: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:                                       # noqa: BLE001
        return ""


def worktrees() -> list[Path]:
    seen, out = set(), []
    for line in git(MAIN, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            p = Path(line[9:])
            if p.exists() and str(p) not in seen:
                seen.add(str(p)); out.append(p)
    for d in CODEX.iterdir() if CODEX.exists() else []:
        p = d / "Outreach Program"
        if p.exists() and str(p) not in seen:
            seen.add(str(p)); out.append(p)
    return out


def survey(p: Path) -> dict:
    branch = git(p, "rev-parse", "--abbrev-ref", "HEAD")
    head = git(p, "log", "-1", "--format=%h %ad %s", "--date=short")
    dirty = len([x for x in git(p, "status", "--porcelain").splitlines() if x])
    ahead = git(p, "rev-list", "--count", "origin/main..HEAD") or "?"
    eps = []
    proj = p / "content/video_engine/projects"
    if proj.exists():
        for series in proj.iterdir():
            if not series.is_dir():
                continue
            for ep in series.iterdir():
                if ep.is_dir() and ep.name not in ("review",):
                    marks = []
                    if (ep / "build-f").exists() or list(ep.glob("build*")):
                        marks.append("build")
                    if list(ep.glob("*VO*")) or list(ep.glob("vo")):
                        marks.append("vo")
                    if list(ep.glob("SHOT-TABLE*")):
                        marks.append("shots")
                    eps.append(f"{series.name}/{ep.name}"
                               + (f" [{'+'.join(marks)}]" if marks else ""))
    return {"path": p, "branch": branch, "head": head,
            "dirty": dirty, "ahead": ahead, "episodes": eps}


def main() -> int:
    rows = [survey(p) for p in worktrees()]
    lines = [
        "# STATE OF WORK - every worktree, regenerated",
        "",
        f"Generated {datetime.now():%Y-%m-%d %H:%M} by "
        "`survey_worktrees.py`. DO NOT hand-edit - rerun the script.",
        "",
        "A worktree with unmerged commits holds work that exists NOWHERE",
        "else. The harvest rule: an episode's durable output (scripts,",
        "evidence, tables, doctrine) merges to main when its stage",
        "completes - not when the whole episode ships. Worktrees are for",
        "isolation, not for storage.",
        "",
    ]
    for r in rows:
        lines.append(f"## `{r['path']}`")
        lines.append("")
        lines.append(f"- branch `{r['branch']}` - HEAD {r['head']}")
        lines.append(f"- {r['ahead']} commits not on origin/main - "
                     f"{r['dirty']} dirty files")
        if r["episodes"]:
            lines.append(f"- episodes: " + " - ".join(r["episodes"]))
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(rows)} worktrees -> {OUT}")
    for r in rows:
        flag = " <-- UNMERGED WORK" if r["ahead"] not in ("0", "?") else ""
        print(f"  {r['branch'] or 'detached':44} ahead {r['ahead']:>3}  "
              f"dirty {r['dirty']:>3}  eps {len(r['episodes'])}{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

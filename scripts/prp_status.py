from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def summarize(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---", source, flags=re.DOTALL)
    frontmatter: dict[str, str] = {}
    if frontmatter_match:
        for line in frontmatter_match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()
    task_statuses = re.findall(
        r"^### (T\d+): .+?$.*?^- Status:\s*(\S+)",
        source,
        flags=re.MULTILINE | re.DOTALL,
    )
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "id": frontmatter.get("id"),
        "title": frontmatter.get("title"),
        "status": frontmatter.get("status"),
        "tasks": {
            "total": len(task_statuses),
            "complete": sum(status == "complete" for _, status in task_statuses),
            "blocked": [task for task, status in task_statuses if status == "blocked"],
            "ready": [task for task, status in task_statuses if status == "pending"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", nargs="?", type=Path)
    args = parser.parse_args()
    plans = [args.plan] if args.plan else sorted((REPO_ROOT / ".claude" / "PRPs" / "plans").glob("*.plan.md"))
    print(json.dumps([summarize(path.resolve()) for path in plans if path.exists()], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_FIELDS = {
    "id",
    "title",
    "status",
    "operation",
    "risk",
    "owner",
    "branch",
    "created",
    "updated",
}
REQUIRED_SECTIONS = {
    "Summary",
    "Intent And Acceptance",
    "Scope",
    "Not Building",
    "Human Gates",
    "Mandatory Reads",
    "Execution Path",
    "Patterns To Mirror",
    "Task Slices",
    "Verification",
    "Evidence And Handoff",
}
PLAN_STATUSES = {"draft", "approved", "running", "review", "blocked", "complete"}
TASK_FIELDS = {"Status", "Owner", "Depends on", "Write set", "Acceptance", "Validate", "Evidence"}


def parse_frontmatter(source: str) -> dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", source, flags=re.DOTALL)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def validate(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    errors: list[str] = []
    frontmatter = parse_frontmatter(source)
    missing_fields = sorted(REQUIRED_FIELDS - frontmatter.keys())
    if missing_fields:
        errors.append(f"missing frontmatter: {', '.join(missing_fields)}")
    if frontmatter.get("status") not in PLAN_STATUSES:
        errors.append(f"invalid status: {frontmatter.get('status')}")

    sections = set(re.findall(r"^## (.+?)\s*$", source, flags=re.MULTILINE))
    missing_sections = sorted(REQUIRED_SECTIONS - sections)
    if missing_sections:
        errors.append(f"missing sections: {', '.join(missing_sections)}")

    tasks = list(re.finditer(r"^### (T\d+): .+?$", source, flags=re.MULTILINE))
    if not tasks:
        errors.append("missing task slices")
    for index, task in enumerate(tasks):
        end = tasks[index + 1].start() if index + 1 < len(tasks) else len(source)
        block = source[task.end() : end]
        fields = set(re.findall(r"^- ([^:]+):", block, flags=re.MULTILINE))
        missing = sorted(TASK_FIELDS - fields)
        if missing:
            errors.append(f"{task.group(1)} missing fields: {', '.join(missing)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plans", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.plans:
        errors = validate(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

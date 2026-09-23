"""Read-only pre-push check for video capabilities, effect cards and recipes.

Run after `git fetch` and before an explicitly authorized push. A Claude
bridge review must acknowledge the exact candidate fingerprint; this command
never fetches, edits, merges, commits or pushes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CAPABILITIES = "docs/content-video-engine/CAPABILITIES.md"
CARDS = "content/video_engine/effects/cards/"
RECIPES = "content/video_engine/effects/recipes/"
PATHS = (CAPABILITIES, CARDS, RECIPES)
ACK_RE = re.compile(r"^REGISTRY-ACK:\s*([0-9a-f]{64})\s*$", re.MULTILINE)
POSITION_RE = re.compile(r"^POSITION:\s*done\b", re.MULTILINE | re.IGNORECASE)


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    if check and result.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
    return result


def changed_lines(root: Path, *args: str) -> set[str]:
    return {line for line in git(root, *args).stdout.splitlines() if line}


def shared_dirty(root: Path) -> set[str]:
    changed = changed_lines(root, "diff", "--name-only", "HEAD", "--", *PATHS)
    changed |= changed_lines(root, "diff", "--cached", "--name-only", "--", *PATHS)
    changed |= changed_lines(root, "ls-files", "--others", "--exclude-standard", "--", *PATHS)
    return changed


def worktrees(root: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for block in git(root, "worktree", "list", "--porcelain").stdout.strip().split("\n\n"):
        fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
        if "worktree" in fields:
            records.append(fields)
    return records


def fingerprint(
    root: Path, base: str, head: str, paths: set[str], claude_heads: dict[str, str]
) -> tuple[str, dict[str, Any]]:
    base_sha = git(root, "rev-parse", base).stdout.strip()
    head_sha = git(root, "rev-parse", head).stdout.strip()
    blobs: dict[str, str | None] = {}
    for path in sorted(paths):
        result = git(root, "rev-parse", "-q", "--verify", f"{head_sha}:{path}", check=False)
        blobs[path] = result.stdout.strip() if result.returncode == 0 else None
    manifest = {"base": base_sha, "head": head_sha, "paths": blobs,
                "claude_heads": claude_heads}
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), manifest


def claude_ack(reply: Path, expected: str, candidate: dict[str, Any]) -> str | None:
    try:
        text = reply.read_text(encoding="utf-8")
        order = json.loads((reply.parent / "order.json").read_text(encoding="utf-8"))
        result = json.loads((reply.parent / "reply.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return f"Claude bridge acknowledgment is unreadable: {exc}"
    if order.get("lane") != "claude" or not result.get("session_id"):
        return "acknowledgment lacks a completed Claude bridge session"
    required = [
        f"REGISTRY-FINGERPRINT: {expected}",
        f"REGISTRY-CANDIDATE: {candidate['head']}",
        *(f"REGISTRY-CLAUDE-HEAD: {branch} {sha}"
          for branch, sha in sorted(candidate["claude_heads"].items())),
    ]
    brief = order.get("brief", "")
    if any(line not in brief.splitlines() for line in required):
        return "Claude order did not name the exact fingerprint, candidate and Claude heads"
    match = ACK_RE.search(text)
    if (not POSITION_RE.search(text) or match is None or match.group(1) != expected
            or any(line not in text.splitlines() for line in required[1:])):
        return ("Claude reply must acknowledge the exact fingerprint, candidate "
                "and Claude branch heads")
    return None


def checks(root: Path, paths: set[str]) -> list[dict[str, Any]]:
    commands: list[list[str]] = [
        [sys.executable, "content/video_engine/scripts/build_capabilities_index.py", "--check"],
        [sys.executable, "content/video_engine/scripts/build_effects_catalog.py", "--check"],
    ]
    if any(path.startswith((CARDS, RECIPES)) for path in paths):
        commands.append([sys.executable, "content/video_engine/scripts/effects_catalog_check.py"])
    results: list[dict[str, Any]] = []
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
        results.append({
            "command": " ".join(command), "exit_code": result.returncode,
            "output": (result.stdout + result.stderr).strip(),
        })
    return results


def inspect(root: Path, base: str, head: str, ack_file: Path | None) -> dict[str, Any]:
    base_sha = git(root, "rev-parse", base).stdout.strip()
    head_sha = git(root, "rev-parse", head).stdout.strip()
    ancestor = git(root, "merge-base", "--is-ancestor", base_sha, head_sha, check=False)
    if ancestor.returncode:
        raise RuntimeError(f"{base} is not an ancestor of {head}; fetch/merge before preflight")
    changed = changed_lines(root, "diff", "--name-only", base_sha, head_sha, "--", *PATHS)
    local_dirty = sorted(shared_dirty(root))
    overlaps: list[dict[str, Any]] = []
    other_state: list[dict[str, Any]] = []
    claude_heads: dict[str, str] = {}
    unstable_worktrees: list[str] = []
    for entry in worktrees(root):
        branch = entry.get("branch", "")
        other = Path(entry["worktree"])
        if other.resolve() == root.resolve() or not branch:
            continue
        head_before = git(root, "rev-parse", branch).stdout.strip()
        if head_before != entry["HEAD"]:
            unstable_worktrees.append(branch)
        if branch.startswith("refs/heads/claude/"):
            claude_heads[branch] = head_before
        dirty = sorted(shared_dirty(other))
        divergent = sorted(changed_lines(root, "diff", "--name-only", f"{head_sha}...{branch}", "--", *PATHS))
        head_after = git(root, "rev-parse", branch).stdout.strip()
        if head_after != head_before:
            unstable_worktrees.append(branch)
        collision = sorted(changed.intersection(set(dirty).union(divergent)))
        other_state.append({"worktree": str(other), "branch": branch,
                            "head": head_before, "dirty": dirty, "divergent": divergent})
        if collision:
            overlaps.append({"branch": branch, "paths": collision})
    digest, candidate = fingerprint(root, base_sha, head_sha, changed, claude_heads)
    check_results = checks(root, changed) if changed else []
    errors = []
    if local_dirty:
        errors.append("current checkout has uncommitted shared-registry edits")
    if overlaps:
        errors.append("another worktree has an unmerged or uncommitted edit to a candidate shared path")
    if any(entry["dirty"] for entry in other_state):
        errors.append("another worktree has in-progress shared-registry content edits")
    if unstable_worktrees:
        errors.append("worktree branch heads moved during inspection; rerun preflight")
    if (git(root, "rev-parse", base).stdout.strip() != base_sha
            or git(root, "rev-parse", head).stdout.strip() != head_sha):
        errors.append("candidate or base moved during inspection; rerun preflight")
    if any(git(root, "rev-parse", branch).stdout.strip() != sha
           for branch, sha in claude_heads.items()):
        errors.append("Claude branch head moved during inspection; rerun preflight")
    if any(item["exit_code"] for item in check_results):
        errors.append("registry validation failed")
    if changed:
        if ack_file is None:
            errors.append("Claude acknowledgment required for this candidate fingerprint")
        elif problem := claude_ack(ack_file, digest, candidate):
            errors.append(problem)
    return {
        "status": "BLOCK" if errors else ("PASS" if changed else "NOT_APPLICABLE"),
        "fingerprint": digest if changed else None,
        "candidate": candidate,
        "changed": sorted(changed),
        "local_dirty": local_dirty,
        "other_worktrees": other_state,
        "overlaps": overlaps,
        "unstable_worktrees": sorted(set(unstable_worktrees)),
        "checks": check_results,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--ack-file", type=Path)
    parser.add_argument("--repo", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        result = inspect(args.repo.resolve(strict=True), args.base, args.head, args.ack_file)
    except (OSError, RuntimeError) as exc:
        print(json.dumps({"status": "BLOCK", "errors": [str(exc)]}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] != "BLOCK" else 2


if __name__ == "__main__":
    raise SystemExit(main())

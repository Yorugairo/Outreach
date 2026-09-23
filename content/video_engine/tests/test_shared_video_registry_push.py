"""Read-only, exact-candidate checks for shared video registry pushes."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from content.video_engine.scripts import check_shared_video_registries as gate


def run(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


@pytest.fixture
def two_lanes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    run(repo, "init", "-b", "main")
    run(repo, "config", "user.email", "test@example.invalid")
    run(repo, "config", "user.name", "Registry Test")
    cap = repo / gate.CAPABILITIES
    cap.parent.mkdir(parents=True)
    cap.write_text("starter\n", encoding="utf-8")
    run(repo, "add", gate.CAPABILITIES)
    run(repo, "commit", "-m", "baseline")
    base = run(repo, "rev-parse", "HEAD")
    fable = tmp_path / "fable"
    run(repo, "worktree", "add", "-b", "claude/fable", str(fable), base)
    cap.write_text("proved capability\n", encoding="utf-8")
    run(repo, "add", gate.CAPABILITIES)
    run(repo, "commit", "-m", "capability")
    monkeypatch.setattr(gate, "checks", lambda _root, _paths: [])
    return repo, fable, base


def test_changed_shared_file_requires_exact_claude_ack(two_lanes: tuple[Path, Path, str], tmp_path: Path):
    repo, _, base = two_lanes
    first = gate.inspect(repo, base, "HEAD", None)
    assert first["status"] == "BLOCK"
    assert first["changed"] == [gate.CAPABILITIES]
    assert first["errors"] == ["Claude acknowledgment required for this candidate fingerprint"]

    exact = [
        f"REGISTRY-FINGERPRINT: {first['fingerprint']}",
        f"REGISTRY-CANDIDATE: {first['candidate']['head']}",
        *(f"REGISTRY-CLAUDE-HEAD: {branch} {sha}"
          for branch, sha in sorted(first["candidate"]["claude_heads"].items())),
    ]
    packet = tmp_path / "replied" / "packet"
    packet.mkdir(parents=True)
    (packet / "order.json").write_text(json.dumps({
        "lane": "claude", "brief": "\n".join(exact)
    }), encoding="utf-8")
    (packet / "reply.json").write_text(json.dumps({"session_id": "claude-session"}), encoding="utf-8")
    reply = packet / "reply.md"
    reply.write_text("\n".join(["POSITION: done", f"REGISTRY-ACK: {first['fingerprint']}",
                                *exact[1:]]) + "\n", encoding="utf-8")
    assert gate.inspect(repo, base, "HEAD", reply)["status"] == "PASS"

    reply.write_text("POSITION: done\nREGISTRY-ACK: " + "0" * 64 + "\n", encoding="utf-8")
    assert gate.inspect(repo, base, "HEAD", reply)["status"] == "BLOCK"


def test_dirty_claude_candidate_path_blocks_even_with_ack(
    two_lanes: tuple[Path, Path, str], tmp_path: Path
):
    repo, fable, base = two_lanes
    (fable / gate.CAPABILITIES).write_text("Claude work in progress\n", encoding="utf-8")
    report = gate.inspect(repo, base, "HEAD", None)
    assert report["overlaps"] == [{"branch": "refs/heads/claude/fable", "paths": [gate.CAPABILITIES]}]
    assert any("unmerged or uncommitted" in error for error in report["errors"])


def test_unrelated_claude_edit_is_reported_without_false_overlap(
    two_lanes: tuple[Path, Path, str]
):
    repo, fable, base = two_lanes
    card = fable / gate.CARDS / "dock.json"
    card.parent.mkdir(parents=True)
    card.write_text("Claude edit\n", encoding="utf-8")
    report = gate.inspect(repo, base, "HEAD", None)
    assert report["overlaps"] == []
    assert report["other_worktrees"][0]["dirty"] == [gate.CARDS + "dock.json"]
    assert any("in-progress shared-registry" in error for error in report["errors"])


def test_current_checkout_dirty_shared_file_blocks(two_lanes: tuple[Path, Path, str]):
    repo, _, base = two_lanes
    (repo / gate.CAPABILITIES).write_text("uncommitted revision\n", encoding="utf-8")
    report = gate.inspect(repo, base, "HEAD", None)
    assert report["status"] == "BLOCK"
    assert report["local_dirty"] == [gate.CAPABILITIES]


def test_divergent_claude_commit_blocks(two_lanes: tuple[Path, Path, str]):
    repo, fable, base = two_lanes
    (fable / gate.CAPABILITIES).write_text("Claude committed variant\n", encoding="utf-8")
    run(fable, "add", gate.CAPABILITIES)
    run(fable, "commit", "-m", "Claude capability")
    report = gate.inspect(repo, base, "HEAD", None)
    assert report["overlaps"] == [{"branch": "refs/heads/claude/fable", "paths": [gate.CAPABILITIES]}]


def test_claude_branch_advance_invalidates_prior_fingerprint(
    two_lanes: tuple[Path, Path, str]
):
    repo, fable, base = two_lanes
    before = gate.inspect(repo, base, "HEAD", None)
    unrelated = fable / "unrelated.txt"
    unrelated.write_text("different work\n", encoding="utf-8")
    run(fable, "add", "unrelated.txt")
    run(fable, "commit", "-m", "unrelated advance")
    after = gate.inspect(repo, base, "HEAD", None)
    assert before["fingerprint"] != after["fingerprint"]
    assert before["candidate"]["head"] == after["candidate"]["head"]


def test_non_claude_worktree_overlap_blocks(two_lanes: tuple[Path, Path, str], tmp_path: Path):
    repo, _, base = two_lanes
    other = tmp_path / "other"
    run(repo, "worktree", "add", "-b", "codex/other", str(other), base)
    (other / gate.CAPABILITIES).write_text("other lane edit\n", encoding="utf-8")
    report = gate.inspect(repo, base, "HEAD", None)
    assert {item["branch"] for item in report["overlaps"]} == {"refs/heads/codex/other"}

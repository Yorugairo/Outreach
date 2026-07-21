from __future__ import annotations

import json
import sys
from pathlib import Path

from src.orchestrator import InsightRunOrchestrator
from src.repositories.file_repository import FileBackedInsightRepository


def _make_repo(tmp_path: Path) -> FileBackedInsightRepository:
    return FileBackedInsightRepository(tmp_path / "artifacts")


def test_orchestrator_diffs_two_same_target_runs(tmp_path: Path):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    before = orch.start("python.org", mode="quick", max_pages=1)
    after = orch.start("python.org", mode="quick", max_pages=1)

    diff = orch.diff_runs(before.id, after.id)

    assert diff["base_run_id"] == before.id
    assert diff["comparison_run_id"] == after.id
    assert diff["same_target"] is True
    assert diff["score_delta"] == 0
    assert diff["page_count_delta"] == 0
    assert diff["recommendation_changes"]["unchanged_count"] >= 1


def test_cli_diff_command_returns_run_comparison(tmp_path: Path, capsys):
    repo = _make_repo(tmp_path)
    orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / "artifacts")
    before = orch.start("python.org", mode="quick", max_pages=1)
    after = orch.start("python.org", mode="quick", max_pages=1)

    import scripts.run_insight_pipeline as cli

    old_argv = sys.argv
    try:
        sys.argv = [
            "run_insight_pipeline.py",
            "--artifact-root",
            str(tmp_path / "artifacts"),
            "diff",
            before.id,
            after.id,
        ]
        assert cli.main() == 0
    finally:
        sys.argv = old_argv

    payload = json.loads(capsys.readouterr().out)
    assert payload["same_target"] is True
    assert payload["recommendation_changes"]["unchanged_count"] >= 1

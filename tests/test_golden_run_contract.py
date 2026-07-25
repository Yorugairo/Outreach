from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestrator import InsightRunOrchestrator  # noqa: E402
from src.repositories.file_repository import FileBackedInsightRepository  # noqa: E402


def test_golden_domains_preserve_artifact_contract(tmp_path: Path):
    cases = json.loads((PROJECT_ROOT / "tests" / "fixtures" / "golden_domains.json").read_text())
    assert len(cases) >= 3

    for case in cases:
        repo = FileBackedInsightRepository(tmp_path / case["name"] / "artifacts")
        orch = InsightRunOrchestrator(repo, artifact_root=tmp_path / case["name"] / "artifacts")

        run = orch.start(case["url"], mode=case["mode"], max_pages=case["max_pages"])
        validation = orch.validate(run.id)
        report_path = tmp_path / case["name"] / "artifacts" / "runs" / run.id / "reports" / "v1.json"
        report = json.loads(report_path.read_text())
        report_v2_path = tmp_path / case["name"] / "artifacts" / "runs" / run.id / "reports" / "v2.json"
        report_v2 = json.loads(report_v2_path.read_text())

        assert validation["valid"] is True
        assert validation["completed_stage_count"] == case["expected_stage_count"]
        assert validation["run_limits_recorded"] is True
        assert validation["report_actions_have_evidence_refs"] is True
        assert report["report_payload"]["run"]["input_payload"]["limits"]["max_pages"] == case["max_pages"]
        assert all(action.get("evidence_refs") for action in report["key_actions"])
        assert report["report_version"] == "v1"
        assert report_v2["report_version"] == "v2"
        assert report_v2["report_payload"]["findings"] is not None
        assert (report_v2_path.parent / "v1.md").exists()
        assert (report_v2_path.parent / "v2.md").exists()

from __future__ import annotations

import pytest

from src.models import canonical_sha256
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.report_comparison_service import ReportComparisonService


def _snapshot(name: str, target: str, payload: dict) -> dict:
    return {
        "id": name,
        "target_id": target,
        "payload_sha256": canonical_sha256(payload),
    }


def test_comparison_aligns_context_and_classifies_changes() -> None:
    baseline = {
        "target": {"id": "target-1"},
        "formula_version": "seo-health.v2",
        "checks": [
            {"id": "title", "status": "failed"},
            {"id": "schema", "status": "unknown"},
        ],
        "pages": [{"url": "https://example.test/services/", "status": "fetched"}],
        "keyword_set_id": "keywords-1",
        "keywords": [{"keyword": "Acme services", "status": "measured"}],
        "score": 61,
    }
    current = {
        "target": {"id": "target-1"},
        "formula_version": "seo-health.v2",
        "checks": [
            {"id": "title", "status": "failed"},
            {"id": "schema", "status": "measured"},
        ],
        "pages": [
            {"url": "https://example.test/services", "status": "fetched"},
            {"url": "https://example.test/contact", "status": "fetched"},
        ],
        "keyword_set_id": "keywords-1",
        "keywords": [{"keyword": "acme services", "status": "measured"}],
        "score": 66,
    }

    result = ReportComparisonService().compare(
        _snapshot("baseline", "target-1", baseline),
        _snapshot("current", "target-1", current),
        baseline,
        current,
        target_id="target-1",
    )

    assert result.contract_version == "comparison-v1"
    assert result.compatibility["same_target"] is True
    assert result.changes["pages"]["introduced"] == ["https://example.test/contact"]
    assert result.changes["pages"]["persisting"] == ["https://example.test/services"]
    assert result.changes["checks"]["unknown"] == ["schema"]
    assert result.changes["numeric_deltas"]["score"] == 5


def test_incompatible_context_marks_unknown_and_suppresses_numeric_deltas() -> None:
    baseline = {"target": {"id": "target-1"}, "formula_version": "seo-health.v2", "score": 61}
    current = {"target": {"id": "target-1"}, "formula_version": "seo-health.v3", "score": 66}

    result = ReportComparisonService().compare(
        _snapshot("baseline", "target-1", baseline),
        _snapshot("current", "target-1", current),
        baseline,
        current,
        target_id="target-1",
    )

    assert result.compatibility["stable_checks"] is False
    assert "numeric_deltas" not in result.changes
    assert result.unknown_reasons
    assert result.changes["checks"]["status"] == "unknown"


def test_persistence_requires_explicit_repository_contract() -> None:
    payload = {"target": {"id": "target-1"}}
    result = ReportComparisonService().compare(
        _snapshot("baseline", "target-1", payload),
        _snapshot("current", "target-1", payload),
        payload,
        payload,
        target_id="target-1",
    )

    with pytest.raises(RuntimeError, match="save_report_comparison_snapshot"):
        ReportComparisonService(object()).persist(result)


def test_agent_recommendations_are_compared_only_when_validated_contract_matches() -> None:
    baseline = {"target": {"id": "target-1"}, "score": 40}
    current = {"target": {"id": "target-1"}, "score": 45}
    baseline_assessment = {
        "served_provider": "provider-a",
        "served_model": "model-a",
        "prompt_version": "prompt.v1",
        "rubric_version": "rubric.v1",
        "validation_result": {"customer_safe": True},
        "findings": [{"id": "rec-1", "claim_type": "recommendation", "customer_safe": True}],
    }
    current_assessment = {
        **baseline_assessment,
        "served_model": "model-b",
        "findings": [{"id": "rec-2", "claim_type": "recommendation", "customer_safe": True}],
    }

    result = ReportComparisonService().compare(
        _snapshot("baseline", "target-1", baseline),
        _snapshot("current", "target-1", current),
        baseline,
        current,
        target_id="target-1",
        baseline_assessment=baseline_assessment,
        current_assessment=current_assessment,
    )

    assert result.compatibility["agent_model"] is False
    assert result.changes["recommendations"]["status"] == "unknown"
    assert "numeric_deltas" not in result.changes


@pytest.mark.parametrize("backend", ["file", "sqlite"])
def test_comparison_snapshots_are_immutable_and_queryable(tmp_path, backend: str) -> None:
    repository = (
        FileBackedInsightRepository(tmp_path / "files")
        if backend == "file"
        else SQLiteInsightRepository(tmp_path / "comparison.db", tmp_path / "artifacts")
    )
    payload = {"target": {"id": "target-1"}, "formula_version": "seo-health.v2"}
    snapshot = ReportComparisonService(repository).compare_and_persist(
        _snapshot("baseline", "target-1", payload),
        _snapshot("current", "target-1", payload),
        payload,
        payload,
        target_id="target-1",
    )
    assert repository.get_report_comparison_snapshot(snapshot.id).id == snapshot.id
    assert repository.list_report_comparison_snapshots(target_id="target-1")[0].id == snapshot.id

    changed = type(snapshot)(
        **{
            **snapshot.to_dict(),
            "changes": {**snapshot.changes, "introduced": ["tampered"]},
        }
    )
    with pytest.raises(ValueError, match="immutable"):
        repository.save_report_comparison_snapshot(changed)

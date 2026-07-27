from __future__ import annotations

from pathlib import Path

import pytest

from src.models import (
    AgenticEvidenceReviewEvent,
    AgenticToolStep,
    AgenticWorkItem,
    BusinessFactLedgerSnapshot,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository


SHA = "a" * 64


def _item() -> AgenticWorkItem:
    return AgenticWorkItem(
        id="work-1",
        run_id="run-1",
        attempt_id="attempt-1",
        evidence_pack_id="pack-1",
        vertical_pack_version="national_bjj_registry.agentic.v1",
        work_kind="business_fact_ledger",
        mode="prospect",
        source_sha256=SHA,
        idempotency_key="work-key-1",
        requested_runtime="hermes-openrouter",
        requested_provider="openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        prompt_version="prompt.v1",
        rubric_version="rubric.v1",
        schema_version="schema.v1",
    )


def _snapshot(item: AgenticWorkItem) -> BusinessFactLedgerSnapshot:
    return BusinessFactLedgerSnapshot(
        id="ledger-1",
        run_id=item.run_id,
        attempt_id=item.attempt_id,
        work_item_id=item.id,
        vertical_pack_version=item.vertical_pack_version,
        source_sha256=SHA,
        facts=[],
    )


def _repositories(tmp_path: Path):
    yield FileBackedInsightRepository(tmp_path / "files")
    sqlite = SQLiteInsightRepository(tmp_path / "insights.db", tmp_path / "artifacts")
    try:
        yield sqlite
    finally:
        sqlite.close()


def test_work_items_are_idempotent_leased_and_snapshots_immutable(tmp_path: Path) -> None:
    for repository in _repositories(tmp_path):
        item = _item()
        assert repository.save_agentic_work_item(item).id == item.id
        assert repository.save_agentic_work_item(item).id == item.id
        leased = repository.lease_agentic_work_item(item.id, "worker-1", lease_seconds=60)
        assert leased.state == "leased"
        assert leased.lease_owner == "worker-1"
        with pytest.raises(ValueError, match="held by another"):
            repository.lease_agentic_work_item(item.id, "worker-2", lease_seconds=60)

        snapshot = _snapshot(item)
        assert repository.save_business_fact_ledger_snapshot(snapshot).id == snapshot.id
        assert repository.get_business_fact_ledger_snapshot(snapshot.id).content_sha256 == snapshot.content_sha256
        event = AgenticEvidenceReviewEvent(
            snapshot_id=snapshot.id,
            snapshot_type="business_fact_ledger",
            event_type="review_requested",
            operator="operator",
            reason_code="requires_grounding",
        )
        repository.append_agentic_evidence_review_event(event)
        assert repository.get_agentic_evidence_review_state(snapshot.id) == "needs_review"
        with pytest.raises(ValueError, match="immutable"):
            repository.save_business_fact_ledger_snapshot(
                BusinessFactLedgerSnapshot(**{**snapshot.to_dict(), "limitations": ["changed"], "content_sha256": None})
            )

        step = AgenticToolStep(
            id="step-1",
            work_item_id=item.id,
            sequence=1,
            action_kind="navigate_candidate",
            candidate_action_id="candidate-1",
            policy_decision="allowed",
            outcome="navigated",
        )
        assert repository.append_agentic_tool_step(step).id == step.id
        with pytest.raises(ValueError, match="append-only"):
            repository.append_agentic_tool_step(AgenticToolStep(**{**step.to_dict(), "outcome": "changed"}))


def test_sqlite_p12_records_survive_reopen(tmp_path: Path) -> None:
    db = tmp_path / "insights.db"
    artifacts = tmp_path / "artifacts"
    repository = SQLiteInsightRepository(db, artifacts)
    item = repository.save_agentic_work_item(_item())
    snapshot = repository.save_business_fact_ledger_snapshot(_snapshot(item))
    repository.close()

    reopened = SQLiteInsightRepository(db, artifacts)
    assert reopened.get_agentic_work_item(item.id).id == item.id
    assert reopened.get_business_fact_ledger_snapshot(snapshot.id).id == snapshot.id
    assert reopened.list_business_fact_ledger_snapshots(run_id="run-1")[0].id == snapshot.id
    reopened.close()


from __future__ import annotations

from pathlib import Path

from src.models import (
    AgenticWorkItem,
    InsightRun,
    SEOTarget,
    SiteEvidencePack,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.agentic_runtime import AgenticRuntimeResponse
from src.services.agentic_worker_service import AgenticWorkerService
from src.services.vertical_agentic_work_executor import VerticalAgenticWorkExecutor
from src.vertical_agentic_packs import ONE_TRADE_NETWORK_AGENTIC_V1


class FakeRuntime:
    runtime_id = "fake-runtime"

    def __init__(self) -> None:
        self.passes: list[str] = []

    def analyze(self, request):
        self.passes.append(request.pass_name)
        assert request.tool_policy == "none"
        payload = (
            {"facts": []}
            if request.pass_name == "business_fact_ledger"
            else {"answers": []}
        )
        return AgenticRuntimeResponse(
            payload=payload,
            served_provider=request.requested_provider,
            served_model=request.requested_model,
            input_tokens=20,
            output_tokens=5,
            actual_cost_usd=0.01,
            raw_response={"fixture": True},
        )


def seed(tmp_path: Path):
    repository = FileBackedInsightRepository(tmp_path)
    target = repository.upsert_target(
        SEOTarget(
            input_url="https://example.test",
            normalized_url="https://example.test/",
            normalized_domain="example.test",
        )
    )
    run = repository.create_run(
        InsightRun(
            id="run-1",
            seo_target_id=target.id,
            requested_url=target.normalized_url,
            requested_domain=target.normalized_domain,
            status="completed",
            current_stage="completed",
        )
    )
    repository.save_vertical_agentic_pack(ONE_TRADE_NETWORK_AGENTIC_V1)
    evidence_pack = repository.save_site_evidence_pack(
        SiteEvidencePack(
            id="evidence-1",
            run_id=run.id,
            attempt_id=run.attempt_id,
            source_snapshot_ids={},
            source_hashes={},
            target_facts={"business_name": "Example Plumbing"},
            page_facts=[],
            deterministic_surfaces={},
            evidence_refs=[],
            vertical_pack_version="one_trade_network.v1",
        )
    )

    def item(item_id: str, work_kind: str) -> AgenticWorkItem:
        return AgenticWorkItem(
            id=item_id,
            run_id=run.id,
            attempt_id=run.attempt_id,
            evidence_pack_id=evidence_pack.id,
            vertical_pack_version=ONE_TRADE_NETWORK_AGENTIC_V1.version,
            work_kind=work_kind,
            mode="prospect",
            source_sha256=str(evidence_pack.content_sha256),
            idempotency_key=f"key-{item_id}",
            requested_runtime="fake-runtime",
            requested_provider="fixture",
            requested_model="fixture-model",
            prompt_version="vertical-agentic.prompt.v1",
            rubric_version="vertical-agentic.rubric.v1",
            schema_version="vertical-agentic-evidence.v1",
            max_cost_usd=0.05,
            max_output_tokens=100,
        )

    # Save the dependent item first to prove the worker applies semantic
    # ordering rather than relying on backend insertion order.
    repository.save_agentic_work_item(item("decision-work", "decision_coverage"))
    repository.save_agentic_work_item(item("fact-work", "business_fact_ledger"))
    return repository


def test_durable_worker_executes_fact_then_decision_with_persisted_calls(tmp_path: Path) -> None:
    repository = seed(tmp_path)
    runtime = FakeRuntime()
    executor = VerticalAgenticWorkExecutor(
        repository,
        runtime=runtime,
        artifact_root=tmp_path,
        action_policy_root=Path("config/agentic/action-host-policies"),
    )
    worker = AgenticWorkerService(
        repository,
        artifact_root=str(tmp_path),
        runtime=runtime,
        work_item_executor=executor,
    )

    result = worker.run_once(max_jobs=0, max_work_items=2)

    assert result["p12"]["completed"] == 2
    assert runtime.passes == ["business_fact_ledger", "decision_coverage"]
    assert repository.get_agentic_work_item("fact-work").actual_cost_usd == 0.01
    assert repository.get_agentic_work_item("decision-work").actual_cost_usd == 0.01
    ledgers = repository.list_business_fact_ledger_snapshots(run_id="run-1")
    decisions = repository.list_decision_coverage_snapshots(run_id="run-1")
    assert len(ledgers) == len(decisions) == 1
    assert len(decisions[0].coverage) == len(ONE_TRADE_NETWORK_AGENTIC_V1.buyer_questions)
    steps = repository.list_agentic_tool_steps(limit=100)
    assert len(steps) == 2
    assert all(step.model_call_ref for step in steps)
    assert all((tmp_path / str(step.model_call_ref)).is_file() for step in steps)

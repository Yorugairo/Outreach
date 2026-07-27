from __future__ import annotations

from pathlib import Path

from src.config import AgenticAnalysisSettings
from src.models import InsightRun, PageRecord
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.agentic_analysis_service import (
    AgenticAnalysisService,
    PASS_NAMES,
)
from src.services.agentic_job_service import AgenticJobService
from src.services.agentic_runtime import (
    AgenticRuntimeError,
    AgenticRuntimeRequest,
    AgenticRuntimeResponse,
)
from src.services.hermes_runtime import HermesOpenRouterRuntime


class FakeRuntime:
    runtime_id = "hermes-openrouter"

    def __init__(self) -> None:
        self.calls: list[AgenticRuntimeRequest] = []

    def analyze(self, request: AgenticRuntimeRequest) -> AgenticRuntimeResponse:
        self.calls.append(request)
        return AgenticRuntimeResponse(
            payload={
                "findings": [
                    {
                        "claim_type": "recommendation",
                        "title": "Clarify the trial path",
                        "claim": "Make the signup action visible from the homepage.",
                        "confidence": "high",
                        "severity": "high",
                        "commercial_relevance": "Reduces ambiguity in the next step.",
                        "service_fit": ["vertical_plugin_embed"],
                        "evidence_refs": [
                            {
                                "artifact_path": "pages/page-1.json",
                                "field": "title",
                                "reason": "The persisted title identifies the page.",
                                "observed": "Nova Ryu",
                            }
                        ],
                    }
                ],
                "limitations": [],
            },
            served_provider=request.requested_provider,
            served_model=request.requested_model,
            input_tokens=50,
            output_tokens=20,
            actual_cost_usd=0.005,
            latency_ms=10,
            raw_response={"pass_name": request.pass_name},
            routing_mode="fixed-zdr",
        )


class FailedRuntime:
    runtime_id = "hermes-openrouter"

    def analyze(self, request: AgenticRuntimeRequest) -> AgenticRuntimeResponse:
        raise AgenticRuntimeError(
            f"{request.pass_name} could not authenticate",
            failure_class="authentication",
        )


def _setup(tmp_path: Path):
    repo = FileBackedInsightRepository(tmp_path)
    run = InsightRun(
        id="run-1",
        attempt_id="attempt-1",
        seo_target_id="target-1",
        requested_url="https://novaryu.com/",
        requested_domain="novaryu.com",
        status="completed",
        current_stage="completed",
        summary={"report_versions": []},
    )
    repo.create_run(run)
    repo.save_page_record(
        PageRecord(
            id="page-1",
            attempt_id=run.attempt_id,
            insight_run_id=run.id,
            seo_target_id=run.seo_target_id,
            url=run.requested_url,
            page_class="homepage",
            fetch_status="fetched",
            http_status=200,
            indexable=True,
            title="Nova Ryu",
            h1="Brazilian Jiu-Jitsu in Tacoma",
            ai_evidence={},
        )
    )
    settings = AgenticAnalysisSettings(
        enabled=True,
        operator_approved=True,
        promotion_approved=True,
    )
    jobs = AgenticJobService(repo, settings)
    service = AgenticAnalysisService(
        repo,
        artifact_root=tmp_path,
        job_service=jobs,
    )
    pack = service.build_evidence_pack(
        run.id,
        vertical_pack_version="national_bjj_registry.v1",
        target_facts={
            "business_name": "Nova Ryu",
            "market": "Tacoma, WA",
        },
    )
    return repo, service, jobs, pack


def test_four_fixed_passes_use_one_immutable_pack_and_record_usage(tmp_path: Path):
    repo, service, jobs, pack = _setup(tmp_path)
    job = jobs.enqueue_job(pack)
    runtime = FakeRuntime()

    assessment = service.run_job(job.id, runtime)

    assert [request.pass_name for request in runtime.calls] == list(PASS_NAMES)
    assert {request.evidence_pack_sha256 for request in runtime.calls} == {
        pack.content_sha256
    }
    assert len(assessment.call_ids) == 4
    assert assessment.total_cost_usd == 0.02
    assert assessment.validation_result["customer_safe"] is True
    assert repo.get_agentic_analysis_job(job.id).state == "complete"
    assert len(repo.list_agent_call_records(job_id=job.id)) == 4


def test_hermes_command_is_one_shot_profile_scoped_and_shell_free(tmp_path: Path):
    request = AgenticRuntimeRequest(
        job_id="job-1",
        evidence_pack_id="pack-1",
        evidence_pack_sha256="a" * 64,
        pass_name="evidence_analyst",
        prompt_version="prompt.v1",
        rubric_version="rubric.v1",
        schema_version="agentic-assessment.v1",
        requested_provider="openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        profile="outreach-analysis",
        prompt='{"evidence_pack_id":"pack-1"}',
    )
    command = HermesOpenRouterRuntime().build_command(
        request,
        usage_file=tmp_path / "usage.json",
    )

    assert command[0] == "hermes"
    assert command[command.index("--profile") + 1] == "outreach-analysis"
    assert command[command.index("--oneshot") + 1] == request.prompt
    assert "--ignore-rules" in command
    assert "--toolsets" in command
    assert command[command.index("--toolsets") + 1] == "mcp"
    assert isinstance(command, list)


def test_p12_hermes_command_disables_all_model_tools(tmp_path: Path) -> None:
    request = AgenticRuntimeRequest(
        job_id="work-1",
        evidence_pack_id="pack-1",
        evidence_pack_sha256="a" * 64,
        pass_name="journey_decision",
        prompt_version="prompt.v1",
        rubric_version="rubric.v1",
        schema_version="vertical-agentic-evidence.v1",
        requested_provider="openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        profile="outreach-analysis",
        prompt="{}",
        tool_policy="none",
    )

    command = HermesOpenRouterRuntime().build_command(
        request,
        usage_file=tmp_path / "usage.json",
    )

    assert command[command.index("--toolsets") + 1] == "none"
    assert "mcp" not in command


def test_terminal_runtime_error_fails_job_and_clears_lease(tmp_path: Path):
    repo, service, jobs, pack = _setup(tmp_path)
    job = jobs.enqueue_job(pack)

    try:
        service.run_job(job.id, FailedRuntime())
    except AgenticRuntimeError:
        pass
    else:
        raise AssertionError("runtime error should propagate after durable failure")

    failed = repo.get_agentic_analysis_job(job.id)
    assert failed is not None
    assert failed.state == "failed"
    assert failed.error_class == "authentication"
    assert failed.lease_owner is None
    assert failed.lease_expires_at is None

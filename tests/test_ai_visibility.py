from __future__ import annotations

from src.config import DataForSEOSettings
from src.dataforseo_client import DataForSEOClient
from src.models import PromptTopicSet, canonical_sha256
from src.services.ai_visibility_service import AIVisibilityService


def approved_topics() -> PromptTopicSet:
    return PromptTopicSet(
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        topics=[
            {"id": "topic-1", "prompt": "Which BJJ academies serve Tacoma?"},
            {"id": "topic-2", "prompt": "What are the best BJJ classes in Tacoma?"},
        ],
        source_sha256=canonical_sha256({"source": "operator", "version": 1}),
        state="approved",
        approved_by="operator",
        approved_at="2026-07-26T00:00:00+00:00",
    )


def evidence(topic_set: PromptTopicSet) -> list[dict]:
    context = {
        "market": "Tacoma, WA",
        "location_code": 1027773,
        "language_code": "en",
        "device": "desktop",
        "snapshot_date": "2026-07-26",
    }
    return [
        {
            **context,
            "context": context,
            "topic_id": "topic-1",
            "prompt_topic_set_id": topic_set.id,
            "prompt_topic_set_version": topic_set.version,
            "status": "complete",
            "mentions": [
                {"name": "Nova Ryu", "domain": "novaryu.com"},
                {"name": "Competitor Academy", "domain": "competitor.example"},
            ],
            "citations": [{"url": "https://novaryu.com/program"}],
            "raw_artifact_ref": "artifacts/dataforseo_raw/ai-1.json",
        },
        {
            **context,
            "context": context,
            "topic_id": "topic-2",
            "prompt_topic_set_id": topic_set.id,
            "prompt_topic_set_version": topic_set.version,
            "status": "complete",
            "mentions": [{"name": "Nova Ryu", "domain": "novaryu.com"}],
            "citations": [{"url": "https://novaryu.com/classes"}],
            "raw_artifact_ref": "artifacts/dataforseo_raw/ai-2.json",
        },
    ]


def test_approved_matching_evidence_reports_attributable_visibility() -> None:
    topic_set = approved_topics()
    result = AIVisibilityService().build(
        topic_set,
        evidence(topic_set),
        "novaryu.com",
        context={
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
            "snapshot_date": "2026-07-26",
        },
    )

    assert result.version == "ai-visibility.v1"
    assert result.status == "complete"
    assert result.metrics["mention_count"] == 2
    assert result.metrics["citation_count"] == 2
    assert result.metrics["distinct_cited_pages"] == 2
    assert result.metrics["prompt_coverage_percent"] == 100.0
    assert result.metrics["share_of_voice_percent"] == 66.6667
    assert result.metrics["raw_artifact_refs"] == [
        "artifacts/dataforseo_raw/ai-1.json",
        "artifacts/dataforseo_raw/ai-2.json",
    ]
    assert any("never changes AI Readiness" in warning for warning in result.warnings)


def test_sparse_or_context_mismatched_evidence_is_unknown() -> None:
    topic_set = approved_topics()
    row = evidence(topic_set)[0]
    row["market"] = "Seattle, WA"
    row["context"] = {**row["context"], "market": "Seattle, WA"}
    result = AIVisibilityService().build(
        topic_set,
        [row],
        "novaryu.com",
        context={"market": "Tacoma, WA", "location_code": 1027773, "language_code": "en", "device": "desktop"},
    )
    assert result.status == "unknown"
    assert result.metrics["mention_count"] is None
    assert result.metrics["share_of_voice_percent"] is None


def test_empty_provider_envelope_is_unavailable_not_zero_visibility() -> None:
    topic_set = approved_topics()
    result = AIVisibilityService().build(
        topic_set,
        [{"topic_id": "topic-1", "status": "complete", "items": []}, {"topic_id": "topic-2", "status": "complete", "items": []}],
        "novaryu.com",
        context={"market": "Tacoma, WA"},
    )
    assert result.status == "unknown"
    assert result.metrics["mention_count"] is None


def test_preflight_is_paid_bounded_and_has_no_network_side_effect() -> None:
    topic_set = approved_topics()
    service = AIVisibilityService()
    blocked = service.preflight(topic_set, provider_configured=True, operator_approved=False, allow_paid_api_calls=False)
    assert blocked["status"] == "blocked"
    assert blocked["planned_calls"] == 2
    assert blocked["call_cap"] == 20
    assert blocked["network_check_performed"] is False
    ready = service.preflight(topic_set, provider_configured=True, operator_approved=True, allow_paid_api_calls=True)
    assert ready["status"] == "ready"
    assert ready["conservative_max_cost_usd"] == 0.04


def test_missing_context_or_topic_set_identity_is_unknown_and_collection_is_blocked_by_default() -> None:
    topic_set = approved_topics()
    row = evidence(topic_set)[0]
    row.pop("prompt_topic_set_version")
    result = AIVisibilityService().build(
        topic_set,
        [row, evidence(topic_set)[1]],
        "novaryu.com",
        context={
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
            "snapshot_date": "2026-07-26",
        },
    )
    assert result.status == "partial"
    assert result.completeness_percent == 50.0

    class MustNotRun:
        def collect_ai_visibility(self, *args, **kwargs):
            raise AssertionError("paid provider must not run without approval")

    blocked = AIVisibilityService().collect(
        topic_set,
        MustNotRun(),
        target_domain="novaryu.com",
        context={
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
        },
    )
    assert blocked.status == "unknown"
    assert blocked.metrics["preflight"]["status"] == "blocked"


def test_dataforseo_ai_adapter_binds_context_and_preserves_raw_artifact(tmp_path) -> None:
    client = DataForSEOClient(DataForSEOSettings("login", "password"), artifact_dir=tmp_path)
    calls: list[tuple[str, list[dict]]] = []

    def fake_post(path, payload):
        calls.append((path, payload))
        raw = tmp_path / "ai.json"
        raw.write_text("{}", encoding="utf-8")
        client.last_raw_artifact = str(raw)
        return {"tasks": [{"cost": 0.01, "result": [{"items": [{"type": "ai_overview", "mentions": []}]}]}]}

    client.post = fake_post
    payload = client.collect_ai_visibility(
        "Which BJJ academies serve Tacoma?",
        location_code=1027773,
        language_code="en",
        device="desktop",
        market="Tacoma, WA",
        topic_id="topic-1",
        topic_set_id="set-1",
    )
    assert calls[0][0] == "/v3/serp/google/ai_overview/live/advanced"
    assert calls[0][1][0]["keyword"] == "Which BJJ academies serve Tacoma?"
    assert calls[0][1][0]["location_code"] == 1027773
    assert payload["status"] == "complete"
    assert payload["topic_id"] == "topic-1"
    assert payload["provider_cost_usd"] == 0.01
    assert payload["raw_artifact_ref"] == str(tmp_path / "ai.json")

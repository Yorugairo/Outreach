from __future__ import annotations

from src.dataforseo_client import DataForSEOProviderError
from src.models import InsightRun, SEOTarget, utc_now_iso
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.keyword_set_service import KeywordSetService
from src.services.market_evidence_service import MarketEvidenceService


class RecoveryProvider:
    def __init__(
        self,
        *,
        fail_keyword: str | None = None,
        payment_failure: bool = False,
        empty_metrics: bool = False,
    ) -> None:
        self.calls: list[tuple[str, str]] = []
        self.fail_keyword = fail_keyword
        self.payment_failure = payment_failure
        self.empty_metrics = empty_metrics

    def collect_keyword_metrics(self, keywords, *, location_code, language_code):
        self.calls.append(("keyword_metrics", "50-keyword-batch"))
        if self.payment_failure:
            raise DataForSEOProviderError(
                "DataForSEO HTTP 402",
                http_status=402,
            )
        return {
            "status": "complete",
            "source": "fixture",
            "snapshot_date": "2026-07-25",
            "items": [] if self.empty_metrics else [
                {"keyword": keyword, "search_volume": 100}
                for keyword in keywords
            ],
            "provider_cost_usd": 0.01,
            "raw_artifact_ref": "raw/metrics.json",
        }

    def collect_organic_serp(
        self,
        keyword,
        *,
        location_code,
        language_code,
        device,
        depth=100,
    ):
        self.calls.append(("organic_serp", keyword))
        if keyword == self.fail_keyword:
            raise TimeoutError("temporary organic timeout")
        return {
            "status": "complete",
            "keyword": keyword,
            "source": "fixture",
            "snapshot_date": "2026-07-25",
            "results": [
                {
                    "rank": 2,
                    "url": "https://competitor.example/program",
                    "title": "Competitor",
                },
                {
                    "rank": 7,
                    "url": "https://novaryu.com/program",
                    "title": "Nova Ryu",
                },
            ],
            "provider_cost_usd": 0.01,
            "raw_artifact_ref": f"raw/organic-{keyword}.json",
        }

    def collect_maps_serp(
        self,
        keyword,
        *,
        location_code,
        language_code,
        device,
        depth=20,
    ):
        self.calls.append(("maps_serp", keyword))
        return {
            "status": "complete",
            "keyword": keyword,
            "source": "fixture",
            "snapshot_date": "2026-07-25",
            "results": [
                {
                    "rank": 1,
                    "website": "https://competitor.example",
                    "place_id": "competitor-place",
                    "title": "Competitor",
                },
                {
                    "rank": 4,
                    "website": "https://novaryu.com",
                    "place_id": "nova-place",
                    "title": "Nova Ryu",
                },
            ],
            "provider_cost_usd": 0.01,
            "raw_artifact_ref": f"raw/maps-{keyword}.json",
        }


def _setup(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    target = repository.upsert_target(
        SEOTarget(
            input_url="https://novaryu.com",
            normalized_url="https://novaryu.com",
            normalized_domain="novaryu.com",
        )
    )
    run = repository.create_run(
        InsightRun(
            seo_target_id=target.id,
            requested_url=target.normalized_url,
            requested_domain=target.normalized_domain,
            status="completed",
            current_stage="completed",
            completed_at=utc_now_iso(),
        )
    )
    keyword_service = KeywordSetService(repository)
    keyword_set = keyword_service.approve(
        keyword_service.seed_tacoma_bjj(),
        operator="operator",
    )
    return repository, run, keyword_set


def test_paid_preflight_exposes_readiness_ceiling_and_warning_policy(tmp_path):
    _, _, keyword_set = _setup(tmp_path)
    preflight = MarketEvidenceService.paid_preflight(
        keyword_set,
        phase="pilot",
        provider_configured=True,
        reusable_calls=3,
        unresolved_calls=2,
        retry_ceiling=2,
    )

    assert preflight["planned_calls"] == 25
    assert preflight["account_readiness"] == "configured_unverified"
    assert preflight["billing_readiness"] == "not_checked"
    assert preflight["conservative_max_cost_usd"] == 0.58
    assert preflight["premium_warning_threshold_usd"] == 1.5
    assert preflight["reusable_calls"] == 3
    assert preflight["retry_ceiling"] == 2


def test_payment_failure_stops_paid_queue_and_marks_required_work_partial(tmp_path):
    repository, run, keyword_set = _setup(tmp_path)
    provider = RecoveryProvider(payment_failure=True)
    service = MarketEvidenceService(repository, lambda: provider)

    market_run = service.start_pilot(
        insight_run_id=run.id,
        keyword_set_id=keyword_set.id,
    )

    assert provider.calls == [("keyword_metrics", "50-keyword-batch")]
    assert market_run.state == "partial"
    assert market_run.provider_calls[0]["failure_class"] == "balance_payment"
    assert market_run.provider_calls[0]["retryable"] is False
    assert market_run.provider_completeness["unresolved"] == {
        "keyword_metrics": 1,
        "organic_serp": 12,
        "maps_serp": 12,
    }


def test_empty_paid_volume_response_is_unknown_not_zero_demand(tmp_path):
    repository, run, keyword_set = _setup(tmp_path)
    service = MarketEvidenceService(
        repository,
        lambda: RecoveryProvider(empty_metrics=True),
    )

    market_run = service.start_pilot(
        insight_run_id=run.id,
        keyword_set_id=keyword_set.id,
    )

    assert market_run.keyword_metrics == []
    assert market_run.state == "partial"
    assert market_run.provider_completeness["unresolved"]["keyword_metrics"] == 1
    assert any(
        item["kind"] == "empty_keyword_metrics"
        for item in market_run.evidence_limits
    )


def test_resume_creates_immutable_successor_and_retries_only_unresolved(tmp_path):
    repository, run, keyword_set = _setup(tmp_path)
    pilot = KeywordSetService().select_pilot(keyword_set)
    first = RecoveryProvider(fail_keyword=pilot[0].keyword)
    second = RecoveryProvider()
    providers = iter((first, second))
    service = MarketEvidenceService(repository, lambda: next(providers))
    predecessor = service.start_pilot(
        insight_run_id=run.id,
        keyword_set_id=keyword_set.id,
        target_entity_name="Nova Ryu",
    )

    assert predecessor.state == "partial"
    successor = service.resume_unresolved(predecessor.id)

    assert successor.id != predecessor.id
    assert successor.predecessor_market_run_id == predecessor.id
    assert successor.recovery_operation == "resume_unresolved"
    assert repository.get_market_evidence_run(predecessor.id).state == "partial"
    assert second.calls == [("organic_serp", pilot[0].keyword)]
    assert successor.provider_completeness["unresolved"] == {
        "keyword_metrics": 0,
        "organic_serp": 0,
        "maps_serp": 0,
    }
    assert successor.provider_completeness["reused"] == {
        "keyword_metrics": 1,
        "organic_serp": 11,
        "maps_serp": 12,
    }
    assert successor.actual_provider_cost == 0.01
    assert successor.state == "needs_competitor_approval"
    assert not any(
        item.get("operation") == "organic_serp"
        and item.get("query") == pilot[0].keyword
        for item in successor.evidence_limits
    )

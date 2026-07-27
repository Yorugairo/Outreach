from collections import Counter

import pytest

from src.models import InsightRun, SEOTarget, utc_now_iso
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.keyword_set_service import KeywordSetService
from src.services.market_evidence_service import MarketEvidenceService


class FakeMarketProvider:
    def __init__(self, *, fail_keyword: str | None = None):
        self.calls = []
        self.fail_keyword = fail_keyword

    def collect_keyword_metrics(self, keywords, *, location_code, language_code):
        self.calls.append(("metrics", tuple(keywords)))
        return {
            "status": "complete",
            "source": "fake_metrics",
            "snapshot_date": "2026-07-25",
            "items": [
                {"keyword": keyword, "search_volume": 100, "cpc": 2.5, "competition": 0.4}
                for keyword in keywords
            ],
            "provider_cost_usd": 0.01,
            "raw_artifact_ref": "raw/metrics.json",
        }

    def collect_organic_serp(self, keyword, *, location_code, language_code, device, depth=100):
        self.calls.append(("organic", keyword))
        if keyword == self.fail_keyword:
            raise RuntimeError("simulated organic failure")
        return {
            "status": "complete",
            "keyword": keyword,
            "snapshot_date": "2026-07-25",
            "source": "fake_organic",
            "results": [
                {"rank": 2, "url": "https://tacomabjj.example/program", "title": "Tacoma BJJ"},
                {"rank": 7, "url": "https://novaryu.com/program", "title": "Nova Ryu"},
                {"rank": 8, "url": "https://yelp.com/biz/tacoma-bjj", "title": "Directory"},
            ],
            "provider_cost_usd": 0.01,
            "raw_artifact_ref": f"raw/organic-{keyword}.json",
        }

    def collect_maps_serp(self, keyword, *, location_code, language_code, device, depth=20):
        self.calls.append(("maps", keyword))
        return {
            "status": "complete",
            "keyword": keyword,
            "snapshot_date": "2026-07-25",
            "source": "fake_maps",
            "results": [
                {
                    "rank": 1,
                    "website": "https://tacomabjj.example",
                    "place_id": "place-competitor",
                    "title": "Tacoma BJJ",
                },
                {
                    "rank": 4,
                    "website": "https://novaryu.com",
                    "place_id": "place-nova",
                    "title": "Nova Ryu",
                },
            ],
            "provider_cost_usd": 0.01,
            "raw_artifact_ref": f"raw/maps-{keyword}.json",
        }


def _setup(tmp_path, *, approve_all_risk=False):
    repository = FileBackedInsightRepository(tmp_path)
    target = SEOTarget(
        input_url="https://novaryu.com",
        normalized_url="https://novaryu.com",
        normalized_domain="novaryu.com",
    )
    repository.upsert_target(target)
    run = InsightRun(
        seo_target_id=target.id,
        requested_url=target.normalized_url,
        requested_domain=target.normalized_domain,
        status="completed",
        current_stage="completed",
        completed_at=utc_now_iso(),
    )
    repository.create_run(run)
    keyword_service = KeywordSetService(repository)
    keyword_set = keyword_service.seed_tacoma_bjj()
    if approve_all_risk:
        risky = [
            target.keyword
            for target in keyword_set.targets()
            if target.review_status == "needs_review"
        ]
        keyword_set = keyword_service.review_targets(keyword_set, approved_keywords=risky)
    keyword_set = keyword_service.approve(keyword_set, operator="operator")
    return repository, run, keyword_set


def test_pilot_preflight_budget_cost_and_candidate_merge(tmp_path):
    repository, run, keyword_set = _setup(tmp_path)
    provider = FakeMarketProvider()
    service = MarketEvidenceService(repository, lambda: provider)

    preflight = service.preflight(keyword_set, phase="pilot")
    assert preflight == {
        "phase": "pilot",
        "keyword_metrics_calls": 1,
        "organic_calls": 12,
        "maps_calls": 12,
        "planned_calls": 25,
        "call_cap": 26,
        "keyword_count": 12,
    }

    market_run = service.start_pilot(
        insight_run_id=run.id,
        keyword_set_id=keyword_set.id,
        target_entity_name="Nova Ryu",
    )
    assert market_run.state == "needs_competitor_approval"
    assert len(market_run.provider_calls) == 25
    assert market_run.actual_provider_cost == pytest.approx(0.25)
    assert len(market_run.keyword_metrics) == 50
    assert len(market_run.organic_evidence) == 12
    assert len(market_run.maps_evidence) == 12
    assert market_run.competitor_candidates[0]["candidate_id"] == "tacomabjj.example"
    assert market_run.competitor_candidates[0]["appearances"] == 24
    assert market_run.competitor_candidates[0]["maps_appearances"] == 12
    excluded = next(ref for ref in market_run.artifact_refs if ref["kind"] == "excluded_serp_landscape")
    assert any(item["reason"] == "directory_or_aggregator" for item in excluded["items"])


def test_competitor_approval_is_bounded_and_provenanced(tmp_path):
    repository, run, keyword_set = _setup(tmp_path)
    service = MarketEvidenceService(repository, lambda: FakeMarketProvider())
    market_run = service.start_pilot(insight_run_id=run.id, keyword_set_id=keyword_set.id)

    with pytest.raises(ValueError, match="between one and three"):
        service.approve_competitors(market_run.id, candidate_ids=[], operator="operator")
    approved = service.approve_competitors(
        market_run.id,
        candidate_ids=["tacomabjj.example"],
        operator="operator",
    )
    assert approved.state == "enriching"
    assert approved.approved_competitors[0]["approval_set_version"] == 1
    assert approved.approved_competitors[0]["approved_by"] == "operator"


def test_full_review_produces_38_organic_and_two_maps_deep_calls(tmp_path):
    repository, run, keyword_set = _setup(tmp_path, approve_all_risk=True)
    provider = FakeMarketProvider()
    service = MarketEvidenceService(repository, lambda: provider)
    assert service.preflight(keyword_set, phase="deep")["planned_calls"] == 40

    market_run = service.start_pilot(insight_run_id=run.id, keyword_set_id=keyword_set.id)
    market_run = service.approve_competitors(
        market_run.id,
        candidate_ids=["tacomabjj.example"],
        operator="operator",
    )
    before = Counter(call[0] for call in provider.calls)
    deep = service.deepen(market_run.id)
    after = Counter(call[0] for call in provider.calls)

    assert after["organic"] - before["organic"] == 38
    assert after["maps"] - before["maps"] == 2
    assert len(deep.organic_evidence) == 50
    assert len(deep.maps_evidence) == 14
    assert deep.phase == "deep"
    assert deep.state == "enriching"
    assert len(deep.provider_calls) == 65
    assert deep.id != market_run.id
    assert repository.get_market_evidence_run(market_run.id).state == "superseded"


def test_provider_failure_is_an_evidence_limit_not_zero(tmp_path):
    repository, run, keyword_set = _setup(tmp_path)
    pilot = KeywordSetService().select_pilot(keyword_set)
    provider = FakeMarketProvider(fail_keyword=pilot[0].keyword)
    service = MarketEvidenceService(repository, lambda: provider)

    market_run = service.start_pilot(insight_run_id=run.id, keyword_set_id=keyword_set.id)
    assert len(market_run.organic_evidence) == 11
    assert any(
        item["kind"] == "provider_failure" and item["query"] == pilot[0].keyword
        for item in market_run.evidence_limits
    )
    failed_call = next(item for item in market_run.provider_calls if item["status"] == "failed")
    assert failed_call["cost_usd"] == 0.0

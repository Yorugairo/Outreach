from types import SimpleNamespace

from src.models import (
    InsightReport,
    InsightRun,
    MarketEvidenceRun,
    PageRecord,
    SEOTarget,
    utc_now_iso,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.competitor_evidence_service import CompetitorEvidenceService
from src.services.page_analysis_service import PageAnalysisOutput


class FakePageAnalysis:
    def __init__(self):
        self.requests = []

    def crawl_site(self, target, insight_run_id, seed_urls, *, max_pages):
        self.requests.append((target.normalized_domain, list(seed_urls), max_pages))
        return PageAnalysisOutput(
            pages=[
                PageRecord(
                    insight_run_id=insight_run_id,
                    seo_target_id=target.id,
                    url=f"https://{target.normalized_domain}",
                    page_class="homepage",
                    http_status=200,
                    content_type="text/html",
                    title="Competitor BJJ Tacoma",
                    meta_description="Tacoma classes and schedule",
                    h1="Brazilian Jiu Jitsu in Tacoma",
                    schema_types=["LocalBusiness"],
                    word_count=900,
                    internal_links=[f"https://{target.normalized_domain}/schedule"],
                    ai_evidence={"first_text_after_headings": [{"heading": "Classes", "text": "Train today"}]},
                ),
                PageRecord(
                    insight_run_id=insight_run_id,
                    seo_target_id=target.id,
                    url=f"https://{target.normalized_domain}/program",
                    page_class="service",
                    http_status=200,
                    content_type="text/html",
                    title="BJJ Program",
                    meta_description="Beginner classes",
                    h1="BJJ Program",
                    schema_types=["Service"],
                    word_count=750,
                    internal_links=[f"https://{target.normalized_domain}/trial"],
                    ai_evidence={"direct_answer_blocks": [{"heading": "Start", "answer_excerpt": "Book a trial."}]},
                ),
            ],
            attempted_count=2,
            discovered_count=2,
        )


class FakeSitemap:
    def discover(self, domain):
        return SimpleNamespace(sitemap_urls=[], errors=[])


class FakeAuthority:
    def __init__(self):
        self.domains = []

    def collect_offsite_authority(self, domain):
        self.domains.append(domain)
        return {
            "status": "complete",
            "target_domain": domain,
            "source": "dataforseo_backlinks_summary_live",
            "snapshot_date": "2026-07-25",
            "link_rank": 30,
            "provider_cost_usd": 0.02,
            "raw_artifact_ref": f"raw/{domain}.json",
        }


class FakeScreenshots:
    def __init__(self):
        self.requests = []

    def capture(self, **request):
        self.requests.append(request)
        return {
            "capture_status": "complete",
            "url": request["url"],
            "final_url": request["url"],
            "http_status": 200,
            "viewport": {"name": request["viewport_name"]},
            "captured_at": "2026-07-25T12:00:00+00:00",
            "artifact_path": f"screenshots/{request['artifact_name']}",
            "caption": request["caption"],
            "source": "fake_playwright",
            "participates_in_scoring": False,
        }


def _setup(tmp_path):
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
    repository.save_page_record(PageRecord(
        insight_run_id=run.id,
        seo_target_id=target.id,
        url="https://novaryu.com/program",
        page_class="service",
        http_status=200,
        content_type="text/html",
        title="Nova Program",
        meta_description=None,
        h1=None,
        schema_types=[],
        word_count=200,
        internal_links=[],
    ))
    repository.save_report(InsightReport(
        insight_run_id=run.id,
        seo_target_id=target.id,
        report_version="v2",
        report_payload={"offsite_authority": {"status": "complete", "link_rank": 10}},
    ))

    from src.services.keyword_set_service import KeywordSetService
    keywords = KeywordSetService(repository)
    keyword_set = keywords.approve(keywords.seed_tacoma_bjj(), operator="operator")
    market_run = MarketEvidenceRun(
        insight_run_id=run.id,
        insight_attempt_id=run.attempt_id,
        keyword_set_id=keyword_set.id,
        keyword_set_version=keyword_set.keyword_set_key,
        target_domain="novaryu.com",
        target_entity_name="Nova Ryu",
        vertical_id=keyword_set.vertical_id,
        market=keyword_set.market,
        location_code=keyword_set.location_code,
        state="enriching",
        organic_evidence=[{
            "keyword": "bjj tacoma",
            "category": "Primary Local Core",
            "search_intent": "Commercial / Transactional",
            "optimization_focus": "SEO",
            "target_page_usage": "Homepage / Main Landing",
            "target_rank": 7,
            "target_url": "https://novaryu.com/program",
            "raw_artifact_ref": "raw/organic.json",
            "results": [
                {"rank": 2, "url": "https://competitor.example/program", "title": "Competitor"},
                {"rank": 7, "url": "https://novaryu.com/program", "title": "Nova Ryu"},
            ],
        }],
        maps_evidence=[{
            "keyword": "bjj tacoma",
            "category": "Primary Local Core",
            "search_intent": "Commercial / Transactional",
            "optimization_focus": "SEO",
            "target_page_usage": "Homepage / Main Landing",
            "target_rank": None,
            "target_url": None,
            "raw_artifact_ref": "raw/maps.json",
            "results": [
                {"rank": 1, "website": "https://competitor.example", "title": "Competitor"},
            ],
        }],
        keyword_metrics=[{"keyword": "bjj tacoma", "search_volume": 500}],
        competitor_candidates=[{
            "candidate_id": "competitor.example",
            "domain": "competitor.example",
            "name": "Competitor",
            "observations": [
                {"keyword": "bjj tacoma", "source_type": "organic", "rank": 2, "url": "https://competitor.example/program"},
            ],
        }],
        approved_competitors=[{
            "candidate_id": "competitor.example",
            "domain": "competitor.example",
            "name": "Competitor",
            "approval_set_version": 1,
            "approved_by": "operator",
            "approved_at": utc_now_iso(),
            "observations": [
                {"keyword": "bjj tacoma", "source_type": "organic", "rank": 2, "url": "https://competitor.example/program"},
            ],
        }],
    )
    repository.save_market_evidence_run(market_run)
    return repository, run, market_run


def test_bounded_competitor_enrichment_gap_and_screenshot_contract(tmp_path):
    repository, _, market_run = _setup(tmp_path)
    analyzer = FakePageAnalysis()
    authority = FakeAuthority()
    screenshots = FakeScreenshots()
    service = CompetitorEvidenceService(
        repository,
        page_analysis_factory=lambda: analyzer,
        sitemap_factory=FakeSitemap,
        authority_provider_factory=lambda: authority,
        screenshot_service=screenshots,
    )

    enriched = service.enrich(market_run.id, target_program_url="https://novaryu.com/program")

    assert enriched.state == "partial"
    assert enriched.actual_provider_cost == 0.02
    assert authority.domains == ["competitor.example"]
    assert analyzer.requests[0][2] == 10
    competitor = enriched.competitor_evidence[0]
    assert competitor["pages_collected"] == 2
    assert competitor["page_cap"] == 10
    assert competitor["no_competitor_score"] is True
    assert "score" not in competitor
    assert len(enriched.screenshots) == 4
    assert all(item["participates_in_scoring"] is False for item in enriched.screenshots)
    row = enriched.gap_matrix[0]
    assert {"local_pack_gap", "near_win", "conversion_gap", "authority_gap"} <= set(row["opportunity_classes"])
    assert row["why_they_may_be_winning"]
    assert len(enriched.recommended_gaps) == 1
    assert enriched.recommended_gaps[0]["ranking_promise"] is False
    assert repository.get_market_evidence_run(enriched.id).gap_matrix


def test_capture_failure_is_limit_not_enrichment_failure(tmp_path):
    repository, _, market_run = _setup(tmp_path)

    class FailedScreenshots(FakeScreenshots):
        def capture(self, **request):
            value = super().capture(**request)
            value.update(capture_status="failed", artifact_path=None, error="browser unavailable")
            return value

    service = CompetitorEvidenceService(
        repository,
        page_analysis_factory=FakePageAnalysis,
        sitemap_factory=FakeSitemap,
        screenshot_service=FailedScreenshots(),
    )
    enriched = service.enrich(market_run.id)
    assert enriched.state == "partial"
    assert enriched.competitor_evidence
    assert any(item["kind"] == "screenshot_capture_failed" for item in enriched.evidence_limits)

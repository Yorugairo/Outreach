from src.models import PageRecord
from src.services.ai_readiness_service import (
    AIReadinessService,
    COHORT_WEIGHTS,
    DIMENSION_WEIGHTS,
    SCORE_VERSION,
)
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.search_intelligence_service import SearchIntelligenceOutput


def _page(url: str, page_class: str, *, evidence: dict | None = None) -> PageRecord:
    return PageRecord(
        insight_run_id="run-1",
        seo_target_id="target-1",
        url=url,
        page_class=page_class,
        fetch_status="fetched",
        http_status=200,
        indexable=True,
        word_count=300,
        ai_evidence=evidence or {
            "direct_answer_count": 1,
            "heading_hierarchy_valid": True,
            "list_count": 1,
            "table_count": 0,
            "structured_block_count": 1,
            "question_heading_count": 2,
            "entity_names": ["Example Co"],
            "author_names": ["Alex Expert"],
            "external_citation_count": 1,
            "published_dates": ["2026-07-01"],
            "specific_evidence_count": 1,
            "json_ld_valid": True,
            "json_ld_visible_alignment": True,
        },
    )


def test_scoring_contract_is_versioned_and_weights_are_frozen():
    assert SCORE_VERSION == "ai-readiness.v2"
    assert DIMENSION_WEIGHTS == {"aeo": 40.0, "geo": 35.0, "aio": 25.0}
    assert COHORT_WEIGHTS == {"core": 60.0, "supporting": 40.0}


def test_missing_paid_corroboration_is_unknown_not_zero():
    output = AIReadinessService().build(
        CrawlDiscoveryOutput(
            robots_url="https://example.com/robots.txt",
            robots_status=200,
            candidate_page_urls=["https://example.com/"],
            robots_access={"googlebot": True, "bingbot": True, "oai-searchbot": True},
        ),
        PageAnalysisOutput(pages=[_page("https://example.com/", "homepage")]),
        SearchIntelligenceOutput(
            configured=False,
            approved=False,
            skipped_reason="not configured",
            payload={},
        ),
        page_limit=100,
    )
    check = next(
        item
        for item in output.cohorts["core"]["dimensions"]["geo"]["checks"]
        if item["id"] == "external_corroboration"
    )
    assert check["status"] == "unknown"
    assert check["score"] is None
    assert output.cohorts["supporting"]["score"] is None
    assert output.score is not None
    assert output.completeness_percent < 100
    assert output.customer_claim_eligible is False
    assert output.presentation_label.startswith("Provisional")
    direct = next(
        item
        for item in output.cohorts["core"]["dimensions"]["aeo"]["checks"]
        if item["id"] == "direct_answers"
    )
    assert direct["evidence_refs"][0]["field"] == "ai_evidence.direct_answer_count"
    assert isinstance(direct["evidence_refs"][0]["observed"], int)


def test_core_and_supporting_cohorts_share_one_evidence_set():
    pages = [
        _page("https://example.com/", "homepage"),
        _page("https://example.com/resources/guide", "blog_resource"),
    ]
    output = AIReadinessService().build(
        CrawlDiscoveryOutput(
            robots_url="https://example.com/robots.txt",
            robots_status=200,
            candidate_page_urls=[page.url for page in pages],
            robots_access={"googlebot": True, "bingbot": True, "oai-searchbot": True},
        ),
        PageAnalysisOutput(pages=pages, discovered_count=2, attempted_count=2),
        SearchIntelligenceOutput(
            configured=True,
            approved=True,
            skipped_reason=None,
            payload={"external_mentions": [{"domain": "industry.example"}]},
        ),
        page_limit=100,
    )
    assert output.inventory["core_pages"] == 1
    assert output.inventory["supporting_pages"] == 1
    assert output.inventory["collected_pages"] <= output.inventory["attempted_pages"] <= output.inventory["discovered_pages"]
    assert output.score == 90.9
    assert output.status == "complete"
    assert output.customer_claim_eligible is True


def test_failed_external_mention_queries_remain_unknown():
    search = SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        payload={
            "mention_queries": ['"Example" -site:example.com'],
            "external_mentions": [],
            "provider_errors": [{
                "operation": "external_mention_serp",
                "status_code": 40101,
                "status_message": "Internal SE Server Error.",
            }],
        },
    )

    score, measured = AIReadinessService._mention_score(search)

    assert score == 0.0
    assert measured is False


def test_capped_crawl_makes_clean_link_health_unknown():
    output = AIReadinessService().build(
        CrawlDiscoveryOutput(
            robots_url="https://example.com/robots.txt",
            robots_status=200,
            candidate_page_urls=["https://example.com/", "https://example.com/unvisited"],
            robots_access={"googlebot": True, "bingbot": True, "oai-searchbot": True},
        ),
        PageAnalysisOutput(
            pages=[_page("https://example.com/", "homepage")],
            discovered_count=2,
            attempted_count=1,
            capped=True,
        ),
        SearchIntelligenceOutput(
            configured=False,
            approved=False,
            skipped_reason="not configured",
            payload={},
        ),
        page_limit=1,
    )
    check = next(
        item
        for item in output.cohorts["core"]["dimensions"]["aio"]["checks"]
        if item["id"] == "link_health"
    )
    assert check["status"] == "unknown"
    assert check["score"] is None

from src.models import PageRecord
from src.services.ai_readiness_service import AIReadinessV3Service
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.search_intelligence_service import SearchIntelligenceOutput


def test_every_measured_v3_check_has_a_persisted_artifact_reference():
    page = PageRecord(
        id="page-1",
        insight_run_id="run-1",
        seo_target_id="target-1",
        url="https://example.com/",
        page_class="homepage",
        fetch_status="fetched",
        http_status=200,
        indexable=True,
        internal_links=[],
        ai_evidence={
            "headings": [
                {"level": 1, "text": "Example"},
                {"level": 2, "text": "What is beginner BJJ?"},
            ],
            "direct_answer_blocks": [
                {
                    "heading": "What is beginner BJJ?",
                    "answer_excerpt": "Beginner BJJ introduces positional fundamentals.",
                }
            ],
            "list_count": 1,
            "table_count": 0,
            "table_header_count": 0,
            "entity_names": ["Example"],
            "json_ld_valid": True,
            "json_ld_visible_alignment": True,
            "json_ld_alignment": [{"type": "Organization", "aligned": True}],
            "http_text_word_count": 250,
            "main_content_word_count": 200,
            "main_content_ratio": 0.8,
            "in_navigation": True,
        },
    )
    output = AIReadinessV3Service().build(
        CrawlDiscoveryOutput(
            robots_url="https://example.com/robots.txt",
            robots_status=200,
            candidate_page_urls=[page.url],
            robots_access={
                "googlebot": True,
                "bingbot": True,
                "oai-searchbot": True,
            },
        ),
        PageAnalysisOutput(pages=[page], discovered_count=1, attempted_count=1),
        SearchIntelligenceOutput(
            configured=True,
            approved=True,
            skipped_reason=None,
            payload={
                "keywords": [{"keyword": "beginner bjj"}],
                "mention_queries": ['"Example" -site:example.com'],
                "external_mentions": [],
            },
        ),
        page_limit=100,
        attempt_id="attempt-1",
    )

    for cohort in output.cohorts.values():
        for dimension in cohort["dimensions"].values():
            for check in dimension["checks"]:
                if check["status"] != "measured":
                    continue
                assert (
                    check.get("evidence_refs")
                    or check.get("evidence_field")
                    or check["id"]
                    in {"crawler_access", "link_health", "external_corroboration"}
                ), check["id"]

from src.models import AI_READINESS_V3_VERSION, PageRecord
from src.services.ai_readiness_service import AIReadinessV3Service
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.search_intelligence_service import SearchIntelligenceOutput


def _page(
    url: str,
    page_class: str,
    *,
    direct_answers: int = 2,
    evidence_overrides: dict | None = None,
) -> PageRecord:
    headings = [
        {"level": 1, "text": "Example Jiu Jitsu"},
        {"level": 2, "text": "What should a beginner expect?"},
        {"level": 2, "text": "How do kids classes work?"},
    ]
    evidence = {
        "headings": headings,
        "h1_count": 1,
        "direct_answer_blocks": [
            {
                "heading": heading["text"],
                "answer_excerpt": "A direct and useful answer for a prospective student.",
            }
            for heading in headings[1 : 1 + direct_answers]
        ],
        "list_count": 2,
        "table_count": 1,
        "table_header_count": 1,
        "structured_block_count": 3,
        "entity_names": ["Example Jiu Jitsu"],
        "author_names": ["Alex Coach"],
        "external_citation_count": 2,
        "external_citations": [
            "https://source-one.example/fact",
            "https://source-two.example/fact",
        ],
        "published_dates": ["2026-07-01"],
        "specific_evidence_count": 2,
        "specific_evidence_excerpts": ["Serving 150 members for 10 years."],
        "json_ld_valid": True,
        "json_ld_visible_alignment": True,
        "json_ld_alignment": [{"type": "SportsActivityLocation", "aligned": True}],
        "http_text_word_count": 400,
        "main_content_word_count": 320,
        "main_content_ratio": 0.8,
        "in_navigation": page_class == "homepage",
    }
    evidence.update(evidence_overrides or {})
    return PageRecord(
        id=f"page-{page_class}-{url.rsplit('/', 1)[-1] or 'home'}",
        insight_run_id="run-1",
        seo_target_id="target-1",
        url=url,
        page_class=page_class,
        fetch_status="fetched",
        http_status=200,
        indexable=True,
        word_count=400,
        internal_links=["https://example.com/contact"],
        ai_evidence=evidence,
    )


def _crawl(urls: list[str]) -> CrawlDiscoveryOutput:
    return CrawlDiscoveryOutput(
        robots_url="https://example.com/robots.txt",
        robots_status=200,
        candidate_page_urls=urls,
        robots_access={
            "googlebot": True,
            "bingbot": True,
            "oai-searchbot": True,
        },
    )


def _search(*domains: str) -> SearchIntelligenceOutput:
    return SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        payload={
            "keywords": [
                {"keyword": "beginner bjj classes"},
                {"keyword": "kids bjj classes"},
            ],
            "mention_queries": ['"Example Jiu Jitsu" -site:example.com'],
            "external_mentions": [
                {
                    "domain": domain,
                    "title": f"Example Jiu Jitsu profile {index}",
                    "exact_name_match": True,
                    "topic_match": True,
                }
                for index, domain in enumerate(domains)
            ],
        },
    )


def _check(output, cohort: str, dimension: str, check_id: str) -> dict:
    return next(
        check
        for check in output.cohorts[cohort]["dimensions"][dimension]["checks"]
        if check["id"] == check_id
    )


def test_v3_is_versioned_continuous_and_preserves_cohort_formula():
    pages = [
        _page("https://example.com/", "homepage"),
        _page(
            "https://example.com/resources/guide",
            "blog_resource",
            direct_answers=1,
        ),
    ]
    output = AIReadinessV3Service().build(
        _crawl([page.url for page in pages]),
        PageAnalysisOutput(
            pages=pages,
            discovered_count=2,
            attempted_count=2,
        ),
        _search("one.example", "two.example", "three.example", "four.example"),
        page_limit=100,
        attempt_id="attempt-1",
    )

    assert output.score_version == AI_READINESS_V3_VERSION
    assert output.score is not None
    assert output.dimensions["aeo"]["score"] is not None
    assert output.cohorts["core"]["score"] is not None
    assert output.cohorts["supporting"]["score"] is not None
    assert _check(output, "supporting", "aeo", "direct_answers")["score"] == 50.0
    expected = round(
        output.cohorts["core"]["score"] * 0.6
        + output.cohorts["supporting"]["score"] * 0.4,
        2,
    )
    assert output.score == expected


def test_one_external_domain_does_not_satisfy_corroboration():
    page = _page("https://example.com/", "homepage")
    output = AIReadinessV3Service().build(
        _crawl([page.url]),
        PageAnalysisOutput(pages=[page], discovered_count=1, attempted_count=1),
        _search("one.example"),
        page_limit=100,
    )

    check = _check(output, "core", "geo", "external_corroboration")
    assert check["status"] == "measured"
    assert check["score"] == 0.0
    assert "single source" in check["observation"]


def test_missing_paid_enrichment_is_unknown_and_does_not_become_zero():
    page = _page("https://example.com/", "homepage")
    output = AIReadinessV3Service().build(
        _crawl([page.url]),
        PageAnalysisOutput(pages=[page], discovered_count=1, attempted_count=1),
        SearchIntelligenceOutput(
            configured=False,
            approved=False,
            skipped_reason="not configured",
            payload={},
        ),
        page_limit=100,
    )

    check = _check(output, "core", "geo", "external_corroboration")
    assert check["status"] == "unknown"
    assert check["score"] is None
    assert output.cohorts["core"]["dimensions"]["geo"]["score"] is not None
    assert output.completeness_percent < 85
    assert output.customer_claim_eligible is False


def test_faq_and_howto_types_receive_no_automatic_boost():
    base = _page(
        "https://example.com/",
        "homepage",
        evidence_overrides={
            "json_ld_valid": True,
            "json_ld_visible_alignment": True,
            "json_ld_alignment": [{"type": "Organization", "aligned": True}],
        },
    )
    faq = _page(
        "https://example.com/",
        "homepage",
        evidence_overrides={
            "json_ld_valid": True,
            "json_ld_visible_alignment": True,
            "json_ld_alignment": [
                {"type": "FAQPage", "aligned": True},
                {"type": "HowTo", "aligned": True},
            ],
        },
    )
    service = AIReadinessV3Service()

    assert service._schema_alignment_page_score(base) == (100.0, 100.0)
    assert service._schema_alignment_page_score(faq) == (100.0, 100.0)


def test_capped_collection_blocks_customer_claim_eligibility():
    page = _page("https://example.com/", "homepage")
    output = AIReadinessV3Service().build(
        _crawl([page.url, "https://example.com/not-collected"]),
        PageAnalysisOutput(
            pages=[page],
            discovered_count=2,
            attempted_count=1,
            capped=True,
        ),
        _search("one.example", "two.example", "three.example", "four.example"),
        page_limit=1,
    )

    assert output.inventory["capped"] is True
    assert output.customer_claim_eligible is False
    assert any("safety ceiling" in warning for warning in output.warnings)

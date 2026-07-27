from src.services.search_visibility_service import SearchVisibilityService


def test_approved_demand_produces_context_bound_visibility_metrics():
    result = SearchVisibilityService().build(
        [{"keyword": "bjj tacoma", "search_volume": 100, "review_status": "approved"}],
        [{
            "keyword": "bjj tacoma",
            "status": "complete",
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
            "snapshot_date": "2026-07-26",
            "target_rank": 3,
        }],
        "novaryu.com",
        context={
            "market": "Tacoma, WA",
            "location_code": 1027773,
            "language_code": "en",
            "device": "desktop",
            "snapshot_date": "2026-07-26",
        },
    )
    assert result.version == "search-visibility.v2"
    assert result.status == "complete"
    assert result.metrics["tracked_keyword_coverage_percent"] == 100
    assert result.metrics["top_3_count"] == 1
    assert result.metrics["weighted_visibility"] == 98
    assert result.metrics["median_rank"] == 3


def test_context_mismatch_is_unknown_not_zero_visibility():
    result = SearchVisibilityService().build(
        [{"keyword": "bjj tacoma", "search_volume": 100, "review_status": "approved"}],
        [{
            "keyword": "bjj tacoma",
            "status": "complete",
            "market": "Seattle, WA",
            "language_code": "en",
            "device": "desktop",
            "snapshot_date": "2026-07-26",
            "target_rank": 1,
        }],
        "novaryu.com",
        context={
            "market": "Tacoma, WA",
            "language_code": "en",
            "device": "desktop",
            "snapshot_date": "2026-07-26",
        },
    )
    assert result.status == "unknown"
    assert result.metrics["tracked_keyword_coverage_percent"] == 0
    assert result.metrics["keywords"][0]["evidence_status"] == "unknown"


def test_unapproved_demand_never_enters_search_visibility():
    result = SearchVisibilityService().build(
        [{"keyword": "bjj tacoma", "search_volume": 100, "review_status": "needs_review"}],
        [{"keyword": "bjj tacoma", "status": "complete", "target_rank": 1}],
        "novaryu.com",
    )
    assert result.status == "unknown"
    assert result.score is None


def test_non_observation_in_a_complete_serp_is_measured_zero():
    result = SearchVisibilityService().build(
        [{"keyword": "bjj tacoma", "search_volume": 100, "review_status": "approved"}],
        [{
            "keyword": "bjj tacoma",
            "status": "complete",
            "market": "Tacoma, WA",
            "language_code": "en",
            "device": "desktop",
            "snapshot_date": "2026-07-26",
            "results": [],
        }],
        "novaryu.com",
        context={
            "market": "Tacoma, WA",
            "language_code": "en",
            "device": "desktop",
            "snapshot_date": "2026-07-26",
        },
    )
    assert result.status == "complete"
    assert result.metrics["evidence_keyword_count"] == 1
    assert result.metrics["top_10_count"] == 0
    assert result.metrics["weighted_visibility"] == 0

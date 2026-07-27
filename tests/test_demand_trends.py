from __future__ import annotations

from pathlib import Path

import pytest

from src.models import KeywordSet
from src.services.demand_trend_service import DemandTrendService


TRENDS_CSV = """Category: All categories
Country: United States

Week,bjj tacoma,Tacoma BJJ,isPartial
2026-01-04,50,40,FALSE
2026-02-01,70,60,FALSE
2026-03-01,90,80,FALSE
"""

PLANNER_CSV = """Keyword,Avg. monthly searches,Category,Search Intent,Target Page / Usage,Brand
bjj tacoma,100,Primary Local Core,Commercial,Home,No
Tacoma BJJ,80,Primary Local Core,Commercial,Home,No
"""


def test_google_trends_preview_is_relative_context_bound_and_deterministic() -> None:
    service = DemandTrendService()
    kwargs = {
        "source": "google_trends_csv",
        "prospect_id": "prospect-1",
        "vertical_id": "national_bjj_registry",
        "market": "Tacoma, WA",
        "period_start": "2026-01-01",
        "period_end": "2026-03-31",
        "location_code": 1027773,
    }

    first = service.preview_csv(TRENDS_CSV, **kwargs)
    second = service.preview_csv(TRENDS_CSV, **kwargs)

    assert first.valid is True
    assert first.source_sha256 == second.source_sha256
    assert [term["term_id"] for term in first.terms] == [term["term_id"] for term in second.terms]
    assert first.context_sha256 and len(first.context_sha256) == 64
    assert "relative interest index" in first.context["metric_semantics"]
    term = first.terms[0]
    assert term["metrics"]["relative_interest"] == 70
    assert term["trend_direction"] == "rising"
    assert term["seasonality"]["peak_period"] == "2026-03-01"
    assert all("unique searchers" not in str(term).casefold() for term in first.terms)

    snapshot = service.commit(first)
    assert snapshot.state == "draft"
    assert snapshot.source == "google_trends_csv"
    assert snapshot.context["source_sha256"] == first.source_sha256
    assert snapshot.context["timeframe"] == {"period_start": "2026-01-01", "period_end": "2026-03-31"}
    assert service.repository is None


def test_planner_close_variants_are_grouped_and_approval_is_explicit() -> None:
    service = DemandTrendService()
    preview = service.preview_csv(
        PLANNER_CSV,
        source="keyword_planner_csv",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        period_start="2026-07",
        period_end="2026-07",
        location_code=1027773,
    )

    assert preview.valid is True
    assert len(preview.terms) == 2
    assert len(preview.groups) == 1
    group = preview.groups[0]
    assert group["aggregation_rule"] == "max_close_variant"
    assert group["aggregation_status"] == "requires_operator_review"
    assert group["approved_monthly_search_occasions"] == 100
    assert group["excluded_duplicate_terms"]
    assert "people" in preview.terms[0]["semantics"]

    draft = service.commit(preview)
    assert draft.state == "draft"
    assert draft.context["aggregation_status"] == "requires_operator_review"

    approved_preview = service.preview_csv(
        PLANNER_CSV,
        source="keyword_planner_csv",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        period_start="2026-07",
        period_end="2026-07",
        location_code=1027773,
        aggregation_rule="sum_distinct_intents",
        operator_approved=True,
        operator="operator",
    )
    assert approved_preview.valid is True
    assert approved_preview.groups[0]["aggregation_status"] == "approved"
    assert approved_preview.groups[0]["approved_monthly_search_occasions"] == 180
    approved = service.commit(approved_preview)
    assert approved.state == "approved"
    assert approved.approved_by == "operator"


def test_trend_import_rejects_paths_formula_cells_pii_and_unique_claims() -> None:
    service = DemandTrendService()
    with pytest.raises(ValueError, match="paths"):
        service.preview_csv(Path("..\\secrets.csv"))

    unsafe = """Week,Email,bjj tacoma
2026-01-01,person@example.com,=100
"""
    preview = service.preview_csv(
        unsafe,
        source="google_trends_csv",
        prospect_id="prospect-1",
        vertical_id="vertical-1",
        market="Tacoma, WA",
        period_start="2026-01-01",
        period_end="2026-01-31",
    )
    assert preview.valid is False
    assert any("PII" in issue.message for issue in preview.errors)
    assert any("formula" in issue.message for issue in preview.errors)

    unique_claim = """Keyword,Relative interest
bjj tacoma,unique searchers
"""
    preview = service.preview_csv(
        unique_claim,
        source="google_trends_csv",
        prospect_id="prospect-1",
        vertical_id="vertical-1",
        market="Tacoma, WA",
        period_start="2026-01-01",
        period_end="2026-01-31",
    )
    assert preview.valid is False
    assert any("unique-person" in issue.message for issue in preview.errors)


def test_factual_risk_keyword_stays_needs_review_in_trend_terms() -> None:
    keyword_set = KeywordSet(
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        location_code=1027773,
        source_sha256="a" * 64,
        keyword_targets=[
            {
                "keyword": "no gi bjj tacoma",
                "category": "Specialty Programs",
                "search_intent": "Commercial",
                "optimization_focus": "SEO",
                "target_page_usage": "Programs",
                "review_status": "needs_review",
                "review_reasons": ["unsupported_program_claim"],
            }
        ],
    )
    csv_text = """Keyword,Avg. monthly searches,Category,Search Intent,Target Page / Usage
no gi bjj tacoma,100,Specialty Programs,Commercial,Programs
"""
    preview = DemandTrendService().preview_csv(
        csv_text,
        source="keyword_planner_csv",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        period_start="2026-07",
        period_end="2026-07",
        keyword_set=keyword_set,
    )
    assert preview.valid is True
    assert preview.terms[0]["review_status"] == "needs_review"
    assert preview.terms[0]["supported"] is False
    assert preview.groups == []


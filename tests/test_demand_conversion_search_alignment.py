from __future__ import annotations

import pytest

from src.models import (
    DemandEvidenceRow,
    DemandEvidenceSet,
    DemandGroup,
    OwnedMeasurementSnapshot,
)
from src.services.demand_conversion_search_service import (
    DemandConversionSearchService,
)


SHA = "a" * 64


def _approved_demand() -> DemandEvidenceSet:
    rows = [
        DemandEvidenceRow(
            id="row-primary",
            keyword="bjj tacoma",
            market="Tacoma, WA",
            source="keyword_planner_csv",
            snapshot_period="2026-07",
            match_semantics="close_variant",
            monthly_searches=120,
        ),
        DemandEvidenceRow(
            id="row-kids",
            keyword="kids bjj tacoma",
            market="Tacoma, WA",
            source="keyword_planner_csv",
            snapshot_period="2026-07",
            match_semantics="close_variant",
            monthly_searches=80,
        ),
    ]
    groups = [
        DemandGroup(
            id="group-primary",
            intent_family="primary",
            included_keyword_ids=["row-primary"],
            representative_term="bjj tacoma",
            aggregation_rule="max_close_variant",
            approved_monthly_search_occasions=120,
            reviewer="operator",
            rationale="Reviewed primary-intent family.",
            status="approved",
        ),
        DemandGroup(
            id="group-kids",
            intent_family="kids_family",
            included_keyword_ids=["row-kids"],
            representative_term="kids bjj tacoma",
            aggregation_rule="max_close_variant",
            approved_monthly_search_occasions=80,
            reviewer="operator",
            rationale="Reviewed family-intent family.",
            status="approved",
        ),
    ]
    return DemandEvidenceSet(
        id="demand-1",
        prospect_id="prospect-1",
        keyword_set_id="keywords-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        source_sha256=SHA,
        rows=[row.to_dict() for row in rows],
        groups=[group.to_dict() for group in groups],
        state="approved",
        approved_by="operator",
        approved_at="2026-07-26T12:00:00+00:00",
    )


def _gsc(
    snapshot_id: str,
    query: str,
    *,
    impressions: int,
    clicks: int,
    position: float,
    market: str = "Tacoma, WA",
) -> OwnedMeasurementSnapshot:
    return OwnedMeasurementSnapshot(
        id=snapshot_id,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source="gsc_csv",
        period_start="2026-06-01",
        period_end="2026-06-30",
        source_sha256=SHA,
        context={
            "market": market,
            "query": query,
            "page": "https://novaryu.com/programs/bjj",
            "device": "mobile",
        },
        metrics={
            "impressions": impressions,
            "clicks": clicks,
            "position": position,
        },
        artifact_ref=f"owned/{snapshot_id}.json",
    )


def test_aligns_observed_queries_and_public_rankings_to_reviewed_groups() -> None:
    output = DemandConversionSearchService().align(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=_approved_demand(),
        owner_snapshots=[
            _gsc("gsc-1", "bjj tacoma", impressions=100, clicks=10, position=8),
            _gsc(
                "gsc-2",
                "kids bjj tacoma",
                impressions=40,
                clicks=4,
                position=11,
            ),
        ],
        public_rankings=[
            {
                "keyword": "bjj tacoma",
                "position": 12,
                "url": "https://novaryu.com/",
                "snapshot_date": "2026-07-26",
                "evidence_ref": {"artifact_ref": "market/organic-1.json"},
            }
        ],
    )

    by_family = {row["intent_family"]: row for row in output["groups"]}
    assert output["status"] == "complete"
    assert by_family["primary"]["observed_search_console"] == {
        "impressions": 100,
        "clicks": 10,
        "ctr": 0.1,
        "average_position": 8.0,
        "provenance_label": "observed",
    }
    assert by_family["primary"]["ranking_observations"][0]["position"] == 12
    assert by_family["primary"]["evidence_refs"][0]["id"] == "gsc-1"
    assert by_family["kids_family"]["queries"][0]["match_kind"] == "exact"


def test_close_variant_match_is_deterministic_and_ambiguous_queries_are_retained() -> None:
    output = DemandConversionSearchService().align(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=_approved_demand(),
        owner_snapshots=[
            _gsc(
                "gsc-1",
                "tacoma bjj",
                impressions=20,
                clicks=1,
                position=15,
            ),
            _gsc(
                "gsc-2",
                "martial arts",
                impressions=10,
                clicks=0,
                position=30,
            ),
        ],
    )

    primary = next(
        row for row in output["groups"] if row["intent_family"] == "primary"
    )
    assert primary["queries"][0]["match_kind"] == "close_variant"
    assert output["unmatched_queries"][0]["query"] == "martial arts"


def test_context_mismatch_and_unapproved_demand_fail_closed() -> None:
    with pytest.raises(ValueError, match="market does not match"):
        DemandConversionSearchService().align(
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
            demand=_approved_demand(),
            owner_snapshots=[
                _gsc(
                    "gsc-1",
                    "bjj tacoma",
                    impressions=10,
                    clicks=1,
                    position=10,
                    market="Houston, TX",
                )
            ],
        )

    demand = _approved_demand()
    demand.state = "review"
    with pytest.raises(ValueError, match="approved demand"):
        DemandConversionSearchService().align(
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
            demand=demand,
        )


def test_missing_owner_data_is_unknown_not_zero() -> None:
    output = DemandConversionSearchService().align(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=_approved_demand(),
    )

    assert output["status"] == "limited"
    assert output["completeness_percent"] == 0
    assert "unavailable" in output["limitations"][0]
    assert all(
        row["observed_search_console"]["average_position"] is None
        for row in output["groups"]
    )

from __future__ import annotations

from dataclasses import replace

import pytest

from src.models import (
    CONVERSION_EVENT_MAP_VERSION,
    DEMAND_CONVERSION_FORMULA_VERSION,
    DEMAND_CONVERSION_REPORT_VERSION,
    DEMAND_CONVERSION_SOURCE_CLASSES,
    DEMAND_CONVERSION_VERSION,
    DEMAND_TREND_VERSION,
    ConversionEventMap,
    DemandConversionEvidence,
    DemandConversionReportSnapshot,
    DemandTrendSnapshot,
    canonical_sha256,
)


SHA = "a" * 64


def _source(
    *,
    source_class: str = "public_observed",
    provenance_label: str = "observed",
) -> dict:
    return {
        "source_name": "bounded_crawl",
        "source_class": source_class,
        "hierarchy_level": DEMAND_CONVERSION_SOURCE_CLASSES[source_class],
        "provenance_label": provenance_label,
        "source_sha256": SHA,
        "artifact_ref": "runs/run-1/reports/v2.json",
        "snapshot_date": "2026-07-26",
        "prospect_id": "prospect-1",
        "vertical_id": "national_bjj_registry",
        "market": "Tacoma, WA",
    }


def _evidence(**changes) -> DemandConversionEvidence:
    payload = {
        "insight_run_id": "run-1",
        "prospect_id": "prospect-1",
        "vertical_id": "national_bjj_registry",
        "mode": "prospect",
        "market": "Tacoma, WA",
        "source_snapshots": [_source()],
        "intent_groups": [
            {
                "intent_family": "primary",
                "representative_term": "bjj tacoma",
                "monthly_search_occasions": 120,
                "provenance_label": "supplied",
            }
        ],
        "observed_inputs": {"organic_impressions": None},
        "modeled_outputs": {},
        "economics": {"monthly_price": 100},
        "capacity": {"available_customers": 20},
        "completeness_percent": 35,
        "status": "limited",
        "warnings": ["Search volume represents occasions, not people."],
        "evidence_refs": [{"artifact_ref": "runs/run-1/reports/v2.json"}],
    }
    payload.update(changes)
    return DemandConversionEvidence(**payload)


def test_contract_versions_and_prospect_payload_are_stable() -> None:
    evidence = _evidence()

    assert evidence.contract_version == DEMAND_CONVERSION_VERSION
    assert evidence.formula_version == DEMAND_CONVERSION_FORMULA_VERSION
    assert evidence.mode == "prospect"
    assert evidence.status == "limited"
    assert evidence.to_dict()["source_snapshots"][0]["hierarchy_level"] == 4


def test_prospect_mode_rejects_owner_first_party_and_unique_people_claims() -> None:
    with pytest.raises(ValueError, match="prospect mode"):
        _evidence(
            source_snapshots=[
                _source(
                    source_class="owner_first_party",
                    provenance_label="observed",
                )
            ]
        )

    with pytest.raises(ValueError, match="unique people"):
        _evidence(
            intent_groups=[
                {
                    "intent_family": "primary",
                    "unique_searchers": 50,
                }
            ]
        )


def test_owner_verified_mode_requires_context_bound_owner_evidence() -> None:
    with pytest.raises(ValueError, match="requires owner-first-party"):
        _evidence(mode="owner_verified")

    evidence = _evidence(
        mode="owner_verified",
        completeness_percent=90,
        status="complete",
        source_snapshots=[
            _source(
                source_class="owner_first_party",
                provenance_label="observed",
            ),
            _source(),
        ],
        observed_inputs={"gsc_clicks": 37, "ga4_sessions": 81},
    )
    assert evidence.status == "complete"

    mismatched = evidence.to_dict()
    mismatched["source_snapshots"][0]["prospect_id"] = "other"
    with pytest.raises(ValueError, match="prospect does not match"):
        DemandConversionEvidence(**mismatched)


def test_completeness_status_and_modeled_source_are_enforced() -> None:
    with pytest.raises(ValueError, match="status must match"):
        _evidence(completeness_percent=90, status="limited")

    with pytest.raises(ValueError, match="scenario source"):
        _evidence(modeled_outputs={"base": {"incremental_members": 3}})

    modeled = _evidence(
        source_snapshots=[
            _source(),
            _source(source_class="scenario_model", provenance_label="modeled"),
        ],
        modeled_outputs={"base": {"incremental_members": 3}},
    )
    assert modeled.modeled_outputs["base"]["incremental_members"] == 3


def test_trend_event_map_and_report_snapshot_contracts() -> None:
    trend = DemandTrendSnapshot(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        source="google_trends_csv",
        period_start="2025-07-01",
        period_end="2026-06-30",
        source_sha256=SHA,
        artifact_ref="demand_trends/trend-1.json",
        terms=[
            {
                "keyword": "bjj tacoma",
                "intent_family": "primary",
                "provenance_label": "observed",
                "metrics": {"relative_interest": 72},
            }
        ],
    )
    assert trend.contract_version == DEMAND_TREND_VERSION

    event_map = ConversionEventMap(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        mappings={
            "visit": ["sessions"],
            "lead": ["start_signup"],
            "customer": ["new_members"],
        },
        source_snapshot_ids=["gsc-1", "ga4-1", "crm-1"],
    )
    assert event_map.contract_version == CONVERSION_EVENT_MAP_VERSION

    payload_hash = canonical_sha256({"report_contract": "demand-conversion-v1"})
    report = DemandConversionReportSnapshot(
        demand_conversion_evidence_id="evidence-1",
        run_id="run-1",
        mode="prospect",
        payload_sha256=payload_hash,
        payload_artifact_ref="runs/run-1/reports/demand-conversion-v1.json",
        source_hashes={"evidence": SHA},
        completeness_percent=35,
        status="limited",
    )
    assert report.report_contract == DEMAND_CONVERSION_REPORT_VERSION

    with pytest.raises(ValueError, match="relative interest"):
        replace(
            trend,
            terms=[
                {
                    "keyword": "bjj tacoma",
                    "intent_family": "primary",
                    "provenance_label": "observed",
                    "metrics": {"relative_interest": 101},
                }
            ],
        )


def test_invalid_provenance_hierarchy_and_approval_are_rejected() -> None:
    invalid = _source()
    invalid["provenance_label"] = "estimated"
    with pytest.raises(ValueError, match="provenance"):
        _evidence(source_snapshots=[invalid])

    invalid = _source()
    invalid["hierarchy_level"] = 1
    with pytest.raises(ValueError, match="hierarchy"):
        _evidence(source_snapshots=[invalid])

    with pytest.raises(ValueError, match="operator provenance"):
        replace(_evidence(), state="approved")

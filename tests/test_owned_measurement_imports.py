from __future__ import annotations

from src.repositories.file_repository import FileBackedInsightRepository
from src.services.owned_measurement_service import OwnedMeasurementService


GSC_QUERY_CSV = """period_start,period_end,query,page,impressions,clicks,ctr,position,market,device
2026-06-01,2026-06-30,bjj tacoma,https://example.test/classes,1000,100,10%,4.2,Tacoma,desktop
"""
GBP_CSV = """period_start,period_end,action,views,website_clicks,calls,direction_requests,messages,market
2026-06-01,2026-06-30,profile,200,12,3,4,5,Tacoma
"""
GA4_EVENTS_CSV = """period_start,period_end,eventName,eventCount,keyEvents,sessions,users,purchaseRevenue,event_map_id,event_map_version,property_id
2026-06-01,2026-06-30,generate_lead,20,7,80,50,1000,map-1,1,ga4-property-1
"""
CRM_OUTCOMES_CSV = """period_start,period_end,funnel_stage,leads,bookings,customers,revenue,market
2026-06-01,2026-06-30,won,20,10,5,3000,Tacoma
"""


def _kwargs(source: str, context: dict[str, object]) -> dict[str, object]:
    return {
        "prospect_id": "prospect-1",
        "vertical_id": "national_bjj_registry",
        "source": source,
        "context": context,
    }


def test_source_specific_rows_keep_dimensions_and_aggregate_metrics(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    service = OwnedMeasurementService(repository)

    gsc = service.import_csv(GSC_QUERY_CSV, **_kwargs("gsc", {}))[0]
    gbp = service.import_csv(GBP_CSV, **_kwargs("gbp_performance", {}))[0]
    ga4 = service.import_csv(
        GA4_EVENTS_CSV,
        **_kwargs("ga4_events", {"property_id": "ga4-property-1"}),
    )[0]
    crm = service.import_csv(CRM_OUTCOMES_CSV, **_kwargs("crm_outcomes", {}))[0]

    assert gsc.context["query"] == "bjj tacoma"
    assert gsc.context["page"] == "https://example.test/classes"
    assert gsc.metrics["ctr"] == 10
    assert gsc.metrics["position"] == 4.2
    assert gbp.metrics == {
        "profile_views": 200,
        "clicks": 12,
        "calls": 3,
        "direction_requests": 4,
        "messages": 5,
    }
    assert ga4.context["event_name"] == "generate_lead"
    assert ga4.context["event_map_id"] == "map-1"
    assert ga4.context["event_map_version"] == "1"
    assert ga4.metrics["event_count"] == 20
    assert ga4.metrics["key_events"] == 7
    assert crm.context["funnel_stage"] == "won"
    assert crm.metrics["appointments"] == 10

    baseline = service.derive_funnel_baseline([gsc, ga4, crm])
    assert baseline["metrics"]["impressions"] == 1000
    assert baseline["metrics"]["total_users"] == 50
    assert baseline["metrics"]["signups_or_leads"] == 20
    assert baseline["metrics"]["attended_or_appointments"] == 10


def test_preview_and_commit_are_deterministic_and_duplicate_rows_are_rejected(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    service = OwnedMeasurementService(repository)
    kwargs = _kwargs("gsc_csv", {})

    first_preview = service.preview_csv(GSC_QUERY_CSV, **kwargs)
    second_preview = service.preview_csv(GSC_QUERY_CSV, **kwargs)
    assert first_preview.source_sha256 == second_preview.source_sha256
    assert [snapshot.id for snapshot in first_preview.snapshots] == [
        snapshot.id for snapshot in second_preview.snapshots
    ]
    assert [snapshot.metrics for snapshot in first_preview.snapshots] == [
        snapshot.metrics for snapshot in second_preview.snapshots
    ]
    assert [snapshot.context for snapshot in first_preview.snapshots] == [
        snapshot.context for snapshot in second_preview.snapshots
    ]
    first = service.commit(first_preview)
    second = service.commit(second_preview)
    assert first[0].id == second[0].id
    assert service.commit(second_preview)[0].id == first[0].id
    assert repository.get_owned_measurement_snapshot(first[0].id).to_dict() == first[0].to_dict()

    duplicate_csv = GSC_QUERY_CSV + GSC_QUERY_CSV.splitlines(True)[1]
    duplicate_preview = service.preview_csv(duplicate_csv, **kwargs)
    assert not duplicate_preview.valid
    assert any("duplicate" in issue.message for issue in duplicate_preview.issues)


def test_owner_consent_freshness_and_event_map_metadata_are_context_bound():
    service = OwnedMeasurementService()
    kwargs = _kwargs("ga4_csv", {"property_id": "ga4-property-1"})
    kwargs.update(
        {
            "owner_verified": True,
            "owner_consent": {
                "confirmed": True,
                "operator": "operator-1",
                "confirmed_at": "2026-07-26T12:00:00Z",
            },
            "data_freshness": {
                "status": "fresh",
                "snapshot_date": "2026-06-30",
                "age_days": 26,
            },
            "event_map_id": "map-1",
            "event_map_version": "1",
        }
    )
    snapshot = service.preview_csv(
        GA4_EVENTS_CSV,
        **kwargs,
    ).snapshots[0]
    assert snapshot.context["owner_consent"]["confirmed"] is True
    assert snapshot.context["data_freshness"]["snapshot_date"] == "2026-06-30"
    assert snapshot.context["event_map_id"] == "map-1"

    missing_consent = service.preview_csv(
        GA4_EVENTS_CSV,
        **_kwargs("ga4_csv", {"property_id": "ga4-property-1"}),
        owner_verified=True,
    )
    assert not missing_consent.valid
    assert any("consent" in issue.message for issue in missing_consent.issues)

    stale = service.preview_csv(
        GA4_EVENTS_CSV,
        **_kwargs("ga4_csv", {"property_id": "ga4-property-1"}),
        data_freshness={"status": "stale", "snapshot_date": "2024-01-01"},
    )
    assert not stale.valid
    assert any("stale" in issue.message for issue in stale.issues)


def test_scope_mismatch_pii_formula_and_credentials_are_rejected():
    service = OwnedMeasurementService()
    mismatched = (
        "period_start,period_end,prospect_id,vertical_id,market,impressions\n"
        "2026-06-01,2026-06-30,other-prospect,national_bjj_registry,Seattle,100\n"
    )
    preview = service.preview_csv(
        mismatched,
        **_kwargs("gsc_csv", {"market": "Tacoma"}),
    )
    assert not preview.valid
    assert any("prospect" in issue.message for issue in preview.issues)

    market_mismatch = mismatched.replace("other-prospect", "prospect-1")
    market_preview = service.preview_csv(
        market_mismatch,
        **_kwargs("gsc_csv", {"market": "Tacoma"}),
    )
    assert not market_preview.valid
    assert any("context" in issue.message for issue in market_preview.issues)

    unsafe = (
        "period_start,period_end,email,api_key,impressions\n"
        "2026-06-01,2026-06-30,person@example.test,secret,=100\n"
    )
    unsafe_preview = service.preview_csv(
        unsafe,
        **_kwargs("ga4_csv", {"property_id": "ga4-property-1"}),
    )
    assert not unsafe_preview.valid
    messages = " ".join(issue.message for issue in unsafe_preview.issues)
    assert "PII" in messages
    assert "credential" in messages
    assert "formula" in messages

    query_pii = service.preview_csv(
        "period_start,period_end,query,impressions,market\n"
        "2026-06-01,2026-06-30,owner@example.test,10,Tacoma\n",
        **_kwargs("gsc_csv", {}),
    )
    assert not query_pii.valid
    assert any("PII context values" in issue.message for issue in query_pii.issues)

    mismatched_property = service.preview_csv(
        GA4_EVENTS_CSV,
        **_kwargs("ga4_csv", {"property_id": "other-property"}),
    )
    assert not mismatched_property.valid
    assert any("context" in issue.message for issue in mismatched_property.issues)

from __future__ import annotations

import pytest

from src.models import (
    AI_READINESS_V3_DIMENSION_WEIGHTS,
    CLIENT_REPORT_BUNDLE_VERSION,
    PRODUCT_SURFACE_VERSIONS,
    REPORT_COMPARISON_VERSION,
    REPORT_SNAPSHOT_VERSION,
    TECHNICAL_SEO_CHECK_REGISTRY,
    TECHNICAL_SEO_FAMILY_WEIGHTS,
    ClientReportBundle,
    LocalVisibilityGridDefinition,
    OwnedMeasurementSnapshot,
    ProductSurfaceResult,
    PromptTopicSet,
    ReportAlias,
    ReportComparisonSnapshot,
    ReportSnapshot,
    ScoreCheckResult,
    canonical_sha256,
)


SHA_A = "a" * 64
SHA_B = "b" * 64


def test_seven_product_surfaces_are_versioned_and_never_universally_averaged() -> None:
    assert PRODUCT_SURFACE_VERSIONS == {
        "technical_seo_health": "seo-health.v2",
        "search_visibility": "search-visibility.v2",
        "local_visibility": "local-visibility.v1",
        "ai_readiness": "ai-readiness.v3",
        "observed_ai_visibility": "ai-visibility.v1",
        "conversion_readiness": "conversion-readiness.v1",
        "evidence_confidence": "evidence-confidence.v1",
    }
    assert "overall" not in PRODUCT_SURFACE_VERSIONS
    assert sum(TECHNICAL_SEO_FAMILY_WEIGHTS.values()) == pytest.approx(1.0)
    assert sum(AI_READINESS_V3_DIMENSION_WEIGHTS.values()) == pytest.approx(1.0)


def test_technical_registry_has_stable_versions_families_and_score_flags() -> None:
    assert TECHNICAL_SEO_CHECK_REGISTRY
    assert set(TECHNICAL_SEO_FAMILY_WEIGHTS) == {
        payload["family"] for payload in TECHNICAL_SEO_CHECK_REGISTRY.values()
    }
    for check_id, payload in TECHNICAL_SEO_CHECK_REGISTRY.items():
        assert check_id
        assert payload["version"] == 1
        assert payload["severity"] in {"critical", "high", "medium", "low", "info"}
        assert isinstance(payload["score_affecting"], bool)
        assert payload["page_classes"]


def test_unknown_and_inapplicable_checks_never_become_zero() -> None:
    unknown = ScoreCheckResult(
        check_id="field_page_experience",
        check_version=1,
        family="mobile_performance",
        severity="medium",
        status="unknown",
        score_affecting=True,
        limitations=["CrUX was unavailable."],
    )
    assert unknown.score is None
    assert unknown.to_dict()["status"] == "unknown"

    inapplicable = ScoreCheckResult(
        check_id="author_attribution",
        check_version=1,
        family="source_authority",
        severity="low",
        status="inapplicable",
        score_affecting=False,
    )
    assert inapplicable.applicable_page_ids == []

    with pytest.raises(ValueError, match="cannot have a score"):
        ScoreCheckResult(
            check_id="field_page_experience",
            check_version=1,
            family="mobile_performance",
            severity="medium",
            status="unknown",
            score_affecting=True,
            score=0,
        )


def test_surface_envelope_enforces_its_independent_version_and_unknown_semantics() -> None:
    result = ProductSurfaceResult(
        surface="search_visibility",
        version="search-visibility.v2",
        status="unknown",
        score=None,
        completeness_percent=0,
        evidence_confidence=0,
        warnings=["No approved keyword evidence exists."],
    )
    assert result.to_dict()["score"] is None
    with pytest.raises(ValueError, match="unsupported search_visibility version"):
        ProductSurfaceResult(
            surface="search_visibility",
            version="seo-health.v2",
            status="unknown",
            score=None,
            completeness_percent=0,
            evidence_confidence=0,
        )


def test_report_snapshot_alias_and_bundle_contracts_are_separate() -> None:
    snapshot = ReportSnapshot(
        run_id="run-1",
        attempt_id="attempt-1",
        report_contract="operator-v5",
        schema_version=1,
        source_snapshot_ids={"seo": "seo-1"},
        source_hashes={"seo": SHA_A},
        renderer_version="operator-renderer.v1",
        payload_sha256=SHA_B,
        payload_artifact_ref="snapshots/report.json",
        completeness_percent=90,
        status="complete",
    )
    alias = ReportAlias(
        run_id="run-1",
        report_contract="operator-v5",
        alias="latest",
        snapshot_id=snapshot.id,
    )
    bundle = ClientReportBundle(
        report_snapshot_id=snapshot.id,
        run_id="run-1",
        manifest_sha256=SHA_A,
        manifest_artifact_ref="bundles/bundle-1/manifest.json",
        files=[{"path": "report.html", "sha256": SHA_B}],
    )
    assert snapshot.contract_version == REPORT_SNAPSHOT_VERSION
    assert alias.snapshot_id == snapshot.id
    assert bundle.contract_version == CLIENT_REPORT_BUNDLE_VERSION

    with pytest.raises(ValueError, match="safe name"):
        ReportAlias(
            run_id="run-1",
            report_contract="operator-v5",
            alias="../latest",
            snapshot_id=snapshot.id,
        )


def test_grid_prompt_and_owner_measurement_identities_are_explicit() -> None:
    grid = LocalVisibilityGridDefinition(
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        location_code=1027773,
        center_latitude=47.2529,
        center_longitude=-122.4443,
        rows=3,
        columns=3,
        spacing_meters=1600,
        keyword_target_ids=["kw-1", "kw-2", "kw-3"],
        place_id="place-nova",
        approved_by="operator",
    )
    assert len(grid.identity_sha256 or "") == 64

    topics = PromptTopicSet(
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        topics=[{"id": "topic-1", "prompt": "Which BJJ academies serve Tacoma?"}],
        source_sha256=canonical_sha256({"source": "operator"}),
        state="approved",
        approved_by="operator",
        approved_at="2026-07-26T00:00:00+00:00",
    )
    assert topics.state == "approved"

    measurement = OwnedMeasurementSnapshot(
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source="ga4_csv",
        period_start="2026-06-01",
        period_end="2026-06-30",
        source_sha256=SHA_A,
        context={"market": "Tacoma, WA"},
        metrics={"users": 200, "signups": 12},
        artifact_ref="owned-measurements/ga4.csv",
    )
    assert measurement.metrics["signups"] == 12

    with pytest.raises(ValueError, match="lead PII"):
        OwnedMeasurementSnapshot(
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            source="crm_csv",
            period_start="2026-06-01",
            period_end="2026-06-30",
            source_sha256=SHA_A,
            context={"email": "person@example.test"},
            metrics={"customers": 3},
            artifact_ref="owned-measurements/crm.csv",
        )


def test_comparison_suppresses_numeric_deltas_when_context_is_incompatible() -> None:
    comparison = ReportComparisonSnapshot(
        target_id="target-1",
        baseline_snapshot_id="snapshot-1",
        current_snapshot_id="snapshot-2",
        baseline_sha256=SHA_A,
        current_sha256=SHA_B,
        compatibility={"formula_version": False, "market": True},
        changes={"introduced": ["check-a"]},
        unknown_reasons=["Technical-health formula versions differ."],
    )
    assert comparison.contract_version == REPORT_COMPARISON_VERSION

    with pytest.raises(ValueError, match="cannot contain numeric deltas"):
        ReportComparisonSnapshot(
            target_id="target-1",
            baseline_snapshot_id="snapshot-1",
            current_snapshot_id="snapshot-2",
            baseline_sha256=SHA_A,
            current_sha256=SHA_B,
            compatibility={"formula_version": False},
            changes={"numeric_deltas": {"score": 5}},
            unknown_reasons=["Formula versions differ."],
        )

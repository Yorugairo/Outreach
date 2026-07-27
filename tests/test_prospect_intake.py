from __future__ import annotations

from dataclasses import fields

from src.models import CommercialFinding, OutreachActivationEvent, OutreachPackage, ProspectRecord, VerticalPack
from src.services.prospect_intake_service import ProspectIntakeService
from src.vertical_packs import get_vertical_pack, list_vertical_packs


def valid_row(name: str, domain: str, category: str, *, contact: str = "owner@example.com") -> str:
    return f"{name},{domain},{category},Austin TX,{contact},curated-registry\n"


def test_builtin_vertical_packs_are_versioned_and_have_required_contracts():
    packs = list_vertical_packs()
    assert {pack.pack_id for pack in packs} == {"one_trade_network.v1", "national_bjj_registry.v1"}
    for pack in packs:
        assert isinstance(pack, VerticalPack)
        assert pack.required_fields
        assert pack.allowed_business_categories
        assert pack.service_taxonomy["commercial_packages"]
        assert pack.service_taxonomy["commercial_packages"] == [
            "website_seo_vertical_visibility",
            "vertical_plugin_embed",
            "custom_website_crm_saas",
        ]
        assert pack.outreach_constraints["manual_approval_required"] is True
    assert get_vertical_pack("one_trade_network.v1").vertical_id == "one_trade_network"


def test_csv_preview_normalizes_qualifies_and_deduplicates_by_vertical_domain():
    csv_text = (
        "business_name,website_url,category,location,contact_route,source\n"
        + valid_row("Austin Plumbing", "HTTP://WWW.AustinPlumbing.com/", "Plumber")
        + valid_row("Duplicate Plumbing", "https://austinplumbing.com/about", "plumber")
        + valid_row("Missing Contact", "missing.example.com", "plumber", contact="")
    )
    preview = ProspectIntakeService().preview_csv(csv_text, "one_trade_network.v1")
    assert preview.rows_seen == 3
    assert len(preview.records) == 2
    assert len(preview.valid_prospects) == 1
    prospect = preview.valid_prospects[0]
    assert prospect.normalized_domain == "austinplumbing.com"
    assert prospect.website_url == "http://austinplumbing.com/"
    assert prospect.vertical_pack_version == "one_trade_network.v1"
    assert prospect.is_runnable
    assert any("duplicate website" in issue.message for issue in preview.errors)
    assert any(issue.field == "contact_route" for issue in preview.errors)


def test_unknown_category_is_needs_review_and_not_runnable():
    text = "business_name,website_url,category,location,contact_route,source\n" + valid_row(
        "Unknown Business", "unknown.example.com", "accountant"
    )
    preview = ProspectIntakeService().preview_csv(text, "one_trade_network.v1")
    record = preview.records[0]
    assert record.qualification_status == "needs_review"
    assert not record.is_runnable
    assert preview.warnings[0].severity == "warning"


def test_bjj_alias_category_qualifies_and_commit_returns_only_qualified():
    text = "name,url,type,city,email,provenance\n" + valid_row(
        "Southside Academy", "southsidebjj.com", "Brazilian Jiu-Jitsu Academy"
    )
    service = ProspectIntakeService()
    records = service.commit_csv(text, "national_bjj_registry.v1")
    assert len(records) == 1
    assert records[0].category == "brazilian jiu-jitsu academy"
    assert records[0].vertical_id == "national_bjj_registry"


def test_additive_revenue_models_are_slotted_and_serializable():
    assert {field.name for field in fields(VerticalPack)} >= {
        "vertical_id",
        "version",
        "required_fields",
        "service_taxonomy",
    }
    assert {field.name for field in fields(ProspectRecord)} >= {
        "source_provenance",
        "vertical_pack_version",
        "qualification_status",
    }
    finding = CommercialFinding(
        id="finding-1",
        finding_type="prospect_issue",
        category="technical",
        title="Observed issue",
        observation="Persisted fact.",
        impact="Potential search impact.",
        recommended_action="Fix it.",
        severity="medium",
        effort="small",
        confidence="high",
        recommended_services=["web_development_rebuild"],
        service_fit_reason="Persisted website evidence.",
        evidence_refs=[{"artifact_path": "pages/1.json", "field": "title", "reason": "missing", "observed": None}],
    )
    assert finding.evidence_family == "technical_seo"
    assert finding.to_dict()["evidence_family"] == "technical_seo"
    assert OutreachPackage().to_dict()["state"] == "draft"
    event = OutreachActivationEvent(
        insight_run_id="run-1",
        outreach_package_id="package-1",
        stage="package_approved",
        vertical_id="one_trade_network",
        operator="operator",
    )
    assert event.to_dict()["stage"] == "package_approved"

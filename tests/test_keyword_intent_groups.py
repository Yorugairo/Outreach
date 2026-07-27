from __future__ import annotations

from src.services.demand_evidence_service import DemandEvidenceService


def test_close_variant_signature_normalizes_reordered_phrases_and_common_synonyms() -> None:
    service = DemandEvidenceService()

    assert service.close_variant_signature("BJJ Tacoma") == "bjj tacoma"
    assert service.close_variant_signature("Tacoma Brazilian Jiu Jitsu") == "bjj tacoma"
    assert service.close_variant_signature("bjj gym near me Tacoma") == "bjj tacoma"
    assert service.close_variant_signature("Kids BJJ Tacoma") != service.close_variant_signature("BJJ Tacoma")


def test_intent_family_grouping_is_bounded_by_category_intent_page_and_brand() -> None:
    csv_text = """Keyword,Avg. monthly searches,Category,Search Intent,Target Page / Usage,Brand
bjj tacoma,100,Primary Local Core,Commercial,Home,No
Tacoma Brazilian Jiu Jitsu,80,Primary Local Core,Commercial,Home,No
kids bjj tacoma,70,Kids & Family,Commercial,Programs,No
Nova Ryu Tacoma,60,Lineage & Authority,Brand,About,Yes
"""
    preview = DemandEvidenceService().preview_csv(csv_text, market="Tacoma, WA", snapshot_period="2026-07")

    assert preview.valid is True
    assert len(preview.groups) == 3
    primary = next(group for group in preview.groups if group.intent_family.startswith("primary local core"))
    assert primary.approved_monthly_search_occasions == 100
    assert len(primary.excluded_duplicate_ids) == 1
    assert all("unique" not in group.rationale.casefold() for group in preview.groups)


def test_unsupported_keyword_targets_are_preserved_for_review_but_not_grouped() -> None:
    csv_text = """Keyword,Avg. monthly searches,Category,Search Intent,Target Page / Usage
no gi bjj tacoma,100,Specialty Programs,Commercial,Programs
bjj tacoma,80,Primary Local Core,Commercial,Home
"""
    from src.models import KeywordSet

    keyword_set = KeywordSet(
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        location_code=1027773,
        source_sha256="b" * 64,
        keyword_targets=[
            {
                "keyword": "no gi bjj tacoma",
                "category": "Specialty Programs",
                "search_intent": "Commercial",
                "optimization_focus": "SEO",
                "target_page_usage": "Programs",
                "review_status": "needs_review",
                "review_reasons": ["unsupported_program_claim"],
            },
            {
                "keyword": "bjj tacoma",
                "category": "Primary Local Core",
                "search_intent": "Commercial",
                "optimization_focus": "SEO",
                "target_page_usage": "Home",
            },
        ],
    )
    preview = DemandEvidenceService().preview_csv(
        csv_text,
        market="Tacoma, WA",
        snapshot_period="2026-07",
        keyword_set=keyword_set,
    )

    assert preview.valid is True
    unsupported = next(row for row in preview.rows if row.normalized_keyword == "no gi bjj tacoma")
    assert unsupported.supported is False
    assert any(issue.severity == "warning" for issue in preview.issues)
    assert all(unsupported.id not in group.included_keyword_ids for group in preview.groups)
    assert any(row.normalized_keyword == "bjj tacoma" for row in preview.rows)


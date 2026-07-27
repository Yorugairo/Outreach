from __future__ import annotations

from pathlib import Path

import pytest

from src.models import DemandGroup, KeywordSet, ProspectRecord
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.demand_evidence_service import DemandEvidenceService
from src.services.keyword_set_service import KeywordSetService


CSV = """Keyword,Avg. monthly searches,Category,Search Intent,Target Page / Usage,Brand
bjj tacoma,100,Primary Local Core,Commercial,Home,No
Tacoma BJJ,80,Primary Local Core,Commercial,Home,No
Nova Ryu Tacoma,60,Lineage & Authority,Brand,About,Yes
"""


def test_preview_hashes_rows_groups_close_variants_and_separates_brand():
    preview = DemandEvidenceService().preview_csv(CSV, market="Tacoma, WA", snapshot_period="2026-07")

    assert preview.valid
    assert len(preview.source_sha256) == 64
    assert preview.rows_seen == 3
    assert len(preview.groups) == 2
    local = next(group for group in preview.groups if not group.is_brand)
    assert local.approved_monthly_search_occasions == 100
    assert len(local.excluded_duplicate_ids) == 1
    assert any(group.is_brand for group in preview.groups)


def test_preview_rejects_duplicates_missing_volume_formulas_and_pii():
    text = (
        "Keyword,Avg. monthly searches,Email\n"
        "bjj tacoma,=100,a@example.com\n"
        " bjj   tacoma ,90,a@example.com\n"
        "kids bjj tacoma,,a@example.com\n"
    )
    preview = DemandEvidenceService().preview_csv(text)

    assert not preview.valid
    assert any("PII" in issue.message for issue in preview.errors)
    assert any("formula" in issue.message for issue in preview.errors)
    assert any("duplicate" in issue.message for issue in preview.errors)


def test_paths_are_not_accepted_as_uploads():
    with pytest.raises(ValueError, match="paths"):
        DemandEvidenceService().preview_csv(Path("..\\secrets.csv"))


def test_commit_requires_active_prospect_keyword_set_binding(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    prospect = repository.save_prospect(ProspectRecord(
        business_name="Nova Ryu", website_url="https://novaryu.com", category="gym",
        location="Tacoma, WA", source_provenance="test", vertical_pack_version="national_bjj_registry.v1",
        vertical_id="national_bjj_registry", normalized_domain="novaryu.com", qualification_status="qualified",
    ))
    keyword_set = repository.save_keyword_set(KeywordSet(
        vertical_id="national_bjj_registry", market="Tacoma, WA", location_code=1027773,
        source_sha256="a" * 64, keyword_targets=[{
            "keyword": "bjj tacoma", "category": "Primary Local Core", "search_intent": "Commercial",
            "optimization_focus": "SEO", "target_page_usage": "Home",
        }], state="approved", approved_by="operator", approved_at="2026-07-25T00:00:00+00:00",
    ))
    service = DemandEvidenceService(repository)
    preview = service.preview_csv(CSV.splitlines()[0] + "\n" + CSV.splitlines()[1] + "\n", keyword_set=keyword_set)
    with pytest.raises(ValueError, match="binding"):
        service.commit(preview, prospect_id=prospect.id, keyword_set_id=keyword_set.id)
    KeywordSetService(repository).bind(keyword_set, normalized_domain="novaryu.com", prospect_id=prospect.id, operator="operator")
    committed = service.commit(preview, prospect_id=prospect.id, keyword_set_id=keyword_set.id)
    assert committed.state == "draft"
    assert repository.get_demand_evidence_set(committed.id).source_sha256 == preview.source_sha256


def test_review_and_approval_create_immutable_successors(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    # Binding validation is intentionally bypassed only for this lifecycle test.
    service = DemandEvidenceService()
    preview = service.preview_csv(CSV, market="Tacoma, WA", snapshot_period="2026-07")
    draft = service.commit(preview, prospect_id="prospect-1", keyword_set_id="keywords-1", vertical_id="national_bjj_registry")
    reviewed = service.review_groups(draft, reviewer="operator", group_updates={
        group.id: {"status": "approved", "rationale": "reviewed close variants", "reviewer": "operator"}
        for group in (DemandGroup(**payload) for payload in draft.groups)
    })
    approved = service.approve(reviewed, operator="operator")
    assert reviewed.predecessor_id == draft.id
    assert approved.predecessor_id == reviewed.id
    assert approved.state == "approved"
    assert approved.version == draft.version + 2

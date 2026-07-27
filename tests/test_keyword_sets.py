from pathlib import Path

import pytest

from src.models import KeywordSet
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.keyword_set_service import (
    EXPECTED_CATEGORY_COUNTS,
    KeywordSetService,
    TACOMA_BJJ_KEYWORD_SET_KEY,
)


SEED_PATH = Path("src/data/national_bjj_registry_tacoma_v1.csv")


def test_tacoma_seed_contract_and_factual_review_flags(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    service = KeywordSetService(repository)

    preview = service.preview_csv(SEED_PATH.read_text(encoding="utf-8"))
    assert preview.valid is True
    assert preview.rows_seen == 50
    assert preview.category_counts == EXPECTED_CATEGORY_COUNTS
    assert len(preview.source_sha256) == 64

    keyword_set = service.seed_tacoma_bjj()
    assert keyword_set.keyword_set_key == TACOMA_BJJ_KEYWORD_SET_KEY
    assert keyword_set.location_code == 1027773
    assert keyword_set.normalized_domain == "novaryu.com"
    assert len(keyword_set.targets()) == 50

    review_by_keyword = {target.keyword: target for target in keyword_set.targets()}
    assert review_by_keyword["james foster bjj lineage tacoma"].review_status == "needs_review"
    assert "person_or_lineage_claim" in review_by_keyword["james foster bjj lineage tacoma"].review_reasons
    assert review_by_keyword["jiu jitsu 3912 e portland ave"].review_status == "needs_review"
    assert review_by_keyword["bjj tacoma"].review_status == "approved"


def test_pilot_selection_replaces_unapproved_suggestions_in_same_category(tmp_path):
    service = KeywordSetService(FileBackedInsightRepository(tmp_path))
    keyword_set = service.seed_tacoma_bjj()
    approved = service.approve(keyword_set, operator="operator@example.com")

    pilot = service.select_pilot(approved)
    assert len(pilot) == 12
    assert all(target.review_status == "approved" for target in pilot)
    assert {target.category for target in pilot} == set(EXPECTED_CATEGORY_COUNTS)
    assert sum(target.category == "Specialty Programs" for target in pilot) == 2
    assert "no gi bjj tacoma" not in {target.keyword for target in pilot}
    assert "james foster bjj lineage tacoma" not in {target.keyword for target in pilot}


def test_operator_can_approve_factual_risk_before_set_approval(tmp_path):
    service = KeywordSetService(FileBackedInsightRepository(tmp_path))
    keyword_set = service.seed_tacoma_bjj()
    reviewed = service.review_targets(
        keyword_set,
        approved_keywords=["no gi bjj tacoma", "james foster bjj lineage tacoma"],
    )
    approved = service.approve(reviewed, operator="operator")

    statuses = {target.keyword: target.review_status for target in approved.targets()}
    assert statuses["no gi bjj tacoma"] == "approved"
    assert statuses["james foster bjj lineage tacoma"] == "approved"


def test_duplicate_normalization_is_rejected():
    text = (
        "Keyword,Category,Search Intent,Optimization Focus,Target Page / Usage\n"
        "BJJ Tacoma,Primary Local Core,Commercial,SEO,Home\n"
        " bjj   tacoma ,Primary Local Core,Commercial,SEO,Home\n"
    )
    preview = KeywordSetService().preview_csv(text)
    assert preview.valid is False
    assert len(preview.keyword_targets) == 1
    assert preview.errors[0].message == "duplicate normalized keyword"


def test_keyword_set_constructor_rejects_duplicate_payloads():
    payload = {
        "keyword": "bjj tacoma",
        "category": "Primary Local Core",
        "search_intent": "Commercial",
        "optimization_focus": "SEO",
        "target_page_usage": "Home",
    }
    with pytest.raises(ValueError, match="duplicate keyword"):
        KeywordSet(
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
            market_slug="tacoma",
            location_code=1027773,
            source_sha256="a" * 64,
            keyword_targets=[payload, {**payload, "keyword": " BJJ  TACOMA "}],
        )


def test_approved_template_can_be_bound_without_mutating_keyword_version(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    service = KeywordSetService(repository)
    seeded = service.seed_tacoma_bjj()
    approved = service.approve(seeded, operator="operator")

    binding = service.bind(
        approved,
        normalized_domain="another-academy.example",
        prospect_id="prospect-1",
        operator="operator",
    )

    assert binding.keyword_set_id == approved.id
    assert binding.normalized_domain == "another-academy.example"
    assert service.resolve_for_domain("another-academy.example").id == approved.id
    assert repository.get_keyword_set(approved.id).normalized_domain == "novaryu.com"

from src.models import InsightRun, MarketEvidenceRun, SEOTarget
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.keyword_set_service import KeywordSetService


def _exercise(repository):
    target = SEOTarget(
        input_url="https://novaryu.com",
        normalized_url="https://novaryu.com",
        normalized_domain="novaryu.com",
    )
    repository.upsert_target(target)
    run = InsightRun(
        seo_target_id=target.id,
        requested_url=target.normalized_url,
        requested_domain=target.normalized_domain,
    )
    repository.create_run(run)
    service = KeywordSetService(repository)
    keyword_set = service.seed_tacoma_bjj()
    approved = service.approve(keyword_set, operator="operator")
    binding = service.bind(
        approved,
        normalized_domain="other-bjj.example",
        prospect_id="prospect-other",
        operator="operator",
    )

    market_run = MarketEvidenceRun(
        insight_run_id=run.id,
        insight_attempt_id=run.attempt_id,
        keyword_set_id=approved.id,
        keyword_set_version=approved.keyword_set_key,
        target_domain=target.normalized_domain,
        vertical_id=approved.vertical_id,
        market=approved.market,
        location_code=approved.location_code,
    )
    repository.save_market_evidence_run(market_run)

    assert repository.get_keyword_set(approved.id).state == "approved"
    assert repository.list_keyword_sets(normalized_domain="novaryu.com", state="approved")[0].id == approved.id
    assert repository.get_market_evidence_run(market_run.id).insight_run_id == run.id
    assert repository.list_market_evidence_runs(insight_run_id=run.id)[0].id == market_run.id
    assert repository.list_keyword_set_bindings(
        normalized_domain="other-bjj.example"
    )[0].id == binding.id


def test_file_repository_market_contract(tmp_path):
    _exercise(FileBackedInsightRepository(tmp_path / "artifacts"))


def test_sqlite_repository_market_contract(tmp_path):
    repository = SQLiteInsightRepository(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    _exercise(repository)
    assert repository.health()["migration_count"] >= 5

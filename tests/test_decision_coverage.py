from __future__ import annotations

from pathlib import Path

import pytest

from src.models import SiteEvidencePack
from src.services.business_fact_ledger_service import BusinessFactLedgerService
from src.services.decision_coverage_service import DecisionCoverageService
from src.vertical_agentic_packs import get_vertical_agentic_pack


def _setup(tmp_path: Path):
    page = tmp_path / "runs" / "run-1" / "pages" / "page-1.json"
    page.parent.mkdir(parents=True)
    page.write_text('{"attempt_id":"attempt-1","title":"Nova Ryu BJJ"}', encoding="utf-8")
    pack = SiteEvidencePack(
        run_id="run-1", attempt_id="attempt-1", source_snapshot_ids={}, source_hashes={},
        target_facts={}, page_facts=[], deterministic_surfaces={}, evidence_refs=[],
        vertical_pack_version="national_bjj_registry.agentic.v1",
    )
    ref = {"artifact_path": "pages/page-1.json", "field": "title", "observed": "Nova Ryu BJJ", "reason": "page"}
    ledger = BusinessFactLedgerService(tmp_path).build_snapshot(
        pack, "ledger-work", {"facts": [{"fact_id": "programs", "name": "programs", "value": "BJJ classes", "evidence_refs": [ref]}]}
    )
    return get_vertical_agentic_pack("national_bjj_registry.agentic.v1"), ledger, ref


def test_only_approved_questions_are_answered_and_unknown_ids_are_limited(tmp_path: Path) -> None:
    pack, ledger, ref = _setup(tmp_path)
    coverage = DecisionCoverageService(tmp_path).build_snapshot(
        pack, ledger, "decision-work",
        {"answers": {
            "programs": {"status": "answered", "answer": "BJJ classes", "fact_ids": ["programs"], "evidence_refs": [ref]},
            "invented": {"status": "answered", "answer": "made up", "evidence_refs": [ref]},
        }},
    )
    assert coverage.coverage[0]["status"] == "answered"
    assert any("invented" in item for item in coverage.limitations)
    assert all(item["question_id"] != "invented" for item in coverage.coverage)


def test_positive_answer_without_ledger_evidence_becomes_unknown(tmp_path: Path) -> None:
    pack, ledger, ref = _setup(tmp_path)
    other_ref = dict(ref, observed="other")
    coverage = DecisionCoverageService(tmp_path).build_snapshot(
        pack, ledger, "decision-work",
        {"programs": {"status": "answered", "answer": "unsupported", "evidence_refs": [other_ref]}},
    )
    assert coverage.coverage[0]["status"] == "unknown"
    assert coverage.coverage[0]["evidence_refs"] == []
    assert coverage.completeness_percent < 100


def test_missing_questions_are_explicit_and_completeness_is_deterministic(tmp_path: Path) -> None:
    pack, ledger, _ = _setup(tmp_path)
    coverage = DecisionCoverageService(tmp_path).build_snapshot(pack, ledger, "decision-work", {})
    assert coverage.coverage[0]["status"] == "missing"
    assert coverage.completeness_percent == 0
    assert coverage.review_state == "needs_review"


def test_unapproved_pack_cannot_produce_customer_decision_coverage(tmp_path: Path) -> None:
    pack, ledger, _ = _setup(tmp_path)
    payload = pack.to_dict()
    payload.pop("id")
    payload.pop("created_at")
    payload["state"] = "draft"
    from src.models import VerticalAgenticPack
    draft = VerticalAgenticPack(**payload)
    with pytest.raises(ValueError, match="approved vertical agentic pack"):
        DecisionCoverageService(tmp_path).build_snapshot(draft, ledger, "work", {})

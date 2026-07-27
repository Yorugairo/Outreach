"""Deterministic buyer-question coverage over a reviewed vertical pack."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from src.models import BusinessFactLedgerSnapshot, DecisionCoverageSnapshot, SiteEvidencePack, canonical_sha256
from src.services.agentic_validation_service import AgenticEvidenceValidator, normalize_agentic_evidence_ref
from src.vertical_agentic_packs import resolve_vertical_agentic_pack


_STATUSES = {"answered", "partial", "ambiguous", "contradicted", "missing", "unknown"}


def _as_mapping(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError("expected a structured mapping")


def _pack_questions(pack: Any) -> list[dict[str, Any]]:
    payload = _as_mapping(pack)
    questions = payload.get("buyer_questions", [])
    return [dict(item) for item in questions if isinstance(item, Mapping)] if isinstance(questions, list) else []


def _pack_id(pack: Any) -> str:
    payload = _as_mapping(pack)
    return str(payload.get("version") or payload.get("pack_id") or "").strip()


def _ledger_facts(ledger: Any) -> list[dict[str, Any]]:
    payload = _as_mapping(ledger)
    facts = payload.get("facts", [])
    return [dict(item) for item in facts if isinstance(item, Mapping)] if isinstance(facts, list) else []


class DecisionCoverageService:
    """Turn untrusted candidate answers into a conservative coverage snapshot."""

    def __init__(self, artifact_root: str | Path = "artifacts/seo_insight_runs") -> None:
        self.artifact_root = Path(artifact_root)
        self.validator = AgenticEvidenceValidator(self.artifact_root)

    def build_snapshot(
        self,
        pack: Any,
        ledger: BusinessFactLedgerSnapshot | Mapping[str, Any],
        work_item_id: str,
        answers: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
        *,
        source_sha256: str | None = None,
        mode: str = "prospect",
        review_state: str = "needs_review",
    ) -> DecisionCoverageSnapshot:
        pack_payload = _as_mapping(pack)
        ledger_payload = _as_mapping(ledger)
        if pack_payload.get("state") not in {None, "approved"}:
            raise ValueError("decision coverage requires an approved vertical agentic pack")
        run_id = str(ledger_payload.get("run_id") or "").strip()
        attempt_id = str(ledger_payload.get("attempt_id") or "").strip()
        fact_ledger_id = str(ledger_payload.get("id") or "").strip()
        vertical = _pack_id(pack)
        if not run_id or not attempt_id or not fact_ledger_id or not vertical:
            raise ValueError("decision coverage requires run, attempt, ledger, and pack identity")
        if not work_item_id.strip():
            raise ValueError("decision coverage requires work-item identity")
        candidate, _ = self._answers_by_id(answers)
        known_question_ids = {
            str(item.get("question_id") or "").strip()
            for item in _pack_questions(pack)
            if str(item.get("question_id") or "").strip()
        }
        unknown_ids = set(candidate) - known_question_ids
        facts = _ledger_facts(ledger)
        fact_ids = {str(item.get("fact_id")) for item in facts if item.get("fact_id")}
        fact_names = {str(item.get("name") or "").casefold() for item in facts}
        known_fact_ids = {
            str(item.get("fact_id"))
            for item in facts
            if item.get("fact_id") and item.get("source_status") in {"observed", "business_supplied", "conflicted"}
            and isinstance(item.get("evidence_refs"), list) and item.get("evidence_refs")
        }
        ledger_ref_keys = {
            self._ref_key(ref)
            for item in facts
            if isinstance(item.get("evidence_refs"), list)
            for ref in item.get("evidence_refs", [])
            if isinstance(ref, Mapping)
        }
        coverage: list[dict[str, Any]] = []
        limitations: list[str] = []
        if unknown_ids:
            limitations.append("Unknown question IDs were excluded: " + ", ".join(sorted(unknown_ids)))
        applicable_count = 0
        completeness_units = 0.0
        for question in _pack_questions(pack):
            question_id = str(question.get("question_id") or "").strip()
            if not question_id:
                continue
            applicable = self._is_applicable(question, facts=facts, fact_ids=fact_ids, fact_names=fact_names)
            answer = candidate.get(question_id)
            if not applicable:
                status = "unknown"
                result: dict[str, Any] = {
                    "question_id": question_id,
                    "status": status,
                    "answer": None,
                    "evidence_refs": [],
                    "limitations": ["Question applicability could not be established for this target."],
                }
                coverage.append(result)
                continue
            applicable_count += 1
            if answer is None:
                coverage.append(
                    {
                        "question_id": question_id,
                        "status": "missing",
                        "answer": None,
                        "evidence_refs": [],
                        "limitations": ["No candidate answer was supplied."],
                    }
                )
                continue
            result, score_unit, result_limitations = self._normalize_answer(
                question,
                answer,
                run_id=run_id,
                attempt_id=attempt_id,
                fact_ids=fact_ids,
                fact_names=fact_names,
                known_fact_ids=known_fact_ids,
                ledger_ref_keys=ledger_ref_keys,
            )
            coverage.append(result)
            completeness_units += score_unit
            limitations.extend(result_limitations)
        completeness = round((completeness_units / applicable_count) * 100, 2) if applicable_count else 0.0
        # ``review_state`` is a workflow state, not a model assertion.  An
        # automatically generated coverage snapshot remains review-only when
        # any result is unsupported or incomplete.
        effective_review = review_state if review_state in {"unreviewed", "needs_review", "approved", "rejected"} else "needs_review"
        if limitations or any(item["status"] != "answered" for item in coverage):
            effective_review = "needs_review"
        digest = source_sha256 or str(ledger_payload.get("source_sha256") or "")
        if not self._is_sha(digest):
            digest = canonical_sha256({"pack": pack_payload, "ledger": ledger_payload})
        return DecisionCoverageSnapshot(
            run_id=run_id,
            attempt_id=attempt_id,
            work_item_id=work_item_id,
            fact_ledger_id=fact_ledger_id,
            vertical_pack_version=vertical,
            source_sha256=digest,
            coverage=coverage,
            completeness_percent=completeness,
            mode=mode,
            limitations=sorted(set(item[:500] for item in limitations if item.strip())),
            review_state=effective_review,
        )

    create_snapshot = build_snapshot
    evaluate = build_snapshot
    from_candidate = build_snapshot

    def validate_candidate(
        self,
        pack: Any,
        ledger: Any,
        answers: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
    ) -> dict[str, Any]:
        snapshot = self.build_snapshot(pack, ledger, "validation-only", answers)
        return snapshot.to_dict()

    @staticmethod
    def _answers_by_id(
        answers: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
    ) -> tuple[dict[str, Mapping[str, Any]], set[str]]:
        if answers is None:
            return {}, set()
        if isinstance(answers, Mapping):
            raw = answers.get("answers", answers.get("coverage", answers))
            if isinstance(raw, Mapping):
                return {str(key): value for key, value in raw.items() if isinstance(value, Mapping)}, set()
            if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
                answers_by_id: dict[str, Mapping[str, Any]] = {}
                for item in raw:
                    if isinstance(item, Mapping) and str(item.get("question_id") or "").strip():
                        answers_by_id[str(item["question_id"])] = item
                return answers_by_id, set()
            return {}, set()
        if isinstance(answers, Sequence) and not isinstance(answers, (str, bytes, bytearray)):
            answers_by_id: dict[str, Mapping[str, Any]] = {}
            for item in answers:
                if isinstance(item, Mapping) and str(item.get("question_id") or "").strip():
                    answers_by_id[str(item["question_id"])] = item
            return answers_by_id, set()
        return {}, set()

    def _normalize_answer(
        self,
        question: Mapping[str, Any],
        answer: Mapping[str, Any],
        *,
        run_id: str,
        attempt_id: str,
        fact_ids: set[str],
        fact_names: set[str],
        known_fact_ids: set[str],
        ledger_ref_keys: set[str],
    ) -> tuple[dict[str, Any], float, list[str]]:
        question_id = str(question.get("question_id") or "")
        requested_status = str(answer.get("status") or "").strip()
        answer_text = answer.get("answer", answer.get("text"))
        answer_text = str(answer_text).strip() if answer_text is not None else ""
        refs_raw = answer.get("evidence_refs", answer.get("evidence", []))
        refs_raw = refs_raw if isinstance(refs_raw, list) else []
        refs = [normalize_agentic_evidence_ref(ref, run_id=run_id) for ref in refs_raw]
        refs = [ref for ref in refs if ref]
        validation = self.validator.validate_refs(refs, run_id=run_id, expected_attempt_id=attempt_id)
        valid_refs = validation["valid"]
        limits: list[str] = []
        fact_refs = answer.get("fact_ids", answer.get("grounded_fact_ids", []))
        fact_refs = fact_refs if isinstance(fact_refs, list) else []
        unknown_fact_ids = {str(item) for item in fact_refs if str(item) not in fact_ids}
        if unknown_fact_ids:
            limits.append("answer referenced facts outside the validated ledger")
        if fact_refs and any(str(item) not in known_fact_ids for item in fact_refs):
            limits.append("answer referenced a fact that is not positively grounded in the ledger")
        status = requested_status if requested_status in _STATUSES else ("answered" if answer_text else "unknown")
        if not answer_text and status in {"answered", "partial", "ambiguous", "contradicted"}:
            status = "unknown"
            limits.append("positive answer status had no answer text")
        if status in {"answered", "partial", "ambiguous", "contradicted"} and not valid_refs:
            status = "unknown"
            limits.append("positive or contested answer status had no exact resolvable evidence")
        if status in {"answered", "partial", "ambiguous", "contradicted"} and valid_refs:
            ref_keys = {self._ref_key(ref) for ref in valid_refs}
            if not ref_keys.intersection(ledger_ref_keys):
                status = "unknown"
                limits.append("answer evidence was not present in the validated fact ledger")
        if unknown_fact_ids:
            status = "unknown"
        if len(valid_refs) != len(refs):
            limits.append("one or more answer references did not resolve")
        unit = 1.0 if status == "answered" else 0.5 if status == "partial" else 0.0
        result = {
            "question_id": question_id,
            "status": status,
            "answer": answer_text or None,
            "confidence": str(answer.get("confidence") or "low" if status == "unknown" else answer.get("confidence") or "medium"),
            "fact_ids": [str(item) for item in fact_refs if str(item) in fact_ids],
            "evidence_refs": valid_refs,
            "limitations": limits,
        }
        return result, unit, limits

    @staticmethod
    def _is_applicable(
        question: Mapping[str, Any],
        *,
        facts: list[dict[str, Any]],
        fact_ids: set[str],
        fact_names: set[str],
    ) -> bool:
        applicability = question.get("applicability", {})
        if not isinstance(applicability, Mapping):
            return False
        if applicability.get("all") is False:
            return False
        required = applicability.get("requires_facts", [])
        if isinstance(required, list):
            for key in required:
                if str(key) not in fact_ids and str(key).casefold() not in fact_names:
                    return False
        return True

    @staticmethod
    def _is_sha(value: str) -> bool:
        return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdefABCDEF" for char in value)

    @staticmethod
    def _ref_key(reference: Mapping[str, Any]) -> str:
        return "|".join(
            str(reference.get(key) or "")
            for key in ("artifact_ref", "reference_kind", "field_path", "exact_span", "dom_ref", "screenshot_ref", "response_span")
        )


def resolve_pack_and_build_coverage(
    pack: str | Any,
    ledger: BusinessFactLedgerSnapshot | Mapping[str, Any],
    work_item_id: str,
    answers: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    *,
    artifact_root: str | Path = "artifacts/seo_insight_runs",
) -> DecisionCoverageSnapshot:
    """Convenience reconciliation entry point for workers and tests."""

    resolved = resolve_vertical_agentic_pack(pack)
    return DecisionCoverageService(artifact_root).build_snapshot(
        resolved,
        ledger,
        work_item_id,
        answers,
    )


__all__ = ["DecisionCoverageService", "resolve_pack_and_build_coverage"]

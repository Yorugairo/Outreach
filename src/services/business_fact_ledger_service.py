"""Evidence-grounded business truth extraction for P12.

This service is deliberately conservative.  It normalizes candidate facts from
the bounded ``SiteEvidencePack``/model output, but does not invent a fact when
the candidate has no independently persisted reference.  The resulting ledger
is an immutable model snapshot; review remains a separate human action.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from src.models import BusinessFactLedgerSnapshot, SiteEvidencePack, canonical_sha256
from src.services.agentic_validation_service import (
    AgenticEvidenceValidator,
    AgenticValidationService,
    normalize_agentic_evidence_ref,
)


_KNOWN_SOURCE_STATUSES = {"observed", "business_supplied", "conflicted", "unknown"}
_SENSITIVITY = {"public", "sensitive", "private"}
_APPROVAL_STATES = {"unreviewed", "needs_review", "approved", "rejected"}
_SECRET_PARTS = {
    "api_key",
    "authorization",
    "cookie",
    "credential",
    "oauth",
    "password",
    "refresh_token",
    "secret",
}


def _payload(value: Any) -> dict[str, Any]:
    if isinstance(value, SiteEvidencePack):
        return value.to_dict()
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        candidate = value.to_dict()
        if isinstance(candidate, Mapping):
            return dict(candidate)
    raise TypeError("evidence pack must be a SiteEvidencePack or mapping")


def _source_hash(pack: Mapping[str, Any], override: str | None = None) -> str:
    value = str(override or pack.get("content_sha256") or "").strip()
    if len(value) == 64 and all(char in "0123456789abcdefABCDEF" for char in value):
        return value.lower()
    # A mapping supplied by a worker may not carry the model's computed hash.
    # Hash the bounded pack rather than accepting an arbitrary model hash.
    return canonical_sha256({key: pack.get(key) for key in (
        "contract_version", "run_id", "attempt_id", "source_snapshot_ids",
        "source_hashes", "target_facts", "page_facts", "deterministic_surfaces",
        "evidence_refs", "vertical_pack_version", "market_evidence",
        "permitted_service_mappings", "completeness_percent", "limitations",
    )})


class BusinessFactLedgerService:
    """Build a fact ledger while preserving unknown and review-only semantics."""

    def __init__(self, artifact_root: str | Path = "artifacts/seo_insight_runs") -> None:
        self.artifact_root = Path(artifact_root)
        self.validator = AgenticEvidenceValidator(self.artifact_root)
        self.legacy_validator = AgenticValidationService(self.artifact_root)

    def build_snapshot(
        self,
        evidence_pack: SiteEvidencePack | Mapping[str, Any],
        work_item_id: str,
        candidate: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
        *,
        mode: str = "prospect",
        source_sha256: str | None = None,
        review_state: str = "needs_review",
    ) -> BusinessFactLedgerSnapshot:
        pack = _payload(evidence_pack)
        run_id = str(pack.get("run_id") or "").strip()
        attempt_id = str(pack.get("attempt_id") or "").strip()
        vertical = str(pack.get("vertical_pack_version") or "unbound").strip()
        if not run_id or not attempt_id or not work_item_id.strip():
            raise ValueError("fact ledger requires run, attempt, and work identity")
        candidate_facts = self._candidate_facts(candidate)
        facts, limitations, conflicts = self._normalize_facts(
            candidate_facts,
            run_id=run_id,
            attempt_id=attempt_id,
        )
        if not candidate_facts:
            limitations.append("No candidate business facts were supplied; all facts remain unknown.")
        # Never allow a model output to silently mark an entire ledger as
        # approved.  Public facts can be approved by a caller after review,
        # but the default runtime is review-only.
        effective_review = review_state if review_state in _APPROVAL_STATES else "needs_review"
        if any(item["approval_state"] != "approved" for item in facts):
            effective_review = "needs_review"
        return BusinessFactLedgerSnapshot(
            run_id=run_id,
            attempt_id=attempt_id,
            work_item_id=work_item_id,
            vertical_pack_version=vertical,
            source_sha256=_source_hash(pack, source_sha256),
            facts=facts,
            mode=mode,
            conflicts=conflicts,
            limitations=limitations,
            review_state=effective_review,
        )

    # Friendly aliases used by workers and tests while the durable repository
    # layer evolves independently.
    create_snapshot = build_snapshot
    from_candidate = build_snapshot

    def extract_facts(
        self,
        evidence_pack: SiteEvidencePack | Mapping[str, Any],
        candidate: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        pack = _payload(evidence_pack)
        facts, _, _ = self._normalize_facts(
            self._candidate_facts(candidate),
            run_id=str(pack.get("run_id") or ""),
            attempt_id=str(pack.get("attempt_id") or ""),
        )
        return facts

    def _candidate_facts(
        self,
        candidate: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None,
    ) -> list[Mapping[str, Any]]:
        if candidate is None:
            return []
        if isinstance(candidate, Mapping):
            raw = candidate.get("facts", candidate.get("business_facts", candidate.get("items", [])))
            if isinstance(raw, Mapping):
                return [
                    {"fact_id": str(key), "name": str(key), "normalized_value": value}
                    for key, value in raw.items()
                ]
            if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
                return [item for item in raw if isinstance(item, Mapping)]
            return []
        if isinstance(candidate, Sequence) and not isinstance(candidate, (str, bytes, bytearray)):
            return [item for item in candidate if isinstance(item, Mapping)]
        return []

    def _normalize_facts(
        self,
        raw_facts: Sequence[Mapping[str, Any]],
        *,
        run_id: str,
        attempt_id: str,
    ) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
        facts: list[dict[str, Any]] = []
        limitations: list[str] = []
        conflicts: list[dict[str, Any]] = []
        by_name: dict[str, dict[str, Any]] = {}
        for index, raw in enumerate(raw_facts[:200]):
            fact_id = str(raw.get("fact_id") or raw.get("id") or f"fact-{index + 1}").strip()
            name = str(raw.get("name") or raw.get("fact_name") or fact_id).strip()
            value = raw.get("normalized_value", raw.get("value", raw.get("answer")))
            status = str(raw.get("source_status") or raw.get("status") or "observed").strip()
            if status not in _KNOWN_SOURCE_STATUSES:
                status = "unknown"
                limitations.append(f"Fact {fact_id} used an unsupported source status and was downgraded to unknown.")
            sensitivity = str(raw.get("sensitivity_class") or "public").strip()
            if sensitivity not in _SENSITIVITY:
                sensitivity = "sensitive"
                limitations.append(f"Fact {fact_id} used an unsupported sensitivity class and remains review-only.")
            approval = str(raw.get("approval_state") or "needs_review").strip()
            if approval not in _APPROVAL_STATES:
                approval = "needs_review"
            refs_raw = raw.get("evidence_refs", raw.get("evidence", []))
            refs_raw = refs_raw if isinstance(refs_raw, list) else []
            normalized_refs = [normalize_agentic_evidence_ref(ref, run_id=run_id) for ref in refs_raw]
            normalized_refs = [ref for ref in normalized_refs if ref]
            validation = self.validator.validate_refs(
                normalized_refs,
                run_id=run_id,
                expected_attempt_id=attempt_id,
            )
            refs = validation["valid"]
            if validation["invalid"]:
                limitations.append(f"Fact {fact_id} has unresolved evidence and was downgraded to unknown.")
                status = "unknown"
                value = None
                approval = "needs_review"
            text = " ".join(str(value or "") for value in (name, value))
            if self.legacy_validator.has_prompt_injection(text) or self._contains_secret(raw):
                limitations.append(f"Fact {fact_id} contained unsafe or secret-like content and was excluded.")
                status = "unknown"
                value = None
                refs = []
                approval = "needs_review"
            if status in {"observed", "business_supplied", "conflicted"} and not refs:
                limitations.append(f"Fact {fact_id} has no exact persisted evidence and remains unknown.")
                status = "unknown"
                value = None
                approval = "needs_review"
            if sensitivity != "public":
                approval = "needs_review"
            if status == "unknown":
                value = None
                refs = []
                approval = "needs_review"
            fact = {
                "fact_id": fact_id,
                "name": name or fact_id,
                "normalized_value": value,
                "source_status": status,
                "sensitivity_class": sensitivity,
                "approval_state": approval,
                "evidence_refs": refs,
                "confidence": str(raw.get("confidence") or "low" if status == "unknown" else raw.get("confidence") or "medium"),
                "limitations": [str(item)[:500] for item in raw.get("limitations", []) if str(item).strip()]
                if isinstance(raw.get("limitations", []), list)
                else [],
            }
            prior = by_name.get(name.casefold())
            if (
                prior is not None
                and prior.get("source_status") in {"observed", "business_supplied", "conflicted"}
                and fact.get("source_status") in {"observed", "business_supplied", "conflicted"}
                and prior.get("normalized_value") != fact.get("normalized_value")
                and prior.get("evidence_refs")
                and fact.get("evidence_refs")
            ):
                prior["source_status"] = "conflicted"
                prior["approval_state"] = "needs_review"
                fact["source_status"] = "conflicted"
                fact["approval_state"] = "needs_review"
                conflict = {
                    "fact_name": name,
                    "fact_ids": [prior["fact_id"], fact["fact_id"]],
                    "values": [prior.get("normalized_value"), fact.get("normalized_value")],
                    "evidence_refs": [*prior.get("evidence_refs", []), *fact.get("evidence_refs", [])],
                }
                conflicts.append(conflict)
            else:
                by_name[name.casefold()] = fact
            facts.append(fact)
        return facts, limitations, conflicts

    @staticmethod
    def _contains_secret(value: Any) -> bool:
        if isinstance(value, Mapping):
            for key, child in value.items():
                normalized = str(key).casefold().replace("-", "_")
                if any(part in normalized for part in _SECRET_PARTS):
                    return True
                if BusinessFactLedgerService._contains_secret(child):
                    return True
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return any(BusinessFactLedgerService._contains_secret(child) for child in value)
        return False


__all__ = ["BusinessFactLedgerService"]

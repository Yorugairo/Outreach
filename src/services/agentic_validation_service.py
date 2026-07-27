"""Deterministic validation between model output and customer-safe findings."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.models import AgenticFinding, SiteEvidencePack
from src.services.provenance_service import (
    EvidenceReferenceError,
    resolve_evidence_field,
    validate_evidence_ref,
)


INJECTION_PATTERNS = (
    re.compile(r"\bignore\s+(?:all\s+)?(?:previous|prior|system)\b", re.I),
    re.compile(r"\b(system|developer)\s+prompt\b", re.I),
    re.compile(r"\b(disregard|override)\s+(?:the\s+)?(?:instructions|policy)\b", re.I),
    re.compile(r"<\|(?:system|assistant|developer)\|>", re.I),
    re.compile(r"\bexecute\s+(?:this\s+)?(?:command|script)\b", re.I),
)

FACT_RISK_PATTERNS = (
    re.compile(r"[$£€]\s?\d"),
    re.compile(r"\b(?:charges?|tuition|pricing|price)\b", re.I),
    re.compile(r"\b(?:lineage|black belt|certified|licensed|insured)\b", re.I),
    re.compile(r"\b(?:capacity|members?|students?)\s+(?:is|of|at)\s+\d", re.I),
)


class AgenticValidationService:
    def __init__(self, artifact_root: str | Path) -> None:
        self.artifact_root = Path(artifact_root)

    def validate(
        self,
        pack: SiteEvidencePack,
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        raw_findings = candidate.get("findings", [])
        if not isinstance(raw_findings, list):
            raw_findings = []
        permitted = self._permitted_services(pack)
        findings: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        valid_ref_count = 0
        total_ref_count = 0
        contradictions = (
            candidate.get("contradictions", [])
            if isinstance(candidate.get("contradictions"), list)
            else []
        )
        for index, payload in enumerate(raw_findings[:64]):
            normalized, reasons, valid_refs, ref_count = self._validate_finding(
                pack,
                payload,
                permitted,
                index=index,
            )
            valid_ref_count += valid_refs
            total_ref_count += ref_count
            if normalized is None:
                rejected.append(
                    {
                        "index": index,
                        "reasons": reasons or ["invalid finding payload"],
                    }
                )
                continue
            if reasons:
                normalized["customer_safe"] = False
                normalized["review_reason"] = "; ".join(sorted(set(reasons)))[:500]
            else:
                normalized["customer_safe"] = True
                normalized["review_reason"] = None
            try:
                finding = AgenticFinding(**normalized)
            except (TypeError, ValueError) as exc:
                rejected.append({"index": index, "reasons": [str(exc)]})
                continue
            findings.append(finding.to_dict())
        unsafe = [item for item in findings if not item["customer_safe"]]
        evidence_precision = (
            valid_ref_count / total_ref_count if total_ref_count else 0.0
        )
        result = {
            "findings": findings,
            "contradictions": contradictions[:32],
            "rejected_findings": rejected,
            "validation_result": {
                "schema_valid": not rejected,
                "customer_safe": not unsafe and not rejected and not contradictions,
                "finding_count": len(findings),
                "unsafe_finding_count": len(unsafe),
                "rejected_finding_count": len(rejected),
                "invalid_reference_count": total_ref_count - valid_ref_count,
                "evidence_precision": round(evidence_precision, 4),
                "requires_review": bool(unsafe or rejected or contradictions),
            },
            "limitations": self._limitations(candidate),
        }
        return result

    def _validate_finding(
        self,
        pack: SiteEvidencePack,
        payload: object,
        permitted: set[str],
        *,
        index: int,
    ) -> tuple[dict[str, Any] | None, list[str], int, int]:
        if not isinstance(payload, dict):
            return None, ["finding must be an object"], 0, 0
        normalized = dict(payload)
        normalized.setdefault("id", f"candidate-{index + 1}")
        normalized.setdefault("claim_type", "inference")
        normalized.setdefault("confidence", "low")
        normalized.setdefault("severity", "info")
        normalized.setdefault("commercial_relevance", "Requires operator review.")
        normalized.setdefault("service_fit", [])
        normalized.setdefault("evidence_refs", [])
        normalized.setdefault("customer_safe", False)
        normalized.setdefault("review_reason", "Pending deterministic validation.")
        reasons: list[str] = []
        content = " ".join(
            str(normalized.get(key) or "") for key in ("title", "claim")
        )
        if self.has_prompt_injection(content):
            reasons.append("prompt-injection language was rejected")
        service_fit = normalized.get("service_fit")
        if not isinstance(service_fit, list):
            service_fit = []
            reasons.append("service_fit must be a list")
        invalid_services = {
            str(item) for item in service_fit if str(item) not in permitted
        }
        if invalid_services:
            reasons.append(
                "unsupported service mapping: "
                + ", ".join(sorted(invalid_services))
            )
        normalized["service_fit"] = [
            str(item) for item in service_fit if str(item) in permitted
        ]
        refs = normalized.get("evidence_refs")
        if not isinstance(refs, list):
            refs = []
            reasons.append("evidence_refs must be a list")
        total_refs = len(refs)
        valid_refs: list[dict[str, Any]] = []
        for ref in refs:
            try:
                validate_evidence_ref(
                    self.artifact_root / "runs" / pack.run_id,
                    ref,
                    expected_attempt_id=pack.attempt_id,
                )
            except EvidenceReferenceError:
                continue
            valid_refs.append(dict(ref))
        if len(valid_refs) != total_refs:
            reasons.append("one or more evidence references did not resolve")
        if not valid_refs:
            reasons.append("finding has no independently resolved evidence")
        normalized["evidence_refs"] = valid_refs
        if any(pattern.search(content) for pattern in FACT_RISK_PATTERNS):
            if not self._has_fact_provenance(valid_refs):
                reasons.append("sensitive business fact lacks explicit provenance")
        normalized["title"] = str(normalized.get("title") or "").strip()
        normalized["claim"] = str(normalized.get("claim") or "").strip()
        normalized["commercial_relevance"] = str(
            normalized.get("commercial_relevance") or ""
        ).strip()
        if not normalized["title"] or not normalized["claim"]:
            return None, ["finding requires title and claim"], len(valid_refs), total_refs
        return normalized, reasons, len(valid_refs), total_refs

    @staticmethod
    def _permitted_services(pack: SiteEvidencePack) -> set[str]:
        mapping = pack.permitted_service_mappings
        permitted = set(str(key) for key in mapping)
        for value in mapping.values():
            if isinstance(value, str) and "_" in value:
                permitted.add(value)
            elif isinstance(value, list):
                permitted.update(str(item) for item in value)
        return permitted

    @staticmethod
    def _has_fact_provenance(refs: list[dict[str, Any]]) -> bool:
        provenance_markers = (
            "prospect",
            "target_facts",
            "vertical_pack",
            "operator",
            "economics",
            "registry",
        )
        return any(
            any(marker in str(ref.get("artifact_path", "")).casefold()
                or marker in str(ref.get("field", "")).casefold()
                for marker in provenance_markers)
            for ref in refs
        )

    @staticmethod
    def _limitations(candidate: dict[str, Any]) -> list[str]:
        values = candidate.get("limitations", [])
        if not isinstance(values, list):
            return []
        return [str(value)[:500] for value in values[:32] if str(value).strip()]

    @staticmethod
    def has_prompt_injection(value: str) -> bool:
        return any(pattern.search(value) for pattern in INJECTION_PATTERNS)

    # P12 uses a stricter, content-addressable reference shape than the legacy
    # P10 finding references.  Keep this helper on the existing validator so
    # callers can use one policy boundary while old reports remain readable.
    def validate_exact_ref(
        self,
        reference: object,
        *,
        run_id: str | None = None,
        expected_attempt_id: str | None = None,
    ) -> dict[str, Any]:
        return validate_exact_evidence_ref(
            self.artifact_root,
            reference,
            run_id=run_id,
            expected_attempt_id=expected_attempt_id,
        )

    def validate_exact_refs(
        self,
        references: object,
        *,
        run_id: str | None = None,
        expected_attempt_id: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(references, list):
            return {"valid": [], "invalid": [{"reason": "evidence_refs must be a list"}]}
        valid: list[dict[str, Any]] = []
        invalid: list[dict[str, Any]] = []
        for reference in references:
            result = self.validate_exact_ref(
                reference,
                run_id=run_id,
                expected_attempt_id=expected_attempt_id,
            )
            if result["valid"]:
                valid.append(result["normalized"])
            else:
                invalid.append(result)
        return {"valid": valid, "invalid": invalid}


class AgenticEvidenceValidator:
    """Small standalone adapter for P12 services and worker validators."""

    def __init__(self, artifact_root: str | Path) -> None:
        self._service = AgenticValidationService(artifact_root)

    def validate_ref(
        self,
        reference: object,
        *,
        run_id: str | None = None,
        expected_attempt_id: str | None = None,
    ) -> dict[str, Any]:
        return self._service.validate_exact_ref(
            reference,
            run_id=run_id,
            expected_attempt_id=expected_attempt_id,
        )

    def validate_refs(
        self,
        references: object,
        *,
        run_id: str | None = None,
        expected_attempt_id: str | None = None,
    ) -> dict[str, Any]:
        return self._service.validate_exact_refs(
            references,
            run_id=run_id,
            expected_attempt_id=expected_attempt_id,
        )


def normalize_agentic_evidence_ref(reference: object, *, run_id: str | None = None) -> dict[str, Any]:
    """Normalize old artifact_path/field refs into the P12 exact-ref shape.

    Normalization is lossless for the observed value and reason.  It does not
    claim a reference is valid; callers must still run ``validate_exact...``.
    """

    if not isinstance(reference, dict):
        return {}
    if "artifact_ref" in reference and "reference_kind" in reference:
        return dict(reference)
    artifact_path = str(reference.get("artifact_path") or "").strip()
    field_path = str(reference.get("field") or "").strip()
    if not artifact_path or not field_path:
        return dict(reference)
    artifact_ref = artifact_path.replace("\\", "/").lstrip("/")
    if run_id and not artifact_ref.startswith(f"runs/{run_id}/"):
        artifact_ref = f"runs/{run_id}/{artifact_ref}"
    normalized = {
        "artifact_ref": artifact_ref,
        "reference_kind": "persisted_field",
        "field_path": field_path,
    }
    for key in ("observed", "reason", "source_status"):
        if key in reference:
            normalized[key] = reference[key]
    return normalized


def validate_exact_evidence_ref(
    artifact_root: str | Path,
    reference: object,
    *,
    run_id: str | None = None,
    expected_attempt_id: str | None = None,
) -> dict[str, Any]:
    """Resolve and verify one persisted P12 reference.

    ``artifact_ref`` may be ``runs/<run-id>/...`` or run-relative.  For a
    source span the exact text must occur in the persisted JSON artifact; for a
    persisted field the field resolves and, when supplied, equals ``observed``.
    DOM, screenshot, and provider refs are shape-checked because their payloads
    are owned by their respective artifact services.
    """

    normalized = normalize_agentic_evidence_ref(reference, run_id=run_id)
    if not normalized:
        return {"valid": False, "reason": "evidence reference must be an object"}
    artifact_ref = str(normalized.get("artifact_ref") or "").strip().replace("\\", "/")
    kind = str(normalized.get("reference_kind") or "").strip()
    if not artifact_ref or kind not in {
        "source_span",
        "persisted_field",
        "dom",
        "screenshot",
        "provider_artifact",
    }:
        return {"valid": False, "reason": "unsupported P12 evidence reference shape", "normalized": normalized}
    if kind == "source_span" and not str(normalized.get("exact_span") or "").strip():
        return {"valid": False, "reason": "source-span evidence requires exact_span", "normalized": normalized}
    if kind == "persisted_field" and not str(normalized.get("field_path") or "").strip():
        return {"valid": False, "reason": "persisted-field evidence requires field_path", "normalized": normalized}
    if kind == "dom" and not str(normalized.get("dom_ref") or "").strip():
        return {"valid": False, "reason": "DOM evidence requires dom_ref", "normalized": normalized}
    if kind == "screenshot" and not str(normalized.get("screenshot_ref") or "").strip():
        return {"valid": False, "reason": "screenshot evidence requires screenshot_ref", "normalized": normalized}
    if kind == "provider_artifact" and not str(normalized.get("response_span") or "").strip():
        return {"valid": False, "reason": "provider evidence requires response_span", "normalized": normalized}

    # Provider/DOM/screenshot references are persisted by different services;
    # still enforce run-boundary safety when the artifact root is available.
    root = Path(artifact_root).resolve()
    relative_ref = artifact_ref
    if run_id and relative_ref.startswith(f"runs/{run_id}/"):
        relative_ref = relative_ref[len(f"runs/{run_id}/") :]
    elif relative_ref.startswith("runs/"):
        parts = relative_ref.split("/", 2)
        if len(parts) < 3 or (run_id and parts[1] != run_id):
            return {"valid": False, "reason": "evidence reference belongs to another run", "normalized": normalized}
        relative_ref = parts[2]
    relative = Path(relative_ref)
    if relative.is_absolute() or ".." in relative.parts:
        return {"valid": False, "reason": "evidence reference escapes run boundary", "normalized": normalized}
    # Customer-safe P12 output is only allowed after the artifact is actually
    # persisted.  Worker preflight may retain a candidate separately, but it
    # must not promote that candidate to a positive fact/answer.
    artifact = (root / "runs" / run_id / relative if run_id else root / relative).resolve()
    try:
        boundary = (root / "runs" / run_id if run_id else root).resolve()
        artifact.relative_to(boundary)
    except ValueError:
        return {"valid": False, "reason": "evidence reference escapes run boundary", "normalized": normalized}
    if not artifact.is_file():
        return {"valid": False, "reason": "evidence artifact is not persisted", "normalized": normalized}
    try:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "reason": f"evidence artifact is unreadable: {exc}", "normalized": normalized}
    if expected_attempt_id is not None and isinstance(payload, dict):
        if payload.get("attempt_id") not in {None, expected_attempt_id}:
            return {"valid": False, "reason": "evidence artifact belongs to another attempt", "normalized": normalized}
    if kind == "persisted_field":
        try:
            resolved = resolve_evidence_field(payload, str(normalized["field_path"]))
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            return {"valid": False, "reason": f"evidence field cannot be resolved: {exc}", "normalized": normalized}
        if "observed" in normalized and type(resolved) is not type(normalized["observed"]):
            return {"valid": False, "reason": "observed value type does not match persisted field", "normalized": normalized}
        if "observed" in normalized and resolved != normalized["observed"]:
            return {"valid": False, "reason": "observed value does not match persisted field", "normalized": normalized}
    elif kind == "source_span":
        exact = str(normalized["exact_span"])
        if exact not in artifact.read_text(encoding="utf-8"):
            return {"valid": False, "reason": "exact source span is not present in artifact", "normalized": normalized}
    normalized["artifact_ref"] = artifact_ref
    return {"valid": True, "normalized": normalized}


__all__ = [
    "AgenticValidationService",
    "AgenticEvidenceValidator",
    "normalize_agentic_evidence_ref",
    "validate_exact_evidence_ref",
]

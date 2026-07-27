"""Evidence-only comparison of sampled AI responses with business facts.

This module intentionally does not collect provider responses.  It consumes
already persisted, context-compatible ``AIVisibilityService`` rows and a
validated :class:`BusinessFactLedgerSnapshot`, then produces the separate
``AIRepresentationAccuracySnapshot`` evidence contract.  The result never
feeds SEO, AI Readiness, visibility, demand, conversion, or revenue math.

The response text is treated as untrusted input.  A claim is customer-safe only
when its exact span resolves to a persisted provider artifact and any positive
classification resolves to an approved public ledger fact with exact evidence.
Unknown facts remain ``unverifiable`` rather than being inferred as a failure
or a negative claim.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from datetime import date
import json
from pathlib import Path
from typing import Any

from src.models import (
    AI_REPRESENTATION_ACCURACY_VERSION,
    AI_REPRESENTATION_STATUSES,
    AIRepresentationAccuracySnapshot,
    BusinessFactLedgerSnapshot,
    canonical_sha256,
)
from src.services.ai_visibility_service import AIVisibilityContext, AIVisibilityService


_STATUS_VALUES = set(AI_REPRESENTATION_STATUSES)
_MAX_CLAIMS = 64
_RESPONSE_KEYS = ("response_text", "answer", "markdown", "text", "content")
_NESTED_RESPONSE_KEYS = ("response", "result", "ai_overview", "answer")
_NEGATION_RE = re.compile(
    r"\b(?:no|not|never|without|doesn['’]?t|does\s+not|isn['’]?t|is\s+not|aren['’]?t|are\s+not)\b",
    re.IGNORECASE,
)
_FACTUAL_RE = re.compile(
    r"\b(?:is|are|has|have|offers?|provides?|serves?|located|open|closed|available|includes?|costs?|starts?|from)\b|\d",
    re.IGNORECASE,
)
_WORD_RE = re.compile(r"[a-z0-9]+")


def _payload(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    return dict(value) if isinstance(value, Mapping) else {}


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(_text(item) for item in value.values() if item is not None)
    if isinstance(value, (list, tuple, set)):
        return " ".join(_text(item) for item in value)
    return str(value or "")


def _normalized(value: Any) -> str:
    return " ".join(_WORD_RE.findall(_text(value).casefold()))


def _terms(value: Any) -> set[str]:
    """Small deterministic singular/plural normalization for field names."""

    terms = set(_WORD_RE.findall(_text(value).casefold()))
    return terms | {term[:-1] for term in terms if len(term) > 3 and term.endswith("s")}


def _date_value(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _fact_value(fact: Mapping[str, Any]) -> Any:
    for key in ("normalized_value", "value", "observed_value", "fact_value"):
        if key in fact and fact[key] not in (None, "", [], {}):
            return fact[key]
    return None


def _fact_date(fact: Mapping[str, Any]) -> date | None:
    for key in ("as_of", "observed_at", "source_date", "valid_from", "updated_at"):
        parsed = _date_value(fact.get(key))
        if parsed:
            return parsed
    return None


def _raw_artifact_ref(row: Mapping[str, Any]) -> str:
    for key in ("raw_artifact_ref", "provider_artifact_ref", "artifact_ref"):
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def _response_body(row: Mapping[str, Any]) -> str:
    """Return bounded response text without fetching a raw artifact."""

    for key in _RESPONSE_KEYS:
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for key in _NESTED_RESPONSE_KEYS:
        value = row.get(key)
        if isinstance(value, Mapping):
            nested = _response_body(value)
            if nested:
                return nested
        elif isinstance(value, list):
            chunks = [_response_body(item) for item in value if isinstance(item, Mapping)]
            text = " ".join(chunk for chunk in chunks if chunk)
            if text:
                return text
    # AI Visibility rows often contain an ``items``/``results`` envelope.
    for key in ("items", "results"):
        value = row.get(key)
        if isinstance(value, list):
            chunks = [_response_body(item) for item in value if isinstance(item, Mapping)]
            text = " ".join(chunk for chunk in chunks if chunk)
            if text:
                return text
    return ""


def _clean_span(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", text)
    return text.strip()


def _sentence_spans(text: str) -> list[str]:
    if not text:
        return []
    # Keep the exact source substring (apart from surrounding whitespace) so
    # the provider evidence reference can be independently resolved later.
    pieces = re.split(r"(?<=[.!?])\s+|\r?\n+", text)
    output: list[str] = []
    seen: set[str] = set()
    for piece in pieces:
        span = _clean_span(piece)
        if not span or len(span) < 3:
            continue
        key = span.casefold()
        if key in seen:
            continue
        seen.add(key)
        output.append(span)
    return output


def _context_value(row: Mapping[str, Any], key: str) -> Any:
    nested = row.get("context")
    if isinstance(nested, Mapping) and key in nested:
        return nested.get(key)
    return row.get(key)


def _context_matches(row: Mapping[str, Any], context: Mapping[str, Any] | AIVisibilityContext | None) -> bool:
    if context is None:
        return True
    expected = context.to_dict() if isinstance(context, AIVisibilityContext) else dict(context)
    for key in ("market", "location_code", "language_code", "device", "snapshot_date"):
        value = expected.get(key)
        if value is None or value == "":
            continue
        observed = _context_value(row, key)
        if observed != value:
            return False
    return True


def _reference(artifact_ref: str, span: str) -> dict[str, str]:
    return {
        "artifact_ref": artifact_ref,
        "reference_kind": "provider_artifact",
        "response_span": span,
    }


class AIRepresentationAccuracyService:
    """Build representation accuracy from persisted evidence only."""

    VERSION = AI_REPRESENTATION_ACCURACY_VERSION
    MAX_CLAIMS = _MAX_CLAIMS

    def __init__(self, artifact_root: str | Path = ".", *, max_artifact_bytes: int = 1_000_000) -> None:
        self.artifact_root = Path(artifact_root).resolve()
        self.max_artifact_bytes = max(1_024, int(max_artifact_bytes))

    def preflight(
        self,
        evidence: Iterable[Mapping[str, Any]] | None = None,
        *,
        topic_set: Any = None,
        context: Mapping[str, Any] | AIVisibilityContext | None = None,
    ) -> dict[str, Any]:
        """Return a no-network reuse check for existing AI Visibility rows."""

        rows = [dict(row) for row in (evidence or []) if isinstance(row, Mapping)]
        compatible = [row for row in rows if self._compatible_row(row, topic_set, context)]
        return {
            "surface": "ai_representation_accuracy",
            "contract_version": self.VERSION,
            "existing_rows": len(rows),
            "reusable_rows": len(compatible),
            "planned_provider_calls": 0,
            "network_check_performed": False,
            "status": "ready" if compatible else "unknown",
            "blocked_reason": None if compatible else "No context-compatible persisted AI Visibility response artifacts.",
        }

    def analyze(
        self,
        evidence: Iterable[Mapping[str, Any]] | None = None,
        ledger: BusinessFactLedgerSnapshot | Mapping[str, Any] | None = None,
        *,
        run_id: str | None = None,
        attempt_id: str | None = None,
        work_item_id: str | None = None,
        fact_ledger_id: str | None = None,
        source_sha256: str | None = None,
        mode: str = "prospect",
        topic_set: Any = None,
        context: Mapping[str, Any] | AIVisibilityContext | None = None,
        response_artifacts: Iterable[Mapping[str, Any]] | None = None,
        observations: Iterable[Mapping[str, Any]] | None = None,
        **_: Any,
    ) -> AIRepresentationAccuracySnapshot:
        """Compare existing response rows with approved public ledger facts.

        ``provider``/collection arguments are intentionally ignored by this
        method.  Paid collection belongs to the separately approved
        ``AIVisibilityService.collect`` operation and is never performed here.
        """

        rows_input = evidence
        if rows_input is None:
            rows_input = response_artifacts if response_artifacts is not None else observations
        rows = [dict(row) for row in (rows_input or []) if isinstance(row, Mapping)]
        ledger_payload = _payload(ledger)
        if not ledger_payload:
            raise ValueError("AI representation accuracy requires a persisted fact ledger")
        run_id = str(run_id or ledger_payload.get("run_id") or "").strip()
        attempt_id = str(attempt_id or ledger_payload.get("attempt_id") or "").strip()
        fact_ledger_id = str(fact_ledger_id or ledger_payload.get("id") or "").strip()
        work_item_id = str(work_item_id or ledger_payload.get("work_item_id") or "").strip()
        if not all((run_id, attempt_id, fact_ledger_id, work_item_id)):
            raise ValueError("AI representation accuracy requires run, attempt, work, and ledger identity")

        compatible: list[dict[str, Any]] = []
        rejected_context = 0
        missing_artifact = 0
        for row in rows:
            if not self._compatible_row(row, topic_set, context):
                rejected_context += 1
                continue
            if not _raw_artifact_ref(row) and not self._has_explicit_claim_refs(row):
                missing_artifact += 1
                continue
            compatible.append(row)

        public_facts = self._public_facts(ledger_payload)
        claims: list[dict[str, Any]] = []
        limitations: list[str] = []
        total_rows = len(rows)
        if rejected_context:
            limitations.append(f"{rejected_context} response rows were excluded because their market/context did not match the requested sample.")
        if missing_artifact:
            limitations.append(f"{missing_artifact} response rows lacked a persisted provider artifact and were not classified.")
        if not compatible:
            limitations.append("No context-compatible persisted AI Visibility response artifacts were available; representation remains unknown.")
        if not public_facts:
            limitations.append("No approved public fact with exact ledger evidence was available; claims remain unverifiable.")
        if str(ledger_payload.get("review_state") or "needs_review") != "approved":
            limitations.append("The fact ledger is not operator-approved; output remains review-only.")

        for row_index, row in enumerate(compatible):
            body = self._response_body(row)
            raw_ref = _raw_artifact_ref(row)
            candidates = self._candidate_claims(row, body)
            for claim_index, candidate in enumerate(candidates):
                if len(claims) >= self.MAX_CLAIMS:
                    limitations.append(f"Claim extraction was capped at {self.MAX_CLAIMS} claims.")
                    break
                span = _clean_span(candidate.get("response_span") or candidate.get("claim"))
                claim_text = _clean_span(candidate.get("claim") or span)
                if not span or not claim_text:
                    continue
                if body and span not in body:
                    # A supplied model span that cannot be found in the
                    # persisted response is not customer-safe evidence.
                    limitations.append(f"Response claim {row_index + 1}-{claim_index + 1} did not resolve to an exact provider span.")
                    continue
                artifact_ref = str(candidate.get("artifact_ref") or raw_ref).strip()
                if not artifact_ref:
                    limitations.append(f"Response claim {row_index + 1}-{claim_index + 1} lacked a persisted provider artifact.")
                    continue
                response_ref = _reference(artifact_ref, span)
                classification, matched, reason = self._classify_claim(
                    claim_text,
                    candidate,
                    public_facts,
                    snapshot_date=_context_value(row, "snapshot_date"),
                )
                fact_refs: list[dict[str, Any]] = []
                for fact in matched:
                    fact_refs.extend(dict(ref) for ref in fact.get("evidence_refs", []) if isinstance(ref, Mapping))
                # The immutable model requires a grounding ref for every
                # classification other than unverifiable.  An explicit
                # caller-provided unsupported classification is accepted only
                # when it already supplies an exact ledger ref.
                if classification != "unverifiable" and not fact_refs:
                    classification = "unverifiable"
                    reason = "No validated public ledger fact resolved the claim."
                claims.append(
                    {
                        "claim_id": str(candidate.get("claim_id") or f"representation-{row_index + 1}-{claim_index + 1}"),
                        "claim": claim_text,
                        "classification": classification,
                        "reason": reason,
                        "confidence": "high" if classification == "correct" else "medium" if matched else "low",
                        "response_evidence_ref": response_ref,
                        "fact_ids": [str(fact.get("fact_id")) for fact in matched],
                        "fact_evidence_refs": fact_refs,
                        "topic_id": row.get("topic_id") or row.get("prompt_id"),
                        "prompt": row.get("prompt") or row.get("keyword"),
                        "snapshot_date": _context_value(row, "snapshot_date"),
                    }
                )

        completeness = (len(compatible) / total_rows * 100.0) if total_rows else 0.0
        if total_rows and len(compatible) == total_rows:
            completeness = 100.0
        elif total_rows:
            completeness = round(completeness, 4)
        digest_source = {
            "contract_version": self.VERSION,
            "ledger_id": fact_ledger_id,
            "ledger_source_sha256": ledger_payload.get("source_sha256"),
            "responses": [
                {
                    "artifact_ref": _raw_artifact_ref(row),
                    "topic_id": row.get("topic_id") or row.get("prompt_id"),
                    "snapshot_date": _context_value(row, "snapshot_date"),
                }
                for row in compatible
            ],
            "context": context.to_dict() if isinstance(context, AIVisibilityContext) else dict(context or {}),
        }
        source_hash = str(source_sha256 or "").strip()
        if source_hash and (
            len(source_hash) != 64
            or any(char not in "0123456789abcdefABCDEF" for char in source_hash)
        ):
            raise ValueError("AI representation source hash must be SHA-256")
        source_hash = source_hash or canonical_sha256(digest_source)
        return AIRepresentationAccuracySnapshot(
            run_id=run_id,
            attempt_id=attempt_id,
            work_item_id=work_item_id,
            fact_ledger_id=fact_ledger_id,
            source_sha256=source_hash.casefold(),
            claims=claims,
            mode=mode,
            completeness_percent=completeness,
            limitations=sorted(set(limitations)),
            review_state="needs_review",
        )

    build = analyze
    evaluate = analyze

    def collect(self, *args: Any, **kwargs: Any) -> AIRepresentationAccuracySnapshot:
        """Explicitly reject provider collection in the representation layer."""

        if kwargs.get("provider") is not None or kwargs.get("allow_paid_api_calls"):
            raise RuntimeError(
                "AI representation accuracy consumes persisted AI Visibility artifacts; paid collection requires separate operator approval."
            )
        return self.analyze(*args, **kwargs)

    @staticmethod
    def _compatible_row(
        row: Mapping[str, Any],
        topic_set: Any,
        context: Mapping[str, Any] | AIVisibilityContext | None,
    ) -> bool:
        status = str(row.get("status") or "complete").casefold()
        if status not in {"complete", "success", "completed"}:
            return False
        if topic_set is not None:
            service = AIVisibilityService()
            requested = service._context(context, topic_set)
            if not service._evidence_matches(row, topic_set, requested):
                return False
        return _context_matches(row, context)

    def _response_body(self, row: Mapping[str, Any]) -> str:
        """Read an already persisted raw response when the row is an index.

        No URL or provider access is attempted.  The resolved path must stay
        beneath ``artifact_root`` and is bounded before JSON parsing.
        """

        inline = _response_body(row)
        if inline:
            return inline
        artifact_ref = _raw_artifact_ref(row)
        if not artifact_ref:
            return ""
        try:
            candidate = Path(artifact_ref)
            if not candidate.is_absolute():
                candidate = self.artifact_root / candidate
            candidate = candidate.resolve()
            if self.artifact_root not in candidate.parents:
                return ""
            if not candidate.is_file() or candidate.stat().st_size > self.max_artifact_bytes:
                return ""
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            return ""
        return self._nested_response_text(payload)

    @classmethod
    def _nested_response_text(cls, payload: Any, *, depth: int = 0) -> str:
        if depth > 5:
            return ""
        inline = _response_body(payload if isinstance(payload, Mapping) else {})
        if inline:
            return inline
        if isinstance(payload, Mapping):
            for key in ("tasks", "result", "results", "items", "data", "response"):
                value = payload.get(key)
                found = cls._nested_response_text(value, depth=depth + 1)
                if found:
                    return found
        elif isinstance(payload, list):
            for item in payload[:64]:
                found = cls._nested_response_text(item, depth=depth + 1)
                if found:
                    return found
        return ""

    @staticmethod
    def _has_explicit_claim_refs(row: Mapping[str, Any]) -> bool:
        values = row.get("claims") or row.get("atomic_claims")
        if not isinstance(values, list):
            return False
        return any(
            isinstance(item, Mapping)
            and str(item.get("response_span") or item.get("claim") or item.get("text") or "").strip()
            and str(item.get("artifact_ref") or row.get("raw_artifact_ref") or "").strip()
            for item in values
        )

    @staticmethod
    def _candidate_claims(row: Mapping[str, Any], body: str) -> list[dict[str, Any]]:
        explicit = row.get("claims") or row.get("atomic_claims")
        if isinstance(explicit, list):
            candidates = [dict(item) for item in explicit if isinstance(item, Mapping)]
            if candidates:
                return candidates
        return [{"claim": span, "response_span": span} for span in _sentence_spans(body)]

    @staticmethod
    def _public_facts(ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
        facts = ledger.get("facts") if isinstance(ledger.get("facts"), list) else []
        valid: list[dict[str, Any]] = []
        for raw in facts:
            if not isinstance(raw, Mapping):
                continue
            fact = dict(raw)
            if str(fact.get("source_status") or "") not in {"observed", "business_supplied"}:
                continue
            if str(fact.get("sensitivity_class") or "") != "public":
                continue
            if str(fact.get("approval_state") or "") != "approved":
                continue
            if not str(fact.get("fact_id") or "").strip() or not str(fact.get("name") or "").strip():
                continue
            value = _fact_value(fact)
            refs = fact.get("evidence_refs")
            if value in (None, "", [], {}) or not isinstance(refs, list) or not refs:
                continue
            valid.append(fact)
        return valid

    @classmethod
    def _classify_claim(
        cls,
        claim: str,
        candidate: Mapping[str, Any],
        facts: list[Mapping[str, Any]],
        *,
        snapshot_date: Any = None,
    ) -> tuple[str, list[dict[str, Any]], str]:
        if not facts:
            return "unverifiable", [], "No validated public ledger fact is available."
        claim_norm = _normalized(claim)
        claim_date = _date_value(snapshot_date)
        matched_exact: list[dict[str, Any]] = []
        matched_field: list[dict[str, Any]] = []
        partial: list[dict[str, Any]] = []
        for raw in facts:
            fact = dict(raw)
            name_norm = _normalized(fact.get("name"))
            value = _fact_value(fact)
            value_norm = _normalized(value)
            aliases = [_normalized(alias) for alias in (fact.get("aliases") or fact.get("terms") or [])]
            claim_terms = _terms(claim)
            field_match = bool(
                name_norm
                and (
                    name_norm in claim_norm
                    or bool(_terms(fact.get("name")) & claim_terms)
                    or any(alias and (alias in claim_norm or bool(_terms(alias) & claim_terms)) for alias in aliases)
                )
            )
            value_match = bool(value_norm and value_norm in claim_norm)
            if value_match:
                matched_exact.append(fact)
            elif field_match:
                matched_field.append(fact)
                value_tokens = set(value_norm.split())
                claim_tokens = set(claim_norm.split())
                if value_tokens and value_tokens.intersection(claim_tokens):
                    partial.append(fact)
        if matched_exact:
            # A claim that repeats the known value is correct unless the
            # source was captured before a newer conflicting fact.
            outdated = [fact for fact in matched_exact if cls._is_outdated(fact, claim_date)]
            if outdated:
                return "outdated", outdated, "The provider response predates a newer validated ledger observation."
            return "correct", matched_exact, "The response claim matches a validated public ledger fact."
        if partial and _NEGATION_RE.search(claim):
            return "contradicted", partial, "The response negates or conflicts with a validated public ledger fact."
        if partial:
            return "incomplete", partial, "The response mentions part of a validated fact but omits or narrows its supported value."
        if matched_field:
            if _NEGATION_RE.search(claim):
                return "contradicted", matched_field, "The response negates or conflicts with a validated public ledger fact."
            if any(cls._is_outdated(fact, claim_date) for fact in matched_field):
                return "outdated", matched_field, "The response gives a field value that is older than the validated ledger observation."
            hint = str(candidate.get("classification") or candidate.get("classification_hint") or "").casefold()
            if hint in _STATUS_VALUES and hint != "unverifiable":
                return hint, matched_field, "The response supplied an explicit classification requiring review against the ledger."
            return "contradicted", matched_field, "The response names a known field but does not match its validated public value."
        # A factual-looking statement without a matching public fact is an
        # unsupported representation, but it cannot be customer-safe without
        # a ledger ref.  The caller therefore downgrades it to unverifiable.
        if _FACTUAL_RE.search(claim):
            return "unsupported", [], "The response makes a factual assertion that is outside the validated public fact ledger."
        return "unverifiable", [], "The response cannot be verified against the available public fact ledger."

    @staticmethod
    def _is_outdated(fact: Mapping[str, Any], response_date: date | None) -> bool:
        fact_date = _fact_date(fact)
        return bool(fact_date and response_date and response_date < fact_date and _fact_value(fact))


def analyze_ai_representation_accuracy(*args: Any, **kwargs: Any) -> AIRepresentationAccuracySnapshot:
    return AIRepresentationAccuracyService().analyze(*args, **kwargs)


__all__ = [
    "AIRepresentationAccuracyService",
    "analyze_ai_representation_accuracy",
]

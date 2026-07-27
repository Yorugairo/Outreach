"""Private owner-mode evidence packing and non-causal diagnostic validation."""

from __future__ import annotations

import re
from typing import Any, Iterable

from src.models import (
    AgenticWorkItem,
    OwnedMeasurementSnapshot,
    OwnerDiagnosticSnapshot,
    canonical_sha256,
)
from src.repositories.base import InsightRepository


_CAUSAL_ASSERTION_RE = re.compile(
    r"\b(?:caused?|guarantees?|led to|resulted in|responsible for|will increase|will produce)\b",
    re.IGNORECASE,
)
_PRIVATE_FIELD_RE = re.compile(
    r"(?:email|phone|first_name|last_name|full_name|lead_id|customer_id|"
    r"api_key|authorization|cookie|credential|oauth|password|refresh_token|secret)",
    re.IGNORECASE,
)


class OwnerAgenticAnalysisService:
    """Builds private aggregate evidence without exposing owner data to prospect mode."""

    def __init__(self, repository: InsightRepository) -> None:
        self.repository = repository

    def preflight(
        self,
        *,
        prospect_id: str,
        vertical_id: str,
        approved_snapshot_ids: Iterable[str],
        consent_id: str,
    ) -> dict[str, Any]:
        snapshots = self._resolve_sources(
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            approved_snapshot_ids=approved_snapshot_ids,
            consent_id=consent_id,
        )
        return {
            "available": True,
            "mode": "owner_verified",
            "privacy_scope": "private_owner_only",
            "prospect_id": prospect_id,
            "vertical_id": vertical_id,
            "consent_id": consent_id,
            "approved_source_snapshot_ids": [item.id for item in snapshots],
            "source_count": len(snapshots),
            "sources": sorted({item.source for item in snapshots}),
            "aggregate_only": True,
        }

    def build_evidence_pack(
        self,
        *,
        prospect_id: str,
        vertical_id: str,
        approved_snapshot_ids: Iterable[str],
        consent_id: str,
    ) -> dict[str, Any]:
        snapshots = self._resolve_sources(
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            approved_snapshot_ids=approved_snapshot_ids,
            consent_id=consent_id,
        )
        sources = [
            {
                "snapshot_id": snapshot.id,
                "source": snapshot.source,
                "period_start": snapshot.period_start,
                "period_end": snapshot.period_end,
                "source_sha256": snapshot.source_sha256,
                "artifact_ref": snapshot.artifact_ref,
                "metrics": dict(snapshot.metrics),
                "context": self._safe_context(snapshot.context),
            }
            for snapshot in snapshots
        ]
        payload = {
            "mode": "owner_verified",
            "privacy_scope": "private_owner_only",
            "prospect_id": prospect_id,
            "vertical_id": vertical_id,
            "consent_id": consent_id,
            "sources": sources,
            "instructions": [
                "Treat all values as aggregate observations.",
                "Label interpretations as hypotheses.",
                "Do not assert causality or modify deterministic calculations.",
            ],
        }
        self._reject_private_fields(payload)
        return {**payload, "source_sha256": canonical_sha256(payload)}

    def create_snapshot(
        self,
        *,
        work_item: AgenticWorkItem,
        prospect_id: str,
        vertical_id: str,
        approved_snapshot_ids: Iterable[str],
        observations: list[dict[str, Any]],
        hypotheses: list[dict[str, Any]],
        limitations: list[str] | None = None,
    ) -> OwnerDiagnosticSnapshot:
        if work_item.work_kind != "owner_diagnostic":
            raise ValueError("owner analysis requires an owner-diagnostic work item")
        if work_item.mode != "owner_verified" or not work_item.consent_id:
            raise ValueError("owner analysis requires consent-bound owner mode")
        pack = self.build_evidence_pack(
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            approved_snapshot_ids=approved_snapshot_ids,
            consent_id=work_item.consent_id,
        )
        sources = {item["snapshot_id"]: item for item in pack["sources"]}
        normalized_observations = [
            self._validate_entry(
                payload,
                entry_kind="observation",
                source_records=sources,
            )
            for payload in observations
        ]
        normalized_hypotheses = [
            self._validate_entry(
                payload,
                entry_kind="hypothesis",
                source_records=sources,
            )
            for payload in hypotheses
        ]
        snapshot = OwnerDiagnosticSnapshot(
            run_id=work_item.run_id,
            attempt_id=work_item.attempt_id,
            prospect_id=prospect_id,
            work_item_id=work_item.id,
            consent_id=work_item.consent_id,
            approved_source_snapshot_ids=list(sources),
            source_sha256=str(pack["source_sha256"]),
            observations=normalized_observations,
            hypotheses=normalized_hypotheses,
            limitations=list(limitations or []),
        )
        return self.repository.save_owner_diagnostic_snapshot(snapshot)

    @staticmethod
    def client_payload(
        snapshot: OwnerDiagnosticSnapshot,
        *,
        requested_mode: str,
    ) -> dict[str, Any]:
        if requested_mode != "owner_verified":
            raise ValueError("owner diagnostic evidence cannot enter prospect output")
        payload = snapshot.to_dict()
        if payload.get("privacy_scope") != "private_owner_only":
            raise ValueError("owner diagnostic privacy scope is invalid")
        return payload

    def _resolve_sources(
        self,
        *,
        prospect_id: str,
        vertical_id: str,
        approved_snapshot_ids: Iterable[str],
        consent_id: str,
    ) -> list[OwnedMeasurementSnapshot]:
        identifiers = list(dict.fromkeys(str(value).strip() for value in approved_snapshot_ids))
        if not identifiers or any(not value for value in identifiers):
            raise ValueError("owner analysis requires explicitly approved P11 snapshot IDs")
        if not consent_id.strip():
            raise ValueError("owner analysis requires a consent identity")
        snapshots: list[OwnedMeasurementSnapshot] = []
        for snapshot_id in identifiers:
            snapshot = self.repository.get_owned_measurement_snapshot(snapshot_id)
            if snapshot is None:
                raise ValueError(f"approved owner snapshot not found: {snapshot_id}")
            if snapshot.prospect_id != prospect_id or snapshot.vertical_id != vertical_id:
                raise ValueError("owner snapshot is outside the requested prospect/vertical scope")
            consent = snapshot.context.get("owner_consent")
            if not isinstance(consent, dict) or consent.get("confirmed") is not True:
                raise ValueError("owner snapshot lacks confirmed consent")
            required = ("operator", "confirmed_at")
            if any(not str(consent.get(key) or "").strip() for key in required):
                raise ValueError("owner snapshot consent lacks operator provenance")
            observed_consent_id = str(snapshot.context.get("consent_id") or "").strip()
            if not observed_consent_id:
                observed_consent_id = canonical_sha256(consent)
            if observed_consent_id != consent_id:
                raise ValueError("owner snapshot consent identity does not match")
            freshness = snapshot.context.get("data_freshness")
            if isinstance(freshness, dict) and freshness.get("status") == "stale":
                raise ValueError("stale owner evidence cannot enter agentic diagnosis")
            if not snapshot.metrics:
                raise ValueError("owner analysis accepts aggregate measurement metrics only")
            snapshots.append(snapshot)
        return snapshots

    @classmethod
    def _validate_entry(
        cls,
        payload: dict[str, Any],
        *,
        entry_kind: str,
        source_records: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("owner diagnostic entries must be structured records")
        text = str(payload.get("text") or "").strip()
        entry_id = str(
            payload.get("observation_id")
            or payload.get("hypothesis_id")
            or payload.get("id")
            or ""
        ).strip()
        if not entry_id or not text:
            raise ValueError("owner diagnostic entries require identity and text")
        if _CAUSAL_ASSERTION_RE.search(text) or payload.get("causal") is True:
            raise ValueError("owner diagnostics cannot assert causality")
        references = payload.get("evidence_refs")
        if not isinstance(references, list) or not references:
            raise ValueError("owner diagnostic entries require aggregate evidence")
        normalized_refs: list[dict[str, Any]] = []
        for reference in references:
            if not isinstance(reference, dict):
                raise ValueError("owner evidence references must be structured records")
            snapshot_id = str(reference.get("snapshot_id") or "").strip()
            field_path = str(reference.get("field_path") or "").strip()
            source = source_records.get(snapshot_id)
            if source is None:
                raise ValueError("owner evidence reference is not in the approved source set")
            if not field_path.startswith("metrics."):
                raise ValueError("owner diagnosis may reference aggregate metric fields only")
            metric = field_path.removeprefix("metrics.")
            if metric not in source["metrics"]:
                raise ValueError("owner evidence metric field does not resolve")
            normalized_refs.append(
                {
                    "artifact_ref": source["artifact_ref"],
                    "reference_kind": "persisted_field",
                    "field_path": field_path,
                    "snapshot_id": snapshot_id,
                    "source_sha256": source["source_sha256"],
                }
            )
        result = {
            f"{entry_kind}_id": entry_id,
            "text": text,
            "evidence_refs": normalized_refs,
            "inference": entry_kind == "hypothesis",
            "causal_claim": False,
        }
        cls._reject_private_fields(result)
        return result

    @staticmethod
    def _safe_context(context: dict[str, Any]) -> dict[str, Any]:
        allowed = {
            "market",
            "property_id",
            "site_url",
            "location_id",
            "event_map_id",
            "event_map_version",
            "data_freshness",
            "owner_verified",
        }
        return {key: value for key, value in context.items() if key in allowed}

    @classmethod
    def _reject_private_fields(cls, payload: Any, *, path: str = "") -> None:
        if isinstance(payload, dict):
            for key, value in payload.items():
                current = f"{path}.{key}" if path else str(key)
                if _PRIVATE_FIELD_RE.search(str(key)):
                    raise ValueError(f"owner diagnostic pack contains a private field: {current}")
                cls._reject_private_fields(value, path=current)
        elif isinstance(payload, list):
            for index, value in enumerate(payload):
                cls._reject_private_fields(value, path=f"{path}[{index}]")

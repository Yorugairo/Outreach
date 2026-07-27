"""Validation and privacy gates for demand-conversion report/export modes."""

from __future__ import annotations

import re
import json
from pathlib import Path, PurePosixPath
from typing import Any

from src.models import DemandConversionEvidence, canonical_sha256
from src.repositories.base import InsightRepository


_PRIVATE_KEY_RE = re.compile(
    r"(?:email|phone|first_name|last_name|full_name|lead_id|customer_id|"
    r"api_key|authorization|cookie|credential|oauth|password|refresh_token|secret)",
    re.IGNORECASE,
)


class DemandConversionReportValidationService:
    """Resolve source identities and prevent cross-mode/cross-prospect leakage."""

    def __init__(self, repository: InsightRepository) -> None:
        self.repository = repository

    def validate(
        self,
        evidence: DemandConversionEvidence | str,
        *,
        requested_mode: str | None = None,
        for_export: bool = False,
    ) -> dict[str, Any]:
        record = self._resolve(evidence)
        if requested_mode is not None and requested_mode != record.mode:
            raise ValueError(
                "demand conversion mode cannot be changed during report/export"
            )
        if for_export and record.state != "approved":
            raise ValueError(
                "demand conversion export requires approved immutable evidence"
            )
        self._validate_private_keys(record.to_dict())
        owner_sources = [
            source
            for source in record.source_snapshots
            if source.get("source_class") == "owner_first_party"
        ]
        if record.mode == "prospect" and owner_sources:
            raise ValueError("prospect reports cannot contain owner-first-party sources")
        if record.mode == "owner_verified" and not owner_sources:
            raise ValueError("owner-verified reports require owner-first-party sources")
        resolved_refs = [
            self._resolve_ref(record, ref, require_artifact=for_export)
            for ref in record.evidence_refs
        ]
        self._validate_source_coverage(
            record,
            resolved_refs,
            require_artifact=for_export,
        )
        for source in record.source_snapshots:
            self._validate_safe_artifact_ref(str(source.get("artifact_ref") or ""))
            if source.get("prospect_id") not in {None, record.prospect_id}:
                raise ValueError("source prospect does not match report evidence")
            if source.get("vertical_id") not in {None, record.vertical_id}:
                raise ValueError("source vertical does not match report evidence")
            source_market = str(source.get("market") or "").strip()
            if source_market and source_market.casefold() != record.market.casefold():
                raise ValueError("source market does not match report evidence")
        return {
            "valid": True,
            "evidence_id": record.id,
            "mode": record.mode,
            "state": record.state,
            "source_count": len(record.source_snapshots),
            "resolved_reference_count": len(resolved_refs),
            "payload_sha256": canonical_sha256(record.to_dict()),
            "privacy": (
                "owner_aggregate"
                if record.mode == "owner_verified"
                else "public_and_supplied_only"
            ),
        }

    def client_payload(
        self,
        evidence: DemandConversionEvidence | str,
        *,
        requested_mode: str,
        for_export: bool = True,
    ) -> dict[str, Any]:
        record = self._resolve(evidence)
        validation = self.validate(
            record,
            requested_mode=requested_mode,
            for_export=for_export,
        )
        payload = record.to_dict()
        payload["validation"] = validation
        if requested_mode == "prospect":
            # The contract already forbids owner sources. Keep the filter as a
            # defense-in-depth rule for legacy/hand-constructed payloads.
            payload["source_snapshots"] = [
                source
                for source in payload["source_snapshots"]
                if source.get("source_class") != "owner_first_party"
            ]
            baseline = payload.get("observed_inputs", {}).get("funnel_baseline")
            if isinstance(baseline, dict) and baseline.get("sources"):
                raise ValueError(
                    "prospect client payload cannot expose an owner funnel baseline"
                )
        return payload

    def _resolve(
        self,
        evidence: DemandConversionEvidence | str,
    ) -> DemandConversionEvidence:
        if isinstance(evidence, DemandConversionEvidence):
            persisted = self.repository.get_demand_conversion_evidence(evidence.id)
            if persisted is None:
                raise ValueError("demand conversion evidence is not persisted")
            if canonical_sha256(persisted.to_dict()) != canonical_sha256(
                evidence.to_dict()
            ):
                raise ValueError("demand conversion evidence no longer matches")
            return persisted
        persisted = self.repository.get_demand_conversion_evidence(str(evidence))
        if persisted is None:
            raise ValueError(f"demand conversion evidence not found: {evidence}")
        return persisted

    def _resolve_ref(
        self,
        evidence: DemandConversionEvidence,
        ref: dict[str, Any],
        *,
        require_artifact: bool,
    ) -> dict[str, Any]:
        if not isinstance(ref, dict):
            raise ValueError("demand conversion evidence references must be objects")
        kind = str(ref.get("kind") or "")
        record_id = str(ref.get("id") or "")
        if kind == "demand_evidence_set":
            record = self.repository.get_demand_evidence_set(record_id)
            if record is None or record.prospect_id != evidence.prospect_id:
                raise ValueError("referenced demand evidence is missing or mismatched")
            if ref.get("source_sha256") != record.source_sha256:
                raise ValueError("referenced demand evidence hash does not match")
        elif kind == "business_economics_profile":
            record = self.repository.get_business_economics_profile(record_id)
            if record is None or record.prospect_id != evidence.prospect_id:
                raise ValueError("referenced economics profile is missing or mismatched")
            if ref.get("sha256") != canonical_sha256(record.to_dict()):
                raise ValueError("referenced economics profile hash does not match")
        elif kind == "owned_measurement":
            if evidence.mode != "owner_verified":
                raise ValueError("prospect mode cannot reference owned measurements")
            record = self.repository.get_owned_measurement_snapshot(record_id)
            if record is None or record.prospect_id != evidence.prospect_id:
                raise ValueError("referenced owner measurement is missing or mismatched")
            if ref.get("source_sha256") != record.source_sha256:
                raise ValueError("referenced owner measurement hash does not match")
        elif kind == "demand_trend":
            record = self.repository.get_demand_trend_snapshot(record_id)
            if record is None or record.prospect_id != evidence.prospect_id:
                raise ValueError("referenced demand trend is missing or mismatched")
            if ref.get("source_sha256") != record.source_sha256:
                raise ValueError("referenced demand trend hash does not match")
        elif kind == "conversion_event_map":
            record = self.repository.get_conversion_event_map(record_id)
            if record is None or record.prospect_id != evidence.prospect_id:
                raise ValueError("referenced event map is missing or mismatched")
            if ref.get("sha256") != canonical_sha256(record.to_dict()):
                raise ValueError("referenced event map hash does not match")
        elif kind:
            artifact_ref = str(
                ref.get("artifact_ref")
                or ref.get("artifact_path")
                or ref.get("path")
                or ""
            )
            if not artifact_ref:
                raise ValueError(f"unsupported unresolved evidence reference: {kind}")
            self._validate_safe_artifact_ref(artifact_ref)
            if require_artifact:
                self._resolve_artifact(
                    artifact_ref,
                    expected_sha256=str(
                        ref.get("source_sha256") or ref.get("sha256") or ""
                    ),
                )
        else:
            artifact_ref = str(
                ref.get("artifact_ref")
                or ref.get("artifact_path")
                or ref.get("path")
                or ""
            )
            if not artifact_ref:
                raise ValueError("evidence reference requires kind or artifact path")
            self._validate_safe_artifact_ref(artifact_ref)
            if require_artifact:
                self._resolve_artifact(
                    artifact_ref,
                    expected_sha256=str(
                        ref.get("source_sha256") or ref.get("sha256") or ""
                    ),
                )
        return ref

    def _validate_source_coverage(
        self,
        evidence: DemandConversionEvidence,
        resolved_refs: list[dict[str, Any]],
        *,
        require_artifact: bool,
    ) -> None:
        for source in evidence.source_snapshots:
            if source.get("source_class") == "scenario_model":
                continue
            artifact_ref = str(source.get("artifact_ref") or "")
            source_hash = str(source.get("source_sha256") or "")
            snapshot_id = str(source.get("snapshot_id") or "")
            matched = any(
                (
                    snapshot_id
                    and str(ref.get("id") or ref.get("snapshot_id") or "")
                    == snapshot_id
                )
                or (
                    artifact_ref
                    and str(
                        ref.get("artifact_ref")
                        or ref.get("artifact_path")
                        or ref.get("path")
                        or ""
                    )
                    == artifact_ref
                )
                or (
                    source_hash
                    and str(ref.get("source_sha256") or ref.get("sha256") or "")
                    == source_hash
                )
                for ref in resolved_refs
            )
            if not matched:
                raise ValueError(
                    "source snapshot is not covered by a persisted evidence reference"
                )
            if require_artifact:
                self._resolve_artifact(
                    artifact_ref,
                    expected_sha256=source_hash,
                )

    def _resolve_artifact(
        self,
        artifact_ref: str,
        *,
        expected_sha256: str = "",
    ) -> Path:
        normalized = artifact_ref.replace("\\", "/").split("#", 1)[0]
        artifact_root = getattr(self.repository, "artifact_root", None)
        if artifact_root is None:
            artifact_root = getattr(self.repository, "root", None)
        if artifact_root is None:
            files = getattr(self.repository, "_files", None)
            artifact_root = getattr(files, "root", None)
        if artifact_root is None:
            raise ValueError("repository does not expose an artifact root")
        root = Path(artifact_root).resolve()
        path = (root / Path(*PurePosixPath(normalized).parts)).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError("artifact reference escapes the repository root") from exc
        if not path.is_file():
            raise ValueError(f"referenced artifact is missing: {artifact_ref}")
        if expected_sha256:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(
                    f"referenced artifact is unreadable: {artifact_ref}"
                ) from exc
            candidates = {canonical_sha256(payload)}
            if isinstance(payload, dict):
                stored_hash = payload.get("source_sha256")
                if isinstance(stored_hash, str):
                    candidates.add(stored_hash)
                report_payload = payload.get("report_payload")
                if isinstance(report_payload, dict):
                    candidates.add(canonical_sha256(report_payload))
            if expected_sha256 not in candidates:
                raise ValueError(
                    f"referenced artifact hash does not match: {artifact_ref}"
                )
        return path

    @staticmethod
    def _validate_safe_artifact_ref(value: str) -> None:
        if not value.strip():
            raise ValueError("artifact reference is required")
        normalized = value.replace("\\", "/")
        path = PurePosixPath(normalized.split("#", 1)[0])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("artifact reference must be safe and repository-relative")

    @classmethod
    def _validate_private_keys(cls, payload: Any, *, path: str = "") -> None:
        if isinstance(payload, dict):
            for key, value in payload.items():
                normalized = str(key).casefold().replace("-", "_")
                field_path = f"{path}.{key}" if path else str(key)
                if _PRIVATE_KEY_RE.search(normalized):
                    raise ValueError(
                        f"demand conversion payload contains private field: {field_path}"
                    )
                cls._validate_private_keys(value, path=field_path)
        elif isinstance(payload, list):
            for index, value in enumerate(payload):
                cls._validate_private_keys(value, path=f"{path}[{index}]")

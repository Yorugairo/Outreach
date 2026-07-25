from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid4())


@dataclass(slots=True)
class SEOTarget:
    input_url: str
    normalized_url: str
    normalized_domain: str
    id: str = field(default_factory=new_id)
    target_type: str = "domain"
    display_name: str | None = None
    canonical_domain: str | None = None
    default_location_code: int | None = None
    default_language_code: str = "en"
    country_code: str = "US"
    status: str = "active"
    source_system: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    business_entity_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InsightRun:
    seo_target_id: str
    requested_url: str
    requested_domain: str
    id: str = field(default_factory=new_id)
    trigger_source: str = "manual"
    mode: str = "standard"
    location_code: int | None = None
    language_code: str = "en"
    device: str = "desktop"
    status: str = "queued"
    current_stage: str = "queued"
    requested_by: str | None = None
    attempt_count: int = 1
    attempt_id: str = field(default_factory=new_id)
    input_payload: dict[str, Any] = field(default_factory=dict)
    config_snapshot: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    error_text: str | None = None
    business_entity_id: str | None = None
    lease_owner: str | None = None
    heartbeat_at: str | None = None
    lease_expires_at: str | None = None
    queued_at: str = field(default_factory=utc_now_iso)
    started_at: str | None = None
    completed_at: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RunStageEvent:
    insight_run_id: str
    stage_name: str
    status: str
    id: str = field(default_factory=new_id)
    attempt_id: str | None = None
    artifact_path: str | None = None
    stage_order: int | None = None
    message: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    duration_ms: int | None = None
    retry_count: int = 0
    input_payload: dict[str, Any] = field(default_factory=dict)
    output_summary: dict[str, Any] = field(default_factory=dict)
    error_text: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StageCheckpoint:
    insight_run_id: str
    attempt_id: str
    stage_name: str
    payload_type: str
    payload: dict[str, Any]
    id: str = field(default_factory=new_id)
    schema_version: int = 1
    content_sha256: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    ALLOWED_TYPES = {
        "crawl_discovery",
        "page_analysis",
        "search_intelligence",
        "scorecard",
    }

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError(f"unsupported checkpoint schema version: {self.schema_version}")
        if self.payload_type not in self.ALLOWED_TYPES:
            raise ValueError(f"unsupported checkpoint payload type: {self.payload_type}")
        if not isinstance(self.payload, dict):
            raise ValueError("checkpoint payload must be an object")
        digest = self.compute_hash(self.payload)
        if self.content_sha256 is None:
            self.content_sha256 = digest
        elif self.content_sha256 != digest:
            raise ValueError("checkpoint content hash does not match payload")

    @classmethod
    def create(
        cls,
        *,
        insight_run_id: str,
        attempt_id: str,
        stage_name: str,
        payload_type: str,
        payload: dict[str, Any],
    ) -> "StageCheckpoint":
        return cls(
            insight_run_id=insight_run_id,
            attempt_id=attempt_id,
            stage_name=stage_name,
            payload_type=payload_type,
            payload=payload,
        )

    @staticmethod
    def compute_hash(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DiscoveredAsset:
    insight_run_id: str
    asset_type: str
    url: str
    id: str = field(default_factory=new_id)
    attempt_id: str | None = None
    parent_url: str | None = None
    http_status: int | None = None
    content_type: str | None = None
    discovered_from: str | None = None
    depth: int | None = None
    is_primary: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    discovered_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PageRecord:
    insight_run_id: str
    seo_target_id: str
    url: str
    id: str = field(default_factory=new_id)
    attempt_id: str | None = None
    discovered_asset_id: str | None = None
    canonical_url: str | None = None
    normalized_path: str | None = None
    page_class: str | None = None
    fetch_status: str | None = None
    http_status: int | None = None
    content_type: str | None = None
    title: str | None = None
    meta_description: str | None = None
    h1: str | None = None
    robots_meta: str | None = None
    canonical_status: str | None = None
    indexable: bool | None = None
    word_count: int | None = None
    schema_types: list[str] = field(default_factory=list)
    internal_links: list[str] = field(default_factory=list)
    image_assets: list[str] = field(default_factory=list)
    fetch_metadata: dict[str, Any] = field(default_factory=dict)
    duplicate_cluster_key: str | None = None
    fetched_at: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CommercialFinding:
    id: str
    finding_type: str
    category: str
    title: str
    observation: str
    impact: str
    recommended_action: str
    severity: str
    effort: str
    confidence: str
    recommended_services: list[str]
    service_fit_reason: str
    evidence_refs: list[dict[str, Any]]

    def __post_init__(self) -> None:
        required_text = (
            "id",
            "category",
            "title",
            "observation",
            "impact",
            "recommended_action",
            "service_fit_reason",
        )
        if any(not isinstance(getattr(self, name), str) or not getattr(self, name).strip() for name in required_text):
            raise ValueError("commercial finding text fields must be non-empty strings")
        if self.severity not in {"critical", "high", "medium", "low", "info"}:
            raise ValueError(f"invalid severity: {self.severity}")
        if self.effort not in {"small", "medium", "large", "discovery_required"}:
            raise ValueError(f"invalid effort: {self.effort}")
        if self.confidence not in {"high", "medium", "low"}:
            raise ValueError(f"invalid confidence: {self.confidence}")
        if self.finding_type not in {"prospect_issue", "evidence_limit"}:
            raise ValueError(f"invalid finding type: {self.finding_type}")
        allowed_services = {
            "web_development_rebuild",
            "profile_management_reputation",
            "pseo_search_architecture",
        }
        if not isinstance(self.recommended_services, list):
            raise ValueError("recommended_services must be a list")
        invalid_services = set(self.recommended_services) - allowed_services
        if invalid_services:
            raise ValueError(f"invalid recommended services: {sorted(invalid_services)}")
        if self.finding_type == "evidence_limit" and self.recommended_services:
            raise ValueError("evidence limits cannot recommend services")
        if not self.evidence_refs:
            raise ValueError("commercial findings require at least one evidence reference")
        for ref in self.evidence_refs:
            if (
                not isinstance(ref, dict)
                or any(not isinstance(ref.get(key), str) or not ref[key].strip() for key in ("artifact_path", "field", "reason"))
                or "observed" not in ref
            ):
                raise ValueError("evidence references require artifact_path, field, reason, and observed")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InsightReport:
    insight_run_id: str
    seo_target_id: str
    report_payload: dict[str, Any]
    id: str = field(default_factory=new_id)
    report_version: str = "v1"
    attempt_id: str | None = None
    report_status: str = "draft"
    headline: str | None = None
    executive_summary: str | None = None
    key_actions: list[dict[str, Any]] = field(default_factory=list)
    export_markdown: str | None = None
    export_json: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

from __future__ import annotations

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
class DiscoveredAsset:
    insight_run_id: str
    asset_type: str
    url: str
    id: str = field(default_factory=new_id)
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
class InsightReport:
    insight_run_id: str
    seo_target_id: str
    report_payload: dict[str, Any]
    id: str = field(default_factory=new_id)
    report_version: str = "v1"
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

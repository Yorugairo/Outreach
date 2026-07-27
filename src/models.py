from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


PROVIDER_CALL_CONTRACT_VERSION = "provider-calls.v1"
DEMAND_EVIDENCE_VERSION = "demand-evidence.v1"
OPPORTUNITY_FORMULA_VERSION = "opportunity-formula.v1"
OPPORTUNITY_REPORT_VERSION = "opportunity-v1"
FORECAST_DISCLAIMER = "Forecast, not guarantee"
TECHNICAL_SEO_HEALTH_VERSION = "seo-health.v2"
SEARCH_VISIBILITY_VERSION = "search-visibility.v2"
LOCAL_VISIBILITY_VERSION = "local-visibility.v1"
AI_READINESS_V3_VERSION = "ai-readiness.v3"
OBSERVED_AI_VISIBILITY_VERSION = "ai-visibility.v1"
CONVERSION_READINESS_VERSION = "conversion-readiness.v1"
EVIDENCE_CONFIDENCE_VERSION = "evidence-confidence.v1"
REPORT_SNAPSHOT_VERSION = "report-snapshot.v1"
CLIENT_REPORT_BUNDLE_VERSION = "client-report-bundle.v1"
REPORT_COMPARISON_VERSION = "comparison-v1"
AGENTIC_ANALYSIS_VERSION = "agentic-analysis.v1"
AGENTIC_ASSESSMENT_SCHEMA_VERSION = "agentic-assessment.v1"
VERTICAL_AGENTIC_PACK_VERSION = "vertical-agentic-pack.v1"
AGENTIC_WORK_ITEM_VERSION = "agentic-work-item.v1"
AGENTIC_TOOL_STEP_VERSION = "agentic-tool-step.v1"
BUSINESS_FACT_LEDGER_VERSION = "business-fact-ledger.v1"
DECISION_COVERAGE_VERSION = "decision-coverage.v1"
JOURNEY_EVIDENCE_VERSION = "journey-evidence.v1"
AI_REPRESENTATION_ACCURACY_VERSION = "ai-representation-accuracy.v1"
OWNER_DIAGNOSTIC_VERSION = "owner-diagnostic.v1"
REMEDIATION_BLUEPRINT_VERSION = "remediation-blueprint.v1"
RECOMMENDATION_OUTCOME_LINK_VERSION = "recommendation-outcome-link.v1"
AGENTIC_EVIDENCE_REVIEW_VERSION = "agentic-evidence-review.v1"
DECISION_INTELLIGENCE_REPORT_VERSION = "decision-intelligence-v1"
COMBINED_REPORT_V6_VERSION = "v6"
OWNED_MEASUREMENT_VERSION = "owned-measurement.v1"
DEMAND_CONVERSION_VERSION = "demand-conversion.v1"
DEMAND_TREND_VERSION = "demand-trend.v1"
CONVERSION_EVENT_MAP_VERSION = "conversion-event-map.v1"
DEMAND_CONVERSION_REPORT_VERSION = "demand-conversion-v1"
DEMAND_CONVERSION_FORMULA_VERSION = "demand-conversion-formula.v1"

PRODUCT_SURFACE_VERSIONS = {
    "technical_seo_health": TECHNICAL_SEO_HEALTH_VERSION,
    "search_visibility": SEARCH_VISIBILITY_VERSION,
    "local_visibility": LOCAL_VISIBILITY_VERSION,
    "ai_readiness": AI_READINESS_V3_VERSION,
    "observed_ai_visibility": OBSERVED_AI_VISIBILITY_VERSION,
    "conversion_readiness": CONVERSION_READINESS_VERSION,
    "evidence_confidence": EVIDENCE_CONFIDENCE_VERSION,
}
TECHNICAL_SEO_FAMILY_WEIGHTS = {
    "crawl_indexability": 0.30,
    "on_page_template": 0.20,
    "architecture_internal_links": 0.20,
    "structured_data_entity": 0.15,
    "mobile_performance": 0.15,
}
TECHNICAL_SEO_SEVERITY_WEIGHTS = {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25,
    "info": 0.0,
}
TECHNICAL_SEO_CHECK_REGISTRY = {
    "response_eligibility": {
        "version": 1,
        "family": "crawl_indexability",
        "severity": "critical",
        "page_classes": ["*"],
        "score_affecting": True,
    },
    "redirect_integrity": {
        "version": 1,
        "family": "crawl_indexability",
        "severity": "medium",
        "page_classes": ["*"],
        "score_affecting": True,
    },
    "robots_indexability": {
        "version": 1,
        "family": "crawl_indexability",
        "severity": "critical",
        "page_classes": ["*"],
        "score_affecting": True,
    },
    "canonical_integrity": {
        "version": 1,
        "family": "crawl_indexability",
        "severity": "high",
        "page_classes": ["*"],
        "score_affecting": True,
    },
    "metadata_completeness": {
        "version": 1,
        "family": "on_page_template",
        "severity": "high",
        "page_classes": ["homepage", "service", "location", "service_location", "blog_resource"],
        "score_affecting": True,
    },
    "heading_integrity": {
        "version": 1,
        "family": "on_page_template",
        "severity": "medium",
        "page_classes": ["homepage", "service", "location", "service_location", "blog_resource"],
        "score_affecting": True,
    },
    "meaningful_text": {
        "version": 1,
        "family": "on_page_template",
        "severity": "medium",
        "page_classes": ["homepage", "service", "location", "service_location", "blog_resource"],
        "score_affecting": True,
    },
    "duplicate_template_risk": {
        "version": 1,
        "family": "on_page_template",
        "severity": "medium",
        "page_classes": ["homepage", "service", "location", "service_location", "blog_resource"],
        "score_affecting": True,
    },
    "internal_link_health": {
        "version": 1,
        "family": "architecture_internal_links",
        "severity": "high",
        "page_classes": ["*"],
        "score_affecting": True,
    },
    "navigation_discovery": {
        "version": 1,
        "family": "architecture_internal_links",
        "severity": "medium",
        "page_classes": ["homepage", "service", "location", "service_location", "contact_about"],
        "score_affecting": True,
    },
    "sitemap_membership": {
        "version": 1,
        "family": "architecture_internal_links",
        "severity": "medium",
        "page_classes": ["homepage", "service", "location", "service_location", "blog_resource"],
        "score_affecting": True,
    },
    "crawl_depth_orphan_risk": {
        "version": 1,
        "family": "architecture_internal_links",
        "severity": "medium",
        "page_classes": ["service", "location", "service_location", "blog_resource", "project_case_study"],
        "score_affecting": True,
    },
    "structured_data_alignment": {
        "version": 1,
        "family": "structured_data_entity",
        "severity": "medium",
        "page_classes": ["homepage", "service", "location", "service_location", "contact_about"],
        "score_affecting": True,
    },
    "entity_fact_consistency": {
        "version": 1,
        "family": "structured_data_entity",
        "severity": "high",
        "page_classes": ["homepage", "location", "contact_about"],
        "score_affecting": True,
    },
    "mobile_viewport": {
        "version": 1,
        "family": "mobile_performance",
        "severity": "medium",
        "page_classes": ["*"],
        "score_affecting": True,
    },
    "field_page_experience": {
        "version": 1,
        "family": "mobile_performance",
        "severity": "medium",
        "page_classes": ["*"],
        "score_affecting": True,
    },
}
AI_READINESS_V3_DIMENSION_WEIGHTS = {"aeo": 0.40, "geo": 0.35, "aio": 0.25}
SCORE_CHECK_STATUSES = {"measured", "failed", "unknown", "inapplicable"}
AGENTIC_JOB_STATES = {
    "queued",
    "packing",
    "running",
    "validating",
    "needs_review",
    "complete",
    "partial",
    "failed",
    "superseded",
}
AGENTIC_REVIEW_STATES = {"unreviewed", "needs_review", "approved", "rejected"}
AGENTIC_FINDING_TYPES = {"observed", "inference", "recommendation"}
AGENTIC_WORK_ITEM_STATES = {
    "queued",
    "leased",
    "running",
    "validating",
    "needs_review",
    "complete",
    "partial",
    "failed",
    "superseded",
}
AGENTIC_WORK_KINDS = {
    "business_fact_ledger",
    "decision_coverage",
    "target_journey",
    "competitor_journey",
    "ai_representation_accuracy",
    "owner_diagnostic",
    "remediation_blueprint",
}
AGENTIC_EVIDENCE_MODES = {"prospect", "owner_verified"}
DECISION_COVERAGE_STATUSES = {
    "answered",
    "partial",
    "ambiguous",
    "contradicted",
    "missing",
    "unknown",
}
AI_REPRESENTATION_STATUSES = {
    "correct",
    "incomplete",
    "outdated",
    "contradicted",
    "unsupported",
    "unverifiable",
}
JOURNEY_RESULT_STATUSES = {"passed", "failed", "partial", "unknown", "blocked"}
AGENTIC_POLICY_DECISIONS = {"allowed", "blocked", "needs_approval"}
AGENTIC_ALLOWED_ACTIONS = {
    "navigate_candidate",
    "activate_candidate",
    "scroll",
    "go_back",
    "wait",
    "capture",
}
AGENTIC_PROHIBITED_ACTIONS = {
    "authenticate",
    "download",
    "enter_personal_data",
    "fill",
    "message",
    "purchase",
    "submit",
    "upload",
}
DEMAND_AGGREGATION_RULES = {
    "provider_grouped",
    "max_close_variant",
    "sum_distinct_intents",
}
EVIDENCE_PROVENANCE_TYPES = {
    "operator_observed",
    "business_supplied",
    "assumed",
    "aggregate_calibration",
}
DEMAND_CONVERSION_MODES = {"prospect", "owner_verified"}
DEMAND_CONVERSION_PROVENANCE_LABELS = {
    "observed",
    "supplied",
    "assumed",
    "modeled",
}
DEMAND_CONVERSION_SOURCE_CLASSES = {
    "owner_first_party": 1,
    "operator_supplied": 2,
    "approved_market": 3,
    "public_observed": 4,
    "third_party_estimate": 5,
    "scenario_model": 6,
}
CONVERSION_FUNNEL_STAGES = {
    "visit",
    "lead",
    "booking",
    "attended",
    "customer",
    "revenue",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid4())


def canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _is_sha256(value: str | None) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(char in "0123456789abcdef" for char in value.casefold())


def _forbidden_payload_keys(payload: Any, *, prefix: str = "") -> list[str]:
    forbidden_fragments = {
        "api_key",
        "apikey",
        "authorization",
        "cookie",
        "credential",
        "oauth",
        "password",
        "refresh_token",
        "secret",
    }
    matches: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            normalized = str(key).casefold().replace("-", "_")
            path = f"{prefix}.{key}" if prefix else str(key)
            if any(fragment in normalized for fragment in forbidden_fragments):
                matches.append(path)
            matches.extend(_forbidden_payload_keys(value, prefix=path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            path = f"{prefix}[{index}]"
            matches.extend(_forbidden_payload_keys(value, prefix=path))
    return matches


def _validate_agentic_evidence_ref(reference: dict[str, Any]) -> None:
    """Require a persisted artifact and exact, independently resolvable grounding."""

    if not isinstance(reference, dict):
        raise ValueError("agentic evidence references must be structured records")
    artifact_ref = str(reference.get("artifact_ref") or "").strip()
    reference_kind = str(reference.get("reference_kind") or "").strip()
    if not artifact_ref or reference_kind not in {
        "source_span",
        "persisted_field",
        "dom",
        "screenshot",
        "provider_artifact",
    }:
        raise ValueError(
            "agentic evidence references require an artifact and supported reference kind"
        )
    if reference_kind == "source_span":
        exact_span = str(reference.get("exact_span") or "").strip()
        if not exact_span:
            raise ValueError("source-span evidence requires an exact span")
    elif reference_kind == "persisted_field":
        field_path = str(reference.get("field_path") or "").strip()
        if not field_path:
            raise ValueError("persisted-field evidence requires a field path")
    elif reference_kind == "dom":
        if not str(reference.get("dom_ref") or "").strip():
            raise ValueError("DOM evidence requires a persisted DOM reference")
    elif reference_kind == "screenshot":
        if not str(reference.get("screenshot_ref") or "").strip():
            raise ValueError("screenshot evidence requires a persisted screenshot reference")
    elif reference_kind == "provider_artifact":
        if not str(reference.get("response_span") or "").strip():
            raise ValueError("provider evidence requires an exact response span")


def _reject_executable_blueprint_payload(payload: Any, *, prefix: str = "") -> None:
    forbidden_keys = {
        "code",
        "css",
        "executable",
        "html",
        "javascript",
        "raw_html",
        "script",
    }
    if isinstance(payload, dict):
        for key, value in payload.items():
            normalized = str(key).casefold().replace("-", "_")
            path = f"{prefix}.{key}" if prefix else str(key)
            if normalized in forbidden_keys:
                raise ValueError(f"remediation blueprints cannot contain executable field: {path}")
            _reject_executable_blueprint_payload(value, prefix=path)
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            _reject_executable_blueprint_payload(value, prefix=f"{prefix}[{index}]")
    elif isinstance(payload, str):
        normalized = payload.casefold()
        if "<script" in normalized or "javascript:" in normalized:
            raise ValueError("remediation blueprints cannot contain executable markup")


def _validated_content_hash(
    current: str | None,
    payload: dict[str, Any],
    *,
    label: str,
) -> str:
    digest = canonical_sha256(payload)
    if current is not None and current != digest:
        raise ValueError(f"{label} hash does not match its immutable payload")
    return digest


def _contains_unique_person_claim(payload: Any) -> bool:
    phrases = ("unique people", "unique searchers")
    if isinstance(payload, dict):
        return any(
            any(phrase in str(key).casefold().replace("_", " ") for phrase in phrases)
            or _contains_unique_person_claim(value)
            for key, value in payload.items()
        )
    if isinstance(payload, list):
        return any(_contains_unique_person_claim(value) for value in payload)
    if isinstance(payload, str):
        normalized = payload.casefold()
        for phrase in phrases:
            if phrase not in normalized:
                continue
            disclaimers = (
                f"not {phrase}",
                f"never {phrase}",
                f"not a count of {phrase}",
                f"does not represent {phrase}",
            )
            if any(disclaimer in normalized for disclaimer in disclaimers):
                continue
            return True
        return False
    return False


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
        "ai_readiness",
        "technical_seo_health",
        "conversion_readiness",
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
    ai_evidence: dict[str, Any] = field(default_factory=dict)
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
    evidence_family: str = "technical_seo"

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
        if self.evidence_family not in {
            "technical_seo",
            "local_entity",
            "answer_readiness",
            "service_coverage",
            "location_coverage",
        }:
            raise ValueError(f"invalid evidence family: {self.evidence_family}")
        allowed_services = {
            "web_development_rebuild",
            "profile_management_reputation",
            "pseo_search_architecture",
            "one_trade_network_visibility",
            "one_trade_network_crm_saas",
            "national_bjj_registry_visibility",
            "national_bjj_registry_crm_saas",
            "website_seo_vertical_visibility",
            "vertical_plugin_embed",
            "custom_website_crm_saas",
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
class VerticalPack:
    """Versioned, deterministic rules for a prospect vertical."""

    vertical_id: str
    version: str
    display_name: str
    allowed_business_categories: list[str] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)
    service_taxonomy: dict[str, list[str]] = field(default_factory=dict)
    location_taxonomy: list[str] = field(default_factory=list)
    qualification_rules: dict[str, Any] = field(default_factory=dict)
    offer_mappings: dict[str, Any] = field(default_factory=dict)
    outreach_constraints: dict[str, Any] = field(default_factory=dict)

    @property
    def pack_id(self) -> str:
        return f"{self.vertical_id}.{self.version}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ProspectRecord:
    """A normalized prospect candidate and its deterministic intake outcome."""

    business_name: str = ""
    website_url: str = ""
    category: str = ""
    location: str = ""
    contact_route: str = ""
    source_provenance: str = ""
    vertical_pack_version: str = ""
    id: str = field(default_factory=new_id)
    vertical_id: str = ""
    normalized_domain: str = ""
    qualification_status: str = "pending"
    rejection_reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    @property
    def source(self) -> str:
        """Compatibility alias used by CSV exports and operator tooling."""
        return self.source_provenance

    @property
    def pack_id(self) -> str:
        return self.vertical_pack_version

    @property
    def is_runnable(self) -> bool:
        return self.qualification_status == "qualified"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class KeywordTarget:
    """One immutable, operator-reviewed market query definition."""

    keyword: str
    category: str
    search_intent: str
    optimization_focus: str
    target_page_usage: str
    id: str = field(default_factory=new_id)
    pilot_selected: bool = False
    review_status: str = "approved"
    review_reasons: list[str] = field(default_factory=list)
    source_row: int | None = None
    local_intent: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            self.keyword,
            self.category,
            self.search_intent,
            self.optimization_focus,
            self.target_page_usage,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("keyword targets require complete non-empty source fields")
        if self.review_status not in {"approved", "needs_review", "rejected"}:
            raise ValueError(f"invalid keyword review status: {self.review_status}")
        if self.review_status == "needs_review" and not self.review_reasons:
            raise ValueError("needs_review keyword targets require review reasons")

    @property
    def normalized_keyword(self) -> str:
        return " ".join(self.keyword.casefold().split())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class KeywordSet:
    """Versioned keyword research bound to a market, vertical, or prospect."""

    vertical_id: str
    market: str
    location_code: int
    source_sha256: str
    keyword_targets: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    market_slug: str = ""
    version: str = "v1"
    language_code: str = "en"
    state: str = "draft"
    scope_type: str = "vertical"
    scope_id: str | None = None
    normalized_domain: str | None = None
    source_provenance: str = "csv_import"
    approved_by: str | None = None
    approved_at: str | None = None
    superseded_by_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not self.vertical_id.strip() or not self.market.strip() or not self.source_sha256.strip():
            raise ValueError("keyword sets require vertical, market, and source hash")
        if self.location_code <= 0:
            raise ValueError("keyword set location_code must be positive")
        if self.state not in {"draft", "approved", "superseded"}:
            raise ValueError(f"invalid keyword set state: {self.state}")
        if self.scope_type not in {"vertical", "prospect", "domain"}:
            raise ValueError(f"invalid keyword set scope: {self.scope_type}")
        if not self.keyword_targets:
            raise ValueError("keyword sets require at least one keyword target")
        if self.state == "approved" and (not self.approved_by or not self.approved_at):
            raise ValueError("approved keyword sets require operator provenance")
        normalized: set[str] = set()
        for payload in self.keyword_targets:
            target = KeywordTarget(**payload)
            if target.normalized_keyword in normalized:
                raise ValueError(f"duplicate keyword target: {target.keyword}")
            normalized.add(target.normalized_keyword)
        if not self.market_slug:
            self.market_slug = "-".join(
                part for part in "".join(
                    char if char.isalnum() else " " for char in self.market.casefold()
                ).split()
            )

    @property
    def keyword_set_key(self) -> str:
        return f"{self.vertical_id}.{self.market_slug}.{self.version}"

    def targets(self) -> list[KeywordTarget]:
        return [KeywordTarget(**payload) for payload in self.keyword_targets]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class KeywordSetBinding:
    """Immutable attachment of one approved keyword version to a domain/prospect."""

    keyword_set_id: str
    vertical_id: str
    normalized_domain: str
    operator: str
    id: str = field(default_factory=new_id)
    prospect_id: str | None = None
    state: str = "active"
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.keyword_set_id,
                self.vertical_id,
                self.normalized_domain,
                self.operator,
            )
        ):
            raise ValueError("keyword-set bindings require keyword set, vertical, domain, and operator")
        if self.state not in {"active", "superseded"}:
            raise ValueError(f"invalid keyword-set binding state: {self.state}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ProviderCallRecord:
    """One attributable paid-provider operation or reused predecessor result."""

    provider: str
    operation: str
    query_target: str
    context: dict[str, Any]
    status: str
    id: str = field(default_factory=new_id)
    contract_version: str = PROVIDER_CALL_CONTRACT_VERSION
    attempt: int = 1
    failure_class: str | None = None
    retryable: bool = False
    actual_cost: float = 0.0
    cost_usd: float | None = None
    raw_artifact_ref: str | None = None
    started_at: str = field(default_factory=utc_now_iso)
    completed_at: str | None = None
    predecessor_call_id: str | None = None

    ALLOWED_STATUSES = {
        "planned",
        "success",
        "failed",
        "reused",
        "stopped",
        "inapplicable",
    }
    FAILURE_CLASSES = {
        "transient",
        "task_level",
        "authentication",
        "balance_payment",
        "quota",
        "invalid_request",
        "unknown",
    }

    def __post_init__(self) -> None:
        if self.contract_version != PROVIDER_CALL_CONTRACT_VERSION:
            raise ValueError(f"unsupported provider call contract: {self.contract_version}")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (self.provider, self.operation, self.query_target)
        ):
            raise ValueError("provider calls require provider, operation, and query target")
        if self.status not in self.ALLOWED_STATUSES:
            raise ValueError(f"invalid provider call status: {self.status}")
        if self.attempt < 1:
            raise ValueError("provider call attempt must be positive")
        if self.actual_cost < 0:
            raise ValueError("provider call cost cannot be negative")
        if self.cost_usd is None:
            self.cost_usd = self.actual_cost
        elif self.cost_usd < 0 or abs(self.cost_usd - self.actual_cost) > 0.000001:
            raise ValueError("provider call cost aliases must match")
        if self.failure_class is not None and self.failure_class not in self.FAILURE_CLASSES:
            raise ValueError(f"invalid provider failure class: {self.failure_class}")
        if self.status in {"failed", "stopped"} and self.failure_class is None:
            raise ValueError("failed or stopped provider calls require a failure class")
        if self.status in {"success", "reused", "inapplicable"} and self.failure_class is not None:
            raise ValueError("successful, reused, or inapplicable calls cannot have a failure class")
        if self.retryable and self.failure_class in {
            "authentication",
            "balance_payment",
            "invalid_request",
        }:
            raise ValueError("authentication, payment, and invalid requests are not automatically retryable")
        if self.status == "reused" and not self.predecessor_call_id:
            raise ValueError("reused provider calls require a predecessor call")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MarketEvidenceCompleteness:
    """Required-evidence accounting, independent of provider call count."""

    expected: dict[str, int] = field(default_factory=dict)
    successful: dict[str, int] = field(default_factory=dict)
    unresolved: dict[str, int] = field(default_factory=dict)
    inapplicable: dict[str, int] = field(default_factory=dict)
    reused: dict[str, int] = field(default_factory=dict)
    contract_version: str = PROVIDER_CALL_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.contract_version != PROVIDER_CALL_CONTRACT_VERSION:
            raise ValueError(f"unsupported completeness contract: {self.contract_version}")
        operation_names = (
            set(self.expected)
            | set(self.successful)
            | set(self.unresolved)
            | set(self.inapplicable)
            | set(self.reused)
        )
        for operation in operation_names:
            counts = [
                mapping.get(operation, 0)
                for mapping in (
                    self.expected,
                    self.successful,
                    self.unresolved,
                    self.inapplicable,
                    self.reused,
                )
            ]
            if any(not isinstance(value, int) or value < 0 for value in counts):
                raise ValueError("market completeness counts must be non-negative integers")
            expected, successful, unresolved, inapplicable, reused = counts
            if successful + unresolved + inapplicable != expected:
                raise ValueError(
                    f"market completeness does not reconcile for {operation}"
                )
            if reused > successful:
                raise ValueError("reused evidence cannot exceed successful evidence")

    @property
    def total_expected(self) -> int:
        return sum(self.expected.values())

    @property
    def total_unresolved(self) -> int:
        return sum(self.unresolved.values())

    @property
    def is_complete(self) -> bool:
        return self.total_unresolved == 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MarketEvidenceRun:
    """Child lifecycle for optional SERP, competitor, and screenshot evidence."""

    insight_run_id: str
    insight_attempt_id: str
    keyword_set_id: str
    keyword_set_version: str
    target_domain: str
    id: str = field(default_factory=new_id)
    target_entity_name: str | None = None
    state: str = "collecting"
    phase: str = "pilot"
    vertical_id: str = ""
    market: str = ""
    location_code: int | None = None
    language_code: str = "en"
    device: str = "desktop"
    provider_call_cap: int = 26
    provider_calls: list[dict[str, Any]] = field(default_factory=list)
    actual_provider_cost: float = 0.0
    keyword_metrics: list[dict[str, Any]] = field(default_factory=list)
    organic_evidence: list[dict[str, Any]] = field(default_factory=list)
    maps_evidence: list[dict[str, Any]] = field(default_factory=list)
    competitor_candidates: list[dict[str, Any]] = field(default_factory=list)
    approved_competitors: list[dict[str, Any]] = field(default_factory=list)
    competitor_evidence: list[dict[str, Any]] = field(default_factory=list)
    gap_matrix: list[dict[str, Any]] = field(default_factory=list)
    recommended_gaps: list[dict[str, Any]] = field(default_factory=list)
    screenshots: list[dict[str, Any]] = field(default_factory=list)
    evidence_limits: list[dict[str, Any]] = field(default_factory=list)
    artifact_refs: list[dict[str, Any]] = field(default_factory=list)
    provider_contract_version: str | None = None
    provider_completeness: dict[str, Any] = field(default_factory=dict)
    predecessor_market_run_id: str | None = None
    recovery_operation: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    completed_at: str | None = None

    ALLOWED_STATES = {
        "collecting",
        "needs_competitor_approval",
        "enriching",
        "complete",
        "partial",
        "failed",
        "superseded",
    }

    def __post_init__(self) -> None:
        if self.state not in self.ALLOWED_STATES:
            raise ValueError(f"invalid market evidence state: {self.state}")
        if self.phase not in {"pilot", "deep"}:
            raise ValueError(f"invalid market evidence phase: {self.phase}")
        if not all(
            value.strip()
            for value in (
                self.insight_run_id,
                self.insight_attempt_id,
                self.keyword_set_id,
                self.keyword_set_version,
                self.target_domain,
            )
        ):
            raise ValueError("market evidence runs require immutable run, keyword-set, and target identity")
        if self.provider_call_cap < 0 or len(self.provider_calls) > self.provider_call_cap:
            raise ValueError("market evidence provider call cap exceeded")
        if self.actual_provider_cost < 0:
            raise ValueError("actual provider cost cannot be negative")
        if len(self.approved_competitors) > 3:
            raise ValueError("at most three competitors may be approved")
        if len(self.screenshots) > 6:
            raise ValueError("at most six screenshot artifacts may be attached")
        if self.provider_contract_version not in {None, PROVIDER_CALL_CONTRACT_VERSION}:
            raise ValueError(
                f"unsupported provider call contract: {self.provider_contract_version}"
            )
        if self.provider_completeness:
            completeness = MarketEvidenceCompleteness(**self.provider_completeness)
            if self.state == "complete" and not completeness.is_complete:
                raise ValueError("market evidence with unresolved required work cannot be complete")
        if self.recovery_operation not in {None, "resume_unresolved"}:
            raise ValueError(f"invalid market recovery operation: {self.recovery_operation}")
        if self.recovery_operation and not self.predecessor_market_run_id:
            raise ValueError("market recovery requires a predecessor market run")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DemandEvidenceRow:
    """One source row. Monthly searches represent occasions, never people."""

    keyword: str
    market: str
    source: str
    snapshot_period: str
    match_semantics: str
    id: str = field(default_factory=new_id)
    normalized_keyword: str = ""
    keyword_set_target_id: str | None = None
    location_code: int | None = None
    monthly_searches: float | None = None
    source_row: int | None = None
    evidence_ref: dict[str, Any] = field(default_factory=dict)
    brand_demand: bool = False
    supported: bool = True

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.keyword,
                self.market,
                self.source,
                self.snapshot_period,
                self.match_semantics,
            )
        ):
            raise ValueError("demand rows require keyword, market, source, period, and match semantics")
        if self.monthly_searches is not None and self.monthly_searches < 0:
            raise ValueError("monthly search occasions cannot be negative")
        if self.location_code is not None and self.location_code <= 0:
            raise ValueError("demand location code must be positive")
        if self.source_row is not None and self.source_row < 1:
            raise ValueError("demand source row must be positive")
        normalized = " ".join(self.keyword.casefold().split())
        if not self.normalized_keyword:
            self.normalized_keyword = normalized
        elif self.normalized_keyword != normalized:
            raise ValueError("normalized demand keyword does not match keyword")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DemandGroup:
    """Reviewed de-duplication unit used in search-occasion arithmetic."""

    intent_family: str
    included_keyword_ids: list[str]
    representative_term: str
    aggregation_rule: str
    approved_monthly_search_occasions: float | None
    id: str = field(default_factory=new_id)
    excluded_duplicate_ids: list[str] = field(default_factory=list)
    reviewer: str | None = None
    rationale: str = ""
    is_brand: bool = False
    status: str = "draft"

    def __post_init__(self) -> None:
        if not self.intent_family.strip() or not self.representative_term.strip():
            raise ValueError("demand groups require an intent family and representative term")
        if not self.included_keyword_ids:
            raise ValueError("demand groups require at least one included keyword")
        if len(set(self.included_keyword_ids)) != len(self.included_keyword_ids):
            raise ValueError("demand groups cannot include duplicate row ids")
        if set(self.included_keyword_ids) & set(self.excluded_duplicate_ids):
            raise ValueError("included and excluded demand rows must be disjoint")
        if self.aggregation_rule not in DEMAND_AGGREGATION_RULES:
            raise ValueError(f"invalid demand aggregation rule: {self.aggregation_rule}")
        if (
            self.approved_monthly_search_occasions is not None
            and self.approved_monthly_search_occasions < 0
        ):
            raise ValueError("approved monthly search occasions cannot be negative")
        if self.status not in {"draft", "approved", "rejected"}:
            raise ValueError(f"invalid demand group status: {self.status}")
        if self.status == "approved" and (
            not self.reviewer
            or not self.rationale.strip()
            or self.approved_monthly_search_occasions is None
        ):
            raise ValueError("approved demand groups require reviewer, rationale, and volume")
        if self.aggregation_rule == "sum_distinct_intents" and self.status != "approved":
            raise ValueError("sum_distinct_intents requires explicit operator approval")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DemandEvidenceSet:
    """Immutable version of reviewed market-demand evidence."""

    prospect_id: str
    keyword_set_id: str
    vertical_id: str
    market: str
    source_sha256: str
    rows: list[dict[str, Any]]
    groups: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    version: int = 1
    contract_version: str = DEMAND_EVIDENCE_VERSION
    location_code: int | None = None
    source: str = "operator_csv"
    snapshot_period: str = ""
    state: str = "draft"
    approved_by: str | None = None
    approved_at: str | None = None
    predecessor_id: str | None = None
    superseded_by_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != DEMAND_EVIDENCE_VERSION:
            raise ValueError(f"unsupported demand evidence contract: {self.contract_version}")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.prospect_id,
                self.keyword_set_id,
                self.vertical_id,
                self.market,
                self.source_sha256,
                self.source,
            )
        ):
            raise ValueError("demand evidence requires prospect, keyword set, vertical, market, source, and hash")
        if self.version < 1:
            raise ValueError("demand evidence version must be positive")
        if self.location_code is not None and self.location_code <= 0:
            raise ValueError("demand evidence location code must be positive")
        if self.state not in {"draft", "review", "approved", "superseded"}:
            raise ValueError(f"invalid demand evidence state: {self.state}")
        row_models = [DemandEvidenceRow(**payload) for payload in self.rows]
        row_ids = {row.id for row in row_models}
        if len(row_ids) != len(row_models):
            raise ValueError("demand evidence rows require unique ids")
        group_models = [DemandGroup(**payload) for payload in self.groups]
        claimed: set[str] = set()
        for group in group_models:
            unknown = set(group.included_keyword_ids) - row_ids
            if unknown:
                raise ValueError(f"demand group references unknown rows: {sorted(unknown)}")
            overlap = claimed & set(group.included_keyword_ids)
            if overlap:
                raise ValueError(f"demand rows cannot belong to multiple groups: {sorted(overlap)}")
            claimed.update(group.included_keyword_ids)
        if self.state == "approved":
            if not self.approved_by or not self.approved_at:
                raise ValueError("approved demand evidence requires operator provenance")
            if not group_models or any(group.status != "approved" for group in group_models):
                raise ValueError("approved demand evidence requires reviewed groups")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BusinessEconomicsProfile:
    """Versioned, provenance-bearing commercial inputs for one prospect."""

    prospect_id: str
    vertical_id: str
    revenue_model: str
    monthly_price: float
    currency: str
    capacity_headroom: float
    field_provenance: dict[str, str]
    id: str = field(default_factory=new_id)
    version: int = 1
    state: str = "draft"
    gross_margin_mode: str = "unknown"
    gross_margin_percent: float | None = None
    retention_months: float | None = None
    active_customer_count: float | None = None
    desired_fill_months: float | None = None
    current_monthly_leads: float | None = None
    current_monthly_signups: float | None = None
    visit_to_signup_rate: float | None = None
    signup_to_attended_rate: float | None = None
    attended_to_customer_rate: float | None = None
    funnel_labels: list[str] = field(default_factory=list)
    approved_by: str | None = None
    approved_at: str | None = None
    predecessor_id: str | None = None
    superseded_by_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.prospect_id,
                self.vertical_id,
                self.revenue_model,
                self.currency,
            )
        ):
            raise ValueError("economics profiles require prospect, vertical, revenue model, and currency")
        if self.version < 1:
            raise ValueError("economics profile version must be positive")
        if self.monthly_price < 0 or self.capacity_headroom < 0:
            raise ValueError("price and capacity headroom cannot be negative")
        if self.state not in {"draft", "approved", "superseded"}:
            raise ValueError(f"invalid economics profile state: {self.state}")
        if self.gross_margin_mode not in {"unknown", "revenue", "gross_profit"}:
            raise ValueError(f"invalid gross margin mode: {self.gross_margin_mode}")
        numeric_nonnegative = (
            self.retention_months,
            self.active_customer_count,
            self.desired_fill_months,
            self.current_monthly_leads,
            self.current_monthly_signups,
        )
        if any(value is not None and value < 0 for value in numeric_nonnegative):
            raise ValueError("economics counts and periods cannot be negative")
        if self.gross_margin_percent is not None and not 0 <= self.gross_margin_percent <= 1:
            raise ValueError("gross margin percent must be between zero and one")
        for rate in (
            self.visit_to_signup_rate,
            self.signup_to_attended_rate,
            self.attended_to_customer_rate,
        ):
            if rate is not None and not 0 <= rate <= 1:
                raise ValueError("funnel rates must be between zero and one")
        invalid_provenance = set(self.field_provenance.values()) - EVIDENCE_PROVENANCE_TYPES
        if invalid_provenance:
            raise ValueError(f"invalid economics provenance: {sorted(invalid_provenance)}")
        if self.state == "approved" and (
            not self.approved_by
            or not self.approved_at
            or not self.field_provenance
        ):
            raise ValueError("approved economics profiles require provenance and operator approval")

    @property
    def capacity_mrr(self) -> float:
        return self.monthly_price * self.capacity_headroom

    @property
    def capacity_annual_run_rate(self) -> float:
        return self.capacity_mrr * 12

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OpportunityScenario:
    """Immutable capacity-aware forecast attributed to approved inputs."""

    insight_run_id: str
    prospect_id: str
    demand_evidence_set_id: str | None
    demand_evidence_version: int | None
    economics_profile_id: str
    economics_profile_version: int
    assumptions: dict[str, dict[str, Any]]
    outputs: dict[str, dict[str, Any]]
    id: str = field(default_factory=new_id)
    formula_version: str = OPPORTUNITY_FORMULA_VERSION
    status: str = "limited"
    completeness_percent: float = 0.0
    state: str = "draft"
    sensitivity: dict[str, Any] = field(default_factory=dict)
    service_levers: list[dict[str, Any]] = field(default_factory=list)
    evidence_refs: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    approved_by: str | None = None
    approved_at: str | None = None
    predecessor_id: str | None = None
    calibrated_from_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.formula_version != OPPORTUNITY_FORMULA_VERSION:
            raise ValueError(f"unsupported opportunity formula: {self.formula_version}")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.insight_run_id,
                self.prospect_id,
                self.economics_profile_id,
            )
        ):
            raise ValueError("opportunity scenarios require run, prospect, and economics identity")
        if self.economics_profile_version < 1:
            raise ValueError("economics profile version must be positive")
        if (self.demand_evidence_set_id is None) != (self.demand_evidence_version is None):
            raise ValueError("demand evidence id and version must be supplied together")
        if self.demand_evidence_version is not None and self.demand_evidence_version < 1:
            raise ValueError("demand evidence version must be positive")
        if self.status not in {"complete", "partial", "limited"}:
            raise ValueError(f"invalid opportunity status: {self.status}")
        if self.state not in {"draft", "approved", "superseded"}:
            raise ValueError(f"invalid opportunity lifecycle state: {self.state}")
        if not 0 <= self.completeness_percent <= 100:
            raise ValueError("opportunity completeness must be between zero and 100")
        if set(self.assumptions) != {"low", "base", "high"}:
            raise ValueError("opportunity assumptions require low, base, and high")
        if self.outputs and set(self.outputs) != {"low", "base", "high"}:
            raise ValueError("opportunity outputs require low, base, and high")
        if self.state == "approved" and (
            self.status != "complete"
            or not self.approved_by
            or not self.approved_at
        ):
            raise ValueError("approved opportunity scenarios must be complete and operator-approved")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["forecast_label"] = FORECAST_DISCLAIMER
        return payload


@dataclass(slots=True)
class AcquisitionCalibrationRecord:
    """Aggregate funnel outcomes only; raw lead identity is prohibited."""

    prospect_id: str
    vertical_id: str
    market: str
    source: str
    period_start: str
    period_end: str
    artifact_ref: dict[str, Any]
    id: str = field(default_factory=new_id)
    version: int = 1
    impressions: float | None = None
    clicks: float | None = None
    total_users: float | None = None
    signups_or_leads: float | None = None
    attended_or_appointments: float | None = None
    new_customers: float | None = None
    spend: float | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.prospect_id,
                self.vertical_id,
                self.market,
                self.source,
                self.period_start,
                self.period_end,
            )
        ):
            raise ValueError("calibration requires prospect, vertical, market, source, and period")
        if self.version < 1:
            raise ValueError("calibration version must be positive")
        if self.period_end < self.period_start:
            raise ValueError("calibration period end cannot precede its start")
        values = (
            self.impressions,
            self.clicks,
            self.total_users,
            self.signups_or_leads,
            self.attended_or_appointments,
            self.new_customers,
            self.spend,
        )
        if any(value is not None and value < 0 for value in values):
            raise ValueError("calibration aggregates cannot be negative")
        if not self.artifact_ref:
            raise ValueError("calibration requires an aggregate source artifact reference")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ScoreCheckResult:
    """One versioned deterministic check over an explicit applicable scope."""

    check_id: str
    check_version: int
    family: str
    severity: str
    status: str
    score_affecting: bool
    applicable_page_ids: list[str] = field(default_factory=list)
    affected_page_ids: list[str] = field(default_factory=list)
    weighted_affected_ratio: float | None = None
    evidence_confidence: float | None = None
    score: float | None = None
    evidence_refs: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    remediation: str = ""

    def __post_init__(self) -> None:
        if not self.check_id.strip() or not self.family.strip():
            raise ValueError("score checks require check and family identity")
        if self.check_version < 1:
            raise ValueError("score check version must be positive")
        if self.severity not in TECHNICAL_SEO_SEVERITY_WEIGHTS:
            raise ValueError(f"invalid score check severity: {self.severity}")
        if self.status not in SCORE_CHECK_STATUSES:
            raise ValueError(f"invalid score check status: {self.status}")
        for name, value in (
            ("weighted affected ratio", self.weighted_affected_ratio),
            ("evidence confidence", self.evidence_confidence),
        ):
            if value is not None and not 0 <= value <= 1:
                raise ValueError(f"{name} must be between zero and one")
        if self.score is not None and not 0 <= self.score <= 100:
            raise ValueError("score check score must be between zero and 100")
        if self.status in {"unknown", "inapplicable"} and self.score is not None:
            raise ValueError("unknown and inapplicable checks cannot have a score")
        if self.status == "inapplicable" and self.applicable_page_ids:
            raise ValueError("inapplicable checks cannot list applicable pages")
        if set(self.affected_page_ids) - set(self.applicable_page_ids):
            raise ValueError("affected pages must be part of the applicable scope")
        if self.status in {"measured", "failed"} and not self.evidence_refs:
            raise ValueError("measured score checks require evidence references")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ProductSurfaceResult:
    """Common envelope; surface-specific services retain independent arithmetic."""

    surface: str
    version: str
    status: str
    score: float | None
    completeness_percent: float
    evidence_confidence: float
    families: dict[str, Any] = field(default_factory=dict)
    checks: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        expected = PRODUCT_SURFACE_VERSIONS.get(self.surface)
        if expected is None:
            raise ValueError(f"unknown product surface: {self.surface}")
        if self.version != expected:
            raise ValueError(f"unsupported {self.surface} version: {self.version}")
        if self.status not in {"complete", "partial", "limited", "unknown"}:
            raise ValueError(f"invalid product surface status: {self.status}")
        if self.score is not None and not 0 <= self.score <= 100:
            raise ValueError("product surface score must be between zero and 100")
        if not 0 <= self.completeness_percent <= 100:
            raise ValueError("product surface completeness must be between zero and 100")
        if not 0 <= self.evidence_confidence <= 100:
            raise ValueError("evidence confidence must be between zero and 100")
        if self.status == "unknown" and self.score is not None:
            raise ValueError("unknown product surfaces cannot have a score")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportSnapshot:
    """Write-once report payload identity; aliases are persisted separately."""

    run_id: str
    attempt_id: str
    report_contract: str
    schema_version: int
    source_snapshot_ids: dict[str, str]
    source_hashes: dict[str, str]
    renderer_version: str
    payload_sha256: str
    payload_artifact_ref: str
    id: str = field(default_factory=new_id)
    contract_version: str = REPORT_SNAPSHOT_VERSION
    manifest_sha256: str | None = None
    completeness_percent: float = 0.0
    status: str = "limited"
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != REPORT_SNAPSHOT_VERSION:
            raise ValueError(f"unsupported report snapshot contract: {self.contract_version}")
        required = (
            self.run_id,
            self.attempt_id,
            self.report_contract,
            self.renderer_version,
            self.payload_artifact_ref,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("report snapshots require run, attempt, report, renderer, and artifact identity")
        if self.schema_version < 1:
            raise ValueError("report snapshot schema version must be positive")
        if not _is_sha256(self.payload_sha256):
            raise ValueError("report snapshot payload hash must be SHA-256")
        if self.manifest_sha256 is not None and not _is_sha256(self.manifest_sha256):
            raise ValueError("report snapshot manifest hash must be SHA-256")
        invalid_source_hashes = [
            key for key, value in self.source_hashes.items() if not _is_sha256(value)
        ]
        if invalid_source_hashes:
            raise ValueError(f"invalid report source hashes: {sorted(invalid_source_hashes)}")
        if self.status not in {"complete", "partial", "limited"}:
            raise ValueError(f"invalid report snapshot status: {self.status}")
        if not 0 <= self.completeness_percent <= 100:
            raise ValueError("report snapshot completeness must be between zero and 100")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportAlias:
    """Mutable pointer to a write-once report snapshot."""

    run_id: str
    report_contract: str
    alias: str
    snapshot_id: str
    id: str = field(default_factory=new_id)
    updated_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (self.run_id, self.report_contract, self.alias, self.snapshot_id)
        ):
            raise ValueError("report aliases require run, contract, alias, and snapshot identity")
        if "/" in self.alias or "\\" in self.alias or ".." in self.alias:
            raise ValueError("report alias must be a safe name")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ClientReportBundle:
    """Immutable portable report bundle and its content-addressed manifest."""

    report_snapshot_id: str
    run_id: str
    manifest_sha256: str
    manifest_artifact_ref: str
    files: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    contract_version: str = CLIENT_REPORT_BUNDLE_VERSION
    theme_version: str = "client.default.v1"
    renderer_version: str = "client-renderer.v1"
    status: str = "complete"
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != CLIENT_REPORT_BUNDLE_VERSION:
            raise ValueError(f"unsupported client bundle contract: {self.contract_version}")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (
                self.report_snapshot_id,
                self.run_id,
                self.manifest_artifact_ref,
                self.theme_version,
                self.renderer_version,
            )
        ):
            raise ValueError("client bundles require snapshot, run, manifest, theme, and renderer identity")
        if not _is_sha256(self.manifest_sha256):
            raise ValueError("client bundle manifest hash must be SHA-256")
        if self.status not in {"complete", "partial", "failed"}:
            raise ValueError(f"invalid client bundle status: {self.status}")
        for item in self.files:
            if not isinstance(item, dict) or not _is_sha256(item.get("sha256")):
                raise ValueError("client bundle files require SHA-256 manifest entries")
            if not str(item.get("path", "")).strip():
                raise ValueError("client bundle files require paths")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SiteEvidencePack:
    """Bounded, secret-free immutable evidence made available to an LLM."""

    run_id: str
    attempt_id: str
    source_snapshot_ids: dict[str, str]
    source_hashes: dict[str, str]
    target_facts: dict[str, Any]
    page_facts: list[dict[str, Any]]
    deterministic_surfaces: dict[str, Any]
    evidence_refs: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    contract_version: str = AGENTIC_ANALYSIS_VERSION
    vertical_pack_version: str | None = None
    keyword_set_id: str | None = None
    market_run_id: str | None = None
    opportunity_scenario_id: str | None = None
    market_evidence: dict[str, Any] = field(default_factory=dict)
    permitted_service_mappings: dict[str, Any] = field(default_factory=dict)
    completeness_percent: float = 0.0
    limitations: list[str] = field(default_factory=list)
    content_sha256: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != AGENTIC_ANALYSIS_VERSION:
            raise ValueError(f"unsupported site evidence contract: {self.contract_version}")
        if not self.run_id.strip() or not self.attempt_id.strip():
            raise ValueError("site evidence packs require run and attempt identity")
        invalid_source_hashes = [
            key for key, value in self.source_hashes.items() if not _is_sha256(value)
        ]
        if invalid_source_hashes:
            raise ValueError(f"invalid evidence-pack source hashes: {sorted(invalid_source_hashes)}")
        if not 0 <= self.completeness_percent <= 100:
            raise ValueError("site evidence completeness must be between zero and 100")
        protected_payload = {
            "target_facts": self.target_facts,
            "page_facts": self.page_facts,
            "deterministic_surfaces": self.deterministic_surfaces,
            "market_evidence": self.market_evidence,
            "permitted_service_mappings": self.permitted_service_mappings,
        }
        forbidden = _forbidden_payload_keys(protected_payload)
        if forbidden:
            raise ValueError(f"site evidence pack contains forbidden secret fields: {sorted(forbidden)}")
        digest = self.compute_hash()
        if self.content_sha256 is None:
            self.content_sha256 = digest
        elif self.content_sha256 != digest:
            raise ValueError("site evidence pack hash does not match payload")

    def compute_hash(self) -> str:
        return canonical_sha256(
            {
                "contract_version": self.contract_version,
                "run_id": self.run_id,
                "attempt_id": self.attempt_id,
                "source_snapshot_ids": self.source_snapshot_ids,
                "source_hashes": self.source_hashes,
                "vertical_pack_version": self.vertical_pack_version,
                "keyword_set_id": self.keyword_set_id,
                "market_run_id": self.market_run_id,
                "opportunity_scenario_id": self.opportunity_scenario_id,
                "target_facts": self.target_facts,
                "page_facts": self.page_facts,
                "deterministic_surfaces": self.deterministic_surfaces,
                "market_evidence": self.market_evidence,
                "permitted_service_mappings": self.permitted_service_mappings,
                "completeness_percent": self.completeness_percent,
                "limitations": self.limitations,
                "evidence_refs": self.evidence_refs,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgenticAnalysisJob:
    evidence_pack_id: str
    evidence_pack_sha256: str
    idempotency_key: str
    requested_runtime: str
    requested_provider: str
    requested_model: str
    prompt_version: str
    rubric_version: str
    schema_version: str
    id: str = field(default_factory=new_id)
    contract_version: str = AGENTIC_ANALYSIS_VERSION
    profile: str = "outreach-analysis"
    analysis_mode: str = "standard"
    state: str = "queued"
    max_calls: int = 4
    max_cost_usd: float = 0.10
    max_output_tokens: int = 8_000
    timeout_seconds: int = 120
    retry_limit: int = 2
    call_attempts: int = 0
    actual_cost_usd: float = 0.0
    lease_owner: str | None = None
    lease_expires_at: str | None = None
    predecessor_job_id: str | None = None
    error_class: str | None = None
    error_text: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    completed_at: str | None = None

    def __post_init__(self) -> None:
        if self.contract_version != AGENTIC_ANALYSIS_VERSION:
            raise ValueError(f"unsupported agentic job contract: {self.contract_version}")
        required = (
            self.evidence_pack_id,
            self.idempotency_key,
            self.requested_runtime,
            self.requested_provider,
            self.requested_model,
            self.prompt_version,
            self.rubric_version,
            self.schema_version,
            self.profile,
            self.analysis_mode,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("agentic jobs require complete runtime and contract identity")
        if not _is_sha256(self.evidence_pack_sha256):
            raise ValueError("agentic job evidence hash must be SHA-256")
        if self.state not in AGENTIC_JOB_STATES:
            raise ValueError(f"invalid agentic job state: {self.state}")
        if self.max_calls < 1 or self.max_calls > 4:
            raise ValueError("agentic jobs permit one to four model calls")
        if not 0 < self.max_cost_usd <= 0.10:
            raise ValueError("agentic job cost ceiling must be positive and no more than $0.10")
        if self.max_output_tokens < 1 or self.timeout_seconds < 1:
            raise ValueError("agentic token and time ceilings must be positive")
        if not 0 <= self.retry_limit <= 2:
            raise ValueError("agentic transient retry limit cannot exceed two")
        if self.call_attempts < 0 or self.actual_cost_usd < 0:
            raise ValueError("agentic job usage cannot be negative")
        if self.call_attempts > self.max_calls * (self.retry_limit + 1):
            raise ValueError("agentic call attempts exceed the configured retry budget")
        if self.actual_cost_usd > self.max_cost_usd + 0.000001:
            raise ValueError("agentic job cost exceeds its configured ceiling")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgentCallRecord:
    job_id: str
    pass_name: str
    requested_runtime: str
    requested_provider: str
    requested_model: str
    prompt_version: str
    rubric_version: str
    schema_version: str
    status: str
    id: str = field(default_factory=new_id)
    contract_version: str = AGENTIC_ANALYSIS_VERSION
    served_provider: str | None = None
    served_model: str | None = None
    routing_mode: str = "fixed"
    attempt: int = 1
    failure_class: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    actual_cost_usd: float | None = None
    estimated_cost_usd: float | None = None
    latency_ms: int | None = None
    raw_response_ref: str | None = None
    started_at: str = field(default_factory=utc_now_iso)
    completed_at: str | None = None
    predecessor_call_id: str | None = None

    ALLOWED_STATUSES = {"planned", "running", "success", "failed", "stopped"}
    FAILURE_CLASSES = {
        "transient",
        "authentication",
        "payment",
        "quota",
        "invalid_request",
        "validation",
        "budget",
        "policy",
        "unknown",
    }

    def __post_init__(self) -> None:
        if self.contract_version != AGENTIC_ANALYSIS_VERSION:
            raise ValueError(f"unsupported agent call contract: {self.contract_version}")
        required = (
            self.job_id,
            self.pass_name,
            self.requested_runtime,
            self.requested_provider,
            self.requested_model,
            self.prompt_version,
            self.rubric_version,
            self.schema_version,
            self.routing_mode,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("agent calls require complete job, pass, runtime, and contract identity")
        if self.status not in self.ALLOWED_STATUSES:
            raise ValueError(f"invalid agent call status: {self.status}")
        if self.failure_class is not None and self.failure_class not in self.FAILURE_CLASSES:
            raise ValueError(f"invalid agent failure class: {self.failure_class}")
        if self.attempt < 1:
            raise ValueError("agent call attempt must be positive")
        usage = (self.input_tokens, self.output_tokens, self.reasoning_tokens)
        if any(value < 0 for value in usage):
            raise ValueError("agent token usage cannot be negative")
        costs = (self.actual_cost_usd, self.estimated_cost_usd)
        if any(value is not None and value < 0 for value in costs):
            raise ValueError("agent costs cannot be negative")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("agent latency cannot be negative")
        if self.status == "success" and (
            not self.served_provider
            or not self.served_model
            or not self.raw_response_ref
        ):
            raise ValueError("successful agent calls require served route and raw response provenance")
        if self.status == "failed" and not self.failure_class:
            raise ValueError("failed agent calls require a failure class")

    @property
    def routing_diverged(self) -> bool:
        return bool(
            self.served_provider
            and self.served_model
            and (
                self.served_provider != self.requested_provider
                or self.served_model != self.requested_model
            )
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["routing_diverged"] = self.routing_diverged
        return payload


@dataclass(slots=True)
class AgenticFinding:
    claim_type: str
    title: str
    claim: str
    confidence: str
    severity: str
    commercial_relevance: str
    service_fit: list[str]
    evidence_refs: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    customer_safe: bool = False
    review_reason: str | None = None

    def __post_init__(self) -> None:
        if self.claim_type not in AGENTIC_FINDING_TYPES:
            raise ValueError(f"invalid agentic finding type: {self.claim_type}")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (self.title, self.claim, self.commercial_relevance)
        ):
            raise ValueError("agentic findings require title, claim, and commercial relevance")
        if self.confidence not in {"high", "medium", "low"}:
            raise ValueError(f"invalid agentic confidence: {self.confidence}")
        if self.severity not in {"critical", "high", "medium", "low", "info"}:
            raise ValueError(f"invalid agentic severity: {self.severity}")
        if self.customer_safe and not self.evidence_refs:
            raise ValueError("customer-safe agentic findings require evidence references")
        if not self.customer_safe and not self.review_reason:
            raise ValueError("non-customer-safe findings require a review reason")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgenticAssessmentSnapshot:
    job_id: str
    evidence_pack_id: str
    evidence_pack_sha256: str
    runtime: str
    requested_model: str
    served_model: str
    served_provider: str
    prompt_version: str
    rubric_version: str
    schema_version: str
    findings: list[dict[str, Any]]
    validation_result: dict[str, Any]
    id: str = field(default_factory=new_id)
    contract_version: str = AGENTIC_ANALYSIS_VERSION
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    call_ids: list[str] = field(default_factory=list)
    total_cost_usd: float = 0.0
    total_latency_ms: int = 0
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != AGENTIC_ANALYSIS_VERSION:
            raise ValueError(f"unsupported agentic assessment contract: {self.contract_version}")
        required = (
            self.job_id,
            self.evidence_pack_id,
            self.runtime,
            self.requested_model,
            self.served_model,
            self.served_provider,
            self.prompt_version,
            self.rubric_version,
            self.schema_version,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("agentic assessments require job, evidence, route, and schema identity")
        if self.schema_version != AGENTIC_ASSESSMENT_SCHEMA_VERSION:
            raise ValueError(f"unsupported agentic assessment schema: {self.schema_version}")
        if not _is_sha256(self.evidence_pack_sha256):
            raise ValueError("agentic assessment evidence hash must be SHA-256")
        for payload in self.findings:
            AgenticFinding(**payload)
        if self.total_cost_usd < 0 or self.total_latency_ms < 0:
            raise ValueError("agentic assessment usage cannot be negative")
        if self.validation_result.get("customer_safe") is True and any(
            not AgenticFinding(**payload).customer_safe for payload in self.findings
        ):
            raise ValueError("customer-safe assessments cannot contain unsafe findings")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgenticAssessmentReviewEvent:
    assessment_id: str
    event_type: str
    operator: str
    reason_code: str
    id: str = field(default_factory=new_id)
    notes: str | None = None
    external_reference: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    ALLOWED_EVENTS = {
        "review_requested",
        "gpt_review_requested",
        "approved",
        "rejected",
        "correction_recorded",
    }

    def __post_init__(self) -> None:
        if self.event_type not in self.ALLOWED_EVENTS:
            raise ValueError(f"invalid assessment review event: {self.event_type}")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (self.assessment_id, self.operator, self.reason_code)
        ):
            raise ValueError("assessment review events require assessment, operator, and reason")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def derive_agentic_review_state(
    events: list[AgenticAssessmentReviewEvent | dict[str, Any]],
) -> str:
    state = "unreviewed"
    normalized = [
        event if isinstance(event, AgenticAssessmentReviewEvent) else AgenticAssessmentReviewEvent(**event)
        for event in events
    ]
    for event in sorted(normalized, key=lambda item: (item.created_at, item.id)):
        if event.event_type in {"review_requested", "gpt_review_requested", "correction_recorded"}:
            state = "needs_review"
        elif event.event_type == "approved":
            state = "approved"
        elif event.event_type == "rejected":
            state = "rejected"
    if state not in AGENTIC_REVIEW_STATES:  # pragma: no cover - defensive
        raise ValueError(f"invalid derived agentic review state: {state}")
    return state


@dataclass(slots=True)
class VerticalAgenticPack:
    """Reviewed, versioned buyer questions and bounded journey policy."""

    vertical_id: str
    version: str
    display_name: str
    buyer_questions: list[dict[str, Any]]
    journey_tasks: list[dict[str, Any]]
    service_mappings: dict[str, list[str]]
    action_host_policy_version: str
    source_sha256: str
    id: str = field(default_factory=new_id)
    contract_version: str = VERTICAL_AGENTIC_PACK_VERSION
    state: str = "draft"
    approved_by: str | None = None
    approved_at: str | None = None
    predecessor_id: str | None = None
    superseded_by_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != VERTICAL_AGENTIC_PACK_VERSION:
            raise ValueError(f"unsupported vertical agentic pack: {self.contract_version}")
        required = (
            self.vertical_id,
            self.version,
            self.display_name,
            self.action_host_policy_version,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("vertical agentic packs require complete version and policy identity")
        if self.state not in {"draft", "approved", "superseded"}:
            raise ValueError(f"invalid vertical agentic pack state: {self.state}")
        if not _is_sha256(self.source_sha256):
            raise ValueError("vertical agentic pack source hash must be SHA-256")
        if not self.buyer_questions or not self.journey_tasks:
            raise ValueError("vertical agentic packs require questions and journey tasks")
        question_ids: set[str] = set()
        for question in self.buyer_questions:
            if not isinstance(question, dict):
                raise ValueError("buyer questions must be structured records")
            question_id = str(question.get("question_id") or "").strip()
            prompt = str(question.get("question") or "").strip()
            buyer_stage = str(question.get("buyer_stage") or "").strip()
            if not question_id or not prompt or buyer_stage not in {
                "discovery",
                "consideration",
                "decision",
                "conversion",
            }:
                raise ValueError("buyer questions require ID, question, and supported buyer stage")
            if question_id in question_ids:
                raise ValueError("buyer question IDs must be unique")
            question_ids.add(question_id)
            if not isinstance(question.get("applicability"), dict):
                raise ValueError("buyer questions require explicit applicability")
        task_ids: set[str] = set()
        required_journeys = {
            "offer_discovery",
            "decision_resolution",
            "ready_to_convert_cta",
        }
        observed_journeys: set[str] = set()
        for task in self.journey_tasks:
            if not isinstance(task, dict):
                raise ValueError("journey tasks must be structured records")
            task_id = str(task.get("task_id") or "").strip()
            task_kind = str(task.get("task_kind") or "").strip()
            viewport = str(task.get("viewport") or "").strip()
            objective = str(task.get("objective") or "").strip()
            if (
                not task_id
                or not objective
                or task_kind not in required_journeys
                or viewport not in {"desktop", "mobile"}
                or not isinstance(task.get("success_oracle"), dict)
                or not isinstance(task.get("applicability"), dict)
            ):
                raise ValueError("journey tasks require bounded task, viewport, oracle, and applicability")
            if task_id in task_ids:
                raise ValueError("journey task IDs must be unique")
            task_ids.add(task_id)
            observed_journeys.add(task_kind)
        if not required_journeys.issubset(observed_journeys):
            raise ValueError("vertical packs require all three automatic target journeys")
        if self.state == "approved" and (not self.approved_by or not self.approved_at):
            raise ValueError("approved vertical agentic packs require operator provenance")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgenticWorkItem:
    """Durable work queue contract shared by analysis and browser workers."""

    run_id: str
    attempt_id: str
    evidence_pack_id: str
    vertical_pack_version: str
    work_kind: str
    mode: str
    source_sha256: str
    idempotency_key: str
    requested_runtime: str
    requested_provider: str
    requested_model: str
    prompt_version: str
    rubric_version: str
    schema_version: str
    id: str = field(default_factory=new_id)
    contract_version: str = AGENTIC_WORK_ITEM_VERSION
    state: str = "queued"
    budget_class: str = "automatic"
    execution_mode: str = "automatic"
    task_id: str | None = None
    source_snapshot_ids: list[str] = field(default_factory=list)
    host_policy_version: str | None = None
    max_model_decisions: int = 12
    max_browser_actions: int = 30
    max_output_tokens: int = 8_000
    max_cost_usd: float = 0.25
    timeout_seconds: int = 90
    retry_limit: int = 2
    attempt_count: int = 0
    model_decisions_used: int = 0
    browser_actions_used: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    actual_cost_usd: float = 0.0
    lease_owner: str | None = None
    lease_expires_at: str | None = None
    consent_id: str | None = None
    predecessor_id: str | None = None
    error_class: str | None = None
    error_text: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    completed_at: str | None = None

    def __post_init__(self) -> None:
        if self.contract_version != AGENTIC_WORK_ITEM_VERSION:
            raise ValueError(f"unsupported agentic work item: {self.contract_version}")
        required = (
            self.run_id,
            self.attempt_id,
            self.evidence_pack_id,
            self.vertical_pack_version,
            self.idempotency_key,
            self.requested_runtime,
            self.requested_provider,
            self.requested_model,
            self.prompt_version,
            self.rubric_version,
            self.schema_version,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("agentic work items require complete source, runtime, and schema identity")
        if self.work_kind not in AGENTIC_WORK_KINDS:
            raise ValueError(f"invalid agentic work kind: {self.work_kind}")
        if self.mode not in AGENTIC_EVIDENCE_MODES:
            raise ValueError(f"invalid agentic evidence mode: {self.mode}")
        if self.state not in AGENTIC_WORK_ITEM_STATES:
            raise ValueError(f"invalid agentic work state: {self.state}")
        if self.budget_class not in {"automatic", "premium"}:
            raise ValueError(f"invalid agentic budget class: {self.budget_class}")
        if self.execution_mode not in {"automatic", "shadow", "review", "premium"}:
            raise ValueError(f"invalid agentic execution mode: {self.execution_mode}")
        if self.execution_mode == "premium" and self.budget_class != "premium":
            raise ValueError("premium execution requires the premium budget class")
        if not _is_sha256(self.source_sha256):
            raise ValueError("agentic work source hash must be SHA-256")
        cost_ceiling = 0.25 if self.budget_class == "automatic" else 0.75
        if not 0 < self.max_cost_usd <= cost_ceiling:
            raise ValueError(f"{self.budget_class} work cannot exceed ${cost_ceiling:.2f}")
        if not 1 <= self.max_model_decisions <= 12:
            raise ValueError("agentic work permits at most 12 model decisions")
        if not 0 <= self.max_browser_actions <= 30:
            raise ValueError("agentic work permits at most 30 browser actions")
        if not 1 <= self.timeout_seconds <= 90 or not 0 <= self.retry_limit <= 2:
            raise ValueError("agentic work exceeds time or retry policy")
        if self.max_output_tokens < 1:
            raise ValueError("agentic work output-token budget must be positive")
        usage = (
            self.attempt_count,
            self.model_decisions_used,
            self.browser_actions_used,
            self.input_tokens,
            self.output_tokens,
        )
        if any(value < 0 for value in usage) or self.actual_cost_usd < 0:
            raise ValueError("agentic work usage cannot be negative")
        if (
            self.model_decisions_used > self.max_model_decisions
            or self.browser_actions_used > self.max_browser_actions
            or self.actual_cost_usd > self.max_cost_usd + 0.000001
        ):
            raise ValueError("agentic work usage exceeds a configured budget")
        if self.mode == "owner_verified" and not self.consent_id:
            raise ValueError("owner-mode work requires recorded consent")
        if self.work_kind == "owner_diagnostic" and self.mode != "owner_verified":
            raise ValueError("owner diagnostics cannot run in prospect mode")
        if self.mode == "prospect" and self.consent_id:
            raise ValueError("prospect work cannot bind owner consent or evidence")
        if len(set(self.source_snapshot_ids)) != len(self.source_snapshot_ids):
            raise ValueError("agentic work source snapshot IDs must be unique")
        if self.task_id is not None and not self.task_id.strip():
            raise ValueError("agentic work task identity cannot be empty")
        if self.host_policy_version is not None and not self.host_policy_version.strip():
            raise ValueError("agentic work host policy version cannot be empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgenticToolStep:
    work_item_id: str
    sequence: int
    action_kind: str
    candidate_action_id: str
    policy_decision: str
    outcome: str
    id: str = field(default_factory=new_id)
    contract_version: str = AGENTIC_TOOL_STEP_VERSION
    before_url: str | None = None
    after_url: str | None = None
    dom_ref: str | None = None
    screenshot_ref: str | None = None
    model_call_ref: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    actual_cost_usd: float = 0.0
    policy_reason: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != AGENTIC_TOOL_STEP_VERSION:
            raise ValueError(f"unsupported agentic tool step: {self.contract_version}")
        if not self.work_item_id.strip() or not self.candidate_action_id.strip():
            raise ValueError("agentic tool steps require work-item and candidate-action identity")
        if self.sequence < 1:
            raise ValueError("agentic tool-step sequence must be positive")
        if self.action_kind in AGENTIC_PROHIBITED_ACTIONS:
            raise ValueError(f"prohibited browser action: {self.action_kind}")
        if self.action_kind not in AGENTIC_ALLOWED_ACTIONS:
            raise ValueError(f"browser action is not enumerated: {self.action_kind}")
        if self.policy_decision not in AGENTIC_POLICY_DECISIONS:
            raise ValueError(f"invalid browser policy decision: {self.policy_decision}")
        if self.policy_decision != "allowed" and not self.policy_reason:
            raise ValueError("blocked or approval-required actions require a policy reason")
        if self.policy_decision != "allowed" and self.after_url:
            raise ValueError("blocked actions cannot record a navigated destination")
        if self.input_tokens < 0 or self.output_tokens < 0 or self.actual_cost_usd < 0:
            raise ValueError("agentic tool-step usage cannot be negative")
        if not self.outcome.strip():
            raise ValueError("agentic tool steps require an outcome")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BusinessFactLedgerSnapshot:
    run_id: str
    attempt_id: str
    work_item_id: str
    vertical_pack_version: str
    source_sha256: str
    facts: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    contract_version: str = BUSINESS_FACT_LEDGER_VERSION
    mode: str = "prospect"
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    review_state: str = "needs_review"
    content_sha256: str | None = None
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != BUSINESS_FACT_LEDGER_VERSION:
            raise ValueError(f"unsupported business fact ledger: {self.contract_version}")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (
                self.run_id,
                self.attempt_id,
                self.work_item_id,
                self.vertical_pack_version,
            )
        ):
            raise ValueError("fact ledgers require run, attempt, work, and vertical identity")
        if self.mode not in AGENTIC_EVIDENCE_MODES:
            raise ValueError(f"invalid fact-ledger mode: {self.mode}")
        if self.review_state not in AGENTIC_REVIEW_STATES:
            raise ValueError(f"invalid fact-ledger review state: {self.review_state}")
        if not _is_sha256(self.source_sha256):
            raise ValueError("fact-ledger source hash must be SHA-256")
        fact_ids: set[str] = set()
        for fact in self.facts:
            if not isinstance(fact, dict):
                raise ValueError("business facts must be structured records")
            fact_id = str(fact.get("fact_id") or "").strip()
            name = str(fact.get("name") or "").strip()
            source_status = str(fact.get("source_status") or "").strip()
            sensitivity = str(fact.get("sensitivity_class") or "").strip()
            approval = str(fact.get("approval_state") or "").strip()
            references = fact.get("evidence_refs", [])
            if (
                not fact_id
                or not name
                or source_status not in {"observed", "business_supplied", "conflicted", "unknown"}
                or sensitivity not in {"public", "sensitive", "private"}
                or approval not in AGENTIC_REVIEW_STATES
                or not isinstance(references, list)
            ):
                raise ValueError("business facts require status, sensitivity, and approval semantics")
            if fact_id in fact_ids:
                raise ValueError("business fact IDs must be unique")
            fact_ids.add(fact_id)
            if source_status in {"observed", "business_supplied", "conflicted"} and not references:
                raise ValueError("known or conflicted business facts require exact evidence")
            for reference in references:
                _validate_agentic_evidence_ref(reference)
            if sensitivity != "public" and approval == "approved":
                raise ValueError("sensitive/private facts remain review-gated")
        self.content_sha256 = _validated_content_hash(
            self.content_sha256,
            {
                "contract_version": self.contract_version,
                "run_id": self.run_id,
                "attempt_id": self.attempt_id,
                "work_item_id": self.work_item_id,
                "vertical_pack_version": self.vertical_pack_version,
                "source_sha256": self.source_sha256,
                "mode": self.mode,
                "facts": self.facts,
                "conflicts": self.conflicts,
                "limitations": self.limitations,
            },
            label="business fact ledger",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DecisionCoverageSnapshot:
    run_id: str
    attempt_id: str
    work_item_id: str
    fact_ledger_id: str
    vertical_pack_version: str
    source_sha256: str
    coverage: list[dict[str, Any]]
    completeness_percent: float
    id: str = field(default_factory=new_id)
    contract_version: str = DECISION_COVERAGE_VERSION
    mode: str = "prospect"
    limitations: list[str] = field(default_factory=list)
    review_state: str = "needs_review"
    content_sha256: str | None = None
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != DECISION_COVERAGE_VERSION:
            raise ValueError(f"unsupported decision coverage: {self.contract_version}")
        required = (
            self.run_id,
            self.attempt_id,
            self.work_item_id,
            self.fact_ledger_id,
            self.vertical_pack_version,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("decision coverage requires run, work, ledger, and pack identity")
        if self.mode not in AGENTIC_EVIDENCE_MODES:
            raise ValueError(f"invalid decision-coverage mode: {self.mode}")
        if self.review_state not in AGENTIC_REVIEW_STATES:
            raise ValueError(f"invalid decision-coverage review state: {self.review_state}")
        if not _is_sha256(self.source_sha256):
            raise ValueError("decision-coverage source hash must be SHA-256")
        if not 0 <= self.completeness_percent <= 100:
            raise ValueError("decision completeness must be between zero and 100")
        question_ids: set[str] = set()
        for result in self.coverage:
            if not isinstance(result, dict):
                raise ValueError("decision results must be structured records")
            question_id = str(result.get("question_id") or "").strip()
            status = str(result.get("status") or "").strip()
            references = result.get("evidence_refs", [])
            if not question_id or status not in DECISION_COVERAGE_STATUSES:
                raise ValueError("decision results require question identity and supported status")
            if question_id in question_ids:
                raise ValueError("decision question results must be unique")
            question_ids.add(question_id)
            if not isinstance(references, list):
                raise ValueError("decision evidence references must be a list")
            if status in {"answered", "partial", "ambiguous", "contradicted"} and not references:
                raise ValueError(f"{status} decisions require exact evidence")
            for reference in references:
                _validate_agentic_evidence_ref(reference)
        self.content_sha256 = _validated_content_hash(
            self.content_sha256,
            {
                "contract_version": self.contract_version,
                "run_id": self.run_id,
                "attempt_id": self.attempt_id,
                "work_item_id": self.work_item_id,
                "fact_ledger_id": self.fact_ledger_id,
                "vertical_pack_version": self.vertical_pack_version,
                "source_sha256": self.source_sha256,
                "mode": self.mode,
                "coverage": self.coverage,
                "completeness_percent": self.completeness_percent,
                "limitations": self.limitations,
            },
            label="decision coverage",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class JourneyEvidenceRun:
    run_id: str
    attempt_id: str
    work_item_id: str
    task_id: str
    vertical_pack_version: str
    viewport: str
    allowed_hosts: list[str]
    host_policy_version: str
    source_sha256: str
    result_status: str
    id: str = field(default_factory=new_id)
    contract_version: str = JOURNEY_EVIDENCE_VERSION
    mode: str = "prospect"
    tool_step_ids: list[str] = field(default_factory=list)
    oracle_results: list[dict[str, Any]] = field(default_factory=list)
    blockers: list[dict[str, Any]] = field(default_factory=list)
    screenshot_refs: list[str] = field(default_factory=list)
    evidence_refs: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    model_decisions: int = 0
    browser_actions: int = 0
    elapsed_seconds: float = 0.0
    content_sha256: str | None = None
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != JOURNEY_EVIDENCE_VERSION:
            raise ValueError(f"unsupported journey evidence: {self.contract_version}")
        required = (
            self.run_id,
            self.attempt_id,
            self.work_item_id,
            self.task_id,
            self.vertical_pack_version,
            self.host_policy_version,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("journey evidence requires run, work, task, pack, and policy identity")
        if self.mode not in AGENTIC_EVIDENCE_MODES:
            raise ValueError(f"invalid journey mode: {self.mode}")
        if self.viewport not in {"desktop", "mobile"}:
            raise ValueError("journey viewport must be desktop or mobile")
        if self.result_status not in JOURNEY_RESULT_STATUSES:
            raise ValueError(f"invalid journey result: {self.result_status}")
        if not _is_sha256(self.source_sha256):
            raise ValueError("journey source hash must be SHA-256")
        normalized_hosts = [host.casefold().strip().strip(".") for host in self.allowed_hosts]
        if not normalized_hosts or any(not host or "://" in host or "/" in host for host in normalized_hosts):
            raise ValueError("journeys require normalized allowed hostnames")
        if len(set(normalized_hosts)) != len(normalized_hosts):
            raise ValueError("journey allowed hosts must be unique")
        if (
            not 0 <= self.model_decisions <= 12
            or not 0 <= self.browser_actions <= 30
            or not 0 <= self.elapsed_seconds <= 90
        ):
            raise ValueError("journey evidence exceeds the bounded execution contract")
        if self.result_status in {"passed", "failed", "partial"} and not (
            self.evidence_refs or self.tool_step_ids
        ):
            raise ValueError("conclusive journey results require persisted evidence")
        for reference in self.evidence_refs:
            _validate_agentic_evidence_ref(reference)
        self.allowed_hosts = normalized_hosts
        self.content_sha256 = _validated_content_hash(
            self.content_sha256,
            {
                "contract_version": self.contract_version,
                "run_id": self.run_id,
                "attempt_id": self.attempt_id,
                "work_item_id": self.work_item_id,
                "task_id": self.task_id,
                "vertical_pack_version": self.vertical_pack_version,
                "viewport": self.viewport,
                "allowed_hosts": self.allowed_hosts,
                "host_policy_version": self.host_policy_version,
                "source_sha256": self.source_sha256,
                "mode": self.mode,
                "result_status": self.result_status,
                "tool_step_ids": self.tool_step_ids,
                "oracle_results": self.oracle_results,
                "blockers": self.blockers,
                "screenshot_refs": self.screenshot_refs,
                "evidence_refs": self.evidence_refs,
                "limitations": self.limitations,
                "model_decisions": self.model_decisions,
                "browser_actions": self.browser_actions,
                "elapsed_seconds": self.elapsed_seconds,
            },
            label="journey evidence",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AIRepresentationAccuracySnapshot:
    run_id: str
    attempt_id: str
    work_item_id: str
    fact_ledger_id: str
    source_sha256: str
    claims: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    contract_version: str = AI_REPRESENTATION_ACCURACY_VERSION
    mode: str = "prospect"
    completeness_percent: float = 0.0
    limitations: list[str] = field(default_factory=list)
    review_state: str = "needs_review"
    content_sha256: str | None = None
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != AI_REPRESENTATION_ACCURACY_VERSION:
            raise ValueError(f"unsupported AI representation snapshot: {self.contract_version}")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (self.run_id, self.attempt_id, self.work_item_id, self.fact_ledger_id)
        ):
            raise ValueError("AI representation snapshots require run, work, and ledger identity")
        if self.mode not in AGENTIC_EVIDENCE_MODES:
            raise ValueError(f"invalid AI representation mode: {self.mode}")
        if not _is_sha256(self.source_sha256):
            raise ValueError("AI representation source hash must be SHA-256")
        if not 0 <= self.completeness_percent <= 100:
            raise ValueError("AI representation completeness must be between zero and 100")
        if self.review_state not in AGENTIC_REVIEW_STATES:
            raise ValueError(f"invalid AI representation review state: {self.review_state}")
        claim_ids: set[str] = set()
        for claim in self.claims:
            if not isinstance(claim, dict):
                raise ValueError("AI representation claims must be structured records")
            claim_id = str(claim.get("claim_id") or "").strip()
            classification = str(claim.get("classification") or "").strip()
            response_ref = claim.get("response_evidence_ref")
            fact_refs = claim.get("fact_evidence_refs", [])
            if not claim_id or classification not in AI_REPRESENTATION_STATUSES:
                raise ValueError("AI representation claims require identity and classification")
            if claim_id in claim_ids:
                raise ValueError("AI representation claim IDs must be unique")
            claim_ids.add(claim_id)
            _validate_agentic_evidence_ref(response_ref)
            if not isinstance(fact_refs, list):
                raise ValueError("AI representation fact references must be a list")
            if classification != "unverifiable" and not fact_refs:
                raise ValueError("verifiable AI representation claims require ledger evidence")
            for reference in fact_refs:
                _validate_agentic_evidence_ref(reference)
        self.content_sha256 = _validated_content_hash(
            self.content_sha256,
            {
                "contract_version": self.contract_version,
                "run_id": self.run_id,
                "attempt_id": self.attempt_id,
                "work_item_id": self.work_item_id,
                "fact_ledger_id": self.fact_ledger_id,
                "source_sha256": self.source_sha256,
                "mode": self.mode,
                "claims": self.claims,
                "completeness_percent": self.completeness_percent,
                "limitations": self.limitations,
            },
            label="AI representation accuracy",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OwnerDiagnosticSnapshot:
    run_id: str
    attempt_id: str
    prospect_id: str
    work_item_id: str
    consent_id: str
    approved_source_snapshot_ids: list[str]
    source_sha256: str
    observations: list[dict[str, Any]]
    hypotheses: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    contract_version: str = OWNER_DIAGNOSTIC_VERSION
    mode: str = "owner_verified"
    privacy_scope: str = "private_owner_only"
    limitations: list[str] = field(default_factory=list)
    content_sha256: str | None = None
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != OWNER_DIAGNOSTIC_VERSION:
            raise ValueError(f"unsupported owner diagnostic: {self.contract_version}")
        required = (
            self.run_id,
            self.attempt_id,
            self.prospect_id,
            self.work_item_id,
            self.consent_id,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("owner diagnostics require run, prospect, work, and consent identity")
        if self.mode != "owner_verified" or self.privacy_scope != "private_owner_only":
            raise ValueError("owner diagnostics are private owner-mode evidence only")
        if not self.approved_source_snapshot_ids or len(set(self.approved_source_snapshot_ids)) != len(
            self.approved_source_snapshot_ids
        ):
            raise ValueError("owner diagnostics require unique approved aggregate snapshots")
        if not _is_sha256(self.source_sha256):
            raise ValueError("owner diagnostic source hash must be SHA-256")
        for payload in [*self.observations, *self.hypotheses]:
            if not isinstance(payload, dict):
                raise ValueError("owner diagnostic entries must be structured records")
            references = payload.get("evidence_refs", [])
            if not references:
                raise ValueError("owner diagnostic observations and hypotheses require evidence")
            for reference in references:
                _validate_agentic_evidence_ref(reference)
        if _forbidden_payload_keys(
            {"observations": self.observations, "hypotheses": self.hypotheses}
        ):
            raise ValueError("owner diagnostics cannot contain credentials")
        self.content_sha256 = _validated_content_hash(
            self.content_sha256,
            {
                "contract_version": self.contract_version,
                "run_id": self.run_id,
                "attempt_id": self.attempt_id,
                "prospect_id": self.prospect_id,
                "work_item_id": self.work_item_id,
                "consent_id": self.consent_id,
                "approved_source_snapshot_ids": self.approved_source_snapshot_ids,
                "source_sha256": self.source_sha256,
                "observations": self.observations,
                "hypotheses": self.hypotheses,
                "limitations": self.limitations,
            },
            label="owner diagnostic",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RemediationBlueprintSnapshot:
    run_id: str
    attempt_id: str
    work_item_id: str
    mode: str
    source_snapshot_ids: list[str]
    source_sha256: str
    blueprint: dict[str, Any]
    evidence_refs: list[dict[str, Any]]
    id: str = field(default_factory=new_id)
    contract_version: str = REMEDIATION_BLUEPRINT_VERSION
    renderer_version: str = "offline-prototype.v1"
    review_state: str = "needs_review"
    placeholder_fields: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    approved_by: str | None = None
    approved_at: str | None = None
    content_sha256: str | None = None
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != REMEDIATION_BLUEPRINT_VERSION:
            raise ValueError(f"unsupported remediation blueprint: {self.contract_version}")
        required = (self.run_id, self.attempt_id, self.work_item_id, self.renderer_version)
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("remediation blueprints require run, work, and renderer identity")
        if self.mode not in AGENTIC_EVIDENCE_MODES:
            raise ValueError(f"invalid remediation mode: {self.mode}")
        if self.review_state not in AGENTIC_REVIEW_STATES:
            raise ValueError(f"invalid remediation review state: {self.review_state}")
        if self.review_state == "approved" and (not self.approved_by or not self.approved_at):
            raise ValueError("approved remediation blueprints require operator provenance")
        if not self.source_snapshot_ids or not _is_sha256(self.source_sha256):
            raise ValueError("remediation blueprints require source snapshots and SHA-256")
        if not isinstance(self.blueprint, dict) or not self.blueprint:
            raise ValueError("remediation blueprints require a structured payload")
        _reject_executable_blueprint_payload(self.blueprint)
        for reference in self.evidence_refs:
            _validate_agentic_evidence_ref(reference)
        self.content_sha256 = _validated_content_hash(
            self.content_sha256,
            {
                "contract_version": self.contract_version,
                "run_id": self.run_id,
                "attempt_id": self.attempt_id,
                "work_item_id": self.work_item_id,
                "mode": self.mode,
                "source_snapshot_ids": self.source_snapshot_ids,
                "source_sha256": self.source_sha256,
                "blueprint": self.blueprint,
                "evidence_refs": self.evidence_refs,
                "renderer_version": self.renderer_version,
                "placeholder_fields": self.placeholder_fields,
                "limitations": self.limitations,
            },
            label="remediation blueprint",
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RecommendationOutcomeLink:
    recommendation_id: str
    source_snapshot_id: str
    outreach_package_id: str
    outreach_package_version: int
    prospect_id: str
    vertical_id: str
    service_fit: list[str]
    id: str = field(default_factory=new_id)
    contract_version: str = RECOMMENDATION_OUTCOME_LINK_VERSION
    activation_event_ids: list[str] = field(default_factory=list)
    correction_event_ids: list[str] = field(default_factory=list)
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != RECOMMENDATION_OUTCOME_LINK_VERSION:
            raise ValueError(f"unsupported recommendation outcome link: {self.contract_version}")
        required = (
            self.recommendation_id,
            self.source_snapshot_id,
            self.outreach_package_id,
            self.prospect_id,
            self.vertical_id,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("outcome links require recommendation, snapshot, package, and prospect identity")
        if self.outreach_package_version < 1 or not self.service_fit:
            raise ValueError("outcome links require a package version and service fit")
        for identifiers in (self.activation_event_ids, self.correction_event_ids):
            if len(set(identifiers)) != len(identifiers):
                raise ValueError("outcome event identifiers must be unique")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgenticEvidenceReviewEvent:
    snapshot_id: str
    snapshot_type: str
    event_type: str
    operator: str
    reason_code: str
    id: str = field(default_factory=new_id)
    contract_version: str = AGENTIC_EVIDENCE_REVIEW_VERSION
    notes: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != AGENTIC_EVIDENCE_REVIEW_VERSION:
            raise ValueError(f"unsupported agentic evidence review: {self.contract_version}")
        required = (
            self.snapshot_id,
            self.snapshot_type,
            self.operator,
            self.reason_code,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("agentic evidence reviews require snapshot, type, operator, and reason")
        if self.event_type not in {
            "review_requested",
            "approved",
            "rejected",
            "correction_recorded",
            "superseded",
        }:
            raise ValueError(f"invalid agentic evidence review event: {self.event_type}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class LocalVisibilityGridDefinition:
    vertical_id: str
    market: str
    location_code: int
    center_latitude: float
    center_longitude: float
    rows: int
    columns: int
    spacing_meters: int
    keyword_target_ids: list[str]
    place_id: str
    approved_by: str
    id: str = field(default_factory=new_id)
    version: int = 1
    contract_version: str = LOCAL_VISIBILITY_VERSION
    identity_sha256: str | None = None
    approved_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != LOCAL_VISIBILITY_VERSION:
            raise ValueError(f"unsupported local visibility contract: {self.contract_version}")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (self.vertical_id, self.market, self.place_id, self.approved_by)
        ):
            raise ValueError("local grids require vertical, market, place, and approval identity")
        if self.version < 1 or self.location_code <= 0:
            raise ValueError("local grid version and location code must be positive")
        if (self.rows, self.columns) not in {(3, 3), (5, 5)}:
            raise ValueError("local visibility grids must be 3x3 or 5x5")
        if self.spacing_meters <= 0 or not self.keyword_target_ids:
            raise ValueError("local grids require positive spacing and approved keywords")
        if not -90 <= self.center_latitude <= 90 or not -180 <= self.center_longitude <= 180:
            raise ValueError("local grid coordinates are invalid")
        digest = canonical_sha256(
            {
                "contract_version": self.contract_version,
                "vertical_id": self.vertical_id,
                "market": self.market,
                "location_code": self.location_code,
                "center_latitude": self.center_latitude,
                "center_longitude": self.center_longitude,
                "rows": self.rows,
                "columns": self.columns,
                "spacing_meters": self.spacing_meters,
                "keyword_target_ids": self.keyword_target_ids,
                "place_id": self.place_id,
                "version": self.version,
            }
        )
        if self.identity_sha256 is None:
            self.identity_sha256 = digest
        elif self.identity_sha256 != digest:
            raise ValueError("local grid identity hash does not match its definition")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PromptTopicSet:
    vertical_id: str
    market: str
    topics: list[dict[str, Any]]
    source_sha256: str
    id: str = field(default_factory=new_id)
    version: int = 1
    state: str = "draft"
    approved_by: str | None = None
    approved_at: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if not self.vertical_id.strip() or not self.market.strip() or not self.topics:
            raise ValueError("prompt topic sets require vertical, market, and topics")
        if not _is_sha256(self.source_sha256):
            raise ValueError("prompt topic set source hash must be SHA-256")
        if self.version < 1:
            raise ValueError("prompt topic set version must be positive")
        if self.state not in {"draft", "approved", "superseded"}:
            raise ValueError(f"invalid prompt topic set state: {self.state}")
        if self.state == "approved" and (not self.approved_by or not self.approved_at):
            raise ValueError("approved prompt topic sets require operator provenance")
        for topic in self.topics:
            if not isinstance(topic, dict) or not str(topic.get("prompt", "")).strip():
                raise ValueError("prompt topic entries require prompt text")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OwnedMeasurementSnapshot:
    prospect_id: str
    vertical_id: str
    source: str
    period_start: str
    period_end: str
    source_sha256: str
    context: dict[str, Any]
    metrics: dict[str, float | int | None]
    artifact_ref: str
    id: str = field(default_factory=new_id)
    contract_version: str = OWNED_MEASUREMENT_VERSION
    predecessor_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != OWNED_MEASUREMENT_VERSION:
            raise ValueError(f"unsupported owned measurement contract: {self.contract_version}")
        required = (
            self.prospect_id,
            self.vertical_id,
            self.source,
            self.period_start,
            self.period_end,
            self.artifact_ref,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("owned measurements require prospect, vertical, source, period, and artifact")
        if self.source not in {"gsc_csv", "gbp_csv", "ga4_csv", "crm_csv", "ai_performance_csv"}:
            raise ValueError(f"unsupported owned measurement source: {self.source}")
        if self.period_end < self.period_start:
            raise ValueError("owned measurement period end cannot precede its start")
        if not _is_sha256(self.source_sha256):
            raise ValueError("owned measurement source hash must be SHA-256")
        forbidden = _forbidden_payload_keys({"context": self.context, "metrics": self.metrics})
        pii_keys = {
            "email",
            "email_address",
            "first_name",
            "full_name",
            "last_name",
            "name",
            "phone",
            "phone_number",
        }
        observed_keys = {
            str(key).casefold().replace("-", "_")
            for payload in (self.context, self.metrics)
            for key in payload
        }
        if forbidden or observed_keys & pii_keys:
            raise ValueError("owned measurements cannot contain credentials or lead PII")
        if any(value is not None and (not isinstance(value, (int, float)) or value < 0) for value in self.metrics.values()):
            raise ValueError("owned measurement metrics must be non-negative aggregates")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DemandTrendSnapshot:
    """Immutable, context-bound market trend or planner export."""

    prospect_id: str
    vertical_id: str
    market: str
    source: str
    period_start: str
    period_end: str
    source_sha256: str
    terms: list[dict[str, Any]]
    artifact_ref: str
    id: str = field(default_factory=new_id)
    contract_version: str = DEMAND_TREND_VERSION
    version: int = 1
    location_code: int | None = None
    context: dict[str, Any] = field(default_factory=dict)
    state: str = "draft"
    approved_by: str | None = None
    approved_at: str | None = None
    predecessor_id: str | None = None
    superseded_by_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != DEMAND_TREND_VERSION:
            raise ValueError(f"unsupported demand trend contract: {self.contract_version}")
        required = (
            self.prospect_id,
            self.vertical_id,
            self.market,
            self.source,
            self.period_start,
            self.period_end,
            self.source_sha256,
            self.artifact_ref,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError(
                "demand trends require prospect, vertical, market, source, period, hash, and artifact"
            )
        if self.source not in {
            "google_trends_csv",
            "keyword_planner_csv",
            "operator_csv",
        }:
            raise ValueError(f"unsupported demand trend source: {self.source}")
        if self.period_end < self.period_start:
            raise ValueError("demand trend period end cannot precede its start")
        if not _is_sha256(self.source_sha256):
            raise ValueError("demand trend source hash must be SHA-256")
        if self.version < 1:
            raise ValueError("demand trend version must be positive")
        if self.location_code is not None and self.location_code <= 0:
            raise ValueError("demand trend location code must be positive")
        if self.state not in {"draft", "review", "approved", "superseded"}:
            raise ValueError(f"invalid demand trend state: {self.state}")
        if _forbidden_payload_keys({"context": self.context, "terms": self.terms}):
            raise ValueError("demand trends cannot contain credentials")
        if _contains_unique_person_claim(self.terms):
            raise ValueError("demand trends cannot claim keyword observations are unique people")
        if not self.terms:
            raise ValueError("demand trend snapshots require at least one term")
        for term in self.terms:
            if not isinstance(term, dict):
                raise ValueError("demand trend terms must be structured records")
            keyword = str(term.get("keyword") or "").strip()
            family = str(term.get("intent_family") or "").strip()
            provenance = str(term.get("provenance_label") or "").strip()
            metrics = term.get("metrics")
            if not keyword or not family or provenance not in {"observed", "supplied"}:
                raise ValueError(
                    "demand trend terms require keyword, intent family, and observed/supplied provenance"
                )
            if not isinstance(metrics, dict) or not metrics:
                raise ValueError("demand trend terms require metrics")
            if any(
                value is not None
                and (not isinstance(value, (int, float)) or value < 0)
                for value in metrics.values()
            ):
                raise ValueError("demand trend metrics must be non-negative numbers")
            relative_interest = metrics.get("relative_interest")
            if relative_interest is not None and relative_interest > 100:
                raise ValueError("Google Trends relative interest must be between zero and 100")
        if self.state == "approved" and (
            not self.approved_by or not self.approved_at
        ):
            raise ValueError("approved demand trends require operator provenance")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ConversionEventMap:
    """Approved mapping from aggregate measurement fields to funnel stages."""

    prospect_id: str
    vertical_id: str
    mappings: dict[str, list[str]]
    source_snapshot_ids: list[str]
    id: str = field(default_factory=new_id)
    contract_version: str = CONVERSION_EVENT_MAP_VERSION
    version: int = 1
    state: str = "draft"
    approved_by: str | None = None
    approved_at: str | None = None
    predecessor_id: str | None = None
    superseded_by_id: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != CONVERSION_EVENT_MAP_VERSION:
            raise ValueError(
                f"unsupported conversion event map contract: {self.contract_version}"
            )
        if not self.prospect_id.strip() or not self.vertical_id.strip():
            raise ValueError("conversion event maps require prospect and vertical identity")
        if self.version < 1:
            raise ValueError("conversion event map version must be positive")
        if self.state not in {"draft", "approved", "superseded"}:
            raise ValueError(f"invalid conversion event map state: {self.state}")
        invalid_stages = set(self.mappings) - CONVERSION_FUNNEL_STAGES
        if invalid_stages:
            raise ValueError(f"unsupported conversion funnel stages: {sorted(invalid_stages)}")
        if not self.mappings or not self.source_snapshot_ids:
            raise ValueError("conversion event maps require mappings and source snapshots")
        for stage, events in self.mappings.items():
            if not events or any(
                not isinstance(event, str) or not event.strip() for event in events
            ):
                raise ValueError(f"conversion event stage {stage} requires event names")
            if len(set(events)) != len(events):
                raise ValueError(f"conversion event stage {stage} contains duplicate events")
        if len(set(self.source_snapshot_ids)) != len(self.source_snapshot_ids):
            raise ValueError("conversion event maps require unique source snapshots")
        if self.state == "approved" and (
            not self.approved_by or not self.approved_at
        ):
            raise ValueError("approved conversion event maps require operator provenance")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DemandConversionEvidence:
    """Immutable demand-to-conversion evidence and capacity-aware scenarios."""

    insight_run_id: str
    prospect_id: str
    vertical_id: str
    mode: str
    market: str
    source_snapshots: list[dict[str, Any]]
    intent_groups: list[dict[str, Any]]
    observed_inputs: dict[str, Any]
    modeled_outputs: dict[str, Any]
    economics: dict[str, Any]
    capacity: dict[str, Any]
    id: str = field(default_factory=new_id)
    target_id: str | None = None
    normalized_domain: str | None = None
    attempt_id: str | None = None
    contract_version: str = DEMAND_CONVERSION_VERSION
    formula_version: str = DEMAND_CONVERSION_FORMULA_VERSION
    completeness_percent: float = 0.0
    status: str = "limited"
    state: str = "draft"
    assumptions: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    evidence_refs: list[dict[str, Any]] = field(default_factory=list)
    predecessor_id: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != DEMAND_CONVERSION_VERSION:
            raise ValueError(
                f"unsupported demand conversion contract: {self.contract_version}"
            )
        if self.formula_version != DEMAND_CONVERSION_FORMULA_VERSION:
            raise ValueError(
                f"unsupported demand conversion formula: {self.formula_version}"
            )
        required = (
            self.insight_run_id,
            self.prospect_id,
            self.vertical_id,
            self.mode,
            self.market,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError(
                "demand conversion evidence requires run, prospect, vertical, mode, and market"
            )
        if self.mode not in DEMAND_CONVERSION_MODES:
            raise ValueError(f"invalid demand conversion mode: {self.mode}")
        if not 0 <= self.completeness_percent <= 100:
            raise ValueError("demand conversion completeness must be between zero and 100")
        expected_status = (
            "complete"
            if self.completeness_percent >= 85
            else "partial"
            if self.completeness_percent >= 50
            else "limited"
        )
        if self.status != expected_status:
            raise ValueError(
                "demand conversion status must match completeness thresholds"
            )
        if self.state not in {"draft", "approved", "superseded"}:
            raise ValueError(f"invalid demand conversion state: {self.state}")
        sensitive_payload = {
            "sources": self.source_snapshots,
            "observed_inputs": self.observed_inputs,
            "economics": self.economics,
            "capacity": self.capacity,
            "assumptions": self.assumptions,
        }
        if _forbidden_payload_keys(sensitive_payload):
            raise ValueError("demand conversion evidence cannot contain credentials")
        pii_keys = {
            "email",
            "email_address",
            "first_name",
            "full_name",
            "last_name",
            "name",
            "phone",
            "phone_number",
        }
        observed_keys = {
            str(key).casefold().replace("-", "_")
            for payload in (
                self.observed_inputs,
                self.economics,
                self.capacity,
            )
            for key in payload
        }
        if observed_keys & pii_keys:
            raise ValueError("demand conversion evidence cannot contain lead PII")
        if _contains_unique_person_claim(
            {
                "intent_groups": self.intent_groups,
                "observed_inputs": self.observed_inputs,
                "modeled_outputs": self.modeled_outputs,
                "assumptions": self.assumptions,
                "warnings": self.warnings,
            }
        ):
            raise ValueError(
                "demand conversion evidence cannot claim search occasions are unique people"
            )
        owner_sources = 0
        for source in self.source_snapshots:
            if not isinstance(source, dict):
                raise ValueError("demand conversion sources must be structured records")
            source_class = str(source.get("source_class") or "")
            provenance = str(source.get("provenance_label") or "")
            required_source_values = (
                source.get("source_name"),
                source.get("source_sha256"),
                source.get("artifact_ref"),
                source.get("snapshot_date"),
            )
            if source_class not in DEMAND_CONVERSION_SOURCE_CLASSES:
                raise ValueError(f"invalid demand conversion source class: {source_class}")
            if provenance not in DEMAND_CONVERSION_PROVENANCE_LABELS:
                raise ValueError(
                    f"invalid demand conversion provenance label: {provenance}"
                )
            if any(not str(value or "").strip() for value in required_source_values):
                raise ValueError(
                    "demand conversion sources require name, hash, artifact, and snapshot date"
                )
            if not _is_sha256(str(source["source_sha256"])):
                raise ValueError("demand conversion source hash must be SHA-256")
            hierarchy_level = source.get(
                "hierarchy_level",
                DEMAND_CONVERSION_SOURCE_CLASSES[source_class],
            )
            if hierarchy_level != DEMAND_CONVERSION_SOURCE_CLASSES[source_class]:
                raise ValueError("demand conversion source hierarchy is inconsistent")
            if source.get("prospect_id") not in {None, self.prospect_id}:
                raise ValueError("demand conversion source prospect does not match")
            if source.get("vertical_id") not in {None, self.vertical_id}:
                raise ValueError("demand conversion source vertical does not match")
            if source_class == "owner_first_party":
                owner_sources += 1
        if self.mode == "prospect" and owner_sources:
            raise ValueError("prospect mode cannot reference owner-first-party evidence")
        if self.mode == "owner_verified" and not owner_sources:
            raise ValueError("owner-verified mode requires owner-first-party evidence")
        if self.modeled_outputs and not any(
            source.get("source_class") == "scenario_model"
            for source in self.source_snapshots
        ):
            raise ValueError("modeled outputs require an attributable scenario source")
        if self.state == "approved" and (
            not self.approved_by or not self.approved_at
        ):
            raise ValueError("approved demand conversion evidence requires operator provenance")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DemandConversionReportSnapshot:
    """Immutable rendered demand-conversion report identity."""

    demand_conversion_evidence_id: str
    run_id: str
    mode: str
    payload_sha256: str
    payload_artifact_ref: str
    source_hashes: dict[str, str]
    id: str = field(default_factory=new_id)
    report_contract: str = DEMAND_CONVERSION_REPORT_VERSION
    schema_version: int = 1
    manifest_sha256: str | None = None
    completeness_percent: float = 0.0
    status: str = "limited"
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.report_contract != DEMAND_CONVERSION_REPORT_VERSION:
            raise ValueError(
                f"unsupported demand conversion report: {self.report_contract}"
            )
        if self.mode not in DEMAND_CONVERSION_MODES:
            raise ValueError(f"invalid demand conversion report mode: {self.mode}")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (
                self.demand_conversion_evidence_id,
                self.run_id,
                self.payload_artifact_ref,
            )
        ):
            raise ValueError(
                "demand conversion reports require evidence, run, and artifact identity"
            )
        if not _is_sha256(self.payload_sha256):
            raise ValueError("demand conversion report payload hash must be SHA-256")
        if self.manifest_sha256 is not None and not _is_sha256(
            self.manifest_sha256
        ):
            raise ValueError("demand conversion report manifest hash must be SHA-256")
        if any(not _is_sha256(value) for value in self.source_hashes.values()):
            raise ValueError("demand conversion report source hashes must be SHA-256")
        if self.schema_version < 1:
            raise ValueError("demand conversion report schema version must be positive")
        if not 0 <= self.completeness_percent <= 100:
            raise ValueError("demand conversion report completeness must be 0–100")
        expected_status = (
            "complete"
            if self.completeness_percent >= 85
            else "partial"
            if self.completeness_percent >= 50
            else "limited"
        )
        if self.status != expected_status:
            raise ValueError(
                "demand conversion report status must match completeness thresholds"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportComparisonSnapshot:
    target_id: str
    baseline_snapshot_id: str
    current_snapshot_id: str
    baseline_sha256: str
    current_sha256: str
    compatibility: dict[str, bool]
    changes: dict[str, Any]
    id: str = field(default_factory=new_id)
    contract_version: str = REPORT_COMPARISON_VERSION
    unknown_reasons: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.contract_version != REPORT_COMPARISON_VERSION:
            raise ValueError(f"unsupported comparison contract: {self.contract_version}")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (self.target_id, self.baseline_snapshot_id, self.current_snapshot_id)
        ):
            raise ValueError("comparisons require target, baseline, and current snapshot identity")
        if not _is_sha256(self.baseline_sha256) or not _is_sha256(self.current_sha256):
            raise ValueError("comparison source hashes must be SHA-256")
        incompatible = [key for key, value in self.compatibility.items() if value is False]
        if incompatible and self.changes.get("numeric_deltas"):
            raise ValueError("incompatible comparisons cannot contain numeric deltas")
        if incompatible and not self.unknown_reasons:
            raise ValueError("incompatible comparisons require explicit unknown reasons")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OutreachPackage:
    """Immutable commercial framing derived from one persisted report version."""

    insight_run_id: str = ""
    prospect_id: str = ""
    vertical_pack_version: str = ""
    report_version: str = "v2"
    id: str = field(default_factory=new_id)
    package_version: int = 1
    state: str = "draft"
    approved_findings: list[dict[str, Any]] = field(default_factory=list)
    executive_answer: str = ""
    what_we_found: str = ""
    why_it_matters: str = ""
    what_we_would_fix: str = ""
    confidence: str = "low"
    effort: str = "discovery_required"
    recommended_service_package: list[str] = field(default_factory=list)
    subject_line: str = ""
    email_body: str = ""
    evidence_brief: str = ""
    evidence_limits: list[dict[str, Any]] = field(default_factory=list)
    ai_report_version: str | None = None
    ai_score_snapshot: dict[str, Any] = field(default_factory=dict)
    ai_evidence_acknowledged: bool = False
    market_report_version: str | None = None
    market_evidence_run_id: str | None = None
    market_snapshot_sha256: str | None = None
    market_evidence_refs: list[dict[str, Any]] = field(default_factory=list)
    screenshot_refs: list[dict[str, Any]] = field(default_factory=list)
    opportunity_report_version: str | None = None
    opportunity_scenario_id: str | None = None
    opportunity_snapshot_sha256: str | None = None
    opportunity_evidence_refs: list[dict[str, Any]] = field(default_factory=list)
    report_snapshot_id: str | None = None
    report_snapshot_sha256: str | None = None
    client_report_bundle_id: str | None = None
    agentic_assessment_id: str | None = None
    decision_intelligence_report_version: str | None = None
    agentic_snapshot_ids: dict[str, str] = field(default_factory=dict)
    agentic_snapshot_hashes: dict[str, str] = field(default_factory=dict)
    approved_by: str | None = None
    approved_at: str | None = None
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def __post_init__(self) -> None:
        if self.state not in {"draft", "needs_review", "approved", "rejected", "superseded"}:
            raise ValueError(f"invalid outreach package state: {self.state}")
        if self.package_version < 1:
            raise ValueError("outreach package version must be positive")
        if self.confidence not in {"high", "medium", "low"}:
            raise ValueError(f"invalid outreach package confidence: {self.confidence}")
        if self.effort not in {"small", "medium", "large", "discovery_required"}:
            raise ValueError(f"invalid outreach package effort: {self.effort}")
        allowed_services = {
            "web_development_rebuild",
            "profile_management_reputation",
            "pseo_search_architecture",
            "one_trade_network_visibility",
            "one_trade_network_crm_saas",
            "national_bjj_registry_visibility",
            "national_bjj_registry_crm_saas",
            "website_seo_vertical_visibility",
            "vertical_plugin_embed",
            "custom_website_crm_saas",
        }
        invalid_services = set(self.recommended_service_package) - allowed_services
        if invalid_services:
            raise ValueError(f"invalid recommended service package: {sorted(invalid_services)}")
        opportunity_identity = (
            self.opportunity_report_version,
            self.opportunity_scenario_id,
            self.opportunity_snapshot_sha256,
        )
        if any(value is not None for value in opportunity_identity) and not all(
            isinstance(value, str) and value.strip()
            for value in opportunity_identity
        ):
            raise ValueError(
                "opportunity package snapshots require report, scenario, and hash identity"
            )
        if self.decision_intelligence_report_version is not None:
            if self.decision_intelligence_report_version != DECISION_INTELLIGENCE_REPORT_VERSION:
                raise ValueError("outreach packages require decision-intelligence-v1")
            if not self.agentic_snapshot_ids or set(self.agentic_snapshot_ids) != set(
                self.agentic_snapshot_hashes
            ):
                raise ValueError(
                    "decision-intelligence packages require matching snapshot IDs and hashes"
                )
            if any(not _is_sha256(value) for value in self.agentic_snapshot_hashes.values()):
                raise ValueError("agentic outreach snapshot hashes must be SHA-256")
        elif self.agentic_snapshot_ids or self.agentic_snapshot_hashes:
            raise ValueError("agentic snapshot bindings require a decision-intelligence report")
        if self.state == "approved":
            required = (
                self.insight_run_id,
                self.prospect_id,
                self.vertical_pack_version,
                self.report_version,
                self.executive_answer,
                self.what_we_found,
                self.why_it_matters,
                self.what_we_would_fix,
                self.subject_line,
                self.email_body,
                self.evidence_brief,
            )
            if any(not isinstance(value, str) or not value.strip() for value in required):
                raise ValueError("approved outreach packages require complete exportable content")
            if not self.approved_by or not self.approved_at:
                raise ValueError("approved outreach packages require operator approval provenance")
            if not self.approved_findings or any(
                finding.get("finding_type") != "prospect_issue"
                for finding in self.approved_findings
            ):
                raise ValueError(
                    "approved outreach packages require at least one supported prospect issue"
                )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OutreachActivationEvent:
    """Append-only funnel event attributed to an immutable package version."""

    insight_run_id: str = ""
    outreach_package_id: str = ""
    stage: str = ""
    id: str = field(default_factory=new_id)
    package_version: int = 1
    vertical_id: str = ""
    occurred_at: str = field(default_factory=utc_now_iso)
    operator: str = ""
    source_system: str = "manual"
    external_reference: str | None = None
    service_packages: list[str] = field(default_factory=list)
    reason_code: str | None = None
    correction_class: str | None = None
    revenue_amount: float | None = None
    currency: str | None = None

    def __post_init__(self) -> None:
        allowed_stages = {
            "package_approved",
            "outreach_sent",
            "positive_reply",
            "call_booked",
            "proposal_sent",
            "closed_won",
            "closed_lost",
            "correction_recorded",
        }
        if self.stage not in allowed_stages:
            raise ValueError(f"invalid activation stage: {self.stage}")
        if not self.insight_run_id or not self.outreach_package_id or not self.vertical_id:
            raise ValueError("activation events require run, package, and vertical identity")
        if not self.operator.strip():
            raise ValueError("activation events require an operator")
        if self.package_version < 1:
            raise ValueError("activation package version must be positive")
        if self.revenue_amount is not None and self.stage != "closed_won":
            raise ValueError("revenue is permitted only for closed_won events")
        if self.stage == "closed_won":
            if self.revenue_amount is None or self.revenue_amount < 0:
                raise ValueError("closed_won requires non-negative revenue_amount")
            if not self.currency:
                raise ValueError("closed_won requires currency")
        elif self.currency is not None:
            raise ValueError("currency is permitted only for closed_won events")
        if self.stage == "correction_recorded" and not (self.reason_code or self.correction_class):
            raise ValueError("correction_recorded requires a reason_code or correction_class")

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

from __future__ import annotations

import os
import secrets
from dataclasses import replace
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from src.config import APP_RUNTIME_DOTENV, AppConfig, ApprovalPolicy, load_config
from src.dataforseo_client import DataForSEOClient
from src.models import (
    BusinessEconomicsProfile,
    ConversionEventMap,
    AgenticAssessmentReviewEvent,
    AgenticEvidenceReviewEvent,
    OutreachActivationEvent,
    PromptTopicSet,
    canonical_sha256,
    new_id,
    utc_now_iso,
)
from src.orchestrator import InsightRunOrchestrator
from src.repositories.base import InsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.activation_service import ActivationService
from src.services.agentic_analysis_service import AgenticAnalysisService
from src.services.agentic_job_service import AgenticJobPolicyError, AgenticJobService
from src.services.ai_visibility_service import AIVisibilityService
from src.services.client_report_service import ClientReportService
from src.services.competitor_evidence_service import CompetitorEvidenceService
from src.services.calibration_service import CalibrationService
from src.services.demand_evidence_service import DemandEvidenceService
from src.services.demand_conversion_search_service import (
    DemandConversionSearchService,
)
from src.services.demand_conversion_reporting_service import (
    DemandConversionReportingService,
)
from src.services.demand_conversion_service import DemandConversionService
from src.services.demand_trend_service import DemandTrendService
from src.services.decision_intelligence_reporting_service import (
    DecisionIntelligenceReportingService,
)
from src.services.keyword_set_service import KeywordSetService
from src.services.market_evidence_service import MarketEvidenceService
from src.services.market_reporting_service import MarketReportingService
from src.services.outreach_service import OutreachService
from src.services.opportunity_model_service import OpportunityModelService
from src.services.opportunity_reporting_service import OpportunityReportingService
from src.services.owned_measurement_service import OwnedMeasurementService
from src.services.owner_agentic_analysis_service import OwnerAgenticAnalysisService
from src.services.product_strength_service import ProductStrengthService
from src.services.prospect_intake_service import ProspectIntakeService
from src.services.screenshot_service import ScreenshotCaptureService
from src.services.report_validation_service import (
    DemandConversionReportValidationService,
)
from src.vertical_packs import list_vertical_packs, resolve_vertical_pack
from src.vertical_agentic_packs import list_vertical_agentic_packs
from src.services.vertical_agentic_evidence_service import (
    VerticalAgenticEvidenceService,
)


class RunCreateRequest(BaseModel):
    url: str = Field(min_length=3, max_length=2048)
    mode: Literal["quick", "standard", "full"] = "standard"
    max_pages: int = Field(default=100, ge=1, le=100)
    approve_paid_enrichment: bool | None = None


class RerunRequest(BaseModel):
    stage: str
    max_pages: int = Field(default=100, ge=1, le=100)


class ResumeRequest(BaseModel):
    max_pages: int = Field(default=100, ge=1, le=100)


class RecoveryRequest(BaseModel):
    worker_id: str = Field(default="api-reaper", min_length=1, max_length=100)
    reason: str = Field(default="stale lease recovery", min_length=1, max_length=500)


class ProspectCsvRequest(BaseModel):
    csv_text: str = Field(min_length=1, max_length=1_000_000)
    vertical_pack_version: str = Field(default="one_trade_network.v1", min_length=3, max_length=100)


class ProspectRunRequest(BaseModel):
    mode: Literal["quick", "standard", "full"] = "quick"
    max_pages: int = Field(default=100, ge=1, le=100)
    approve_paid_enrichment: bool | None = None


class OutreachPackageCreateRequest(BaseModel):
    prospect_id: str = Field(min_length=1, max_length=200)
    report_version: Literal["v2", "v3", "v4", "v6"] = "v2"
    vertical_pack_version: str | None = Field(default=None, min_length=3, max_length=100)
    report_snapshot_id: str | None = Field(default=None, max_length=200)
    client_report_bundle_id: str | None = Field(default=None, max_length=200)
    agentic_assessment_id: str | None = Field(default=None, max_length=200)


class PackageReviewRequest(BaseModel):
    operator: str = Field(default="operator", min_length=1, max_length=100)
    reason_code: str | None = Field(default=None, max_length=100)
    acknowledge_partial_ai: bool = False


class QualificationUpdateRequest(BaseModel):
    qualification_status: Literal["pending", "needs_review", "qualified", "rejected"]
    rejection_reasons: list[str] = Field(default_factory=list, max_length=20)
    operator: str = Field(default="operator", min_length=1, max_length=100)


class ActivationEventRequest(BaseModel):
    insight_run_id: str = Field(min_length=1, max_length=200)
    outreach_package_id: str = Field(min_length=1, max_length=200)
    package_version: int = Field(default=1, ge=1)
    stage: Literal[
        "package_approved",
        "outreach_sent",
        "positive_reply",
        "call_booked",
        "proposal_sent",
        "closed_won",
        "closed_lost",
        "correction_recorded",
    ]
    vertical_id: str = Field(min_length=1, max_length=100)
    operator: str = Field(min_length=1, max_length=100)
    source_system: str = Field(default="manual", min_length=1, max_length=100)
    external_reference: str | None = Field(default=None, max_length=500)
    service_packages: list[str] = Field(default_factory=list)
    reason_code: str | None = Field(default=None, max_length=100)
    correction_class: str | None = Field(default=None, max_length=100)
    revenue_amount: float | None = None
    currency: str | None = Field(default=None, max_length=12)


class KeywordCsvRequest(BaseModel):
    csv_text: str = Field(min_length=1, max_length=1_000_000)
    vertical_id: str = Field(default="national_bjj_registry", min_length=2, max_length=100)
    market: str = Field(default="Tacoma, WA", min_length=2, max_length=200)
    market_slug: str = Field(default="tacoma", min_length=1, max_length=100)
    location_code: int = Field(default=1027773, ge=1)
    language_code: str = Field(default="en", min_length=2, max_length=12)
    version: str = Field(default="v1", min_length=1, max_length=50)
    normalized_domain: str | None = Field(default=None, max_length=253)
    scope_type: Literal["vertical", "prospect", "domain"] = "vertical"
    scope_id: str | None = Field(default=None, max_length=200)
    source_provenance: str = Field(default="operator_csv_upload", min_length=1, max_length=500)


class KeywordReviewRequest(BaseModel):
    approved_keywords: list[str] = Field(default_factory=list, max_length=1000)
    rejected_keywords: list[str] = Field(default_factory=list, max_length=1000)
    operator: str = Field(default="operator", min_length=1, max_length=100)


class KeywordSupersedeRequest(BaseModel):
    successor_id: str = Field(min_length=1, max_length=200)


class MarketPilotRequest(BaseModel):
    keyword_set_id: str = Field(min_length=1, max_length=200)
    target_entity_name: str | None = Field(default=None, max_length=200)
    approve_paid_enrichment: bool = False


class CompetitorApprovalRequest(BaseModel):
    candidate_ids: list[str] = Field(min_length=1, max_length=3)
    operator: str = Field(default="operator", min_length=1, max_length=100)


class CompetitorEnrichmentRequest(BaseModel):
    approve_paid_enrichment: bool = False
    capture_screenshots: bool = True
    target_program_url: str | None = Field(default=None, max_length=2048)


class MarketDeepRequest(BaseModel):
    approve_paid_enrichment: bool = False


class MarketResumeRequest(BaseModel):
    approve_paid_enrichment: bool = False
    account_recovered: bool = False


class DemandEvidenceCsvRequest(BaseModel):
    csv_text: str = Field(min_length=1, max_length=5_000_000)
    prospect_id: str = Field(min_length=1, max_length=200)
    keyword_set_id: str = Field(min_length=1, max_length=200)
    vertical_id: str = Field(min_length=2, max_length=100)
    market: str = Field(min_length=2, max_length=200)
    location_code: int | None = Field(default=None, ge=1)
    snapshot_period: str = Field(default="2026-07", min_length=4, max_length=50)
    source: str = Field(default="operator_csv", min_length=1, max_length=100)
    brand_terms: list[str] = Field(default_factory=list, max_length=100)


class DemandApprovalRequest(BaseModel):
    operator: str = Field(default="operator", min_length=1, max_length=100)
    rationale: str = Field(
        default="Operator reviewed the deterministic intent and close-variant groups.",
        min_length=3,
        max_length=1000,
    )


class EconomicsRequest(BaseModel):
    vertical_id: str = Field(min_length=2, max_length=100)
    revenue_model: str = Field(min_length=2, max_length=100)
    monthly_price: float = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=12)
    capacity_headroom: float = Field(ge=0)
    field_provenance: dict[str, Literal[
        "operator_observed",
        "business_supplied",
        "assumed",
        "aggregate_calibration",
    ]]
    gross_margin_mode: Literal["unknown", "revenue", "gross_profit"] = "unknown"
    gross_margin_percent: float | None = Field(default=None, ge=0, le=1)
    retention_months: float | None = Field(default=None, gt=0)
    active_customer_count: float | None = Field(default=None, ge=0)
    desired_fill_months: float | None = Field(default=None, gt=0)
    current_monthly_leads: float | None = Field(default=None, ge=0)
    current_monthly_signups: float | None = Field(default=None, ge=0)
    visit_to_signup_rate: float | None = Field(default=None, ge=0, le=1)
    signup_to_attended_rate: float | None = Field(default=None, ge=0, le=1)
    attended_to_customer_rate: float | None = Field(default=None, ge=0, le=1)
    approve: bool = False
    operator: str = Field(default="operator", min_length=1, max_length=100)


class OpportunityScenarioRequest(BaseModel):
    prospect_id: str = Field(min_length=1, max_length=200)
    demand_evidence_set_id: str | None = Field(default=None, max_length=200)
    economics_profile_id: str = Field(min_length=1, max_length=200)
    assumptions: dict[str, dict[str, Any]]


class OpportunityApprovalRequest(BaseModel):
    operator: str = Field(default="operator", min_length=1, max_length=100)


class CalibrationCsvRequest(BaseModel):
    csv_text: str = Field(min_length=1, max_length=1_000_000)
    prospect_id: str = Field(min_length=1, max_length=200)
    vertical_id: str = Field(min_length=2, max_length=100)
    market: str = Field(min_length=2, max_length=200)


class PitchPackRequest(BaseModel):
    prospect_id: str = Field(min_length=1, max_length=200)
    vertical_pack_version: str | None = Field(default=None, max_length=100)
    report_snapshot_id: str | None = Field(default=None, max_length=200)
    client_report_bundle_id: str | None = Field(default=None, max_length=200)
    agentic_assessment_id: str | None = Field(default=None, max_length=200)


class AgenticAnalysisRequest(BaseModel):
    vertical_pack_version: str | None = Field(default=None, max_length=100)
    analysis_mode: Literal["standard", "premium"] = "standard"
    target_facts: dict[str, Any] = Field(default_factory=dict)
    keyword_set_id: str | None = Field(default=None, max_length=200)
    market_run_id: str | None = Field(default=None, max_length=200)
    opportunity_scenario_id: str | None = Field(default=None, max_length=200)


class AgenticReviewRequest(BaseModel):
    event_type: Literal[
        "review_requested",
        "gpt_review_requested",
        "approved",
        "rejected",
        "correction_recorded",
    ]
    operator: str = Field(default="operator", min_length=1, max_length=100)
    reason_code: str = Field(default="operator_review", min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)
    external_reference: str | None = Field(default=None, max_length=500)


class VerticalAgenticEvidenceRequest(AgenticAnalysisRequest):
    execution_mode: Literal["automatic", "shadow", "review", "premium"] = "automatic"


class AgenticEvidenceReviewRequest(BaseModel):
    snapshot_type: Literal[
        "business_fact_ledger",
        "decision_coverage",
        "journey_evidence",
        "ai_representation_accuracy",
        "owner_diagnostic",
        "remediation_blueprint",
    ]
    event_type: Literal[
        "review_requested",
        "approved",
        "rejected",
        "correction_recorded",
        "superseded",
    ]
    operator: str = Field(default="operator", min_length=1, max_length=100)
    reason_code: str = Field(default="operator_review", min_length=1, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class OwnerAgenticAnalysisRequest(AgenticAnalysisRequest):
    prospect_id: str = Field(min_length=1, max_length=200)
    consent_id: str = Field(min_length=1, max_length=200)
    approved_snapshot_ids: list[str] = Field(min_length=1, max_length=20)
    execution_mode: Literal["review", "premium"] = "premium"


class RemediationBlueprintRequest(AgenticAnalysisRequest):
    source_snapshot_ids: list[str] = Field(min_length=1, max_length=50)
    execution_mode: Literal["review", "premium"] = "premium"


class ClientBundleRequest(BaseModel):
    report_snapshot_id: str | None = Field(default=None, max_length=200)
    assessment_id: str | None = Field(default=None, max_length=200)


class OwnedMeasurementCsvRequest(BaseModel):
    csv_text: str = Field(min_length=1, max_length=2_000_000)
    prospect_id: str = Field(min_length=1, max_length=200)
    vertical_id: str = Field(min_length=2, max_length=100)
    source: Literal[
        "gsc_csv",
        "gbp_csv",
        "ga4_csv",
        "crm_csv",
        "ai_performance_csv",
    ]
    context: dict[str, Any]
    artifact_ref: str | None = Field(default=None, max_length=500)
    period_start: str | None = Field(default=None, max_length=50)
    period_end: str | None = Field(default=None, max_length=50)
    owner_verified: bool = False
    owner_consent: dict[str, Any] | None = None
    data_freshness: dict[str, Any] | None = None
    event_map_id: str | None = Field(default=None, max_length=200)
    event_map_version: str | None = Field(default=None, max_length=50)


class DemandTrendCsvRequest(BaseModel):
    csv_text: str = Field(min_length=1, max_length=5_000_000)
    prospect_id: str = Field(min_length=1, max_length=200)
    vertical_id: str = Field(min_length=2, max_length=100)
    market: str = Field(min_length=2, max_length=200)
    source: Literal[
        "google_trends_csv",
        "keyword_planner_csv",
        "operator_csv",
    ]
    period_start: str = Field(min_length=4, max_length=50)
    period_end: str = Field(min_length=4, max_length=50)
    location_code: int | None = Field(default=None, ge=1)
    keyword_set_id: str | None = Field(default=None, max_length=200)
    context: dict[str, Any] = Field(default_factory=dict)
    artifact_ref: str | None = Field(default=None, max_length=500)
    brand_terms: list[str] = Field(default_factory=list, max_length=100)
    aggregation_rule: Literal[
        "provider_grouped",
        "max_close_variant",
        "sum_distinct_intents",
    ] = "max_close_variant"
    operator_approved: bool = False
    operator: str | None = Field(default=None, max_length=100)


class ConversionEventMapRequest(BaseModel):
    prospect_id: str = Field(min_length=1, max_length=200)
    vertical_id: str = Field(min_length=2, max_length=100)
    mappings: dict[
        Literal["visit", "lead", "booking", "attended", "customer", "revenue"],
        list[str],
    ]
    source_snapshot_ids: list[str] = Field(min_length=1, max_length=1000)
    approve: bool = False
    operator: str = Field(default="operator", min_length=1, max_length=100)


class DemandConversionRequest(BaseModel):
    prospect_id: str = Field(min_length=1, max_length=200)
    mode: Literal["prospect", "owner_verified"] = "prospect"
    market: str = Field(min_length=2, max_length=200)
    demand_evidence_set_id: str | None = Field(default=None, max_length=200)
    economics_profile_id: str | None = Field(default=None, max_length=200)
    owner_snapshot_ids: list[str] = Field(default_factory=list, max_length=2000)
    trend_snapshot_ids: list[str] = Field(default_factory=list, max_length=1000)
    event_map_id: str | None = Field(default=None, max_length=200)
    assumptions: dict[str, dict[str, float | int | None]] = Field(
        default_factory=dict
    )
    public_sources: list[dict[str, Any]] = Field(default_factory=list, max_length=1000)


class DemandConversionApprovalRequest(BaseModel):
    operator: str = Field(default="operator", min_length=1, max_length=100)


class AIVisibilityPreflightRequest(BaseModel):
    prompt_topic_set: dict[str, Any]
    context: dict[str, Any] = Field(default_factory=dict)
    approve_paid_enrichment: bool = False
    call_cap: int = Field(default=20, ge=1, le=20)


def resolve_paid_enrichment_approval(configured_default: bool, requested: bool | None) -> bool:
    """An explicit per-run choice wins; omission uses operator policy."""
    return configured_default if requested is None else requested


def create_app(
    *,
    repository: InsightRepository | None = None,
    artifact_root: str | Path | None = None,
    config: AppConfig | None = None,
    api_key: str | None = None,
    environment: str | None = None,
) -> FastAPI:
    root = Path(artifact_root or os.getenv("SEO_INSIGHTS_ARTIFACT_ROOT", "artifacts/seo_insight_runs"))
    runtime_environment = (environment or os.getenv("SEO_INSIGHTS_ENV", "development")).lower()
    configured_api_key = api_key if api_key is not None else os.getenv("SEO_INSIGHTS_API_KEY")
    if runtime_environment == "production" and not configured_api_key:
        raise RuntimeError("SEO_INSIGHTS_API_KEY is required in production")

    active_repository = repository or SQLiteInsightRepository(
        os.getenv("SEO_INSIGHTS_DATABASE_PATH", str(root / "seo-insights.db")),
        artifact_root=root,
    )
    # Production/development use the operator-owned, gitignored runtime file.
    # Tests retain the inert root-.env default unless they inject a config.
    base_config = config or load_config(
        APP_RUNTIME_DOTENV if runtime_environment != "test" else None
    )
    base_orchestrator = InsightRunOrchestrator(active_repository, config=base_config, artifact_root=root)
    prospect_intake = ProspectIntakeService()
    keyword_service = KeywordSetService(active_repository)
    outreach_service = OutreachService(active_repository, artifact_root=root)
    activation_service = ActivationService(active_repository)
    market_reporting = MarketReportingService(active_repository)
    demand_service = DemandEvidenceService(active_repository)
    demand_trend_service = DemandTrendService()
    demand_conversion_search = DemandConversionSearchService()
    demand_conversion_service = DemandConversionService(active_repository)
    demand_conversion_validator = DemandConversionReportValidationService(
        active_repository
    )
    demand_conversion_reporting = DemandConversionReportingService(
        active_repository,
        demand_conversion_validator,
    )
    opportunity_model = OpportunityModelService(active_repository)
    calibration_service = CalibrationService(active_repository)
    opportunity_reporting = OpportunityReportingService(active_repository)
    screenshot_service = ScreenshotCaptureService(active_repository)
    product_strength_service = ProductStrengthService(active_repository)
    agentic_job_service = AgenticJobService(
        active_repository,
        settings=base_config.agentic,
    )
    agentic_analysis_service = AgenticAnalysisService(
        active_repository,
        artifact_root=root,
        job_service=agentic_job_service,
    )
    vertical_agentic_evidence = VerticalAgenticEvidenceService(
        active_repository,
        settings=base_config.agentic,
    )
    decision_intelligence_reporting = DecisionIntelligenceReportingService(
        active_repository
    )
    owner_agentic_analysis = OwnerAgenticAnalysisService(active_repository)
    client_report_service = ClientReportService(
        active_repository,
        artifact_root=root,
        output_root=root,
    )
    owned_measurement_service = OwnedMeasurementService(active_repository)
    ai_visibility_service = AIVisibilityService()

    # Built-in packs are versioned contracts.  Persist them at startup so the
    # operator queue can resolve the exact pack used for each prospect even
    # before the first authenticated request is made.
    for builtin_pack in list_vertical_packs():
        active_repository.save_vertical_pack(builtin_pack)
    for builtin_agentic_pack in list_vertical_agentic_packs():
        active_repository.save_vertical_agentic_pack(builtin_agentic_pack)
    if not active_repository.list_keyword_sets(
        vertical_id="national_bjj_registry",
        normalized_domain="novaryu.com",
        limit=10,
    ):
        keyword_service.seed_tacoma_bjj()

    app = FastAPI(
        title="SEO Insights Platform API",
        version="1.0.0",
        docs_url=None if runtime_environment == "production" else "/docs",
        redoc_url=None,
    )
    app.state.repository = active_repository
    app.state.artifact_root = root
    app.state.environment = runtime_environment

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
        )
        return response

    def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
        if not configured_api_key or not x_api_key or not secrets.compare_digest(x_api_key, configured_api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid or missing API key",
            )

    auth = Depends(require_api_key)

    def orchestrator_for(approve_paid_enrichment: bool | None = None) -> InsightRunOrchestrator:
        effective_approval = resolve_paid_enrichment_approval(
            base_config.approval.allow_paid_api_calls,
            approve_paid_enrichment,
        )
        request_config = replace(
            base_config,
            approval=ApprovalPolicy(allow_paid_api_calls=effective_approval),
        )
        return InsightRunOrchestrator(active_repository, config=request_config, artifact_root=root)

    def run_or_404(run_id: str):
        run = active_repository.get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail=f"run {run_id} not found")
        return run

    def value_error_422(exc: ValueError) -> HTTPException:
        return HTTPException(status_code=422, detail=str(exc))

    def require_paid_market_approval(approved: bool) -> None:
        if not approved:
            raise HTTPException(
                status_code=409,
                detail="This market evidence action requires explicit paid-enrichment approval.",
            )
        if not base_config.dataforseo.configured:
            raise HTTPException(status_code=409, detail="DataForSEO credentials are not configured")

    def market_service_for(run_id: str) -> MarketEvidenceService:
        return MarketEvidenceService(
            active_repository,
            lambda: DataForSEOClient(
                base_config.dataforseo,
                artifact_dir=root / "runs" / run_id / "market-provider",
            ),
        )

    def build_agentic_pack(
        run_id: str,
        payload: AgenticAnalysisRequest,
    ):
        run = run_or_404(run_id)
        prospect = next(
            (
                item
                for item in active_repository.list_prospects(limit=10000)
                if item.normalized_domain == run.requested_domain.casefold().removeprefix("www.")
                and item.qualification_status in {"qualified", "needs_review"}
            ),
            None,
        )
        vertical_pack_version = (
            payload.vertical_pack_version
            or (prospect.vertical_pack_version if prospect else None)
        )
        target_facts = dict(payload.target_facts)
        if prospect is not None:
            target_facts = {
                "business_name": prospect.business_name,
                "category": prospect.category,
                "location": prospect.location,
                "source_provenance": prospect.source_provenance,
                **target_facts,
            }
        market_evidence = {}
        if payload.market_run_id:
            market_run = active_repository.get_market_evidence_run(payload.market_run_id)
            if market_run is None or market_run.insight_run_id != run_id:
                raise ValueError("market evidence does not belong to this run")
            market_evidence = market_run.to_dict()
        return agentic_analysis_service.build_evidence_pack(
            run_id,
            vertical_pack_version=vertical_pack_version,
            target_facts=target_facts,
            keyword_set_id=payload.keyword_set_id,
            market_run_id=payload.market_run_id,
            opportunity_scenario_id=payload.opportunity_scenario_id,
            market_evidence=market_evidence,
        )

    def attach_vertical_agentic_evidence(run) -> dict[str, Any]:
        """Non-blocking automatic handoff; it never executes inference in the request."""

        preliminary = vertical_agentic_evidence.preflight(
            run.id,
            execution_mode="automatic",
        )
        if (
            not preliminary["available"]
            and preliminary.get("unavailable_reason")
            != "A persisted scoped SiteEvidencePack is required."
        ):
            return {"preflight": preliminary, "work_items": []}
        try:
            pack = build_agentic_pack(run.id, AgenticAnalysisRequest())
            preflight = vertical_agentic_evidence.preflight(
                run.id,
                evidence_pack=pack,
                execution_mode="automatic",
            )
            items = (
                vertical_agentic_evidence.enqueue_defaults(pack)
                if preflight["available"]
                else []
            )
        except ValueError as exc:
            return {
                "preflight": {
                    **preliminary,
                    "available": False,
                    "unavailable_reason": str(exc),
                },
                "work_items": [],
            }
        return {
            "preflight": preflight,
            "evidence_pack": {
                "id": pack.id,
                "content_sha256": pack.content_sha256,
            },
            "work_items": [item.to_dict() for item in items],
        }

    def agentic_job_payload(job_id: str) -> dict[str, Any]:
        job = active_repository.get_agentic_analysis_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"agentic job {job_id} not found")
        calls = active_repository.list_agent_call_records(job_id=job.id, limit=5000)
        assessments = active_repository.list_agentic_assessment_snapshots(
            job_id=job.id,
            limit=1000,
        )
        return {
            "job": job.to_dict(),
            "calls": [call.to_dict() for call in calls],
            "assessments": [
                {
                    **assessment.to_dict(),
                    "review_state": agentic_job_service.review_state(assessment.id),
                    "review_events": [
                        event.to_dict()
                        for event in active_repository.list_agentic_assessment_review_events(
                            assessment.id,
                            limit=5000,
                        )
                    ],
                }
                for assessment in assessments
            ],
        }

    def agentic_snapshot_or_404(snapshot_id: str, snapshot_type: str):
        loaders = {
            "business_fact_ledger": active_repository.get_business_fact_ledger_snapshot,
            "decision_coverage": active_repository.get_decision_coverage_snapshot,
            "journey_evidence": active_repository.get_journey_evidence_run,
            "ai_representation_accuracy": (
                active_repository.get_ai_representation_accuracy_snapshot
            ),
            "owner_diagnostic": active_repository.get_owner_diagnostic_snapshot,
            "remediation_blueprint": active_repository.get_remediation_blueprint_snapshot,
        }
        loader = loaders.get(snapshot_type)
        snapshot = loader(snapshot_id) if loader else None
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"{snapshot_type} snapshot {snapshot_id} not found",
            )
        return snapshot

    def attach_market_resolution(run) -> dict | None:
        domain = run.requested_domain.casefold().removeprefix("www.")
        keyword_set = keyword_service.resolve_for_domain(domain)
        if keyword_set is None:
            return None
        try:
            preflight = MarketEvidenceService.preflight(
                keyword_set,
                phase="pilot",
            )
        except ValueError as exc:
            preflight = {
                "ready": False,
                "phase": "pilot",
                "provider_calls": 0,
                "evidence_limit": str(exc),
            }
        run.summary = {
            **run.summary,
            "market_keyword_set_id": keyword_set.id,
            "market_keyword_set_version": keyword_set.keyword_set_key,
            "market_pilot_preflight": preflight,
        }
        run.input_payload = {
            **run.input_payload,
            "market_keyword_set_id": keyword_set.id,
        }
        run.updated_at = utc_now_iso()
        active_repository.update_run(run)
        return {"keyword_set": keyword_set.to_dict(), "pilot_preflight": preflight}

    def attach_prospect_demand_conversion(run, prospect=None) -> dict | None:
        """Create a non-blocking prospect-mode evidence draft after a URL run.

        The URL-first path must remain useful when no operator imports exist.
        Missing demand, economics, or trends therefore stay unknown and
        suppress arithmetic; they never become zero or invented assumptions.
        """

        domain = run.requested_domain.casefold().removeprefix("www.")
        matched = prospect or next(
            (
                item
                for item in active_repository.list_prospects(limit=10000)
                if item.normalized_domain.casefold().removeprefix("www.") == domain
                and item.qualification_status in {"qualified", "needs_review"}
            ),
            None,
        )
        if matched is None:
            return None
        existing = active_repository.list_demand_conversion_evidence(
            insight_run_id=run.id,
            mode="prospect",
        )
        if existing:
            return existing[0].to_dict()
        demand_records = active_repository.list_demand_evidence_sets(
            prospect_id=matched.id,
            state="approved",
        )
        economics_records = active_repository.list_business_economics_profiles(
            prospect_id=matched.id,
            state="approved",
        )
        trend_records = active_repository.list_demand_trend_snapshots(
            prospect_id=matched.id,
            vertical_id=matched.vertical_id,
            market=matched.location,
            state="approved",
        )
        demand = demand_records[0] if demand_records else None
        economics = economics_records[0] if economics_records else None
        market_report = active_repository.get_report(run.id, "market-v1")
        rankings = (
            market_report.report_payload.get("organic_rankings", [])
            if market_report is not None
            else []
        )
        alignment = demand_conversion_search.align(
            prospect_id=matched.id,
            vertical_id=matched.vertical_id,
            market=matched.location,
            demand=demand,
            owner_snapshots=[],
            public_rankings=rankings,
        )
        public_sources: list[dict[str, Any]] = []
        v2 = active_repository.get_report(run.id, "v2")
        if v2 is not None:
            public_sources.append(
                {
                    "source_name": "bounded_crawl_report",
                    "source_class": "public_observed",
                    "hierarchy_level": 4,
                    "provenance_label": "observed",
                    "source_sha256": canonical_sha256(v2.report_payload),
                    "artifact_ref": f"runs/{run.id}/reports/v2.json",
                    "snapshot_date": run.updated_at[:10],
                }
            )
        evidence = demand_conversion_service.build(
            insight_run_id=run.id,
            prospect_id=matched.id,
            vertical_id=matched.vertical_id,
            market=matched.location,
            mode="prospect",
            demand=demand,
            economics=economics,
            trend_snapshots=trend_records,
            search_alignment=alignment,
            public_sources=public_sources,
            assumptions={},
            target_id=run.seo_target_id,
            normalized_domain=run.requested_domain,
            attempt_id=run.attempt_id,
        )
        run.summary = {
            **run.summary,
            "demand_conversion_evidence_id": evidence.id,
            "demand_conversion_mode": evidence.mode,
            "demand_conversion_status": evidence.status,
            "demand_conversion_completeness": evidence.completeness_percent,
        }
        run.updated_at = utc_now_iso()
        active_repository.update_run(run)
        return evidence.to_dict()

    @app.get("/healthz")
    def health() -> dict:
        database = active_repository.health() if hasattr(active_repository, "health") else {"status": "ok", "backend": "file"}
        return {
            "status": "ok" if database.get("status") == "ok" else "degraded",
            "environment": runtime_environment,
            "database": database,
            "search_enrichment": {
                "configured": base_config.dataforseo.configured,
                "default_approved": base_config.approval.allow_paid_api_calls,
                "max_paid_calls": base_config.dataforseo.max_paid_calls,
            },
            "screenshot_runtime": screenshot_service.health(),
            "agentic_analysis": {
                **base_config.agentic.redacted(),
                "available": base_config.agentic.available,
            },
            "vertical_agentic_evidence": {
                "automatic_available": base_config.agentic.available,
                "automatic_inference_ceiling_usd": 0.25,
                "premium_inference_ceiling_usd": 0.75,
                "execution_boundary": "durable_worker_only",
                "playwright": screenshot_service.health(),
            },
            "product_strength_contract": ProductStrengthService.CONTRACT_VERSION,
        }

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> HTMLResponse:
        dashboard_path = Path(__file__).resolve().parent / "static" / "dashboard.html"
        if not dashboard_path.exists():
            return HTMLResponse("<main><h1>SEO Insights Platform</h1><p>Dashboard is not installed.</p></main>")
        return HTMLResponse(dashboard_path.read_text(encoding="utf-8"))

    @app.get("/api/runs", dependencies=[auth])
    def list_runs(limit: int = Query(default=50, ge=1, le=200)) -> dict:
        return {"runs": [run.to_dict() for run in active_repository.list_runs(limit=limit)]}

    @app.post("/api/runs", status_code=201, dependencies=[auth])
    def create_run(payload: RunCreateRequest) -> dict:
        orchestrator = orchestrator_for(payload.approve_paid_enrichment)
        run = orchestrator.start(payload.url, mode=payload.mode, max_pages=payload.max_pages)
        market = attach_market_resolution(run)
        demand_conversion = attach_prospect_demand_conversion(run)
        agentic_evidence = attach_vertical_agentic_evidence(run)
        return {
            "run": run.to_dict(),
            "validation": orchestrator.validate(run.id),
            "market": market,
            "demand_conversion": demand_conversion,
            "agentic_evidence": agentic_evidence,
        }

    @app.post("/api/keyword-sets/csv-preview", dependencies=[auth])
    def preview_keyword_csv(payload: KeywordCsvRequest) -> dict:
        return keyword_service.preview_csv(payload.csv_text).to_dict()

    @app.post("/api/keyword-sets/csv-commit", status_code=201, dependencies=[auth])
    def commit_keyword_csv(payload: KeywordCsvRequest) -> dict:
        try:
            preview = keyword_service.preview_csv(payload.csv_text)
            normalized_domain = payload.normalized_domain.casefold().removeprefix("www.") if payload.normalized_domain else None
            keyword_set = keyword_service.commit(
                preview,
                vertical_id=payload.vertical_id,
                market=payload.market,
                market_slug=payload.market_slug,
                location_code=payload.location_code,
                version=payload.version,
                normalized_domain=normalized_domain,
                scope_type=payload.scope_type,
                scope_id=payload.scope_id,
                source_provenance=payload.source_provenance,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"keyword_set": keyword_set.to_dict(), "preview": preview.to_dict()}

    @app.get("/api/keyword-sets", dependencies=[auth])
    def list_keyword_sets(
        vertical_id: str | None = None,
        normalized_domain: str | None = None,
        state: str | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict:
        return {
            "keyword_sets": [
                item.to_dict() | {"keyword_set_key": item.keyword_set_key}
                for item in active_repository.list_keyword_sets(
                    vertical_id=vertical_id,
                    normalized_domain=normalized_domain,
                    state=state,
                    limit=limit,
                )
            ]
        }

    @app.get("/api/keyword-sets/{keyword_set_id}", dependencies=[auth])
    def get_keyword_set(keyword_set_id: str) -> dict:
        keyword_set = active_repository.get_keyword_set(keyword_set_id)
        if keyword_set is None:
            raise HTTPException(status_code=404, detail=f"keyword set {keyword_set_id} not found")
        return {
            "keyword_set": keyword_set.to_dict() | {"keyword_set_key": keyword_set.keyword_set_key},
            "pilot_preflight": (
                MarketEvidenceService.preflight(keyword_set, phase="pilot")
                if keyword_set.state == "approved"
                else None
            ),
        }

    @app.post("/api/keyword-sets/{keyword_set_id}/approve", dependencies=[auth])
    def approve_keyword_set(keyword_set_id: str, payload: KeywordReviewRequest) -> dict:
        keyword_set = active_repository.get_keyword_set(keyword_set_id)
        if keyword_set is None:
            raise HTTPException(status_code=404, detail=f"keyword set {keyword_set_id} not found")
        try:
            reviewed = keyword_service.review_targets(
                keyword_set,
                approved_keywords=payload.approved_keywords,
                rejected_keywords=payload.rejected_keywords,
            )
            approved = keyword_service.approve(reviewed, operator=payload.operator)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "keyword_set": approved.to_dict() | {"keyword_set_key": approved.keyword_set_key},
            "pilot_preflight": MarketEvidenceService.preflight(approved, phase="pilot"),
            "deep_preflight": MarketEvidenceService.preflight(approved, phase="deep"),
        }

    @app.post("/api/keyword-sets/{keyword_set_id}/supersede", dependencies=[auth])
    def supersede_keyword_set(keyword_set_id: str, payload: KeywordSupersedeRequest) -> dict:
        keyword_set = active_repository.get_keyword_set(keyword_set_id)
        if keyword_set is None:
            raise HTTPException(status_code=404, detail=f"keyword set {keyword_set_id} not found")
        try:
            superseded = keyword_service.supersede(keyword_set, successor_id=payload.successor_id)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"keyword_set": superseded.to_dict()}

    @app.get("/api/vertical-packs", dependencies=[auth])
    def api_vertical_packs() -> dict:
        packs = active_repository.list_vertical_packs() or list_vertical_packs()
        return {"vertical_packs": [pack.to_dict() | {"pack_id": pack.pack_id} for pack in packs]}

    @app.get("/api/vertical-agentic-packs/{version}", dependencies=[auth])
    def get_vertical_agentic_pack(version: str) -> dict:
        pack = active_repository.get_vertical_agentic_pack(version)
        if pack is None:
            raise HTTPException(
                status_code=404,
                detail=f"vertical agentic pack {version} not found",
            )
        return {"vertical_agentic_pack": pack.to_dict()}

    @app.post("/api/prospects/csv-preview", dependencies=[auth])
    def preview_prospect_csv(payload: ProspectCsvRequest) -> dict:
        try:
            preview = prospect_intake.preview_csv(payload.csv_text, payload.vertical_pack_version)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return preview.to_dict()

    @app.post("/api/prospects/csv-commit", status_code=201, dependencies=[auth])
    def commit_prospect_csv(payload: ProspectCsvRequest) -> dict:
        try:
            preview = prospect_intake.preview_csv(payload.csv_text, payload.vertical_pack_version)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        # Deduplicate against both rows in the upload (the intake service does
        # this) and already persisted prospects for this vertical/domain.
        existing_domains = {
            prospect.normalized_domain
            for prospect in active_repository.list_prospects(limit=10000)
            if prospect.vertical_pack_version == payload.vertical_pack_version
        }
        saved = []
        duplicate_issues = []
        for record in preview.records:
            if record.qualification_status not in {"qualified", "needs_review"}:
                continue
            if record.normalized_domain in existing_domains:
                duplicate_issues.append(
                    {
                        "row_number": record.metadata.get("source_row", 0),
                        "field": "website_url",
                        "message": "duplicate website already exists for this vertical; row skipped",
                        "value": record.normalized_domain,
                        "severity": "warning",
                    }
                )
                continue
            existing_domains.add(record.normalized_domain)
            saved.append(active_repository.save_prospect(record))
        return {
            "prospects": [record.to_dict() for record in saved],
            "issues": [issue.to_dict() for issue in preview.issues] + duplicate_issues,
            "saved_count": len(saved),
        }

    @app.get("/api/prospects", dependencies=[auth])
    def list_prospects(
        vertical_id: str | None = None,
        qualification_status: str | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict:
        return {
            "prospects": [
                prospect.to_dict()
                for prospect in active_repository.list_prospects(
                    vertical_id=vertical_id,
                    qualification_status=qualification_status,
                    limit=limit,
                )
            ]
        }

    @app.get("/api/prospects/{prospect_id}", dependencies=[auth])
    def get_prospect(prospect_id: str) -> dict:
        prospect = active_repository.get_prospect(prospect_id)
        if prospect is None:
            raise HTTPException(status_code=404, detail=f"prospect {prospect_id} not found")
        return {"prospect": prospect.to_dict()}

    @app.get("/api/prospects/{prospect_id}/qualification", dependencies=[auth])
    def get_prospect_qualification(prospect_id: str) -> dict:
        prospect = active_repository.get_prospect(prospect_id)
        if prospect is None:
            raise HTTPException(status_code=404, detail=f"prospect {prospect_id} not found")
        return {
            "prospect_id": prospect.id,
            "qualification_status": prospect.qualification_status,
            "rejection_reasons": list(prospect.rejection_reasons),
            "is_runnable": prospect.is_runnable,
        }

    @app.patch("/api/prospects/{prospect_id}/qualification", dependencies=[auth])
    def update_prospect_qualification(prospect_id: str, payload: QualificationUpdateRequest) -> dict:
        prospect = active_repository.get_prospect(prospect_id)
        if prospect is None:
            raise HTTPException(status_code=404, detail=f"prospect {prospect_id} not found")
        reasons = [reason.strip() for reason in payload.rejection_reasons if reason.strip()]
        if payload.qualification_status == "qualified" and reasons:
            raise HTTPException(status_code=422, detail="qualified prospects cannot have rejection reasons")
        if payload.qualification_status == "rejected" and not reasons:
            raise HTTPException(status_code=422, detail="rejected prospects require rejection reasons")
        if payload.qualification_status == "qualified":
            pack = active_repository.get_vertical_pack(prospect.vertical_pack_version)
            if pack is None:
                raise HTTPException(status_code=422, detail="prospect vertical pack is unavailable")
            _, qualification_issues = prospect_intake.qualify(prospect, pack)
            blocking = [issue.message for issue in qualification_issues if issue.severity == "error"]
            if blocking:
                raise HTTPException(
                    status_code=422,
                    detail=f"prospect is missing required runnable evidence: {', '.join(blocking)}",
                )
        metadata = {
            **prospect.metadata,
            "qualification_operator": payload.operator,
            "qualification_updated_at": utc_now_iso(),
        }
        updated = replace(
            prospect,
            qualification_status=payload.qualification_status,
            rejection_reasons=reasons,
            metadata=metadata,
            updated_at=utc_now_iso(),
        )
        return {"prospect": active_repository.save_prospect(updated).to_dict()}

    # POST is retained as a convenient form/API fallback for simple operator
    # clients that cannot issue PATCH; both routes have identical semantics.
    @app.post("/api/prospects/{prospect_id}/qualification", dependencies=[auth])
    def post_prospect_qualification(prospect_id: str, payload: QualificationUpdateRequest) -> dict:
        return update_prospect_qualification(prospect_id, payload)

    @app.post("/api/prospects/{prospect_id}/runs", status_code=201, dependencies=[auth])
    def create_prospect_run(prospect_id: str, payload: ProspectRunRequest) -> dict:
        prospect = active_repository.get_prospect(prospect_id)
        if prospect is None:
            raise HTTPException(status_code=404, detail=f"prospect {prospect_id} not found")
        if not prospect.is_runnable:
            raise HTTPException(status_code=409, detail="prospect is not qualified for a run")
        orchestrator = orchestrator_for(payload.approve_paid_enrichment)
        run = orchestrator.start(prospect.website_url, mode=payload.mode, max_pages=payload.max_pages)
        market = attach_market_resolution(run)
        demand_conversion = attach_prospect_demand_conversion(run, prospect)
        agentic_evidence = attach_vertical_agentic_evidence(run)
        return {
            "run": run.to_dict(),
            "validation": orchestrator.validate(run.id),
            "market": market,
            "demand_conversion": demand_conversion,
            "agentic_evidence": agentic_evidence,
        }

    @app.post("/api/prospects/{prospect_id}/keyword-sets/{keyword_set_id}/bind", dependencies=[auth])
    def bind_prospect_keyword_set(prospect_id: str, keyword_set_id: str) -> dict:
        prospect = active_repository.get_prospect(prospect_id)
        if prospect is None:
            raise HTTPException(status_code=404, detail=f"prospect {prospect_id} not found")
        keyword_set = active_repository.get_keyword_set(keyword_set_id)
        if keyword_set is None:
            raise HTTPException(status_code=404, detail=f"keyword set {keyword_set_id} not found")
        if keyword_set.state != "approved":
            raise HTTPException(status_code=422, detail="only approved keyword sets may be bound")
        if keyword_set.vertical_id != prospect.vertical_id:
            raise HTTPException(status_code=422, detail="keyword set vertical does not match prospect")
        try:
            binding = keyword_service.bind(
                keyword_set,
                normalized_domain=prospect.normalized_domain,
                prospect_id=prospect.id,
                operator="operator",
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        updated = replace(
            prospect,
            metadata={
                **prospect.metadata,
                "keyword_set_id": keyword_set.id,
                "keyword_set_version": keyword_set.keyword_set_key,
                "keyword_set_bound_at": utc_now_iso(),
            },
            updated_at=utc_now_iso(),
        )
        return {
            "prospect": active_repository.save_prospect(updated).to_dict(),
            "keyword_set_binding": binding.to_dict(),
        }

    @app.post("/api/demand-evidence/csv-preview", dependencies=[auth])
    def preview_demand_evidence(payload: DemandEvidenceCsvRequest) -> dict:
        keyword_set = active_repository.get_keyword_set(payload.keyword_set_id)
        if keyword_set is None:
            raise HTTPException(
                status_code=404,
                detail=f"keyword set {payload.keyword_set_id} not found",
            )
        try:
            demand_service.validate_binding(
                prospect_id=payload.prospect_id,
                keyword_set_id=payload.keyword_set_id,
                vertical_id=payload.vertical_id,
            )
            preview = demand_service.preview_csv(
                payload.csv_text,
                market=payload.market,
                source=payload.source,
                snapshot_period=payload.snapshot_period,
                location_code=payload.location_code,
                keyword_set=keyword_set,
                brand_terms=payload.brand_terms,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return preview.to_dict()

    @app.post("/api/demand-evidence/csv-commit", status_code=201, dependencies=[auth])
    def commit_demand_evidence(payload: DemandEvidenceCsvRequest) -> dict:
        keyword_set = active_repository.get_keyword_set(payload.keyword_set_id)
        if keyword_set is None:
            raise HTTPException(
                status_code=404,
                detail=f"keyword set {payload.keyword_set_id} not found",
            )
        try:
            preview = demand_service.preview_csv(
                payload.csv_text,
                market=payload.market,
                source=payload.source,
                snapshot_period=payload.snapshot_period,
                location_code=payload.location_code,
                keyword_set=keyword_set,
                brand_terms=payload.brand_terms,
            )
            evidence = demand_service.commit(
                preview,
                prospect_id=payload.prospect_id,
                keyword_set_id=payload.keyword_set_id,
                vertical_id=payload.vertical_id,
                market=payload.market,
                location_code=payload.location_code,
                source=payload.source,
                snapshot_period=payload.snapshot_period,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "demand_evidence": evidence.to_dict(),
            "preview": preview.to_dict(),
        }

    @app.get("/api/demand-evidence/{evidence_id}", dependencies=[auth])
    def get_demand_evidence(evidence_id: str) -> dict:
        evidence = active_repository.get_demand_evidence_set(evidence_id)
        if evidence is None:
            raise HTTPException(
                status_code=404,
                detail=f"demand evidence {evidence_id} not found",
            )
        return {"demand_evidence": evidence.to_dict()}

    @app.post("/api/demand-evidence/{evidence_id}/approve", dependencies=[auth])
    def approve_demand_evidence(
        evidence_id: str,
        payload: DemandApprovalRequest,
    ) -> dict:
        evidence = active_repository.get_demand_evidence_set(evidence_id)
        if evidence is None:
            raise HTTPException(
                status_code=404,
                detail=f"demand evidence {evidence_id} not found",
            )
        try:
            updates = {
                str(group["id"]): {
                    "status": "approved",
                    "reviewer": payload.operator,
                    "rationale": payload.rationale,
                }
                for group in evidence.groups
            }
            reviewed = demand_service.review_groups(
                evidence,
                reviewer=payload.operator,
                group_updates=updates,
            )
            approved = demand_service.approve(
                reviewed,
                operator=payload.operator,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "demand_evidence": approved.to_dict(),
            "draft_evidence_id": evidence.id,
            "review_evidence_id": reviewed.id,
        }

    @app.post(
        "/api/prospects/{prospect_id}/demand-evidence/{evidence_id}/bind",
        dependencies=[auth],
    )
    def validate_prospect_demand_binding(
        prospect_id: str,
        evidence_id: str,
    ) -> dict:
        evidence = active_repository.get_demand_evidence_set(evidence_id)
        if evidence is None:
            raise HTTPException(
                status_code=404,
                detail=f"demand evidence {evidence_id} not found",
            )
        if evidence.prospect_id != prospect_id:
            raise HTTPException(
                status_code=422,
                detail="demand evidence belongs to a different prospect",
            )
        try:
            demand_service.validate_binding(
                prospect_id=prospect_id,
                keyword_set_id=evidence.keyword_set_id,
                vertical_id=evidence.vertical_id,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "prospect_id": prospect_id,
            "demand_evidence_id": evidence.id,
            "keyword_set_id": evidence.keyword_set_id,
            "binding_status": "valid",
        }

    @app.post(
        "/api/prospects/{prospect_id}/economics",
        status_code=201,
        dependencies=[auth],
    )
    def create_business_economics(
        prospect_id: str,
        payload: EconomicsRequest,
    ) -> dict:
        prospect = active_repository.get_prospect(prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {prospect_id} not found",
            )
        if prospect.vertical_id != payload.vertical_id:
            raise HTTPException(
                status_code=422,
                detail="economics vertical does not match prospect",
            )
        prior = active_repository.list_business_economics_profiles(
            prospect_id=prospect_id,
            limit=1000,
        )
        latest = max(prior, key=lambda item: item.version) if prior else None
        pack = resolve_vertical_pack(prospect.vertical_pack_version)
        try:
            profile = BusinessEconomicsProfile(
                prospect_id=prospect_id,
                vertical_id=payload.vertical_id,
                revenue_model=payload.revenue_model,
                monthly_price=payload.monthly_price,
                currency=payload.currency,
                capacity_headroom=payload.capacity_headroom,
                field_provenance=dict(payload.field_provenance),
                version=(latest.version + 1) if latest else 1,
                state="approved" if payload.approve else "draft",
                gross_margin_mode=payload.gross_margin_mode,
                gross_margin_percent=payload.gross_margin_percent,
                retention_months=payload.retention_months,
                active_customer_count=payload.active_customer_count,
                desired_fill_months=payload.desired_fill_months,
                current_monthly_leads=payload.current_monthly_leads,
                current_monthly_signups=payload.current_monthly_signups,
                visit_to_signup_rate=payload.visit_to_signup_rate,
                signup_to_attended_rate=payload.signup_to_attended_rate,
                attended_to_customer_rate=payload.attended_to_customer_rate,
                funnel_labels=list(
                    pack.service_taxonomy.get("funnel_stages", [])
                ),
                approved_by=payload.operator if payload.approve else None,
                approved_at=utc_now_iso() if payload.approve else None,
                predecessor_id=latest.id if latest else None,
            )
            saved = active_repository.save_business_economics_profile(profile)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "economics_profile": saved.to_dict(),
            "capacity_ceiling": {
                "additional_customers": saved.capacity_headroom,
                "mrr": saved.capacity_mrr,
                "annual_run_rate": saved.capacity_annual_run_rate,
            },
        }

    @app.get("/api/prospects/{prospect_id}/economics", dependencies=[auth])
    def list_business_economics(
        prospect_id: str,
        state: str | None = None,
    ) -> dict:
        if active_repository.get_prospect(prospect_id) is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {prospect_id} not found",
            )
        profiles = active_repository.list_business_economics_profiles(
            prospect_id=prospect_id,
            state=state,
            limit=1000,
        )
        return {
            "economics_profiles": [profile.to_dict() for profile in profiles]
        }

    @app.post("/api/runs/recover-stale", dependencies=[auth])
    def recover_stale(payload: RecoveryRequest) -> dict:
        recovered = base_orchestrator.recover_stale_runs(
            worker_id=payload.worker_id,
            reason=payload.reason,
        )
        return {"recovered_run_ids": recovered, "count": len(recovered)}

    @app.get("/api/runs/{run_id}", dependencies=[auth])
    def get_run(run_id: str) -> dict:
        run = run_or_404(run_id)
        return {"run": run.to_dict(), "status": base_orchestrator.status(run_id)}

    @app.get("/api/runs/{run_id}/validation", dependencies=[auth])
    def validate_run(run_id: str) -> dict:
        run_or_404(run_id)
        return base_orchestrator.validate(run_id)

    @app.get("/api/runs/{run_id}/report", dependencies=[auth])
    def get_report(
        run_id: str,
        version: Literal[
            "v1",
            "v2",
            "ai-v1",
            "ai-v2",
            "ai-v3",
            "seo-health-v2",
            "conversion-v1",
            "market-v1",
            "v3",
            "opportunity-v1",
            "v4",
            "demand-conversion-v1",
            "v5",
            "decision-intelligence-v1",
            "v6",
        ] = Query(default="v1"),
        mode: Literal["prospect", "owner_verified"] | None = None,
    ) -> dict:
        run_or_404(run_id)
        if mode is not None and version not in {
            "demand-conversion-v1",
            "v5",
            "decision-intelligence-v1",
            "v6",
        }:
            raise HTTPException(
                status_code=422,
                detail=(
                    "mode applies only to demand-conversion-v1, v5, "
                    "decision-intelligence-v1, or v6"
                ),
            )
        if mode is not None and version in {
            "decision-intelligence-v1",
            "v6",
        }:
            try:
                reports = decision_intelligence_reporting.assemble(
                    run_id,
                    mode=mode,
                    for_export=False,
                )
            except ValueError as exc:
                raise value_error_422(exc) from exc
            report = reports[version]
        elif mode is not None:
            evidence = active_repository.list_demand_conversion_evidence(
                insight_run_id=run_id,
                mode=mode,
                state="approved",
            )
            if not evidence:
                raise HTTPException(
                    status_code=404,
                    detail=f"approved {mode} demand conversion evidence not found",
                )
            try:
                reports = demand_conversion_reporting.assemble(
                    evidence[0],
                    requested_mode=mode,
                    for_export=True,
                )
            except ValueError as exc:
                raise value_error_422(exc) from exc
            report = reports[version]
        elif version in {"decision-intelligence-v1", "v6"}:
            try:
                reports = decision_intelligence_reporting.assemble(
                    run_id,
                    mode="prospect",
                    for_export=False,
                )
                report = reports[version]
            except ValueError:
                report = active_repository.get_report(run_id, version)
        else:
            report = active_repository.get_report(run_id, version)
        if report is None:
            raise HTTPException(status_code=404, detail=f"report {version} not found")
        return report.to_dict()

    @app.get("/api/runs/{run_id}/ai-readiness", dependencies=[auth])
    def get_ai_readiness(run_id: str) -> dict:
        run_or_404(run_id)
        report = (
            active_repository.get_report(run_id, "ai-v3")
            or active_repository.get_report(run_id, "ai-v2")
            or active_repository.get_report(run_id, "ai-v1")
        )
        if report is None:
            raise HTTPException(status_code=404, detail="AI readiness report not found")
        return report.report_payload

    @app.get("/api/runs/{run_id}/product-strength", dependencies=[auth])
    def get_product_strength(run_id: str) -> dict:
        run_or_404(run_id)
        payload = product_strength_service.assemble(run_id)
        snapshots = active_repository.list_report_snapshots(
            run_id=run_id,
            report_contract=ProductStrengthService.CONTRACT_VERSION,
            limit=100,
        )
        bundles = active_repository.list_client_report_bundles(
            run_id=run_id,
            limit=100,
        )
        packs = active_repository.list_site_evidence_packs(run_id=run_id, limit=100)
        pack_ids = {pack.id for pack in packs}
        jobs = [
            job
            for job in active_repository.list_agentic_analysis_jobs(limit=1000)
            if job.evidence_pack_id in pack_ids
        ]
        comparisons = active_repository.list_report_comparison_snapshots(
            target_id=run_or_404(run_id).requested_domain,
            limit=100,
        )
        return {
            "product_strength": payload,
            "snapshot_history": [snapshot.to_dict() for snapshot in snapshots],
            "bundle_history": [bundle.to_dict() for bundle in bundles],
            "agentic_jobs": [job.to_dict() for job in jobs],
            "comparisons": [item.to_dict() for item in comparisons],
        }

    @app.post(
        "/api/runs/{run_id}/product-strength/snapshot",
        status_code=201,
        dependencies=[auth],
    )
    def create_product_strength_snapshot(run_id: str) -> dict:
        try:
            snapshot = product_strength_service.create_snapshot(run_id)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"report_snapshot": snapshot.to_dict()}

    @app.post(
        "/api/runs/{run_id}/agentic-analysis/preflight",
        dependencies=[auth],
    )
    def preflight_agentic_analysis(
        run_id: str,
        payload: AgenticAnalysisRequest,
    ) -> dict:
        try:
            pack = build_agentic_pack(run_id, payload)
            preflight = agentic_job_service.preflight(
                pack,
                analysis_mode=payload.analysis_mode,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"evidence_pack": pack.to_dict(), "preflight": preflight}

    @app.post(
        "/api/runs/{run_id}/agentic-analysis",
        status_code=202,
        dependencies=[auth],
    )
    def start_agentic_analysis(
        run_id: str,
        payload: AgenticAnalysisRequest,
    ) -> dict:
        try:
            pack = build_agentic_pack(run_id, payload)
            job = agentic_job_service.enqueue_job(
                pack,
                analysis_mode=payload.analysis_mode,
            )
        except AgenticJobPolicyError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "job": job.to_dict(),
            "evidence_pack": {
                "id": pack.id,
                "content_sha256": pack.content_sha256,
                "completeness_percent": pack.completeness_percent,
                "limitations": pack.limitations,
            },
        }

    @app.get("/api/agentic-analysis/jobs/{job_id}", dependencies=[auth])
    def get_agentic_job(job_id: str) -> dict:
        return agentic_job_payload(job_id)

    @app.post("/api/agentic-analysis/jobs/{job_id}/retry", dependencies=[auth])
    def retry_agentic_job(job_id: str) -> dict:
        try:
            job = agentic_job_service.retry_job(job_id)
        except AgenticJobPolicyError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"job": job.to_dict()}

    @app.post(
        "/api/agentic-assessments/{assessment_id}/review",
        status_code=201,
        dependencies=[auth],
    )
    def review_agentic_assessment(
        assessment_id: str,
        payload: AgenticReviewRequest,
    ) -> dict:
        assessment = active_repository.get_agentic_assessment_snapshot(assessment_id)
        if assessment is None:
            raise HTTPException(status_code=404, detail=f"assessment {assessment_id} not found")
        event = agentic_job_service.append_review_event(
            AgenticAssessmentReviewEvent(
                assessment_id=assessment_id,
                event_type=payload.event_type,
                operator=payload.operator,
                reason_code=payload.reason_code,
                notes=payload.notes,
                external_reference=payload.external_reference,
            )
        )
        return {
            "review_event": event.to_dict(),
            "review_state": agentic_job_service.review_state(assessment_id),
        }

    @app.post(
        "/api/agentic-assessments/{assessment_id}/gpt-review",
        status_code=202,
        dependencies=[auth],
    )
    def request_gpt_review(
        assessment_id: str,
        payload: AgenticReviewRequest,
    ) -> dict:
        if active_repository.get_agentic_assessment_snapshot(assessment_id) is None:
            raise HTTPException(status_code=404, detail=f"assessment {assessment_id} not found")
        event = agentic_job_service.append_review_event(
            AgenticAssessmentReviewEvent(
                assessment_id=assessment_id,
                event_type="gpt_review_requested",
                operator=payload.operator,
                reason_code=payload.reason_code,
                notes=payload.notes,
                external_reference=payload.external_reference,
            )
        )
        return {
            "review_event": event.to_dict(),
            "review_state": agentic_job_service.review_state(assessment_id),
            "execution_status": (
                "queued_for_explicit_codex_review"
                if base_config.agentic.allow_codex_review
                else "recorded_but_codex_review_disabled"
            ),
        }

    @app.post(
        "/api/runs/{run_id}/agentic-evidence/preflight",
        dependencies=[auth],
    )
    def preflight_vertical_agentic_evidence(
        run_id: str,
        payload: VerticalAgenticEvidenceRequest,
    ) -> dict:
        try:
            pack = build_agentic_pack(run_id, payload)
            preflight = vertical_agentic_evidence.preflight(
                run_id,
                evidence_pack=pack,
                execution_mode=payload.execution_mode,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "evidence_pack": {
                "id": pack.id,
                "content_sha256": pack.content_sha256,
                "completeness_percent": pack.completeness_percent,
                "limitations": pack.limitations,
            },
            "preflight": preflight,
        }

    @app.post(
        "/api/runs/{run_id}/agentic-evidence",
        status_code=202,
        dependencies=[auth],
    )
    def start_vertical_agentic_evidence(
        run_id: str,
        payload: VerticalAgenticEvidenceRequest,
    ) -> dict:
        try:
            pack = build_agentic_pack(run_id, payload)
            items = vertical_agentic_evidence.enqueue_defaults(
                pack,
                execution_mode=payload.execution_mode,
            )
            preflight = vertical_agentic_evidence.preflight(
                run_id,
                evidence_pack=pack,
                execution_mode=payload.execution_mode,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "preflight": preflight,
            "evidence_pack": {
                "id": pack.id,
                "content_sha256": pack.content_sha256,
            },
            "work_items": [item.to_dict() for item in items],
            "execution": "queued_for_durable_worker",
        }

    @app.get("/api/runs/{run_id}/agentic-evidence", dependencies=[auth])
    def get_vertical_agentic_evidence(
        run_id: str,
        mode: Literal["prospect", "owner_verified"] = "prospect",
    ) -> dict:
        run_or_404(run_id)
        try:
            evidence = vertical_agentic_evidence.evidence(run_id, mode=mode)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        evidence["playwright_health"] = screenshot_service.health()
        evidence["reports"] = {
            version: (
                active_repository.get_report(run_id, version).to_dict()
                if active_repository.get_report(run_id, version)
                else None
            )
            for version in ("decision-intelligence-v1", "v6")
        }
        return evidence

    @app.get("/api/agentic-work-items/{work_item_id}", dependencies=[auth])
    def get_vertical_agentic_work_item(work_item_id: str) -> dict:
        item = active_repository.get_agentic_work_item(work_item_id)
        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"agentic work item {work_item_id} not found",
            )
        return {
            "work_item": item.to_dict(),
            "tool_steps": [
                step.to_dict()
                for step in active_repository.list_agentic_tool_steps(
                    work_item_id=item.id,
                    limit=5000,
                )
            ],
        }

    @app.post(
        "/api/agentic-work-items/{work_item_id}/retry",
        status_code=202,
        dependencies=[auth],
    )
    def retry_vertical_agentic_work_item(work_item_id: str) -> dict:
        try:
            item = vertical_agentic_evidence.retry(work_item_id)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"work_item": item.to_dict(), "execution": "queued_for_durable_worker"}

    @app.post(
        "/api/agentic-evidence/{snapshot_id}/review",
        status_code=201,
        dependencies=[auth],
    )
    def review_vertical_agentic_snapshot(
        snapshot_id: str,
        payload: AgenticEvidenceReviewRequest,
    ) -> dict:
        agentic_snapshot_or_404(snapshot_id, payload.snapshot_type)
        event = active_repository.append_agentic_evidence_review_event(
            AgenticEvidenceReviewEvent(
                snapshot_id=snapshot_id,
                snapshot_type=payload.snapshot_type,
                event_type=payload.event_type,
                operator=payload.operator,
                reason_code=payload.reason_code,
                notes=payload.notes,
            )
        )
        return {
            "review_event": event.to_dict(),
            "review_state": active_repository.get_agentic_evidence_review_state(
                snapshot_id
            ),
        }

    @app.post(
        "/api/runs/{run_id}/owner-agentic-analysis",
        status_code=202,
        dependencies=[auth],
    )
    def start_owner_agentic_analysis(
        run_id: str,
        payload: OwnerAgenticAnalysisRequest,
    ) -> dict:
        run_or_404(run_id)
        prospect = active_repository.get_prospect(payload.prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {payload.prospect_id} not found",
            )
        try:
            owner_preflight = owner_agentic_analysis.preflight(
                prospect_id=payload.prospect_id,
                vertical_id=prospect.vertical_id,
                approved_snapshot_ids=payload.approved_snapshot_ids,
                consent_id=payload.consent_id,
            )
            pack = build_agentic_pack(run_id, payload)
            item = vertical_agentic_evidence.enqueue_optional(
                pack,
                work_kind="owner_diagnostic",
                source_snapshot_ids=payload.approved_snapshot_ids,
                execution_mode=payload.execution_mode,
                consent_id=payload.consent_id,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "preflight": owner_preflight,
            "work_item": item.to_dict(),
            "execution": "queued_for_durable_worker",
        }

    @app.post(
        "/api/runs/{run_id}/remediation-blueprints",
        status_code=202,
        dependencies=[auth],
    )
    def start_remediation_blueprint(
        run_id: str,
        payload: RemediationBlueprintRequest,
    ) -> dict:
        try:
            pack = build_agentic_pack(run_id, payload)
            item = vertical_agentic_evidence.enqueue_optional(
                pack,
                work_kind="remediation_blueprint",
                source_snapshot_ids=payload.source_snapshot_ids,
                execution_mode=payload.execution_mode,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "work_item": item.to_dict(),
            "execution": "queued_for_durable_worker",
        }

    @app.post(
        "/api/remediation-blueprints/{blueprint_id}/review",
        status_code=201,
        dependencies=[auth],
    )
    def review_remediation_blueprint(
        blueprint_id: str,
        payload: AgenticEvidenceReviewRequest,
    ) -> dict:
        if payload.snapshot_type != "remediation_blueprint":
            raise HTTPException(
                status_code=422,
                detail="blueprint review requires remediation_blueprint snapshot_type",
            )
        return review_vertical_agentic_snapshot(blueprint_id, payload)

    @app.post(
        "/api/runs/{run_id}/agentic-evidence/reports",
        status_code=201,
        dependencies=[auth],
    )
    def create_decision_intelligence_reports(
        run_id: str,
        mode: Literal["prospect", "owner_verified"] = "prospect",
        for_export: bool = False,
    ) -> dict:
        try:
            reports = decision_intelligence_reporting.assemble(
                run_id,
                mode=mode,
                for_export=for_export,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"reports": {key: value.to_dict() for key, value in reports.items()}}

    @app.post(
        "/api/runs/{run_id}/client-bundles",
        status_code=201,
        dependencies=[auth],
    )
    def create_client_bundle(run_id: str, payload: ClientBundleRequest) -> dict:
        run_or_404(run_id)
        try:
            snapshot = (
                active_repository.get_report_snapshot(payload.report_snapshot_id)
                if payload.report_snapshot_id
                else product_strength_service.create_snapshot(run_id)
            )
            if snapshot is None or snapshot.run_id != run_id:
                raise ValueError("report snapshot does not belong to this run")
            assessment = None
            if payload.assessment_id:
                assessment = active_repository.get_agentic_assessment_snapshot(
                    payload.assessment_id
                )
                if assessment is None:
                    raise ValueError("agentic assessment does not exist")
                pack = active_repository.get_site_evidence_pack(
                    assessment.evidence_pack_id
                )
                if pack is None or pack.run_id != run_id:
                    raise ValueError("agentic assessment does not belong to this run")
                if agentic_job_service.review_state(assessment.id) != "approved":
                    raise ValueError(
                        "client bundles require operator approval of the selected assessment"
                    )
            bundle = client_report_service.render(
                snapshot,
                assessment=assessment,
            )
            validation = client_report_service.validate(bundle)
        except (ValueError, FileNotFoundError) as exc:
            raise value_error_422(exc) from exc
        return {
            "client_report_bundle": bundle.to_dict(),
            "validation": validation,
        }

    @app.get("/api/runs/{run_id}/client-bundles", dependencies=[auth])
    def list_client_bundles(run_id: str) -> dict:
        run_or_404(run_id)
        return {
            "client_report_bundles": [
                bundle.to_dict()
                for bundle in active_repository.list_client_report_bundles(
                    run_id=run_id,
                    limit=1000,
                )
            ]
        }

    @app.get(
        "/api/client-bundles/{bundle_id}/download/{file_kind}",
        dependencies=[auth],
    )
    def download_client_bundle(
        bundle_id: str,
        file_kind: Literal["html", "pdf", "json", "manifest"],
    ):
        bundle = active_repository.get_client_report_bundle(bundle_id)
        if bundle is None:
            raise HTTPException(status_code=404, detail=f"client bundle {bundle_id} not found")
        try:
            client_report_service.validate(bundle)
        except (ValueError, FileNotFoundError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        relative = {
            "html": "report.html",
            "pdf": "report.pdf",
            "json": "data/report.json",
            "manifest": "manifest.json",
        }[file_kind]
        path = root / "bundles" / bundle.id / Path(*relative.split("/"))
        media_type = {
            "html": "text/html",
            "pdf": "application/pdf",
            "json": "application/json",
            "manifest": "application/json",
        }[file_kind]
        return FileResponse(
            path,
            media_type=media_type,
            filename=f"{bundle.id}-{Path(relative).name}",
        )

    @app.post("/api/owned-measurements/csv-preview", dependencies=[auth])
    def preview_owned_measurement(payload: OwnedMeasurementCsvRequest) -> dict:
        try:
            preview = owned_measurement_service.preview_csv(
                payload.csv_text,
                prospect_id=payload.prospect_id,
                vertical_id=payload.vertical_id,
                source=payload.source,
                context=payload.context,
                artifact_ref=payload.artifact_ref,
                period_start=payload.period_start,
                period_end=payload.period_end,
                owner_verified=payload.owner_verified,
                require_owner_consent=payload.owner_verified,
                owner_consent=payload.owner_consent,
                data_freshness=payload.data_freshness,
                event_map_id=payload.event_map_id,
                event_map_version=payload.event_map_version,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return preview.to_dict()

    @app.post(
        "/api/owned-measurements/csv-commit",
        status_code=201,
        dependencies=[auth],
    )
    def commit_owned_measurement(payload: OwnedMeasurementCsvRequest) -> dict:
        try:
            preview = owned_measurement_service.preview_csv(
                payload.csv_text,
                prospect_id=payload.prospect_id,
                vertical_id=payload.vertical_id,
                source=payload.source,
                context=payload.context,
                artifact_ref=payload.artifact_ref,
                period_start=payload.period_start,
                period_end=payload.period_end,
                owner_verified=payload.owner_verified,
                require_owner_consent=payload.owner_verified,
                owner_consent=payload.owner_consent,
                data_freshness=payload.data_freshness,
                event_map_id=payload.event_map_id,
                event_map_version=payload.event_map_version,
            )
            snapshots = owned_measurement_service.commit(preview)
            baseline = owned_measurement_service.derive_funnel_baseline(snapshots)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "owned_measurements": [snapshot.to_dict() for snapshot in snapshots],
            "baseline": baseline,
        }

    @app.get("/api/owned-measurements", dependencies=[auth])
    def list_owned_measurements(
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        source: str | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict:
        return {
            "owned_measurements": [
                snapshot.to_dict()
                for snapshot in active_repository.list_owned_measurement_snapshots(
                    prospect_id=prospect_id,
                    vertical_id=vertical_id,
                    source=source,
                    limit=limit,
                )
            ]
        }

    @app.post("/api/demand-trends/csv-preview", dependencies=[auth])
    def preview_demand_trends(payload: DemandTrendCsvRequest) -> dict:
        prospect = active_repository.get_prospect(payload.prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {payload.prospect_id} not found",
            )
        if prospect.vertical_id != payload.vertical_id:
            raise HTTPException(
                status_code=422,
                detail="demand trend vertical does not match prospect",
            )
        keyword_set = (
            active_repository.get_keyword_set(payload.keyword_set_id)
            if payload.keyword_set_id
            else None
        )
        if payload.keyword_set_id and keyword_set is None:
            raise HTTPException(
                status_code=404,
                detail=f"keyword set {payload.keyword_set_id} not found",
            )
        try:
            preview = demand_trend_service.preview_csv(
                payload.csv_text,
                source=payload.source,
                prospect_id=payload.prospect_id,
                vertical_id=payload.vertical_id,
                market=payload.market,
                period_start=payload.period_start,
                period_end=payload.period_end,
                location_code=payload.location_code,
                keyword_set=keyword_set,
                context=payload.context,
                artifact_ref=payload.artifact_ref,
                brand_terms=payload.brand_terms,
                aggregation_rule=payload.aggregation_rule,
                operator_approved=payload.operator_approved,
                operator=payload.operator,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return preview.to_dict()

    @app.post(
        "/api/demand-trends/csv-commit",
        status_code=201,
        dependencies=[auth],
    )
    def commit_demand_trends(payload: DemandTrendCsvRequest) -> dict:
        prospect = active_repository.get_prospect(payload.prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {payload.prospect_id} not found",
            )
        if prospect.vertical_id != payload.vertical_id:
            raise HTTPException(
                status_code=422,
                detail="demand trend vertical does not match prospect",
            )
        keyword_set = (
            active_repository.get_keyword_set(payload.keyword_set_id)
            if payload.keyword_set_id
            else None
        )
        if payload.keyword_set_id and keyword_set is None:
            raise HTTPException(
                status_code=404,
                detail=f"keyword set {payload.keyword_set_id} not found",
            )
        try:
            preview = demand_trend_service.preview_csv(
                payload.csv_text,
                source=payload.source,
                prospect_id=payload.prospect_id,
                vertical_id=payload.vertical_id,
                market=payload.market,
                period_start=payload.period_start,
                period_end=payload.period_end,
                location_code=payload.location_code,
                keyword_set=keyword_set,
                context=payload.context,
                artifact_ref=payload.artifact_ref,
                brand_terms=payload.brand_terms,
                aggregation_rule=payload.aggregation_rule,
                operator_approved=payload.operator_approved,
                operator=payload.operator,
            )
            snapshot = demand_trend_service.commit(preview)
            persisted = active_repository.save_demand_trend_snapshot(snapshot)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "demand_trend": persisted.to_dict(),
            "preview": preview.to_dict(),
        }

    @app.post(
        "/api/demand-trends/{snapshot_id}/approve",
        status_code=201,
        dependencies=[auth],
    )
    def approve_demand_trend(
        snapshot_id: str,
        payload: DemandConversionApprovalRequest,
    ) -> dict:
        snapshot = active_repository.get_demand_trend_snapshot(snapshot_id)
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=f"demand trend {snapshot_id} not found",
            )
        try:
            approved = demand_trend_service.approve(
                snapshot,
                operator=payload.operator,
            )
            persisted = active_repository.save_demand_trend_snapshot(approved)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "demand_trend": persisted.to_dict(),
            "predecessor_id": snapshot.id,
        }

    @app.get("/api/demand-trends", dependencies=[auth])
    def list_demand_trends(
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        market: str | None = None,
        source: str | None = None,
        state: str | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict:
        return {
            "demand_trends": [
                snapshot.to_dict()
                for snapshot in active_repository.list_demand_trend_snapshots(
                    prospect_id=prospect_id,
                    vertical_id=vertical_id,
                    market=market,
                    source=source,
                    state=state,
                    limit=limit,
                )
            ]
        }

    @app.post(
        "/api/conversion-event-maps",
        status_code=201,
        dependencies=[auth],
    )
    def create_conversion_event_map(
        payload: ConversionEventMapRequest,
    ) -> dict:
        prospect = active_repository.get_prospect(payload.prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {payload.prospect_id} not found",
            )
        if prospect.vertical_id != payload.vertical_id:
            raise HTTPException(
                status_code=422,
                detail="event map vertical does not match prospect",
            )
        source_snapshots = [
            active_repository.get_owned_measurement_snapshot(snapshot_id)
            for snapshot_id in payload.source_snapshot_ids
        ]
        if any(snapshot is None for snapshot in source_snapshots):
            raise HTTPException(
                status_code=404,
                detail="one or more owner measurement snapshots were not found",
            )
        if any(
            snapshot.prospect_id != payload.prospect_id
            or snapshot.vertical_id != payload.vertical_id
            for snapshot in source_snapshots
            if snapshot is not None
        ):
            raise HTTPException(
                status_code=422,
                detail="event map source context does not match prospect",
            )
        try:
            event_map = ConversionEventMap(
                prospect_id=payload.prospect_id,
                vertical_id=payload.vertical_id,
                mappings={
                    str(stage): list(events)
                    for stage, events in payload.mappings.items()
                },
                source_snapshot_ids=payload.source_snapshot_ids,
                state="approved" if payload.approve else "draft",
                approved_by=payload.operator if payload.approve else None,
                approved_at=utc_now_iso() if payload.approve else None,
            )
            persisted = active_repository.save_conversion_event_map(event_map)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"conversion_event_map": persisted.to_dict()}

    @app.post(
        "/api/conversion-event-maps/{event_map_id}/approve",
        status_code=201,
        dependencies=[auth],
    )
    def approve_conversion_event_map(
        event_map_id: str,
        payload: DemandConversionApprovalRequest,
    ) -> dict:
        event_map = active_repository.get_conversion_event_map(event_map_id)
        if event_map is None:
            raise HTTPException(
                status_code=404,
                detail=f"conversion event map {event_map_id} not found",
            )
        if event_map.state != "draft":
            raise HTTPException(
                status_code=422,
                detail="only draft event maps may be approved",
            )
        approved = replace(
            event_map,
            id=new_id(),
            version=event_map.version + 1,
            state="approved",
            approved_by=payload.operator,
            approved_at=utc_now_iso(),
            predecessor_id=event_map.id,
            created_at=utc_now_iso(),
        )
        try:
            persisted = active_repository.save_conversion_event_map(approved)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "conversion_event_map": persisted.to_dict(),
            "predecessor_id": event_map.id,
        }

    @app.get(
        "/api/prospects/{prospect_id}/evidence-readiness",
        dependencies=[auth],
    )
    def get_evidence_readiness(prospect_id: str) -> dict:
        prospect = active_repository.get_prospect(prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {prospect_id} not found",
            )
        demand = active_repository.list_demand_evidence_sets(
            prospect_id=prospect_id,
            state="approved",
        )
        economics = active_repository.list_business_economics_profiles(
            prospect_id=prospect_id,
            state="approved",
        )
        owner = active_repository.list_owned_measurement_snapshots(
            prospect_id=prospect_id,
        )
        trends = active_repository.list_demand_trend_snapshots(
            prospect_id=prospect_id,
            state="approved",
        )
        event_maps = active_repository.list_conversion_event_maps(
            prospect_id=prospect_id,
            state="approved",
        )
        return {
            "prospect_id": prospect_id,
            "prospect_mode": {
                "ready": True,
                "approved_demand": bool(demand),
                "approved_economics": bool(economics),
                "approved_trends": bool(trends),
            },
            "owner_verified_mode": {
                "ready": bool(owner),
                "owner_snapshot_count": len(owner),
                "sources": sorted({snapshot.source for snapshot in owner}),
                "approved_event_map": bool(event_maps),
            },
            "latest": {
                "demand_evidence_id": demand[0].id if demand else None,
                "economics_profile_id": economics[0].id if economics else None,
                "trend_snapshot_ids": [snapshot.id for snapshot in trends],
                "event_map_id": event_maps[0].id if event_maps else None,
            },
        }

    @app.post(
        "/api/runs/{run_id}/demand-conversion",
        status_code=201,
        dependencies=[auth],
    )
    def build_demand_conversion(
        run_id: str,
        payload: DemandConversionRequest,
    ) -> dict:
        run = run_or_404(run_id)
        prospect = active_repository.get_prospect(payload.prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {payload.prospect_id} not found",
            )
        if (
            run.requested_domain.casefold().removeprefix("www.")
            != prospect.normalized_domain.casefold().removeprefix("www.")
        ):
            raise HTTPException(
                status_code=422,
                detail="demand conversion prospect domain does not match run",
            )
        demand = (
            active_repository.get_demand_evidence_set(
                payload.demand_evidence_set_id
            )
            if payload.demand_evidence_set_id
            else None
        )
        economics = (
            active_repository.get_business_economics_profile(
                payload.economics_profile_id
            )
            if payload.economics_profile_id
            else None
        )
        if payload.demand_evidence_set_id and demand is None:
            raise HTTPException(
                status_code=404,
                detail="demand evidence not found",
            )
        if payload.economics_profile_id and economics is None:
            raise HTTPException(
                status_code=404,
                detail="economics profile not found",
            )
        owner_snapshots = [
            active_repository.get_owned_measurement_snapshot(snapshot_id)
            for snapshot_id in payload.owner_snapshot_ids
        ]
        trend_snapshots = [
            active_repository.get_demand_trend_snapshot(snapshot_id)
            for snapshot_id in payload.trend_snapshot_ids
        ]
        if any(snapshot is None for snapshot in owner_snapshots):
            raise HTTPException(
                status_code=404,
                detail="one or more owner measurements were not found",
            )
        if any(snapshot is None for snapshot in trend_snapshots):
            raise HTTPException(
                status_code=404,
                detail="one or more demand trends were not found",
            )
        event_map = (
            active_repository.get_conversion_event_map(payload.event_map_id)
            if payload.event_map_id
            else None
        )
        if payload.event_map_id and event_map is None:
            raise HTTPException(
                status_code=404,
                detail="conversion event map not found",
            )
        market_report = active_repository.get_report(run_id, "market-v1")
        public_rankings = (
            market_report.report_payload.get("organic_rankings", [])
            if market_report is not None
            else []
        )
        try:
            alignment = demand_conversion_search.align(
                prospect_id=payload.prospect_id,
                vertical_id=prospect.vertical_id,
                market=payload.market,
                demand=demand,
                owner_snapshots=[
                    snapshot
                    for snapshot in owner_snapshots
                    if snapshot is not None
                ],
                public_rankings=public_rankings,
            )
            public_sources = list(payload.public_sources)
            v2 = active_repository.get_report(run_id, "v2")
            if v2 is not None:
                public_sources.append(
                    {
                        "source_name": "bounded_crawl_report",
                        "source_class": "public_observed",
                        "hierarchy_level": 4,
                        "provenance_label": "observed",
                        "source_sha256": canonical_sha256(v2.report_payload),
                        "artifact_ref": f"runs/{run_id}/reports/v2.json",
                        "snapshot_date": run.updated_at[:10],
                    }
                )
            evidence = demand_conversion_service.build(
                insight_run_id=run_id,
                prospect_id=payload.prospect_id,
                vertical_id=prospect.vertical_id,
                market=payload.market,
                mode=payload.mode,
                demand=demand,
                economics=economics,
                owner_snapshots=[
                    snapshot
                    for snapshot in owner_snapshots
                    if snapshot is not None
                ],
                trend_snapshots=[
                    snapshot
                    for snapshot in trend_snapshots
                    if snapshot is not None
                ],
                event_map=event_map,
                search_alignment=alignment,
                public_sources=public_sources,
                assumptions=payload.assumptions,
                target_id=run.seo_target_id,
                normalized_domain=run.requested_domain,
                attempt_id=run.attempt_id,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "demand_conversion": evidence.to_dict(),
            "search_alignment": alignment,
        }

    @app.post(
        "/api/demand-conversion/{evidence_id}/approve",
        status_code=201,
        dependencies=[auth],
    )
    def approve_demand_conversion(
        evidence_id: str,
        payload: DemandConversionApprovalRequest,
    ) -> dict:
        try:
            approved = demand_conversion_service.approve(
                evidence_id,
                operator=payload.operator,
            )
            validation = demand_conversion_validator.validate(
                approved,
                requested_mode=approved.mode,
                for_export=True,
            )
            reports = demand_conversion_reporting.assemble(
                approved,
                requested_mode=approved.mode,
                for_export=True,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "demand_conversion": approved.to_dict(),
            "validation": validation,
            "reports": {
                version: report.to_dict()
                for version, report in reports.items()
            },
            "predecessor_id": evidence_id,
        }

    @app.get("/api/runs/{run_id}/demand-conversion", dependencies=[auth])
    def get_run_demand_conversion(
        run_id: str,
        mode: Literal["prospect", "owner_verified"] | None = None,
    ) -> dict:
        run_or_404(run_id)
        records = active_repository.list_demand_conversion_evidence(
            insight_run_id=run_id,
            mode=mode,
        )
        selected = records[0] if records else None
        reports = {}
        if selected is not None and selected.state == "approved":
            try:
                reports = demand_conversion_reporting.assemble(
                    selected,
                    requested_mode=selected.mode,
                    for_export=True,
                )
            except ValueError as exc:
                raise value_error_422(exc) from exc
        report = reports.get("demand-conversion-v1")
        combined = reports.get("v5")
        return {
            "demand_conversion": selected.to_dict() if selected else None,
            "history": [record.to_dict() for record in records],
            "report": report.to_dict() if report else None,
            "combined_report": combined.to_dict() if combined else None,
        }

    @app.post("/api/ai-visibility/preflight", dependencies=[auth])
    def preflight_ai_visibility(payload: AIVisibilityPreflightRequest) -> dict:
        try:
            topic_set = PromptTopicSet(**payload.prompt_topic_set)
        except (TypeError, ValueError) as exc:
            raise value_error_422(exc) from exc
        return ai_visibility_service.preflight(
            topic_set,
            provider_configured=base_config.dataforseo.configured,
            operator_approved=payload.approve_paid_enrichment,
            allow_paid_api_calls=payload.approve_paid_enrichment,
            context=payload.context,
            call_cap=payload.call_cap,
        )

    @app.get("/api/runs/{run_id}/search-visibility", dependencies=[auth])
    def get_search_visibility(run_id: str) -> dict:
        run_or_404(run_id)
        report = active_repository.get_report(run_id, "v2")
        if report is None:
            raise HTTPException(status_code=404, detail="v2 report not found")
        payload = report.report_payload.get("search_visibility")
        if not isinstance(payload, dict):
            raise HTTPException(status_code=404, detail="search visibility view not found")
        return payload

    @app.get("/api/runs/{run_id}/market-evidence", dependencies=[auth])
    def list_run_market_evidence(run_id: str) -> dict:
        run_or_404(run_id)
        records = active_repository.list_market_evidence_runs(insight_run_id=run_id)
        return {"market_evidence_runs": [record.to_dict() for record in records]}

    @app.post("/api/runs/{run_id}/market-evidence/pilot", status_code=201, dependencies=[auth])
    def start_market_pilot(run_id: str, payload: MarketPilotRequest) -> dict:
        run_or_404(run_id)
        require_paid_market_approval(payload.approve_paid_enrichment)
        try:
            market_run = market_service_for(run_id).start_pilot(
                insight_run_id=run_id,
                keyword_set_id=payload.keyword_set_id,
                target_entity_name=payload.target_entity_name,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"market_evidence_run": market_run.to_dict()}

    @app.get("/api/market-evidence/{market_run_id}", dependencies=[auth])
    def get_market_evidence(market_run_id: str) -> dict:
        market_run = active_repository.get_market_evidence_run(market_run_id)
        if market_run is None:
            raise HTTPException(status_code=404, detail=f"market evidence run {market_run_id} not found")
        return {"market_evidence_run": market_run.to_dict()}

    @app.post("/api/market-evidence/{market_run_id}/competitors/approve", dependencies=[auth])
    def approve_market_competitors(market_run_id: str, payload: CompetitorApprovalRequest) -> dict:
        market_run = active_repository.get_market_evidence_run(market_run_id)
        if market_run is None:
            raise HTTPException(status_code=404, detail=f"market evidence run {market_run_id} not found")
        try:
            approved = market_service_for(market_run.insight_run_id).approve_competitors(
                market_run_id,
                candidate_ids=payload.candidate_ids,
                operator=payload.operator,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"market_evidence_run": approved.to_dict()}

    @app.post("/api/market-evidence/{market_run_id}/enrich", dependencies=[auth])
    def enrich_market_competitors(market_run_id: str, payload: CompetitorEnrichmentRequest) -> dict:
        market_run = active_repository.get_market_evidence_run(market_run_id)
        if market_run is None:
            raise HTTPException(status_code=404, detail=f"market evidence run {market_run_id} not found")
        if payload.approve_paid_enrichment:
            require_paid_market_approval(True)
            authority_factory = lambda: DataForSEOClient(
                base_config.dataforseo,
                artifact_dir=root / "runs" / market_run.insight_run_id / "market-provider",
            )
        else:
            authority_factory = None
        try:
            enriched = CompetitorEvidenceService(
                active_repository,
                authority_provider_factory=authority_factory,
                screenshot_service=screenshot_service,
            ).enrich(
                market_run_id,
                capture_screenshots=payload.capture_screenshots,
                target_program_url=payload.target_program_url,
            )
            reports = market_reporting.assemble(enriched.id)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "market_evidence_run": enriched.to_dict(),
            "reports": {name: report.to_dict() for name, report in reports.items()},
        }

    @app.post("/api/market-evidence/{market_run_id}/deep-run", dependencies=[auth])
    def deepen_market_evidence(market_run_id: str, payload: MarketDeepRequest) -> dict:
        market_run = active_repository.get_market_evidence_run(market_run_id)
        if market_run is None:
            raise HTTPException(status_code=404, detail=f"market evidence run {market_run_id} not found")
        require_paid_market_approval(payload.approve_paid_enrichment)
        try:
            deep = market_service_for(market_run.insight_run_id).deepen(market_run_id)
            reports = market_reporting.assemble(deep.id) if deep.state in {"partial", "complete"} else {}
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "market_evidence_run": deep.to_dict(),
            "superseded_market_run_id": market_run_id,
            "reports": {name: report.to_dict() for name, report in reports.items()},
        }

    @app.post("/api/market-evidence/{market_run_id}/resume", dependencies=[auth])
    def resume_market_evidence(
        market_run_id: str,
        payload: MarketResumeRequest,
    ) -> dict:
        market_run = active_repository.get_market_evidence_run(market_run_id)
        if market_run is None:
            raise HTTPException(
                status_code=404,
                detail=f"market evidence run {market_run_id} not found",
            )
        require_paid_market_approval(payload.approve_paid_enrichment)
        try:
            resumed = market_service_for(
                market_run.insight_run_id
            ).resume_unresolved(
                market_run_id,
                account_recovered=payload.account_recovered,
            )
            reports = (
                market_reporting.assemble(resumed.id)
                if resumed.state in {"partial", "complete"}
                else {}
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "market_evidence_run": resumed.to_dict(),
            "predecessor_market_run_id": market_run.id,
            "reports": {
                name: report.to_dict()
                for name, report in reports.items()
            },
        }

    @app.post("/api/market-evidence/{market_run_id}/reports", dependencies=[auth])
    def assemble_market_reports(market_run_id: str) -> dict:
        try:
            reports = market_reporting.assemble(market_run_id)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"reports": {name: report.to_dict() for name, report in reports.items()}}

    @app.get("/api/runs/{run_id}/offsite-authority", dependencies=[auth])
    def get_offsite_authority(run_id: str) -> dict:
        run_or_404(run_id)
        report = active_repository.get_report(run_id, "v2")
        if report is None:
            raise HTTPException(status_code=404, detail="v2 report not found")
        payload = report.report_payload.get("offsite_authority")
        if not isinstance(payload, dict):
            raise HTTPException(status_code=404, detail="off-site authority view not found")
        return payload

    @app.post(
        "/api/runs/{run_id}/opportunity-scenarios",
        status_code=201,
        dependencies=[auth],
    )
    def create_opportunity_scenario(
        run_id: str,
        payload: OpportunityScenarioRequest,
    ) -> dict:
        run = run_or_404(run_id)
        prospect = active_repository.get_prospect(payload.prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {payload.prospect_id} not found",
            )
        if (
            run.requested_domain.casefold().removeprefix("www.")
            != prospect.normalized_domain.casefold().removeprefix("www.")
        ):
            raise HTTPException(
                status_code=422,
                detail="opportunity prospect domain does not match insight run",
            )
        economics = active_repository.get_business_economics_profile(
            payload.economics_profile_id
        )
        if economics is None:
            raise HTTPException(
                status_code=404,
                detail=f"economics profile {payload.economics_profile_id} not found",
            )
        demand = (
            active_repository.get_demand_evidence_set(
                payload.demand_evidence_set_id
            )
            if payload.demand_evidence_set_id
            else None
        )
        if payload.demand_evidence_set_id and demand is None:
            raise HTTPException(
                status_code=404,
                detail=f"demand evidence {payload.demand_evidence_set_id} not found",
            )
        try:
            scenario = opportunity_model.create_scenario(
                insight_run_id=run_id,
                prospect_id=payload.prospect_id,
                economics=economics,
                demand=demand,
                assumptions=payload.assumptions,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"opportunity_scenario": scenario.to_dict()}

    @app.get("/api/opportunity-scenarios/{scenario_id}", dependencies=[auth])
    def get_opportunity_scenario(scenario_id: str) -> dict:
        scenario = active_repository.get_opportunity_scenario(scenario_id)
        if scenario is None:
            raise HTTPException(
                status_code=404,
                detail=f"opportunity scenario {scenario_id} not found",
            )
        return {"opportunity_scenario": scenario.to_dict()}

    @app.post(
        "/api/opportunity-scenarios/{scenario_id}/approve",
        dependencies=[auth],
    )
    def approve_opportunity_scenario(
        scenario_id: str,
        payload: OpportunityApprovalRequest,
    ) -> dict:
        try:
            approved = opportunity_model.approve_scenario(
                scenario_id,
                operator=payload.operator,
            )
            reports = opportunity_reporting.assemble(approved.id)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "opportunity_scenario": approved.to_dict(),
            "draft_scenario_id": scenario_id,
            "reports": {
                name: report.to_dict()
                for name, report in reports.items()
            },
        }

    @app.post("/api/calibration/csv-preview", dependencies=[auth])
    def preview_calibration(payload: CalibrationCsvRequest) -> dict:
        prospect = active_repository.get_prospect(payload.prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {payload.prospect_id} not found",
            )
        if prospect.vertical_id != payload.vertical_id:
            raise HTTPException(
                status_code=422,
                detail="calibration vertical does not match prospect",
            )
        try:
            preview = calibration_service.preview_csv(
                payload.csv_text,
                prospect_id=payload.prospect_id,
                vertical_id=payload.vertical_id,
                market=payload.market,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return preview.to_dict()

    @app.post(
        "/api/calibration/csv-commit",
        status_code=201,
        dependencies=[auth],
    )
    def commit_calibration(payload: CalibrationCsvRequest) -> dict:
        prospect = active_repository.get_prospect(payload.prospect_id)
        if prospect is None:
            raise HTTPException(
                status_code=404,
                detail=f"prospect {payload.prospect_id} not found",
            )
        if prospect.vertical_id != payload.vertical_id:
            raise HTTPException(
                status_code=422,
                detail="calibration vertical does not match prospect",
            )
        try:
            preview = calibration_service.preview_csv(
                payload.csv_text,
                prospect_id=payload.prospect_id,
                vertical_id=payload.vertical_id,
                market=payload.market,
            )
            records = calibration_service.commit(preview)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {
            "calibration_records": [
                record.to_dict()
                for record in records
            ],
            "preview": preview.to_dict(),
        }

    @app.get("/api/runs/{run_id}/opportunity", dependencies=[auth])
    def get_run_opportunity(run_id: str) -> dict:
        run_or_404(run_id)
        opportunity = active_repository.get_report(run_id, "opportunity-v1")
        combined = active_repository.get_report(run_id, "v4")
        if opportunity is None:
            raise HTTPException(
                status_code=404,
                detail="opportunity report not found",
            )
        return {
            "opportunity": opportunity.to_dict(),
            "combined_report": combined.to_dict() if combined else None,
        }

    @app.post(
        "/api/runs/{run_id}/pitch-pack",
        status_code=201,
        dependencies=[auth],
    )
    def create_pitch_pack(run_id: str, payload: PitchPackRequest) -> dict:
        try:
            package = outreach_service.create_package(
                insight_run_id=run_id,
                prospect_id=payload.prospect_id,
                report_version="v4",
                vertical_pack_version=payload.vertical_pack_version,
                report_snapshot_id=payload.report_snapshot_id,
                client_report_bundle_id=payload.client_report_bundle_id,
                agentic_assessment_id=payload.agentic_assessment_id,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"outreach_package": package.to_dict()}

    @app.post("/api/runs/{run_id}/outreach-packages", status_code=201, dependencies=[auth])
    def create_outreach_package(run_id: str, payload: OutreachPackageCreateRequest) -> dict:
        try:
            package = outreach_service.create_package(
                insight_run_id=run_id,
                prospect_id=payload.prospect_id,
                report_version=payload.report_version,
                vertical_pack_version=payload.vertical_pack_version,
                report_snapshot_id=payload.report_snapshot_id,
                client_report_bundle_id=payload.client_report_bundle_id,
                agentic_assessment_id=payload.agentic_assessment_id,
            )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"outreach_package": package.to_dict()}

    @app.get("/api/outreach-packages", dependencies=[auth])
    def list_outreach_packages(
        prospect_id: str | None = None,
        insight_run_id: str | None = None,
        state: str | None = None,
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> dict:
        return {
            "outreach_packages": [
                package.to_dict()
                for package in active_repository.list_outreach_packages(
                    prospect_id=prospect_id,
                    insight_run_id=insight_run_id,
                    state=state,
                    limit=limit,
                )
            ]
        }

    @app.get("/api/outreach-packages/{package_id}", dependencies=[auth])
    def get_outreach_package(package_id: str) -> dict:
        package = active_repository.get_outreach_package(package_id)
        if package is None:
            raise HTTPException(status_code=404, detail=f"outreach package {package_id} not found")
        return {"outreach_package": package.to_dict()}

    @app.post("/api/outreach-packages/{package_id}/approve", dependencies=[auth])
    def approve_outreach_package(package_id: str, payload: PackageReviewRequest) -> dict:
        try:
            package = outreach_service.approve_package(
                package_id,
                operator=payload.operator,
                acknowledge_partial_ai=payload.acknowledge_partial_ai,
            )
            existing_approval = any(
                event.stage == "package_approved"
                for event in active_repository.list_activation_events(
                    outreach_package_id=package.id,
                    limit=5000,
                )
            )
            if not existing_approval:
                prospect = active_repository.get_prospect(package.prospect_id)
                if prospect is None:
                    raise ValueError(f"prospect {package.prospect_id} not found")
                activation_service.append_event(
                    OutreachActivationEvent(
                        insight_run_id=package.insight_run_id,
                        outreach_package_id=package.id,
                        package_version=package.package_version,
                        stage="package_approved",
                        vertical_id=prospect.vertical_id,
                        operator=payload.operator,
                        service_packages=package.recommended_service_package,
                    )
                )
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"outreach_package": package.to_dict()}

    @app.post("/api/outreach-packages/{package_id}/reject", dependencies=[auth])
    def reject_outreach_package(package_id: str, payload: PackageReviewRequest) -> dict:
        try:
            package = outreach_service.reject_package(package_id, reason_code=payload.reason_code)
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"outreach_package": package.to_dict()}

    @app.get("/api/outreach-packages/{package_id}/export", dependencies=[auth])
    def export_outreach_package(package_id: str) -> dict:
        try:
            return outreach_service.export_package(package_id)
        except ValueError as exc:
            raise value_error_422(exc) from exc

    @app.post("/api/activation-events", status_code=201, dependencies=[auth])
    def append_activation_event(payload: ActivationEventRequest) -> dict:
        try:
            payload_dict = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
            package = active_repository.get_outreach_package(payload.outreach_package_id)
            if package is None:
                raise ValueError(f"outreach package {payload.outreach_package_id} not found")
            prospect = active_repository.get_prospect(package.prospect_id)
            if prospect is None:
                raise ValueError(f"prospect {package.prospect_id} not found for outreach package")
            if payload.vertical_id != prospect.vertical_id:
                raise ValueError("activation event vertical does not match package prospect")
            event = activation_service.append_event(OutreachActivationEvent(**payload_dict))
        except ValueError as exc:
            raise value_error_422(exc) from exc
        return {"activation_event": event.to_dict()}

    @app.get("/api/funnel", dependencies=[auth])
    def funnel_summary(vertical_id: str | None = None) -> dict:
        return activation_service.summarize(vertical_id=vertical_id)

    @app.post("/api/runs/{run_id}/resume", dependencies=[auth])
    def resume_run(run_id: str, payload: ResumeRequest) -> dict:
        run_or_404(run_id)
        run = base_orchestrator.resume(run_id, max_pages=payload.max_pages)
        return {"run": run.to_dict(), "validation": base_orchestrator.validate(run_id)}

    @app.post("/api/runs/{run_id}/rerun", dependencies=[auth])
    def rerun_stage(run_id: str, payload: RerunRequest) -> dict:
        run_or_404(run_id)
        try:
            run = base_orchestrator.rerun_stage(run_id, payload.stage, max_pages=payload.max_pages)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {"run": run.to_dict(), "validation": base_orchestrator.validate(run_id)}

    @app.post("/api/runs/{run_id}/approve-paid-enrichment", dependencies=[auth])
    def approve_paid_enrichment(run_id: str, payload: ResumeRequest) -> dict:
        run_or_404(run_id)
        if not base_config.dataforseo.configured:
            raise HTTPException(status_code=409, detail="DataForSEO credentials are not configured")
        approved_orchestrator = orchestrator_for(True)
        run = approved_orchestrator.rerun_stage(
            run_id,
            "pulling_search_intelligence",
            max_pages=payload.max_pages,
        )
        return {"run": run.to_dict(), "validation": approved_orchestrator.validate(run_id)}

    @app.get("/api/diff", dependencies=[auth])
    def diff_runs(base_run_id: str, comparison_run_id: str) -> dict:
        try:
            return base_orchestrator.diff_runs(base_run_id, comparison_run_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app

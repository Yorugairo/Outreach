from __future__ import annotations

from typing import Protocol

from src.models import (
    DiscoveredAsset,
    AcquisitionCalibrationRecord,
    BusinessEconomicsProfile,
    ConversionEventMap,
    DemandConversionEvidence,
    DemandConversionReportSnapshot,
    DemandEvidenceSet,
    DemandTrendSnapshot,
    InsightReport,
    InsightRun,
    KeywordSet,
    KeywordSetBinding,
    MarketEvidenceRun,
    OutreachActivationEvent,
    OutreachPackage,
    OpportunityScenario,
    PageRecord,
    ProspectRecord,
    ReportAlias,
    ReportSnapshot,
    ReportComparisonSnapshot,
    ClientReportBundle,
    SiteEvidencePack,
    AgenticAnalysisJob,
    AgentCallRecord,
    AgenticAssessmentSnapshot,
    AgenticAssessmentReviewEvent,
    VerticalAgenticPack,
    AgenticWorkItem,
    AgenticToolStep,
    BusinessFactLedgerSnapshot,
    DecisionCoverageSnapshot,
    JourneyEvidenceRun,
    AIRepresentationAccuracySnapshot,
    OwnerDiagnosticSnapshot,
    RemediationBlueprintSnapshot,
    RecommendationOutcomeLink,
    AgenticEvidenceReviewEvent,
    RunStageEvent,
    SEOTarget,
    StageCheckpoint,
    VerticalPack,
    OwnedMeasurementSnapshot,
)


class InsightRepository(Protocol):
    def upsert_target(self, target: SEOTarget) -> SEOTarget: ...

    def create_run(self, run: InsightRun) -> InsightRun: ...

    def update_run(self, run: InsightRun) -> InsightRun: ...

    def append_stage_event(self, event: RunStageEvent) -> RunStageEvent: ...

    def save_discovered_asset(self, asset: DiscoveredAsset) -> DiscoveredAsset: ...

    def save_page_record(self, page: PageRecord) -> PageRecord: ...
    def list_page_records(self, run_id: str) -> list[PageRecord]: ...

    def save_report(self, report: InsightReport) -> InsightReport: ...
    def save_report_snapshot_payload(
        self, run_id: str, payload_sha256: str, payload: dict
    ) -> str: ...

    def save_report_snapshot(self, snapshot: ReportSnapshot) -> ReportSnapshot: ...
    def get_report_snapshot(self, snapshot_id: str) -> "ReportSnapshot | None": ...
    def list_report_snapshots(
        self,
        *,
        run_id: str | None = None,
        report_contract: str | None = None,
        limit: int = 1000,
    ) -> list[ReportSnapshot]: ...
    def get_latest_report_snapshot(
        self, run_id: str, report_contract: str, alias: str = "latest"
    ) -> "ReportSnapshot | None": ...
    def list_report_snapshot_history(
        self, run_id: str, report_contract: str, limit: int = 1000
    ) -> list[ReportSnapshot]: ...

    def save_report_comparison_snapshot(
        self, snapshot: ReportComparisonSnapshot
    ) -> ReportComparisonSnapshot: ...
    def get_report_comparison_snapshot(
        self, snapshot_id: str
    ) -> "ReportComparisonSnapshot | None": ...
    def list_report_comparison_snapshots(
        self,
        *,
        target_id: str | None = None,
        baseline_snapshot_id: str | None = None,
        current_snapshot_id: str | None = None,
        limit: int = 1000,
    ) -> list[ReportComparisonSnapshot]: ...

    def save_report_alias(self, alias: ReportAlias) -> ReportAlias: ...
    def get_report_alias(self, run_id: str, report_contract: str, alias: str) -> "ReportAlias | None": ...
    def list_report_aliases(
        self,
        *,
        run_id: str | None = None,
        report_contract: str | None = None,
        limit: int = 1000,
    ) -> list[ReportAlias]: ...

    def save_client_report_bundle(self, bundle: ClientReportBundle) -> ClientReportBundle: ...
    def get_client_report_bundle(self, bundle_id: str) -> "ClientReportBundle | None": ...
    def list_client_report_bundles(
        self,
        *,
        run_id: str | None = None,
        report_snapshot_id: str | None = None,
        limit: int = 1000,
    ) -> list[ClientReportBundle]: ...

    def save_site_evidence_pack(self, pack: SiteEvidencePack) -> SiteEvidencePack: ...
    def get_site_evidence_pack(self, pack_id: str) -> "SiteEvidencePack | None": ...
    def list_site_evidence_packs(
        self, *, run_id: str | None = None, limit: int = 1000
    ) -> list[SiteEvidencePack]: ...

    def save_agentic_analysis_job(self, job: AgenticAnalysisJob) -> AgenticAnalysisJob: ...
    def update_agentic_analysis_job(self, job: AgenticAnalysisJob) -> AgenticAnalysisJob: ...
    def get_agentic_analysis_job(self, job_id: str) -> "AgenticAnalysisJob | None": ...
    def get_agentic_job_by_idempotency_key(self, idempotency_key: str) -> "AgenticAnalysisJob | None": ...
    def list_agentic_analysis_jobs(
        self, *, evidence_pack_id: str | None = None, state: str | None = None, limit: int = 1000
    ) -> list[AgenticAnalysisJob]: ...

    def append_agent_call_record(self, call: AgentCallRecord) -> AgentCallRecord: ...
    def get_agent_call_record(self, call_id: str) -> "AgentCallRecord | None": ...
    def list_agent_call_records(
        self, *, job_id: str | None = None, limit: int = 5000
    ) -> list[AgentCallRecord]: ...

    def save_agentic_assessment_snapshot(self, assessment: AgenticAssessmentSnapshot) -> AgenticAssessmentSnapshot: ...
    def get_agentic_assessment_snapshot(self, assessment_id: str) -> "AgenticAssessmentSnapshot | None": ...
    def list_agentic_assessment_snapshots(
        self, *, job_id: str | None = None, evidence_pack_id: str | None = None,
        predecessor_id: str | None = None, limit: int = 1000,
    ) -> list[AgenticAssessmentSnapshot]: ...

    def append_agentic_assessment_review_event(
        self, event: AgenticAssessmentReviewEvent
    ) -> AgenticAssessmentReviewEvent: ...
    def list_agentic_assessment_review_events(
        self, assessment_id: str, limit: int = 5000
    ) -> list[AgenticAssessmentReviewEvent]: ...
    def get_agentic_assessment_review_state(self, assessment_id: str) -> str: ...

    # P12 durable agentic evidence lifecycle. Work items are leased and
    # updated; snapshots and review events are immutable/append-only.
    def save_vertical_agentic_pack(self, pack: VerticalAgenticPack) -> VerticalAgenticPack: ...
    def get_vertical_agentic_pack(self, pack_id: str) -> "VerticalAgenticPack | None": ...
    def list_vertical_agentic_packs(
        self, *, vertical_id: str | None = None, version: str | None = None,
        state: str | None = None, limit: int = 1000,
    ) -> list[VerticalAgenticPack]: ...

    def save_agentic_work_item(self, item: AgenticWorkItem) -> AgenticWorkItem: ...
    def update_agentic_work_item(self, item: AgenticWorkItem) -> AgenticWorkItem: ...
    def get_agentic_work_item(self, item_id: str) -> "AgenticWorkItem | None": ...
    def get_agentic_work_item_by_idempotency_key(self, idempotency_key: str) -> "AgenticWorkItem | None": ...
    def list_agentic_work_items(
        self, *, run_id: str | None = None, state: str | None = None,
        work_kind: str | None = None, mode: str | None = None,
        limit: int = 1000,
    ) -> list[AgenticWorkItem]: ...
    def lease_agentic_work_item(
        self, item_id: str, owner: str, *, lease_seconds: int = 90
    ) -> AgenticWorkItem: ...

    def append_agentic_tool_step(self, step: AgenticToolStep) -> AgenticToolStep: ...
    def get_agentic_tool_step(self, step_id: str) -> "AgenticToolStep | None": ...
    def list_agentic_tool_steps(
        self, *, work_item_id: str | None = None, limit: int = 5000
    ) -> list[AgenticToolStep]: ...

    def save_business_fact_ledger_snapshot(
        self, snapshot: BusinessFactLedgerSnapshot
    ) -> BusinessFactLedgerSnapshot: ...
    def get_business_fact_ledger_snapshot(
        self, snapshot_id: str
    ) -> "BusinessFactLedgerSnapshot | None": ...
    def list_business_fact_ledger_snapshots(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[BusinessFactLedgerSnapshot]: ...

    def save_decision_coverage_snapshot(
        self, snapshot: DecisionCoverageSnapshot
    ) -> DecisionCoverageSnapshot: ...
    def get_decision_coverage_snapshot(
        self, snapshot_id: str
    ) -> "DecisionCoverageSnapshot | None": ...
    def list_decision_coverage_snapshots(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[DecisionCoverageSnapshot]: ...

    def save_journey_evidence_run(self, evidence: JourneyEvidenceRun) -> JourneyEvidenceRun: ...
    def get_journey_evidence_run(self, evidence_id: str) -> "JourneyEvidenceRun | None": ...
    def list_journey_evidence_runs(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[JourneyEvidenceRun]: ...

    def save_ai_representation_accuracy_snapshot(
        self, snapshot: AIRepresentationAccuracySnapshot
    ) -> AIRepresentationAccuracySnapshot: ...
    def get_ai_representation_accuracy_snapshot(
        self, snapshot_id: str
    ) -> "AIRepresentationAccuracySnapshot | None": ...
    def list_ai_representation_accuracy_snapshots(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[AIRepresentationAccuracySnapshot]: ...

    def save_owner_diagnostic_snapshot(
        self, snapshot: OwnerDiagnosticSnapshot
    ) -> OwnerDiagnosticSnapshot: ...
    def get_owner_diagnostic_snapshot(
        self, snapshot_id: str
    ) -> "OwnerDiagnosticSnapshot | None": ...
    def list_owner_diagnostic_snapshots(
        self, *, run_id: str | None = None, prospect_id: str | None = None,
        limit: int = 1000,
    ) -> list[OwnerDiagnosticSnapshot]: ...

    def save_remediation_blueprint_snapshot(
        self, snapshot: RemediationBlueprintSnapshot
    ) -> RemediationBlueprintSnapshot: ...
    def get_remediation_blueprint_snapshot(
        self, snapshot_id: str
    ) -> "RemediationBlueprintSnapshot | None": ...
    def list_remediation_blueprint_snapshots(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[RemediationBlueprintSnapshot]: ...

    def save_recommendation_outcome_link(
        self, link: RecommendationOutcomeLink
    ) -> RecommendationOutcomeLink: ...
    def get_recommendation_outcome_link(
        self, link_id: str
    ) -> "RecommendationOutcomeLink | None": ...
    def list_recommendation_outcome_links(
        self, *, prospect_id: str | None = None, vertical_id: str | None = None,
        recommendation_id: str | None = None, limit: int = 1000,
    ) -> list[RecommendationOutcomeLink]: ...

    def append_agentic_evidence_review_event(
        self, event: AgenticEvidenceReviewEvent
    ) -> AgenticEvidenceReviewEvent: ...
    def list_agentic_evidence_review_events(
        self, snapshot_id: str, *, limit: int = 5000
    ) -> list[AgenticEvidenceReviewEvent]: ...
    def get_agentic_evidence_review_state(self, snapshot_id: str) -> str: ...

    # Convenience spellings used by snapshot/bundle service callers.
    save_snapshot = save_report_snapshot
    get_snapshot = get_report_snapshot
    list_snapshots = list_report_snapshots
    get_latest_snapshot = get_latest_report_snapshot
    list_snapshot_history = list_report_snapshot_history
    get_report_snapshot_history = list_report_snapshot_history
    save_comparison_snapshot = save_report_comparison_snapshot
    get_comparison_snapshot = get_report_comparison_snapshot
    list_comparison_snapshots = list_report_comparison_snapshots
    save_alias = save_report_alias
    get_alias = get_report_alias
    list_aliases = list_report_aliases
    save_bundle = save_client_report_bundle
    get_bundle = get_client_report_bundle
    list_bundles = list_client_report_bundles
    save_evidence_pack = save_site_evidence_pack
    get_evidence_pack = get_site_evidence_pack
    list_evidence_packs = list_site_evidence_packs
    save_agentic_job = save_agentic_analysis_job
    update_agentic_job = update_agentic_analysis_job
    get_agentic_job = get_agentic_analysis_job
    list_agentic_jobs = list_agentic_analysis_jobs
    append_agent_call = append_agent_call_record
    save_agent_call_record = append_agent_call_record
    list_agent_calls = list_agent_call_records
    get_agent_call_records = list_agent_call_records
    save_assessment = save_agentic_assessment_snapshot
    save_agentic_assessment = save_agentic_assessment_snapshot
    get_assessment = get_agentic_assessment_snapshot
    list_assessments = list_agentic_assessment_snapshots
    append_review_event = append_agentic_assessment_review_event
    append_assessment_review_event = append_agentic_assessment_review_event
    get_review_state = get_agentic_assessment_review_state
    save_agentic_pack = save_vertical_agentic_pack
    get_agentic_pack = get_vertical_agentic_pack
    list_agentic_packs = list_vertical_agentic_packs
    save_work_item = save_agentic_work_item
    update_work_item = update_agentic_work_item
    get_work_item = get_agentic_work_item
    list_work_items = list_agentic_work_items
    lease_work_item = lease_agentic_work_item
    append_tool_step = append_agentic_tool_step
    save_agentic_tool_step = append_agentic_tool_step
    save_fact_ledger = save_business_fact_ledger_snapshot
    save_business_fact_ledger = save_business_fact_ledger_snapshot
    get_business_fact_ledger = get_business_fact_ledger_snapshot
    list_business_fact_ledgers = list_business_fact_ledger_snapshots
    save_decision_coverage = save_decision_coverage_snapshot
    get_decision_coverage = get_decision_coverage_snapshot
    list_decision_coverages = list_decision_coverage_snapshots
    save_journey_evidence = save_journey_evidence_run
    get_journey_evidence = get_journey_evidence_run
    list_journey_evidence = list_journey_evidence_runs
    save_ai_representation = save_ai_representation_accuracy_snapshot
    get_ai_representation = get_ai_representation_accuracy_snapshot
    list_ai_representations = list_ai_representation_accuracy_snapshots
    save_owner_diagnostic = save_owner_diagnostic_snapshot
    get_owner_diagnostic = get_owner_diagnostic_snapshot
    list_owner_diagnostics = list_owner_diagnostic_snapshots
    save_remediation_blueprint = save_remediation_blueprint_snapshot
    get_remediation_blueprint = get_remediation_blueprint_snapshot
    list_remediation_blueprints = list_remediation_blueprint_snapshots
    save_outcome_link = save_recommendation_outcome_link
    get_outcome_link = get_recommendation_outcome_link
    list_outcome_links = list_recommendation_outcome_links
    append_evidence_review_event = append_agentic_evidence_review_event
    save_agentic_evidence_review_event = append_agentic_evidence_review_event
    list_evidence_review_events = list_agentic_evidence_review_events
    get_evidence_review_state = get_agentic_evidence_review_state

    def save_checkpoint(self, checkpoint: StageCheckpoint) -> StageCheckpoint: ...

    def get_run(self, run_id: str) -> "InsightRun | None": ...
    def list_runs(self, limit: int = 20) -> list["InsightRun"]: ...
    def list_stage_events(self, run_id: str) -> list["RunStageEvent"]: ...
    def get_report(self, run_id: str, report_version: str) -> "InsightReport | None": ...
    def get_checkpoint(self, run_id: str, attempt_id: str, stage_name: str) -> "StageCheckpoint | None": ...

    def save_vertical_pack(self, pack: VerticalPack) -> VerticalPack: ...
    def get_vertical_pack(self, pack_id: str) -> "VerticalPack | None": ...
    def list_vertical_packs(self) -> list[VerticalPack]: ...

    def save_prospect(self, prospect: ProspectRecord) -> ProspectRecord: ...
    def get_prospect(self, prospect_id: str) -> "ProspectRecord | None": ...
    def list_prospects(
        self,
        *,
        vertical_id: str | None = None,
        qualification_status: str | None = None,
        limit: int = 1000,
    ) -> list[ProspectRecord]: ...

    def save_keyword_set(self, keyword_set: KeywordSet) -> KeywordSet: ...
    def get_keyword_set(self, keyword_set_id: str) -> "KeywordSet | None": ...
    def list_keyword_sets(
        self,
        *,
        vertical_id: str | None = None,
        normalized_domain: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[KeywordSet]: ...
    def save_keyword_set_binding(self, binding: KeywordSetBinding) -> KeywordSetBinding: ...
    def list_keyword_set_bindings(
        self,
        *,
        keyword_set_id: str | None = None,
        normalized_domain: str | None = None,
        prospect_id: str | None = None,
        state: str | None = "active",
        limit: int = 1000,
    ) -> list[KeywordSetBinding]: ...

    def save_market_evidence_run(self, market_run: MarketEvidenceRun) -> MarketEvidenceRun: ...
    def get_market_evidence_run(self, market_run_id: str) -> "MarketEvidenceRun | None": ...
    def list_market_evidence_runs(
        self,
        *,
        insight_run_id: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[MarketEvidenceRun]: ...
    def save_market_artifact(
        self,
        insight_run_id: str,
        market_run_id: str,
        relative_path: str,
        payload: dict | bytes,
    ) -> str: ...
    def save_opportunity_artifact(
        self,
        insight_run_id: str,
        scenario_id: str,
        relative_path: str,
        payload: dict | bytes,
    ) -> str: ...

    def save_outreach_package(self, package: OutreachPackage) -> OutreachPackage: ...
    def get_outreach_package(self, package_id: str) -> "OutreachPackage | None": ...
    def list_outreach_packages(
        self,
        *,
        prospect_id: str | None = None,
        insight_run_id: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[OutreachPackage]: ...

    def append_activation_event(self, event: OutreachActivationEvent) -> OutreachActivationEvent: ...
    def list_activation_events(
        self,
        *,
        insight_run_id: str | None = None,
        outreach_package_id: str | None = None,
        vertical_id: str | None = None,
        limit: int = 5000,
    ) -> list[OutreachActivationEvent]: ...

    def save_demand_evidence_set(self, evidence: DemandEvidenceSet) -> DemandEvidenceSet: ...
    def get_demand_evidence_set(self, evidence_id: str) -> "DemandEvidenceSet | None": ...
    def list_demand_evidence_sets(
        self,
        *,
        prospect_id: str | None = None,
        keyword_set_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        superseded_by_id: str | None = None,
        limit: int = 1000,
    ) -> list[DemandEvidenceSet]: ...

    def save_business_economics_profile(self, profile: BusinessEconomicsProfile) -> BusinessEconomicsProfile: ...
    def get_business_economics_profile(self, profile_id: str) -> "BusinessEconomicsProfile | None": ...
    def list_business_economics_profiles(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        superseded_by_id: str | None = None,
        limit: int = 1000,
    ) -> list[BusinessEconomicsProfile]: ...

    def save_opportunity_scenario(self, scenario: OpportunityScenario) -> OpportunityScenario: ...
    def get_opportunity_scenario(self, scenario_id: str) -> "OpportunityScenario | None": ...
    def list_opportunity_scenarios(
        self,
        *,
        insight_run_id: str | None = None,
        prospect_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        calibrated_from_id: str | None = None,
        limit: int = 1000,
    ) -> list[OpportunityScenario]: ...

    def save_acquisition_calibration_record(self, record: AcquisitionCalibrationRecord) -> AcquisitionCalibrationRecord: ...
    def get_acquisition_calibration_record(self, record_id: str) -> "AcquisitionCalibrationRecord | None": ...
    def list_acquisition_calibration_records(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        market: str | None = None,
        limit: int = 1000,
    ) -> list[AcquisitionCalibrationRecord]: ...

    def save_owned_measurement_snapshot(self, snapshot: OwnedMeasurementSnapshot) -> OwnedMeasurementSnapshot: ...
    def get_owned_measurement_snapshot(self, snapshot_id: str) -> "OwnedMeasurementSnapshot | None": ...
    def list_owned_measurement_snapshots(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        source: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[OwnedMeasurementSnapshot]: ...

    def save_demand_trend_snapshot(
        self, snapshot: DemandTrendSnapshot
    ) -> DemandTrendSnapshot: ...
    def get_demand_trend_snapshot(
        self, snapshot_id: str
    ) -> "DemandTrendSnapshot | None": ...
    def list_demand_trend_snapshots(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        market: str | None = None,
        source: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[DemandTrendSnapshot]: ...

    def save_conversion_event_map(
        self, event_map: ConversionEventMap
    ) -> ConversionEventMap: ...
    def get_conversion_event_map(
        self, event_map_id: str
    ) -> "ConversionEventMap | None": ...
    def list_conversion_event_maps(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[ConversionEventMap]: ...

    def save_demand_conversion_evidence(
        self, evidence: DemandConversionEvidence
    ) -> DemandConversionEvidence: ...
    def get_demand_conversion_evidence(
        self, evidence_id: str
    ) -> "DemandConversionEvidence | None": ...
    def list_demand_conversion_evidence(
        self,
        *,
        insight_run_id: str | None = None,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        mode: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[DemandConversionEvidence]: ...

    def save_demand_conversion_report_snapshot(
        self, snapshot: DemandConversionReportSnapshot
    ) -> DemandConversionReportSnapshot: ...
    def get_demand_conversion_report_snapshot(
        self, snapshot_id: str
    ) -> "DemandConversionReportSnapshot | None": ...
    def list_demand_conversion_report_snapshots(
        self,
        *,
        run_id: str | None = None,
        demand_conversion_evidence_id: str | None = None,
        mode: str | None = None,
        limit: int = 1000,
    ) -> list[DemandConversionReportSnapshot]: ...

    # Short aliases keep the repository ergonomic for service callers.
    save_demand_evidence = save_demand_evidence_set
    get_demand_evidence = get_demand_evidence_set
    list_demand_evidence = list_demand_evidence_sets
    save_economics_profile = save_business_economics_profile
    get_economics_profile = get_business_economics_profile
    list_economics_profiles = list_business_economics_profiles
    save_opportunity = save_opportunity_scenario
    get_opportunity = get_opportunity_scenario
    list_opportunities = list_opportunity_scenarios
    save_calibration_record = save_acquisition_calibration_record
    get_calibration_record = get_acquisition_calibration_record
    list_calibration_records = list_acquisition_calibration_records
    save_acquisition_calibration = save_acquisition_calibration_record
    get_acquisition_calibration = get_acquisition_calibration_record
    list_acquisition_calibrations = list_acquisition_calibration_records
    save_owned_measurement = save_owned_measurement_snapshot
    get_owned_measurement = get_owned_measurement_snapshot
    list_owned_measurements = list_owned_measurement_snapshots
    save_demand_trend = save_demand_trend_snapshot
    get_demand_trend = get_demand_trend_snapshot
    list_demand_trends = list_demand_trend_snapshots
    save_event_map = save_conversion_event_map
    get_event_map = get_conversion_event_map
    list_event_maps = list_conversion_event_maps
    save_demand_conversion = save_demand_conversion_evidence
    get_demand_conversion = get_demand_conversion_evidence
    list_demand_conversions = list_demand_conversion_evidence
